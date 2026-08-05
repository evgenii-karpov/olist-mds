# Olist Modern Data Stack

An end-to-end local data platform built around CDC (change data capture) for
the Olist Brazilian e-commerce dataset. It captures changes from MySQL,
processes them as events, stores them in an Iceberg lakehouse and publishes
analytical data through ClickHouse.

## High-level architecture

```text
MySQL
  -> Debezium / Kafka Connect
  -> Kafka + Apicurio Registry
  -> Spark Structured Streaming
  -> Iceberg through Polaris on MinIO
  -> ClickHouse serving
  -> Airflow and dbt publication
```

The runtime is reproducible with Docker Compose. MySQL owns business data.
PostgreSQL stores Airflow metadata, Polaris catalog metadata and serving
control data.

## Key capabilities

- **CDC ingestion:** Debezium, Kafka Connect and Kafka transport source
  changes reliably between services.
- **Data contracts:** Avro and Apicurio Registry validate event structure,
  keys and schema compatibility.
- **Lakehouse processing:** Spark Structured Streaming writes Bronze, Silver
  and audit Iceberg tables.
- **Consistent serving:** the ClickHouse serving boundary prevents incomplete
  or rejected source transactions from being published.
- **Analytics:** Airflow coordinates serving operations and dbt builds
  ClickHouse dimensions, facts and analytical marts.
- **Operations:** lifecycle, recovery, rebuild, maintenance and validation
  procedures are documented and testable.
- **Observability:** metrics, alerts, dashboards and container logs are
  collected and validated as part of the platform.

## Technology stack

| Area                    | Technologies                                          | Purpose                                                               |
| ----------------------- | ----------------------------------------------------- | --------------------------------------------------------------------- |
| Source                  | MySQL 8.4                                             | Operational source of business entities and CDC transactions.         |
| CDC and transport       | Debezium MySQL Connector, Kafka Connect, Apache Kafka | Captures and transports source changes.                               |
| Contracts               | Apache Avro, Apicurio Registry                        | Defines event schemas and checks compatibility.                       |
| Processing              | Apache Spark Structured Streaming, Scala              | Decodes events and writes Iceberg tables.                             |
| Lakehouse               | Apache Iceberg, Apache Polaris, MinIO                 | Provides versioned tables, catalog metadata and local object storage. |
| Serving                 | ClickHouse                                            | Supports fast serving queries and analytical models.                  |
| Orchestration           | Apache Airflow                                        | Coordinates serving synchronization and maintenance.                  |
| Modeling                | dbt for ClickHouse                                    | Builds tested dimensions, facts and analytical marts.                 |
| Control plane           | PostgreSQL                                            | Stores orchestration, catalog and serving state.                      |
| Metrics                 | Prometheus, Kafka exporter, target-probe              | Monitors services, Kafka positions and CDC/serving health.            |
| Alerting and dashboards | Alertmanager, Grafana                                 | Routes alerts and presents operational views.                         |
| Logs                    | Grafana Alloy, Loki                                   | Collects and stores Docker container logs.                            |
| Quality and delivery    | Docker Compose, GitHub Actions, Pytest, Ruff, Pyright | Provides reproducible execution and automated validation.             |

## Engineering focus

- Contract-first integration and schema evolution.
- Layered lakehouse modeling with raw evidence, normalized state and audit
  records.
- Transaction-aware and idempotent serving operations.
- Recovery runbooks, deterministic fixtures and reviewable CI evidence.
- Secret-file based configuration with credentials excluded from logs and
  command arguments.

## Repository layout

```text
airflow/dags/             Serving and maintenance DAGs.
dbt/olist_clickhouse/     ClickHouse dbt project and model catalog.
docker/                   Runtime image definitions and local secrets.
infra/                    MySQL, PostgreSQL, Polaris and ClickHouse setup.
streaming/                Kafka, Debezium, schemas, Spark and MinIO resources.
scripts/cdc/              Local CDC lifecycle and validation helpers.
scripts/serving/          ClickHouse serving boundary and control code.
scripts/simulation/       Deterministic MySQL fixture simulator.
observability/            Metrics, alerts, dashboards and log collection.
tests/                    Component contracts and local acceptance tests.
docs/                     Architecture, data model, CI and operational guides.
```

## Documentation

Operational commands are kept in the platform runbooks:

- [Windows runbook](docs/runbook_windows.md)
- [macOS and Linux runbook](docs/runbook_macos.md)
- [All operational runbooks](docs/runbooks/)

Architecture and design references:

- [Architecture](docs/architecture.md)
- [Architecture diagrams](docs/diagrams.md)
- [Data model](docs/data_model.md)
- [Source contract](docs/source_contract.md)
- [CI and validation](docs/ci.md)
- [Observability](docs/observability.md)
- [ClickHouse model catalog](dbt/olist_clickhouse/MODEL_CATALOG.md)
- [Data license](DATA_LICENSE.md)
