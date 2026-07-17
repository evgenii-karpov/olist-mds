"""Run the deterministic batch-versus-CDC parity integration test."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import boto3
import psycopg2
from confluent_kafka import OFFSET_INVALID, Consumer, TopicPartition
from confluent_kafka.admin import AdminClient
from psycopg2 import sql
from psycopg2.extensions import connection as PgConnection

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.cdc.stage2_admin import connector_has_failed, connector_is_running
from scripts.ci.pipeline_helpers import (
    fetch_dag_run_state,
    fetch_one,
    wait_for_dag_success,
)
from scripts.utilities.validate_source_contract import load_contract, validate_archive
from streaming.nifi.deploy_flow import NifiClient

DEFAULT_ARCHIVE = (
    PROJECT_ROOT / "tests" / "fixtures" / "olist_small" / "olist_small.zip"
)
DEFAULT_PROFILE = (
    PROJECT_ROOT / "tests" / "fixtures" / "olist_small" / "source_profile_small.json"
)
DEFAULT_REPORT = PROJECT_ROOT / "data" / "reports" / "batch-cdc-parity.json"
DEFAULT_TIMEOUT_SECONDS = 1200
DEFAULT_POLL_SECONDS = 2
FIXTURE_BATCH_DATE = "2018-09-01"
FIXED_SEED = 20260717
SEED_RUN_ID = "batch_cdc_parity_seed"
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
SOURCE_TO_BATCH_MODEL = {table: f"stg_olist__{table}" for table in CAPTURED_TABLES}
SOURCE_TO_REALTIME_MODEL = {
    table: f"stg_cdc__{table}_current" for table in CAPTURED_TABLES
}
TOPIC_PREFIX = "olist_cdc.public."
NIFI_GROUP_ID = "olist-nifi-cdc-v1"
NIFI_FLOW_NAME = "olist-cdc-v1"
CONNECT_URL = "http://kafka-connect:8083"
REGISTRY_URL = "http://apicurio-registry:8080"
KAFKA_BOOTSTRAP = "kafka:29092"
MINIO_ENDPOINT = "http://minio:9000"
MINIO_BUCKET = "olist-cdc"
WAREHOUSE_HOST = "postgres"
OLTP_HOST = "oltp-postgres"
PASSWORD_FILE = PROJECT_ROOT / "docker" / "secrets" / "dev" / "postgres_password.txt"
NIFI_PASSWORD_FILE = (
    PROJECT_ROOT / "docker" / "secrets" / "dev" / "airflow_api_secret_key.txt"
)
NIFI_SECRET_PATH = Path("/run/secrets/nifi_admin_password")
MINIO_SECRET_PATH = Path("/run/secrets/minio_cdc_loader_password")
NORMALIZED_PREFIX = "manifests/cdc/kind=normalized/"
COVERAGE_PREFIX = "manifests/cdc/kind=coverage/"
QUARANTINE_PREFIX = "quarantine/"
DBT_UTILS_TESTS = (
    "dbt_utils_equality_daily_revenue",
    "dbt_utils_equality_monthly_arpu",
)
SECRET_OPTION_NAMES = {"--password", "--password-file", "--secret", "--token"}


@dataclass
class Deadline:
    timeout_seconds: float
    started_at: float = field(default_factory=time.monotonic)

    @property
    def remaining(self) -> float:
        return max(0.0, self.timeout_seconds - (time.monotonic() - self.started_at))


def new_deadline(timeout_seconds: float) -> Deadline:
    return Deadline(timeout_seconds=timeout_seconds)


def now_utc() -> datetime:
    return datetime.now(UTC)


def iso_timestamp(value: datetime | None = None) -> str:
    return (value or now_utc()).isoformat()


def parse_timestamp(value: object) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    text = str(value).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def read_secret(value: str | None, file_value: Path | None, default: str) -> str:
    if value:
        return value
    if file_value and file_value.exists():
        return file_value.read_text(encoding="utf-8").strip()
    return default


def secret_values() -> list[str]:
    values = [
        os.environ.get("POSTGRES_PASSWORD", ""),
        os.environ.get("OLTP_POSTGRES_PASSWORD", ""),
        os.environ.get("AIRFLOW_POSTGRES_PASSWORD", ""),
    ]
    for path in (
        Path(os.environ.get("POSTGRES_PASSWORD_FILE", str(PASSWORD_FILE))),
        Path(os.environ.get("OLTP_POSTGRES_PASSWORD_FILE", str(PASSWORD_FILE))),
        Path(os.environ.get("CDC_S3_SECRET_FILE", str(MINIO_SECRET_PATH))),
        Path(os.environ.get("NIFI_ADMIN_PASSWORD_FILE", str(NIFI_PASSWORD_FILE))),
    ):
        try:
            values.append(path.read_text(encoding="utf-8").strip())
        except OSError:
            continue
    return [value for value in values if value]


def redact_text(value: object) -> str:
    text = str(value)
    for secret in secret_values():
        text = text.replace(secret, "[REDACTED]")
    text = re.sub(
        r"(?i)(password|secret|token|authorization)=([^\s,;]+)",
        r"\1=[REDACTED]",
        text,
    )
    return text[:4000]


def redact_value(value: object) -> object:
    if isinstance(value, Mapping):
        redacted: dict[str, object] = {}
        for key, item in value.items():
            key_text = str(key)
            if re.search(r"(?i)(password|secret|token|authorization)", key_text):
                redacted[key_text] = "[REDACTED]"
            else:
                redacted[key_text] = redact_value(item)
        return redacted
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if isinstance(value, tuple):
        return [redact_value(item) for item in value]
    if isinstance(value, str):
        return redact_text(value)
    return value


def wait_for_condition(
    label: str,
    check: Callable[[], tuple[bool, object]],
    deadline: Deadline,
    poll_seconds: float,
) -> object:
    last_observed: object = None
    while deadline.remaining > 0:
        try:
            satisfied, observed = check()
            last_observed = redact_value(observed)
            if satisfied:
                return observed
        except Exception as exc:
            last_observed = {"error": redact_text(f"{type(exc).__name__}: {exc}")}
        sleep_for = min(max(0.0, poll_seconds), deadline.remaining)
        if sleep_for > 0:
            time.sleep(sleep_for)
    raise TimeoutError(
        f"Timed out waiting for {label}; last_observed={json.dumps(last_observed, default=str)}"
    )


def archive_sha256(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_same_archive_identity(batch_archive: Path, cdc_archive: Path) -> str:
    batch_path = batch_archive.resolve()
    cdc_path = cdc_archive.resolve()
    if batch_path != cdc_path:
        raise ValueError(
            f"batch and CDC archive paths differ: {batch_path} != {cdc_path}"
        )
    batch_digest = archive_sha256(batch_path)
    cdc_digest = archive_sha256(cdc_path)
    if batch_digest != cdc_digest:
        raise ValueError("batch and CDC archive SHA-256 identities differ")
    return batch_digest


def command_env(overrides: Mapping[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    if overrides:
        env.update(overrides)
    return env


def run_command(
    command: list[str],
    *,
    env: Mapping[str, str] | None = None,
    check: bool = True,
    announce: bool = True,
) -> subprocess.CompletedProcess[str]:
    if announce:
        safe_command = []
        redact_next = False
        for item in command:
            if redact_next:
                safe_command.append("[REDACTED]")
                redact_next = False
            else:
                safe_command.append(item)
                redact_next = item in SECRET_OPTION_NAMES
        print(f"+ {' '.join(safe_command)}", flush=True)
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=None if env is None else dict(env),
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode,
            command,
            output=redact_text(result.stdout),
        )
    return result


def last_json_line(output: str) -> dict[str, Any] | None:
    for line in reversed(output.splitlines()):
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return None


def request_json(
    url: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    accepted: tuple[int, ...] = (200,),
) -> tuple[int, Any]:
    payload = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(
        url,
        data=payload,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            raw = response.read()
            status = response.status
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        status = exc.code
    if status not in accepted:
        raise RuntimeError(f"{method} {url} returned HTTP {status}: {redact_text(raw)}")
    if not raw:
        return status, None
    try:
        return status, json.loads(raw)
    except json.JSONDecodeError:
        return status, raw.decode(errors="replace")


def warehouse_connection() -> PgConnection:
    password_file = Path(
        os.environ.get(
            "POSTGRES_PASSWORD_FILE", str(Path("/run/secrets/postgres_password"))
        )
    )
    if not password_file.exists():
        password_file = PASSWORD_FILE
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", WAREHOUSE_HOST),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        dbname=os.environ.get("POSTGRES_DB", "olist_analytics"),
        user=os.environ.get("POSTGRES_USER", "olist"),
        password=read_secret(
            os.environ.get("POSTGRES_PASSWORD"), password_file, "olist"
        ),
        connect_timeout=10,
    )


def oltp_connection() -> PgConnection:
    password_file = Path(
        os.environ.get(
            "OLTP_POSTGRES_PASSWORD_FILE", str(Path("/run/secrets/oltp_admin_password"))
        )
    )
    if not password_file.exists():
        password_file = PASSWORD_FILE
    return psycopg2.connect(
        host=os.environ.get("OLTP_POSTGRES_HOST", OLTP_HOST),
        port=int(os.environ.get("OLTP_POSTGRES_PORT", "5432")),
        dbname=os.environ.get("OLTP_POSTGRES_DB", "olist_oltp"),
        user=os.environ.get("OLTP_POSTGRES_USER", "olist_simulator"),
        password=read_secret(
            os.environ.get("OLTP_POSTGRES_PASSWORD"), password_file, "olist"
        ),
        connect_timeout=10,
    )


def s3_client():
    secret_file = Path(
        os.environ.get(
            "CDC_S3_SECRET_FILE", str(Path("/run/secrets/minio_cdc_loader_password"))
        )
    )
    if not secret_file.exists():
        secret_file = PASSWORD_FILE
    return boto3.client(
        "s3",
        endpoint_url=os.environ.get("CDC_S3_ENDPOINT", MINIO_ENDPOINT),
        region_name=os.environ.get("CDC_S3_REGION", "us-east-1"),
        aws_access_key_id=os.environ.get("CDC_S3_ACCESS_KEY", "olist_cdc_loader"),
        aws_secret_access_key=read_secret(None, secret_file, "olist"),
    )


def nifi_client() -> NifiClient:
    password_file = Path(
        os.environ.get("NIFI_ADMIN_PASSWORD_FILE", str(NIFI_SECRET_PATH))
    )
    if not password_file.exists():
        password_file = NIFI_PASSWORD_FILE
    return NifiClient(
        os.environ.get("NIFI_API_URL", "https://nifi:8443/nifi-api"),
        os.environ.get("NIFI_ADMIN_USERNAME", "nifi-admin"),
        read_secret(None, password_file, "olist"),
    )


def source_contract(archive: Path, profile: Path) -> dict[str, int]:
    entities = load_contract(profile)
    validate_archive(archive, entities)
    return {entity.entity_name: entity.row_count for entity in entities}


def expected_topic_metadata() -> dict[str, dict[str, Any]]:
    payload = json.loads(
        (PROJECT_ROOT / "streaming" / "kafka" / "topics.json").read_text(
            encoding="utf-8"
        )
    )
    return {str(item["name"]): item for item in payload["topics"]}


def validate_topic_inventory() -> dict[str, Any]:
    expected = expected_topic_metadata()
    client = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP})
    metadata = client.list_topics(timeout=10)
    actual = set(metadata.topics)
    missing = sorted(set(expected) - actual)
    unexpected_sources = sorted(
        name
        for name in actual - set(expected)
        if name.startswith("olist_cdc.public.")
        or name.startswith("olist_cdc.heartbeat")
    )
    partition_mismatches = []
    for name, definition in expected.items():
        topic = metadata.topics.get(name)
        if topic is None:
            continue
        actual_partitions = len(topic.partitions)
        if actual_partitions != int(definition["partitions"]):
            partition_mismatches.append(
                {
                    "topic": name,
                    "actual": actual_partitions,
                    "expected": int(definition["partitions"]),
                }
            )
    if missing or unexpected_sources or partition_mismatches:
        raise RuntimeError(
            "Kafka topic inventory mismatch: "
            + redact_text(
                json.dumps(
                    {
                        "missing": missing,
                        "unexpected_sources": unexpected_sources,
                        "partition_mismatches": partition_mismatches,
                    },
                    sort_keys=True,
                )
            )
        )
    return {
        "expected_topics": len(expected),
        "actual_topics": len(actual),
        "captured_topics": [f"{TOPIC_PREFIX}{table}" for table in CAPTURED_TABLES],
    }


def configure_registry() -> dict[str, str]:
    base = REGISTRY_URL.rstrip("/")
    status, _ = request_json(f"{base}/apis/registry/v3/system/info")
    rule_url = f"{base}/apis/registry/v3/admin/rules/COMPATIBILITY"
    rule_status, _ = request_json(rule_url, accepted=(200, 404))
    body = {"ruleType": "COMPATIBILITY", "config": "BACKWARD_TRANSITIVE"}
    if rule_status == 404:
        request_json(
            f"{base}/apis/registry/v3/admin/rules",
            method="POST",
            body=body,
            accepted=(200, 201, 204),
        )
    else:
        request_json(rule_url, method="PUT", body=body, accepted=(200, 204))
    _, rule = request_json(rule_url)
    if not isinstance(rule, Mapping) or rule.get("config") != "BACKWARD_TRANSITIVE":
        raise RuntimeError(f"Unexpected Apicurio compatibility rule: {rule}")
    return {"system_info_status": str(status), "compatibility": str(rule["config"])}


def connector_status() -> dict[str, Any]:
    _, status = request_json(f"{CONNECT_URL}/connectors/olist-postgres-cdc/status")
    if not isinstance(status, dict):
        raise RuntimeError("Kafka Connect status is not a JSON object")
    return status


def connector_state_summary(status: Mapping[str, Any]) -> dict[str, Any]:
    connector = status.get("connector")
    tasks = status.get("tasks")
    connector_state = connector.get("state") if isinstance(connector, Mapping) else None
    task_states = (
        [task.get("state") for task in tasks if isinstance(task, Mapping)]
        if isinstance(tasks, list)
        else []
    )
    return {
        "connector_state": connector_state,
        "task_states": task_states,
        "running": connector_is_running(dict(status)),
        "failed": connector_has_failed(dict(status)),
    }


def register_connector(deadline: Deadline, poll_seconds: float) -> dict[str, Any]:
    from scripts.cdc.stage2_admin import render_connector

    password_path = Path(
        os.environ.get(
            "OLTP_CDC_READER_PASSWORD_FILE",
            str(Path("/run/secrets/oltp_cdc_reader_password")),
        )
    )
    if not password_path.exists():
        password_path = PASSWORD_FILE
    payload = render_connector(password_path)
    name = str(payload["name"])
    config = payload["config"]

    def plugin_ready() -> tuple[bool, object]:
        _, plugins = request_json(f"{CONNECT_URL}/connector-plugins")
        classes = {
            plugin.get("class") for plugin in plugins if isinstance(plugin, Mapping)
        }
        required = "io.debezium.connector.postgresql.PostgresConnector"
        return required in classes, {"plugin_count": len(classes)}

    wait_for_condition(
        "Kafka Connect Debezium plugin",
        plugin_ready,
        deadline,
        poll_seconds,
    )
    config_url = f"{CONNECT_URL}/connectors/{name}/config"
    existing_status, existing = request_json(config_url, accepted=(200, 404))
    if existing_status == 404:
        request_json(
            f"{CONNECT_URL}/connectors",
            method="POST",
            body=payload,
            accepted=(200, 201, 202),
        )
        action = "created"
    elif (
        isinstance(existing, Mapping)
        and {key: value for key, value in existing.items() if key != "name"} == config
    ):
        action = "unchanged"
    else:
        request_json(config_url, method="PUT", body=config, accepted=(200, 201, 202))
        action = "updated"

    def running() -> tuple[bool, object]:
        status = connector_status()
        summary = connector_state_summary(status)
        return bool(summary["running"]), summary

    summary = wait_for_condition(
        "Debezium connector and task RUNNING", running, deadline, poll_seconds
    )
    if not isinstance(summary, Mapping):
        raise RuntimeError(f"Unexpected connector wait result: {summary!r}")
    return {
        "action": action,
        **{str(key): value for key, value in summary.items()},
    }


def create_minio_client():
    return s3_client()


def list_s3_objects(client: Any, prefix: str) -> list[dict[str, Any]]:
    paginator = client.get_paginator("list_objects_v2")
    objects: list[dict[str, Any]] = []
    for page in paginator.paginate(Bucket=MINIO_BUCKET, Prefix=prefix):
        objects.extend(page.get("Contents", []))
    return objects


def manifest_objects(
    client: Any,
    prefix: str,
    started_at: datetime,
) -> list[dict[str, Any]]:
    manifests: list[dict[str, Any]] = []
    for item in list_s3_objects(client, prefix):
        key = str(item.get("Key", ""))
        if not key.endswith(".manifest.json"):
            continue
        try:
            body = client.get_object(Bucket=MINIO_BUCKET, Key=key)["Body"].read()
            payload = json.loads(body)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise RuntimeError(f"Cannot read CDC manifest {key}: {exc}") from exc
        closed_at = parse_timestamp(payload.get("closed_at"))
        if closed_at is None or closed_at < started_at:
            continue
        manifests.append({"key": key, **payload})
    return manifests


def manifest_summary(client: Any, started_at: datetime) -> dict[str, Any]:
    normalized = manifest_objects(client, NORMALIZED_PREFIX, started_at)
    coverage = manifest_objects(client, COVERAGE_PREFIX, started_at)
    normalized_by_table: dict[str, int] = {}
    coverage_by_table: dict[str, int] = {}
    for manifest in normalized:
        table = str(manifest.get("table", ""))
        normalized_by_table[table] = normalized_by_table.get(table, 0) + int(
            manifest.get("row_count", 0)
        )
    for manifest in coverage:
        table = str(manifest.get("table", ""))
        coverage_by_table[table] = coverage_by_table.get(table, 0) + int(
            manifest.get("business_event_count", 0)
        )
    return {
        "normalized_manifest_count": len(normalized),
        "coverage_manifest_count": len(coverage),
        "normalized_tables": sorted(normalized_by_table),
        "coverage_tables": sorted(coverage_by_table),
        "normalized_rows_by_table": normalized_by_table,
        "coverage_business_rows_by_table": coverage_by_table,
    }


def manifests_complete(observed: Mapping[str, Any]) -> bool:
    required = set(CAPTURED_TABLES)
    return (
        set(observed.get("normalized_tables", [])) >= required
        and set(observed.get("coverage_tables", [])) >= required
    )


def kafka_consumer_lag() -> dict[str, Any]:
    admin = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP})
    metadata = admin.list_topics(timeout=10)
    assignments = [
        TopicPartition(f"{TOPIC_PREFIX}{table}", partition)
        for table in CAPTURED_TABLES
        for partition in range(
            len(metadata.topics[f"{TOPIC_PREFIX}{table}"].partitions)
        )
    ]
    consumer = Consumer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP,
            "group.id": NIFI_GROUP_ID,
            "enable.auto.commit": False,
        }
    )
    values: dict[str, int] = {}
    try:
        committed = consumer.committed(assignments, timeout=10)
        for item in committed:
            high = consumer.get_watermark_offsets(item, timeout=10, cached=False)[1]
            offset = item.offset
            lag = high if offset in (OFFSET_INVALID, -1) else max(0, high - offset)
            values[f"{item.topic}:{item.partition}"] = int(lag)
    finally:
        consumer.close()
    return {
        "total_lag": sum(values.values()),
        "max_lag": max(values.values(), default=0),
        "partitions": values,
    }


def kafka_nifi_drained(lag: Mapping[str, Any], nifi_state: Mapping[str, Any]) -> bool:
    return (
        int(lag.get("total_lag", 0)) == 0
        and int(nifi_state.get("queued_count", 0)) == 0
        and not nifi_state.get("processor_errors")
        and not nifi_state.get("bulletins")
    )


def nifi_flow_group(client: NifiClient) -> tuple[str, dict[str, Any]]:
    root = client.get("/flow/process-groups/root")["processGroupFlow"]
    groups = root["flow"].get("processGroups", [])
    for group in groups:
        component = group.get("component", {})
        if component.get("name") == NIFI_FLOW_NAME:
            group_id = str(group["id"])
            flow = client.get(f"/flow/process-groups/{group_id}")["processGroupFlow"]
            return group_id, flow["flow"]
    raise RuntimeError(f"NiFi process group {NIFI_FLOW_NAME!r} is not deployed")


def nifi_snapshot(client: NifiClient) -> dict[str, Any]:
    group_id, flow = nifi_flow_group(client)
    queued_count = 0
    queued_size = 0
    queues: list[dict[str, Any]] = []
    for connection in flow.get("connections", []):
        snapshot = (
            connection.get("status", {}).get("aggregateSnapshot", {})
            if isinstance(connection, Mapping)
            else {}
        )
        count = int(snapshot.get("queuedCount", 0) or 0)
        size = str(snapshot.get("queuedSize", "0"))
        queues.append(
            {
                "id": connection.get("id"),
                "source": connection.get("component", {}).get("source", {}).get("id"),
                "destination": connection.get("component", {})
                .get("destination", {})
                .get("id"),
                "queued_count": count,
                "queued_size": size,
            }
        )
        queued_count += count
        with suppress(ValueError):
            queued_size += int(size.split(" ", 1)[0].replace(",", ""))

    processors: list[dict[str, Any]] = []
    processor_errors: list[str] = []
    for processor in flow.get("processors", []):
        component = processor.get("component", {})
        status = processor.get("status", {}).get("aggregateSnapshot", {})
        validation_errors = component.get("validationErrors") or []
        run_status = component.get("state") or status.get("runStatus")
        item = {
            "name": component.get("name"),
            "state": run_status,
            "active_threads": status.get("activeThreadCount", 0),
            "validation_errors": [redact_text(error) for error in validation_errors],
        }
        processors.append(item)
        processor_errors.extend(
            f"{component.get('name')}: {redact_text(error)}"
            for error in validation_errors
        )
        if run_status not in (None, "RUNNING"):
            processor_errors.append(
                f"{component.get('name')}: processor state is {run_status}"
            )

    bulletins: list[str] = []
    try:
        bulletin_payload = client.get(f"/flow/process-groups/{group_id}/bulletins")
        for bulletin in bulletin_payload.get("bulletins", []):
            message = bulletin.get("bulletin", {}).get("message")
            if message:
                bulletins.append(redact_text(message))
    except (OSError, RuntimeError, KeyError, TypeError):
        # The queue and processor snapshots are sufficient when the optional
        # bulletin endpoint is unavailable on a local NiFi patch release.
        pass
    return {
        "queued_count": queued_count,
        "queued_size": queued_size,
        "queues": queues[:100],
        "processors": processors[:100],
        "processor_errors": processor_errors[:100],
        "bulletins": bulletins[:100],
    }


def count_minio_objects_since(client: Any, prefix: str, started_at: datetime) -> int:
    count = 0
    for item in list_s3_objects(client, prefix):
        modified_at = parse_timestamp(item.get("LastModified"))
        if modified_at is not None and modified_at >= started_at:
            count += 1
    return count


def table_count(connection: PgConnection, schema: str, table: str) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("select count(*) from {}.{}").format(
                sql.Identifier(schema), sql.Identifier(table)
            )
        )
        row = cursor.fetchone()
    if row is None:
        raise RuntimeError(f"Count query returned no row for {schema}.{table}")
    return int(row[0])


def captured_row_counts(connection: PgConnection) -> dict[str, dict[str, int]]:
    batch = {
        table: table_count(connection, "staging", SOURCE_TO_BATCH_MODEL[table])
        for table in CAPTURED_TABLES
    }
    realtime = {
        table: table_count(
            connection, "realtime_staging", SOURCE_TO_REALTIME_MODEL[table]
        )
        for table in CAPTURED_TABLES
    }
    raw = {
        table: table_count(connection, "raw_cdc", table) for table in CAPTURED_TABLES
    }
    return {"batch": batch, "realtime": realtime, "raw_cdc": raw}


def relation_exists(connection: PgConnection, schema: str, table: str) -> bool:
    with connection.cursor() as cursor:
        cursor.execute("select to_regclass(%s)", (f"{schema}.{table}",))
        row = cursor.fetchone()
    return row is not None and row[0] is not None


def warehouse_bootstrap_snapshot() -> dict[str, Any]:
    with warehouse_connection() as connection:
        raw_tables = {
            table: relation_exists(connection, "raw_cdc", table)
            for table in CAPTURED_TABLES
        }
        audit_tables = {
            table: relation_exists(connection, "cdc_audit", table)
            for table in (
                "cdc_ingest_runs",
                "cdc_files",
                "cdc_coverage_files",
                "cdc_reconciliation",
                "cdc_transform_runs",
                "cdc_publication_state",
            )
        }
    return {"raw_tables": raw_tables, "audit_tables": audit_tables}


def service_snapshot(s3: Any, nifi: NifiClient) -> tuple[bool, dict[str, Any]]:
    status: dict[str, Any] = {}
    checks: list[tuple[str, Callable[[], object]]] = [
        ("warehouse_postgres", lambda: warehouse_bootstrap_snapshot()),
        ("oltp_postgres", lambda: oltp_health()),
        ("kafka", lambda: validate_topic_inventory()),
        ("kafka_connect", lambda: request_json(f"{CONNECT_URL}/connectors")[0]),
        (
            "apicurio_registry",
            lambda: request_json(f"{REGISTRY_URL}/apis/registry/v3/system/info")[0],
        ),
        (
            "minio",
            lambda: (
                s3.head_bucket(Bucket=MINIO_BUCKET),
                s3.list_objects_v2(Bucket=MINIO_BUCKET, MaxKeys=1).get("KeyCount", 0),
            ),
        ),
        ("nifi_bootstrap", lambda: nifi_snapshot(nifi)),
    ]
    for name, check in checks:
        try:
            status[name] = {"ok": True, "observed": redact_value(check())}
        except Exception as exc:
            status[name] = {
                "ok": False,
                "error": redact_text(f"{type(exc).__name__}: {exc}"),
            }
    healthy = all(item.get("ok") for item in status.values())
    return healthy, status


def oltp_health() -> dict[str, Any]:
    with oltp_connection() as connection, connection.cursor() as cursor:
        cursor.execute("select 1")
        cursor.fetchone()
        cursor.execute("select count(*) from public.customers")
        row = cursor.fetchone()
    return {"customers": int(row[0]) if row else 0}


def ensure_airflow_dags_registered(
    dag_ids: tuple[str, ...], deadline: Deadline, poll_seconds: float
) -> None:
    run_command(["airflow", "dags", "reserialize"])
    run_command(["python", "scripts/ci/check_airflow_dag_imports.py"])

    def registered() -> tuple[bool, object]:
        result = run_command(["airflow", "dags", "list"], check=False, announce=False)
        output = result.stdout or ""
        missing = [dag_id for dag_id in dag_ids if dag_id not in output]
        return not missing, {"missing": missing, "exit_code": result.returncode}

    wait_for_condition("Airflow DAG registration", registered, deadline, poll_seconds)


def trigger_dag(
    dag_id: str,
    run_id: str,
    *,
    conf: dict[str, Any] | None = None,
) -> None:
    run_command(["airflow", "dags", "unpause", dag_id])
    command = ["airflow", "dags", "trigger", dag_id, "--run-id", run_id]
    if conf is not None:
        command.extend(["--conf", json.dumps(conf, sort_keys=True)])
    run_command(command)


def wait_for_dag(
    dag_id: str, run_id: str, deadline: Deadline, poll_seconds: float
) -> None:
    wait_for_dag_success(
        dag_id,
        run_id,
        timeout_seconds=deadline.remaining,
        poll_seconds=poll_seconds,
        on_state=lambda state: print(
            f"DAG run {dag_id}/{run_id} state: {state}", flush=True
        ),
    )


def batch_reconciliation_summary(
    batch_id: str, expected_counts: Mapping[str, int]
) -> dict[str, Any]:
    with warehouse_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            select entity_name, expected_source_rows, raw_loaded_rows, status,
                   failed_checks
            from audit.batch_reconciliation
            where batch_id = %s
            order by entity_name
            """,
            (batch_id,),
        )
        rows = cursor.fetchall()
    values = [
        {
            "entity_name": str(entity),
            "expected_source_rows": int(expected or 0),
            "raw_loaded_rows": int(loaded or 0),
            "status": str(status),
            "failed_checks": failed,
        }
        for entity, expected, loaded, status, failed in rows
    ]
    by_entity = {item["entity_name"]: item for item in values}
    missing = sorted(set(expected_counts) - set(by_entity))
    failed = [
        item["entity_name"]
        for item in values
        if item["status"] != "PASS"
        or item["raw_loaded_rows"] != expected_counts.get(item["entity_name"])
    ]
    return {
        "rows": values[:100],
        "row_count": len(values),
        "missing_entities": missing,
        "failed_entities": failed,
        "passed": not missing and not failed,
    }


def seed_oltp(archive: Path) -> dict[str, Any]:
    env = command_env(
        {
            "OLTP_POSTGRES_HOST": OLTP_HOST,
            "OLTP_POSTGRES_PORT": "5432",
            "OLTP_POSTGRES_DB": "olist_oltp",
            "OLTP_POSTGRES_USER": "olist_simulator",
            "OLTP_POSTGRES_PASSWORD_FILE": str(PASSWORD_FILE),
        }
    )
    result = run_command(
        [
            "python",
            "-m",
            "scripts.simulation",
            "seed",
            "--archive",
            str(archive),
            "--seed",
            str(FIXED_SEED),
            "--run-id",
            SEED_RUN_ID,
            "--host",
            OLTP_HOST,
            "--port",
            "5432",
            "--database",
            "olist_oltp",
            "--user",
            "olist_simulator",
            "--password-file",
            str(PASSWORD_FILE),
        ],
        env=env,
    )
    return last_json_line(result.stdout or "") or {
        "run_id": SEED_RUN_ID,
        "status": "completed",
    }


def fetch_dag_run_ids(dag_id: str) -> set[str]:
    from scripts.ci.pipeline_helpers import airflow_metadata_connection

    with airflow_metadata_connection() as connection, connection.cursor() as cursor:
        cursor.execute("select run_id from dag_run where dag_id = %s", (dag_id,))
        return {str(row[0]) for row in cursor.fetchall()}


def fetch_new_dag_runs(dag_id: str, existing: set[str]) -> list[dict[str, Any]]:
    from scripts.ci.pipeline_helpers import airflow_metadata_connection

    with airflow_metadata_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            select run_id, state, start_date, end_date
            from dag_run
            where dag_id = %s
            order by coalesce(start_date, logical_date) desc
            limit 50
            """,
            (dag_id,),
        )
        rows = cursor.fetchall()
    return [
        {
            "run_id": str(run_id),
            "state": None if state is None else str(state),
            "start_date": iso_timestamp(parse_timestamp(start_date)),
            "end_date": iso_timestamp(parse_timestamp(end_date))
            if end_date is not None
            else None,
        }
        for run_id, state, start_date, end_date in rows
        if str(run_id) not in existing
    ]


def choose_asset_transform_run(
    runs: list[dict[str, Any]], existing: set[str]
) -> dict[str, Any] | None:
    candidates = [run for run in runs if run.get("run_id") not in existing]
    candidates.sort(key=lambda item: str(item.get("start_date") or ""))
    for run in candidates:
        if run.get("state") in {"failed", "upstream_failed"}:
            raise AssertionError(
                "Asset-triggered transform failed: "
                f"{run.get('run_id')} state={run.get('state')}"
            )
        if run.get("state") == "success":
            return run
    return None


def wait_for_asset_transform(
    existing_runs: set[str], deadline: Deadline, poll_seconds: float
) -> dict[str, Any]:
    last_observed: object = None
    while deadline.remaining > 0:
        runs = fetch_new_dag_runs("olist_cdc_transform_local", existing_runs)
        last_observed = runs[:10]
        selected = choose_asset_transform_run(runs, existing_runs)
        if selected is not None:
            return selected
        time.sleep(min(max(0.0, poll_seconds), deadline.remaining))
    raise TimeoutError(
        "Timed out waiting for Asset-triggered olist_cdc_transform_local run; "
        f"last_observed={json.dumps(last_observed, default=str)}"
    )


def safe_airflow_run_id(prefix: str, token: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", f"{prefix}_{token}")


def audit_summary(
    ingest_run_id: str,
    transform_run_id: str,
    s3: Any,
    started_at: datetime,
) -> dict[str, Any]:
    with warehouse_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            select ingest_run_id, dag_id, orchestration_run_id, status,
                   files_discovered, coverage_manifests_discovered,
                   files_claimed, files_loaded, object_rows, inserted_rows,
                   duplicate_rows, rejected_rows, gap_count, failure_summary
            from cdc_audit.cdc_ingest_runs
            where ingest_run_id = %s
            """,
            (ingest_run_id,),
        )
        ingest = cursor.fetchone()
        cursor.execute(
            """
            select count(*),
                   coalesce(sum(duplicate_rows), 0),
                   coalesce(sum(rejected_rows), 0),
                   coalesce(sum(gap_count), 0),
                   count(*) filter (where status <> 'PASS')
            from cdc_audit.cdc_reconciliation
            where ingest_run_id = %s
            """,
            (ingest_run_id,),
        )
        reconciliation = fetch_one(cursor)
        cursor.execute(
            """
            select count(*)
            from cdc_audit.cdc_dead_letters
            where resolution_status = 'OPEN'
              and created_at >= %s
            """,
            (started_at,),
        )
        open_dlq = int(fetch_one(cursor)[0])
        cursor.execute(
            """
            select coalesce(sum(gap_count), 0)
            from cdc_audit.cdc_partition_watermarks
            """
        )
        offset_gaps = int(fetch_one(cursor)[0])
        cursor.execute(
            """
            select transform_run_id, dag_id, orchestration_run_id, status,
                   files_selected, events_selected, dbt_completed_at,
                   finished_at, failure_summary
            from cdc_audit.cdc_transform_runs
            where transform_run_id = %s
            """,
            (transform_run_id,),
        )
        transform = cursor.fetchone()

    ingest_summary = None
    if ingest is not None:
        ingest_summary = {
            "ingest_run_id": str(ingest[0]),
            "dag_id": ingest[1],
            "orchestration_run_id": ingest[2],
            "status": str(ingest[3]),
            "files_discovered": int(ingest[4]),
            "coverage_manifests_discovered": int(ingest[5]),
            "files_claimed": int(ingest[6]),
            "files_loaded": int(ingest[7]),
            "object_rows": int(ingest[8]),
            "inserted_rows": int(ingest[9]),
            "duplicate_rows": int(ingest[10]),
            "rejected_rows": int(ingest[11]),
            "gap_count": int(ingest[12]),
            "failure_summary": ingest[13],
        }
    transform_summary = None
    if transform is not None:
        transform_summary = {
            "transform_run_id": str(transform[0]),
            "dag_id": transform[1],
            "orchestration_run_id": transform[2],
            "status": str(transform[3]),
            "files_selected": int(transform[4]),
            "events_selected": int(transform[5]),
            "dbt_completed_at": str(transform[6]) if transform[6] else None,
            "finished_at": str(transform[7]) if transform[7] else None,
            "failure_summary": transform[8],
        }
    reconciliation_summary = {
        "manifest_count": int(reconciliation[0]),
        "duplicate_rows": int(reconciliation[1]),
        "rejected_rows": int(reconciliation[2]),
        "gap_count": int(reconciliation[3]),
        "failed_rows": int(reconciliation[4]),
    }
    return {
        "ingest": ingest_summary,
        "transform": transform_summary,
        "reconciliation": reconciliation_summary,
        "offset_gap_count": offset_gaps,
        "open_dlq_count": open_dlq,
        "quarantine_object_count": count_minio_objects_since(
            s3, QUARANTINE_PREFIX, started_at
        ),
    }


def record_parity() -> dict[str, Any]:
    result = run_command(
        ["python", "scripts/cdc/realtime_transform.py", "record-parity"],
        check=False,
    )
    summary = last_json_line(result.stdout or "") or {
        "parity_status": "FAIL",
        "failed_metrics": 1,
        "failure": "record-parity did not return JSON",
    }
    summary["command_exit_code"] = result.returncode
    return summary


def publication_parity_status() -> str | None:
    with warehouse_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            select parity_status
            from cdc_audit.cdc_publication_state
            where publication_name = 'olist_marts'
            """
        )
        row = cursor.fetchone()
    return None if row is None else str(row[0])


def parity_relation_summary() -> dict[str, Any]:
    relations = (
        "realtime_parity_report",
        "realtime_parity_checksums",
        "realtime_parity_grain_diffs",
    )
    result: dict[str, Any] = {}
    with warehouse_connection() as connection, connection.cursor() as cursor:
        for relation in relations:
            if relation == "realtime_parity_grain_diffs":
                cursor.execute(
                    """
                        select count(*),
                           coalesce(
                               array_agg(distinct metric_name order by metric_name),
                               array[]::text[]
                           )
                        from cdc_audit.realtime_parity_grain_diffs
                    """
                )
                count, metrics = fetch_one(cursor)
                result[relation] = {
                    "failed_count": int(count),
                    "failed_metrics": [str(metric) for metric in (metrics or [])][:100],
                }
            else:
                cursor.execute(
                    sql.SQL(
                        """
                        select count(*) filter (where status <> 'PASS'),
                               coalesce(
                                   array_agg(metric_name order by metric_name)
                                   filter (where status <> 'PASS'),
                                   array[]::text[]
                               )
                        from cdc_audit.{}
                        """
                    ).format(sql.Identifier(relation))
                )
                count, metrics = fetch_one(cursor)
                result[relation] = {
                    "failed_count": int(count),
                    "failed_metrics": [str(metric) for metric in (metrics or [])][:100],
                }
    return result


def acceptance_failures(result: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    if not result.get("source_contract_valid"):
        failures.append("source profile/archive contract did not pass")
    if not result.get("archive_sha256"):
        failures.append("archive SHA-256 is missing")
    batch = result.get("batch_reconciliation", {})
    if not batch.get("passed"):
        failures.append("batch reconciliation did not pass")
    row_counts = result.get("row_counts", {})
    expected = row_counts.get("expected", {})
    for side in ("batch", "realtime", "raw_cdc"):
        actual = row_counts.get(side, {})
        if actual != expected:
            failures.append(f"{side} current-state row counts differ from profile")
    connector = result.get("connector", {})
    if not connector.get("running") or connector.get("failed"):
        failures.append("Debezium connector or task is not RUNNING")
    audits = result.get("audit", {})
    if (audits.get("ingest") or {}).get("status") != "SUCCEEDED":
        failures.append("CDC ingest audit is not SUCCEEDED")
    if (audits.get("transform") or {}).get("status") != "SUCCEEDED":
        failures.append("CDC transform audit is not SUCCEEDED")
    for name in (
        "duplicate_rows",
        "rejected_rows",
        "gap_count",
        "failed_rows",
    ):
        if int((audits.get("reconciliation") or {}).get(name, 0)) != 0:
            failures.append(f"CDC reconciliation has non-zero {name}")
    if int(audits.get("offset_gap_count", 0)) != 0:
        failures.append("CDC partition watermarks contain offset gaps")
    if int(audits.get("open_dlq_count", 0)) != 0:
        failures.append("CDC has open DLQ records")
    if int(audits.get("quarantine_object_count", 0)) != 0:
        failures.append("NiFi produced quarantine objects")
    if result.get("overall_parity_status") != "PASS":
        failures.append("overall parity status is not PASS")
    parity = result.get("parity", {})
    if (
        int(parity.get("custom_failed_metric_count", parity.get("failed_metrics", 0)))
        != 0
    ):
        failures.append("custom parity reports contain failures")
    if parity.get("failed_dbt_utils_tests"):
        failures.append("dbt-utils equality tests contain failures")
    if int(parity.get("command_exit_code", 1)) != 0:
        failures.append("record-parity returned a non-zero exit code")
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", default=str(DEFAULT_ARCHIVE))
    parser.add_argument("--profile", default=str(DEFAULT_PROFILE))
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--poll-seconds", type=float, default=DEFAULT_POLL_SECONDS)
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    return parser.parse_args()


def write_report(path: Path, report: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(redact_value(report), indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )


def run_integration(
    args: argparse.Namespace, report: dict[str, Any] | None = None
) -> dict[str, Any]:
    started_at = now_utc()
    deadline = new_deadline(args.timeout_seconds)
    archive = Path(args.archive)
    profile = Path(args.profile)
    if not archive.is_absolute():
        archive = PROJECT_ROOT / archive
    if not profile.is_absolute():
        profile = PROJECT_ROOT / profile
    archive_digest = validate_same_archive_identity(archive, archive)
    contract_counts = source_contract(archive, profile)
    expected_counts = {
        table: contract_counts[table]
        for table in CAPTURED_TABLES
        if table in contract_counts
    }
    report = {} if report is None else report
    report.update(
        {
            "status": "RUNNING",
            "started_at": iso_timestamp(started_at),
            "archive": str(archive),
            "batch_archive": str(archive),
            "cdc_archive": str(archive),
            "profile": str(profile),
            "archive_sha256": archive_digest,
            "batch_archive_sha256": archive_digest,
            "cdc_archive_sha256": archive_digest,
            "source_contract_valid": True,
            "expected_batch_counts": contract_counts,
            "expected_capture_counts": expected_counts,
            "expected_capture_tables": list(CAPTURED_TABLES),
        }
    )

    s3 = create_minio_client()
    nifi_holder: list[NifiClient | None] = [None]

    def services_ready() -> tuple[bool, object]:
        if nifi_holder[0] is None:
            try:
                nifi_holder[0] = nifi_client()
            except Exception as exc:
                return False, {
                    "nifi_client": redact_text(f"{type(exc).__name__}: {exc}")
                }
        return service_snapshot(s3, nifi_holder[0])

    service_state = wait_for_condition(
        "required Compose services and bootstrap containers",
        services_ready,
        deadline,
        args.poll_seconds,
    )
    nifi = nifi_holder[0]
    if nifi is None:
        raise RuntimeError("NiFi client was not initialized after service readiness")
    report["services"] = service_state
    ensure_airflow_dags_registered(
        (
            "olist_modern_data_stack_local",
            "olist_cdc_ingest_local",
            "olist_cdc_transform_local",
            "olist_cdc_backfill_local",
            "olist_cdc_quality_local",
        ),
        deadline,
        args.poll_seconds,
    )

    token = now_utc().strftime("%Y%m%d%H%M%S")
    raw_dir = PROJECT_ROOT / "data" / "ci" / "raw" / f"batch-cdc-parity-{token}"
    raw_dir.mkdir(parents=True, exist_ok=True)
    batch_run_id = safe_airflow_run_id("manual__batch_cdc_parity", token)
    batch_conf = {
        "batch_date": FIXTURE_BATCH_DATE,
        "lookback_days": 3,
        "full_refresh": True,
        "source_archive": str(archive),
        "source_profile": str(profile),
        "raw_dir": str(raw_dir),
        "dead_letter_max_rows": 0,
        "dead_letter_max_rate": 0,
    }
    trigger_dag("olist_modern_data_stack_local", batch_run_id, conf=batch_conf)
    wait_for_dag(
        "olist_modern_data_stack_local", batch_run_id, deadline, args.poll_seconds
    )
    report["batch_run_id"] = batch_run_id
    report["batch_airflow_state"] = fetch_dag_run_state(
        "olist_modern_data_stack_local", batch_run_id
    )
    report["batch_reconciliation"] = batch_reconciliation_summary(
        FIXTURE_BATCH_DATE, contract_counts
    )

    report["registry"] = configure_registry()
    report["topic_inventory"] = validate_topic_inventory()

    report["seed"] = seed_oltp(archive)
    connector = register_connector(deadline, args.poll_seconds)
    report["connector"] = connector

    snapshot_started_at = started_at
    report["manifests"] = wait_for_condition(
        "closed normalized and coverage manifests for all captured tables",
        lambda: (lambda observed: (manifests_complete(observed), observed))(
            manifest_summary(s3, snapshot_started_at)
        ),
        deadline,
        args.poll_seconds,
    )
    report["kafka_lag_and_nifi"] = wait_for_condition(
        "Kafka consumer lag zero and NiFi queues drained without errors",
        lambda: (
            lambda lag, nifi_state: (
                kafka_nifi_drained(lag, nifi_state),
                {"kafka_lag": lag, "nifi": nifi_state},
            )
        )(kafka_consumer_lag(), nifi_snapshot(nifi)),
        deadline,
        args.poll_seconds,
    )

    existing_transform_runs = fetch_dag_run_ids("olist_cdc_transform_local")
    run_command(["airflow", "dags", "unpause", "olist_cdc_transform_local"])

    ingest_airflow_run_id = safe_airflow_run_id(
        "manual__batch_cdc_parity_ingest", token
    )
    trigger_dag("olist_cdc_ingest_local", ingest_airflow_run_id)
    wait_for_dag(
        "olist_cdc_ingest_local",
        ingest_airflow_run_id,
        deadline,
        args.poll_seconds,
    )
    report["ingest_airflow_run_id"] = ingest_airflow_run_id
    report["ingest_airflow_state"] = fetch_dag_run_state(
        "olist_cdc_ingest_local", ingest_airflow_run_id
    )

    transform_airflow_run = wait_for_asset_transform(
        existing_transform_runs, deadline, args.poll_seconds
    )
    transform_airflow_run_id = str(transform_airflow_run["run_id"])
    wait_for_dag(
        "olist_cdc_transform_local",
        transform_airflow_run_id,
        deadline,
        args.poll_seconds,
    )
    transform_run_id = f"olist_cdc_transform_local__{transform_airflow_run_id}".replace(
        ":", "_"
    ).replace("+", "_")
    report["transform_airflow_run"] = transform_airflow_run
    report["transform_airflow_state"] = fetch_dag_run_state(
        "olist_cdc_transform_local", transform_airflow_run_id
    )

    with warehouse_connection() as connection:
        report["row_counts"] = {
            "expected": expected_counts,
            **captured_row_counts(connection),
        }
    report["audit"] = audit_summary(
        f"olist_cdc_ingest_local__{ingest_airflow_run_id}",
        transform_run_id,
        s3,
        started_at,
    )
    report["parity"] = record_parity()
    report["parity_relations"] = parity_relation_summary()
    report["overall_parity_status"] = publication_parity_status()
    report["status"] = "PASS"
    report["finished_at"] = iso_timestamp()
    return report


def main() -> int:
    args = parse_args()
    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = PROJECT_ROOT / report_path
    report: dict[str, Any] = {
        "status": "FAIL",
        "started_at": iso_timestamp(),
        "report_path": str(report_path),
        "archive": str(args.archive),
        "profile": str(args.profile),
    }
    try:
        report = run_integration(args, report)
        report["acceptance_failures"] = acceptance_failures(report)
        report["status"] = "PASS" if not report["acceptance_failures"] else "FAIL"
    except Exception as exc:
        report["status"] = "FAIL"
        report["failure"] = redact_text(f"{type(exc).__name__}: {exc}")
        report["acceptance_failures"] = ["integration runner raised an exception"]
    finally:
        report["finished_at"] = iso_timestamp()
        write_report(report_path, report)
    print(json.dumps(redact_value(report), default=str, sort_keys=True))
    return 0 if report.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
