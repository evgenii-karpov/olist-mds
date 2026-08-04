#!/usr/bin/env python3
"""Validate the target observability configuration and ownership contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_SERVICES = {
    "platform-postgres",
    "mysql",
    "kafka",
    "kafka-exporter",
    "apicurio-registry",
    "kafka-connect",
    "minio",
    "polaris",
    "spark-master",
    "spark-worker",
    "spark-bronze",
    "spark-silver",
    "clickhouse",
    "airflow",
    "target-probe",
    "prometheus",
    "alertmanager",
    "grafana",
    "loki",
    "alloy",
}
OBSERVABILITY_SERVICES = {
    "kafka-exporter",
    "target-probe",
    "prometheus",
    "alertmanager",
    "grafana",
}
LOG_SERVICES = {"loki", "alloy"}
KAFKA_EXPORTER_GROUP_FILTER = r"^olist-spark-bronze(-.*)?$"
KAFKA_EXPORTER_TOPIC_FILTER = (
    r"^olist_cdc\.(olist_oltp\.(customers|orders|order_items|order_payments|"
    r"order_reviews|products|sellers|product_category_translation)|transaction|heartbeat)$"
)
REQUIRED_SCRAPE_JOBS = {
    "prometheus",
    "alertmanager",
    "grafana",
    "loki",
    "alloy",
    "target-probe",
    "mysql",
    "kafka",
    "kafka-lag",
    "kafka-connect",
    "apicurio",
    "spark",
    "spark-streaming",
    "minio",
    "polaris",
    "clickhouse",
    "airflow",
    "control-postgres",
}
REQUIRED_ALERTS = {
    "LakehouseMySQLUnavailable",
    "LakehouseKafkaUnavailable",
    "LakehouseKafkaLagHigh",
    "LakehouseKafkaConnectUnavailable",
    "LakehouseKafkaConnectTaskNotRunning",
    "LakehouseApicurioUnavailable",
    "LakehouseApicurioCompatibilityUnavailable",
    "LakehouseSparkUnavailable",
    "LakehouseSparkStreamingDegraded",
    "LakehouseMinioUnavailable",
    "LakehousePolarisUnavailable",
    "LakehouseClickHouseUnavailable",
    "LakehouseAirflowUnavailable",
    "LakehouseControlPostgresUnavailable",
    "LakehouseServingPublicationStalled",
    "LakehouseServingRejectedBoundary",
    "LakehouseServingLeaseStalled",
    "ObservabilityTargetProbeUnavailable",
    "ObservabilityPrometheusUnavailable",
    "ObservabilityAlertmanagerUnavailable",
    "ObservabilityGrafanaUnavailable",
    "ObservabilityLokiUnavailable",
    "ObservabilityAlloyUnavailable",
}
REQUIRED_DASHBOARDS = {
    "olist-lakehouse-source",
    "olist-lakehouse-kafka",
    "olist-lakehouse-slo",
    "olist-lakehouse-airflow",
    "olist-lakehouse-capacity",
    "lakehouse-serving",
}
REQUIRED_RUNBOOKS = {
    "cdc-alert-testing.md",
    "cdc-connector-resnapshot.md",
    "cdc-kafka-replay.md",
    "cdc-schema-migration.md",
    "cdc-service-restart.md",
    "lakehouse-serving-rejected-boundary.md",
    "lakehouse-serving-sync.md",
}
FORBIDDEN_ACTIVE_TOKENS = (
    "olist-postgres-cdc",
    "olist-nifi-cdc-v1",
    "postgres-exporter",
    "statsd-exporter",
    "node-exporter",
    "cadvisor",
    "cdc-pipeline-exporter",
    "nifi-metrics-proxy",
    "replication_slot",
    "retained_wal",
    "raw_freshness",
    "warehouse-postgres",
)
RUNTIME_IMAGE_CONTRACT = {
    "prometheus": "prom/prometheus:v3.5.0",
    "alertmanager": "prom/alertmanager:v0.30.0",
    "grafana": "grafana/grafana:12.1.1",
    "alloy": "grafana/alloy:v1.16.1",
    "loki": "grafana/loki:3.6.5",
    "kafka_exporter": "danielqsj/kafka-exporter:v1.9.0",
    "observability_probe": "olist-observability-probe:1.0.0",
}


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def _service_names(compose: dict[str, Any]) -> set[str]:
    services = compose.get("services", {})
    return set(services) if isinstance(services, dict) else set()


def _compose_file_references(compose: dict[str, Any]) -> str:
    services = compose.get("services", {})
    return json.dumps(services, sort_keys=True)


def _scrape_targets(job: dict[str, Any]) -> list[str]:
    targets: list[str] = []
    for block in job.get("static_configs", []):
        if isinstance(block, dict):
            values = block.get("targets", [])
            if isinstance(values, list):
                targets.extend(str(value) for value in values)
    return targets


def _target_host(value: str) -> str:
    return value.rsplit(":", 1)[0].strip("[]")


def _observability_files() -> list[Path]:
    paths = [
        ROOT / "observability/README.md",
        ROOT / "observability/alertmanager/alertmanager.yml",
        ROOT / "observability/alloy/config.alloy",
        ROOT / "observability/loki/loki.yml",
        ROOT / "observability/prometheus/prometheus.yml",
        ROOT / "observability/prometheus/rules/cdc-component-alerts.yml",
        ROOT / "observability/prometheus/rules/cdc-slo-recording.yml",
        ROOT / "observability/prometheus/rules/lakehouse-serving-alerts.yml",
    ]
    paths.extend((ROOT / "observability/grafana/dashboards").glob("*.json"))
    return paths


def _validate_runtime_images(errors: list[str]) -> None:
    manifest = load_yaml(ROOT / "streaming/runtime-versions.json")
    components = manifest.get("components", {})
    for component, expected in RUNTIME_IMAGE_CONTRACT.items():
        actual = components.get(component, {}).get("image")
        if actual != expected:
            errors.append(
                f"runtime image drift for {component}: expected {expected!r}, got {actual!r}"
            )


def main() -> int:
    errors: list[str] = []
    compose = load_yaml(ROOT / "compose.yaml")
    services = compose.get("services", {})
    service_names = _service_names(compose)
    missing_services = REQUIRED_SERVICES - service_names
    if missing_services:
        errors.append(f"missing target Compose services: {sorted(missing_services)}")

    for service in OBSERVABILITY_SERVICES:
        profiles = set(services.get(service, {}).get("profiles", []))
        if "observability" not in profiles:
            errors.append(f"{service} is not attached to the observability profile")
    for service in LOG_SERVICES:
        profiles = set(services.get(service, {}).get("profiles", []))
        if "logs" not in profiles:
            errors.append(f"{service} is not attached to the logs profile")

    exporter_command = [
        str(value) for value in services.get("kafka-exporter", {}).get("command", [])
    ]
    if f"--group.filter={KAFKA_EXPORTER_GROUP_FILTER}" not in exporter_command:
        errors.append(
            "Kafka exporter group filter is not the bounded Spark Bronze prefix"
        )
    if f"--topic.filter={KAFKA_EXPORTER_TOPIC_FILTER}" not in exporter_command:
        errors.append("Kafka exporter topic filter is not the target topic allowlist")

    compose_text = _compose_file_references(compose)
    for required_mount in (
        "observability/prometheus/rules",
        "observability/grafana/provisioning",
        "observability/grafana/dashboards",
        "observability/alertmanager/alertmanager.yml",
        "observability/alloy/config.alloy",
    ):
        if required_mount not in compose_text:
            errors.append(f"Compose does not mount {required_mount}")

    prometheus = load_yaml(ROOT / "observability/prometheus/prometheus.yml")
    jobs = {
        str(job.get("job_name")): job
        for job in prometheus.get("scrape_configs", [])
        if isinstance(job, dict) and job.get("job_name")
    }
    missing_jobs = REQUIRED_SCRAPE_JOBS - set(jobs)
    if missing_jobs:
        errors.append(f"missing Prometheus scrape jobs: {sorted(missing_jobs)}")
    duplicate_jobs = len(jobs) != len(prometheus.get("scrape_configs", []))
    if duplicate_jobs:
        errors.append("Prometheus scrape job names must be unique")
    for job_name, job in jobs.items():
        targets = _scrape_targets(job)
        if not targets:
            errors.append(f"Prometheus job {job_name} has no static target")
        for target in targets:
            host = _target_host(target)
            if host not in service_names:
                errors.append(
                    f"Prometheus job {job_name} references unknown target service {host!r}"
                )
    for job_name in (
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
        job = jobs.get(job_name, {})
        if job.get("metrics_path") != "/probe":
            errors.append(f"Prometheus job {job_name} must use target-probe /probe")
        if job.get("params", {}).get("target") != [job_name]:
            errors.append(f"Prometheus job {job_name} has an invalid target parameter")

    for path in _observability_files():
        if not path.is_file():
            errors.append(f"missing observability asset: {path.relative_to(ROOT)}")
            continue
        payload = path.read_text(encoding="utf-8").lower()
        for token in FORBIDDEN_ACTIVE_TOKENS:
            if token.lower() in payload:
                errors.append(f"legacy observability token {token!r} in {path.name}")

    rule_files = sorted((ROOT / "observability/prometheus/rules").glob("*.yml"))
    alerts: set[str] = set()
    for path in rule_files:
        rules = load_yaml(path)
        for group in rules.get("groups", []):
            for rule in group.get("rules", []):
                if not isinstance(rule, dict):
                    continue
                alert = rule.get("alert")
                if not alert:
                    continue
                alerts.add(str(alert))
                runbook = rule.get("annotations", {}).get("runbook", "")
                if not str(runbook).startswith("docs/runbooks/"):
                    errors.append(f"alert {alert} has no target runbook")
                elif not (ROOT / str(runbook)).is_file():
                    errors.append(f"alert {alert} references missing runbook {runbook}")
    missing_alerts = REQUIRED_ALERTS - alerts
    if missing_alerts:
        errors.append(f"missing target alerts: {sorted(missing_alerts)}")

    dashboard_dir = ROOT / "observability/grafana/dashboards"
    dashboards: dict[str, dict[str, Any]] = {}
    for path in sorted(dashboard_dir.glob("*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid dashboard JSON {path.name}: {exc}")
            continue
        uid = value.get("uid")
        if uid:
            if str(uid) in dashboards:
                errors.append(f"duplicate dashboard uid {uid}")
            dashboards[str(uid)] = value
        panels = value.get("panels", [])
        if not isinstance(panels, list) or len(panels) < 6:
            errors.append(f"dashboard {path.name} must contain at least six panels")
        for panel in panels if isinstance(panels, list) else []:
            for target in panel.get("targets", []) if isinstance(panel, dict) else []:
                if not isinstance(target, dict) or not target.get("expr"):
                    errors.append(f"dashboard {path.name} contains an empty query")
    missing_dashboards = REQUIRED_DASHBOARDS - set(dashboards)
    if missing_dashboards:
        errors.append(f"missing target dashboards: {sorted(missing_dashboards)}")

    alertmanager = load_yaml(ROOT / "observability/alertmanager/alertmanager.yml")
    receivers = alertmanager.get("receivers", [])
    webhook_urls = [
        config.get("url")
        for receiver in receivers
        for config in receiver.get("webhook_configs", [])
        if isinstance(config, dict)
    ]
    if "http://target-probe:9108/alertmanager/webhook" not in webhook_urls:
        errors.append("Alertmanager does not route to the target-probe webhook")

    alloy = (ROOT / "observability/alloy/config.alloy").read_text(encoding="utf-8")
    for forbidden in ("simulation_run_id", "_event_id", "cdc_run_id"):
        if f'target_label = "{forbidden}"' in alloy:
            errors.append(f"high-cardinality Loki label is forbidden: {forbidden}")
    if "unix:///var/run/docker.sock" not in alloy:
        errors.append("Alloy does not use the Docker socket discovery owner")
    if "http://loki:3100/loki/api/v1/push" not in alloy:
        errors.append("Alloy does not write to the target Loki service")

    loki = load_yaml(ROOT / "observability/loki/loki.yml")
    retention = loki.get("limits_config", {}).get("retention_period")
    if not retention:
        errors.append("Loki retention_period is not configured")

    for datasource in (
        ROOT / "observability/grafana/provisioning/datasources/prometheus.yml",
        ROOT / "observability/grafana/provisioning/datasources/loki.yml",
    ):
        value = load_yaml(datasource)
        if not value.get("datasources"):
            errors.append(f"Grafana datasource file is empty: {datasource.name}")

    secret_paths = sorted((ROOT / "docker/secrets/dev").glob("*.txt"))
    active_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in _observability_files()
        if path.is_file()
    )
    for path in secret_paths:
        secret = path.read_text(encoding="utf-8").strip()
        # Development usernames and short fixture passwords intentionally
        # overlap with service names; only scan values long enough to be
        # meaningful accidental credential leakage.
        if len(secret) >= 12 and secret in active_text:
            errors.append(f"observability asset contains secret value from {path.name}")

    _validate_runtime_images(errors)

    if errors:
        print("Target observability configuration validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "Target observability contract is valid: "
        f"{len(REQUIRED_SCRAPE_JOBS)} scrape jobs, {len(REQUIRED_ALERTS)} alerts, "
        f"{len(REQUIRED_DASHBOARDS)} dashboards."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
