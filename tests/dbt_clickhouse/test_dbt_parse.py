from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = ROOT / "dbt/olist_clickhouse"


class ClickHouseDbtParseSmokeTests(unittest.TestCase):
    def test_project_parses_with_explicit_run_contract(self) -> None:
        dbt = shutil.which("dbt")
        self.assertIsNotNone(dbt, "dbt executable is required by the project")

        with tempfile.TemporaryDirectory(prefix="olist-dbt-profile-") as temp_dir:
            profiles_dir = Path(temp_dir)
            shutil.copyfile(
                PROJECT_ROOT / "profiles.yml.example",
                profiles_dir / "profiles.yml",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "CLICKHOUSE_PASSWORD": "parse-only",
                    "DBT_TARGET": "local_clickhouse",
                }
            )
            result = subprocess.run(
                [
                    str(dbt),
                    "parse",
                    "--project-dir",
                    str(PROJECT_ROOT),
                    "--profiles-dir",
                    str(profiles_dir),
                    "--no-partial-parse",
                    "--vars",
                    '{"sync_run_seq": 1, "sync_run_id": "parse-smoke"}',
                ],
                cwd=ROOT,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
                timeout=60,
            )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"dbt parse failed:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )

        manifest = json.loads(
            (PROJECT_ROOT / "target/manifest.json").read_text(encoding="utf-8")
        )
        physical_models = {
            node["name"]
            for node in manifest["nodes"].values()
            if node["resource_type"] == "model"
            and node["original_file_path"].replace("\\", "/").startswith("models/gold/")
        }
        self.assertEqual(
            physical_models,
            {
                "dim_date",
                "dim_order_status",
                "dim_seller",
                "dim_customer_scd2",
                "dim_product_scd2",
                "fact_order_items",
                "mart_daily_revenue",
                "mart_monthly_arpu",
            },
        )


if __name__ == "__main__":
    unittest.main()
