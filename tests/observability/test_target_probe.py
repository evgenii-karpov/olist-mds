from __future__ import annotations

import json
import sys
import tempfile
import unittest
from importlib import import_module
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

target_probe = import_module("scripts.observability.target_probe")


class TargetProbeTests(unittest.TestCase):
    def test_mysql_probe_uses_mysql_84_binary_log_statement(self) -> None:
        source = (ROOT / "scripts/observability/target_probe.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('cursor.execute("SHOW BINARY LOG STATUS")', source)
        self.assertNotIn('cursor.execute("SHOW MASTER STATUS")', source)

    def test_render_escapes_labels_and_declares_metric_types(self) -> None:
        output = target_probe._render(
            [
                target_probe.Sample(
                    "olist_target_up", 1, (("target", 'mysql"primary'),)
                ),
                target_probe.Sample("olist_target_probe_requests_total", 2),
            ]
        )

        self.assertIn("# TYPE olist_target_up gauge", output)
        self.assertIn("# TYPE olist_target_probe_requests_total counter", output)
        self.assertIn('target="mysql\\"primary"', output)

    def test_probe_failure_fails_closed_without_error_labels(self) -> None:
        with patch.object(
            target_probe,
            "probe_target",
            side_effect=RuntimeError("password must not be exported"),
        ):
            output = target_probe.collect_metrics("mysql")

        self.assertIn('olist_target_up{target="mysql"} 0', output)
        self.assertNotIn("password must not be exported", output)

    def test_spark_status_requires_fresh_ready_queries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            status_root = Path(temp_dir)
            payload = {
                "overall_state": "READY",
                "updated_at_utc": "2099-01-01T00:00:00Z",
                "queries": [{"state": "RUNNING"}],
            }
            for component in ("bronze", "silver"):
                directory = status_root / component
                directory.mkdir()
                (directory / "status.json").write_text(
                    json.dumps(payload), encoding="utf-8"
                )
            with patch.object(target_probe, "SPARK_STATUS_DIR", status_root):
                result = target_probe.probe_target("spark-streaming")

        self.assertTrue(result.up)
        self.assertEqual(
            2,
            sum(
                1
                for sample in result.samples
                if sample.name == "olist_spark_streaming_state" and sample.value == 1
            ),
        )
        self.assertEqual(
            2,
            sum(
                1
                for sample in result.samples
                if sample.name == "olist_spark_streaming_status_stale"
                and sample.value == 0
            ),
        )

    def test_spark_status_exposes_scoped_checkpoint_lag(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            status_root = Path(temp_dir)
            payload = {
                "overall_state": "READY",
                "updated_at_utc": "2099-01-01T00:00:00Z",
                "queries": [
                    {
                        "name": "kafka_to_bronze",
                        "state": "RUNNING",
                        "partition_offsets": {
                            "olist_cdc.transaction:0": 4,
                            "olist_cdc.heartbeat:0": 2,
                        },
                    }
                ],
            }
            directory = status_root / "bronze"
            directory.mkdir()
            (directory / "status.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )
            silver_directory = status_root / "silver"
            silver_directory.mkdir()
            (silver_directory / "status.json").write_text(
                json.dumps(
                    {
                        "overall_state": "READY",
                        "updated_at_utc": "2099-01-01T00:00:00Z",
                        "queries": [{"state": "RUNNING"}],
                    }
                ),
                encoding="utf-8",
            )
            with (
                patch.object(target_probe, "SPARK_STATUS_DIR", status_root),
                patch.object(
                    target_probe,
                    "_kafka_partition_end_offsets",
                    return_value=(
                        200,
                        {
                            "olist_cdc.transaction:0": 9,
                            "olist_cdc.heartbeat:0": 2,
                        },
                    ),
                ),
            ):
                result = target_probe.probe_target("spark-streaming")

        self.assertTrue(result.up)
        lag_samples = {
            tuple(sample.labels): sample.value
            for sample in result.samples
            if sample.name == "olist_kafka_consumer_lag"
        }
        self.assertEqual(
            5,
            lag_samples[
                (
                    ("consumer_group", "olist-spark-bronze"),
                    ("topic", "olist_cdc.transaction"),
                    ("partition", "0"),
                )
            ],
        )


if __name__ == "__main__":
    unittest.main()
