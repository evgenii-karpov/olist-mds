from collections.abc import Iterable, Mapping

import pytest
from scripts.serving.bigquery_control import BigQueryServingControlRepository
from scripts.serving.control_adapters import PostgresServingControlAdapter
from scripts.serving.domain import ServingTarget, TargetMismatchError
from scripts.serving.models import OperationType, StatusReason, SyncStatus


class FakeBigQueryRunner:
    def __init__(self, responses: Iterable[Mapping[str, object]]) -> None:
        self.responses = [dict(response) for response in responses]
        self.queries: list[tuple[str, Mapping[str, object]]] = []

    def execute(
        self,
        sql: str,
        parameters: Mapping[str, object],
    ) -> Iterable[Mapping[str, object]]:
        self.queries.append((sql, parameters))
        return [self.responses.pop(0)]


def _repository(
    responses: Iterable[Mapping[str, object]],
) -> tuple[BigQueryServingControlRepository, FakeBigQueryRunner]:
    runner = FakeBigQueryRunner(responses)
    return BigQueryServingControlRepository(runner, "olist-dev-123"), runner


def test_bigquery_allocate_uses_gcp_local_sequence_and_transaction() -> None:
    repository, runner = _repository(
        [
            {
                "target": "gcp",
                "sync_run_seq": 1,
                "sync_run_id": "gcp-sync-00000000000000000001",
            }
        ]
    )

    run = repository.allocate_sync_run(OperationType.SYNC, "dag-1")

    query, parameters = runner.queries[0]
    assert run["target"] == "gcp"
    assert "BEGIN TRANSACTION" in query
    assert "next_sync_run_seq = allocated_seq + 1" in query
    assert "FROM `olist-dev-123.olist_serving_control.control_state`" in query
    assert "'gcp'" in query
    assert parameters["operation_type"] == "SYNC"


def test_bigquery_status_transition_is_optimistic_and_can_report_conflict() -> None:
    repository, runner = _repository([{"updated_count": 0}])

    updated = repository.update_status(
        sync_run_seq=7,
        expected_status=SyncStatus.READY_TO_PUBLISH,
        new_status=SyncStatus.SUCCEEDED,
        expected_active_sync_run_seq=6,
        status_reason=StatusReason.NONE,
    )

    query, parameters = runner.queries[0]
    assert not updated
    assert "active_sync_run_seq" in query
    assert "@expected_active_sync_run_seq" in query
    assert "target = 'gcp'" in query
    assert parameters["expected_active_sync_run_seq"] == 6


def test_bigquery_same_run_retry_does_not_allocate_new_sequence() -> None:
    repository, runner = _repository([{"retried": True}])

    assert repository.prepare_same_run_retry(
        sync_run_seq=7,
        expected_active_sync_run_seq=6,
    )

    query, parameters = runner.queries[0]
    assert "DELETE FROM `olist-dev-123.olist_serving_control.entity_results`" in query
    assert "DELETE FROM `olist-dev-123.olist_serving_control.model_results`" in query
    assert "next_sync_run_seq = allocated_seq + 1" not in query
    assert parameters["sync_run_seq"] == 7


def test_bigquery_compare_and_set_active_state_requires_ready_predecessor() -> None:
    repository, runner = _repository([{"updated_count": 1}])

    assert repository.advance_active_sync_run(
        sync_run_seq=7,
        expected_active_sync_run_seq=6,
    )

    query, _parameters = runner.queries[0]
    assert "status = 'READY_TO_PUBLISH'" in query
    assert "active_sync_run_seq = @expected_active_sync_run_seq" in query


def test_adapters_cannot_be_constructed_for_the_other_target() -> None:
    with pytest.raises(TargetMismatchError):
        PostgresServingControlAdapter(target=ServingTarget.GCP)

    with pytest.raises(TargetMismatchError):
        BigQueryServingControlRepository(
            FakeBigQueryRunner([]),
            "olist-dev-123",
            target=ServingTarget.LOCAL,
        )


def test_bigquery_project_id_is_validated_before_any_query() -> None:
    with pytest.raises(ValueError):
        BigQueryServingControlRepository(FakeBigQueryRunner([]), "not valid")
