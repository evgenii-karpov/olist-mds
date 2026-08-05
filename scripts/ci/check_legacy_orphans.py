"""Fail when removed lakehouse implementations still have active consumers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

REMOVED_PATHS = (
    ".github/workflows/batch-cdc-parity.yml",
    "airflow/dags/olist_cdc_local.py",
    "airflow/dags/olist_cdc_dbt_local.py",
    "airflow/dags/olist_modern_data_stack_local.py",
    "airflow/dags/olist_modern_data_stack_aws.py",
    "dbt/olist_analytics",
    "infra/oltp",
    "infra/redshift",
    "infra/aws/realtime",
    "infra/clickhouse/initdb",
    "streaming/nifi",
    "streaming/minio/init.sh",
    "streaming/minio/nifi-policy.json",
    "streaming/minio/cdc-loader-policy.json",
    "streaming/schemas/normalized",
    "streaming/schemas/cdc-landing",
    "streaming/schemas/cdc-coverage",
    "scripts/cdc/avro_wire.py",
    "scripts/cdc/benchmark_local.py",
    "scripts/cdc/pipeline_metrics.py",
    "scripts/cdc/realtime_transform.py",
    "scripts/cdc/warehouse_ingest.py",
    "scripts/ingestion",
    "scripts/loading",
    "scripts/orchestration",
    "scripts/quality",
    "scripts/ci/check_batch_cdc_parity_integration.py",
    "scripts/ci/check_clickhouse_cdc_ingest_resilience.py",
    "scripts/ci/check_clickhouse_fact_insert_overwrite_edges.py",
    "scripts/ci/check_clickhouse_smoke.py",
    "scripts/ci/check_dbt_selector_boundaries.py",
    "scripts/ci/check_fixture_pipeline_idempotency.py",
    "scripts/ci/check_oltp_cdc_configuration.py",
    "scripts/ci/check_oltp_simulator_integration.py",
    "scripts/ci/pipeline_helpers.py",
    "scripts/ci/validate_nifi_flow.py",
    "scripts/ci/validate_realtime_configuration.py",
    "scripts/utilities/fetch_aws_secret.py",
    "scripts/utilities/generate_redshift_raw_ddl.py",
    "docker/secrets/dev/postgres_password.txt",
    "docker/secrets/dev/redshift_password.txt",
    "tests/fixtures/postgresql_oracle",
)

ACTIVE_ROOTS = (
    ".dockerignore",
    ".env.example",
    ".sqlfluff",
    ".sqlfluffignore",
    "README.md",
    "docs/ci.md",
    "docs/data_model.md",
    "docs/architecture.md",
    "docs/runbook_windows.md",
    "docs/runbook_macos.md",
    "docs/runbooks",
    ".github/workflows",
    "airflow/dags",
    "compose.yaml",
    "dbt/olist_clickhouse",
    "infra",
    "scripts",
    "streaming",
)

FORBIDDEN_REFERENCES = (
    "redshift",
    "dbt/olist_analytics",
    "infra/oltp",
    "infra/redshift",
    "infra/aws/realtime",
    "streaming/nifi",
    "streaming/schemas/normalized",
    "streaming/schemas/cdc-landing",
    "streaming/schemas/cdc-coverage",
    "scripts/ingestion/",
    "scripts/loading/",
    "scripts/orchestration/",
    "scripts/quality/",
    "scripts/cdc/realtime_transform.py",
    "scripts/cdc/warehouse_ingest.py",
    "scripts/cdc/pipeline_metrics.py",
    "scripts/cdc/benchmark_local.py",
    "scripts/ci/validate_nifi_flow.py",
    "scripts/ci/validate_realtime_configuration.py",
    "olist_cdc.public.",
    "olist_nifi",
    "nifi-bootstrap",
    "_nifi_written_at",
    "cdc_audit",
    "raw_data.",
    "realtime-core",
    "redshift",
    "OLIST_S3_PREFIX",
    "docker/secrets/dev/postgres_password.txt",
    "docker/secrets/dev/redshift_password.txt",
)

TEXT_SUFFIXES = {
    "",
    ".dockerignore",
    ".env.example",
    ".sqlfluff",
    ".sqlfluffignore",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".sql",
    ".toml",
    ".yml",
    ".yaml",
}

# These validators intentionally contain the strings they reject. Their own
# behavior is covered by their dedicated tests; scanning their source would
# turn the guard into a self-match rather than an orphan check.
SCAN_EXCLUSIONS = {
    "scripts/ci/check_legacy_orphans.py",
    "scripts/ci/check_repository_contracts.py",
    "scripts/ci/check_dbt_clickhouse_contract.py",
    "scripts/ci/check_airflow_dag_imports.py",
    "scripts/ci/validate_observability_contract.py",
}


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _candidate_files() -> list[Path]:
    files: list[Path] = []
    for raw_root in ACTIVE_ROOTS:
        path = ROOT / raw_root
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(
                candidate for candidate in path.rglob("*") if candidate.is_file()
            )
    return sorted(
        {
            path
            for path in files
            if _relative(path) not in SCAN_EXCLUSIONS
            and (path.name in TEXT_SUFFIXES or path.suffix.lower() in TEXT_SUFFIXES)
        }
    )


def _removed_path_is_present(path: Path) -> bool:
    """Treat an empty checkout directory as absent until Git materializes it."""

    if path.is_file():
        return True
    if not path.is_dir():
        return False
    return any(
        candidate.is_file()
        and candidate.suffix.lower() != ".pyc"
        and "__pycache__" not in candidate.parts
        for candidate in path.rglob("*")
    )


def check() -> dict[str, Any]:
    errors: list[str] = []
    for raw_path in REMOVED_PATHS:
        path = ROOT / raw_path
        if _removed_path_is_present(path):
            errors.append(f"removed path still exists: {raw_path}")

    for path in _candidate_files():
        source = path.read_text(encoding="utf-8").lower()
        for token in FORBIDDEN_REFERENCES:
            if token.lower() in source:
                errors.append(f"active legacy reference {token!r} in {_relative(path)}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "removed_path_count": len(REMOVED_PATHS),
        "scanned_file_count": len(_candidate_files()),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = check()
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
