#!/usr/bin/env python3
"""Expose low-cardinality Phase 4 pipeline metrics from read-only audit queries."""

from __future__ import annotations

import argparse
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import psycopg2
from psycopg2 import sql
from scripts.cdc.warehouse_ingest import BUSINESS_COLUMNS, read_secret


def labels(**values: str) -> str:
    rendered = ",".join(
        f'{key}="{value.replace(chr(92), chr(92) * 2).replace(chr(34), chr(92) + chr(34))}"'
        for key, value in values.items()
    )
    return "{" + rendered + "}"


def render_metrics(connection_factory) -> bytes:
    lines = ["olist_cdc_pipeline_up 1"]
    try:
        with connection_factory() as connection:
            connection.set_session(readonly=True, autocommit=False)
            with connection.cursor() as cursor:
                for table in BUSINESS_COLUMNS:
                    cursor.execute(
                        sql.SQL(
                            """
                            select _op, count(*),
                                   extract(epoch from max(_source_ts)),
                                   extract(epoch from clock_timestamp() - max(_source_ts))
                            from raw_cdc.{} group by _op
                            """
                        ).format(sql.Identifier(table))
                    )
                    rows = cursor.fetchall()
                    max_timestamp = None
                    freshness = None
                    for operation, count, source_timestamp, age in rows:
                        lines.append(
                            "olist_cdc_raw_events_total"
                            f"{labels(environment='local', table=table, operation=str(operation))} {count}"
                        )
                        if source_timestamp is not None and (
                            max_timestamp is None or source_timestamp > max_timestamp
                        ):
                            max_timestamp = source_timestamp
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
    except Exception:
        lines[0] = "olist_cdc_pipeline_up 0"
    return ("\n".join(lines) + "\n").encode()


def handler(connection_factory):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in {"/metrics", "/-/healthy"}:
                self.send_error(404)
                return
            body = (
                b"ok\n"
                if self.path == "/-/healthy"
                else render_metrics(connection_factory)
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
    parser.add_argument("--listen-port", type=int, default=9107)
    args = parser.parse_args()

    def connect():
        return psycopg2.connect(
            host=args.host,
            port=args.port,
            dbname=args.database,
            user=args.user,
            password=read_secret(args.password, args.password_file),
            connect_timeout=5,
            application_name="olist_cdc_metrics_readonly",
        )

    ThreadingHTTPServer(("0.0.0.0", args.listen_port), handler(connect)).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
