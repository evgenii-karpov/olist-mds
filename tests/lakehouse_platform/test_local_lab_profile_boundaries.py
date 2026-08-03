"""Tests enforcing profile boundaries for local_lab CLI commands.

S0 requirement: Verify that platform commands (bootstrap, up, status, validate)
use only the platform profile and do not depend on serving (ClickHouse/Airflow).
These tests fail on J1 implementation (which uses SERVING_PROFILES) and pass after S8.
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from scripts.cdc.local_lab import (
    PLATFORM_PROFILES,
    SERVING_PROFILES,
    _bootstrap,
    _start_serving,
    _status,
    _up,
    compose_command,
)


class TestLocalLabProfileBoundaries(unittest.TestCase):
    """Test that bootstrap and up use ONLY the platform profile."""

    def test_up_uses_platform_profile_only(self) -> None:
        """up must build compose commands with profile platform only."""
        cmd = compose_command("up", "-d", profiles=PLATFORM_PROFILES)
        self.assertIn("--profile", cmd)
        self.assertIn("platform", cmd)
        self.assertNotIn("serving", cmd)

    @patch("scripts.cdc.local_lab._compose_up")
    def test_up_func_invokes_platform_profile(self, mock_compose_up: MagicMock) -> None:
        """_up function must pass PLATFORM_PROFILES to _compose_up."""
        args = MagicMock()
        args.build = False
        args.timeout = 100.0
        _up(args)
        mock_compose_up.assert_called_once()
        _, kwargs = mock_compose_up.call_args
        self.assertEqual(kwargs.get("profiles"), PLATFORM_PROFILES)

    @patch("scripts.cdc.local_lab._compose_up")
    def test_start_serving_requires_serving_services(
        self, mock_compose_up: MagicMock
    ) -> None:
        """Serving startup must use both profiles and wait for Airflow/ClickHouse."""
        args = MagicMock()
        args.build = True
        args.timeout = 100.0
        _start_serving(args)
        mock_compose_up.assert_called_once()
        _, kwargs = mock_compose_up.call_args
        self.assertEqual(kwargs.get("profiles"), SERVING_PROFILES)
        self.assertEqual(kwargs.get("required_services"), ("clickhouse", "airflow"))

    @patch("scripts.cdc.local_lab._validate_runtime")
    @patch("scripts.cdc.local_lab._capture_and_contracts")
    @patch("scripts.cdc.local_lab._connector_bootstrap")
    @patch("scripts.cdc.local_lab._run_seed")
    @patch("scripts.cdc.local_lab._compose_up")
    @patch("scripts.cdc.local_lab._archive_or_fail")
    def test_bootstrap_uses_platform_profile_only(
        self,
        mock_archive: MagicMock,
        mock_compose_up: MagicMock,
        mock_seed: MagicMock,
        mock_conn: MagicMock,
        mock_cap: MagicMock,
        mock_val: MagicMock,
    ) -> None:
        """_bootstrap must invoke _compose_up with platform profile only and never SERVING_PROFILES."""
        args = MagicMock()
        args.archive = "dummy.zip"
        args.timeout = 100.0
        mock_val.return_value = {"status": "ready"}
        _bootstrap(args)

        # In J1, _compose_up was called twice: first with PLATFORM_PROFILES, then with SERVING_PROFILES.
        # In S8, _compose_up must be called ONLY with PLATFORM_PROFILES.
        for call_item in mock_compose_up.call_args_list:
            _, kwargs = call_item
            self.assertEqual(kwargs.get("profiles"), PLATFORM_PROFILES)

    @patch("scripts.cdc.local_lab._http_json")
    @patch("scripts.cdc.local_lab._connector_state")
    @patch("scripts.cdc.local_lab._mysql_counts")
    @patch("scripts.cdc.local_lab._compose_records")
    def test_serving_failure_does_not_block_platform_status(
        self,
        mock_compose_records: MagicMock,
        mock_mysql_counts: MagicMock,
        mock_connector_state: MagicMock,
        mock_http_json: MagicMock,
    ) -> None:
        """Status --require platform should be ready even if ClickHouse (serving) is unavailable."""
        mock_compose_records.return_value = [
            {"Service": "mysql", "State": "running", "Health": "healthy"},
            {"Service": "polaris", "State": "running", "Health": "healthy"},
        ]
        mock_mysql_counts.return_value = {}
        mock_connector_state.return_value = {
            "connector_state": "RUNNING",
            "task_0_state": "RUNNING",
        }
        # First call is for registry compatibility, second for ClickHouse
        mock_http_json.side_effect = [
            (200, {"config": "BACKWARD_TRANSITIVE"}),  # Apicurio
            (0, None),  # ClickHouse down
        ]
        args = MagicMock()
        args.require = "platform"

        # Must pass with exit code 0 (ready) for platform scope despite ClickHouse 0
        with (
            patch(
                "scripts.cdc.local_lab._writer_capture_state", return_value="captured"
            ),
            patch("scripts.cdc.local_lab._emit") as mock_emit,
        ):
            _status(args)
            mock_emit.assert_called_once()
            status_arg = mock_emit.call_args[0][1]
            self.assertEqual(status_arg, "ready")


if __name__ == "__main__":
    unittest.main()
