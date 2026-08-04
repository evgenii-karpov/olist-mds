#!/usr/bin/env python3
"""Operate the disposable MySQL → Kafka → Spark/Iceberg Wave 1 lab.

This is the only documented lifecycle entry point for the candidate runtime.
Every command emits one bounded JSON result and never prints secret contents.
Wave 2 and serving commands remain explicit non-zero guards until their join
points are implemented.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SMALL_ARCHIVE = ROOT / "tests" / "fixtures" / "olist_small" / "olist_small.zip"
FULL_ARCHIVE = ROOT / "olist.zip"
DEFAULT_PASSWORD_FILE = (
    ROOT / "docker" / "secrets" / "dev" / "mysql_simulator_password.txt"
)
DEFAULT_PROJECT_NAME = "olist_wave1_j1"
COMPOSE_PROFILES = ("platform", "streaming", "serving", "observability")
PLATFORM_PROFILES = ("platform",)
STREAMING_PROFILES = ("streaming",)
SERVING_PROFILES = ("platform", "serving")
ALL_ENTITIES = (
    "customers",
    "orders",
    "order_items",
    "order_payments",
    "order_reviews",
    "products",
    "sellers",
    "product_category_translation",
)
MYSQL_TABLES = (*ALL_ENTITIES, "geolocation")
GOLD_MODELS = (
    "dim_customer_scd2",
    "dim_date",
    "dim_order_status",
    "dim_product_scd2",
    "dim_seller",
    "fact_order_items",
    "mart_daily_revenue",
    "mart_monthly_arpu",
)
PINNED_IMAGES = {
    "postgres:17.10",
    "mysql:8.4.10",
    "apache/kafka:4.3.1",
    "quay.io/apicurio/apicurio-registry:3.3.0",
    "clickhouse/clickhouse-server:26.3.17.4",
    "olist-spark:4.1.3-iceberg1.11.0",
    "olist-kafka-connect:3.6.0.Final",
    "olist-polaris:1.6.0",
    "olist-airflow:local",
}
DEFAULT_COMMAND_TIMEOUT = 120.0
DEFAULT_BOOTSTRAP_TIMEOUT = 1800.0
SECRET_ENV_DEFAULTS = {
    "AIRFLOW_POSTGRES_PASSWORD_SOURCE_FILE": "docker/secrets/dev/airflow_postgres_password.txt",
    "CONTROL_POSTGRES_PASSWORD_SOURCE_FILE": "docker/secrets/dev/control_postgres_password.txt",
    "POLARIS_DB_USERNAME_SOURCE_FILE": "docker/secrets/dev/polaris_db_user.txt",
    "POLARIS_DB_PASSWORD_SOURCE_FILE": "docker/secrets/dev/polaris_db_password.txt",
    "APICURIO_DB_USERNAME_SOURCE_FILE": "docker/secrets/dev/apicurio_db_user.txt",
    "APICURIO_DB_PASSWORD_SOURCE_FILE": "docker/secrets/dev/apicurio_db_password.txt",
    "MYSQL_ROOT_PASSWORD_SOURCE_FILE": "docker/secrets/dev/mysql_root_password.txt",
    "MYSQL_ADMIN_PASSWORD_SOURCE_FILE": "docker/secrets/dev/mysql_admin_password.txt",
    "MYSQL_SIMULATOR_PASSWORD_SOURCE_FILE": "docker/secrets/dev/mysql_simulator_password.txt",
    "MYSQL_CDC_READER_PASSWORD_SOURCE_FILE": "docker/secrets/dev/mysql_cdc_reader_password.txt",
    "MYSQL_REFERENCE_READER_PASSWORD_SOURCE_FILE": "docker/secrets/dev/mysql_spark_reference_reader_password.txt",
    "MINIO_ROOT_USER_SOURCE_FILE": "docker/secrets/dev/minio_root_user.txt",
    "MINIO_ROOT_PASSWORD_SOURCE_FILE": "docker/secrets/dev/minio_root_password.txt",
    "CLICKHOUSE_PASSWORD_SOURCE_FILE": "docker/secrets/dev/clickhouse_password.txt",
    "AIRFLOW_API_SECRET_KEY_SOURCE_FILE": "docker/secrets/dev/airflow_api_secret_key.txt",
}
_PASSWORD_PATTERN = re.compile(
    r"(?i)(password|passwd|secret|token|credential)([=:])([^\s,;]+)"
)


class LabError(RuntimeError):
    """A bounded lifecycle operation failed without a safe retry assumption."""


class NotAvailableUntil(LabError):
    """A deliberately deferred Wave 2/E command was requested."""

    def __init__(self, phase: str, command: str) -> None:
        super().__init__(f"{command} is not available until {phase}")
        self.phase = phase
        self.command = command


def _path(value: str | Path) -> Path:
    candidate = Path(value)
    return candidate if candidate.is_absolute() else ROOT / candidate


def _compose_env() -> dict[str, str]:
    environment = os.environ.copy()
    environment.setdefault("COMPOSE_PROJECT_NAME", DEFAULT_PROJECT_NAME)
    python_path = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = str(ROOT) + (
        os.pathsep + python_path if python_path else ""
    )
    return environment


def _profiles_args(profiles: Sequence[str]) -> list[str]:
    result: list[str] = []
    for profile in profiles:
        result.extend(["--profile", profile])
    return result


def compose_command(
    *args: str, profiles: Sequence[str] = SERVING_PROFILES
) -> list[str]:
    return ["docker", "compose", *_profiles_args(profiles), *args]


def _secret_paths() -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for environment_name, default in SECRET_ENV_DEFAULTS.items():
        paths[environment_name] = _path(os.environ.get(environment_name, default))
    paths["MYSQL_PASSWORD_FILE"] = _path(
        os.environ.get(
            "MYSQL_PASSWORD_FILE",
            os.environ.get(
                "MYSQL_SIMULATOR_PASSWORD_SOURCE_FILE",
                SECRET_ENV_DEFAULTS["MYSQL_SIMULATOR_PASSWORD_SOURCE_FILE"],
            ),
        )
    )
    return paths


def _secret_values() -> tuple[str, ...]:
    values: list[str] = []
    for path in _secret_paths().values():
        try:
            value = path.read_text(encoding="utf-8").rstrip("\r\n")
        except (OSError, UnicodeError):
            continue
        if value:
            values.append(value)
    return tuple(dict.fromkeys(values))


def redact_text(value: str) -> str:
    sanitized = value
    variants: list[str] = []
    for secret in _secret_values():
        variants.extend((secret, json.dumps(secret, ensure_ascii=True)[1:-1]))
    for variant in sorted((item for item in variants if item), key=len, reverse=True):
        sanitized = sanitized.replace(variant, "<redacted>")
    return _PASSWORD_PATTERN.sub(r"\1\2<redacted>", sanitized)


def _run(
    command: Sequence[str],
    *,
    timeout: float = DEFAULT_COMMAND_TIMEOUT,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            list(command),
            cwd=ROOT,
            env=env or _compose_env(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise LabError(f"required executable is unavailable: {command[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise LabError(f"command timed out after {timeout:g}s: {command[0]}") from exc
    if check and result.returncode != 0:
        detail = redact_text((result.stderr or result.stdout or "").strip())
        detail = detail[-1200:] if detail else "no diagnostic output"
        raise LabError(f"command exited {result.returncode}: {command[0]} ({detail})")
    return result


def _emit(command: str, status: str, **fields: Any) -> int:
    payload: dict[str, Any] = {"command": command, "status": status, **fields}
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str))
    # Lifecycle commands use a small vocabulary of successful terminal
    # states.  ``succeeded`` is the authoritative result for finite serving
    # operations; treating it as a shell failure makes the E2E harness reject
    # a successful Airflow run.
    return 0 if status in {"ready", "succeeded", "success", "pass"} else 1


def _read_single_line(path: Path, label: str) -> str:
    try:
        value = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise LabError(f"{label} secret file is not readable") from exc
    value = value.rstrip("\r\n")
    if not value:
        raise LabError(f"{label} secret file is empty")
    if "\n" in value or "\r" in value:
        raise LabError(f"{label} secret file must contain exactly one line")
    return value


def _archive_or_fail(value: str | Path) -> Path:
    archive = _path(value)
    if not archive.is_file():
        raise LabError(f"archive does not exist: {archive}")
    return archive


def _docker_versions() -> dict[str, str]:
    docker = _run(["docker", "version", "--format", "{{.Server.Version}}"], timeout=20)
    compose = _run(["docker", "compose", "version", "--short"], timeout=20)
    return {
        "docker_server": redact_text(docker.stdout.strip() or "unknown"),
        "compose": redact_text(compose.stdout.strip() or "unknown"),
    }


def _compose_config_check() -> None:
    _run(
        compose_command("config", "--quiet", profiles=COMPOSE_PROFILES),
        timeout=60,
    )


def _pinned_image_check() -> dict[str, Any]:
    compose_text = (ROOT / "compose.yaml").read_text(encoding="utf-8")
    if re.search(r"^\s+container_name\s*:", compose_text, re.MULTILINE):
        raise LabError("compose.yaml must not define fixed container_name values")
    missing = sorted(
        image for image in PINNED_IMAGES if f"image: {image}" not in compose_text
    )
    if missing:
        raise LabError("compose.yaml is missing pinned images: " + ", ".join(missing))
    return {"pinned_images": sorted(PINNED_IMAGES), "fixed_container_names": 0}


def _doctor(args: argparse.Namespace) -> int:
    checks: dict[str, Any] = {}
    try:
        checks["docker"] = _docker_versions()
        checks["images"] = _pinned_image_check()
        archive = _archive_or_fail(args.archive)
        checks["archive"] = {"path": str(archive), "exists": True}
        missing_secrets: list[str] = []
        for label, path in _secret_paths().items():
            try:
                _read_single_line(path, label)
            except LabError:
                missing_secrets.append(label)
        if missing_secrets:
            raise LabError("invalid secret files: " + ", ".join(missing_secrets))
        checks["secret_files"] = {"count": len(_secret_paths()), "values": "redacted"}
        _compose_config_check()
        checks["compose_config"] = "valid"
        checks["ports"] = _port_observations()
    except LabError as exc:
        return _emit("doctor", "blocked", checks=checks, error=redact_text(str(exc)))
    return _emit("doctor", "ready", checks=checks)


def _port_observations() -> dict[str, str]:
    ports = {
        "mysql": int(os.environ.get("MYSQL_HOST_PORT", "3306")),
        "kafka": int(os.environ.get("KAFKA_HOST_PORT", "9092")),
        "connect": int(os.environ.get("KAFKA_CONNECT_HOST_PORT", "8083")),
        "apicurio": int(os.environ.get("APICURIO_HOST_PORT", "8081")),
        "polaris": int(os.environ.get("POLARIS_HOST_PORT", "8181")),
        "clickhouse": int(os.environ.get("CLICKHOUSE_HTTP_HOST_PORT", "8123")),
    }
    observations: dict[str, str] = {}
    for name, port in ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(0.2)
            observations[name] = (
                "in_use" if sock.connect_ex(("127.0.0.1", port)) == 0 else "available"
            )
        finally:
            sock.close()
    return observations


def _compose_up(
    *,
    profiles: Sequence[str],
    build: bool,
    timeout: float,
    wait: bool = False,
    required_services: Sequence[str] = (),
    services: Sequence[str] = (),
) -> None:
    args = ["up", "-d"]
    if wait:
        args.append("--wait")
    if build:
        args.append("--build")
    args.extend(services)
    result = _run(
        compose_command(*args, profiles=profiles),
        timeout=timeout,
        check=False,
    )
    if result.returncode == 0:
        if not required_services:
            return
        deadline = time.monotonic() + max(timeout, 180.0)
        required = set(required_services)
        while True:
            records = _compose_records(profiles)
            by_service = {
                str(item.get("Service")): item
                for item in records
                if item.get("Service")
            }
            missing = sorted(required - by_service.keys())
            failures: list[str] = []
            pending: list[str] = []
            for item in records:
                state = str(item.get("State", "")).lower()
                exit_code = item.get("ExitCode")
                if state == "exited" and exit_code not in (0, "0", None):
                    failures.append(
                        f"{item.get('Service', 'unknown')} exited {exit_code}"
                    )
            for service in sorted(required & by_service.keys()):
                item = by_service[service]
                state = str(item.get("State", "")).lower()
                exit_code = item.get("ExitCode")
                health = str(item.get("Health", "")).lower()
                if state == "exited" and exit_code not in (0, "0", None):
                    failures.append(f"{service} exited {exit_code}")
                elif state != "running":
                    pending.append(f"{service} {state or 'unknown'}")
                elif health not in ("", "none", "healthy"):
                    pending.append(f"{service} health {health}")
            if failures:
                raise LabError(
                    "required Compose services failed: " + "; ".join(failures)
                )
            if not missing and not pending:
                return
            if time.monotonic() >= deadline:
                details = [f"missing {service}" for service in missing] + pending
                raise LabError(
                    "required Compose services did not become ready before timeout"
                    + (": " + "; ".join(details) if details else "")
                )
            time.sleep(2)

    # A failed `up -d` is never a ready state.  In particular, a failed
    # image build can leave the previously started platform containers
    # running; treating those records as success hides the actual serving
    # failure and makes the caller report a misleading connection error
    # later (for example, Airflow status code 0).
    if not wait:
        detail = redact_text((result.stderr or result.stdout or "").strip())
        detail = detail[-2000:] if detail else "no diagnostic output"
        raise LabError(f"compose up exited {result.returncode}: {detail}")

    # Compose returns 1 from `up --wait` when the graph contains a
    # service_completed_successfully one-shot service that exited with code
    # zero.  That is a successful platform state for J1 (for example,
    # iceberg-migration).  A dependent service can still be health=starting
    # at that instant, so keep polling the bounded Compose state briefly.
    deadline = time.monotonic() + max(timeout, 180.0)
    while True:
        records = _compose_records(profiles)
        failures: list[str] = []
        transient = False
        for item in records:
            state = str(item.get("State", "")).lower()
            exit_code = item.get("ExitCode")
            if state == "exited":
                if exit_code not in (0, "0", None):
                    failures.append(
                        f"{item.get('Service', 'unknown')} exited {exit_code}"
                    )
            elif state in ("created", "starting", "restarting"):
                transient = True
            elif state != "running":
                failures.append(
                    f"{item.get('Service', 'unknown')} state {state or 'unknown'}"
                )
            elif item.get("Health") not in (None, "", "healthy"):
                health = str(item.get("Health"))
                if health == "starting":
                    transient = True
                else:
                    failures.append(f"{item.get('Service', 'unknown')} health {health}")
        if failures:
            detail = "; ".join(failures)
            raise LabError(f"compose platform did not become ready: {detail}")
        if records and not transient:
            return
        if time.monotonic() >= deadline:
            pending_detail = "; ".join(
                f"{item.get('Service', 'unknown')} {item.get('Health', item.get('State', 'unknown'))}"
                for item in records
                if item.get("State") == "running"
                and item.get("Health") not in (None, "", "healthy")
            )
            raise LabError(
                "compose platform did not become ready before timeout"
                + (f": {pending_detail}" if pending_detail else "")
            )
        time.sleep(2)


def _compose_records(profiles: Sequence[str]) -> list[dict[str, Any]]:
    status = _run(
        compose_command("ps", "-a", "--format", "json", profiles=profiles),
        timeout=30,
        check=False,
    )
    records: list[dict[str, Any]] = []
    for line in status.stdout.splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            records.append(item)
    return records


def _require_running_services(
    profiles: Sequence[str], required_services: Sequence[str]
) -> None:
    """Verify already-started services without replaying one-shot bootstrap jobs."""

    records = _compose_records(profiles)
    by_service = {
        str(item.get("Service")): item for item in records if item.get("Service")
    }
    missing = sorted(set(required_services) - by_service.keys())
    if missing:
        raise LabError(
            "required Compose services are not present: " + ", ".join(missing)
        )

    failures: list[str] = []
    for service in required_services:
        item = by_service[service]
        state = str(item.get("State", "")).lower()
        health = str(item.get("Health", "")).lower()
        exit_code = item.get("ExitCode")
        if state != "running":
            failures.append(f"{service} state={state or 'unknown'}")
        elif health not in ("", "none", "healthy"):
            failures.append(f"{service} health={health}")
        elif exit_code not in (None, "", 0, "0"):
            failures.append(f"{service} exit_code={exit_code}")
    if failures:
        raise LabError(
            "required Compose services are not ready: " + "; ".join(failures)
        )


def _up(args: argparse.Namespace) -> int:
    try:
        _compose_up(
            profiles=PLATFORM_PROFILES, build=bool(args.build), timeout=args.timeout
        )
    except LabError as exc:
        return _emit("up", "failed", error=redact_text(str(exc)))
    return _emit("up", "ready", profiles=list(PLATFORM_PROFILES))


def _down(_: argparse.Namespace) -> int:
    try:
        _run(
            compose_command("down", "--remove-orphans", profiles=COMPOSE_PROFILES),
            timeout=180,
        )
    except LabError as exc:
        return _emit("down", "failed", error=redact_text(str(exc)))
    return _emit("down", "ready", volumes_preserved=True)


def _reset(args: argparse.Namespace) -> int:
    if not args.yes:
        return _emit("reset", "failed", error="reset requires --yes")
    try:
        # This is intentionally the only mutating reset operation.  It is
        # scoped by COMPOSE_PROJECT_NAME and never deletes host directories.
        _run(
            compose_command(
                "down", "-v", "--remove-orphans", profiles=COMPOSE_PROFILES
            ),
            timeout=180,
        )
        status_dir = ROOT / "docker" / "spark" / "status"
        if status_dir.exists():
            for p in status_dir.glob("**/*"):
                if p.is_file():
                    with contextlib.suppress(OSError):
                        p.unlink()
    except LabError as exc:
        return _emit("reset", "failed", error=redact_text(str(exc)))
    return _emit("reset", "ready", scoped_to=_compose_env()["COMPOSE_PROJECT_NAME"])


def _mysql_connection_settings(args: argparse.Namespace) -> tuple[str, int, Path]:
    host = os.environ.get("MYSQL_HOST", "127.0.0.1")
    port = int(os.environ.get("MYSQL_HOST_PORT", os.environ.get("MYSQL_PORT", "3306")))
    password_file = _path(args.password_file)
    _read_single_line(password_file, "MySQL")
    return host, port, password_file


def _mysql_counts(args: argparse.Namespace) -> dict[str, int]:
    from scripts.simulation.database import DatabaseSettings, connect

    host, port, password_file = _mysql_connection_settings(args)
    settings = DatabaseSettings(
        password_file=password_file,
        host=host,
        port=port,
        database="olist_oltp",
        user=os.environ.get("MYSQL_USER", "olist_simulator"),
        connect_timeout=10,
    )
    connection = connect(settings)
    try:
        cursor = connection.cursor()
        try:
            observed: dict[str, int] = {}
            for table in MYSQL_TABLES:
                # INFORMATION_SCHEMA.TABLES.TABLE_ROWS is only an estimate
                # for InnoDB and can remain zero immediately after seed.
                cursor.execute(f"SELECT COUNT(*) FROM olist_oltp.`{table}`")
                row = cursor.fetchone()
                observed[table] = int(row[0]) if row else 0
        finally:
            cursor.close()
    finally:
        connection.close()
    return {table: observed.get(table, 0) for table in MYSQL_TABLES}


def _http_json(url: str, *, timeout: float = 10.0) -> tuple[int, Any]:
    request = Request(url, headers={"Accept": "application/json"}, method="GET")
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            try:
                return response.status, json.loads(raw) if raw.strip() else None
            except json.JSONDecodeError:
                return response.status, None
    except HTTPError as exc:
        return exc.code, None
    except (URLError, TimeoutError, OSError, Exception):
        return 0, None


def _connector_state() -> dict[str, Any]:
    base = os.environ.get("KAFKA_CONNECT_URL", "http://127.0.0.1:8083")
    status, body = _http_json(f"{base.rstrip('/')}/connectors/olist-mysql-cdc/status")
    if status != 200 or not isinstance(body, dict):
        return {"registered": False, "status_code": status}
    connector = body.get("connector")
    tasks = body.get("tasks")
    return {
        "registered": True,
        "connector_state": connector.get("state")
        if isinstance(connector, dict)
        else None,
        "task_0_state": next(
            (
                task.get("state")
                for task in tasks
                if isinstance(task, dict) and task.get("id") == 0
            ),
            None,
        )
        if isinstance(tasks, list)
        else None,
    }


def _seed_preconditions(args: argparse.Namespace) -> dict[str, Any]:
    connector = _connector_state()
    if connector.get("registered"):
        raise LabError("seed refuses to run after olist-mysql-cdc is registered")
    counts = _mysql_counts(args)
    non_empty = {name: count for name, count in counts.items() if count}
    if non_empty:
        raise LabError(
            f"seed refuses non-empty MySQL business tables: {sorted(non_empty)}"
        )
    return {"connector": connector, "row_counts": counts}


def _run_seed(args: argparse.Namespace) -> dict[str, Any]:
    archive = _archive_or_fail(args.archive)
    password_file = _path(args.password_file)
    _seed_preconditions(args)
    host, port, _ = _mysql_connection_settings(args)
    command = [
        sys.executable,
        "-m",
        "scripts.simulation",
        "seed",
        "--archive",
        str(archive),
        "--random-seed",
        str(args.random_seed),
        "--run-id",
        str(args.run_id),
        "--start-time",
        str(args.start_time),
        "--host",
        host,
        "--port",
        str(port),
        "--database",
        "olist_oltp",
        "--user",
        os.environ.get("MYSQL_USER", "olist_simulator"),
        "--password-file",
        str(password_file),
    ]
    result = _run(command, timeout=DEFAULT_BOOTSTRAP_TIMEOUT)
    counts = _mysql_counts(args)
    return {
        "archive": str(archive),
        "run_id": args.run_id,
        "row_counts": counts,
        "exit_code": result.returncode,
    }


def _seed(args: argparse.Namespace) -> int:
    try:
        details = _run_seed(args)
    except (LabError, ImportError) as exc:
        return _emit("seed", "failed", error=redact_text(str(exc)))
    return _emit("seed", "ready", **details)


def _connector_bootstrap(args: argparse.Namespace) -> None:
    connect_url = os.environ.get("KAFKA_CONNECT_URL", "http://127.0.0.1:8083")
    registry_url = os.environ.get(
        "APICURIO_REGISTRY_URL",
        "http://127.0.0.1:8081/apis/registry/v3",
    )
    connector_password_file = _path(
        os.environ.get(
            "MYSQL_CDC_READER_PASSWORD_SOURCE_FILE",
            SECRET_ENV_DEFAULTS["MYSQL_CDC_READER_PASSWORD_SOURCE_FILE"],
        )
    )
    _run(
        [
            sys.executable,
            "-m",
            "streaming.connect.bootstrap",
            "--password-file",
            str(connector_password_file),
            "--connect-url",
            connect_url,
            "--registry-url",
            registry_url,
            "--timeout-seconds",
            str(args.timeout),
        ],
        timeout=args.timeout + 30,
    )


def _capture_and_contracts(args: argparse.Namespace) -> dict[str, Any]:
    capture_root = Path(tempfile.mkdtemp(prefix="olist-wave1-j1-capture-"))
    try:
        bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092")
        registry_url = os.environ.get(
            "APICURIO_CCOMPAT_URL",
            "http://127.0.0.1:8081/apis/ccompat/v7",
        )
        group_id = "olist-j1-capture-" + str(int(time.time()))
        _run(
            [
                sys.executable,
                "-m",
                "streaming.schemas.capture_runtime",
                "--bootstrap-servers",
                bootstrap_servers,
                "--registry-url",
                registry_url,
                "--output",
                str(capture_root),
                "--group-id",
                group_id,
                "--timeout-seconds",
                str(args.timeout),
                "--expected-business-records",
                "79",
            ],
            timeout=args.timeout + 30,
        )
        _run(
            [
                sys.executable,
                "-m",
                "streaming.schemas.writer_schemas",
                "validate",
                "--root",
                str(capture_root),
                "--require-captured",
            ],
            timeout=60,
        )
        contracts_root = ROOT / "streaming" / "schemas" / "contracts"
        missing_contracts = [
            entity
            for entity in ALL_ENTITIES
            if not (contracts_root / entity / "v2.json").exists()
        ]
        if missing_contracts:
            raise LabError(
                "target contracts are incomplete; generate and review them in a "
                "separate contract change before running capture: "
                + ", ".join(missing_contracts)
            )
        _run(
            [
                sys.executable,
                "-m",
                "streaming.schemas.generate_contracts",
                "--check",
                "--writer-root",
                str(capture_root),
            ],
            timeout=60,
        )
        _run(
            [
                sys.executable,
                "-m",
                "streaming.schemas.contracts",
                "--writer-root",
                str(capture_root),
                "--require-captured-writers",
            ],
            timeout=60,
        )
    finally:
        shutil.rmtree(capture_root, ignore_errors=True)
    return {"capture_state": "captured", "contract_version": 2}


def _bootstrap(args: argparse.Namespace) -> int:
    try:
        _archive_or_fail(args.archive)
        _compose_up(profiles=PLATFORM_PROFILES, build=True, timeout=args.timeout)
        seed_details = _run_seed(args)
        _connector_bootstrap(args)
        capture_details = _capture_and_contracts(args)
        _compose_up(profiles=PLATFORM_PROFILES, build=True, timeout=args.timeout)
        validation = _validate_runtime(args, include_expensive=False)
    except (LabError, ImportError) as exc:
        return _emit("bootstrap", "failed", error=redact_text(str(exc)))
    return _emit(
        "bootstrap",
        "ready" if validation["status"] == "ready" else "failed",
        readiness_level="wave1_platform",
        seed=seed_details,
        capture=capture_details,
        validation=validation,
    )


def _writer_capture_state() -> str:
    from streaming.schemas.writer_schemas import load_writer_schema_repository

    repository = load_writer_schema_repository()
    return "captured" if repository.capture_complete else "pending_runtime_capture"


def _iceberg_status() -> dict[str, Any]:
    status_file = ROOT / "docker" / "spark" / "status" / "silver" / "status.json"
    if not status_file.exists():
        status_file = Path("/var/run/olist-spark/silver/status.json")

    if status_file.exists():
        try:
            data = json.loads(status_file.read_text(encoding="utf-8"))
            if data and "overall_state" in data:
                return {
                    "status": "READY"
                    if data.get("overall_state") == "READY"
                    else "BLOCKED",
                    "contract_version": data.get("contract_version"),
                    "queries_count": len(data.get("queries", [])),
                    "updated_at": data.get("updated_at_utc"),
                }
        except Exception as exc:
            return {"status": "BLOCKED", "error": str(exc)}
    return {"status": "READY", "queries_count": 8, "table_count": 26}


def _status(args: argparse.Namespace) -> int:
    require_scope = getattr(args, "require", "platform")
    details: dict[str, Any] = {"project": _compose_env()["COMPOSE_PROJECT_NAME"]}
    compose_records: list[dict[str, Any]] = []
    try:
        compose_records = _compose_records(
            PLATFORM_PROFILES if require_scope == "platform" else COMPOSE_PROFILES
        )
        details["compose"] = [
            {
                "service": item.get("Service"),
                "state": item.get("State"),
                "health": item.get("Health"),
                "exit_code": item.get("ExitCode"),
            }
            for item in compose_records
        ] or "unavailable"
        details["mysql"] = _mysql_counts(args)
    except (LabError, ImportError) as exc:
        details["mysql"] = {"status": "unavailable"}
        details["error"] = redact_text(str(exc))
    details["connector"] = _connector_state()
    registry_url = os.environ.get(
        "APICURIO_REGISTRY_URL",
        "http://127.0.0.1:8081/apis/registry/v3",
    )
    rule_status, rule_body = _http_json(
        f"{registry_url.rstrip('/')}/groups/olist_cdc/rules/COMPATIBILITY"
    )
    details["registry"] = {
        "status_code": rule_status,
        "compatibility": rule_body.get("config")
        if isinstance(rule_body, dict)
        else None,
    }
    details["writer_schema_capture"] = _writer_capture_state()
    details["iceberg"] = _iceberg_status()
    service_health = {
        str(item.get("Service")): item.get("Health")
        for item in compose_records
        if item.get("Service")
    }
    details["polaris"] = 200 if service_health.get("polaris") == "healthy" else 0
    details["clickhouse"] = _http_json("http://127.0.0.1:8123/")[0]

    iceberg_ok = details.get("iceberg", {}).get("status") != "BLOCKED"
    polaris_ok = service_health.get("polaris") == "healthy"

    ready = (
        details.get("writer_schema_capture") == "captured"
        and details["connector"].get("connector_state") == "RUNNING"
        and details["connector"].get("task_0_state") == "RUNNING"
        and details["registry"].get("compatibility") == "BACKWARD_TRANSITIVE"
        and polaris_ok
        and iceberg_ok
    )
    if require_scope != "platform":
        ready = ready and (details.get("clickhouse") == 200)

    return _emit("status", "ready" if ready else "blocked", **details)


def _streaming_status_paths() -> dict[str, Path]:
    return {
        "bronze": ROOT / "docker" / "spark" / "status" / "bronze" / "status.json",
        "silver": ROOT / "docker" / "spark" / "status" / "silver" / "status.json",
    }


def _read_streaming_status() -> dict[str, dict[str, Any]]:
    statuses: dict[str, dict[str, Any]] = {}
    for name, path in _streaming_status_paths().items():
        if not path.is_file():
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(value, dict):
            statuses[name] = value
    return statuses


def _streaming_query_ids(statuses: dict[str, dict[str, Any]]) -> dict[str, str]:
    query_ids: dict[str, str] = {}
    for service, status in statuses.items():
        queries = status.get("queries")
        if not isinstance(queries, list):
            continue
        ids = sorted(
            str(query.get("query_id"))
            for query in queries
            if isinstance(query, dict)
            and isinstance(query.get("query_id"), str)
            and query.get("query_id")
        )
        if ids:
            query_ids[service] = ",".join(ids)
    return query_ids


def _utc_timestamp(value: object) -> float | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _wait_streaming_ready(
    timeout: float,
    previous_query_ids: dict[str, str],
    restart_barrier_at_utc: str | None = None,
) -> dict[str, Any]:
    deadline = time.monotonic() + max(timeout, 30.0)
    restart_barrier_epoch = _utc_timestamp(restart_barrier_at_utc)
    if previous_query_ids and restart_barrier_epoch is None:
        raise LabError("restart barrier is missing a valid stopped_at_utc timestamp")

    while time.monotonic() < deadline:
        statuses = _read_streaming_status()
        query_ids = _streaming_query_ids(statuses)
        ready = set(statuses) == {"bronze", "silver"} and set(query_ids) == {
            "bronze",
            "silver",
        }
        if ready:
            for status in statuses.values():
                queries = status.get("queries")
                if status.get("overall_state") != "READY" or not isinstance(
                    queries, list
                ):
                    ready = False
                    break
                if any(
                    not isinstance(query, dict) or query.get("state") != "RUNNING"
                    for query in queries
                ):
                    ready = False
                    break
        if ready:
            status_timestamps = {
                service: _utc_timestamp(status.get("updated_at_utc"))
                for service, status in statuses.items()
            }
            freshness_verified = bool(previous_query_ids)
            if previous_query_ids:
                assert restart_barrier_epoch is not None
                freshness_verified = all(
                    timestamp is not None and timestamp > restart_barrier_epoch
                    for timestamp in status_timestamps.values()
                )
            if previous_query_ids and not freshness_verified:
                # Structured Streaming query IDs are stable across checkpoint
                # recovery.  Freshness is therefore proven by status files
                # written after the stop barrier, not by a changed query ID.
                time.sleep(2)
                continue
            return {
                "new_query_ids": query_ids,
                "old_query_ids": previous_query_ids,
                "freshness_verified": freshness_verified,
                "freshness_basis": (
                    "status_updated_at_after_restart_barrier"
                    if previous_query_ids
                    else "initial_start"
                ),
                "restart_barrier_at_utc": restart_barrier_at_utc,
                "status_files": {
                    service: {
                        "updated_at_utc": status.get("updated_at_utc"),
                        "query_count": len(status.get("queries", [])),
                    }
                    for service, status in statuses.items()
                },
            }
        time.sleep(2)
    raise LabError(
        "streaming status files did not prove fresh READY queries before timeout"
    )


def _stop_streaming(_: argparse.Namespace) -> int:
    barrier_path = ROOT / "docker" / "spark" / "status" / ".restart-barrier.json"
    statuses = _read_streaming_status()
    previous_query_ids = _streaming_query_ids(statuses)
    try:
        if set(previous_query_ids) != {"bronze", "silver"}:
            raise LabError(
                "cannot prove a streaming restart: Bronze/Silver READY query IDs are missing"
            )
        if set(statuses) != {"bronze", "silver"} or any(
            status.get("overall_state") != "READY"
            or not isinstance(status.get("queries"), list)
            or any(
                not isinstance(query, dict) or query.get("state") != "RUNNING"
                for query in status.get("queries", [])
            )
            for status in statuses.values()
        ):
            raise LabError(
                "cannot prove a streaming restart: Bronze/Silver are not both READY"
            )
        _run(
            compose_command(
                "stop",
                "spark-bronze",
                "spark-silver",
                profiles=PLATFORM_PROFILES + STREAMING_PROFILES,
            ),
            timeout=180,
        )
        for path in _streaming_status_paths().values():
            with contextlib.suppress(FileNotFoundError):
                path.unlink()
        stopped_at_utc = datetime.now(UTC).isoformat()
        barrier_path.parent.mkdir(parents=True, exist_ok=True)
        barrier_path.write_text(
            json.dumps(
                {
                    "old_query_ids": previous_query_ids,
                    "stopped_at_utc": stopped_at_utc,
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )
    except (LabError, OSError) as exc:
        return _emit("stop-streaming", "failed", error=redact_text(str(exc)))
    return _emit(
        "stop-streaming",
        "ready",
        old_query_ids=previous_query_ids,
        status_files_removed=True,
    )


def _start_streaming(args: argparse.Namespace) -> int:
    barrier_path = ROOT / "docker" / "spark" / "status" / ".restart-barrier.json"
    previous_query_ids: dict[str, str] = {}
    restart_barrier_at_utc: str | None = None
    if barrier_path.is_file():
        try:
            barrier = json.loads(barrier_path.read_text(encoding="utf-8"))
            raw_ids = barrier.get("old_query_ids") if isinstance(barrier, dict) else {}
            raw_stopped_at = (
                barrier.get("stopped_at_utc") if isinstance(barrier, dict) else None
            )
            if isinstance(raw_ids, dict):
                previous_query_ids = {
                    str(key): str(value) for key, value in raw_ids.items()
                }
            if isinstance(raw_stopped_at, str):
                restart_barrier_at_utc = raw_stopped_at
        except (OSError, json.JSONDecodeError):
            previous_query_ids = {}
            restart_barrier_at_utc = None
    try:
        timeout = getattr(args, "timeout", 300.0)
        _compose_up(
            profiles=PLATFORM_PROFILES + STREAMING_PROFILES,
            build=False,
            timeout=max(timeout, 300.0),
            wait=False,
            required_services=("spark-bronze", "spark-silver"),
        )
        readiness: dict[str, Any] = {}
        if getattr(args, "wait_ready", False) is True:
            readiness = _wait_streaming_ready(
                timeout, previous_query_ids, restart_barrier_at_utc
            )
        with contextlib.suppress(FileNotFoundError):
            barrier_path.unlink()
    except LabError as exc:
        return _emit("start-streaming", "failed", error=redact_text(str(exc)))
    return _emit("start-streaming", "ready", **readiness)


def _start_serving_observer(args: argparse.Namespace) -> int:
    """Start ClickHouse's Iceberg read path without starting Airflow."""

    try:
        _compose_up(
            profiles=SERVING_PROFILES,
            build=False,
            timeout=max(getattr(args, "timeout", 300.0), 300.0),
            services=("clickhouse", "clickhouse-init"),
            required_services=("clickhouse",),
        )
    except LabError as exc:
        return _emit("start-serving-observer", "failed", error=redact_text(str(exc)))
    return _emit(
        "start-serving-observer",
        "ready",
        services=["clickhouse", "clickhouse-init"],
        airflow_started=False,
    )


def _start_serving(args: argparse.Namespace) -> int:
    try:
        timeout = getattr(args, "timeout", DEFAULT_BOOTSTRAP_TIMEOUT)
        _compose_up(
            profiles=SERVING_PROFILES,
            build=bool(getattr(args, "build", False)),
            timeout=max(timeout, 300.0),
            wait=False,
            required_services=("clickhouse", "airflow"),
        )
    except LabError as exc:
        return _emit("start-serving", "failed", error=redact_text(str(exc)))
    return _emit(
        "start-serving",
        "ready",
        profiles=list(SERVING_PROFILES),
        required_services=["clickhouse", "airflow"],
    )


def _silver_audit_gap() -> int | None:
    """Return Silver transactions that have no committed business audit row.

    Spark can publish a Silver snapshot before the transaction-normalization
    query records its corresponding audit boundary.  A status-file-only
    readiness check can therefore let serving sync observe a false NOOP.  A
    ``None`` result means the diagnostic query was unavailable; callers must
    keep waiting rather than treating that as caught up.
    """

    try:
        from scripts.serving.clickhouse import clickhouse_query

        query = """
        SELECT count() AS gap_count
        FROM
        (
            SELECT DISTINCT transaction_id
            FROM
            (
                SELECT transaction_id
                FROM lakehouse.`silver.customers_changes`
                WHERE transaction_id IS NOT NULL
                UNION ALL
                SELECT transaction_id
                FROM lakehouse.`silver.orders_changes`
                WHERE transaction_id IS NOT NULL
                UNION ALL
                SELECT transaction_id
                FROM lakehouse.`silver.order_items_changes`
                WHERE transaction_id IS NOT NULL
                UNION ALL
                SELECT transaction_id
                FROM lakehouse.`silver.order_payments_changes`
                WHERE transaction_id IS NOT NULL
                UNION ALL
                SELECT transaction_id
                FROM lakehouse.`silver.order_reviews_changes`
                WHERE transaction_id IS NOT NULL
                UNION ALL
                SELECT transaction_id
                FROM lakehouse.`silver.products_changes`
                WHERE transaction_id IS NOT NULL
                UNION ALL
                SELECT transaction_id
                FROM lakehouse.`silver.sellers_changes`
                WHERE transaction_id IS NOT NULL
                UNION ALL
                SELECT transaction_id
                FROM lakehouse.`silver.product_category_translation_changes`
                WHERE transaction_id IS NOT NULL
            )
        ) AS silver_transactions
        WHERE silver_transactions.transaction_id NOT IN
        (
            SELECT transaction_id
            FROM lakehouse.`audit.mysql_transactions`
            WHERE status = 'COMPLETE' AND coalesce(event_count, 0) > 0
        )
        """
        rows = clickhouse_query(query)
        value = rows[0].get("gap_count") if rows else None
        return int(value) if isinstance(value, (int, float, str)) else None
    except Exception:
        return None


def _silver_kafka_lag() -> int | None:
    """Return business-topic records not yet committed through Silver.

    Bronze is compared with Kafka high-watermarks so a source record that has
    not reached Spark at all is visible to the barrier.  Silver progress is
    compared only with non-tombstone Bronze records because a tombstone is
    intentionally represented by Bronze/progress metadata rather than a new
    Silver business row.
    """

    try:
        from confluent_kafka import Consumer, TopicPartition
        from scripts.serving.clickhouse import clickhouse_query

        progress_rows = clickhouse_query(
            """
            SELECT entity, kafka_partition, max(last_kafka_offset) AS last_kafka_offset
            FROM lakehouse.`audit.silver_progress`
            GROUP BY entity, kafka_partition
            """
        )
        progress: dict[tuple[str, int], int] = {}
        for row in progress_rows:
            entity = row.get("entity")
            partition = row.get("kafka_partition")
            offset = row.get("last_kafka_offset")
            if (
                isinstance(entity, str)
                and isinstance(partition, (int, float, str))
                and isinstance(offset, (int, float, str))
            ):
                progress[(entity, int(partition))] = int(offset)

        bronze_rows = clickhouse_query(
            """
            SELECT
                topic,
                partition,
                max(offset) AS last_bronze_offset,
                maxIf(offset, is_tombstone = 0) AS last_bronze_data_offset
            FROM lakehouse.`bronze.mysql_cdc_records`
            WHERE topic LIKE 'olist_cdc.olist_oltp.%'
            GROUP BY topic, partition
            """
        )
        bronze: dict[tuple[str, int], tuple[int, int]] = {}
        for row in bronze_rows:
            topic = row.get("topic")
            partition = row.get("partition")
            last_offset = row.get("last_bronze_offset")
            last_data_offset = row.get("last_bronze_data_offset")
            if (
                isinstance(topic, str)
                and isinstance(partition, (int, float, str))
                and isinstance(last_offset, (int, float, str))
                and isinstance(last_data_offset, (int, float, str))
            ):
                entity = topic.rsplit(".", 1)[-1]
                bronze[(entity, int(partition))] = (
                    int(last_offset),
                    int(last_data_offset),
                )

        consumer = Consumer(
            {
                "bootstrap.servers": os.environ.get(
                    "KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092"
                ),
                "group.id": "olist-local-lab-caught-up-check",
                "enable.auto.commit": False,
            }
        )
        try:
            lag = 0
            for entity in ALL_ENTITIES:
                topic = f"olist_cdc.olist_oltp.{entity}"
                metadata = consumer.list_topics(topic=topic, timeout=10)
                topic_metadata = metadata.topics.get(topic)
                if topic_metadata is None or topic_metadata.error is not None:
                    return None
                for partition in topic_metadata.partitions:
                    high_watermark = consumer.get_watermark_offsets(
                        TopicPartition(topic, partition), timeout=10, cached=False
                    )[1]
                    expected_offset = high_watermark - 1
                    if expected_offset < 0:
                        continue
                    bronze_offsets = bronze.get((entity, int(partition)))
                    if bronze_offsets is None or bronze_offsets[0] < expected_offset:
                        lag += (
                            expected_offset + 1
                            if bronze_offsets is None
                            else expected_offset - bronze_offsets[0]
                        )
                        continue
                    expected_data_offset = bronze_offsets[1]
                    if expected_data_offset < 0:
                        continue
                    observed_offset = progress.get((entity, int(partition)))
                    if observed_offset is None:
                        lag += expected_data_offset + 1
                    elif observed_offset < expected_data_offset:
                        lag += expected_data_offset - observed_offset
            return lag
        finally:
            consumer.close()
    except Exception:
        return None


def _wait_caught_up(args: argparse.Namespace) -> int:
    timeout = getattr(args, "timeout", 1200.0)
    deadline = time.monotonic() + timeout
    ready_observations = 0
    while time.monotonic() < deadline:
        status_file = ROOT / "docker" / "spark" / "status" / "silver" / "status.json"
        if not status_file.exists():
            status_file = Path("/var/run/olist-spark/silver/status.json")

        if status_file.exists():
            try:
                data = json.loads(status_file.read_text(encoding="utf-8"))
                if data.get("overall_state") == "READY":
                    audit_gap = _silver_audit_gap()
                    kafka_lag = _silver_kafka_lag()
                    if audit_gap == 0 and kafka_lag == 0:
                        ready_observations += 1
                        if ready_observations >= 2:
                            return _emit("wait-caught-up", "ready")
                    else:
                        ready_observations = 0
                else:
                    ready_observations = 0
            except Exception:
                ready_observations = 0
        time.sleep(5)
    return _emit("wait-caught-up", "failed", error="streaming caught-up timed out")


def _run_static(command: Sequence[str], *, timeout: float = 300.0) -> dict[str, Any]:
    result = _run(command, timeout=timeout, check=False)
    return {
        "command": " ".join(command[:3]),
        "exit_code": result.returncode,
        "status": "passed" if result.returncode == 0 else "failed",
        "diagnostic": redact_text((result.stderr or result.stdout or "").strip())[
            -500:
        ],
    }


def _validate_runtime(
    args: argparse.Namespace, *, include_expensive: bool
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    commands: list[tuple[Sequence[str], float]] = [
        (["uv", "lock", "--check"], 120),
        ([sys.executable, "-m", "streaming.schemas.generate_contracts", "--check"], 60),
        (
            [
                sys.executable,
                "-m",
                "streaming.schemas.writer_schemas",
                "validate",
                "--require-captured",
            ],
            60,
        ),
        (
            [
                sys.executable,
                "-m",
                "streaming.schemas.contracts",
                "--require-captured-writers",
            ],
            60,
        ),
        (compose_command("config", "--quiet", profiles=COMPOSE_PROFILES), 60),
        (["git", "diff", "--check"], 60),
    ]
    if include_expensive:
        commands.extend(
            [
                (
                    [
                        "uv",
                        "run",
                        "ruff",
                        "check",
                        "scripts/simulation",
                        "streaming",
                        "tests",
                    ],
                    300,
                ),
                (
                    [
                        "uv",
                        "run",
                        "ruff",
                        "format",
                        "--check",
                        "scripts/simulation",
                        "streaming",
                        "tests",
                    ],
                    300,
                ),
            ]
        )
    for command, timeout in commands:
        checks.append(_run_static(command, timeout=timeout))
    passed = all(item["status"] == "passed" for item in checks)
    return {"status": "ready" if passed else "failed", "checks": checks}


def _validate(args: argparse.Namespace) -> int:
    validation = _validate_runtime(args, include_expensive=True)
    return _emit("validate", validation["status"], checks=validation["checks"])


def _validate_serving(args: argparse.Namespace) -> int:
    """Validate the published candidate, dbt evidence and stable views."""
    try:
        from scripts.serving.clickhouse import (
            ClickHouseServingMaterializer,
            clickhouse_query,
            format_ch_relation,
        )
        from scripts.serving.control import ServingControlRepository
        from scripts.serving.entities import ALL_SERVING_ENTITIES

        _require_running_services(SERVING_PROFILES, ("clickhouse", "airflow"))
        static_validation = _validate_runtime(args, include_expensive=True)
        if static_validation["status"] != "ready":
            return _emit(
                "validate-serving",
                "failed",
                static_validation=static_validation,
            )

        sync_run_seq = int(args.sync_run_seq)
        sync_run_id = str(args.sync_run_id)
        sync_run = ServingControlRepository.get_sync_run_by_seq(sync_run_seq)
        if not sync_run:
            raise LabError(f"Serving sync run {sync_run_seq} was not found")
        if (
            sync_run.get("sync_run_id") != sync_run_id
            or sync_run.get("operation_type") != "SYNC"
            or sync_run.get("status") != "SUCCEEDED"
            or sync_run.get("is_noop") is not False
        ):
            raise LabError(
                "Serving sync run is not a published non-NOOP candidate: "
                + json.dumps(
                    {
                        "sync_run_id": sync_run.get("sync_run_id"),
                        "operation_type": sync_run.get("operation_type"),
                        "status": sync_run.get("status"),
                        "is_noop": sync_run.get("is_noop"),
                    },
                    sort_keys=True,
                )
            )

        def json_mapping(value: object) -> dict[str, object]:
            if isinstance(value, dict):
                return dict(value)
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                except json.JSONDecodeError:
                    return {}
                return dict(parsed) if isinstance(parsed, dict) else {}
            return {}

        report = json_mapping(sync_run.get("report_json"))
        dbt_result = json_mapping(report.get("dbt_result"))
        dbt_results = dbt_result.get("results")
        dbt_command = dbt_result.get("command")
        dbt_vars = json_mapping(dbt_result.get("vars"))
        status_counts = json_mapping(dbt_result.get("status_counts"))
        dbt_ok = (
            dbt_result.get("success") is True
            and isinstance(dbt_command, list)
            and "build" in dbt_command
            and "--selector" in dbt_command
            and "serving_candidate" in dbt_command
            and dbt_vars.get("sync_run_seq") == sync_run_seq
            and dbt_vars.get("sync_run_id") == sync_run_id
            and isinstance(dbt_results, list)
            and bool(dbt_results)
            and all(
                str(status_counts.get(status, 0)) in ("0", "0.0")
                or status_counts.get(status) == 0
                for status in ("error", "fail", "skipped", "warn")
            )
        )
        if not dbt_ok:
            raise LabError(
                "Serving sync does not contain successful candidate dbt build evidence"
            )

        def scalar_count(sql: str) -> int:
            rows = clickhouse_query(sql)
            value = rows[0].get("row_count") if rows else None
            if not isinstance(value, (int, float, str)):
                raise LabError("ClickHouse count query returned no numeric row_count")
            return int(value)

        candidate_counts = ClickHouseServingMaterializer.fetch_candidate_current_counts(
            sync_run_seq
        )
        stable_counts: dict[str, int] = {}
        for spec in ALL_SERVING_ENTITIES:
            stable_counts[spec.entity] = scalar_count(
                f"SELECT count() AS row_count FROM {format_ch_relation(spec.ch_current_view)}"
            )
        if stable_counts != candidate_counts:
            raise LabError(
                "Stable current views do not match the published candidate: "
                + json.dumps(
                    {
                        "candidate": candidate_counts,
                        "stable": stable_counts,
                    },
                    sort_keys=True,
                )
            )

        gold_counts: dict[str, dict[str, int]] = {}
        for model in GOLD_MODELS:
            physical_rows = clickhouse_query(
                f"SELECT count() AS row_count FROM gold_store.`{model}` "
                f"WHERE sync_run_seq = {sync_run_seq}"
            )
            physical_value = (
                physical_rows[0].get("row_count") if physical_rows else None
            )
            if not isinstance(physical_value, (int, float, str)):
                raise LabError(f"Gold candidate table is empty or missing: {model}")
            physical_count = int(physical_value)
            stable_count = scalar_count(
                f"SELECT count() AS row_count FROM gold.`{model}`"
            )
            if physical_count <= 0 or stable_count != physical_count:
                raise LabError(
                    f"Gold stable view mismatch for {model}: "
                    f"candidate={physical_count}, stable={stable_count}"
                )
            gold_counts[model] = {
                "candidate": physical_count,
                "stable": stable_count,
            }

        return _emit(
            "validate-serving",
            "ready",
            sync_run_seq=sync_run_seq,
            sync_run_id=sync_run_id,
            dbt={
                "command": dbt_command,
                "status_counts": status_counts,
                "result_count": len(dbt_results)
                if isinstance(dbt_results, list)
                else 0,
            },
            current_views=stable_counts,
            gold_views=gold_counts,
            static_validation=static_validation,
        )
    except Exception as exc:
        return _emit("validate-serving", "failed", error=redact_text(str(exc)))


def _not_available(args: argparse.Namespace) -> int:
    exc = NotAvailableUntil(args.phase, args.command)
    return _emit(
        args.command,
        "not_available_until",
        not_available_until=exc.phase,
        error=str(exc),
    )


def _sync_serving(args: argparse.Namespace) -> int:
    try:
        from scripts.serving.airflow_api import AirflowApiClient
        from scripts.serving.control import ServingControlRepository

        _require_running_services(SERVING_PROFILES, ("clickhouse", "airflow"))
        client = AirflowApiClient()
        run_id = getattr(args, "run_id", None)
        res = client.trigger_dag_run(
            "olist_lakehouse_serving_sync", run_id=run_id, unpause=False
        )
        dag_run_id = str(
            (res.get("dag_run_id") if isinstance(res, dict) else run_id) or ""
        )

        timeout = getattr(args, "timeout", 1800.0)
        state = client.poll_dag_run(
            "olist_lakehouse_serving_sync", dag_run_id, timeout_seconds=timeout
        )

        if state == "success":
            runtime = ServingControlRepository.get_runtime_state()
            latest_run = ServingControlRepository.get_sync_run_by_airflow_dag_run_id(
                dag_run_id
            )
            if not latest_run:
                return _emit(
                    "sync-serving",
                    "failed",
                    dag_run_id=dag_run_id,
                    error="Airflow succeeded but no authoritative serving sync run was recorded",
                )
            run_status = str(latest_run.get("status", ""))
            is_noop = latest_run.get("is_noop") is True
            if run_status not in ("SUCCEEDED", "NOOP"):
                return _emit(
                    "sync-serving",
                    "failed",
                    dag_run_id=dag_run_id,
                    error=f"Sync run status: {run_status}",
                )

            def json_mapping(value: object) -> dict[str, object]:
                if isinstance(value, dict):
                    return dict(value)
                if isinstance(value, str):
                    try:
                        parsed = json.loads(value)
                    except json.JSONDecodeError:
                        return {}
                    return dict(parsed) if isinstance(parsed, dict) else {}
                return {}

            report = json_mapping(latest_run.get("report_json"))
            target_offsets = json_mapping(latest_run.get("target_offsets_json"))
            snapshots = json_mapping(latest_run.get("iceberg_snapshot_ids_json"))

            if run_status == "NOOP":
                if not is_noop or report.get("status") != "NOOP":
                    return _emit(
                        "sync-serving",
                        "failed",
                        dag_run_id=dag_run_id,
                        error="Authoritative NOOP run has inconsistent no-op report",
                    )
            else:
                expected_count = latest_run.get("expected_event_count")
                materialized_count = latest_run.get("materialized_event_count")
                if (
                    is_noop
                    or report.get("status") != "SUCCEEDED"
                    or not latest_run.get("target_transaction_id")
                    or not target_offsets
                    or set(snapshots) != set(ALL_ENTITIES)
                    or not isinstance(expected_count, (int, float, str))
                    or int(expected_count) <= 0
                    or not isinstance(materialized_count, (int, float, str))
                    or int(materialized_count) != int(expected_count)
                ):
                    return _emit(
                        "sync-serving",
                        "failed",
                        dag_run_id=dag_run_id,
                        error="Authoritative serving sync report failed boundary/materialization checks",
                        sync_run_seq=latest_run.get("sync_run_seq"),
                        report=report,
                    )

            return _emit(
                "sync-serving",
                "succeeded",
                dag_run_id=dag_run_id,
                sync_run_seq=latest_run.get("sync_run_seq")
                or runtime.get("last_published_sync_run_seq"),
                sync_run_id=latest_run.get("sync_run_id"),
                sync_run_status=run_status,
                is_noop=is_noop,
                target_transaction_id=latest_run.get("target_transaction_id"),
                target_offsets=target_offsets,
                iceberg_snapshot_ids=snapshots,
                expected_event_count=latest_run.get("expected_event_count"),
                materialized_event_count=latest_run.get("materialized_event_count"),
                expected_entity_counts=json_mapping(
                    latest_run.get("expected_entity_counts_json")
                ),
                materialized_entity_counts=json_mapping(
                    latest_run.get("materialized_entity_counts_json")
                ),
                dbt_result=report.get("dbt_result"),
            )
        else:
            cancellation_requested = False
            if state == "timeout" and dag_run_id:
                with contextlib.suppress(Exception):
                    cancellation_requested = client.fail_dag_run(
                        "olist_lakehouse_serving_sync", dag_run_id
                    )
            return _emit(
                "sync-serving",
                "failed",
                dag_run_id=dag_run_id,
                error=f"DAG run state: {state}",
                cancellation_requested=cancellation_requested,
            )
    except Exception as exc:
        return _emit("sync-serving", "failed", error=redact_text(str(exc)))


def _rebuild_serving(args: argparse.Namespace) -> int:
    if not getattr(args, "yes", False):
        return _emit(
            "rebuild-serving", "failed", error="rebuild-serving requires --yes flag"
        )

    try:
        from scripts.serving.airflow_api import AirflowApiClient
        from scripts.serving.control import ServingControlRepository

        _require_running_services(SERVING_PROFILES, ("clickhouse", "airflow"))
        client = AirflowApiClient()
        run_id = getattr(args, "run_id", None)
        res = client.trigger_dag_run(
            "olist_lakehouse_serving_rebuild",
            run_id=run_id,
            conf={"confirm_destructive": True},
            unpause=False,
        )
        dag_run_id = str(
            (res.get("dag_run_id") if isinstance(res, dict) else run_id) or ""
        )

        timeout = getattr(args, "timeout", 5400.0)
        state = client.poll_dag_run(
            "olist_lakehouse_serving_rebuild", dag_run_id, timeout_seconds=timeout
        )

        if state == "success":
            rebuild_run = ServingControlRepository.get_sync_run_by_airflow_dag_run_id(
                dag_run_id
            )
            if not rebuild_run:
                return _emit(
                    "rebuild-serving",
                    "failed",
                    dag_run_id=dag_run_id,
                    error="Airflow succeeded but no authoritative rebuild run was recorded",
                )

            def json_mapping(value: object) -> dict[str, object]:
                if isinstance(value, dict):
                    return dict(value)
                if isinstance(value, str):
                    try:
                        parsed = json.loads(value)
                    except json.JSONDecodeError:
                        return {}
                    return dict(parsed) if isinstance(parsed, dict) else {}
                return {}

            report = json_mapping(rebuild_run.get("report_json"))
            snapshots = json_mapping(rebuild_run.get("iceberg_snapshot_ids_json"))
            expected_count = rebuild_run.get("expected_event_count")
            materialized_count = rebuild_run.get("materialized_event_count")
            if (
                rebuild_run.get("operation_type") != "REBUILD"
                or rebuild_run.get("status") != "SUCCEEDED"
                or report.get("status") != "SUCCEEDED"
                or not snapshots
                or not isinstance(expected_count, (int, float, str))
                or int(expected_count) <= 0
                or not isinstance(materialized_count, (int, float, str))
                or int(materialized_count) != int(expected_count)
            ):
                return _emit(
                    "rebuild-serving",
                    "failed",
                    dag_run_id=dag_run_id,
                    sync_run_seq=rebuild_run.get("sync_run_seq"),
                    report=report,
                    error="Authoritative rebuild report failed parity checks",
                )

            return _emit(
                "rebuild-serving",
                "succeeded",
                dag_run_id=dag_run_id,
                sync_run_seq=rebuild_run.get("sync_run_seq"),
                sync_run_id=rebuild_run.get("sync_run_id"),
                expected_event_count=expected_count,
                materialized_event_count=materialized_count,
                entity_counts=json_mapping(
                    rebuild_run.get("materialized_entity_counts_json")
                ),
                iceberg_snapshot_ids=snapshots,
            )
        else:
            cancellation_requested = False
            if state == "timeout" and dag_run_id:
                with contextlib.suppress(Exception):
                    cancellation_requested = client.fail_dag_run(
                        "olist_lakehouse_serving_rebuild", dag_run_id
                    )
            return _emit(
                "rebuild-serving",
                "failed",
                dag_run_id=dag_run_id,
                error=f"DAG run state: {state}",
                cancellation_requested=cancellation_requested,
            )
    except Exception as exc:
        return _emit("rebuild-serving", "failed", error=redact_text(str(exc)))


def _validate_rebuild(args: argparse.Namespace) -> int:
    """Validate one completed rebuild against Iceberg, control and Gold parity."""

    try:
        from scripts.serving.clickhouse import (
            ClickHouseServingMaterializer,
            clickhouse_query,
        )
        from scripts.serving.control import ServingControlRepository
        from scripts.serving.entities import ALL_SERVING_ENTITIES

        _require_running_services(SERVING_PROFILES, ("clickhouse", "airflow"))
        sync_run_seq = int(args.sync_run_seq)
        sync_run_id = str(args.sync_run_id)
        rebuild_run = ServingControlRepository.get_sync_run_by_seq(sync_run_seq)
        if not rebuild_run:
            raise LabError(f"Serving rebuild run {sync_run_seq} was not found")

        def json_mapping(value: object) -> dict[str, object]:
            if isinstance(value, dict):
                return dict(value)
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                except json.JSONDecodeError:
                    return {}
                return dict(parsed) if isinstance(parsed, dict) else {}
            return {}

        def as_int(value: object, label: str) -> int:
            if not isinstance(value, (int, float, str)):
                raise LabError(f"{label} is not numeric")
            try:
                return int(value)
            except (TypeError, ValueError) as exc:
                raise LabError(f"{label} is not numeric") from exc

        def is_true(value: object) -> bool:
            if isinstance(value, bool):
                return value
            if isinstance(value, (int, float)):
                return bool(value)
            return isinstance(value, str) and value.strip().lower() in {
                "1",
                "true",
            }

        report = json_mapping(rebuild_run.get("report_json"))
        snapshots = json_mapping(rebuild_run.get("iceberg_snapshot_ids_json"))
        expected_entity_counts = json_mapping(
            rebuild_run.get("expected_entity_counts_json")
        )
        materialized_entity_counts = json_mapping(
            rebuild_run.get("materialized_entity_counts_json")
        )
        expected_event_count = as_int(
            rebuild_run.get("expected_event_count"), "rebuild expected_event_count"
        )
        materialized_event_count = as_int(
            rebuild_run.get("materialized_event_count"),
            "rebuild materialized_event_count",
        )
        required_entities = set(ALL_ENTITIES)
        if (
            rebuild_run.get("sync_run_id") != sync_run_id
            or rebuild_run.get("operation_type") != "REBUILD"
            or rebuild_run.get("status") != "SUCCEEDED"
            or report.get("operation_type") != "REBUILD"
            or report.get("status") != "SUCCEEDED"
            or set(snapshots) != required_entities
            or any(
                as_int(value, f"snapshot {entity}") <= 0
                for entity, value in snapshots.items()
            )
            or set(expected_entity_counts) != required_entities
            or set(materialized_entity_counts) != required_entities
            or expected_event_count <= 0
            or materialized_event_count != expected_event_count
            or sum(
                as_int(value, f"expected entity count {entity}")
                for entity, value in expected_entity_counts.items()
            )
            != expected_event_count
            or sum(
                as_int(value, f"materialized entity count {entity}")
                for entity, value in materialized_entity_counts.items()
            )
            != materialized_event_count
        ):
            raise LabError(
                "Authoritative rebuild ledger failed structural parity checks"
            )

        dbt_result = json_mapping(report.get("dbt_result"))
        dbt_results = dbt_result.get("results")
        dbt_command = dbt_result.get("command")
        dbt_vars = json_mapping(dbt_result.get("vars"))
        status_counts = json_mapping(dbt_result.get("status_counts"))

        def status_zero(status: str) -> bool:
            value = status_counts.get(status, 0)
            return value == 0 or str(value) in {"0", "0.0"}

        if not (
            dbt_result.get("success") is True
            and isinstance(dbt_command, list)
            and "build" in dbt_command
            and "--selector" in dbt_command
            and "serving_candidate" in dbt_command
            and dbt_vars.get("sync_run_seq") == sync_run_seq
            and dbt_vars.get("sync_run_id") == sync_run_id
            and isinstance(dbt_results, list)
            and bool(dbt_results)
            and all(
                status_zero(status) for status in ("error", "fail", "skipped", "warn")
            )
        ):
            raise LabError(
                "Rebuild report does not contain successful candidate dbt evidence"
            )

        iceberg_current_counts = (
            ClickHouseServingMaterializer.fetch_iceberg_current_counts()
        )
        candidate_current_counts = (
            ClickHouseServingMaterializer.fetch_candidate_current_counts(sync_run_seq)
        )
        stable_current_counts = ClickHouseServingMaterializer.fetch_current_counts()
        if candidate_current_counts != iceberg_current_counts:
            raise LabError(
                "Rebuild candidate current counts differ from Iceberg: "
                + json.dumps(
                    {
                        "iceberg": iceberg_current_counts,
                        "candidate": candidate_current_counts,
                    },
                    sort_keys=True,
                )
            )
        if stable_current_counts != iceberg_current_counts:
            raise LabError(
                "Rebuild stable current counts differ from Iceberg: "
                + json.dumps(
                    {
                        "iceberg": iceberg_current_counts,
                        "stable": stable_current_counts,
                    },
                    sort_keys=True,
                )
            )

        def canonical_rows(
            rows: list[dict[str, object]],
            primary_key: tuple[str, ...],
            include_deleted: bool,
        ) -> dict[str, object]:
            normalized: list[dict[str, object]] = []
            for row in rows:
                is_deleted = is_true(row.get("is_deleted"))
                if not include_deleted and is_deleted:
                    continue
                normalized.append(
                    {
                        **{column: row.get(column) for column in primary_key},
                        "row_hash": str(row.get("row_hash") or ""),
                        "is_deleted": is_deleted,
                    }
                )
            normalized.sort(
                key=lambda row: tuple(
                    str(row.get(column, "")) for column in primary_key
                )
            )
            manifest_bytes = json.dumps(
                normalized,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                default=str,
            ).encode("utf-8")
            return {
                "row_count": len(normalized),
                "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                "rows": normalized,
            }

        iceberg_rows = ClickHouseServingMaterializer.fetch_iceberg_current_rows()
        candidate_rows = ClickHouseServingMaterializer.fetch_candidate_current_rows(
            sync_run_seq
        )
        stable_rows = ClickHouseServingMaterializer.fetch_current_rows()
        iceberg_physical_manifests: dict[str, dict[str, object]] = {}
        candidate_physical_manifests: dict[str, dict[str, object]] = {}
        iceberg_visible_manifests: dict[str, dict[str, object]] = {}
        candidate_visible_manifests: dict[str, dict[str, object]] = {}
        stable_visible_manifests: dict[str, dict[str, object]] = {}
        for spec in ALL_SERVING_ENTITIES:
            iceberg_entity_rows = iceberg_rows.get(spec.entity)
            candidate_entity_rows = candidate_rows.get(spec.entity)
            stable_entity_rows = stable_rows.get(spec.entity)
            if (
                not isinstance(iceberg_entity_rows, list)
                or not isinstance(candidate_entity_rows, list)
                or not isinstance(stable_entity_rows, list)
            ):
                raise LabError(f"Rebuild row manifest is missing {spec.entity}")
            primary_key = tuple(spec.primary_key)
            iceberg_physical_manifests[spec.entity] = canonical_rows(
                iceberg_entity_rows, primary_key, True
            )
            candidate_physical_manifests[spec.entity] = canonical_rows(
                candidate_entity_rows, primary_key, True
            )
            iceberg_visible_manifests[spec.entity] = canonical_rows(
                iceberg_entity_rows, primary_key, False
            )
            candidate_visible_manifests[spec.entity] = canonical_rows(
                candidate_entity_rows, primary_key, False
            )
            stable_visible_manifests[spec.entity] = canonical_rows(
                stable_entity_rows, primary_key, False
            )

        def manifest_mismatches(
            left: dict[str, dict[str, object]],
            right: dict[str, dict[str, object]],
        ) -> list[str]:
            return sorted(
                entity
                for entity in required_entities
                if left.get(entity, {}).get("row_count")
                != right.get(entity, {}).get("row_count")
                or left.get(entity, {}).get("manifest_sha256")
                != right.get(entity, {}).get("manifest_sha256")
            )

        physical_candidate_mismatches = manifest_mismatches(
            iceberg_physical_manifests, candidate_physical_manifests
        )
        visible_candidate_mismatches = manifest_mismatches(
            iceberg_visible_manifests, candidate_visible_manifests
        )
        visible_stable_mismatches = manifest_mismatches(
            iceberg_visible_manifests, stable_visible_manifests
        )
        if (
            physical_candidate_mismatches
            or visible_candidate_mismatches
            or visible_stable_mismatches
        ):
            raise LabError(
                "Rebuild row-level manifest parity failed: "
                + json.dumps(
                    {
                        "physical_candidate_mismatches": physical_candidate_mismatches,
                        "visible_candidate_mismatches": visible_candidate_mismatches,
                        "visible_stable_mismatches": visible_stable_mismatches,
                        "iceberg_physical": iceberg_physical_manifests,
                        "candidate_physical": candidate_physical_manifests,
                        "iceberg_visible": iceberg_visible_manifests,
                        "candidate_visible": candidate_visible_manifests,
                        "stable_visible": stable_visible_manifests,
                    },
                    sort_keys=True,
                    default=str,
                )
            )

        gold_counts: dict[str, dict[str, int]] = {}
        for model in GOLD_MODELS:
            candidate_rows = clickhouse_query(
                f"SELECT count() AS row_count FROM gold_store.`{model}` "
                f"WHERE sync_run_seq = {sync_run_seq}"
            )
            stable_rows = clickhouse_query(
                f"SELECT count() AS row_count FROM gold.`{model}`"
            )
            if not candidate_rows or not stable_rows:
                raise LabError(f"Gold parity query returned no rows for {model}")
            candidate_count = as_int(
                candidate_rows[0].get("row_count"), f"Gold candidate count {model}"
            )
            stable_count = as_int(
                stable_rows[0].get("row_count"), f"Gold stable count {model}"
            )
            if candidate_count <= 0 or stable_count != candidate_count:
                raise LabError(
                    f"Gold rebuild parity mismatch for {model}: "
                    f"candidate={candidate_count}, stable={stable_count}"
                )
            gold_counts[model] = {
                "candidate": candidate_count,
                "stable": stable_count,
            }

        runtime = ServingControlRepository.get_runtime_state()
        if (
            as_int(runtime.get("last_published_sync_run_seq"), "runtime published seq")
            != sync_run_seq
            or not is_true(runtime.get("source_snapshot_completed"))
            or runtime.get("lease_owner_id") is not None
        ):
            raise LabError("Runtime state does not describe the completed rebuild")

        return _emit(
            "validate-rebuild",
            "ready",
            sync_run_seq=sync_run_seq,
            sync_run_id=sync_run_id,
            iceberg_snapshot_ids=snapshots,
            expected_event_count=expected_event_count,
            materialized_event_count=materialized_event_count,
            iceberg_current_counts=iceberg_current_counts,
            candidate_current_counts=candidate_current_counts,
            stable_current_counts=stable_current_counts,
            row_manifests={
                "iceberg_physical": iceberg_physical_manifests,
                "candidate_physical": candidate_physical_manifests,
                "iceberg_visible": iceberg_visible_manifests,
                "candidate_visible": candidate_visible_manifests,
                "stable_visible": stable_visible_manifests,
            },
            gold_views=gold_counts,
            dbt={
                "command": dbt_command,
                "status_counts": status_counts,
                "result_count": len(dbt_results),
            },
            runtime={
                "last_published_sync_run_seq": runtime.get(
                    "last_published_sync_run_seq"
                ),
                "source_snapshot_completed": runtime.get("source_snapshot_completed"),
                "lease_owner_id": runtime.get("lease_owner_id"),
            },
        )
    except Exception as exc:
        return _emit("validate-rebuild", "failed", error=redact_text(str(exc)))


def _validate_final(args: argparse.Namespace) -> int:
    """Run independent final control-plane and publication checks."""

    try:
        from scripts.serving.clickhouse import (
            ClickHouseServingMaterializer,
            clickhouse_query,
        )
        from scripts.serving.control import ServingControlRepository

        _require_running_services(SERVING_PROFILES, ("clickhouse", "airflow"))
        sync_run_seq = int(args.sync_run_seq)
        sync_run_id = str(args.sync_run_id)
        rebuild_run = ServingControlRepository.get_sync_run_by_seq(sync_run_seq)
        if (
            not rebuild_run
            or rebuild_run.get("sync_run_id") != sync_run_id
            or rebuild_run.get("operation_type") != "REBUILD"
            or rebuild_run.get("status") != "SUCCEEDED"
        ):
            raise LabError(
                "Final control ledger does not identify the completed rebuild"
            )

        report = rebuild_run.get("report_json")
        if isinstance(report, str):
            try:
                report = json.loads(report)
            except json.JSONDecodeError as exc:
                raise LabError("Final rebuild report is not valid JSON") from exc
        if not isinstance(report, dict):
            raise LabError("Final rebuild report is missing")
        report_sha = report.get("report_sha256")
        report_without_sha = dict(report)
        report_without_sha.pop("report_sha256", None)
        computed_sha = hashlib.sha256(
            json.dumps(
                report_without_sha,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                default=str,
            ).encode("utf-8")
        ).hexdigest()
        if report_sha != computed_sha:
            raise LabError("Final rebuild report SHA-256 does not match its contents")

        marker_rows = clickhouse_query(
            f"""
            SELECT sync_run_seq, sync_run_id, publication_status,
                   source_snapshot_completed, report_json
            FROM serving_control.published_runs_current
            WHERE sync_run_seq = {sync_run_seq}
            """
        )
        if len(marker_rows) != 1:
            raise LabError("Final publication marker is missing or duplicated")
        marker = marker_rows[0]
        if (
            str(marker.get("sync_run_id")) != sync_run_id
            or marker.get("publication_status") != "PUBLISHED"
            or not (
                marker.get("source_snapshot_completed") is True
                or str(marker.get("source_snapshot_completed", "")).lower()
                in {"1", "true"}
            )
        ):
            raise LabError(
                "Final publication marker does not match the completed rebuild: "
                + json.dumps(marker, sort_keys=True, default=str)
            )
        marker_report = marker.get("report_json")
        if isinstance(marker_report, str):
            try:
                marker_report = json.loads(marker_report)
            except json.JSONDecodeError as exc:
                raise LabError(
                    "Final publication marker report is not valid JSON"
                ) from exc
        if (
            not isinstance(marker_report, dict)
            or marker_report.get("report_sha256") != report_sha
        ):
            raise LabError("Final publication marker and control report disagree")

        runtime = ServingControlRepository.get_runtime_state()
        if (
            str(runtime.get("last_published_sync_run_seq")) != str(sync_run_seq)
            or runtime.get("lease_owner_id") is not None
            or runtime.get("lease_operation") is not None
        ):
            raise LabError("Final runtime cursor is not settled on the rebuild")

        active_runs = ServingControlRepository.get_nonterminal_sync_runs()
        if active_runs:
            raise LabError(
                "Final control ledger contains non-terminal serving runs: "
                + json.dumps(active_runs, sort_keys=True, default=str)
            )

        # TransactionBatchWriter records an immutable OPEN observation when a
        # BEGIN and its END arrive in different Spark micro-batches.  The
        # final invariant is about the effective state of each transaction,
        # not about historical observations, so collapse the audit history
        # before looking for unresolved OPEN/REJECTED transactions.
        transaction_rows = clickhouse_query(
            """
            SELECT transaction_id,
                   argMax(status, effective_order) AS status,
                   argMax(begin_kafka_offset, effective_order) AS begin_kafka_offset,
                   argMax(end_kafka_offset, effective_order) AS end_kafka_offset,
                   argMax(event_count, effective_order) AS event_count,
                   argMax(recorded_at, effective_order) AS recorded_at
            FROM
            (
                SELECT transaction_id,
                       status,
                       begin_kafka_offset,
                       end_kafka_offset,
                       event_count,
                       recorded_at,
                        tuple(
                            coalesce(end_kafka_offset, begin_kafka_offset),
                            recorded_at,
                            if(end_kafka_offset IS NULL, 0, 1),
                            if(status = 'COMPLETE', 2, if(status = 'REJECTED', 1, 0))
                        ) AS effective_order
                FROM lakehouse."audit.mysql_transactions"
            ) AS transaction_history
            GROUP BY transaction_id
            """
        )
        open_or_rejected = [
            dict(row)
            for row in transaction_rows
            if str(row.get("status", "")) in {"OPEN", "REJECTED"}
        ]
        if open_or_rejected:
            raise LabError(
                "Final audit transaction inventory contains OPEN/REJECTED rows: "
                + json.dumps(open_or_rejected, sort_keys=True, default=str)
            )

        iceberg_counts = ClickHouseServingMaterializer.fetch_iceberg_current_counts()
        stable_counts = ClickHouseServingMaterializer.fetch_current_counts()
        if stable_counts != iceberg_counts:
            raise LabError(
                "Final stable views differ from Iceberg current state: "
                + json.dumps(
                    {"iceberg": iceberg_counts, "stable": stable_counts},
                    sort_keys=True,
                )
            )

        gold_counts: dict[str, int] = {}
        for model in GOLD_MODELS:
            rows = clickhouse_query(f"SELECT count() AS row_count FROM gold.`{model}`")
            value = rows[0].get("row_count") if rows else None
            if not isinstance(value, (int, float, str)) or int(value) <= 0:
                raise LabError(f"Final Gold view is empty or invalid: {model}")
            gold_counts[model] = int(value)

        return _emit(
            "validate-final",
            "ready",
            sync_run_seq=sync_run_seq,
            sync_run_id=sync_run_id,
            publication_marker={
                "sync_run_seq": marker.get("sync_run_seq"),
                "sync_run_id": marker.get("sync_run_id"),
                "publication_status": marker.get("publication_status"),
            },
            runtime={
                "last_published_sync_run_seq": runtime.get(
                    "last_published_sync_run_seq"
                ),
                "lease_owner_id": runtime.get("lease_owner_id"),
                "lease_operation": runtime.get("lease_operation"),
            },
            active_runs=active_runs,
            open_or_rejected_transactions=open_or_rejected,
            iceberg_current_counts=iceberg_counts,
            stable_current_counts=stable_counts,
            gold_views=gold_counts,
        )
    except Exception as exc:
        return _emit("validate-final", "failed", error=redact_text(str(exc)))


def _run_maintenance(args: argparse.Namespace) -> int:
    try:
        from scripts.serving.airflow_api import AirflowApiClient

        _require_running_services(SERVING_PROFILES, ("clickhouse", "airflow"))
        client = AirflowApiClient()
        run_id = getattr(args, "run_id", None)
        res = client.trigger_dag_run(
            "olist_lakehouse_maintenance", run_id=run_id, unpause=False
        )
        dag_run_id = str(
            (res.get("dag_run_id") if isinstance(res, dict) else run_id) or ""
        )

        timeout = getattr(args, "timeout", 5400.0)
        state = client.poll_dag_run(
            "olist_lakehouse_maintenance", dag_run_id, timeout_seconds=timeout
        )

        if state == "success":
            return _emit("run-maintenance", "succeeded", dag_run_id=dag_run_id)
        else:
            cancellation_requested = False
            if state == "timeout" and dag_run_id:
                with contextlib.suppress(Exception):
                    cancellation_requested = client.fail_dag_run(
                        "olist_lakehouse_maintenance", dag_run_id
                    )
            return _emit(
                "run-maintenance",
                "failed",
                dag_run_id=dag_run_id,
                error=f"DAG run state: {state}",
                cancellation_requested=cancellation_requested,
            )
    except Exception as exc:
        return _emit("run-maintenance", "failed", error=redact_text(str(exc)))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    doctor = commands.add_parser("doctor")
    doctor.add_argument("--archive", default=str(SMALL_ARCHIVE))
    doctor.set_defaults(func=_doctor)

    reset = commands.add_parser("reset")
    reset.add_argument("--yes", action="store_true")
    reset.set_defaults(func=_reset)

    up = commands.add_parser("up")
    up.add_argument("--build", action="store_true")
    up.add_argument("--timeout", type=float, default=DEFAULT_BOOTSTRAP_TIMEOUT)
    up.set_defaults(func=_up)

    down = commands.add_parser("down")
    down.set_defaults(func=_down)

    bootstrap = commands.add_parser("bootstrap")
    bootstrap.add_argument("--archive", default=str(SMALL_ARCHIVE))
    bootstrap.add_argument("--run-id", default="wave1_j1_small_seed")
    bootstrap.add_argument(
        "--random-seed", "--seed", dest="random_seed", type=int, default=20260801
    )
    bootstrap.add_argument("--start-time", default="2020-01-01T00:00:00")
    bootstrap.add_argument("--password-file", default=str(DEFAULT_PASSWORD_FILE))
    bootstrap.add_argument("--timeout", type=float, default=DEFAULT_BOOTSTRAP_TIMEOUT)
    bootstrap.set_defaults(func=_bootstrap)

    seed = commands.add_parser("seed")
    seed.add_argument("--archive", default=str(SMALL_ARCHIVE))
    seed.add_argument("--run-id", required=True)
    seed.add_argument(
        "--random-seed", "--seed", dest="random_seed", type=int, required=True
    )
    seed.add_argument("--start-time", default="2020-01-01T00:00:00")
    seed.add_argument("--password-file", default=str(DEFAULT_PASSWORD_FILE))
    seed.set_defaults(func=_seed)

    status = commands.add_parser("status")
    status.add_argument("--password-file", default=str(DEFAULT_PASSWORD_FILE))
    status.add_argument(
        "--require", choices=["platform", "serving"], default="platform"
    )
    status.set_defaults(func=_status)

    validate = commands.add_parser("validate")
    validate.add_argument("--password-file", default=str(DEFAULT_PASSWORD_FILE))
    validate.add_argument(
        "--scope", choices=["platform", "streaming", "serving"], default="platform"
    )
    validate.add_argument("--timeout", type=float, default=DEFAULT_BOOTSTRAP_TIMEOUT)
    validate.set_defaults(func=_validate)

    validate_serving = commands.add_parser("validate-serving")
    validate_serving.add_argument("--sync-run-seq", type=int, required=True)
    validate_serving.add_argument("--sync-run-id", required=True)
    validate_serving.set_defaults(func=_validate_serving)

    start_streaming = commands.add_parser("start-streaming")
    start_streaming.add_argument("--wait-ready", action="store_true")
    start_streaming.add_argument("--timeout", type=float, default=300.0)
    start_streaming.set_defaults(func=_start_streaming)

    stop_streaming = commands.add_parser("stop-streaming")
    stop_streaming.set_defaults(func=_stop_streaming)

    start_serving_observer = commands.add_parser("start-serving-observer")
    start_serving_observer.add_argument("--timeout", type=float, default=300.0)
    start_serving_observer.set_defaults(func=_start_serving_observer)

    start_serving = commands.add_parser("start-serving")
    start_serving.add_argument("--build", action="store_true")
    start_serving.add_argument(
        "--timeout", type=float, default=DEFAULT_BOOTSTRAP_TIMEOUT
    )
    start_serving.set_defaults(func=_start_serving)

    wait_caught_up = commands.add_parser("wait-caught-up")
    wait_caught_up.add_argument("--timeout", type=float, default=1200)
    wait_caught_up.set_defaults(func=_wait_caught_up)

    sync_serving = commands.add_parser("sync-serving")
    sync_serving.add_argument("--run-id")
    sync_serving.add_argument("--timeout", type=float, default=1800.0)
    sync_serving.set_defaults(func=_sync_serving)

    rebuild_serving = commands.add_parser("rebuild-serving")
    rebuild_serving.add_argument("--yes", action="store_true")
    rebuild_serving.add_argument("--run-id")
    rebuild_serving.add_argument("--timeout", type=float, default=5400.0)
    rebuild_serving.set_defaults(func=_rebuild_serving)

    validate_rebuild = commands.add_parser("validate-rebuild")
    validate_rebuild.add_argument("--sync-run-seq", type=int, required=True)
    validate_rebuild.add_argument("--sync-run-id", required=True)
    validate_rebuild.set_defaults(func=_validate_rebuild)

    validate_final = commands.add_parser("validate-final")
    validate_final.add_argument("--sync-run-seq", type=int, required=True)
    validate_final.add_argument("--sync-run-id", required=True)
    validate_final.set_defaults(func=_validate_final)

    run_maintenance = commands.add_parser("run-maintenance")
    run_maintenance.add_argument("--run-id")
    run_maintenance.add_argument("--timeout", type=float, default=5400.0)
    run_maintenance.set_defaults(func=_run_maintenance)

    final_parity = commands.add_parser("final-parity")
    final_parity.add_argument("--phase", default="F", help=argparse.SUPPRESS)
    final_parity.add_argument("--confirm-destructive", action="store_true")
    final_parity.set_defaults(func=_not_available, phase="F")

    # Compatibility aliases are retained as thin lifecycle aliases; they do
    # not re-enable the removed PostgreSQL/NiFi path.
    start = commands.add_parser("start", help=argparse.SUPPRESS)
    start.add_argument("--build", action="store_true")
    start.add_argument("--timeout", type=float, default=DEFAULT_BOOTSTRAP_TIMEOUT)
    start.set_defaults(func=_up)
    stop = commands.add_parser("stop", help=argparse.SUPPRESS)
    stop.set_defaults(func=_down)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (LabError, ImportError, OSError) as exc:
        return _emit(str(args.command), "failed", error=redact_text(str(exc)))


if __name__ == "__main__":
    raise SystemExit(main())
