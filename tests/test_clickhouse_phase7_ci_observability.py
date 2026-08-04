from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class TargetObservabilityCiTests(unittest.TestCase):
    def test_clickhouse_and_probe_have_target_scrape_owners(self) -> None:
        compose = yaml.safe_load((ROOT / "compose.yaml").read_text(encoding="utf-8"))
        services = compose["services"]
        self.assertIn("clickhouse", services)
        self.assertIn("target-probe", services)
        self.assertIn("kafka-exporter", services)
        self.assertNotIn("postgres-exporter-oltp", services)

        prometheus = yaml.safe_load(
            (ROOT / "observability/prometheus/prometheus.yml").read_text(
                encoding="utf-8"
            )
        )
        scrape_jobs = {job["job_name"]: job for job in prometheus["scrape_configs"]}
        self.assertEqual(
            ["clickhouse:9363"],
            scrape_jobs["clickhouse"]["static_configs"][0]["targets"],
        )
        self.assertEqual(
            ["target-probe:9108"],
            scrape_jobs["control-postgres"]["static_configs"][0]["targets"],
        )

    def test_serving_alerts_and_dashboard_use_target_metrics(self) -> None:
        rules = yaml.safe_load(
            (
                ROOT / "observability/prometheus/rules/lakehouse-serving-alerts.yml"
            ).read_text(encoding="utf-8")
        )
        alerts = {
            rule["alert"]: rule for group in rules["groups"] for rule in group["rules"]
        }
        self.assertIn("LakehouseServingPublicationStalled", alerts)
        self.assertIn(
            "olist_serving_publication_age_seconds",
            alerts["LakehouseServingPublicationStalled"]["expr"],
        )

        dashboard = json.loads(
            (
                ROOT / "observability/grafana/dashboards/cdc-airflow-warehouse.json"
            ).read_text(encoding="utf-8")
        )
        payload = json.dumps(dashboard)
        self.assertIn("olist_serving_publication_age_seconds", payload)
        self.assertIn("olist_target_up", payload)
        self.assertNotIn("raw_freshness", payload)

    def test_ci_keeps_observability_validator_as_a_separate_check(self) -> None:
        ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("scripts/ci/validate_stage6_configuration.py", ci)
        self.assertNotIn("stage_v_candidate_e2e.py", ci)


if __name__ == "__main__":
    unittest.main()
