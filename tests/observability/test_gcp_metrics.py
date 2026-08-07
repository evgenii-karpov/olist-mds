from __future__ import annotations

import json
from pathlib import Path

import pytest
from scripts.observability.gcp_metrics import (
    metrics_from_cost_evidence,
    render,
    validate_payload,
)

ROOT = Path(__file__).resolve().parents[2]


def test_gcp_metric_renderer_adds_bounded_contour_and_run_labels() -> None:
    output = render(
        {
            "contour": "gcp",
            "run_id": "run-7",
            "metrics": [
                {
                    "name": "olist_gcp_dbt_model_rows",
                    "value": 8,
                    "labels": {"model": "fact_order_items"},
                }
            ],
        }
    )

    assert "# TYPE olist_gcp_dbt_model_rows gauge" in output
    assert 'contour="gcp"' in output
    assert 'run="run-7"' in output
    assert 'model="fact_order_items"' in output


def test_unknown_metric_and_high_cardinality_label_are_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported GCP metric"):
        validate_payload(
            {
                "contour": "gcp",
                "run_id": "run-1",
                "metrics": [{"name": "unknown", "value": 1}],
            }
        )
    with pytest.raises(ValueError, match="unsupported GCP metric label"):
        render(
            {
                "contour": "gcp",
                "run_id": "run-1",
                "metrics": [
                    {
                        "name": "olist_gcp_dbt_model_rows",
                        "value": 1,
                        "labels": {"job_id": "high-cardinality"},
                    }
                ],
            }
        )


def test_cost_evidence_becomes_low_cardinality_bigquery_metrics() -> None:
    payload = metrics_from_cost_evidence(
        {
            "run_id": "run-7",
            "jobs": [
                {"bytes_processed": 100, "bytes_billed": 80, "status": "SUCCEEDED"},
                {
                    "bytes_processed": 200,
                    "bytes_billed": 0,
                    "status": "REJECTED_MAX_BYTES",
                },
            ],
        }
    )

    values = {item["name"]: item["value"] for item in payload["metrics"]}
    assert values == {
        "olist_gcp_bigquery_bytes_processed": 300.0,
        "olist_gcp_bigquery_bytes_billed": 80.0,
        "olist_gcp_bigquery_max_bytes_rejections_total": 1.0,
    }


def test_gcp_serving_dashboard_and_recordings_cover_cost_and_failure_signals() -> None:
    dashboard = json.loads(
        (ROOT / "observability/grafana/dashboards/lakehouse-serving.json").read_text(
            encoding="utf-8"
        )
    )
    payload = json.dumps(dashboard)
    for metric in (
        "olist_gcp_bigquery_bytes_billed",
        "olist_gcp_bigquery_max_bytes_rejections_total",
        "olist_gcp_dbt_model_rows",
        "olist_gcp_publication_conflicts_total",
        "olist_gcp_biglake_auth_errors_total",
    ):
        assert metric in payload
    recordings = (
        ROOT / "observability/prometheus/rules/gcp-serving-recording.yml"
    ).read_text(encoding="utf-8")
    assert "olist_lakehouse:gcp_bigquery_bytes_billed" in recordings
    assert "olist_lakehouse:gcp_biglake_errors" in recordings
