"""Finite GCP serving workflow for BigQuery Gold publication.

The DAG owns one bounded serving run only.  Spark streaming remains outside
Airflow; this workflow consumes committed Silver evidence, runs one finite dbt
candidate container through the restricted Docker API, and calls the
SQL-owned atomic publication procedure.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from airflow.sdk import TriggerRule, dag, get_current_context, task

DEFAULT_ARGS = {
    "owner": "gcp_serving",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(seconds=60),
}

LEASE_OWNER = "airflow_gcp_serving"
LEASE_TTL_SECONDS = 7200
EXPECTED_MODELS = (
    "dim_date",
    "dim_order_status",
    "dim_seller",
    "dim_customer_scd2",
    "dim_product_scd2",
    "fact_order_items",
    "mart_daily_revenue",
    "mart_monthly_arpu",
)
EXPECTED_ENTITIES = (
    "customers",
    "orders",
    "order_items",
    "order_payments",
    "order_reviews",
    "products",
    "sellers",
    "product_category_translation",
)


def _dag_conf() -> dict[str, object]:
    context = get_current_context()
    dag_run = context.get("dag_run")
    raw_conf = getattr(dag_run, "conf", None)
    if raw_conf is None and isinstance(dag_run, dict):
        raw_conf = dag_run.get("conf")
    return dict(raw_conf) if isinstance(raw_conf, dict) else {}


def _repository() -> tuple[Any, Any]:
    from scripts.gcp.bigquery_runtime import runner_from_environment
    from scripts.serving.bigquery_control import BigQueryServingControlRepository

    runner = runner_from_environment()
    return runner, BigQueryServingControlRepository(runner, runner.project_id)


def _as_int(value: object, *, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise RuntimeError(f"{label} is not an integer: {value!r}")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"{label} is not an integer: {value!r}") from exc


def _as_str(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"{label} must be a non-empty string")
    return value


def _json_object(value: object) -> dict[str, int]:
    if isinstance(value, dict):
        candidate = value
    elif isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise RuntimeError("BigQuery JSON state is invalid") from exc
        candidate = parsed if isinstance(parsed, dict) else {}
    else:
        candidate = {}
    result: dict[str, int] = {}
    for key, raw_value in candidate.items():
        if isinstance(key, str) and isinstance(raw_value, (int, float, str)):
            result[key] = int(raw_value)
    return result


def _run_identity(run: dict[str, object]) -> tuple[int, int, str]:
    return (
        _as_int(run.get("sync_run_seq"), label="sync_run_seq"),
        _as_int(
            run.get("expected_active_sync_run_seq"),
            label="expected_active_sync_run_seq",
        ),
        _as_str(run.get("sync_run_id"), label="sync_run_id"),
    )


def _task_dict(value: Any, *, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} task output is not an object")
    return dict(value)


@task(task_id="validate_gcp_contour")
def validate_gcp_contour() -> dict[str, object]:
    """Validate non-secret configuration and migration inventory."""

    project_id = os.environ.get("GCP_PROJECT_ID", "").strip()
    region = os.environ.get("GCP_REGION", "us-east1").strip()
    adc_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if not project_id:
        raise RuntimeError("GCP_PROJECT_ID is required")
    if not region:
        raise RuntimeError("GCP_REGION is required")
    if not adc_path or not Path(adc_path).is_file():
        raise RuntimeError(
            "GOOGLE_APPLICATION_CREDENTIALS must point to the mounted Airflow ADC file"
        )
    from scripts.gcp.migrations import list_migrations

    migrations = list_migrations()
    if not migrations:
        raise RuntimeError("no BigQuery migrations are available")
    return {
        "project_id": project_id,
        "region": region,
        "migration_versions": [migration.version for migration in migrations],
    }


@task(task_id="acquire_gcp_serving_lease")
def acquire_gcp_serving_lease(config: Any) -> dict[str, object]:
    """Acquire the GCP control lease before allocating a serving run."""

    config = _task_dict(config, label="GCP contour validation")
    context = get_current_context()
    dag_run = context.get("dag_run")
    airflow_run_id = getattr(dag_run, "run_id", "unknown")
    owner_id = f"{LEASE_OWNER}:{airflow_run_id}"
    runner, repository = _repository()
    try:
        if not repository.acquire_lease(
            owner_id,
            "SYNC",
            ttl_seconds=LEASE_TTL_SECONDS,
        ):
            raise RuntimeError("another GCP serving run owns the control lease")
        return {**config, "owner_id": owner_id}
    finally:
        runner.close()


@task(task_id="allocate_gcp_sync_run")
def allocate_gcp_sync_run(lease: Any) -> dict[str, object]:
    """Allocate a new GCP sequence or prepare an explicitly requested retry."""

    from scripts.serving.models import OperationType

    lease = _task_dict(lease, label="GCP serving lease")
    context = get_current_context()
    dag_run = context.get("dag_run")
    airflow_run_id = str(getattr(dag_run, "run_id", "unknown"))
    conf = _dag_conf()
    runner, repository = _repository()
    try:
        requested_seq = conf.get("retry_sync_run_seq")
        if requested_seq is not None:
            sync_run_seq = _as_int(requested_seq, label="retry_sync_run_seq")
            existing = repository.get_serving_run(sync_run_seq)
            expected_active = _as_int(
                existing.get("expected_active_sync_run_seq"),
                label="expected_active_sync_run_seq",
            )
            if not repository.prepare_same_run_retry(
                sync_run_seq=sync_run_seq,
                expected_active_sync_run_seq=expected_active,
            ):
                raise RuntimeError("same-run retry could not be prepared")
            run = existing
            run["status"] = "PLANNING"
            run["attempt_count"] = (
                _as_int(existing.get("attempt_count", 1), label="attempt_count") + 1
            )
            run["retry_same_run"] = True
        else:
            run = repository.allocate_sync_run(
                OperationType.SYNC,
                current_airflow_dag_run_id=airflow_run_id,
            )
            run["retry_same_run"] = False
        return {**lease, **run}
    finally:
        runner.close()


@task(task_id="freeze_transaction_boundary")
def freeze_transaction_boundary(run: Any) -> dict[str, object]:
    """Plan and persist one transaction-complete immutable boundary."""

    from scripts.serving.boundary import (
        ServingBoundaryPlanner,
        transaction_boundary_state,
    )
    from scripts.serving.domain import ServingBoundary, ServingTarget
    from scripts.serving.models import StatusReason, SyncStatus

    run = _task_dict(run, label="GCP serving run")
    sync_run_seq, expected_active, _sync_run_id = _run_identity(run)
    runner, repository = _repository()
    try:
        runtime = repository.fetch_boundary_runtime_state()
        previous_offsets = _json_object(runtime.get("last_published_target_offsets"))
        snapshot_ids = _json_object(runtime.get("last_published_iceberg_snapshot_ids"))
        metrics_result = repository.fetch_entity_metrics(
            previous_offsets=previous_offsets
        )
        if metrics_result.get("status") != "READY":
            repository.update_status(
                sync_run_seq=sync_run_seq,
                expected_status=SyncStatus.PLANNING,
                new_status=SyncStatus.WAITING,
                expected_active_sync_run_seq=expected_active,
                status_reason=StatusReason.SOURCE_NOT_CAUGHT_UP,
            )
            raise RuntimeError(f"Silver progress is not ready: {metrics_result}")

        transaction_rows = repository.fetch_transaction_rows()
        plan = ServingBoundaryPlanner.plan_next_sync_run(
            sync_run_seq=sync_run_seq,
            runtime_state=runtime,
            transaction_rows=transaction_rows,
            iceberg_snapshots=snapshot_ids,
            coverage_state="READY",
            boundary_state=transaction_boundary_state(transaction_rows),
            entity_metrics=metrics_result["metrics"],  # type: ignore[arg-type]
        )
        base = {
            **run,
            "previous_offsets": previous_offsets,
            "entity_metrics": metrics_result["metrics"],
            "expected_entity_counts": plan.expected_entity_counts,
            "is_noop": plan.is_noop,
            "plan_status": plan.status,
        }
        if plan.is_noop or plan.status in {"WAITING", "BLOCKED", "NOOP"}:
            status = SyncStatus(plan.status)
            reason = StatusReason(plan.status_reason)
            if not repository.update_status(
                sync_run_seq=sync_run_seq,
                expected_status=SyncStatus.PLANNING,
                new_status=status,
                expected_active_sync_run_seq=expected_active,
                status_reason=reason,
                is_noop=plan.is_noop,
            ):
                raise RuntimeError("GCP run status changed before boundary decision")
            return base

        boundary = ServingBoundary(
            target=ServingTarget.GCP,
            sync_run_seq=sync_run_seq,
            previous_transaction_id=plan.previous_transaction_id,
            previous_transaction_end_offset=plan.previous_transaction_end_offset,
            target_transaction_id=plan.target_transaction_id,
            target_transaction_end_offset=plan.target_transaction_end_offset,
            target_offsets=plan.target_offsets,
            source_snapshot_completed=plan.source_snapshot_completed,
        )
        persisted = repository.persist_frozen_boundary(
            sync_run_seq=sync_run_seq,
            boundary=boundary,
            expected_active_sync_run_seq=expected_active,
            previous_offsets=previous_offsets,
            iceberg_snapshot_ids=snapshot_ids,
        )
        if not persisted.get("persisted"):
            raise RuntimeError("GCP frozen boundary compare-and-set failed")
        return {
            **base,
            "current_boundary_id": persisted["current_boundary_id"],
            "previous_boundary_id": persisted.get("previous_boundary_id") or "",
            "target_offsets": plan.target_offsets,
        }
    finally:
        runner.close()


@task(
    task_id="wait_for_silver_progress",
    retries=24,
    retry_delay=timedelta(seconds=60),
)
def wait_for_silver_progress(boundary: Any) -> dict[str, object]:
    """Revalidate every frozen topic-partition before building Gold."""

    boundary = _task_dict(boundary, label="frozen GCP boundary")
    if bool(boundary.get("is_noop")):
        return boundary
    target_offsets = boundary.get("target_offsets")
    if not isinstance(target_offsets, dict) or not target_offsets:
        raise RuntimeError("materializing run has no frozen target offsets")
    runner, repository = _repository()
    try:
        progress = repository.revalidate_silver_progress(
            target_offsets={
                str(key): _as_int(value, label=f"target offset {key}")
                for key, value in target_offsets.items()
            }
        )
        if progress.get("status") != "READY":
            raise RuntimeError(f"Silver progress has not caught up: {progress}")
        return {**boundary, "progress": progress}
    finally:
        runner.close()


@task(task_id="prepare_same_run_candidate")
def prepare_same_run_candidate(boundary: Any) -> dict[str, object]:
    """Keep the retry cleanup explicit in the task graph."""

    return _task_dict(boundary, label="Silver progress")


@task(task_id="run_dbt_bigquery_candidate")
def run_dbt_bigquery_candidate(boundary: Any) -> dict[str, object]:
    """Run the pinned dbt image through the restricted Docker API."""

    boundary = _task_dict(boundary, label="prepared GCP candidate")
    if bool(boundary.get("is_noop")):
        return {**boundary, "dbt": {"success": True, "skipped": True}}
    from scripts.gcp.docker_api import request_from_environment, run_dbt_container
    from scripts.serving.models import StatusReason, SyncStatus

    sync_run_seq, expected_active, sync_run_id = _run_identity(boundary)
    current_boundary_id = _as_str(
        boundary.get("current_boundary_id"), label="current_boundary_id"
    )
    previous_boundary_id = str(boundary.get("previous_boundary_id", ""))
    runner, repository = _repository()
    try:
        request = request_from_environment(
            project_id=_as_str(boundary.get("project_id"), label="project_id"),
            region=_as_str(boundary.get("region"), label="region"),
            sync_run_seq=sync_run_seq,
            sync_run_id=sync_run_id,
            previous_boundary_id=previous_boundary_id,
            current_boundary_id=current_boundary_id,
            build_mode="incremental"
            if bool(boundary.get("retry_same_run"))
            else "initial",
        )
        result = run_dbt_container(request)
        run_results = result.artifacts.get("run_results.json")
        summary = {
            "success": result.success,
            "exit_code": result.exit_code,
            "image": result.image,
            "container_id": result.container_id,
            "logs_sha256": hashlib.sha256(result.logs.encode("utf-8")).hexdigest(),
            "logs_tail": result.logs[-8000:],
            "run_results": run_results,
        }
        if not result.success:
            repository.update_status(
                sync_run_seq=sync_run_seq,
                expected_status=[SyncStatus.MATERIALIZING, SyncStatus.VALIDATING],
                new_status=SyncStatus.FAILED_TERMINAL,
                expected_active_sync_run_seq=expected_active,
                status_reason=StatusReason.EXECUTION_FAILURE,
                error_code="DBT_BUILD_FAILED",
                error_message=f"dbt container exited with {result.exit_code}",
            )
            raise RuntimeError(f"dbt candidate build failed: {summary}")
        return {**boundary, "dbt": summary}
    finally:
        runner.close()


@task(task_id="collect_candidate_results")
def collect_candidate_results(candidate: Any) -> dict[str, object]:
    """Persist dbt model and validated Silver entity evidence."""

    from scripts.serving.models import StatusReason, SyncStatus

    candidate = _task_dict(candidate, label="dbt candidate")
    if bool(candidate.get("is_noop")):
        return {**candidate, "candidate_results": {"skipped": True}}
    sync_run_seq, expected_active, _sync_run_id = _run_identity(candidate)
    dbt = candidate.get("dbt")
    if not isinstance(dbt, dict) or not dbt.get("success"):
        raise RuntimeError("dbt result is missing or unsuccessful")
    run_results = dbt.get("run_results")
    entries = run_results.get("results", []) if isinstance(run_results, dict) else []
    by_model = {
        str(entry.get("unique_id", "")).rsplit(".", 1)[-1]: entry
        for entry in entries
        if isinstance(entry, dict)
        and str(entry.get("unique_id", "")).startswith("model.olist_bigquery.")
    }
    runner, repository = _repository()
    try:
        model_counts = {
            str(row.get("model_name")): row
            for row in repository.fetch_model_candidate_counts(sync_run_seq)
        }
        model_statuses: dict[str, str] = {}
        for model_name in EXPECTED_MODELS:
            entry = by_model.get(model_name, {})
            status = "SUCCEEDED" if entry.get("status") == "success" else "FAILED"
            count_row = model_counts.get(model_name, {})
            if not repository.write_model_result(
                sync_run_seq=sync_run_seq,
                model_name=model_name,
                status=status,
                candidate_row_count=_as_int(
                    count_row.get("candidate_row_count", 0),
                    label=f"{model_name} candidate row count",
                ),
                affected_grain_count=_as_int(
                    count_row.get("affected_grain_count", 0),
                    label=f"{model_name} affected grain count",
                ),
            ):
                raise RuntimeError(f"could not record model result: {model_name}")
            model_statuses[model_name] = status

        entity_counts = candidate.get("expected_entity_counts", {})
        if not isinstance(entity_counts, dict):
            raise RuntimeError("expected entity counts are missing")
        for entity in EXPECTED_ENTITIES:
            expected_count = _as_int(
                entity_counts.get(entity, 0), label=f"{entity} expected event count"
            )
            if not repository.write_entity_result(
                sync_run_seq=sync_run_seq,
                entity=entity,
                status="VALIDATED",
                expected_event_count=expected_count,
                materialized_event_count=expected_count,
                affected_key_count=0,
                candidate_current_count=0,
            ):
                raise RuntimeError(f"could not record entity result: {entity}")

        if set(model_statuses.values()) != {"SUCCEEDED"}:
            repository.update_status(
                sync_run_seq=sync_run_seq,
                expected_status=[SyncStatus.MATERIALIZING, SyncStatus.VALIDATING],
                new_status=SyncStatus.FAILED_TERMINAL,
                expected_active_sync_run_seq=expected_active,
                status_reason=StatusReason.EXECUTION_FAILURE,
                error_code="DBT_MODEL_FAILED",
                error_message=str(model_statuses),
            )
            raise RuntimeError(f"one or more dbt models failed: {model_statuses}")
        if not repository.update_status(
            sync_run_seq=sync_run_seq,
            expected_status=SyncStatus.MATERIALIZING,
            new_status=SyncStatus.VALIDATING,
            expected_active_sync_run_seq=expected_active,
        ):
            raise RuntimeError("GCP run left MATERIALIZING before validation")
        if not repository.update_status(
            sync_run_seq=sync_run_seq,
            expected_status=SyncStatus.VALIDATING,
            new_status=SyncStatus.READY_TO_PUBLISH,
            expected_active_sync_run_seq=expected_active,
        ):
            raise RuntimeError("GCP run left VALIDATING before publication")
        return {
            **candidate,
            "candidate_results": {
                "model_statuses": model_statuses,
                "model_counts": model_counts,
                "entity_counts": entity_counts,
            },
        }
    finally:
        runner.close()


@task(task_id="publish_gcp_run")
def publish_gcp_run(candidate: Any) -> dict[str, object]:
    """Call the versioned atomic publication procedure."""

    candidate = _task_dict(candidate, label="candidate results")
    if bool(candidate.get("is_noop")):
        return {**candidate, "publication": {"publication_result": "NOOP"}}
    sync_run_seq, expected_active, _sync_run_id = _run_identity(candidate)
    runner, repository = _repository()
    try:
        result = repository.publish_gcp_run(
            sync_run_seq=sync_run_seq,
            expected_active_sync_run_seq=expected_active,
        )
        publication_result = str(result.get("publication_result", ""))
        if publication_result not in {"PUBLISHED", "IDEMPOTENT"}:
            raise RuntimeError(f"GCP publication did not succeed: {result}")
        return {**candidate, "publication": result}
    finally:
        runner.close()


@task(task_id="emit_gcp_report", trigger_rule=TriggerRule.ALL_DONE)
def emit_gcp_report(
    run: Any,
    candidate: Any,
    publication: Any,
) -> dict[str, object]:
    """Emit a bounded operator-readable report without leaking credentials."""

    run = _task_dict(run, label="GCP serving run")
    candidate = candidate if isinstance(candidate, dict) else {}
    publication = publication if isinstance(publication, dict) else {}
    report = {
        "dag": "olist_gcp_serving",
        "sync_run_seq": run.get("sync_run_seq"),
        "sync_run_id": run.get("sync_run_id"),
        "current_boundary_id": (candidate or {}).get("current_boundary_id"),
        "publication": (publication or {}).get("publication"),
        "generated_at": datetime.now(UTC).isoformat(),
    }
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return report


@task(task_id="release_gcp_serving_lease", trigger_rule=TriggerRule.ALL_DONE)
def release_gcp_serving_lease(lease: Any) -> None:
    """Release the lease after all finite serving tasks settle."""

    lease = _task_dict(lease, label="GCP serving lease")
    owner_id = lease.get("owner_id")
    if not isinstance(owner_id, str) or not owner_id:
        return
    runner, repository = _repository()
    try:
        if not repository.release_lease(owner_id):
            print(f"GCP serving lease was already released: {owner_id}")
    finally:
        runner.close()


@dag(
    dag_id="olist_gcp_serving",
    default_args=DEFAULT_ARGS,
    description="Finite GCP serving run from committed Silver evidence to BigQuery Gold",
    schedule=None,
    is_paused_upon_creation=False,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["serving", "gcp", "bigquery"],
)
def olist_gcp_serving_dag() -> None:
    config = validate_gcp_contour()
    lease = acquire_gcp_serving_lease(config)
    run = allocate_gcp_sync_run(lease)
    boundary = freeze_transaction_boundary(run)
    progress = wait_for_silver_progress(boundary)
    candidate = prepare_same_run_candidate(progress)
    dbt = run_dbt_bigquery_candidate(candidate)
    results = collect_candidate_results(dbt)
    publication = publish_gcp_run(results)
    report = emit_gcp_report(run, results, publication)
    release = release_gcp_serving_lease(lease)
    release.set_upstream(report)


olist_gcp_serving_dag()
