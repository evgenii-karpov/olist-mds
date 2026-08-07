from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

import pytest
from scripts import lab
from scripts.gcp.vertical_slice import (
    DEFAULT_BRIDGE_DATASET,
    VERTICAL_SLICE_VERSION,
    build_probe_plan,
    validate_probe_plan,
)


def test_probe_plan_contains_the_four_required_tables_and_pcnt_queries() -> None:
    plan = build_probe_plan(
        "demo-project",
        "demo-lakehouse-catalog",
        DEFAULT_BRIDGE_DATASET,
    )

    assert plan["version"] == VERTICAL_SLICE_VERSION
    assert [table["source"] for table in plan["tables"]] == [
        "bronze.mysql_cdc_records",
        "silver.order_items_changes",
        "reference.geolocation",
        "audit.silver_progress",
    ]
    assert plan["tables"][0]["direct_identifier"] == (
        "`demo-project.demo-lakehouse-catalog.bronze.mysql_cdc_records`"
    )
    assert plan["tables"][0]["bridge_identifier"] == (
        "`demo-project.olist_lakehouse_bridge.bronze_mysql_cdc_records`"
    )
    assert validate_probe_plan(plan) == []


def test_probe_plan_covers_documented_type_mapping_and_forbidden_metadata_tables() -> (
    None
):
    plan = build_probe_plan("demo-project", "catalog")
    by_source = {table["source"]: table for table in plan["tables"]}

    bronze_types = {
        item["column"]: item["bigquery_type"]
        for item in by_source["bronze.mysql_cdc_records"]["type_expectations"]
    }
    assert bronze_types == {
        "kafka_timestamp": "TIMESTAMP",
        "key_bytes": "BYTES",
        "headers": "ARRAY<STRUCT<key STRING, value BYTES>>",
    }
    silver_types = {
        item["column"]: item["bigquery_type"]
        for item in by_source["silver.order_items_changes"]["type_expectations"]
    }
    assert silver_types == {
        "source_ts": "TIMESTAMP",
        "price": "NUMERIC",
        "freight_value": "NUMERIC",
    }
    reference_types = {
        item["column"]: item["bigquery_type"]
        for item in by_source["reference.geolocation"]["type_expectations"]
    }
    assert reference_types == {
        "geolocation_lat": "BIGNUMERIC",
        "geolocation_lng": "BIGNUMERIC",
    }
    for table in plan["tables"]:
        for key, query in table.items():
            if key.endswith("_sql"):
                assert ".snapshots" not in query
                assert ".files" not in query
    assert "TYPEOF" in by_source["bronze.mysql_cdc_records"]["direct_type_sql"]


def test_probe_plan_rejects_unsafe_cloud_identifiers() -> None:
    with pytest.raises(ValueError, match="unsafe identifier"):
        build_probe_plan("demo-project", "catalog.with.dot")
    with pytest.raises(ValueError, match="project ID"):
        build_probe_plan("not a project", "catalog")


def test_lab_vertical_slice_writes_a_blocked_cloud_plan_without_gcp(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    monkeypatch.setattr(
        lab,
        "_gcp_preflight",
        lambda: {
            "checks": {"project_id": False, "adc_file": False},
            "missing": ["project_id", "adc_file"],
            "project_id": None,
            "region": None,
        },
    )
    output = tmp_path / "vertical-slice-plan.json"
    result = lab._gcp_vertical_slice(
        Namespace(
            action="run",
            project_id="demo-project",
            catalog_id="demo-catalog",
            bridge_dataset=DEFAULT_BRIDGE_DATASET,
            output=str(output),
            allow_missing_auth=True,
        )
    )

    assert result == 0
    plan = json.loads(output.read_text(encoding="utf-8"))
    assert plan["cloud_execution"] == "PENDING_GCP_ACCESS"
    assert '"status": "blocked"' in capsys.readouterr().out


def test_lab_vertical_slice_report_is_not_a_cloud_go_decision(
    tmp_path: Path, capsys
) -> None:
    output = tmp_path / "vertical-slice-plan.json"
    output.write_text(
        json.dumps(build_probe_plan("demo-project", "demo-catalog")),
        encoding="utf-8",
    )

    result = lab._gcp_vertical_slice(Namespace(action="report", output=str(output)))

    assert result == 0
    rendered = capsys.readouterr().out
    assert '"status": "blocked"' in rendered
    assert "PENDING_GCP_ACCESS" in rendered
