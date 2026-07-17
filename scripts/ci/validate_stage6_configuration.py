#!/usr/bin/env python3
"""Validate the version-controlled Phase 6 observability and recovery contract."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_SERVICES = {
    "prometheus",
    "alertmanager",
    "grafana",
    "loki",
    "alloy",
    "node-exporter",
    "cadvisor",
    "statsd-exporter",
    "postgres-exporter-oltp",
    "postgres-exporter-warehouse",
    "cdc-pipeline-exporter",
}
REQUIRED_ALERTS = {
    "CdcConnectorNotRunning",
    "CdcConnectorTaskNotRunning",
    "CdcHeartbeatMissing",
    "CdcRetainedWalHighAndGrowing",
    "CdcWarehouseOffsetGap",
    "CdcDlqOrQuarantineRecords",
    "CdcNifiBackpressureHigh",
    "CdcKafkaBacklogHigh",
    "CdcCommitToMartSloBreach",
    "CdcLatencyErrorBudgetBurn",
    "CdcIngestStalled",
    "CdcTransformStalled",
    "CdcTooManySmallFiles",
    "CdcAirflowDagFailure",
    "CdcDbtTransformFailure",
    "CdcMartStale",
    "CdcContainerDiskPressure",
}
REQUIRED_DASHBOARDS = {
    "olist-cdc-slo",
    "olist-cdc-source",
    "olist-cdc-kafka",
    "olist-cdc-nifi",
    "olist-cdc-airflow",
    "olist-cdc-capacity",
}
REQUIRED_RUNBOOKS = {
    "cdc-service-restart.md",
    "cdc-kafka-replay.md",
    "cdc-warehouse-rebuild.md",
    "cdc-rebuild-from-landing.md",
    "cdc-connector-resnapshot.md",
    "cdc-schema-migration.md",
    "cdc-secret-rotation.md",
    "cdc-alert-testing.md",
}


def load_yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def main() -> int:
    errors: list[str] = []
    compose = load_yaml(ROOT / "compose.yaml")
    services = compose.get("services", {})
    missing_services = REQUIRED_SERVICES - set(services)
    if missing_services:
        errors.append(f"missing Compose services: {sorted(missing_services)}")
    for service in ("loki", "alloy"):
        profiles = set(services.get(service, {}).get("profiles", []))
        if "logs" not in profiles:
            errors.append(f"{service} is not attached to the logs profile")

    rules = load_yaml(ROOT / "observability/prometheus/rules/cdc-component-alerts.yml")
    alerts = {
        rule.get("alert")
        for group in rules.get("groups", [])
        for rule in group.get("rules", [])
        if rule.get("alert")
    }
    missing_alerts = REQUIRED_ALERTS - alerts
    if missing_alerts:
        errors.append(f"missing alerts: {sorted(missing_alerts)}")
    for group in rules.get("groups", []):
        for rule in group.get("rules", []):
            if rule.get("alert") and not rule.get("annotations", {}).get("runbook"):
                errors.append(f"alert {rule['alert']} has no runbook annotation")

    dashboard_dir = ROOT / "observability/grafana/dashboards"
    dashboards: dict[str, dict] = {}
    for path in dashboard_dir.glob("*.json"):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid dashboard JSON {path.name}: {exc}")
            continue
        uid = value.get("uid")
        if uid:
            dashboards[str(uid)] = value
    missing_dashboards = REQUIRED_DASHBOARDS - set(dashboards)
    if missing_dashboards:
        errors.append(f"missing dashboards: {sorted(missing_dashboards)}")
    for uid in REQUIRED_DASHBOARDS & set(dashboards):
        if len(dashboards[uid].get("panels", [])) < 6:
            errors.append(f"dashboard {uid} has fewer than six operational panels")

    runbook_dir = ROOT / "docs/runbooks"
    missing_runbooks = {
        name for name in REQUIRED_RUNBOOKS if not (runbook_dir / name).is_file()
    }
    if missing_runbooks:
        errors.append(f"missing recovery runbooks: {sorted(missing_runbooks)}")

    alloy = (ROOT / "observability/alloy/config.alloy").read_text(encoding="utf-8")
    for forbidden in ("simulation_run_id", "_event_id", "cdc_run_id"):
        if f'target_label = "{forbidden}"' in alloy:
            errors.append(f"high-cardinality Loki label is forbidden: {forbidden}")

    loki = load_yaml(ROOT / "observability/loki/loki.yml")
    retention = loki.get("limits_config", {}).get("retention_period")
    if not retention:
        errors.append("Loki retention_period is not configured")

    if errors:
        print("Phase 6 configuration validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "Phase 6 observability contract is valid: "
        f"{len(REQUIRED_DASHBOARDS)} dashboards, {len(REQUIRED_ALERTS)} alerts, "
        f"{len(REQUIRED_RUNBOOKS)} recovery runbooks."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
