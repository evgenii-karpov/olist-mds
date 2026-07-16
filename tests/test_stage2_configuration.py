from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from scripts.cdc.stage2_admin import connector_is_running, parse_topic_description

ROOT = Path(__file__).resolve().parents[1]

CAPTURED = {
    "customers": (1, ("customer_id",)),
    "orders": (3, ("order_id",)),
    "order_items": (3, ("order_id", "order_item_id")),
    "order_payments": (3, ("order_id", "payment_sequential")),
    "order_reviews": (3, ("review_id", "order_id")),
    "products": (1, ("product_id",)),
    "sellers": (1, ("seller_id",)),
    "product_category_translation": (1, ("product_category_name",)),
}


class Stage2ConfigurationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.topics = json.loads(
            (ROOT / "streaming/kafka/topics.json").read_text(encoding="utf-8")
        )["topics"]
        self.connector = json.loads(
            (ROOT / "streaming/connect/olist-postgres-cdc.json").read_text(
                encoding="utf-8"
            )
        )

    def test_exact_images_and_no_floating_tags(self) -> None:
        compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
        self.assertIn("image: apache/kafka:4.3.1", compose)
        self.assertIn("image: quay.io/apicurio/apicurio-registry:3.3.0", compose)
        dockerfile = (ROOT / "streaming/connect/Dockerfile").read_text(encoding="utf-8")
        self.assertIn("quay.io/debezium/connect@sha256:", dockerfile)
        self.assertNotIn(":latest", compose + dockerfile)

    def test_source_and_dlq_topics_match_contract(self) -> None:
        by_name = {topic["name"]: topic for topic in self.topics}
        for table, (partitions, _key_fields) in CAPTURED.items():
            source = by_name[f"olist_cdc.public.{table}"]
            dlq = by_name[f"olist_cdc.dlq.{table}"]
            for topic in (source, dlq):
                self.assertEqual(partitions, topic["partitions"])
                self.assertEqual(1, topic["replication_factor"])
                self.assertEqual("delete", topic["cleanup_policy"])
                self.assertEqual(604_800_000, topic["retention_ms"])
        self.assertNotIn("olist_cdc.public.geolocation", by_name)

    def test_topic_bootstrap_matches_manifest(self) -> None:
        script = (ROOT / "streaming/kafka/create-topics.sh").read_text(encoding="utf-8")
        created = set(re.findall(r"^create_topic\s+(\S+)", script, re.MULTILINE))
        self.assertEqual({topic["name"] for topic in self.topics}, created)

    def test_internal_topic_contract(self) -> None:
        by_name = {topic["name"]: topic for topic in self.topics}
        expected = {
            "olist_connect_configs": (1, "compact"),
            "olist_connect_offsets": (25, "compact"),
            "olist_connect_status": (5, "compact"),
            "olist_cdc.schema_history": (1, "compact"),
            "olist_cdc.transaction": (1, "delete"),
            "olist_cdc.heartbeat": (1, "delete"),
        }
        for name, (partitions, policy) in expected.items():
            self.assertEqual(partitions, by_name[name]["partitions"])
            self.assertEqual(policy, by_name[name]["cleanup_policy"])

    def test_connector_is_secret_free_and_excludes_control_data(self) -> None:
        config = self.connector["config"]
        self.assertEqual("${OLTP_CDC_READER_PASSWORD}", config["database.password"])
        include = set(config["table.include.list"].split(","))
        self.assertEqual({f"public.{name}" for name in CAPTURED}, include)
        self.assertNotIn("public.geolocation", include)
        self.assertNotIn("simulator_control", config["schema.include.list"])
        self.assertEqual("true", config["provide.transaction.metadata"])
        self.assertEqual("true", config["tombstones.on.delete"])
        self.assertFalse(any(key.startswith("topic.creation.") for key in config))
        self.assertEqual("none", config["errors.tolerance"])
        compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
        self.assertIn('CONNECT_TOPIC_CREATION_ENABLE: "false"', compose)
        self.assertEqual(
            "isDerivedHeartbeat", config["transforms.routeHeartbeat.predicate"]
        )
        self.assertEqual(
            "olist_cdc.heartbeat", config["transforms.routeHeartbeat.replacement"]
        )

    def test_confluent_compatible_avro_converter_contract(self) -> None:
        config = self.connector["config"]
        for side in ("key", "value"):
            prefix = f"{side}.converter"
            self.assertEqual(
                "io.apicurio.registry.utils.converter.AvroConverter", config[prefix]
            )
            self.assertEqual("true", config[f"{prefix}.apicurio.registry.as-confluent"])
            self.assertEqual("contentId", config[f"{prefix}.apicurio.use-id"])
            self.assertEqual("false", config[f"{prefix}.schemas.enable"])
            self.assertEqual(
                "false", config[f"{prefix}.apicurio.registry.headers.enabled"]
            )

    def test_primary_key_contract_is_explicit(self) -> None:
        expected = {
            "order_items": ("order_id", "order_item_id"),
            "order_payments": ("order_id", "payment_sequential"),
            "order_reviews": ("review_id", "order_id"),
        }
        self.assertEqual(expected, {k: CAPTURED[k][1] for k in expected})

    def test_status_parser_rejects_failed_or_partial_state(self) -> None:
        running = {"connector": {"state": "RUNNING"}, "tasks": [{"state": "RUNNING"}]}
        failed = {"connector": {"state": "FAILED"}, "tasks": [{"state": "FAILED"}]}
        partial = {
            "connector": {"state": "RUNNING"},
            "tasks": [{"state": "UNASSIGNED"}],
        }
        self.assertTrue(connector_is_running(running))
        self.assertFalse(connector_is_running(failed))
        self.assertFalse(connector_is_running(partial))

    def test_topic_description_parser(self) -> None:
        output = (
            "Topic: x\tTopicId: id\tPartitionCount: 3\tReplicationFactor: 1\t"
            "Configs: cleanup.policy=delete,retention.ms=604800000\n"
        )
        partitions, replication, configs = parse_topic_description(output)
        self.assertEqual((3, 1), (partitions, replication))
        self.assertEqual("delete", configs["cleanup.policy"])


if __name__ == "__main__":
    unittest.main()
