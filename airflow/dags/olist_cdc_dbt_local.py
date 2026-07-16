"""Phase 5 Asset-triggered realtime dbt and scheduled quality DAGs."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from airflow.sdk import Asset, dag, get_current_context, task
from airflow.sdk.exceptions import AirflowException

TRANSFORM_DAG_ID = "olist_cdc_transform_local"
QUALITY_DAG_ID = "olist_cdc_quality_local"
RAW_CDC_ASSET = Asset("olist://cdc/raw/local")
CDC_POOL = os.environ.get("OLIST_CDC_AIRFLOW_POOL", "default_pool")


def project_root() -> Path:
    configured = os.environ.get("OLIST_PROJECT_ROOT")
    return Path(configured) if configured else Path(__file__).resolve().parents[2]


def safe_run_id(value: str) -> str:
    return value.replace(":", "_").replace("+", "_")


def transform_run_id() -> str:
    context = get_current_context()
    run_id = context.get("run_id")
    if run_id is None:
        raise AirflowException("Airflow context has no run_id")
    return f"{TRANSFORM_DAG_ID}__{safe_run_id(str(run_id))}"


def command_prefix() -> list[str]:
    return [
        os.environ.get("OLIST_PYTHON_BIN", "python"),
        "scripts/cdc/realtime_transform.py",
    ]


def run_json(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(
        command,
        cwd=project_root(),
        check=True,
        capture_output=True,
        text=True,
    )
    lines = result.stdout.strip().splitlines()
    if not lines:
        raise AirflowException("realtime transform command returned no summary")
    summary = json.loads(lines[-1])
    if not isinstance(summary, dict):
        raise AirflowException("realtime transform summary must be an object")
    return summary


def mark_transform_failed(context: dict[str, Any]) -> None:
    """Best-effort callback that preserves the original dbt exception."""
    run_id = f"{TRANSFORM_DAG_ID}__{safe_run_id(str(context.get('run_id', 'unknown')))}"
    subprocess.run(
        [
            *command_prefix(),
            "fail",
            "--transform-run-id",
            run_id,
            "--failure-summary",
            str(context.get("exception", "unknown transform failure"))[:65535],
        ],
        cwd=project_root(),
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
    task_id="prepare_transform",
    pool=CDC_POOL,
    execution_timeout=timedelta(minutes=2),
    on_failure_callback=mark_transform_failed,
)
def prepare_transform() -> dict[str, Any]:
    context = get_current_context()
    orchestration_run_id = context.get("run_id")
    if orchestration_run_id is None:
        raise AirflowException("Airflow context has no run_id")
    return run_json(
        [
            *command_prefix(),
            "prepare",
            "--transform-run-id",
            transform_run_id(),
            "--dag-id",
            TRANSFORM_DAG_ID,
            "--orchestration-run-id",
            str(orchestration_run_id),
        ]
    )


@task(
    task_id="build_realtime_models",
    pool=CDC_POOL,
    execution_timeout=timedelta(minutes=8),
    on_failure_callback=mark_transform_failed,
)
def build_realtime_models(_: Any) -> dict[str, Any]:
    return run_json(
        [
            *command_prefix(),
            "build",
            "--transform-run-id",
            transform_run_id(),
        ]
    )


@task(
    task_id="commit_transform_checkpoint",
    pool=CDC_POOL,
    execution_timeout=timedelta(minutes=2),
    on_failure_callback=mark_transform_failed,
)
def commit_transform_checkpoint(_: Any) -> dict[str, Any]:
    return run_json(
        [
            *command_prefix(),
            "finish",
            "--transform-run-id",
            transform_run_id(),
        ]
    )


@task(task_id="run_quality", pool=CDC_POOL, execution_timeout=timedelta(minutes=20))
def run_quality() -> dict[str, Any]:
    context = get_current_context()
    logical_date = context.get("logical_date")
    if logical_date is None:
        raise AirflowException("Airflow context has no logical_date")
    command = [*command_prefix(), "quality"]
    if logical_date.hour == 0:
        command.append("--full")
    return run_json(command)


@dag(
    dag_id=TRANSFORM_DAG_ID,
    description="Build the exact local CDC manifest micro-batch after raw Asset commit.",
    default_args=default_args(),
    start_date=datetime(2026, 1, 1),
    schedule=[RAW_CDC_ASSET],
    catchup=False,
    max_active_runs=1,
    max_active_tasks=1,
    dagrun_timeout=timedelta(minutes=12),
    tags=["olist", "cdc", "local", "dbt", "realtime"],
)
def olist_cdc_transform_local():
    prepared = prepare_transform()
    built = build_realtime_models(prepared)
    commit_transform_checkpoint(built)


@dag(
    dag_id=QUALITY_DAG_ID,
    description="Hourly realtime integrity checks with nightly full dbt and Elementary.",
    default_args=default_args(),
    start_date=datetime(2026, 1, 1),
    schedule="0 * * * *",
    catchup=False,
    max_active_runs=1,
    max_active_tasks=1,
    dagrun_timeout=timedelta(minutes=25),
    tags=["olist", "cdc", "local", "dbt", "quality"],
)
def olist_cdc_quality_local():
    run_quality()


olist_cdc_transform_local()
olist_cdc_quality_local()
