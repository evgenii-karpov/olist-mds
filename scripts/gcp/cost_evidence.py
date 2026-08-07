"""Credential-free validation and reporting for GCP cost evidence.

Cloud runners may populate this schema after a real run. The validator itself
only checks bounded, redacted evidence and therefore remains safe to execute
in CI without GCP credentials or billing access.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

COST_EVIDENCE_VERSION = "wp11-v1"
_LABEL_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{0,62}$")
_RUN_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_JOB_STATUSES = {"SUCCEEDED", "FAILED", "REJECTED_MAX_BYTES"}
_CLEANUP_STATUSES = {"PASS", "FAIL", "PENDING_GCP_ACCESS", "NOT_RUN"}


def _non_negative_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _require_text(
    value: Any, field: str, pattern: re.Pattern[str] | None = None
) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text")
    normalized = value.strip()
    if pattern is not None and not pattern.fullmatch(normalized):
        raise ValueError(f"{field} has an unsafe value")
    return normalized


def validate_job(job: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one BigQuery job evidence record and return a redacted copy."""

    job_id = _require_text(job.get("job_id"), "job_id")
    status = _require_text(job.get("status"), "status")
    if status not in _JOB_STATUSES:
        raise ValueError(f"job {job_id} has an unsupported status {status!r}")
    raw_labels = job.get("labels")
    if not isinstance(raw_labels, Mapping):
        raise ValueError(f"job {job_id} labels must be an object")
    labels = {
        _require_text(key, "label key", _LABEL_PATTERN): _require_text(
            value, "label value", _LABEL_PATTERN
        )
        for key, value in raw_labels.items()
    }
    required_labels = {"component", "target", "run"}
    if not required_labels <= set(labels):
        raise ValueError(f"job {job_id} is missing required labels")
    bytes_processed = _non_negative_int(
        job.get("bytes_processed", 0), f"job {job_id} bytes_processed"
    )
    bytes_billed = _non_negative_int(
        job.get("bytes_billed", 0), f"job {job_id} bytes_billed"
    )
    maximum = job.get("maximum_bytes_billed")
    if maximum is not None:
        maximum = _non_negative_int(maximum, f"job {job_id} maximum_bytes_billed")
        if maximum == 0:
            raise ValueError(f"job {job_id} maximum_bytes_billed must be positive")
    if status == "SUCCEEDED" and maximum is not None and bytes_billed > maximum:
        raise ValueError(f"successful job {job_id} exceeded maximum_bytes_billed")
    return {
        "job_id": job_id,
        "status": status,
        "labels": labels,
        "bytes_processed": bytes_processed,
        "bytes_billed": bytes_billed,
        "maximum_bytes_billed": maximum,
        "location": str(job.get("location", "")),
    }


def validate_cost_evidence(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and normalize a complete run cost/resource evidence payload."""

    if payload.get("version") != COST_EVIDENCE_VERSION:
        raise ValueError("unsupported cost evidence version")
    run_id = _require_text(payload.get("run_id"), "run_id", _RUN_PATTERN)
    jobs = payload.get("jobs")
    if not isinstance(jobs, list) or not all(isinstance(job, Mapping) for job in jobs):
        raise ValueError("jobs must be a list of objects")
    normalized_jobs = [validate_job(job) for job in jobs]
    job_ids = [job["job_id"] for job in normalized_jobs]
    if len(job_ids) != len(set(job_ids)):
        raise ValueError("job_id values must be unique")

    gcs = payload.get("gcs", {})
    if not isinstance(gcs, Mapping):
        raise ValueError("gcs must be an object")
    normalized_gcs = {
        "object_count": _non_negative_int(
            gcs.get("object_count", 0), "gcs.object_count"
        ),
        "bytes": _non_negative_int(gcs.get("bytes", 0), "gcs.bytes"),
    }

    resources = payload.get("residual_resources", [])
    if not isinstance(resources, list):
        raise ValueError("residual_resources must be a list")
    normalized_resources: list[dict[str, Any]] = []
    for resource in resources:
        if not isinstance(resource, Mapping):
            raise ValueError("each residual resource must be an object")
        normalized_resources.append(
            {
                "kind": _require_text(resource.get("kind"), "resource kind"),
                "name": _require_text(resource.get("name"), "resource name"),
                "managed": bool(resource.get("managed", True)),
            }
        )

    cleanup = _require_text(payload.get("cleanup", "NOT_RUN"), "cleanup")
    if cleanup not in _CLEANUP_STATUSES:
        raise ValueError(f"unsupported cleanup status {cleanup!r}")
    free_trial = _require_text(
        payload.get("free_trial_observation", "NOT_OBSERVED"),
        "free_trial_observation",
    )
    return {
        "version": COST_EVIDENCE_VERSION,
        "status": str(payload.get("status", "RECORDED")),
        "cloud_execution": str(payload.get("cloud_execution", "READY")),
        "run_id": run_id,
        "jobs": normalized_jobs,
        "gcs": normalized_gcs,
        "residual_resources": normalized_resources,
        "cleanup": cleanup,
        "free_trial_observation": free_trial,
    }


def pending_cost_report(run_id: str = "not-run") -> dict[str, Any]:
    return {
        "version": COST_EVIDENCE_VERSION,
        "status": "BLOCKED",
        "cloud_execution": "PENDING_GCP_ACCESS",
        "run_id": _require_text(run_id, "run_id", _RUN_PATTERN),
        "jobs": [],
        "gcs": {"object_count": 0, "bytes": 0},
        "residual_resources": [],
        "cleanup": "PENDING_GCP_ACCESS",
        "free_trial_observation": "NOT_OBSERVED",
        "next_steps": [
            "record BigQuery job labels and processed/billed bytes",
            "record GCS object count/bytes and residual resource inventory",
            "record manual Free Trial/billing observation and cleanup result",
        ],
    }


def load_cost_evidence(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"cost evidence does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cost evidence is not valid JSON: {path}") from exc
    if not isinstance(payload, Mapping):
        raise ValueError("cost evidence root must be an object")
    return validate_cost_evidence(payload)


def write_cost_report(output_dir: Path, report: Mapping[str, Any]) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "cost.json"
    markdown_path = output_dir / "cost.md"
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    jobs = report.get("jobs", [])
    total_processed = sum(int(job.get("bytes_processed", 0)) for job in jobs)
    total_billed = sum(int(job.get("bytes_billed", 0)) for job in jobs)
    lines = [
        "# GCP cost and residual-resource evidence",
        "",
        f"- Run: `{report.get('run_id', '')}`",
        f"- Status: **{report.get('status', 'UNKNOWN')}**",
        f"- Cloud execution: `{report.get('cloud_execution', 'UNKNOWN')}`",
        f"- BigQuery bytes processed: `{total_processed}`",
        f"- BigQuery bytes billed: `{total_billed}`",
        f"- GCS objects: `{report.get('gcs', {}).get('object_count', 0)}`",
        f"- GCS bytes: `{report.get('gcs', {}).get('bytes', 0)}`",
        f"- Cleanup: `{report.get('cleanup', 'UNKNOWN')}`",
        "",
        "## BigQuery jobs",
        "",
        "| Job | Status | Run label | Bytes processed | Bytes billed | Cap |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for job in jobs if isinstance(jobs, Sequence) else []:
        lines.append(
            f"| `{job.get('job_id', '')}` | `{job.get('status', '')}` | "
            f"`{job.get('labels', {}).get('run', '')}` | "
            f"{job.get('bytes_processed', 0)} | {job.get('bytes_billed', 0)} | "
            f"{job.get('maximum_bytes_billed', '')} |"
        )
    lines.extend(["", "## Residual resources", ""])
    resources = report.get("residual_resources", [])
    if resources:
        lines.extend(["| Kind | Name | Managed |", "| --- | --- | --- |"])
        for resource in resources:
            lines.append(
                f"| `{resource.get('kind', '')}` | `{resource.get('name', '')}` | "
                f"{resource.get('managed', True)} |"
            )
    else:
        lines.append("No residual resources recorded.")
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, markdown_path
