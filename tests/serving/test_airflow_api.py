from __future__ import annotations

from unittest.mock import MagicMock

from airflow.dags.olist_lakehouse_serving import (  # pyright: ignore[reportMissingImports]
    NON_TERMINAL_SYNC_STATUSES,
    default_args,
    mark_sync_run_failed,
)
from scripts.serving.airflow_api import AirflowApiClient, AirflowApiError


def test_manual_trigger_keeps_dag_paused_by_default() -> None:
    client = AirflowApiClient("http://airflow.test")
    client._request = MagicMock(  # type: ignore[method-assign]
        return_value=(200, {"dag_run_id": "manual__validation"})
    )
    client.unpause_dag = MagicMock()  # type: ignore[method-assign]

    result = client.trigger_dag_run(
        "olist_lakehouse_serving_sync", run_id="manual__validation"
    )

    assert result["dag_run_id"] == "manual__validation"
    client.unpause_dag.assert_not_called()
    client._request.assert_called_once_with(  # type: ignore[attr-defined]
        "/api/v2/dags/olist_lakehouse_serving_sync/dagRuns",
        method="POST",
        body={
            "logical_date": client._request.call_args.kwargs["body"]["logical_date"],
            "dag_run_id": "manual__validation",
        },
    )


def test_pause_dag_uses_airflow_pause_patch() -> None:
    client = AirflowApiClient("http://airflow.test")
    client._request = MagicMock(return_value=(200, {}))  # type: ignore[method-assign]

    assert client.pause_dag("olist_lakehouse_serving_sync") is True
    client._request.assert_called_once_with(  # type: ignore[attr-defined]
        "/api/v2/dags/olist_lakehouse_serving_sync",
        method="PATCH",
        body={"is_paused": True},
    )


def test_duplicate_dag_run_is_not_reused() -> None:
    client = AirflowApiClient("http://airflow.test")
    client._request = MagicMock(return_value=(409, {"detail": "already exists"}))  # type: ignore[method-assign]

    try:
        client.trigger_dag_run(
            "olist_lakehouse_serving_sync", run_id="stale__validation"
        )
    except AirflowApiError as exc:
        assert "refusing to reuse stale run" in str(exc)
    else:
        raise AssertionError("trigger_dag_run reused a duplicate run")


def test_timed_out_run_can_be_marked_failed() -> None:
    client = AirflowApiClient("http://airflow.test")
    client._request = MagicMock(return_value=(200, {}))  # type: ignore[method-assign]

    assert client.fail_dag_run("olist_lakehouse_serving_rebuild", "run-1") is True
    client._request.assert_called_once_with(  # type: ignore[attr-defined]
        "/api/v2/dags/olist_lakehouse_serving_rebuild/dagRuns/run-1",
        method="PATCH",
        body={"state": "failed"},
    )


def test_serving_sync_failure_is_terminal_and_not_retried() -> None:
    repository = MagicMock()

    mark_sync_run_failed(repository, 42, RuntimeError("candidate failed"))

    assert default_args["retries"] == 0
    kwargs = repository.update_status.call_args.kwargs
    assert kwargs["sync_run_seq"] == 42
    assert kwargs["new_status"].value == "FAILED_TERMINAL"
    assert kwargs["status_reason"].value == "EXECUTION_FAILURE"
    assert [status.value for status in kwargs["expected_status"]] == list(
        NON_TERMINAL_SYNC_STATUSES
    )
