from __future__ import annotations

import base64
import hashlib
import json
from datetime import UTC, datetime

from nifiapi.flowfiletransform import FlowFileTransform, FlowFileTransformResult


class BuildDlqEnvelope(FlowFileTransform):
    class Java:
        implements = ["org.apache.nifi.python.processor.FlowFileTransform"]

    class ProcessorDetails:
        version = "1.0.0"
        description = (
            "Build a versioned JSON error envelope for quarantine and Kafka DLQ."
        )
        tags = ["olist", "cdc", "quarantine", "dlq"]

    def __init__(self, **kwargs):
        super().__init__()

    def transform(self, context, flowfile):
        attributes = flowfile.getAttributes()
        topic = attributes.get("kafka.topic", "unknown")
        table = topic.rsplit(".", 1)[-1]
        partition = int(attributes.get("kafka.partition", "-1"))
        offset = int(attributes.get("kafka.offset", "-1"))
        event_id = f"{topic}:{partition}:{offset}"
        content = bytes(flowfile.getContentsAsBytes())
        reason = (attributes.get("cdc.error.reason") or "invalid CDC event")[:512]
        envelope = {
            "contract_version": 1,
            "stage": attributes.get("cdc.error.stage", "normalize"),
            "reason": reason,
            "processor": "BuildCdcAvro",
            "event_id": event_id,
            "topic": topic,
            "partition": partition,
            "offset": offset,
            "schema_id": attributes.get("cdc.schema_id"),
            "key_hex": attributes.get("kafka.key"),
            "value_base64": base64.b64encode(content).decode(),
            "quarantined_at": datetime.now(UTC).isoformat(),
        }
        output = json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode()
        digest = hashlib.sha256(output).hexdigest()[:16]
        date_text = datetime.now(UTC).strftime("%Y-%m-%d")
        object_key = (
            f"quarantine/stage=normalize/reason=invalid_event/event_date={date_text}/"
            f"{table}-p={partition:05d}-o={offset:020d}-{digest}.json"
        )
        return FlowFileTransformResult(
            relationship="success",
            contents=output,
            attributes={
                "cdc.kind": "quarantine",
                "cdc.table": table,
                "cdc.object.key": object_key,
                "cdc.dlq.topic": f"olist_cdc.dlq.{table}",
                "mime.type": "application/json",
            },
        )
