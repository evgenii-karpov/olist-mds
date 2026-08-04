from __future__ import annotations

import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ControlPostgresContractTests(unittest.TestCase):
    def test_compose_defines_target_control_database_init_and_secret(self) -> None:
        compose = (PROJECT_ROOT / "compose.yaml").read_text(encoding="utf-8")

        self.assertIn("platform-postgres-bootstrap:", compose)
        self.assertIn(
            "./infra/control-postgres:/opt/olist/control-postgres:ro", compose
        )
        self.assertIn(
            "CONTROL_POSTGRES_DB: olist_control",
            compose,
        )
        self.assertIn(
            "CONTROL_POSTGRES_PASSWORD_FILE: /run/secrets/control_postgres_password",
            compose,
        )
        self.assertIn("control_postgres_password:", compose)
        self.assertIn(
            "serving.sync_runs",
            "\n".join(
                path.read_text(encoding="utf-8")
                for path in (
                    PROJECT_ROOT / "infra" / "control-postgres" / "initdb"
                ).glob("*.sql")
            ),
        )

    def test_control_postgres_ddl_contains_only_target_serving_state(self) -> None:
        ddl_dir = PROJECT_ROOT / "infra" / "control-postgres" / "initdb"
        ddl = "\n".join(
            path.read_text(encoding="utf-8") for path in sorted(ddl_dir.glob("*.sql"))
        )

        lowered = ddl.lower()
        self.assertIn("create schema if not exists serving", lowered)
        self.assertIn("serving.sync_runs", lowered)

    def test_control_bootstrap_applies_only_target_migrations(self) -> None:
        bootstrap = (
            PROJECT_ROOT / "infra/control-postgres/init-control-db.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("001_create_schemas.sql", bootstrap)
        self.assertIn("005_create_serving_control_tables.sql", bootstrap)
        self.assertIn("999_grant_control_role.sql", bootstrap)
        self.assertEqual(3, bootstrap.count("--file"))


if __name__ == "__main__":
    unittest.main()
