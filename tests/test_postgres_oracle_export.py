from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import yaml
from scripts.parity.export_postgres_oracle import (
    NULL_VALUE,
    ColumnType,
    aggregate_hash,
    canonical_row,
    canonical_value,
    load_contract,
    row_hash,
)


class PostgresOracleExportTests(unittest.TestCase):
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

    def test_repository_contracts_declare_fifteen_oracle_relations(self) -> None:
        batch = load_contract(Path("scripts/parity/postgres_oracle_relations.json"))
        stage5 = load_contract(
            Path("scripts/parity/postgres_stage5_oracle_relations.json")
        )
        self.assertEqual("olist_small", batch["dataset"])
        self.assertEqual("synthetic_stage5_initial_parity", stage5["dataset"])
        self.assertEqual(15, len(batch["relations"]) + len(stage5["relations"]))

    def test_every_terminal_model_has_unit_test_coverage(self) -> None:
        inventory = json.loads(
            Path("tests/fixtures/postgresql_oracle/dbt_inventory.json").read_text(
                encoding="utf-8"
            )
        )
        tested_models: set[str] = set()
        for path in Path("dbt/olist_analytics/models").rglob("*.yml"):
            payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            tested_models.update(
                test["model"] for test in payload.get("unit_tests", [])
            )
        self.assertEqual(
            set(inventory["terminal_models"]),
            set(inventory["terminal_models"]) & tested_models,
        )


if __name__ == "__main__":
    unittest.main()
