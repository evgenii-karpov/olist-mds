"""Durable orchestration for Phase 5 dbt micro-batches and publication."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from contextlib import suppress
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extensions import connection as PgConnection

ROOT = Path(__file__).resolve().parents[2]
DBT_PROJECT = ROOT / "dbt" / "olist_analytics"
PARITY_REPORTS = (
    "realtime_parity_report",
    "realtime_parity_checksums",
    "realtime_parity_grain_diffs",
)
DBT_UTILS_PARITY_TESTS = (
    "dbt_utils_equality_daily_revenue",
    "dbt_utils_equality_monthly_arpu",
)


def read_secret(value: str | None, file_value: str | None, default: str) -> str:
    if value:
        return value
    if file_value:
        return Path(file_value).read_text(encoding="utf-8").strip()
    return default


def connect(args: argparse.Namespace) -> PgConnection:
    password = read_secret(args.password, args.password_file, "olist")
    return psycopg2.connect(
        host=args.host,
        port=args.port,
        dbname=args.database,
        user=args.user,
        password=password,
        connect_timeout=10,
    )


def bootstrap(connection: PgConnection) -> None:
    sql = (ROOT / "infra/postgres/007_create_cdc_transform_audit.sql").read_text(
        encoding="utf-8"
    )
    with connection.cursor() as cursor:
        cursor.execute(sql)
    connection.commit()


def prepare(connection: PgConnection, args: argparse.Namespace) -> dict[str, Any]:
    bootstrap(connection)
    with connection, connection.cursor() as cursor:
        cursor.execute(
            "select pg_advisory_xact_lock(hashtext('olist_cdc_transform_prepare'))"
        )
        cursor.execute(
            """
            select status
            from cdc_audit.cdc_transform_runs
            where transform_run_id = %s
            for update
            """,
            (args.transform_run_id,),
        )
        existing = cursor.fetchone()
        if existing is not None and existing[0] == "SUCCEEDED":
            raise ValueError("a SUCCEEDED transform run cannot be reopened")
        cursor.execute(
            """
                insert into cdc_audit.cdc_transform_runs (
                    transform_run_id, dag_id, orchestration_run_id, status
                ) values (%s, %s, %s, 'STARTED')
                on conflict (transform_run_id) do update set
                    status = 'STARTED',
                    failure_summary = null,
                    finished_at = null,
                    dbt_completed_at = null
                """,
            (args.transform_run_id, args.dag_id, args.orchestration_run_id),
        )
        cursor.execute(
            """
                select count(*)
                from cdc_audit.cdc_transform_run_files
                where transform_run_id = %s
                """,
            (args.transform_run_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise ValueError("failed to read existing transform membership")
        existing_count = int(row[0])
        if existing_count == 0:
            cursor.execute(
                """
                    insert into cdc_audit.cdc_transform_run_files (
                        transform_run_id, manifest_uri
                    )
                    select %s, files.manifest_uri
                    from cdc_audit.cdc_files as files
                    where
                        files.status = 'LOADED'
                        and not exists (
                            select 1
                            from cdc_audit.cdc_transform_run_files as processed_files
                            where
                                processed_files.manifest_uri = files.manifest_uri
                        )
                    """,
                (args.transform_run_id,),
            )
        cursor.execute(
            """
                select count(*), coalesce(sum(files.manifest_row_count), 0)
                from cdc_audit.cdc_transform_run_files as run_files
                inner join cdc_audit.cdc_files as files using (manifest_uri)
                where run_files.transform_run_id = %s
                """,
            (args.transform_run_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise ValueError("failed to summarize transform membership")
        files_selected, events_selected = row
        cursor.execute(
            """
                update cdc_audit.cdc_transform_runs
                set files_selected = %s, events_selected = %s
                where transform_run_id = %s
                """,
            (files_selected, events_selected, args.transform_run_id),
        )
    return {
        "transform_run_id": args.transform_run_id,
        "files_selected": int(files_selected),
        "events_selected": int(events_selected),
    }


def run_dbt(
    arguments: list[str], *, check: bool = True, capture_output: bool = False
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [os.environ.get("DBT_BIN", "dbt"), *arguments],
        cwd=DBT_PROJECT,
        check=False,
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.STDOUT if capture_output else None,
        text=True if capture_output else None,
    )
    if check and result.returncode != 0:
        if result.stdout:
            print(result.stdout, end="", file=sys.stderr, flush=True)
        raise subprocess.CalledProcessError(
            result.returncode,
            result.args,
            output=result.stdout,
        )
    return result


def read_dbt_utils_results() -> list[dict[str, Any]]:
    run_results_path = DBT_PROJECT / "target" / "run_results.json"
    if not run_results_path.exists():
        return [
            {
                "name": name,
                "status": "ERROR",
                "message": "dbt did not produce target/run_results.json",
            }
            for name in DBT_UTILS_PARITY_TESTS
        ]

    payload = json.loads(run_results_path.read_text(encoding="utf-8"))
    results = payload.get("results", [])
    by_name: dict[str, dict[str, Any]] = {}
    for item in results:
        if not isinstance(item, dict) or not str(item.get("unique_id", "")).startswith(
            "test."
        ):
            continue
        unique_id = str(item.get("unique_id", ""))
        item_name = str(item.get("name", ""))
        for expected_name in DBT_UTILS_PARITY_TESTS:
            if item_name == expected_name or f".{expected_name}." in unique_id:
                by_name[expected_name] = item
    parsed: list[dict[str, Any]] = []
    for name in DBT_UTILS_PARITY_TESTS:
        item = by_name.get(name)
        if item is None:
            parsed.append(
                {
                    "name": name,
                    "status": "ERROR",
                    "message": "test was not present in dbt run results",
                }
            )
            continue
        parsed.append(
            {
                "name": name,
                "status": str(item.get("status", "ERROR")).upper(),
                "failures": item.get("failures"),
                "message": str(item.get("message", ""))[:1000],
            }
        )
    return parsed


def dbt_utils_error_results(message: str) -> list[dict[str, Any]]:
    return [
        {"name": name, "status": "ERROR", "message": message[:1000]}
        for name in DBT_UTILS_PARITY_TESTS
    ]


def read_custom_parity_results(
    connection: PgConnection,
) -> tuple[dict[str, list[dict[str, str]]], list[str]]:
    results: dict[str, list[dict[str, str]]] = {}
    failed_metrics: list[str] = []
    try:
        with connection.cursor() as cursor:
            for report in PARITY_REPORTS:
                if report == "realtime_parity_grain_diffs":
                    cursor.execute(
                        """
                        select metric_name, grain_key
                        from cdc_audit.realtime_parity_grain_diffs
                        order by metric_name, grain_key
                        limit 1000
                        """
                    )
                    rows = [
                        {"metric_name": str(metric), "grain_key": str(grain)}
                        for metric, grain in cursor.fetchall()
                    ]
                    results[report] = rows
                    failed_metrics.extend(f"{metric}:{grain}" for metric, grain in rows)
                    continue

                cursor.execute(
                    f"""
                    select metric_name, status
                    from cdc_audit.{report}
                    where status <> 'PASS'
                    order by metric_name
                    limit 1000
                    """
                )
                rows = [
                    {"metric_name": str(metric), "status": str(status)}
                    for metric, status in cursor.fetchall()
                ]
                results[report] = rows
                failed_metrics.extend(str(row["metric_name"]) for row in rows)
    except Exception:
        connection.rollback()
        raise
    return results, failed_metrics


def parity_status(
    *,
    custom_failed_metric_count: int,
    failed_dbt_utils_tests: list[str],
    dbt_exit_code: int,
) -> str:
    return (
        "PASS"
        if (
            dbt_exit_code == 0
            and custom_failed_metric_count == 0
            and not failed_dbt_utils_tests
        )
        else "FAIL"
    )


def record_parity(connection: PgConnection, args: argparse.Namespace) -> dict[str, Any]:
    bootstrap(connection)
    with connection, connection.cursor() as cursor:
        cursor.execute(
            """
            update cdc_audit.cdc_publication_state
            set parity_status = 'PENDING', updated_at = clock_timestamp()
            where publication_name = 'olist_marts'
            """
        )

    run_results_path = DBT_PROJECT / "target" / "run_results.json"
    with suppress(FileNotFoundError):
        run_results_path.unlink()
    dbt_arguments = ["build", "--selector", "realtime_parity"]
    try:
        dbt_result = run_dbt(
            dbt_arguments,
            check=False,
            capture_output=True,
        )
    except OSError as exc:
        dbt_result = subprocess.CompletedProcess(
            [os.environ.get("DBT_BIN", "dbt"), *dbt_arguments],
            1,
            stdout=f"Unable to execute dbt parity build: {exc}",
        )
    try:
        dbt_utils_results = read_dbt_utils_results()
    except (OSError, TypeError, ValueError) as exc:
        dbt_utils_results = dbt_utils_error_results(
            f"Unable to read dbt parity results: {exc}"
        )
    failed_dbt_utils_tests = [
        str(item["name"]) for item in dbt_utils_results if item.get("status") != "PASS"
    ]

    custom_results: dict[str, list[dict[str, str]]]
    custom_failed_metrics: list[str]
    try:
        custom_results, custom_failed_metrics = read_custom_parity_results(connection)
    except Exception as exc:
        custom_results = {
            report: [
                {
                    "metric_name": "parity_relation_unavailable",
                    "status": "ERROR",
                }
            ]
            for report in PARITY_REPORTS
        }
        custom_failed_metrics = [f"parity_relation_unavailable: {exc}"]

    custom_failed_metric_count = len(custom_failed_metrics)
    status = parity_status(
        custom_failed_metric_count=custom_failed_metric_count,
        failed_dbt_utils_tests=failed_dbt_utils_tests,
        dbt_exit_code=dbt_result.returncode,
    )
    with connection, connection.cursor() as cursor:
        cursor.execute(
            """
            update cdc_audit.cdc_publication_state
            set parity_status = %s, updated_at = clock_timestamp()
            where publication_name = 'olist_marts'
            """,
            (status,),
        )

    output_tail = str(dbt_result.stdout or "")[-4000:]
    if output_tail and dbt_result.returncode != 0:
        print(output_tail, end="", file=sys.stderr, flush=True)
    return {
        "parity_status": status,
        "failed_metrics": custom_failed_metric_count,
        "custom_failed_metric_count": custom_failed_metric_count,
        "custom_failed_metrics": custom_failed_metrics[:1000],
        "custom_results": custom_results,
        "dbt_utils_tests": dbt_utils_results,
        "failed_dbt_utils_tests": failed_dbt_utils_tests,
        "dbt_exit_code": dbt_result.returncode,
        "dbt_output_tail": output_tail,
    }


def build(connection: PgConnection, args: argparse.Namespace) -> dict[str, Any]:
    with connection.cursor() as cursor:
        cursor.execute("select pg_advisory_lock(hashtext('olist_cdc_transform_build'))")
    try:
        with connection, connection.cursor() as cursor:
            cursor.execute(
                """
                update cdc_audit.cdc_transform_runs
                set status = 'STARTED', failure_summary = null,
                    finished_at = null, dbt_completed_at = null
                where transform_run_id = %s and status = 'FAILED'
                returning transform_run_id
                """,
                (args.transform_run_id,),
            )
            resumed = cursor.fetchone()
            if resumed is None:
                cursor.execute(
                    """
                    select status
                    from cdc_audit.cdc_transform_runs
                    where transform_run_id = %s
                    """,
                    (args.transform_run_id,),
                )
                row = cursor.fetchone()
                if row is None or row[0] != "STARTED":
                    raise ValueError("transform run is missing or cannot be built")
        variables = json.dumps({"cdc_transform_run_id": args.transform_run_id})
        run_dbt(
            [
                "build",
                "--selector",
                "realtime_transform",
                "--vars",
                variables,
                "--exclude-resource-type",
                "unit_test",
                "--quiet",
                "--warn-error-options",
                json.dumps({"error": ["NoNodesForSelectionCriteria"]}),
            ]
        )
        with connection, connection.cursor() as cursor:
            cursor.execute(
                """
                update cdc_audit.cdc_transform_runs
                set dbt_completed_at = clock_timestamp()
                where transform_run_id = %s and status = 'STARTED'
                returning transform_run_id
                """,
                (args.transform_run_id,),
            )
            if cursor.fetchone() is None:
                raise ValueError("transform run is missing or is not STARTED")
    finally:
        with connection.cursor() as cursor:
            cursor.execute(
                "select pg_advisory_unlock(hashtext('olist_cdc_transform_build'))"
            )
    return {"transform_run_id": args.transform_run_id, "dbt_status": "success"}


def finish(connection: PgConnection, args: argparse.Namespace) -> dict[str, Any]:
    with connection, connection.cursor() as cursor:
        cursor.execute(
            """
                update cdc_audit.cdc_transform_runs
                set status = 'SUCCEEDED', finished_at = clock_timestamp()
                where
                    transform_run_id = %s
                    and status = 'STARTED'
                    and dbt_completed_at is not null
                returning transform_run_id
                """,
            (args.transform_run_id,),
        )
        if cursor.fetchone() is None:
            raise ValueError(
                "transform run is missing, not STARTED, or dbt did not complete"
            )
        cursor.execute(
            """
            update cdc_audit.cdc_publication_state
            set parity_status = 'PENDING', updated_at = clock_timestamp()
            where publication_name = 'olist_marts'
            """
        )
        cursor.execute(
            """
            select max(files.source_ts_max)
            from cdc_audit.cdc_transform_run_files as run_files
            inner join cdc_audit.cdc_files as files using (manifest_uri)
            where run_files.transform_run_id = %s
            """,
            (args.transform_run_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise ValueError("failed to read transform source horizon")
        max_source_ts = row[0]
        for model_name in (
            "mart_daily_revenue_realtime",
            "mart_monthly_arpu_realtime",
        ):
            cursor.execute(
                """
                    insert into cdc_audit.cdc_mart_freshness (
                        model_name, max_source_ts, build_time, latency_seconds,
                        build_run_id
                    ) values (
                        %s, %s, clock_timestamp(),
                        extract(epoch from clock_timestamp() - %s), %s
                    )
                    on conflict (model_name) do update set
                        max_source_ts = coalesce(
                            greatest(
                                cdc_audit.cdc_mart_freshness.max_source_ts,
                                excluded.max_source_ts
                            ),
                            cdc_audit.cdc_mart_freshness.max_source_ts,
                            excluded.max_source_ts
                        ),
                        build_time = excluded.build_time,
                        latency_seconds = extract(
                            epoch from excluded.build_time - coalesce(
                                greatest(
                                    cdc_audit.cdc_mart_freshness.max_source_ts,
                                    excluded.max_source_ts
                                ),
                                cdc_audit.cdc_mart_freshness.max_source_ts,
                                excluded.max_source_ts
                            )
                        ),
                        build_run_id = excluded.build_run_id
                    """,
                (model_name, max_source_ts, max_source_ts, args.transform_run_id),
            )
    return {"transform_run_id": args.transform_run_id, "status": "SUCCEEDED"}


def fail(connection: PgConnection, args: argparse.Namespace) -> dict[str, Any]:
    bootstrap(connection)
    with connection, connection.cursor() as cursor:
        cursor.execute(
            """
                update cdc_audit.cdc_transform_runs
                set status = 'FAILED', finished_at = clock_timestamp(),
                    failure_summary = %s
                where transform_run_id = %s
                """,
            (args.failure_summary[:65535], args.transform_run_id),
        )
    return {"transform_run_id": args.transform_run_id, "status": "FAILED"}


def quality(args: argparse.Namespace) -> dict[str, Any]:
    run_dbt(
        [
            "test",
            "--selector",
            "realtime_quality",
            "--quiet",
            "--warn-error-options",
            json.dumps({"error": ["NoNodesForSelectionCriteria"]}),
        ]
    )
    if args.full:
        run_dbt(["test", "--selector", "realtime_transform"])
        target = os.environ.get("DBT_TARGET", "local_pg")
        subprocess.run(
            [
                os.environ.get("EDR_BIN", "edr"),
                "report",
                "--env",
                "prod",
                "--profiles-dir",
                ".",
                "--profile-target",
                target,
                "--target-path",
                "target/edr",
                "--file-path",
                "target/edr/realtime.html",
                "--open-browser",
                "false",
            ],
            cwd=DBT_PROJECT,
            check=True,
        )
    return {"quality_status": "success", "full": bool(args.full)}


def publish(connection: PgConnection, args: argparse.Namespace) -> dict[str, Any]:
    bootstrap(connection)
    with connection, connection.cursor() as cursor:
        cursor.execute(
            """
                select parity_status
                from cdc_audit.cdc_publication_state
                where publication_name = 'olist_marts'
                for update
                """
        )
        row = cursor.fetchone()
        if row is None:
            raise ValueError("publication state is missing")
        parity_status = row[0]
        if args.target == "realtime" and parity_status != "PASS":
            raise ValueError("realtime publication requires recorded parity PASS")
        targets = {
            "batch": ("marts.mart_daily_revenue", "marts.mart_monthly_arpu"),
            "realtime": (
                "realtime_marts.mart_daily_revenue_realtime",
                "realtime_marts.mart_monthly_arpu_realtime",
            ),
        }
        daily, monthly = targets[args.target]
        cursor.execute(
            f"""
            create or replace view analytics.mart_daily_revenue as
            select
                order_purchase_date, gross_revenue,
                allocated_payment_revenue, product_revenue, freight_revenue,
                orders_count, customers_count, items_count,
                average_order_value, average_paid_order_value,
                average_delivery_days, late_deliveries_count
            from {daily}
            """
        )
        cursor.execute(
            f"""
            create or replace view analytics.mart_monthly_arpu as
            select
                order_month, active_customers, total_revenue, arpu,
                orders_count, orders_per_customer, average_order_value,
                repeat_customer_rate
            from {monthly}
            """
        )
        cursor.execute(
            """
                update cdc_audit.cdc_publication_state
                set target_path = %s, approved_by = %s,
                    approved_at = clock_timestamp(), updated_at = clock_timestamp()
                where publication_name = 'olist_marts'
                """,
            (args.target, args.approved_by),
        )
    return {"publication": "olist_marts", "target": args.target}


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("--host", default=os.environ.get("POSTGRES_HOST", "localhost"))
    value.add_argument(
        "--port", type=int, default=int(os.environ.get("POSTGRES_PORT", "5432"))
    )
    value.add_argument(
        "--database", default=os.environ.get("POSTGRES_DB", "olist_analytics")
    )
    value.add_argument("--user", default=os.environ.get("POSTGRES_USER", "olist"))
    value.add_argument("--password", default=os.environ.get("POSTGRES_PASSWORD"))
    value.add_argument(
        "--password-file", default=os.environ.get("POSTGRES_PASSWORD_FILE")
    )
    commands = value.add_subparsers(dest="command", required=True)
    for name in ("prepare", "finish", "fail"):
        command = commands.add_parser(name)
        command.add_argument("--transform-run-id", required=True)
        if name == "prepare":
            command.add_argument("--dag-id")
            command.add_argument("--orchestration-run-id")
        if name == "fail":
            command.add_argument("--failure-summary", required=True)
    build_command = commands.add_parser("build")
    build_command.add_argument("--transform-run-id", required=True)
    quality_command = commands.add_parser("quality")
    quality_command.add_argument("--full", action="store_true")
    publish_command = commands.add_parser("publish")
    publish_command.add_argument(
        "--target", choices=("batch", "realtime"), required=True
    )
    publish_command.add_argument("--approved-by", required=True)
    commands.add_parser("record-parity")
    return value


def main() -> None:
    args = parser().parse_args()
    if args.command == "quality":
        result = quality(args)
    else:
        connection = connect(args)
        try:
            result = {
                "prepare": prepare,
                "build": build,
                "finish": finish,
                "fail": fail,
                "publish": publish,
                "record-parity": record_parity,
            }[args.command](connection, args)
        finally:
            connection.close()
    print(json.dumps(result, default=str, sort_keys=True))
    if args.command == "record-parity" and result.get("parity_status") != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
