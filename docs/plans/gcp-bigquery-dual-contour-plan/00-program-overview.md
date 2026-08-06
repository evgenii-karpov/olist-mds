# Program Overview

## 1. Objective

Add a permanent GCP contour without replacing, simplifying, or demoting the existing local contour.

```text
LOCAL
MySQL -> Debezium/Kafka Connect -> Kafka/Apicurio -> local Spark cluster
      -> Polaris REST catalog -> MinIO Iceberg
      -> ClickHouse projection -> dbt-clickhouse Gold
      -> local serving state in PostgreSQL

GCP
MySQL -> Debezium/Kafka Connect -> Kafka/Apicurio -> the same local Spark cluster
      -> Google Lakehouse runtime Iceberg REST catalog -> GCS Iceberg
      -> BigQuery bridge views -> dbt-bigquery incremental history/deltas
      -> one BigQuery publication transaction -> materialized current Gold
      -> stable BigQuery serving views and BigQuery-native control state
```

Only one contour is active at a time. The shared Spark master/worker pool is therefore an accepted resource optimization, not a claim of compute failure isolation.

## 2. Scope

The primary plan includes the complete cloud data path:

- local MySQL, Debezium, Kafka Connect, Kafka, Apicurio, Spark, Airflow, and observability;
- GCS Iceberg data and Structured Streaming checkpoint storage;
- Google Lakehouse runtime catalog with the Iceberg REST endpoint and credential vending;
- BigQuery bridge, Gold store, serving views, control state, SQL migrations, and publication procedure;
- a separate `dbt-bigquery` project and runtime container;
- separate local and GCP serving DAGs;
- local CLI operations through `scripts/lab.py`;
- repeatable cross-contour parity reporting.

Live cloud integration tests in GitHub Actions are out of scope for the first implementation. CI remains credential-free and performs static cloud checks only.

## 3. Program invariants

1. Local operation requires no GCP credentials and no live GCP resources.
2. GCP operation requires no active Polaris, MinIO, ClickHouse, or local-lakehouse bootstrap.
3. Only `core + lakehouse-local` or `core + lakehouse-gcp` is supported; never both lakehouse profiles simultaneously.
4. The Iceberg namespaces remain `bronze`, `silver`, `reference`, and `audit`.
5. Spark is the sole schema authority and writer for repository-owned Iceberg tables.
6. BigQuery consumes Iceberg through stable bridge views and does not mutate Bronze, Silver, Reference, or Audit.
7. A serving run is based on a frozen, transaction-complete Kafka prefix.
8. Missing or incomplete transaction metadata blocks serving publication.
9. Incremental Gold is derived from the exact Silver change interval between the prior and current boundaries, not from `updated_at` lookbacks.
10. BigQuery publication is all-or-nothing across all Gold models and control-state updates.
11. The local and BigQuery serving ledgers are physically separate: PostgreSQL for local, BigQuery for GCP.
12. Cross-contour parity is a separate acceptance operation and is not a prerequisite for every individual GCP publication.
13. Real monetary spend must remain zero: use a Free Trial account, never upgrade it to paid billing, apply query limits, and remove resources before credits or trial time expire.

## 4. Stage graph

```text
WP0  Baseline, ordering, and timestamp contract
  -> WP1  Compose/profile and CLI redesign
  -> WP2  Target-scoped serving-control separation
  -> WP3  GCP bootstrap and flat Terraform root
  -> WP4  Catalog, Spark backend, and runtime dependencies
  -> WP5  Blocking four-table vertical slice
       -> NO-GO: stop and redesign after diagnosing the actual failure
       -> GO / GO-WITH-CONSTRAINTS
          -> WP6  Full GCP Iceberg lakehouse
          -> WP7  BigQuery datasets, migrations, and bridge views
          -> WP8  Transaction-boundary serving planner
          -> WP9  Incremental dbt-bigquery Gold history/deltas
          -> WP10 Atomic current-state publication and Airflow DAG
          -> WP11 Parity, observability, CI, and cost evidence
          -> WP12 Operations, documentation, and final acceptance
```

## 5. Blocking gates

| Gate | Required evidence | Blocks |
|---|---|---|
| G0 Baseline pinned | Baseline SHA, local acceptance evidence, current model/table inventory | All refactoring |
| G1 Ordering corrected | Canonical ordering implemented; malformed coordinates fail closed; rebuilt local fixture | Cloud Silver and Gold |
| G2 Runtime isolation | Compose renders cleanly for each profile; GCP path has no Polaris/MinIO dependency | Cloud runtime |
| G3 Infrastructure ready | State bootstrap, flat Terraform root, IAM and buckets verified | Vertical slice |
| G4 Vertical slice accepted | Four representative tables, BigQuery P.C.N.T reads, bridge views, restart, types, costs | Full cloud port |
| G5 Full lakehouse ready | All Iceberg tables and progress contracts validated | dbt-bigquery |
| G6 Publication safe | Same-run retry, stale-run conflict, all-or-nothing current-state update proven | Production-style serving |
| G7 Semantic parity | Repeatable JSON/Markdown parity report passes for a frozen boundary | Program completion |

## 6. Definition of completion

The program is complete when:

- both contours can be brought up, operated, and torn down independently;
- the local path still passes its existing tests and acceptance workflows;
- the GCP path can start from a clean MySQL/Debezium/Kafka history and reach published BigQuery Gold;
- the BigQuery current state is built incrementally after the first full run;
- failed, stale, or retried runs cannot partially alter published state;
- source ordering, timestamps, decimals, deletes, SCD2 state, aggregates, and late-arriving corrections behave consistently;
- parity produces machine-readable and Markdown evidence;
- the documented cleanup sequence leaves no main-contour GCP resources behind while preserving the manually bootstrapped Terraform state bucket until explicitly removed.
