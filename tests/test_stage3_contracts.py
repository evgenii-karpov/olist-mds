from __future__ import annotations

import hashlib
import json
import unittest
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import Any, cast

from fastavro import parse_schema, reader, writer
from streaming.nifi.python.cdc_common import offset_ranges

ROOT = Path(__file__).resolve().parents[1]


class Stage3ContractTests(unittest.TestCase):
    def test_offset_ranges_preserve_non_contiguous_coverage(self) -> None:
        self.assertEqual([[1, 3], [7, 8], [11, 11]], offset_ranges([8, 2, 1, 3, 7, 11]))

    def test_landing_schema_round_trips_raw_bytes_and_tombstone(self) -> None:
        schema = parse_schema(
            json.loads(
                (ROOT / "streaming/schemas/cdc-landing/v1.avsc").read_text(
                    encoding="utf-8"
                )
            )
        )
        record = {
            "_event_id": "topic:0:1",
            "_table": "orders",
            "_op": None,
            "_source_ts": None,
            "_source_lsn": None,
            "_tx_id": None,
            "_tx_order": None,
            "_topic": "topic",
            "_partition": 0,
            "_offset": 1,
            "_kafka_ts": datetime.now(UTC),
            "_key_schema_id": 1,
            "_schema_id": None,
            "_tombstone": True,
            "_nifi_written_at": datetime.now(UTC),
            "key_bytes": b"key",
            "value_bytes": None,
            "key_json": "{}",
            "envelope_json": None,
        }
        output = BytesIO()
        writer(output, schema, [record])
        actual = cast(dict[str, Any], next(iter(reader(BytesIO(output.getvalue())))))
        self.assertEqual(b"key", actual["key_bytes"])
        self.assertTrue(actual["_tombstone"])

    def test_manifest_identity_is_stable_for_same_event_set(self) -> None:
        events = ["topic:0:7", "topic:0:9", "topic:0:8"]
        first = hashlib.sha256("\n".join(sorted(events)).encode()).hexdigest()[:16]
        second = hashlib.sha256(
            "\n".join(sorted(reversed(events))).encode()
        ).hexdigest()[:16]
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
