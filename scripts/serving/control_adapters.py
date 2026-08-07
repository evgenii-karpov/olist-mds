"""Target-scoped persistence adapters for the serving-control domain."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scripts.serving.control import ServingControlRepository
from scripts.serving.domain import ServingTarget, TargetMismatchError
from scripts.serving.models import OperationType, StatusReason, SyncStatus


def _assert_row_target(row: dict[str, object], target: ServingTarget) -> None:
    raw_target = row.get("target")
    if raw_target is not None and str(raw_target) != target.value:
        raise TargetMismatchError(
            f"row target {raw_target!r} cannot be used by {target.value!r} adapter"
        )


@dataclass(frozen=True, slots=True)
class PostgresServingControlAdapter:
    """Local adapter; all state is persisted in the PostgreSQL control DB."""

    repository: Any = ServingControlRepository
    target: ServingTarget = ServingTarget.LOCAL

    def __post_init__(self) -> None:
        if self.target is not ServingTarget.LOCAL:
            raise TargetMismatchError(
                "PostgresServingControlAdapter is reserved for the local target"
            )

    def allocate_sync_run(
        self,
        operation_type: OperationType,
        current_airflow_dag_run_id: str | None = None,
    ) -> dict[str, object]:
        row = dict(
            self.repository.allocate_sync_run(
                operation_type,
                current_airflow_dag_run_id,
            )
        )
        row.setdefault("target", self.target.value)
        _assert_row_target(row, self.target)
        return row

    def update_status(
        self,
        *,
        sync_run_seq: int,
        expected_status: SyncStatus | list[SyncStatus],
        new_status: SyncStatus,
        expected_active_sync_run_seq: int | None = None,
        status_reason: StatusReason = StatusReason.NONE,
        **fields: object,
    ) -> bool:
        """Forward a target-checked transition to the PostgreSQL repository."""

        return bool(
            self.repository.update_status(
                sync_run_seq=sync_run_seq,
                expected_status=expected_status,
                new_status=new_status,
                status_reason=status_reason,
                expected_active_sync_run_seq=expected_active_sync_run_seq,
                **fields,
            )
        )

    def prepare_same_run_retry(
        self,
        *,
        sync_run_seq: int,
        expected_active_sync_run_seq: int,
    ) -> bool:
        """Reset local candidate results without allocating a new sequence."""

        return bool(
            self.repository.prepare_same_run_retry(
                sync_run_seq,
                expected_active_sync_run_seq,
            )
        )

    def get_runtime_state(self) -> dict[str, object]:
        row = dict(self.repository.get_runtime_state())
        row.setdefault("target", self.target.value)
        _assert_row_target(row, self.target)
        return row
