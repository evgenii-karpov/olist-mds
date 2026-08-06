"""Fail-closed CDC ordering contract shared by serving and cloud tooling.

The source coordinates are stronger than timestamps or transport offsets.  A
caller must validate an event before using :func:`canonical_order_key`; there
is intentionally no timestamp-only fallback for live CDC records.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum

from scripts.serving.time import normalize_source_timestamp

CANONICAL_ORDER_FIELDS = (
    "is_non_snapshot",
    "source_binlog_file_index",
    "source_binlog_pos",
    "source_row",
    "transaction_total_order",
    "transaction_data_collection_order",
    "source_ts",
    "kafka_partition",
    "kafka_offset",
    "event_id",
)

_BINLOG_FILENAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*\.(?P<index>[0-9]+)$")
_INTEGER = re.compile(r"^[0-9]+$")


class OrderingContractError(ValueError):
    """Raised when a CDC record cannot be ordered deterministically."""

    def __init__(self, code: str, message: str, *, event_id: str | None = None) -> None:
        self.code = code
        self.event_id = event_id
        suffix = f" (event_id={event_id})" if event_id else ""
        super().__init__(f"{code}: {message}{suffix}")


class EventCategory(StrEnum):
    """CDC event category with an explicit required-field contract."""

    SNAPSHOT = "SNAPSHOT"
    LIVE_NON_TRANSACTIONAL = "LIVE_NON_TRANSACTIONAL"
    LIVE_TRANSACTIONAL = "LIVE_TRANSACTIONAL"


@dataclass(frozen=True, slots=True)
class ValidatedOrderingEvent:
    """Validated source coordinates used to construct the canonical tuple."""

    event_id: str
    category: EventCategory
    source_binlog_file_index: int | None
    source_binlog_pos: int | None
    source_row: int | None
    transaction_total_order: int | None
    transaction_data_collection_order: int | None
    source_ts_micros: int | None
    kafka_partition: int
    kafka_offset: int

    @property
    def is_non_snapshot(self) -> int:
        return int(self.category is not EventCategory.SNAPSHOT)

    def order_key(self) -> tuple[int, int, int, int, int, int, int, int, int, str]:
        """Return the one canonical ascending order tuple.

        Null fields are represented by ``-1`` only in categories where the
        contract explicitly allows them.  Invalid live rows are rejected
        before this method can be used.
        """

        return (
            self.is_non_snapshot,
            self.source_binlog_file_index
            if self.source_binlog_file_index is not None
            else -1,
            self.source_binlog_pos if self.source_binlog_pos is not None else -1,
            self.source_row if self.source_row is not None else -1,
            self.transaction_total_order
            if self.transaction_total_order is not None
            else -1,
            self.transaction_data_collection_order
            if self.transaction_data_collection_order is not None
            else -1,
            self.source_ts_micros if self.source_ts_micros is not None else -1,
            self.kafka_partition,
            self.kafka_offset,
            self.event_id,
        )

    @property
    def source_coordinate_key(self) -> tuple[object, ...]:
        """Return the coordinate identity used to detect conflicting duplicates."""

        if self.category is EventCategory.SNAPSHOT:
            return (self.category, self.kafka_partition, self.kafka_offset)
        return (
            self.category,
            self.source_binlog_file_index,
            self.source_binlog_pos,
            self.source_row,
            self.transaction_total_order,
            self.transaction_data_collection_order,
        )


def parse_binlog_file_index(filename: object) -> int:
    """Parse a MySQL binlog filename such as ``mysql-bin.000123``.

    Paths, missing numeric suffixes, negative values, and non-string values are
    rejected.  The parser is deliberately independent of the current MySQL
    server naming convention beyond the mandatory numeric suffix.
    """

    if not isinstance(filename, str) or not filename.strip():
        raise OrderingContractError(
            "MISSING_BINLOG_FILENAME", "live CDC requires source_binlog_file"
        )
    value = filename.strip()
    if "/" in value or "\\" in value:
        raise OrderingContractError(
            "MALFORMED_BINLOG_FILENAME", "source_binlog_file must not be a path"
        )
    match = _BINLOG_FILENAME.fullmatch(value)
    if match is None:
        raise OrderingContractError(
            "MALFORMED_BINLOG_FILENAME",
            "source_binlog_file must end with a numeric binlog index",
        )
    return int(match.group("index"))


def _required_text(row: Mapping[str, object], name: str, event_id: str | None) -> str:
    value = row.get(name)
    if not isinstance(value, str) or not value.strip():
        raise OrderingContractError(
            f"MISSING_{name.upper()}", f"{name} is required", event_id=event_id
        )
    return value.strip()


def _optional_non_negative_int(
    row: Mapping[str, object], name: str, *, event_id: str | None
) -> int | None:
    value = row.get(name)
    if value is None:
        return None
    if isinstance(value, bool):
        raise OrderingContractError(
            f"MALFORMED_{name.upper()}",
            f"{name} must be a non-negative integer",
            event_id=event_id,
        )
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str) and _INTEGER.fullmatch(value.strip()):
        parsed = int(value.strip())
    else:
        raise OrderingContractError(
            f"MALFORMED_{name.upper()}",
            f"{name} must be a non-negative integer",
            event_id=event_id,
        )
    if parsed < 0:
        raise OrderingContractError(
            f"MALFORMED_{name.upper()}",
            f"{name} must be non-negative",
            event_id=event_id,
        )
    return parsed


def _is_snapshot(row: Mapping[str, object]) -> bool:
    value = row.get("is_snapshot", row.get("snapshot"))
    if isinstance(value, bool):
        return value
    return isinstance(value, str) and value.strip().lower() in {"true", "last"}


def _source_ts_micros(value: object, *, event_id: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise OrderingContractError(
            "MALFORMED_SOURCE_TS",
            "source_ts must be a timestamp or epoch value",
            event_id=event_id,
        )
    if isinstance(value, int):
        # Debezium ts_ms is the only numeric source timestamp in the contract.
        return value * 1000
    if isinstance(value, float) and value.is_integer():
        return int(value) * 1000
    if isinstance(value, (datetime, date, str)):
        try:
            normalized = normalize_source_timestamp(value)
        except (TypeError, ValueError) as exc:
            raise OrderingContractError(
                "MALFORMED_SOURCE_TS",
                "source_ts is not a valid timestamp",
                event_id=event_id,
            ) from exc
        return int(normalized.timestamp() * 1_000_000)
    raise OrderingContractError(
        "MALFORMED_SOURCE_TS", "source_ts is not a valid timestamp", event_id=event_id
    )


def validate_ordering_event(row: Mapping[str, object]) -> ValidatedOrderingEvent:
    """Validate one event according to its explicit CDC category."""

    event_id = _required_text(row, "event_id", None)
    partition = _optional_non_negative_int(row, "kafka_partition", event_id=event_id)
    offset = _optional_non_negative_int(row, "kafka_offset", event_id=event_id)
    if partition is None or offset is None:
        raise OrderingContractError(
            "MISSING_KAFKA_COORDINATE",
            "kafka_partition and kafka_offset are required",
            event_id=event_id,
        )
    _required_text(row, "topic", event_id)

    snapshot = _is_snapshot(row)
    transaction_id = row.get("transaction_id")
    transaction_total = _optional_non_negative_int(
        row, "transaction_total_order", event_id=event_id
    )
    transaction_collection = _optional_non_negative_int(
        row, "transaction_data_collection_order", event_id=event_id
    )
    transaction_present = any(
        value is not None
        for value in (transaction_id, transaction_total, transaction_collection)
    )

    if snapshot:
        if transaction_present:
            raise OrderingContractError(
                "SNAPSHOT_HAS_TRANSACTION_METADATA",
                "snapshot events cannot carry transaction ordering fields",
                event_id=event_id,
            )
        category = EventCategory.SNAPSHOT
        source_file_index = source_pos = source_row = None
    else:
        source_file = _required_text(row, "source_binlog_file", event_id)
        parsed_file_index = parse_binlog_file_index(source_file)
        supplied_file_index = _optional_non_negative_int(
            row, "source_binlog_file_index", event_id=event_id
        )
        if supplied_file_index is not None and supplied_file_index != parsed_file_index:
            raise OrderingContractError(
                "BINLOG_INDEX_MISMATCH",
                "source_binlog_file_index does not match source_binlog_file",
                event_id=event_id,
            )
        source_file_index = parsed_file_index
        source_pos = _optional_non_negative_int(
            row, "source_binlog_pos", event_id=event_id
        )
        source_row = _optional_non_negative_int(row, "source_row", event_id=event_id)
        if source_pos is None or source_row is None:
            raise OrderingContractError(
                "MISSING_BINLOG_COORDINATE",
                "live CDC requires source_binlog_pos and source_row",
                event_id=event_id,
            )
        if transaction_present:
            if (
                not isinstance(transaction_id, str)
                or not transaction_id.strip()
                or transaction_total is None
                or transaction_collection is None
            ):
                raise OrderingContractError(
                    "INCOMPLETE_TRANSACTION_METADATA",
                    "transaction id, total order, and collection order are all required",
                    event_id=event_id,
                )
            category = EventCategory.LIVE_TRANSACTIONAL
        else:
            category = EventCategory.LIVE_NON_TRANSACTIONAL

    return ValidatedOrderingEvent(
        event_id=event_id,
        category=category,
        source_binlog_file_index=source_file_index,
        source_binlog_pos=source_pos,
        source_row=source_row,
        transaction_total_order=transaction_total,
        transaction_data_collection_order=transaction_collection,
        source_ts_micros=_source_ts_micros(row.get("source_ts"), event_id=event_id),
        kafka_partition=partition,
        kafka_offset=offset,
    )


def canonical_order_key(
    row: Mapping[str, object],
) -> tuple[int, int, int, int, int, int, int, int, int, str]:
    """Validate and return the canonical source-version tuple."""

    return validate_ordering_event(row).order_key()


def validate_ordering_batch(
    rows: Iterable[Mapping[str, object]],
) -> tuple[ValidatedOrderingEvent, ...]:
    """Validate a batch and reject conflicting duplicate source coordinates."""

    validated: list[ValidatedOrderingEvent] = []
    coordinates: dict[tuple[object, ...], str] = {}
    for row in rows:
        event = validate_ordering_event(row)
        previous_event_id = coordinates.get(event.source_coordinate_key)
        if previous_event_id is not None and previous_event_id != event.event_id:
            raise OrderingContractError(
                "CONFLICTING_SOURCE_COORDINATE",
                f"source coordinates are shared by {previous_event_id} and {event.event_id}",
                event_id=event.event_id,
            )
        coordinates[event.source_coordinate_key] = event.event_id
        validated.append(event)
    return tuple(sorted(validated, key=ValidatedOrderingEvent.order_key))


def canonical_order_sql(alias: str = "") -> str:
    """Return a dialect-neutral tuple expression for contract documentation.

    Concrete ClickHouse and BigQuery adapters may wrap the fields in their
    native tuple/STRUCT syntax, but must preserve this field order.
    """

    prefix = f"{alias}." if alias else ""
    return "(" + ", ".join(f"{prefix}{field}" for field in CANONICAL_ORDER_FIELDS) + ")"
