"""Exercise ClickHouse fact insert_overwrite moved/delete/empty-partition edges."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import clickhouse_connect

RAW_TABLES = (
    "customers",
    "geolocation",
    "order_items",
    "order_payments",
    "order_reviews",
    "orders",
    "products",
    "sellers",
    "product_category_translation",
    "customer_profile_changes",
    "product_attribute_changes",
)
DERIVED_DATABASES = (
    "staging",
    "intermediate",
    "core",
    "marts",
    "snapshots",
    "elementary",
)
PROJECT_DIR = PROJECT_ROOT / "dbt/olist_analytics"
PROFILES_DIR = PROJECT_ROOT / "dbt/olist_analytics"


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _password(args: argparse.Namespace) -> str:
    if args.clickhouse_password:
        return args.clickhouse_password
    if args.clickhouse_password_file:
        return Path(args.clickhouse_password_file).read_text(encoding="utf-8").strip()
    return os.getenv("CLICKHOUSE_PASSWORD", "olist")


def _client(args: argparse.Namespace) -> Any:
    return clickhouse_connect.get_client(
        host=args.clickhouse_host,
        port=args.clickhouse_port,
        username=args.clickhouse_user,
        password=_password(args),
        database=args.clickhouse_database,
    )


def _assert_local(args: argparse.Namespace) -> None:
    if args.clickhouse_host not in {"localhost", "127.0.0.1"}:
        raise SystemExit(
            "This destructive fixture is only allowed against local ClickHouse."
        )


def _reset_clickhouse(client: Any) -> None:
    for table in RAW_TABLES:
        client.command(f"truncate table if exists raw_data.{table}")
    for database in DERIVED_DATABASES:
        client.command(f"drop database if exists {database}")
        client.command(f"create database if not exists {database}")


def _insert(
    client: Any, table: str, columns: list[str], rows: list[tuple[Any, ...]]
) -> None:
    if rows:
        client.insert(f"raw_data.{table}", rows, column_names=columns)


def _load_dimension_rows(client: Any, loaded_at: datetime) -> None:
    _insert(
        client,
        "customers",
        [
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
            "_batch_id",
            "_loaded_at",
            "_source_file",
            "_source_system",
        ],
        [
            (
                "customer_move",
                "unique_move",
                "01001",
                "sao paulo",
                "SP",
                "edge",
                loaded_at,
                "edge",
                "edge",
            ),
            (
                "customer_empty",
                "unique_empty",
                "01002",
                "sao paulo",
                "SP",
                "edge",
                loaded_at,
                "edge",
                "edge",
            ),
            (
                "customer_stay",
                "unique_stay",
                "01003",
                "sao paulo",
                "SP",
                "edge",
                loaded_at,
                "edge",
                "edge",
            ),
        ],
    )
    _insert(
        client,
        "products",
        [
            "product_id",
            "product_category_name",
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
            "_batch_id",
            "_loaded_at",
            "_source_file",
            "_source_system",
        ],
        [
            (
                "product_a",
                "category_a",
                10,
                20,
                1,
                100,
                10,
                10,
                10,
                "edge",
                loaded_at,
                "edge",
                "edge",
            ),
            (
                "product_b",
                "category_b",
                11,
                21,
                1,
                200,
                20,
                20,
                20,
                "edge",
                loaded_at,
                "edge",
                "edge",
            ),
        ],
    )
    _insert(
        client,
        "sellers",
        [
            "seller_id",
            "seller_zip_code_prefix",
            "seller_city",
            "seller_state",
            "_batch_id",
            "_loaded_at",
            "_source_file",
            "_source_system",
        ],
        [("seller_a", "02001", "sao paulo", "SP", "edge", loaded_at, "edge", "edge")],
    )
    _insert(
        client,
        "product_category_translation",
        [
            "product_category_name",
            "product_category_name_english",
            "_batch_id",
            "_loaded_at",
            "_source_file",
            "_source_system",
        ],
        [
            ("category_a", "category a", "edge", loaded_at, "edge", "edge"),
            ("category_b", "category b", "edge", loaded_at, "edge", "edge"),
        ],
    )


def _replace_orders_and_items(
    client: Any,
    loaded_at: datetime,
    include_empty_partition_order: bool,
) -> None:
    client.command("truncate table raw_data.orders")
    client.command("truncate table raw_data.order_items")
    client.command("truncate table raw_data.order_payments")
    orders = [
        (
            "order_move",
            "customer_move",
            "delivered",
            _timestamp("2018-02-15 10:00:00"),
            _timestamp("2018-02-15 10:10:00"),
            _timestamp("2018-02-16 10:00:00"),
            _timestamp("2018-02-18 10:00:00"),
            _timestamp("2018-02-20 10:00:00"),
            "edge",
            loaded_at,
            "edge",
            "edge",
        ),
        (
            "order_stay",
            "customer_stay",
            "delivered",
            _timestamp("2018-02-10 10:00:00"),
            _timestamp("2018-02-10 10:10:00"),
            _timestamp("2018-02-11 10:00:00"),
            _timestamp("2018-02-12 10:00:00"),
            _timestamp("2018-02-20 10:00:00"),
            "edge",
            loaded_at,
            "edge",
            "edge",
        ),
    ]
    items = [
        (
            "order_move",
            1,
            "product_a",
            "seller_a",
            _timestamp("2018-02-16 10:00:00"),
            Decimal("100.00"),
            Decimal("10.00"),
            "edge",
            loaded_at,
            "edge",
            "edge",
        ),
        (
            "order_stay",
            1,
            "product_b",
            "seller_a",
            _timestamp("2018-02-11 10:00:00"),
            Decimal("200.00"),
            Decimal("20.00"),
            "edge",
            loaded_at,
            "edge",
            "edge",
        ),
    ]
    payments = [
        (
            "order_move",
            1,
            "credit_card",
            1,
            Decimal("110.00"),
            "edge",
            loaded_at,
            "edge",
            "edge",
        ),
        (
            "order_stay",
            1,
            "credit_card",
            1,
            Decimal("220.00"),
            "edge",
            loaded_at,
            "edge",
            "edge",
        ),
    ]
    if include_empty_partition_order:
        orders.append(
            (
                "order_empty",
                "customer_empty",
                "delivered",
                _timestamp("2018-01-20 10:00:00"),
                _timestamp("2018-01-20 10:10:00"),
                _timestamp("2018-01-21 10:00:00"),
                _timestamp("2018-01-22 10:00:00"),
                _timestamp("2018-01-30 10:00:00"),
                "edge",
                loaded_at,
                "edge",
                "edge",
            )
        )
        items.append(
            (
                "order_empty",
                1,
                "product_a",
                "seller_a",
                _timestamp("2018-01-21 10:00:00"),
                Decimal("50.00"),
                Decimal("5.00"),
                "edge",
                loaded_at,
                "edge",
                "edge",
            )
        )
        payments.append(
            (
                "order_empty",
                1,
                "credit_card",
                1,
                Decimal("55.00"),
                "edge",
                loaded_at,
                "edge",
                "edge",
            )
        )
        orders[0] = (
            "order_move",
            "customer_move",
            "delivered",
            _timestamp("2018-01-15 10:00:00"),
            _timestamp("2018-01-15 10:10:00"),
            _timestamp("2018-01-16 10:00:00"),
            _timestamp("2018-01-18 10:00:00"),
            _timestamp("2018-01-30 10:00:00"),
            "edge",
            loaded_at,
            "edge",
            "edge",
        )
        items[0] = (
            "order_move",
            1,
            "product_a",
            "seller_a",
            _timestamp("2018-01-16 10:00:00"),
            Decimal("100.00"),
            Decimal("10.00"),
            "edge",
            loaded_at,
            "edge",
            "edge",
        )

    _insert(
        client,
        "orders",
        [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
            "_batch_id",
            "_loaded_at",
            "_source_file",
            "_source_system",
        ],
        orders,
    )
    _insert(
        client,
        "order_items",
        [
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
            "_batch_id",
            "_loaded_at",
            "_source_file",
            "_source_system",
        ],
        items,
    )
    _insert(
        client,
        "order_payments",
        [
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value",
            "_batch_id",
            "_loaded_at",
            "_source_file",
            "_source_system",
        ],
        payments,
    )


def _dbt_build(full_refresh: bool) -> None:
    command = [
        "uv",
        "run",
        "dbt",
        "build",
        "--project-dir",
        str(PROJECT_DIR),
        "--profiles-dir",
        str(PROFILES_DIR),
        "--target",
        "local_clickhouse",
        "--select",
        "+fact_order_items",
        "--exclude",
        "resource_type:test",
        "--vars",
        '{"batch_date":"2018-09-01","lookback_days":3}',
        "--no-partial-parse",
        "--quiet",
        "--warn-error-options",
        '{"error": ["NoNodesForSelectionCriteria"]}',
    ]
    if full_refresh:
        command.append("--full-refresh")
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def _active_fact_partitions(client: Any) -> list[tuple[str, int]]:
    return client.query(
        """
        select partition_id, sum(rows)
        from system.parts
        where active and database = 'core' and table = 'fact_order_items'
        group by partition_id
        order by partition_id
        """
    ).result_rows


def _assert_rows(client: Any, expected_partitions: list[tuple[str, int]]) -> None:
    partitions = _active_fact_partitions(client)
    if partitions != expected_partitions:
        raise AssertionError(
            f"Expected partitions {expected_partitions}, got {partitions}"
        )
    rows = client.query(
        """
        select order_id, toYYYYMM(toDate(order_purchase_timestamp)) as purchase_month
        from core.fact_order_items
        order by order_id
        """
    ).result_rows
    if rows != [("order_move", 201802), ("order_stay", 201802)]:
        raise AssertionError(f"Unexpected fact rows after incremental edge run: {rows}")
    helper_count = client.query(
        """
        select count()
        from system.tables
        where database = 'core' and name = 'fact_order_items__affected_partitions'
        """
    ).first_row[0]
    if helper_count != 0:
        raise AssertionError("Affected partitions helper table was not dropped")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--clickhouse-host", default=os.getenv("CLICKHOUSE_HOST", "localhost")
    )
    parser.add_argument(
        "--clickhouse-port", type=int, default=int(os.getenv("CLICKHOUSE_PORT", "8123"))
    )
    parser.add_argument(
        "--clickhouse-user", default=os.getenv("CLICKHOUSE_USER", "olist")
    )
    parser.add_argument("--clickhouse-password")
    parser.add_argument(
        "--clickhouse-password-file",
        default="docker/secrets/dev/clickhouse_password.txt",
    )
    parser.add_argument(
        "--clickhouse-database", default=os.getenv("CLICKHOUSE_DATABASE", "analytics")
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    _assert_local(args)
    client = _client(args)
    try:
        _reset_clickhouse(client)
        _load_dimension_rows(client, _timestamp("2018-01-01 00:00:00"))
        _replace_orders_and_items(
            client,
            _timestamp("2018-01-01 00:00:00"),
            include_empty_partition_order=True,
        )
        _dbt_build(full_refresh=True)
        initial_partitions = _active_fact_partitions(client)
        if initial_partitions != [("201801", 2), ("201802", 1)]:
            raise AssertionError(
                f"Unexpected baseline partitions: {initial_partitions}"
            )

        _replace_orders_and_items(
            client,
            _timestamp("2018-01-02 00:00:00"),
            include_empty_partition_order=False,
        )
        _dbt_build(full_refresh=False)
        _assert_rows(client, [("201802", 2)])
        print(
            "ClickHouse fact_order_items insert_overwrite edge fixture passed: "
            "moved key, stale key removal, and empty partition drop verified."
        )
    finally:
        client.close()


if __name__ == "__main__":
    main()
