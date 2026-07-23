"""Export a deterministic ClickHouse analytical candidate manifest."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

import clickhouse_connect

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.parity.export_postgres_oracle import (
    DEFAULT_CONTRACT,
    NULL_VALUE,
    ColumnType,
    aggregate_hash,
    canonical_value,
    load_contract,
    row_hash,
)

IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]*$")


def _unwrap_clickhouse_type(data_type: str) -> str:
    for prefix in ("Nullable(", "LowCardinality("):
        if data_type.startswith(prefix) and data_type.endswith(")"):
            return _unwrap_clickhouse_type(data_type[len(prefix) : -1])
    return data_type


def _semantic_type(column_name: str, data_type: str) -> ColumnType:
    normalized = _unwrap_clickhouse_type(data_type)
    if normalized in {"String", "FixedString"} or normalized.startswith("FixedString("):
        return ColumnType("string")
    if normalized in {"Bool", "Boolean"}:
        return ColumnType("boolean")
    if normalized.startswith(("Int", "UInt")):
        if column_name.startswith("is_"):
            return ColumnType("boolean")
        return ColumnType("integer")
    if normalized.startswith(("Float", "Decimal")):
        match = re.search(r"Decimal(?:32|64|128|256)?\(\d+,\s*(\d+)\)", normalized)
        return ColumnType("decimal", int(match.group(1)) if match else None)
    if normalized == "Date":
        return ColumnType("date")
    if normalized.startswith(("DateTime", "DateTime64")):
        return ColumnType("timestamp")
    if normalized.startswith(("Array(", "Tuple(", "Map(")):
        return ColumnType("structured")
    raise ValueError(f"no semantic type mapping for ClickHouse type {data_type!r}")


def _validate_identifier(value: str) -> str:
    if not IDENTIFIER.fullmatch(value):
        raise ValueError(f"unsafe SQL identifier: {value!r}")
    return value


class ClickHouseManifestConnection:
    def __init__(self, client: Any) -> None:
        self.client = client

    def columns(self, schema: str, name: str) -> dict[str, ColumnType]:
        schema = _validate_identifier(schema)
        name = _validate_identifier(name)
        result = self.client.query(
            """
            select name, type
            from system.columns
            where database = {database:String} and table = {table:String}
            order by position
            """,
            parameters={"database": schema, "table": name},
        )
        rows = result.result_rows
        if not rows:
            raise ValueError(f"relation not found or has no columns: {schema}.{name}")
        return {column: _semantic_type(column, data_type) for column, data_type in rows}

    def fetch_rows(
        self, schema: str, name: str, columns: list[str]
    ) -> list[dict[str, object]]:
        schema = _validate_identifier(schema)
        name = _validate_identifier(name)
        for column in columns:
            _validate_identifier(column)
        selected = ", ".join(f"`{column}`" for column in columns)
        result = self.client.query(f"select {selected} from `{schema}`.`{name}`")
        return [dict(zip(columns, row, strict=True)) for row in result.result_rows]


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _business_version_sort_key(value: object) -> tuple[int, str]:
    return (0, "") if value == NULL_VALUE else (1, _canonical_json(value))


def _relation_metrics(
    rows: list[dict[str, object]],
    column_types: dict[str, ColumnType],
    spec: dict[str, Any],
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


def relation_manifest(
    connection: ClickHouseManifestConnection, spec: dict[str, Any]
) -> dict[str, object]:
    schema = spec["schema"]
    name = spec["name"]
    grain = list(spec["grain"])
    excluded = set(spec.get("exclude_columns", []))
    all_types = connection.columns(schema, name)
    missing = sorted(set(grain) - set(all_types))
    if missing:
        raise ValueError(f"{schema}.{name} grain columns not found: {missing}")
    column_types = {
        column: column_type
        for column, column_type in all_types.items()
        if column not in excluded
    }
    rows = connection.fetch_rows(schema, name, list(column_types))
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


def export_manifest(
    connection: ClickHouseManifestConnection, contract: dict[str, Any]
) -> dict[str, object]:
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
    parser.add_argument("--host", default=os.getenv("CLICKHOUSE_HOST", "localhost"))
    parser.add_argument(
        "--port", type=int, default=int(os.getenv("CLICKHOUSE_PORT", "8123"))
    )
    parser.add_argument("--user", default=os.getenv("CLICKHOUSE_USER", "olist"))
    parser.add_argument("--password", default=os.getenv("CLICKHOUSE_PASSWORD", "olist"))
    parser.add_argument("--password-file")
    parser.add_argument(
        "--secure",
        action="store_true",
        default=os.getenv("CLICKHOUSE_SECURE", "false").lower() == "true",
    )
    args = parser.parse_args()
    contract = load_contract(args.contract)
    client = clickhouse_connect.get_client(
        host=args.host,
        port=args.port,
        username=args.user,
        password=_password(args),
        secure=args.secure,
    )
    try:
        manifest = export_manifest(ClickHouseManifestConnection(client), contract)
    finally:
        client.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
