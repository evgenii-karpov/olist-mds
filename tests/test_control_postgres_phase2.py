from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ControlPostgresPhase2Tests(unittest.TestCase):
    def test_batch_control_defaults_use_control_postgres_not_warehouse(self) -> None:
        from scripts.orchestration import batch_control

        environment = {
            "POSTGRES_HOST": "warehouse-postgres",
            "POSTGRES_DB": "olist_analytics",
            "POSTGRES_USER": "olist",
            "POSTGRES_PASSWORD": "warehouse-password",
            "CONTROL_POSTGRES_HOST": "airflow-postgres",
            "CONTROL_POSTGRES_DB": "olist_control",
            "CONTROL_POSTGRES_USER": "olist_control",
            "CONTROL_POSTGRES_PASSWORD": "control-password",
        }
        argv = [
            "batch_control.py",
            "start",
            "--batch-date",
            "2018-09-01",
            "--run-id",
            "unit",
        ]

        with (
            patch.dict(os.environ, environment, clear=True),
            patch.object(sys, "argv", argv),
        ):
            args = batch_control.parse_args()

        self.assertEqual(args.host, "airflow-postgres")
        self.assertEqual(args.database, "olist_control")
        self.assertEqual(args.user, "olist_control")
        self.assertEqual(args.password, "control-password")

    def test_compose_defines_control_database_init_and_secret(self) -> None:
        compose = (PROJECT_ROOT / "compose.yaml").read_text(encoding="utf-8")

        self.assertIn("control-db-init:", compose)
        self.assertIn(
            'CONTROL_POSTGRES_DB: "${CONTROL_POSTGRES_DB:-olist_control}"',
            compose,
        )
        self.assertIn(
            "CONTROL_POSTGRES_PASSWORD_FILE: /run/secrets/control_postgres_password",
            compose,
        )
        self.assertIn("control_postgres_password:", compose)

    def test_control_postgres_ddl_excludes_warehouse_raw_tables(self) -> None:
        ddl_dir = PROJECT_ROOT / "infra" / "control-postgres" / "initdb"
        ddl = "\n".join(
            path.read_text(encoding="utf-8") for path in sorted(ddl_dir.glob("*.sql"))
        )

        self.assertIn("create schema if not exists audit", ddl)
        self.assertIn("create schema if not exists cdc_audit", ddl)
        self.assertIn("create table if not exists audit.batch_runs", ddl)
        self.assertIn("create table if not exists cdc_audit.cdc_files", ddl)
        self.assertNotIn("create table if not exists raw_cdc.", ddl)
        self.assertNotIn("create schema if not exists realtime_core", ddl)

    def test_local_batch_control_dag_no_longer_bootstraps_warehouse_ddl(self) -> None:
        dag = (
            PROJECT_ROOT / "airflow" / "dags" / "olist_modern_data_stack_local.py"
        ).read_text(encoding="utf-8")

        batch_control_function = dag.split("def batch_control_args(", maxsplit=1)[1]
        batch_control_function = batch_control_function.split(
            "def mark_batch_failed(", maxsplit=1
        )[0]
        self.assertNotIn("--bootstrap-sql-dir", batch_control_function)


if __name__ == "__main__":
    unittest.main()
