from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OltpSeedContractTests(unittest.TestCase):
    def test_order_schema_accepts_full_olist_carrier_timestamp_anomalies(self) -> None:
        schema = (ROOT / "infra/oltp/initdb/020_create_oltp_schema.sql").read_text(
            encoding="utf-8"
        )

        self.assertIn("ck_orders_approval_after_purchase", schema)
        self.assertIn("ck_orders_customer_after_purchase", schema)
        self.assertNotIn("ck_orders_carrier_after_purchase", schema)


if __name__ == "__main__":
    unittest.main()
