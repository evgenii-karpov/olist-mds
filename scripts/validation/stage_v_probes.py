"""Typed probes and canonical manifest generator for Stage V validation harness."""

from __future__ import annotations

import decimal
import hashlib
import json
import os
import re
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

ALLOWLISTED_FIXTURES = {
    "insert.sql": ROOT / "tests" / "stage_v" / "fixtures" / "insert.sql",
    "update.sql": ROOT / "tests" / "stage_v" / "fixtures" / "update.sql",
    "delete.sql": ROOT / "tests" / "stage_v" / "fixtures" / "delete.sql",
    "add_nullable_column.sql": ROOT
    / "tests"
    / "stage_v"
    / "fixtures"
    / "add_nullable_column.sql",
    "emit_nullable_event.sql": ROOT
    / "tests"
    / "stage_v"
    / "fixtures"
    / "emit_nullable_event.sql",
}
ALLOWED_FIXTURES = ALLOWLISTED_FIXTURES

SECRET_PATTERNS = [
    re.compile(
        r"(?i)(password|passwd|secret|token|credential)\s*=\s*['\"]?[^\s'\",;]+['\"]?"
    ),
    re.compile(r"(?i)mysql://[^:]+:[^@]+@"),
]

PRIMARY_KEYS: dict[str, list[str]] = {
    "customers": ["customer_id"],
    "orders": ["order_id"],
    "order_items": ["order_id", "order_item_id"],
    "order_payments": ["order_id", "payment_sequential"],
    "order_reviews": ["review_id", "order_id"],
    "products": ["product_id"],
    "sellers": ["seller_id"],
    "product_category_translation": ["product_category_name"],
    "geolocation": ["geolocation_zip_code_prefix"],
}


def sanitize_text(text: str) -> str:
    """Redact sensitive values like passwords or connection strings."""
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED_SECRET]", redacted)
    return redacted


def normalize_value(val: Any) -> Any:
    """Normalize timestamp/decimal/null values for canonical manifest."""
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, str)):
        return val
    if isinstance(val, (float, decimal.Decimal)):
        # Convert numeric to string with fixed scale representation without float inaccuracy
        return str(decimal.Decimal(str(val)))
    if isinstance(val, datetime):
        val = val.replace(tzinfo=UTC) if val.tzinfo is None else val.astimezone(UTC)
        return val.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"
    return str(val)


def build_canonical_manifest(
    entity: str,
    rows: list[dict[str, Any]],
    pk_columns: list[str] | None = None,
) -> dict[str, Any]:
    """Construct deterministic canonical manifest with sorted rows and SHA-256 digest."""
    keys = pk_columns or PRIMARY_KEYS.get(entity, ["id"])

    normalized_rows = []
    for row in rows:
        norm_row = {k: normalize_value(v) for k, v in row.items()}
        # Compute row_hash
        pk_tuple = tuple(str(norm_row.get(k, "")) for k in keys)
        row_str = json.dumps(norm_row, sort_keys=True, ensure_ascii=False)
        row_hash = hashlib.sha256(row_str.encode("utf-8")).hexdigest()
        norm_row["_canonical_pk"] = pk_tuple
        norm_row["_canonical_row_hash"] = row_hash
        normalized_rows.append(norm_row)

    # Sort rows by canonical PK
    normalized_rows.sort(key=lambda r: r["_canonical_pk"])

    # Clean out internal sorting key before serializing
    final_rows = []
    for r in normalized_rows:
        r_copy = dict(r)
        del r_copy["_canonical_pk"]
        final_rows.append(r_copy)

    manifest_bytes = json.dumps(
        final_rows, indent=2, sort_keys=True, ensure_ascii=False
    ).encode("utf-8")
    manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()

    return {
        "entity": entity,
        "row_count": len(final_rows),
        "primary_keys": keys,
        "manifest_sha256": manifest_sha256,
        "rows": final_rows,
    }


class BaseProbe:
    """Base probe for standardizing query execution and sanitization."""

    def __init__(self, name: str) -> None:
        self.name = name


class MySQLProbe(BaseProbe):
    """Probe for MySQL source layer queries and allowed fixture execution."""

    def __init__(self, password_file: Path | None = None) -> None:
        super().__init__("MySQLProbe")
        default_password_file = os.environ.get(
            "MYSQL_PASSWORD_FILE",
            os.environ.get(
                "MYSQL_SIMULATOR_PASSWORD_SOURCE_FILE",
                str(
                    ROOT / "docker" / "secrets" / "dev" / "mysql_simulator_password.txt"
                ),
            ),
        )
        self.password_file = password_file or Path(default_password_file)
        default_admin_password_file = os.environ.get(
            "MYSQL_ADMIN_PASSWORD_FILE",
            os.environ.get(
                "MYSQL_ADMIN_PASSWORD_SOURCE_FILE",
                str(ROOT / "docker" / "secrets" / "dev" / "mysql_admin_password.txt"),
            ),
        )
        self.admin_password_file = Path(default_admin_password_file)

    def _connect_with(self, password_file: Path, user: str) -> Any:
        """Open a file-secret MySQL connection or raise the real failure."""

        if not password_file.is_file():
            raise FileNotFoundError(f"MySQL password file is missing: {password_file}")

        from scripts.simulation.database import DatabaseSettings, connect

        host = os.environ.get("MYSQL_HOST", "127.0.0.1")
        port = int(
            os.environ.get("MYSQL_HOST_PORT", os.environ.get("MYSQL_PORT", "3306"))
        )
        settings = DatabaseSettings(
            password_file=password_file,
            host=host,
            port=port,
            database="olist_oltp",
            user=user,
            connect_timeout=10,
        )
        return connect(settings)

    def _connect(self) -> Any:
        """Open the DML connection for source assertions and fixtures."""

        return self._connect_with(
            self.password_file,
            os.environ.get("MYSQL_USER", "olist_simulator"),
        )

    def _connect_admin(self) -> Any:
        """Open the schema-owner connection for additive DDL fixtures."""

        return self._connect_with(
            self.admin_password_file,
            os.environ.get("MYSQL_ADMIN_USER", "olist_admin"),
        )

    def execute_fixture(self, fixture_name: str) -> dict[str, Any]:
        if fixture_name not in ALLOWED_FIXTURES:
            raise ValueError(
                f"Fixture {fixture_name!r} is not in MySQLProbe allowlist: {sorted(ALLOWED_FIXTURES)}"
            )
        fixture_path = ALLOWED_FIXTURES[fixture_name]
        sql_content = fixture_path.read_text(encoding="utf-8")
        statements = [s.strip() for s in sql_content.split(";") if s.strip()]

        connection = (
            self._connect_admin()
            if fixture_name == "add_nullable_column.sql"
            else self._connect()
        )
        cursor: Any | None = None
        try:
            cursor_handle: Any = connection.cursor()
            cursor = cursor_handle
            for stmt in statements:
                cursor_handle.execute(stmt)
            connection.commit()
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

        return {
            "fixture": fixture_name,
            "path": str(fixture_path),
            "status": "EXECUTED",
            "statements_count": len(statements),
        }

    def inspect_table_counts(self, tables: list[str]) -> dict[str, int]:
        """Read exact source counts for the Stage V oracle."""

        if not tables or any(
            not re.fullmatch(r"[A-Za-z0-9_]+", table) for table in tables
        ):
            raise ValueError("table count probe received an invalid table name")
        connection = self._connect()
        cursor: Any | None = None
        try:
            cursor_handle: Any = connection.cursor(dictionary=True)
            cursor = cursor_handle
            result: dict[str, int] = {}
            for table in tables:
                cursor_handle.execute(
                    f"SELECT COUNT(*) AS row_count FROM olist_oltp.`{table}`"
                )
                row = cursor_handle.fetchone()
                value = row.get("row_count") if isinstance(row, Mapping) else None
                if not isinstance(value, (int, float, str)):
                    raise RuntimeError(f"Source count is unavailable for {table}")
                result[table] = int(value)
            return result
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def inspect_nullable_event(
        self,
        customer_id: str,
        expected_city: str,
        column_name: str = "stage_v_optional_note",
    ) -> dict[str, Any]:
        """Verify the source nullable/default contract and emitted source row."""

        connection = self._connect()
        cursor: Any | None = None
        try:
            cursor_handle: Any = connection.cursor(dictionary=True)
            cursor = cursor_handle
            cursor_handle.execute(
                """
                SELECT
                    COLUMN_NAME AS column_name,
                    IS_NULLABLE AS is_nullable,
                    COLUMN_DEFAULT AS column_default
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = 'olist_oltp'
                  AND TABLE_NAME = 'customers'
                  AND COLUMN_NAME = %s
                """,
                (column_name,),
            )
            column = cursor_handle.fetchone()
            if not isinstance(column, Mapping):
                raise RuntimeError(
                    f"MySQL source column olist_oltp.customers.{column_name} was not found"
                )
            if (
                str(column.get("is_nullable", "")).upper() != "YES"
                or column.get("column_default") is not None
            ):
                raise RuntimeError(
                    "Nullable source contract mismatch: "
                    + json.dumps(dict(column), sort_keys=True, default=str)
                )

            cursor_handle.execute(
                f"""
                SELECT customer_id, customer_city, `{column_name}` AS optional_value
                FROM olist_oltp.customers
                WHERE customer_id = %s
                """,
                (customer_id,),
            )
            source_row = cursor_handle.fetchone()
            if not isinstance(source_row, Mapping):
                raise RuntimeError(f"Source customer row was not found: {customer_id}")
            if source_row.get("customer_city") != expected_city:
                raise RuntimeError(
                    "Source customer city mismatch: "
                    + json.dumps(dict(source_row), sort_keys=True, default=str)
                )
            if source_row.get("optional_value") is not None:
                raise RuntimeError(
                    f"Source nullable column {column_name} is not NULL for {customer_id}"
                )

            return {
                "status": "VERIFIED",
                "column": dict(column),
                "source_row": dict(source_row),
            }
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()


class KafkaProbe(BaseProbe):
    """Probe for Kafka topics, offsets, and tombstones."""

    def __init__(self) -> None:
        super().__init__("KafkaProbe")

    def inspect_offsets(self, topics: list[str]) -> dict[str, Any]:
        return {
            "topics": topics,
            "status": "INSPECTED",
        }


class IcebergProbe(BaseProbe):
    """Probe for Iceberg tables, snapshots, and row manifests."""

    def __init__(self) -> None:
        super().__init__("IcebergProbe")


class PostgresControlProbe(BaseProbe):
    """Probe for Postgres control database."""

    def __init__(self) -> None:
        super().__init__("PostgresControlProbe")


class ClickHouseProbe(BaseProbe):
    """Probe for ClickHouse serving layer and gold views."""

    def __init__(self) -> None:
        super().__init__("ClickHouseProbe")

    def inspect_stage_counts(
        self,
        phase: str,
        expected: Mapping[str, Any],
        source_probe: MySQLProbe | None = None,
        operation_expected: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Verify exact Silver/current counts and duplicate-event invariants.

        The expected values come from the versioned Stage V oracle file.  The
        observed values are queried from Iceberg-backed ClickHouse relations,
        so a command exit code alone cannot produce a PASS.
        """

        from scripts.serving.clickhouse import (
            ClickHouseServingMaterializer,
            clickhouse_query,
            format_ch_relation,
        )
        from scripts.serving.entities import ALL_SERVING_ENTITIES

        all_metrics = ClickHouseServingMaterializer.fetch_entity_metrics()
        all_progress = ClickHouseServingMaterializer.fetch_silver_progress()
        entity_changes: dict[str, int] = {}
        manifests: dict[str, dict[str, Any]] = {}
        operation_counts = {"c": 0, "u": 0, "d": 0, "r": 0}
        duplicate_event_ids = 0
        for spec in ALL_SERVING_ENTITIES:
            metrics = all_metrics.get(spec.entity, {})
            raw_count = metrics.get("event_count")
            if not isinstance(raw_count, (int, float, str)):
                raise RuntimeError(
                    f"Silver event count is unavailable for {spec.entity}"
                )
            entity_changes[spec.entity] = int(raw_count)

            relation = format_ch_relation(spec.changes_relation)
            operation_rows = clickhouse_query(
                f"""
                SELECT op, count() AS operation_count
                FROM {relation}
                GROUP BY op
                """
            )
            for operation_row in operation_rows:
                operation = operation_row.get("op")
                count = operation_row.get("operation_count")
                if operation in operation_counts and isinstance(
                    count, (int, float, str)
                ):
                    operation_counts[str(operation)] += int(count)
            duplicate_rows = clickhouse_query(
                f"""
                SELECT count() AS duplicate_groups
                FROM
                (
                    SELECT event_id
                    FROM {relation}
                    GROUP BY event_id
                    HAVING count() > 1
                )
                """
            )
            duplicate_value = (
                duplicate_rows[0].get("duplicate_groups") if duplicate_rows else None
            )
            if not isinstance(duplicate_value, (int, float, str)):
                raise RuntimeError(
                    f"Duplicate event probe is unavailable for {spec.entity}"
                )
            duplicate_event_ids += int(duplicate_value)

            pk_columns = ", ".join(spec.primary_key)
            manifest_rows = clickhouse_query(
                f"""
                SELECT
                    {pk_columns},
                    argMax(kafka_offset, (kafka_partition, kafka_offset)) AS last_kafka_offset,
                    argMax(is_deleted, (kafka_partition, kafka_offset)) AS is_deleted
                FROM {relation}
                GROUP BY {pk_columns}
                """
            )
            manifests[spec.entity] = build_canonical_manifest(
                spec.entity, manifest_rows, list(spec.primary_key)
            )

        visible_current = ClickHouseServingMaterializer.fetch_iceberg_current_counts()
        physical_current = ClickHouseServingMaterializer.fetch_iceberg_physical_counts()
        deleted_current = ClickHouseServingMaterializer.fetch_iceberg_deleted_counts()
        audit_errors = ClickHouseServingMaterializer.fetch_audit_error_counts()

        expected_entity_changes = expected.get("entity_changes")
        if phase == "initial_snapshot":
            expected_entity_changes = {
                spec.entity: expected.get(spec.entity, 0)
                for spec in ALL_SERVING_ENTITIES
            }
        if not isinstance(expected_entity_changes, Mapping):
            raise RuntimeError(f"Oracle has no entity_changes for phase {phase}")
        expected_entity_changes = {
            str(key): int(value) for key, value in expected_entity_changes.items()
        }
        expected_visible = expected.get("entity_visible_current")
        if phase == "initial_snapshot":
            expected_visible = {
                spec.entity: expected.get(spec.entity, 0)
                for spec in ALL_SERVING_ENTITIES
            }
        if isinstance(expected_visible, Mapping):
            expected_visible = {
                str(key): int(value)
                for key, value in expected_visible.items()
                if str(key) in {spec.entity for spec in ALL_SERVING_ENTITIES}
            }
        else:
            expected_visible = None

        source_counts: dict[str, int] = {}
        if source_probe is not None:
            source_counts = source_probe.inspect_table_counts(["geolocation"])

        observed = {
            "phase": phase,
            "entity_changes": entity_changes,
            "total_applied_changes": sum(entity_changes.values()),
            "entity_visible_current": visible_current,
            "total_visible_current": sum(visible_current.values()),
            "physical_current": physical_current,
            "total_physical_current": sum(physical_current.values()),
            "deleted_current": deleted_current,
            "total_deleted_current": sum(deleted_current.values()),
            "source_counts": source_counts,
            "rejected": audit_errors["rejected"],
            "schema_violations": audit_errors["schema_violations"],
            "duplicate_event_id_groups": duplicate_event_ids,
            "operation_counts": operation_counts,
            "silver_progress": all_progress,
            "manifests": {
                entity: {
                    "row_count": manifest.get("row_count"),
                    "manifest_sha256": manifest.get("manifest_sha256"),
                }
                for entity, manifest in manifests.items()
            },
        }

        def row_is_deleted(row: Mapping[str, Any]) -> bool:
            value = row.get("is_deleted")
            if isinstance(value, str):
                return value.strip().lower() in {"1", "true", "yes"}
            return bool(value)

        manifest_physical_counts = {
            entity: int(manifest.get("row_count", -1))
            for entity, manifest in manifests.items()
        }
        manifest_visible_counts = {
            entity: sum(
                1
                for row in manifest.get("rows", [])
                if isinstance(row, Mapping) and not row_is_deleted(row)
            )
            for entity, manifest in manifests.items()
        }
        manifest_deleted_counts = {
            entity: sum(
                1
                for row in manifest.get("rows", [])
                if isinstance(row, Mapping) and row_is_deleted(row)
            )
            for entity, manifest in manifests.items()
        }
        observed["manifest_physical_counts"] = manifest_physical_counts
        observed["manifest_visible_counts"] = manifest_visible_counts
        observed["manifest_deleted_counts"] = manifest_deleted_counts

        expected_total_changes = int(expected.get("total_applied_changes", 0))
        expected_total_visible = int(expected.get("total_visible_current", 0))
        expected_physical = int(
            expected.get("total_physical_current", expected_total_visible)
        )
        expected_deleted = int(expected.get("total_deleted_current", 0))
        expected_geolocation = int(expected.get("geolocation", 0))

        def numeric_int(value: object, default: int = -1) -> int:
            if not isinstance(value, (int, float, str)):
                return default
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        checks = {
            "entity_changes": entity_changes == expected_entity_changes,
            "total_applied_changes": observed["total_applied_changes"]
            == expected_total_changes,
            "entity_visible_current": expected_visible is None
            or visible_current == expected_visible,
            "total_visible_current": observed["total_visible_current"]
            == expected_total_visible,
            "total_physical_current": observed["total_physical_current"]
            == expected_physical,
            "total_deleted_current": observed["total_deleted_current"]
            == expected_deleted,
            "canonical_manifest_physical_parity": manifest_physical_counts
            == physical_current,
            "canonical_manifest_visible_parity": manifest_visible_counts
            == visible_current,
            "canonical_manifest_deleted_parity": manifest_deleted_counts
            == deleted_current,
            "geolocation": source_counts.get("geolocation") == expected_geolocation
            if source_probe is not None
            else True,
            "rejected": observed["rejected"] == int(expected.get("rejected", 0)),
            "schema_violations": observed["schema_violations"]
            == int(expected.get("schema_violations", 0)),
            "duplicate_event_ids": duplicate_event_ids == 0,
            "silver_progress": set(all_progress)
            == {spec.entity for spec in ALL_SERVING_ENTITIES}
            and all(
                row.get("status") == "COMMITTED"
                and numeric_int(row.get("last_kafka_offset")) >= 0
                and numeric_int(row.get("changes_snapshot_id"), 0) > 0
                for row in all_progress.values()
            ),
        }
        if operation_expected is not None:
            checks["crud_operation_counts"] = all(
                operation_counts[operation]
                == int(operation_expected.get(expected_name, 0))
                for operation, expected_name in (
                    ("c", "insert_events"),
                    ("u", "update_events"),
                    ("d", "delete_events"),
                )
            )
        failed_checks = sorted(name for name, ok in checks.items() if not ok)
        if failed_checks:
            raise RuntimeError(
                f"Exact Stage V oracle mismatch for {phase}: "
                + json.dumps(
                    {
                        "failed_checks": failed_checks,
                        "expected": dict(expected),
                        "observed": observed,
                    },
                    sort_keys=True,
                    default=str,
                )
            )
        return {
            "status": "VERIFIED",
            "phase": phase,
            "checks": checks,
            "observed": observed,
        }

    def inspect_nullable_event(
        self,
        customer_id: str,
        expected_city: str,
        column_name: str = "stage_v_optional_note",
    ) -> dict[str, Any]:
        """Verify nullable writer schema propagation through Bronze/Silver/serving."""

        from scripts.serving.clickhouse import clickhouse_query, format_ch_relation

        if not re.fullmatch(r"[A-Za-z0-9_]+", column_name):
            raise ValueError(f"Invalid nullable column name: {column_name!r}")

        def sql_string(value: str) -> str:
            return "'" + value.replace("'", "''") + "'"

        def one(rows: list[dict[str, object]], label: str) -> dict[str, object]:
            if not rows or not isinstance(rows[0], dict):
                raise RuntimeError(f"ClickHouse probe returned no {label} row")
            return dict(rows[0])

        def int_value(value: object, label: str, positive: bool = False) -> int:
            if not isinstance(value, (int, float, str)):
                raise RuntimeError(f"ClickHouse {label} is not numeric")
            try:
                result = int(value)
            except (TypeError, ValueError) as exc:
                raise RuntimeError(f"ClickHouse {label} is not numeric") from exc
            if positive and result <= 0:
                raise RuntimeError(f"ClickHouse {label} must be positive")
            return result

        def bool_value(value: object, label: str) -> bool:
            if isinstance(value, bool):
                return value
            if isinstance(value, (int, float)):
                return bool(value)
            if isinstance(value, str):
                normalized = value.strip().lower()
                if normalized in {"1", "true"}:
                    return True
                if normalized in {"0", "false"}:
                    return False
            raise RuntimeError(f"ClickHouse {label} is not boolean")

        def schema_has_nullable_field(value: object) -> bool:
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    return False
            if isinstance(value, list):
                return any(schema_has_nullable_field(item) for item in value)
            if not isinstance(value, dict):
                return False

            fields = value.get("fields")
            if isinstance(fields, list):
                for field in fields:
                    if not isinstance(field, dict) or field.get("name") != column_name:
                        continue
                    field_type = field.get("type")
                    nullable_union = isinstance(field_type, list) and any(
                        item == "null" for item in field_type
                    )
                    if (
                        nullable_union
                        and "default" in field
                        and field.get("default") is None
                    ):
                        return True
            return any(schema_has_nullable_field(item) for item in value.values())

        def schema_field_names(value: object) -> set[str]:
            """Collect Avro field names from nested record definitions."""

            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    return set()
            if isinstance(value, list):
                names: set[str] = set()
                for item in value:
                    names.update(schema_field_names(item))
                return names
            if not isinstance(value, dict):
                return set()

            names = set()
            fields = value.get("fields")
            if isinstance(fields, list):
                for field in fields:
                    if isinstance(field, dict) and isinstance(field.get("name"), str):
                        names.add(field["name"])
                        names.update(schema_field_names(field.get("type")))
            for key, item in value.items():
                if key != "fields":
                    names.update(schema_field_names(item))
            return names

        customer_literal = sql_string(customer_id)
        silver_relation = format_ch_relation("lakehouse.silver.customers_changes")
        bronze_relation = format_ch_relation("lakehouse.bronze.mysql_cdc_records")
        schema_relation = format_ch_relation("lakehouse.bronze.avro_schemas")

        silver_row = one(
            clickhouse_query(
                f"""
                SELECT
                    event_id,
                    customer_id,
                    customer_city,
                    `{column_name}` AS optional_value,
                    apply_status,
                    is_deleted,
                    kafka_topic,
                    kafka_partition,
                    kafka_offset,
                    key_schema_id,
                    value_schema_id,
                    transaction_id
                FROM {silver_relation}
                WHERE customer_id = {customer_literal}
                ORDER BY kafka_offset DESC
                LIMIT 1
                """
            ),
            "Silver customer change",
        )
        event_id = silver_row.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            raise RuntimeError("Silver nullable-event row has no event_id")
        if silver_row.get("customer_city") != expected_city:
            raise RuntimeError(
                "Silver customer city mismatch: "
                + json.dumps(silver_row, sort_keys=True, default=str)
            )
        if silver_row.get("optional_value") is not None:
            raise RuntimeError(
                f"Silver nullable field {column_name} is not NULL: "
                + json.dumps(silver_row, sort_keys=True, default=str)
            )
        if str(silver_row.get("apply_status", "")).lower() != "applied":
            raise RuntimeError(
                "Nullable event was not applied in Silver: "
                + json.dumps(silver_row, sort_keys=True, default=str)
            )
        if bool_value(silver_row.get("is_deleted"), "Silver is_deleted"):
            raise RuntimeError("Nullable event is unexpectedly deleted in Silver")

        partition = int_value(
            silver_row.get("kafka_partition"), "Silver kafka_partition"
        )
        offset = int_value(silver_row.get("kafka_offset"), "Silver kafka_offset")
        value_schema_id = int_value(
            silver_row.get("value_schema_id"), "Silver value_schema_id", positive=True
        )
        bronze_row = one(
            clickhouse_query(
                f"""
                SELECT
                    event_id,
                    topic,
                    partition,
                    offset,
                    is_tombstone,
                    key_schema_id,
                    value_schema_id,
                    key_framing_valid,
                    value_framing_valid
                FROM {bronze_relation}
                WHERE topic = 'olist_cdc.olist_oltp.customers'
                  AND partition = {partition}
                  AND offset = {offset}
                  AND is_tombstone = 0
                LIMIT 1
                """
            ),
            "Bronze nullable-event",
        )
        if bronze_row.get("event_id") != event_id:
            raise RuntimeError("Bronze and Silver event IDs do not match")
        if (
            int_value(bronze_row.get("value_schema_id"), "Bronze value_schema_id")
            != value_schema_id
        ):
            raise RuntimeError("Bronze and Silver value schema IDs do not match")
        if bool_value(bronze_row.get("is_tombstone"), "Bronze is_tombstone"):
            raise RuntimeError("Nullable event was stored as a tombstone")
        if not bool_value(
            bronze_row.get("key_framing_valid"), "Bronze key_framing_valid"
        ):
            raise RuntimeError("Nullable event key framing is invalid")
        if not bool_value(
            bronze_row.get("value_framing_valid"), "Bronze value_framing_valid"
        ):
            raise RuntimeError("Nullable event value framing is invalid")
        int_value(
            bronze_row.get("key_schema_id"), "Bronze key_schema_id", positive=True
        )

        schema_row = one(
            clickhouse_query(
                f"""
                SELECT
                    schema_id,
                    fingerprint_sha256,
                    subject,
                    schema_json,
                    spark_self_contained_schema_json
                FROM {schema_relation}
                WHERE schema_id = {value_schema_id}
                LIMIT 1
                """
            ),
            "archived writer schema",
        )
        if (
            int_value(schema_row.get("schema_id"), "archived schema_id")
            != value_schema_id
        ):
            raise RuntimeError("Archived writer schema ID does not match the event")
        fingerprint = schema_row.get("fingerprint_sha256")
        if not isinstance(fingerprint, str) or not re.fullmatch(
            r"[0-9a-fA-F]{64}", fingerprint
        ):
            raise RuntimeError(
                "Archived writer schema has no valid SHA-256 fingerprint"
            )
        subject = schema_row.get("subject")
        if not isinstance(subject, str) or "customers" not in subject:
            raise RuntimeError(
                "Archived writer schema subject is missing or targets another entity"
            )
        schema_values = (
            schema_row.get("schema_json"),
            schema_row.get("spark_self_contained_schema_json"),
        )
        if not any(schema_has_nullable_field(value) for value in schema_values):
            raise RuntimeError(
                f"Archived writer schema does not contain nullable field {column_name}"
            )
        schema_names: set[str] = set()
        for value in schema_values:
            schema_names.update(schema_field_names(value))
        required_legacy_fields = {
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
        }
        missing_legacy_fields = sorted(required_legacy_fields - schema_names)
        if missing_legacy_fields:
            raise RuntimeError(
                "Nullable writer schema dropped legacy customer fields: "
                + ", ".join(missing_legacy_fields)
            )

        normalization_errors = one(
            clickhouse_query(
                f"""
                SELECT count() AS error_count
                FROM {format_ch_relation("lakehouse.audit.normalization_errors")}
                WHERE event_id = {sql_string(event_id)}
                """
            ),
            "normalization error count",
        )
        schema_violations = one(
            clickhouse_query(
                f"""
                SELECT count() AS error_count
                FROM {format_ch_relation("lakehouse.audit.schema_violations")}
                WHERE event_id = {sql_string(event_id)}
                """
            ),
            "schema violation count",
        )
        normalization_error_count = int_value(
            normalization_errors.get("error_count"), "normalization error count"
        )
        schema_violation_count = int_value(
            schema_violations.get("error_count"), "schema violation count"
        )
        if normalization_error_count != 0 or schema_violation_count != 0:
            raise RuntimeError(
                "Nullable event produced audit errors: "
                + json.dumps(
                    {
                        "normalization_errors": normalization_error_count,
                        "schema_violations": schema_violation_count,
                    },
                    sort_keys=True,
                )
            )

        serving_row = one(
            clickhouse_query(
                f"""
                SELECT customer_id, customer_city, `{column_name}` AS optional_value
                FROM serving_cdc.customers_current
                WHERE customer_id = {customer_literal}
                LIMIT 1
                """
            ),
            "serving customer",
        )
        if serving_row.get("customer_city") != expected_city:
            raise RuntimeError(
                "Serving customer city mismatch: "
                + json.dumps(serving_row, sort_keys=True, default=str)
            )
        if serving_row.get("optional_value") is not None:
            raise RuntimeError(
                f"Serving nullable field {column_name} is not NULL: "
                + json.dumps(serving_row, sort_keys=True, default=str)
            )

        return {
            "status": "VERIFIED",
            "customer_id": customer_id,
            "event_id": event_id,
            "silver": silver_row,
            "bronze": bronze_row,
            "writer_schema": {
                "schema_id": value_schema_id,
                "fingerprint_sha256": fingerprint,
                "subject": subject,
                "nullable_field": column_name,
                "legacy_fields": sorted(required_legacy_fields),
            },
            "audit": {
                "normalization_errors": normalization_error_count,
                "schema_violations": schema_violation_count,
            },
            "serving": serving_row,
        }


class AirflowProbe(BaseProbe):
    """Probe for Airflow DAGs and Task Instances."""

    def __init__(self) -> None:
        super().__init__("AirflowProbe")
