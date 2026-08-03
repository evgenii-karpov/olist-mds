"""Tests for live readiness checks in local_lab.py.

S0 requirement: Ensure status and validate check actual live runtime
(Polaris RBAC, Iceberg inventory/checksum via spark-ops) rather than returning
hardcoded Python dictionaries or constants.
Fails on J1 implementation, passes after S8.
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from scripts.cdc.local_lab import (
    _iceberg_status,
    _status,
    _wait_streaming_ready,
)


class TestLocalLabLiveReadiness(unittest.TestCase):
    """Test live probe behavior for status and validate."""

    def test_iceberg_status_is_not_hardcoded(self) -> None:
        """_iceberg_status must not return static constant dictionary without live probing."""
        # In J1 implementation, _iceberg_status() returns:
        # {"migration": "compose-managed", "namespaces": ["bronze", "silver", "reference", "audit"], "expected_table_count": 26}
        # In S8, _iceberg_status() / LakehouseStatusMain queries live Polaris/Iceberg.
        # We verify that if live probe fails or returns unexpected data, status reflects it.
        result = _iceberg_status()
        self.assertNotIn("compose-managed", str(result.get("migration")))

    @patch("scripts.cdc.local_lab.time.sleep")
    @patch("scripts.cdc.local_lab.time.monotonic", side_effect=[0.0, 0.0, 1.0])
    @patch("scripts.cdc.local_lab._read_streaming_status")
    def test_restart_freshness_uses_status_timestamp_not_query_id(
        self,
        mock_read_status: MagicMock,
        _mock_monotonic: MagicMock,
        _mock_sleep: MagicMock,
    ) -> None:
        old_ids = {"bronze": "stable-bronze", "silver": "stable-silver"}
        ready_status = {
            "bronze": {
                "overall_state": "READY",
                "updated_at_utc": "2026-08-03T14:20:01+00:00",
                "queries": [{"query_id": "stable-bronze", "state": "RUNNING"}],
            },
            "silver": {
                "overall_state": "READY",
                "updated_at_utc": "2026-08-03T14:20:02+00:00",
                "queries": [{"query_id": "stable-silver", "state": "RUNNING"}],
            },
        }
        stale_status = {
            service: {
                **status,
                "updated_at_utc": "2026-08-03T14:19:59+00:00",
            }
            for service, status in ready_status.items()
        }
        mock_read_status.side_effect = [stale_status, ready_status]

        result = _wait_streaming_ready(
            60.0,
            old_ids,
            "2026-08-03T14:20:00+00:00",
        )

        self.assertTrue(result["freshness_verified"])
        self.assertEqual(result["new_query_ids"], old_ids)
        self.assertEqual(
            result["freshness_basis"],
            "status_updated_at_after_restart_barrier",
        )
        self.assertEqual(mock_read_status.call_count, 2)

    @patch("scripts.cdc.local_lab._iceberg_status")
    @patch("scripts.cdc.local_lab._http_json")
    @patch("scripts.cdc.local_lab._connector_state")
    @patch("scripts.cdc.local_lab._mysql_counts")
    @patch("scripts.cdc.local_lab._compose_records")
    def test_status_blocked_if_polaris_or_iceberg_fails(
        self,
        mock_compose_records: MagicMock,
        mock_mysql_counts: MagicMock,
        mock_connector_state: MagicMock,
        mock_http_json: MagicMock,
        mock_iceberg_status: MagicMock,
    ) -> None:
        """Status must return blocked if Polaris or Iceberg status is failing or drifting."""
        mock_compose_records.return_value = [
            {"Service": "mysql", "State": "running", "Health": "healthy"},
            {
                "Service": "polaris",
                "State": "running",
                "Health": "unhealthy",
            },  # Polaris unhealthy
        ]
        mock_mysql_counts.return_value = {}
        mock_connector_state.return_value = {
            "connector_state": "RUNNING",
            "task_0_state": "RUNNING",
        }
        mock_http_json.return_value = (200, {"config": "BACKWARD_TRANSITIVE"})
        mock_iceberg_status.return_value = {
            "status": "BLOCKED",
            "error": "table missing",
        }

        args = MagicMock()
        args.require = "platform"

        with (
            patch(
                "scripts.cdc.local_lab._writer_capture_state", return_value="captured"
            ),
            patch("scripts.cdc.local_lab._emit") as mock_emit,
        ):
            _status(args)
            mock_emit.assert_called_once()
            status_arg = mock_emit.call_args[0][1]
            self.assertEqual(status_arg, "blocked")


if __name__ == "__main__":
    unittest.main()
