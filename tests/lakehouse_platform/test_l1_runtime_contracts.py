import argparse
import json
from pathlib import Path
from unittest.mock import patch

from scripts.cdc import stage2_admin
from scripts.cdc.local_lab import (
    DEFAULT_PASSWORD_FILE,
    SECRET_ENV_DEFAULTS,
    _capture_and_contracts,
    _connector_bootstrap,
)
from scripts.ingestion.raw_files import load_source_entities

ROOT = Path(__file__).resolve().parents[2]


def test_target_secret_defaults_are_dedicated_and_present():
    assert DEFAULT_PASSWORD_FILE.name == "mysql_simulator_password.txt"
    for environment_name, relative_path in SECRET_ENV_DEFAULTS.items():
        assert environment_name.endswith("SOURCE_FILE")
        assert (ROOT / relative_path).is_file(), relative_path

    compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
    secrets_block = compose.split("secrets:", maxsplit=1)[1]
    assert "./docker/secrets/dev/postgres_password.txt}" not in secrets_block
    assert (
        "airflow_api_secret_key.txt"
        not in secrets_block.split("minio_root_password:", maxsplit=1)[1].split(
            "clickhouse_password:", maxsplit=1
        )[0]
    )


def test_source_profiles_use_target_neutral_raw_type_metadata():
    for profile_path in (
        ROOT / "docs/source_profile.json",
        ROOT / "tests/fixtures/olist_small/source_profile_small.json",
    ):
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        assert profile
        assert all(
            "raw_type" in column and "redshift_raw_type" not in column
            for entity in profile
            for column in entity["columns"]
        )

    entities = load_source_entities(
        ROOT / "tests/fixtures/olist_small/source_profile_small.json"
    )
    assert entities
    assert all(entity.column_types for entity in entities)


def test_stage2_admin_uses_the_target_mysql_connector():
    assert stage2_admin.CONNECTOR_NAME == "olist-mysql-cdc"
    assert stage2_admin.CONNECTOR_TEMPLATE.is_file()
    template = json.loads(stage2_admin.CONNECTOR_TEMPLATE.read_text(encoding="utf-8"))
    assert template["config"]["connector.class"] == (
        "io.debezium.connector.mysql.MySqlConnector"
    )
    assert "database.password" not in template["config"]


def test_local_lab_uses_the_dedicated_cdc_reader_secret_for_connector_bootstrap():
    args = argparse.Namespace(
        password_file=ROOT / "docker/secrets/dev/mysql_simulator_password.txt",
        timeout=1,
    )
    with patch("scripts.cdc.local_lab._run") as run:
        _connector_bootstrap(args)

    command = run.call_args.args[0]
    password_index = command.index("--password-file") + 1
    assert command[password_index].endswith(
        "docker\\secrets\\dev\\mysql_cdc_reader_password.txt"
    ) or command[password_index].endswith(
        "docker/secrets/dev/mysql_cdc_reader_password.txt"
    )
    assert "mysql_simulator_password.txt" not in command[password_index]


def test_airflow_wrapper_is_file_only_and_has_no_legacy_cloud_defaults():
    wrapper = (ROOT / "docker/airflow/load-env-and-run.sh").read_text(encoding="utf-8")
    assert "fetch_aws_secret" not in wrapper
    assert "AWS_SECRET_ID" not in wrapper
    assert "REDSHIFT" not in wrapper
    assert "POSTGRES_PASSWORD:=olist" not in wrapper
    assert "${base_name}_FILE" in wrapper
    assert "Plaintext secret environment variable" in wrapper


def test_capture_validation_isolated_from_frozen_writer_repository():
    args = argparse.Namespace(timeout=1)
    with patch("scripts.cdc.local_lab._run") as run:
        result = _capture_and_contracts(args)

    commands = [call.args[0] for call in run.call_args_list]
    assert result == {"capture_state": "captured", "contract_version": 2}
    assert not any("capture-bundle" in command for command in commands)

    writer_validate = next(
        command
        for command in commands
        if "writer_schemas" in " ".join(command) and "validate" in command
    )
    assert "--root" in writer_validate

    contract_check = next(
        command
        for command in commands
        if "generate_contracts" in " ".join(command) and "--check" in command
    )
    assert "--writer-root" in contract_check

    entity_check = next(
        command for command in commands if "schemas.contracts" in " ".join(command)
    )
    assert "--writer-root" in entity_check
