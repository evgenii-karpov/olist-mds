"""BigQuery-native serving-control adapter and SQL state transitions.

The adapter intentionally depends on a tiny query-runner protocol instead of
``google-cloud-bigquery``.  Production wiring can provide the official client
later, while query construction, target isolation, and optimistic state
contracts remain testable without GCP credentials.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Protocol

from scripts.serving.domain import (
    ServingBoundary,
    ServingTarget,
    TargetMismatchError,
)
from scripts.serving.models import (
    OperationType,
    StatusReason,
    SyncStatus,
    canonical_json_bytes,
)

_PROJECT_ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$")
_CONTROL_TARGET = "gcp"
_CONTROL_DATASET = "olist_serving_control"
_BRIDGE_DATASET = "olist_lakehouse_bridge"
_GOLD_DATASET = "olist_gold_store"
_GOLD_HISTORY_MODELS = (
    "dim_date",
    "dim_order_status",
    "dim_seller",
    "dim_customer_scd2",
    "dim_product_scd2",
    "fact_order_items",
    "mart_daily_revenue",
    "mart_monthly_arpu",
)
_TOPIC_PARTITION_PATTERN = re.compile(
    r"^(?P<topic>[A-Za-z0-9._-]+):(?P<partition>[0-9]+)$"
)


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


def _optional_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _topic_partition(value: str) -> tuple[str, int]:
    match = _TOPIC_PARTITION_PATTERN.fullmatch(value)
    if match is None:
        raise ValueError(f"invalid topic-partition key: {value!r}")
    return match.group("topic"), int(match.group("partition"))


def _boundary_id(
    sync_run_seq: int,
    target_offsets: Mapping[str, int],
    previous_offsets: Mapping[str, int],
    *,
    previous_transaction_id: str | None,
    previous_transaction_end_offset: int | None,
    target_transaction_id: str | None,
    target_transaction_end_offset: int | None,
    source_snapshot_completed: bool,
    iceberg_snapshot_ids: Mapping[str, int],
) -> str:
    payload = {
        "sync_run_seq": sync_run_seq,
        "previous_offsets": dict(sorted(previous_offsets.items())),
        "target_offsets": dict(sorted(target_offsets.items())),
        "previous_transaction_id": previous_transaction_id,
        "previous_transaction_end_offset": previous_transaction_end_offset,
        "target_transaction_id": target_transaction_id,
        "target_transaction_end_offset": target_transaction_end_offset,
        "source_snapshot_completed": source_snapshot_completed,
        "iceberg_snapshot_ids": dict(sorted(iceberg_snapshot_ids.items())),
    }
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _progress_entity(topic: str) -> str:
    return topic.rsplit(".", 1)[-1]


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
        if not re.fullmatch(r"[a-z0-9_]+", name):
            raise ValueError(f"invalid control table name: {name!r}")
        return f"`{self.project_id}.{self.dataset}.{name}`"

    def _dataset_table(self, dataset: str, name: str) -> str:
        if not re.fullmatch(r"[a-z_]+", dataset):
            raise ValueError(f"invalid dataset name: {dataset!r}")
        if not re.fullmatch(r"[a-z0-9_]+", name):
            raise ValueError(f"invalid table name: {name!r}")
        return f"`{self.project_id}.{dataset}.{name}`"

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

    def persist_frozen_boundary(
        self,
        *,
        sync_run_seq: int,
        boundary: ServingBoundary,
        expected_active_sync_run_seq: int,
        previous_offsets: Mapping[str, int] | None = None,
        iceberg_snapshot_ids: Mapping[str, int] | None = None,
        previous_boundary_id: str | None = None,
        current_boundary_id: str | None = None,
    ) -> dict[str, object]:
        """Persist one immutable offset interval and attach it to the run.

        The SQL is intentionally generated from validated topic/partition
        keys. Values remain named query parameters, so the production runner
        can map them to BigQuery query parameters without interpolating data.
        """

        if boundary.target is not ServingTarget.GCP:
            raise TargetMismatchError("GCP boundary required")
        if boundary.sync_run_seq != sync_run_seq:
            raise ValueError("boundary and sync sequence must match")
        if sync_run_seq < 1:
            raise ValueError("sync_run_seq must be positive")

        target_offsets = dict(boundary.target_offsets)
        prior_offsets = dict(previous_offsets or {})
        snapshot_ids = dict(iceberg_snapshot_ids or {})
        if not target_offsets:
            raise ValueError("a frozen boundary requires target offsets")
        for key, offset in (*target_offsets.items(), *prior_offsets.items()):
            _topic_partition(key)
            if not isinstance(offset, int) or offset < 0:
                raise ValueError(f"offset must be a non-negative integer: {key}")

        computed_id = _boundary_id(
            sync_run_seq,
            target_offsets,
            prior_offsets,
            previous_transaction_id=boundary.previous_transaction_id,
            previous_transaction_end_offset=boundary.previous_transaction_end_offset,
            target_transaction_id=boundary.target_transaction_id,
            target_transaction_end_offset=boundary.target_transaction_end_offset,
            source_snapshot_completed=boundary.source_snapshot_completed,
            iceberg_snapshot_ids=snapshot_ids,
        )
        if current_boundary_id is not None and current_boundary_id != computed_id:
            raise ValueError("current_boundary_id does not match boundary contents")
        current_id = computed_id
        previous_id = previous_boundary_id
        boundary_table = self._table("boundary_offsets")
        runs = self._table("serving_runs")

        value_rows: list[str] = []
        parameters: dict[str, object] = {
            "sync_run_seq": sync_run_seq,
            "expected_active_sync_run_seq": expected_active_sync_run_seq,
            "previous_boundary_id": previous_id,
            "current_boundary_id": current_id,
            "previous_transaction_id": boundary.previous_transaction_id,
            "previous_transaction_end_offset": boundary.previous_transaction_end_offset,
            "target_transaction_id": boundary.target_transaction_id,
            "target_transaction_end_offset": boundary.target_transaction_end_offset,
            "source_snapshot_completed": boundary.source_snapshot_completed,
            "target_offsets_json": json.dumps(target_offsets, sort_keys=True),
            "iceberg_snapshot_ids_json": json.dumps(snapshot_ids, sort_keys=True),
        }
        for index, (key, target_offset) in enumerate(sorted(target_offsets.items())):
            topic, partition = _topic_partition(key)
            previous_offset = prior_offsets.get(key)
            topic_name = f"topic_{index}"
            partition_name = f"partition_{index}"
            previous_name = f"previous_{index}"
            target_name = f"target_{index}"
            parameters[topic_name] = topic
            parameters[partition_name] = partition
            parameters[previous_name] = previous_offset
            parameters[target_name] = target_offset
            value_rows.append(
                "  SELECT @"
                f"{topic_name} AS topic, @{partition_name} AS partition_id, "
                f"@{previous_name} AS previous_offset, @{target_name} AS target_offset"
            )

        candidate_sql = "\nUNION ALL\n".join(value_rows)
        query = f"""
DECLARE updated_count INT64;
BEGIN TRANSACTION;
INSERT INTO {boundary_table} (
  target, sync_run_seq, topic, partition_id, previous_offset, target_offset,
  transaction_id, frozen_at
)
SELECT
  'gcp',
  @sync_run_seq,
  candidate.topic,
  candidate.partition_id,
  candidate.previous_offset,
  candidate.target_offset,
  @target_transaction_id,
  CURRENT_TIMESTAMP()
FROM (
{candidate_sql}
) AS candidate
WHERE NOT EXISTS (
  SELECT 1
  FROM {boundary_table}
  WHERE target = 'gcp' AND sync_run_seq = @sync_run_seq
);
UPDATE {runs}
SET previous_boundary_id = @previous_boundary_id,
    current_boundary_id = @current_boundary_id,
    previous_transaction_id = @previous_transaction_id,
    previous_transaction_end_offset = @previous_transaction_end_offset,
    target_transaction_id = @target_transaction_id,
    target_transaction_end_offset = @target_transaction_end_offset,
    source_snapshot_completed = @source_snapshot_completed,
    target_offsets = PARSE_JSON(@target_offsets_json),
    iceberg_snapshot_ids = PARSE_JSON(@iceberg_snapshot_ids_json),
    status = 'MATERIALIZING',
    updated_at = CURRENT_TIMESTAMP()
WHERE target = 'gcp'
  AND sync_run_seq = @sync_run_seq
  AND status = 'PLANNING'
  AND expected_active_sync_run_seq = @expected_active_sync_run_seq
  AND (
    current_boundary_id IS NULL
    OR current_boundary_id = @current_boundary_id
  );
SET updated_count = @@row_count;
IF updated_count = 0 THEN
  ROLLBACK TRANSACTION;
  SELECT 0 AS updated_count;
ELSE
  COMMIT TRANSACTION;
  SELECT updated_count;
END IF;
"""
        persisted = _row_count(self._execute(query, parameters)) == 1
        return {
            "persisted": persisted,
            "sync_run_seq": sync_run_seq,
            "current_boundary_id": current_id,
            "previous_boundary_id": previous_id,
            "target_offsets": target_offsets,
        }

    def check_silver_progress(
        self,
        *,
        target_offsets: Mapping[str, int],
    ) -> dict[str, object]:
        """Check that every frozen topic-partition has committed Silver progress."""

        if not target_offsets:
            raise ValueError("progress check requires target offsets")
        expected_keys = list(sorted(target_offsets))
        entities = sorted(
            {_progress_entity(_topic_partition(key)[0]) for key in expected_keys}
        )
        topics = sorted({_topic_partition(key)[0] for key in expected_keys})
        progress_table = self._dataset_table(_BRIDGE_DATASET, "audit_silver_progress")
        query = f"""
SELECT entity, source_topic, kafka_partition, last_kafka_offset, status,
       updated_at, spark_batch_id
FROM {progress_table}
WHERE entity IN UNNEST(@entities)
  AND source_topic IN UNNEST(@source_topics)
"""
        rows = [
            dict(row)
            for row in self._execute(
                query,
                {"entities": entities, "source_topics": topics},
            )
        ]
        latest: dict[tuple[str, int], dict[str, object]] = {}
        for row in rows:
            topic = row.get("source_topic")
            partition = row.get("kafka_partition")
            if not isinstance(topic, str) or not isinstance(partition, int):
                continue
            key = (topic, partition)
            previous = latest.get(key)
            row_order = (
                str(row.get("updated_at", "")),
                _optional_int(row.get("spark_batch_id")) or 0,
            )
            if previous is None:
                latest[key] = row
                continue
            previous_order = (
                str(previous.get("updated_at", "")),
                _optional_int(previous.get("spark_batch_id")) or 0,
            )
            if row_order >= previous_order:
                latest[key] = row

        missing: list[str] = []
        for key in expected_keys:
            topic, partition = _topic_partition(key)
            progress = latest.get((topic, partition))
            last_offset = progress.get("last_kafka_offset") if progress else None
            if (
                progress is None
                or str(progress.get("status", "")) != "COMMITTED"
                or not isinstance(last_offset, int)
                or last_offset < target_offsets[key]
            ):
                missing.append(key)

        return {
            "status": "READY" if not missing else "WAITING",
            "missing": missing,
            "checked_rows": len(rows),
            "target_offsets": dict(target_offsets),
        }

    def fetch_transaction_rows(self) -> list[dict[str, object]]:
        """Read append-only Debezium transaction observations from the bridge."""

        transactions = self._dataset_table(_BRIDGE_DATASET, "audit_mysql_transactions")
        query = f"""
SELECT
  transaction_id,
  status,
  event_count,
  data_collections,
  begin_event_id,
  end_event_id,
  kafka_topic,
  kafka_partition,
  begin_kafka_offset,
  end_kafka_offset,
  source_ts,
  first_seen_at,
  completed_at,
  rejected_event_ids,
  recorded_at
FROM {transactions}
ORDER BY
  COALESCE(end_kafka_offset, begin_kafka_offset),
  recorded_at,
  transaction_id
"""
        return [dict(row) for row in self._execute(query, {})]

    def revalidate_silver_progress(
        self,
        *,
        target_offsets: Mapping[str, int],
    ) -> dict[str, object]:
        """Repeat the exact progress proof after the dbt candidate build."""

        return self.check_silver_progress(target_offsets=target_offsets)

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
        history_tables = tuple(
            self._dataset_table(_GOLD_DATASET, f"{model}__history")
            for model in _GOLD_HISTORY_MODELS
        )
        history_cleanup = "\n".join(
            f"  DELETE FROM {table} WHERE sync_run_seq = @sync_run_seq;"
            for table in history_tables
        )
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
{history_cleanup}
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
