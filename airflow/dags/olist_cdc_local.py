"""Local Phase 4 CDC ingest and manual object replay DAGs."""

from __future__ import annotations

import json
import os
import subprocess
from collections.abc import Mapping
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from airflow.sdk import Asset, Param, dag, get_current_context, task
from airflow.sdk.exceptions import AirflowException, AirflowSkipException

INGEST_DAG_ID = "olist_cdc_ingest_local"
BACKFILL_DAG_ID = "olist_cdc_backfill_local"
RAW_CDC_ASSET = Asset("olist://cdc/raw/local")
CDC_POOL = os.environ.get("OLIST_CDC_AIRFLOW_POOL", "default_pool")
CDC_TABLES = [
    "customers",
    "order_items",
    "order_payments",
    "order_reviews",
    "orders",
    "product_category_translation",
    "products",
    "sellers",
]


def project_root() -> Path:
    configured = os.environ.get("OLIST_PROJECT_ROOT")
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[2]


def python_bin() -> str:
    return os.environ.get("OLIST_PYTHON_BIN", "python")


def safe_run_id(value: str) -> str:
    return value.replace(":", "_").replace("+", "_")


def context_values() -> tuple[Mapping[str, Any], str, str]:
    context = get_current_context()
    params = context.get("params")
    run_id = context.get("run_id")
    dag = context.get("dag")
    if not isinstance(params, Mapping) or run_id is None or dag is None:
        raise AirflowException("Airflow task context is incomplete")
    return params, str(dag.dag_id), str(run_id)


def command_prefix() -> list[str]:
    return [
        python_bin(),
        "scripts/cdc/warehouse_ingest.py",
        "--bootstrap-sql-dir",
        "infra/postgres",
    ]


def run_json_command(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(
        command,
        cwd=str(project_root()),
        check=True,
        capture_output=True,
        text=True,
    )
    output = result.stdout.strip().splitlines()
    if not output:
        raise AirflowException("CDC command returned no summary")
    value = json.loads(output[-1])
    if not isinstance(value, dict):
        raise AirflowException("CDC command summary must be a JSON object")
    return value


def selector_args(params: Mapping[str, Any]) -> list[str]:
    result: list[str] = []
    for param, option in (
        ("table", "--table"),
        ("date_from", "--date-from"),
        ("date_to", "--date-to"),
        ("object_pattern", "--object-pattern"),
    ):
        value = params.get(param)
        if value:
            result.extend([option, str(value)])
    return result


def mark_ingest_failed(context: dict[str, Any]) -> None:
    """Best-effort audit callback; never masks the original task exception."""
    dag = context.get("dag")
    dag_id = str(getattr(dag, "dag_id", "unknown_cdc_dag"))
    orchestration_run_id = str(context.get("run_id", "unknown_run"))
    ingest_run_id = f"{dag_id}__{safe_run_id(orchestration_run_id)}"
    task_instance = context.get("task_instance")
    task_id = str(getattr(task_instance, "task_id", "unknown_task"))
    failure = f"{task_id}: {context.get('exception')}"
    subprocess.run(
        [
            *command_prefix(),
            "record-failure",
            "--ingest-run-id",
            ingest_run_id,
            "--dag-id",
            dag_id,
            "--orchestration-run-id",
            orchestration_run_id,
            "--failure-summary",
            failure[:65535],
        ],
        cwd=str(project_root()),
        check=False,
    )


def default_args() -> dict[str, Any]:
    return {
        "owner": "data-engineering",
        "retries": int(os.environ.get("OLIST_AIRFLOW_RETRIES", "2")),
        "retry_delay": timedelta(
            seconds=int(os.environ.get("OLIST_AIRFLOW_RETRY_DELAY_SECONDS", "300"))
        ),
        "retry_exponential_backoff": True,
    }


@task(
    task_id="load_closed_normalized_objects",
    pool=CDC_POOL,
    execution_timeout=timedelta(minutes=10),
    on_failure_callback=mark_ingest_failed,
)
def load_closed_normalized_objects(run_kind: str) -> dict[str, Any]:
    params, dag_id, orchestration_run_id = context_values()
    ingest_run_id = f"{dag_id}__{safe_run_id(orchestration_run_id)}"
    command = [
        *command_prefix(),
        "ingest",
        "--ingest-run-id",
        ingest_run_id,
        "--run-kind",
        run_kind,
        "--dag-id",
        dag_id,
        "--orchestration-run-id",
        orchestration_run_id,
    ]
    if run_kind == "REPLAY":
        command.extend(["--replay-request-id", ingest_run_id])
    command.extend(selector_args(params))
    return run_json_command(command)


@task(
    task_id="request_object_replay",
    pool=CDC_POOL,
    execution_timeout=timedelta(minutes=2),
)
def request_object_replay() -> dict[str, Any]:
    params, dag_id, orchestration_run_id = context_values()
    replay_id = f"{dag_id}__{safe_run_id(orchestration_run_id)}"
    return run_json_command(
        [
            *command_prefix(),
            "replay",
            "--replay-request-id",
            replay_id,
            "--requested-by",
            "airflow",
            *selector_args(params),
        ]
    )


@task(task_id="emit_raw_cdc_asset", outlets=[RAW_CDC_ASSET], pool=CDC_POOL)
def emit_raw_cdc_asset(summary: Any) -> None:
    if not isinstance(summary, Mapping):
        raise AirflowException("CDC ingest summary is not a mapping")
    if int(summary.get("inserted_rows", 0)) <= 0:
        raise AirflowSkipException("No new raw CDC events were committed")


@dag(
    dag_id=INGEST_DAG_ID,
    description="Discover and idempotently ingest closed local CDC Parquet objects.",
    default_args=default_args(),
    start_date=datetime(2026, 1, 1),
    schedule="*/2 * * * *",
    catchup=False,
    max_active_runs=1,
    max_active_tasks=2,
    dagrun_timeout=timedelta(minutes=12),
    tags=["olist", "cdc", "local", "postgres", "minio"],
)
def olist_cdc_ingest_local():
    summary = load_closed_normalized_objects("SCHEDULED")
    emit_raw_cdc_asset(summary)


@dag(
    dag_id=BACKFILL_DAG_ID,
    description="Replay selected immutable local CDC objects without duplicating events.",
    default_args=default_args(),
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    max_active_tasks=2,
    dagrun_timeout=timedelta(minutes=15),
    tags=["olist", "cdc", "local", "postgres", "replay"],
    params={
        "table": Param(None, type=["null", "string"], enum=[None, *CDC_TABLES]),
        "date_from": Param(
            None,
            type=["null", "string"],
            pattern=r"^\d{4}-\d{2}-\d{2}$",
        ),
        "date_to": Param(
            None,
            type=["null", "string"],
            pattern=r"^\d{4}-\d{2}-\d{2}$",
        ),
        "object_pattern": Param(None, type=["null", "string"]),
    },
)
def olist_cdc_backfill_local():
    replay = request_object_replay()
    summary = load_closed_normalized_objects("REPLAY")
    _ = replay >> summary
    emit_raw_cdc_asset(summary)


olist_cdc_ingest_local()
olist_cdc_backfill_local()
