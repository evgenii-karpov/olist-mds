import pytest
from scripts.serving.domain import (
    PredecessorConflictError,
    ServingBoundary,
    ServingTarget,
    TargetControlLedger,
    TargetMismatchError,
)
from scripts.serving.models import OperationType, SyncStatus


def _boundary(target: ServingTarget, sync_run_seq: int) -> ServingBoundary:
    return ServingBoundary(
        target=target,
        sync_run_seq=sync_run_seq,
        previous_transaction_id="tx-previous",
        previous_transaction_end_offset=10,
        target_transaction_id="tx-target",
        target_transaction_end_offset=20,
        target_offsets={"topic:0": 20},
        source_snapshot_completed=True,
    )


def test_sequences_and_active_state_are_scoped_per_target() -> None:
    local = TargetControlLedger(ServingTarget.LOCAL)
    gcp = TargetControlLedger(ServingTarget.GCP)

    local_run = local.allocate_sync_run(OperationType.SYNC)
    gcp_run = gcp.allocate_sync_run(OperationType.SYNC)

    assert local_run.sync_run_seq == 1
    assert gcp_run.sync_run_seq == 1
    local.set_status(
        1,
        expected_status=SyncStatus.PLANNING,
        new_status=SyncStatus.READY_TO_PUBLISH,
    )
    local.advance_active_sync_run(1, expected_active_sync_run_seq=0)

    assert local.active_sync_run_seq == 1
    assert gcp.active_sync_run_seq == 0
    assert gcp.runs[gcp_run.sync_run_seq].status is SyncStatus.PLANNING


def test_cross_target_boundary_is_rejected_before_allocation() -> None:
    local = TargetControlLedger(ServingTarget.LOCAL)

    with pytest.raises(TargetMismatchError):
        local.allocate_sync_run(
            OperationType.SYNC,
            boundary=_boundary(ServingTarget.GCP, 1),
        )


def test_stale_predecessor_cannot_advance_target_state() -> None:
    ledger = TargetControlLedger(ServingTarget.GCP)
    ledger.allocate_sync_run(OperationType.SYNC)

    with pytest.raises(PredecessorConflictError):
        ledger.allocate_sync_run(
            OperationType.SYNC,
            expected_active_sync_run_seq=99,
        )


def test_same_run_retry_preserves_identity_boundary_and_predecessor() -> None:
    ledger = TargetControlLedger(ServingTarget.GCP)
    run = ledger.allocate_sync_run(
        OperationType.SYNC,
        boundary=_boundary(ServingTarget.GCP, 1),
    )
    ledger.set_status(
        run.sync_run_seq,
        expected_status=SyncStatus.PLANNING,
        new_status=SyncStatus.FAILED_RETRYABLE,
    )

    retried = ledger.retry_same_run(
        run.sync_run_seq,
        expected_active_sync_run_seq=0,
    )

    assert retried.sync_run_seq == run.sync_run_seq
    assert retried.sync_run_id == run.sync_run_id
    assert retried.boundary == run.boundary
    assert retried.expected_active_sync_run_seq == 0
    assert retried.attempt_count == 2
    assert retried.status is SyncStatus.PLANNING
