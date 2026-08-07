from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIGRATION = PROJECT_ROOT / "sql/bigquery/migrations/V001__control_tables.sql"


def test_bigquery_control_migration_is_parameterized_and_complete() -> None:
    sql = MIGRATION.read_text(encoding="utf-8")
    lowered = sql.lower()

    assert "{{ project_id }}" in sql
    for table in (
        "control_state",
        "serving_runs",
        "boundary_offsets",
        "entity_results",
        "model_results",
        "publication_state",
        "schema_migrations",
    ):
        assert f"olist_serving_control.{table}" in sql
    assert "'gcp' AS target" in sql
    assert "next_sync_run_seq" in sql
    assert "expected_active_sync_run_seq" in sql
    assert "target_offsets JSON" in sql
    assert "merge" in lowered
    assert "terraform" in lowered


def test_local_control_ddl_is_explicitly_local() -> None:
    ddl = (
        PROJECT_ROOT
        / "infra/control-postgres/initdb/005_create_serving_control_tables.sql"
    ).read_text(encoding="utf-8")

    assert "target text NOT NULL DEFAULT 'local' CHECK (target = 'local')" in ddl
    assert "expected_active_sync_run_seq bigint" in ddl
