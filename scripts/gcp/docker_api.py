"""Restricted Docker API runner for the GCP dbt candidate container.

The Airflow GCP contour talks to a socket proxy over HTTP.  This module uses
only the small Docker API surface required for one finite dbt build and never
exposes a general-purpose Docker client or shell command.
"""

from __future__ import annotations

import http.client
import json
import ntpath
import os
import posixpath
import re
import tarfile
from collections.abc import Mapping
from dataclasses import dataclass
from io import BytesIO
from urllib.parse import urlencode, urlsplit

_IMAGE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
_NETWORK_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
_CONTAINER_ID_PATTERN = re.compile(r"^[A-Fa-f0-9]{12,64}$")
_MAX_ARTIFACT_BYTES = 16 * 1024 * 1024


class DockerApiError(RuntimeError):
    """Raised when the restricted Docker API rejects an operation."""


@dataclass(frozen=True, slots=True)
class DbtContainerRequest:
    """Validated inputs for one finite BigQuery dbt candidate build."""

    project_id: str
    region: str
    sync_run_seq: int
    sync_run_id: str
    previous_boundary_id: str
    current_boundary_id: str
    build_mode: str
    project_host_path: str
    adc_host_path: str
    image: str = "olist-dbt-bigquery:1.11.3"
    network: str | None = None
    timeout_seconds: int = 7200

    def __post_init__(self) -> None:
        if not re.fullmatch(r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$", self.project_id):
            raise ValueError("project_id is not a valid GCP project ID")
        if not self.region or not re.fullmatch(r"^[a-z0-9-]+$", self.region):
            raise ValueError("region is not a valid GCP region")
        if self.sync_run_seq < 1:
            raise ValueError("sync_run_seq must be positive")
        if not self.sync_run_id.strip():
            raise ValueError("sync_run_id must not be empty")
        if not self.current_boundary_id.strip():
            raise ValueError("current_boundary_id must not be empty")
        if self.build_mode not in {"initial", "incremental"}:
            raise ValueError("build_mode must be initial or incremental")
        if not _IMAGE_PATTERN.fullmatch(self.image):
            raise ValueError("image contains unsafe characters")
        if self.network is not None and not _NETWORK_PATTERN.fullmatch(self.network):
            raise ValueError("network contains unsafe characters")
        for label, path in (
            ("project_host_path", self.project_host_path),
            ("adc_host_path", self.adc_host_path),
        ):
            if not path or not (posixpath.isabs(path) or ntpath.isabs(path)):
                raise ValueError(f"{label} must be an absolute host path")
        if self.timeout_seconds < 1:
            raise ValueError("timeout_seconds must be positive")


@dataclass(frozen=True, slots=True)
class DbtContainerResult:
    """Finite dbt container outcome and small JSON artifacts."""

    container_id: str
    exit_code: int
    logs: str
    artifacts: Mapping[str, object]
    image: str

    @property
    def success(self) -> bool:
        return self.exit_code == 0

    def to_dict(self) -> dict[str, object]:
        return {
            "container_id": self.container_id,
            "exit_code": self.exit_code,
            "logs": self.logs,
            "artifacts": dict(self.artifacts),
            "image": self.image,
            "success": self.success,
        }


def build_dbt_command(request: DbtContainerRequest) -> list[str]:
    """Build an argv-style dbt command with no shell interpolation."""

    vars_json = json.dumps(
        {
            "sync_run_seq": request.sync_run_seq,
            "sync_run_id": request.sync_run_id,
            "target": "gcp",
            "build_mode": request.build_mode,
            "previous_boundary_id": request.previous_boundary_id,
            "current_boundary_id": request.current_boundary_id,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return [
        "build",
        "--project-dir",
        "/opt/olist/dbt/olist_bigquery",
        "--profiles-dir",
        "/opt/olist/dbt/olist_bigquery",
        "--target",
        "local_static",
        "--target-path",
        "/tmp/dbt-target",
        "--select",
        "tag:gold_candidate",
        "--vars",
        vars_json,
        "--no-partial-parse",
        "--fail-fast",
        "--log-format",
        "json",
    ]


def build_dbt_container_payload(request: DbtContainerRequest) -> dict[str, object]:
    """Build the allowlisted Docker create payload for the dbt image."""

    environment = [
        f"GCP_LAKEHOUSE_PROJECT_ID={request.project_id}",
        f"GCP_REGION={request.region}",
        "DBT_BIGQUERY_DATASET=olist_gold_store",
        "GOOGLE_APPLICATION_CREDENTIALS=/run/gcp/adc/dbt.json",
        "DBT_TARGET_PATH=/tmp/dbt-target",
    ]
    binds = [
        f"{request.project_host_path}:/opt/olist/dbt/olist_bigquery:ro",
        f"{request.adc_host_path}:/run/gcp/adc/dbt.json:ro",
    ]
    payload: dict[str, object] = {
        "Image": request.image,
        "Cmd": build_dbt_command(request),
        "Env": environment,
        "WorkingDir": "/opt/olist",
        "Tty": True,
        "OpenStdin": False,
        "Labels": {
            "com.olist.mds.component": "gcp-serving-dbt",
            "com.olist.mds.sync-run-seq": str(request.sync_run_seq),
        },
        "HostConfig": {
            "AutoRemove": False,
            "Binds": binds,
            "ReadonlyRootfs": True,
        },
    }
    if request.network is not None:
        payload["NetworkingConfig"] = {"EndpointsConfig": {request.network: {}}}
    return payload


class DockerApiClient:
    """Minimal Docker API client intended to sit behind a socket proxy."""

    def __init__(self, endpoint: str | None = None, *, timeout: float = 30.0) -> None:
        raw_endpoint = endpoint or os.environ.get("DOCKER_HOST", "")
        if not raw_endpoint:
            raise ValueError("DOCKER_HOST must point to the restricted socket proxy")
        parsed = urlsplit(raw_endpoint)
        if parsed.scheme not in {"http", "https", "tcp"} or not parsed.hostname:
            raise ValueError("DOCKER_HOST must be an http(s) or tcp endpoint")
        scheme = "http" if parsed.scheme == "tcp" else parsed.scheme
        self._scheme = scheme
        self._host = parsed.hostname
        self._port = parsed.port or (443 if scheme == "https" else 80)
        self._timeout = timeout

    def _connection(self) -> http.client.HTTPConnection:
        connection_type = (
            http.client.HTTPSConnection
            if self._scheme == "https"
            else http.client.HTTPConnection
        )
        return connection_type(self._host, self._port, timeout=self._timeout)

    def _request(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, object] | None = None,
        body: Mapping[str, object] | None = None,
        timeout: float | None = None,
    ) -> tuple[int, bytes]:
        if not path.startswith("/") or "?" in path:
            raise ValueError("Docker API paths must be absolute and query-free")
        query_string = urlencode(query or {})
        request_path = f"{path}?{query_string}" if query_string else path
        encoded_body = (
            json.dumps(body, separators=(",", ":")).encode("utf-8")
            if body is not None
            else None
        )
        connection = self._connection()
        if timeout is not None:
            connection.timeout = timeout
        try:
            connection.request(
                method,
                request_path,
                body=encoded_body,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )
            response = connection.getresponse()
            return response.status, response.read()
        finally:
            connection.close()

    @staticmethod
    def _check(status: int, body: bytes, operation: str) -> bytes:
        if status >= 400:
            detail = body.decode("utf-8", errors="replace")[:2048]
            raise DockerApiError(f"Docker API {operation} failed ({status}): {detail}")
        return body

    def create(self, payload: Mapping[str, object]) -> str:
        status, body = self._request("POST", "/containers/create", body=payload)
        checked = self._check(status, body, "create")
        try:
            response = json.loads(checked)
            container_id = response["Id"]
        except (KeyError, TypeError, ValueError) as exc:
            raise DockerApiError("Docker create response did not contain Id") from exc
        if not isinstance(container_id, str) or not _CONTAINER_ID_PATTERN.fullmatch(
            container_id
        ):
            raise DockerApiError("Docker create response contained an invalid Id")
        return container_id

    def start(self, container_id: str) -> None:
        self._check_container_id(container_id)
        status, body = self._request(
            "POST", f"/containers/{container_id}/start", body={}
        )
        self._check(status, body, "start")

    def wait(self, container_id: str, *, timeout_seconds: int) -> int:
        self._check_container_id(container_id)
        status, body = self._request(
            "POST",
            f"/containers/{container_id}/wait",
            body={},
            timeout=float(timeout_seconds) + 30.0,
        )
        checked = self._check(status, body, "wait")
        try:
            exit_code = json.loads(checked)["StatusCode"]
            return int(exit_code)
        except (KeyError, TypeError, ValueError) as exc:
            raise DockerApiError(
                "Docker wait response did not contain StatusCode"
            ) from exc

    def logs(self, container_id: str, *, max_bytes: int = 2 * 1024 * 1024) -> str:
        self._check_container_id(container_id)
        status, body = self._request(
            "GET",
            f"/containers/{container_id}/logs",
            query={"stdout": 1, "stderr": 1, "timestamps": 1, "follow": 0},
        )
        checked = self._check(status, body, "logs")
        return checked[:max_bytes].decode("utf-8", errors="replace")

    def archive(self, container_id: str, path: str) -> bytes:
        self._check_container_id(container_id)
        if not path.startswith("/") or ".." in path.split("/"):
            raise ValueError("archive path must be an absolute container path")
        status, body = self._request(
            "GET",
            f"/containers/{container_id}/archive",
            query={"path": path},
        )
        return self._check(status, body, "archive")

    def remove(self, container_id: str) -> None:
        self._check_container_id(container_id)
        status, body = self._request(
            "DELETE",
            f"/containers/{container_id}",
            query={"force": 1, "v": 1},
        )
        self._check(status, body, "remove")

    @staticmethod
    def _check_container_id(container_id: str) -> None:
        if not _CONTAINER_ID_PATTERN.fullmatch(container_id):
            raise ValueError("invalid Docker container ID")


def _artifact_from_archive(payload: bytes, filename: str) -> object | None:
    """Extract one bounded JSON artifact without trusting archive paths."""

    if len(payload) > _MAX_ARTIFACT_BYTES:
        raise DockerApiError(f"Docker artifact is too large: {filename}")
    try:
        with tarfile.open(fileobj=BytesIO(payload), mode="r:*") as archive:
            candidates = [member for member in archive.getmembers() if member.isfile()]
            member = next(
                (
                    candidate
                    for candidate in candidates
                    if posixpath.basename(candidate.name) == filename
                ),
                None,
            )
            if member is None or member.size > _MAX_ARTIFACT_BYTES:
                return None
            extracted = archive.extractfile(member)
            if extracted is None:
                return None
            return json.loads(extracted.read(_MAX_ARTIFACT_BYTES + 1))
    except (OSError, tarfile.TarError, json.JSONDecodeError) as exc:
        raise DockerApiError(f"invalid dbt artifact archive: {filename}") from exc


def run_dbt_container(
    request: DbtContainerRequest,
    *,
    client: DockerApiClient | None = None,
) -> DbtContainerResult:
    """Run one finite dbt container and clean it up on every exit path."""

    docker = client or DockerApiClient(timeout=30.0)
    container_id = docker.create(build_dbt_container_payload(request))
    try:
        docker.start(container_id)
        exit_code = docker.wait(
            container_id,
            timeout_seconds=request.timeout_seconds,
        )
        logs = docker.logs(container_id)
        artifacts: dict[str, object] = {}
        for filename in ("run_results.json", "manifest.json"):
            artifact = _artifact_from_archive(
                docker.archive(container_id, f"/tmp/dbt-target/{filename}"), filename
            )
            if artifact is not None:
                artifacts[filename] = artifact
        return DbtContainerResult(
            container_id=container_id,
            exit_code=exit_code,
            logs=logs,
            artifacts=artifacts,
            image=request.image,
        )
    finally:
        docker.remove(container_id)


def request_from_environment(
    *,
    project_id: str,
    region: str,
    sync_run_seq: int,
    sync_run_id: str,
    previous_boundary_id: str,
    current_boundary_id: str,
    build_mode: str,
) -> DbtContainerRequest:
    """Build a request from non-secret Airflow configuration."""

    return DbtContainerRequest(
        project_id=project_id,
        region=region,
        sync_run_seq=sync_run_seq,
        sync_run_id=sync_run_id,
        previous_boundary_id=previous_boundary_id,
        current_boundary_id=current_boundary_id,
        build_mode=build_mode,
        project_host_path=os.environ.get("GCP_DBT_PROJECT_HOST_PATH", ""),
        adc_host_path=os.environ.get("GCP_DBT_ADC_HOST_PATH", ""),
        image=os.environ.get("GCP_DBT_IMAGE", "olist-dbt-bigquery:1.11.3"),
        network=os.environ.get("GCP_DBT_NETWORK") or None,
        timeout_seconds=int(os.environ.get("GCP_DBT_TIMEOUT_SECONDS", "7200")),
    )
