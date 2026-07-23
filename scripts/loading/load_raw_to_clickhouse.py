"""Load S3-shaped local raw files into ClickHouse raw tables."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import os
import re
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import clickhouse_connect

from scripts.ingestion.raw_files import raw_file_path
from scripts.loading.load_raw_to_postgres import (
    RAW_SCHEMA,
    DeadLetterManifestEntry,
    RawLoadSpec,
    load_dead_letter_manifest_entries,
    load_specs,
    record_dead_letter_event,
    record_failure,
)
from scripts.orchestration.batch_control import BatchRunContext, mark_batch_status
from scripts.orchestration.control_postgres import (
    add_control_postgres_args,
    control_connection,
)

STAGING_PREFIX = "_batch_staging"
FAILURE_POINTS = {
    "before_staging_insert",
    "after_staging_insert",
    "after_staging_validation",
    "after_partition_replacement",
    "after_target_readback",
    "before_control_success",
}


class ClickHouseClient(Protocol):
    def command(
        self,
        cmd: str,
        parameters: Sequence[Any] | dict[str, Any] | None = None,
        data: str | bytes | None = None,
        settings: dict[str, Any] | None = None,
        use_database: bool = True,
        external_data: Any = None,
        transport_settings: dict[str, str] | None = None,
    ) -> Any: ...

    def query(self, query: str, *args: Any, **kwargs: Any) -> Any: ...

    def raw_insert(
        self,
        table: str,
        column_names: Sequence[str] | None = None,
        insert_block: str | bytes | Any | None = None,
        settings: dict[str, Any] | None = None,
        fmt: str | None = None,
        compression: str | None = None,
        transport_settings: dict[str, str] | None = None,
    ) -> Any: ...

    def close(self) -> None: ...


@dataclass(frozen=True)
class ClickHouseLoadOutcome:
    entity_name: str
    source_path: Path
    staging_table: str
    staged_rows: int
    target_rows: int


def utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0, tzinfo=None)


def clickhouse_password() -> str:
    if password := os.environ.get("CLICKHOUSE_PASSWORD"):
        return password

    password_file = os.environ.get("CLICKHOUSE_PASSWORD_FILE")
    if not password_file:
        return "olist"

    return Path(password_file).read_text(encoding="utf-8").rstrip("\r\n")


def clickhouse_client(args: argparse.Namespace) -> ClickHouseClient:
    return clickhouse_connect.get_client(
        host=args.clickhouse_host,
        port=args.clickhouse_port,
        username=args.clickhouse_user,
        password=args.clickhouse_password or clickhouse_password(),
        database=args.clickhouse_database,
        secure=args.clickhouse_secure,
    )


def ch_identifier(identifier: str) -> str:
    if "\x00" in identifier:
        raise ValueError("ClickHouse identifier contains a null byte")
    return f"`{identifier.replace('`', '``')}`"


def ch_string(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def qualified(database: str, table: str) -> str:
    return f"{ch_identifier(database)}.{ch_identifier(table)}"


def deterministic_staging_table(batch_id: str, run_id: str, entity_name: str) -> str:
    raw_name = f"{STAGING_PREFIX}_{batch_id}_{run_id}_{entity_name}"
    normalized = re.sub(r"[^0-9A-Za-z_]+", "_", raw_name).strip("_").lower()
    digest = hashlib.sha256(raw_name.encode("utf-8")).hexdigest()[:12]
    prefix = normalized[:80].rstrip("_") or STAGING_PREFIX
    return f"{prefix}_{digest}"


def inject_failure(args: argparse.Namespace, point: str) -> None:
    if args.inject_failure == point:
        raise RuntimeError(f"Injected ClickHouse batch loader failure at {point}")


def fetch_one_int(client: ClickHouseClient, query: str) -> int:
    row = client.query(query).first_row
    if row is None:
        raise ValueError("Expected ClickHouse query to return exactly one row")
    return int(row[0])


def clickhouse_columns(
    client: ClickHouseClient,
    database: str,
    table: str,
) -> list[str]:
    rows = client.query(
        """
        SELECT name
        FROM system.columns
        WHERE database = {database:String}
          AND table = {table:String}
        ORDER BY position
        """,
        parameters={"database": database, "table": table},
    ).result_rows
    columns = [str(row[0]) for row in rows]
    if not columns:
        raise ValueError(f"ClickHouse table {database}.{table} does not exist")
    return columns


def csv_header(source_path: Path) -> list[str]:
    with gzip.open(source_path, mode="rt", encoding="utf-8", newline="") as csv_file:
        reader = csv.reader(csv_file)
        try:
            return next(reader)
        except StopIteration as exc:
            raise ValueError(f"Prepared raw file is empty: {source_path}") from exc


def validate_source_schema(
    client: ClickHouseClient,
    spec: RawLoadSpec,
    source_path: Path,
) -> list[str]:
    table_columns = clickhouse_columns(client, RAW_SCHEMA, spec.entity_name)
    header = csv_header(source_path)
    if header != table_columns:
        raise ValueError(
            f"Prepared raw file header for {spec.entity_name} does not match "
            f"ClickHouse table columns. Expected {table_columns}, got {header}"
        )
    return table_columns


def create_staging_table(
    client: ClickHouseClient,
    spec: RawLoadSpec,
    staging_table: str,
) -> None:
    client.command(f"DROP TABLE IF EXISTS {qualified(RAW_SCHEMA, staging_table)}")
    client.command(
        "CREATE TABLE "
        f"{qualified(RAW_SCHEMA, staging_table)} AS "
        f"{qualified(RAW_SCHEMA, spec.entity_name)}"
    )


def drop_staging_table(client: ClickHouseClient, staging_table: str) -> None:
    client.command(f"DROP TABLE IF EXISTS {qualified(RAW_SCHEMA, staging_table)}")


def count_table_batch(
    client: ClickHouseClient,
    table: str,
    batch_id: str,
) -> int:
    return fetch_one_int(
        client,
        "SELECT count() "
        f"FROM {qualified(RAW_SCHEMA, table)} "
        f"WHERE _batch_id = {ch_string(batch_id)}",
    )


def load_csv_to_staging(
    client: ClickHouseClient,
    staging_table: str,
    source_path: Path,
    columns: Sequence[str],
) -> None:
    with gzip.open(source_path, mode="rb") as source_file:
        client.raw_insert(
            qualified(RAW_SCHEMA, staging_table),
            column_names=columns,
            insert_block=source_file,
            fmt="CSVWithNames",
            settings={
                "input_format_csv_empty_as_default": 1,
                "input_format_null_as_default": 1,
            },
        )


def replace_target_partition(
    client: ClickHouseClient,
    spec: RawLoadSpec,
    staging_table: str,
    batch_id: str,
) -> None:
    client.command(
        "ALTER TABLE "
        f"{qualified(RAW_SCHEMA, spec.entity_name)} "
        f"REPLACE PARTITION {ch_string(batch_id)} "
        f"FROM {qualified(RAW_SCHEMA, staging_table)}"
    )


def record_success(
    control_pg_connection: Any,
    spec: RawLoadSpec,
    batch_id: str,
    run_id: str,
    source_path: Path,
    started_at: datetime,
    rows_loaded: int,
) -> None:
    with control_pg_connection.cursor() as cursor:
        cursor.execute(
            """
            delete from audit.load_runs
            where batch_id = %s
              and entity_name = %s;
            """,
            (batch_id, spec.entity_name),
        )
        cursor.execute(
            """
            insert into audit.load_runs (
                load_run_id,
                batch_id,
                entity_name,
                source_uri,
                target_table,
                status,
                rows_loaded,
                started_at,
                finished_at,
                error_message
            )
            values (%s, %s, %s, %s, %s, 'SUCCESS', %s, %s, current_timestamp, null);
            """,
            (
                run_id,
                batch_id,
                spec.entity_name,
                source_path.resolve().as_uri(),
                f"{RAW_SCHEMA}.{spec.entity_name}",
                rows_loaded,
                started_at,
            ),
        )


def load_one_spec(
    client: ClickHouseClient,
    control_pg_connection: Any,
    spec: RawLoadSpec,
    raw_dir: Path,
    batch_date: str,
    batch_id: str,
    run_id: str,
    dead_letter_entry: DeadLetterManifestEntry | None,
    args: argparse.Namespace,
) -> ClickHouseLoadOutcome:
    source_path = raw_file_path(
        raw_dir, spec.entity_name, batch_date, run_id, spec.file_name
    )
    staging_table = deterministic_staging_table(batch_id, run_id, spec.entity_name)
    started_at = utc_now()
    try:
        with control_pg_connection.cursor() as cursor:
            cursor.execute(
                """
                delete from audit.load_runs
                where batch_id = %s
                  and entity_name = %s;
                """,
                (batch_id, spec.entity_name),
            )

        record_dead_letter_event(
            control_connection=control_pg_connection,
            spec=spec,
            batch_id=batch_id,
            run_id=run_id,
            manifest_entry=dead_letter_entry,
        )

        if not source_path.exists():
            raise FileNotFoundError(f"Missing prepared raw file: {source_path}")

        columns = validate_source_schema(client, spec, source_path)
        create_staging_table(client, spec, staging_table)
        inject_failure(args, "before_staging_insert")
        load_csv_to_staging(client, staging_table, source_path, columns)
        inject_failure(args, "after_staging_insert")

        staged_rows = count_table_batch(client, staging_table, batch_id)
        expected_rows = (
            dead_letter_entry.valid_rows if dead_letter_entry is not None else None
        )
        if expected_rows is not None and staged_rows != expected_rows:
            raise ValueError(
                f"ClickHouse staging count mismatch for {spec.entity_name}: "
                f"expected {expected_rows}, got {staged_rows}"
            )
        inject_failure(args, "after_staging_validation")

        replace_target_partition(client, spec, staging_table, batch_id)
        inject_failure(args, "after_partition_replacement")

        target_rows = count_table_batch(client, spec.entity_name, batch_id)
        if target_rows != staged_rows:
            raise ValueError(
                f"ClickHouse target count mismatch for {spec.entity_name}: "
                f"staged {staged_rows}, target {target_rows}"
            )
        inject_failure(args, "after_target_readback")
        inject_failure(args, "before_control_success")

        record_success(
            control_pg_connection,
            spec,
            batch_id,
            run_id,
            source_path,
            started_at,
            target_rows,
        )
        control_pg_connection.commit()
        print(
            f"Loaded {target_rows} rows for {spec.entity_name} into "
            f"{RAW_SCHEMA}.{spec.entity_name}"
        )
        return ClickHouseLoadOutcome(
            entity_name=spec.entity_name,
            source_path=source_path,
            staging_table=staging_table,
            staged_rows=staged_rows,
            target_rows=target_rows,
        )
    except Exception as exc:
        control_pg_connection.rollback()
        try:
            record_failure(
                control_pg_connection,
                spec,
                batch_id,
                run_id,
                source_path,
                started_at,
                exc,
            )
        finally:
            drop_staging_table(client, staging_table)
        raise
    finally:
        if not args.keep_staging_tables:
            drop_staging_table(client, staging_table)


def load_all(
    client: ClickHouseClient,
    control_pg_connection: Any,
    specs: Iterable[RawLoadSpec],
    raw_dir: Path,
    batch_date: str,
    batch_id: str,
    run_id: str,
    dead_letter_entries: dict[str, DeadLetterManifestEntry],
    args: argparse.Namespace,
) -> list[ClickHouseLoadOutcome]:
    outcomes = []
    for spec in specs:
        outcomes.append(
            load_one_spec(
                client=client,
                control_pg_connection=control_pg_connection,
                spec=spec,
                raw_dir=raw_dir,
                batch_date=batch_date,
                batch_id=batch_id,
                run_id=run_id,
                dead_letter_entry=dead_letter_entries.get(spec.entity_name),
                args=args,
            )
        )
    return outcomes


def add_clickhouse_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--clickhouse-host",
        default=os.environ.get("CLICKHOUSE_HOST", "localhost"),
    )
    parser.add_argument(
        "--clickhouse-port",
        type=int,
        default=int(os.environ.get("CLICKHOUSE_PORT", "8123")),
    )
    parser.add_argument(
        "--clickhouse-user",
        default=os.environ.get("CLICKHOUSE_USER", "olist"),
    )
    parser.add_argument("--clickhouse-password")
    parser.add_argument(
        "--clickhouse-database",
        default=os.environ.get("CLICKHOUSE_DATABASE", "analytics"),
    )
    parser.add_argument(
        "--clickhouse-secure",
        action=argparse.BooleanOptionalAction,
        default=os.environ.get("CLICKHOUSE_SECURE", "false").lower() == "true",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", default="data/raw/olist")
    parser.add_argument("--profile", default="docs/source_profile.json")
    parser.add_argument("--batch-date", required=True)
    parser.add_argument("--batch-id")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--dag-id")
    parser.add_argument("--disable-batch-control", action="store_true")
    parser.add_argument("--keep-staging-tables", action="store_true")
    parser.add_argument(
        "--inject-failure",
        choices=sorted(FAILURE_POINTS),
        help="Testing hook that raises at a named ClickHouse load boundary.",
    )
    add_clickhouse_args(parser)
    add_control_postgres_args(parser)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    batch_id = args.batch_id or args.batch_date
    raw_dir = Path(args.raw_dir)
    client = clickhouse_client(args)
    control_pg_connection = control_connection(args)
    batch_context = BatchRunContext(
        batch_id=batch_id,
        batch_date=args.batch_date,
        run_id=args.run_id,
        dag_id=args.dag_id,
    )
    try:
        try:
            load_all(
                client=client,
                control_pg_connection=control_pg_connection,
                specs=load_specs(Path(args.profile)),
                raw_dir=raw_dir,
                batch_date=args.batch_date,
                batch_id=batch_id,
                run_id=args.run_id,
                dead_letter_entries=load_dead_letter_manifest_entries(raw_dir),
                args=args,
            )
            if not args.disable_batch_control:
                mark_batch_status(
                    control_pg_connection,
                    batch_context,
                    "RAW_LOADED",
                    raw_dir=raw_dir,
                )
        except Exception as exc:
            if not args.disable_batch_control:
                mark_batch_status(
                    control_pg_connection,
                    batch_context,
                    "FAILED",
                    raw_dir=raw_dir,
                    error_message=str(exc),
                )
            raise
    finally:
        client.close()
        control_pg_connection.close()


if __name__ == "__main__":
    main()
