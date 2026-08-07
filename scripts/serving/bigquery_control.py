"""BigQuery-native serving-control adapter and SQL state transitions.

The adapter intentionally depends on a tiny query-runner protocol instead of
``google-cloud-bigquery``.  Production wiring can provide the official client
later, while query construction, target isolation, and optimistic state
contracts remain testable without GCP credentials.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Protocol

from scripts.serving.domain import ServingTarget, TargetMismatchError
from scripts.serving.models import OperationType, StatusReason, SyncStatus

_PROJECT_ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$")
_CONTROL_TARGET = "gcp"
_CONTROL_DATASET = "olist_serving_control"


class BigQueryQueryRunner(Protocol):
    """Small seam for an official BigQuery client or a credential-free fake."""

    def execute(
        self,
        sql: str,
        parameters: Mapping[str, object],
    ) -> Iterable[Mapping[str, object]]: ...


def _first_row(
    rows: Iterable[Mapping[str, object]], operation: str
) -> dict[str, object]:
    for row in rows:
        return dict(row)
    raise RuntimeError(f"BigQuery control operation returned no row: {operation}")


def _row_count(rows: Iterable[Mapping[str, object]]) -> int:
    row = _first_row(rows, "row count")
    raw_count = row.get("updated_count", 0)
    if not isinstance(raw_count, (int, float, str)):
        raise RuntimeError(f"invalid BigQuery DML row count: {raw_count!r}")
    try:
        return int(raw_count)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"invalid BigQuery DML row count: {raw_count!r}") from exc


@dataclass(frozen=True, slots=True)
class BigQueryServingControlRepository:
    """GCP serving-control persistence in the dedicated control dataset."""

    runner: BigQueryQueryRunner
    project_id: str
    target: ServingTarget = ServingTarget.GCP
    dataset: str = _CONTROL_DATASET

    def __post_init__(self) -> None:
        if self.target is not ServingTarget.GCP:
            raise TargetMismatchError(
                "BigQueryServingControlRepository is reserved for the GCP target"
            )
        if not _PROJECT_ID_PATTERN.fullmatch(self.project_id):
            raise ValueError(f"invalid GCP project ID: {self.project_id!r}")
        if self.dataset != _CONTROL_DATASET:
            raise ValueError(
                "GCP serving control must remain in the dedicated control dataset"
            )

    def _table(self, name: str) -> str:
        if not re.fullmatch(r"[a-z_]+", name):
            raise ValueError(f"invalid control table name: {name!r}")
        return f"`{self.project_id}.{self.dataset}.{name}`"

    def _execute(
        self,
        sql: str,
        parameters: Mapping[str, object],
    ) -> list[Mapping[str, object]]:
        return list(self.runner.execute(sql, parameters))

    def allocate_sync_run(
        self,
        operation_type: OperationType,
        current_airflow_dag_run_id: str | None = None,
    ) -> dict[str, object]:
        """Allocate from GCP-local state; no local sequence is consulted."""

        state = self._table("control_state")
        runs = self._table("serving_runs")
        query = f"""
DECLARE allocated_seq INT64;
DECLARE predecessor_seq INT64;
SET allocated_seq = (
  SELECT next_sync_run_seq
  FROM {state}
  WHERE state_key = 'gcp' AND target = 'gcp'
);
SET predecessor_seq = (
  SELECT active_sync_run_seq
  FROM {state}
  WHERE state_key = 'gcp' AND target = 'gcp'
);
BEGIN TRANSACTION;
UPDATE {state}
SET next_sync_run_seq = allocated_seq + 1,
    row_version = row_version + 1,
    updated_at = CURRENT_TIMESTAMP()
WHERE state_key = 'gcp' AND target = 'gcp';
INSERT INTO {runs} (
  target,
  sync_run_seq,
  sync_run_id,
  operation_type,
  status,
  status_reason,
  current_airflow_dag_run_id,
  attempt_count,
  expected_active_sync_run_seq,
  created_at,
  updated_at
)
VALUES (
  'gcp',
  allocated_seq,
  FORMAT('gcp-sync-%020d', allocated_seq),
  @operation_type,
  'PLANNING',
  'NONE',
  @current_airflow_dag_run_id,
  1,
  predecessor_seq,
  CURRENT_TIMESTAMP(),
  CURRENT_TIMESTAMP()
);
COMMIT TRANSACTION;
SELECT *
FROM {runs}
WHERE target = 'gcp' AND sync_run_seq = allocated_seq;
"""
        row = _first_row(
            self._execute(
                query,
                {
                    "operation_type": operation_type.value,
                    "current_airflow_dag_run_id": current_airflow_dag_run_id,
                },
            ),
            "allocate sync run",
        )
        if str(row.get("target", _CONTROL_TARGET)) != _CONTROL_TARGET:
            raise TargetMismatchError("BigQuery returned a non-GCP serving run")
        return row

    def update_status(
        self,
        *,
        sync_run_seq: int,
        expected_status: SyncStatus | list[SyncStatus],
        new_status: SyncStatus,
        expected_active_sync_run_seq: int | None = None,
        status_reason: StatusReason = StatusReason.NONE,
        is_noop: bool | None = None,
        report_json: str | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> bool:
        """Apply a status transition only when the predecessor is still active."""

        statuses = (
            [expected_status.value]
            if isinstance(expected_status, SyncStatus)
            else [status.value for status in expected_status]
        )
        state = self._table("control_state")
        runs = self._table("serving_runs")
        query = f"""
UPDATE {runs}
SET status = @new_status,
    status_reason = @status_reason,
    is_noop = IF(@is_noop IS NULL, is_noop, @is_noop),
    report_json = IF(@report_json IS NULL, report_json, PARSE_JSON(@report_json)),
    error_code = @error_code,
    error_message = @error_message,
    completed_at = IF(
      @new_status IN ('SUCCEEDED', 'NOOP', 'FAILED_TERMINAL'),
      CURRENT_TIMESTAMP(),
      completed_at
    ),
    updated_at = CURRENT_TIMESTAMP()
WHERE target = 'gcp'
  AND sync_run_seq = @sync_run_seq
  AND status IN UNNEST(@expected_statuses)
  AND (
    @expected_active_sync_run_seq IS NULL
    OR (
      SELECT active_sync_run_seq
      FROM {state}
      WHERE state_key = 'gcp' AND target = 'gcp'
    ) = @expected_active_sync_run_seq
  );
SELECT @@row_count AS updated_count;
"""
        return (
            _row_count(
                self._execute(
                    query,
                    {
                        "sync_run_seq": sync_run_seq,
                        "expected_statuses": statuses,
                        "new_status": new_status.value,
                        "status_reason": status_reason.value,
                        "expected_active_sync_run_seq": expected_active_sync_run_seq,
                        "is_noop": is_noop,
                        "report_json": report_json,
                        "error_code": error_code,
                        "error_message": error_message,
                    },
                )
            )
            == 1
        )

    def prepare_same_run_retry(
        self,
        *,
        sync_run_seq: int,
        expected_active_sync_run_seq: int,
    ) -> bool:
        """Reset candidate results while retaining the frozen boundary and sequence."""

        state = self._table("control_state")
        runs = self._table("serving_runs")
        entity_results = self._table("entity_results")
        model_results = self._table("model_results")
        query = f"""
DECLARE updated_count INT64;
BEGIN TRANSACTION;
UPDATE {runs}
SET status = 'PLANNING',
    status_reason = 'NONE',
    attempt_count = attempt_count + 1,
    report_json = NULL,
    error_code = NULL,
    error_message = NULL,
    updated_at = CURRENT_TIMESTAMP()
WHERE target = 'gcp'
  AND sync_run_seq = @sync_run_seq
  AND status IN ('FAILED_RETRYABLE', 'MATERIALIZING', 'VALIDATING', 'READY_TO_PUBLISH')
  AND expected_active_sync_run_seq = @expected_active_sync_run_seq
  AND (
    SELECT active_sync_run_seq
    FROM {state}
    WHERE state_key = 'gcp' AND target = 'gcp'
  ) = @expected_active_sync_run_seq;
SET updated_count = @@row_count;
IF updated_count = 0 THEN
  ROLLBACK TRANSACTION;
  SELECT FALSE AS retried;
ELSE
  DELETE FROM {entity_results}
  WHERE target = 'gcp' AND sync_run_seq = @sync_run_seq;
  DELETE FROM {model_results}
  WHERE target = 'gcp' AND sync_run_seq = @sync_run_seq;
  COMMIT TRANSACTION;
  SELECT TRUE AS retried;
END IF;
"""
        row = _first_row(
            self._execute(
                query,
                {
                    "sync_run_seq": sync_run_seq,
                    "expected_active_sync_run_seq": expected_active_sync_run_seq,
                },
            ),
            "same-run retry",
        )
        return bool(row.get("retried", False))

    def advance_active_sync_run(
        self,
        *,
        sync_run_seq: int,
        expected_active_sync_run_seq: int,
    ) -> bool:
        """Compare-and-set active sequence for a prepared publication.

        The later publication procedure must compose this guard with all model
        mutations in one transaction.  This adapter method is the reusable
        predecessor contract, not a replacement for that procedure.
        """

        state = self._table("control_state")
        publication = self._table("publication_state")
        runs = self._table("serving_runs")
        query = f"""
DECLARE updated_count INT64;
BEGIN TRANSACTION;
UPDATE {state}
SET active_sync_run_seq = @sync_run_seq,
    row_version = row_version + 1,
    updated_at = CURRENT_TIMESTAMP()
WHERE state_key = 'gcp'
  AND target = 'gcp'
  AND active_sync_run_seq = @expected_active_sync_run_seq
  AND EXISTS (
    SELECT 1
    FROM {runs}
    WHERE target = 'gcp'
      AND sync_run_seq = @sync_run_seq
      AND expected_active_sync_run_seq = @expected_active_sync_run_seq
      AND status = 'READY_TO_PUBLISH'
  );
SET updated_count = @@row_count;
IF updated_count = 0 THEN
  ROLLBACK TRANSACTION;
  SELECT 0 AS updated_count;
ELSE
  UPDATE {publication}
  SET active_sync_run_seq = @sync_run_seq,
      updated_at = CURRENT_TIMESTAMP()
  WHERE state_key = 'gcp' AND target = 'gcp';
  COMMIT TRANSACTION;
  SELECT updated_count;
END IF;
"""
        return (
            _row_count(
                self._execute(
                    query,
                    {
                        "sync_run_seq": sync_run_seq,
                        "expected_active_sync_run_seq": expected_active_sync_run_seq,
                    },
                )
            )
            == 1
        )

    def get_runtime_state(self) -> dict[str, object]:
        state = self._table("control_state")
        rows = self._execute(
            f"""
SELECT *
FROM {state}
WHERE state_key = 'gcp' AND target = 'gcp'
""",
            {},
        )
        row = _first_row(rows, "get runtime state")
        if str(row.get("target", _CONTROL_TARGET)) != _CONTROL_TARGET:
            raise TargetMismatchError("BigQuery returned a non-GCP runtime state")
        return row
