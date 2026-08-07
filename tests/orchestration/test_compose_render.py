from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


def _render(*profiles: str) -> dict[str, Any]:
    command = ["docker", "compose"]
    for profile in profiles:
        command.extend(("--profile", profile))
    command.extend(("config", "--format", "json"))
    environment = os.environ.copy()
    for key in (
        "GCP_PROJECT_ID",
        "GCP_REGION",
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GCP_LAKEHOUSE_WAREHOUSE",
    ):
        environment.pop(key, None)
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    rendered = json.loads(result.stdout)
    assert isinstance(rendered, dict)
    return rendered


def _services(rendered: dict[str, Any]) -> dict[str, Any]:
    services = rendered.get("services")
    assert isinstance(services, dict)
    return services


@pytest.mark.skipif(shutil.which("docker") is None, reason="Docker is unavailable")
def test_gcp_render_has_no_local_lakehouse_services_or_mounts() -> None:
    services = _services(_render("core", "lakehouse-gcp"))
    forbidden_services = {
        "minio",
        "minio-init",
        "polaris",
        "polaris-admin",
        "polaris-bootstrap",
        "clickhouse",
        "airflow",
    }
    assert forbidden_services.isdisjoint(services)
    assert "airflow-gcp" in services
    assert {"spark-gcp-migration", "spark-gcp-geolocation", "spark-gcp-ops"} <= set(
        services
    )
    assert {"spark-gcp-bronze", "spark-gcp-silver"}.isdisjoint(services)
    active_text = json.dumps(services, sort_keys=True)
    assert "polaris_db_password" not in active_text
    assert "clickhouse_password" not in active_text
    assert "minio_root_password" not in active_text
    assert {"mysql", "kafka", "kafka-connect", "apicurio-registry"} <= set(services)


@pytest.mark.skipif(shutil.which("docker") is None, reason="Docker is unavailable")
def test_local_render_needs_no_gcp_inputs_and_contains_local_lakehouse() -> None:
    services = _services(_render("core", "lakehouse-local"))
    assert {"minio", "polaris", "clickhouse", "airflow"} <= set(services)
    assert "airflow-gcp" not in services
    active_text = json.dumps(services, sort_keys=True)
    assert "GOOGLE_APPLICATION_CREDENTIALS" not in active_text
    assert "GCP_PROJECT_ID" not in active_text


@pytest.mark.skipif(shutil.which("docker") is None, reason="Docker is unavailable")
def test_streaming_is_explicit_for_the_local_contour() -> None:
    services = _services(_render("core", "lakehouse-local"))
    assert {"spark-bronze", "spark-silver", "spark-ops"}.isdisjoint(services)

    streaming_services = _services(_render("core", "lakehouse-local", "streaming"))
    assert {"spark-bronze", "spark-silver", "spark-ops"} <= set(streaming_services)


@pytest.mark.skipif(shutil.which("docker") is None, reason="Docker is unavailable")
def test_streaming_is_explicit_for_the_gcp_contour() -> None:
    services = _services(_render("core", "lakehouse-gcp"))
    assert {"spark-gcp-bronze", "spark-gcp-silver"}.isdisjoint(services)

    streaming_services = _services(_render("core", "lakehouse-gcp", "streaming-gcp"))
    assert {"spark-gcp-bronze", "spark-gcp-silver"} <= set(streaming_services)
