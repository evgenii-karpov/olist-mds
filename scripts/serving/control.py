"""PostgreSQL serving ledger repository, state machine, durable lease and reconciliation."""

from __future__ import annotations

import contextlib
import datetime
import json
import os
from collections.abc import Iterator
from typing import cast

import psycopg2
from psycopg2.extras import RealDictCursor

from scripts.serving.models import (
    OperationType,
    StatusReason,
    SyncStatus,
)


def get_control_connection_params() -> dict[str, str | int]:
    host = os.environ.get("CONTROL_POSTGRES_HOST", "127.0.0.1")
    port = int(os.environ.get("CONTROL_POSTGRES_PORT", "5432"))
    db = os.environ.get("CONTROL_POSTGRES_DB", "olist_control")
    user = os.environ.get("CONTROL_POSTGRES_USER", "olist_control")

    password_file = os.environ.get(
        "CONTROL_POSTGRES_PASSWORD_FILE",
        "docker/secrets/dev/control_postgres_password.txt",
    )
    password = ""
    if os.path.exists(password_file):
        with open(password_file, encoding="utf-8") as f:
            password = f.read().strip()

    return {
        "host": host,
        "port": port,
        "dbname": db,
        "user": user,
        "password": password,
    }


@contextlib.contextmanager
def control_db_cursor() -> Iterator[RealDictCursor]:
    params = get_control_connection_params()
    conn = psycopg2.connect(
        host=str(params["host"]),
        port=int(params["port"]),
        dbname=str(params["dbname"]),
        user=str(params["user"]),
        password=str(params["password"]),
    )
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


class ServingControlRepository:
    @staticmethod
    def allocate_sync_run(
        operation_type: OperationType,
        current_airflow_dag_run_id: str | None = None,
    ) -> dict[str, object]:
        with control_db_cursor() as cur:
            cur.execute("SELECT nextval('serving.sync_run_seq') AS seq")
            row = cur.fetchone()
            seq = cast(int, row["seq"]) if row else 1
            sync_run_id = f"sync-{seq:020d}"

            cur.execute(
                """
                INSERT INTO serving.sync_runs (
                    sync_run_seq, sync_run_id, operation_type, status, status_reason,
                    current_airflow_dag_run_id, attempt_count
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, 1
                ) RETURNING *
                """,
                (
                    seq,
                    sync_run_id,
                    operation_type.value,
                    SyncStatus.PLANNING.value,
                    StatusReason.NONE.value,
                    current_airflow_dag_run_id,
                ),
            )
            inserted = cur.fetchone()
            return dict(inserted) if inserted else {}

    @staticmethod
    def update_status(
        sync_run_seq: int,
        expected_status: SyncStatus | list[SyncStatus],
        new_status: SyncStatus,
        status_reason: StatusReason = StatusReason.NONE,
        report_json: dict[str, object] | None = None,
        error_details_json: dict[str, object] | None = None,
        published_at: datetime.datetime | None = None,
    ) -> bool:
        expected_list = (
            [expected_status.value]
            if isinstance(expected_status, SyncStatus)
            else [s.value for s in expected_status]
        )
        completed_at = (
            datetime.datetime.now(datetime.UTC)
            if new_status
            in (SyncStatus.SUCCEEDED, SyncStatus.NOOP, SyncStatus.FAILED_TERMINAL)
            else None
        )

        with control_db_cursor() as cur:
            cur.execute(
                """
                UPDATE serving.sync_runs
                SET status = %s,
                    status_reason = %s,
                    report_json = COALESCE(%s, report_json),
                    error_details_json = COALESCE(%s, error_details_json),
                    published_at = COALESCE(%s, published_at),
                    completed_at = COALESCE(%s, completed_at),
                    updated_at = clock_timestamp()
                WHERE sync_run_seq = %s AND status = ANY(%s)
                """,
                (
                    new_status.value,
                    status_reason.value,
                    json.dumps(report_json) if report_json else None,
                    json.dumps(error_details_json) if error_details_json else None,
                    published_at,
                    completed_at,
                    sync_run_seq,
                    expected_list,
                ),
            )
            return cur.rowcount > 0

    @staticmethod
    def acquire_lease(
        owner_id: str,
        operation: str,
        sync_run_seq: int | None = None,
        ttl_seconds: int = 1800,
    ) -> bool:
        now = datetime.datetime.now(datetime.UTC)
        expires_at = now + datetime.timedelta(seconds=ttl_seconds)

        with control_db_cursor() as cur:
            cur.execute(
                """
                UPDATE serving.runtime_state
                SET lease_owner_id = %s,
                    lease_operation = %s,
                    lease_owner_sync_run_seq = %s,
                    lease_acquired_at = %s,
                    lease_heartbeat_at = %s,
                    lease_expires_at = %s,
                    updated_at = clock_timestamp()
                WHERE singleton_key = 1 AND (
                    lease_expires_at IS NULL OR lease_expires_at < %s OR lease_owner_id = %s
                )
                """,
                (
                    owner_id,
                    operation,
                    sync_run_seq,
                    now,
                    now,
                    expires_at,
                    now,
                    owner_id,
                ),
            )
            return cur.rowcount > 0

    @staticmethod
    def heartbeat_lease(owner_id: str, ttl_seconds: int = 1800) -> bool:
        now = datetime.datetime.now(datetime.UTC)
        expires_at = now + datetime.timedelta(seconds=ttl_seconds)

        with control_db_cursor() as cur:
            cur.execute(
                """
                UPDATE serving.runtime_state
                SET lease_heartbeat_at = %s,
                    lease_expires_at = %s,
                    updated_at = clock_timestamp()
                WHERE singleton_key = 1 AND lease_owner_id = %s
                """,
                (now, expires_at, owner_id),
            )
            return cur.rowcount > 0

    @staticmethod
    def release_lease(owner_id: str) -> bool:
        with control_db_cursor() as cur:
            cur.execute(
                """
                UPDATE serving.runtime_state
                SET lease_owner_id = NULL,
                    lease_operation = NULL,
                    lease_owner_sync_run_seq = NULL,
                    lease_acquired_at = NULL,
                    lease_heartbeat_at = NULL,
                    lease_expires_at = NULL,
                    updated_at = clock_timestamp()
                WHERE singleton_key = 1 AND lease_owner_id = %s
                """,
                (owner_id,),
            )
            return cur.rowcount > 0

    @staticmethod
    def get_runtime_state() -> dict[str, object]:
        with control_db_cursor() as cur:
            cur.execute("SELECT * FROM serving.runtime_state WHERE singleton_key = 1")
            row = cur.fetchone()
            return dict(row) if row else {}

    @staticmethod
    def update_published_cursor(
        sync_run_seq: int,
        transaction_id: str | None,
        end_offset: int | None,
        target_offsets_json: dict[str, int],
        snapshot_completed: bool,
    ) -> None:
        with control_db_cursor() as cur:
            cur.execute(
                """
                UPDATE serving.runtime_state
                SET last_published_sync_run_seq = %s,
                    last_published_transaction_id = %s,
                    last_published_transaction_end_offset = %s,
                    last_published_target_offsets_json = %s,
                    source_snapshot_completed = %s,
                    updated_at = clock_timestamp()
                WHERE singleton_key = 1
                """,
                (
                    sync_run_seq,
                    transaction_id,
                    end_offset,
                    json.dumps(target_offsets_json),
                    snapshot_completed,
                ),
            )
