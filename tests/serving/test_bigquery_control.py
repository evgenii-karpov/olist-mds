from collections.abc import Iterable, Mapping

import pytest
from scripts.serving.bigquery_control import BigQueryServingControlRepository
from scripts.serving.control_adapters import PostgresServingControlAdapter
from scripts.serving.domain import ServingBoundary, ServingTarget, TargetMismatchError
from scripts.serving.entities import ALL_SERVING_ENTITIES
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


class MultiRowBigQueryRunner:
    def __init__(self, responses: Iterable[Iterable[Mapping[str, object]]]) -> None:
        self.responses = [[dict(response) for response in batch] for batch in responses]
        self.queries: list[tuple[str, Mapping[str, object]]] = []

    def execute(
        self,
        sql: str,
        parameters: Mapping[str, object],
    ) -> Iterable[Mapping[str, object]]:
        self.queries.append((sql, parameters))
        return self.responses.pop(0)


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
    assert "AND next_sync_run_seq = allocated_seq" in query
    assert "is_noop" in query
    assert "source_snapshot_completed" in query
    assert "FROM `olist-dev-123.olist_serving_control.control_state`" in query
    assert "'gcp'" in query
    assert parameters["operation_type"] == "SYNC"


def test_bigquery_sequence_allocation_conflict_fails_closed() -> None:
    repository, _runner = _repository(
        [{"sync_run_seq": None, "error_code": "SEQUENCE_ALLOCATION_CONFLICT"}]
    )

    with pytest.raises(RuntimeError, match="sequence allocation conflicted"):
        repository.allocate_sync_run(OperationType.SYNC)


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


def test_bigquery_entity_metrics_preserve_all_configured_topic_partitions() -> None:
    progress_rows = []
    count_rows = []
    for spec in ALL_SERVING_ENTITIES:
        topic = f"olist_cdc.olist_oltp.{spec.entity}"
        for partition in range(spec.topic_partitions):
            progress_rows.append(
                {
                    "entity": spec.entity,
                    "source_topic": topic,
                    "kafka_partition": partition,
                    "last_kafka_offset": 10 + partition,
                    "status": "COMMITTED",
                    "updated_at": "2026-08-07T00:00:00Z",
                    "spark_batch_id": partition,
                }
            )
            count_rows.append({"entity": spec.entity, "event_count": 1})

    runner = MultiRowBigQueryRunner((progress_rows, count_rows))
    repository = BigQueryServingControlRepository(runner, "olist-dev-123")

    result = repository.fetch_entity_metrics(previous_offsets={})

    assert result["status"] == "READY"
    metrics = result["metrics"]
    assert isinstance(metrics, dict)
    orders = metrics["orders"]
    assert orders["event_count"] == 3
    assert orders["target_offsets"] == {
        "olist_cdc.olist_oltp.orders:0": 10,
        "olist_cdc.olist_oltp.orders:1": 11,
        "olist_cdc.olist_oltp.orders:2": 12,
    }
    query, parameters = runner.queries[1]
    assert "kafka_partition = @partition_" in query
    assert set(
        value for name, value in parameters.items() if name.startswith("partition_")
    ) >= {0, 1, 2}


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


def test_bigquery_lease_uses_expiry_and_owner_compare_and_set() -> None:
    repository, runner = _repository([{"acquired": True}])

    assert repository.acquire_lease("airflow-gcp", "SYNC", ttl_seconds=60)

    query, parameters = runner.queries[0]
    assert "BEGIN TRANSACTION" in query
    assert "lease_expires_at < CURRENT_TIMESTAMP()" in query
    assert "lease_owner_id = @owner_id" in query
    assert parameters["ttl_seconds"] == 60


def test_bigquery_runtime_state_joins_latest_published_boundary() -> None:
    repository, runner = _repository([{"target": "gcp", "active_sync_run_seq": 6}])

    state = repository.fetch_boundary_runtime_state()

    assert state["active_sync_run_seq"] == 6
    query, _parameters = runner.queries[0]
    assert "last_published_transaction_id" in query
    assert "status IN ('SUCCEEDED', 'NOOP')" in query
    assert "ROW_NUMBER() OVER" in query


def test_bigquery_publication_calls_the_versioned_procedure() -> None:
    repository, runner = _repository(
        [{"publication_result": "PUBLISHED", "sync_run_seq": 7}]
    )

    result = repository.publish_gcp_run(
        sync_run_seq=7,
        expected_active_sync_run_seq=6,
    )

    assert result["publication_result"] == "PUBLISHED"
    query, parameters = runner.queries[0]
    assert "CALL `olist-dev-123.olist_serving_control.publish_gcp_run`" in query
    assert parameters == {
        "sync_run_seq": 7,
        "expected_active_sync_run_seq": 6,
    }


def test_bigquery_result_writes_are_target_scoped_and_named() -> None:
    repository, runner = _repository([{"updated_count": 1}, {"updated_count": 1}])

    assert repository.write_entity_result(
        sync_run_seq=7,
        entity="customers",
        status="VALIDATED",
        expected_event_count=3,
        materialized_event_count=3,
        affected_key_count=2,
        candidate_current_count=2,
    )
    assert repository.write_model_result(
        sync_run_seq=7,
        model_name="dim_customer_scd2",
        status="SUCCEEDED",
        candidate_row_count=2,
        affected_grain_count=2,
    )

    entity_query, entity_parameters = runner.queries[0]
    model_query, model_parameters = runner.queries[1]
    assert (
        "INSERT INTO `olist-dev-123.olist_serving_control.entity_results`"
        in entity_query
    )
    assert (
        "INSERT INTO `olist-dev-123.olist_serving_control.model_results`" in model_query
    )
    assert entity_parameters["entity"] == "customers"
    assert model_parameters["model_name"] == "dim_customer_scd2"


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
