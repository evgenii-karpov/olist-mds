"""Data models, enums, canonical JSON reports, and checksum helpers for serving."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from enum import StrEnum

JsonValue = dict[str, object] | list[object] | str | int | float | bool | None


class OperationType(StrEnum):
    SYNC = "SYNC"
    REBUILD = "REBUILD"


class SyncStatus(StrEnum):
    PLANNING = "PLANNING"
    WAITING = "WAITING"
    BLOCKED = "BLOCKED"
    MATERIALIZING = "MATERIALIZING"
    VALIDATING = "VALIDATING"
    READY_TO_PUBLISH = "READY_TO_PUBLISH"
    PUBLISHED_PENDING_FINALIZATION = "PUBLISHED_PENDING_FINALIZATION"
    SUCCEEDED = "SUCCEEDED"
    NOOP = "NOOP"
    FAILED_RETRYABLE = "FAILED_RETRYABLE"
    FAILED_TERMINAL = "FAILED_TERMINAL"


class StatusReason(StrEnum):
    NONE = "NONE"
    NO_NEW_TRANSACTION = "NO_NEW_TRANSACTION"
    SOURCE_NOT_CAUGHT_UP = "SOURCE_NOT_CAUGHT_UP"
    OPEN_TRANSACTION = "OPEN_TRANSACTION"
    OPEN_TRANSACTION_STALE = "OPEN_TRANSACTION_STALE"
    REJECTED_TRANSACTION = "REJECTED_TRANSACTION"
    SNAPSHOT_REJECTED = "SNAPSHOT_REJECTED"
    ACTIVE_LEASE = "ACTIVE_LEASE"
    MATERIALIZATION_MISMATCH = "MATERIALIZATION_MISMATCH"
    PUBLICATION_DRIFT = "PUBLICATION_DRIFT"
    INVARIANT_FAILURE = "INVARIANT_FAILURE"
    EXECUTION_FAILURE = "EXECUTION_FAILURE"


class EntitySyncStatus(StrEnum):
    PLANNED = "PLANNED"
    MATERIALIZED = "MATERIALIZED"
    VALIDATED = "VALIDATED"
    FAILED = "FAILED"


@dataclass
class EntityResult:
    sync_run_seq: int
    entity: str
    status: EntitySyncStatus
    expected_event_count: int = 0
    materialized_event_count: int = 0
    affected_key_count: int = 0
    candidate_current_count: int = 0
    event_checksum: str | None = None
    error_code: str | None = None


@dataclass
class ServingSyncReport:
    sync_run_seq: int
    sync_run_id: str
    operation_type: str
    status: str
    status_reason: str
    is_noop: bool
    previous_transaction_id: str | None
    target_transaction_id: str | None
    expected_event_count: int
    materialized_event_count: int
    entity_counts: dict[str, int]
    published_at: str
    dbt_result: dict[str, object] | None = None
    report_sha256: str = ""

    def compute_sha256(self) -> str:
        d = asdict(self)
        d.pop("report_sha256", None)
        canonical_bytes = canonical_json_bytes(d)
        return hashlib.sha256(canonical_bytes).hexdigest()

    def to_canonical_dict(self) -> dict[str, object]:
        d = asdict(self)
        d["report_sha256"] = self.compute_sha256()
        return d


def canonical_json_bytes(data: JsonValue) -> bytes:
    """Serialize object into canonical UTF-8 bytes: sorted keys, no whitespace separators."""
    raw = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return raw.encode("utf-8")


def compute_event_checksum(rows: list[tuple[str, str | None, str | None]]) -> str:
    """Compute event checksum: UTF-8 'event_id|row_hash|transaction_id', sorted, joined by \\n."""
    formatted = [
        f"{ev_id}|{row_hash or '<null>'}|{tx_id or '<snapshot>'}"
        for ev_id, row_hash, tx_id in rows
    ]
    formatted.sort()
    content = "\n".join(formatted).encode("utf-8")
    return hashlib.sha256(content).hexdigest()
