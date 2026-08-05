from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from scripts.serving.dbt_runner import run_dbt_candidate_build


def test_dbt_runner_extracts_wrapped_run_execution_results() -> None:
    node = SimpleNamespace(name="dim_customer_scd2")
    runner_result = SimpleNamespace(
        success=True,
        exception=None,
        result=SimpleNamespace(
            results=[
                SimpleNamespace(node=node, status="success", execution_time=0.25),
                SimpleNamespace(
                    node=SimpleNamespace(name="test_customer"),
                    status="pass",
                    execution_time=0.1,
                ),
            ]
        ),
    )
    runner = MagicMock()
    runner.invoke.return_value = runner_result

    with patch("scripts.serving.dbt_runner.dbtRunner", return_value=runner):
        result = run_dbt_candidate_build(7, "sync-00000000000000000007")

    assert result["success"] is True
    assert result["status_counts"] == {"success": 1, "pass": 1}
    assert isinstance(result["results"], list)
    assert len(result["results"]) == 2
