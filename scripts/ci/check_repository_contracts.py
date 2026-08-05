"""Run the repository-level target checks required by the common CI job."""

from __future__ import annotations

import argparse
import json
import re
import tomllib
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]

REMOVED_WORKFLOWS = {
    "batch-cdc-parity.yml",
}
REQUIRED_WORKFLOWS = {
    "ci.yml",
    "lakehouse-components.yml",
    "lakehouse-cdc.yml",
    "lakehouse-serving.yml",
    "lakehouse-acceptance.yml",
}
LEGACY_ACTIVE_TOKENS = (
    "nifi",
    "realtime-core",
    "oltp-postgres",
    "postgres-exporter",
    "dbt/olist_analytics",
    "redshift",
)
LINK_PATTERN = re.compile(r"(?<!!)\[[^]]*\]\(([^)]+)\)")

YAML_PATHS = (
    ROOT / "compose.yaml",
    ROOT / "observability/prometheus/prometheus.yml",
    ROOT / "observability/prometheus/rules/cdc-component-alerts.yml",
    ROOT / "observability/prometheus/rules/cdc-slo-recording.yml",
    ROOT / "observability/prometheus/rules/lakehouse-serving-alerts.yml",
    ROOT / "observability/alertmanager/alertmanager.yml",
    ROOT / "observability/loki/loki.yml",
    ROOT / "dbt/olist_clickhouse/dbt_project.yml",
    ROOT / "dbt/olist_clickhouse/profiles.yml.example",
    ROOT / "dbt/olist_clickhouse/selectors.yml",
)
JSON_PATHS = (
    ROOT / "streaming/runtime-versions.json",
    *sorted((ROOT / "observability/grafana/dashboards").glob("*.json")),
)
ACTIVE_SCAN_PATHS = (
    ROOT / ".github/workflows",
    ROOT / "compose.yaml",
    ROOT / "airflow/dags/olist_lakehouse_maintenance.py",
    ROOT / "airflow/dags/olist_lakehouse_serving.py",
    ROOT / "dbt/olist_clickhouse",
    ROOT / "observability/prometheus",
    ROOT / "observability/alertmanager",
    ROOT / "observability/loki",
    ROOT / "observability/alloy",
)


def _files(paths: tuple[Path, ...]) -> list[Path]:
    result: list[Path] = []
    for path in paths:
        if path.is_file():
            result.append(path)
        elif path.is_dir():
            result.extend(
                candidate
                for candidate in path.rglob("*")
                if candidate.is_file()
                and candidate.suffix.lower() in {".json", ".md", ".yml", ".yaml"}
            )
    return sorted(set(result))


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _check_workflows(errors: list[str]) -> None:
    workflow_dir = ROOT / ".github/workflows"
    workflow_paths = sorted(workflow_dir.glob("*.y*ml"))
    actual = {path.name for path in workflow_paths}
    missing = REQUIRED_WORKFLOWS - actual
    if missing:
        errors.append(f"missing required workflows: {sorted(missing)}")
    unexpected_legacy = REMOVED_WORKFLOWS & actual
    if unexpected_legacy:
        errors.append(f"legacy workflows still active: {sorted(unexpected_legacy)}")

    for path in workflow_paths:
        try:
            workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"invalid workflow YAML in {_relative(path)}: {exc}")
            continue
        if not isinstance(workflow, dict):
            errors.append(f"workflow is not a mapping: {_relative(path)}")
            continue
        permissions = workflow.get("permissions")
        if permissions != {"contents": "read"}:
            errors.append(
                f"workflow must grant only read contents permission: {_relative(path)}"
            )
        jobs = workflow.get("jobs")
        if not isinstance(jobs, dict) or not jobs:
            errors.append(f"workflow has no jobs mapping: {_relative(path)}")
            continue
        for job_id, job in jobs.items():
            if not isinstance(job, dict) or "timeout-minutes" not in job:
                errors.append(
                    f"workflow job {job_id!r} has no timeout-minutes: {_relative(path)}"
                )


def _check_syntax(errors: list[str]) -> None:
    for path in _files(YAML_PATHS):
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"invalid YAML in {_relative(path)}: {exc}")
    for path in _files(JSON_PATHS):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON in {_relative(path)}: {exc}")
    try:
        tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        errors.append(f"invalid TOML in pyproject.toml: {exc}")


def _check_links(errors: list[str]) -> None:
    markdown_files = list((ROOT / "docs/plans/lakehouse").rglob("*.md"))
    markdown_files.extend((ROOT / "docs/reports").rglob("*.md"))
    for path in markdown_files:
        source = path.read_text(encoding="utf-8")
        for raw_target in LINK_PATTERN.findall(source):
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if not target or target.startswith(("http:", "https:", "mailto:")):
                continue
            if "{" in target or "}" in target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.is_file() and not resolved.is_dir():
                errors.append(
                    f"broken Markdown link in {_relative(path)}: {raw_target}"
                )


def _check_active_legacy_references(errors: list[str]) -> None:
    for root in ACTIVE_SCAN_PATHS:
        paths = [root] if root.is_file() else list(root.rglob("*"))
        for path in paths:
            if not path.is_file() or path.suffix.lower() not in {
                ".json",
                ".py",
                ".sql",
                ".yml",
                ".yaml",
            }:
                continue
            source = path.read_text(encoding="utf-8").lower()
            for token in LEGACY_ACTIVE_TOKENS:
                if token.lower() in source:
                    errors.append(f"active legacy token {token!r} in {_relative(path)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    _check_workflows(errors)
    _check_syntax(errors)
    _check_links(errors)
    _check_active_legacy_references(errors)
    result: dict[str, Any] = {
        "status": "PASS" if not errors else "FAIL",
        "required_workflows": sorted(REQUIRED_WORKFLOWS),
        "removed_workflows": sorted(REMOVED_WORKFLOWS),
        "errors": errors,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
