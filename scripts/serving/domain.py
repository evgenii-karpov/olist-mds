"""Provider-independent serving-control contracts and state transitions.

The local PostgreSQL and GCP BigQuery implementations persist these same
contracts in different physical stores.  The in-memory ledger in this module
is deliberately small: it is a deterministic reference implementation used
to exercise target isolation, predecessor checks, and same-run retries
without credentials or a warehouse connection.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from enum import StrEnum

from scripts.serving.models import (
    EntitySyncStatus,
    OperationType,
    StatusReason,
    SyncStatus,
)


class ServingTarget(StrEnum):
    """A physically isolated serving-control target."""

    LOCAL = "local"
    GCP = "gcp"


class ControlContractError(RuntimeError):
    """Base error for a violated provider-independent control contract."""


class TargetMismatchError(ControlContractError):
    """Raised when a run or boundary is used by another target."""


class PredecessorConflictError(ControlContractError):
    """Raised when an operation was planned against a stale active sequence."""


class RetryContractError(ControlContractError):
    """Raised when a run cannot be retried with the same sequence."""


RETRYABLE_RUN_STATUSES = frozenset(
    {
        SyncStatus.FAILED_RETRYABLE,
        SyncStatus.MATERIALIZING,
        SyncStatus.VALIDATING,
        SyncStatus.READY_TO_PUBLISH,
    }
)


@dataclass(frozen=True, slots=True)
class ServingBoundary:
    """Frozen source interval used by one serving run."""

    target: ServingTarget
    sync_run_seq: int
    previous_transaction_id: str | None = None
    previous_transaction_end_offset: int | None = None
    target_transaction_id: str | None = None
    target_transaction_end_offset: int | None = None
    target_offsets: Mapping[str, int] = field(default_factory=dict)
    source_snapshot_completed: bool = False

    def __post_init__(self) -> None:
        if self.sync_run_seq < 1:
            raise ValueError("sync_run_seq must be positive")
        if (
            self.previous_transaction_end_offset is not None
            and self.previous_transaction_end_offset < 0
        ):
            raise ValueError("previous transaction offset must be non-negative")
        if (
            self.target_transaction_end_offset is not None
            and self.target_transaction_end_offset < 0
        ):
            raise ValueError("target transaction offset must be non-negative")
        if (
            self.target_transaction_id is None
            and self.target_transaction_end_offset is not None
        ):
            raise ValueError("target transaction offset requires a transaction ID")
        if (
            self.target_transaction_id is not None
            and self.target_transaction_end_offset is None
        ):
            raise ValueError("target transaction ID requires an end offset")
        normalized_offsets = dict(self.target_offsets)
        if any(offset < 0 for offset in normalized_offsets.values()):
            raise ValueError("target offsets must be non-negative")
        object.__setattr__(self, "target_offsets", normalized_offsets)


@dataclass(frozen=True, slots=True)
class ServingRun:
    """Provider-neutral serving-run identity and control metadata."""

    target: ServingTarget
    sync_run_seq: int
    sync_run_id: str
    operation_type: OperationType
    status: SyncStatus = SyncStatus.PLANNING
    status_reason: StatusReason = StatusReason.NONE
    expected_active_sync_run_seq: int = 0
    attempt_count: int = 1
    is_noop: bool = False
    boundary: ServingBoundary | None = None

    def __post_init__(self) -> None:
        if self.sync_run_seq < 1:
            raise ValueError("sync_run_seq must be positive")
        if not self.sync_run_id:
            raise ValueError("sync_run_id must not be empty")
        if self.expected_active_sync_run_seq < 0:
            raise ValueError("expected_active_sync_run_seq must be non-negative")
        if self.attempt_count < 1:
            raise ValueError("attempt_count must be positive")
        if self.boundary is not None and self.boundary.target is not self.target:
            raise TargetMismatchError(
                f"run target {self.target.value!r} does not match boundary "
                f"target {self.boundary.target.value!r}"
            )
        if (
            self.boundary is not None
            and self.boundary.sync_run_seq != self.sync_run_seq
        ):
            raise ValueError("boundary and run sequence must match")


@dataclass(frozen=True, slots=True)
class ServingResult:
    """Provider-neutral entity/model result record."""

    target: ServingTarget
    sync_run_seq: int
    name: str
    status: EntitySyncStatus
    expected_count: int = 0
    materialized_count: int = 0
    affected_key_count: int = 0
    checksum: str | None = None
    error_code: str | None = None

    def __post_init__(self) -> None:
        if self.sync_run_seq < 1:
            raise ValueError("sync_run_seq must be positive")
        if not self.name:
            raise ValueError("result name must not be empty")
        if (
            min(
                self.expected_count,
                self.materialized_count,
                self.affected_key_count,
            )
            < 0
        ):
            raise ValueError("result counts must be non-negative")


@dataclass
class TargetControlLedger:
    """Deterministic reference ledger with one sequence per target instance."""

    target: ServingTarget
    next_sync_run_seq: int = 1
    active_sync_run_seq: int = 0
    runs: dict[int, ServingRun] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.next_sync_run_seq < 1:
            raise ValueError("next_sync_run_seq must be positive")
        if self.active_sync_run_seq < 0:
            raise ValueError("active_sync_run_seq must be non-negative")

    def _assert_target(self, target: ServingTarget) -> None:
        if target is not self.target:
            raise TargetMismatchError(
                f"ledger target {self.target.value!r} cannot mutate "
                f"{target.value!r} state"
            )

    def _assert_predecessor(self, expected_active_sync_run_seq: int) -> None:
        if expected_active_sync_run_seq != self.active_sync_run_seq:
            raise PredecessorConflictError(
                "expected active sequence does not match target state: "
                f"expected {expected_active_sync_run_seq}, "
                f"actual {self.active_sync_run_seq}"
            )

    def allocate_sync_run(
        self,
        operation_type: OperationType,
        *,
        expected_active_sync_run_seq: int | None = None,
        boundary: ServingBoundary | None = None,
    ) -> ServingRun:
        if expected_active_sync_run_seq is not None:
            self._assert_predecessor(expected_active_sync_run_seq)
        if boundary is not None:
            self._assert_target(boundary.target)
        seq = self.next_sync_run_seq
        run = ServingRun(
            target=self.target,
            sync_run_seq=seq,
            sync_run_id=f"{self.target.value}-sync-{seq:020d}",
            operation_type=operation_type,
            expected_active_sync_run_seq=self.active_sync_run_seq,
            boundary=boundary,
        )
        self.next_sync_run_seq += 1
        self.runs[seq] = run
        return run

    def set_status(
        self,
        sync_run_seq: int,
        *,
        expected_status: SyncStatus | frozenset[SyncStatus],
        new_status: SyncStatus,
        expected_active_sync_run_seq: int | None = None,
        status_reason: StatusReason = StatusReason.NONE,
    ) -> ServingRun:
        run = self.runs[sync_run_seq]
        if run.target is not self.target:
            raise TargetMismatchError("run belongs to another target")
        accepted = (
            {expected_status}
            if isinstance(expected_status, SyncStatus)
            else set(expected_status)
        )
        if run.status not in accepted:
            raise ControlContractError(
                f"run {sync_run_seq} is {run.status.value}, expected "
                f"one of {sorted(status.value for status in accepted)}"
            )
        if expected_active_sync_run_seq is not None:
            self._assert_predecessor(expected_active_sync_run_seq)
        updated = replace(run, status=new_status, status_reason=status_reason)
        self.runs[sync_run_seq] = updated
        return updated

    def retry_same_run(
        self,
        sync_run_seq: int,
        *,
        expected_active_sync_run_seq: int,
    ) -> ServingRun:
        self._assert_predecessor(expected_active_sync_run_seq)
        run = self.runs[sync_run_seq]
        if run.target is not self.target:
            raise TargetMismatchError("run belongs to another target")
        if run.expected_active_sync_run_seq != expected_active_sync_run_seq:
            raise PredecessorConflictError(
                "run predecessor does not match the requested retry predecessor"
            )
        if run.status not in RETRYABLE_RUN_STATUSES:
            raise RetryContractError(
                f"run {sync_run_seq} in {run.status.value} cannot be retried"
            )
        updated = replace(
            run,
            status=SyncStatus.PLANNING,
            status_reason=StatusReason.NONE,
            attempt_count=run.attempt_count + 1,
        )
        self.runs[sync_run_seq] = updated
        return updated

    def advance_active_sync_run(
        self,
        sync_run_seq: int,
        *,
        expected_active_sync_run_seq: int,
    ) -> ServingRun:
        self._assert_predecessor(expected_active_sync_run_seq)
        run = self.runs[sync_run_seq]
        if run.target is not self.target:
            raise TargetMismatchError("run belongs to another target")
        if run.status is not SyncStatus.READY_TO_PUBLISH:
            raise ControlContractError(
                "only READY_TO_PUBLISH runs may advance active state"
            )
        self.active_sync_run_seq = sync_run_seq
        updated = replace(run, status=SyncStatus.SUCCEEDED)
        self.runs[sync_run_seq] = updated
        return updated
