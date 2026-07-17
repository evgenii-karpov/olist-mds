from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Stage5ConfigurationTests(unittest.TestCase):
    def test_transform_audit_uses_immutable_manifest_membership(self) -> None:
        ddl = (ROOT / "infra/postgres/007_create_cdc_transform_audit.sql").read_text(
            encoding="utf-8"
        )
        runtime = (ROOT / "scripts/cdc/realtime_transform.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("cdc_transform_runs", ddl)
        self.assertIn("cdc_transform_run_files", ddl)
        self.assertIn("processed_files.manifest_uri = files.manifest_uri", runtime)
        self.assertIn("pg_advisory_lock", runtime)
        self.assertIn("pg_advisory_unlock", runtime)
        self.assertNotIn("max(_warehouse_loaded_at)", runtime.lower())

    def test_realtime_dags_have_asset_and_hourly_separation(self) -> None:
        dag = (ROOT / "airflow/dags/olist_cdc_dbt_local.py").read_text(encoding="utf-8")
        self.assertIn('TRANSFORM_DAG_ID = "olist_cdc_transform_local"', dag)
        self.assertIn('QUALITY_DAG_ID = "olist_cdc_quality_local"', dag)
        self.assertIn('Asset("olist://cdc/raw/local")', dag)
        self.assertIn("schedule=[RAW_CDC_ASSET]", dag)
        self.assertIn('schedule="0 * * * *"', dag)
        self.assertGreaterEqual(dag.count("max_active_runs=1"), 2)

    def test_all_captured_entities_have_event_current_and_history_models(self) -> None:
        model_root = ROOT / "dbt/olist_analytics/models/realtime"
        for entity in (
            "customers",
            "orders",
            "order_items",
            "order_payments",
            "order_reviews",
            "products",
            "sellers",
            "product_category_translation",
        ):
            self.assertTrue(
                (model_root / "staging" / f"stg_cdc__{entity}_events.sql").exists()
            )
            self.assertTrue(
                (model_root / "staging" / f"stg_cdc__{entity}_current.sql").exists()
            )
            self.assertTrue((model_root / "core" / f"hist_cdc__{entity}.sql").exists())

    def test_publication_is_gated_and_reversible(self) -> None:
        runtime = (ROOT / "scripts/cdc/realtime_transform.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("realtime publication requires recorded parity PASS", runtime)
        self.assertIn('"batch": ("marts.mart_daily_revenue"', runtime)
        self.assertIn('"realtime": (', runtime)
        self.assertIn("create or replace view analytics.mart_daily_revenue", runtime)

    def test_dbt_entrypoints_use_named_selectors(self) -> None:
        selectors = (ROOT / "dbt/olist_analytics/selectors.yml").read_text(
            encoding="utf-8"
        )
        for selector in (
            "batch",
            "realtime_transform",
            "realtime_quality",
            "realtime_parity",
        ):
            self.assertIn(f"- name: {selector}", selectors)
        self.assertIn("method: package\n          value: elementary", selectors)

        for dag_name in (
            "olist_modern_data_stack_local.py",
            "olist_modern_data_stack_aws.py",
        ):
            dag = (ROOT / "airflow/dags" / dag_name).read_text(encoding="utf-8")
            self.assertIn("dbt build --selector batch", dag)

        runtime = (ROOT / "scripts/cdc/realtime_transform.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('"realtime_transform"', runtime)
        self.assertIn('"realtime_quality"', runtime)
        self.assertIn('"realtime_parity"', runtime)

    def test_parity_models_are_an_explicit_bridge(self) -> None:
        parity_root = ROOT / "dbt/olist_analytics/models/parity"
        old_root = ROOT / "dbt/olist_analytics/models/realtime/core"
        for name in (
            "realtime_parity_report.sql",
            "realtime_parity_checksums.sql",
            "realtime_parity_grain_diffs.sql",
        ):
            self.assertTrue((parity_root / name).exists())
            self.assertFalse((old_root / name).exists())

    def test_stage5_disposable_check_exercises_both_parity_comparators(self) -> None:
        checker = (ROOT / "scripts/ci/check_stage5_cdc_integration.py").read_text(
            encoding="utf-8"
        )
        for fragment in (
            "verify_parity_comparator_sensitivity",
            "dbt_utils_equality_daily_revenue",
            "realtime_parity_grain_diffs",
            "parity_status",
        ):
            self.assertIn(fragment, checker)


if __name__ == "__main__":
    unittest.main()
