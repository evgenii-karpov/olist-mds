from collections.abc import Iterable, Mapping

import pytest
from scripts.serving.bigquery_control import BigQueryServingControlRepository
from scripts.serving.control_adapters import PostgresServingControlAdapter
from scripts.serving.domain import ServingBoundary, ServingTarget, TargetMismatchError
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
    assert "DELETE FROM `olist-dev-123.olist_gold_store.dim_date__history`" in query
    assert (
        "DELETE FROM `olist-dev-123.olist_gold_store.mart_monthly_arpu__history`"
        in query
    )
    assert "next_sync_run_seq = allocated_seq + 1" not in query
    assert parameters["sync_run_seq"] == 7


def test_bigquery_persists_frozen_offsets_and_run_boundary_atomically() -> None:
    repository, runner = _repository([{"updated_count": 1}])
    boundary = ServingBoundary(
        target=ServingTarget.GCP,
        sync_run_seq=7,
        previous_transaction_id="tx-previous",
        previous_transaction_end_offset=10,
        target_transaction_id="tx-target",
        target_transaction_end_offset=20,
        target_offsets={"olist_cdc.olist_oltp.customers:0": 20},
        source_snapshot_completed=True,
    )

    result = repository.persist_frozen_boundary(
        sync_run_seq=7,
        boundary=boundary,
        expected_active_sync_run_seq=6,
        previous_offsets={"olist_cdc.olist_oltp.customers:0": 10},
    )

    query, parameters = runner.queries[0]
    assert result["persisted"] is True
    assert "INSERT INTO `olist-dev-123.olist_serving_control.boundary_offsets`" in query
    assert "WHERE NOT EXISTS" in query
    assert "status = 'MATERIALIZING'" in query
    assert "BEGIN TRANSACTION" in query and "COMMIT TRANSACTION" in query
    assert parameters["previous_0"] == 10
    assert parameters["target_0"] == 20


def test_bigquery_progress_check_fails_closed_until_every_partition_is_committed() -> (
    None
):
    repository, runner = _repository(
        [
            {
                "entity": "customers",
                "source_topic": "olist_cdc.olist_oltp.customers",
                "kafka_partition": 0,
                "last_kafka_offset": 19,
                "status": "COMMITTED",
                "updated_at": "2026-08-07T00:00:00Z",
                "spark_batch_id": 4,
            }
        ]
    )

    result = repository.check_silver_progress(
        target_offsets={"olist_cdc.olist_oltp.customers:0": 20}
    )

    query, parameters = runner.queries[0]
    assert result["status"] == "WAITING"
    assert result["missing"] == ["olist_cdc.olist_oltp.customers:0"]
    assert "IN UNNEST(@entities)" in query
    assert parameters["entities"] == ["customers"]


def test_bigquery_reads_debezium_transaction_metadata_from_read_only_bridge() -> None:
    repository, runner = _repository(
        [
            {
                "transaction_id": "tx-7",
                "status": "COMPLETE",
                "end_kafka_offset": 20,
            }
        ]
    )

    rows = repository.fetch_transaction_rows()

    query, parameters = runner.queries[0]
    assert rows == [
        {
            "transaction_id": "tx-7",
            "status": "COMPLETE",
            "end_kafka_offset": 20,
        }
    ]
    assert "olist_lakehouse_bridge.audit_mysql_transactions" in query
    assert "ORDER BY" in query
    assert parameters == {}


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
