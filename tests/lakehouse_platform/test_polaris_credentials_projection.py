from __future__ import annotations

import json
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
POLARIS_DIRECTORY = REPOSITORY_ROOT / "infra" / "polaris"


def _read(relative_path: str) -> str:
    return (POLARIS_DIRECTORY / relative_path).read_text(encoding="utf-8")


def _projection_contract() -> dict[str, object]:
    return json.loads(_read("credentials/projection-contract.json"))


def _consumer_sources(contract: dict[str, object], consumer: str) -> set[str]:
    consumers = contract["consumers"]
    assert isinstance(consumers, dict)
    definition = consumers[consumer]
    assert isinstance(definition, dict)
    files = definition["files"]
    assert isinstance(files, list)
    return {entry["source"] for entry in files}


def test_projection_contract_exposes_only_per_consumer_credentials() -> None:
    contract = _projection_contract()
    consumers = contract["consumers"]
    assert isinstance(consumers, dict)

    assert contract["contract_version"] == 1
    assert contract["security_model"] == "one-dedicated-volume-per-consumer"
    assert set(consumers) == {
        "polaris-admin",
        "polaris-server",
        "spark",
        "clickhouse",
        "airflow",
    }

    assert _consumer_sources(contract, "polaris-admin") == {
        "bootstrap-admin-client-id",
        "bootstrap-admin-client-secret",
    }
    assert _consumer_sources(contract, "polaris-server") == {
        "bootstrap-admin-client-id",
        "bootstrap-admin-client-secret",
        "minio-polaris-access-key",
        "minio-polaris-secret-key",
    }
    assert _consumer_sources(contract, "spark") == {
        "polaris-spark-client-id",
        "polaris-spark-client-secret",
        "minio-checkpoints-access-key",
        "minio-checkpoints-secret-key",
    }
    assert _consumer_sources(contract, "clickhouse") == {
        "polaris-clickhouse-client-id",
        "polaris-clickhouse-client-secret",
    }
    assert _consumer_sources(contract, "airflow") == {
        "polaris-airflow-client-id",
        "polaris-airflow-client-secret",
    }

    for consumer in ("spark", "clickhouse", "airflow"):
        own_sources = _consumer_sources(contract, consumer)
        assert not any(source.startswith("bootstrap-admin-") for source in own_sources)
        assert not any(source.startswith("minio-polaris-") for source in own_sources)

    runtime_consumers = ("spark", "clickhouse", "airflow")
    for index, consumer in enumerate(runtime_consumers):
        for other_consumer in runtime_consumers[index + 1 :]:
            assert _consumer_sources(contract, consumer).isdisjoint(
                _consumer_sources(contract, other_consumer)
            )


def test_projection_environment_file_contract_matches_consumers() -> None:
    contract = _projection_contract()
    consumers = contract["consumers"]
    assert isinstance(consumers, dict)

    expected_environment = {
        "polaris-admin": {
            "POLARIS_ROOT_CLIENT_ID_FILE",
            "POLARIS_ROOT_CLIENT_SECRET_FILE",
        },
        "polaris-server": {
            "POLARIS_ROOT_CLIENT_ID_FILE",
            "POLARIS_ROOT_CLIENT_SECRET_FILE",
            "POLARIS_WAREHOUSE_ACCESS_KEY_FILE",
            "POLARIS_WAREHOUSE_SECRET_KEY_FILE",
        },
        "spark": {
            "POLARIS_SPARK_CLIENT_ID_FILE",
            "POLARIS_SPARK_CLIENT_SECRET_FILE",
            "OBJECT_STORE_ACCESS_KEY_FILE",
            "OBJECT_STORE_SECRET_KEY_FILE",
        },
        "clickhouse": {
            "POLARIS_PRINCIPAL_ID_FILE",
            "POLARIS_PRINCIPAL_SECRET_FILE",
        },
        "airflow": {
            "POLARIS_AIRFLOW_CLIENT_ID_FILE",
            "POLARIS_AIRFLOW_CLIENT_SECRET_FILE",
        },
    }

    for consumer, definition in consumers.items():
        assert isinstance(definition, dict)
        files = definition["files"]
        assert isinstance(files, list)
        environments = {entry["environment"] for entry in files}
        assert environments == expected_environment[consumer]
        assert len(files) == len(_consumer_sources(contract, consumer))


def test_projector_enforces_owner_modes_allowlist_and_dedicated_volume() -> None:
    projector = _read("credentials/project.sh")
    dockerfile = _read("credentials/projector.Dockerfile")
    documentation = _read("README.md")

    for required_variable in (
        "CREDENTIAL_CONSUMER",
        "CREDENTIAL_TARGET_UID",
        "CREDENTIAL_TARGET_GID",
    ):
        assert f"${{{required_variable}:?" in projector
    assert 'test "${source_dir}" != "${target_dir}"' in projector
    assert 'test "$(id -u)" = 0' in projector
    assert "unexpected artifact in dedicated" in projector
    assert "credential projection target must be a real directory" in projector
    assert "existing projected artifact must be a regular file" in projector
    assert "test ! -L" in projector
    assert "credential source must have mode 0600" in projector
    assert "credential source must be owned by root" in projector
    assert 'chmod 0600 "${temp_path}"' in projector
    assert 'chmod 0700 "${target_dir}"' in projector
    assert 'chown "${target_uid}:${target_gid}"' in projector
    assert "one-dedicated-volume-per-consumer" in projector
    assert "printf '%s\\n' \"credential projection for ${consumer} is ready\"" in (
        projector
    )

    assert "FROM alpine:3.22.1" in dockerfile
    assert "USER 0" in dockerfile
    assert 'ENTRYPOINT ["/usr/local/bin/project-polaris-credentials"]' in dockerfile
    assert "must never" in documentation
    assert "different target volume for every entry" in documentation
    assert "must not use a Compose `user: root` override" in documentation
