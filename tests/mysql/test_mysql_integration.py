"""Opt-in integration contract for an externally provisioned disposable MySQL.

The module never starts or resets infrastructure.  Schema checks require
``OLIST_RUN_MYSQL_INTEGRATION=1``.  The mutating seed check additionally
requires ``OLIST_MYSQL_INTEGRATION_DISPOSABLE=1`` and refuses to insert unless
all nine business tables are empty.  It deliberately leaves the seeded fixture
in place so an operator, rather than this test, owns disposal of the database.
"""

from __future__ import annotations

import os
import unittest
from datetime import datetime
from pathlib import Path
from typing import Any

from scripts.simulation.database import DatabaseSettings, SimulatorRepository, connect
from scripts.simulation.seeding import seed_archive

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "olist_small" / "olist_small.zip"
BUSINESS_DATABASE = "olist_oltp"

RUN_FLAG = "OLIST_RUN_MYSQL_INTEGRATION"
DISPOSABLE_FLAG = "OLIST_MYSQL_INTEGRATION_DISPOSABLE"

EXPECTED_COUNTS = {
    "customers": 8,
    "orders": 12,
    "order_items": 16,
    "order_payments": 14,
    "order_reviews": 12,
    "products": 8,
    "sellers": 4,
    "product_category_translation": 5,
    "geolocation": 6,
}

# column_name, data_type, column_type, is_nullable, extra
EXPECTED_COLUMNS = {
    "customers": (
        ("customer_id", "varchar", "varchar(64)", "NO", ""),
        ("customer_unique_id", "varchar", "varchar(64)", "NO", ""),
        ("customer_zip_code_prefix", "varchar", "varchar(16)", "NO", ""),
        ("customer_city", "varchar", "varchar(256)", "NO", ""),
        ("customer_state", "varchar", "varchar(2)", "NO", ""),
    ),
    "geolocation": (
        ("geolocation_id", "bigint", "bigint", "NO", "auto_increment"),
        (
            "geolocation_zip_code_prefix",
            "varchar",
            "varchar(16)",
            "NO",
            "",
        ),
        ("geolocation_lat", "decimal", "decimal(18,14)", "NO", ""),
        ("geolocation_lng", "decimal", "decimal(18,14)", "NO", ""),
        ("geolocation_city", "varchar", "varchar(256)", "NO", ""),
        ("geolocation_state", "varchar", "varchar(2)", "NO", ""),
    ),
    "order_items": (
        ("order_id", "varchar", "varchar(64)", "NO", ""),
        ("order_item_id", "int", "int", "NO", ""),
        ("product_id", "varchar", "varchar(64)", "NO", ""),
        ("seller_id", "varchar", "varchar(64)", "NO", ""),
        ("shipping_limit_date", "datetime", "datetime(6)", "NO", ""),
        ("price", "decimal", "decimal(18,2)", "NO", ""),
        ("freight_value", "decimal", "decimal(18,2)", "NO", ""),
    ),
    "order_payments": (
        ("order_id", "varchar", "varchar(64)", "NO", ""),
        ("payment_sequential", "int", "int", "NO", ""),
        ("payment_type", "varchar", "varchar(32)", "NO", ""),
        ("payment_installments", "int", "int", "NO", ""),
        ("payment_value", "decimal", "decimal(18,2)", "NO", ""),
    ),
    "order_reviews": (
        ("review_id", "varchar", "varchar(64)", "NO", ""),
        ("order_id", "varchar", "varchar(64)", "NO", ""),
        ("review_score", "int", "int", "NO", ""),
        ("review_comment_title", "varchar", "varchar(1024)", "YES", ""),
        ("review_comment_message", "text", "text", "YES", ""),
        ("review_creation_date", "datetime", "datetime(6)", "NO", ""),
        ("review_answer_timestamp", "datetime", "datetime(6)", "NO", ""),
    ),
    "orders": (
        ("order_id", "varchar", "varchar(64)", "NO", ""),
        ("customer_id", "varchar", "varchar(64)", "NO", ""),
        ("order_status", "varchar", "varchar(32)", "NO", ""),
        ("order_purchase_timestamp", "datetime", "datetime(6)", "NO", ""),
        ("order_approved_at", "datetime", "datetime(6)", "YES", ""),
        (
            "order_delivered_carrier_date",
            "datetime",
            "datetime(6)",
            "YES",
            "",
        ),
        (
            "order_delivered_customer_date",
            "datetime",
            "datetime(6)",
            "YES",
            "",
        ),
        (
            "order_estimated_delivery_date",
            "datetime",
            "datetime(6)",
            "NO",
            "",
        ),
    ),
    "product_category_translation": (
        ("product_category_name", "varchar", "varchar(256)", "NO", ""),
        (
            "product_category_name_english",
            "varchar",
            "varchar(256)",
            "NO",
            "",
        ),
    ),
    "products": (
        ("product_id", "varchar", "varchar(64)", "NO", ""),
        ("product_category_name", "varchar", "varchar(256)", "YES", ""),
        ("product_name_lenght", "int", "int", "YES", ""),
        ("product_description_lenght", "int", "int", "YES", ""),
        ("product_photos_qty", "int", "int", "YES", ""),
        ("product_weight_g", "int", "int", "YES", ""),
        ("product_length_cm", "int", "int", "YES", ""),
        ("product_height_cm", "int", "int", "YES", ""),
        ("product_width_cm", "int", "int", "YES", ""),
    ),
    "sellers": (
        ("seller_id", "varchar", "varchar(64)", "NO", ""),
        ("seller_zip_code_prefix", "varchar", "varchar(16)", "NO", ""),
        ("seller_city", "varchar", "varchar(256)", "NO", ""),
        ("seller_state", "varchar", "varchar(2)", "NO", ""),
    ),
}

EXPECTED_PRIMARY_KEYS = {
    "customers": ("customer_id",),
    "geolocation": ("geolocation_id",),
    "order_items": ("order_id", "order_item_id"),
    "order_payments": ("order_id", "payment_sequential"),
    "order_reviews": ("review_id", "order_id"),
    "orders": ("order_id",),
    "product_category_translation": ("product_category_name",),
    "products": ("product_id",),
    "sellers": ("seller_id",),
}

EXPECTED_FOREIGN_KEYS = {
    ("order_items", "order_id", "orders", "order_id"),
    ("order_items", "product_id", "products", "product_id"),
    ("order_items", "seller_id", "sellers", "seller_id"),
    ("order_payments", "order_id", "orders", "order_id"),
    ("order_reviews", "order_id", "orders", "order_id"),
    ("orders", "customer_id", "customers", "customer_id"),
    (
        "products",
        "product_category_name",
        "product_category_translation",
        "product_category_name",
    ),
}

EXPECTED_CHECKS = {
    "customers": {"ck_customers_state"},
    "geolocation": {
        "ck_geolocation_lat",
        "ck_geolocation_lng",
        "ck_geolocation_state",
    },
    "order_items": {
        "ck_order_items_freight",
        "ck_order_items_price",
        "ck_order_items_sequence",
    },
    "order_payments": {
        "ck_order_payments_installments",
        "ck_order_payments_sequence",
        "ck_order_payments_type",
        "ck_order_payments_value",
    },
    "order_reviews": {
        "ck_order_reviews_score",
        "ck_review_answer_after_creation",
    },
    "orders": {
        "ck_orders_approval_after_purchase",
        "ck_orders_customer_after_purchase",
        "ck_orders_status",
    },
    "product_category_translation": set(),
    "products": {
        "ck_products_description_lenght",
        "ck_products_height_cm",
        "ck_products_length_cm",
        "ck_products_name_lenght",
        "ck_products_photos_qty",
        "ck_products_weight_g",
        "ck_products_width_cm",
    },
    "sellers": {"ck_sellers_state"},
}


def _enabled(name: str) -> bool:
    return os.environ.get(name) == "1"


@unittest.skipUnless(
    _enabled(RUN_FLAG),
    f"set {RUN_FLAG}=1 to run against an already-provisioned MySQL instance",
)
class MySQLIntegrationTests(unittest.TestCase):
    connection: Any

    @classmethod
    def setUpClass(cls) -> None:
        database = os.environ.get("MYSQL_DATABASE", BUSINESS_DATABASE)
        if database != BUSINESS_DATABASE:
            raise RuntimeError(
                f"MYSQL_DATABASE must be exactly {BUSINESS_DATABASE!r}; got {database!r}"
            )
        password_file = os.environ.get("MYSQL_PASSWORD_FILE")
        if not password_file:
            raise RuntimeError(
                "MYSQL_PASSWORD_FILE must point to the integration credential"
            )
        settings = DatabaseSettings(
            password_file=password_file,
            host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
            port=int(os.environ.get("MYSQL_PORT", "3306")),
            database=database,
            user=os.environ.get("MYSQL_USER", "olist_simulator"),
            connect_timeout=int(os.environ.get("MYSQL_CONNECT_TIMEOUT", "10")),
        )
        cls.connection = connect(settings)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.connection.close()

    def _query(self, statement: str, parameters: tuple[Any, ...] = ()) -> list[Any]:
        cursor = self.connection.cursor()
        try:
            cursor.execute(statement, parameters)
            return list(cursor.fetchall())
        finally:
            cursor.close()

    def _business_counts(self) -> dict[str, int]:
        return {
            table: int(
                self._query(f"SELECT COUNT(*) FROM `{BUSINESS_DATABASE}`.`{table}`")[0][
                    0
                ]
            )
            for table in EXPECTED_COUNTS
        }

    def test_information_schema_matches_the_exact_business_contract(self) -> None:
        table_rows = self._query(
            """
            SELECT table_name, engine, table_collation
            FROM information_schema.tables
            WHERE table_schema = %s
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """,
            (BUSINESS_DATABASE,),
        )
        observed_tables = {
            str(table): (str(engine), str(collation))
            for table, engine, collation in table_rows
        }
        self.assertEqual(
            observed_tables,
            {table: ("InnoDB", "utf8mb4_0900_bin") for table in EXPECTED_COLUMNS},
        )

        column_rows = self._query(
            """
            SELECT
                table_name,
                column_name,
                data_type,
                column_type,
                is_nullable,
                extra,
                collation_name
            FROM information_schema.columns
            WHERE table_schema = %s
            ORDER BY table_name, ordinal_position
            """,
            (BUSINESS_DATABASE,),
        )
        observed_columns: dict[str, list[tuple[str, str, str, str, str]]] = {
            table: [] for table in EXPECTED_COLUMNS
        }
        for (
            table,
            name,
            data_type,
            column_type,
            nullable,
            extra,
            collation,
        ) in column_rows:
            table_name = str(table)
            self.assertIn(table_name, observed_columns)
            normalized = (
                str(name),
                str(data_type).lower(),
                str(column_type).lower(),
                str(nullable),
                str(extra).lower(),
            )
            observed_columns[table_name].append(normalized)
            expected_collation = (
                "utf8mb4_0900_bin" if normalized[1] in {"varchar", "text"} else None
            )
            self.assertEqual(collation, expected_collation)
        self.assertEqual(
            {table: tuple(columns) for table, columns in observed_columns.items()},
            EXPECTED_COLUMNS,
        )

        primary_key_rows = self._query(
            """
            SELECT table_name, column_name
            FROM information_schema.key_column_usage
            WHERE constraint_schema = %s
              AND constraint_name = 'PRIMARY'
            ORDER BY table_name, ordinal_position
            """,
            (BUSINESS_DATABASE,),
        )
        observed_primary_keys: dict[str, list[str]] = {
            table: [] for table in EXPECTED_PRIMARY_KEYS
        }
        for table, column in primary_key_rows:
            observed_primary_keys[str(table)].append(str(column))
        self.assertEqual(
            {table: tuple(columns) for table, columns in observed_primary_keys.items()},
            EXPECTED_PRIMARY_KEYS,
        )

        foreign_key_rows = self._query(
            """
            SELECT
                table_name,
                column_name,
                referenced_table_name,
                referenced_column_name
            FROM information_schema.key_column_usage
            WHERE constraint_schema = %s
              AND referenced_table_schema = %s
            """,
            (BUSINESS_DATABASE, BUSINESS_DATABASE),
        )
        self.assertEqual(
            {tuple(str(value) for value in row) for row in foreign_key_rows},
            EXPECTED_FOREIGN_KEYS,
        )

        check_rows = self._query(
            """
            SELECT table_name, constraint_name
            FROM information_schema.table_constraints
            WHERE table_schema = %s
              AND constraint_type = 'CHECK'
            """,
            (BUSINESS_DATABASE,),
        )
        observed_checks = {table: set() for table in EXPECTED_CHECKS}
        for table, constraint in check_rows:
            observed_checks[str(table)].add(str(constraint))
        self.assertEqual(observed_checks, EXPECTED_CHECKS)

    @unittest.skipUnless(
        _enabled(DISPOSABLE_FLAG),
        f"set {DISPOSABLE_FLAG}=1 to acknowledge that MySQL is disposable",
    )
    def test_small_fixture_reseed_is_idempotent_with_exact_counts(self) -> None:
        before = self._business_counts()
        self.assertEqual(
            before,
            {table: 0 for table in EXPECTED_COUNTS},
            "Refusing to seed non-empty business tables; this test never truncates "
            f"or deletes data. Observed row counts: {before!r}",
        )

        repository = SimulatorRepository(self.connection)
        seed_arguments = {
            "random_seed": 20260801,
            "run_id": "mysql-integration-small-reseed",
            "logical_time": datetime(2020, 1, 1),
        }
        first_report = seed_archive(repository, FIXTURE, **seed_arguments)
        first_counts = self._business_counts()
        first_geolocation_ids = self._query(
            f"SELECT geolocation_id FROM `{BUSINESS_DATABASE}`.`geolocation` "
            "ORDER BY geolocation_id"
        )

        second_report = seed_archive(repository, FIXTURE, **seed_arguments)
        second_counts = self._business_counts()
        second_geolocation_ids = self._query(
            f"SELECT geolocation_id FROM `{BUSINESS_DATABASE}`.`geolocation` "
            "ORDER BY geolocation_id"
        )

        self.assertEqual(first_report, EXPECTED_COUNTS)
        self.assertEqual(second_report, EXPECTED_COUNTS)
        self.assertEqual(first_counts, EXPECTED_COUNTS)
        self.assertEqual(second_counts, EXPECTED_COUNTS)
        self.assertEqual(second_geolocation_ids, first_geolocation_ids)


if __name__ == "__main__":
    unittest.main()
