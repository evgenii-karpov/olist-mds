"""Bounded live assertions for Stage 2 snapshot, CRUD, Avro, and ordering."""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import psycopg2
from confluent_kafka import Consumer, KafkaError, KafkaException, TopicPartition

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.cdc.avro_wire import ApicurioAvroDecoder

TOPICS = {
    "customers": (1, ("customer_id",)),
    "orders": (3, ("order_id",)),
    "order_items": (3, ("order_id", "order_item_id")),
    "order_payments": (3, ("order_id", "payment_sequential")),
    "order_reviews": (3, ("review_id", "order_id")),
    "products": (1, ("product_id",)),
    "sellers": (1, ("seller_id",)),
    "product_category_translation": (1, ("product_category_name",)),
}
EXPECTED_SNAPSHOT = {
    "customers": 8,
    "orders": 12,
    "order_items": 16,
    "order_payments": 14,
    "order_reviews": 12,
    "products": 8,
    "sellers": 4,
    "product_category_translation": 5,
}


@dataclass(frozen=True)
class DecodedRecord:
    topic: str
    partition: int
    offset: int
    key_schema_id: int | None
    value_schema_id: int | None
    key: dict[str, Any] | None
    value: dict[str, Any] | None


def consumer(bootstrap_servers: str) -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": bootstrap_servers,
            "group.id": f"olist-stage2-check-{uuid.uuid4()}",
            "enable.auto.commit": False,
            "auto.offset.reset": "earliest",
        }
    )


def source_topic(table: str) -> str:
    return f"olist_cdc.public.{table}"


def beginning_assignments() -> list[TopicPartition]:
    return [
        TopicPartition(source_topic(table), partition, 0)
        for table, (partitions, _keys) in TOPICS.items()
        for partition in range(partitions)
    ]


def end_offsets(
    client: Consumer, topics: dict[str, tuple[int, tuple[str, ...]]]
) -> dict[tuple[str, int], int]:
    result: dict[tuple[str, int], int] = {}
    for table, (partitions, _keys) in topics.items():
        topic = source_topic(table)
        for partition in range(partitions):
            _, high = client.get_watermark_offsets(
                TopicPartition(topic, partition), timeout=10, cached=False
            )
            result[(topic, partition)] = high
    return result


def decode_records(
    client: Consumer,
    decoder: ApicurioAvroDecoder,
    assignments: list[TopicPartition],
    *,
    timeout: float = 60,
    idle_seconds: float = 3,
) -> list[DecodedRecord]:
    client.assign(assignments)
    deadline = time.monotonic() + timeout
    idle_deadline = time.monotonic() + idle_seconds
    records: list[DecodedRecord] = []
    while time.monotonic() < deadline:
        message = client.poll(0.5)
        if message is None:
            if time.monotonic() >= idle_deadline:
                break
            continue
        error = message.error()
        if error is not None:
            if error.code() == KafkaError._PARTITION_EOF:
                continue
            raise KafkaException(error)
        idle_deadline = time.monotonic() + idle_seconds
        raw_key = message.key()
        raw_value = message.value()
        key_id, key = (None, None) if raw_key is None else decoder.decode(raw_key)
        value_id, value = (
            (None, None) if raw_value is None else decoder.decode(raw_value)
        )
        topic = message.topic()
        partition = message.partition()
        offset = message.offset()
        assert topic is not None and partition is not None and offset is not None
        records.append(
            DecodedRecord(
                topic=topic,
                partition=partition,
                offset=offset,
                key_schema_id=key_id,
                value_schema_id=value_id,
                key=key,
                value=value,
            )
        )
    return records


def assert_snapshot(records: list[DecodedRecord]) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    schema_ids: dict[str, set[int]] = {}
    for record in records:
        table = record.topic.rsplit(".", 1)[-1]
        if record.value is None or record.value.get("op") != "r":
            continue
        counts[table] += 1
        expected_key_fields = set(TOPICS[table][1])
        if record.key is None or set(record.key) != expected_key_fields:
            raise AssertionError(
                f"{table} key fields are {set(record.key or {})}, "
                f"expected {expected_key_fields}"
            )
        if not record.key_schema_id or not record.value_schema_id:
            raise AssertionError(f"{table} record has no numeric schema ids")
        schema_ids.setdefault(table, set()).update(
            (record.key_schema_id, record.value_schema_id)
        )
        source = record.value.get("source") or {}
        if source.get("snapshot") in {None, "false"}:
            raise AssertionError(f"{table} snapshot marker is missing: {source}")
    if dict(counts) != EXPECTED_SNAPSHOT:
        raise AssertionError(
            f"snapshot reconciliation failed: actual={dict(counts)}, "
            f"expected={EXPECTED_SNAPSHOT}"
        )
    return {"counts": dict(counts), "schema_ids": schema_ids}


def create_crud_fixture(connection: Any) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "select product_id from public.products order by product_id limit 1"
        )
        product_id = cursor.fetchone()[0]
        cursor.execute(
            "select seller_id from public.sellers order by seller_id limit 1"
        )
        seller_id = cursor.fetchone()[0]
        cursor.execute(
            """
            insert into public.customers values
                ('cdc_customer_0001', 'cdc_unique_0001', '01001', 'sao paulo', 'SP');
            insert into public.orders values
                ('cdc_order_0001', 'cdc_customer_0001', 'created',
                 '2026-07-16 00:00:00', null, null, null, '2026-07-23 00:00:00');
            insert into public.order_items values
                ('cdc_order_0001', 1, %s, %s, '2026-07-17 00:00:00', 10.00, 2.00);
            insert into public.order_payments values
                ('cdc_order_0001', 1, 'credit_card', 1, 12.00)
            """,
            (product_id, seller_id),
        )
    connection.commit()

    with connection.cursor() as cursor:
        cursor.execute(
            "update public.orders set order_status='approved', "
            "order_approved_at='2026-07-16 00:01:00' where order_id='cdc_order_0001'"
        )
        cursor.execute(
            "update public.orders set order_status='shipped', "
            "order_delivered_carrier_date='2026-07-16 00:02:00' "
            "where order_id='cdc_order_0001'"
        )
    connection.commit()

    with connection.cursor() as cursor:
        cursor.execute(
            "delete from public.order_payments where order_id='cdc_order_0001'"
        )
        cursor.execute("delete from public.order_items where order_id='cdc_order_0001'")
        cursor.execute("delete from public.orders where order_id='cdc_order_0001'")
        cursor.execute(
            "delete from public.customers where customer_id='cdc_customer_0001'"
        )
    connection.commit()


def assert_crud(records: list[DecodedRecord]) -> dict[str, Any]:
    order_records = [
        record
        for record in records
        if record.topic == source_topic("orders")
        and record.key == {"order_id": "cdc_order_0001"}
    ]
    business = [record for record in order_records if record.value is not None]
    tombstones = [record for record in order_records if record.value is None]
    operations = [record.value["op"] for record in business if record.value]
    if operations != ["c", "u", "u", "d"]:
        raise AssertionError(f"unexpected order CRUD operations: {operations}")
    if len(tombstones) != 1 or tombstones[0].offset <= business[-1].offset:
        raise AssertionError("hard delete must be followed by exactly one tombstone")
    partitions = {record.partition for record in order_records}
    offsets = [record.offset for record in order_records]
    if len(partitions) != 1 or offsets != sorted(offsets):
        raise AssertionError("one source key did not remain ordered in one partition")

    updates = [
        record for record in business if record.value and record.value["op"] == "u"
    ]
    update_transactions: set[int] = set()
    orders: list[int] = []
    for record in updates:
        value = record.value
        assert value is not None
        update_transactions.add(value["source"]["txId"])
        transaction = value["transaction"]
        assert transaction is not None
        orders.append(transaction["data_collection_order"])
    if len(update_transactions) != 1:
        raise AssertionError(
            "multiple updates in one source transaction lost identity: "
            f"{sorted(update_transactions)}"
        )
    if orders != sorted(orders) or len(set(orders)) != 2:
        raise AssertionError(f"transaction event ordering is invalid: {orders}")
    for record in business:
        value = record.value
        assert value is not None
        source = value.get("source") or {}
        if not source.get("lsn") or not source.get("ts_us"):
            raise AssertionError(f"source LSN/timestamp missing: {source}")
        if value.get("transaction") is None:
            raise AssertionError("transaction metadata missing from CRUD record")

    create_graph = [
        record
        for record in records
        if record.value
        and record.value.get("op") == "c"
        and record.topic
        in {
            source_topic("customers"),
            source_topic("orders"),
            source_topic("order_items"),
            source_topic("order_payments"),
        }
        and record.key is not None
        and str(next(iter(record.key.values()))).startswith("cdc_")
    ]
    transaction_ids: set[int] = set()
    for record in create_graph:
        value = record.value
        assert value is not None
        transaction_ids.add(value["source"]["txId"])
    if len(create_graph) != 4 or len(transaction_ids) != 1:
        raise AssertionError(
            "multi-table create graph lost shared transaction identity"
        )
    return {
        "order_operations": operations,
        "partition": next(iter(partitions)),
        "offset_range": [min(offsets), max(offsets)],
        "update_transaction": next(iter(update_transactions)),
        "create_transaction": next(iter(transaction_ids)),
        "tombstones": len(tombstones),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--registry-url", default="http://localhost:8081")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5433)
    parser.add_argument("--database", default="olist_oltp")
    parser.add_argument("--user", default="olist_simulator")
    parser.add_argument(
        "--password-file",
        type=Path,
        default=Path("docker/secrets/dev/postgres_password.txt"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    decoder = ApicurioAvroDecoder(args.registry_url)
    kafka = consumer(args.bootstrap_servers)
    try:
        snapshot = decode_records(kafka, decoder, beginning_assignments())
        snapshot_evidence = assert_snapshot(snapshot)
        baseline = end_offsets(kafka, TOPICS)
        password = args.password_file.read_text(encoding="utf-8").strip()
        connection = psycopg2.connect(
            host=args.host,
            port=args.port,
            dbname=args.database,
            user=args.user,
            password=password,
        )
        try:
            create_crud_fixture(connection)
        finally:
            connection.close()
        assignments = [
            TopicPartition(topic, partition, offset)
            for (topic, partition), offset in baseline.items()
        ]
        crud = decode_records(kafka, decoder, assignments, timeout=60, idle_seconds=5)
        crud_evidence = assert_crud(crud)
    finally:
        kafka.close()
    evidence = {
        "snapshot": {
            "counts": snapshot_evidence["counts"],
            "schema_ids": {
                table: sorted(ids)
                for table, ids in snapshot_evidence["schema_ids"].items()
            },
        },
        "crud": crud_evidence,
    }
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
