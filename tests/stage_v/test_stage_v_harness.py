from __future__ import annotations

import decimal
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.validation.stage_v_candidate_e2e import StageVOrchestrator
from scripts.validation.stage_v_probes import (
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
        result = probe.execute_fixture("insert.sql")
        self.assertEqual(result["status"], "EXECUTED")

        with self.assertRaises(ValueError):
            probe.execute_fixture("unauthorized_drop_tables.sql")

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


if __name__ == "__main__":
    unittest.main()
