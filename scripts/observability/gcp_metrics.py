"""Bounded Prometheus rendering for GCP serving evidence.

The renderer is intentionally transport-agnostic. A future Linux runtime may
serve its output through the existing target-probe, while CI can validate the
metric names, labels, and cost-derived samples without contacting GCP.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

GCP_METRIC_CONTRACT: dict[str, str] = {
    "olist_gcp_kafka_current_offset": "gauge",
    "olist_gcp_kafka_target_offset": "gauge",
    "olist_gcp_kafka_lag": "gauge",
    "olist_gcp_boundary_last_transaction_timestamp": "gauge",
    "olist_gcp_spark_batch_duration_seconds": "gauge",
    "olist_gcp_spark_input_rows": "gauge",
    "olist_gcp_spark_commit_failures_total": "counter",
    "olist_gcp_checkpoint_restart_failures_total": "counter",
    "olist_gcp_dbt_model_duration_seconds": "gauge",
    "olist_gcp_dbt_model_rows": "gauge",
    "olist_gcp_dbt_test_failures_total": "counter",
    "olist_gcp_publication_duration_seconds": "gauge",
    "olist_gcp_publication_idempotent_total": "counter",
    "olist_gcp_publication_conflicts_total": "counter",
    "olist_gcp_bigquery_bytes_processed": "gauge",
    "olist_gcp_bigquery_bytes_billed": "gauge",
    "olist_gcp_bigquery_max_bytes_rejections_total": "counter",
    "olist_gcp_biglake_auth_errors_total": "counter",
    "olist_gcp_biglake_catalog_errors_total": "counter",
    "olist_gcp_biglake_checkpoint_errors_total": "counter",
    "olist_gcp_biglake_commit_errors_total": "counter",
}
ALLOWED_LABELS = frozenset(
    {"contour", "run", "model", "query", "topic", "partition", "entity", "status"}
)
MAX_LABEL_LENGTH = 128


def _escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _labels(labels: Mapping[str, Any]) -> str:
    if not labels:
        return ""
    normalized = []
    for key, value in sorted(labels.items(), key=lambda item: str(item[0])):
        name = str(key)
        text = str(value)
        if name not in ALLOWED_LABELS:
            raise ValueError(f"unsupported GCP metric label: {name}")
        if not text or len(text) > MAX_LABEL_LENGTH:
            raise ValueError(f"GCP metric label {name!r} is empty or too long")
        normalized.append(f'{name}="{_escape_label(text)}"')
    return "{" + ",".join(normalized) + "}"


def validate_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    contour = str(payload.get("contour", "gcp"))
    run_id = str(payload.get("run_id", ""))
    if contour != "gcp":
        raise ValueError("GCP metrics contour must be gcp")
    if not run_id or len(run_id) > MAX_LABEL_LENGTH:
        raise ValueError("GCP metrics run_id is required and bounded")
    raw_metrics = payload.get("metrics")
    if not isinstance(raw_metrics, list):
        raise ValueError("GCP metrics payload must contain a metrics list")
    metrics: list[dict[str, Any]] = []
    for item in raw_metrics:
        if not isinstance(item, Mapping):
            raise ValueError("each GCP metric must be an object")
        name = str(item.get("name", ""))
        if name not in GCP_METRIC_CONTRACT:
            raise ValueError(f"unsupported GCP metric: {name}")
        value = item.get("value")
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise ValueError(f"GCP metric {name} must have a finite numeric value")
        raw_labels = item.get("labels", {})
        if not isinstance(raw_labels, Mapping):
            raise ValueError(f"GCP metric {name} labels must be an object")
        labels = {"contour": contour, "run": run_id, **dict(raw_labels)}
        _labels(labels)
        metrics.append({"name": name, "value": float(value), "labels": labels})
    return {"contour": contour, "run_id": run_id, "metrics": metrics}


def render(payload: Mapping[str, Any]) -> str:
    normalized = validate_payload(payload)
    lines: list[str] = []
    emitted: set[str] = set()
    for metric in normalized["metrics"]:
        name = metric["name"]
        if name not in emitted:
            lines.append(f"# HELP {name} GCP serving evidence metric.")
            lines.append(f"# TYPE {name} {GCP_METRIC_CONTRACT[name]}")
            emitted.add(name)
        lines.append(f"{name}{_labels(metric['labels'])} {metric['value']:g}")
    return "\n".join(lines) + ("\n" if lines else "")


def metrics_from_cost_evidence(cost_report: Mapping[str, Any]) -> dict[str, Any]:
    """Derive low-cardinality BigQuery cost metrics from validated evidence."""

    run_id = str(cost_report.get("run_id", ""))
    if not run_id:
        raise ValueError("cost report run_id is required")
    jobs = cost_report.get("jobs", [])
    if not isinstance(jobs, Sequence):
        raise ValueError("cost report jobs must be a sequence")
    processed = sum(
        int(job.get("bytes_processed", 0)) for job in jobs if isinstance(job, Mapping)
    )
    billed = sum(
        int(job.get("bytes_billed", 0)) for job in jobs if isinstance(job, Mapping)
    )
    rejections = sum(
        1
        for job in jobs
        if isinstance(job, Mapping) and job.get("status") == "REJECTED_MAX_BYTES"
    )
    return validate_payload(
        {
            "contour": "gcp",
            "run_id": run_id,
            "metrics": [
                {"name": "olist_gcp_bigquery_bytes_processed", "value": processed},
                {"name": "olist_gcp_bigquery_bytes_billed", "value": billed},
                {
                    "name": "olist_gcp_bigquery_max_bytes_rejections_total",
                    "value": rejections,
                },
            ],
        }
    )
