from __future__ import annotations

import ast
import json
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from fastavro import parse_schema, reader
from streaming.nifi.deploy_flow import connection_bends, expected_connection_names
from streaming.nifi.python.cdc_common import (
    SUPPORTED_NORMALIZED_TABLES,
    avro_container,
    intermediate_avro_container,
    load_output_schemas,
)

ROOT = Path(__file__).resolve().parents[1]


class NifiOptimizationTests(unittest.TestCase):
    def test_schedule_schema_loader_initializes_all_output_schemas_once(self) -> None:
        calls: list[tuple[str, str, str | None]] = []

        def fake_load_schema(
            directory: str, kind: str, table: str | None = None
        ) -> str:
            calls.append((directory, kind, table))
            return f"{kind}:{table or 'landing'}"

        with patch(
            "streaming.nifi.python.cdc_common.load_schema",
            side_effect=fake_load_schema,
        ):
            landing, normalized = load_output_schemas("/schemas")

        self.assertEqual("landing:landing", landing)
        self.assertEqual(set(SUPPORTED_NORMALIZED_TABLES), set(normalized))
        self.assertEqual(
            [
                ("/schemas", "landing", None),
                *[
                    ("/schemas", "normalized", table)
                    for table in SUPPORTED_NORMALIZED_TABLES
                ],
            ],
            calls,
        )

    def test_missing_normalized_schema_fails_during_schedule_initialization(
        self,
    ) -> None:
        def missing_products(
            _directory: str, kind: str, table: str | None = None
        ) -> object:
            if kind == "normalized" and table == "products":
                raise FileNotFoundError("products/v1.avsc")
            return object()

        with (
            patch(
                "streaming.nifi.python.cdc_common.load_schema",
                side_effect=missing_products,
            ),
            self.assertRaisesRegex(ValueError, "products"),
        ):
            load_output_schemas("/schemas")

    def test_build_processor_does_not_load_local_schemas_per_flowfile(self) -> None:
        source = (ROOT / "streaming/nifi/python/BuildCdcAvro.py").read_text(
            encoding="utf-8"
        )
        module = ast.parse(source)
        processor = next(
            node
            for node in module.body
            if isinstance(node, ast.ClassDef) and node.name == "BuildCdcAvro"
        )
        functions = {
            node.name: node
            for node in processor.body
            if isinstance(node, ast.FunctionDef)
        }
        transform_names = {
            node.id
            for node in ast.walk(functions["transform"])
            if isinstance(node, ast.Name)
        }
        scheduled_names = {
            node.id
            for node in ast.walk(functions["onScheduled"])
            if isinstance(node, ast.Name)
        }
        self.assertNotIn("load_schema", transform_names)
        self.assertNotIn("parse_schema", transform_names)
        self.assertNotIn("loads", transform_names)
        self.assertIn("load_output_schemas", scheduled_names)
        self.assertIn("landing_schema", ast.unparse(functions["transform"]))
        self.assertIn("normalized_schemas", ast.unparse(functions["transform"]))

    def test_intermediate_avro_uses_null_codec_and_final_helper_stays_deflated(
        self,
    ) -> None:
        schema = parse_schema(
            {
                "type": "record",
                "name": "OptimizationRecord",
                "fields": [{"name": "id", "type": "long"}],
            }
        )
        record = {"id": 7}

        intermediate = intermediate_avro_container(schema, record)
        intermediate_reader = reader(BytesIO(intermediate))
        self.assertEqual("null", intermediate_reader.metadata["avro.codec"])
        self.assertEqual([record], list(intermediate_reader))

        final = avro_container(schema, record)
        final_reader = reader(BytesIO(final))
        self.assertEqual("deflate", final_reader.metadata["avro.codec"])
        self.assertEqual([record], list(final_reader))

    def test_shared_final_avro_writer_remains_compressed(self) -> None:
        flow = json.loads(
            (ROOT / "streaming/nifi/flow/olist-cdc-v1.json").read_text(encoding="utf-8")
        )
        services = {item["name"]: item for item in flow["controller_services"]}
        self.assertEqual(
            "DEFLATE",
            services["avro-writer"]["properties"]["Compression Format"],
        )

    def test_deploy_fingerprint_includes_both_relationship_fanout_connections(
        self,
    ) -> None:
        flow = json.loads(
            (ROOT / "streaming/nifi/flow/olist-cdc-v1.json").read_text(encoding="utf-8")
        )
        names = expected_connection_names(flow)
        self.assertEqual(len(flow["connections"]), len(names))
        self.assertIn(
            "Route Tombstones [unmatched] to Build Landing Avro",
            names,
        )
        self.assertIn(
            "Route Tombstones [unmatched] to Build Normalized Avro",
            names,
        )

    def test_flow_separates_overlapping_tombstone_landing_connections(self) -> None:
        flow = json.loads(
            (ROOT / "streaming/nifi/flow/olist-cdc-v1.json").read_text(encoding="utf-8")
        )

        self.assertEqual(
            [{"x": 900, "y": 80}],
            connection_bends(
                flow, "Route Tombstones [tombstone] to Build Landing Avro"
            ),
        )


if __name__ == "__main__":
    unittest.main()
