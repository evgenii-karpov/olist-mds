from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

import pytest
from scripts import lab
from scripts.gcp.cost_evidence import (
    load_cost_evidence,
    pending_cost_report,
    validate_cost_evidence,
    write_cost_report,
)


def _job(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "job_id": "job-1",
        "status": "SUCCEEDED",
        "labels": {
            "component": "olist-gcp-serving",
            "target": "gcp",
            "run": "run-7",
        },
        "bytes_processed": 100,
        "bytes_billed": 80,
        "maximum_bytes_billed": 1000,
        "location": "us-east1",
    }
    value.update(overrides)
    return value


def _payload(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "version": "wp11-v1",
        "status": "RECORDED",
        "cloud_execution": "READY",
        "run_id": "run-7",
        "jobs": [_job()],
        "gcs": {"object_count": 2, "bytes": 42},
        "residual_resources": [],
        "cleanup": "PASS",
        "free_trial_observation": "MANUAL_CONFIRMED",
    }
    value.update(overrides)
    return value


def test_cost_evidence_validates_labels_bytes_and_cleanup() -> None:
    report = validate_cost_evidence(_payload())

    assert report["run_id"] == "run-7"
    assert report["jobs"][0]["bytes_billed"] == 80
    assert report["cleanup"] == "PASS"


def test_successful_job_cannot_exceed_the_declared_cap() -> None:
    with pytest.raises(ValueError, match="exceeded maximum_bytes_billed"):
        validate_cost_evidence(_payload(jobs=[_job(bytes_billed=1001)]))


def test_required_labels_are_fail_closed() -> None:
    job = _job(labels={"component": "olist-gcp-serving", "target": "gcp"})

    with pytest.raises(ValueError, match="missing required labels"):
        validate_cost_evidence(_payload(jobs=[job]))


def test_pending_cost_report_is_explicit_and_writable(tmp_path: Path) -> None:
    report = pending_cost_report()
    json_path, markdown_path = write_cost_report(tmp_path, report)

    assert report["cloud_execution"] == "PENDING_GCP_ACCESS"
    assert json.loads(json_path.read_text(encoding="utf-8"))["status"] == "BLOCKED"
    assert "PENDING_GCP_ACCESS" in markdown_path.read_text(encoding="utf-8")


def test_load_cost_evidence_uses_the_same_validator(tmp_path: Path) -> None:
    path = tmp_path / "cost.json"
    path.write_text(json.dumps(_payload()), encoding="utf-8")

    assert load_cost_evidence(path)["jobs"][0]["job_id"] == "job-1"


def test_lab_cost_report_without_input_is_blocked_but_writes_evidence(
    tmp_path: Path, capsys
) -> None:
    result = lab._gcp_cost_report(Namespace(input=None, output=str(tmp_path)))

    assert result == 0
    assert (
        json.loads((tmp_path / "cost.json").read_text(encoding="utf-8"))["status"]
        == "BLOCKED"
    )
    assert '"status": "blocked"' in capsys.readouterr().out
