"""Validate that batch, realtime, and parity dbt entrypoints stay isolated."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DBT_PROJECT = ROOT / "dbt" / "olist_analytics"
SELECTORS = ("batch", "realtime_transform", "realtime_quality", "realtime_parity")
REALTIME_QUALITY_TESTS = {
    "assert_realtime_latest_reconciliation_passed",
    "assert_realtime_mart_freshness",
    "assert_realtime_offset_continuity",
}
ALLOWED_BATCH_PACKAGES = {"olist_analytics", "elementary"}
REQUIRED_ELEMENTARY_MODELS = {
    "dbt_invocations",
    "dbt_models",
    "dbt_run_results",
}


def normalized_path(value: str | None) -> str:
    return (value or "").replace("\\", "/")


def dbt_ls(selector: str) -> list[dict[str, Any]]:
    result = subprocess.run(
        [
            os.environ.get("DBT_BIN", "dbt"),
            "ls",
            "--selector",
            selector,
            "--output",
            "json",
            "--output-keys",
            "unique_id resource_type original_file_path name package_name",
        ],
        cwd=DBT_PROJECT,
        check=True,
        capture_output=True,
        text=True,
    )
    resources = [
        json.loads(line)
        for line in result.stdout.splitlines()
        if line.lstrip().startswith("{")
    ]
    if not resources:
        raise ValueError(f"dbt selector {selector!r} selected no resources")
    return resources


def assert_selector_membership(selected: dict[str, list[dict[str, Any]]]) -> None:
    elementary_models: set[str] = set()
    for resource in selected["batch"]:
        path = normalized_path(resource.get("original_file_path"))
        name = str(resource.get("name", ""))
        package_name = str(resource.get("package_name", ""))
        if package_name not in ALLOWED_BATCH_PACKAGES:
            raise ValueError(
                f"batch selector leaked package {package_name!r}: {name} ({path})"
            )
        if package_name == "elementary":
            if resource.get("resource_type") == "model":
                elementary_models.add(name)
            continue
        if path.startswith(("models/realtime/", "models/parity/")) or name.startswith(
            "assert_realtime_"
        ):
            raise ValueError(
                f"batch selector leaked realtime resource: {name} ({path})"
            )

    missing_elementary_models = REQUIRED_ELEMENTARY_MODELS - elementary_models
    if missing_elementary_models:
        raise ValueError(
            "batch selector must provision Elementary artifact models: "
            f"missing {sorted(missing_elementary_models)}"
        )

    for resource in selected["realtime_transform"]:
        if resource.get("resource_type") != "model":
            continue
        path = normalized_path(resource.get("original_file_path"))
        if not path.startswith("models/realtime/"):
            raise ValueError(f"realtime transform leaked non-realtime model: {path}")

    quality_names = {str(item.get("name")) for item in selected["realtime_quality"]}
    if quality_names != REALTIME_QUALITY_TESTS:
        raise ValueError(
            "realtime quality selector mismatch: "
            f"expected {sorted(REALTIME_QUALITY_TESTS)}, got {sorted(quality_names)}"
        )

    for resource in selected["realtime_parity"]:
        path = normalized_path(resource.get("original_file_path"))
        resource_type = resource.get("resource_type")
        if resource_type == "model" and not path.startswith("models/parity/"):
            raise ValueError(f"parity selector leaked model outside bridge: {path}")
        if resource_type == "test" and resource.get("name") != (
            "assert_realtime_parity_passed"
        ):
            raise ValueError(f"parity selector leaked test: {resource.get('name')}")


def model_side(node: dict[str, Any]) -> str:
    path = normalized_path(node.get("original_file_path"))
    if path.startswith("models/realtime/"):
        return "realtime"
    if path.startswith("models/parity/"):
        return "parity"
    return "batch"


def assert_cross_group_lineage() -> None:
    manifest_path = DBT_PROJECT / "target" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    models = {
        unique_id: node
        for unique_id, node in manifest["nodes"].items()
        if unique_id.startswith("model.olist_analytics.")
    }
    cross_edges: list[tuple[str, str]] = []
    for consumer_id, consumer in models.items():
        consumer_side = model_side(consumer)
        for producer_id in consumer.get("depends_on", {}).get("nodes", []):
            producer = models.get(producer_id)
            if producer is None or model_side(producer) == consumer_side:
                continue
            cross_edges.append((producer_id, consumer_id))
            if consumer_side != "parity":
                raise ValueError(
                    "cross-boundary ref must terminate in models/parity: "
                    f"{producer_id} -> {consumer_id}"
                )
    if not cross_edges:
        raise ValueError("expected parity bridge to contain cross-boundary refs")


def assert_bounded_build_entrypoints() -> None:
    paths = [
        *sorted((ROOT / "airflow" / "dags").glob("*.py")),
        *sorted((ROOT / ".github" / "workflows").glob("*.yml")),
        *sorted((ROOT / ".github" / "workflows").glob("*.yaml")),
    ]
    for path in paths:
        source = path.read_text(encoding="utf-8")
        for match in re.finditer(r"dbt\s+build\s+--", source):
            command_window = source[match.start() : match.start() + 160]
            if "--selector" not in command_window:
                relative = path.relative_to(ROOT)
                raise ValueError(f"unbounded dbt build entrypoint in {relative}")


def main() -> None:
    selected = {selector: dbt_ls(selector) for selector in SELECTORS}
    assert_selector_membership(selected)
    assert_cross_group_lineage()
    assert_bounded_build_entrypoints()
    counts = {selector: len(resources) for selector, resources in selected.items()}
    print(json.dumps({"selectors": counts, "status": "success"}, sort_keys=True))


if __name__ == "__main__":
    main()
