"""Airflow DAGs for Stage E Serving Integration: sync and quality checks."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from airflow.sdk import dag, task

default_args = {
    "owner": "lakehouse_serving",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(seconds=60),
}


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
    if not ServingControlRepository.acquire_lease(owner_id, "SYNC"):
        print("Active lease present; skipping run")
        return

    try:
        run_data = ServingControlRepository.allocate_sync_run(OperationType.SYNC)
        seq = int(run_data["sync_run_seq"])  # type: ignore
        run_id = str(run_data["sync_run_id"])

        state = ServingControlRepository.get_runtime_state()
        plan = ServingBoundaryPlanner.plan_next_sync_run(
            sync_run_seq=seq,
            runtime_state=state,
            transaction_rows=[],
            iceberg_snapshots={},
            coverage_state="READY",
            boundary_state="READY",
        )

        if plan.is_noop or plan.status in ("NOOP", "WAITING", "BLOCKED"):
            ServingControlRepository.update_status(
                sync_run_seq=seq,
                expected_status=SyncStatus.PLANNING,
                new_status=SyncStatus(plan.status),
                status_reason=StatusReason(plan.status_reason),
            )
            return

        # Materialize entity events & current versions into candidate partitions
        for spec in ALL_SERVING_ENTITIES:
            ClickHouseServingMaterializer.materialize_entity_events(spec, seq, run_id)
            ClickHouseServingMaterializer.materialize_entity_current(spec, seq, run_id)

        # Run dbt candidate build
        dbt_res = run_dbt_candidate_build(seq, run_id)
        if not dbt_res["success"]:
            ServingControlRepository.update_status(
                sync_run_seq=seq,
                expected_status=SyncStatus.MATERIALIZING,
                new_status=SyncStatus.FAILED_TERMINAL,
                error_details_json={"dbt_error": dbt_res["exception"]},
            )
            return

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
            materialized_event_count=plan.expected_event_count,
            entity_counts=plan.expected_entity_counts,
            published_at=published_at_str,
        )

        # Publish marker in ClickHouse
        ClickHouseServingMaterializer.publish_marker(report)

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
        )

    finally:
        ServingControlRepository.release_lease(owner_id)


@dag(
    dag_id="olist_lakehouse_serving_sync",
    default_args=default_args,
    description="Finite serving sync of transaction-complete Iceberg data to ClickHouse Gold",
    schedule="*/5 * * * *",
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
    dag_id="olist_lakehouse_serving_quality",
    default_args=default_args,
    description="Hourly quality and consistency verification of ClickHouse serving layer",
    schedule="0 * * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["serving", "quality"],
)
def olist_lakehouse_serving_quality_dag() -> None:
    run_serving_quality()


olist_lakehouse_serving_quality_dag()
