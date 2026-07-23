"""Export a deterministic, compact PostgreSQL analytical oracle manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2 import sql

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACT = ROOT / "scripts/parity/postgres_oracle_relations.json"
NULL_VALUE = {"$null": True}
IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]*$")


@dataclass(frozen=True)
class ColumnType:
    semantic_type: str
    scale: int | None = None


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_value(value: object, column_type: ColumnType) -> object:
    """Normalize a database value without collapsing null and empty string."""
    if value is None:
        return NULL_VALUE
    semantic_type = column_type.semantic_type
    if semantic_type == "string":
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


def _business_version_sort_key(value: object) -> tuple[int, str]:
    return (0, "") if value == NULL_VALUE else (1, _canonical_json(value))


def _semantic_type(data_type: str, scale: int | None) -> ColumnType:
    if data_type in {"character", "character varying", "text", "uuid"}:
        return ColumnType("string")
    if data_type == "boolean":
        return ColumnType("boolean")
    if data_type in {"smallint", "integer", "bigint"}:
        return ColumnType("integer")
    if data_type in {"numeric", "decimal", "real", "double precision"}:
        return ColumnType("decimal", scale)
    if data_type == "date":
        return ColumnType("date")
    if data_type in {
        "timestamp without time zone",
        "timestamp with time zone",
    }:
        return ColumnType("timestamp")
    if data_type in {"ARRAY", "json", "jsonb"}:
        return ColumnType("structured")
    raise ValueError(f"no semantic type mapping for PostgreSQL type {data_type!r}")


def _validate_identifier(value: str) -> str:
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
        schema = _validate_identifier(relation["schema"])
        name = _validate_identifier(relation["name"])
        qualified = f"{schema}.{name}"
        if qualified in seen:
            raise ValueError(f"duplicate relation: {qualified}")
        seen.add(qualified)
        grain = relation.get("grain")
        if not isinstance(grain, list) or not grain:
            raise ValueError(f"relation {qualified} must declare a grain")
        for column in [*grain, *relation.get("exclude_columns", [])]:
            _validate_identifier(column)
    return payload


def _columns(connection: Any, schema: str, name: str) -> dict[str, ColumnType]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select column_name, data_type, numeric_scale
            from information_schema.columns
            where table_schema = %s and table_name = %s
            order by ordinal_position
            """,
            (schema, name),
        )
        rows = cursor.fetchall()
    if not rows:
        raise ValueError(f"relation not found or has no columns: {schema}.{name}")
    return {
        column: _semantic_type(data_type, scale) for column, data_type, scale in rows
    }


def _fetch_rows(
    connection: Any, schema: str, name: str, columns: Sequence[str]
) -> list[dict[str, object]]:
    query = sql.SQL("select {} from {}.{}").format(
        sql.SQL(", ").join(sql.Identifier(column) for column in columns),
        sql.Identifier(schema),
        sql.Identifier(name),
    )
    with connection.cursor() as cursor:
        cursor.execute(query)
        return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]


def _relation_metrics(
    rows: Sequence[Mapping[str, object]],
    column_types: Mapping[str, ColumnType],
    spec: Mapping[str, Any],
) -> dict[str, object]:
    temporal_bounds: dict[str, object] = {}
    for column, column_type in column_types.items():
        if column_type.semantic_type not in {"date", "timestamp"}:
            continue
        values = [row[column] for row in rows if row[column] is not None]
        ordered_values = sorted(
            values,
            key=lambda item: _canonical_json(canonical_value(item, column_type)),
        )
        temporal_bounds[column] = {
            "min": canonical_value(ordered_values[0], column_type)
            if ordered_values
            else NULL_VALUE,
            "max": canonical_value(ordered_values[-1], column_type)
            if ordered_values
            else NULL_VALUE,
        }
    measures: dict[str, object] = {}
    for column in spec.get("measures", []):
        column_type = column_types[column]
        total = sum(
            (Decimal(str(row[column])) for row in rows if row[column] is not None),
            Decimal(0),
        )
        measures[column] = canonical_value(total, column_type)
    distinct_counts = {
        column: len(
            {
                _canonical_json(canonical_value(row[column], column_types[column]))
                for row in rows
                if row[column] is not None
            }
        )
        for column in spec.get("distinct_counts", [])
    }
    metrics: dict[str, object] = {
        "null_counts": {
            column: sum(row[column] is None for row in rows)
            for column in sorted(column_types)
        },
        "temporal_bounds": temporal_bounds,
        "measure_totals": measures,
        "distinct_counts": distinct_counts,
    }
    snapshot = spec.get("snapshot")
    if snapshot:
        business_key = snapshot["business_key"]
        version_column = snapshot["version_column"]
        versions: dict[str, int] = {}
        business_versions: dict[str, list[object]] = {}
        for row in rows:
            key = canonical_value(row[business_key], column_types[business_key])
            key_json = _canonical_json(key)
            versions[key_json] = versions.get(key_json, 0) + 1
            business_versions.setdefault(key_json, []).append(
                canonical_value(row[version_column], column_types[version_column])
            )
        metrics["snapshot"] = {
            "business_key": business_key,
            "version_column": version_column,
            "version_counts": [
                {"key": json.loads(key), "versions": versions[key]}
                for key in sorted(versions)
            ],
            "current_versions": [
                {
                    "key": json.loads(key),
                    "version": sorted(
                        business_versions[key], key=_business_version_sort_key
                    )[-1],
                }
                for key in sorted(business_versions)
            ],
        }
    return metrics


def relation_manifest(connection: Any, spec: Mapping[str, Any]) -> dict[str, object]:
    schema = spec["schema"]
    name = spec["name"]
    grain = list(spec["grain"])
    excluded = set(spec.get("exclude_columns", []))
    all_types = _columns(connection, schema, name)
    missing = sorted(set(grain) - set(all_types))
    if missing:
        raise ValueError(f"{schema}.{name} grain columns not found: {missing}")
    column_types = {
        column: column_type
        for column, column_type in all_types.items()
        if column not in excluded
    }
    rows = _fetch_rows(connection, schema, name, list(column_types))
    canonical_grains = [
        [canonical_value(row[column], all_types[column]) for column in grain]
        for row in rows
    ]
    grain_strings = [_canonical_json(value) for value in canonical_grains]
    hashes = [row_hash(row, column_types) for row in rows]
    paired = sorted(zip(grain_strings, canonical_grains, hashes, strict=True))
    duplicate_count = len(grain_strings) - len(set(grain_strings))
    return {
        "name": f"{schema}.{name}",
        "grain": grain,
        "semantic_columns": {
            column: {
                "type": column_type.semantic_type,
                **(
                    {"scale": column_type.scale}
                    if column_type.scale is not None
                    else {}
                ),
            }
            for column, column_type in sorted(column_types.items())
        },
        "row_count": len(rows),
        "duplicate_grain_count": duplicate_count,
        "grain_keys": [item[1] for item in paired],
        "rows": [{"grain": item[1], "hash": item[2]} for item in paired],
        "aggregate_hash": aggregate_hash(hashes),
        "metrics": _relation_metrics(rows, column_types, spec),
    }


def export_manifest(connection: Any, contract: Mapping[str, Any]) -> dict[str, object]:
    return {
        "format_version": 1,
        "canonicalization": {
            "hash": "sha256",
            "null": NULL_VALUE,
            "timestamp": "UTC with six fractional digits",
            "row_order": "declared grain",
        },
        "dataset": contract["dataset"],
        "relations": [
            relation_manifest(connection, relation)
            for relation in contract["relations"]
        ],
    }


def _password(args: argparse.Namespace) -> str:
    if args.password_file:
        return Path(args.password_file).read_text(encoding="utf-8").strip()
    return args.password


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--host", default=os.getenv("POSTGRES_HOST", "localhost"))
    parser.add_argument(
        "--port", type=int, default=int(os.getenv("POSTGRES_PORT", "5432"))
    )
    parser.add_argument(
        "--database", default=os.getenv("POSTGRES_DB", "olist_analytics")
    )
    parser.add_argument("--user", default=os.getenv("POSTGRES_USER", "olist"))
    parser.add_argument("--password", default=os.getenv("POSTGRES_PASSWORD", "olist"))
    parser.add_argument("--password-file")
    args = parser.parse_args()
    contract = load_contract(args.contract)
    connection = psycopg2.connect(
        host=args.host,
        port=args.port,
        dbname=args.database,
        user=args.user,
        password=_password(args),
    )
    try:
        manifest = export_manifest(connection, contract)
    finally:
        connection.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
