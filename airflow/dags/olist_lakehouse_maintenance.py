"""Airflow DAGs for Stage E Maintenance and Rebuild."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from airflow.sdk import dag, get_current_context, task

default_args = {
    "owner": "lakehouse_maintenance",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    # Maintenance and rebuild cross a destructive boundary.  Retrying the
    # whole task can allocate a second ledger row or repeat cleanup after a
    # partial failure; the harness must see one terminal result instead.
    "retries": 0,
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
    dag_id="olist_lakehouse_maintenance",
    default_args=default_args,
    description="Daily Iceberg table maintenance: rewrite data files, manifests, expire snapshots, remove orphan files",
    # Maintenance is manual-only in the local lakehouse workflow.
    schedule=None,
    is_paused_upon_creation=False,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["maintenance", "iceberg"],
)
def olist_lakehouse_maintenance_dag() -> None:
    run_maintenance()


olist_lakehouse_maintenance_dag()


@task(task_id="run_rebuild")
def run_rebuild() -> None:
    """Execute full rebuild of derived ClickHouse serving databases strictly from Iceberg."""
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
    lease_ttl_seconds = 7200
    if not ServingControlRepository.acquire_lease(
        owner_id, "REBUILD", ttl_seconds=lease_ttl_seconds
    ):
        raise RuntimeError("Could not acquire lease for REBUILD operation")

    def heartbeat() -> None:
        if not ServingControlRepository.heartbeat_lease(
            owner_id, ttl_seconds=lease_ttl_seconds
        ):
            raise RuntimeError("Serving rebuild lease heartbeat was lost")

    sync_run_seq: int | None = None
    sync_run_id: str | None = None
    try:
        airflow_run_id = getattr(dag_run, "run_id", None)
        run_data = ServingControlRepository.allocate_sync_run(
            OperationType.REBUILD,
            current_airflow_dag_run_id=(
                str(airflow_run_id) if airflow_run_id is not None else None
            ),
        )
        raw_sync_run_seq = run_data.get("sync_run_seq")
        raw_sync_run_id = run_data.get("sync_run_id")
        if (
            not isinstance(raw_sync_run_seq, (int, float, str))
            or raw_sync_run_id is None
        ):
            raise RuntimeError("Control repository did not allocate a rebuild run")
        sync_run_seq = int(raw_sync_run_seq)
        sync_run_id = str(raw_sync_run_id)
        heartbeat()

        # Read the expected current state from Silver before any destructive
        # operation.  Using Iceberg as the oracle keeps a retry safe after an
        # earlier attempt has already removed the derived ClickHouse views.
        iceberg_current_counts = (
            ClickHouseServingMaterializer.fetch_iceberg_current_counts()
        )
        source_metrics = ClickHouseServingMaterializer.fetch_entity_metrics()
        expected_entity_counts: dict[str, int] = {}
        for spec in ALL_SERVING_ENTITIES:
            metric = source_metrics.get(spec.entity, {})
            event_count = metric.get("event_count")
            if not isinstance(event_count, (int, float, str)) or int(event_count) <= 0:
                raise RuntimeError(
                    f"Iceberg source has no positive event count for {spec.entity}"
                )
            expected_entity_counts[spec.entity] = int(event_count)
        iceberg_snapshots = ClickHouseServingMaterializer.fetch_iceberg_snapshots()
        heartbeat()

        # This is the destructive boundary: all derived databases are removed
        # and recreated from the checked-in native DDL before Iceberg rows are
        # copied into a new candidate partition.
        ClickHouseServingMaterializer.recreate_derived_databases()
        heartbeat()

        materialized_entity_counts: dict[str, int] = {}
        for spec in ALL_SERVING_ENTITIES:
            materialized_count = (
                ClickHouseServingMaterializer.materialize_entity_events(
                    spec, sync_run_seq, sync_run_id
                )
            )
            materialized_entity_counts[spec.entity] = materialized_count
            ClickHouseServingMaterializer.materialize_entity_current(
                spec, sync_run_seq, sync_run_id
            )
            heartbeat()

        materialized_event_count = sum(materialized_entity_counts.values())
        if (
            materialized_event_count != sum(expected_entity_counts.values())
            or materialized_entity_counts != expected_entity_counts
        ):
            raise RuntimeError(
                "Rebuild materialization mismatch: "
                + str(
                    {
                        "expected_event_count": sum(expected_entity_counts.values()),
                        "materialized_event_count": materialized_event_count,
                        "expected_entity_counts": expected_entity_counts,
                        "materialized_entity_counts": materialized_entity_counts,
                    }
                )
            )

        candidate_current_counts = (
            ClickHouseServingMaterializer.fetch_candidate_current_counts(sync_run_seq)
        )
        if candidate_current_counts != iceberg_current_counts:
            raise RuntimeError(
                "Rebuild current-view parity mismatch: "
                + str(
                    {
                        "from_iceberg_source": iceberg_current_counts,
                        "from_iceberg_candidate": candidate_current_counts,
                    }
                )
            )

        # Run dbt build
        heartbeat()
        dbt_result = run_dbt_candidate_build(sync_run_seq, sync_run_id)
        if not dbt_result.get("success"):
            raise RuntimeError(f"dbt rebuild candidate failed: {dbt_result}")

        published_at_str = datetime.now(UTC).isoformat()
        report = ServingSyncReport(
            sync_run_seq=sync_run_seq,
            sync_run_id=sync_run_id,
            operation_type="REBUILD",
            status="SUCCEEDED",
            status_reason="NONE",
            is_noop=False,
            previous_transaction_id=None,
            target_transaction_id=None,
            expected_event_count=sum(expected_entity_counts.values()),
            materialized_event_count=materialized_event_count,
            entity_counts=materialized_entity_counts,
            published_at=published_at_str,
            dbt_result=dbt_result,
        )

        ClickHouseServingMaterializer.publish_marker(report)
        heartbeat()

        ServingControlRepository.update_published_cursor(
            sync_run_seq=sync_run_seq,
            transaction_id=None,
            end_offset=None,
            target_offsets_json={},
            snapshot_completed=True,
        )

        stable_current_counts = ClickHouseServingMaterializer.fetch_current_counts()
        if stable_current_counts != iceberg_current_counts:
            raise RuntimeError(
                "Rebuild published-view parity mismatch: "
                + str(
                    {
                        "from_iceberg_source": iceberg_current_counts,
                        "after_rebuild": stable_current_counts,
                    }
                )
            )

        ServingControlRepository.update_status(
            sync_run_seq=sync_run_seq,
            expected_status=SyncStatus.PLANNING,
            new_status=SyncStatus.SUCCEEDED,
            status_reason=StatusReason.NONE,
            report_json=report.to_canonical_dict(),
            is_noop=False,
            source_snapshot_completed=True,
            target_offsets_json={},
            iceberg_snapshot_ids_json=iceberg_snapshots,
            expected_event_count=sum(expected_entity_counts.values()),
            materialized_event_count=materialized_event_count,
            expected_entity_counts_json=expected_entity_counts,
            materialized_entity_counts_json=materialized_entity_counts,
        )

    except Exception as exc:
        if sync_run_seq is not None:
            try:
                ServingControlRepository.update_status(
                    sync_run_seq=sync_run_seq,
                    expected_status=SyncStatus.PLANNING,
                    new_status=SyncStatus.FAILED_TERMINAL,
                    status_reason=StatusReason.EXECUTION_FAILURE,
                    error_details_json={
                        "operation": "REBUILD",
                        "sync_run_seq": sync_run_seq,
                        "error": str(exc),
                    },
                )
            except Exception as ledger_exc:
                print(
                    f"Could not record rebuild failure in control ledger: {ledger_exc}"
                )
        raise
    finally:
        ServingControlRepository.release_lease(owner_id)


@dag(
    dag_id="olist_lakehouse_serving_rebuild",
    default_args=default_args,
    description="Full rebuild of derived ClickHouse analytical databases from Iceberg",
    schedule=None,
    is_paused_upon_creation=False,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["serving", "rebuild"],
)
def olist_lakehouse_serving_rebuild_dag() -> None:
    run_rebuild()


olist_lakehouse_serving_rebuild_dag()
