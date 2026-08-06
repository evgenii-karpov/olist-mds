# Target Architecture and Runtime Isolation

## 1. Local contour

```text
core services
  MySQL -> Debezium/Kafka Connect -> Kafka/Apicurio
  shared Spark master/workers
  Airflow + platform PostgreSQL + Prometheus/Grafana

lakehouse-local
  local Spark drivers
  -> Polaris REST catalog
  -> MinIO Iceberg (bronze/silver/reference/audit)
  -> ClickHouse serving projection
  -> dbt-clickhouse Gold
  -> local serving ledger in PostgreSQL
```

Local operation must remain possible with no ADC files, no `gcloud`, and no live GCP project.

## 2. GCP contour

```text
core services
  MySQL -> Debezium/Kafka Connect -> Kafka/Apicurio
  shared Spark master/workers
  Airflow + platform PostgreSQL + Prometheus/Grafana

lakehouse-gcp
  GCP Spark drivers
  -> Lakehouse runtime Iceberg REST catalog
  -> GCS Iceberg data + separate GCS checkpoints
  -> BigQuery bridge views
  -> dbt-bigquery per-run history/deltas
  -> BigQuery publication procedure
  -> materialized current-state tables
  -> stable olist_gold views
  -> GCP serving ledger in BigQuery
```

The GCP render must not contain active Polaris, MinIO, ClickHouse, or `dbt-clickhouse` services.

## 3. Compose profiles

| Profile | Main responsibilities |
|---|---|
| `core` | MySQL, Kafka, Kafka Connect, Apicurio, shared Spark cluster, Airflow, platform PostgreSQL, observability |
| `lakehouse-local` | Polaris, MinIO, local drivers, ClickHouse, local dbt runtime/bootstrap |
| `lakehouse-gcp` | GCP drivers, SQL migration runner, dedicated `dbt-bigquery` service |

Supported combinations:

```text
docker compose --profile core --profile lakehouse-local ...
docker compose --profile core --profile lakehouse-gcp ...
```

`lab.py` is responsible for validating that both lakehouse profiles are not selected together.

## 4. Spark isolation

The shared Spark cluster is accepted because contours are sequential. Isolation is supplied by:

- separate driver services;
- separate application/query IDs;
- separate catalog and warehouse configuration;
- separate checkpoint roots;
- separate ADC mounts;
- explicit streaming start/stop commands;
- no sink fan-out and no query that writes to both contours.

If concurrent operation becomes a future requirement, that is a new architecture decision requiring separate worker pools or clusters.

## 5. Repository layout

Recommended additive layout:

```text
infra/gcp/
  bootstrap/README.md
  dev/
    backend.tf
    versions.tf
    providers.tf
    variables.tf
    locals.tf
    services.tf
    storage.tf
    lakehouse.tf
    bigquery.tf
    iam.tf
    budgets.tf
    outputs.tf
    terraform.tfvars.example
    .terraform.lock.hcl

sql/bigquery/migrations/
  V001__control_tables.sql
  V002__bridge_views.sql
  V003__gold_history_and_current.sql
  V004__publication_procedure.sql
  V005__serving_views.sql

streaming/spark/
  platform/
  scala/src/main/scala/com/olist/mds/spark/
    config/
    ordering/
    ...

dbt/
  olist_clickhouse/
  olist_bigquery/

scripts/
  lab.py
  serving/
    boundary/
    control/
    readers/
    targets/
    parity/

airflow/dags/
  olist_local_serving.py
  olist_gcp_serving.py
```

The exact paths may follow current repository conventions, but the ownership boundaries are normative.
