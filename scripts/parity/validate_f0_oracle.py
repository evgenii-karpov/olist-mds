"""Independent validator for Stage F0 baseline oracle and metadata artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

EXPECTED_BASELINE_SHA = "1400d08345ad81a0121f0ee85ee9ae81cd575a73"
EXPECTED_FIXTURE_SHA256 = (
    "5cf2ff7a104cae75d8a56cf8c6e00959894154a8d55aed2ddf0e3fa133a13976"
)
EXPECTED_RELATIONS = {
    "public.customers",
    "public.orders",
    "public.order_items",
    "public.order_payments",
    "public.order_reviews",
    "public.products",
    "public.sellers",
    "public.product_category_translation",
    "core.fact_order_items",
    "marts.mart_daily_revenue",
    "marts.mart_monthly_arpu",
}

DISALLOWED_PATTERNS = [
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"\/Users\/", re.IGNORECASE),
    re.compile(r"C:\\Users\\", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
]


def validate_f0(oracle_path: Path, metadata_path: Path) -> list[str]:
    errors: list[str] = []

    if not oracle_path.exists():
        return [f"Oracle file not found: {oracle_path}"]
    if not metadata_path.exists():
        return [f"Metadata file not found: {metadata_path}"]

    oracle_bytes = oracle_path.read_bytes()
    computed_oracle_sha = hashlib.sha256(oracle_bytes).hexdigest()

    try:
        oracle = json.loads(oracle_bytes.decode("utf-8"))
    except Exception as exc:
        return [f"Failed to parse oracle JSON: {exc}"]

    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"Failed to parse metadata JSON: {exc}"]

    # 1. Format and Dataset
    if oracle.get("format_version") != 1:
        errors.append(
            f"Oracle format_version must be 1, got {oracle.get('format_version')}"
        )
    if oracle.get("dataset") != "olist_small":
        errors.append(
            f"Oracle dataset must be 'olist_small', got {oracle.get('dataset')}"
        )

    # 2. Metadata Provenance
    if metadata.get("baseline_commit") != EXPECTED_BASELINE_SHA:
        errors.append(
            f"Metadata baseline_commit mismatch: expected {EXPECTED_BASELINE_SHA}, got {metadata.get('baseline_commit')}"
        )
    if metadata.get("fixture_sha256") != EXPECTED_FIXTURE_SHA256:
        errors.append(
            f"Metadata fixture_sha256 mismatch: expected {EXPECTED_FIXTURE_SHA256}, got {metadata.get('fixture_sha256')}"
        )
    if metadata.get("oracle_sha256") != computed_oracle_sha:
        errors.append(
            f"Metadata oracle_sha256 mismatch: metadata claims {metadata.get('oracle_sha256')}, actual computed is {computed_oracle_sha}"
        )
    if metadata.get("status") != "PASS":
        errors.append(f"Metadata status must be 'PASS', got {metadata.get('status')}")

    # 3. Relations Coverage
    relations = oracle.get("relations", [])
    found_relation_names = {rel["name"] for rel in relations}

    missing_relations = EXPECTED_RELATIONS - found_relation_names
    if missing_relations:
        errors.append(
            f"Missing expected relations in oracle: {sorted(missing_relations)}"
        )
    extra_relations = found_relation_names - EXPECTED_RELATIONS
    if extra_relations:
        errors.append(
            f"Unexpected extra relations in oracle: {sorted(extra_relations)}"
        )

    # 4. Relation Structure & Grains
    for rel in relations:
        name = rel.get("name")
        row_count = rel.get("row_count", 0)
        dup_count = rel.get("duplicate_grain_count", -1)
        agg_hash = rel.get("aggregate_hash", "")
        rows = rel.get("rows", [])
        grain_keys = rel.get("grain_keys", [])

        if row_count <= 0:
            errors.append(
                f"Relation {name} has zero or negative row count: {row_count}"
            )
        if dup_count != 0:
            errors.append(
                f"Relation {name} has non-zero duplicate grain count: {dup_count}"
            )
        if not agg_hash or len(agg_hash) != 64:
            errors.append(f"Relation {name} has invalid aggregate hash: {agg_hash}")
        if len(rows) != row_count:
            errors.append(
                f"Relation {name} rows length ({len(rows)}) does not match row_count ({row_count})"
            )
        if len(grain_keys) != row_count:
            errors.append(
                f"Relation {name} grain_keys length ({len(grain_keys)}) does not match row_count ({row_count})"
            )

    # 5. Sanity Checks for Disallowed Contents
    oracle_text = oracle_bytes.decode("utf-8")
    for pattern in DISALLOWED_PATTERNS:
        if pattern.search(oracle_text):
            errors.append(f"Oracle contains disallowed pattern: {pattern.pattern}")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate F0 oracle and metadata artifacts."
    )
    parser.add_argument("--oracle", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    args = parser.parse_args()

    errors = validate_f0(args.oracle, args.metadata)
    if errors:
        print("Validation FAILED with errors:")
        for err in errors:
            print(f" - {err}")
        sys.exit(1)
    else:
        print("Validation PASSED successfully.")


if __name__ == "__main__":
    main()
