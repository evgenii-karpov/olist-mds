from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_gcp_serving_dag_is_finite_and_has_the_required_control_flow() -> None:
    namespace = runpy.run_path(str(ROOT / "airflow/dags/olist_gcp_serving.py"))
    dag = namespace["olist_gcp_serving_dag"]()

    expected = {
        "validate_gcp_contour",
        "acquire_gcp_serving_lease",
        "allocate_gcp_sync_run",
        "freeze_transaction_boundary",
        "wait_for_silver_progress",
        "prepare_same_run_candidate",
        "run_dbt_bigquery_candidate",
        "collect_candidate_results",
        "publish_gcp_run",
        "emit_gcp_report",
        "release_gcp_serving_lease",
    }
    assert dag.dag_id == "olist_gcp_serving"
    assert {task.task_id for task in dag.tasks} == expected
    assert dag.schedule is None
    assert dag.max_active_runs == 1

    by_id = {task.task_id: task for task in dag.tasks}
    assert by_id["validate_gcp_contour"].downstream_task_ids == {
        "acquire_gcp_serving_lease"
    }
    assert by_id["freeze_transaction_boundary"].downstream_task_ids == {
        "wait_for_silver_progress"
    }
    assert by_id["wait_for_silver_progress"].downstream_task_ids == {
        "prepare_same_run_candidate"
    }
    assert by_id["run_dbt_bigquery_candidate"].downstream_task_ids == {
        "collect_candidate_results"
    }
    assert by_id["collect_candidate_results"].downstream_task_ids == {
        "publish_gcp_run",
        "emit_gcp_report",
    }
    assert by_id["publish_gcp_run"].downstream_task_ids == {"emit_gcp_report"}
    assert by_id["emit_gcp_report"].downstream_task_ids == {"release_gcp_serving_lease"}


def test_gcp_dag_uses_restricted_dbt_api_and_does_not_own_streaming() -> None:
    source = (ROOT / "airflow/dags/olist_gcp_serving.py").read_text(encoding="utf-8")

    assert "run_dbt_container" in source
    assert "DOCKER_HOST" not in source
    assert "spark-bronze" not in source
    assert "spark-silver" not in source
    assert "schedule=None" in source
