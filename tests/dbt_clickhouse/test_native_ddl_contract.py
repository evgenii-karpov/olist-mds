from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DDL_ROOT = ROOT / "infra/clickhouse/lakehouse"

ENTITIES = {
    "customers",
    "orders",
    "order_items",
    "order_payments",
    "order_reviews",
    "products",
    "sellers",
    "product_category_translation",
}


class NativeLakehouseDdlContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.event_ddl = (DDL_ROOT / "003_create_event_tables.sql").read_text(
            encoding="utf-8"
        )
        cls.current_ddl = (
            DDL_ROOT / "004_create_current_version_tables.sql"
        ).read_text(encoding="utf-8")
        cls.views_ddl = (DDL_ROOT / "005_create_stable_current_views.sql").read_text(
            encoding="utf-8"
        )

    def test_exactly_eight_event_and_current_version_tables_exist(self) -> None:
        event_entities = set(
            re.findall(r"serving_cdc\.([a-z_]+)_events", self.event_ddl)
        )
        current_entities = set(
            re.findall(r"serving_cdc\.([a-z_]+)_current_versions", self.current_ddl)
        )
        self.assertEqual(event_entities, ENTITIES)
        self.assertEqual(current_entities, ENTITIES)

    def test_event_tables_use_run_partitions_and_transport_order(self) -> None:
        self.assertEqual(self.event_ddl.count("ENGINE = MergeTree"), 8)
        self.assertEqual(self.event_ddl.count("PARTITION BY sync_run_seq"), 8)
        self.assertEqual(
            self.event_ddl.count("ORDER BY (kafka_partition, kafka_offset)"), 8
        )
        for column in (
            "event_id String",
            "transaction_id Nullable(String)",
            "source_server_id Nullable(UInt64)",
            "schema_fingerprint Nullable(String)",
            "row_hash Nullable(String)",
            "contract_version UInt32",
        ):
            self.assertEqual(
                len(re.findall(rf"^    {re.escape(column)},?$", self.event_ddl, re.M)),
                8,
            )

    def test_event_business_columns_are_nullable_for_rejected_rows(self) -> None:
        for declaration in (
            "customer_id Nullable(String)",
            "order_id Nullable(String)",
            "order_item_id Nullable(Int32)",
            "payment_sequential Nullable(Int32)",
            "review_id Nullable(String)",
            "product_id Nullable(String)",
            "seller_id Nullable(String)",
            "product_category_name_english Nullable(String)",
        ):
            self.assertIn(declaration, self.event_ddl)

    def test_current_tables_use_replacing_merge_tree_without_partitions(self) -> None:
        self.assertEqual(
            self.current_ddl.count("ENGINE = ReplacingMergeTree(kafka_offset)"),
            8,
        )
        self.assertEqual(self.current_ddl.count("PARTITION BY sync_run_seq"), 8)
        self.assertEqual(self.current_ddl.count("sync_run_seq UInt64"), 8)
        self.assertEqual(self.current_ddl.count("is_deleted Bool"), 8)

    def test_stable_views_hide_unpublished_and_deleted_versions(self) -> None:
        self.assertEqual(self.views_ddl.count("CREATE VIEW IF NOT EXISTS"), 8)
        self.assertEqual(self.views_ddl.count("publication_status = 'PUBLISHED'"), 8)
        self.assertEqual(self.views_ddl.count("sync_run_seq IN"), 8)
        self.assertEqual(self.views_ddl.count("row_number() OVER"), 8)
        self.assertEqual(
            self.views_ddl.count("WHERE _version_rank = 1 AND NOT is_deleted"), 8
        )
        self.assertNotIn("sync_run_seq <= published_seq", self.views_ddl)

    def test_catalog_template_contains_no_committed_credential(self) -> None:
        template = (DDL_ROOT / "catalog.sql.template").read_text(encoding="utf-8")
        bootstrap = (DDL_ROOT / "bootstrap-catalog.sh").read_text(encoding="utf-8")

        self.assertIn("http://polaris:8181/api/catalog", template)
        self.assertIn("warehouse = 'olist_lakehouse'", template)
        self.assertIn("__POLARIS_CATALOG_CREDENTIAL_HEX__", template)
        self.assertIn("unhex(", template)
        self.assertIn("set +x", bootstrap)
        self.assertIn("POLARIS_PRINCIPAL_SECRET_FILE", bootstrap)
        self.assertIn("CLICKHOUSE_PASSWORD_FILE", bootstrap)
        self.assertIn("chmod 0600", bootstrap)
        self.assertIn("--config-file", bootstrap)
        self.assertIn("od -An -tx1", bootstrap)
        self.assertIn("must contain exactly one line", bootstrap)
        self.assertNotIn("escaped_credential", bootstrap)
        self.assertNotIn("--password", bootstrap)
        self.assertIn("printf '%s\\n'", bootstrap)

    def test_learning_test_covers_final_argmax_and_delete_order(self) -> None:
        learning_sql = (
            DDL_ROOT / "tests/001_replacing_merge_tree_learning.sql"
        ).read_text(encoding="utf-8")
        self.assertIn("plain SELECT", learning_sql)
        self.assertIn(" FINAL", learning_sql)
        self.assertIn("argMax", learning_sql)
        self.assertIn("latest_is_deleted", learning_sql)
        self.assertNotIn("OPTIMIZE TABLE", learning_sql.upper())

    def test_catalog_smoke_lists_counts_and_time_travels_customers(self) -> None:
        smoke_script = (DDL_ROOT / "tests/run-catalog-smoke.sh").read_text(
            encoding="utf-8"
        )
        smoke_sql = (DDL_ROOT / "tests/catalog-smoke.sql.template").read_text(
            encoding="utf-8"
        )

        self.assertIn("SHOW TABLES FROM lakehouse", smoke_script)
        self.assertIn("silver.customers_current", smoke_script)
        self.assertIn("CLICKHOUSE_PASSWORD_FILE", smoke_script)
        self.assertIn("ICEBERG_CUSTOMERS_SNAPSHOT_ID", smoke_script)
        self.assertIn("must contain exactly one line", smoke_script)
        self.assertNotIn("--password", smoke_script)
        self.assertEqual(smoke_sql.count("silver.customers_current"), 2)
        self.assertIn("count() AS current_row_count", smoke_sql)
        self.assertIn("iceberg_snapshot_id = {snapshot_id:UInt64}", smoke_sql)


if __name__ == "__main__":
    unittest.main()
