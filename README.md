# Olist Modern Data Stack

Data engineering project built around the Olist Brazilian e-commerce dataset.
The local stack is moving from PostgreSQL to ClickHouse as the analytical
warehouse. The migration plan is tracked in
[Local PostgreSQL-to-ClickHouse Warehouse Migration Plan](docs/plans/local-clickhouse-warehouse-migration-plan.md).

The project remains fully reviewable without cloud access. PostgreSQL is still
used locally where transactional semantics are required: Airflow metadata, the
OLTP source captured by Debezium, and the `olist_control` pipeline-control
database. During the migration, PostgreSQL also remains available as the local
analytical oracle for parity checks. The AWS path remains a batch-oriented
S3/Redshift path; local CDC has been implemented with Docker Compose services
and is not currently implemented for AWS.

## What It Demonstrates

- End-to-end batch pipeline from CSV archive to analytics marts.
- Deterministic raw-zone contract that can map to local files or object
  storage.
- Local ClickHouse analytical warehouse migration with PostgreSQL retained as a
  temporary oracle during parity validation.
- Parallel Airflow DAG variants for local warehouse runs and AWS Redshift batch
  runs.
- Row-level validation, dead-letter files, threshold checks, and replay support.
- PostgreSQL control-plane tables for batch state, raw load attempts,
  reconciliation, CDC claims, watermarks, transform state, dead-letter events,
  and replays.
- Airflow orchestration with clear task boundaries and parameterized batch
  runs.
- dbt layers for staging, intermediate logic, snapshots, core dimensions/facts,
  and business marts.
- Local CDC pipeline with OLTP PostgreSQL, Debezium/Kafka, Apicurio, MinIO,
  NiFi, typed warehouse ingestion, realtime dbt transforms, quality gates, and
  ClickHouse-backed observability scaffolding.
- Elementary data observability with collected dbt artifacts, test results, and
  an automated observability report after dbt builds.
- SCD Type 2 customer and product dimensions using deterministic correction
  feeds.
- Incremental fact loading with late-arriving data handling.
- Small committed fixture dataset and CI gates that exercise the real pipeline
  path quickly.

## High-Level Flow

```text
Olist CSV archive
  -> Python ingestion and validation
  -> raw and dead-letter zones on local storage or S3
  -> ClickHouse raw_data locally, or Redshift raw schemas on AWS
  -> dbt staging, intermediate, snapshots, core, and marts
  -> Elementary observability schema and report
  -> Airflow-controlled quality gates
```

```text
Local OLTP PostgreSQL
  -> Debezium, Kafka, and Apicurio
  -> MinIO CDC landing objects
  -> NiFi normalization and manifest publication
  -> ClickHouse raw_cdc locally
  -> dbt realtime transforms and parity checks
  -> PostgreSQL olist_control state transitions
```

## Repository Layout

```text
airflow/
  dags/                 Local and AWS Airflow DAGs with warehouse-specific
                        dbt targets and CDC orchestration.

dbt/
  olist_analytics/      dbt project: sources, models, snapshots, tests,
                        analyses, macros, and profile example.

docker/
  airflow/              Airflow image and container entrypoint for local and AWS runs.
  clickhouse/           Local ClickHouse server configuration.

docs/
  architecture.md       System design, orchestration, audit, and reliability.
  data_model.md         Dimensional model, grains, SCD2, facts, and marts.
  ci.md                 GitHub Actions quality-gate strategy.
  diagrams.md           Mermaid architecture and data model diagrams.
  source_contract.md    Generated source-file contract from the Olist archive.
  runbook_macos.md      macOS local setup and execution commands.
  runbook_windows.md    Windows local setup and execution commands.

infra/
  clickhouse/           ClickHouse local database, raw, CDC, and runtime DDL.
  control-postgres/     PostgreSQL control-plane DDL for Airflow-hosted
                        olist_control.
  postgres/             PostgreSQL warehouse DDL for schemas, raw tables, audit,
                        and correction tables during the oracle period.
  redshift/             Redshift warehouse DDL and COPY templates.

observability/          Local Prometheus, Grafana, Alertmanager, Loki, and
                        dashboard/rule configuration.

scripts/
  cdc/                  CDC control, warehouse ingest, realtime transform, and
                        operational helpers.
  ingestion/            Source validation, raw file preparation, corrections.
  loading/              PostgreSQL, ClickHouse, and Redshift raw load helpers.
  orchestration/        Batch-control helpers.
  parity/               Cross-engine oracle/candidate manifest export and
                        comparison utilities.
  quality/              Reconciliation checks.
  testing/              Fixture generation.
  utilities/            Profiling, validation, and helper scripts.

tests/
  fixtures/olist_small/ Small synthetic fixture used by CI.
  test_*.py             Python tests for ingestion, dead-letter handling,
                        replay behavior, and CI failure modes.
```

## Main Design Choices

- The local analytical warehouse is migrating to ClickHouse. PostgreSQL is
  temporarily retained as the analytical oracle until the ClickHouse cutover is
  complete.
- PostgreSQL remains the right local store for Airflow metadata, the Debezium
  OLTP source, and transactional pipeline-control state.
- The AWS/Redshift path is batch-oriented and remains supported separately from
  the local ClickHouse migration.
- CDC is implemented for the local Docker Compose stack only. AWS CDC is not a
  current supported path.
- Raw files are immutable and partitioned by entity, batch date, and run id.
- Structural source-contract failures fail fast, while record-level failures
  are isolated in the dead-letter zone.
- Batch and CDC lifecycle state is stored in PostgreSQL control tables instead
  of relying only on Airflow UI state.
- Reconciliation runs before dbt so silent data loss or duplicate raw loads stop
  the pipeline early.
- dbt owns analytical modeling and data quality checks after the raw load.
- Elementary adds dbt observability while keeping dependencies pinned and
  resolved before Airflow runs.
- CI uses local, self-contained services so pull-request checks remain
  reproducible and independent of cloud infrastructure.
- CI uses a small deterministic fixture while still covering the real
  ingestion, loading, reconciliation, and dbt path.
- Phase 7 CI also compiles ClickHouse candidate selectors, uploads
  oracle/candidate comparator artifacts, and validates ClickHouse Prometheus
  coverage while preserving the PostgreSQL oracle until cutover.

## Running Locally

Use the OS-specific runbook:

- [Windows runbook](docs/runbook_windows.md)
- [macOS runbook](docs/runbook_macos.md)

Both runbooks cover dependency setup, Docker Compose, manual smoke runs, the
Airflow DAG, dbt execution, CI-style fixture validation, and cleanup. The
ClickHouse migration plan documents the staged local warehouse cutover and the
local-only CDC scope.

Local Docker runs use committed development-only Docker secret files by
default, so `docker compose up -d` works without creating a `.env` file. Copy
`.env.example` to `.env` only when you want to override local config, point
Compose at different secret files, or configure the AWS/Redshift path.

For AWS/Redshift execution, prefer standard AWS authentication resolution
(IAM role, SSO, shared config, or a short-lived local session) together with
the optional runtime configuration in `.env`. Sensitive values such as the
Redshift password and Airflow API secret key can be resolved inside the Airflow
container from AWS Secrets Manager by setting `*_AWS_SECRET_ID` entries in
`.env`.

## Data License

The repository includes the Olist Brazilian E-Commerce Public Dataset archive
for reproducible local runs. See [Data license](DATA_LICENSE.md) for source
attribution and license terms.

## More Documentation

- [Architecture](docs/architecture.md)
- [Data model](docs/data_model.md)
- [CI quality gates](docs/ci.md)
- [Diagrams](docs/diagrams.md)
- [Source contract](docs/source_contract.md)
