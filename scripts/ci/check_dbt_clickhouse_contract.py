"""Validate the compiled target dbt-clickhouse project contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "dbt/olist_clickhouse"
EXPECTED_GOLD_MODELS = {
    "dim_customer_scd2",
    "dim_date",
    "dim_order_status",
    "dim_product_scd2",
    "dim_seller",
    "fact_order_items",
    "mart_daily_revenue",
    "mart_monthly_arpu",
}
EXPECTED_SOURCES = {"serving_cdc", "serving_control"}


def _manifest() -> dict[str, Any]:
    return json.loads((PROJECT / "target/manifest.json").read_text(encoding="utf-8"))


def validate() -> dict[str, Any]:
    manifest = _manifest()
    errors: list[str] = []
    if manifest.get("metadata", {}).get("project_name") != "olist_clickhouse":
        errors.append("compiled project is not olist_clickhouse")

    models = {
        node["name"]: node
        for unique_id, node in manifest.get("nodes", {}).items()
        if unique_id.startswith("model.olist_clickhouse.")
    }
    missing_models = EXPECTED_GOLD_MODELS - set(models)
    if missing_models:
        errors.append(f"missing required gold models: {sorted(missing_models)}")
    for name, node in models.items():
        path = str(node.get("original_file_path", "")).replace("\\", "/")
        if not path.startswith("models/"):
            errors.append(f"model outside target project path: {name} ({path})")

    sources = {
        node["source_name"]
        for unique_id, node in manifest.get("sources", {}).items()
        if unique_id.startswith("source.olist_clickhouse.")
    }
    if sources != EXPECTED_SOURCES:
        errors.append(
            f"source contract mismatch: expected {sorted(EXPECTED_SOURCES)}, "
            f"got {sorted(sources)}"
        )

    selectors = yaml.safe_load((PROJECT / "selectors.yml").read_text(encoding="utf-8"))
    selector_names = {
        selector.get("name") for selector in selectors.get("selectors", [])
    }
    if "serving_candidate" not in selector_names:
        errors.append("serving_candidate selector is missing")

    for path in PROJECT.rglob("*"):
        if not path.is_file() or path.name in {"profiles.yml", ".user.yml"}:
            continue
        if path.suffix.lower() not in {".sql", ".yml", ".yaml"}:
            continue
        source = path.read_text(encoding="utf-8").lower()
        for token in ("dbt/olist_analytics", "redshift", "nifi"):
            if token in source:
                errors.append(f"legacy token {token!r} in {path.relative_to(ROOT)}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "model_count": len(models),
        "source_names": sorted(sources),
        "selector": "serving_candidate",
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
