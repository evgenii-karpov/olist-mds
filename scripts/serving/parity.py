"""Strict, evidence-based cross-contour parity comparison.

The comparator deliberately does not contact either contour. Local and GCP
operators can run their contours sequentially and hand the resulting JSON
evidence to this module. When the GCP evidence is absent, the command writes a
reproducible blocked report instead of presenting a static plan as parity
acceptance.
"""

from __future__ import annotations

import base64
import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

PARITY_VERSION = "wp11-v1"
DEFAULT_OUTPUT_DIR = Path("data/acceptance/gcp/parity")
MAX_DIFFERENCES = 50
MAX_HASH_SAMPLES = 10


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _normalize_decimal(value: Any) -> str:
    try:
        candidate = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"numeric value is not finite decimal: {value!r}") from exc
    if not candidate.is_finite():
        raise ValueError(f"numeric value is not finite decimal: {value!r}")
    if candidate == 0:
        return "0"
    return format(candidate.normalize(), "f")


def _normalize_timestamp(value: Any) -> str:
    if isinstance(value, datetime):
        candidate = value
    elif isinstance(value, str):
        text = value.strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            candidate = datetime.fromisoformat(text)
        except ValueError as exc:
            raise ValueError(f"invalid timestamp value: {value!r}") from exc
    else:
        raise ValueError(f"timestamp value must be ISO text or datetime: {value!r}")
    if candidate.tzinfo is None:
        candidate = candidate.replace(tzinfo=UTC)
    else:
        candidate = candidate.astimezone(UTC)
    return candidate.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _normalize_binary(value: Any) -> str:
    if isinstance(value, bytes):
        encoded = base64.b64encode(value).decode("ascii")
    elif isinstance(value, str):
        encoded = value.removeprefix("base64:")
    else:
        raise ValueError(f"binary value must be bytes or base64 text: {value!r}")
    return f"base64:{encoded}"


def _normalize_value(value: Any, kind: str | None = None) -> Any:
    if kind == "numeric":
        return _normalize_decimal(value)
    if kind == "timestamp":
        return _normalize_timestamp(value)
    if kind == "binary":
        return _normalize_binary(value)
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"floating-point value is not finite: {value!r}")
        return value
    if isinstance(value, Decimal):
        return _normalize_decimal(value)
    if isinstance(value, datetime):
        return _normalize_timestamp(value)
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, bytes):
        return _normalize_binary(value)
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_value(item)
            for key, item in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_normalize_value(item) for item in value]
    raise ValueError(f"unsupported parity value type: {type(value).__name__}")


def _field_rules(spec: Mapping[str, Any]) -> dict[str, set[str]]:
    rules = {
        "numeric": set(str(value) for value in spec.get("numeric_fields", [])),
        "timestamp": set(str(value) for value in spec.get("timestamp_fields", [])),
        "binary": set(str(value) for value in spec.get("binary_fields", [])),
    }
    all_fields: list[str] = []
    for kind, fields in rules.items():
        if not isinstance(spec.get(f"{kind}_fields", []), list):
            raise ValueError(f"{kind}_fields must be a list")
        all_fields.extend(fields)
    if len(all_fields) != len(set(all_fields)):
        raise ValueError("parity representation fields cannot have multiple types")
    return rules


def _normalize_row(
    row: Mapping[str, Any], rules: Mapping[str, set[str]]
) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in sorted(row.items(), key=lambda item: str(item[0])):
        field = str(key)
        kind = next((name for name, fields in rules.items() if field in fields), None)
        normalized[field] = _normalize_value(value, kind)
    return normalized


def _row_key(row: Mapping[str, Any], primary_keys: Sequence[str]) -> tuple[str, ...]:
    values: list[str] = []
    for field in primary_keys:
        if field not in row:
            raise ValueError(f"row is missing primary-key field {field!r}")
        value = row[field]
        if value is None:
            raise ValueError(f"primary-key field {field!r} cannot be null")
        values.append(_canonical_json(value))
    return tuple(values)


def _key_hash(key: Sequence[str]) -> str:
    return hashlib.sha256("\x1f".join(key).encode("utf-8")).hexdigest()


def _normalize_model(name: str, spec: Mapping[str, Any]) -> dict[str, Any]:
    primary_keys = spec.get("primary_keys")
    rows = spec.get("rows")
    if not isinstance(primary_keys, list) or not primary_keys:
        raise ValueError(f"model {name!r} must declare a non-empty primary_keys list")
    if not all(isinstance(field, str) and field for field in primary_keys):
        raise ValueError(f"model {name!r} has invalid primary_keys")
    if len(primary_keys) != len(set(primary_keys)):
        raise ValueError(f"model {name!r} has duplicate primary_keys")
    if not isinstance(rows, list) or not all(isinstance(row, Mapping) for row in rows):
        raise ValueError(f"model {name!r} must contain a list of object rows")
    rules = _field_rules(spec)
    normalized_rows = [_normalize_row(row, rules) for row in rows]
    keyed_rows: dict[tuple[str, ...], dict[str, Any]] = {}
    for row in normalized_rows:
        key = _row_key(row, primary_keys)
        if key in keyed_rows:
            raise ValueError(f"model {name!r} contains duplicate primary key")
        keyed_rows[key] = row
    ordered_rows = [keyed_rows[key] for key in sorted(keyed_rows)]
    return {
        "primary_keys": list(primary_keys),
        "rows": ordered_rows,
        "row_count": len(ordered_rows),
        "checksum": _sha256(ordered_rows),
        "keyed_rows": keyed_rows,
    }


def load_evidence(path: Path) -> dict[str, Any]:
    """Load and validate one contour's JSON evidence file."""

    if not path.is_file():
        raise ValueError(f"parity evidence does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"parity evidence is not valid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ValueError("parity evidence root must be an object")
    contour = payload.get("contour")
    if contour not in {"local", "gcp"}:
        raise ValueError("parity evidence contour must be 'local' or 'gcp'")
    models = payload.get("models")
    if not isinstance(models, dict) or not models:
        raise ValueError("parity evidence must contain a non-empty models object")
    normalized_models = {
        str(name): _normalize_model(str(name), spec)
        for name, spec in sorted(models.items(), key=lambda item: str(item[0]))
        if isinstance(spec, Mapping)
    }
    if len(normalized_models) != len(models):
        raise ValueError("every parity model must be an object")
    return {
        "contour": contour,
        "run_id": str(payload.get("run_id", "")),
        "boundary": _normalize_value(payload.get("boundary"))
        if "boundary" in payload
        else None,
        "models": normalized_models,
    }


def _difference(
    differences: list[dict[str, Any]],
    category: str,
    **fields: Any,
) -> None:
    if len(differences) < MAX_DIFFERENCES:
        differences.append({"category": category, **fields})


def _model_summary(model: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "row_count": model["row_count"],
        "checksum": model["checksum"],
        "primary_keys": model["primary_keys"],
    }


def compare_evidence(
    local: Mapping[str, Any], gcp: Mapping[str, Any]
) -> dict[str, Any]:
    """Compare two loaded evidence payloads without exposing row values."""

    if local.get("contour") != "local" or gcp.get("contour") != "gcp":
        raise ValueError("compare_evidence requires local and gcp contours")
    differences: list[dict[str, Any]] = []
    if local.get("boundary") != gcp.get("boundary"):
        _difference(
            differences,
            "boundary",
            local_hash=_sha256(local.get("boundary")),
            gcp_hash=_sha256(gcp.get("boundary")),
        )
    local_models = local["models"]
    gcp_models = gcp["models"]
    local_names = set(local_models)
    gcp_names = set(gcp_models)
    for name in sorted(local_names - gcp_names):
        _difference(differences, "missing_model", model=name, contour="gcp")
    for name in sorted(gcp_names - local_names):
        _difference(differences, "missing_model", model=name, contour="local")

    summaries: dict[str, Any] = {}
    for name in sorted(local_names & gcp_names):
        left = local_models[name]
        right = gcp_models[name]
        summaries[name] = {
            "local": _model_summary(left),
            "gcp": _model_summary(right),
            "equal": True,
        }
        if left["primary_keys"] != right["primary_keys"]:
            summaries[name]["equal"] = False
            _difference(
                differences,
                "primary_keys",
                model=name,
                local=left["primary_keys"],
                gcp=right["primary_keys"],
            )
        if left["row_count"] != right["row_count"]:
            summaries[name]["equal"] = False
            _difference(
                differences,
                "row_count",
                model=name,
                local=left["row_count"],
                gcp=right["row_count"],
            )
        left_keys = set(left["keyed_rows"])
        right_keys = set(right["keyed_rows"])
        missing = sorted(left_keys - right_keys)
        extra = sorted(right_keys - left_keys)
        if missing or extra:
            summaries[name]["equal"] = False
            _difference(
                differences,
                "keys",
                model=name,
                local_missing_count=len(missing),
                gcp_missing_count=len(extra),
                local_missing_hashes=[
                    _key_hash(key) for key in missing[:MAX_HASH_SAMPLES]
                ],
                gcp_missing_hashes=[_key_hash(key) for key in extra[:MAX_HASH_SAMPLES]],
            )
        for key in sorted(left_keys & right_keys):
            left_row = left["keyed_rows"][key]
            right_row = right["keyed_rows"][key]
            if left_row != right_row:
                summaries[name]["equal"] = False
                fields = sorted(set(left_row) | set(right_row))
                differing_fields = [
                    field
                    for field in fields
                    if left_row.get(field) != right_row.get(field)
                ]
                _difference(
                    differences,
                    "row",
                    model=name,
                    key_hash=_key_hash(key),
                    fields=differing_fields,
                    local_row_hash=_sha256(left_row),
                    gcp_row_hash=_sha256(right_row),
                )
    return {
        "version": PARITY_VERSION,
        "status": "PASS" if not differences else "FAIL",
        "cloud_execution": "READY",
        "sequence": ["local", "gcp"],
        "run_ids": {"local": local.get("run_id", ""), "gcp": gcp.get("run_id", "")},
        "boundary": local.get("boundary"),
        "models": summaries,
        "differences": differences,
        "difference_count": len(differences),
        "differences_truncated": len(differences) >= MAX_DIFFERENCES,
        "normalization": {
            "timestamps": "UTC ISO-8601 with microseconds and Z suffix",
            "numeric_fields": "decimal text with insignificant trailing zeros removed",
            "binary_fields": "base64: prefixed text",
            "rows": "sorted by declared primary_keys",
        },
    }


def pending_report(reason: str = "PENDING_GCP_ACCESS") -> dict[str, Any]:
    return {
        "version": PARITY_VERSION,
        "status": "BLOCKED",
        "cloud_execution": "PENDING_GCP_ACCESS",
        "sequence": ["local", "gcp"],
        "reason": reason,
        "models": {},
        "differences": [],
        "difference_count": 0,
        "normalization": {
            "timestamps": "UTC ISO-8601 with microseconds and Z suffix",
            "numeric_fields": "decimal text with insignificant trailing zeros removed",
            "binary_fields": "base64: prefixed text",
            "rows": "sorted by declared primary_keys",
        },
        "next_steps": [
            "run the local contour and export model evidence",
            "run the GCP contour sequentially with the same frozen boundary",
            "rerun parity with both evidence paths",
        ],
    }


def compare_evidence_files(local_path: Path, gcp_path: Path) -> dict[str, Any]:
    return compare_evidence(load_evidence(local_path), load_evidence(gcp_path))


def write_report(output_dir: Path, report: Mapping[str, Any]) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "parity.json"
    markdown_path = output_dir / "parity.md"
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Cross-contour parity report",
        "",
        f"- Version: `{report.get('version', 'unknown')}`",
        f"- Status: **{report.get('status', 'UNKNOWN')}**",
        f"- Cloud execution: `{report.get('cloud_execution', 'UNKNOWN')}`",
        f"- Sequence: `{', '.join(str(item) for item in report.get('sequence', []))}`",
        f"- Differences: `{report.get('difference_count', 0)}`",
        "",
    ]
    if report.get("reason"):
        lines.extend([f"Reason: `{report['reason']}`", ""])
    lines.extend(
        [
            "## Model summary",
            "",
            "| Model | Local rows | GCP rows | Local checksum | GCP checksum | Equal |",
            "| --- | ---: | ---: | --- | --- | --- |",
        ]
    )
    models = report.get("models", {})
    for name, summary in sorted(models.items()):
        local = summary.get("local", {})
        gcp = summary.get("gcp", {})
        lines.append(
            f"| `{name}` | {local.get('row_count', '')} | {gcp.get('row_count', '')} | "
            f"`{local.get('checksum', '')}` | `{gcp.get('checksum', '')}` | "
            f"{summary.get('equal', False)} |"
        )
    lines.extend(["", "## Differences", ""])
    differences = report.get("differences", [])
    if not differences:
        lines.append("No differences recorded.")
    else:
        lines.extend(["| Category | Model | Detail |", "| --- | --- | --- |"])
        for difference in differences:
            detail = {
                key: value
                for key, value in difference.items()
                if key not in {"category", "model"}
            }
            lines.append(
                f"| `{difference.get('category', '')}` | `{difference.get('model', '')}` | "
                f"`{_canonical_json(detail)}` |"
            )
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, markdown_path


def read_report(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"parity report does not exist: {path}")
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"parity report is not valid JSON: {path}") from exc
    if not isinstance(report, dict) or report.get("version") != PARITY_VERSION:
        raise ValueError("unsupported or malformed parity report")
    if report.get("status") not in {"PASS", "FAIL", "BLOCKED"}:
        raise ValueError("parity report has an invalid status")
    return report
