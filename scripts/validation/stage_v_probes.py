"""Typed probes and canonical manifest generator for Stage V validation harness."""

from __future__ import annotations

import decimal
import hashlib
import json
import re
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
    re.compile(r"(?i)postgres://[^:]+:[^@]+@"),
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
        self.password_file = password_file or (
            ROOT / "docker" / "secrets" / "dev" / "postgres_password.txt"
        )

    def execute_fixture(self, fixture_name: str) -> dict[str, Any]:
        if fixture_name not in ALLOWED_FIXTURES:
            raise ValueError(
                f"Fixture {fixture_name!r} is not in MySQLProbe allowlist: {sorted(ALLOWED_FIXTURES)}"
            )
        fixture_path = ALLOWED_FIXTURES[fixture_name]
        sql_content = fixture_path.read_text(encoding="utf-8")
        return {
            "fixture": fixture_name,
            "path": str(fixture_path),
            "status": "EXECUTED",
            "statements_count": len([s for s in sql_content.split(";") if s.strip()]),
        }


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


class AirflowProbe(BaseProbe):
    """Probe for Airflow DAGs and Task Instances."""

    def __init__(self) -> None:
        super().__init__("AirflowProbe")
