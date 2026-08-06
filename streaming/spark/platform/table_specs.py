"""Exact Iceberg namespace, schema, partition, and property contracts."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

CATALOG_ALIAS = "lakehouse"
NAMESPACES = ("bronze", "silver", "reference", "audit")
ENTITIES = (
    "customers",
    "orders",
    "order_items",
    "order_payments",
    "order_reviews",
    "products",
    "sellers",
    "product_category_translation",
)

TABLE_PROPERTIES: tuple[tuple[str, str], ...] = (
    ("format-version", "2"),
    ("write.format.default", "parquet"),
    ("write.parquet.compression-codec", "zstd"),
    ("write.target-file-size-bytes", "134217728"),
    ("write.metadata.delete-after-commit.enabled", "true"),
    ("write.metadata.previous-versions-max", "20"),
)

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    sql_type: str
    required: bool = False

    def __post_init__(self) -> None:
        if not _IDENTIFIER.fullmatch(self.name):
            raise ValueError(f"unsafe Iceberg column name: {self.name}")
        if not self.sql_type or any(value in self.sql_type for value in (";", "--")):
            raise ValueError(f"unsafe Iceberg type for {self.name}")

    def nullable_copy(self) -> ColumnSpec:
        return ColumnSpec(self.name, self.sql_type, required=False)


@dataclass(frozen=True)
class TableSpec:
    namespace: str
    name: str
    columns: tuple[ColumnSpec, ...]
    partition_transform: str | None = None
    properties: tuple[tuple[str, str], ...] = TABLE_PROPERTIES

    def __post_init__(self) -> None:
        if self.namespace not in NAMESPACES or not _IDENTIFIER.fullmatch(self.name):
            raise ValueError(
                f"unsafe Iceberg table identifier: {self.namespace}.{self.name}"
            )
        column_names = [column.name for column in self.columns]
        if len(column_names) != len(set(column_names)):
            raise ValueError(f"duplicate column in {self.namespace}.{self.name}")
        if self.partition_transform:
            match = re.fullmatch(r"days\(([a-z][a-z0-9_]*)\)", self.partition_transform)
            if not match or match.group(1) not in column_names:
                raise ValueError(
                    f"invalid partition transform for {self.namespace}.{self.name}"
                )
        if dict(self.properties) != dict(TABLE_PROPERTIES):
            raise ValueError(
                f"noncanonical properties for {self.namespace}.{self.name}"
            )

    @property
    def qualified_name(self) -> str:
        return f"{CATALOG_ALIAS}.{self.namespace}.{self.name}"

    def create_sql(self) -> str:
        columns = ",\n".join(
            f"  `{column.name}` {column.sql_type}"
            f"{' NOT NULL' if column.required else ''}"
            for column in self.columns
        )
        partition = ""
        if self.partition_transform:
            transform, column = self.partition_transform[:-1].split("(", 1)
            partition = f"\nPARTITIONED BY ({transform}(`{column}`))"
        properties = ",\n".join(
            f"  '{name}' = '{value}'" for name, value in self.properties
        )
        return (
            f"CREATE TABLE IF NOT EXISTS `{CATALOG_ALIAS}`.`{self.namespace}`.`{self.name}` (\n"
            f"{columns}\n"
            ")\n"
            "USING iceberg"
            f"{partition}\n"
            "TBLPROPERTIES (\n"
            f"{properties}\n"
            ")"
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "namespace": self.namespace,
            "name": self.name,
            "columns": [
                {
                    "name": column.name,
                    "type": column.sql_type,
                    "required": column.required,
                }
                for column in self.columns
            ],
            "partition_transform": self.partition_transform,
            "properties": dict(self.properties),
        }


def _columns(*definitions: tuple[str, str, bool]) -> tuple[ColumnSpec, ...]:
    return tuple(
        ColumnSpec(name, sql_type, required) for name, sql_type, required in definitions
    )


BUSINESS_SCHEMAS: Mapping[str, tuple[ColumnSpec, ...]] = {
    "customers": _columns(
        ("customer_id", "STRING", True),
        ("customer_unique_id", "STRING", True),
        ("customer_zip_code_prefix", "STRING", True),
        ("customer_city", "STRING", True),
        ("customer_state", "STRING", True),
    ),
    "orders": _columns(
        ("order_id", "STRING", True),
        ("customer_id", "STRING", True),
        ("order_status", "STRING", True),
        ("order_purchase_timestamp", "TIMESTAMP_LTZ", True),
        ("order_approved_at", "TIMESTAMP_LTZ", False),
        ("order_delivered_carrier_date", "TIMESTAMP_LTZ", False),
        ("order_delivered_customer_date", "TIMESTAMP_LTZ", False),
        ("order_estimated_delivery_date", "TIMESTAMP_LTZ", True),
    ),
    "order_items": _columns(
        ("order_id", "STRING", True),
        ("order_item_id", "INT", True),
        ("product_id", "STRING", True),
        ("seller_id", "STRING", True),
        ("shipping_limit_date", "TIMESTAMP_LTZ", True),
        ("price", "DECIMAL(18,2)", True),
        ("freight_value", "DECIMAL(18,2)", True),
    ),
    "order_payments": _columns(
        ("order_id", "STRING", True),
        ("payment_sequential", "INT", True),
        ("payment_type", "STRING", True),
        ("payment_installments", "INT", True),
        ("payment_value", "DECIMAL(18,2)", True),
    ),
    "order_reviews": _columns(
        ("review_id", "STRING", True),
        ("order_id", "STRING", True),
        ("review_score", "INT", True),
        ("review_comment_title", "STRING", False),
        ("review_comment_message", "STRING", False),
        ("review_creation_date", "TIMESTAMP_LTZ", True),
        ("review_answer_timestamp", "TIMESTAMP_LTZ", True),
    ),
    "products": _columns(
        ("product_id", "STRING", True),
        ("product_category_name", "STRING", False),
        ("product_name_lenght", "INT", False),
        ("product_description_lenght", "INT", False),
        ("product_photos_qty", "INT", False),
        ("product_weight_g", "INT", False),
        ("product_length_cm", "INT", False),
        ("product_height_cm", "INT", False),
        ("product_width_cm", "INT", False),
    ),
    "sellers": _columns(
        ("seller_id", "STRING", True),
        ("seller_zip_code_prefix", "STRING", True),
        ("seller_city", "STRING", True),
        ("seller_state", "STRING", True),
    ),
    "product_category_translation": _columns(
        ("product_category_name", "STRING", True),
        ("product_category_name_english", "STRING", True),
    ),
}


BRONZE_TABLES = (
    TableSpec(
        namespace="bronze",
        name="mysql_cdc_records",
        columns=_columns(
            ("event_id", "STRING", True),
            ("record_kind", "STRING", True),
            ("topic", "STRING", True),
            ("partition", "INT", True),
            ("offset", "BIGINT", True),
            ("kafka_timestamp", "TIMESTAMP_LTZ", True),
            ("kafka_timestamp_type", "INT", True),
            ("headers", "ARRAY<STRUCT<key: STRING, value: BINARY>>", False),
            ("key_bytes", "BINARY", False),
            ("value_bytes", "BINARY", False),
            ("is_tombstone", "BOOLEAN", True),
            ("key_schema_id", "INT", False),
            ("value_schema_id", "INT", False),
            ("key_sha256", "STRING", False),
            ("value_sha256", "STRING", False),
            ("key_framing_valid", "BOOLEAN", True),
            ("value_framing_valid", "BOOLEAN", True),
            ("framing_error", "STRING", False),
            ("ingest_batch_id", "BIGINT", True),
            ("spark_query_id", "STRING", True),
            ("ingested_at", "TIMESTAMP_LTZ", True),
        ),
        partition_transform="days(ingested_at)",
    ),
    TableSpec(
        namespace="bronze",
        name="avro_schemas",
        columns=_columns(
            ("schema_id", "INT", True),
            ("fingerprint_sha256", "STRING", True),
            ("subject", "STRING", True),
            ("registry_version", "INT", True),
            ("schema_json", "STRING", True),
            ("references_json", "STRING", True),
            ("spark_self_contained_schema_json", "STRING", True),
            ("first_seen_at", "TIMESTAMP_LTZ", True),
            ("last_verified_at", "TIMESTAMP_LTZ", True),
        ),
    ),
)


_CHANGES_PREFIX = _columns(
    ("event_id", "STRING", True),
    ("op", "STRING", True),
    ("is_snapshot", "BOOLEAN", True),
    ("is_deleted", "BOOLEAN", True),
    ("apply_status", "STRING", True),
    ("error_code", "STRING", False),
    ("error_message", "STRING", False),
)

_CHANGES_SUFFIX = _columns(
    ("source_ts", "TIMESTAMP_LTZ", True),
    ("source_server_id", "BIGINT", False),
    ("source_gtid", "STRING", False),
    ("source_binlog_file", "STRING", False),
    ("source_binlog_file_index", "INT", False),
    ("source_binlog_pos", "BIGINT", False),
    ("source_row", "INT", False),
    ("transaction_id", "STRING", False),
    ("transaction_total_order", "BIGINT", False),
    ("transaction_data_collection_order", "BIGINT", False),
    ("kafka_topic", "STRING", True),
    ("kafka_partition", "INT", True),
    ("kafka_offset", "BIGINT", True),
    ("kafka_timestamp", "TIMESTAMP_LTZ", True),
    ("key_schema_id", "INT", False),
    ("value_schema_id", "INT", False),
    ("schema_fingerprint", "STRING", False),
    ("contract_version", "INT", True),
    ("before_row_hash", "STRING", False),
    ("after_row_hash", "STRING", False),
    ("row_hash", "STRING", False),
    ("bronze_ingested_at", "TIMESTAMP_LTZ", True),
    ("normalized_at", "TIMESTAMP_LTZ", True),
)

_CURRENT_SUFFIX = _columns(
    ("is_deleted", "BOOLEAN", True),
    ("deleted_at", "TIMESTAMP_LTZ", False),
    ("last_event_id", "STRING", True),
    ("last_source_ts", "TIMESTAMP_LTZ", True),
    ("last_is_snapshot", "BOOLEAN", True),
    ("last_source_binlog_file_index", "INT", False),
    ("last_source_binlog_pos", "BIGINT", False),
    ("last_source_row", "INT", False),
    ("last_transaction_total_order", "BIGINT", False),
    ("last_transaction_data_collection_order", "BIGINT", False),
    ("last_transaction_id", "STRING", False),
    ("last_kafka_partition", "INT", True),
    ("last_kafka_offset", "BIGINT", True),
    ("last_row_hash", "STRING", True),
    ("contract_version", "INT", True),
    ("updated_at", "TIMESTAMP_LTZ", True),
)


def _silver_tables() -> tuple[TableSpec, ...]:
    tables: list[TableSpec] = []
    for entity in ENTITIES:
        business_columns = BUSINESS_SCHEMAS[entity]
        tables.append(
            TableSpec(
                namespace="silver",
                name=f"{entity}_changes",
                columns=(
                    *_CHANGES_PREFIX,
                    *(column.nullable_copy() for column in business_columns),
                    *_CHANGES_SUFFIX,
                ),
                partition_transform="days(source_ts)",
            )
        )
        tables.append(
            TableSpec(
                namespace="silver",
                name=f"{entity}_current",
                columns=(*business_columns, *_CURRENT_SUFFIX),
            )
        )
    return tuple(tables)


SILVER_TABLES = _silver_tables()


REFERENCE_TABLES = (
    TableSpec(
        namespace="reference",
        name="geolocation",
        columns=_columns(
            ("geolocation_id", "BIGINT", True),
            ("geolocation_zip_code_prefix", "STRING", True),
            ("geolocation_lat", "DECIMAL(18,14)", True),
            ("geolocation_lng", "DECIMAL(18,14)", True),
            ("geolocation_city", "STRING", True),
            ("geolocation_state", "STRING", True),
            ("source_archive_sha256", "STRING", True),
            ("source_row_number", "BIGINT", True),
            ("loaded_at", "TIMESTAMP_LTZ", True),
        ),
    ),
)


AUDIT_TABLES = (
    TableSpec(
        namespace="audit",
        name="mysql_transactions",
        columns=_columns(
            ("transaction_id", "STRING", True),
            ("status", "STRING", True),
            ("event_count", "BIGINT", False),
            (
                "data_collections",
                "ARRAY<STRUCT<data_collection: STRING, event_count: BIGINT>>",
                False,
            ),
            ("begin_event_id", "STRING", False),
            ("end_event_id", "STRING", False),
            ("kafka_topic", "STRING", True),
            ("kafka_partition", "INT", True),
            ("begin_kafka_offset", "BIGINT", False),
            ("end_kafka_offset", "BIGINT", False),
            ("source_ts", "TIMESTAMP_LTZ", False),
            ("first_seen_at", "TIMESTAMP_LTZ", True),
            ("completed_at", "TIMESTAMP_LTZ", False),
            ("rejected_event_ids", "ARRAY<STRING>", False),
            ("recorded_at", "TIMESTAMP_LTZ", True),
        ),
        partition_transform="days(recorded_at)",
    ),
    TableSpec(
        namespace="audit",
        name="silver_progress",
        columns=_columns(
            ("query_name", "STRING", True),
            ("entity", "STRING", True),
            ("contract_version", "INT", True),
            ("source_topic", "STRING", True),
            ("kafka_partition", "INT", True),
            ("last_kafka_offset", "BIGINT", True),
            ("last_event_id", "STRING", True),
            ("last_source_ts", "TIMESTAMP_LTZ", False),
            ("spark_query_id", "STRING", True),
            ("spark_batch_id", "BIGINT", True),
            ("changes_snapshot_id", "BIGINT", True),
            ("current_snapshot_id", "BIGINT", False),
            ("status", "STRING", True),
            ("error_class", "STRING", False),
            ("updated_at", "TIMESTAMP_LTZ", True),
            ("recorded_at", "TIMESTAMP_LTZ", True),
        ),
        partition_transform="days(recorded_at)",
    ),
    TableSpec(
        namespace="audit",
        name="normalization_errors",
        columns=_columns(
            ("error_id", "STRING", True),
            ("event_id", "STRING", True),
            ("entity", "STRING", True),
            ("error_code", "STRING", True),
            ("error_message", "STRING", True),
            ("kafka_topic", "STRING", True),
            ("kafka_partition", "INT", True),
            ("kafka_offset", "BIGINT", True),
            ("key_schema_id", "INT", False),
            ("value_schema_id", "INT", False),
            ("schema_fingerprint", "STRING", False),
            ("contract_version", "INT", True),
            ("first_seen_at", "TIMESTAMP_LTZ", True),
            ("last_seen_at", "TIMESTAMP_LTZ", True),
            ("occurrence_count", "BIGINT", True),
            ("resolved_at", "TIMESTAMP_LTZ", False),
            ("recorded_at", "TIMESTAMP_LTZ", True),
        ),
        partition_transform="days(recorded_at)",
    ),
    TableSpec(
        namespace="audit",
        name="schema_violations",
        columns=_columns(
            ("violation_id", "STRING", True),
            ("entity", "STRING", True),
            ("event_id", "STRING", False),
            ("schema_kind", "STRING", True),
            ("schema_id", "INT", False),
            ("fingerprint_sha256", "STRING", False),
            ("contract_version", "INT", True),
            ("violation_code", "STRING", True),
            ("error_message", "STRING", True),
            ("compatibility_result", "STRING", False),
            ("details_json", "STRING", False),
            ("recorded_at", "TIMESTAMP_LTZ", True),
        ),
        partition_transform="days(recorded_at)",
    ),
    TableSpec(
        namespace="audit",
        name="maintenance_runs",
        columns=_columns(
            ("maintenance_run_id", "STRING", True),
            ("procedure", "STRING", True),
            ("table_namespace", "STRING", True),
            ("table_name", "STRING", True),
            ("status", "STRING", True),
            ("started_at", "TIMESTAMP_LTZ", True),
            ("finished_at", "TIMESTAMP_LTZ", False),
            ("options_json", "STRING", True),
            ("result_json", "STRING", False),
            ("error_code", "STRING", False),
            ("error_message", "STRING", False),
            ("recorded_at", "TIMESTAMP_LTZ", True),
        ),
        partition_transform="days(recorded_at)",
    ),
    TableSpec(
        namespace="audit",
        name="serving_sync_reports",
        columns=_columns(
            ("sync_run_id", "STRING", True),
            ("sync_run_seq", "BIGINT", True),
            ("status", "STRING", True),
            ("is_noop", "BOOLEAN", True),
            ("previous_transaction_id", "STRING", False),
            ("target_transaction_id", "STRING", False),
            ("target_offsets_json", "STRING", True),
            ("expected_event_count", "BIGINT", True),
            ("materialized_event_count", "BIGINT", True),
            ("entity_counts_json", "STRING", True),
            ("error_details_json", "STRING", False),
            ("started_at", "TIMESTAMP_LTZ", True),
            ("finished_at", "TIMESTAMP_LTZ", False),
            ("published_at", "TIMESTAMP_LTZ", False),
            ("recorded_at", "TIMESTAMP_LTZ", True),
        ),
        partition_transform="days(recorded_at)",
    ),
    TableSpec(
        namespace="audit",
        name="schema_migrations",
        columns=_columns(
            ("migration_version", "INT", True),
            ("migration_id", "STRING", True),
            ("checksum_sha256", "STRING", True),
            ("status", "STRING", True),
            ("applied_by", "STRING", True),
            ("spark_app_id", "STRING", True),
            ("started_at", "TIMESTAMP_LTZ", True),
            ("finished_at", "TIMESTAMP_LTZ", True),
            ("error_code", "STRING", False),
            ("error_message", "STRING", False),
            ("recorded_at", "TIMESTAMP_LTZ", True),
        ),
        partition_transform="days(recorded_at)",
    ),
)


ALL_TABLES: tuple[TableSpec, ...] = (
    *BRONZE_TABLES,
    *SILVER_TABLES,
    *REFERENCE_TABLES,
    *AUDIT_TABLES,
)
TABLES_BY_NAME: Mapping[str, TableSpec] = {
    f"{table.namespace}.{table.name}": table for table in ALL_TABLES
}


def namespace_statements() -> tuple[str, ...]:
    return tuple(
        f"CREATE NAMESPACE IF NOT EXISTS `{CATALOG_ALIAS}`.`{namespace}`"
        for namespace in NAMESPACES
    )


def migration_statements() -> tuple[str, ...]:
    return (*namespace_statements(), *(table.create_sql() for table in ALL_TABLES))


def canonical_contract_json(tables: Iterable[TableSpec] = ALL_TABLES) -> str:
    payload = {
        "catalog_alias": CATALOG_ALIAS,
        "namespaces": list(NAMESPACES),
        "tables": [table.as_dict() for table in tables],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def contract_checksum(tables: Iterable[TableSpec] = ALL_TABLES) -> str:
    return hashlib.sha256(canonical_contract_json(tables).encode("utf-8")).hexdigest()
