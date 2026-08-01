from __future__ import annotations

import json
import unittest
from email.message import Message
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError

from streaming.schemas.avro import (
    ConfluentFramingError,
    build_confluent_frame,
    canonical_schema_json,
    inspect_confluent_frame,
    parse_confluent_frame,
    schema_fingerprint_sha256,
)
from streaming.schemas.registry import (
    ApicurioCCompatClient,
    RecursiveSchemaResolver,
    RegistryContractViolation,
    RegistrySchemaDocument,
    RegistryUnavailable,
    SchemaIdConsistencyGuard,
    SchemaReference,
)


class ConfluentFramingTests(unittest.TestCase):
    def test_round_trip_uses_unsigned_big_endian_schema_id(self) -> None:
        framed = build_confluent_frame(0x01020304, b"avro")
        self.assertEqual(b"\x00\x01\x02\x03\x04avro", framed)
        parsed = parse_confluent_frame(framed)
        self.assertEqual(0x01020304, parsed.schema_id)
        self.assertEqual(b"avro", parsed.payload)

    def test_invalid_short_magic_and_zero_id_have_stable_codes(self) -> None:
        cases = (
            (b"\x00\x01", "frame_too_short"),
            (b"\x01\x00\x00\x00\x01", "invalid_magic_byte"),
            (b"\x00\x00\x00\x00\x00", "invalid_schema_id"),
        )
        for payload, code in cases:
            with (
                self.subTest(code=code),
                self.assertRaises(ConfluentFramingError) as raised,
            ):
                parse_confluent_frame(payload)
            self.assertEqual(code, raised.exception.code)

    def test_inspection_preserves_tombstone_and_malformed_distinction(self) -> None:
        tombstone = inspect_confluent_frame(None)
        self.assertTrue(tombstone.is_tombstone)
        self.assertTrue(tombstone.framing_valid)
        self.assertIsNone(tombstone.schema_id)

        malformed = inspect_confluent_frame(b"bad")
        self.assertFalse(malformed.is_tombstone)
        self.assertFalse(malformed.framing_valid)
        self.assertEqual("frame_too_short", malformed.error_code)

        valid = inspect_confluent_frame(build_confluent_frame(42, b"payload"))
        self.assertTrue(valid.framing_valid)
        self.assertEqual(42, valid.schema_id)
        self.assertEqual(b"payload", valid.payload)


class FingerprintTests(unittest.TestCase):
    def test_canonical_fingerprint_ignores_json_key_order_and_whitespace(self) -> None:
        left = {
            "type": "record",
            "name": "R",
            "fields": [{"name": "id", "type": "string"}],
        }
        right = json.loads(
            '{ "fields" : [ { "type":"string", "name":"id" } ],'
            ' "name":"R", "type":"record" }'
        )
        self.assertEqual(canonical_schema_json(left), canonical_schema_json(right))
        self.assertEqual(
            schema_fingerprint_sha256(left), schema_fingerprint_sha256(right)
        )

    def test_logical_type_is_part_of_durable_identity(self) -> None:
        plain = {"type": "long"}
        timestamp = {"type": "long", "logicalType": "timestamp-micros"}
        self.assertNotEqual(
            schema_fingerprint_sha256(plain),
            schema_fingerprint_sha256(timestamp),
        )


class FakeRegistryReader:
    def __init__(self, root: RegistrySchemaDocument) -> None:
        self.root = root
        self.documents: dict[tuple[str, str], RegistrySchemaDocument] = {}
        self.calls: list[tuple[str, str]] = []

    def schema_by_id(self, schema_id: int) -> RegistrySchemaDocument:
        if schema_id != 42:
            raise AssertionError(schema_id)
        return self.root

    def schema_by_subject_version(
        self, subject: str, version: str
    ) -> RegistrySchemaDocument:
        self.calls.append((subject, version))
        return self.documents[(subject, version)]


class RecursiveReferenceTests(unittest.TestCase):
    def make_reader(self) -> FakeRegistryReader:
        root = RegistrySchemaDocument(
            schema={
                "type": "record",
                "name": "Envelope",
                "namespace": "io.test",
                "fields": [{"name": "after", "type": "io.test.Row"}],
            },
            references=(SchemaReference("io.test.Row", "row-value", "2"),),
        )
        reader = FakeRegistryReader(root)
        reader.documents[("row-value", "2")] = RegistrySchemaDocument(
            schema={
                "type": "record",
                "name": "Row",
                "namespace": "io.test",
                "fields": [{"name": "address", "type": "io.test.Address"}],
            },
            references=(SchemaReference("io.test.Address", "address-value", "1"),),
        )
        reader.documents[("address-value", "1")] = RegistrySchemaDocument(
            schema={
                "type": "record",
                "name": "Address",
                "namespace": "io.test",
                "fields": [{"name": "city", "type": "string"}],
            },
            references=(),
        )
        return reader

    def test_recursive_references_become_one_spark_schema(self) -> None:
        reader = self.make_reader()
        resolved = RecursiveSchemaResolver(reader).resolve(42)
        row = resolved.self_contained_schema["fields"][0]["type"]
        address = row["fields"][0]["type"]
        self.assertEqual("Row", row["name"])
        self.assertEqual("Address", address["name"])
        self.assertEqual(
            [("row-value", "2"), ("address-value", "1")],
            reader.calls,
        )
        self.assertEqual(
            schema_fingerprint_sha256(resolved.self_contained_schema),
            resolved.fingerprint_sha256,
        )
        archive = resolved.archive_row(
            subject="topic-value",
            registry_version="3",
            first_seen_at="2026-08-01T00:00:00Z",
            last_verified_at="2026-08-01T00:00:00Z",
        )
        self.assertEqual(42, archive["schema_id"])
        self.assertEqual(2, len(json.loads(archive["references_json"])))
        self.assertIn("Address", archive["spark_self_contained_schema_json"])

    def test_external_reference_cycle_is_a_contract_violation(self) -> None:
        root = RegistrySchemaDocument(
            schema={"type": "record", "name": "Root", "fields": []},
            references=(SchemaReference("A", "a", "1"),),
        )
        reader = FakeRegistryReader(root)
        reader.documents[("a", "1")] = RegistrySchemaDocument(
            schema={"type": "record", "name": "A", "fields": []},
            references=(SchemaReference("B", "b", "1"),),
        )
        reader.documents[("b", "1")] = RegistrySchemaDocument(
            schema={"type": "record", "name": "B", "fields": []},
            references=(SchemaReference("A", "a", "1"),),
        )
        with self.assertRaisesRegex(RegistryContractViolation, "cyclic"):
            RecursiveSchemaResolver(reader).resolve(42)

    def test_one_numeric_id_cannot_change_fingerprint(self) -> None:
        guard = SchemaIdConsistencyGuard()
        guard.observe(42, "a" * 64)
        guard.observe(42, "a" * 64)
        with self.assertRaises(RegistryContractViolation):
            guard.observe(42, "b" * 64)


class RegistryFailureClassificationTests(unittest.TestCase):
    def test_missing_schema_is_contract_violation(self) -> None:
        error = HTTPError(
            "http://registry/schemas/ids/42",
            404,
            "not found",
            Message(),
            BytesIO(b'{"error_code":40403,"message":"schema not found"}'),
        )
        self.addCleanup(error.close)
        with (
            patch("streaming.schemas.registry.urlopen", side_effect=error),
            self.assertRaises(RegistryContractViolation),
        ):
            ApicurioCCompatClient("http://registry").schema_by_id(42)

    def test_registry_server_failure_is_transient(self) -> None:
        error = HTTPError(
            "http://registry/schemas/ids/42",
            503,
            "unavailable",
            Message(),
            BytesIO(b"unavailable"),
        )
        self.addCleanup(error.close)
        with (
            patch("streaming.schemas.registry.urlopen", side_effect=error),
            self.assertRaises(RegistryUnavailable),
        ):
            ApicurioCCompatClient("http://registry").schema_by_id(42)


if __name__ == "__main__":
    unittest.main()
