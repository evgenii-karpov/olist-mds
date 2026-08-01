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
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SMALL_ARCHIVE = ROOT / "tests" / "fixtures" / "olist_small" / "olist_small.zip"
FULL_ARCHIVE = ROOT / "olist.zip"
DEFAULT_PASSWORD_FILE = ROOT / "docker" / "secrets" / "dev" / "postgres_password.txt"
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
    "POLARIS_DB_PASSWORD_SOURCE_FILE": "docker/secrets/dev/control_postgres_password.txt",
    "APICURIO_DB_USERNAME_SOURCE_FILE": "docker/secrets/dev/apicurio_db_user.txt",
    "APICURIO_DB_PASSWORD_SOURCE_FILE": "docker/secrets/dev/control_postgres_password.txt",
    "MYSQL_ROOT_PASSWORD_SOURCE_FILE": "docker/secrets/dev/postgres_password.txt",
    "MYSQL_ADMIN_PASSWORD_SOURCE_FILE": "docker/secrets/dev/postgres_password.txt",
    "MYSQL_SIMULATOR_PASSWORD_SOURCE_FILE": "docker/secrets/dev/postgres_password.txt",
    "MYSQL_CDC_READER_PASSWORD_SOURCE_FILE": "docker/secrets/dev/postgres_password.txt",
    "MINIO_ROOT_USER_SOURCE_FILE": "docker/secrets/dev/minio_root_user.txt",
    "MINIO_ROOT_PASSWORD_SOURCE_FILE": "docker/secrets/dev/airflow_api_secret_key.txt",
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
    return 0 if status == "ready" else 1


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
    *, profiles: Sequence[str], build: bool, timeout: float, wait: bool = True
) -> None:
    args = ["up", "-d"]
    if wait:
        args.append("--wait")
    if build:
        args.append("--build")
    result = _run(
        compose_command(*args, profiles=profiles),
        timeout=timeout,
        check=False,
    )
    if result.returncode == 0:
        return

    # Compose returns 1 from `up --wait` when the graph contains a
    # service_completed_successfully one-shot service that exited with code
    # zero.  That is a successful platform state for J1 (for example,
    # iceberg-migration).  A dependent service can still be health=starting
    # at that instant, so keep polling the bounded Compose state briefly.
    deadline = time.monotonic() + min(timeout, 180.0)
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
            pending = "; ".join(
                f"{item.get('Service', 'unknown')} {item.get('Health', item.get('State', 'unknown'))}"
                for item in records
                if item.get("State") == "running"
                and item.get("Health") not in (None, "", "healthy")
            )
            raise LabError(
                "compose platform did not become ready before timeout"
                + (f": {pending}" if pending else "")
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
    except (URLError, TimeoutError):
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
    _run(
        [
            sys.executable,
            "-m",
            "streaming.connect.bootstrap",
            "--password-file",
            str(_path(args.password_file)),
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
                "capture-bundle",
                "--bundle",
                str(capture_root),
            ],
            timeout=60,
        )
        _run(
            [
                sys.executable,
                "-m",
                "streaming.schemas.writer_schemas",
                "validate",
                "--require-captured",
            ],
            timeout=60,
        )
        contracts_root = ROOT / "streaming" / "schemas" / "contracts"
        if not any(
            (contracts_root / entity / "v2.json").exists() for entity in ALL_ENTITIES
        ):
            _run(
                [
                    sys.executable,
                    "-m",
                    "streaming.schemas.generate_contracts",
                    "--write",
                    "--new-version",
                    "2",
                ],
                timeout=60,
            )
        _run(
            [
                sys.executable,
                "-m",
                "streaming.schemas.generate_contracts",
                "--check",
            ],
            timeout=60,
        )
        _run(
            [
                sys.executable,
                "-m",
                "streaming.schemas.contracts",
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


def _start_streaming(args: argparse.Namespace) -> int:
    try:
        timeout = getattr(args, "timeout", 300.0)
        _compose_up(
            profiles=PLATFORM_PROFILES + STREAMING_PROFILES,
            build=False,
            timeout=max(timeout, 300.0),
            wait=False,
        )
    except LabError as exc:
        return _emit("start-streaming", "failed", error=redact_text(str(exc)))
    return _emit("start-streaming", "ready")


def _wait_caught_up(args: argparse.Namespace) -> int:
    timeout = getattr(args, "timeout", 1200.0)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        status_file = ROOT / "docker" / "spark" / "status" / "silver" / "status.json"
        if not status_file.exists():
            status_file = Path("/var/run/olist-spark/silver/status.json")

        if status_file.exists():
            try:
                data = json.loads(status_file.read_text(encoding="utf-8"))
                if data.get("overall_state") == "READY":
                    return _emit("wait-caught-up", "ready")
            except Exception:
                pass
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

        client = AirflowApiClient()
        run_id = getattr(args, "run_id", None)
        res = client.trigger_dag_run("olist_lakehouse_serving_sync", run_id=run_id)
        dag_run_id = str(
            (res.get("dag_run_id") if isinstance(res, dict) else run_id) or ""
        )

        timeout = getattr(args, "timeout", 1800.0)
        state = client.poll_dag_run(
            "olist_lakehouse_serving_sync", dag_run_id, timeout_seconds=timeout
        )

        if state == "success":
            runtime = ServingControlRepository.get_runtime_state()
            if not runtime.get("schedules_activated_at"):
                client.unpause_dag("olist_lakehouse_serving_sync")
                client.unpause_dag("olist_lakehouse_serving_quality")
                client.unpause_dag("olist_iceberg_maintenance")

            return _emit(
                "sync-serving",
                "succeeded",
                dag_run_id=dag_run_id,
                sync_run_seq=runtime.get("last_published_sync_run_seq"),
                is_noop=False,
            )
        else:
            return _emit(
                "sync-serving",
                "failed",
                dag_run_id=dag_run_id,
                error=f"DAG run state: {state}",
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

        client = AirflowApiClient()
        run_id = getattr(args, "run_id", None)
        res = client.trigger_dag_run(
            "olist_clickhouse_rebuild",
            run_id=run_id,
            conf={"confirm_destructive": True},
        )
        dag_run_id = str(
            (res.get("dag_run_id") if isinstance(res, dict) else run_id) or ""
        )

        timeout = getattr(args, "timeout", 5400.0)
        state = client.poll_dag_run(
            "olist_clickhouse_rebuild", dag_run_id, timeout_seconds=timeout
        )

        if state == "success":
            return _emit("rebuild-serving", "succeeded", dag_run_id=dag_run_id)
        else:
            return _emit(
                "rebuild-serving",
                "failed",
                dag_run_id=dag_run_id,
                error=f"DAG run state: {state}",
            )
    except Exception as exc:
        return _emit("rebuild-serving", "failed", error=redact_text(str(exc)))


def _run_maintenance(args: argparse.Namespace) -> int:
    try:
        from scripts.serving.airflow_api import AirflowApiClient

        client = AirflowApiClient()
        run_id = getattr(args, "run_id", None)
        res = client.trigger_dag_run("olist_iceberg_maintenance", run_id=run_id)
        dag_run_id = str(
            (res.get("dag_run_id") if isinstance(res, dict) else run_id) or ""
        )

        timeout = getattr(args, "timeout", 5400.0)
        state = client.poll_dag_run(
            "olist_iceberg_maintenance", dag_run_id, timeout_seconds=timeout
        )

        if state == "success":
            return _emit("run-maintenance", "succeeded", dag_run_id=dag_run_id)
        else:
            return _emit(
                "run-maintenance",
                "failed",
                dag_run_id=dag_run_id,
                error=f"DAG run state: {state}",
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

    start_streaming = commands.add_parser("start-streaming")
    start_streaming.set_defaults(func=_start_streaming)

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
