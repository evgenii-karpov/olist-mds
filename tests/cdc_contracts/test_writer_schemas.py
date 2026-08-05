from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from streaming.schemas.avro import schema_fingerprint_sha256
from streaming.schemas.contracts import (
    UnknownSchemaFingerprint,
    load_contracts,
    validate_contract_repository,
)
from streaming.schemas.generate_contracts import (
    ENTITIES,
    key_schema,
    value_schema,
    write_contracts,
)
from streaming.schemas.writer_schemas import (
    CAPTURE_COMMAND,
    CAPTURED,
    ENTITY_NAMES,
    SCHEMA_KINDS,
    WriterSchemaContractError,
    load_writer_schema_repository,
    validate_writer_schema_repository,
)


def write_synthetic_captured_repository(root: Path) -> None:
    """Write test-only runtime evidence; these schemas are never checked in."""

    by_name = {entity.name: entity for entity in ENTITIES}
    entries: list[dict[str, object]] = []
    schema_id = 1000
    for entity_name in ENTITY_NAMES:
        topic = f"olist_cdc.olist_oltp.{entity_name}"
        entry: dict[str, object] = {"entity": entity_name}
        for kind in SCHEMA_KINDS:
            entity = by_name[entity_name]
            schema = key_schema(entity) if kind == "key" else value_schema(entity)
            relative_path = f"{entity_name}/{kind}/schema-{schema_id}.avsc"
            path = root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(schema), encoding="utf-8")
            entry[kind] = {
                "state": CAPTURED,
                "schemas": [
                    {
                        "path": relative_path,
                        "sha256": schema_fingerprint_sha256(schema),
                        "provenance": {
                            "registry_url": (
                                "http://apicurio-registry:8080/apis/registry/v2"
                            ),
                            "registry_group": "olist_cdc",
                            "artifact_id": f"{topic}-{kind}",
                            "artifact_version": "1",
                            "schema_id": schema_id,
                            "captured_at_utc": "2026-08-01T00:00:00Z",
                            "connector_name": "olist-mysql-cdc",
                            "topic": topic,
                        },
                    }
                ],
            }
            schema_id += 1
        entries.append(entry)
    manifest = {
        "manifest_version": 1,
        "capture_state": CAPTURED,
        "capture_command": CAPTURE_COMMAND,
        "entities": entries,
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


class CapturedWriterSchemaTests(unittest.TestCase):
    def test_checked_in_source_bytes_are_the_fingerprint_authority(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "writers"
            write_synthetic_captured_repository(root)
            self.assertEqual(
                [], validate_writer_schema_repository(root, require_captured=True)
            )
            repository = load_writer_schema_repository(root, require_captured=True)
            self.assertTrue(repository.capture_complete)
            self.assertEqual(
                16,
                sum(len(records) for records in repository.records.values()),
            )

            record = repository.schemas("customers", "key")[0]
            schema = json.loads(record.path.read_text(encoding="utf-8"))
            schema["fields"].append(
                {"name": "runtime_extra", "type": ["null", "string"], "default": None}
            )
            record.path.write_text(json.dumps(schema), encoding="utf-8")
            errors = validate_writer_schema_repository(root, require_captured=True)
            self.assertTrue(any("SHA-256 is stale" in error for error in errors))

    def test_contract_allowlist_is_derived_from_captured_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            writer_root = base / "writers"
            contract_root = base / "contracts"
            write_synthetic_captured_repository(writer_root)
            write_contracts(contract_root, writer_root=writer_root)

            self.assertEqual(
                [],
                validate_contract_repository(
                    contract_root,
                    writer_root=writer_root,
                ),
            )
            contracts = load_contracts(
                contract_root,
                writer_root=writer_root,
                require_captured_writers=True,
            )
            for versioned in contracts.values():
                self.assertEqual(
                    "captured",
                    versioned.document["avro"]["writer_schema_capture_state"],
                )
                for kind in ("key", "value"):
                    entries = versioned.document["avro"][f"allowed_{kind}_fingerprints"]
                    self.assertEqual(1, len(entries))
                    versioned.assert_fingerprint_allowed(kind, entries[0]["sha256"])
                with self.assertRaises(UnknownSchemaFingerprint):
                    versioned.assert_fingerprint_allowed("value", "0" * 64)

            customer_path = contract_root / "customers" / "v1.json"
            customer = json.loads(customer_path.read_text(encoding="utf-8"))
            customer["avro"]["allowed_key_fingerprints"][0]["source"] = (
                "captured-writer-schemas/customers/key/not-the-source.avsc"
            )
            customer_path.write_text(
                json.dumps(customer, indent=2) + "\n", encoding="utf-8"
            )
            errors = validate_contract_repository(
                contract_root,
                writer_root=writer_root,
            )
            self.assertTrue(
                any("provenance/source is stale" in error for error in errors)
            )

    def test_manifest_rejects_incomplete_captured_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "writers"
            write_synthetic_captured_repository(root)
            manifest_path = root / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["entities"][0]["key"] = {
                "state": "pending_runtime_capture",
                "schemas": [],
            }
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(
                WriterSchemaContractError, "capture_state must be"
            ):
                load_writer_schema_repository(root)

    def test_partial_capture_cannot_activate_any_contract_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            writer_root = base / "writers"
            contract_root = base / "contracts"
            write_synthetic_captured_repository(writer_root)
            manifest_path = writer_root / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["capture_state"] = "pending_runtime_capture"
            manifest["entities"][0]["key"] = {
                "state": "pending_runtime_capture",
                "schemas": [],
            }
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            repository = load_writer_schema_repository(writer_root)
            self.assertFalse(repository.capture_complete)
            write_contracts(contract_root, writer_root=writer_root)
            for versioned in load_contracts(
                contract_root, writer_root=writer_root
            ).values():
                avro = versioned.document["avro"]
                self.assertEqual(
                    "pending_runtime_capture", avro["writer_schema_capture_state"]
                )
                self.assertEqual([], avro["allowed_key_fingerprints"])
                self.assertEqual([], avro["allowed_value_fingerprints"])


if __name__ == "__main__":
    unittest.main()
