from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

from scripts.parity.canonical_manifest import (
    NULL_VALUE,
    ColumnType,
    aggregate_hash,
    canonical_row,
    canonical_value,
    load_contract,
    row_hash,
)
from scripts.parity.compare_manifests import compare_manifests


class CanonicalManifestTests(unittest.TestCase):
    def test_canonical_values_preserve_semantic_distinctions(self) -> None:
        self.assertEqual(NULL_VALUE, canonical_value(None, ColumnType("string")))
        self.assertEqual("", canonical_value("", ColumnType("string")))
        self.assertEqual(
            "1.20", canonical_value(Decimal("1.2"), ColumnType("decimal", 2))
        )
        self.assertEqual(
            "2026-07-23", canonical_value(date(2026, 7, 23), ColumnType("date"))
        )
        self.assertEqual(
            "2026-07-23T08:09:10.123456Z",
            canonical_value(
                datetime(2026, 7, 23, 8, 9, 10, 123456, tzinfo=UTC),
                ColumnType("timestamp"),
            ),
        )

    def test_row_and_aggregate_hashes_are_order_independent(self) -> None:
        types = {"id": ColumnType("string"), "amount": ColumnType("decimal", 2)}
        first = {"amount": Decimal("2"), "id": "a"}
        reordered = {"id": "a", "amount": Decimal("2.00")}
        self.assertEqual(canonical_row(first, types), canonical_row(reordered, types))
        self.assertEqual(row_hash(first, types), row_hash(reordered, types))
        self.assertEqual(aggregate_hash(["b", "a"]), aggregate_hash(["a", "b"]))

    def test_contract_rejects_unsafe_and_duplicate_relations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "contract.json"
            path.write_text(
                json.dumps(
                    {
                        "format_version": 1,
                        "dataset": "fixture",
                        "relations": [
                            {"schema": "core", "name": "orders;drop", "grain": ["id"]}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unsafe SQL identifier"):
                load_contract(path)

    def test_repository_contract_declares_target_canonical_relations(self) -> None:
        batch = load_contract(Path("scripts/parity/canonical_batch_relations.json"))
        self.assertEqual("olist_small", batch["dataset"])
        self.assertEqual(9, len(batch["relations"]))

    def test_f0_oracle_and_metadata_are_immutable_target_inputs(self) -> None:
        oracle = Path("tests/fixtures/final_parity/main-1400d08.json")
        metadata = Path("tests/fixtures/final_parity/main-1400d08.metadata.json")
        self.assertTrue(oracle.is_file())
        self.assertTrue(metadata.is_file())

        metadata_payload = json.loads(metadata.read_text(encoding="utf-8"))
        self.assertEqual(
            "1400d08345ad81a0121f0ee85ee9ae81cd575a73",
            metadata_payload["baseline_commit"],
        )
        self.assertEqual(11, len(metadata_payload["relation_summary"]))

    def test_final_parity_contract_maps_every_relation_to_candidate_columns(
        self,
    ) -> None:
        contract = load_contract(Path("scripts/parity/final_parity_contract.json"))
        self.assertEqual(11, len(contract["relations"]))
        for relation in contract["relations"]:
            candidate = relation["candidate"]
            self.assertNotEqual(
                (relation["schema"], relation["name"]),
                (candidate["schema"], candidate["name"]),
            )
            self.assertTrue(candidate["columns"])

    def test_final_parity_comparator_exposes_bounded_relation_diagnostics(self) -> None:
        oracle = json.loads(
            Path("tests/fixtures/final_parity/main-1400d08.json").read_text(
                encoding="utf-8"
            )
        )
        candidate = json.loads(json.dumps(oracle))
        candidate["relations"][0]["rows"][0]["hash"] = "0" * 64
        result = compare_manifests(oracle, candidate)
        self.assertEqual("FAIL", result["status"])
        self.assertEqual(1, result["column_mismatch_count"])
        customers = next(
            relation
            for relation in result["relations"]
            if relation["relation"] == "public.customers"
        )
        self.assertEqual("FAIL", customers["status"])
        self.assertEqual(1, customers["column_mismatch_count"])


if __name__ == "__main__":
    unittest.main()
