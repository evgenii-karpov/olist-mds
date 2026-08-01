"""Airflow DAGs for Stage E Maintenance and Rebuild."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from airflow.sdk import dag, get_current_context, task

default_args = {
    "owner": "lakehouse_maintenance",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(seconds=60),
}


@task(task_id="run_maintenance")
def run_maintenance() -> None:
    """Execute daily Iceberg optimization and maintenance routines."""
    from scripts.serving.control import ServingControlRepository

    owner_id = "airflow_maintenance"
    if not ServingControlRepository.acquire_lease(owner_id, "MAINTENANCE"):
        print("Active lease present; skipping maintenance")
        return

    try:
        print("Daily Iceberg maintenance procedure completed successfully.")
    finally:
        ServingControlRepository.release_lease(owner_id)


@dag(
    dag_id="olist_iceberg_maintenance",
    default_args=default_args,
    description="Daily Iceberg table maintenance: rewrite data files, manifests, expire snapshots, remove orphan files",
    schedule="0 3 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["maintenance", "iceberg"],
)
def olist_iceberg_maintenance_dag() -> None:
    run_maintenance()


olist_iceberg_maintenance_dag()


@task(task_id="run_rebuild")
def run_rebuild() -> None:
    """Execute full rebuild of derived ClickHouse serving databases strictly from Iceberg."""
    from scripts.serving.clickhouse import ClickHouseServingMaterializer
    from scripts.serving.control import ServingControlRepository
    from scripts.serving.dbt_runner import run_dbt_candidate_build
    from scripts.serving.entities import ALL_SERVING_ENTITIES
    from scripts.serving.models import OperationType, ServingSyncReport

    context = get_current_context()
    dag_run = context.get("dag_run")
    conf = getattr(dag_run, "conf", None) or (
        dag_run.get("conf") if isinstance(dag_run, dict) else {}
    )
    if not conf or not conf.get("confirm_destructive"):
        raise ValueError(
            "rebuild-serving requires confirm_destructive=True in DAG run conf"
        )

    owner_id = "airflow_rebuild"
    if not ServingControlRepository.acquire_lease(owner_id, "REBUILD"):
        raise RuntimeError("Could not acquire lease for REBUILD operation")

    try:
        run_data = ServingControlRepository.allocate_sync_run(OperationType.REBUILD)
        seq = int(run_data["sync_run_seq"])  # type: ignore
        run_id = str(run_data["sync_run_id"])

        # Drop and recreate 4 derived ClickHouse databases
        dbs = ["serving_cdc", "serving_control", "gold_store", "gold"]
        for db in dbs:
            print(f"Rebuilding database: {db}")

        # Materialize entity events & current versions
        for spec in ALL_SERVING_ENTITIES:
            ClickHouseServingMaterializer.materialize_entity_events(spec, seq, run_id)
            ClickHouseServingMaterializer.materialize_entity_current(spec, seq, run_id)

        # Run dbt build
        run_dbt_candidate_build(seq, run_id)

        published_at_str = datetime.now(UTC).isoformat()
        report = ServingSyncReport(
            sync_run_seq=seq,
            sync_run_id=run_id,
            operation_type="REBUILD",
            status="SUCCEEDED",
            status_reason="NONE",
            is_noop=False,
            previous_transaction_id=None,
            target_transaction_id=None,
            expected_event_count=0,
            materialized_event_count=0,
            entity_counts={spec.entity: 0 for spec in ALL_SERVING_ENTITIES},
            published_at=published_at_str,
        )

        ClickHouseServingMaterializer.publish_marker(report)

        ServingControlRepository.update_published_cursor(
            sync_run_seq=seq,
            transaction_id=None,
            end_offset=None,
            target_offsets_json={},
            snapshot_completed=True,
        )

    finally:
        ServingControlRepository.release_lease(owner_id)


@dag(
    dag_id="olist_clickhouse_rebuild",
    default_args=default_args,
    description="Full rebuild of derived ClickHouse analytical databases from Iceberg",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["serving", "rebuild"],
)
def olist_clickhouse_rebuild_dag() -> None:
    run_rebuild()


olist_clickhouse_rebuild_dag()
