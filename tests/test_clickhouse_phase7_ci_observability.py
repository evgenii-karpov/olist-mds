from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class ClickHousePhase7CiObservabilityTests(unittest.TestCase):
    def test_observability_uses_clickhouse_not_warehouse_postgres_exporter(
        self,
    ) -> None:
        compose = yaml.safe_load((ROOT / "compose.yaml").read_text(encoding="utf-8"))
        services = compose["services"]
        self.assertNotIn("postgres", services)
        self.assertIn("postgres-exporter-oltp", services)
        removed_exporter = "postgres-exporter-" + "warehouse"
        self.assertNotIn(removed_exporter, services)

        prometheus = yaml.safe_load(
            (ROOT / "observability/prometheus/prometheus.yml").read_text(
                encoding="utf-8"
            )
        )
        scrape_jobs = {job["job_name"]: job for job in prometheus["scrape_configs"]}
        self.assertIn("clickhouse", scrape_jobs)
        self.assertNotIn("warehouse-postgres", scrape_jobs)
        self.assertIn(
            "clickhouse:9363",
            scrape_jobs["clickhouse"]["static_configs"][0]["targets"],
        )

    def test_pipeline_exporter_is_split_between_clickhouse_and_control_postgres(
        self,
    ) -> None:
        compose = yaml.safe_load((ROOT / "compose.yaml").read_text(encoding="utf-8"))
        service = compose["services"]["cdc-pipeline-exporter"]
        self.assertIn("clickhouse-init", service["depends_on"])
        self.assertIn("clickhouse_password", service["secrets"])
        self.assertIn("control_postgres_password", service["secrets"])
        self.assertEqual(["--listen-port", "9107"], service["command"])

        exporter = (ROOT / "scripts/cdc/pipeline_metrics.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("clickhouse_connect.get_client", exporter)
        self.assertIn("CONTROL_POSTGRES_HOST", exporter)
        self.assertIn("FROM raw_cdc.`{table}` FINAL", exporter)
        self.assertIn("cdc_audit.cdc_files", exporter)

    def test_alerts_and_dashboard_track_clickhouse_health(self) -> None:
        rules = yaml.safe_load(
            (
                ROOT / "observability/prometheus/rules/cdc-component-alerts.yml"
            ).read_text(encoding="utf-8")
        )
        alerts = {
            rule["alert"]: rule
            for group in rules["groups"]
            for rule in group["rules"]
            if "alert" in rule
        }
        self.assertIn("CdcClickHouseUnavailable", alerts)
        self.assertIn(
            'up{job="clickhouse"}', alerts["CdcClickHouseUnavailable"]["expr"]
        )

        dashboard = json.loads(
            (
                ROOT / "observability/grafana/dashboards/cdc-airflow-warehouse.json"
            ).read_text(encoding="utf-8")
        )
        payload = json.dumps(dashboard)
        self.assertIn("ClickHouse scrape", payload)
        self.assertIn("ClickHouseProfileEvents_FailedQuery", payload)
        self.assertIn("olist_cdc_raw_freshness_seconds", payload)

    def test_workflows_have_clickhouse_runtime_and_comparator_jobs(self) -> None:
        ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        parity = (ROOT / ".github/workflows/batch-cdc-parity.yml").read_text(
            encoding="utf-8"
        )
        parity_runner = (
            ROOT / "scripts/ci/check_batch_cdc_parity_integration.py"
        ).read_text(encoding="utf-8")
        stage6 = (ROOT / ".github/workflows/cdc-stage6-operations.yml").read_text(
            encoding="utf-8"
        )
        sqlfluff = (ROOT / ".sqlfluff").read_text(encoding="utf-8")
        removed_exporter = "postgres-exporter-" + "warehouse"

        self.assertIn("local_clickhouse", ci)
        self.assertIn("docker compose up -d --wait clickhouse", ci)
        self.assertIn("docker compose run --rm clickhouse-init", ci)
        self.assertIn("uv run dbt parse --no-partial-parse", ci)
        self.assertIn("uv run dbt compile --no-partial-parse", ci)
        self.assertIn("dialect = clickhouse", sqlfluff)
        self.assertIn("target = local_clickhouse", sqlfluff)
        self.assertNotIn("target = local_pg", sqlfluff)
        self.assertIn("clickhouse-runtime-contract", ci)
        self.assertIn("cdc-clickhouse-ingest-resilience", ci)
        self.assertIn("check_clickhouse_cdc_ingest_resilience.py", ci)
        self.assertIn("scripts/parity/compare_manifests.py", ci)
        self.assertIn("scripts/parity/export_clickhouse_candidate.py", parity)
        self.assertIn("scripts/parity/compare_manifests.py", parity)
        self.assertIn("DBT_TARGET: local_clickhouse", parity)
        self.assertIn("CDC_WAREHOUSE_TYPE: clickhouse", parity)
        self.assertIn(
            '"warehouse_target": "clickhouse"',
            parity_runner,
        )
        self.assertIn("data/reports/clickhouse-candidate-manifest.json", parity)
        self.assertIn(
            "--candidate data/reports/clickhouse-candidate-manifest.json",
            parity,
        )
        self.assertNotIn(
            "--candidate data/reports/" + "postgres-" + "oracle-manifest.json",
            parity,
        )
        self.assertNotIn("candidate-run", parity)
        self.assertNotIn("run_clickhouse_candidate", parity)
        self.assertIn("clickhouse-init", stage6)
        self.assertNotIn(removed_exporter, stage6)


if __name__ == "__main__":
    unittest.main()
