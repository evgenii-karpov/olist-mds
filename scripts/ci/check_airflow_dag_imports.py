"""Validate the exact target Airflow DAG inventory and imports."""

from __future__ import annotations

import json
import os
from pathlib import Path

# Keep the import-only CI check away from repository-mounted Airflow state.
os.environ.setdefault("AIRFLOW_HOME", "/tmp/airflow")
os.environ.setdefault("AIRFLOW__LOGGING__BASE_LOG_FOLDER", "/tmp/airflow/logs")

from airflow.dag_processing.dagbag import DagBag

TARGET_DAG_FILES = {
    "olist_lakehouse_maintenance.py",
    "olist_lakehouse_serving.py",
}
EXPECTED_DAG_IDS = {
    "olist_lakehouse_maintenance",
    "olist_lakehouse_serving_sync",
    "olist_lakehouse_quality",
    "olist_lakehouse_serving_rebuild",
}


def airflow_dags_folder() -> Path:
    configured_folder = os.environ.get("AIRFLOW__CORE__DAGS_FOLDER")
    if configured_folder:
        return Path(configured_folder)
    return Path("/opt/airflow/dags")


def main() -> None:
    dags_dir = airflow_dags_folder()
    dag_bag = DagBag(dag_folder=str(dags_dir))
    if dag_bag.import_errors:
        print(json.dumps(dag_bag.import_errors, indent=2, sort_keys=True))
        raise SystemExit(1)

    imported_target_ids = {
        dag_id
        for dag_id, dag in dag_bag.dags.items()
        if Path(dag.fileloc).name in TARGET_DAG_FILES
    }
    if imported_target_ids != EXPECTED_DAG_IDS:
        print(
            json.dumps(
                {
                    "expected_target_dag_ids": sorted(EXPECTED_DAG_IDS),
                    "imported_target_dag_ids": sorted(imported_target_ids),
                    "status": "FAIL",
                },
                indent=2,
                sort_keys=True,
            )
        )
        raise SystemExit(1)

    for filename in sorted(TARGET_DAG_FILES):
        source = (dags_dir / filename).read_text(encoding="utf-8")
        if "dbt/olist_analytics" in source or "olist_analytics" in source:
            raise SystemExit(f"legacy dbt path found in target DAG: {filename}")

    print(
        json.dumps(
            {
                "dags_dir": str(dags_dir),
                "imported_dag_count": len(dag_bag.dags),
                "target_dag_ids": sorted(imported_target_ids),
                "status": "PASS",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
