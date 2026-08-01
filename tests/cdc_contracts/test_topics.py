from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from streaming.kafka.validate_topics import (
    TopicState,
    load_manifest,
    parse_describe,
    validate_states,
)

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "streaming" / "kafka" / "topics.json"
BOOTSTRAP_PATH = ROOT / "streaming" / "kafka" / "create-topics.sh"

EXPECTED = {
    "olist_cdc.olist_oltp.customers": (1, "delete", "604800000", None),
    "olist_cdc.olist_oltp.orders": (3, "delete", "604800000", None),
    "olist_cdc.olist_oltp.order_items": (3, "delete", "604800000", None),
    "olist_cdc.olist_oltp.order_payments": (3, "delete", "604800000", None),
    "olist_cdc.olist_oltp.order_reviews": (3, "delete", "604800000", None),
    "olist_cdc.olist_oltp.products": (1, "delete", "604800000", None),
    "olist_cdc.olist_oltp.sellers": (1, "delete", "604800000", None),
    "olist_cdc.olist_oltp.product_category_translation": (
        1,
        "delete",
        "604800000",
        None,
    ),
    "olist_cdc.transaction": (1, "delete", "604800000", None),
    "olist_cdc.heartbeat": (1, "delete", "604800000", None),
    "olist_cdc": (1, "delete", "-1", "-1"),
    "olist_cdc.schema_history": (1, "delete", "-1", "-1"),
    "olist_connect_configs": (1, "compact", "-1", None),
    "olist_connect_offsets": (25, "compact", "-1", None),
    "olist_connect_status": (5, "compact", "-1", None),
}


class TopicManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_manifest_is_the_closed_fifteen_topic_set(self) -> None:
        self.assertFalse(self.manifest["auto_create_topics"])
        self.assertEqual(1, self.manifest["replication_factor"])
        topics = self.manifest["topics"]
        self.assertEqual(15, len(topics))
        self.assertEqual(set(EXPECTED), {topic["name"] for topic in topics})
        self.assertFalse(any(".dlq." in topic["name"] for topic in topics))
        self.assertFalse(any(".public." in topic["name"] for topic in topics))
        validated = load_manifest(MANIFEST_PATH)
        self.assertIn("retention.bytes", validated["dangerous_unmanifested_configs"])

    def test_every_topic_has_exact_partitions_and_properties(self) -> None:
        by_name = {topic["name"]: topic for topic in self.manifest["topics"]}
        for name, (partitions, cleanup, retention, retention_bytes) in EXPECTED.items():
            with self.subTest(topic=name):
                topic = by_name[name]
                self.assertEqual(partitions, topic["partitions"])
                self.assertEqual(cleanup, topic["config"]["cleanup.policy"])
                self.assertEqual(retention, topic["config"]["retention.ms"])
                self.assertEqual(
                    retention_bytes, topic["config"].get("retention.bytes")
                )

    def test_schema_history_is_not_compacted(self) -> None:
        topic = next(
            topic
            for topic in self.manifest["topics"]
            if topic["name"] == "olist_cdc.schema_history"
        )
        self.assertEqual(
            {
                "cleanup.policy": "delete",
                "retention.ms": "-1",
                "retention.bytes": "-1",
            },
            topic["config"],
        )

    def test_dependency_free_bootstrap_matches_manifest(self) -> None:
        declarations: dict[str, tuple[int, dict[str, str]]] = {}
        pattern = re.compile(r"^create_topic\s+(\S+)\s+(\d+)\s+(.+)$")
        for line in BOOTSTRAP_PATH.read_text(encoding="utf-8").splitlines():
            match = pattern.match(line)
            if match is None:
                continue
            configs = dict(item.split("=", 1) for item in match.group(3).split())
            declarations[match.group(1)] = (int(match.group(2)), configs)
        expected = {
            topic["name"]: (topic["partitions"], topic["config"])
            for topic in self.manifest["topics"]
        }
        self.assertEqual(expected, declarations)
        script = BOOTSTRAP_PATH.read_text(encoding="utf-8")
        self.assertIn("partition drift", script)
        self.assertIn("dangerous unmanifested override", script)
        self.assertIn("PartitionCount:", script)
        lines = script.splitlines()
        start = lines.index("dangerous_configs=(") + 1
        end = lines.index(")", start)
        self.assertEqual(
            self.manifest["dangerous_unmanifested_configs"],
            [line.strip() for line in lines[start:end]],
        )

    def test_live_validator_detects_all_contract_drift(self) -> None:
        states = {
            topic["name"]: TopicState(
                topic["name"],
                topic["partitions"],
                1,
                dict(topic["config"]),
            )
            for topic in self.manifest["topics"]
        }
        self.assertEqual([], validate_states(self.manifest, states))

        drifted = dict(states)
        drifted["olist_cdc.olist_oltp.orders"] = TopicState(
            "olist_cdc.olist_oltp.orders",
            2,
            1,
            {"cleanup.policy": "compact", "retention.ms": "1"},
        )
        drifted.pop("olist_cdc.heartbeat")
        drifted["olist_cdc.unexpected"] = TopicState(
            "olist_cdc.unexpected", 1, 1, {"cleanup.policy": "delete"}
        )
        errors = validate_states(self.manifest, drifted)
        self.assertTrue(any("missing topic" in error for error in errors))
        self.assertTrue(any("unexpected managed topic" in error for error in errors))
        self.assertTrue(any("partitions=2" in error for error in errors))
        self.assertTrue(any("cleanup.policy" in error for error in errors))

    def test_live_validator_rejects_dangerous_unmanifested_override(self) -> None:
        states = {
            topic["name"]: TopicState(
                topic["name"], topic["partitions"], 1, dict(topic["config"])
            )
            for topic in self.manifest["topics"]
        }
        customers = states["olist_cdc.olist_oltp.customers"]
        states[customers.name] = TopicState(
            customers.name,
            customers.partitions,
            customers.replication_factor,
            {**customers.config, "retention.bytes": "42"},
        )
        errors = validate_states(self.manifest, states)
        self.assertTrue(
            any(
                "dangerous unmanifested override retention.bytes" in error
                for error in errors
            )
        )

    def test_kafka_describe_parser_extracts_explicit_config(self) -> None:
        output = (
            "Topic: olist_cdc TopicId: abc PartitionCount: 1 "
            "ReplicationFactor: 1 Configs: cleanup.policy=delete,"
            "retention.ms=-1,retention.bytes=-1\n"
        )
        state = parse_describe(output)["olist_cdc"]
        self.assertEqual(1, state.partitions)
        self.assertEqual("delete", state.config["cleanup.policy"])
        self.assertEqual("-1", state.config["retention.bytes"])


if __name__ == "__main__":
    unittest.main()
