"""Reusable bounded polling and PostgreSQL relation helpers for CI checks."""

from __future__ import annotations

import json
import os
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import connection as PgConnection
from psycopg2.extensions import cursor as PgCursor

TERMINAL_DAG_STATES = {"success", "failed"}
DEFAULT_FINGERPRINT_COLUMNS: dict[str, list[str]] = {
    "core.dim_customer_scd2": [
        "customer_key",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
        "latest_correction_effective_at",
        "latest_change_reason",
        "valid_from",
        "valid_to",
        "is_current",
    ],
    "core.dim_product_scd2": [
        "product_key",
        "product_id",
        "product_category_name",
        "product_category_name_english",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
        "latest_correction_effective_at",
        "latest_change_reason",
        "valid_from",
        "valid_to",
        "is_current",
    ],
    "core.dim_seller": [
        "seller_key",
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ],
    "core.dim_date": ["date_key", "date_day"],
    "core.dim_order_status": ["order_status_key", "order_status"],
    "core.fact_order_items": [
        "order_item_key",
        "order_id",
        "order_item_id",
        "customer_key",
        "product_key",
        "seller_key",
        "order_status_key",
        "order_purchase_date_key",
        "order_approved_date_key",
        "order_delivered_customer_date_key",
        "order_estimated_delivery_date_key",
        "customer_id",
        "customer_unique_id",
        "product_id",
        "seller_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "shipping_limit_date",
        "price",
        "freight_value",
        "gross_item_amount",
        "allocated_payment_value",
        "delivery_days",
        "delivery_delay_days",
        "is_delivered_late",
    ],
    "marts.mart_daily_revenue": [
        "order_purchase_date",
        "gross_revenue",
        "product_revenue",
        "freight_revenue",
        "allocated_payment_revenue",
        "orders_count",
        "customers_count",
        "items_count",
        "late_deliveries_count",
        "average_order_value",
        "average_paid_order_value",
    ],
    "marts.mart_monthly_arpu": [
        "order_month",
        "active_customers",
        "orders_count",
        "total_revenue",
        "arpu",
        "orders_per_customer",
        "average_order_value",
        "repeat_customer_rate",
    ],
}


@dataclass(frozen=True)
class RelationFingerprint:
    row_count: int
    checksum: str


def pipeline_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("POSTGRES_HOST", "postgres")
    env.setdefault("POSTGRES_PORT", "5432")
    env.setdefault("POSTGRES_DB", "olist_analytics")
    env.setdefault("POSTGRES_USER", "olist")
    env.setdefault("POSTGRES_PASSWORD", "olist")
    return env


def postgres_connection(env: dict[str, str] | None = None) -> PgConnection:
    settings = pipeline_env() if env is None else env
    return psycopg2.connect(
        host=settings["POSTGRES_HOST"],
        port=int(settings["POSTGRES_PORT"]),
        dbname=settings["POSTGRES_DB"],
        user=settings["POSTGRES_USER"],
        password=settings["POSTGRES_PASSWORD"],
    )


def airflow_metadata_connection() -> PgConnection:
    return psycopg2.connect(
        host=os.environ.get("AIRFLOW_POSTGRES_HOST", "airflow-postgres"),
        port=int(os.environ.get("AIRFLOW_POSTGRES_PORT", "5432")),
        dbname=os.environ.get("AIRFLOW_POSTGRES_DB", "airflow"),
        user=os.environ.get("AIRFLOW_POSTGRES_USER", "airflow"),
        password=os.environ.get("AIRFLOW_POSTGRES_PASSWORD", "airflow"),
    )


def control_postgres_connection() -> PgConnection:
    return psycopg2.connect(
        host=os.environ.get("CONTROL_POSTGRES_HOST", "airflow-postgres"),
        port=int(os.environ.get("CONTROL_POSTGRES_PORT", "5432")),
        dbname=os.environ.get("CONTROL_POSTGRES_DB", "olist_control"),
        user=os.environ.get("CONTROL_POSTGRES_USER", "olist_control"),
        password=os.environ.get("CONTROL_POSTGRES_PASSWORD", "olist_control"),
    )


def fetch_dag_run_state(dag_id: str, run_id: str) -> str | None:
    with airflow_metadata_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            select state
            from dag_run
            where dag_id = %s and run_id = %s
            """,
            (dag_id, run_id),
        )
        row = cursor.fetchone()
    return None if row is None else str(row[0])


def fetch_failed_tasks(dag_id: str, run_id: str) -> list[tuple[str, str]]:
    with airflow_metadata_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            select task_id, state
            from task_instance
            where dag_id = %s
              and run_id = %s
              and state in ('failed', 'upstream_failed')
            order by task_id
            """,
            (dag_id, run_id),
        )
        rows = cursor.fetchall()
    return [(str(task_id), str(state)) for task_id, state in rows]


def wait_for_dag_success(
    dag_id: str,
    run_id: str,
    *,
    timeout_seconds: float,
    poll_seconds: float,
    state_fetcher: Callable[[str, str], str | None] = fetch_dag_run_state,
    failed_task_fetcher: Callable[
        [str, str], list[tuple[str, str]]
    ] = fetch_failed_tasks,
    on_state: Callable[[str | None], None] | None = None,
    on_failure: Callable[[list[tuple[str, str]]], None] | None = None,
) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_state: str | None = None
    while time.monotonic() < deadline:
        state = state_fetcher(dag_id, run_id)
        if state != last_state:
            if on_state is not None:
                on_state(state)
            last_state = state
        if state == "success":
            return
        if state in TERMINAL_DAG_STATES:
            failed_tasks = failed_task_fetcher(dag_id, run_id)
            if on_failure is not None:
                on_failure(failed_tasks)
            raise AssertionError(
                f"DAG run {run_id} finished with state={state}; "
                f"failed_tasks={json.dumps(failed_tasks)}"
            )
        time.sleep(min(poll_seconds, max(0.0, deadline - time.monotonic())))

    raise TimeoutError(
        f"Timed out after {timeout_seconds}s waiting for DAG run {run_id}; "
        f"last_state={last_state!r}"
    )


def fetch_one(cursor: PgCursor) -> tuple[Any, ...]:
    row = cursor.fetchone()
    if row is None:
        raise AssertionError("Expected query to return exactly one row")
    return row


def fingerprint_expression(columns: Sequence[str]) -> sql.Composable:
    values = [
        sql.SQL("coalesce({}::text, '<NULL>')").format(sql.Identifier(column))
        for column in columns
    ]
    return sql.SQL("concat_ws('|', {})").format(sql.SQL(", ").join(values))


def relation_fingerprint(
    connection: PgConnection,
    relation_name: str,
    columns: Sequence[str],
) -> RelationFingerprint:
    schema_name, table_name = relation_name.split(".", maxsplit=1)
    query = sql.SQL(
        """
        with row_fingerprints as (
            select md5({fingerprint_expression}) as row_fingerprint
            from {schema_name}.{table_name}
        )
        select
            count(*)::bigint as row_count,
            coalesce(
                md5(string_agg(row_fingerprint, '|' order by row_fingerprint)),
                md5('')
            ) as checksum
        from row_fingerprints;
        """
    ).format(
        fingerprint_expression=fingerprint_expression(columns),
        schema_name=sql.Identifier(schema_name),
        table_name=sql.Identifier(table_name),
    )
    with connection.cursor() as cursor:
        cursor.execute(query)
        row_count, checksum = fetch_one(cursor)
    return RelationFingerprint(row_count=int(row_count), checksum=str(checksum))


def capture_fingerprints(
    connection: PgConnection,
    relations: dict[str, list[str]] | None = None,
) -> dict[str, RelationFingerprint]:
    selected = DEFAULT_FINGERPRINT_COLUMNS if relations is None else relations
    return {
        relation_name: relation_fingerprint(connection, relation_name, columns)
        for relation_name, columns in selected.items()
    }
