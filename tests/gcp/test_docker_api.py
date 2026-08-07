from __future__ import annotations

import io
import json
import tarfile
from typing import cast

import pytest
from scripts.gcp.docker_api import (
    DbtContainerRequest,
    DockerApiClient,
    build_dbt_command,
    build_dbt_container_payload,
    run_dbt_container,
)


def _request(**overrides: object) -> DbtContainerRequest:
    values: dict[str, object] = {
        "project_id": "demo-project",
        "region": "us-east1",
        "sync_run_seq": 7,
        "sync_run_id": "gcp-sync-00000000000000000007",
        "previous_boundary_id": "previous",
        "current_boundary_id": "current",
        "build_mode": "incremental",
        "project_host_path": "/workspace/dbt/olist_bigquery",
        "adc_host_path": "/workspace/.gcp/dbt-adc.json",
    }
    values.update(overrides)
    return DbtContainerRequest(**values)  # type: ignore[arg-type]


def test_dbt_command_is_argv_based_and_run_scoped() -> None:
    request = _request()

    command = build_dbt_command(request)

    assert command[0] == "build"
    assert "--project-dir" in command
    assert "--fail-fast" in command
    vars_json = command[command.index("--vars") + 1]
    assert json.loads(vars_json) == {
        "build_mode": "incremental",
        "current_boundary_id": "current",
        "previous_boundary_id": "previous",
        "sync_run_id": "gcp-sync-00000000000000000007",
        "sync_run_seq": 7,
        "target": "gcp",
    }


def test_dbt_payload_only_mounts_project_and_adc_read_only() -> None:
    payload = build_dbt_container_payload(_request(network="gcp-network"))

    assert payload["Image"] == "olist-dbt-bigquery:1.11.3"
    assert payload["WorkingDir"] == "/opt/olist"
    assert payload["NetworkingConfig"] == {"EndpointsConfig": {"gcp-network": {}}}
    host_config = cast(dict[str, object], payload["HostConfig"])
    assert host_config["AutoRemove"] is False
    assert host_config["ReadonlyRootfs"] is True
    assert host_config["Binds"] == [
        "/workspace/dbt/olist_bigquery:/opt/olist/dbt/olist_bigquery:ro",
        "/workspace/.gcp/dbt-adc.json:/run/gcp/adc/dbt.json:ro",
    ]
    environment = cast(list[str], payload["Env"])
    assert all("DOCKER_HOST" not in value for value in environment)


def test_request_rejects_relative_host_paths() -> None:
    with pytest.raises(ValueError, match="absolute host path"):
        _request(project_host_path="./dbt/olist_bigquery")


class _FakeDockerClient:
    def __init__(self) -> None:
        self.removed: list[str] = []

    def create(self, _payload: dict[str, object]) -> str:
        return "a" * 64

    def start(self, _container_id: str) -> None:
        return None

    def wait(self, _container_id: str, *, timeout_seconds: int) -> int:
        assert timeout_seconds == 7200
        return 0

    def logs(self, _container_id: str) -> str:
        return "dbt completed"

    def archive(self, _container_id: str, path: str) -> bytes:
        filename = path.rsplit("/", 1)[-1]
        content = json.dumps({"artifact": filename}).encode("utf-8")
        result = io.BytesIO()
        with tarfile.open(fileobj=result, mode="w") as archive:
            info = tarfile.TarInfo(name=f"tmp/dbt-target/{filename}")
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))
        return result.getvalue()

    def remove(self, container_id: str) -> None:
        self.removed.append(container_id)


def test_dbt_container_runner_collects_artifacts_and_cleans_up() -> None:
    fake = _FakeDockerClient()

    result = run_dbt_container(
        _request(),
        client=cast(DockerApiClient, fake),
    )

    assert result.success
    assert result.exit_code == 0
    assert result.logs == "dbt completed"
    assert result.artifacts == {
        "run_results.json": {"artifact": "run_results.json"},
        "manifest.json": {"artifact": "manifest.json"},
    }
    assert fake.removed == ["a" * 64]
