from __future__ import annotations

import csv
import hashlib
import unittest
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from scripts.simulation.seeding import (
    SEED_BATCH_SIZE,
    SEED_SPECS,
    batches,
    convert_row,
    open_source,
    seed_archive,
    upsert_statement,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "olist_small" / "olist_small.zip"
EXPECTED_COUNTS = {
    "customers": 8,
    "orders": 12,
    "order_items": 16,
    "order_payments": 14,
    "order_reviews": 12,
    "products": 8,
    "sellers": 4,
    "product_category_translation": 5,
    "geolocation": 6,
}


class FixtureAndSeedSpecTests(unittest.TestCase):
    def test_fixture_digest_and_exact_counts(self) -> None:
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "5cf2ff7a104cae75d8a56cf8c6e00959894154a8d55aed2ddf0e3fa133a13976",
        )
        observed: dict[str, int] = {}
        for spec in SEED_SPECS:
            with open_source(FIXTURE, spec.file_name) as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(tuple(reader.fieldnames or ()), spec.columns)
                observed[spec.entity_name] = sum(1 for _ in reader)
        self.assertEqual(observed, EXPECTED_COUNTS)

    def test_fk_safe_seed_order_is_fixed(self) -> None:
        self.assertEqual(
            [spec.entity_name for spec in SEED_SPECS],
            [
                "product_category_translation",
                "customers",
                "sellers",
                "products",
                "orders",
                "order_items",
                "order_payments",
                "order_reviews",
                "geolocation",
            ],
        )

    def test_batch_size_is_exactly_five_thousand(self) -> None:
        self.assertEqual(SEED_BATCH_SIZE, 5_000)
        rows = ((value,) for value in range(10_001))
        self.assertEqual([len(batch) for batch in batches(rows)], [5_000, 5_000, 1])

    def test_type_conversion_keeps_null_decimal_and_microsecond_time(self) -> None:
        spec = next(item for item in SEED_SPECS if item.entity_name == "order_items")
        row = {
            "order_id": "order-1",
            "order_item_id": "2",
            "product_id": "product-1",
            "seller_id": "seller-1",
            "shipping_limit_date": "2026-07-31 12:13:14.123456",
            "price": "10.20",
            "freight_value": "0.30",
        }
        converted = convert_row(spec, row)
        self.assertEqual(converted[1], 2)
        self.assertEqual(converted[4], datetime(2026, 7, 31, 12, 13, 14, 123456))
        self.assertEqual(converted[5:], (Decimal("10.20"), Decimal("0.30")))

    def test_upsert_is_mysql_qualified_and_preserves_composite_key_columns(
        self,
    ) -> None:
        spec = next(item for item in SEED_SPECS if item.entity_name == "order_items")
        statement = upsert_statement(spec)
        self.assertIn("INSERT INTO olist_oltp.order_items", statement)
        self.assertIn("AS new ON DUPLICATE KEY UPDATE", statement)
        self.assertIn("ON DUPLICATE KEY UPDATE", statement)
        self.assertNotIn("order_id = new.order_id", statement)
        self.assertNotIn("order_item_id = new.order_item_id", statement)
        self.assertNotIn("ON CONFLICT", statement)


class RecordingCursor:
    def __init__(self) -> None:
        self.statements: list[str] = []
        self._rows: list[tuple[int]] = []
        self._seed_tokens: dict[tuple[str, str], list[int]] = {}

    def execute(self, statement: str, parameters: Any = None) -> None:
        self.statements.append(statement)
        normalized = " ".join(statement.lower().split())
        if "select source_row_number" in normalized:
            identity, token = parameters
            self._rows = [
                (number,) for number in self._seed_tokens.get((identity, token), [])
            ]

    def executemany(self, statement: str, values: list[tuple[Any, ...]]) -> None:
        self.statements.append(statement)
        if "olist_simulator.seed_rows" in statement:
            for identity, row_number, token, _loaded_at in values:
                self._seed_tokens.setdefault((identity, token), []).append(row_number)

    def fetchall(self) -> list[tuple[int]]:
        return self._rows


class RecordingRepository:
    def __init__(self) -> None:
        self.cursor = RecordingCursor()
        self.started: list[tuple[str, str]] = []
        self.finished: list[tuple[str, str]] = []
        self.transactions = 0

    def start_run(self, run_id: str, command: str, config: Any) -> None:
        del config
        self.started.append((run_id, command))

    @contextmanager
    def transaction(self):  # type: ignore[no-untyped-def]
        self.transactions += 1
        yield self.cursor

    def finish_run(self, run_id: str, state: str, finished_at: datetime) -> None:
        del finished_at
        self.finished.append((run_id, state))


class SeedTransactionContractTests(unittest.TestCase):
    def test_small_fixture_uses_one_transaction_per_entity(self) -> None:
        repository = RecordingRepository()
        counts = seed_archive(
            repository,
            FIXTURE,
            random_seed=101,
            run_id="seed-small",
            logical_time=datetime(2026, 1, 1),
        )
        self.assertEqual(counts, EXPECTED_COUNTS)
        self.assertEqual(repository.started, [("seed-small", "seed")])
        self.assertEqual(repository.transactions, len(SEED_SPECS) + 1)
        self.assertFalse(repository.finished)
        statements = [statement.lower() for statement in repository.cursor.statements]
        self.assertTrue(
            all(
                "olist_oltp." in statement or "olist_simulator." in statement
                for statement in statements
            )
        )


if __name__ == "__main__":
    unittest.main()
