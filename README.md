# Olist Modern Data Stack

Data engineering project built around the Olist Brazilian e-commerce dataset.
It demonstrates a reproducible batch analytics pipeline and a local
near-realtime CDC path.

The default local stack uses ClickHouse as the analytical warehouse. PostgreSQL
is still used locally for transactional services: Airflow metadata, the OLTP
source captured by Debezium, and the `olist_control` pipeline-control database.

## Current Capabilities

- Batch ingestion is implemented locally with filesystem raw storage,
  ClickHouse, Airflow, dbt, and Elementary.
- Batch ingestion is also implemented for AWS with S3, Redshift, Airflow, dbt,
  and the same logical raw-zone contract.
- CDC is implemented for the local Docker Compose stack only. It is not
  currently implemented for AWS.
- The local CDC path includes a deterministic OLTP workload simulator,
  Debezium/Kafka, Apicurio, MinIO, NiFi, ClickHouse raw CDC ingestion,
  realtime dbt models, quality checks, publication gates, and observability.
- Automated parity tests verify that the deterministic batch and CDC/realtime
  paths produce identical business outputs for the covered entities, item-grain
  fact, and marts.
- CI uses local, self-contained services and a committed fixture dataset to
  exercise ingestion, loading, reconciliation, dbt, batch idempotency, CDC
  contracts, and observability checks without cloud credentials.

## High-Level Flow

```text
Olist CSV archive
  -> Python ingestion and validation
  -> raw and dead-letter zones on local storage or S3
  -> ClickHouse raw_data locally, or Redshift raw_data on AWS
  -> dbt staging, intermediate, snapshots, core, and marts
  -> Elementary observability report
  -> Airflow-controlled quality gates
```

```text
Local OLTP PostgreSQL
  -> Debezium, Kafka, and Apicurio
  -> MinIO CDC landing and normalized objects
  -> NiFi validation, batching, and manifest publication
  -> ClickHouse raw_cdc locally
  -> dbt realtime transforms and parity checks
  -> PostgreSQL olist_control state transitions
```

## Repository Layout

```text
airflow/dags/          Local batch, AWS batch, and local CDC DAGs.
dbt/olist_analytics/   dbt project, tests, snapshots, macros, and profiles.
docker/                Local Airflow and ClickHouse container configuration.
infra/clickhouse/      Local ClickHouse database, raw, CDC, and runtime DDL.
infra/control-postgres/ PostgreSQL control-plane DDL for olist_control.
infra/oltp/            Local OLTP schema and CDC bootstrap assets.
infra/redshift/        AWS Redshift warehouse DDL and COPY templates.
observability/         Local Prometheus, Grafana, Alertmanager, Loki, and Alloy.
scripts/cdc/           CDC ingest, transforms, metrics, recovery, and benchmarks.
scripts/ingestion/     Source validation, raw preparation, and corrections.
scripts/loading/       ClickHouse and Redshift raw loaders plus replay helpers.
scripts/quality/       Reconciliation checks.
tests/                 Unit tests and the committed CI fixture dataset.
```

## Design Choices

- ClickHouse is the only supported local analytical warehouse.
- Redshift is the AWS analytical warehouse for batch execution.
- PostgreSQL is used locally for three non-analytical roles: Airflow metadata,
  the OLTP source captured by Debezium, and the `olist_control` batch/CDC
  control plane.
- Batch and CDC schemas are isolated and compared through explicit parity
  checks; they are never merged into one raw source of truth.
- Raw files and CDC objects are immutable and partitioned by entity, date, and
  run or manifest identity.
- Source-contract failures fail fast; record-level failures go to dead-letter
  files and can be replayed.
- Lifecycle state is stored in PostgreSQL control tables instead of relying only
  on Airflow UI state.
- dbt owns analytical transformations and data-quality checks after raw loading.

## Running Locally

Use the OS-specific runbook:

- [Windows runbook](docs/runbook_windows.md)
- [macOS runbook](docs/runbook_macos.md)

Local Docker runs use committed development-only Docker secret files by
default, so `docker compose up -d` works without creating a `.env` file. Copy
`.env.example` to `.env` only when you want to override local config, point
Compose at different secret files, or configure the AWS/Redshift path.

For AWS/Redshift execution, prefer standard AWS authentication resolution
(IAM role, SSO, shared config, or a short-lived local session). Sensitive values
such as the Redshift password and Airflow API secret key can be resolved inside
the Airflow container from AWS Secrets Manager by setting `*_AWS_SECRET_ID`
entries in `.env`.

## Data License

The repository includes the Olist Brazilian E-Commerce Public Dataset archive
for reproducible local runs. See [Data license](DATA_LICENSE.md) for source
attribution and license terms.

## Documentation

- [Architecture](docs/architecture.md)
- [Data model](docs/data_model.md)
- [CI quality gates](docs/ci.md)
- [Diagrams](docs/diagrams.md)
- [Source contract](docs/source_contract.md)
