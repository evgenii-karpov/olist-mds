from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = ROOT / "dbt/olist_clickhouse"

PHYSICAL_MODELS = {
    "dim_date",
    "dim_order_status",
    "dim_seller",
    "dim_customer_scd2",
    "dim_product_scd2",
    "fact_order_items",
    "mart_daily_revenue",
    "mart_monthly_arpu",
}


class ClickHouseDbtProjectContractTests(unittest.TestCase):
    def test_project_is_clickhouse_only_and_has_exact_physical_graph(self) -> None:
        project = yaml.safe_load(
            (PROJECT_ROOT / "dbt_project.yml").read_text(encoding="utf-8")
        )
        profile = yaml.safe_load(
            (PROJECT_ROOT / "profiles.yml.example").read_text(encoding="utf-8")
        )
        physical_models = {
            path.stem for path in (PROJECT_ROOT / "models/gold").glob("*.sql")
        }

        self.assertEqual(project["name"], "olist_clickhouse")
        self.assertEqual(physical_models, PHYSICAL_MODELS)
        self.assertEqual(
            set(profile["olist_clickhouse"]["outputs"]), {"local_clickhouse"}
        )
        self.assertEqual(
            profile["olist_clickhouse"]["outputs"]["local_clickhouse"]["type"],
            "clickhouse",
        )

        project_code = "\n".join(
            path.read_text(encoding="utf-8")
            for path in PROJECT_ROOT.rglob("*")
            if path.is_file() and path.suffix in {".sql", ".yml"}
        ).lower()
        self.assertNotIn("target.type", project_code)
        self.assertNotIn("adapter.dispatch", project_code)
        self.assertNotIn("redshift", project_code)
        self.assertNotIn("bigquery", project_code)

    def test_all_gold_models_are_run_partitioned_and_publish_stable_views(self) -> None:
        for path in (PROJECT_ROOT / "models/gold").glob("*.sql"):
            sql = path.read_text(encoding="utf-8")
            with self.subTest(model=path.stem):
                self.assertIn("incremental_strategy='insert_overwrite'", sql)
                self.assertIn("partition_by='sync_run_seq'", sql)
                self.assertIn("candidate_run_columns()", sql)
                self.assertIn("create_or_replace_gold_view()", sql)

        hook = (PROJECT_ROOT / "macros/run_context.sql").read_text(encoding="utf-8")
        self.assertIn("CREATE OR REPLACE VIEW gold.", hook)
        self.assertIn("publication_status = 'PUBLISHED'", hook)
        self.assertIn("* EXCEPT (sync_run_seq, sync_run_id)", hook)
        self.assertIn("this.identifier == 'mart_daily_revenue'", hook)
        self.assertIn("this.identifier == 'mart_monthly_arpu'", hook)

    def test_source_interface_is_complete(self) -> None:
        source_yaml = yaml.safe_load(
            (PROJECT_ROOT / "models/_sources.yml").read_text(encoding="utf-8")
        )
        serving = next(
            source
            for source in source_yaml["sources"]
            if source["name"] == "serving_cdc"
        )
        table_names = {table["name"] for table in serving["tables"]}
        expected = {
            f"{entity}_{suffix}"
            for entity in (
                "customers",
                "orders",
                "order_items",
                "order_payments",
                "order_reviews",
                "products",
                "sellers",
                "product_category_translation",
            )
            for suffix in ("events", "current_versions")
        }
        self.assertEqual(table_names, expected)

    def test_business_formulas_and_scd2_rules_are_explicit(self) -> None:
        allocation = (
            PROJECT_ROOT / "models/intermediate/int_order_payment_allocations.sql"
        ).read_text(encoding="utf-8")
        fact = (PROJECT_ROOT / "models/gold/fact_order_items.sql").read_text(
            encoding="utf-8"
        )
        customer = (PROJECT_ROOT / "models/gold/dim_customer_scd2.sql").read_text(
            encoding="utf-8"
        )
        product = (PROJECT_ROOT / "models/gold/dim_product_scd2.sql").read_text(
            encoding="utf-8"
        )
        source_state_macros = (PROJECT_ROOT / "macros/source_state.sql").read_text(
            encoding="utf-8"
        )

        self.assertIn("order_payment_value", allocation)
        self.assertIn("item_gross_amount", allocation)
        self.assertIn("order_gross_amount", allocation)
        self.assertIn("round(", allocation)
        self.assertIn("order_gross_amount = 0", allocation)
        self.assertIn("gross_item_amount", fact)
        self.assertIn("delivery_delay_days", fact)
        self.assertIn("is_delivered_late", fact)
        self.assertIn("scd_valid_from('events')", customer)
        self.assertIn("1900-01-01 00:00:00", source_state_macros)
        self.assertIn("previous_dimension_row_hash", customer)
        self.assertIn("translation_driven", product)
        self.assertIn("previous_dimension_row_hash", product)
        self.assertIn("product_rank = 1", product)
        self.assertIn("product_category_name = translation_category_name", product)

        source_state = (PROJECT_ROOT / "macros/source_state.sql").read_text(
            encoding="utf-8"
        )
        self.assertIn("sync_run_seq = {{ sync_run_seq_sql() }}", source_state)
        self.assertIn("publication_status = 'PUBLISHED'", source_state)
        self.assertNotIn("sync_run_seq <=", source_state)

    def test_secret_wrapper_reads_only_file_based_input(self) -> None:
        wrapper = (PROJECT_ROOT / "bin/run-dbt.sh").read_text(encoding="utf-8")
        self.assertIn("CLICKHOUSE_PASSWORD_FILE", wrapper)
        self.assertIn("set +x", wrapper)
        self.assertIn("must contain exactly one line", wrapper)
        self.assertNotIn('echo "${CLICKHOUSE_PASSWORD}', wrapper)

    def test_gold_cleanup_is_finite_guarded_and_not_automatic(self) -> None:
        cleanup = (PROJECT_ROOT / "macros/cleanup_gold_partitions.sql").read_text(
            encoding="utf-8"
        )
        project = (PROJECT_ROOT / "dbt_project.yml").read_text(encoding="utf-8")

        self.assertIn("keep_published=2", cleanup)
        self.assertIn("dry_run=true", cleanup)
        self.assertIn("DROP PARTITION", cleanup)
        self.assertIn("current and previous published runs", cleanup)
        self.assertNotIn("on-run-end", project)


if __name__ == "__main__":
    unittest.main()
