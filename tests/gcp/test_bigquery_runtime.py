from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

import pytest
from scripts.gcp.bigquery_runtime import BigQueryClientRunner, runner_from_environment


@dataclass
class _Parameter:
    name: str
    type_: str
    value: object


class _FakeJobConfig:
    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs
        self.maximum_bytes_billed: int | None = None


class _FakeJob:
    job_id = "job-7"
    labels: ClassVar[dict[str, str]] = {
        "component": "olist-gcp-serving",
        "target": "gcp",
        "run": "run-7",
    }
    total_bytes_processed = 120
    total_bytes_billed = 100
    location = "us-east1"

    def result(self) -> list[dict[str, object]]:
        return [{"updated_count": 1}]


class _FakeClient:
    def __init__(self) -> None:
        self.sql = ""
        self.config: _FakeJobConfig | None = None

    def query(self, sql: str, *, job_config: _FakeJobConfig) -> _FakeJob:
        self.sql = sql
        self.config = job_config
        return _FakeJob()

    def close(self) -> None:
        return None


class _FakeBigQuery:
    QueryJobConfig = _FakeJobConfig

    @staticmethod
    def ScalarQueryParameter(name: str, type_: str, value: object) -> _Parameter:
        return _Parameter(name, type_, value)

    @staticmethod
    def ArrayQueryParameter(name: str, type_: str, value: list[object]) -> _Parameter:
        return _Parameter(name, type_, value)


def _runner() -> tuple[BigQueryClientRunner, _FakeClient]:
    runner = object.__new__(BigQueryClientRunner)
    fake_client = _FakeClient()
    runner._bigquery = _FakeBigQuery
    runner._client = fake_client
    runner.project_id = "demo-project"
    runner.location = "us-east1"
    runner.maximum_bytes_billed = 1000
    runner.labels = {"component": "olist-gcp-serving", "target": "gcp"}
    return runner, fake_client


def test_bigquery_runner_builds_typed_named_parameters_and_labels() -> None:
    runner, client = _runner()

    rows = runner.execute(
        "SELECT @sync_run_seq AS sync_run_seq",
        {
            "sync_run_seq": 7,
            "expected_active_sync_run_seq": None,
            "expected_statuses": ["READY_TO_PUBLISH"],
        },
    )

    assert rows == [{"updated_count": 1}]
    assert client.config is not None
    parameters = client.config.kwargs["query_parameters"]
    assert parameters == [
        _Parameter("sync_run_seq", "INT64", 7),
        _Parameter("expected_active_sync_run_seq", "INT64", None),
        _Parameter("expected_statuses", "STRING", ["READY_TO_PUBLISH"]),
    ]
    assert client.config.kwargs["labels"] == {
        "component": "olist-gcp-serving",
        "target": "gcp",
        "run": "run-7",
    }
    assert client.config.maximum_bytes_billed == 1000
    assert runner.last_job_evidence is not None
    assert runner.last_job_evidence.to_dict() == {
        "job_id": "job-7",
        "status": "SUCCEEDED",
        "labels": {
            "component": "olist-gcp-serving",
            "target": "gcp",
            "run": "run-7",
        },
        "bytes_processed": 120,
        "bytes_billed": 100,
        "maximum_bytes_billed": 1000,
        "location": "us-east1",
    }


def test_runner_from_environment_fails_closed_without_project(monkeypatch) -> None:
    monkeypatch.delenv("GCP_PROJECT_ID", raising=False)

    with pytest.raises(RuntimeError, match="GCP_PROJECT_ID"):
        runner_from_environment()
