from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import UTC, datetime
from io import BytesIO

from fastavro import reader
from nifiapi.flowfiletransform import FlowFileTransform, FlowFileTransformResult


class DescribeAvroBatch(FlowFileTransform):
    class Java:
        implements = ["org.apache.nifi.python.processor.FlowFileTransform"]

    class ProcessorDetails:
        version = "1.0.0"
        description = (
            "Validate a merged CDC Avro batch and derive immutable object identity."
        )
        tags = ["olist", "cdc", "avro", "manifest"]

    def __init__(self, **kwargs):
        super().__init__()

    def transform(self, context, flowfile):
        from cdc_common import offset_ranges

        content = bytes(flowfile.getContentsAsBytes())
        records = list(reader(BytesIO(content)))
        if not records:
            return FlowFileTransformResult(
                relationship="failure",
                attributes={"cdc.error.reason": "empty Avro batch"},
            )
        topics = {record["_topic"] for record in records}
        partitions = {int(record["_partition"]) for record in records}
        schema_ids = {record.get("_schema_id") for record in records}
        if len(topics) != 1 or len(partitions) != 1 or len(schema_ids) != 1:
            return FlowFileTransformResult(
                relationship="failure",
                attributes={
                    "cdc.error.reason": "batch mixed topic, partition, or schema"
                },
            )
        topic = next(iter(topics))
        table = topic.rsplit(".", 1)[-1]
        partition = next(iter(partitions))
        schema_id = next(iter(schema_ids))
        offsets = [int(record["_offset"]) for record in records]
        event_ids = [str(record["_event_id"]) for record in records]
        kind = flowfile.getAttribute("cdc.kind") or "normalized"
        extension = "avro" if kind == "landing" else "parquet"
        prefix = "landing/debezium" if kind == "landing" else "stage/cdc"
        timestamps = [
            record.get("_source_ts") or record.get("_kafka_ts") for record in records
        ]
        timestamps = [value for value in timestamps if value is not None]
        event_time = min(timestamps) if timestamps else datetime.now(UTC)
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=UTC)
        digest = hashlib.sha256("\n".join(sorted(event_ids)).encode()).hexdigest()[:16]
        safe_topic = re.sub(r"[^a-zA-Z0-9_.-]", "_", topic)
        schema_text = "tombstone" if schema_id is None else str(schema_id)
        stem = (
            f"{safe_topic}-p={partition:05d}-o={min(offsets):020d}-"
            f"{max(offsets):020d}-sid={schema_text}-{digest}"
        )
        date_text = event_time.strftime("%Y-%m-%d")
        hour_text = event_time.strftime("%H")
        object_key = (
            f"{prefix}/table={table}/event_date={date_text}/hour={hour_text}/"
            f"{stem}.{extension}"
        )
        manifest_key = (
            f"manifests/cdc/kind={kind}/table={table}/ingest_date={date_text}/"
            f"hour={hour_text}/{stem}.manifest.json"
        )
        op_counts = Counter(str(record.get("_op") or "tombstone") for record in records)
        attributes = {
            "cdc.table": table,
            "cdc.topic": topic,
            "cdc.partition": str(partition),
            "cdc.schema_id": schema_text,
            "cdc.kind": kind,
            "cdc.row_count": str(len(records)),
            "cdc.covered_offset_ranges": json.dumps(
                offset_ranges(offsets), separators=(",", ":")
            ),
            "cdc.operation_counts": json.dumps(
                dict(op_counts), sort_keys=True, separators=(",", ":")
            ),
            "cdc.object.key": object_key,
            "cdc.manifest.key": manifest_key,
            "cdc.batch.identity": digest,
            "cdc.source_ts_min": min(timestamps).isoformat() if timestamps else "",
            "cdc.source_ts_max": max(timestamps).isoformat() if timestamps else "",
            "cdc.closed_at": datetime.now(UTC).isoformat(),
            "filename": f"{stem}.{extension}",
        }
        return FlowFileTransformResult(relationship="success", attributes=attributes)
