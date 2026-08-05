"""Serving transaction boundary planner and caught-up target resolution."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime

from scripts.serving.entities import ALL_SERVING_ENTITIES

logger = logging.getLogger(__name__)


def _as_int(value: object, default: int = 0) -> int:
    return int(value) if isinstance(value, (int, float, str)) else default


def _optional_int(value: object) -> int | None:
    if not isinstance(value, (int, float, str)):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _timestamp_key(value: object) -> str:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value) if value is not None else ""


def _transaction_observation_order(row: dict[str, object]) -> tuple[object, ...]:
    """Return a deterministic order for append-only transaction observations.

    Kafka offsets are the primary progress coordinate.  ``recorded_at`` is the
    tie-breaker for a BEGIN/END pair written in separate Spark micro-batches;
    the status rank only resolves identical coordinates and makes COMPLETE win
    over an otherwise equal OPEN/REJECTED observation.
    """

    end_offset = _optional_int(row.get("end_kafka_offset"))
    begin_offset = _optional_int(row.get("begin_kafka_offset"))
    effective_offset = end_offset if end_offset is not None else begin_offset
    status_rank = {"OPEN": 0, "REJECTED": 1, "COMPLETE": 2}.get(
        str(row.get("status", "")), -1
    )
    return (
        effective_offset if effective_offset is not None else -1,
        _timestamp_key(row.get("recorded_at")),
        1 if end_offset is not None else 0,
        status_rank,
        str(row.get("end_event_id", "")),
        str(row.get("begin_event_id", "")),
    )


def transaction_sort_key(row: dict[str, object]) -> tuple[object, ...]:
    """Sort effective transaction rows in source-boundary order."""

    return (
        *_transaction_observation_order(row),
        str(row.get("transaction_id", "")),
    )


def collapse_transaction_history(
    rows: Iterable[dict[str, object]],
) -> list[dict[str, object]]:
    """Collapse append-only transaction observations to effective state.

    The audit table intentionally retains immutable observations.  Serving,
    however, needs exactly one state per transaction: a BEGIN followed by a
    later END is COMPLETE, an unresolved BEGIN remains OPEN, and duplicate END
    observations are idempotent.  Rows with an invalid/missing transaction id
    are retained so the planner can fail closed instead of silently dropping
    an invariant violation.
    """

    effective: dict[str, tuple[tuple[object, ...], dict[str, object]]] = {}
    invalid_rows: list[dict[str, object]] = []
    for raw_row in rows:
        row = dict(raw_row)
        transaction_id = row.get("transaction_id")
        if transaction_id is None or not str(transaction_id).strip():
            invalid_rows.append(row)
            continue
        transaction_key = str(transaction_id)
        order = _transaction_observation_order(row)
        previous = effective.get(transaction_key)
        if previous is None or order >= previous[0]:
            effective[transaction_key] = (order, row)

    collapsed = invalid_rows + [row for _, row in effective.values()]
    return sorted(collapsed, key=transaction_sort_key)


def transaction_boundary_state(rows: Iterable[dict[str, object]]) -> str:
    """Return the effective boundary gate for a transaction inventory."""

    return (
        "REJECTED"
        if any(
            str(row.get("status", "")) == "REJECTED"
            for row in collapse_transaction_history(rows)
        )
        else "READY"
    )


@dataclass
class TransactionCandidatePlan:
    sync_run_seq: int
    operation_type: str
    is_noop: bool
    status: str
    status_reason: str
    previous_transaction_id: str | None
    previous_transaction_end_offset: int | None
    target_transaction_id: str | None
    target_transaction_end_offset: int | None
    source_snapshot_completed: bool
    target_offsets: dict[str, int]
    iceberg_snapshot_ids: dict[str, int]
    expected_event_count: int
    expected_entity_counts: dict[str, int]


class ServingBoundaryPlanner:
    @staticmethod
    def plan_next_sync_run(
        sync_run_seq: int,
        runtime_state: dict[str, object],
        transaction_rows: list[dict[str, object]],
        iceberg_snapshots: dict[str, int],
        coverage_state: str = "READY",
        boundary_state: str = "READY",
        entity_metrics: dict[str, dict[str, object]] | None = None,
    ) -> TransactionCandidatePlan:
        transaction_rows = collapse_transaction_history(transaction_rows)
        prev_tx_id_raw = runtime_state.get("last_published_transaction_id")
        prev_tx_id = str(prev_tx_id_raw) if prev_tx_id_raw is not None else None

        prev_offset_raw = runtime_state.get("last_published_transaction_end_offset")
        prev_offset = (
            int(prev_offset_raw)
            if isinstance(prev_offset_raw, (int, str, float))
            else None
        )

        snapshot_done = bool(runtime_state.get("source_snapshot_completed", False))

        metric_entity_counts = {
            spec.entity: _as_int(
                entity_metrics.get(spec.entity, {}).get("event_count", 0)
                if entity_metrics is not None
                else 0
            )
            for spec in ALL_SERVING_ENTITIES
        }
        metric_offsets: dict[str, int] = {}
        if entity_metrics is not None:
            for metrics in entity_metrics.values():
                offsets = metrics.get("target_offsets", {})
                if isinstance(offsets, dict):
                    for key, value in offsets.items():
                        if isinstance(value, (int, float, str)):
                            metric_offsets[str(key)] = int(value)

        if coverage_state != "READY":
            return TransactionCandidatePlan(
                sync_run_seq=sync_run_seq,
                operation_type="SYNC",
                is_noop=True,
                status="WAITING",
                status_reason="SOURCE_NOT_CAUGHT_UP",
                previous_transaction_id=prev_tx_id,
                previous_transaction_end_offset=prev_offset,
                target_transaction_id=prev_tx_id,
                target_transaction_end_offset=prev_offset,
                source_snapshot_completed=snapshot_done,
                target_offsets={},
                iceberg_snapshot_ids=iceberg_snapshots,
                expected_event_count=0,
                expected_entity_counts={
                    spec.entity: 0 for spec in ALL_SERVING_ENTITIES
                },
            )

        if boundary_state == "REJECTED":
            return TransactionCandidatePlan(
                sync_run_seq=sync_run_seq,
                operation_type="SYNC",
                is_noop=True,
                status="BLOCKED",
                status_reason="REJECTED_TRANSACTION",
                previous_transaction_id=prev_tx_id,
                previous_transaction_end_offset=prev_offset,
                target_transaction_id=prev_tx_id,
                target_transaction_end_offset=prev_offset,
                source_snapshot_completed=snapshot_done,
                target_offsets={},
                iceberg_snapshot_ids=iceberg_snapshots,
                expected_event_count=0,
                expected_entity_counts={
                    spec.entity: 0 for spec in ALL_SERVING_ENTITIES
                },
            )

        # Select complete transaction prefix
        complete_txs: list[dict[str, object]] = []
        target_tx_id = prev_tx_id
        target_offset = prev_offset
        total_events = 0
        entity_counts = {spec.entity: 0 for spec in ALL_SERVING_ENTITIES}
        open_transaction: dict[str, object] | None = None

        for tx in transaction_rows:
            tx_status = str(tx.get("status", ""))
            if tx_status == "REJECTED":
                return TransactionCandidatePlan(
                    sync_run_seq=sync_run_seq,
                    operation_type="SYNC",
                    is_noop=True,
                    status="BLOCKED",
                    status_reason="REJECTED_TRANSACTION",
                    previous_transaction_id=prev_tx_id,
                    previous_transaction_end_offset=prev_offset,
                    target_transaction_id=prev_tx_id,
                    target_transaction_end_offset=prev_offset,
                    source_snapshot_completed=snapshot_done,
                    target_offsets={},
                    iceberg_snapshot_ids=iceberg_snapshots,
                    expected_event_count=0,
                    expected_entity_counts=entity_counts,
                )
            elif tx_status == "OPEN":
                # Stop prefix at OPEN transaction
                open_transaction = tx
                break
            elif tx_status == "COMPLETE":
                tx_id_raw = tx.get("transaction_id")
                offset_raw = tx.get("end_kafka_offset")
                tx_end_offset = (
                    int(offset_raw)
                    if isinstance(offset_raw, (int, str, float))
                    else None
                )
                # A COMPLETE row without both boundary coordinates cannot be
                # published safely.  Previously this fell through to a
                # MATERIALIZING plan with a NULL target and zero expected
                # counts, which allowed dbt to run against an unbounded
                # candidate partition and obscured the real metadata failure.
                if (
                    not isinstance(tx_id_raw, str)
                    or not tx_id_raw.strip()
                    or tx_end_offset is None
                ):
                    return TransactionCandidatePlan(
                        sync_run_seq=sync_run_seq,
                        operation_type="SYNC",
                        is_noop=True,
                        status="BLOCKED",
                        status_reason="INVARIANT_FAILURE",
                        previous_transaction_id=prev_tx_id,
                        previous_transaction_end_offset=prev_offset,
                        target_transaction_id=prev_tx_id,
                        target_transaction_end_offset=prev_offset,
                        source_snapshot_completed=snapshot_done,
                        target_offsets={},
                        iceberg_snapshot_ids=iceberg_snapshots,
                        expected_event_count=0,
                        expected_entity_counts=entity_counts,
                    )
                if prev_offset is not None and tx_end_offset <= prev_offset:
                    continue
                cnt_raw = tx.get("event_count")
                tx_event_count = (
                    int(cnt_raw) if isinstance(cnt_raw, (int, str, float)) else 0
                )
                # Debezium may emit COMPLETE metadata transactions with no
                # business events (for example heartbeat/empty transactions).
                # They advance the Kafka metadata offset but must not advance
                # the serving publication boundary or turn a repeat into a
                # false non-NOOP.
                if tx_event_count <= 0:
                    continue
                complete_txs.append(tx)
                target_tx_id = tx_id_raw
                target_offset = tx_end_offset
                total_events += tx_event_count
            else:
                return TransactionCandidatePlan(
                    sync_run_seq=sync_run_seq,
                    operation_type="SYNC",
                    is_noop=True,
                    status="BLOCKED",
                    status_reason="INVARIANT_FAILURE",
                    previous_transaction_id=prev_tx_id,
                    previous_transaction_end_offset=prev_offset,
                    target_transaction_id=prev_tx_id,
                    target_transaction_end_offset=prev_offset,
                    source_snapshot_completed=snapshot_done,
                    target_offsets={},
                    iceberg_snapshot_ids=iceberg_snapshots,
                    expected_event_count=0,
                    expected_entity_counts=entity_counts,
                )

        if not complete_txs and open_transaction is not None:
            return TransactionCandidatePlan(
                sync_run_seq=sync_run_seq,
                operation_type="SYNC",
                is_noop=True,
                status="WAITING",
                status_reason="OPEN_TRANSACTION",
                previous_transaction_id=prev_tx_id,
                previous_transaction_end_offset=prev_offset,
                target_transaction_id=prev_tx_id,
                target_transaction_end_offset=prev_offset,
                source_snapshot_completed=snapshot_done,
                target_offsets={},
                iceberg_snapshot_ids=iceberg_snapshots,
                expected_event_count=0,
                expected_entity_counts=entity_counts,
            )

        if not complete_txs and snapshot_done:
            return TransactionCandidatePlan(
                sync_run_seq=sync_run_seq,
                operation_type="SYNC",
                is_noop=True,
                status="NOOP",
                status_reason="NO_NEW_TRANSACTION",
                previous_transaction_id=prev_tx_id,
                previous_transaction_end_offset=prev_offset,
                target_transaction_id=prev_tx_id,
                target_transaction_end_offset=prev_offset,
                source_snapshot_completed=snapshot_done,
                target_offsets={},
                iceberg_snapshot_ids=iceberg_snapshots,
                expected_event_count=0,
                expected_entity_counts=entity_counts,
            )

        # The first publication may contain only the completed initial
        # snapshot.  Snapshot rows intentionally have no transaction ID or
        # transaction-topic end offset; the per-entity Kafka offsets supplied
        # by ``entity_metrics`` are the publication boundary in that case.
        # Once the snapshot has already been published, a non-NOOP plan must
        # always have a real complete transaction boundary.
        initial_snapshot_only = (
            not snapshot_done and not complete_txs and open_transaction is None
        )
        if (
            target_tx_id is None or target_offset is None
        ) and not initial_snapshot_only:
            return TransactionCandidatePlan(
                sync_run_seq=sync_run_seq,
                operation_type="SYNC",
                is_noop=True,
                status="BLOCKED",
                status_reason="INVARIANT_FAILURE",
                previous_transaction_id=prev_tx_id,
                previous_transaction_end_offset=prev_offset,
                target_transaction_id=prev_tx_id,
                target_transaction_end_offset=prev_offset,
                source_snapshot_completed=snapshot_done,
                target_offsets={},
                iceberg_snapshot_ids=iceberg_snapshots,
                expected_event_count=0,
                expected_entity_counts=entity_counts,
            )

        if entity_metrics is not None:
            target_offsets = metric_offsets
            expected_entity_counts = metric_entity_counts
            expected_event_count = sum(metric_entity_counts.values())
            expected_topics = {
                f"olist_cdc.olist_oltp.{spec.entity}:0" for spec in ALL_SERVING_ENTITIES
            }
            missing_topics = sorted(expected_topics - set(target_offsets))
            if missing_topics:
                return TransactionCandidatePlan(
                    sync_run_seq=sync_run_seq,
                    operation_type="SYNC",
                    is_noop=True,
                    status="BLOCKED",
                    status_reason="INVARIANT_FAILURE",
                    previous_transaction_id=prev_tx_id,
                    previous_transaction_end_offset=prev_offset,
                    target_transaction_id=target_tx_id,
                    target_transaction_end_offset=target_offset,
                    source_snapshot_completed=snapshot_done,
                    target_offsets={},
                    iceberg_snapshot_ids=iceberg_snapshots,
                    expected_event_count=0,
                    expected_entity_counts=entity_counts,
                )
        else:
            target_offsets = {}
            target_offsets["transaction"] = target_offset
            expected_entity_counts = entity_counts
            expected_event_count = total_events

        return TransactionCandidatePlan(
            sync_run_seq=sync_run_seq,
            operation_type="SYNC",
            is_noop=False,
            status="MATERIALIZING",
            status_reason="NONE",
            previous_transaction_id=prev_tx_id,
            previous_transaction_end_offset=prev_offset,
            target_transaction_id=target_tx_id,
            target_transaction_end_offset=target_offset,
            source_snapshot_completed=True,
            target_offsets=target_offsets,
            iceberg_snapshot_ids=iceberg_snapshots,
            expected_event_count=expected_event_count,
            expected_entity_counts=expected_entity_counts,
        )
