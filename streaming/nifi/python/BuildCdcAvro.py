from __future__ import annotations

import json
import struct
import time
from decimal import Decimal
from typing import Any

from nifiapi.flowfiletransform import FlowFileTransform, FlowFileTransformResult
from nifiapi.properties import PropertyDescriptor, StandardValidators


class BuildCdcAvro(FlowFileTransform):
    class Java:
        implements = ["org.apache.nifi.python.processor.FlowFileTransform"]

    class ProcessorDetails:
        version = "1.0.0"
        description = "Decode Debezium Avro and build landing or normalized Avro OCF."
        tags = ["olist", "cdc", "debezium", "avro"]

    def __init__(self, **kwargs):
        super().__init__()
        self.output_kind = PropertyDescriptor(
            name="Output Kind",
            description="landing preserves the envelope; normalized selects after/before.",
            required=True,
            default_value="normalized",
            allowable_values=["landing", "normalized"],
        )
        self.registry_url = PropertyDescriptor(
            name="Registry URL",
            description="Apicurio base URL without the ccompat suffix.",
            required=True,
            default_value="http://apicurio-registry:8080",
            validators=[StandardValidators.NON_EMPTY_VALIDATOR],
        )
        self.schema_directory = PropertyDescriptor(
            name="Schema Directory",
            description="Directory containing versioned landing and normalized schemas.",
            required=True,
            default_value="/opt/olist/schemas",
            validators=[StandardValidators.NON_EMPTY_VALIDATOR],
        )

    def getPropertyDescriptors(self):
        return [self.output_kind, self.registry_url, self.schema_directory]

    def onScheduled(self, context):
        from cdc_common import ApicurioAvroDecoder

        self.decoder = ApicurioAvroDecoder(
            context.getProperty(self.registry_url).getValue()
        )

    @staticmethod
    def _decimal(value: Any) -> Decimal:
        return value if isinstance(value, Decimal) else Decimal(str(value))

    @staticmethod
    def _business_timestamps(table: str) -> set[str]:
        return {
            "orders": {
                "order_purchase_timestamp",
                "order_approved_at",
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
                "order_estimated_delivery_date",
            },
            "order_items": {"shipping_limit_date"},
            "order_reviews": {"review_creation_date", "review_answer_timestamp"},
        }.get(table, set())

    def transform(self, context, flowfile):
        from cdc_common import (
            avro_container,
            epoch_micros,
            epoch_millis,
            json_default,
            load_schema,
            to_long,
        )

        attributes = flowfile.getAttributes()
        topic = attributes.get("kafka.topic", "")
        table = topic.rsplit(".", 1)[-1]
        partition = int(attributes.get("kafka.partition", "-1"))
        offset = int(attributes.get("kafka.offset", "-1"))
        kafka_ts = attributes.get("kafka.timestamp")
        tombstone = (attributes.get("kafka.tombstone") or "false").lower() == "true"
        event_id = f"{topic}:{partition}:{offset}"
        raw_value = bytes(flowfile.getContentsAsBytes())
        key_hex = attributes.get("kafka.key")
        raw_key = bytes.fromhex(key_hex) if key_hex else None
        kind = context.getProperty(self.output_kind).getValue()
        schema_directory = context.getProperty(self.schema_directory).getValue()

        try:
            try:
                key_schema_id, key = (
                    (None, None) if raw_key is None else self.decoder.decode(raw_key)
                )
                value_schema_id, envelope = (
                    (None, None) if tombstone else self.decoder.decode(raw_value)
                )
            except ValueError:
                if kind != "landing":
                    raise
                key_schema_id = (
                    struct.unpack(">I", raw_key[1:5])[0]
                    if raw_key is not None and len(raw_key) >= 5 and raw_key[0] == 0
                    else None
                )
                value_schema_id = (
                    struct.unpack(">I", raw_value[1:5])[0]
                    if not tombstone and len(raw_value) >= 5 and raw_value[0] == 0
                    else None
                )
                key = None
                envelope = None
            source = (envelope or {}).get("source") or {}
            transaction = (envelope or {}).get("transaction") or {}
            op = (envelope or {}).get("op")
            source_ts_value = source.get("ts_us")
            if source_ts_value is None and source.get("ts_ms") is not None:
                source_ts_value = int(source["ts_ms"]) * 1000
            metadata = {
                "_event_id": event_id,
                "_op": op,
                "_source_ts": epoch_micros(source_ts_value),
                "_source_lsn": to_long(source.get("lsn")),
                "_tx_id": to_long(source.get("txId")),
                "_tx_order": to_long(transaction.get("data_collection_order")),
                "_topic": topic,
                "_partition": partition,
                "_offset": offset,
                "_kafka_ts": epoch_millis(kafka_ts),
                "_key_schema_id": key_schema_id,
                "_schema_id": value_schema_id,
                "_nifi_written_at": epoch_millis(int(time.time() * 1000)),
            }

            if kind == "landing":
                record = {
                    **metadata,
                    "_table": table,
                    "_tombstone": tombstone,
                    "key_bytes": raw_key,
                    "value_bytes": None if tombstone else raw_value,
                    "key_json": None
                    if key is None
                    else json.dumps(key, default=json_default, sort_keys=True),
                    "envelope_json": None
                    if envelope is None
                    else json.dumps(envelope, default=json_default, sort_keys=True),
                }
                schema = load_schema(schema_directory, "landing")
                schema_key = (
                    value_schema_id if value_schema_id is not None else "tombstone"
                )
            else:
                if tombstone:
                    raise ValueError("tombstones do not produce normalized records")
                if op not in {"r", "c", "u", "d"}:
                    raise ValueError(f"unsupported Debezium operation: {op!r}")
                business = envelope.get("before" if op == "d" else "after")
                if not isinstance(business, dict):
                    raise ValueError(f"operation {op!r} has no business row")
                record = dict(business)
                for field in self._business_timestamps(table):
                    if field in record and record[field] is not None:
                        record[field] = epoch_micros(record[field])
                for field in {"price", "freight_value", "payment_value"}:
                    if field in record and record[field] is not None:
                        record[field] = self._decimal(record[field])
                record.update(metadata)
                schema = load_schema(schema_directory, "normalized", table)
                schema_key = value_schema_id

            content = avro_container(schema, record)
            output_attributes = {
                "cdc.event_id": event_id,
                "cdc.table": table,
                "cdc.topic": topic,
                "cdc.partition": str(partition),
                "cdc.schema_id": str(schema_key),
                "cdc.kind": kind,
                "cdc.bin.key": f"{kind}|{topic}|{partition}|{schema_key}",
                "mime.type": "application/avro",
            }
            return FlowFileTransformResult(
                relationship="success", contents=content, attributes=output_attributes
            )
        except ValueError as exc:
            return FlowFileTransformResult(
                relationship="failure",
                attributes={
                    "cdc.error.stage": "normalize",
                    "cdc.error.reason": str(exc)[:512],
                    "cdc.event_id": event_id,
                    "cdc.table": table,
                },
            )
