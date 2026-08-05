from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_COUNTS_PATH = ROOT / "tests" / "local_cdc_acceptance" / "expected_counts.json"


class ExpectedCountsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(
            EXPECTED_COUNTS_PATH.exists(),
            f"Expected-counts JSON file missing: {EXPECTED_COUNTS_PATH}",
        )
        self.expected_counts = json.loads(
            EXPECTED_COUNTS_PATH.read_text(encoding="utf-8")
        )

    def test_initial_snapshot_counts(self) -> None:
        init = self.expected_counts["initial_snapshot"]
        self.assertEqual(init["total_business"], 79)
        self.assertEqual(init["geolocation"], 6)
        self.assertEqual(init["total_applied_changes"], 79)
        self.assertEqual(init["total_visible_current"], 79)
        self.assertEqual(init["rejected"], 0)
        self.assertEqual(init["schema_violations"], 0)

        # Entity count sum
        entities = [
            "customers",
            "orders",
            "order_items",
            "order_payments",
            "order_reviews",
            "products",
            "sellers",
            "product_category_translation",
        ]
        sum_entities = sum(init[e] for e in entities)
        self.assertEqual(sum_entities, 79)

    def test_crud_delta_breakdown(self) -> None:
        crud = self.expected_counts["crud_delta"]
        self.assertEqual(crud["insert_events"], 7)
        self.assertEqual(crud["update_events"], 2)
        self.assertEqual(crud["delete_events"], 1)
        self.assertEqual(crud["total_crud_events"], 10)

    def test_post_crud_totals(self) -> None:
        post_crud = self.expected_counts["post_crud"]
        self.assertEqual(post_crud["total_applied_changes"], 89)
        self.assertEqual(post_crud["total_visible_current"], 85)
        self.assertEqual(post_crud["total_physical_current"], 86)
        self.assertEqual(post_crud["total_deleted_current"], 1)

    def test_post_schema_totals(self) -> None:
        post_schema = self.expected_counts["post_schema"]
        self.assertEqual(post_schema["total_applied_changes"], 90)
        self.assertEqual(post_schema["total_visible_current"], 85)


if __name__ == "__main__":
    unittest.main()
