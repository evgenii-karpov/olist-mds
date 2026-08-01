"""Stable streaming query names and physically isolated checkpoint paths."""

from __future__ import annotations

import re

BRONZE_QUERY = "kafka_to_bronze"
SILVER_QUERIES = (
    "capture_avro_schemas",
    "normalize_mysql_transactions",
    "normalize_customers",
    "normalize_orders",
    "normalize_order_items",
    "normalize_order_payments",
    "normalize_order_reviews",
    "normalize_products",
    "normalize_sellers",
    "normalize_product_category_translation",
)
ALL_CONTINUOUS_QUERIES = (BRONZE_QUERY, *SILVER_QUERIES)

_QUERY_NAME = re.compile(r"^[a-z][a-z0-9_]*$")


def checkpoint_path(
    query_name: str,
    contract_version: int,
    root: str = "s3a://olist-checkpoints",
) -> str:
    if query_name not in ALL_CONTINUOUS_QUERIES or not _QUERY_NAME.fullmatch(
        query_name
    ):
        raise ValueError(f"unknown continuous query name: {query_name}")
    if isinstance(contract_version, bool) or contract_version < 1:
        raise ValueError("contract_version must be a positive integer")
    if root.rstrip("/") != "s3a://olist-checkpoints":
        raise ValueError(
            "checkpoints must remain in the isolated olist-checkpoints bucket"
        )
    return f"s3a://olist-checkpoints/{query_name}/contract-v{contract_version}/"
