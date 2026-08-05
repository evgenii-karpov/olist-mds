"""Compare canonical cross-engine parity manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _relation_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {relation["name"]: relation for relation in manifest["relations"]}


def _sample_difference(left: list[Any], right: list[Any], limit: int) -> dict[str, Any]:
    left_values = {json.dumps(value, sort_keys=True): value for value in left}
    right_values = {json.dumps(value, sort_keys=True): value for value in right}
    left_keys = set(left_values)
    right_keys = set(right_values)
    return {
        "missing_from_candidate": [
            left_values[key] for key in sorted(left_keys - right_keys)[:limit]
        ],
        "unexpected_in_candidate": [
            right_values[key] for key in sorted(right_keys - left_keys)[:limit]
        ],
    }


def _semantic_columns_mismatch(
    expected: dict[str, Any], observed: dict[str, Any]
) -> dict[str, Any]:
    mismatches: dict[str, Any] = {}
    for column in sorted(set(expected) | set(observed)):
        if column not in expected:
            mismatches[column] = {"issue": "extra", "candidate": observed[column]}
            continue
        if column not in observed:
            mismatches[column] = {"issue": "missing", "oracle": expected[column]}
            continue
        expected_column = expected[column]
        observed_column = observed[column]
        if expected_column["type"] != observed_column["type"]:
            mismatches[column] = {
                "oracle": expected_column,
                "candidate": observed_column,
            }
            continue
        if (
            expected_column["type"] == "decimal"
            and "scale" in expected_column
            and "scale" in observed_column
            and expected_column["scale"] != observed_column["scale"]
        ):
            mismatches[column] = {
                "oracle": expected_column,
                "candidate": observed_column,
            }
    return mismatches


def compare_manifests(
    oracle: dict[str, Any], candidate: dict[str, Any], sample_limit: int = 10
) -> dict[str, Any]:
    mismatches: list[dict[str, Any]] = []
    relation_results: list[dict[str, Any]] = []
    oracle_relations = _relation_map(oracle)
    candidate_relations = _relation_map(candidate)
    for relation_name in sorted(set(oracle_relations) | set(candidate_relations)):
        if relation_name not in oracle_relations:
            relation_results.append(
                {
                    "relation": relation_name,
                    "status": "FAIL",
                    "issue": "extra_relation",
                    "oracle_row_count": 0,
                    "candidate_row_count": candidate_relations[relation_name].get(
                        "row_count", 0
                    ),
                    "missing_key_count": 0,
                    "extra_key_count": len(
                        candidate_relations[relation_name].get("grain_keys", [])
                    ),
                    "column_mismatch_count": 0,
                }
            )
            mismatches.append(
                {"relation": relation_name, "check": "relation", "issue": "extra"}
            )
            continue
        if relation_name not in candidate_relations:
            relation_results.append(
                {
                    "relation": relation_name,
                    "status": "FAIL",
                    "issue": "missing_relation",
                    "oracle_row_count": oracle_relations[relation_name].get(
                        "row_count", 0
                    ),
                    "candidate_row_count": 0,
                    "missing_key_count": len(
                        oracle_relations[relation_name].get("grain_keys", [])
                    ),
                    "extra_key_count": 0,
                    "column_mismatch_count": 0,
                }
            )
            mismatches.append(
                {"relation": relation_name, "check": "relation", "issue": "missing"}
            )
            continue
        expected = oracle_relations[relation_name]
        observed = candidate_relations[relation_name]
        relation_mismatch_count = 0
        semantic_mismatches = _semantic_columns_mismatch(
            expected["semantic_columns"], observed["semantic_columns"]
        )
        if semantic_mismatches:
            relation_mismatch_count += 1
            mismatches.append(
                {
                    "relation": relation_name,
                    "check": "semantic_columns",
                    "columns": semantic_mismatches,
                }
            )
        for check in ("row_count", "duplicate_grain_count", "aggregate_hash"):
            if expected[check] != observed[check]:
                relation_mismatch_count += 1
                mismatches.append(
                    {
                        "relation": relation_name,
                        "check": check,
                        "oracle": expected[check],
                        "candidate": observed[check],
                    }
                )
        expected_key_strings = {
            json.dumps(value, sort_keys=True) for value in expected["grain_keys"]
        }
        observed_key_strings = {
            json.dumps(value, sort_keys=True) for value in observed["grain_keys"]
        }
        missing_keys = expected_key_strings - observed_key_strings
        extra_keys = observed_key_strings - expected_key_strings
        if missing_keys or extra_keys:
            relation_mismatch_count += 1
            mismatches.append(
                {
                    "relation": relation_name,
                    "check": "grain_keys",
                    "missing_key_count": len(missing_keys),
                    "extra_key_count": len(extra_keys),
                    "sample": _sample_difference(
                        expected["grain_keys"], observed["grain_keys"], sample_limit
                    ),
                }
            )
        expected_rows = {
            json.dumps(row["grain"], sort_keys=True): row for row in expected["rows"]
        }
        observed_rows = {
            json.dumps(row["grain"], sort_keys=True): row for row in observed["rows"]
        }
        hash_mismatches = [
            {
                "grain": expected_rows[key]["grain"],
                "oracle_hash": expected_rows[key]["hash"],
                "candidate_hash": observed_rows[key]["hash"],
            }
            for key in sorted(set(expected_rows) & set(observed_rows))
            if expected_rows[key]["hash"] != observed_rows[key]["hash"]
        ]
        if hash_mismatches:
            relation_mismatch_count += 1
            mismatches.append(
                {
                    "relation": relation_name,
                    "check": "row_hash",
                    "sample": hash_mismatches[:sample_limit],
                }
            )
        if expected["metrics"] != observed["metrics"]:
            relation_mismatch_count += 1
            mismatches.append(
                {
                    "relation": relation_name,
                    "check": "metrics",
                    "oracle": expected["metrics"],
                    "candidate": observed["metrics"],
                }
            )
        relation_results.append(
            {
                "relation": relation_name,
                "status": "PASS" if relation_mismatch_count == 0 else "FAIL",
                "oracle_row_count": expected.get("row_count", 0),
                "candidate_row_count": observed.get("row_count", 0),
                "oracle_duplicate_grain_count": expected.get(
                    "duplicate_grain_count", 0
                ),
                "candidate_duplicate_grain_count": observed.get(
                    "duplicate_grain_count", 0
                ),
                "missing_key_count": len(missing_keys),
                "extra_key_count": len(extra_keys),
                "column_mismatch_count": len(hash_mismatches),
                "semantic_column_mismatch_count": len(semantic_mismatches),
                "aggregate_hash_match": expected.get("aggregate_hash")
                == observed.get("aggregate_hash"),
                "metrics_match": expected.get("metrics") == observed.get("metrics"),
                "mismatch_sample": hash_mismatches[:sample_limit],
            }
        )
    return {
        "format_version": 1,
        "dataset": oracle.get("dataset"),
        "status": "PASS" if not mismatches else "FAIL",
        "mismatch_count": len(mismatches),
        "missing_key_count": sum(
            relation["missing_key_count"] for relation in relation_results
        ),
        "extra_key_count": sum(
            relation["extra_key_count"] for relation in relation_results
        ),
        "column_mismatch_count": sum(
            relation["column_mismatch_count"] for relation in relation_results
        ),
        "relations": relation_results,
        "mismatches": mismatches,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--oracle", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample-limit", type=int, default=10)
    args = parser.parse_args()
    result = compare_manifests(
        json.loads(args.oracle.read_text(encoding="utf-8")),
        json.loads(args.candidate.read_text(encoding="utf-8")),
        sample_limit=args.sample_limit,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
