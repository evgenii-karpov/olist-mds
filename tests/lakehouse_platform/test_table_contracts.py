from __future__ import annotations

import re

from streaming.spark.platform.migrations.initial_lakehouse import (
    MIGRATION_ID,
    MIGRATION_VERSION,
)
from streaming.spark.platform.table_specs import (
    ALL_TABLES,
    AUDIT_TABLES,
    BRONZE_TABLES,
    BUSINESS_SCHEMAS,
    CATALOG_ALIAS,
    ENTITIES,
    NAMESPACES,
    REFERENCE_TABLES,
    SILVER_TABLES,
    TABLE_PROPERTIES,
    TABLES_BY_NAME,
    contract_checksum,
    migration_statements,
)

EXPECTED_BUSINESS_COLUMNS = {
    "customers": (
        ("customer_id", "STRING", True),
        ("customer_unique_id", "STRING", True),
        ("customer_zip_code_prefix", "STRING", True),
        ("customer_city", "STRING", True),
        ("customer_state", "STRING", True),
    ),
    "orders": (
        ("order_id", "STRING", True),
        ("customer_id", "STRING", True),
        ("order_status", "STRING", True),
        ("order_purchase_timestamp", "TIMESTAMP_LTZ", True),
        ("order_approved_at", "TIMESTAMP_LTZ", False),
        ("order_delivered_carrier_date", "TIMESTAMP_LTZ", False),
        ("order_delivered_customer_date", "TIMESTAMP_LTZ", False),
        ("order_estimated_delivery_date", "TIMESTAMP_LTZ", True),
    ),
    "order_items": (
        ("order_id", "STRING", True),
        ("order_item_id", "INT", True),
        ("product_id", "STRING", True),
        ("seller_id", "STRING", True),
        ("shipping_limit_date", "TIMESTAMP_LTZ", True),
        ("price", "DECIMAL(18,2)", True),
        ("freight_value", "DECIMAL(18,2)", True),
    ),
    "order_payments": (
        ("order_id", "STRING", True),
        ("payment_sequential", "INT", True),
        ("payment_type", "STRING", True),
        ("payment_installments", "INT", True),
        ("payment_value", "DECIMAL(18,2)", True),
    ),
    "order_reviews": (
        ("review_id", "STRING", True),
        ("order_id", "STRING", True),
        ("review_score", "INT", True),
        ("review_comment_title", "STRING", False),
        ("review_comment_message", "STRING", False),
        ("review_creation_date", "TIMESTAMP_LTZ", True),
        ("review_answer_timestamp", "TIMESTAMP_LTZ", True),
    ),
    "products": (
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
    "sellers": (
        ("seller_id", "STRING", True),
        ("seller_zip_code_prefix", "STRING", True),
        ("seller_city", "STRING", True),
        ("seller_state", "STRING", True),
    ),
    "product_category_translation": (
        ("product_category_name", "STRING", True),
        ("product_category_name_english", "STRING", True),
    ),
}

EXPECTED_CHANGES_PREFIX = (
    "event_id",
    "op",
    "is_snapshot",
    "is_deleted",
    "apply_status",
    "error_code",
    "error_message",
)
EXPECTED_CHANGES_SUFFIX = (
    "source_ts",
    "source_server_id",
    "source_gtid",
    "source_binlog_file",
    "source_binlog_file_index",
    "source_binlog_pos",
    "source_row",
    "transaction_id",
    "transaction_total_order",
    "transaction_data_collection_order",
    "kafka_topic",
    "kafka_partition",
    "kafka_offset",
    "kafka_timestamp",
    "key_schema_id",
    "value_schema_id",
    "schema_fingerprint",
    "contract_version",
    "before_row_hash",
    "after_row_hash",
    "row_hash",
    "bronze_ingested_at",
    "normalized_at",
)
EXPECTED_CURRENT_SUFFIX = (
    "is_deleted",
    "deleted_at",
    "last_event_id",
    "last_source_ts",
    "last_is_snapshot",
    "last_source_binlog_file_index",
    "last_source_binlog_pos",
    "last_source_row",
    "last_transaction_total_order",
    "last_transaction_data_collection_order",
    "last_transaction_id",
    "last_kafka_partition",
    "last_kafka_offset",
    "last_row_hash",
    "contract_version",
    "updated_at",
)


def _columns(table_name: str) -> tuple[str, ...]:
    return tuple(column.name for column in TABLES_BY_NAME[table_name].columns)


def test_namespace_and_table_surface_is_exact() -> None:
    assert CATALOG_ALIAS == "lakehouse"
    assert NAMESPACES == ("bronze", "silver", "reference", "audit")
    assert "gold" not in NAMESPACES
    assert len(BRONZE_TABLES) == 2
    assert len(SILVER_TABLES) == 16
    assert len(REFERENCE_TABLES) == 1
    assert len(AUDIT_TABLES) == 7
    assert len(ALL_TABLES) == len(TABLES_BY_NAME) == 26
    assert {table.namespace for table in ALL_TABLES} == set(NAMESPACES)


def test_business_schemas_keep_exact_mysql_to_iceberg_types() -> None:
    assert tuple(BUSINESS_SCHEMAS) == ENTITIES
    actual = {
        entity: tuple(
            (column.name, column.sql_type, column.required)
            for column in BUSINESS_SCHEMAS[entity]
        )
        for entity in ENTITIES
    }

    assert actual == EXPECTED_BUSINESS_COLUMNS


def test_bronze_schema_and_partition_contract() -> None:
    assert _columns("bronze.mysql_cdc_records") == (
        "event_id",
        "record_kind",
        "topic",
        "partition",
        "offset",
        "kafka_timestamp",
        "kafka_timestamp_type",
        "headers",
        "key_bytes",
        "value_bytes",
        "is_tombstone",
        "key_schema_id",
        "value_schema_id",
        "key_sha256",
        "value_sha256",
        "key_framing_valid",
        "value_framing_valid",
        "framing_error",
        "ingest_batch_id",
        "spark_query_id",
        "ingested_at",
    )
    assert TABLES_BY_NAME["bronze.mysql_cdc_records"].partition_transform == (
        "days(ingested_at)"
    )
    assert _columns("bronze.avro_schemas") == (
        "schema_id",
        "fingerprint_sha256",
        "subject",
        "registry_version",
        "schema_json",
        "references_json",
        "spark_self_contained_schema_json",
        "first_seen_at",
        "last_verified_at",
    )
    assert TABLES_BY_NAME["bronze.avro_schemas"].partition_transform is None


def test_each_entity_has_matching_changes_and_current_tables() -> None:
    for entity in ENTITIES:
        business = tuple(column.name for column in BUSINESS_SCHEMAS[entity])
        changes = TABLES_BY_NAME[f"silver.{entity}_changes"]
        current = TABLES_BY_NAME[f"silver.{entity}_current"]

        assert tuple(column.name for column in changes.columns) == (
            *EXPECTED_CHANGES_PREFIX,
            *business,
            *EXPECTED_CHANGES_SUFFIX,
        )
        assert all(
            not column.required
            for column in changes.columns[
                len(EXPECTED_CHANGES_PREFIX) : len(EXPECTED_CHANGES_PREFIX)
                + len(business)
            ]
        )
        assert changes.partition_transform == "days(source_ts)"
        assert tuple(column.name for column in current.columns) == (
            *business,
            *EXPECTED_CURRENT_SUFFIX,
        )
        assert current.partition_transform is None


def test_reference_and_audit_table_names_and_partitions_are_exact() -> None:
    geolocation = TABLES_BY_NAME["reference.geolocation"]
    assert tuple((column.name, column.sql_type) for column in geolocation.columns) == (
        ("geolocation_id", "BIGINT"),
        ("geolocation_zip_code_prefix", "STRING"),
        ("geolocation_lat", "DECIMAL(18,14)"),
        ("geolocation_lng", "DECIMAL(18,14)"),
        ("geolocation_city", "STRING"),
        ("geolocation_state", "STRING"),
        ("source_archive_sha256", "STRING"),
        ("source_row_number", "BIGINT"),
        ("loaded_at", "TIMESTAMP_LTZ"),
    )
    assert geolocation.partition_transform is None

    assert tuple(table.name for table in AUDIT_TABLES) == (
        "mysql_transactions",
        "silver_progress",
        "normalization_errors",
        "schema_violations",
        "maintenance_runs",
        "serving_sync_reports",
        "schema_migrations",
    )
    assert all(
        table.partition_transform == "days(recorded_at)" for table in AUDIT_TABLES
    )


def test_every_table_gets_only_the_canonical_iceberg_properties() -> None:
    expected = {
        "format-version": "2",
        "write.format.default": "parquet",
        "write.parquet.compression-codec": "zstd",
        "write.target-file-size-bytes": "134217728",
        "write.metadata.delete-after-commit.enabled": "true",
        "write.metadata.previous-versions-max": "20",
    }
    assert dict(TABLE_PROPERTIES) == expected
    assert all(dict(table.properties) == expected for table in ALL_TABLES)


def test_migration_sql_is_deterministic_and_complete() -> None:
    statements = migration_statements()

    assert len(statements) == len(NAMESPACES) + len(ALL_TABLES)
    assert statements[:4] == tuple(
        f"CREATE NAMESPACE IF NOT EXISTS `lakehouse`.`{namespace}`"
        for namespace in NAMESPACES
    )
    for table, statement in zip(ALL_TABLES, statements[4:], strict=True):
        assert statement.startswith(
            f"CREATE TABLE IF NOT EXISTS `lakehouse`.`{table.namespace}`.`{table.name}`"
        )
        assert "\nUSING iceberg" in statement
        assert statement.count("TBLPROPERTIES") == 1
        if table.partition_transform:
            assert "PARTITIONED BY (days(" in statement
        else:
            assert "PARTITIONED BY" not in statement

    assert MIGRATION_VERSION == 1
    assert MIGRATION_ID == "0001_initial_lakehouse"
    assert re.fullmatch(r"[0-9a-f]{64}", contract_checksum())
    assert contract_checksum() == contract_checksum()
