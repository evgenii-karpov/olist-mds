"""Programmatic dbt invocation helper for Stage E serving candidate models."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from dbt.cli.main import dbtRunner, dbtRunnerResult

logger = logging.getLogger(__name__)

DBT_PROJECT_DIR = Path(__file__).resolve().parents[2] / "dbt" / "olist_clickhouse"


def run_dbt_candidate_build(sync_run_seq: int, sync_run_id: str) -> dict[str, object]:
    """Execute dbt build for candidate Gold models with explicit vars."""
    dbt = dbtRunner()

    vars_dict = {
        "sync_run_seq": sync_run_seq,
        "sync_run_id": sync_run_id,
    }
    vars_json = json.dumps(vars_dict)

    cli_args = [
        "build",
        "--project-dir",
        str(DBT_PROJECT_DIR),
        "--select",
        "tag:serving_candidate",
        "--vars",
        vars_json,
    ]

    logger.info("Executing dbt runner with args: %s", cli_args)
    res: dbtRunnerResult = dbt.invoke(cli_args)

    success = res.success
    results_summary: list[dict[str, str | float]] = []
    res_result = getattr(res, "result", None)
    if isinstance(res_result, list):
        for r in res_result:
            node = getattr(r, "node", None)
            node_name = getattr(node, "name", "unknown") if node else "unknown"
            results_summary.append(
                {
                    "node": str(node_name),
                    "status": str(getattr(r, "status", "unknown")),
                    "execution_time": float(getattr(r, "execution_time", 0.0)),
                }
            )

    return {
        "success": success,
        "results": results_summary,
        "exception": str(res.exception) if res.exception else None,
    }
