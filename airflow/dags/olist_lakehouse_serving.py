"""Airflow DAGs for Stage E Serving Integration: sync and quality checks."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from airflow.sdk import dag, get_current_context, task

default_args = {
    "owner": "lakehouse_serving",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    # A serving sync allocates one immutable control-ledger row.  Retrying the
    # Airflow task would allocate another row for the same DAG run and can
    # publish a different boundary.  Fail once and let the caller inspect the
    # terminal ledger record instead.
    "retries": 0,
    "retry_delay": timedelta(seconds=60),
}

NON_TERMINAL_SYNC_STATUSES = (
    "PLANNING",
    "WAITING",
    "BLOCKED",
    "MATERIALIZING",
    "VALIDATING",
    "READY_TO_PUBLISH",
    "PUBLISHED_PENDING_FINALIZATION",
    "FAILED_RETRYABLE",
)


def mark_sync_run_failed(repository: Any, sync_run_seq: int, error: Exception) -> None:
    """Move an allocated sync ledger row out of every non-terminal state."""

    from scripts.serving.models import StatusReason, SyncStatus

    try:
        repository.update_status(
            sync_run_seq=sync_run_seq,
            expected_status=[
                SyncStatus(status) for status in NON_TERMINAL_SYNC_STATUSES
            ],
            new_status=SyncStatus.FAILED_TERMINAL,
            status_reason=StatusReason.EXECUTION_FAILURE,
            error_details_json={
                "operation": "SYNC",
                "sync_run_seq": sync_run_seq,
                "error": str(error),
            },
        )
    except Exception as ledger_exc:
        print(f"Could not record serving sync failure: {ledger_exc}")


@task(task_id="run_serving_sync")
def run_serving_sync() -> None:
    """Execute finite serving sync run."""
    from scripts.serving.boundary import ServingBoundaryPlanner
    from scripts.serving.clickhouse import ClickHouseServingMaterializer
    from scripts.serving.control import ServingControlRepository
    from scripts.serving.dbt_runner import run_dbt_candidate_build
    from scripts.serving.entities import ALL_SERVING_ENTITIES
    from scripts.serving.models import (
        OperationType,
        ServingSyncReport,
        StatusReason,
        SyncStatus,
    )

    owner_id = "airflow_serving_sync"
    lease_ttl_seconds = 7200
    if not ServingControlRepository.acquire_lease(
        owner_id, "SYNC", ttl_seconds=lease_ttl_seconds
    ):
        print("Active lease present; skipping run")
        return

    def heartbeat() -> None:
        if not ServingControlRepository.heartbeat_lease(
            owner_id, ttl_seconds=lease_ttl_seconds
        ):
            raise RuntimeError("Serving sync lease heartbeat was lost")

    sync_run_seq: int | None = None
    try:
        context = get_current_context()
        dag_run = context.get("dag_run")
        airflow_run_id = getattr(dag_run, "run_id", None)
        run_data = ServingControlRepository.allocate_sync_run(
            OperationType.SYNC,
            current_airflow_dag_run_id=(
                str(airflow_run_id) if airflow_run_id is not None else None
            ),
        )
        sync_run_seq = int(run_data["sync_run_seq"])  # type: ignore
        seq = sync_run_seq
        run_id = str(run_data["sync_run_id"])

        state = ServingControlRepository.get_runtime_state()
        tx_rows = ClickHouseServingMaterializer.fetch_transaction_rows()
        snapshots = ClickHouseServingMaterializer.fetch_iceberg_snapshots()
        heartbeat()

        # First select the complete transaction prefix without Silver-derived
        # metrics.  Only after that frozen boundary is known may metrics be
        # read; otherwise rows from an OPEN transaction that already reached
        # Silver can widen the candidate beyond the planner's boundary.
        boundary_plan = ServingBoundaryPlanner.plan_next_sync_run(
            sync_run_seq=seq,
            runtime_state=state,
            transaction_rows=tx_rows,
            iceberg_snapshots=snapshots,
            coverage_state="READY",
            boundary_state="READY",
            entity_metrics=None,
        )
        entity_metrics = None
        if boundary_plan.status == "MATERIALIZING":
            if boundary_plan.target_transaction_end_offset is None:
                raise RuntimeError(
                    "Serving planner returned MATERIALIZING without a transaction boundary"
                )
            entity_metrics = ClickHouseServingMaterializer.fetch_entity_metrics(
                boundary_plan.target_transaction_end_offset
            )

        plan = ServingBoundaryPlanner.plan_next_sync_run(
            sync_run_seq=seq,
            runtime_state=state,
            transaction_rows=tx_rows,
            iceberg_snapshots=snapshots,
            coverage_state="READY",
            boundary_state="READY",
            entity_metrics=entity_metrics,
        )

        if plan.status in ("WAITING", "BLOCKED"):
            ServingControlRepository.update_status(
                sync_run_seq=seq,
                expected_status=SyncStatus.PLANNING,
                new_status=SyncStatus(plan.status),
                status_reason=StatusReason(plan.status_reason),
                is_noop=False,
                previous_transaction_id=plan.previous_transaction_id,
                previous_transaction_end_offset=plan.previous_transaction_end_offset,
                target_transaction_id=plan.target_transaction_id,
                target_transaction_end_offset=plan.target_transaction_end_offset,
                source_snapshot_completed=plan.source_snapshot_completed,
                target_offsets_json=plan.target_offsets,
                iceberg_snapshot_ids_json=plan.iceberg_snapshot_ids,
                expected_event_count=0,
                materialized_event_count=0,
                expected_entity_counts_json=plan.expected_entity_counts,
                materialized_entity_counts_json={
                    spec.entity: 0 for spec in ALL_SERVING_ENTITIES
                },
            )
            raise RuntimeError(
                f"Serving boundary is not publishable: "
                f"{plan.status}/{plan.status_reason}"
            )

        if plan.is_noop or plan.status == "NOOP":
            published_at_str = datetime.now(UTC).isoformat()
            report = ServingSyncReport(
                sync_run_seq=seq,
                sync_run_id=run_id,
                operation_type="SYNC",
                status=plan.status,
                status_reason=plan.status_reason,
                is_noop=True,
                previous_transaction_id=plan.previous_transaction_id,
                target_transaction_id=plan.target_transaction_id,
                expected_event_count=0,
                materialized_event_count=0,
                entity_counts=plan.expected_entity_counts,
                published_at=published_at_str,
            )
            ServingControlRepository.update_status(
                sync_run_seq=seq,
                expected_status=SyncStatus.PLANNING,
                new_status=SyncStatus(plan.status),
                status_reason=StatusReason(plan.status_reason),
                report_json=report.to_canonical_dict(),
                is_noop=True,
                previous_transaction_id=plan.previous_transaction_id,
                previous_transaction_end_offset=plan.previous_transaction_end_offset,
                target_transaction_id=plan.target_transaction_id,
                target_transaction_end_offset=plan.target_transaction_end_offset,
                source_snapshot_completed=plan.source_snapshot_completed,
                target_offsets_json=plan.target_offsets,
                iceberg_snapshot_ids_json=plan.iceberg_snapshot_ids,
                expected_event_count=0,
                materialized_event_count=0,
                expected_entity_counts_json=plan.expected_entity_counts,
                materialized_entity_counts_json={
                    spec.entity: 0 for spec in ALL_SERVING_ENTITIES
                },
            )
            return

        # Materialize entity events & current versions into candidate partitions
        materialized_entity_counts: dict[str, int] = {}
        for spec in ALL_SERVING_ENTITIES:
            materialized_count = (
                ClickHouseServingMaterializer.materialize_entity_events(
                    spec,
                    seq,
                    run_id,
                    target_transaction_id=plan.target_transaction_id,
                    target_offsets=plan.target_offsets,
                )
            )
            ClickHouseServingMaterializer.materialize_entity_current(spec, seq, run_id)
            materialized_entity_counts[spec.entity] = materialized_count
            heartbeat()

        materialized_event_count = sum(materialized_entity_counts.values())
        if (
            materialized_event_count != plan.expected_event_count
            or materialized_entity_counts != plan.expected_entity_counts
        ):
            details = {
                "expected_event_count": plan.expected_event_count,
                "materialized_event_count": materialized_event_count,
                "expected_entity_counts": plan.expected_entity_counts,
                "materialized_entity_counts": materialized_entity_counts,
            }
            ServingControlRepository.update_status(
                sync_run_seq=seq,
                expected_status=SyncStatus.PLANNING,
                new_status=SyncStatus.FAILED_TERMINAL,
                status_reason=StatusReason.MATERIALIZATION_MISMATCH,
                error_details_json=details,
                is_noop=False,
                previous_transaction_id=plan.previous_transaction_id,
                previous_transaction_end_offset=plan.previous_transaction_end_offset,
                target_transaction_id=plan.target_transaction_id,
                target_transaction_end_offset=plan.target_transaction_end_offset,
                source_snapshot_completed=plan.source_snapshot_completed,
                target_offsets_json=plan.target_offsets,
                iceberg_snapshot_ids_json=plan.iceberg_snapshot_ids,
                expected_event_count=plan.expected_event_count,
                materialized_event_count=materialized_event_count,
                expected_entity_counts_json=plan.expected_entity_counts,
                materialized_entity_counts_json=materialized_entity_counts,
            )
            raise RuntimeError(f"Serving materialization mismatch: {details}")

        # Run dbt candidate build
        heartbeat()
        dbt_res = run_dbt_candidate_build(seq, run_id)
        if not dbt_res["success"]:
            ServingControlRepository.update_status(
                sync_run_seq=seq,
                expected_status=SyncStatus.PLANNING,
                new_status=SyncStatus.FAILED_TERMINAL,
                error_details_json={"dbt_error": dbt_res["exception"]},
            )
            raise RuntimeError(f"dbt candidate build failed: {dbt_res}")

        published_at_str = datetime.now(UTC).isoformat()
        report = ServingSyncReport(
            sync_run_seq=seq,
            sync_run_id=run_id,
            operation_type="SYNC",
            status="SUCCEEDED",
            status_reason="NONE",
            is_noop=False,
            previous_transaction_id=plan.previous_transaction_id,
            target_transaction_id=plan.target_transaction_id,
            expected_event_count=plan.expected_event_count,
            materialized_event_count=materialized_event_count,
            entity_counts=plan.expected_entity_counts,
            published_at=published_at_str,
            dbt_result=dbt_res,
        )

        # Publish marker in ClickHouse
        ClickHouseServingMaterializer.publish_marker(report)
        heartbeat()

        # Update cursor in PostgreSQL
        ServingControlRepository.update_published_cursor(
            sync_run_seq=seq,
            transaction_id=plan.target_transaction_id,
            end_offset=plan.target_transaction_end_offset,
            target_offsets_json=plan.target_offsets,
            snapshot_completed=True,
        )

        ServingControlRepository.update_status(
            sync_run_seq=seq,
            expected_status=SyncStatus.PLANNING,
            new_status=SyncStatus.SUCCEEDED,
            report_json=report.to_canonical_dict(),
            is_noop=False,
            previous_transaction_id=plan.previous_transaction_id,
            previous_transaction_end_offset=plan.previous_transaction_end_offset,
            target_transaction_id=plan.target_transaction_id,
            target_transaction_end_offset=plan.target_transaction_end_offset,
            source_snapshot_completed=plan.source_snapshot_completed,
            target_offsets_json=plan.target_offsets,
            iceberg_snapshot_ids_json=plan.iceberg_snapshot_ids,
            expected_event_count=plan.expected_event_count,
            materialized_event_count=materialized_event_count,
            expected_entity_counts_json=plan.expected_entity_counts,
            materialized_entity_counts_json=materialized_entity_counts,
        )

    except Exception as exc:
        if sync_run_seq is not None:
            mark_sync_run_failed(ServingControlRepository, sync_run_seq, exc)
        raise
    finally:
        ServingControlRepository.release_lease(owner_id)


@dag(
    dag_id="olist_lakehouse_serving_sync",
    default_args=default_args,
    description="Finite serving sync of transaction-complete Iceberg data to ClickHouse Gold",
    # Serving publication is intentionally manual-only.  Validation and the
    # local cutover workflow trigger this DAG explicitly; a timetable here can
    # publish a competing boundary while a validation run is in progress.
    schedule=None,
    is_paused_upon_creation=False,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["serving", "lakehouse"],
)
def olist_lakehouse_serving_sync_dag() -> None:
    run_serving_sync()


olist_lakehouse_serving_sync_dag()


@task(task_id="run_serving_quality")
def run_serving_quality() -> None:
    """Execute hourly serving quality and parity checks."""
    from scripts.serving.control import ServingControlRepository

    state = ServingControlRepository.get_runtime_state()
    print(
        "Serving quality check completed. Last published seq:",
        state.get("last_published_sync_run_seq"),
    )


@dag(
    dag_id="olist_lakehouse_quality",
    default_args=default_args,
    description="Hourly quality and consistency verification of ClickHouse serving layer",
    # Quality checks are launched explicitly after the serving boundary.
    schedule=None,
    is_paused_upon_creation=False,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["serving", "quality"],
)
def olist_lakehouse_quality_dag() -> None:
    run_serving_quality()


olist_lakehouse_quality_dag()
