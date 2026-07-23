from __future__ import annotations

import unittest
from pathlib import Path

from scripts.parity.compare_manifests import compare_manifests
from scripts.parity.export_clickhouse_candidate import _semantic_type

ROOT = Path(__file__).resolve().parents[1]
BATCH_SQL_PATHS = [
    ROOT / "dbt/olist_analytics/models/staging/olist",
    ROOT / "dbt/olist_analytics/models/intermediate",
    ROOT / "dbt/olist_analytics/models/core",
    ROOT / "dbt/olist_analytics/models/marts",
]
BATCH_TESTS = [
    ROOT / "dbt/olist_analytics/tests/assert_batch_reconciliation_passed.sql",
    ROOT
    / "dbt/olist_analytics/tests/assert_fact_order_items_matches_staging_grain.sql",
    ROOT / "dbt/olist_analytics/tests/assert_daily_revenue_components_match.sql",
    ROOT / "dbt/olist_analytics/tests/assert_order_payment_allocations_balance.sql",
    ROOT / "dbt/olist_analytics/tests/assert_monthly_arpu_calculation.sql",
]


class ClickHousePhase4DbtGraphTests(unittest.TestCase):
    def test_batch_sql_uses_dispatched_compatibility_macros(self) -> None:
        forbidden = ("::", "to_char(", "extract(", "date_trunc(", "md5(")
        checked_files = [
            *[path for root in BATCH_SQL_PATHS for path in root.rglob("*.sql")],
            *BATCH_TESTS,
        ]
        for path in checked_files:
            sql = path.read_text(encoding="utf-8").lower()
            for token in forbidden:
                self.assertNotIn(token, sql, f"{path} still contains {token}")

    def test_fact_order_items_uses_clickhouse_insert_overwrite(self) -> None:
        sql = (ROOT / "dbt/olist_analytics/models/core/fact_order_items.sql").read_text(
            encoding="utf-8"
        )
        macro_sql = (
            ROOT
            / "dbt/olist_analytics/macros/clickhouse_incremental_partition_replacement.sql"
        ).read_text(encoding="utf-8")

        self.assertIn("target.type == 'clickhouse'", sql)
        self.assertIn("materialized='incremental'", sql)
        self.assertIn("incremental_strategy='insert_overwrite'", sql)
        self.assertIn("partition_by=", sql)
        self.assertIn("order_by=", sql)
        self.assertIn("clickhouse_drop_empty_partitions=true", sql)
        self.assertNotIn("unique_key='order_item_key'", sql.split("{% else %}")[0])
        self.assertIn("incremental_strategy='delete+insert'", sql)
        self.assertIn("drop partition id", macro_sql.lower())
        self.assertIn("replace partition id", macro_sql.lower())

    def test_dim_date_clickhouse_semantics_match_postgres_contract(self) -> None:
        macro_sql = (
            ROOT / "dbt/olist_analytics/macros/warehouse_compat.sql"
        ).read_text(encoding="utf-8")
        contract = (ROOT / "scripts/parity/postgres_oracle_relations.json").read_text(
            encoding="utf-8"
        )

        self.assertIn("toISOWeek", macro_sql)
        self.assertIn("rightPad(monthName({{ expression }}), 9, ' ')", macro_sql)
        self.assertIn('"schema": "core", "name": "dim_date"', contract)

    def test_fact_order_items_affected_partitions_cover_stale_and_moved_keys(
        self,
    ) -> None:
        model_sql = (
            ROOT / "dbt/olist_analytics/models/core/fact_order_items.sql"
        ).read_text(encoding="utf-8")
        macro_sql = (
            ROOT
            / "dbt/olist_analytics/macros/clickhouse_incremental_partition_replacement.sql"
        ).read_text(encoding="utf-8")
        edge_fixture_sql = (
            ROOT / "scripts/ci/check_clickhouse_fact_insert_overwrite_edges.py"
        ).read_text(encoding="utf-8")

        self.assertIn("not in", macro_sql.lower())
        self.assertIn(
            "source_items.source_partition_id != existing_items.existing_partition_id",
            macro_sql,
        )
        self.assertIn("clickhouse_drop_empty_partitions=true", model_sql)
        self.assertIn(
            "drop_relation_if_exists(affected_partitions_relation)", macro_sql
        )
        self.assertIn("include_empty_partition_order=False", edge_fixture_sql)
        self.assertIn("Expected partitions", edge_fixture_sql)

    def test_local_dag_routes_dbt_target_from_warehouse_target(self) -> None:
        dag_text = (ROOT / "airflow/dags/olist_modern_data_stack_local.py").read_text(
            encoding="utf-8"
        )

        self.assertIn('CLICKHOUSE_DBT_TARGET = "local_clickhouse"', dag_text)
        self.assertIn("params.warehouse_target == 'clickhouse'", dag_text)
        self.assertIn('"DBT_TARGET": dbt_target', dag_text)
        self.assertIn("--profile-target {dbt_target}", dag_text)

    def test_clickhouse_manifest_type_mapping_preserves_semantics(self) -> None:
        self.assertEqual(_semantic_type("seller_id", "String").semantic_type, "string")
        self.assertEqual(
            _semantic_type("orders_count", "UInt64").semantic_type, "integer"
        )
        self.assertEqual(_semantic_type("is_current", "UInt8").semantic_type, "boolean")
        decimal_type = _semantic_type("total_revenue", "Nullable(Decimal(18, 2))")
        self.assertEqual(decimal_type.semantic_type, "decimal")
        self.assertEqual(decimal_type.scale, 2)

    def test_manifest_comparator_reports_hash_mismatch_sample(self) -> None:
        oracle = {
            "dataset": "unit",
            "relations": [
                {
                    "name": "marts.mart_daily_revenue",
                    "row_count": 1,
                    "duplicate_grain_count": 0,
                    "aggregate_hash": "oracle",
                    "semantic_columns": {
                        "gross_revenue": {"type": "decimal", "scale": 2}
                    },
                    "grain_keys": [["2018-01-01"]],
                    "rows": [{"grain": ["2018-01-01"], "hash": "a"}],
                    "metrics": {"measure_totals": {"gross_revenue": "10.00"}},
                }
            ],
        }
        candidate = {
            "dataset": "unit",
            "relations": [
                {
                    "name": "marts.mart_daily_revenue",
                    "row_count": 1,
                    "duplicate_grain_count": 0,
                    "aggregate_hash": "candidate",
                    "semantic_columns": {
                        "gross_revenue": {"type": "decimal", "scale": 3}
                    },
                    "grain_keys": [["2018-01-01"]],
                    "rows": [{"grain": ["2018-01-01"], "hash": "b"}],
                    "metrics": {"measure_totals": {"gross_revenue": "11.00"}},
                }
            ],
        }

        result = compare_manifests(oracle, candidate)

        self.assertEqual(result["status"], "FAIL")
        checks = {mismatch["check"] for mismatch in result["mismatches"]}
        self.assertIn("semantic_columns", checks)
        self.assertIn("aggregate_hash", checks)
        self.assertIn("row_hash", checks)
        self.assertIn("metrics", checks)


if __name__ == "__main__":
    unittest.main()
