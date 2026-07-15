from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ci.check_avro_schema_compatibility import check_schema_directory


def record(fields: list[dict[str, object]]) -> dict[str, object]:
    return {
        "type": "record",
        "name": "Order",
        "namespace": "io.olist.cdc",
        "fields": fields,
    }


class AvroSchemaCompatibilityTests(unittest.TestCase):
    def write_schema(
        self, root: Path, subject: str, version: int, schema: dict[str, object]
    ) -> None:
        directory = root / subject
        directory.mkdir(parents=True, exist_ok=True)
        (directory / f"v{version}.avsc").write_text(
            json.dumps(schema), encoding="utf-8"
        )

    def test_nullable_field_with_default_is_backward_transitive(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self.write_schema(
                root, "orders-value", 1, record([{"name": "id", "type": "string"}])
            )
            self.write_schema(
                root,
                "orders-value",
                2,
                record(
                    [
                        {"name": "id", "type": "string"},
                        {"name": "note", "type": ["null", "string"], "default": None},
                    ]
                ),
            )
            self.write_schema(
                root,
                "orders-value",
                3,
                record(
                    [
                        {"name": "id", "type": "string"},
                        {"name": "note", "type": ["null", "string"], "default": None},
                        {"name": "attempt", "type": "int", "default": 0},
                    ]
                ),
            )

            self.assertEqual([], check_schema_directory(root))

    def test_removing_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self.write_schema(
                root,
                "orders-value",
                1,
                record(
                    [
                        {"name": "id", "type": "string"},
                        {"name": "status", "type": "string"},
                    ]
                ),
            )
            self.write_schema(
                root, "orders-value", 2, record([{"name": "id", "type": "string"}])
            )

            errors = check_schema_directory(root)

            self.assertTrue(any("removed or renamed" in error for error in errors))

    def test_new_field_without_default_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self.write_schema(
                root, "orders-value", 1, record([{"name": "id", "type": "string"}])
            )
            self.write_schema(
                root,
                "orders-value",
                2,
                record(
                    [
                        {"name": "id", "type": "string"},
                        {"name": "status", "type": "string"},
                    ]
                ),
            )

            errors = check_schema_directory(root)

            self.assertTrue(any("has no default" in error for error in errors))

    def test_nested_record_change_is_rejected_conservatively(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            address = {
                "type": "record",
                "name": "Address",
                "fields": [{"name": "city", "type": "string"}],
            }
            changed_address = {
                "type": "record",
                "name": "Address",
                "fields": [
                    {"name": "city", "type": "string"},
                    {"name": "state", "type": "string", "default": "SP"},
                ],
            }
            self.write_schema(
                root,
                "customers-value",
                1,
                record([{"name": "address", "type": address}]),
            )
            self.write_schema(
                root,
                "customers-value",
                2,
                record([{"name": "address", "type": changed_address}]),
            )

            errors = check_schema_directory(root)

            self.assertTrue(any("changed incompatibly" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
