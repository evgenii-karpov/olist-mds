from __future__ import annotations

from scripts.ci.check_dbt_bigquery_contract import EXPECTED_GOLD_MODELS, PROJECT


def test_bigquery_project_contains_all_independent_gold_models() -> None:
    model_names = {path.stem for path in (PROJECT / "models" / "gold").glob("*.sql")}

    assert model_names == EXPECTED_GOLD_MODELS


def test_gold_models_use_run_scoped_history_and_exact_interval_sources() -> None:
    gold_sql = [
        path.read_text(encoding="utf-8")
        for path in (PROJECT / "models" / "gold").glob("*.sql")
    ]
    source_state = (PROJECT / "macros" / "source_state.sql").read_text(encoding="utf-8")

    assert all("materialized='incremental'" in sql for sql in gold_sql)
    assert all("__history" in sql for sql in gold_sql)
    assert all("delete_same_run_history" in sql for sql in gold_sql)
    assert "previous_offset" in source_state
    assert "target_offset" in source_state
    assert "updated_at" not in "\n".join(gold_sql).lower()


def test_bigquery_project_does_not_reference_local_clickhouse_or_iceberg_metadata() -> (
    None
):
    project_files = [
        path
        for path in PROJECT.rglob("*")
        if path.is_file() and "target" not in path.parts
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in project_files)

    assert "dbt/olist_clickhouse" not in text
    assert "serving_cdc." not in text
    assert ".snapshots" not in text
    assert ".files" not in text
