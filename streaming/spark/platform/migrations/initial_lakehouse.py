"""Migration 0001: the complete Bronze/Silver/reference/audit table surface."""

from __future__ import annotations

import getpass
import re
from typing import Any

from ..table_specs import ALL_TABLES, CATALOG_ALIAS, TableSpec, contract_checksum

MIGRATION_VERSION = 1
MIGRATION_ID = "0001_initial_lakehouse"


def _normalized_type(sql_type: str) -> str:
    normalized = re.sub(r"\s+", "", sql_type.lower())
    aliases = {
        "bigint": "bigint",
        "int": "int",
        "timestamp_ltz": "timestamp",
        "timestamp_ntz": "timestamp_ntz",
    }
    return aliases.get(normalized, normalized)


def _validate_schema(spark: Any, table: TableSpec, catalog_alias: str) -> None:
    qualified_name = table.qualified_name_for(catalog_alias)
    actual_fields = spark.table(qualified_name).schema.fields
    actual = [
        (field.name, field.dataType.simpleString().replace(" ", ""), not field.nullable)
        for field in actual_fields
    ]
    expected = [
        (column.name, _normalized_type(column.sql_type), column.required)
        for column in table.columns
    ]
    if actual != expected:
        raise RuntimeError(
            f"schema drift for {qualified_name}: expected {expected!r}, got {actual!r}"
        )


def _validate_properties(spark: Any, table: TableSpec, catalog_alias: str) -> None:
    qualified_name = table.qualified_name_for(catalog_alias)
    rows = spark.sql(f"SHOW TBLPROPERTIES {qualified_name}").collect()
    actual = {row[0]: row[1] for row in rows}
    for name, expected in table.properties:
        if actual.get(name) != expected:
            raise RuntimeError(
                f"property drift for {qualified_name}.{name}: "
                f"expected {expected!r}, got {actual.get(name)!r}"
            )


def _validate_partition(spark: Any, table: TableSpec, catalog_alias: str) -> None:
    qualified_name = table.qualified_name_for(catalog_alias)
    create_rows = spark.sql(f"SHOW CREATE TABLE {qualified_name}").collect()
    create_sql = "\n".join(str(row[0]) for row in create_rows)
    normalized = re.sub(r"[`\s]", "", create_sql.lower())
    if table.partition_transform:
        expected = f"partitionedby({table.partition_transform})"
        if expected not in normalized:
            raise RuntimeError(
                f"partition drift for {qualified_name}: expected {table.partition_transform}"
            )
    elif "partitionedby(" in normalized:
        raise RuntimeError(f"{qualified_name} must be unpartitioned")


def _record_migration(spark: Any, checksum: str, catalog_alias: str) -> None:
    app_id = spark.sparkContext.applicationId.replace("'", "''")
    applied_by = getpass.getuser().replace("'", "''")
    spark.sql(
        f"""
        MERGE INTO {catalog_alias}.audit.schema_migrations AS target
        USING (
          SELECT
            {MIGRATION_VERSION} AS migration_version,
            '{MIGRATION_ID}' AS migration_id,
            '{checksum}' AS checksum_sha256,
            'APPLIED' AS status,
            '{applied_by}' AS applied_by,
            '{app_id}' AS spark_app_id,
            current_timestamp() AS started_at,
            current_timestamp() AS finished_at,
            CAST(NULL AS STRING) AS error_code,
            CAST(NULL AS STRING) AS error_message,
            current_timestamp() AS recorded_at
        ) AS incoming
        ON target.migration_version = incoming.migration_version
        WHEN NOT MATCHED THEN INSERT *
        """
    )


def _assert_migration_history(spark: Any, checksum: str, catalog_alias: str) -> bool:
    if not spark.catalog.tableExists(f"{catalog_alias}.audit.schema_migrations"):
        return False
    rows = spark.sql(
        f"""
        SELECT checksum_sha256, status
        FROM {catalog_alias}.audit.schema_migrations
        WHERE migration_version = {MIGRATION_VERSION}
        ORDER BY recorded_at DESC
        LIMIT 1
        """
    ).collect()
    if not rows:
        return False
    if rows[0][0] != checksum or rows[0][1] != "APPLIED":
        raise RuntimeError(
            f"migration {MIGRATION_VERSION} history conflicts with source contract"
        )
    return True


def apply(spark: Any, catalog_alias: str = CATALOG_ALIAS) -> str:
    """Idempotently create and then verify all configured Iceberg relations."""

    checksum = contract_checksum()
    already_applied = _assert_migration_history(spark, checksum, catalog_alias)

    for namespace in ("bronze", "silver", "reference", "audit"):
        spark.sql(f"CREATE NAMESPACE IF NOT EXISTS {catalog_alias}.{namespace}")
    for table in ALL_TABLES:
        spark.sql(table.create_sql(catalog_alias))

    for table in ALL_TABLES:
        _validate_schema(spark, table, catalog_alias)
        _validate_properties(spark, table, catalog_alias)
        _validate_partition(spark, table, catalog_alias)

    if not already_applied:
        _record_migration(spark, checksum, catalog_alias)
    return checksum
