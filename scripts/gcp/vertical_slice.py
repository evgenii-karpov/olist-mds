"""Deterministic BigLake/BigQuery vertical-slice probe matrix.

The module deliberately separates the cloud-independent contract from cloud
execution. It can generate and validate the exact direct P.C.N.T and bridge
queries before credentials or a GCP project are available. A later operator
run can execute the generated SQL after Spark has populated the four required
tables.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from streaming.spark.platform.table_specs import TABLES_BY_NAME, TableSpec

DEFAULT_BRIDGE_DATASET = "olist_lakehouse_bridge"
VERTICAL_SLICE_VERSION = "wp5-v1"
_IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
_PROJECT_ID = re.compile(r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$")


@dataclass(frozen=True)
class SliceDefinition:
    """One required source table and the fields needed by the probe matrix."""

    source_name: str
    probe_columns: tuple[str, ...]

    @property
    def bridge_view(self) -> str:
        namespace, table = self.source_name.split(".", 1)
        return f"{namespace}_{table}"


SLICE_DEFINITIONS = (
    SliceDefinition(
        "bronze.mysql_cdc_records",
        ("kafka_timestamp", "key_bytes", "headers"),
    ),
    SliceDefinition(
        "silver.order_items_changes",
        ("source_ts", "price", "freight_value"),
    ),
    SliceDefinition(
        "reference.geolocation",
        ("geolocation_lat", "geolocation_lng"),
    ),
    SliceDefinition(
        "audit.silver_progress",
        ("last_source_ts", "last_kafka_offset"),
    ),
)


def _validate_identifier(value: str, label: str) -> str:
    if not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"{label} contains an unsafe identifier")
    return value


def _validate_project_id(value: str) -> str:
    if not _PROJECT_ID.fullmatch(value):
        raise ValueError("project_id is not a valid GCP project ID")
    return value


def _quoted_relation(*parts: str) -> str:
    return "`" + ".".join(parts) + "`"


def _bigquery_type(sql_type: str) -> str:
    """Map repository Iceberg types to the documented BigQuery type surface."""

    direct = {
        "STRING": "STRING",
        "INT": "INT64",
        "BIGINT": "INT64",
        "BOOLEAN": "BOOL",
        "TIMESTAMP_LTZ": "TIMESTAMP",
        "TIMESTAMP_NTZ": "DATETIME",
        "BINARY": "BYTES",
        "ARRAY<STRING>": "ARRAY<STRING>",
        "ARRAY<STRUCT<key: STRING, value: BINARY>>": (
            "ARRAY<STRUCT<key STRING, value BYTES>>"
        ),
    }
    if sql_type in direct:
        return direct[sql_type]
    decimal = re.fullmatch(r"DECIMAL\((\d+),(\d+)\)", sql_type)
    if decimal:
        scale = int(decimal.group(2))
        return "BIGNUMERIC" if scale > 9 else "NUMERIC"
    raise ValueError(f"no BigQuery mapping is registered for Iceberg type {sql_type}")


def _type_expectations(
    table: TableSpec, columns: tuple[str, ...]
) -> list[dict[str, str]]:
    by_name = {column.name: column for column in table.columns}
    missing = sorted(set(columns) - set(by_name))
    if missing:
        raise ValueError(
            f"vertical-slice columns are absent from {table.namespace}.{table.name}: "
            + ", ".join(missing)
        )
    return [
        {
            "column": column_name,
            "iceberg_type": by_name[column_name].sql_type,
            "bigquery_type": _bigquery_type(by_name[column_name].sql_type),
        }
        for column_name in columns
    ]


def _typeof_sql(identifier: str, columns: tuple[str, ...]) -> str:
    expressions = ",\n  ".join(
        f"TYPEOF(`{column}`) AS `{column}__typeof`" for column in columns
    )
    return f"SELECT\n  {expressions}\nFROM {identifier}\nLIMIT 1"


def _duplicate_retry_sql(identifier: str, table: TableSpec) -> str:
    if table.namespace in {"bronze", "silver"}:
        expressions = (
            "COUNT(*) AS row_count",
            "COUNT(DISTINCT `event_id`) AS distinct_event_count",
        )
    elif table.namespace == "reference":
        expressions = (
            "COUNT(*) AS row_count",
            "COUNT(DISTINCT `geolocation_id`) AS distinct_key_count",
        )
    else:
        expressions = (
            "COUNT(*) AS row_count",
            "COUNT(DISTINCT CONCAT(`query_name`, '/', `entity`, '/', "
            "CAST(`spark_batch_id` AS STRING))) AS distinct_progress_count",
        )
    return "SELECT " + ", ".join(expressions) + f"\nFROM {identifier}"


def build_probe_plan(
    project_id: str,
    catalog_id: str,
    bridge_dataset: str = DEFAULT_BRIDGE_DATASET,
) -> dict[str, Any]:
    """Build the cloud execution plan without contacting Google Cloud."""

    project = _validate_project_id(project_id)
    catalog = _validate_identifier(catalog_id, "catalog_id")
    bridge = _validate_identifier(bridge_dataset, "bridge_dataset")
    tables: list[dict[str, Any]] = []

    for definition in SLICE_DEFINITIONS:
        table = TABLES_BY_NAME[definition.source_name]
        namespace, name = definition.source_name.split(".", 1)
        direct_identifier = _quoted_relation(project, catalog, namespace, name)
        bridge_identifier = _quoted_relation(project, bridge, definition.bridge_view)
        tables.append(
            {
                "source": definition.source_name,
                "direct_identifier": direct_identifier,
                "bridge_identifier": bridge_identifier,
                "bridge_view": definition.bridge_view,
                "type_expectations": _type_expectations(
                    table, definition.probe_columns
                ),
                "direct_read_sql": f"SELECT * FROM {direct_identifier} LIMIT 10",
                "bridge_read_sql": f"SELECT * FROM {bridge_identifier} LIMIT 10",
                "direct_schema_sql": f"SELECT * FROM {direct_identifier} LIMIT 0",
                "bridge_schema_sql": f"SELECT * FROM {bridge_identifier} LIMIT 0",
                "direct_type_sql": _typeof_sql(
                    direct_identifier, definition.probe_columns
                ),
                "bridge_type_sql": _typeof_sql(
                    bridge_identifier, definition.probe_columns
                ),
                "duplicate_retry_sql": _duplicate_retry_sql(direct_identifier, table),
            }
        )

    return {
        "version": VERTICAL_SLICE_VERSION,
        "project_id": project,
        "catalog_id": catalog,
        "bridge_dataset": bridge,
        "tables": tables,
        "runtime_checks": [
            "load all four tables with the final GCP Spark image and Spark ADC",
            "restart streaming from the GCS checkpoint and prove the query resumes",
            "rerun the same input/retry and prove no duplicate business rows",
            "query direct P.C.N.T and bridge relations while Spark commits",
            "record UTC timestamp, decimal, binary, nested-field and schema results",
            "record query latency, bytes processed/billed and metadata.json size",
        ],
        "decision_values": ["GO", "GO-WITH-CONSTRAINTS", "NO-GO"],
        "cloud_execution": "PENDING_GCP_ACCESS",
    }


def validate_probe_plan(plan: dict[str, Any]) -> list[str]:
    """Return deterministic contract violations for a generated plan."""

    errors: list[str] = []
    if plan.get("version") != VERTICAL_SLICE_VERSION:
        errors.append("unexpected vertical-slice plan version")
    sources = [table.get("source") for table in plan.get("tables", [])]
    expected = [definition.source_name for definition in SLICE_DEFINITIONS]
    if sources != expected:
        errors.append(f"required table order mismatch: expected {expected!r}")
    for table in plan.get("tables", []):
        for key in (
            "direct_read_sql",
            "bridge_read_sql",
            "direct_schema_sql",
            "bridge_schema_sql",
            "direct_type_sql",
            "bridge_type_sql",
        ):
            query = table.get(key, "")
            if ".snapshots" in query or ".files" in query:
                errors.append(f"{key} must not query Iceberg metadata tables")
    return errors


def write_probe_plan(path: Path, plan: dict[str, Any]) -> None:
    """Persist a reproducible plan for an operator or a future cloud runner."""

    errors = validate_probe_plan(plan)
    if errors:
        raise ValueError("invalid vertical-slice plan: " + "; ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
