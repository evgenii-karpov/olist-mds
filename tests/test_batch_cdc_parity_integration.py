from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.cdc.realtime_transform import parity_status
from scripts.ci.check_batch_cdc_parity_integration import (
    CAPTURED_TABLES,
    Deadline,
    acceptance_failures,
    choose_asset_transform_run,
    connector_state_summary,
    kafka_nifi_drained,
    manifests_complete,
    redact_value,
    validate_same_archive_identity,
    wait_for_condition,
)


class BatchCdcParityIntegrationTests(unittest.TestCase):
    def test_defaults_use_bounded_fixture_runner_inputs(self) -> None:
        workflow = Path(".github/workflows/batch-cdc-parity.yml").read_text(
            encoding="utf-8"
        )
        runner = Path("scripts/ci/check_batch_cdc_parity_integration.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn("schedule:", workflow)
        self.assertNotIn("cron:", workflow)
        self.assertIn("--timeout-seconds 1200", workflow)
        self.assertIn("--poll-seconds 2", workflow)
        self.assertIn("DEFAULT_TIMEOUT_SECONDS = 1200", runner)
        self.assertIn("DEFAULT_POLL_SECONDS = 2", runner)

    def test_archive_identity_rejects_a_different_batch_or_cdc_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "batch.zip"
            second = Path(directory) / "cdc.zip"
            first.write_bytes(b"same fixture")
            second.write_bytes(b"same fixture")
            with self.assertRaisesRegex(ValueError, "paths differ"):
                validate_same_archive_identity(first, second)

    def test_manifest_and_queue_gates_require_all_tables_and_zero_lag(self) -> None:
        complete = {
            "normalized_tables": list(CAPTURED_TABLES),
            "coverage_tables": list(CAPTURED_TABLES),
        }
        self.assertTrue(manifests_complete(complete))
        incomplete = {**complete, "coverage_tables": list(CAPTURED_TABLES[:-1])}
        self.assertFalse(manifests_complete(incomplete))
        nifi = {"queued_count": 0, "processor_errors": [], "bulletins": []}
        self.assertTrue(kafka_nifi_drained({"total_lag": 0}, nifi))
        self.assertFalse(kafka_nifi_drained({"total_lag": 1}, nifi))

    def test_failed_asset_transform_is_not_treated_as_success(self) -> None:
        with self.assertRaisesRegex(AssertionError, "Asset-triggered transform failed"):
            choose_asset_transform_run(
                [{"run_id": "asset-run", "state": "failed"}], set()
            )

    def test_connector_failure_is_visible_in_status_summary(self) -> None:
        summary = connector_state_summary(
            {
                "connector": {"state": "FAILED"},
                "tasks": [{"state": "FAILED"}],
            }
        )
        self.assertFalse(summary["running"])
        self.assertTrue(summary["failed"])
        self.assertEqual(summary["task_states"], ["FAILED"])

    def test_polling_timeout_contains_last_observation(self) -> None:
        with (
            patch(
                "scripts.ci.check_batch_cdc_parity_integration.time.monotonic",
                return_value=10.0,
            ),
            self.assertRaisesRegex(TimeoutError, "last_observed=null"),
        ):
            wait_for_condition(
                "unit-test gate",
                lambda: (False, {"state": "starting"}),
                Deadline(timeout_seconds=0, started_at=10.0),
                poll_seconds=0,
            )

    def test_report_redacts_password_like_values(self) -> None:
        rendered = json.dumps(
            redact_value(
                {
                    "password": "secret-value",
                    "url": "postgres://user@warehouse/db?password=secret-value",
                }
            )
        )
        self.assertNotIn("secret-value", rendered)
        self.assertIn("[REDACTED]", rendered)

    def test_custom_and_dbt_utils_comparators_both_gate_parity(self) -> None:
        self.assertEqual(
            parity_status(
                custom_failed_metric_count=0,
                failed_dbt_utils_tests=[],
                dbt_exit_code=0,
            ),
            "PASS",
        )
        self.assertEqual(
            parity_status(
                custom_failed_metric_count=1,
                failed_dbt_utils_tests=[],
                dbt_exit_code=0,
            ),
            "FAIL",
        )
        self.assertEqual(
            parity_status(
                custom_failed_metric_count=0,
                failed_dbt_utils_tests=["dbt_utils_equality_daily_revenue"],
                dbt_exit_code=1,
            ),
            "FAIL",
        )

    def test_acceptance_report_fails_when_either_parity_path_fails(self) -> None:
        base = {
            "source_contract_valid": True,
            "archive_sha256": "abc",
            "batch_reconciliation": {"passed": True},
            "row_counts": {
                "expected": {"customers": 1},
                "batch": {"customers": 1},
                "realtime": {"customers": 1},
            },
            "audit": {
                "ingest": {"status": "SUCCEEDED"},
                "transform": {"status": "SUCCEEDED"},
                "reconciliation": {
                    "duplicate_rows": 0,
                    "rejected_rows": 0,
                    "gap_count": 0,
                    "failed_rows": 0,
                },
                "offset_gap_count": 0,
                "open_dlq_count": 0,
                "quarantine_object_count": 0,
            },
            "overall_parity_status": "FAIL",
            "parity": {
                "custom_failed_metric_count": 1,
                "failed_dbt_utils_tests": ["dbt_utils_equality_daily_revenue"],
                "command_exit_code": 1,
            },
        }
        failures = acceptance_failures(base)
        self.assertIn("custom parity reports contain failures", failures)
        self.assertIn("dbt-utils equality tests contain failures", failures)
        self.assertIn("record-parity returned a non-zero exit code", failures)


if __name__ == "__main__":
    unittest.main()
