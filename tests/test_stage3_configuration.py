from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.ci.validate_nifi_flow import REQUIRED_METADATA, TABLES

ROOT = Path(__file__).resolve().parents[1]


class Stage3ConfigurationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
        self.flow = json.loads(
            (ROOT / "streaming/nifi/flow/olist-cdc-v1.json").read_text(encoding="utf-8")
        )

    def test_realtime_services_and_persistent_repositories(self) -> None:
        for service in ("minio", "minio-init", "nifi", "nifi-bootstrap"):
            self.assertIn(f"  {service}:", self.compose)
        for volume in (
            "olist_minio_data",
            "olist_nifi_conf",
            "olist_nifi_flowfile",
            "olist_nifi_content",
            "olist_nifi_provenance",
            "olist_nifi_state",
        ):
            self.assertIn(volume, self.compose)

    def test_minio_uses_final_security_release_from_source(self) -> None:
        dockerfile = (ROOT / "streaming/minio/Dockerfile").read_text(encoding="utf-8")
        self.assertIn("RELEASE.2025-10-15T17-29-55Z", dockerfile)
        self.assertIn("go install github.com/minio/minio@", dockerfile)
        init = (ROOT / "streaming/minio/init.sh").read_text(encoding="utf-8")
        self.assertIn("mc version enable", init)
        self.assertIn("olist_nifi", init)

    def test_flow_uses_durable_group_and_bounded_bins(self) -> None:
        by_name = {item["name"]: item for item in self.flow["processors"]}
        consume = by_name["Consume Olist CDC"]["properties"]
        self.assertEqual("#{kafka_group_id}", consume["Group ID"])
        self.assertEqual("true", consume["Commit Offsets"])
        for name in ("Merge Landing", "Merge Normalized"):
            self.assertEqual(
                "#{max_bin_age}", by_name[name]["properties"]["Max Bin Age"]
            )
            self.assertEqual(
                "#{maximum_bin_size}", by_name[name]["properties"]["Maximum Bin Size"]
            )

    def test_flow_routes_delete_tombstone_and_poison_records_once(self) -> None:
        by_name = {item["name"]: item for item in self.flow["processors"]}
        self.assertIn("tombstone", by_name["Route Tombstones"]["properties"])
        self.assertEqual(
            "Rollback", by_name["Publish Table DLQ"]["properties"]["Failure Strategy"]
        )
        connections = {tuple(item) for item in self.flow["connections"]}
        self.assertIn(
            ("Build Normalized Avro", "failure", "Build DLQ Envelope"), connections
        )
        self.assertIn(
            ("Route Quarantine and DLQ", "quarantine", "Put Quarantine Immutable"),
            connections,
        )
        self.assertIn(
            ("Route Quarantine and DLQ", "dlq", "Publish Table DLQ"), connections
        )

    def test_all_normalized_schemas_have_ordering_metadata(self) -> None:
        for table in TABLES:
            schema = json.loads(
                (ROOT / f"streaming/schemas/normalized/{table}/v1.avsc").read_text(
                    encoding="utf-8"
                )
            )
            fields = {field["name"] for field in schema["fields"]}
            self.assertTrue(fields >= REQUIRED_METADATA, table)

    def test_no_secret_values_in_flow_or_parameter_template(self) -> None:
        text = json.dumps(self.flow) + (
            ROOT / "streaming/nifi/parameters/local.template.json"
        ).read_text(encoding="utf-8")
        self.assertNotIn("minioadmin123", text.lower())
        self.assertNotIn("secret-access-key", text.lower())
        self.assertIn("/run/secrets/minio_nifi_password", text)


if __name__ == "__main__":
    unittest.main()
