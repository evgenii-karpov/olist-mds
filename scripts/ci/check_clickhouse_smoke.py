from __future__ import annotations

import os
from pathlib import Path

import clickhouse_connect

EXPECTED_TABLES = {
    ("raw_data", "customers"),
    ("raw_data", "orders"),
    ("raw_data", "order_items"),
    ("raw_data", "order_payments"),
    ("raw_data", "order_reviews"),
    ("raw_data", "products"),
    ("raw_data", "sellers"),
    ("raw_data", "geolocation"),
    ("raw_data", "product_category_translation"),
    ("raw_data", "customer_profile_changes"),
    ("raw_data", "product_attribute_changes"),
    ("raw_cdc", "customers"),
    ("raw_cdc", "orders"),
    ("raw_cdc", "order_items"),
    ("raw_cdc", "order_payments"),
    ("raw_cdc", "order_reviews"),
    ("raw_cdc", "products"),
    ("raw_cdc", "sellers"),
    ("raw_cdc", "product_category_translation"),
    ("pipeline_runtime", "cdc_transform_run_files"),
}


def _read_password() -> str:
    if password := os.environ.get("CLICKHOUSE_PASSWORD"):
        return password

    password_file = os.environ.get("CLICKHOUSE_PASSWORD_FILE")
    if not password_file:
        return "olist"

    return Path(password_file).read_text(encoding="utf-8").rstrip("\r\n")


def main() -> None:
    client = clickhouse_connect.get_client(
        host=os.environ.get("CLICKHOUSE_HOST", "localhost"),
        port=int(os.environ.get("CLICKHOUSE_PORT", "8123")),
        username=os.environ.get("CLICKHOUSE_USER", "olist"),
        password=_read_password(),
        database=os.environ.get("CLICKHOUSE_DATABASE", "analytics"),
        secure=os.environ.get("CLICKHOUSE_SECURE", "false").lower() == "true",
    )

    version_row = client.query("SELECT version(), timezone()").first_row
    if version_row is None or len(version_row) != 2:
        raise SystemExit("ClickHouse version query returned no result.")

    version, timezone = version_row
    if timezone != "UTC":
        raise SystemExit(f"Expected ClickHouse timezone UTC, got {timezone!r}")

    rows = client.query(
        """
        SELECT database, name
        FROM system.tables
        WHERE database IN ('raw_data', 'raw_cdc', 'pipeline_runtime')
        """
    ).result_rows
    actual_tables = {(database, name) for database, name in rows}
    missing_tables = sorted(EXPECTED_TABLES - actual_tables)
    if missing_tables:
        raise SystemExit(f"Missing ClickHouse tables: {missing_tables!r}")

    print(f"ClickHouse {version} smoke check passed with {len(actual_tables)} tables.")


if __name__ == "__main__":
    main()
