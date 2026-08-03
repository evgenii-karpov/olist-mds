"""Serving transaction boundary planner and caught-up target resolution."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from scripts.serving.entities import ALL_SERVING_ENTITIES

logger = logging.getLogger(__name__)


def _as_int(value: object, default: int = 0) -> int:
    return int(value) if isinstance(value, (int, float, str)) else default


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

        if target_tx_id is None or target_offset is None:
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
