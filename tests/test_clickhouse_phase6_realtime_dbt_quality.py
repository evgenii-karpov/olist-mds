from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REALTIME_SQL_PATHS = [
    ROOT / "dbt/olist_analytics/models/realtime",
    ROOT / "dbt/olist_analytics/models/parity",
]
OPERATIONAL_TESTS = [
    ROOT / "dbt/olist_analytics/tests/assert_realtime_latest_reconciliation_passed.sql",
    ROOT / "dbt/olist_analytics/tests/assert_realtime_mart_freshness.sql",
    ROOT / "dbt/olist_analytics/tests/assert_realtime_offset_continuity.sql",
]
MUTABLE_REALTIME_MODELS = [
    ROOT / "dbt/olist_analytics/models/realtime/core/dim_customer_realtime_scd2.sql",
    ROOT / "dbt/olist_analytics/models/realtime/core/dim_product_realtime_scd2.sql",
    ROOT / "dbt/olist_analytics/models/realtime/core/dim_seller_realtime.sql",
    ROOT / "dbt/olist_analytics/models/realtime/core/fact_order_items_realtime.sql",
    ROOT / "dbt/olist_analytics/models/realtime/marts/mart_daily_revenue_realtime.sql",
    ROOT / "dbt/olist_analytics/models/realtime/marts/mart_monthly_arpu_realtime.sql",
]


class ClickHousePhase6RealtimeDbtQualityTests(unittest.TestCase):
    def test_realtime_sql_uses_clickhouse_safe_compatibility_macros(self) -> None:
        forbidden = (
            "::",
            "to_char(",
            "date_trunc(",
            "string_agg(",
            "at time zone",
            "filter (",
            "incremental_strategy='merge'",
            "pre_hook",
        )
        checked_files = [
            path for root in REALTIME_SQL_PATHS for path in root.rglob("*.sql")
        ]

        for path in checked_files:
            sql = path.read_text(encoding="utf-8").lower()
            for token in forbidden:
                self.assertNotIn(token, sql, f"{path} still contains {token}")

    def test_mutable_realtime_models_use_full_table_parity_pass(self) -> None:
        for path in MUTABLE_REALTIME_MODELS:
            sql = path.read_text(encoding="utf-8")
            self.assertIn("materialized='table'", sql, str(path))
            self.assertNotIn("incremental_strategy", sql, str(path))
            self.assertNotIn("delete_impacted_", sql, str(path))

    def test_clickhouse_operational_dbt_tests_delegate_to_python(self) -> None:
        runtime = (ROOT / "scripts/cdc/realtime_transform.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("control_quality_checks", runtime)
        self.assertIn("latest_reconciliation", runtime)
        self.assertIn("offset_continuity", runtime)
        self.assertIn("mart_freshness", runtime)

        for path in OPERATIONAL_TESTS:
            sql = path.read_text(encoding="utf-8")
            self.assertIn("target.name == 'local_clickhouse'", sql)
            self.assertIn("where 1 = 0", sql)

    def test_python_publication_and_parity_support_clickhouse(self) -> None:
        runtime = (ROOT / "scripts/cdc/realtime_transform.py").read_text(
            encoding="utf-8"
        )

        self.assertIn("read_custom_parity_results_clickhouse", runtime)
        self.assertIn("publish_clickhouse_views", runtime)
        self.assertIn("create or replace view analytics.mart_daily_revenue", runtime)
        self.assertIn("not use_clickhouse_warehouse()", runtime)
        self.assertIn("DBT_TARGET", runtime)

    def test_clickhouse_runtime_projection_remains_retry_safe(self) -> None:
        runtime = (ROOT / "scripts/cdc/realtime_transform.py").read_text(
            encoding="utf-8"
        )
        ddl = " ".join(
            path.read_text(encoding="utf-8")
            for path in (ROOT / "infra/clickhouse/initdb").glob("*.sql")
        )

        self.assertIn("manifest_selection_digest", runtime)
        self.assertIn("pipeline_runtime", runtime)
        self.assertIn("ReplacingMergeTree(selected_at)", ddl)
        self.assertIn("ORDER BY (transform_run_id, object_uri)", ddl)


if __name__ == "__main__":
    unittest.main()
