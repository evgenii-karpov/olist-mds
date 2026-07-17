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

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import psycopg2
from psycopg2 import sql
from scripts.cdc.warehouse_ingest import BUSINESS_COLUMNS, read_secret

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


def event_latency_samples(connection, started: datetime, finished: datetime):
    """Return per-event source-commit-to-successful-transform latency."""
    samples: list[float] = []
    raw_events = 0
    with connection.cursor() as cursor:
        for table in BUSINESS_COLUMNS:
            relation = sql.Identifier(table)
            cursor.execute(
                sql.SQL(
                    """
                    select count(*) from raw_cdc.{}
                    where _source_ts >= %s and _source_ts <= %s
                    """
                ).format(relation),
                (started, finished),
            )
            raw_events += int(cursor.fetchone()[0])
            cursor.execute(
                sql.SQL(
                    """
                    select extract(epoch from min(t.finished_at) - r._source_ts)
                    from raw_cdc.{} r
                    join cdc_audit.cdc_files f
                      on f.object_uri = r._source_object_uri
                    join cdc_audit.cdc_transform_run_files rf
                      on rf.manifest_uri = f.manifest_uri
                    join cdc_audit.cdc_transform_runs t
                      on t.transform_run_id = rf.transform_run_id
                     and t.status = 'SUCCEEDED'
                    where r._source_ts >= %s and r._source_ts <= %s
                    group by r._event_id, r._source_ts
                    """
                ).format(relation),
                (started, finished),
            )
            samples.extend(float(row[0]) for row in cursor.fetchall())
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
        "--warehouse-host", default=os.environ.get("POSTGRES_HOST", "localhost")
    )
    parser.add_argument(
        "--warehouse-port",
        type=int,
        default=int(os.environ.get("POSTGRES_PORT", "5432")),
    )
    parser.add_argument(
        "--warehouse-database", default=os.environ.get("POSTGRES_DB", "olist_analytics")
    )
    parser.add_argument(
        "--warehouse-user", default=os.environ.get("POSTGRES_USER", "olist")
    )
    parser.add_argument(
        "--warehouse-password", default=os.environ.get("POSTGRES_PASSWORD")
    )
    parser.add_argument(
        "--warehouse-password-file",
        default=os.environ.get(
            "POSTGRES_PASSWORD_FILE", "docker/secrets/dev/postgres_password.txt"
        ),
    )
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
    connection = psycopg2.connect(
        host=args.warehouse_host,
        port=args.warehouse_port,
        dbname=args.warehouse_database,
        user=args.warehouse_user,
        password=read_secret(args.warehouse_password, args.warehouse_password_file),
        connect_timeout=10,
        application_name="olist_cdc_benchmark",
    )
    try:
        samples, raw_events = event_latency_samples(
            connection,
            datetime.fromtimestamp(started, UTC),
            datetime.fromtimestamp(workload_finished, UTC),
        )
    finally:
        connection.close()
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
