"""Airflow REST API client for manual serving DAG runs and polling."""

from __future__ import annotations

import contextlib
import json
import logging
import os
import time
import urllib.parse
import urllib.request
from collections.abc import Mapping
from datetime import UTC, datetime
from urllib.error import HTTPError, URLError

logger = logging.getLogger(__name__)


class AirflowApiError(RuntimeError):
    """Airflow was unreachable or returned an unusable response."""


TRANSIENT_HTTP_STATUSES = frozenset({408, 429, 500, 502, 503, 504})
MAX_REQUEST_ATTEMPTS = 3


def get_airflow_url() -> str:
    return os.environ.get("AIRFLOW_URL", "http://127.0.0.1:8080").rstrip("/")


class AirflowApiClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or get_airflow_url()).rstrip("/")
        self._token: str | None = None

    def _get_token(self) -> str:
        if self._token:
            return self._token
        token_url = f"{self.base_url}/auth/token"
        data = urllib.parse.urlencode(
            {"username": "admin", "password": "admin"}
        ).encode("utf-8")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        req = urllib.request.Request(
            token_url, data=data, headers=headers, method="POST"
        )
        last_error: Exception | None = None
        for attempt in range(1, MAX_REQUEST_ATTEMPTS + 1):
            try:
                with urllib.request.urlopen(req, timeout=15.0) as resp:
                    if resp.status not in (200, 201):
                        raise AirflowApiError(
                            f"Airflow token endpoint returned status {resp.status}"
                        )
                    raw = json.loads(resp.read().decode("utf-8"))
                    break
            except HTTPError as exc:
                last_error = exc
                if (
                    exc.code not in TRANSIENT_HTTP_STATUSES
                    or attempt == MAX_REQUEST_ATTEMPTS
                ):
                    raise AirflowApiError(
                        f"Failed to obtain Airflow JWT token from {token_url}: {exc}"
                    ) from exc
            except (URLError, TimeoutError, OSError) as exc:
                last_error = exc
                if attempt == MAX_REQUEST_ATTEMPTS:
                    raise AirflowApiError(
                        f"Failed to obtain Airflow JWT token from {token_url}: {exc}"
                    ) from exc
            time.sleep(float(attempt))
        else:
            raise AirflowApiError(
                f"Failed to obtain Airflow JWT token from {token_url}: {last_error}"
            ) from last_error
        token = raw.get("access_token") if isinstance(raw, dict) else None
        if not isinstance(token, str) or not token:
            raise AirflowApiError("Airflow token response did not contain access_token")
        self._token = token
        return token

    def _request(
        self,
        path: str,
        method: str = "GET",
        body: Mapping[str, object] | None = None,
    ) -> tuple[int, object]:
        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        for attempt in range(1, MAX_REQUEST_ATTEMPTS + 1):
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self._get_token()}",
            }
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=30.0) as resp:
                    raw = resp.read().decode("utf-8")
                    return resp.status, json.loads(raw) if raw.strip() else None
            except HTTPError as exc:
                error_body = ""
                with contextlib.suppress(Exception):
                    error_body = exc.read().decode("utf-8", errors="replace").strip()
                if exc.code == 401 and attempt < MAX_REQUEST_ATTEMPTS:
                    self._token = None
                    continue
                if (
                    exc.code in TRANSIENT_HTTP_STATUSES
                    and attempt < MAX_REQUEST_ATTEMPTS
                ):
                    time.sleep(float(attempt))
                    continue
                logger.error(
                    "Airflow API request failed (%s): %s", exc.code, error_body
                )
                return exc.code, error_body or None
            except (URLError, TimeoutError, OSError) as exc:
                if attempt < MAX_REQUEST_ATTEMPTS:
                    time.sleep(float(attempt))
                    continue
                raise AirflowApiError(
                    f"Airflow API request error to {url}: {exc}"
                ) from exc
        raise AirflowApiError(f"Airflow API request failed to {url} after retries")

    def trigger_dag_run(
        self,
        dag_id: str,
        run_id: str | None = None,
        conf: Mapping[str, object] | None = None,
        *,
        unpause: bool = False,
    ) -> dict[str, object]:
        # Serving validation DAGs are manual-only and intentionally unpaused.
        # There is no timetable for the scheduler to compete with this
        # explicit DagRun; ``unpause`` remains an opt-in compatibility flag
        # for callers that manage a scheduled DAG outside this workflow.
        if unpause:
            self.unpause_dag(dag_id)
        path = f"/api/v2/dags/{dag_id}/dagRuns"
        body: dict[str, object] = {
            "logical_date": datetime.now(UTC).isoformat(),
        }
        if run_id:
            body["dag_run_id"] = run_id
        if conf:
            body["conf"] = dict(conf)

        status, resp = self._request(path, method="POST", body=body)
        if status in (200, 201) and isinstance(resp, dict):
            return dict(resp)
        if status == 409 and run_id:
            # Reusing an existing run would let a stale success from an older
            # validation execute as if it belonged to this invocation.  The
            # caller must generate a fresh run ID and inspect the 409 instead.
            raise AirflowApiError(
                f"DAG run already exists; refusing to reuse stale run {dag_id}/{run_id}"
            )
        raise RuntimeError(f"Failed to trigger DAG {dag_id}, status code {status}")

    def fail_dag_run(self, dag_id: str, dag_run_id: str) -> bool:
        """Request terminal failure for a timed-out run before returning control."""

        path = f"/api/v2/dags/{dag_id}/dagRuns/{dag_run_id}"
        status, _response = self._request(
            path,
            method="PATCH",
            body={"state": "failed"},
        )
        return status in (200, 204)

    def poll_dag_run(
        self, dag_id: str, dag_run_id: str, timeout_seconds: float = 1800.0
    ) -> str:
        path = f"/api/v2/dags/{dag_id}/dagRuns/{dag_run_id}"
        deadline = time.monotonic() + timeout_seconds
        last_error: str | None = None

        while time.monotonic() < deadline:
            try:
                status, resp = self._request(path, method="GET")
            except AirflowApiError as exc:
                # Airflow's API server can briefly lose its database/network
                # connection while a LocalExecutor task is under load.  A
                # transient poll failure must not turn a still-running DAG
                # into a false validation failure.
                last_error = str(exc)
                time.sleep(2.0)
                continue
            if status == 401:
                self._token = None
                time.sleep(1.0)
                continue
            if status == 200 and isinstance(resp, dict):
                state = resp.get("state")
                if state in ("success", "failed"):
                    return str(state)
            time.sleep(5)
        if last_error:
            logger.warning(
                "Airflow DAG polling ended after transient errors: %s", last_error
            )
        return "timeout"

    def unpause_dag(self, dag_id: str) -> bool:
        path = f"/api/v2/dags/{dag_id}"
        body: dict[str, object] = {"is_paused": False}
        status, _resp = self._request(path, method="PATCH", body=body)
        return status in (200, 204)

    def pause_dag(self, dag_id: str) -> bool:
        """Pause scheduled creation without cancelling manual DagRuns."""
        path = f"/api/v2/dags/{dag_id}"
        body: dict[str, object] = {"is_paused": True}
        status, _resp = self._request(path, method="PATCH", body=body)
        return status in (200, 204)
