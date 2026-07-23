from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class ClickHousePhase1ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.compose = yaml.safe_load(
            (ROOT / "compose.yaml").read_text(encoding="utf-8")
        )
        self.profile = yaml.safe_load(
            (ROOT / "dbt/olist_analytics/profiles.yml.example").read_text(
                encoding="utf-8"
            )
        )
        self.ddl = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((ROOT / "infra/clickhouse/initdb").glob("*.sql"))
        )

    def test_compose_uses_pinned_clickhouse_with_secret_and_safe_ports(self) -> None:
        services = self.compose["services"]
        clickhouse = services["clickhouse"]

        self.assertEqual(clickhouse["image"], "clickhouse/clickhouse-server:26.3.17.4")
        self.assertEqual(clickhouse["container_name"], "olist-clickhouse")
        self.assertIn("clickhouse_password", clickhouse["secrets"])
        self.assertEqual(
            clickhouse["environment"]["CLICKHOUSE_PASSWORD_FILE"],
            "/run/secrets/clickhouse_password",
        )
        self.assertIn("${CLICKHOUSE_HTTP_HOST_PORT:-8123}:8123", clickhouse["ports"])
        self.assertIn("${CLICKHOUSE_NATIVE_HOST_PORT:-19000}:9000", clickhouse["ports"])
        self.assertNotIn("9000:9000", clickhouse["ports"])
        self.assertEqual(clickhouse["ulimits"]["nofile"]["soft"], 262144)

        init = services["clickhouse-init"]
        self.assertEqual(
            init["depends_on"]["clickhouse"]["condition"], "service_healthy"
        )
        self.assertIn("infra/clickhouse/initdb", "\n".join(init["volumes"]))

    def test_airflow_keeps_local_pg_default_and_resolves_clickhouse_secret(
        self,
    ) -> None:
        airflow = self.compose["services"]["airflow"]
        environment = airflow["environment"]

        self.assertEqual(environment["DBT_TARGET"], "${DBT_TARGET:-local_pg}")
        self.assertEqual(environment["CLICKHOUSE_HOST"], "clickhouse")
        self.assertEqual(
            environment["CLICKHOUSE_PASSWORD_FILE"], "/run/secrets/clickhouse_password"
        )
        self.assertIn("clickhouse_password", airflow["secrets"])
        self.assertEqual(
            airflow["depends_on"]["clickhouse-init"]["condition"],
            "service_completed_successfully",
        )

    def test_dbt_and_elementary_define_local_clickhouse_outputs(self) -> None:
        for profile_name, schema in (
            ("olist_analytics", "{{ env_var('CLICKHOUSE_DATABASE', 'analytics') }}"),
            ("elementary", "elementary"),
        ):
            output = self.profile[profile_name]["outputs"]["local_clickhouse"]
            self.assertEqual(output["type"], "clickhouse")
            self.assertEqual(output["driver"], "http")
            self.assertEqual(output["schema"], schema)
            self.assertEqual(output["custom_settings"]["join_use_nulls"], 1)

        self.assertEqual(
            self.profile["olist_analytics"]["target"],
            "{{ env_var('DBT_TARGET', 'local_pg') }}",
        )

    def test_clickhouse_ddl_matches_phase1_storage_contract(self) -> None:
        self.assertEqual(self.ddl.count("CREATE TABLE IF NOT EXISTS raw_data."), 11)
        self.assertEqual(self.ddl.count("CREATE TABLE IF NOT EXISTS raw_cdc."), 8)
        self.assertIn("CREATE DATABASE IF NOT EXISTS analytics", self.ddl)
        self.assertIn("ENGINE = MergeTree", self.ddl)
        self.assertIn("ENGINE = ReplacingMergeTree(_warehouse_loaded_at)", self.ddl)
        self.assertIn("PARTITION BY _batch_id", self.ddl)
        self.assertIn("ORDER BY (_topic, _partition, _offset)", self.ddl)
        self.assertIn("DateTime64(6, 'UTC')", self.ddl)
        self.assertIn("pipeline_runtime.cdc_transform_run_files", self.ddl)
        self.assertIn("TTL selected_at + INTERVAL 7 DAY DELETE", self.ddl)
        self.assertNotIn("PostgreSQL", self.ddl)
        self.assertNotIn("ENGINE = PostgreSQL", self.ddl)


if __name__ == "__main__":
    unittest.main()
