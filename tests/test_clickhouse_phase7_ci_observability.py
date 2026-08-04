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

    def test_common_ci_uses_target_jobs_and_no_full_e2e(self) -> None:
        ci_path = ROOT / ".github/workflows/ci.yml"
        ci = ci_path.read_text(encoding="utf-8")
        workflow = yaml.safe_load(ci)
        self.assertEqual(
            {
                "docs-and-repository-contracts",
                "python-quality",
                "python-contract-tests",
                "scala-fast",
                "compose-contract",
                "airflow-dag-imports",
                "dbt-clickhouse-static",
                "ci-success",
            },
            set(workflow["jobs"]),
        )
        self.assertIn("scripts/ci/validate_stage6_configuration.py", ci)
        self.assertNotIn("stage_v_candidate_e2e.py", ci)
        self.assertNotIn("dbt/olist_analytics", ci)
        self.assertNotIn("realtime-core", ci)

    def test_bounded_workflow_has_observability_and_summary(self) -> None:
        path = ROOT / ".github/workflows/lakehouse-components.yml"
        workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertEqual(
            {
                "spark-image-contract",
                "cdc-component",
                "serving-component",
                "airflow-runtime",
                "observability-contract",
                "component-summary",
            },
            set(workflow["jobs"]),
        )
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("stage_v_candidate_e2e.py", text)
        self.assertIn("scripts/ci/validate_stage6_configuration.py", text)

    def test_manual_acceptance_is_dispatch_only(self) -> None:
        path = ROOT / ".github/workflows/lakehouse-acceptance.yml"
        workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
        triggers = workflow.get("on", workflow.get(True, {}))
        self.assertIn("workflow_dispatch", triggers)
        self.assertNotIn("pull_request", workflow)
        text = path.read_text(encoding="utf-8")
        self.assertIn("confirm_destructive", text)
        self.assertIn("stage_v_candidate_e2e.py", text)

    def test_legacy_ci_workflows_are_removed(self) -> None:
        for name in (
            "batch-cdc-parity.yml",
            "cdc-stage2-kafka-debezium.yml",
            "cdc-stage6-operations.yml",
        ):
            self.assertFalse((ROOT / ".github/workflows" / name).exists())


if __name__ == "__main__":
    unittest.main()
