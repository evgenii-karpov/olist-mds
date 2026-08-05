"""Canonical manifest helpers shared by warehouse-specific exporters."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACT = ROOT / "scripts/parity/canonical_batch_relations.json"
NULL_VALUE = {"$null": True}
IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]*$")


@dataclass(frozen=True)
class ColumnType:
    semantic_type: str
    scale: int | None = None


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_value(value: object, column_type: ColumnType) -> object:
    if value is None:
        return NULL_VALUE
    semantic_type = column_type.semantic_type
    if semantic_type == "string":
        if isinstance(value, (bytes, bytearray, memoryview)):
            return bytes(value).decode("utf-8")
        return str(value)
    if semantic_type == "boolean":
        return bool(value)
    if semantic_type == "integer":
        return str(value)
    if semantic_type == "decimal":
        scale = column_type.scale
        decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
        if scale is None:
            return format(decimal_value, "f")
        quantum = Decimal(1).scaleb(-scale)
        return format(decimal_value.quantize(quantum), f".{scale}f")
    if semantic_type == "date":
        if isinstance(value, datetime):
            value = value.date()
        if not isinstance(value, date):
            raise TypeError(f"expected date, got {type(value).__name__}")
        return value.isoformat()
    if semantic_type == "timestamp":
        if not isinstance(value, datetime):
            raise TypeError(f"expected datetime, got {type(value).__name__}")
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    if semantic_type == "structured":
        if isinstance(value, str):
            value = json.loads(value)
        return json.loads(_canonical_json(value))
    raise ValueError(f"unsupported semantic type: {semantic_type}")


def canonical_row(
    row: Mapping[str, object], column_types: Mapping[str, ColumnType]
) -> dict[str, object]:
    return {
        name: canonical_value(row[name], column_types[name])
        for name in sorted(column_types)
    }


def row_hash(row: Mapping[str, object], column_types: Mapping[str, ColumnType]) -> str:
    payload = _canonical_json(canonical_row(row, column_types)).encode()
    return hashlib.sha256(payload).hexdigest()


def aggregate_hash(hashes: Sequence[str]) -> str:
    return hashlib.sha256("\n".join(sorted(hashes)).encode()).hexdigest()


def validate_identifier(value: str) -> str:
    if not IDENTIFIER.fullmatch(value):
        raise ValueError(f"unsafe SQL identifier: {value!r}")
    return value


def load_contract(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("format_version") != 1:
        raise ValueError("contract format_version must be 1")
    relations = payload.get("relations")
    if not isinstance(relations, list) or not relations:
        raise ValueError("contract must declare at least one relation")
    seen: set[str] = set()
    for relation in relations:
        schema = validate_identifier(relation["schema"])
        name = validate_identifier(relation["name"])
        qualified = f"{schema}.{name}"
        if qualified in seen:
            raise ValueError(f"duplicate relation: {qualified}")
        seen.add(qualified)
        grain = relation.get("grain")
        if not isinstance(grain, list) or not grain:
            raise ValueError(f"relation {qualified} must declare a grain")
        for column in [*grain, *relation.get("exclude_columns", [])]:
            validate_identifier(column)
        candidate = relation.get("candidate")
        if candidate is not None:
            if not isinstance(candidate, dict):
                raise ValueError(f"relation {qualified} candidate must be an object")
            candidate_schema = validate_identifier(candidate["schema"])
            candidate_name = validate_identifier(candidate["name"])
            candidate_columns = candidate.get("columns")
            if not isinstance(candidate_columns, list) or not candidate_columns:
                raise ValueError(f"relation {qualified} candidate must declare columns")
            seen_candidate_columns: set[str] = set()
            for column in candidate_columns:
                validate_identifier(column)
                if column in seen_candidate_columns:
                    raise ValueError(
                        f"relation {qualified} candidate has duplicate column: {column}"
                    )
                seen_candidate_columns.add(column)
            if candidate_schema == schema and candidate_name == name:
                raise ValueError(
                    f"relation {qualified} candidate must identify a separate source"
                )
    return payload
