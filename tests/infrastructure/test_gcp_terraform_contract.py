from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

from scripts import lab

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TERRAFORM_ROOT = PROJECT_ROOT / "infra/gcp/dev"


def _read(name: str) -> str:
    return (TERRAFORM_ROOT / name).read_text(encoding="utf-8")


def test_flat_terraform_root_and_provider_lock_are_present() -> None:
    expected_files = {
        "backend.tf",
        "versions.tf",
        "providers.tf",
        "variables.tf",
        "locals.tf",
        "services.tf",
        "storage.tf",
        "lakehouse.tf",
        "bigquery.tf",
        "iam.tf",
        "budgets.tf",
        "outputs.tf",
        "terraform.tfvars.example",
        "README.md",
        ".terraform.lock.hcl",
    }
    assert expected_files <= {path.name for path in TERRAFORM_ROOT.iterdir()}
    assert 'version = ">= 7.41, < 8.0"' in _read("versions.tf")
    assert 'version     = "7.43.0"' in _read(".terraform.lock.hcl")
    assert 'backend "gcs" {}' in _read("backend.tf")


def test_storage_contract_has_no_automatic_data_deletion_policy() -> None:
    storage = _read("storage.tf")

    assert storage.count('storage_class               = "STANDARD"') == 2
    assert storage.count("uniform_bucket_level_access = true") == 2
    assert storage.count("enabled = false") == 2
    assert storage.count("retention_duration_seconds = 0") == 2
    assert "lifecycle_rule" not in storage
    assert "versioning {\n    enabled = true" not in storage


def test_gcp_resource_ownership_matches_plan() -> None:
    services = _read("services.tf")
    lakehouse = _read("lakehouse.tf")
    bigquery = _read("bigquery.tf")
    iam = _read("iam.tf")

    for service in (
        "biglake.googleapis.com",
        "bigquery.googleapis.com",
        "bigquerystorage.googleapis.com",
        "iam.googleapis.com",
        "storage.googleapis.com",
    ):
        assert service in _read("locals.tf")
    assert "google_project_service" in services
    assert "CATALOG_TYPE_GCS_BUCKET" in lakehouse
    assert "CREDENTIAL_MODE_VENDED_CREDENTIALS" in lakehouse
    for namespace in ("bronze", "silver", "reference", "audit"):
        assert f'"{namespace}"' in _read("locals.tf")
    for dataset in (
        "olist_lakehouse_bridge",
        "olist_gold_store",
        "olist_gold",
        "olist_serving_control",
        "olist_cloud_test",
    ):
        assert dataset in _read("locals.tf")
    assert "delete_contents_on_destroy" in bigquery
    assert "google_service_account" in iam
    assert "google_service_account_key" not in iam
    assert "roles/storage.objectAdmin" in iam
    assert "google_bigquery_dataset_iam_member" in iam


def test_terraform_init_is_credential_free(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_run(command, **_kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=0, stdout="initialized", stderr="")

    monkeypatch.setattr(lab.subprocess, "run", fake_run)
    result = lab._terraform(
        Namespace(
            action="init",
            yes=False,
            timeout=10.0,
            backend_config=[],
            var_file=None,
            allow_missing_auth=False,
        )
    )

    assert result == 0
    assert calls
    assert "-backend=false" in calls[0]
    assert "-input=false" in calls[0]


def test_terraform_plan_requires_gcp_preflight(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        lab,
        "_gcp_preflight",
        lambda: {
            "checks": {"project_id": False},
            "missing": ["project_id"],
            "project_id": None,
            "region": None,
        },
    )
    result = lab._terraform(
        Namespace(
            action="plan",
            yes=False,
            timeout=10.0,
            backend_config=[],
            var_file=None,
            allow_missing_auth=False,
        )
    )

    assert result == 0
    assert '"status": "blocked"' in capsys.readouterr().out
