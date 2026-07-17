"""Trigger the local Airflow DAG twice on the small fixture and compare outputs."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from psycopg2.extensions import connection as PgConnection

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.ci.pipeline_helpers import (
    RelationFingerprint,
    capture_fingerprints,
    fetch_one,
    pipeline_env,
    postgres_connection,
)
from scripts.ci.pipeline_helpers import (
    wait_for_dag_success as wait_for_dag_success_helper,
)

DEFAULT_ARCHIVE = (
    PROJECT_ROOT / "tests" / "fixtures" / "olist_small" / "olist_small.zip"
)
DEFAULT_PROFILE = (
    PROJECT_ROOT / "tests" / "fixtures" / "olist_small" / "source_profile_small.json"
)
DEFAULT_RAW_DIR = PROJECT_ROOT / "data" / "ci" / "raw" / "olist_small"
DEFAULT_FIXTURE_BATCH_DATE = "2018-09-01"
POSTGRES_SQL_DIR = PROJECT_ROOT / "infra" / "postgres"
RESET_SCHEMAS = (
    "raw_data",
    "audit",
    "staging",
    "intermediate",
    "snapshots",
    "core",
    "marts",
)
VOLATILE_RAW_COLUMNS = {"_loaded_at"}
AIRFLOW_LOG_DIR = Path(
    os.environ.get("AIRFLOW__LOGGING__BASE_LOG_FOLDER", "/opt/airflow/logs")
)


@dataclass(frozen=True)
class RawFileFingerprint:
    row_count: int
    checksum: str


def airflow_dags_folder() -> Path:
    configured_folder = os.environ.get("AIRFLOW__CORE__DAGS_FOLDER")
    if configured_folder:
        return Path(configured_folder)
    return Path("/opt/airflow/dags")


def local_dag_file() -> Path:
    configured_file = os.environ.get("OLIST_LOCAL_DAG_FILE")
    if configured_file:
        return Path(configured_file)
    return airflow_dags_folder() / "olist_modern_data_stack_local.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", default=str(DEFAULT_ARCHIVE))
    parser.add_argument("--profile", default=str(DEFAULT_PROFILE))
    parser.add_argument("--raw-dir", default=str(DEFAULT_RAW_DIR))
    parser.add_argument("--batch-date", default=DEFAULT_FIXTURE_BATCH_DATE)
    parser.add_argument("--batch-id", default=DEFAULT_FIXTURE_BATCH_DATE)
    parser.add_argument("--initial-run-id")
    parser.add_argument("--replay-run-id")
    parser.add_argument("--dag-id", default="olist_modern_data_stack_local")
    parser.add_argument("--lookback-days", type=int, default=3)
    parser.add_argument("--dead-letter-max-rows", type=int, default=0)
    parser.add_argument("--dead-letter-max-rate", type=float, default=0)
    parser.add_argument("--dbt-threads", type=int, default=1)
    parser.add_argument("--dag-registration-timeout-seconds", type=int, default=180)
    parser.add_argument("--dag-registration-poll-seconds", type=int, default=5)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--poll-seconds", type=int, default=5)
    return parser.parse_args()


def reset_warehouse(env: dict[str, str]) -> None:
    connection = postgres_connection(env)
    try:
        with connection.cursor() as cursor:
            for schema in RESET_SCHEMAS:
                cursor.execute(f"drop schema if exists {schema} cascade;")
        connection.commit()
    finally:
        connection.close()


def clean_raw_dir(raw_dir: Path) -> None:
    resolved_raw_dir = raw_dir.resolve()
    project_root = PROJECT_ROOT.resolve()
    if not resolved_raw_dir.is_relative_to(project_root):
        raise ValueError(f"Refusing to delete raw dir outside project: {raw_dir}")
    if resolved_raw_dir.exists():
        shutil.rmtree(resolved_raw_dir)


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    print(f"+ {' '.join(command)}", flush=True)
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0:
        print(result.stdout, end="", flush=True)
        raise subprocess.CalledProcessError(
            result.returncode,
            command,
            output=result.stdout,
        )
    return result


def run_streaming_command(command: list[str]) -> None:
    print(f"+ {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def print_airflow_diagnostics() -> None:
    dags_folder = airflow_dags_folder()
    diagnostics = [
        ["airflow", "config", "get-value", "core", "dags_folder"],
        [
            "python",
            "-c",
            (
                "from pathlib import Path; "
                f"print(sorted(str(p) for p in Path({str(dags_folder)!r}).glob('*.py')))"
            ),
        ],
        ["airflow", "dags", "list-import-errors"],
        ["airflow", "dags", "list"],
    ]
    for command in diagnostics:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        print(f"+ {' '.join(command)}", flush=True)
        print(result.stdout, end="", flush=True)


def wait_for_dag_registration(args: argparse.Namespace) -> None:
    deadline = time.monotonic() + args.dag_registration_timeout_seconds
    last_output = ""
    reserialize = subprocess.run(
        ["airflow", "dags", "reserialize"],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if reserialize.returncode != 0:
        last_output = reserialize.stdout
        print(last_output, end="", flush=True)

    while time.monotonic() < deadline:
        result = subprocess.run(
            ["airflow", "dags", "list"],
            cwd=PROJECT_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        last_output = result.stdout
        if result.returncode == 0 and args.dag_id in result.stdout:
            print(f"DAG {args.dag_id} is registered in Airflow", flush=True)
            return

        print(f"Waiting for DAG {args.dag_id} to be registered", flush=True)
        time.sleep(args.dag_registration_poll_seconds)

    print(last_output, end="", flush=True)
    print_airflow_diagnostics()
    raise TimeoutError(
        "Timed out after "
        f"{args.dag_registration_timeout_seconds}s waiting for DAG {args.dag_id}"
    )


def dag_conf(args: argparse.Namespace, *, full_refresh: bool) -> dict[str, Any]:
    return {
        "batch_date": args.batch_date,
        "lookback_days": args.lookback_days,
        "full_refresh": full_refresh,
        "source_archive": args.archive,
        "source_profile": args.profile,
        "raw_dir": args.raw_dir,
        "dead_letter_max_rows": args.dead_letter_max_rows,
        "dead_letter_max_rate": args.dead_letter_max_rate,
    }


def print_log_tail(path: Path, line_count: int = 200) -> None:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        print(f"Could not read {path}: {exc}", flush=True)
        return

    print(f"--- {path} last {line_count} lines ---", flush=True)
    for line in lines[-line_count:]:
        print(line, flush=True)


def print_failed_task_logs(dag_id: str, run_id: str, task_ids: Sequence[str]) -> None:
    for task_id in task_ids:
        log_dir = AIRFLOW_LOG_DIR / f"dag_id={dag_id}" / f"run_id={run_id}"
        candidates = sorted((log_dir / f"task_id={task_id}").glob("*.log")) + sorted(
            log_dir.glob(f"**/task_id={task_id}/**/*.log")
        )
        if not candidates:
            print(
                f"No local log files found for task {task_id} under {log_dir}",
                flush=True,
            )
            continue
        for path in candidates:
            print_log_tail(path)


def trigger_dag(args: argparse.Namespace, *, run_id: str, full_refresh: bool) -> None:
    wait_for_dag_registration(args)
    try:
        unpause = run_command(["airflow", "dags", "unpause", args.dag_id])
        print(unpause.stdout, end="", flush=True)
    except subprocess.CalledProcessError as exc:
        print(exc.stdout, end="", flush=True)
        raise

    conf = json.dumps(dag_conf(args, full_refresh=full_refresh), sort_keys=True)
    result = run_command(
        [
            "airflow",
            "dags",
            "trigger",
            args.dag_id,
            "--run-id",
            run_id,
            "--conf",
            conf,
        ]
    )
    print(result.stdout, end="", flush=True)


def dag_test_logical_date(offset_seconds: int) -> str:
    logical_date = datetime.now(UTC).replace(microsecond=0) + timedelta(
        seconds=offset_seconds
    )
    return logical_date.isoformat()


def run_dag_test(
    args: argparse.Namespace,
    *,
    full_refresh: bool,
    offset_seconds: int,
) -> None:
    wait_for_dag_registration(args)
    conf = json.dumps(dag_conf(args, full_refresh=full_refresh), sort_keys=True)
    run_streaming_command(
        [
            "airflow",
            "dags",
            "test",
            args.dag_id,
            dag_test_logical_date(offset_seconds),
            "--conf",
            conf,
            "--dagfile-path",
            str(local_dag_file()),
        ]
    )


def wait_for_dag_success(args: argparse.Namespace, *, run_id: str) -> None:
    wait_for_dag_success_helper(
        args.dag_id,
        run_id,
        timeout_seconds=args.timeout_seconds,
        poll_seconds=args.poll_seconds,
        on_state=lambda state: print(f"DAG run {run_id} state: {state}", flush=True),
        on_failure=lambda failed_tasks: print_failed_task_logs(
            args.dag_id,
            run_id,
            [task_id for task_id, _ in failed_tasks],
        ),
    )


def normalized_raw_path(path: Path, raw_dir: Path) -> str:
    parts = path.relative_to(raw_dir).parts
    return "/".join(part for part in parts if not part.startswith("run_id="))


def raw_row_fingerprint(row: dict[str, str]) -> str:
    normalized_items = [
        (key, value)
        for key, value in sorted(row.items())
        if key not in VOLATILE_RAW_COLUMNS
    ]
    payload = json.dumps(normalized_items, sort_keys=True, separators=(",", ":"))
    return hashlib.md5(payload.encode("utf-8")).hexdigest()


def raw_file_fingerprint(path: Path) -> RawFileFingerprint:
    row_hashes = []
    with gzip.open(path, mode="rt", encoding="utf-8", newline="") as raw_file:
        reader = csv.DictReader(raw_file)
        for row in reader:
            row_hashes.append(raw_row_fingerprint(row))
    checksum = hashlib.md5("|".join(sorted(row_hashes)).encode("utf-8")).hexdigest()
    return RawFileFingerprint(row_count=len(row_hashes), checksum=checksum)


def capture_raw_file_fingerprints(raw_dir: Path) -> dict[str, RawFileFingerprint]:
    return {
        normalized_raw_path(path, raw_dir): raw_file_fingerprint(path)
        for path in sorted(raw_dir.rglob("*.csv.gz"))
    }


def assert_fact_matches_staging(connection: PgConnection) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            with expected_items as (
                select
                    md5(
                        order_items.order_id || '|'
                        || order_items.order_item_id::varchar
                    ) as order_item_key
                from staging.stg_olist__order_items as order_items
                inner join staging.stg_olist__orders as orders
                    on order_items.order_id = orders.order_id
            ),

            actual_items as (
                select order_item_key
                from core.fact_order_items
            ),

            missing_from_fact as (
                select count(*) as row_count
                from expected_items
                left join actual_items
                    on expected_items.order_item_key = actual_items.order_item_key
                where actual_items.order_item_key is null
            ),

            unexpected_fact_rows as (
                select count(*) as row_count
                from actual_items
                left join expected_items
                    on actual_items.order_item_key = expected_items.order_item_key
                where expected_items.order_item_key is null
            )

            select
                missing_from_fact.row_count,
                unexpected_fact_rows.row_count
            from missing_from_fact
            cross join unexpected_fact_rows;
            """
        )
        missing_rows, unexpected_rows = fetch_one(cursor)

    if missing_rows or unexpected_rows:
        raise AssertionError(
            "fact_order_items does not match the current staging grain: "
            f"missing_from_fact={missing_rows}, "
            f"unexpected_fact_rows={unexpected_rows}"
        )


def assert_no_orphan_fact_keys(connection: PgConnection) -> None:
    orphan_queries = {
        "customer_key": """
            select count(*)
            from core.fact_order_items as fact
            left join core.dim_customer_scd2 as dim
                on fact.customer_key = dim.customer_key
            where dim.customer_key is null
        """,
        "product_key": """
            select count(*)
            from core.fact_order_items as fact
            left join core.dim_product_scd2 as dim
                on fact.product_key = dim.product_key
            where dim.product_key is null
        """,
        "seller_key": """
            select count(*)
            from core.fact_order_items as fact
            left join core.dim_seller as dim
                on fact.seller_key = dim.seller_key
            where dim.seller_key is null
        """,
    }
    failures = {}
    with connection.cursor() as cursor:
        for key_name, query in orphan_queries.items():
            cursor.execute(query)
            orphan_count = int(fetch_one(cursor)[0])
            if orphan_count:
                failures[key_name] = orphan_count

    if failures:
        raise AssertionError(f"fact_order_items has orphan dimension keys: {failures}")


def assert_output_contracts(connection: PgConnection) -> None:
    assert_fact_matches_staging(connection)
    assert_no_orphan_fact_keys(connection)


def assert_replay_matches_initial(
    initial: dict[str, RelationFingerprint],
    replay: dict[str, RelationFingerprint],
) -> None:
    mismatches = {}
    for relation_name, initial_fingerprint in initial.items():
        replay_fingerprint = replay[relation_name]
        if initial_fingerprint != replay_fingerprint:
            mismatches[relation_name] = {
                "initial": initial_fingerprint.__dict__,
                "replay": replay_fingerprint.__dict__,
            }

    if mismatches:
        formatted = json.dumps(mismatches, indent=2, sort_keys=True)
        raise AssertionError(f"Fixture replay changed analytical outputs:\n{formatted}")


def assert_raw_files_match_initial(
    initial: dict[str, RawFileFingerprint],
    replay: dict[str, RawFileFingerprint],
) -> None:
    if initial == replay:
        return

    all_paths = sorted(set(initial) | set(replay))
    mismatches = {}
    for path in all_paths:
        if initial.get(path) != replay.get(path):
            mismatches[path] = {
                "initial": None if path not in initial else initial[path].__dict__,
                "replay": None if path not in replay else replay[path].__dict__,
            }

    formatted = json.dumps(mismatches, indent=2, sort_keys=True)
    raise AssertionError(f"Fixture replay changed raw file outputs:\n{formatted}")


def print_fingerprints(
    label: str,
    fingerprints: dict[str, RelationFingerprint],
) -> None:
    print(f"{label} analytical fingerprints:", flush=True)
    for relation_name, fingerprint in fingerprints.items():
        print(
            f"- {relation_name}: rows={fingerprint.row_count}, "
            f"checksum={fingerprint.checksum}",
            flush=True,
        )


def print_raw_fingerprints(
    label: str,
    fingerprints: dict[str, RawFileFingerprint],
) -> None:
    print(f"{label} raw file fingerprints:", flush=True)
    for path, fingerprint in fingerprints.items():
        print(
            f"- {path}: rows={fingerprint.row_count}, checksum={fingerprint.checksum}",
            flush=True,
        )


def main() -> None:
    args = parse_args()
    env = pipeline_env()
    raw_dir = Path(args.raw_dir)
    run_id_suffix = str(int(time.time()))
    args.initial_run_id = args.initial_run_id or f"ci_fixture_initial_{run_id_suffix}"
    args.replay_run_id = args.replay_run_id or f"ci_fixture_replay_{run_id_suffix}"

    print("Resetting warehouse for initial fixture DAG run", flush=True)
    clean_raw_dir(raw_dir)
    reset_warehouse(env)

    print("Running initial fixture DAG test", flush=True)
    run_dag_test(args, full_refresh=True, offset_seconds=0)

    initial_raw_fingerprints = capture_raw_file_fingerprints(raw_dir)
    print_raw_fingerprints("Initial", initial_raw_fingerprints)
    with postgres_connection(env) as connection:
        assert_output_contracts(connection)
        initial_fingerprints = capture_fingerprints(connection)
    print_fingerprints("Initial", initial_fingerprints)

    print("Running replay fixture DAG test", flush=True)
    run_dag_test(args, full_refresh=False, offset_seconds=1)

    replay_raw_fingerprints = capture_raw_file_fingerprints(raw_dir)
    print_raw_fingerprints("Replay", replay_raw_fingerprints)
    with postgres_connection(env) as connection:
        assert_output_contracts(connection)
        replay_fingerprints = capture_fingerprints(connection)
    print_fingerprints("Replay", replay_fingerprints)

    assert_raw_files_match_initial(initial_raw_fingerprints, replay_raw_fingerprints)
    assert_replay_matches_initial(initial_fingerprints, replay_fingerprints)
    print("Fixture replay is idempotent", flush=True)


if __name__ == "__main__":
    main()
