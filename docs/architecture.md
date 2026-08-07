# Local CDC architecture

## Data flow

The local runtime moves source changes through one path:

```text
MySQL
  -> Debezium MySQL Connector / Kafka Connect
  -> Kafka and Apicurio Registry
  -> Spark Structured Streaming
  -> Iceberg Bronze, Silver and audit tables
  -> ClickHouse serving tables
  -> Airflow serving operations and dbt models
```

Polaris provides the Iceberg catalog. MinIO stores Iceberg data and Spark
checkpoints. They run as local Compose services.

## Component responsibilities

| Component                                         | Responsibility                                                                         |
| ------------------------------------------------- | -------------------------------------------------------------------------------------- |
| MySQL                                             | Authoritative Olist business source and CDC transaction source.                        |
| PostgreSQL                                        | Airflow metadata, Polaris catalog metadata and serving control data.                   |
| Debezium / Kafka Connect                          | Reads MySQL changes and publishes the CDC envelope.                                    |
| Kafka                                             | Carries entity, transaction, heartbeat and schema-history topics.                      |
| Apicurio Registry                                 | Stores and validates the Avro key and value schemas.                                   |
| Spark                                             | Decodes CDC records, writes Bronze/Silver Iceberg tables and records processing state. |
| Polaris / MinIO                                   | Catalogs and stores Iceberg tables and checkpoints.                                    |
| ClickHouse                                        | Stores the serving projection and published analytical models.                         |
| Airflow                                           | Runs serving sync, rebuild and maintenance operations.                                 |
| dbt                                               | Builds ClickHouse candidate models and stable publication views.                       |
| Prometheus, Alertmanager, Grafana, Loki and Alloy | Collect, route, display and retain local telemetry.                                    |

The business source remains in MySQL. PostgreSQL is not a business-data store.

## Data boundaries

The eight keyed source entities captured by the connector have versioned
contracts in `streaming/schemas/contracts/`. Bronze preserves the transport
identity and framing evidence. Silver owns normalized event records and
current projections. Invalid records remain visible in the audit tables.

The serving planner publishes only a complete transaction prefix. An `OPEN`
or `REJECTED` transaction blocks publication at that boundary. The control
schema in `infra/control-postgres/` records serving leases, sync runs,
entity results and publication state.

## Local lifecycle

[`scripts/lab.py`](../scripts/lab.py) is the normative target-scoped lifecycle
entry point. It delegates the existing local implementation to
[`scripts/cdc/local_lab.py`](../scripts/cdc/local_lab.py), which remains a
compatibility surface for detailed local operations and the acceptance
harness. Each command emits one redacted JSON result.

Compose profiles group the runtime:

| Profile         | Services                                                         |
| --------------- | ---------------------------------------------------------------- |
| `core`          | MySQL, PostgreSQL, Kafka, Apicurio and shared Spark.             |
| `lakehouse-local` | Polaris, MinIO, local Spark drivers, ClickHouse and local Airflow. |
| `lakehouse-gcp` | GCP Airflow shell and the future GCP drivers/dbt services.       |
| `platform`      | Legacy alias for the local/core bootstrap combination.           |
| `streaming`     | Explicit local streaming drivers.                                |
| `serving`       | Legacy alias for local serving services.                         |
| `observability` | Prometheus, Alertmanager, Grafana and target probe.              |
| `logs`          | Loki and Alloy.                                                  |

The acceptance runner does not start observability services. Start the
observability and log profiles explicitly when telemetry is being checked.
The local and GCP lakehouse profiles are mutually exclusive; `gcp up` does
not select a streaming profile.
