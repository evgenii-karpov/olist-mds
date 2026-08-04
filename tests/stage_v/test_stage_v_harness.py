from __future__ import annotations

import decimal
import json
import os
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.validation.stage_v_candidate_e2e import (
    MANDATORY_GATES,
    REQUIRED_ASSERTIONS,
    StageVOrchestrator,
    valid_additive_snapshot_transition,
    valid_serving_target_offsets,
    validate_acceptance_summary,
)
from scripts.validation.stage_v_probes import (
    ClickHouseProbe,
    MySQLProbe,
    build_canonical_manifest,
    normalize_value,
    sanitize_text,
)

ROOT = Path(__file__).resolve().parents[2]


class StageVHarnessUnitTests(unittest.TestCase):
    def test_secrets_redaction(self) -> None:
        raw_log = "Error connecting with password=my_secret_pwd_123; postgres://user:pass123@localhost:5432/db"
        sanitized = sanitize_text(raw_log)
        self.assertNotIn("my_secret_pwd_123", sanitized)
        self.assertNotIn("pass123", sanitized)
        self.assertIn("[REDACTED_SECRET]", sanitized)

    def test_value_normalization(self) -> None:
        self.assertIsNone(normalize_value(None))
        self.assertEqual(normalize_value("hello"), "hello")
        self.assertEqual(normalize_value(123), 123)
        self.assertEqual(normalize_value(decimal.Decimal("19.99")), "19.99")

        dt = datetime(2026, 8, 1, 12, 0, 0, 123456, tzinfo=UTC)
        self.assertEqual(normalize_value(dt), "2026-08-01T12:00:00.123456Z")

    def test_target_offsets_accept_all_partitions_for_each_serving_topic(self) -> None:
        offsets = {
            "olist_cdc.olist_oltp.customers:0": 8,
            "olist_cdc.olist_oltp.orders:0": 3,
            "olist_cdc.olist_oltp.orders:1": 4,
            "olist_cdc.olist_oltp.orders:2": 4,
            "olist_cdc.olist_oltp.order_items:0": 5,
            "olist_cdc.olist_oltp.order_items:1": 5,
            "olist_cdc.olist_oltp.order_items:2": 6,
            "olist_cdc.olist_oltp.order_payments:0": 5,
            "olist_cdc.olist_oltp.order_payments:1": 4,
            "olist_cdc.olist_oltp.order_payments:2": 4,
            "olist_cdc.olist_oltp.order_reviews:0": 5,
            "olist_cdc.olist_oltp.order_reviews:1": 4,
            "olist_cdc.olist_oltp.order_reviews:2": 2,
            "olist_cdc.olist_oltp.products:0": 7,
            "olist_cdc.olist_oltp.sellers:0": 3,
            "olist_cdc.olist_oltp.product_category_translation:0": 4,
        }

        self.assertTrue(valid_serving_target_offsets(offsets))
        self.assertFalse(
            valid_serving_target_offsets({**offsets, "olist_cdc.unknown.extra:0": 1})
        )

    def test_additive_snapshot_transition_changes_only_affected_entity(self) -> None:
        previous = {
            "iceberg_snapshot_ids": {
                "customers": 101,
                "orders": 202,
                "order_items": 303,
                "order_payments": 404,
                "order_reviews": 505,
                "products": 606,
                "sellers": 707,
                "product_category_translation": 808,
            }
        }
        current = {
            "iceberg_snapshot_ids": {
                **previous["iceberg_snapshot_ids"],
                "customers": 909,
            }
        }

        self.assertTrue(valid_additive_snapshot_transition(previous, current))
        self.assertFalse(valid_additive_snapshot_transition(previous, previous))
        self.assertFalse(
            valid_additive_snapshot_transition(
                previous,
                {
                    "iceberg_snapshot_ids": {
                        **current["iceberg_snapshot_ids"],
                        "orders": 1001,
                    }
                },
            )
        )

    def test_canonical_manifest_sorting_and_hashing(self) -> None:
        rows = [
            {
                "customer_id": "cust_002",
                "customer_city": "rio",
                "price": decimal.Decimal("20.00"),
            },
            {
                "customer_id": "cust_001",
                "customer_city": "sao paulo",
                "price": decimal.Decimal("10.00"),
            },
        ]
        manifest1 = build_canonical_manifest("customers", rows, ["customer_id"])
        self.assertEqual(manifest1["row_count"], 2)
        self.assertEqual(manifest1["rows"][0]["customer_id"], "cust_001")
        self.assertEqual(manifest1["rows"][1]["customer_id"], "cust_002")

        # Reversed order input should yield identical manifest_sha256
        manifest2 = build_canonical_manifest(
            "customers", list(reversed(rows)), ["customer_id"]
        )
        self.assertEqual(manifest1["manifest_sha256"], manifest2["manifest_sha256"])

    def test_mysql_probe_fixture_allowlist(self) -> None:
        probe = MySQLProbe()
        connection = MagicMock()
        cursor = MagicMock()
        connection.cursor.return_value = cursor
        with patch.object(probe, "_connect", return_value=connection):
            result = probe.execute_fixture("insert.sql")
        self.assertEqual(result["status"], "EXECUTED")
        self.assertGreater(result["statements_count"], 0)
        connection.commit.assert_called_once()
        connection.close.assert_called_once()
        cursor.close.assert_called_once()

        with self.assertRaises(ValueError):
            probe.execute_fixture("unauthorized_drop_tables.sql")

    def test_mysql_probe_default_identity_matches_simulator_secret(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("scripts.simulation.database.connect") as connect,
        ):
            MySQLProbe()._connect()

        settings = connect.call_args.args[0]
        self.assertEqual(settings.user, "olist_simulator")
        self.assertEqual(settings.password_file.name, "mysql_simulator_password.txt")

    def test_mysql_probe_schema_fixture_uses_admin_secret(self) -> None:
        probe = MySQLProbe()
        connection = MagicMock()
        cursor = MagicMock()
        connection.cursor.return_value = cursor
        with patch.object(probe, "_connect_admin", return_value=connection) as admin:
            probe.execute_fixture("add_nullable_column.sql")

        admin.assert_called_once_with()
        connection.commit.assert_called_once()
        connection.close.assert_called_once()
        cursor.close.assert_called_once()

    def test_mysql_probe_fixture_connection_errors_are_not_suppressed(self) -> None:
        probe = MySQLProbe()
        with (
            patch.object(
                probe, "_connect", side_effect=ConnectionError("database unavailable")
            ),
            self.assertRaisesRegex(ConnectionError, "database unavailable"),
        ):
            probe.execute_fixture("insert.sql")

    def test_acceptance_summary_rejects_missing_or_failed_gate(self) -> None:
        summary = {
            "run_id": "test",
            "overall_status": "PASS",
            "mandatory_gates": list(MANDATORY_GATES),
            "missing_gates": [],
            "failed_or_skipped_gates": [],
            "gates": {
                gate: {
                    "status": "PASS",
                    "assertions": [{"name": "check", "status": "PASS"}],
                }
                for gate in MANDATORY_GATES[:-1]
            },
        }
        errors = validate_acceptance_summary(summary)
        self.assertTrue(any("10-final" in error for error in errors))

    def test_acceptance_summary_accepts_all_mandatory_pass_gates(self) -> None:
        summary = {
            "run_id": "test",
            "overall_status": "PASS",
            "mandatory_gates": list(MANDATORY_GATES),
            "missing_gates": [],
            "failed_or_skipped_gates": [],
            "gates": {
                gate: {
                    "gate": gate,
                    "status": "PASS",
                    "assertions": [
                        {"name": name, "status": "PASS"}
                        for name in REQUIRED_ASSERTIONS[gate]
                    ],
                }
                for gate in MANDATORY_GATES
            },
            "runtime_cleanup": {"status": "PASS"},
        }
        self.assertEqual(validate_acceptance_summary(summary), [])

    def test_acceptance_summary_rejects_generic_assertions(self) -> None:
        summary = {
            "run_id": "test",
            "overall_status": "PASS",
            "mandatory_gates": list(MANDATORY_GATES),
            "missing_gates": [],
            "failed_or_skipped_gates": [],
            "gates": {
                gate: {
                    "gate": gate,
                    "status": "PASS",
                    "assertions": [{"name": "check", "status": "PASS"}],
                }
                for gate in MANDATORY_GATES
            },
            "runtime_cleanup": {"status": "PASS"},
        }
        errors = validate_acceptance_summary(summary)
        self.assertTrue(any("unexpected assertions" in error for error in errors))

    @patch("scripts.serving.clickhouse.clickhouse_query")
    def test_clickhouse_nullable_probe_requires_full_path_evidence(
        self, mock_clickhouse_query: MagicMock
    ) -> None:
        writer_schema = {
            "type": "record",
            "name": "Value",
            "fields": [
                {"name": "customer_id", "type": "string"},
                {"name": "customer_unique_id", "type": "string"},
                {"name": "customer_zip_code_prefix", "type": "string"},
                {"name": "customer_city", "type": "string"},
                {"name": "customer_state", "type": "string"},
                {
                    "name": "stage_v_optional_note",
                    "type": ["null", "string"],
                    "default": None,
                },
            ],
        }
        mock_clickhouse_query.side_effect = [
            [
                {
                    "event_id": "event-001",
                    "customer_id": "wave2_customer_001",
                    "customer_city": "sao paulo stage v",
                    "optional_value": None,
                    "apply_status": "APPLIED",
                    "is_deleted": 0,
                    "kafka_topic": "olist_cdc.olist_oltp.customers",
                    "kafka_partition": 0,
                    "kafka_offset": 10,
                    "key_schema_id": 7,
                    "value_schema_id": 37,
                    "transaction_id": "tx-001",
                }
            ],
            [
                {
                    "event_id": "event-001",
                    "topic": "olist_cdc.olist_oltp.customers",
                    "partition": 0,
                    "offset": 10,
                    "is_tombstone": 0,
                    "key_schema_id": 7,
                    "value_schema_id": 37,
                    "key_framing_valid": 1,
                    "value_framing_valid": 1,
                }
            ],
            [
                {
                    "schema_id": 37,
                    "fingerprint_sha256": "a" * 64,
                    "subject": "olist_cdc.olist_oltp.customers-value",
                    "schema_json": "{}",
                    "spark_self_contained_schema_json": json.dumps(writer_schema),
                }
            ],
            [{"error_count": 0}],
            [{"error_count": 0}],
            [
                {
                    "customer_id": "wave2_customer_001",
                    "customer_city": "sao paulo stage v",
                    "optional_value": None,
                }
            ],
        ]

        result = ClickHouseProbe().inspect_nullable_event(
            "wave2_customer_001", "sao paulo stage v"
        )

        self.assertEqual(result["status"], "VERIFIED")
        self.assertEqual(result["event_id"], "event-001")
        self.assertEqual(mock_clickhouse_query.call_count, 6)

    @patch("scripts.serving.clickhouse.clickhouse_query")
    def test_entity_metrics_are_bounded_to_complete_transaction_prefix(
        self, mock_clickhouse_query: MagicMock
    ) -> None:
        from scripts.serving.clickhouse import ClickHouseServingMaterializer

        mock_clickhouse_query.return_value = []

        result = ClickHouseServingMaterializer.fetch_entity_metrics(42)

        self.assertEqual(result["customers"]["event_count"], 0)
        self.assertEqual(mock_clickhouse_query.call_count, 8)
        queries = [call.args[0] for call in mock_clickhouse_query.call_args_list]
        self.assertTrue(
            all(
                "transaction_id IS NULL" in query
                and "status = 'COMPLETE'" in query
                and "end_kafka_offset <= 42" in query
                for query in queries
            )
        )

    @patch("scripts.serving.clickhouse.clickhouse_query")
    def test_silver_progress_excludes_internal_transaction_row(
        self, mock_clickhouse_query: MagicMock
    ) -> None:
        from scripts.serving.clickhouse import ClickHouseServingMaterializer

        mock_clickhouse_query.return_value = [
            {
                "entity": "customers",
                "last_kafka_offset": 7,
                "changes_snapshot_id": 123,
                "status": "COMMITTED",
            },
            {
                "entity": "__transactions__",
                "last_kafka_offset": 19,
                "changes_snapshot_id": 456,
                "status": "COMMITTED",
            },
        ]

        result = ClickHouseServingMaterializer.fetch_silver_progress()

        self.assertEqual(set(result), {"customers"})
        query = mock_clickhouse_query.call_args.args[0]
        self.assertIn("WHERE entity IN", query)
        self.assertIn("argMax(changes_snapshot_id, recorded_at)", query)

    @patch("scripts.serving.clickhouse.clickhouse_query")
    def test_iceberg_snapshots_use_latest_progress_row(
        self, mock_clickhouse_query: MagicMock
    ) -> None:
        from scripts.serving.clickhouse import ClickHouseServingMaterializer

        mock_clickhouse_query.return_value = [
            {"entity": entity, "snapshot_id": index + 1}
            for index, entity in enumerate(
                (
                    "customers",
                    "orders",
                    "order_items",
                    "order_payments",
                    "order_reviews",
                    "products",
                    "sellers",
                    "product_category_translation",
                )
            )
        ]

        result = ClickHouseServingMaterializer.fetch_iceberg_snapshots()

        self.assertEqual(result["customers"], 1)
        query = mock_clickhouse_query.call_args.args[0]
        self.assertIn("argMax(changes_snapshot_id, recorded_at)", query)
        self.assertIn("WHERE entity IN", query)
        self.assertNotIn("max(changes_snapshot_id)", query)

    @patch("scripts.serving.clickhouse.clickhouse_execute")
    @patch("scripts.serving.clickhouse.clickhouse_query")
    def test_additive_columns_refresh_stable_current_view(
        self,
        mock_clickhouse_query: MagicMock,
        mock_clickhouse_execute: MagicMock,
    ) -> None:
        from scripts.serving.clickhouse import ClickHouseServingMaterializer
        from scripts.serving.entities import get_entity_spec

        mock_clickhouse_query.return_value = [
            {"name": "customer_id", "type": "String"},
            {"name": "stage_v_optional_note", "type": "Nullable(String)"},
        ]

        columns = ClickHouseServingMaterializer._serving_business_columns(
            get_entity_spec("customers")
        )

        self.assertIn("stage_v_optional_note", columns)
        statements = [call.args[0] for call in mock_clickhouse_execute.call_args_list]
        self.assertTrue(
            any(
                "ALTER TABLE serving_cdc.customers_current_versions" in statement
                for statement in statements
            )
        )
        self.assertTrue(
            any(
                "CREATE OR REPLACE VIEW serving_cdc.customers_current" in statement
                and "published_runs_current" in statement
                for statement in statements
            )
        )

    @patch("scripts.serving.clickhouse.clickhouse_query")
    def test_publish_marker_preserves_nested_json_escapes(
        self, mock_clickhouse_query: MagicMock
    ) -> None:
        from scripts.serving.clickhouse import ClickHouseServingMaterializer
        from scripts.serving.models import ServingSyncReport

        report = ServingSyncReport(
            sync_run_seq=7,
            sync_run_id="sync-00000000000000000007",
            operation_type="SYNC",
            status="SUCCEEDED",
            status_reason="NONE",
            is_noop=False,
            previous_transaction_id=None,
            target_transaction_id="tx-7",
            expected_event_count=1,
            materialized_event_count=1,
            entity_counts={"customers": 1},
            published_at="2026-08-03T00:00:00+00:00",
            dbt_result={
                "command": ["--vars", '{"sync_run_seq": 7, "sync_run_id": "x"}']
            },
        )

        ClickHouseServingMaterializer.publish_marker(report)

        insert_sql = mock_clickhouse_query.call_args.args[0]
        self.assertIn(r'{\\"sync_run_seq\\": 7', insert_sql)

    @patch.object(StageVOrchestrator, "run_cmd")
    def test_orchestrator_prepare_creates_evidence_dirs(
        self, mock_run_cmd: MagicMock
    ) -> None:
        mock_run_cmd.return_value = (0, "Mocked output", "")
        with tempfile.TemporaryDirectory() as tmp_dir:
            ev_dir = Path(tmp_dir) / "evidence"
            orchestrator = StageVOrchestrator("test_run_001", ev_dir)
            res = orchestrator.prepare()
            self.assertIn("status", res)
            self.assertTrue((ev_dir / "00-preflight" / "summary.json").exists())
            self.assertTrue((ev_dir / "01-harness-ready" / "summary.json").exists())

    def test_checksums_include_nested_gate_summaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            ev_dir = Path(tmp_dir) / "evidence"
            gate_summary = ev_dir / "00-preflight" / "summary.json"
            gate_summary.parent.mkdir(parents=True)
            gate_summary.write_text("{}", encoding="utf-8")
            (ev_dir / "summary.json").write_text("{}", encoding="utf-8")

            checksums = StageVOrchestrator("test_run_002", ev_dir).generate_checksums()

            self.assertIn("00-preflight/summary.json", checksums)
            self.assertNotIn("summary.json", checksums)
            self.assertTrue((ev_dir / "checksums.json").exists())

    def test_failed_run_preserves_runtime_for_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            ev_dir = Path(tmp_dir) / "evidence"
            orchestrator = StageVOrchestrator("failed_run", ev_dir)

            orchestrator.preserve_runtime_for_diagnostics(
                {"status": "FAIL", "gate": "03-initial-snapshot"}
            )

            cleanup = json.loads(
                (ev_dir / "runtime_cleanup.json").read_text(encoding="utf-8")
            )
            self.assertEqual(cleanup["status"], "SKIPPED")
            self.assertEqual(
                cleanup["reason"],
                "E2E_FAILED_RUNTIME_PRESERVED_FOR_DIAGNOSTICS",
            )
            self.assertEqual(cleanup["failed_gate"], "03-initial-snapshot")


if __name__ == "__main__":
    unittest.main()
