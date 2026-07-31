from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any

from scripts.ci.validate_nifi_flow import REQUIRED_METADATA, TABLES

ROOT = Path(__file__).resolve().parents[1]


class Stage3ConfigurationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
        self.flow = json.loads(
            (ROOT / "streaming/nifi/flow/olist-cdc-v1.json").read_text(encoding="utf-8")
        )
        self.parameters = json.loads(
            (ROOT / "streaming/nifi/parameters/local.template.json").read_text(
                encoding="utf-8"
            )
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

    def test_nifi_uses_python_312_for_processor_discovery(self) -> None:
        dockerfile = (ROOT / "streaming/nifi/Dockerfile").read_text(encoding="utf-8")
        start = (ROOT / "streaming/nifi/start.sh").read_text(encoding="utf-8")
        self.assertIn(
            "FROM python:3.12-slim-bookworm AS nifi-python-runtime", dockerfile
        )
        self.assertIn(
            "COPY --from=nifi-python-runtime /usr/local /usr/local", dockerfile
        )
        self.assertIn('NIFI_PYTHON_COMMAND="/usr/local/bin/python3.12"', start)
        self.assertIn("nifi.python.command=${NIFI_PYTHON_COMMAND}", start)
        self.assertIn("NIFI_JVM_HEAP_INIT: 2g", self.compose)
        self.assertIn("NIFI_JVM_HEAP_MAX: 4g", self.compose)

    def test_flow_uses_durable_group_and_bounded_bins(self) -> None:
        by_name = {item["name"]: item for item in self.flow["processors"]}
        consume = by_name["Consume Olist CDC"]["properties"]
        self.assertEqual("#{kafka_group_id}", consume["Group ID"])
        self.assertEqual("true", consume["Commit Offsets"])
        kafka_service = self.flow["controller_services"][0]["properties"]
        self.assertEqual("500", kafka_service["max.poll.records"])
        self.assertNotIn("max.poll.interval.ms", kafka_service)
        for name in ("Merge Landing", "Merge Normalized"):
            self.assertEqual(
                "#{max_bin_age}", by_name[name]["properties"]["Max Bin Age"]
            )
            self.assertEqual(
                "#{maximum_bin_size}", by_name[name]["properties"]["Maximum Bin Size"]
            )

    def test_local_nifi_profile_is_sized_for_full_fixture_snapshot(self) -> None:
        self.assertEqual("0 sec", self.parameters["default_scheduling_period"])
        self.assertEqual(4, self.parameters["default_concurrent_tasks"])
        self.assertEqual(20000, self.parameters["backpressure_object_threshold"])
        self.assertEqual("1 GB", self.parameters["backpressure_data_size_threshold"])
        concurrency = self.parameters["processor_concurrent_tasks"]
        self.assertEqual(2, concurrency["Consume Olist CDC"])
        self.assertEqual(8, concurrency["Route Tombstones"])
        self.assertEqual(8, concurrency["Build Landing Avro"])
        self.assertEqual(8, concurrency["Build Normalized Avro"])
        self.assertEqual(4, concurrency["Merge Landing Micro-batch"])
        self.assertEqual(4, concurrency["Merge Normalized Micro-batch"])

    def test_nifi_bootstrap_updates_existing_runtime_settings(self) -> None:
        deploy = (ROOT / "streaming/nifi/deploy_flow.py").read_text(encoding="utf-8")
        self.assertIn("update_processor", deploy)
        self.assertIn("update_service", deploy)
        self.assertIn("update_connection", deploy)
        self.assertIn("stop_processors", deploy)
        self.assertIn("disable_services", deploy)
        self.assertIn("default_scheduling_period", deploy)
        self.assertIn("processor_concurrent_tasks", deploy)

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
            ("Build DLQ Envelope", "success", "Put Quarantine Immutable"),
            connections,
        )
        self.assertIn(
            ("Build DLQ Envelope", "success", "Publish Table DLQ"), connections
        )

    def test_flow_uses_direct_relationship_fanout_and_two_stage_merges(self) -> None:
        names = {item["name"] for item in self.flow["processors"]}
        self.assertNotIn("Duplicate Business Event", names)
        self.assertNotIn("Route Landing and Normalized", names)
        self.assertNotIn("Duplicate DLQ Envelope", names)
        self.assertNotIn("Route Quarantine and DLQ", names)
        self.assertNotIn("copy.index", json.dumps(self.flow))

        connections = {tuple(item) for item in self.flow["connections"]}
        for branch in ("Landing", "Normalized"):
            self.assertIn(
                (f"Build {branch} Avro", "success", f"Merge {branch} Micro-batch"),
                connections,
            )
            self.assertIn(
                (
                    f"Merge {branch} Micro-batch",
                    "merged",
                    f"Merge {branch}",
                ),
                connections,
            )
            micro = self.flow_processor(f"Merge {branch} Micro-batch")
            final = self.flow_processor(f"Merge {branch}")
            self.assertEqual(
                "cdc.bin.key", micro["properties"]["Correlation Attribute Name"]
            )
            self.assertEqual(
                "cdc.bin.key", final["properties"]["Correlation Attribute Name"]
            )
            self.assertEqual("1000", micro["properties"]["Maximum Number of Records"])
            self.assertEqual("50000", final["properties"]["Maximum Number of Records"])

        self.assertIn(
            ("Route Tombstones", "unmatched", "Build Landing Avro"), connections
        )
        self.assertIn(
            ("Route Tombstones", "unmatched", "Build Normalized Avro"), connections
        )
        self.assertIn(
            ("Route Tombstones", "tombstone", "Build Landing Avro"), connections
        )
        self.assertNotIn(
            ("Route Tombstones", "tombstone", "Build Normalized Avro"), connections
        )

    def flow_processor(self, name: str) -> dict[str, Any]:
        return next(item for item in self.flow["processors"] if item["name"] == name)

    def test_all_normalized_schemas_have_ordering_metadata(self) -> None:
        for table in TABLES:
            schema = json.loads(
                (ROOT / f"streaming/schemas/normalized/{table}/v1.avsc").read_text(
                    encoding="utf-8"
                )
            )
            fields = {field["name"] for field in schema["fields"]}
            self.assertTrue(fields >= REQUIRED_METADATA, table)

    def test_coverage_manifest_contract_is_versioned(self) -> None:
        schema = json.loads(
            (ROOT / "streaming/schemas/cdc-coverage/v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(1, schema["properties"]["contract_version"]["const"])
        self.assertEqual("coverage", schema["properties"]["kind"]["const"])
        put_processor = (
            ROOT / "streaming/nifi/python/PutImmutableS3Object.py"
        ).read_text(encoding="utf-8")
        self.assertIn('"tombstone_offset_ranges"', put_processor)
        self.assertIn('attributes.get("cdc.coverage.key")', put_processor)
        describe_processor = (
            ROOT / "streaming/nifi/python/DescribeAvroBatch.py"
        ).read_text(encoding="utf-8")
        self.assertIn("batch contains duplicate offset or event ID", describe_processor)

    def test_no_secret_values_in_flow_or_parameter_template(self) -> None:
        text = json.dumps(self.flow) + (
            ROOT / "streaming/nifi/parameters/local.template.json"
        ).read_text(encoding="utf-8")
        self.assertNotIn("minioadmin123", text.lower())
        self.assertNotIn("secret-access-key", text.lower())
        self.assertIn("/run/secrets/minio_nifi_password", text)


if __name__ == "__main__":
    unittest.main()
