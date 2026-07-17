from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class Stage6ContractTests(unittest.TestCase):
    def test_logs_profile_has_real_services(self) -> None:
        compose = yaml.safe_load((ROOT / "compose.yaml").read_text(encoding="utf-8"))
        for service in ("loki", "alloy"):
            self.assertIn(service, compose["services"])
            self.assertIn("logs", compose["services"][service]["profiles"])

    def test_dashboards_are_unique_and_query_data(self) -> None:
        dashboards = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in (ROOT / "observability/grafana/dashboards").glob("*.json")
        ]
        uids = [dashboard["uid"] for dashboard in dashboards]
        self.assertEqual(len(uids), len(set(uids)))
        for dashboard in dashboards:
            self.assertTrue(dashboard.get("title"))
            self.assertTrue(dashboard.get("panels"))
            self.assertTrue(
                any(panel.get("targets") for panel in dashboard["panels"]),
                dashboard["uid"],
            )

    def test_alerts_have_actionable_runbooks(self) -> None:
        rules = yaml.safe_load(
            (
                ROOT / "observability/prometheus/rules/cdc-component-alerts.yml"
            ).read_text(encoding="utf-8")
        )
        alerts = [
            rule
            for group in rules["groups"]
            for rule in group["rules"]
            if "alert" in rule
        ]
        self.assertGreaterEqual(len(alerts), 17)
        for alert in alerts:
            runbook = alert.get("annotations", {}).get("runbook", "")
            self.assertTrue(runbook.startswith("docs/runbooks/"), alert["alert"])
            self.assertTrue((ROOT / runbook).is_file(), alert["alert"])

    def test_loki_labels_are_low_cardinality(self) -> None:
        config = (ROOT / "observability/alloy/config.alloy").read_text(encoding="utf-8")
        for forbidden in ("simulation_run_id", "_event_id", "cdc_run_id"):
            self.assertNotIn(f'target_label = "{forbidden}"', config)


if __name__ == "__main__":
    unittest.main()
