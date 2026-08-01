"""Airflow REST API client for triggering, polling and unpausing serving DAGs."""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.request
from collections.abc import Mapping
from urllib.error import HTTPError

logger = logging.getLogger(__name__)


def get_airflow_url() -> str:
    return os.environ.get("AIRFLOW_URL", "http://127.0.0.1:8080").rstrip("/")


def get_auth_token() -> str | None:
    secret_key_file = os.environ.get(
        "AIRFLOW_API_SECRET_KEY_SOURCE_FILE",
        "docker/secrets/dev/airflow_api_secret_key.txt",
    )
    if os.path.exists(secret_key_file):
        with open(secret_key_file, encoding="utf-8") as f:
            return f.read().strip()
    return None


class AirflowApiClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or get_airflow_url()).rstrip("/")
        self.token = get_auth_token()

    def _request(
        self,
        path: str,
        method: str = "GET",
        body: Mapping[str, object] | None = None,
    ) -> tuple[int, object]:
        url = f"{self.base_url}{path}"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        data = json.dumps(body).encode("utf-8") if body else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30.0) as resp:
                raw = resp.read().decode("utf-8")
                return resp.status, json.loads(raw) if raw.strip() else None
        except HTTPError as exc:
            return exc.code, None
        except Exception as exc:
            logger.error("Airflow API request error to %s: %s", url, exc)
            return 0, None

    def trigger_dag_run(
        self,
        dag_id: str,
        run_id: str | None = None,
        conf: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        path = f"/api/v1/dags/{dag_id}/dagRuns"
        body: dict[str, object] = {}
        if run_id:
            body["dag_run_id"] = run_id
        if conf:
            body["conf"] = dict(conf)

        status, resp = self._request(path, method="POST", body=body)
        if status in (200, 201) and isinstance(resp, dict):
            return dict(resp)
        raise RuntimeError(f"Failed to trigger DAG {dag_id}, status code {status}")

    def poll_dag_run(
        self, dag_id: str, dag_run_id: str, timeout_seconds: float = 1800.0
    ) -> str:
        path = f"/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}"
        deadline = time.monotonic() + timeout_seconds

        while time.monotonic() < deadline:
            status, resp = self._request(path, method="GET")
            if status == 200 and isinstance(resp, dict):
                state = resp.get("state")
                if state in ("success", "failed"):
                    return str(state)
            time.sleep(5)
        return "timeout"

    def unpause_dag(self, dag_id: str) -> bool:
        path = f"/api/v1/dags/{dag_id}"
        body: dict[str, object] = {"is_paused": False}
        status, _resp = self._request(path, method="PATCH", body=body)
        return status == 200
