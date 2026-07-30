#!/usr/bin/env python3
"""Operate the local CDC lab from infrastructure startup through CDC validation."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROFILES = ("realtime-core", "observability", "logs")
RUNTIME_IMAGES = ("airflow", "kafka-connect", "minio", "nifi")
STACK_SERVICES = (
    "airflow-postgres",
    "clickhouse",
    "clickhouse-init",
    "control-db-init",
    "airflow",
    "oltp-postgres",
    "kafka",
    "kafka-topics",
    "apicurio-registry",
    "kafka-connect",
    "minio",
    "minio-init",
    "nifi",
    "kafka-exporter",
    "postgres-exporter-oltp",
    "statsd-exporter",
    "node-exporter",
    "cadvisor",
    "nifi-metrics-proxy",
    "cdc-component-exporter",
    "cdc-pipeline-exporter",
    "prometheus",
    "alertmanager",
    "grafana",
    "loki",
    "alloy",
)
CDC_DAGS = (
    "olist_cdc_ingest_local",
    "olist_cdc_backfill_local",
    "olist_cdc_transform_local",
    "olist_cdc_quality_local",
)
ACTIVE_CDC_DAGS = (
    "olist_cdc_transform_local",
    "olist_cdc_ingest_local",
    "olist_cdc_quality_local",
)
DEFAULT_CONSUMER_GROUP = "olist-nifi-cdc-v1"
FULL_ARCHIVE = ROOT / "olist.zip"
SMALL_ARCHIVE = ROOT / "tests" / "fixtures" / "olist_small" / "olist_small.zip"
DEFAULT_PASSWORD_FILE = ROOT / "docker" / "secrets" / "dev" / "postgres_password.txt"
CAPTURED_TABLES = (
    "customers",
    "orders",
    "order_items",
    "order_payments",
    "order_reviews",
    "products",
    "sellers",
    "product_category_translation",
)


def compose_args(*args: str) -> list[str]:
    command = ["docker", "compose"]
    for profile in PROFILES:
        command.extend(["--profile", profile])
    command.extend(args)
    return command


def run(
    command: list[str],
    *,
    check: bool = True,
    capture: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    print("+ " + " ".join(command), flush=True)
    return subprocess.run(
        command,
        cwd=ROOT,
        check=check,
        text=True,
        capture_output=capture,
        env=env,
    )


def relative_or_absolute(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def lab_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def compose_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("AIRFLOW_STATSD_ON", "true")
    return env


def stage2_command(*args: str) -> list[str]:
    return [sys.executable, "scripts/cdc/stage2_admin.py", *args]


def airflow_command(*args: str) -> list[str]:
    return ["docker", "compose", "exec", "-T", "airflow", "airflow", *args]


def build_images(env: dict[str, str]) -> None:
    run(compose_args("build", *RUNTIME_IMAGES), env=env)


def start_stack(env: dict[str, str]) -> None:
    run(compose_args("up", "-d", "--wait", *STACK_SERVICES), env=env)


def stop_stack(env: dict[str, str], *, volumes: bool) -> None:
    command = compose_args("down", "--remove-orphans")
    if volumes:
        command.append("--volumes")
    run(command, env=env)


def bootstrap_nifi(env: dict[str, str]) -> None:
    run(
        [
            "docker",
            "compose",
            "--profile",
            "realtime-core",
            "run",
            "--rm",
            "--no-deps",
            "nifi-bootstrap",
        ],
        env=env,
    )


def check_airflow_dags(env: dict[str, str]) -> None:
    run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "airflow",
            "airflow",
            "dags",
            "list-import-errors",
        ],
        env=env,
    )
    result = run(
        ["docker", "compose", "exec", "-T", "airflow", "airflow", "dags", "list"],
        capture=True,
        env=env,
    )
    missing = [dag_id for dag_id in CDC_DAGS if dag_id not in result.stdout]
    if missing:
        raise RuntimeError(f"Airflow does not list required CDC DAGs: {missing}")
    print(f"Validated {len(CDC_DAGS)} CDC Airflow DAGs.", flush=True)


def check_stage2_contracts(env: dict[str, str]) -> None:
    run(stage2_command("configure-registry"), env=env)
    run(stage2_command("validate-topics"), env=env)


def seed_source(
    *,
    archive: Path,
    seed: int,
    run_id: str,
    start_time: str,
    password_file: Path,
    env: dict[str, str],
) -> None:
    if not archive.exists():
        raise FileNotFoundError(
            f"Source archive does not exist: {archive}. "
            "Use seed-small for the committed fixture archive."
        )
    run(
        [
            sys.executable,
            "-m",
            "scripts.simulation",
            "seed",
            "--archive",
            str(archive),
            "--seed",
            str(seed),
            "--run-id",
            run_id,
            "--start-time",
            start_time,
            "--password-file",
            str(password_file),
        ],
        env=env,
    )


def source_counts(env: dict[str, str]) -> dict[str, int]:
    selects = [
        f"select '{table}' as table_name, count(*)::bigint as row_count from public.{table}"
        for table in CAPTURED_TABLES
    ]
    sql = " union all ".join(selects) + " order by table_name;"
    result = run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "oltp-postgres",
            "psql",
            "-U",
            "olist_admin",
            "-d",
            "olist_oltp",
            "-t",
            "-A",
            "-F",
            ",",
            "-c",
            sql,
        ],
        capture=True,
        env=env,
    )
    counts: dict[str, int] = {}
    for line in result.stdout.splitlines():
        if not line.strip() or "," not in line:
            continue
        table_name, row_count = line.split(",", 1)
        counts[table_name] = int(row_count)
    missing = [table for table in CAPTURED_TABLES if counts.get(table, 0) <= 0]
    if missing:
        raise RuntimeError(f"Seed verification found empty captured tables: {missing}")
    print(json.dumps({"event": "source_counts_validated", "row_counts": counts}))
    return counts


def print_status(env: dict[str, str]) -> None:
    run(compose_args("ps", "-a"), env=env)


def run_nonfatal(label: str, command: list[str], env: dict[str, str]) -> None:
    print(f"\n== {label} ==", flush=True)
    result = run(command, check=False, env=env)
    if result.returncode != 0:
        print(f"{label} failed with exit code {result.returncode}; continuing.")


def json_from_cli_output(output: str) -> Any:
    for index, character in enumerate(output):
        if character not in "[{":
            continue
        try:
            return json.loads(output[index:])
        except json.JSONDecodeError:
            continue
    raise ValueError("Airflow CLI output did not contain JSON payload")


def print_airflow_runs(dag_id: str, *, limit: int, env: dict[str, str]) -> None:
    result = run(
        airflow_command("dags", "list-runs", dag_id, "-o", "json"),
        capture=True,
        env=env,
    )
    runs = json_from_cli_output(result.stdout)
    if not isinstance(runs, list):
        raise ValueError(f"Unexpected Airflow list-runs payload for {dag_id}: {runs!r}")
    print(
        json.dumps(
            {
                "dag_id": dag_id,
                "runs": runs[:limit],
            },
            indent=2,
            sort_keys=True,
        )
    )


def print_airflow_runs_nonfatal(
    dag_id: str, *, limit: int, env: dict[str, str]
) -> None:
    print(f"\n== airflow-runs {dag_id} ==", flush=True)
    try:
        print_airflow_runs(dag_id, limit=limit, env=env)
    except Exception as exc:
        print(f"airflow-runs {dag_id} failed: {exc}; continuing.")


def start(args: argparse.Namespace) -> int:
    env = compose_env()
    if not args.skip_build:
        build_images(env)
    start_stack(env)
    if not args.skip_nifi_bootstrap:
        bootstrap_nifi(env)
    if not args.skip_checks:
        run_checks(env)
    if args.status:
        print_status(env)
    return 0


def stop(args: argparse.Namespace) -> int:
    stop_stack(compose_env(), volumes=bool(args.volumes))
    return 0


def seed(args: argparse.Namespace) -> int:
    env = compose_env()
    seed_source(
        archive=lab_path(args.archive),
        seed=int(args.seed),
        run_id=str(args.run_id),
        start_time=str(args.start_time),
        password_file=lab_path(args.password_file),
        env=env,
    )
    source_counts(env)
    return 0


def run_checks(env: dict[str, str]) -> None:
    check_airflow_dags(env)
    check_stage2_contracts(env)


def check(_: argparse.Namespace) -> int:
    run_checks(compose_env())
    return 0


def bootstrap_nifi_command(_: argparse.Namespace) -> int:
    bootstrap_nifi(compose_env())
    return 0


def register_connector(args: argparse.Namespace) -> int:
    env = compose_env()
    run(
        stage2_command(
            "register-connector",
            "--url",
            str(args.url),
            "--password-file",
            str(lab_path(args.password_file)),
        ),
        env=env,
    )
    return 0


def connector_status(args: argparse.Namespace) -> int:
    run(stage2_command("connector-status", "--url", str(args.url)), env=compose_env())
    return 0


def wait_connector_running(args: argparse.Namespace) -> int:
    run(
        stage2_command(
            "wait-connector-running",
            "--url",
            str(args.url),
            "--timeout",
            str(args.timeout),
        ),
        env=compose_env(),
    )
    return 0


def restart_failed_connector(args: argparse.Namespace) -> int:
    run(stage2_command("restart-failed", "--url", str(args.url)), env=compose_env())
    return 0


def enable_dags(args: argparse.Namespace) -> int:
    env = compose_env()
    dag_ids: list[str] = list(ACTIVE_CDC_DAGS)
    if args.include_backfill:
        dag_ids.insert(1, "olist_cdc_backfill_local")
    for dag_id in dag_ids:
        run(airflow_command("dags", "unpause", dag_id), env=env)
    return 0


def trigger_ingest(args: argparse.Namespace) -> int:
    run_id = args.run_id or (
        "local_lab_ingest__" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    )
    command = airflow_command(
        "dags",
        "trigger",
        "olist_cdc_ingest_local",
        "--run-id",
        run_id,
    )
    if args.conf:
        command.extend(["--conf", str(args.conf)])
    run(command, env=compose_env())
    print(json.dumps({"event": "ingest_triggered", "run_id": run_id}))
    return 0


def airflow_runs(args: argparse.Namespace) -> int:
    env = compose_env()
    dag_ids = ACTIVE_CDC_DAGS if args.dag_id is None else args.dag_id
    for dag_id in dag_ids:
        print_airflow_runs(dag_id, limit=int(args.limit), env=env)
    return 0


def kafka_lag(args: argparse.Namespace) -> int:
    run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "kafka",
            "/opt/kafka/bin/kafka-consumer-groups.sh",
            "--bootstrap-server",
            "kafka:29092",
            "--describe",
            "--group",
            str(args.group),
        ],
        env=compose_env(),
    )
    return 0


def _read_secret(value: str | None, password_file: str | None, default: str) -> str:
    if value:
        return value
    if password_file:
        secret = Path(password_file).read_text(encoding="utf-8").strip()
        if secret:
            return secret
    return default


def warehouse_status_in_container(_: argparse.Namespace) -> int:
    import importlib

    clickhouse_connect = importlib.import_module("clickhouse_connect")
    psycopg2 = importlib.import_module("psycopg2")

    clickhouse = clickhouse_connect.get_client(
        host=os.environ.get("CLICKHOUSE_HOST", "clickhouse"),
        port=int(os.environ.get("CLICKHOUSE_PORT", "8123")),
        username=os.environ.get("CLICKHOUSE_USER", "olist"),
        password=_read_secret(
            os.environ.get("CLICKHOUSE_PASSWORD"),
            os.environ.get("CLICKHOUSE_PASSWORD_FILE"),
            "olist",
        ),
        database=os.environ.get("CLICKHOUSE_DATABASE", "analytics"),
        secure=os.environ.get("CLICKHOUSE_SECURE", "false").lower() == "true",
    )
    control = psycopg2.connect(
        host=os.environ.get("CONTROL_POSTGRES_HOST", "airflow-postgres"),
        port=int(os.environ.get("CONTROL_POSTGRES_PORT", "5432")),
        dbname=os.environ.get("CONTROL_POSTGRES_DB", "olist_control"),
        user=os.environ.get("CONTROL_POSTGRES_USER", "olist_control"),
        password=_read_secret(
            os.environ.get("CONTROL_POSTGRES_PASSWORD"),
            os.environ.get("CONTROL_POSTGRES_PASSWORD_FILE"),
            "olist_control",
        ),
        application_name="local_lab_warehouse_status",
        connect_timeout=5,
    )
    try:
        raw_counts: dict[str, dict[str, Any]] = {}
        for table in CAPTURED_TABLES:
            row = clickhouse.query(
                f"""
                SELECT count(), max(_source_ts), max(_warehouse_loaded_at)
                FROM raw_cdc.`{table}` FINAL
                """
            ).first_row
            raw_counts[table] = {
                "rows": int(row[0]),
                "max_source_ts": None if row[1] is None else str(row[1]),
                "max_loaded_at": None if row[2] is None else str(row[2]),
            }

        with control, control.cursor() as cursor:
            cursor.execute(
                """
                select 'ingest_runs' as metric, count(*)::text as value
                from cdc_audit.cdc_ingest_runs
                union all
                select 'last_ingest_status',
                       coalesce((
                           select status
                           from cdc_audit.cdc_ingest_runs
                           order by started_at desc limit 1
                       ), 'none')
                union all
                select 'transform_runs', count(*)::text
                from cdc_audit.cdc_transform_runs
                union all
                select 'last_transform_status',
                       coalesce((
                           select status
                           from cdc_audit.cdc_transform_runs
                           order by started_at desc limit 1
                       ), 'none')
                union all
                select 'open_dead_letters', count(*)::text
                from cdc_audit.cdc_dead_letters
                where resolution_status = 'OPEN'
                union all
                select 'watermarks', count(*)::text
                from cdc_audit.cdc_partition_watermarks
                order by metric
                """
            )
            audit_summary = {str(metric): str(value) for metric, value in cursor}
    finally:
        control.close()
        clickhouse.close()

    print(
        json.dumps(
            {
                "event": "warehouse_status",
                "raw_cdc": raw_counts,
                "cdc_audit": audit_summary,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def warehouse_status(_: argparse.Namespace) -> int:
    run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "airflow",
            "python",
            "scripts/cdc/local_lab.py",
            "_warehouse-status-in-container",
        ],
        env=compose_env(),
    )
    return 0


def status(args: argparse.Namespace) -> int:
    env = compose_env()
    print_status(env)
    if not args.compose_only:
        run_nonfatal("connector-status", stage2_command("connector-status"), env)
        run_nonfatal(
            "kafka-lag",
            [
                "docker",
                "compose",
                "exec",
                "-T",
                "kafka",
                "/opt/kafka/bin/kafka-consumer-groups.sh",
                "--bootstrap-server",
                "kafka:29092",
                "--describe",
                "--group",
                str(args.group),
            ],
            env,
        )
        for dag_id in ACTIVE_CDC_DAGS:
            print_airflow_runs_nonfatal(dag_id, limit=int(args.limit), env=env)
        run_nonfatal(
            "warehouse-status",
            [
                "docker",
                "compose",
                "exec",
                "-T",
                "airflow",
                "python",
                "scripts/cdc/local_lab.py",
                "_warehouse-status-in-container",
            ],
            env,
        )
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "_warehouse-status-in-container":
        return warehouse_status_in_container(argparse.Namespace())

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser(
        "start",
        help="Build images, start the local CDC stack, deploy NiFi, and run checks.",
    )
    start_parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Do not rebuild local runtime images before starting services.",
    )
    start_parser.add_argument(
        "--skip-nifi-bootstrap",
        action="store_true",
        help="Do not deploy the version-controlled NiFi process group.",
    )
    start_parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Do not run Airflow, registry, and Kafka topic smoke checks.",
    )
    start_parser.add_argument(
        "--status",
        action="store_true",
        help="Print docker compose ps -a after startup and checks.",
    )
    start_parser.set_defaults(func=start)

    stop_parser = subparsers.add_parser(
        "stop",
        help="Stop and remove the local CDC Compose stack.",
    )
    stop_parser.add_argument(
        "--volumes",
        "-v",
        action="store_true",
        help="Also delete local Compose volumes for a clean restart.",
    )
    stop_parser.set_defaults(func=stop)

    seed_parser = subparsers.add_parser(
        "seed",
        help="Seed the OLTP source from the full local olist.zip archive.",
    )
    seed_parser.add_argument("--archive", default=relative_or_absolute(FULL_ARCHIVE))
    seed_parser.add_argument("--seed", type=int, default=101)
    seed_parser.add_argument("--run-id", default="e2e_initial_seed")
    seed_parser.add_argument("--start-time", default="2020-01-01T00:00:00")
    seed_parser.add_argument(
        "--password-file",
        default=relative_or_absolute(DEFAULT_PASSWORD_FILE),
    )
    seed_parser.set_defaults(func=seed)

    seed_small_parser = subparsers.add_parser(
        "seed-small",
        help="Seed the OLTP source from the committed small fixture archive.",
    )
    seed_small_parser.add_argument(
        "--archive",
        default=relative_or_absolute(SMALL_ARCHIVE),
    )
    seed_small_parser.add_argument("--seed", type=int, default=101)
    seed_small_parser.add_argument("--run-id", default="e2e_small_seed")
    seed_small_parser.add_argument("--start-time", default="2020-01-01T00:00:00")
    seed_small_parser.add_argument(
        "--password-file",
        default=relative_or_absolute(DEFAULT_PASSWORD_FILE),
    )
    seed_small_parser.set_defaults(func=seed)

    check_parser = subparsers.add_parser(
        "check",
        help="Run Airflow, registry, and Kafka topic smoke checks only.",
    )
    check_parser.set_defaults(func=check)

    bootstrap_nifi_parser = subparsers.add_parser(
        "bootstrap-nifi",
        help="Deploy or update the version-controlled NiFi CDC process group.",
    )
    bootstrap_nifi_parser.set_defaults(func=bootstrap_nifi_command)

    register_parser = subparsers.add_parser(
        "register-connector",
        help="Create or update the Debezium PostgreSQL connector and wait for RUNNING.",
    )
    register_parser.add_argument("--url", default="http://localhost:8083")
    register_parser.add_argument(
        "--password-file",
        default=relative_or_absolute(DEFAULT_PASSWORD_FILE),
    )
    register_parser.set_defaults(func=register_connector)

    connector_status_parser = subparsers.add_parser(
        "connector-status",
        help="Print Debezium connector and task state from Kafka Connect.",
    )
    connector_status_parser.add_argument("--url", default="http://localhost:8083")
    connector_status_parser.set_defaults(func=connector_status)

    wait_connector_parser = subparsers.add_parser(
        "wait-connector-running",
        help="Wait until the Debezium connector and task are RUNNING.",
    )
    wait_connector_parser.add_argument("--url", default="http://localhost:8083")
    wait_connector_parser.add_argument("--timeout", type=float, default=120)
    wait_connector_parser.set_defaults(func=wait_connector_running)

    restart_parser = subparsers.add_parser(
        "restart-failed-connector",
        help="Restart only failed Debezium connector tasks and wait for RUNNING.",
    )
    restart_parser.add_argument("--url", default="http://localhost:8083")
    restart_parser.set_defaults(func=restart_failed_connector)

    enable_parser = subparsers.add_parser(
        "enable-dags",
        help="Unpause the CDC DAGs needed for near-realtime local flow.",
    )
    enable_parser.add_argument(
        "--include-backfill",
        action="store_true",
        help="Also unpause the manual CDC backfill DAG.",
    )
    enable_parser.set_defaults(func=enable_dags)

    trigger_parser = subparsers.add_parser(
        "trigger-ingest",
        help="Trigger one olist_cdc_ingest_local DAG run.",
    )
    trigger_parser.add_argument("--run-id")
    trigger_parser.add_argument(
        "--conf",
        help="Optional JSON string passed to Airflow as DAG run conf.",
    )
    trigger_parser.set_defaults(func=trigger_ingest)

    airflow_runs_parser = subparsers.add_parser(
        "airflow-runs",
        help="List recent runs for CDC DAGs.",
    )
    airflow_runs_parser.add_argument(
        "--dag-id",
        action="append",
        help="DAG id to inspect. Can be repeated.",
    )
    airflow_runs_parser.add_argument("--limit", type=int, default=5)
    airflow_runs_parser.set_defaults(func=airflow_runs)

    kafka_lag_parser = subparsers.add_parser(
        "kafka-lag",
        help="Show Kafka offsets and lag for the NiFi CDC consumer group.",
    )
    kafka_lag_parser.add_argument("--group", default=DEFAULT_CONSUMER_GROUP)
    kafka_lag_parser.set_defaults(func=kafka_lag)

    warehouse_parser = subparsers.add_parser(
        "warehouse-status",
        help="Print raw_cdc row counts and cdc_audit run counters.",
    )
    warehouse_parser.set_defaults(func=warehouse_status)

    status_parser = subparsers.add_parser(
        "status",
        help="Print compose, connector, Kafka, Airflow, and warehouse status.",
    )
    status_parser.add_argument("--compose-only", action="store_true")
    status_parser.add_argument("--group", default=DEFAULT_CONSUMER_GROUP)
    status_parser.add_argument("--limit", type=int, default=3)
    status_parser.set_defaults(func=status)

    args = parser.parse_args()
    try:
        return int(args.func(args))
    except subprocess.CalledProcessError as exc:
        print(
            f"Command failed with exit code {exc.returncode}: {exc.cmd}",
            file=sys.stderr,
        )
        return exc.returncode
    except Exception as exc:
        print(f"Local CDC stack command failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
