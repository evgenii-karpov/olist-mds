"""Common normalization API frozen at the J1 join point.

This module contains interfaces and transport-level invariants only.  It does
not contain an entity schema, business transform, Spark query, or MERGE
implementation.  Wave 2 entity agents implement the protocols from their
owned entity paths and must not edit this module.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, Protocol, runtime_checkable

from .topology import ALL_CONTINUOUS_QUERIES, checkpoint_path

NORMALIZATION_API_VERSION = 1
EVENT_ID_FORMAT = "topic:partition:offset"
ORDERING_RULE = (
    "same business key stays in one Kafka partition; current accepts an event "
    "only when kafka offset is greater than the stored version"
)
DEDUPE_RULE = (
    "deduplicate by event_id within every micro-batch and append changes with "
    "insert-only MERGE semantics"
)
ENTITY_AGENT_GUARDRAIL = (
    "Wave 2 entity agents may implement only their entity contract/normalizer "
    "paths; common platform modules are integration-owned."
)


@dataclass(frozen=True)
class CanonicalEventMetadata:
    """Transport metadata retained for every non-internal Kafka record."""

    topic: str
    partition: int
    offset: int
    kafka_timestamp: datetime | None
    key_schema_id: int | None
    value_schema_id: int | None
    schema_fingerprint: str | None
    transaction_id: str | None = None
    transaction_total_order: int | None = None
    transaction_data_collection_order: int | None = None

    def __post_init__(self) -> None:
        if not self.topic:
            raise ValueError("topic is required")
        if self.partition < 0 or self.offset < 0:
            raise ValueError("Kafka partition and offset must be non-negative")

    @property
    def event_id(self) -> str:
        """The stable identity within one disposable lab generation."""

        return f"{self.topic}:{self.partition}:{self.offset}"


@dataclass(frozen=True)
class WriterSchemaFingerprint:
    """The captured writer identity supplied by the schema resolver boundary."""

    entity: str
    contract_version: int
    key_fingerprint_sha256: str
    value_fingerprint_sha256: str

    def __post_init__(self) -> None:
        if not self.entity:
            raise ValueError("entity is required")
        if self.contract_version < 1:
            raise ValueError("contract_version must be positive")
        for name, value in (
            ("key_fingerprint_sha256", self.key_fingerprint_sha256),
            ("value_fingerprint_sha256", self.value_fingerprint_sha256),
        ):
            if len(value) != 64 or any(
                character not in "0123456789abcdef" for character in value
            ):
                raise ValueError(f"{name} must be a lowercase SHA-256 fingerprint")


@dataclass(frozen=True)
class DebeziumEnvelope:
    """Decoded Debezium envelope before entity-specific normalization."""

    before: Mapping[str, Any] | None
    after: Mapping[str, Any] | None
    op: Literal["c", "r", "u", "d"]
    source: Mapping[str, Any]
    transaction: Mapping[str, Any] | None


@dataclass(frozen=True)
class NormalizationEvent:
    """Input presented to an entity normalizer."""

    metadata: CanonicalEventMetadata
    envelope: DebeziumEnvelope
    writer: WriterSchemaFingerprint

    @property
    def event_id(self) -> str:
        return self.metadata.event_id


@dataclass(frozen=True)
class NormalizedChange:
    """Entity-neutral result passed to changes/current/audit boundaries."""

    event: NormalizationEvent
    business_row: Mapping[str, Any] | None
    is_deleted: bool
    apply_status: Literal["applied", "rejected"]
    error_code: str | None = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        if self.apply_status == "applied" and self.error_code is not None:
            raise ValueError("applied change cannot have an error code")
        if self.apply_status == "rejected" and not self.error_code:
            raise ValueError("rejected change requires a stable error code")


@dataclass(frozen=True)
class NormalizationContext:
    """Stable query/checkpoint context shared by streaming and finite replay."""

    entity: str
    contract_version: int
    query_name: str
    checkpoint: str
    writer: WriterSchemaFingerprint

    @classmethod
    def for_entity(
        cls,
        entity: str,
        *,
        contract_version: int,
        writer: WriterSchemaFingerprint,
        checkpoint_root: str = "s3a://olist-checkpoints",
    ) -> NormalizationContext:
        query_name = f"normalize_{entity}"
        if query_name not in ALL_CONTINUOUS_QUERIES:
            raise ValueError(f"entity has no fixed topology query: {entity}")
        return cls(
            entity=entity,
            contract_version=contract_version,
            query_name=query_name,
            checkpoint=checkpoint_path(query_name, contract_version, checkpoint_root),
            writer=writer,
        )


@runtime_checkable
class SchemaResolver(Protocol):
    """Boundary for captured writer schema and reference resolution."""

    def resolve(self, schema_id: int) -> Mapping[str, Any]:
        """Return one self-contained writer schema or raise a fatal contract error."""

        ...


@runtime_checkable
class EntityNormalizer(Protocol):
    """Entity-owned pure transform; no streaming or storage side effects."""

    def normalize(
        self,
        event: NormalizationEvent,
        *,
        context: NormalizationContext,
    ) -> NormalizedChange:
        """Decode one validated event into the entity-neutral change result."""

        ...


@runtime_checkable
class ChangesAppender(Protocol):
    """Insert-only Silver changes boundary used by both streaming and replay."""

    def append_changes(
        self,
        changes: Iterable[NormalizedChange],
        *,
        context: NormalizationContext,
    ) -> None:
        """Append idempotently by event_id; never update an existing ledger row."""

        ...


@runtime_checkable
class CurrentMergeExecutor(Protocol):
    """Silver current-state MERGE boundary."""

    def merge_current(
        self,
        changes: Iterable[NormalizedChange],
        *,
        primary_key: Sequence[str],
        context: NormalizationContext,
    ) -> None:
        """Apply only the greatest Kafka offset for each business key."""

        ...


@runtime_checkable
class AuditErrorWriter(Protocol):
    """Boundary for progress, transaction, and redacted error writes."""

    def write_audit(
        self,
        changes: Iterable[NormalizedChange],
        *,
        context: NormalizationContext,
    ) -> None:
        """Write idempotent audit/error rows without raw payload bytes."""

        ...


def deduplicate_event_ids(
    events: Iterable[NormalizationEvent],
) -> tuple[NormalizationEvent, ...]:
    """Keep the first occurrence of each event_id in input order.

    A second occurrence is a retry duplicate.  Entity implementations must not
    use this helper to collapse different offsets or different business keys.
    """

    seen: set[str] = set()
    result: list[NormalizationEvent] = []
    for event in events:
        if event.event_id in seen:
            continue
        seen.add(event.event_id)
        result.append(event)
    return tuple(result)


def ensure_checkpoint_contract(
    context: NormalizationContext, *, expected_contract_version: int
) -> None:
    """Fail closed if a caller uses a query/checkpoint from another contract."""

    if context.contract_version != expected_contract_version:
        raise ValueError(
            "normalization context contract version does not match writer contract"
        )
    expected = checkpoint_path(
        context.query_name,
        expected_contract_version,
        "s3a://olist-checkpoints",
    )
    if context.checkpoint != expected:
        raise ValueError("normalization checkpoint does not match topology contract")
