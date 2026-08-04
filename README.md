# Olist Modern Data Stack

Local-first lakehouse for the Olist Brazilian e-commerce dataset. The target
runtime has one authoritative business source and one serving path:

```text
MySQL -> Debezium/Kafka Connect -> Kafka + Apicurio
      -> Spark Structured Streaming -> Iceberg/Polaris on MinIO
      -> ClickHouse serving -> Airflow/dbt publication
```

MySQL owns business data. PostgreSQL is limited to the platform and serving
control planes. MinIO is the local S3-compatible adapter for Iceberg; no
external cloud warehouse runtime is part of this repository.

## Repository layout

```text
airflow/dags/             Target maintenance and serving DAGs.
dbt/olist_clickhouse/     Target ClickHouse dbt project.
docker/                   Airflow, Spark and runtime image definitions.
infra/mysql/              MySQL source schema, CDC user and simulator users.
infra/control-postgres/   Serving control ledger migrations.
infra/polaris/             Polaris catalog and MinIO bootstrap.
infra/clickhouse/lakehouse/ Native serving DDL and catalog smoke checks.
streaming/connect/         Debezium MySQL connector image and bootstrap.
streaming/kafka/           Target topic manifest and topic bootstrap.
streaming/schemas/         Versioned Avro/entity contracts and writer evidence.
streaming/spark/           Bronze/Silver/ops/replay data plane.
scripts/cdc/               Target lifecycle and bounded CDC operations.
scripts/serving/           ClickHouse serving boundary and control repository.
scripts/simulation/        Deterministic MySQL fixture seeding and workload.
observability/             Prometheus, Alertmanager, Grafana, Loki and Alloy.
tests/                     Target contract suites and frozen acceptance fixtures.
```

## Local validation

Install the locked environment and inspect prerequisites:

```powershell
uv sync --all-groups
uv run python scripts/cdc/local_lab.py doctor
```

Run a clean bounded bootstrap:

```powershell
uv run python scripts/cdc/local_lab.py reset --yes
uv run python scripts/cdc/local_lab.py bootstrap `
  --archive tests/fixtures/olist_small/olist_small.zip `
  --run-id local-small-seed
uv run python scripts/cdc/local_lab.py status --require platform
```

The authoritative full acceptance command is:

```powershell
uv run python scripts/validation/stage_v_candidate_e2e.py run `
  --run-id local-stage-v `
  --evidence-dir data/stage-l-evidence/manual/local-stage-v `
  --confirm-reset
```

For component-specific checks, use the target test suites named in
`docs/plans/lakehouse/contracts/testing-and-evidence.md`. Observability has a
separate contract validator and is not implicitly started by the Stage V
runner.

## Documentation

- [Architecture](docs/architecture.md)
- [Target source contract](docs/source_contract.md)
- [CI and validation contract](docs/plans/lakehouse/contracts/validation-and-ci.md)
- [Observability contract](docs/plans/lakehouse/contracts/observability.md)
- [Stage L plan](docs/plans/lakehouse/completed/stage-l-legacy-removal-ci-cutover.md)
- [Data license](DATA_LICENSE.md)
