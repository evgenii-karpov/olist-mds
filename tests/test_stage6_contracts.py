from __future__ import annotations

import json
import sys
import unittest
from importlib import import_module
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_contract = import_module("scripts.ci.validate_stage6_configuration")
FORBIDDEN_ACTIVE_TOKENS = _contract.FORBIDDEN_ACTIVE_TOKENS
REQUIRED_ALERTS = _contract.REQUIRED_ALERTS
REQUIRED_DASHBOARDS = _contract.REQUIRED_DASHBOARDS
REQUIRED_SCRAPE_JOBS = _contract.REQUIRED_SCRAPE_JOBS
KAFKA_EXPORTER_GROUP_FILTER = _contract.KAFKA_EXPORTER_GROUP_FILTER
KAFKA_EXPORTER_TOPIC_FILTER = _contract.KAFKA_EXPORTER_TOPIC_FILTER


class TargetObservabilityContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.compose = yaml.safe_load(
            (ROOT / "compose.yaml").read_text(encoding="utf-8")
        )
        self.prometheus = yaml.safe_load(
            (ROOT / "observability/prometheus/prometheus.yml").read_text(
                encoding="utf-8"
            )
        )

    def test_observability_and_logs_profiles_have_real_owners(self) -> None:
        services = self.compose["services"]
        for service in (
            "kafka-exporter",
            "target-probe",
            "prometheus",
            "alertmanager",
            "grafana",
        ):
            self.assertIn("observability", services[service]["profiles"])
        for service in ("loki", "alloy"):
            self.assertIn("logs", services[service]["profiles"])

    def test_every_scrape_job_targets_a_compose_service(self) -> None:
        services = set(self.compose["services"])
        jobs = {job["job_name"]: job for job in self.prometheus["scrape_configs"]}
        self.assertEqual(REQUIRED_SCRAPE_JOBS, set(jobs))
        for job in jobs.values():
            for block in job["static_configs"]:
                for target in block["targets"]:
                    self.assertIn(target.rsplit(":", 1)[0], services)

    def test_target_probe_jobs_use_bounded_target_parameters(self) -> None:
        jobs = {job["job_name"]: job for job in self.prometheus["scrape_configs"]}
        for name in (
            "mysql",
            "kafka",
            "kafka-connect",
            "apicurio",
            "spark",
            "spark-streaming",
            "polaris",
            "airflow",
            "control-postgres",
        ):
            self.assertEqual("/probe", jobs[name]["metrics_path"])
            self.assertEqual([name], jobs[name]["params"]["target"])

    def test_kafka_lag_uses_explicit_target_group_and_topic_allowlists(self) -> None:
        command = self.compose["services"]["kafka-exporter"]["command"]
        self.assertIn(f"--group.filter={KAFKA_EXPORTER_GROUP_FILTER}", command)
        self.assertIn(f"--topic.filter={KAFKA_EXPORTER_TOPIC_FILTER}", command)
        for path in (
            ROOT / "observability/prometheus/rules/cdc-component-alerts.yml",
            ROOT / "observability/prometheus/rules/cdc-slo-recording.yml",
        ):
            payload = path.read_text(encoding="utf-8")
            self.assertIn("olist-spark-bronze(-.*)?", payload)
            self.assertIn("product_category_translation", payload)
            self.assertIn("olist_kafka_consumer_lag", payload)
            self.assertNotIn("kafka_consumergroup_lag", payload)
        recording_payload = (
            ROOT / "observability/prometheus/rules/cdc-slo-recording.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("olist_lakehouse:kafka_business_consumer_lag", recording_payload)

    def test_dashboards_are_unique_target_views(self) -> None:
        dashboards = []
        for path in (ROOT / "observability/grafana/dashboards").glob("*.json"):
            value = json.loads(path.read_text(encoding="utf-8"))
            dashboards.append(value)
            self.assertGreaterEqual(len(value.get("panels", [])), 6, path.name)
            self.assertTrue(
                all(
                    target.get("expr")
                    for panel in value["panels"]
                    for target in panel["targets"]
                ),
                path.name,
            )
        uids = {dashboard["uid"] for dashboard in dashboards}
        self.assertEqual(len(uids), len(dashboards))
        self.assertTrue(uids >= REQUIRED_DASHBOARDS)

    def test_alerts_have_target_runbooks(self) -> None:
        rules = yaml.safe_load(
            (
                ROOT / "observability/prometheus/rules/cdc-component-alerts.yml"
            ).read_text(encoding="utf-8")
        )
        rules["groups"].extend(
            yaml.safe_load(
                (
                    ROOT / "observability/prometheus/rules/lakehouse-serving-alerts.yml"
                ).read_text(encoding="utf-8")
            )["groups"]
        )
        alerts = {
            rule["alert"]
            for group in rules["groups"]
            for rule in group["rules"]
            if "alert" in rule
        }
        self.assertTrue(alerts >= REQUIRED_ALERTS)
        for group in rules["groups"]:
            for rule in group["rules"]:
                if "alert" not in rule:
                    continue
                runbook = rule["annotations"]["runbook"]
                self.assertTrue(runbook.startswith("docs/runbooks/"))
                self.assertTrue((ROOT / runbook).is_file(), rule["alert"])

    def test_active_observability_assets_have_no_legacy_tokens(self) -> None:
        paths = [
            ROOT / "observability/prometheus/prometheus.yml",
            *(ROOT / "observability/prometheus/rules").glob("*.yml"),
            *(ROOT / "observability/grafana/dashboards").glob("*.json"),
        ]
        payload = "\n".join(path.read_text(encoding="utf-8") for path in paths)
        lowered = payload.lower()
        for token in FORBIDDEN_ACTIVE_TOKENS:
            self.assertNotIn(token.lower(), lowered)

    def test_loki_and_alloy_keep_bounded_log_contract(self) -> None:
        alloy = (ROOT / "observability/alloy/config.alloy").read_text(encoding="utf-8")
        for forbidden in ("simulation_run_id", "_event_id", "cdc_run_id"):
            self.assertNotIn(f'target_label = "{forbidden}"', alloy)
        self.assertIn("http://loki:3100/loki/api/v1/push", alloy)
        loki = yaml.safe_load(
            (ROOT / "observability/loki/loki.yml").read_text(encoding="utf-8")
        )
        self.assertEqual("168h", loki["limits_config"]["retention_period"])


if __name__ == "__main__":
    unittest.main()
