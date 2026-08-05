#!/usr/bin/env python3
"""Run bounded live acceptance checks for the target observability stack."""

from __future__ import annotations

import argparse
import base64
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_JOBS = {
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
TARGETS = (
    "mysql",
    "kafka",
    "kafka-connect",
    "apicurio",
    "spark",
    "spark-streaming",
    "minio",
    "polaris",
    "clickhouse",
    "airflow",
    "control-postgres",
)


def _get_json(url: str, headers: dict[str, str] | None = None) -> tuple[int, Any]:
    request = Request(url, headers=headers or {"Accept": "application/json"})
    try:
        with urlopen(request, timeout=15) as response:
            raw = response.read().decode("utf-8", errors="replace")
            try:
                return response.status, json.loads(raw) if raw.strip() else None
            except json.JSONDecodeError:
                return response.status, None
    except HTTPError as exc:
        return exc.code, None
    except URLError:
        return 0, None


def _get_text(url: str) -> tuple[int, str]:
    try:
        with urlopen(url, timeout=15) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        return exc.code, ""
    except URLError:
        return 0, ""


def _check_http(checks: list[dict[str, Any]], name: str, url: str) -> None:
    status, _ = _get_text(url)
    checks.append(
        {"name": name, "url": url, "status_code": status, "ok": status == 200}
    )


def _basic_auth(user: str, password: str) -> dict[str, str]:
    token = base64.b64encode(f"{user}:{password}".encode()).decode("ascii")
    return {"Accept": "application/json", "Authorization": f"Basic {token}"}


def _probe_value(body: str, target: str) -> float | None:
    pattern = re.compile(
        rf'^olist_target_up\{{target="{re.escape(target)}"\}}\s+([0-9.]+)$',
        re.MULTILINE,
    )
    match = pattern.search(body)
    return float(match.group(1)) if match else None


def _metric_value(body: str, metric: str, label: str) -> float | None:
    pattern = re.compile(
        rf'^{re.escape(metric)}\{{state="{re.escape(label)}"\}}\s+([0-9.]+)$',
        re.MULTILINE,
    )
    match = pattern.search(body)
    return float(match.group(1)) if match else None


def _check_prometheus(
    checks: list[dict[str, Any]],
    errors: list[str],
    prometheus_url: str,
) -> None:
    status, payload = _get_json(f"{prometheus_url}/api/v1/targets")
    active = (
        payload.get("data", {}).get("activeTargets", [])
        if isinstance(payload, dict)
        else []
    )
    by_job: dict[str, list[dict[str, Any]]] = {}
    for target in active:
        labels = target.get("labels", {}) if isinstance(target, dict) else {}
        job = labels.get("job")
        if job:
            by_job.setdefault(str(job), []).append(target)
    checks.append(
        {
            "name": "prometheus-targets",
            "url": f"{prometheus_url}/api/v1/targets",
            "status_code": status,
            "active_jobs": sorted(by_job),
            "ok": status == 200 and set(by_job) >= REQUIRED_JOBS,
        }
    )
    if status != 200:
        errors.append(f"Prometheus targets API returned HTTP {status}")
    for job in sorted(REQUIRED_JOBS):
        targets = by_job.get(job, [])
        if not targets:
            errors.append(f"Prometheus target job is missing: {job}")
            continue
        unhealthy = [
            target.get("scrapeUrl", job)
            for target in targets
            if target.get("health") != "up"
        ]
        if unhealthy:
            errors.append(f"Prometheus target job is not UP: {job}: {unhealthy}")

    status, payload = _get_json(f"{prometheus_url}/api/v1/rules?type=alert")
    loaded_alerts = {
        str(rule.get("name"))
        for group in (payload or {}).get("data", {}).get("groups", [])
        for rule in group.get("rules", [])
        if isinstance(rule, dict) and rule.get("name")
    }
    missing_alerts = sorted(REQUIRED_ALERTS - loaded_alerts)
    checks.append(
        {
            "name": "prometheus-alert-rules",
            "url": f"{prometheus_url}/api/v1/rules?type=alert",
            "status_code": status,
            "loaded_alerts": sorted(loaded_alerts),
            "missing_alerts": missing_alerts,
            "ok": status == 200 and not missing_alerts,
        }
    )
    errors.extend(
        f"Prometheus alert rule is missing: {name}" for name in missing_alerts
    )

    query = urlencode({"query": "olist_target_up"})
    status, payload = _get_json(f"{prometheus_url}/api/v1/query?{query}")
    result = (payload or {}).get("data", {}).get("result", [])
    checks.append(
        {
            "name": "prometheus-target-metric",
            "url": f"{prometheus_url}/api/v1/query",
            "status_code": status,
            "series_count": len(result) if isinstance(result, list) else 0,
            "ok": status == 200 and bool(result),
        }
    )
    if status != 200 or not result:
        errors.append("Prometheus target metric query returned no data")

    query = urlencode({"query": "olist_lakehouse:kafka_consumer_lag"})
    status, payload = _get_json(f"{prometheus_url}/api/v1/query?{query}")
    result = (payload or {}).get("data", {}).get("result", [])
    checks.append(
        {
            "name": "prometheus-target-kafka-lag",
            "url": f"{prometheus_url}/api/v1/query",
            "status_code": status,
            "series_count": len(result) if isinstance(result, list) else 0,
            "ok": status == 200 and bool(result),
        }
    )
    if status != 200 or not result:
        errors.append("Prometheus target Kafka lag query returned no data")


def _check_loki(
    checks: list[dict[str, Any]],
    errors: list[str],
    loki_url: str,
) -> None:
    labels_url = f"{loki_url}/loki/api/v1/labels"
    status, payload = _get_json(labels_url)
    labels_value = (payload or {}).get("data", []) if isinstance(payload, dict) else []
    labels = labels_value if isinstance(labels_value, list) else []
    checks.append(
        {
            "name": "loki-labels",
            "url": labels_url,
            "status_code": status,
            "labels": sorted(str(label) for label in labels),
            "ok": status == 200 and "service" in labels,
        }
    )
    if status != 200 or "service" not in labels:
        errors.append("Loki did not expose the bounded service label")

    query = urlencode(
        {"query": '{service=~".+"}', "limit": "1", "direction": "backward"}
    )
    query_url = f"{loki_url}/loki/api/v1/query_range?{query}"
    status, payload = _get_json(query_url)
    streams = (payload or {}).get("data", {}).get("result", [])
    checks.append(
        {
            "name": "loki-log-query",
            "url": query_url,
            "status_code": status,
            "stream_count": len(streams) if isinstance(streams, list) else 0,
            "ok": status == 200 and bool(streams),
        }
    )
    if status != 200 or not streams:
        errors.append("Loki returned no ingested target log streams")


def _check_grafana(
    checks: list[dict[str, Any]],
    errors: list[str],
    grafana_url: str,
    user: str,
    password: str,
) -> None:
    headers = _basic_auth(user, password)
    status, payload = _get_json(f"{grafana_url}/api/search?type=dash-db", headers)
    dashboards = payload if isinstance(payload, list) else []
    dashboard_uids = {str(item.get("uid")) for item in dashboards if item.get("uid")}
    missing_dashboards = sorted(REQUIRED_DASHBOARDS - dashboard_uids)
    checks.append(
        {
            "name": "grafana-dashboards",
            "url": f"{grafana_url}/api/search?type=dash-db",
            "status_code": status,
            "dashboard_uids": sorted(dashboard_uids),
            "missing_dashboards": missing_dashboards,
            "ok": status == 200 and not missing_dashboards,
        }
    )
    errors.extend(f"Grafana dashboard is missing: {uid}" for uid in missing_dashboards)

    status, payload = _get_json(f"{grafana_url}/api/datasources", headers)
    datasource_uids = {
        str(item.get("uid"))
        for item in (payload if isinstance(payload, list) else [])
        if item.get("uid")
    }
    missing_datasources = sorted({"prometheus", "loki"} - datasource_uids)
    checks.append(
        {
            "name": "grafana-datasources",
            "url": f"{grafana_url}/api/datasources",
            "status_code": status,
            "datasource_uids": sorted(datasource_uids),
            "missing_datasources": missing_datasources,
            "ok": status == 200 and not missing_datasources,
        }
    )
    errors.extend(
        f"Grafana datasource is missing: {uid}" for uid in missing_datasources
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prometheus-url", default="http://localhost:9090")
    parser.add_argument("--alertmanager-url", default="http://localhost:9093")
    parser.add_argument("--grafana-url", default="http://localhost:3000")
    parser.add_argument("--loki-url", default="http://localhost:3100")
    parser.add_argument("--alloy-url", default="http://localhost:12345")
    parser.add_argument("--probe-url", default="http://localhost:9108")
    parser.add_argument("--grafana-user", default="admin")
    parser.add_argument("--grafana-password", default="admin")
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("data/acceptance/observability-acceptance.json"),
    )
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []
    errors: list[str] = []
    _check_http(checks, "prometheus-ready", f"{args.prometheus_url}/-/ready")
    _check_http(checks, "alertmanager-ready", f"{args.alertmanager_url}/-/ready")
    _check_http(checks, "grafana-health", f"{args.grafana_url}/api/health")
    _check_http(checks, "loki-ready", f"{args.loki_url}/ready")
    _check_http(checks, "alloy-ready", f"{args.alloy_url}/-/ready")
    _check_http(checks, "target-probe-ready", f"{args.probe_url}/healthz")
    for check in checks:
        if not check["ok"]:
            errors.append(f"{check['name']} returned HTTP {check['status_code']}")

    for target in TARGETS:
        url = f"{args.probe_url}/probe?{urlencode({'target': target})}"
        status, body = _get_text(url)
        value = _probe_value(body, target)
        ok = status == 200 and value == 1.0
        checks.append(
            {
                "name": f"target-probe-{target}",
                "url": url,
                "status_code": status,
                "up_value": value,
                "ok": ok,
            }
        )
        if not ok:
            errors.append(
                f"target probe is not UP: {target} (value={value!r}, HTTP={status})"
            )

    _check_prometheus(checks, errors, args.prometheus_url.rstrip("/"))
    _check_loki(checks, errors, args.loki_url.rstrip("/"))
    status, body = _get_text(f"{args.probe_url}/metrics")
    firing_webhooks = _metric_value(
        body, "olist_alertmanager_webhook_alerts_total", "firing"
    )
    resolved_webhooks = _metric_value(
        body, "olist_alertmanager_webhook_alerts_total", "resolved"
    )
    checks.append(
        {
            "name": "alertmanager-webhook-receiver",
            "url": f"{args.probe_url}/metrics",
            "status_code": status,
            "firing_webhooks": firing_webhooks,
            "resolved_webhooks": resolved_webhooks,
            "ok": status == 200
            and firing_webhooks is not None
            and resolved_webhooks is not None,
        }
    )
    if status != 200 or firing_webhooks is None or resolved_webhooks is None:
        errors.append("Alertmanager webhook receiver metrics are unavailable")
    _check_grafana(
        checks,
        errors,
        args.grafana_url.rstrip("/"),
        args.grafana_user,
        args.grafana_password,
    )

    result = {
        "status": "PASS" if not errors else "FAIL",
        "started_at": datetime.now(UTC).isoformat(),
        "candidate": "uncommitted worktree",
        "local_cdc_acceptance": "not_run_and_not_modified",
        "checks": checks,
        "errors": errors,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
