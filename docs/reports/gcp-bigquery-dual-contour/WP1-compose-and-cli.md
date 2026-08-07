# WP1 — Compose profiles and lifecycle CLI report

Date: 2026-08-07
Branch: `gcp-bigquery-dual-contour`

## Status

**WP1 is complete for the credential-free checks available without GCP
access.**

The Compose ownership boundaries, profile exclusivity contract, target-scoped
CLI and split PostgreSQL bootstraps are implemented. The local contour has
been revalidated end to end after the bootstrap split. Cloud preflight and
actual GCP execution remain intentionally pending.

## Implemented

- Added canonical `core`, `lakehouse-local` and `lakehouse-gcp` profile
  contracts, with explicit local `streaming` and reserved GCP
  `streaming-gcp` lifecycle profiles.
- Kept `platform` and `serving` as compatibility aliases so existing local
  runbooks and acceptance tooling continue to work.
- Moved common PostgreSQL bootstrap to Airflow/Apicurio only; control and
  Polaris database initialization now run in separate local-only bootstrap
  services with explicit secret inheritance.
- Kept Polaris, MinIO, local Spark drivers, ClickHouse and local Airflow out
  of the active GCP render. Added an `airflow-gcp` shell with only shared
  PostgreSQL/API secrets and the documented BigLake REST catalog defaults.
- Added `scripts/lab.py` with local compatibility delegation, GCP preflight,
  contour lifecycle, explicit streaming commands and Terraform command
  guards. `gcp up` never selects a streaming profile; GCP streaming start is
  blocked until the GCP Spark drivers are delivered in WP4.
- Added unit tests and Docker-backed render tests for profile exclusivity,
  active service ownership, secret leakage and the GCP-up streaming boundary.

The GCP Airflow defaults follow the current Google Developer Knowledge MCP
documentation for the BigLake Iceberg REST catalog endpoint and credential
vending configuration:

- [Set up the Apache Iceberg REST catalog](https://docs.cloud.google.com/lakehouse/docs/set-up-lakehouse-iceberg-rest-catalog)
- [Query Iceberg tables with the Lakehouse runtime catalog](https://docs.cloud.google.com/lakehouse/docs/query-iceberg-tables-with-lakehouse)

No cloud API call was made by the repository changes or local checks.

## Evidence

### Static and render checks

Passed:

```text
uv run pre-commit run --all-files
Ruff, Ruff format, Pyright and dbt-parse: Passed

uv run pytest -q tests/orchestration \
  tests/lakehouse_platform/test_local_lab_profile_boundaries.py
15 passed

docker compose --profile core --profile lakehouse-local config --quiet
PASS

docker compose --profile core --profile lakehouse-gcp config --quiet
PASS

docker compose --profile platform --profile streaming --profile serving \
  --profile observability config --quiet
PASS
```

The GCP service inventory contains shared source/Kafka/Spark services and
`airflow-gcp`, but no active Polaris, MinIO, ClickHouse, local Airflow or
local serving secrets. The local render succeeds with GCP environment inputs
unset.

### CLI preflight

With no project, region, ADC file or `gcloud` executable configured:

```text
uv run python scripts/lab.py gcp preflight
status=blocked
missing=project_id, region, adc_file, gcloud

uv run python scripts/lab.py gcp up
status=blocked
```

This is the expected credential-free behavior. Terraform availability is
reported separately; no Terraform operation was invoked in WP1.

### Full local CDC acceptance

Evidence:

- Run ID: `wp1-local-acceptance-r4`
- Report: `data/acceptance/local-cdc/wp1-local-acceptance-r4/report.md`
- Compose project: `olist_local_cdc_acceptance`
- Result: `11/11` mandatory gates passed
- Started: `2026-08-07T01:41:02.817235+00:00`
- Finished: `2026-08-07T01:57:25.439533+00:00`

The clean-domain run passed bootstrap, initial snapshot, CRUD/restart,
catch-up, serving sync, dbt/stable views, additive schema evolution, rebuild
and final consistency gates. Acceptance cleanup removed the project-scoped
containers and volumes.

## Remaining checks

1. GCP `gcloud`/ADC preflight with real project inputs.
2. Terraform `init -backend=false`, `validate` and later plan/apply after WP3
   adds `infra/gcp/dev`.
3. GCP Spark drivers, migrations and dedicated `dbt-bigquery` service in WP4+
   and later work packages.
4. Cloud contour acceptance and parity against real BigQuery/Lakehouse data.

No GCP credentials, resources, Terraform apply, BigQuery job or BigLake read
was used for this package.
