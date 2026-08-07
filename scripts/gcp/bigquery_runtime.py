"""Official BigQuery client wiring for the GCP serving contour.

The control adapter itself remains client-agnostic.  This module is the
runtime seam used by Airflow: it converts named values to BigQuery query
parameters, applies bounded query labels/byte caps, and relies on ADC rather
than embedding credentials.
"""

from __future__ import annotations

import os
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

_PROJECT_ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$")
_LOCATION_PATTERN = re.compile(r"^[a-z0-9-]+$")
_NULL_PARAMETER_TYPES = {
    "expected_active_sync_run_seq": "INT64",
    "sync_run_seq": "INT64",
    "is_noop": "BOOL",
    "ttl_seconds": "INT64",
    "expected_event_count": "INT64",
    "materialized_event_count": "INT64",
    "affected_key_count": "INT64",
    "candidate_current_count": "INT64",
    "candidate_row_count": "INT64",
    "affected_grain_count": "INT64",
}


def _scalar_type(name: str, value: object) -> str:
    if value is None:
        return _NULL_PARAMETER_TYPES.get(name, "STRING")
    if isinstance(value, bool):
        return "BOOL"
    if isinstance(value, int):
        return "INT64"
    if isinstance(value, float):
        return "FLOAT64"
    return "STRING"


def _array_type(name: str, values: Sequence[object]) -> str:
    for value in values:
        if value is not None:
            return _scalar_type(name, value)
    if name == "expected_statuses":
        return "STRING"
    if name in {"entities", "source_topics"}:
        return "STRING"
    return "STRING"


@dataclass(slots=True)
class BigQueryClientRunner:
    """Adapter implementing ``BigQueryQueryRunner`` with named parameters."""

    project_id: str
    location: str = "us-east1"
    maximum_bytes_billed: int | None = 1_000_000_000
    labels: Mapping[str, str] = field(
        default_factory=lambda: {
            "component": "olist-gcp-serving",
            "target": "gcp",
        }
    )
    _client: Any = field(init=False, repr=False)
    _bigquery: Any = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not _PROJECT_ID_PATTERN.fullmatch(self.project_id):
            raise ValueError(f"invalid GCP project ID: {self.project_id!r}")
        if not _LOCATION_PATTERN.fullmatch(self.location):
            raise ValueError(f"invalid BigQuery location: {self.location!r}")
        if self.maximum_bytes_billed is not None and self.maximum_bytes_billed < 1:
            raise ValueError("maximum_bytes_billed must be positive")
        from google.cloud import bigquery

        self._bigquery = bigquery
        self._client = bigquery.Client(project=self.project_id, location=self.location)

    def _query_parameters(
        self,
        parameters: Mapping[str, object],
    ) -> list[Any]:
        query_parameters: list[Any] = []
        for name, value in parameters.items():
            if isinstance(value, (list, tuple)):
                values = list(value)
                query_parameters.append(
                    self._bigquery.ArrayQueryParameter(
                        name,
                        _array_type(name, values),
                        values,
                    )
                )
            else:
                query_parameters.append(
                    self._bigquery.ScalarQueryParameter(
                        name,
                        _scalar_type(name, value),
                        value,
                    )
                )
        return query_parameters

    def _labels_for(self, parameters: Mapping[str, object]) -> dict[str, str]:
        labels = {str(key): str(value) for key, value in self.labels.items()}
        raw_seq = parameters.get("sync_run_seq")
        if isinstance(raw_seq, int):
            labels["run"] = f"run-{raw_seq}"
        return labels

    def execute(
        self,
        sql: str,
        parameters: Mapping[str, object],
    ) -> list[Mapping[str, object]]:
        if not sql.strip():
            raise ValueError("BigQuery SQL must not be empty")
        job_config = self._bigquery.QueryJobConfig(
            query_parameters=self._query_parameters(parameters),
            use_query_cache=False,
            labels=self._labels_for(parameters),
        )
        if self.maximum_bytes_billed is not None:
            job_config.maximum_bytes_billed = self.maximum_bytes_billed
        job = self._client.query(sql, job_config=job_config)
        return [dict(row.items()) for row in job.result()]

    def close(self) -> None:
        self._client.close()


def runner_from_environment() -> BigQueryClientRunner:
    """Create a runner from non-secret environment settings and ADC."""

    project_id = os.environ.get("GCP_PROJECT_ID", "").strip()
    if not project_id:
        raise RuntimeError("GCP_PROJECT_ID is required for the GCP serving DAG")
    raw_cap = os.environ.get("GCP_BIGQUERY_MAX_BYTES_BILLED", "1000000000")
    try:
        maximum_bytes_billed = int(raw_cap)
    except ValueError as exc:
        raise RuntimeError("GCP_BIGQUERY_MAX_BYTES_BILLED must be an integer") from exc
    return BigQueryClientRunner(
        project_id=project_id,
        location=os.environ.get("GCP_REGION", "us-east1"),
        maximum_bytes_billed=maximum_bytes_billed,
    )
