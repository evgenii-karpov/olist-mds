"""Export frozen legacy baseline oracle and provenance metadata for Stage F0."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import clickhouse_connect
import psycopg2

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.parity.canonical_manifest import (
    NULL_VALUE,
    ColumnType,
    aggregate_hash,
    canonical_value,
    load_contract,
    row_hash,
)

DEFAULT_CONTRACT = ROOT / "scripts/parity/final_parity_contract.json"
IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]*$")


def _validate_identifier(value: str) -> str:
    if not IDENTIFIER.fullmatch(value):
        raise ValueError(f"unsafe SQL identifier: {value!r}")
    return value


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _postgres_semantic_type(data_type: str, scale: int | None) -> ColumnType:
    dt = data_type.lower()
    if dt in {"character varying", "varchar", "text", "character", "char", "uuid"}:
        return ColumnType("string")
    if dt in {"boolean", "bool"}:
        return ColumnType("boolean")
    if dt in {"integer", "bigint", "smallint"}:
        return ColumnType("integer")
    if dt in {"numeric", "decimal", "double precision", "real"}:
        return ColumnType("decimal", scale if scale is not None else 2)
    if dt == "date":
        return ColumnType("date")
    if dt.startswith("timestamp"):
        return ColumnType("timestamp")
    if dt in {"json", "jsonb"}:
        return ColumnType("structured")
    return ColumnType("string")


def _clickhouse_unwrap(data_type: str) -> str:
    for prefix in ("Nullable(", "LowCardinality("):
        if data_type.startswith(prefix) and data_type.endswith(")"):
            return _clickhouse_unwrap(data_type[len(prefix) : -1])
    return data_type


def _clickhouse_semantic_type(column_name: str, data_type: str) -> ColumnType:
    normalized = _clickhouse_unwrap(data_type)
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
        return ColumnType("decimal", int(match.group(1)) if match else 2)
    if normalized == "Date":
        return ColumnType("date")
    if normalized.startswith(("DateTime", "DateTime64")):
        return ColumnType("timestamp")
    if normalized.startswith(("Array(", "Tuple(", "Map(")):
        return ColumnType("structured")
    return ColumnType("string")


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
        if column not in column_types:
            continue
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
        if column in column_types
    }
    return {
        "null_counts": {
            column: sum(row[column] is None for row in rows)
            for column in sorted(column_types)
        },
        "temporal_bounds": temporal_bounds,
        "measure_totals": measures,
        "distinct_counts": distinct_counts,
    }


def fetch_postgres_relation(pg_conn: Any, spec: dict[str, Any]) -> dict[str, object]:
    schema = spec["schema"]
    name = spec["name"]
    grain = list(spec["grain"])
    excluded = set(spec.get("exclude_columns", []))

    with pg_conn.cursor() as cursor:
        cursor.execute(
            """
            select column_name, data_type, numeric_scale
            from information_schema.columns
            where table_schema = %s and table_name = %s
            order by ordinal_position
            """,
            (schema, name),
        )
        col_rows = cursor.fetchall()
        if not col_rows:
            raise ValueError(f"PostgreSQL relation not found: {schema}.{name}")
        all_types = {col: _postgres_semantic_type(dt, sc) for col, dt, sc in col_rows}

        missing = sorted(set(grain) - set(all_types))
        if missing:
            raise ValueError(
                f"PostgreSQL relation {schema}.{name} missing grain columns: {missing}"
            )

        column_types = {
            col: ctype for col, ctype in all_types.items() if col not in excluded
        }

        cols_str = ", ".join(f'"{c}"' for c in column_types)
        cursor.execute(f'select {cols_str} from "{schema}"."{name}"')
        raw_rows = [
            dict(zip(column_types.keys(), r, strict=True)) for r in cursor.fetchall()
        ]

    canonical_grains = [
        [canonical_value(r[col], column_types[col]) for col in grain] for r in raw_rows
    ]
    grain_strings = [_canonical_json(val) for val in canonical_grains]
    hashes = [row_hash(r, column_types) for r in raw_rows]
    paired = sorted(zip(grain_strings, canonical_grains, hashes, strict=True))
    duplicate_count = len(grain_strings) - len(set(grain_strings))

    return {
        "name": f"{schema}.{name}",
        "grain": grain,
        "semantic_columns": {
            col: {
                "type": ctype.semantic_type,
                **({"scale": ctype.scale} if ctype.scale is not None else {}),
            }
            for col, ctype in sorted(column_types.items())
        },
        "row_count": len(raw_rows),
        "duplicate_grain_count": duplicate_count,
        "grain_keys": [item[1] for item in paired],
        "rows": [{"grain": item[1], "hash": item[2]} for item in paired],
        "aggregate_hash": aggregate_hash(hashes),
        "metrics": _relation_metrics(raw_rows, column_types, spec),
    }


def fetch_clickhouse_relation(
    ch_client: Any, spec: dict[str, Any]
) -> dict[str, object]:
    schema = spec["schema"]
    name = spec["name"]
    grain = list(spec["grain"])
    excluded = set(spec.get("exclude_columns", []))

    ch_db = schema
    ch_table = name

    res = ch_client.query(
        """
        select name, type
        from system.columns
        where database = {db:String} and table = {tbl:String}
        order by position
        """,
        parameters={"db": ch_db, "tbl": ch_table},
    )
    if not res.result_rows:
        raise ValueError(f"ClickHouse table not found: {ch_db}.{ch_table}")

    all_types = {r[0]: _clickhouse_semantic_type(r[0], r[1]) for r in res.result_rows}
    missing = sorted(set(grain) - set(all_types))
    if missing:
        raise ValueError(
            f"ClickHouse relation {ch_db}.{ch_table} missing grain: {missing}"
        )

    column_types = {
        col: ctype for col, ctype in all_types.items() if col not in excluded
    }
    cols_str = ", ".join(f"`{c}`" for c in column_types)
    raw_res = ch_client.query(f"select {cols_str} from `{ch_db}`.`{ch_table}`")
    raw_rows = [
        dict(zip(column_types.keys(), r, strict=True)) for r in raw_res.result_rows
    ]

    canonical_grains = [
        [canonical_value(r[col], column_types[col]) for col in grain] for r in raw_rows
    ]
    grain_strings = [_canonical_json(val) for val in canonical_grains]
    hashes = [row_hash(r, column_types) for r in raw_rows]
    paired = sorted(zip(grain_strings, canonical_grains, hashes, strict=True))
    duplicate_count = len(grain_strings) - len(set(grain_strings))

    return {
        "name": f"{schema}.{name}",
        "grain": grain,
        "semantic_columns": {
            col: {
                "type": ctype.semantic_type,
                **({"scale": ctype.scale} if ctype.scale is not None else {}),
            }
            for col, ctype in sorted(column_types.items())
        },
        "row_count": len(raw_rows),
        "duplicate_grain_count": duplicate_count,
        "grain_keys": [item[1] for item in paired],
        "rows": [{"grain": item[1], "hash": item[2]} for item in paired],
        "aggregate_hash": aggregate_hash(hashes),
        "metrics": _relation_metrics(raw_rows, column_types, spec),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export F0 legacy baseline oracle and metadata."
    )
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--oracle-output", type=Path, required=True)
    parser.add_argument("--metadata-output", type=Path, required=True)
    parser.add_argument(
        "--baseline-sha", default="1400d08345ad81a0121f0ee85ee9ae81cd575a73"
    )
    parser.add_argument(
        "--fixture-path", default="tests/fixtures/olist_small/olist_small.zip"
    )
    parser.add_argument(
        "--fixture-sha256",
        default="5cf2ff7a104cae75d8a56cf8c6e00959894154a8d55aed2ddf0e3fa133a13976",
    )
    parser.add_argument("--pg-host", default=os.getenv("POSTGRES_HOST", "localhost"))
    parser.add_argument(
        "--pg-port", type=int, default=int(os.getenv("POSTGRES_PORT", "5433"))
    )
    parser.add_argument("--pg-db", default=os.getenv("POSTGRES_DB", "olist_oltp"))
    parser.add_argument("--pg-user", default=os.getenv("POSTGRES_USER", "olist_admin"))
    parser.add_argument(
        "--pg-password", default=os.getenv("POSTGRES_PASSWORD", "olist_password")
    )
    parser.add_argument("--ch-host", default=os.getenv("CLICKHOUSE_HOST", "localhost"))
    parser.add_argument(
        "--ch-port", type=int, default=int(os.getenv("CLICKHOUSE_PORT", "8123"))
    )
    parser.add_argument("--ch-user", default=os.getenv("CLICKHOUSE_USER", "olist"))
    parser.add_argument(
        "--ch-password", default=os.getenv("CLICKHOUSE_PASSWORD", "olist")
    )
    args = parser.parse_args()

    started_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    contract = load_contract(args.contract)

    pg_conn = psycopg2.connect(
        host=args.pg_host,
        port=args.pg_port,
        dbname=args.pg_db,
        user=args.pg_user,
        password=args.pg_password,
    )
    ch_client = clickhouse_connect.get_client(
        host=args.ch_host,
        port=args.ch_port,
        username=args.ch_user,
        password=args.ch_password,
    )

    relations_manifest = []
    try:
        for rel_spec in contract["relations"]:
            schema = rel_spec["schema"]
            if schema == "public":
                rel = fetch_postgres_relation(pg_conn, rel_spec)
            else:
                rel = fetch_clickhouse_relation(ch_client, rel_spec)
            relations_manifest.append(rel)
    finally:
        pg_conn.close()
        ch_client.close()

    oracle_payload = {
        "format_version": 1,
        "canonicalization": {
            "hash": "sha256",
            "null": NULL_VALUE,
            "timestamp": "UTC with six fractional digits",
            "row_order": "declared grain",
        },
        "dataset": contract["dataset"],
        "relations": relations_manifest,
    }

    oracle_bytes = (
        json.dumps(oracle_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    oracle_sha256 = hashlib.sha256(oracle_bytes).hexdigest()

    finished_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    metadata_payload = {
        "format_version": 1,
        "baseline_commit": args.baseline_sha,
        "fixture_path": args.fixture_path,
        "fixture_sha256": args.fixture_sha256,
        "oracle_sha256": oracle_sha256,
        "canonicalization_version": 1,
        "started_at": started_at,
        "finished_at": finished_at,
        "status": "PASS",
        "relation_summary": [
            {
                "name": rel["name"],
                "grain": rel["grain"],
                "row_count": rel["row_count"],
                "duplicate_grain_count": rel["duplicate_grain_count"],
                "aggregate_hash": rel["aggregate_hash"],
            }
            for rel in relations_manifest
        ],
    }

    args.oracle_output.parent.mkdir(parents=True, exist_ok=True)
    args.oracle_output.write_bytes(oracle_bytes)

    args.metadata_output.parent.mkdir(parents=True, exist_ok=True)
    args.metadata_output.write_text(
        json.dumps(metadata_payload, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    print(f"Exported oracle to {args.oracle_output} (SHA-256: {oracle_sha256})")
    print(f"Exported metadata to {args.metadata_output}")


if __name__ == "__main__":
    main()
