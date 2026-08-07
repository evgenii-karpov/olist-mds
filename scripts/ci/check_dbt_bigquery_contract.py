"""Validate the credential-free contract of the dedicated BigQuery dbt project."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "dbt/olist_bigquery"
EXPECTED_GOLD_MODELS = {
    "dim_date",
    "dim_order_status",
    "dim_seller",
    "dim_customer_scd2",
    "dim_product_scd2",
    "fact_order_items",
    "mart_daily_revenue",
    "mart_monthly_arpu",
}
EXPECTED_BRIDGE_SOURCES = {
    "silver_customers_changes",
    "silver_orders_changes",
    "silver_order_items_changes",
    "silver_order_payments_changes",
    "silver_order_reviews_changes",
    "silver_products_changes",
    "silver_sellers_changes",
    "silver_product_category_translation_changes",
}


def _manifest() -> dict[str, Any]:
    return json.loads((PROJECT / "target/manifest.json").read_text(encoding="utf-8"))


def validate() -> dict[str, Any]:
    errors: list[str] = []
    project_sql = "\n".join(
        path.read_text(encoding="utf-8")
        for path in PROJECT.rglob("*.sql")
        if "target" not in path.parts
    ).lower()
    forbidden = (
        "updated_at - interval",
        "updated_at >=",
        "dbt/olist_clickhouse",
        "serving_cdc.",
        ".snapshots",
        ".files",
    )
    for token in forbidden:
        if token in project_sql:
            errors.append(f"forbidden token {token!r} is present in dbt SQL")

    manifest = _manifest()
    models = {
        node["name"]: node
        for unique_id, node in manifest.get("nodes", {}).items()
        if unique_id.startswith("model.olist_bigquery.")
    }
    gold_models = {
        name
        for name, node in models.items()
        if node.get("path", "").replace("\\", "/").startswith("gold/")
    }
    if gold_models != EXPECTED_GOLD_MODELS:
        errors.append(
            f"gold model mismatch: expected {sorted(EXPECTED_GOLD_MODELS)}, "
            f"got {sorted(gold_models)}"
        )
    for name in EXPECTED_GOLD_MODELS:
        node = models.get(name)
        if node is None:
            continue
        alias = node.get("alias")
        if alias != f"{name}__history":
            errors.append(f"{name} must materialize as {name}__history, got {alias}")
        if node.get("config", {}).get("materialized") != "incremental":
            errors.append(f"{name} is not incremental")

    sources = {
        node["name"]
        for unique_id, node in manifest.get("sources", {}).items()
        if unique_id.startswith("source.olist_bigquery.lakehouse_bridge.")
    }
    if not EXPECTED_BRIDGE_SOURCES.issubset(sources):
        errors.append(
            "bridge source mismatch: missing "
            f"{sorted(EXPECTED_BRIDGE_SOURCES - sources)}"
        )

    return {
        "status": "PASS" if not errors else "FAIL",
        "gold_model_count": len(gold_models),
        "bridge_source_count": len(sources),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = validate()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
