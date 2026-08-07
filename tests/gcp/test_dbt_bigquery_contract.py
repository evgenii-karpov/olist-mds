from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "dbt/olist_bigquery"


def test_bigquery_gold_models_use_the_migration_owned_dataset() -> None:
    project = yaml.safe_load((PROJECT / "dbt_project.yml").read_text(encoding="utf-8"))

    gold_config = project["models"]["olist_bigquery"]["gold"]
    assert gold_config["+tags"] == ["gold_candidate"]
    assert "+schema" not in gold_config

    profile = yaml.safe_load((PROJECT / "profiles.yml").read_text(encoding="utf-8"))
    target = profile["olist_bigquery"]["outputs"]["local_static"]
    assert "olist_gold_store" in target["dataset"]
