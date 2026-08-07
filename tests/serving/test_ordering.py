from __future__ import annotations

from datetime import UTC, datetime

import pytest
from scripts.serving.ordering import (
    EventCategory,
    OrderingContractError,
    canonical_order_key,
    parse_binlog_file_index,
    validate_ordering_batch,
    validate_ordering_event,
)
from scripts.serving.time import (
    DEFAULT_SOURCE_TIME_ZONE,
    configured_source_time_zone,
    normalize_source_timestamp,
)


def _event(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "event_id": "olist_cdc.olist_oltp.orders:0:10",
        "topic": "olist_cdc.olist_oltp.orders",
        "kafka_partition": 0,
        "kafka_offset": 10,
        "source_ts": "2026-08-07T12:00:00",
        "is_snapshot": False,
        "source_binlog_file": "mysql-bin.000007",
        "source_binlog_pos": 100,
        "source_row": 1,
    }
    value.update(overrides)
    return value


def test_binlog_filename_index_is_strict_and_numeric() -> None:
    assert parse_binlog_file_index("mysql-bin.000007") == 7
    assert parse_binlog_file_index("server-a.12") == 12

    for value in (None, "mysql-bin", "mysql-bin.abc", "C:\\mysql-bin.000001"):
        with pytest.raises(OrderingContractError):
            parse_binlog_file_index(value)


def test_snapshot_contract_does_not_require_live_coordinates() -> None:
    validated = validate_ordering_event(
        _event(
            event_id="snapshot-1",
            is_snapshot=True,
            source_binlog_file=None,
            source_binlog_pos=None,
            source_row=None,
        )
    )

    assert validated.category is EventCategory.SNAPSHOT
    assert validated.source_coordinate_key == (
        "olist_cdc.olist_oltp.orders",
        EventCategory.SNAPSHOT,
        0,
        10,
    )


def test_snapshot_coordinates_are_scoped_by_topic() -> None:
    first = _event(event_id="snapshot-orders", is_snapshot=True)
    second = _event(
        event_id="snapshot-customers",
        topic="olist_cdc.olist_oltp.customers",
        is_snapshot=True,
    )

    assert len(validate_ordering_batch((first, second))) == 2


def test_live_non_transactional_requires_validated_binlog_coordinates() -> None:
    with pytest.raises(OrderingContractError, match="MISSING_BINLOG_COORDINATE"):
        validate_ordering_event(_event(source_binlog_pos=None))

    with pytest.raises(OrderingContractError, match="MALFORMED_BINLOG_FILENAME"):
        validate_ordering_event(_event(source_binlog_file="mysql-bin"))

    validated = validate_ordering_event(_event())
    assert validated.category is EventCategory.LIVE_NON_TRANSACTIONAL
    assert validated.source_binlog_file_index == 7


def test_transactional_events_require_the_complete_transaction_tuple() -> None:
    with pytest.raises(OrderingContractError, match="INCOMPLETE_TRANSACTION_METADATA"):
        validate_ordering_event(_event(transaction_id="tx-1"))

    validated = validate_ordering_event(
        _event(
            transaction_id="tx-1",
            transaction_total_order=2,
            transaction_data_collection_order=1,
        )
    )
    assert validated.category is EventCategory.LIVE_TRANSACTIONAL
    assert validated.order_key()[4:6] == (2, 1)


def test_canonical_order_uses_source_coordinates_before_timestamp_and_transport() -> (
    None
):
    older_timestamp = _event(
        event_id="later-coordinate",
        source_binlog_file="mysql-bin.000008",
        source_binlog_pos=1,
        source_ts="2020-01-01T00:00:00",
        kafka_offset=1,
    )
    stronger_source_order = _event(
        event_id="earlier-coordinate",
        source_binlog_file="mysql-bin.000007",
        source_binlog_pos=999,
        source_ts="2030-01-01T00:00:00",
        kafka_offset=999,
    )

    assert canonical_order_key(stronger_source_order) < canonical_order_key(
        older_timestamp
    )


def test_conflicting_duplicate_source_coordinates_fail_closed() -> None:
    first = _event(event_id="event-a")
    second = _event(event_id="event-b", kafka_offset=11)
    with pytest.raises(OrderingContractError, match="CONFLICTING_SOURCE_COORDINATE"):
        validate_ordering_batch((first, second))


def test_source_wall_clock_is_normalized_to_utc(monkeypatch) -> None:
    monkeypatch.delenv("SOURCE_TIME_ZONE", raising=False)
    normalized = normalize_source_timestamp("2020-01-01T00:00:00")
    assert normalized == datetime(2020, 1, 1, 3, tzinfo=UTC)
    assert configured_source_time_zone({}) == DEFAULT_SOURCE_TIME_ZONE
    assert configured_source_time_zone({"SOURCE_TIME_ZONE": "UTC"}) == "UTC"

    with pytest.raises(ValueError, match="unknown SOURCE_TIME_ZONE"):
        configured_source_time_zone({"SOURCE_TIME_ZONE": "Not/AZone"})


def test_source_wall_clock_uses_the_environment_timezone(monkeypatch) -> None:
    monkeypatch.setenv("SOURCE_TIME_ZONE", "UTC")

    normalized = normalize_source_timestamp("2020-01-01T00:00:00")

    assert normalized == datetime(2020, 1, 1, tzinfo=UTC)


def test_source_timestamp_preserves_microsecond_precision(monkeypatch) -> None:
    monkeypatch.setenv("SOURCE_TIME_ZONE", "UTC")

    validated = validate_ordering_event(_event(source_ts="2020-01-01T00:00:00.000001"))

    assert validated.source_ts_micros == 1_577_836_800_000_001
