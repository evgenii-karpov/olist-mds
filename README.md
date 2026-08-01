# Olist Modern Data Stack

Data engineering project built around the Olist Brazilian e-commerce dataset.
It demonstrates a reproducible batch analytics pipeline and the Wave 1
MySQL-to-Iceberg CDC foundation.

The candidate CDC runtime uses MySQL as the only OLTP source, Kafka and
Apicurio for transport/schema identity, and Spark/Iceberg on MinIO through the
Polaris REST catalog. PostgreSQL remains only a control plane for Airflow,
Polaris, Apicurio, and `olist_control`.

## Current Capabilities

- Batch ingestion is implemented locally with filesystem raw storage,
  ClickHouse, Airflow, dbt, and Elementary.
- Batch ingestion is also implemented for AWS with S3, Redshift, Airflow, dbt,
  and the same logical raw-zone contract.
- Wave 1 includes deterministic MySQL source/bootstrap assets, exact Kafka and
  Apicurio contracts, Polaris/MinIO credential projections, Spark/Iceberg table
  migration, and the ClickHouse/dbt serving skeleton.
- Wave 2 entity normalizers, Silver streaming, Airflow publication, serving
  sync, and final parity are intentionally deferred.
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
MySQL OLTP
  -> Debezium MySQL / Kafka Connect
  -> Kafka + Apicurio Confluent-framed Avro
  -> Spark Structured Streaming foundation
  -> Iceberg Bronze/Silver on MinIO through Polaris
  -> finite ClickHouse serving sync (deferred)
```

## Repository Layout

```text
airflow/dags/          Local batch, AWS batch, and local CDC DAGs.
dbt/olist_analytics/   dbt project, tests, snapshots, macros, and profiles.
docker/                Local Airflow, Spark, and ClickHouse configuration.
infra/mysql/           MySQL source schema, simulator control schema, and users.
infra/polaris/         Polaris, MinIO, PostgreSQL, and credential projections.
infra/clickhouse/      Native serving DDL and Iceberg DataLakeCatalog bootstrap.
infra/control-postgres/ PostgreSQL control-plane DDL for olist_control.
infra/redshift/        AWS Redshift warehouse DDL and COPY templates.
observability/         Local Prometheus, Grafana, Alertmanager, Loki, and Alloy.
scripts/cdc/           The Wave 1 lifecycle CLI and deferred CDC helpers.
scripts/ingestion/     Source validation, raw preparation, and corrections.
scripts/loading/       ClickHouse and Redshift raw loaders plus replay helpers.
scripts/quality/       Reconciliation checks.
tests/                 Unit tests and the committed CI fixture dataset.
```

## Design Choices

- ClickHouse is the local serving/Gold warehouse; Iceberg is the durable CDC
  source of truth.
- Redshift is the AWS analytical warehouse for batch execution.
- MySQL is the authoritative OLTP source. PostgreSQL is restricted to control
  plane databases; business tables never live there.
- Batch and CDC schemas are isolated and compared through explicit parity
  checks; they are never merged into one raw source of truth.
- Raw files and CDC objects are immutable and partitioned by entity, date, and
  run or manifest identity.
- Source-contract failures fail fast; record-level failures go to dead-letter
  files and can be replayed.
- All Wave 1 persisted services use one disposable Compose consistency domain.
- Warehouse credentials are vended by Polaris; Spark receives static MinIO
  credentials only for the isolated checkpoint bucket.
- dbt owns analytical transformations and data-quality checks after raw loading.

## Running Locally

Use the Wave 1 lifecycle CLI:

```powershell
uv sync --all-groups
python scripts/cdc/local_lab.py doctor
python scripts/cdc/local_lab.py reset --yes
python scripts/cdc/local_lab.py bootstrap --archive tests/fixtures/olist_small/olist_small.zip
python scripts/cdc/local_lab.py status
```

`start-streaming`, `wait-caught-up`, serving, maintenance, and parity commands
remain explicit structured non-zero guards until J2/E. The legacy stack remains
in the repository for later parity work but is not part of the Wave 1 profiles.

For the older batch workflow, use the OS-specific runbook:

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
