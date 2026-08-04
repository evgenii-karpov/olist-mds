from __future__ import annotations

import json
import tempfile
import unittest
from collections import defaultdict, deque
from collections.abc import Mapping, Sequence
from email.message import Message
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest.mock import patch
from urllib.error import HTTPError

from streaming.connect.bootstrap import (
    BootstrapError,
    HttpResponse,
    JsonHttpClient,
    ensure_connector,
    ensure_registry,
    read_password,
    redact,
    redact_text,
    render_connector_payload,
    wait_for_connector_running,
)

ROOT = Path(__file__).resolve().parents[2]
CONNECTOR_PATH = ROOT / "streaming" / "connect" / "olist-mysql-cdc.json"
REGISTRY_PATH = ROOT / "streaming" / "connect" / "apicurio-contract.json"
APICURIO_ENTRYPOINT = ROOT / "streaming" / "connect" / "apicurio-file-env.sh"
CONNECT_DOCKERFILE = ROOT / "streaming" / "connect" / "Dockerfile"
PLUGIN_INVENTORY = ROOT / "streaming" / "connect" / "plugin-inventory.sha256"

TABLES = (
    "customers",
    "orders",
    "order_items",
    "order_payments",
    "order_reviews",
    "products",
    "sellers",
    "product_category_translation",
)


class FakeTransport:
    def __init__(self) -> None:
        self.responses: dict[tuple[str, str], deque[HttpResponse]] = defaultdict(deque)
        self.calls: list[
            tuple[str, str, Mapping[str, Any] | None, tuple[str, ...]]
        ] = []

    def add(self, method: str, path: str, status: int, body: Any = None) -> None:
        self.responses[(method, path)].append(HttpResponse(status, body))

    def request(
        self,
        method: str,
        path: str,
        payload: Mapping[str, Any] | None = None,
        *,
        expected: frozenset[int] = frozenset({200}),
        sensitive_values: Sequence[str] = (),
    ) -> HttpResponse:
        self.calls.append((method, path, payload, tuple(sensitive_values)))
        response = self.responses[(method, path)].popleft()
        if response.status not in expected:
            raise AssertionError(
                f"fake response {response.status} not in expected {expected}"
            )
        return response


class ConnectorContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.template = json.loads(CONNECTOR_PATH.read_text(encoding="utf-8"))
        self.config = self.template["config"]

    def test_connector_is_exact_mysql_capture_contract(self) -> None:
        self.assertEqual("olist-mysql-cdc", self.template["name"])
        expected = {
            "connector.class": "io.debezium.connector.mysql.MySqlConnector",
            "tasks.max": "1",
            "database.hostname": "mysql",
            "database.port": "3306",
            "database.user": "olist_cdc_reader",
            "database.server.id": "18402",
            "database.include.list": "olist_oltp",
            "topic.prefix": "olist_cdc",
            "snapshot.mode": "initial",
            "include.schema.changes": "true",
            "provide.transaction.metadata": "true",
            "tombstones.on.delete": "true",
            "decimal.handling.mode": "precise",
            "time.precision.mode": "adaptive_time_microseconds",
            "binary.handling.mode": "bytes",
            "schema.history.internal.kafka.topic": "olist_cdc.schema_history",
            "schema.history.internal.kafka.bootstrap.servers": "kafka:29092",
            "heartbeat.interval.ms": "10000",
            "topic.heartbeat.prefix": "olist_cdc.heartbeat",
            "errors.tolerance": "none",
            "schema.name.adjustment.mode": "avro",
        }
        for key, value in expected.items():
            self.assertEqual(value, self.config[key], key)
        self.assertEqual(
            [f"olist_oltp.{table}" for table in TABLES],
            self.config["table.include.list"].split(","),
        )
        self.assertNotIn("geolocation", self.config["table.include.list"])
        self.assertNotIn("olist_simulator", self.config["table.include.list"])

    def test_only_heartbeat_router_smt_is_configured(self) -> None:
        self.assertEqual("routeHeartbeat", self.config["transforms"])
        transform_types = {
            value
            for key, value in self.config.items()
            if key.startswith("transforms.") and key.endswith(".type")
        }
        self.assertEqual(
            {"org.apache.kafka.connect.transforms.RegexRouter"}, transform_types
        )
        self.assertFalse(
            any("ExtractNewRecordState" in value for value in self.config.values())
        )
        self.assertEqual(
            "olist_cdc\\.heartbeat\\.olist_cdc",
            self.config["transforms.routeHeartbeat.regex"],
        )
        self.assertIn(
            "ON DUPLICATE KEY UPDATE",
            self.config["heartbeat.action.query"],
        )

    def test_key_and_value_converters_match_apicurio_contract(self) -> None:
        for side in ("key", "value"):
            prefix = f"{side}.converter"
            self.assertEqual(
                "io.apicurio.registry.utils.converter.AvroConverter",
                self.config[prefix],
            )
            self.assertEqual(
                "http://apicurio-registry:8080/apis/registry/v2",
                self.config[f"{prefix}.apicurio.registry.url"],
            )
            self.assertEqual(
                "true", self.config[f"{prefix}.apicurio.registry.auto-register"]
            )
            self.assertEqual(
                "true", self.config[f"{prefix}.apicurio.registry.find-latest"]
            )
            self.assertEqual(
                "true", self.config[f"{prefix}.apicurio.registry.as-confluent"]
            )
            self.assertEqual("contentId", self.config[f"{prefix}.apicurio.use-id"])
            self.assertEqual(
                "false", self.config[f"{prefix}.apicurio.registry.headers.enabled"]
            )
            self.assertEqual("false", self.config[f"{prefix}.schemas.enable"])
            self.assertEqual(
                "io.apicurio.registry.serde.strategy.TopicIdStrategy",
                self.config[f"{prefix}.apicurio.registry.artifact-resolver-strategy"],
            )
            self.assertEqual(
                "olist_cdc",
                self.config[f"{prefix}.apicurio.registry.artifact.group-id"],
            )

    def test_template_contains_no_password_or_placeholder(self) -> None:
        raw = CONNECTOR_PATH.read_text(encoding="utf-8").lower()
        self.assertNotIn("database.password", raw)
        self.assertNotIn("${", raw)
        payload = render_connector_payload(self.template, "p@ss word")
        self.assertEqual("p@ss word", payload["config"]["database.password"])
        self.assertNotIn("database.password", self.template["config"])

    def test_connect_image_declares_only_target_plugins(self) -> None:
        dockerfile = CONNECT_DOCKERFILE.read_text(encoding="utf-8")
        inventory = PLUGIN_INVENTORY.read_text(encoding="utf-8")
        self.assertIn("quay.io/debezium/connect:3.6.0.Final", dockerfile)
        self.assertIn("debezium-connector-mysql-3.6.0.Final.jar", dockerfile)
        self.assertEqual(
            {
                "apicurio-registry-utils-converter-3.2.5.jar",
                "apicurio-registry-avro-serde-kafka-3.2.5.jar",
                "avro-1.12.1.jar",
            },
            {
                line.split()[-1].rsplit("/", maxsplit=1)[-1]
                for line in inventory.splitlines()
            },
        )

    def test_password_file_preserves_spaces_and_removes_only_newline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "secret"
            path.write_text("  p@ss word  \r\n", encoding="utf-8")
            self.assertEqual("  p@ss word  ", read_password(path))
            path.write_text("first\nsecond\n", encoding="utf-8")
            with self.assertRaises(BootstrapError):
                read_password(path)

    def test_redaction_handles_nested_values_and_error_text(self) -> None:
        value = {
            "config": {"database.password": "danger", "database.user": "safe"},
            "tokenValue": "also-danger",
        }
        redacted = redact(value)
        self.assertEqual("<redacted>", redacted["config"]["database.password"])
        self.assertEqual("<redacted>", redacted["tokenValue"])
        self.assertEqual("safe", redacted["config"]["database.user"])
        message = '{"database.password":"danger","reason":"danger"}'
        sanitized = redact_text(message, ("danger",))
        self.assertNotIn("danger", sanitized)
        self.assertIn("<redacted>", sanitized)

    def test_redaction_handles_literal_and_json_escaped_secret(self) -> None:
        secret = 's"e\\cret'
        escaped = json.dumps(secret)[1:-1]
        message = f"literal={secret}; json={escaped}"
        sanitized = redact_text(message, (secret,))
        self.assertNotIn(secret, sanitized)
        self.assertNotIn(escaped, sanitized)
        self.assertEqual(2, sanitized.count("<redacted>"))

    def test_secret_bearing_http_error_never_includes_response_body(self) -> None:
        secret = 's"e\\cret'
        body = json.dumps(
            {"database.password": secret, "unique_marker": "body-must-stay-hidden"}
        ).encode()
        error = HTTPError(
            "http://connect/connectors",
            500,
            "Internal Server Error",
            hdrs=Message(),
            fp=BytesIO(body),
        )
        client = JsonHttpClient("http://connect")
        with (
            patch("streaming.connect.bootstrap.urlopen", side_effect=error),
            self.assertRaises(BootstrapError) as caught,
        ):
            client.request(
                "POST",
                "connectors",
                {"database.password": secret},
                sensitive_values=(secret,),
            )
        message = str(caught.exception)
        self.assertNotIn("body-must-stay-hidden", message)
        self.assertNotIn(secret, message)
        self.assertNotIn(json.dumps(secret)[1:-1], message)

    def test_registry_bootstrap_creates_group_then_group_rule(self) -> None:
        contract = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        transport = FakeTransport()
        transport.add("GET", "groups/olist_cdc", 404)
        transport.add("POST", "groups", 200, {"groupId": "olist_cdc"})
        transport.add("GET", "groups/olist_cdc/rules/COMPATIBILITY", 404)
        transport.add("POST", "groups/olist_cdc/rules", 204)

        self.assertEqual("created", ensure_registry(transport, contract))
        self.assertEqual(
            [
                ("GET", "groups/olist_cdc"),
                ("POST", "groups"),
                ("GET", "groups/olist_cdc/rules/COMPATIBILITY"),
                ("POST", "groups/olist_cdc/rules"),
            ],
            [(method, path) for method, path, _, _ in transport.calls],
        )
        self.assertEqual(
            {"ruleType": "COMPATIBILITY", "config": "BACKWARD_TRANSITIVE"},
            transport.calls[-1][2],
        )

    def test_registry_runtime_uses_sql_postgres_and_file_secrets(self) -> None:
        contract = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            {
                "APICURIO_STORAGE_KIND": "sql",
                "APICURIO_STORAGE_SQL_KIND": "postgresql",
                "APICURIO_DATASOURCE_URL": (
                    "jdbc:postgresql://platform-postgres:5432/apicurio"
                ),
                "APICURIO_DATASOURCE_USERNAME_FILE": ("/run/secrets/apicurio_db_user"),
                "APICURIO_DATASOURCE_PASSWORD_FILE": (
                    "/run/secrets/apicurio_db_password"
                ),
            },
            contract["runtime_environment"],
        )
        wrapper = APICURIO_ENTRYPOINT.read_text(encoding="utf-8")
        self.assertNotIn("set -x", wrapper)
        self.assertIn("unset APICURIO_DATASOURCE_USERNAME_FILE", wrapper)
        self.assertIn("unset secret_value", wrapper)

    def test_registry_bootstrap_updates_drift_and_is_idempotent(self) -> None:
        contract = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        drifted = FakeTransport()
        drifted.add("GET", "groups/olist_cdc", 200, {"groupId": "olist_cdc"})
        drifted.add(
            "GET",
            "groups/olist_cdc/rules/COMPATIBILITY",
            200,
            {"ruleType": "COMPATIBILITY", "config": "BACKWARD"},
        )
        drifted.add("PUT", "groups/olist_cdc/rules/COMPATIBILITY", 204)
        self.assertEqual("updated", ensure_registry(drifted, contract))

        current = FakeTransport()
        current.add("GET", "groups/olist_cdc", 200, {"groupId": "olist_cdc"})
        current.add(
            "GET",
            "groups/olist_cdc/rules/COMPATIBILITY",
            200,
            {"ruleType": "COMPATIBILITY", "config": "BACKWARD_TRANSITIVE"},
        )
        self.assertEqual("unchanged", ensure_registry(current, contract))

    def test_connector_create_immutable_drift_and_failed_guard(self) -> None:
        payload = render_connector_payload(self.template, "danger")

        create = FakeTransport()
        create.add("GET", "connectors/olist-mysql-cdc/config", 404)
        create.add("POST", "connectors", 201)
        create.add(
            "GET",
            "connectors/olist-mysql-cdc/status",
            200,
            {
                "connector": {"state": "RUNNING"},
                "tasks": [{"id": 0, "state": "RUNNING"}],
            },
        )
        self.assertEqual("created", ensure_connector(create, payload))
        self.assertEqual(("danger",), create.calls[-1][3])

        drifted = FakeTransport()
        old_config = dict(payload["config"])
        old_config["heartbeat.interval.ms"] = "1"
        drifted.add("GET", "connectors/olist-mysql-cdc/config", 200, old_config)
        drifted.add(
            "GET",
            "connectors/olist-mysql-cdc/status",
            200,
            {
                "connector": {"state": "RUNNING"},
                "tasks": [{"id": 0, "state": "RUNNING"}],
            },
        )
        with self.assertRaisesRegex(BootstrapError, "configuration drift"):
            ensure_connector(drifted, payload)
        self.assertFalse(any(call[0] == "PUT" for call in drifted.calls))

        unchanged = FakeTransport()
        masked_config = dict(payload["config"])
        masked_config["database.password"] = "********"
        unchanged.add("GET", "connectors/olist-mysql-cdc/config", 200, masked_config)
        unchanged.add(
            "GET",
            "connectors/olist-mysql-cdc/status",
            200,
            {
                "connector": {"state": "RUNNING"},
                "tasks": [{"id": 0, "state": "RUNNING"}],
            },
        )
        self.assertEqual("unchanged", ensure_connector(unchanged, payload))

        failed = FakeTransport()
        failed.add("GET", "connectors/olist-mysql-cdc/config", 200, payload["config"])
        failed.add(
            "GET",
            "connectors/olist-mysql-cdc/status",
            200,
            {
                "connector": {"state": "RUNNING"},
                "tasks": [{"id": 0, "state": "FAILED"}],
            },
        )
        with self.assertRaisesRegex(BootstrapError, "task-0"):
            ensure_connector(failed, payload)

    def test_connector_readiness_polls_transitional_states(self) -> None:
        transport = FakeTransport()
        transport.add(
            "GET",
            "connectors/olist-mysql-cdc/status",
            200,
            {"connector": {"state": "PAUSED"}, "tasks": []},
        )
        transport.add(
            "GET",
            "connectors/olist-mysql-cdc/status",
            200,
            {
                "connector": {"state": "RUNNING"},
                "tasks": [{"id": 0, "state": "UNASSIGNED"}],
            },
        )
        transport.add(
            "GET",
            "connectors/olist-mysql-cdc/status",
            200,
            {
                "connector": {"state": "RUNNING"},
                "tasks": [{"id": 0, "state": "RUNNING"}],
            },
        )
        current = 0.0

        def monotonic() -> float:
            return current

        def sleep(seconds: float) -> None:
            nonlocal current
            current += seconds

        wait_for_connector_running(
            transport,
            password="danger",
            timeout_seconds=2,
            poll_interval_seconds=0.5,
            monotonic=monotonic,
            sleep=sleep,
        )
        self.assertEqual(1.0, current)

    def test_connector_readiness_times_out_for_empty_or_paused_status(self) -> None:
        for body in (
            {"connector": {"state": "RUNNING"}, "tasks": []},
            {
                "connector": {"state": "PAUSED"},
                "tasks": [{"id": 0, "state": "PAUSED"}],
            },
            {
                "connector": {"state": "RESTARTING"},
                "tasks": [{"id": 0, "state": "RESTARTING"}],
            },
        ):
            with self.subTest(body=body):
                transport = FakeTransport()
                transport.add("GET", "connectors/olist-mysql-cdc/status", 200, body)
                with self.assertRaisesRegex(BootstrapError, "timed out"):
                    wait_for_connector_running(
                        transport,
                        password="danger",
                        timeout_seconds=0,
                        sleep=lambda _: None,
                    )

    def test_failed_status_diagnostic_redacts_escaped_secret(self) -> None:
        secret = 's"e\\cret'
        transport = FakeTransport()
        transport.add(
            "GET",
            "connectors/olist-mysql-cdc/status",
            200,
            {
                "connector": {"state": "RUNNING"},
                "tasks": [{"id": 0, "state": "FAILED", "trace": f"failure: {secret}"}],
            },
        )
        with self.assertRaises(BootstrapError) as caught:
            wait_for_connector_running(
                transport,
                password=secret,
                timeout_seconds=0,
                sleep=lambda _: None,
            )
        message = str(caught.exception)
        self.assertNotIn(secret, message)
        self.assertNotIn(json.dumps(secret)[1:-1], message)
        self.assertIn("<redacted>", message)


if __name__ == "__main__":
    unittest.main()
