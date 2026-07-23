#!/usr/bin/env python3
"""Expose low-cardinality Phase 4 pipeline metrics from read-only audit queries."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import clickhouse_connect
import psycopg2
from scripts.cdc.warehouse_ingest import BUSINESS_COLUMNS, read_secret

LATENCY_BUCKETS = (15, 30, 60, 120, 180, 300, 600, 1800)


def labels(**values: str) -> str:
    rendered = ",".join(
        f'{key}="{value.replace(chr(92), chr(92) * 2).replace(chr(34), chr(92) + chr(34))}"'
        for key, value in values.items()
    )
    return "{" + rendered + "}"


def timestamp_seconds(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.timestamp()
    if isinstance(value, int | float | str):
        return float(value)
    raise TypeError(f"Unsupported timestamp value type: {type(value).__name__}")


def render_raw_metrics_postgres(connection_factory) -> list[str]:
    lines: list[str] = []
    with connection_factory() as connection:
        connection.set_session(readonly=True, autocommit=False)
        with connection.cursor() as cursor:
            for table in BUSINESS_COLUMNS:
                cursor.execute(
                    f"""
                    select _op, count(*),
                           extract(epoch from max(_source_ts)),
                           extract(epoch from clock_timestamp() - max(_source_ts))
                    from raw_cdc.{table} group by _op
                    """
                )
                for operation, count, source_timestamp, age in cursor.fetchall():
                    lines.append(
                        "olist_cdc_raw_events_total"
                        f"{labels(environment='local', table=table, operation=str(operation))} {count}"
                    )
                    if source_timestamp is not None:
                        lines.append(
                            "olist_cdc_raw_max_source_timestamp_seconds"
                            f"{labels(environment='local', table=table)} {source_timestamp}"
                        )
                        lines.append(
                            "olist_cdc_raw_freshness_seconds"
                            f"{labels(environment='local', table=table)} {age}"
                        )
    return lines


def render_raw_metrics_clickhouse(client_factory) -> list[str]:
    lines: list[str] = []
    client = client_factory()
    try:
        for table in BUSINESS_COLUMNS:
            rows = client.query(
                f"""
                SELECT _op, count(), max(_source_ts),
                       dateDiff('second', max(_source_ts), now64(6, 'UTC'))
                FROM raw_cdc.`{table}` FINAL
                GROUP BY _op
                """
            ).result_rows
            max_timestamp = None
            freshness = None
            for operation, count, source_timestamp, age in rows:
                lines.append(
                    "olist_cdc_raw_events_total"
                    f"{labels(environment='local', table=table, operation=str(operation))} {count}"
                )
                source_seconds = timestamp_seconds(source_timestamp)
                if source_seconds is not None and (
                    max_timestamp is None or source_seconds > max_timestamp
                ):
                    max_timestamp = source_seconds
                    freshness = age
            if max_timestamp is not None:
                lines.append(
                    "olist_cdc_raw_max_source_timestamp_seconds"
                    f"{labels(environment='local', table=table)} {max_timestamp}"
                )
                lines.append(
                    "olist_cdc_raw_freshness_seconds"
                    f"{labels(environment='local', table=table)} {freshness}"
                )
    finally:
        client.close()
    return lines


def transform_finish_by_object(cursor) -> dict[str, datetime]:
    cursor.execute(
        """
        select f.object_uri, min(t.finished_at)
        from cdc_audit.cdc_files f
        join cdc_audit.cdc_transform_run_files rf
          on rf.manifest_uri = f.manifest_uri
        join cdc_audit.cdc_transform_runs t
          on t.transform_run_id = rf.transform_run_id
         and t.status = 'SUCCEEDED'
        where t.finished_at >= clock_timestamp() - interval '10 minutes'
        group by f.object_uri
        """
    )
    return {
        str(object_uri): finished_at for object_uri, finished_at in cursor.fetchall()
    }


def raw_event_rows_postgres(connection_factory) -> list[tuple[str, datetime, str]]:
    rows: list[tuple[str, datetime, str]] = []
    with connection_factory() as connection:
        connection.set_session(readonly=True, autocommit=False)
        with connection.cursor() as cursor:
            for table in BUSINESS_COLUMNS:
                cursor.execute(
                    f"""
                    select _event_id, _source_ts, _source_object_uri
                    from raw_cdc.{table}
                    where _source_ts is not null
                    """
                )
                rows.extend(cursor.fetchall())
    return rows


def raw_event_rows_clickhouse(client_factory) -> list[tuple[str, datetime, str]]:
    rows: list[tuple[str, datetime, str]] = []
    client = client_factory()
    try:
        for table in BUSINESS_COLUMNS:
            rows.extend(
                client.query(
                    f"""
                    SELECT _event_id, _source_ts, _source_object_uri
                    FROM raw_cdc.`{table}` FINAL
                    WHERE _source_ts IS NOT NULL
                    """
                ).result_rows
            )
    finally:
        client.close()
    return rows


def render_event_latency_histogram(
    cursor,
    raw_connection_factory,
    warehouse_type: str,
) -> list[str]:
    """Render a rolling event-level histogram from immutable transform membership."""
    finished_by_object = transform_finish_by_object(cursor)
    if not finished_by_object:
        total_count = 0
        total_sum = 0.0
        bucket_counts = {bucket: 0 for bucket in LATENCY_BUCKETS}
    else:
        raw_rows = (
            raw_event_rows_clickhouse(raw_connection_factory)
            if warehouse_type == "clickhouse"
            else raw_event_rows_postgres(raw_connection_factory)
        )
        event_latencies: dict[str, float] = {}
        for event_id, source_ts, object_uri in raw_rows:
            finished_at = finished_by_object.get(str(object_uri))
            if finished_at is None:
                continue
            source_seconds = timestamp_seconds(source_ts)
            finished_seconds = timestamp_seconds(finished_at)
            if source_seconds is None or finished_seconds is None:
                continue
            latency = max(0.0, finished_seconds - source_seconds)
            current = event_latencies.get(str(event_id))
            if current is None or latency < current:
                event_latencies[str(event_id)] = latency
        bucket_counts = {
            bucket: sum(latency <= bucket for latency in event_latencies.values())
            for bucket in LATENCY_BUCKETS
        }
        total_count = len(event_latencies)
        total_sum = sum(event_latencies.values())
    result = [
        "olist_cdc_event_commit_to_mart_latency_seconds_bucket"
        f"{labels(environment='local', le=str(bucket))} {bucket_counts[bucket]}"
        for bucket in LATENCY_BUCKETS
    ]
    result.extend(
        [
            "olist_cdc_event_commit_to_mart_latency_seconds_bucket"
            f"{labels(environment='local', le='+Inf')} {total_count}",
            "olist_cdc_event_commit_to_mart_latency_seconds_count"
            f"{labels(environment='local')} {total_count}",
            "olist_cdc_event_commit_to_mart_latency_seconds_sum"
            f"{labels(environment='local')} {total_sum}",
        ]
    )
    return result


def render_metrics(
    control_connection_factory,
    raw_connection_factory,
    warehouse_type: str,
) -> bytes:
    lines = ["olist_cdc_pipeline_up 1"]
    try:
        if warehouse_type == "clickhouse":
            lines.extend(render_raw_metrics_clickhouse(raw_connection_factory))
        else:
            lines.extend(render_raw_metrics_postgres(raw_connection_factory))
        with control_connection_factory() as connection:
            connection.set_session(readonly=True, autocommit=False)
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    select source_table, status, count(*)
                    from cdc_audit.cdc_files group by source_table, status
                    """
                )
                for table, status, count in cursor.fetchall():
                    lines.append(
                        "olist_cdc_files"
                        f"{labels(environment='local', table=str(table), status=str(status))} {count}"
                    )
                cursor.execute(
                    """
                    select source_table, sum(duplicate_rows), sum(rejected_rows)
                    from cdc_audit.cdc_reconciliation group by source_table
                    """
                )
                for table, duplicates, rejected in cursor.fetchall():
                    metric_labels = labels(environment="local", table=str(table))
                    lines.append(
                        f"olist_cdc_duplicate_events_total{metric_labels} {duplicates or 0}"
                    )
                    lines.append(
                        f"olist_cdc_rejected_events_total{metric_labels} {rejected or 0}"
                    )
                cursor.execute(
                    """
                    select split_part(topic, '.', 3), sum(gap_count)
                    from cdc_audit.cdc_partition_watermarks
                    group by split_part(topic, '.', 3)
                    """
                )
                for table, count in cursor.fetchall():
                    lines.append(
                        "olist_cdc_offset_gaps"
                        f"{labels(environment='local', table=str(table))} {count or 0}"
                    )
                cursor.execute(
                    """
                    select split_part(topic, '.', 3), coverage_kind, count(*)
                    from cdc_audit.cdc_offset_coverage
                    group by split_part(topic, '.', 3), coverage_kind
                    """
                )
                for table, coverage_kind, count in cursor.fetchall():
                    lines.append(
                        "olist_cdc_offset_coverage_ranges"
                        f"{labels(environment='local', table=str(table), status=str(coverage_kind))} {count}"
                    )
                cursor.execute(
                    """
                    select split_part(topic, '.', 3), last_contiguous_offset,
                           last_loaded_event_offset
                    from cdc_audit.cdc_partition_watermarks
                    """
                )
                for table, contiguous, loaded in cursor.fetchall():
                    metric_labels = labels(environment="local", table=str(table))
                    lines.append(
                        f"olist_cdc_last_contiguous_offset{metric_labels} {contiguous}"
                    )
                    if loaded is not None:
                        lines.append(
                            f"olist_cdc_last_loaded_event_offset{metric_labels} {loaded}"
                        )
                cursor.execute(
                    """
                    select status, count(*)
                    from cdc_audit.cdc_reconciliation group by status
                    """
                )
                for status, count in cursor.fetchall():
                    lines.append(
                        "olist_cdc_reconciliations_total"
                        f"{labels(environment='local', status=str(status))} {count}"
                    )
                cursor.execute(
                    """
                    select extract(epoch from max(finished_at))
                    from cdc_audit.cdc_ingest_runs where status = 'SUCCEEDED'
                    """
                )
                success = cursor.fetchone()[0]
                if success is not None:
                    lines.append(
                        f"olist_cdc_last_ingest_success_timestamp_seconds {success}"
                    )
                cursor.execute(
                    """
                    select count(*) from cdc_audit.cdc_ingest_runs
                    where status = 'FAILED'
                    """
                )
                lines.append(f"olist_cdc_ingest_failures_total {cursor.fetchone()[0]}")
                cursor.execute(
                    """
                    select extract(epoch from max(finished_at - started_at))
                    from cdc_audit.cdc_ingest_runs
                    where status = 'SUCCEEDED'
                      and finished_at = (
                        select max(finished_at)
                        from cdc_audit.cdc_ingest_runs
                        where status = 'SUCCEEDED'
                      )
                    """
                )
                ingest_duration = cursor.fetchone()[0]
                if ingest_duration is not None:
                    lines.append(
                        f"olist_cdc_last_ingest_duration_seconds {ingest_duration}"
                    )
                cursor.execute(
                    """
                    select source_table, count(*),
                           coalesce(sum(object_size_bytes), 0),
                           coalesce(percentile_cont(0.5) within group (
                             order by object_size_bytes
                           ), 0)
                    from cdc_audit.cdc_files
                    where closed_at >= clock_timestamp() - interval '1 hour'
                    group by source_table
                    """
                )
                for table, count, total_size, median_size in cursor.fetchall():
                    metric_labels = labels(environment="local", table=str(table))
                    lines.append(f"olist_cdc_files_last_hour{metric_labels} {count}")
                    lines.append(
                        f"olist_cdc_file_bytes_last_hour{metric_labels} {total_size}"
                    )
                    lines.append(
                        f"olist_cdc_file_median_size_bytes{metric_labels} {median_size}"
                    )
                cursor.execute(
                    """
                    select count(*) from cdc_audit.cdc_dead_letters
                    where resolution_status = 'OPEN'
                    """
                )
                lines.append(f"olist_cdc_dlq_open_records {cursor.fetchone()[0]}")
                cursor.execute(
                    """
                    select coalesce(sum(rejected_rows), 0)
                    from cdc_audit.cdc_reconciliation
                    where created_at >= clock_timestamp() - interval '10 minutes'
                    """
                )
                lines.append(
                    f"olist_cdc_quarantine_recent_records {cursor.fetchone()[0]}"
                )
                cursor.execute(
                    """
                    select extract(epoch from max(finished_at))
                    from cdc_audit.cdc_transform_runs where status = 'SUCCEEDED'
                    """
                )
                transform_success = cursor.fetchone()[0]
                if transform_success is not None:
                    lines.append(
                        "olist_cdc_last_transform_success_timestamp_seconds "
                        f"{transform_success}"
                    )
                cursor.execute(
                    """
                    select count(*) from cdc_audit.cdc_transform_runs
                    where status = 'FAILED'
                    """
                )
                lines.append(
                    f"olist_cdc_transform_failures_total {cursor.fetchone()[0]}"
                )
                cursor.execute(
                    """
                    select extract(epoch from finished_at - started_at)
                    from cdc_audit.cdc_transform_runs
                    where status = 'SUCCEEDED'
                    order by finished_at desc limit 1
                    """
                )
                transform_duration = cursor.fetchone()
                if transform_duration and transform_duration[0] is not None:
                    lines.append(
                        "olist_cdc_last_transform_duration_seconds "
                        f"{transform_duration[0]}"
                    )
                cursor.execute(
                    """
                    select model_name, extract(epoch from build_time),
                           latency_seconds
                    from cdc_audit.cdc_mart_freshness
                    """
                )
                for model, build_time, latency in cursor.fetchall():
                    metric_labels = labels(environment="local", table=str(model))
                    lines.append(
                        f"olist_cdc_mart_build_timestamp_seconds{metric_labels} "
                        f"{build_time}"
                    )
                    if latency is not None:
                        lines.append(
                            f"olist_cdc_mart_freshness_latency_seconds{metric_labels} "
                            f"{latency}"
                        )
                lines.extend(
                    render_event_latency_histogram(
                        cursor, raw_connection_factory, warehouse_type
                    )
                )
    except Exception:
        lines[0] = "olist_cdc_pipeline_up 0"
    return ("\n".join(lines) + "\n").encode()


def handler(control_connection_factory, raw_connection_factory, warehouse_type: str):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in {"/metrics", "/-/healthy"}:
                self.send_error(404)
                return
            body = (
                b"ok\n"
                if self.path == "/-/healthy"
                else render_metrics(
                    control_connection_factory, raw_connection_factory, warehouse_type
                )
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            return

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--warehouse-type",
        choices=["postgres", "clickhouse"],
        default=os.environ.get("CDC_WAREHOUSE_TYPE", "clickhouse"),
    )
    parser.add_argument("--host", default=os.environ.get("POSTGRES_HOST", "localhost"))
    parser.add_argument(
        "--port", type=int, default=int(os.environ.get("POSTGRES_PORT", "5432"))
    )
    parser.add_argument(
        "--database", default=os.environ.get("POSTGRES_DB", "olist_analytics")
    )
    parser.add_argument("--user", default=os.environ.get("POSTGRES_USER", "olist"))
    parser.add_argument("--password", default=os.environ.get("POSTGRES_PASSWORD"))
    parser.add_argument(
        "--password-file", default=os.environ.get("POSTGRES_PASSWORD_FILE")
    )
    parser.add_argument(
        "--control-host", default=os.environ.get("CONTROL_POSTGRES_HOST", "localhost")
    )
    parser.add_argument(
        "--control-port",
        type=int,
        default=int(os.environ.get("CONTROL_POSTGRES_PORT", "5432")),
    )
    parser.add_argument(
        "--control-database",
        default=os.environ.get("CONTROL_POSTGRES_DB", "olist_control"),
    )
    parser.add_argument(
        "--control-user",
        default=os.environ.get("CONTROL_POSTGRES_USER", "olist_control"),
    )
    parser.add_argument(
        "--control-password", default=os.environ.get("CONTROL_POSTGRES_PASSWORD")
    )
    parser.add_argument(
        "--control-password-file",
        default=os.environ.get("CONTROL_POSTGRES_PASSWORD_FILE"),
    )
    parser.add_argument(
        "--clickhouse-host", default=os.environ.get("CLICKHOUSE_HOST", "localhost")
    )
    parser.add_argument(
        "--clickhouse-port",
        type=int,
        default=int(os.environ.get("CLICKHOUSE_PORT", "8123")),
    )
    parser.add_argument(
        "--clickhouse-user", default=os.environ.get("CLICKHOUSE_USER", "olist")
    )
    parser.add_argument(
        "--clickhouse-password", default=os.environ.get("CLICKHOUSE_PASSWORD")
    )
    parser.add_argument(
        "--clickhouse-password-file",
        default=os.environ.get("CLICKHOUSE_PASSWORD_FILE"),
    )
    parser.add_argument(
        "--clickhouse-database",
        default=os.environ.get("CLICKHOUSE_DATABASE", "analytics"),
    )
    parser.add_argument(
        "--clickhouse-secure",
        action="store_true",
        default=os.environ.get("CLICKHOUSE_SECURE", "false").lower() == "true",
    )
    parser.add_argument("--listen-port", type=int, default=9107)
    args = parser.parse_args()

    def connect_postgres_raw():
        return psycopg2.connect(
            host=args.host,
            port=args.port,
            dbname=args.database,
            user=args.user,
            password=read_secret(args.password, args.password_file),
            connect_timeout=5,
            application_name="olist_cdc_metrics_readonly",
        )

    def connect_control():
        return psycopg2.connect(
            host=args.control_host,
            port=args.control_port,
            dbname=args.control_database,
            user=args.control_user,
            password=read_secret(args.control_password, args.control_password_file),
            connect_timeout=5,
            application_name="olist_cdc_control_metrics_readonly",
        )

    def connect_clickhouse_raw():
        return clickhouse_connect.get_client(
            host=args.clickhouse_host,
            port=args.clickhouse_port,
            username=args.clickhouse_user,
            password=read_secret(
                args.clickhouse_password, args.clickhouse_password_file
            )
            or "olist",
            database=args.clickhouse_database,
            secure=args.clickhouse_secure,
        )

    raw_connection_factory = (
        connect_clickhouse_raw
        if args.warehouse_type == "clickhouse"
        else connect_postgres_raw
    )
    ThreadingHTTPServer(
        ("0.0.0.0", args.listen_port),
        handler(connect_control, raw_connection_factory, args.warehouse_type),
    ).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
