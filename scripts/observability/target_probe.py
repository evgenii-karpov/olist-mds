#!/usr/bin/env python3
"""Expose bounded target health and serving metrics for the local observability stack."""

from __future__ import annotations

import contextlib
import json
import logging
import os
import re
import socket
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, cast
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

LOGGER = logging.getLogger("olist.target_probe")
LISTEN_HOST = os.environ.get("TARGET_PROBE_LISTEN_HOST", "0.0.0.0")
LISTEN_PORT = int(os.environ.get("TARGET_PROBE_LISTEN_PORT", "9108"))
SPARK_STATUS_DIR = Path(os.environ.get("SPARK_STATUS_DIR", "/var/run/olist-spark"))
SPARK_STATUS_MAX_AGE_SECONDS = float(
    os.environ.get("SPARK_STATUS_MAX_AGE_SECONDS", "120")
)
KAFKA_EXPORTER_URL = os.environ.get(
    "KAFKA_EXPORTER_URL", "http://kafka-exporter:9308"
).rstrip("/")
SPARK_BRONZE_CONSUMER_GROUP = "olist-spark-bronze"
TARGET_CDC_TOPICS = frozenset(
    {
        "olist_cdc.olist_oltp.customers",
        "olist_cdc.olist_oltp.orders",
        "olist_cdc.olist_oltp.order_items",
        "olist_cdc.olist_oltp.order_payments",
        "olist_cdc.olist_oltp.order_reviews",
        "olist_cdc.olist_oltp.products",
        "olist_cdc.olist_oltp.sellers",
        "olist_cdc.olist_oltp.product_category_translation",
        "olist_cdc.transaction",
        "olist_cdc.heartbeat",
    }
)

TARGET_NAMES = (
    "mysql",
    "kafka",
    "kafka-connect",
    "apicurio",
    "spark",
    "spark-streaming",
    "minio",
    "polaris",
    "clickhouse",
    "airflow",
    "control-postgres",
)

_alert_lock = threading.Lock()
_alert_counts = {"firing": 0, "resolved": 0}
_request_count = 0


@dataclass(frozen=True, slots=True)
class Sample:
    name: str
    value: float
    labels: tuple[tuple[str, str], ...] = ()


@dataclass(slots=True)
class ProbeResult:
    up: bool
    samples: list[Sample] = field(default_factory=list)


def _read_secret(path: str) -> str:
    value = Path(path).read_text(encoding="utf-8").strip()
    if not value:
        raise RuntimeError(f"secret file is empty: {path}")
    return value


def _labels(labels: tuple[tuple[str, str], ...]) -> str:
    if not labels:
        return ""
    encoded = ",".join(
        f'{key}="{value.replace(chr(92), chr(92) * 2).replace(chr(34), chr(92) + chr(34))}"'
        for key, value in labels
    )
    return "{" + encoded + "}"


def _render(samples: list[Sample]) -> str:
    help_text = {
        "olist_target_up": "Whether a bounded target probe is healthy.",
        "olist_target_probe_requests_total": "Number of target probe HTTP requests.",
        "olist_target_probe_failures_total": "Number of failed target probe operations.",
        "olist_alertmanager_webhook_alerts_total": "Alerts received by the local Alertmanager webhook.",
        "olist_mysql_binlog_position": "Current MySQL binary log position.",
        "olist_mysql_gtid_enabled": "Whether MySQL GTID mode is enabled.",
        "olist_connect_connector_running": "Whether the target Debezium connector is RUNNING.",
        "olist_connect_task_running": "Whether a target Debezium task is RUNNING.",
        "olist_apicurio_compatibility_ready": "Whether the target registry compatibility rule is available.",
        "olist_spark_master_up": "Whether the Spark master HTTP endpoint is healthy.",
        "olist_spark_worker_up": "Whether the Spark worker HTTP endpoint is healthy.",
        "olist_spark_streaming_state": "Whether a Spark streaming application is READY.",
        "olist_spark_streaming_status_stale": "Whether a Spark streaming status file is stale.",
        "olist_spark_streaming_last_update_timestamp_seconds": "Last Spark streaming status update time.",
        "olist_spark_streaming_queries_running": "Number of RUNNING queries in a Spark streaming application.",
        "olist_spark_streaming_query_failures": "Number of failed queries in a Spark streaming application.",
        "olist_kafka_lag_source_up": "Whether the target Kafka partition offset source is available.",
        "olist_kafka_consumer_lag": "Kafka records between the target Spark checkpoint and the partition end offset.",
        "olist_serving_publication_age_seconds": "Age of the latest successful serving publication.",
        "olist_serving_last_published_sync_run_seq": "Latest published serving sync sequence.",
        "olist_serving_rejected_boundary": "Whether the latest serving boundary is rejected.",
        "olist_serving_active_lease": "Whether serving currently holds a mutation lease.",
    }
    counter_names = {
        "olist_target_probe_requests_total",
        "olist_target_probe_failures_total",
        "olist_alertmanager_webhook_alerts_total",
    }
    lines: list[str] = []
    emitted: set[str] = set()
    for sample in samples:
        if sample.name not in emitted:
            description = help_text.get(sample.name, sample.name)
            lines.append(f"# HELP {sample.name} {description}")
            lines.append(
                f"# TYPE {sample.name} {'counter' if sample.name in counter_names else 'gauge'}"
            )
            emitted.add(sample.name)
        lines.append(f"{sample.name}{_labels(sample.labels)} {sample.value:g}")
    return "\n".join(lines) + "\n"


def _http_json(url: str, timeout: float = 5.0) -> tuple[int, Any]:
    request = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            try:
                return response.status, json.loads(raw) if raw.strip() else None
            except json.JSONDecodeError:
                return response.status, None
    except HTTPError as exc:
        return exc.code, None
    except URLError:
        return 0, None


def _http_text(url: str, timeout: float = 5.0) -> tuple[int, str]:
    try:
        with urlopen(url, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        return exc.code, ""
    except URLError:
        return 0, ""


def _http_up(url: str, timeout: float = 5.0) -> bool:
    status, _ = _http_json(url, timeout)
    return 200 <= status < 300


def _tcp_up(host: str, port: int, timeout: float = 5.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _probe_mysql() -> ProbeResult:
    import mysql.connector

    connection = mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "mysql"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        database=os.environ.get("MYSQL_DATABASE", "olist_oltp"),
        user=os.environ.get("MYSQL_USER", "olist_cdc_reader"),
        password=_read_secret(
            os.environ.get(
                "MYSQL_PASSWORD_FILE", "/run/secrets/mysql_cdc_reader_password"
            )
        ),
        connection_timeout=5,
    )
    try:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SHOW BINARY LOG STATUS")
            binlog = cast(dict[str, Any], cursor.fetchone() or {})
            cursor.execute(
                "SELECT @@GLOBAL.gtid_mode AS gtid_mode, "
                "@@GLOBAL.gtid_executed AS gtid_executed"
            )
            gtid = cast(dict[str, Any], cursor.fetchone() or {})
        finally:
            cursor.close()
    finally:
        connection.close()
    position = float(binlog.get("Position") or 0)
    gtid_mode = str(gtid.get("gtid_mode") or "OFF").upper()
    return ProbeResult(
        up=True,
        samples=[
            Sample("olist_mysql_binlog_position", position),
            Sample("olist_mysql_gtid_enabled", float(gtid_mode != "OFF")),
        ],
    )


def _probe_kafka() -> ProbeResult:
    up = _tcp_up(
        os.environ.get("KAFKA_HOST", "kafka"),
        int(os.environ.get("KAFKA_PORT", "29092")),
    )
    return ProbeResult(up=up)


def _probe_connect() -> ProbeResult:
    base = os.environ.get("KAFKA_CONNECT_URL", "http://kafka-connect:8083").rstrip("/")
    status, payload = _http_json(
        f"{base}/connectors/{os.environ.get('CONNECTOR_NAME', 'olist-mysql-cdc')}/status"
    )
    connector = payload.get("connector", {}) if isinstance(payload, dict) else {}
    tasks = payload.get("tasks", []) if isinstance(payload, dict) else []
    connector_running = connector.get("state") == "RUNNING"
    samples = [
        Sample(
            "olist_connect_connector_running",
            float(connector_running),
            (("connector", os.environ.get("CONNECTOR_NAME", "olist-mysql-cdc")),),
        )
    ]
    task_states = []
    for task in tasks[:16]:
        task_id = str(task.get("id", "unknown"))
        running = task.get("state") == "RUNNING"
        task_states.append(running)
        samples.append(
            Sample(
                "olist_connect_task_running",
                float(running),
                (
                    ("connector", os.environ.get("CONNECTOR_NAME", "olist-mysql-cdc")),
                    ("task", task_id),
                ),
            )
        )
    return ProbeResult(
        up=status == 200
        and connector_running
        and bool(task_states)
        and all(task_states),
        samples=samples,
    )


def _probe_apicurio() -> ProbeResult:
    base = os.environ.get(
        "APICURIO_REGISTRY_URL",
        "http://apicurio-registry:8080/apis/registry/v3",
    ).rstrip("/")
    health_status, _ = _http_json(f"{base}/system/info")
    rule_status, _ = _http_json(f"{base}/groups/olist_cdc/rules/COMPATIBILITY")
    return ProbeResult(
        up=200 <= health_status < 300,
        samples=[
            Sample("olist_apicurio_compatibility_ready", float(rule_status == 200))
        ],
    )


def _probe_spark() -> ProbeResult:
    master_up = _http_up("http://spark-master:8080")
    worker_up = _http_up("http://spark-worker:8081")
    return ProbeResult(
        up=master_up and worker_up,
        samples=[
            Sample("olist_spark_master_up", float(master_up)),
            Sample("olist_spark_worker_up", float(worker_up)),
        ],
    )


def _parse_timestamp(value: object) -> float:
    if not isinstance(value, str):
        return 0.0
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def _prometheus_labels(raw: str) -> dict[str, str]:
    labels: dict[str, str] = {}
    for match in re.finditer(r'([a-zA-Z_][a-zA-Z0-9_]*)="((?:\\.|[^"])*)"', raw):
        value = match.group(2).replace(r"\"", '"').replace(r"\\", "\\")
        labels[match.group(1)] = value
    return labels


def _kafka_partition_end_offsets() -> tuple[int, dict[str, float]]:
    status, body = _http_text(f"{KAFKA_EXPORTER_URL}/metrics")
    offsets: dict[str, float] = {}
    if status != 200:
        return status, offsets
    for line in body.splitlines():
        match = re.match(
            r"^kafka_topic_partition_current_offset\{([^}]*)\}\s+([-+0-9.eE]+)$",
            line,
        )
        if not match:
            continue
        labels = _prometheus_labels(match.group(1))
        topic = labels.get("topic")
        partition = labels.get("partition")
        if topic in TARGET_CDC_TOPICS and partition is not None:
            try:
                offsets[f"{topic}:{partition}"] = float(match.group(2))
            except ValueError:
                continue
    return status, offsets


def _probe_spark_streaming() -> ProbeResult:
    now = time.time()
    samples: list[Sample] = []
    healthy = True
    bronze_partition_offsets: dict[str, float] = {}
    for component in ("bronze", "silver"):
        path = SPARK_STATUS_DIR / component / "status.json"
        status: dict[str, Any] = {}
        with contextlib.suppress(OSError, json.JSONDecodeError):
            status = json.loads(path.read_text(encoding="utf-8"))
        updated_at = _parse_timestamp(status.get("updated_at_utc"))
        stale = updated_at <= 0 or now - updated_at > SPARK_STATUS_MAX_AGE_SECONDS
        queries = status.get("queries", [])
        if not isinstance(queries, list):
            queries = []
        if component == "bronze":
            for query in queries:
                if (
                    not isinstance(query, dict)
                    or query.get("name") != "kafka_to_bronze"
                ):
                    continue
                offsets = query.get("partition_offsets", {})
                if not isinstance(offsets, dict):
                    continue
                for key, value in offsets.items():
                    if not isinstance(key, str) or not isinstance(value, (int, float)):
                        continue
                    topic, separator, partition = key.rpartition(":")
                    if separator and topic in TARGET_CDC_TOPICS and partition.isdigit():
                        bronze_partition_offsets[key] = float(value)
        failures = sum(
            1
            for query in queries
            if isinstance(query, dict)
            and (query.get("error_class") or query.get("error_code"))
        )
        ready = (
            status.get("overall_state") == "READY"
            and bool(queries)
            and failures == 0
            and all(
                isinstance(query, dict) and query.get("state") == "RUNNING"
                for query in queries
            )
        )
        healthy = healthy and ready
        samples.extend(
            [
                Sample(
                    "olist_spark_streaming_state",
                    float(ready),
                    (("component", component),),
                ),
                Sample(
                    "olist_spark_streaming_status_stale",
                    float(stale),
                    (("component", component),),
                ),
                Sample(
                    "olist_spark_streaming_last_update_timestamp_seconds",
                    updated_at,
                    (("component", component),),
                ),
                Sample(
                    "olist_spark_streaming_queries_running",
                    float(
                        sum(
                            1
                            for query in queries
                            if isinstance(query, dict)
                            and query.get("state") == "RUNNING"
                        )
                    ),
                    (("component", component),),
                ),
                Sample(
                    "olist_spark_streaming_query_failures",
                    float(failures),
                    (("component", component),),
                ),
            ]
        )
    lag_source_up = True
    if bronze_partition_offsets:
        offset_status, end_offsets = _kafka_partition_end_offsets()
        lag_source_up = offset_status == 200 and all(
            key in end_offsets for key in bronze_partition_offsets
        )
        for key, processed_offset in sorted(bronze_partition_offsets.items()):
            topic, _, partition = key.rpartition(":")
            lag = max(end_offsets.get(key, processed_offset) - processed_offset, 0.0)
            samples.append(
                Sample(
                    "olist_kafka_consumer_lag",
                    lag,
                    (
                        ("consumer_group", SPARK_BRONZE_CONSUMER_GROUP),
                        ("topic", topic),
                        ("partition", partition),
                    ),
                )
            )
    samples.append(Sample("olist_kafka_lag_source_up", float(lag_source_up)))
    healthy = healthy and lag_source_up
    return ProbeResult(up=healthy, samples=samples)


def _probe_control_postgres() -> ProbeResult:
    import psycopg2

    connection = psycopg2.connect(
        host=os.environ.get("CONTROL_POSTGRES_HOST", "platform-postgres"),
        port=int(os.environ.get("CONTROL_POSTGRES_PORT", "5432")),
        dbname=os.environ.get("CONTROL_POSTGRES_DB", "olist_control"),
        user=os.environ.get("CONTROL_POSTGRES_USER", "olist_control"),
        password=_read_secret(
            os.environ.get(
                "CONTROL_POSTGRES_PASSWORD_FILE",
                "/run/secrets/control_postgres_password",
            )
        ),
        connect_timeout=5,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(EXTRACT(EPOCH FROM clock_timestamp() - "
                "MAX(published_at)), 86400) "
                "FROM serving.sync_runs WHERE status IN ('SUCCEEDED', 'NOOP')"
            )
            publication_row = cursor.fetchone()
            publication_age = float(publication_row[0]) if publication_row else 86400.0
            cursor.execute(
                "SELECT last_published_sync_run_seq, lease_owner_id "
                "FROM serving.runtime_state WHERE singleton_key = 1"
            )
            runtime = cursor.fetchone() or (0, None)
            cursor.execute(
                "SELECT status, status_reason FROM serving.sync_runs "
                "ORDER BY sync_run_seq DESC LIMIT 1"
            )
            latest = cursor.fetchone() or ("NOOP", "NONE")
    finally:
        connection.close()
    rejected = latest[1] in ("REJECTED_TRANSACTION", "SNAPSHOT_REJECTED")
    return ProbeResult(
        up=True,
        samples=[
            Sample("olist_serving_publication_age_seconds", publication_age),
            Sample("olist_serving_last_published_sync_run_seq", float(runtime[0] or 0)),
            Sample("olist_serving_active_lease", float(runtime[1] is not None)),
            Sample("olist_serving_rejected_boundary", float(rejected)),
            Sample(
                "olist_serving_publication_status",
                1.0,
                (("status", str(latest[0] or "UNKNOWN")),),
            ),
        ],
    )


def _probe_http_target(target: str, url: str) -> ProbeResult:
    return ProbeResult(up=_http_up(url), samples=[])


def probe_target(target: str) -> ProbeResult:
    if target == "mysql":
        return _probe_mysql()
    if target == "kafka":
        return _probe_kafka()
    if target == "kafka-connect":
        return _probe_connect()
    if target == "apicurio":
        return _probe_apicurio()
    if target == "spark":
        return _probe_spark()
    if target == "spark-streaming":
        return _probe_spark_streaming()
    if target == "control-postgres":
        return _probe_control_postgres()
    urls = {
        "minio": "http://minio:9000/minio/health/ready",
        "polaris": "http://polaris:8182/q/health",
        "clickhouse": "http://clickhouse:8123/ping",
        "airflow": "http://airflow:8080/api/v2/monitor/health",
    }
    if target in urls:
        return _probe_http_target(target, urls[target])
    raise ValueError(f"unknown target: {target}")


def _self_samples() -> list[Sample]:
    with _alert_lock:
        request_count = _request_count
        alert_counts = dict(_alert_counts)
    return [
        Sample("olist_target_probe_requests_total", float(request_count)),
        *(
            Sample(
                "olist_alertmanager_webhook_alerts_total",
                float(count),
                (("state", state),),
            )
            for state, count in alert_counts.items()
        ),
    ]


def collect_metrics(target: str | None = None) -> str:
    samples = _self_samples()
    if target is None:
        return _render(samples)
    try:
        result = probe_target(target)
    except Exception as exc:
        LOGGER.warning("target probe failed for %s: %s", target, type(exc).__name__)
        result = ProbeResult(up=False)
    samples.append(Sample("olist_target_up", float(result.up), (("target", target),)))
    samples.extend(result.samples)
    if not result.up:
        samples.append(
            Sample("olist_target_probe_failures_total", 1.0, (("target", target),))
        )
    return _render(samples)


class ProbeHandler(BaseHTTPRequestHandler):
    server_version = "olist-target-probe/1.0"

    def _write(self, status: int, body: str, content_type: str = "text/plain") -> None:
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        global _request_count
        with _alert_lock:
            _request_count += 1
        parsed = urlparse(self.path)
        if parsed.path in ("/healthz", "/-/ready"):
            self._write(200, "ready\n")
            return
        if parsed.path not in ("/metrics", "/probe"):
            self._write(404, "not found\n")
            return
        target_values = parse_qs(parsed.query).get("target", [])
        target = target_values[0] if target_values else None
        if parsed.path == "/probe" and target not in TARGET_NAMES:
            self._write(400, "target query parameter is required\n")
            return
        self._write(200, collect_metrics(target))

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/alertmanager/webhook":
            self._write(404, "not found\n")
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(size) or b"{}")
            state = str(payload.get("status", "unknown"))
        except (ValueError, json.JSONDecodeError):
            self._write(400, "invalid webhook payload\n")
            return
        if state not in _alert_counts:
            self._write(400, "unsupported alert state\n")
            return
        with _alert_lock:
            _alert_counts[state] += 1
        self._write(200, "accepted\n")

    def log_message(self, format: str, *_args: object) -> None:
        return


def main() -> int:
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    server = ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), ProbeHandler)
    LOGGER.info("target probe listening on %s:%s", LISTEN_HOST, LISTEN_PORT)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
