"""Shared raw batch loading helpers for local ClickHouse and AWS Redshift."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.ingestion.correction_specs import CORRECTION_FEEDS
from scripts.ingestion.raw_files import load_source_entities

RAW_SCHEMA = "raw_data"


@dataclass(frozen=True)
class RawLoadSpec:
    entity_name: str
    file_name: str


@dataclass(frozen=True)
class DeadLetterManifestEntry:
    entity_name: str
    source_uri: str | None
    dead_letter_uri: str | None
    total_rows: int
    valid_rows: int
    failed_rows: int
    threshold_max_rows: int
    threshold_max_rate: float
    reason_summary: str


def utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0, tzinfo=None)


def fetch_one(cursor: Any) -> tuple[Any, ...]:
    row = cursor.fetchone()
    if row is None:
        raise ValueError("Expected query to return exactly one row")
    return row


def load_specs(profile_path: Path) -> list[RawLoadSpec]:
    source_specs = [
        RawLoadSpec(
            entity_name=entity.entity_name, file_name=f"{entity.entity_name}.csv.gz"
        )
        for entity in load_source_entities(profile_path)
    ]
    correction_specs = [
        RawLoadSpec(entity_name=feed.entity_name, file_name=feed.file_name)
        for feed in CORRECTION_FEEDS
    ]
    return [*source_specs, *correction_specs]


def load_dead_letter_manifest_entries(
    raw_dir: Path,
) -> dict[str, DeadLetterManifestEntry]:
    manifest_entries: dict[str, DeadLetterManifestEntry] = {}

    for manifest_name in ("manifest.json", "correction_manifest.json"):
        manifest_path = raw_dir / manifest_name
        if not manifest_path.exists():
            continue

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        threshold = manifest.get("dead_letter_threshold") or {}

        for file_entry in manifest.get("files", []):
            entity_name = file_entry["entity_name"]
            dead_letter = file_entry.get("dead_letter") or {}
            reason_counts = dead_letter.get("reason_counts") or {}
            manifest_entries[entity_name] = DeadLetterManifestEntry(
                entity_name=entity_name,
                source_uri=file_entry.get("local_uri") or file_entry.get("s3_uri"),
                dead_letter_uri=dead_letter.get("local_uri")
                or dead_letter.get("s3_uri"),
                total_rows=int(file_entry.get("total_row_count") or 0),
                valid_rows=int(
                    file_entry.get("valid_row_count")
                    if file_entry.get("valid_row_count") is not None
                    else file_entry.get("row_count") or 0
                ),
                failed_rows=int(file_entry.get("dead_letter_row_count") or 0),
                threshold_max_rows=int(threshold.get("max_rows") or 0),
                threshold_max_rate=float(threshold.get("max_rate") or 0),
                reason_summary=json.dumps(reason_counts, sort_keys=True),
            )

    return manifest_entries


def execute_sql_files(connection: Any, sql_dir: Path) -> None:
    sql_files = [
        "001_create_schemas.sql",
        "002_create_raw_tables.sql",
        "003_create_audit_tables.sql",
        "005_create_correction_tables.sql",
    ]
    with connection.cursor() as cursor:
        for file_name in sql_files:
            sql_path = sql_dir / file_name
            cursor.execute(sql_path.read_text(encoding="utf-8"))
            print(f"Executed {sql_path}")
    connection.commit()


def record_dead_letter_event(
    control_connection: Any,
    spec: RawLoadSpec,
    batch_id: str,
    run_id: str,
    manifest_entry: DeadLetterManifestEntry | None,
) -> None:
    with control_connection.cursor() as cursor:
        cursor.execute(
            """
            delete from audit.dead_letter_events
            where batch_id = %s
              and entity_name = %s;
            """,
            (batch_id, spec.entity_name),
        )

        if manifest_entry is None or manifest_entry.failed_rows == 0:
            return

        cursor.execute(
            """
            insert into audit.dead_letter_events (
                dead_letter_event_id,
                batch_id,
                load_run_id,
                entity_name,
                source_uri,
                dead_letter_uri,
                total_rows,
                valid_rows,
                failed_rows,
                threshold_max_rows,
                threshold_max_rate,
                reason_summary,
                created_at
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, current_timestamp);
            """,
            (
                f"{batch_id}:{run_id}:{spec.entity_name}",
                batch_id,
                run_id,
                spec.entity_name,
                manifest_entry.source_uri,
                manifest_entry.dead_letter_uri,
                manifest_entry.total_rows,
                manifest_entry.valid_rows,
                manifest_entry.failed_rows,
                manifest_entry.threshold_max_rows,
                manifest_entry.threshold_max_rate,
                manifest_entry.reason_summary[:65535],
            ),
        )


def record_failure(
    control_connection: Any,
    spec: RawLoadSpec,
    batch_id: str,
    run_id: str,
    source_path: Path,
    started_at: datetime,
    error: Exception,
) -> None:
    with control_connection.cursor() as cursor:
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
            delete from audit.dead_letter_events
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
            values (%s, %s, %s, %s, %s, 'FAILED', 0, %s, current_timestamp, %s);
            """,
            (
                run_id,
                batch_id,
                spec.entity_name,
                source_path.resolve().as_uri()
                if source_path.exists()
                else str(source_path),
                f"{RAW_SCHEMA}.{spec.entity_name}",
                started_at,
                str(error)[:65535],
            ),
        )
    control_connection.commit()
