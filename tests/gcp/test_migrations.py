from __future__ import annotations

from argparse import Namespace
from pathlib import Path

import pytest
from scripts import lab
from scripts.gcp.migrations import (
    list_migrations,
    migration_manifest,
    render_migration,
)


def test_bigquery_migrations_are_ordered_and_checksummed() -> None:
    migrations = list_migrations()

    assert [migration.version for migration in migrations] == [1, 2, 3, 4]
    assert [migration.migration_id for migration in migrations] == [
        "V001__control_tables",
        "V002__bridge_views",
        "V003__gold_source_bridge_views",
        "V004__transaction_boundary_bridge",
    ]
    assert all(len(migration.checksum) == 64 for migration in migrations)
    assert [item["version"] for item in migration_manifest()] == [1, 2, 3, 4]


def test_rendered_migrations_replace_only_validated_identifiers() -> None:
    migration = next(
        migration
        for migration in list_migrations()
        if migration.migration_id == "V002__bridge_views"
    )

    rendered = render_migration(migration, "demo-project", "demo-catalog")

    assert "{{" not in rendered
    assert "demo-project.demo-catalog.bronze.mysql_cdc_records" in rendered
    assert "demo-project.olist_lakehouse_bridge.silver_order_items_changes" in rendered
    assert "CREATE OR REPLACE VIEW" in rendered
    assert "BIGNUMERIC" in rendered


def test_transaction_boundary_bridge_normalizes_debezium_metadata() -> None:
    migration = Path("sql/bigquery/migrations/V004__transaction_boundary_bridge.sql")
    sql = migration.read_text(encoding="utf-8")

    assert sql.count("CREATE OR REPLACE VIEW") == 1
    assert "audit.mysql_transactions" in sql
    assert "audit_mysql_transactions" in sql
    assert "CAST(`end_kafka_offset` AS INT64)" in sql
    assert "CAST(collection.`event_count` AS INT64)" in sql
    assert "ARRAY(" in sql
    assert "INSERT INTO" not in sql
    assert ".snapshots" not in sql
    assert ".files" not in sql


def test_migration_renderer_rejects_unsafe_identifiers() -> None:
    migration = list_migrations()[0]

    with pytest.raises(ValueError, match="project ID"):
        render_migration(migration, "not a project", "catalog")
    with pytest.raises(ValueError, match="unsafe identifier"):
        render_migration(migration, "demo-project", "catalog.with.dot")


def test_bridge_migration_is_read_only_and_does_not_use_iceberg_metadata_tables() -> (
    None
):
    migration = next(
        path
        for path in (Path("sql/bigquery/migrations")).glob("V002__bridge_views.sql")
    )
    sql = migration.read_text(encoding="utf-8")

    assert sql.count("CREATE OR REPLACE VIEW") == 4
    assert ".snapshots" not in sql
    assert ".files" not in sql
    assert "INSERT INTO" not in sql
    assert "UPDATE `" not in sql
    for source in (
        "bronze.mysql_cdc_records",
        "silver.order_items_changes",
        "reference.geolocation",
        "audit.silver_progress",
    ):
        assert f"{{{{ project_id }}}}.{{{{ catalog_id }}}}.{source}" in sql


def test_gold_source_bridge_migration_covers_all_non_slice_silver_changes() -> None:
    migration = Path("sql/bigquery/migrations/V003__gold_source_bridge_views.sql")
    sql = migration.read_text(encoding="utf-8")

    assert sql.count("CREATE OR REPLACE VIEW") == 7
    assert ".snapshots" not in sql
    assert ".files" not in sql
    assert "INSERT INTO" not in sql
    for source in (
        "silver.customers_changes",
        "silver.orders_changes",
        "silver.order_payments_changes",
        "silver.order_reviews_changes",
        "silver.products_changes",
        "silver.sellers_changes",
        "silver.product_category_translation_changes",
    ):
        assert f"{{{{ project_id }}}}.{{{{ catalog_id }}}}.{source}" in sql


def test_lab_migration_status_is_cloud_independent(capsys) -> None:
    result = lab._gcp_migrate(Namespace(action="status"))

    assert result == 0
    output = capsys.readouterr().out
    assert '"status": "ready"' in output
    assert "V004__transaction_boundary_bridge" in output


def test_lab_migration_render_writes_a_reproducible_local_bundle(
    tmp_path, capsys
) -> None:
    result = lab._gcp_migrate(
        Namespace(
            action="render",
            project_id="demo-project",
            catalog_id="demo-catalog",
            output=str(tmp_path / "rendered"),
        )
    )

    assert result == 0
    assert (tmp_path / "rendered" / "V001__control_tables.sql").is_file()
    assert (tmp_path / "rendered" / "V002__bridge_views.sql").is_file()
    assert (tmp_path / "rendered" / "V003__gold_source_bridge_views.sql").is_file()
    assert (tmp_path / "rendered" / "V004__transaction_boundary_bridge.sql").is_file()
    assert (tmp_path / "rendered" / "manifest.json").is_file()
    assert '"status": "accepted"' in capsys.readouterr().out
