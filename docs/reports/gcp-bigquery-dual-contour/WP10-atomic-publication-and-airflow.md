# WP10 — Atomic Publication and GCP DAG

Date: 2026-08-07
Branch: `gcp-bigquery-dual-contour`

## Status

**Credential-free implementation is complete; WP10 is not fully closed.**

The local work now includes the SQL-owned Gold current state, the versioned
publication procedure, the finite GCP serving DAG, a restricted Docker API
runner for the dbt candidate container, and the BigQuery runtime adapter. No
BigQuery job, GCP resource, Airflow run, or cloud credential was used. Failure
injection, compensation-run, and real retry/conflict acceptance remain
pending until GCP is available.

## Implemented

- Added `V005__gold_current_and_publication.sql` with eight explicit
  `olist_gold_store.<model>__current` schemas.
- Added stable `olist_gold.<model>` views over the current tables.
- Added `olist_serving_control.publish_gcp_run(sync_run_seq,
  expected_active_sync_run_seq)`.
- The procedure checks run readiness and all eight model/entity result sets,
  handles already-active idempotency, rejects stale predecessors, applies
  replace-grain and merge operations inside one BigQuery transaction, and
  advances both publication pointers only after a compare-and-set row-count
  check.
- A failed compare-and-set rolls back candidate/current mutations and records
  a terminal publication-drift conflict without overwriting a newer active
  sequence.
- Current facts and marts have explicit date partitioning and business-key
  clustering; small dimensions are clustered by their serving key.
- Added `olist_gcp_serving`, a finite manual Airflow DAG that validates the
  contour, acquires a BigQuery lease, allocates or resumes a same-run
  sequence, freezes a transaction-complete boundary, waits for Silver
  progress, runs a dbt BigQuery candidate, records model/entity results, and
  calls the atomic publication procedure before releasing the lease.
- Added a standard-library Docker REST client with an allow-listed request
  shape. The dbt task can create/start/wait/log/remove one read-only candidate
  container and collect bounded `run_results.json`/`manifest.json` artifacts;
  it cannot execute arbitrary commands or access Docker exec/images/networks/
  volumes APIs.
- Added a Docker socket proxy service for the GCP Compose contour. The proxy
  exposes only the container/start POST surface required by the runner and is
  not published outside the private Compose network. Its security model still
  requires Linux-container and IAM validation in the cloud environment; see
  the [upstream socket proxy documentation](https://github.com/Tecnativa/docker-socket-proxy).
- Added a lazy `google-cloud-bigquery` runtime adapter with named and array
  query parameters, explicit GoogleSQL mode, run labels, location, disabled
  query cache, and a configurable `maximum_bytes_billed` cap. Query jobs use
  the official `QueryJobConfig` mechanism for labels and byte limits.
- Added lease heartbeat/release, Silver progress metrics, candidate-count
  collection, bounded report emission, fail-closed result writes, and
  `ALL_DONE` lease cleanup to the GCP control path.

## Static evidence

```text
uv run pytest tests/gcp/test_migrations.py -q
9 passed, 1 warning

uv run sqlfluff parse sql/bigquery/migrations/V005__gold_current_and_publication.sql \
  --templater raw --dialect bigquery
SQLFLUFF_PARSE_OK

uv run dbt parse --project-dir dbt/olist_bigquery \
  --profiles-dir dbt/olist_bigquery --no-partial-parse
dbt=1.11.8; adapter bigquery=1.11.3; parse passed

uv run ruff check tests/gcp/test_migrations.py
All checks passed!

uv run pyright tests/gcp/test_migrations.py
0 errors, 0 warnings, 0 informations

uv run python scripts/lab.py gcp migrate status
5 ordered migrations; status=ready; cloud_execution=NOT_RUN

uv run ruff check airflow/dags/olist_gcp_serving.py scripts/gcp/docker_api.py \
  scripts/gcp/bigquery_runtime.py scripts/serving/bigquery_control.py \
  tests/airflow/test_gcp_dag_contract.py tests/gcp/test_docker_api.py \
  tests/gcp/test_bigquery_runtime.py tests/serving/test_bigquery_control.py \
  tests/orchestration/test_compose_render.py
All checks passed!

uv run pyright airflow/dags/olist_gcp_serving.py scripts/gcp/docker_api.py \
  scripts/gcp/bigquery_runtime.py scripts/serving/bigquery_control.py \
  tests/airflow/test_gcp_dag_contract.py tests/gcp/test_docker_api.py \
  tests/gcp/test_bigquery_runtime.py tests/serving/test_bigquery_control.py \
  tests/orchestration/test_compose_render.py
0 errors, 0 warnings, 0 informations

uv run pytest tests/airflow/test_gcp_dag_contract.py \
  tests/gcp/test_docker_api.py tests/gcp/test_bigquery_runtime.py \
  tests/serving/test_bigquery_control.py \
  tests/orchestration/test_compose_render.py -q
25 passed, 2 warnings

Direct DAG import with `runpy` passed and produced 11 tasks. The standard
Airflow `DagBag` path is not usable on this Windows host because Airflow
imports POSIX-only `fcntl`; this is an environment limitation, so the DAG is
validated through direct import and the contract test instead.

`docker compose --profile core --profile lakehouse-gcp config --format json`
passed, and `uv lock --check` passed after adding the BigQuery client to the
Airflow image dependency set.
```

The pytest warning is the existing Windows cache-directory permission
warning. It does not affect test execution.

## Documentation basis

The procedure syntax and transaction safeguards were checked against the
Google Developer Knowledge MCP documentation for [multi-statement
transactions](https://docs.cloud.google.com/bigquery/docs/transactions), the
[procedural language](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language),
[`@@row_count`](https://docs.cloud.google.com/bigquery/docs/reference/system-variables),
and [clustered and partitioned table DDL](https://docs.cloud.google.com/bigquery/docs/creating-clustered-tables).

## Required cloud closeout

Before WP10 can be marked fully complete, execute and record:

1. V001–V005 application and migration-ledger evidence in the real project;
2. procedure execution for initial, incremental, same-run retry, stale
   predecessor, injected DML failure, and compensating-run cases;
3. proof that a failed transaction leaves every current table, pointer, and
   status unchanged except for the explicitly recorded failure/conflict row;
4. real import/run evidence for `olist_gcp_serving` in the target Linux
   Airflow environment;
5. restricted Docker API and dbt artifact collection evidence, with no
   long-lived streaming owned by Airflow.
6. ADC/IAM validation for BigQuery, GCS/BigLake, the dbt candidate container,
   and the Docker socket proxy;
7. failure injection proving that compensation and lease cleanup work after
   container, dbt, query, and publication failures.

No cloud run ID exists because GCP access was intentionally unavailable.
