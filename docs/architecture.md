# Target lakehouse architecture

## Scope

The repository implements a local, reproducible target stack for the Olist
dataset. MySQL is the only authoritative business source. The data-plane
boundary is:

```text
MySQL
  -> Debezium MySQL Connector / Kafka Connect
  -> Kafka + Apicurio Registry (Confluent-compatible Avro)
  -> Spark Structured Streaming
  -> Iceberg Bronze/Silver/Audit through Polaris
  -> ClickHouse serving boundary
  -> Airflow serving DAGs and dbt Gold candidate publication
```

MinIO provides the local S3-compatible storage adapter for Iceberg and Spark
checkpoints. It does not imply a cloud-provider deployment. PostgreSQL is
reserved for platform metadata and the `serving` control ledger.

## Data contracts

The eight captured MySQL entities have versioned contracts under
`streaming/schemas/contracts/`. Kafka topics, primary keys, Avro writer
fingerprints, Spark reader schemas and Iceberg projections are validated as one
contract. Bronze keeps the raw framed record and framing evidence. Silver owns
append-only changes and current projections. Normalization failures are
recorded in `audit.normalization_errors` or `audit.schema_violations`; a
rejected transaction remains visible to serving until a later valid completion
resolves it.

The durable Iceberg table inventory and migrations are defined in
`streaming/spark/platform/table_specs.py`. The serving boundary consumes only
effective transaction state and never publishes past an unresolved `OPEN` or
effective `REJECTED` transaction.

## Control and serving

`infra/control-postgres/initdb/` creates only the target `serving` schema.
`scripts/serving/control.py` owns leases, sync-run state, entity results and
runtime state. ClickHouse native DDL under `infra/clickhouse/lakehouse/` owns
the serving event/current-version projection; dbt under
`dbt/olist_clickhouse/` owns candidate Gold models and stable publication
views.

`scripts/cdc/local_lab.py` is the lifecycle boundary for the disposable
Compose project. It emits bounded redacted JSON and delegates business and
serving invariants to the target components. The full V0–V10 acceptance
runner is `scripts/validation/stage_v_candidate_e2e.py`.

## Observability

Prometheus, Alertmanager, Grafana, Loki and Alloy are target services with
explicit scrape owners, dashboards, alerts and runbooks. `target-probe` owns
bounded control-plane and serving signals; Kafka exporter owns target consumer
lag. Observability is validated separately by
`scripts/ci/validate_observability_contract.py` and the observability test
suite.

## Removed architecture

The repository no longer contains the former source, orchestration, raw-file
loader or analytical-project implementations. Historical design and migration
records under `docs/cdc/`, `docs/postgresql-to-clickhouse/`, `docs/plans/` and
`docs/reports/` are provenance, not active runtime instructions.
