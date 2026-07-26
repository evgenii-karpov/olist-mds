#!/usr/bin/env python3
"""Run a bounded local CDC workload and capture Prometheus SLO evidence."""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import clickhouse_connect
from scripts.cdc.warehouse_ingest import BUSINESS_COLUMNS
from scripts.loading.load_raw_to_clickhouse import ch_string
from scripts.orchestration.control_postgres import (
    add_control_postgres_args,
    control_connection,
    read_secret,
)

PROFILES = {
    "reference": {"rate": 5.0, "duration_seconds": 1800},
    "burst": {"rate": 20.0, "duration_seconds": 600},
    "soak": {"rate": 2.0, "duration_seconds": 14400},
}


def prometheus_query(base_url: str, query: str) -> list[dict]:
    url = f"{base_url.rstrip('/')}/api/v1/query?" + urllib.parse.urlencode(
        {"query": query}
    )
    with urllib.request.urlopen(url, timeout=15) as response:
        payload = json.loads(response.read())
    if payload.get("status") != "success":
        raise RuntimeError(f"Prometheus query failed: {query}")
    return payload.get("data", {}).get("result", [])


def scalar(base_url: str, query: str) -> float | None:
    result = prometheus_query(base_url, query)
    if not result:
        return None
    return float(result[0]["value"][1])


def quantile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, math.ceil(fraction * len(ordered)) - 1)
    return ordered[index]


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


def clickhouse_password(args: argparse.Namespace) -> str:
    return (
        read_secret(
            args.clickhouse_password,
            args.clickhouse_password_file,
            "olist",
        )
        or "olist"
    )


def clickhouse_client(args: argparse.Namespace) -> Any:
    return clickhouse_connect.get_client(
        host=args.clickhouse_host,
        port=args.clickhouse_port,
        username=args.clickhouse_user,
        password=clickhouse_password(args),
        database=args.clickhouse_database,
        secure=args.clickhouse_secure,
    )


def transformed_objects(connection) -> dict[str, datetime]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select f.object_uri, min(t.finished_at)
            from cdc_audit.cdc_files f
            join cdc_audit.cdc_transform_run_files rf
              on rf.manifest_uri = f.manifest_uri
            join cdc_audit.cdc_transform_runs t
              on t.transform_run_id = rf.transform_run_id
             and t.status = 'SUCCEEDED'
            group by f.object_uri
            """
        )
        return {
            str(object_uri): finished_at
            for object_uri, finished_at in cursor.fetchall()
        }


def event_latency_samples(
    raw_client,
    control_pg_connection,
    started: datetime,
    finished: datetime,
):
    """Return per-event source-commit-to-successful-transform latency."""
    finished_by_object = transformed_objects(control_pg_connection)
    samples: list[float] = []
    raw_events = 0
    started_literal = ch_string(started.isoformat())
    finished_literal = ch_string(finished.isoformat())
    for table in BUSINESS_COLUMNS:
        rows = raw_client.query(
            f"""
            SELECT _event_id, _source_ts, _source_object_uri
            FROM raw_cdc.`{table}` FINAL
            WHERE _source_ts >= parseDateTime64BestEffort({started_literal}, 6, 'UTC')
              AND _source_ts <= parseDateTime64BestEffort({finished_literal}, 6, 'UTC')
            """
        ).result_rows
        raw_events += len(rows)
        event_latencies: dict[str, float] = {}
        for event_id, source_ts, object_uri in rows:
            finished_at = finished_by_object.get(str(object_uri))
            if finished_at is None:
                continue
            source_seconds = timestamp_seconds(source_ts)
            finished_seconds = timestamp_seconds(finished_at)
            if source_seconds is None or finished_seconds is None:
                continue
            latency = max(0.0, finished_seconds - source_seconds)
            event_key = str(event_id)
            current = event_latencies.get(event_key)
            if current is None or latency < current:
                event_latencies[event_key] = latency
        samples.extend(event_latencies.values())
    return samples, raw_events


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=sorted(PROFILES), required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--seed", type=int, default=20260717)
    parser.add_argument("--run-id")
    parser.add_argument("--settle-seconds", type=int, default=180)
    parser.add_argument("--prometheus-url", default="http://localhost:9090")
    parser.add_argument("--verified-no-lost-events", action="store_true")
    parser.add_argument("--verified-no-duplicate-current-keys", action="store_true")
    parser.add_argument(
        "--password-file", default="docker/secrets/dev/postgres_password.txt"
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
        action=argparse.BooleanOptionalAction,
        default=os.environ.get("CLICKHOUSE_SECURE", "false").lower() == "true",
    )
    add_control_postgres_args(parser)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    profile = PROFILES[args.profile]
    run_id = args.run_id or f"phase6_{args.profile}_{args.seed}"
    command = [
        "uv",
        "run",
        "python",
        "-m",
        "scripts.simulation",
        "run",
        "--seed",
        str(args.seed),
        "--run-id",
        run_id,
        "--rate",
        str(profile["rate"]),
        "--duration-seconds",
        str(profile["duration_seconds"]),
        "--password-file",
        args.password_file,
    ]
    if not args.execute:
        print(
            json.dumps({"status": "plan", "profile": args.profile, "command": command})
        )
        return 0

    started = time.time()
    subprocess.run(command, cwd=ROOT, check=True)
    workload_finished = time.time()
    time.sleep(args.settle_seconds)
    finished = time.time()
    raw_client = clickhouse_client(args)
    control_pg_connection = control_connection(args)
    try:
        samples, raw_events = event_latency_samples(
            raw_client,
            control_pg_connection,
            datetime.fromtimestamp(started, UTC),
            datetime.fromtimestamp(workload_finished, UTC),
        )
    finally:
        raw_client.close()
        control_pg_connection.close()
    p50 = quantile(samples, 0.50)
    p95 = quantile(samples, 0.95)
    p99 = quantile(samples, 0.99)
    offset_gaps = scalar(args.prometheus_url, "sum(olist_cdc_offset_gaps)")
    report = {
        "profile": args.profile,
        "simulation_run_id": run_id,
        "started_at": datetime.fromtimestamp(started, UTC).isoformat(),
        "finished_at": datetime.fromtimestamp(finished, UTC).isoformat(),
        "configured_rate": profile["rate"],
        "configured_duration_seconds": profile["duration_seconds"],
        "latency_observations": len(samples),
        "latency_basis": "raw_event_source_ts_to_successful_transform_finished_at",
        "raw_events_in_window": raw_events,
        "events_without_successful_transform": raw_events - len(samples),
        "commit_to_mart_seconds": {
            "p50": p50,
            "p95": p95,
            "p99": p99,
        },
        "offset_gaps": offset_gaps,
        "open_dlq_records": scalar(args.prometheus_url, "olist_cdc_dlq_open_records"),
        "kafka_lag": scalar(args.prometheus_url, "olist_cdc:kafka_consumer_lag"),
        "nifi_queue_utilization": scalar(
            args.prometheus_url, "olist_cdc:nifi_queue_utilization_ratio"
        ),
        "host_cpu_busy_ratio": scalar(
            args.prometheus_url,
            '1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m]))',
        ),
        "verified_no_lost_events": args.verified_no_lost_events,
        "verified_no_duplicate_current_keys": (args.verified_no_duplicate_current_keys),
        "pass": p95 is not None
        and p95 <= 300
        and offset_gaps == 0
        and raw_events == len(samples)
        and args.verified_no_lost_events
        and args.verified_no_duplicate_current_keys,
    }
    output = args.report or Path(f"data/reports/stage6-{args.profile}.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
