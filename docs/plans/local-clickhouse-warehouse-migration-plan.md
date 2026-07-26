# Local PostgreSQL-to-ClickHouse Warehouse Migration Plan

## Document Control

| Field                    | Value                                                        |
| ------------------------ | ------------------------------------------------------------ |
| Status                   | Approved implementation plan                                 |
| Last updated             | 2026-07-19                                                   |
| Repository               | `olist-mds`                                                  |
| Primary audience         | AI implementation agents and maintainers                     |
| Scope                    | Local analytical warehouse only                              |
| Target warehouse         | ClickHouse 26.3 LTS                                          |
| AWS warehouse            | Amazon Redshift, unchanged                                   |
| Delivery strategy        | Temporary dual run, then remove the local PostgreSQL target  |
| Existing data strategy   | Rebuild from source files and immutable CDC landing objects  |
| Optimization strategy    | Establish semantic parity first, then tune measured hotspots |
| Related plans            | `docs/plans/near-realtime-cdc-implementation-plan.md`        |
| Related integration test | `docs/plans/batch-realtime-parity-integration-test-plan.md`  |

This document is the source of truth for replacing the local PostgreSQL
analytical warehouse with ClickHouse. It is intentionally self-contained. An
implementation agent must be able to execute it without access to the
conversation that produced it.

The migration applies to both the local batch and near-realtime analytical
paths. It does not remove PostgreSQL where PostgreSQL is serving a transactional
purpose: the Airflow metadata database, the OLTP source captured by Debezium,
and a small pipeline control database remain PostgreSQL.

## 1. Executive Summary

The repository currently uses one PostgreSQL container as the local analytical
warehouse. That database serves several distinct responsibilities:

1. batch raw tables and dbt-derived analytical models;
2. typed, append-only CDC event tables;
3. batch audit records;
4. CDC file claims, leases, watermarks, reconciliation, and publication state;
5. queries used by local quality gates and the CDC Prometheus exporter.

ClickHouse is an appropriate replacement for the first two responsibilities,
but not for the transactional coordination semantics in the remaining
responsibilities. The target architecture therefore separates the analytical
data plane from the control plane:

```text
Batch files -------------------------> ClickHouse raw_data
                                            |
CDC Parquet in MinIO ---------------> ClickHouse raw_cdc
                                            |
                                            v
                              shared dbt project
                         staging -> core -> marts
                                            |
                                            v
                              ClickHouse analytics

Airflow metadata --------------------> PostgreSQL database: airflow
Batch/CDC locks and state -----------> PostgreSQL database: olist_control
OLTP source for Debezium ------------> PostgreSQL service: oltp-postgres
AWS analytical path -----------------> Amazon Redshift
```

The existing `airflow-postgres` server will host `olist_control` as a separate
database with separate credentials. ClickHouse will not query that database
through a PostgreSQL table engine. Python tasks will query control state
directly, while dbt will query ClickHouse only.

The migration will temporarily retain PostgreSQL as an oracle. Both targets
will process deterministic fixtures in isolated environments, and a canonical
comparator will prove semantic equivalence. After two consecutive successful
end-to-end candidate runs, ClickHouse becomes the only supported local
analytical warehouse and the `local_pg` target and warehouse PostgreSQL service
are removed.

## 2. Current Repository Baseline

Implementation must begin by confirming this baseline. If the repository has
changed, update this document before changing the design.

### 2.1 Docker Compose services

`compose.yaml` currently defines:

- `postgres`, using PostgreSQL 18.4, as the local analytical warehouse;
- `airflow-postgres`, using PostgreSQL 17.10, as the Airflow metadata store;
- `airflow`, with `DBT_TARGET=local_pg` and `POSTGRES_*` pointing to the
  analytical warehouse;
- `oltp-postgres` under the `realtime-core` profile as the Debezium source;
- `cdc-warehouse-init`, which bootstraps `infra/postgres` into the analytical
  PostgreSQL database;
- Kafka, Kafka Connect, Apicurio, MinIO, NiFi, and their initialization
  services for the local CDC path;
- Prometheus, Grafana, Alertmanager, Loki, StatsD exporter, PostgreSQL
  exporters, and the custom CDC pipeline exporter under observability
  profiles.

The MinIO API already uses host port `9000`. A ClickHouse native protocol port
must therefore not be published as host port `9000`.

### 2.2 Batch path

The local batch DAG is
`airflow/dags/olist_modern_data_stack_local.py`.

It currently:

1. validates the Olist source archive;
2. prepares source and correction files;
3. manages `audit.batch_runs` through
   `scripts/orchestration/batch_control.py`;
4. loads gzip CSV files with
   `scripts/loading/load_raw_to_postgres.py`;
5. reconciles source and warehouse counts with
   `scripts/quality/reconcile_batch.py`;
6. runs `dbt build --selector batch`;
7. generates an Elementary report.

The loader uses `psycopg2`, PostgreSQL `COPY`, transactions, per-batch deletes,
and mutable audit rows. Raw tables are declared in:

- `infra/postgres/002_create_raw_tables.sql`;
- `infra/postgres/005_create_correction_tables.sql`.

The batch control and audit tables are declared in
`infra/postgres/003_create_audit_tables.sql`.

### 2.3 Near-realtime path

The local CDC DAGs are:

- `olist_cdc_ingest_local`;
- `olist_cdc_backfill_local`;
- `olist_cdc_transform_local`;
- `olist_cdc_quality_local`.

`scripts/cdc/warehouse_ingest.py` currently performs both warehouse writes and
transactional coordination. It uses PostgreSQL-specific features including:

- transactions and rollback;
- `ON CONFLICT`;
- `FOR UPDATE SKIP LOCKED`;
- advisory locks;
- temporary tables;
- `RETURNING`;
- unique constraints;
- mutable audit and watermark rows.

`scripts/cdc/realtime_transform.py` also combines:

- PostgreSQL control transactions;
- advisory locks;
- transform-run and publication state;
- dbt process execution;
- queries against dbt-created parity relations.

The typed CDC tables and most CDC control tables are mixed in
`infra/postgres/006_create_cdc_tables.sql`. Transform and publication state is
declared in `infra/postgres/007_create_cdc_transform_audit.sql`.

### 2.4 dbt project

The shared dbt project is `dbt/olist_analytics`.

Its profile currently contains:

- `local_pg`, using `dbt-postgres`;
- `redshift`, using `dbt-redshift`;
- matching Elementary outputs.

The project currently contains:

- 64 project models;
- two snapshots, `snap_customers` and `snap_products`;
- four dbt unit tests;
- 15 project leaf models at the time this plan was written;
- batch, realtime transform, realtime quality, and parity selectors.

Current SQL is primarily PostgreSQL/Redshift-oriented. Incompatibilities
include:

- PostgreSQL `::` casts;
- PostgreSQL intervals;
- `to_char`;
- `string_agg`;
- PostgreSQL timestamp and timezone expressions;
- PostgreSQL hash return conventions;
- direct mutable `DELETE` pre-hooks;
- `incremental_strategy='merge'`, which is not supported by
  `dbt-clickhouse`;
- audit sources that resolve to tables in the analytical PostgreSQL database.

The following models require an explicit ClickHouse materialization decision:

- `fact_order_items`;
- `dim_customer_realtime_scd2`;
- `dim_product_realtime_scd2`;
- `dim_seller_realtime`;
- `fact_order_items_realtime`;
- `mart_daily_revenue_realtime`;
- `mart_monthly_arpu_realtime`.

### 2.5 CI and observability

The main affected workflows are:

- `.github/workflows/ci.yml`;
- `.github/workflows/batch-cdc-parity.yml`;
- `.github/workflows/cdc-stage6-operations.yml`.

Current CI provisions PostgreSQL for dbt compilation, batch fixture execution,
CDC ingestion tests, realtime dbt tests, and operational tests.

Prometheus currently scrapes:

- the OLTP PostgreSQL exporter;
- the analytical warehouse PostgreSQL exporter;
- the custom CDC pipeline exporter.

The OLTP exporter must remain. The warehouse exporter must be replaced with
ClickHouse metrics.

## 3. Goals, Success Criteria, and Non-Goals

### 3.1 Goals

- Make ClickHouse the only supported local analytical warehouse.
- Move local batch raw data, typed CDC events, dbt snapshots, derived models,
  parity relations, and Elementary relations to ClickHouse.
- Preserve one shared dbt project for ClickHouse and Redshift.
- Preserve batch and realtime business semantics.
- Preserve idempotent batch reruns, CDC replay, and recovery from ambiguous
  insert outcomes.
- Keep transactional control state in PostgreSQL without exposing it as a
  ClickHouse external database.
- Preserve the AWS Redshift path.
- Keep the local environment reproducible on Windows, macOS, and Linux through
  Docker Compose.
- Preserve or improve current diagnostics, metrics, and failure messages.

### 3.2 Core acceptance criteria

The migration is complete only when all of the following are true:

- The default `docker compose up` path starts ClickHouse, Airflow PostgreSQL,
  Airflow, and the required initialization services without starting a
  PostgreSQL analytical warehouse.
- The same deterministic fixture produces equivalent published analytical
  values in PostgreSQL and ClickHouse during the dual-run phase.
- The final ClickHouse-only batch path passes all source validation,
  reconciliation, dbt, snapshot, data-test, and Elementary gates.
- The final ClickHouse-only realtime path passes insert, update, hard-delete,
  ordering, replay, offset-continuity, reconciliation, freshness, and parity
  gates.
- Repeating the same batch does not change logical raw or derived row counts.
- Retrying a CDC file after an insert acknowledgement failure does not create
  logical duplicate events.
- A failure between a ClickHouse write and a PostgreSQL control-state update is
  recoverable without manual data repair.
- No ClickHouse model or quality query needs PostgreSQL credentials.
- The Redshift target still parses, compiles, and passes its existing
  target-specific validation.
- The local analytical `postgres` service, `local_pg` target, old loader, and
  warehouse PostgreSQL exporter are removed.
- All affected DAGs remain within their existing execution timeouts for the
  committed small fixtures.

### 3.3 Non-goals

- Removing PostgreSQL as the Airflow metadata database.
- Replacing the OLTP PostgreSQL source used by Debezium.
- Replacing Redshift on AWS.
- Migrating existing local PostgreSQL warehouse contents.
- Supporting `local_pg` indefinitely as a fallback.
- Introducing ClickHouse Keeper, replication, sharding, or Distributed tables.
- Replacing MinIO, Kafka, NiFi, or Debezium.
- Performing a ClickHouse denormalization redesign during the parity milestone.
- Adding projections, aggressive codecs, or materialized views without
  benchmark evidence.
- Adopting dbt Fusion for the ClickHouse target. The target remains on dbt
  Core.

## 4. Accepted Architecture Decisions

These decisions are final for this implementation. An implementation agent
must not reopen them without amending this plan.

| Decision                   | Accepted outcome                                                                                                       |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Analytical scope           | Both local batch and realtime analytical data move to ClickHouse.                                                      |
| PostgreSQL control state   | Retain PostgreSQL only for Airflow metadata, OLTP, and transactional pipeline control.                                 |
| Control database placement | Create `olist_control` as a separate database and role on the existing `airflow-postgres` server.                      |
| dbt structure              | Keep one dbt project with adapter-dispatched SQL and target-specific materializations.                                 |
| Quality boundary           | Query operational state with Python; do not expose PostgreSQL control tables through ClickHouse table engines.         |
| Transform file selection   | Mirror only the immutable run selection into a short-lived ClickHouse runtime table. PostgreSQL remains authoritative. |
| Migration method           | Run PostgreSQL and ClickHouse against deterministic fixtures temporarily, then remove PostgreSQL warehouse support.    |
| Existing local data        | Recreate batch data from source archives and CDC data from immutable landing objects.                                  |
| First priority             | Prove semantic parity and recovery behavior before performance tuning.                                                 |
| ClickHouse topology        | Use one non-replicated local node with Atomic databases.                                                               |
| Timezone                   | Run ClickHouse in UTC and use `DateTime64(6, 'UTC')` for analytical timestamps.                                        |

## 5. Target Architecture and Data Ownership

### 5.1 Component ownership

| Data or capability                     | Authoritative store                                       |
| -------------------------------------- | --------------------------------------------------------- |
| Airflow metadata                       | PostgreSQL database `airflow`                             |
| Batch run state                        | PostgreSQL database `olist_control`, schema `audit`       |
| CDC file claims and attempts           | PostgreSQL database `olist_control`, schema `cdc_audit`   |
| CDC coverage and watermarks            | PostgreSQL database `olist_control`, schema `cdc_audit`   |
| Transform checkpoints                  | PostgreSQL database `olist_control`, schema `cdc_audit`   |
| Publication approval state             | PostgreSQL database `olist_control`, schema `cdc_audit`   |
| Batch raw rows                         | ClickHouse database `raw_data`                            |
| Typed CDC business events              | ClickHouse database `raw_cdc`                             |
| Run-scoped selected-file projection    | ClickHouse database `pipeline_runtime`                    |
| dbt staging and intermediate relations | ClickHouse databases `staging` and `intermediate`         |
| dbt snapshots                          | ClickHouse database `snapshots`                           |
| Batch facts, dimensions, and marts     | ClickHouse databases `core` and `marts`                   |
| Realtime facts, dimensions, and marts  | ClickHouse databases `realtime_core` and `realtime_marts` |
| Parity reports                         | ClickHouse database `cdc_audit`                           |
| Published analytics views              | ClickHouse database `analytics`                           |
| Elementary relations                   | ClickHouse database `elementary`                          |
| AWS analytical data                    | Amazon Redshift                                           |

The name `cdc_audit` exists in both systems for different purposes:

- PostgreSQL `olist_control.cdc_audit` contains authoritative operational
  state;
- ClickHouse database `cdc_audit` contains analytical parity reports only.

No query may implicitly join those namespaces.

### 5.2 Batch flow

```text
source archive
  -> source validation
  -> prepared gzip CSV and correction files
  -> PostgreSQL control row: batch STARTED
  -> ClickHouse staging table per entity
  -> schema and row-count validation
  -> atomic raw_data partition replacement
  -> PostgreSQL load and reconciliation state
  -> dbt build against local_clickhouse
  -> ClickHouse data tests and Elementary
  -> PostgreSQL control row: batch SUCCEEDED
```

### 5.3 CDC ingest flow

```text
closed manifest and Parquet object in MinIO
  -> discover manifest
  -> PostgreSQL transaction claims file
  -> validate object identity, schema, offsets, and row count
  -> Arrow batch insert into ClickHouse raw_cdc
  -> ClickHouse logical-count and offset validation
  -> PostgreSQL transaction records reconciliation and LOADED status
  -> emit the existing raw CDC Airflow Asset
```

### 5.4 Realtime transform flow

```text
raw CDC Airflow Asset
  -> PostgreSQL transaction creates transform run and selects files
  -> selected object URIs are projected into ClickHouse pipeline_runtime
  -> dbt builds the manifest-bounded ClickHouse graph
  -> ClickHouse data and parity checks run
  -> Python control checks query PostgreSQL
  -> PostgreSQL transaction commits transform checkpoint/publication state
```

### 5.5 Cross-store consistency rule

There is no distributed transaction between PostgreSQL and ClickHouse.
Correctness must come from idempotency and explicit state transitions:

1. commit a PostgreSQL claim before writing ClickHouse;
2. write ClickHouse using deterministic data and a deterministic insert token;
3. validate the logical ClickHouse result;
4. commit PostgreSQL success only after validation;
5. allow an expired claim or failed task to repeat steps 2 through 4 safely.

Never mark a batch entity or CDC file successful before its ClickHouse result
has been read back and reconciled.

## 6. Version and Dependency Baseline

Pin these versions during the migration. Do not use floating image tags.

| Component                 | Required baseline                              |
| ------------------------- | ---------------------------------------------- |
| ClickHouse server         | `clickhouse/clickhouse-server:26.3.17.4`       |
| dbt Core                  | current locked `1.11.8`                        |
| dbt ClickHouse adapter    | `dbt-clickhouse==1.10.1`                       |
| ClickHouse Python client  | `clickhouse-connect==1.5.0`                    |
| dbt Redshift adapter      | retain the current locked compatible release   |
| Elementary CLI            | `elementary-data[clickhouse,redshift]==0.23.4` |
| Elementary dbt package    | retain the current pinned package release      |
| PostgreSQL control driver | retain `psycopg2-binary`                       |
| Python                    | retain 3.12                                    |

Reference documentation:

- ClickHouse dbt configuration:
  <https://clickhouse.com/docs/integrations/dbt/features-and-configurations>
- ClickHouse dbt materializations:
  <https://clickhouse.com/docs/integrations/dbt/materializations>
- Atomic partition replacement:
  <https://clickhouse.com/docs/sql-reference/statements/alter/partition>
- Insert deduplication tokens:
  <https://clickhouse.com/docs/operations/settings/settings#insert_deduplication_token>
- ClickHouse Prometheus endpoint:
  <https://clickhouse.com/docs/operations/server-configuration-parameters/settings#prometheus>
- dbt ClickHouse release:
  <https://pypi.org/project/dbt-clickhouse/1.10.1/>

Update `pyproject.toml` and `uv.lock` together. During the final cleanup remove
the direct `dbt-postgres` dependency. A transitive installation through another
adapter is acceptable, but the repository must no longer declare or test a
`local_pg` dbt output.

## 7. Public Configuration Contract

### 7.1 New ClickHouse variables

Add these variables to `.env.example`, Compose, Airflow, local commands, and CI:

| Variable                      | Default or source                | Purpose                       |
| ----------------------------- | -------------------------------- | ----------------------------- |
| `DBT_TARGET`                  | `local_clickhouse` after cutover | Default dbt output            |
| `CLICKHOUSE_HOST`             | `clickhouse` in Compose          | Internal server hostname      |
| `CLICKHOUSE_PORT`             | `8123`                           | HTTP client port              |
| `CLICKHOUSE_USER`             | `olist`                          | Shared local application user |
| `CLICKHOUSE_PASSWORD_FILE`    | Docker secret path               | Runtime password source       |
| `CLICKHOUSE_DATABASE`         | `analytics`                      | Default dbt database/schema   |
| `CLICKHOUSE_HTTP_HOST_PORT`   | `8123`                           | Optional host HTTP mapping    |
| `CLICKHOUSE_NATIVE_HOST_PORT` | `19000`                          | Optional host native mapping  |
| `CLICKHOUSE_SECURE`           | `false`                          | Local HTTP/TCP mode           |

### 7.2 New control PostgreSQL variables

| Variable                         | Default or source  | Purpose                    |
| -------------------------------- | ------------------ | -------------------------- |
| `CONTROL_POSTGRES_HOST`          | `airflow-postgres` | Shared server hostname     |
| `CONTROL_POSTGRES_PORT`          | `5432`             | PostgreSQL port            |
| `CONTROL_POSTGRES_DB`            | `olist_control`    | Dedicated control database |
| `CONTROL_POSTGRES_USER`          | `olist_control`    | Dedicated control role     |
| `CONTROL_POSTGRES_PASSWORD_FILE` | Docker secret path | Runtime password source    |

Add `control_postgres_password` to the committed development-secret mechanism
and allow a `CONTROL_POSTGRES_PASSWORD_SOURCE_FILE` override.

### 7.3 Variables that remain

Do not rename or repurpose:

- `AIRFLOW_POSTGRES_*`;
- `OLTP_POSTGRES_*`;
- `REDSHIFT_*`;
- MinIO, Kafka, NiFi, or observability variables.

### 7.4 Variables that disappear after cutover

Remove the analytical warehouse meaning of:

- `POSTGRES_HOST`;
- `POSTGRES_PORT`;
- `POSTGRES_DB`;
- `POSTGRES_USER`;
- `POSTGRES_PASSWORD_FILE`;
- `POSTGRES_PASSWORD_SOURCE_FILE`.

Do not overload `POSTGRES_*` to mean control state. Explicit
`CONTROL_POSTGRES_*` names are required to prevent accidental cross-database
connections.

### 7.5 dbt profile contract

Add the following logical output to both the project and Elementary profiles:

```yaml
local_clickhouse:
  type: clickhouse
  driver: http
  host: "{{ env_var('CLICKHOUSE_HOST', 'localhost') }}"
  port: "{{ env_var('CLICKHOUSE_PORT', 8123) | as_number }}"
  user: "{{ env_var('CLICKHOUSE_USER', 'olist') }}"
  password: "{{ env_var('CLICKHOUSE_PASSWORD', 'olist') }}"
  schema: "{{ env_var('CLICKHOUSE_DATABASE', 'analytics') }}"
  secure: false
  verify: false
  threads: 4
  connect_timeout: 10
  send_receive_timeout: 300
  use_lw_deletes: false
  check_exchange: true
  custom_settings:
    join_use_nulls: 1
```

The container entrypoint must continue resolving `*_FILE` into the matching
environment variable before dbt starts. Do not commit a real password to the
profile.

ClickHouse maps the dbt `schema` concept to a ClickHouse database. Keep the
existing custom schema names rather than prefixing every table name.

## 8. ClickHouse Storage Contracts

### 8.1 Database engine and topology

- Use the default Atomic database engine.
- Do not set a ClickHouse cluster in the dbt profile.
- Do not use Replicated, SharedMergeTree, or Distributed engines.
- Configure server timezone as UTC.
- Set `ulimit nofile=262144:262144` for the ClickHouse service.
- Persist `/var/lib/clickhouse`.
- Keep the Prometheus port internal to the Compose network unless a debugging
  use case requires a host mapping.

### 8.2 Common type mapping

| PostgreSQL-oriented type            | ClickHouse type                  |
| ----------------------------------- | -------------------------------- |
| nullable `varchar` or `text`        | `Nullable(String)`               |
| required `varchar` or `text`        | `String`                         |
| low-cardinality status or operation | `LowCardinality(String)`         |
| nullable `integer`                  | `Nullable(Int32)`                |
| required `integer`                  | `Int32`                          |
| nullable `bigint`                   | `Nullable(Int64)`                |
| required `bigint`                   | `Int64`                          |
| `decimal(18, 2)`                    | `Decimal(18, 2)`                 |
| `decimal(18, 8)`                    | `Decimal(18, 8)`                 |
| `decimal(18, 14)`                   | `Decimal(18, 14)`                |
| `date`                              | `Date`                           |
| `timestamp` or `timestamptz`        | `DateTime64(6, 'UTC')`           |
| boolean                             | `Bool`                           |
| 64-character SHA-256                | `FixedString(64)` where non-null |

Source business columns retain their current nullability. Ingestion metadata
that is currently required remains non-null.

Olist batch timestamps do not carry source timezone information. Preserve
their wall-clock values and store them in the UTC-configured
`DateTime64(6, 'UTC')` type. Do not apply a Brazil-to-UTC offset during this
migration.

### 8.3 Batch raw tables

Create the eleven existing raw entities in ClickHouse database `raw_data`:

- customers;
- geolocation;
- order items;
- order payments;
- order reviews;
- orders;
- products;
- sellers;
- product category translation;
- customer profile changes;
- product attribute changes.

Use this engine contract:

```sql
ENGINE = MergeTree
PARTITION BY _batch_id
ORDER BY (<documented business grain>, _loaded_at)
```

Use the existing source profile and dbt grain tests to select the business
grain. Examples include:

- customers: `customer_id`;
- orders: `order_id`;
- order items: `(order_id, order_item_id)`;
- order payments: `(order_id, payment_sequential)`;
- products: `product_id`;
- sellers: `seller_id`.

Partitioning by `_batch_id` is intentional for the bounded local environment.
It enables deterministic batch replacement and is not a recommendation for a
high-volume production ClickHouse deployment.

### 8.4 Atomic batch replacement

For each entity and batch:

1. create a uniquely named staging table with the exact target structure,
   engine, partition key, order key, storage policy, indices, and projections;
2. stream the prepared gzip CSV into the staging table;
3. validate column compatibility and expected row count;
4. verify that the staging table contains only the requested `_batch_id`;
5. execute:

   ```sql
   ALTER TABLE raw_data.<entity>
   REPLACE PARTITION '<batch_id>'
   FROM raw_data.<staging_table>
   ```

6. read back the target partition count;
7. update PostgreSQL load and reconciliation state;
8. drop the staging table in a `finally` path.

The staging table name must be generated from an allow-listed entity plus a
sanitized run identifier. Never interpolate an arbitrary user-provided
identifier into DDL.

### 8.5 Typed CDC event tables

Create the existing eight typed CDC entity tables in database `raw_cdc`.

Use this engine contract:

```sql
ENGINE = ReplacingMergeTree(_warehouse_loaded_at)
PARTITION BY toYYYYMM(
    coalesce(_source_ts, _kafka_ts, _nifi_written_at)
)
ORDER BY (_topic, _partition, _offset)
SETTINGS non_replicated_deduplication_window = 10000
```

The logical event identity is `(_topic, _partition, _offset)`.
`_event_id` remains a required business-facing event identifier but is not the
ReplacingMergeTree sorting key.

Every file insert must:

- send a deterministic `insert_deduplication_token` based on the verified
  object SHA-256;
- set `wait_for_async_insert=1`, or disable asynchronous inserts for that
  session;
- insert rows in deterministic order;
- validate the logical target range after insertion.

All dbt event staging models must read a dispatched relation that adds `FINAL`
for ClickHouse. Do not rely on background merges for query correctness.

### 8.6 Runtime transform selection

Create:

```text
pipeline_runtime.cdc_transform_run_files
```

with at least:

- `transform_run_id String`;
- `object_uri String`;
- `manifest_sha256 FixedString(64)`;
- `selected_at DateTime64(6, 'UTC')`.

Use:

```sql
ENGINE = ReplacingMergeTree(selected_at)
PARTITION BY toYYYYMM(selected_at)
ORDER BY (transform_run_id, object_uri)
TTL selected_at + INTERVAL 7 DAY DELETE
```

The transform preparation command must project the exact PostgreSQL selection
into this table before invoking dbt. The insert token must be derived from the
transform run identifier and the sorted selection digest.

Replace the current dbt join to PostgreSQL `cdc_transform_run_files` and
`cdc_files` with a ClickHouse join to this runtime relation and raw
`_source_object_uri`.

### 8.7 dbt-derived tables

Use `MergeTree` unless a model-specific section says otherwise.

| Model family                  | Initial parity materialization | Final cutover materialization  |
| ----------------------------- | ------------------------------ | ------------------------------ |
| staging and intermediate      | view                           | view                           |
| batch dimensions              | table                          | table                          |
| batch marts                   | table                          | table                          |
| dbt snapshots                 | native snapshot                | native snapshot                |
| `fact_order_items`            | full table                     | incremental `insert_overwrite` |
| realtime history models       | full table                     | full table                     |
| realtime current-state models | view                           | view                           |
| realtime SCD2 dimensions      | full table                     | full table                     |
| realtime seller dimension     | full table                     | full table                     |
| `fact_order_items_realtime`   | full table                     | incremental `insert_overwrite` |
| daily realtime mart           | full table                     | incremental `insert_overwrite` |
| monthly realtime mart         | full table                     | incremental `insert_overwrite` |
| parity resources              | view                           | view                           |

Required order and partition keys:

- batch and realtime facts:
  - partition by purchase month;
  - order by `(order_purchase_timestamp, order_id, order_item_id)`;
- daily mart:
  - partition by `toYYYYMM(order_purchase_date)`;
  - order by `order_purchase_date`;
- monthly mart:
  - partition by `toYYYYMM(order_month)`;
  - order by `order_month`;
- history tables:
  - order by business key followed by
    `(_source_lsn, _tx_order, _partition, _offset)`;
- dimensions:
  - order by their stable business or surrogate key.

For nullable fact timestamps, dispatch the partition expression to a fixed
`1900-01-01` sentinel rather than enabling nullable partition keys.

### 8.8 Incremental partition replacement

Do not port PostgreSQL `DELETE` pre-hooks or `merge`.

For each incremental fact or mart:

1. calculate the affected partition set from new and changed source records;
2. include partitions found in the existing target for deleted or moved keys;
3. select the complete current result for every affected partition;
4. let `insert_overwrite` replace non-empty partitions;
5. explicitly drop an affected target partition only when the successfully
   built staging result proves that the partition is now empty;
6. make every partition action retry-safe.

The batch fact affected range must include:

- the configured lookback boundary;
- correction-feed effective dates;
- newly discovered item keys;
- existing target keys no longer present in current source state.

The realtime fact affected range must include:

- direct order, item, payment, and review changes;
- customer, product, seller, and translation changes propagated to related
  orders;
- the existing target partition for an order that has been deleted.

The realtime marts must replace every date or month affected by the fact
partitions. An incremental query must never return only changed rows for an
`insert_overwrite` partition; it must return the complete partition.

## 9. PostgreSQL Control-Plane Contract

### 9.1 Database provisioning

Add an idempotent `control-db-init` one-shot service.

It must:

1. wait for `airflow-postgres`;
2. connect with the Airflow PostgreSQL administrator credential;
3. create role `olist_control` if absent;
4. update that role's password from the current secret;
5. create database `olist_control` owned by that role if absent;
6. connect to `olist_control`;
7. apply ordered, idempotent DDL from `infra/control-postgres`;
8. exit successfully only after a connection and schema smoke test.

Do not rely only on `/docker-entrypoint-initdb.d`; those scripts do not run
against an existing Airflow PostgreSQL volume.

### 9.2 DDL split

Create:

```text
infra/clickhouse/
infra/control-postgres/
```

Move or rewrite:

- batch and CDC operational schemas into `infra/control-postgres`;
- batch raw and CDC event schemas into `infra/clickhouse`;
- dbt-owned derived schemas remain managed by dbt.

Do not copy raw business tables into the control database.

### 9.3 Control repository interface

Introduce one shared PostgreSQL control connection factory that reads only
`CONTROL_POSTGRES_*`.

Batch, CDC ingest, transform, replay, and quality code must use repository
methods rather than constructing separate connection settings. Preserve
PostgreSQL transactions, row locks, advisory locks, and uniqueness where those
semantics are currently required.

The following state remains mutable PostgreSQL state:

- batch runs;
- load attempts;
- batch reconciliation;
- dead-letter events and replays;
- CDC ingest runs;
- file discovery, claims, attempts, and replay requests;
- coverage manifests and offset coverage;
- partition watermarks;
- CDC reconciliation;
- CDC dead letters;
- transform runs and selected manifests;
- mart freshness;
- publication approval.

### 9.4 Operational quality checks

Replace ClickHouse-target dbt tests that query control tables with Python
checks preserving the same failure conditions:

- latest batch reconciliation passed;
- latest CDC reconciliation passed per source table;
- mart freshness is within the configured threshold;
- partition offsets are continuous and gap counts are zero.

The Python gate must emit:

- a machine-readable JSON summary;
- a non-zero exit status on failure;
- bounded, actionable diagnostics identifying the source table, partition,
  expected state, and observed state.

Keep the existing Redshift batch reconciliation dbt test enabled. Disable the
control-source dbt tests only for `target.type == 'clickhouse'`.

## 10. dbt Portability Specification

### 10.1 One shared project

Do not fork `dbt/olist_analytics`.

Keep:

- one model graph;
- one set of business tests;
- one package lock;
- one model naming and grouping convention;
- target-specific macros and materialization config only where behavior truly
  differs.

### 10.2 Schema handling

ClickHouse treats a dbt schema as a database. Keep the existing custom schema
names.

Remove `database: "{{ target.database }}"` from same-target source definitions
where it prevents ClickHouse resolution. Redshift sources are in the same
configured database and do not require that explicit property.

Expected ClickHouse databases are:

- `analytics`;
- `raw_data`;
- `raw_cdc`;
- `staging`;
- `intermediate`;
- `snapshots`;
- `core`;
- `marts`;
- `realtime_staging`;
- `realtime_core`;
- `realtime_marts`;
- `cdc_audit`;
- `pipeline_runtime`;
- `elementary`.

### 10.3 Required dispatch macros

Extend the compatibility layer with explicit default, Redshift, and ClickHouse
implementations for:

- adding days;
- day differences;
- date and month truncation;
- date-key formatting;
- stable hexadecimal MD5 output;
- safe string concatenation;
- string aggregation;
- null-safe equality and inequality;
- timestamp, date, decimal, integer, and string casts;
- UTC conversion where required;
- two-decimal rounding;
- CDC lexicographic ordering;
- selecting a deduplicated CDC source relation;
- selecting manifest-bounded CDC events;
- ClickHouse partition expressions.

The stable hash macro must return the same lowercase 32-character hexadecimal
string in ClickHouse and Redshift. Replace direct `md5(...)` expressions used
for durable analytical keys with that macro.

The CDC ordering macro must preserve this exact precedence:

1. `_source_lsn`;
2. `coalesce(_tx_order, 0)`;
3. `_partition`;
4. `_offset`.

Use an explicit boolean comparison chain if a row-constructor comparison does
not compile identically across both adapters.

### 10.4 Forbidden SQL outside compatibility macros

Add a CI check rejecting these patterns in project models and tests:

- PostgreSQL `::` casts;
- `interval '...'` literals;
- direct `to_char`;
- direct PostgreSQL `string_agg`;
- PostgreSQL `AT TIME ZONE`;
- `IS DISTINCT FROM` unless dispatched;
- target-specific date arithmetic;
- direct mutable `DELETE` pre-hooks.

Redshift-specific distribution and sort configuration may remain inside an
explicit `target.type == 'redshift'` block.

### 10.5 Snapshot behavior

Keep the two current dbt snapshots and use the adapter's native snapshot
materialization.

Validate:

- one current row per business key;
- positive validity windows;
- no overlapping windows;
- stable behavior on a no-change rerun;
- correct row closure after a correction feed;
- equivalent business history across PostgreSQL and ClickHouse.

Do not require adapter-generated snapshot identifiers or runtime timestamps to
match byte-for-byte across engines.

### 10.6 Elementary

Install both the ClickHouse and Redshift extras for the existing Elementary
version. Preserve the Elementary dbt package and report generation.

During implementation explicitly validate:

- `dbt deps`;
- package parsing against `local_clickhouse`;
- Elementary model build;
- data-test materialization;
- report generation;
- no regression for Redshift profile parsing.

If the existing project override of Elementary's test materialization is
unnecessary or incompatible on ClickHouse, dispatch it by adapter instead of
removing Redshift behavior.

## 11. Python Loader and Coordinator Design

### 11.1 Shared ClickHouse client

Create a small shared client module responsible for:

- resolving `CLICKHOUSE_*` settings and secret files;
- creating `clickhouse-connect` clients;
- applying required session settings;
- validating identifiers against allow lists;
- executing scalar count queries;
- inserting Arrow batches;
- closing clients;
- translating driver errors into bounded pipeline diagnostics.

Do not introduce an ORM. Use the ClickHouse client directly.

### 11.2 Batch loader

Replace `load_raw_to_postgres.py` with a ClickHouse-specific loader. Preserve
the existing command inputs for raw directory, source profile, batch date,
batch ID, run ID, DAG ID, and dead-letter handling.

The loader must:

- use the PostgreSQL control repository for state;
- use the ClickHouse client for raw data;
- stream or batch CSV input rather than insert one row at a time;
- use the atomic partition replacement contract;
- record expected and observed counts;
- make a rerun of the same batch deterministic;
- never leave a staging table after normal success;
- report a failed staging-table cleanup without hiding the original failure.

Rename Airflow task IDs and descriptions from
`load_raw_files_to_postgres` to ClickHouse-neutral or ClickHouse-specific
names.

### 11.3 CDC ingest refactor

Split `warehouse_ingest.py` into clear responsibilities while preserving its
CLI behavior:

- object storage and manifest validation;
- PostgreSQL control repository;
- ClickHouse raw CDC sink;
- reconciliation and summary formatting.

Keep manifest discovery, claim, replay, coverage, and watermark logic in
PostgreSQL. Replace only the raw warehouse write and read-back portions.

Use the existing PyArrow dependency. Prefer inserting the validated Arrow table
or bounded record batches rather than converting an entire Parquet object to a
Python list.

### 11.4 Reconciliation semantics

For each CDC object:

- `object_rows` is the validated Parquet row count;
- logical event identity is topic, partition, and offset;
- `inserted_rows` is the increase in logical unique events;
- `duplicate_rows` is the portion already present logically;
- `rejected_rows` is the portion rejected before ClickHouse insert;
- success requires:

  ```text
  inserted_rows + duplicate_rows + rejected_rows == object_rows
  ```

- any unexpected payload mismatch for an already present event identity is a
  failure, not a duplicate.

Because one ingest DAG run is active at a time, before/after logical range
counts are sufficient for the local path. Keep the existing PostgreSQL lock
that enforces this serialization.

### 11.5 Realtime transform refactor

`realtime_transform.py` must use two explicit clients:

- PostgreSQL for run state, locks, selected manifests, checkpoints, freshness,
  and publication;
- ClickHouse for selection projection, dbt outputs, parity results, and mart
  source timestamps.

Required command behavior:

- `prepare`:
  - create or resume the PostgreSQL transform run;
  - select the exact eligible manifests;
  - commit that selection;
  - project object URIs into ClickHouse;
  - return selection counts and digest;
- `build`:
  - invoke dbt against `local_clickhouse`;
  - pass `cdc_transform_run_id`;
  - query ClickHouse build/parity evidence;
- `finish`:
  - verify the same selection digest;
  - record mart freshness;
  - commit success and publication state in PostgreSQL;
- `fail`:
  - record bounded failure information in PostgreSQL;
- `quality`:
  - run PostgreSQL control checks and ClickHouse data checks separately;
  - combine only their JSON results in Python.

No SQL statement may attempt a cross-database join between the two systems.

## 12. Docker Compose and Initialization Design

### 12.1 ClickHouse image

Add `docker/clickhouse/Dockerfile` based on the pinned server image.

Add an entrypoint wrapper that:

1. reads `/run/secrets/clickhouse_password`;
2. exports `CLICKHOUSE_PASSWORD` only inside the container process;
3. executes the official ClickHouse entrypoint.

Do not place the clear-text password directly in Compose environment values.

### 12.2 ClickHouse service

The final no-profile service must include:

- the pinned image;
- container name `olist-clickhouse`;
- persistent data volume;
- config and user fragments mounted read-only;
- the ClickHouse password secret;
- `CLICKHOUSE_DB=analytics`;
- `CLICKHOUSE_USER=olist`;
- `CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1`;
- HTTP host port `${CLICKHOUSE_HTTP_HOST_PORT:-8123}`;
- native host port `${CLICKHOUSE_NATIVE_HOST_PORT:-19000}`;
- internal Prometheus port `9363`;
- a credential-aware `SELECT 1` healthcheck;
- a sufficient start period for first initialization.

### 12.3 Initialization services

Use two explicit one-shot services:

- `control-db-init`, for PostgreSQL control database and DDL;
- `clickhouse-init`, for ClickHouse databases, users/grants, raw tables, and
  runtime tables.

Both must be idempotent and usable against existing volumes.

Airflow must wait for:

- healthy ClickHouse;
- healthy Airflow PostgreSQL;
- successful control initialization;
- successful ClickHouse initialization.

The realtime profile's current `cdc-warehouse-init` must be removed or replaced
by these general initialization services.

### 12.4 Secrets

Add:

- `clickhouse_password`;
- `control_postgres_password`.

Remove the analytical `postgres_password` secret only after no service,
workflow, or script references it. Keep the Airflow and OLTP PostgreSQL
secrets.

## 13. Airflow and Quality-Gate Changes

### 13.1 Local batch DAG

Update the local batch DAG to:

- describe ClickHouse as its warehouse;
- use the new loader;
- use `local_clickhouse`;
- remove `POSTGRES_SQL_DIR`;
- rely on initialization services rather than bootstrap DDL on each run;
- keep the current batch state transitions and failure callback;
- run reconciliation before dbt;
- run ClickHouse dbt data tests and Elementary before marking success;
- use `clickhouse` rather than `postgres` tags.

The AWS DAG remains Redshift-specific and must not import ClickHouse
configuration.

### 13.2 CDC ingest and backfill DAGs

Update command construction to remove `--bootstrap-sql-dir infra/postgres`.

Preserve:

- scheduling;
- max active runs;
- Airflow pool usage;
- Asset emission;
- replay filters;
- failure callbacks;
- JSON summary contract.

Update descriptions and tags to identify ClickHouse.

### 13.3 Realtime transform DAG

Preserve the three-step prepare/build/finish boundary.

Do not commit the PostgreSQL transform checkpoint from the dbt build task. A
successful dbt process followed by a failed checkpoint must remain safely
retryable.

### 13.4 Realtime quality DAG

Run these gates in order:

1. PostgreSQL control reconciliation and offset checks;
2. ClickHouse realtime data tests;
3. ClickHouse batch-to-realtime parity tests;
4. nightly full dbt and Elementary checks where currently configured.

Return one JSON summary with distinct `control`, `warehouse`, `parity`, and
`elementary` sections.

## 14. Observability Migration

### 14.1 ClickHouse Prometheus endpoint

Mount a server configuration fragment equivalent to:

```xml
<clickhouse>
    <prometheus>
        <endpoint>/metrics</endpoint>
        <port>9363</port>
        <metrics>true</metrics>
        <events>true</events>
        <asynchronous_metrics>true</asynchronous_metrics>
        <errors>true</errors>
    </prometheus>
</clickhouse>
```

Add a Prometheus target named `clickhouse` for
`clickhouse:9363/metrics`.

### 14.2 Exporters

- Keep `postgres-exporter-oltp`.
- Remove `postgres-exporter-warehouse`.
- Make the custom CDC pipeline exporter read control state through
  `CONTROL_POSTGRES_*`.
- Query ClickHouse only where an analytical metric cannot be derived from
  validated control state.
- Expose separate exporter health for control PostgreSQL and ClickHouse.

### 14.3 Dashboards and alerts

Replace warehouse PostgreSQL panels and checks with:

- ClickHouse availability;
- query error count;
- active and inactive part counts;
- parts per partition;
- pending or failed mutations;
- disk bytes and inode pressure;
- insert latency and rejected inserts;
- dbt model duration;
- batch and CDC reconciliation status;
- source-to-mart freshness.

Keep PostgreSQL WAL and replication-slot panels for the OLTP source.

Update Stage 6 configuration validation to require the ClickHouse target and
forbid the removed warehouse PostgreSQL exporter.

## 15. Detailed Implementation Phases

Each phase must be a reviewable change with its own exit gate. Do not combine
all phases into one unreviewable rewrite.

### Phase 0: Capture the PostgreSQL oracle

Tasks:

1. Confirm a clean PostgreSQL execution of the small batch fixture.
2. Confirm the current synthetic Stage 5 realtime fixture.
3. Run `dbt ls` and record the current model, snapshot, test, and leaf counts.
4. Add or complete dbt unit tests for every project leaf model.
5. Add focused mid-graph tests for:
   - latest-source selection;
   - correction precedence;
   - payment allocation;
   - SCD2 window construction;
   - CDC current-state ordering;
   - product-translation history;
   - changed-order propagation;
   - hard deletes.
6. Create the canonical cross-engine result format and PostgreSQL exporter.
7. Store only compact expected metadata and fixture results in the repository,
   not a dump of the full Olist database.

Exit gate:

- the current PostgreSQL pipeline is green;
- all new golden tests pass before any SQL port;
- a deterministic PostgreSQL parity manifest can be regenerated.

### Phase 1: Add dependencies and ClickHouse infrastructure

Tasks:

1. Update dependencies and lock file.
2. Add the ClickHouse image, config, secrets, data volume, healthcheck, and
   init service.
3. Add initial raw batch, raw CDC, and runtime-selection DDL.
4. Add the `local_clickhouse` project and Elementary outputs.
5. Add `dbt debug` and a trivial connection smoke test.
6. Keep `local_pg` as the default during this phase.

Exit gate:

- Compose validates;
- ClickHouse starts on amd64 and arm64-compatible Docker environments;
- initialization is idempotent;
- `dbt debug --target local_clickhouse` succeeds;
- Redshift profile parsing remains green.

### Phase 2: Separate control PostgreSQL

Tasks:

1. Add `olist_control` provisioning and secret handling.
2. Split control DDL from analytical DDL.
3. Introduce the shared control repository.
4. Move batch control scripts to `CONTROL_POSTGRES_*`.
5. Move CDC control queries to the repository without changing warehouse
   writes yet.
6. Add tests proving that Airflow metadata and control connections target
   different databases.

Exit gate:

- the existing PostgreSQL analytical path still works;
- all mutable control state resides in `olist_control`;
- no control script uses warehouse `POSTGRES_*`.

### Phase 3: Implement ClickHouse batch ingestion

Tasks:

1. Implement the ClickHouse batch loader and staging-table lifecycle.
2. Implement raw row-count queries and reconciliation.
3. Update the local batch DAG behind an explicit candidate configuration.
4. Add failure injection around:
   - staging insert;
   - staging validation;
   - partition replacement;
   - target read-back;
   - PostgreSQL success update.
5. Add batch idempotency tests.

Exit gate:

- the small batch fixture loads into ClickHouse;
- two identical runs produce identical logical raw counts;
- a failed run resumes without manual table cleanup;
- the PostgreSQL oracle remains available for comparison.

### Phase 4: Port the dbt batch graph

Tasks:

1. Implement compatibility macros.
2. Replace direct dialect-specific SQL in batch models and tests.
3. Build staging, intermediate, snapshots, dimensions, facts, marts, and
   Elementary against ClickHouse.
4. Keep `fact_order_items` as a full table until parity is proven.
5. Compare all batch leaf outputs against PostgreSQL.
6. Implement and validate monthly `insert_overwrite`.

Exit gate:

- all batch unit and data tests pass on both active targets;
- published batch values match the oracle;
- snapshots are stable on rerun;
- final batch fact partition replacement passes delete and correction tests.

### Phase 5: Implement ClickHouse CDC ingestion

Tasks:

1. Implement the ClickHouse raw CDC sink.
2. Add deterministic insert tokens and `FINAL` read behavior.
3. Preserve PostgreSQL claims, attempts, watermarks, and reconciliation.
4. Add the runtime transform selection projection.
5. Update ingest and backfill DAGs.
6. Test ambiguous insert outcomes and long-delayed retries.

Exit gate:

- initial CDC ingest, replay, duplicate delivery, and offset checks pass;
- logical raw CDC state contains one event per topic/partition/offset;
- a crash after ClickHouse insert and before PostgreSQL commit self-recovers.

### Phase 6: Port realtime dbt and quality

Tasks:

1. Port realtime staging, history, current-state, dimensions, fact, marts, and
   parity SQL.
2. Run the seven mutable models as full tables for the first parity pass.
3. Move operational dbt checks to Python.
4. Refactor transform prepare/build/finish around two clients.
5. Prove batch-to-realtime parity in ClickHouse.
6. Introduce partition overwrite for realtime fact and marts.
7. Preserve publication approval semantics in PostgreSQL.

Exit gate:

- insert, update, hard-delete, ordering, translation, and related-order tests
  pass;
- the current parity integration plan passes with ClickHouse;
- transform retries are idempotent;
- no ClickHouse dbt query reads PostgreSQL control state.

### Phase 7: Migrate CI, observability, and documentation

Tasks:

1. Add ClickHouse jobs to the affected workflows.
2. Add the cross-engine manifest comparator.
3. Replace the warehouse PostgreSQL exporter.
4. Update alerts, dashboards, and Stage 6 validation.
5. Update local runbooks and architecture documentation.
6. Run two consecutive full-stack ClickHouse candidate workflows.

Exit gate:

- all required CI jobs are green twice consecutively;
- Prometheus reports ClickHouse healthy;
- runbooks reproduce batch and realtime flows from a clean machine.

### Phase 8: Cut over and remove the oracle

Tasks:

1. Set `DBT_TARGET=local_clickhouse`.
2. Make ClickHouse the default no-profile warehouse service.
3. Run one final ClickHouse-only batch and realtime smoke test.
4. Remove:
   - analytical `postgres` service and container;
   - `olist_postgres_data` from active Compose configuration;
   - analytical `postgres_password`;
   - `local_pg` dbt outputs;
   - direct `dbt-postgres` dependency;
   - old PostgreSQL raw DDL;
   - old PostgreSQL loader;
   - warehouse PostgreSQL exporter;
   - PostgreSQL warehouse CI jobs and documentation.
5. Keep:
   - `airflow-postgres`;
   - `oltp-postgres`;
   - `psycopg2-binary`;
   - Redshift adapter and AWS path.

Exit gate:

- a repository-wide search finds no active local analytical PostgreSQL
  references;
- ClickHouse-only CI is green;
- AWS Redshift validation is green;
- the completion checklist in this document is satisfied.

## 16. Cross-Engine Parity Contract

### 16.1 Canonical representation

The comparator must normalize representation without hiding business
differences:

- strings remain case-sensitive and are not trimmed;
- null uses one explicit sentinel distinct from an empty string;
- booleans serialize as `true` or `false`;
- decimals serialize at their declared scale;
- timestamps serialize in UTC with six fractional digits;
- dates serialize as ISO `YYYY-MM-DD`;
- arrays or structured values serialize with stable key ordering;
- rows sort by the model's declared business grain before hashing.

Do not compare database-specific physical type names directly. Compare them
through a semantic type map.

### 16.2 Required comparisons

For every published or leaf model compare:

- row count;
- duplicate count at declared grain;
- complete grain-key set;
- normalized per-row hash;
- aggregate hash over sorted row hashes.

For facts and marts additionally compare:

- total revenue and payment measures;
- order, item, and customer counts;
- min and max business timestamps;
- null counts for important dimensions and measures.

For snapshots compare:

- business key and version count;
- current-row identity;
- business attributes;
- validity ordering and non-overlap.

Exclude:

- engine-specific physical metadata;
- adapter-generated relation names;
- runtime load timestamps;
- adapter-generated snapshot identifiers where business history is otherwise
  equal;
- Elementary internal relations.

### 16.3 Required parity artifacts

Each candidate run must upload:

- PostgreSQL oracle manifest;
- ClickHouse candidate manifest;
- comparator JSON result;
- bounded mismatch sample;
- dbt manifest and run results;
- Airflow task summaries;
- ClickHouse server version and dependency lock digest.

## 17. Failure and Retry Matrix

| Failure point                                       | Required durable state                             | Required retry result                               |
| --------------------------------------------------- | -------------------------------------------------- | --------------------------------------------------- |
| Before batch staging insert                         | Batch STARTED in PostgreSQL                        | Retry creates a fresh staging table                 |
| During batch staging insert                         | No target partition change                         | Retry discards/recreates staging table              |
| After staging validation, before replace            | Old target partition intact                        | Retry repeats validation and replace                |
| After partition replace, before control commit      | New target partition present, batch not successful | Retry replaces the same partition and commits       |
| Before CDC file claim commit                        | File remains discoverable                          | A later run claims it                               |
| After claim, before ClickHouse insert               | File CLAIMED with lease                            | Retry after task restart or lease expiry inserts it |
| Insert acknowledgement lost                         | Logical rows may already exist                     | Same token and `FINAL` produce one logical event    |
| After ClickHouse insert, before reconciliation      | Raw events present, file not LOADED                | Retry validates existing events and commits LOADED  |
| After transform selection commit, before projection | Run STARTED in PostgreSQL                          | Retry projects the same selection digest            |
| After projection, before dbt                        | Runtime rows present                               | Retry upserts the same runtime selection            |
| After dbt success, before checkpoint                | Derived data present, run STARTED                  | Retry rebuilds safely and commits checkpoint        |
| During partition overwrite                          | Some partitions may be replaced                    | Retry recomputes the complete affected set          |
| During empty-partition drop                         | Target may already be empty                        | Retry treats missing partition as success           |

Tests must exercise every row in this matrix.

## 18. Test Plan

### 18.1 Static and unit tests

- Ruff and Pyright for new Python code.
- SQLFluff for shared and target-dispatched SQL.
- Airflow DAG import checks.
- Compose configuration validation for default, realtime, and observability
  profiles.
- DDL identifier allow-list tests.
- Secret-file resolution tests.
- PostgreSQL control repository tests.
- ClickHouse client tests with mocked transport errors.
- Unit tests for manifest selection digest and insert token generation.
- dbt unit tests for every current project leaf model.
- A static test forbidding PostgreSQL dialect in shared model SQL.
- A static test forbidding ClickHouse PostgreSQL table engines.

### 18.2 dbt target tests

For `local_clickhouse`:

- `dbt debug`;
- `dbt deps`;
- `dbt parse --no-partial-parse`;
- `dbt compile`;
- all unit tests;
- `dbt build --selector batch`;
- `dbt build --selector realtime_transform`;
- realtime data and parity tests;
- snapshots run twice;
- Elementary report generation.

For `redshift`:

- dependency resolution;
- parse and compile;
- existing static target checks;
- existing AWS DAG import checks.

### 18.3 Batch integration scenarios

- clean full build;
- identical batch rerun;
- lookback incremental run;
- customer correction;
- product correction;
- missing input file;
- malformed input row and dead letter;
- row-count mismatch;
- hard-delete simulation;
- failure before partition replacement;
- failure after partition replacement;
- ClickHouse restart between Airflow retries.

### 18.4 CDC integration scenarios

- initial snapshot;
- create event;
- multiple ordered updates;
- out-of-order object arrival;
- hard delete;
- tombstone coverage;
- duplicate manifest discovery;
- duplicate Parquet delivery;
- explicit replay;
- expired claim;
- insert acknowledgement loss;
- offset gap;
- payload mismatch for an existing event identity;
- transform failure before and after dbt completion;
- product translation affecting related orders;
- customer/product/seller changes propagating to facts and marts;
- publication approval and rejection.

### 18.5 Observability tests

- ClickHouse Prometheus endpoint is scrapeable;
- the removed warehouse PostgreSQL exporter is absent;
- OLTP PostgreSQL metrics remain;
- control and ClickHouse exporter health are independent;
- ClickHouse-down alert fires;
- reconciliation and freshness alerts retain existing semantics;
- dashboards load without missing data-source errors.

### 18.6 Performance acceptance for the migration

Performance optimization is not the first gate, but the migrated path must:

- stay within existing Airflow task and DAG timeouts on committed fixtures;
- avoid unbounded per-row inserts;
- avoid uncontrolled small-part growth;
- leave no pending failed mutation after a successful test;
- keep part counts stable after an idempotent rerun.

Record:

- dbt model duration;
- batch rows per second;
- CDC rows per second;
- parts per table and partition;
- ClickHouse query errors;
- disk usage.

Do not add projections, specialized codecs, or denormalized tables in the
migration pull request. Create a follow-up benchmark task using
`system.query_log`, `system.parts`, and representative mart queries.

## 19. CI Delivery and Cutover Sequence

### 19.1 Candidate period

Keep `local_pg` temporarily while adding `local_clickhouse`.

Use isolated Compose project names and volumes:

- one for the PostgreSQL oracle;
- one for the ClickHouse candidate.

Do not let both candidates share control state.

Required pull-request checks during the candidate period:

- fast PostgreSQL golden tests;
- fast ClickHouse batch fixture;
- ClickHouse synthetic CDC Stage 5;
- canonical cross-engine comparator;
- Redshift parse/compile;
- DAG import and static checks.

Run the full Debezium/Kafka/NiFi/MinIO parity workflow on demand and before
cutover.

### 19.2 Cutover gate

Cutover requires:

1. two consecutive green full ClickHouse candidate workflows;
2. zero row-count, grain-key, or canonical-hash mismatches;
3. successful duplicate/replay and crash-window tests;
4. successful batch-to-realtime parity;
5. healthy ClickHouse Prometheus target;
6. current Redshift validation still green;
7. updated runbooks reviewed from a clean environment.

### 19.3 Removal

After the default switch and one final ClickHouse-only smoke run, remove the
oracle in the next reviewable change. Do not leave a dormant but untested
`local_pg` target.

## 20. Rollback and Local Data Handling

### 20.1 Before PostgreSQL removal

Rollback consists of:

- setting `DBT_TARGET=local_pg`;
- using the PostgreSQL oracle Compose configuration;
- leaving ClickHouse volumes untouched for diagnosis.

This is a temporary migration mechanism, not a supported long-term mode.

### 20.2 After PostgreSQL removal

Rollback consists of:

1. reverting to the last pre-removal commit;
2. starting its PostgreSQL warehouse services;
3. rebuilding batch data from the source archive;
4. replaying required immutable CDC landing objects.

No reverse ClickHouse-to-PostgreSQL data migration is required.

### 20.3 Volume cleanup

Do not automatically delete the old PostgreSQL warehouse volume during
cutover. Remove it only through an explicit documented maintenance command
after the ClickHouse-only acceptance gate.

Do not use `docker compose down -v` as the standard migration instruction
because it also removes Airflow metadata, control, OLTP, Kafka, and MinIO
volumes.

## 21. Documentation Updates

Update at least:

- root `README.md`;
- architecture documentation;
- local Windows runbook;
- local macOS/Linux runbook;
- CI documentation;
- CDC operations documentation;
- observability documentation;
- `.env.example`;
- dbt profile example.

The final documentation must clearly distinguish:

- ClickHouse analytical settings;
- Airflow PostgreSQL settings;
- control PostgreSQL settings;
- OLTP PostgreSQL settings;
- Redshift settings.

Document:

- clean startup;
- ClickHouse client access;
- batch DAG execution;
- realtime profile startup;
- CDC replay;
- quality checks;
- Elementary report location;
- Prometheus/Grafana access;
- targeted cleanup of the obsolete warehouse volume;
- recovery from a failed batch or CDC insert.

## 22. Expected File Change Map

This is a navigation aid, not a requirement to combine all edits into one
commit.

| Area                                       | Expected change                                                     |
| ------------------------------------------ | ------------------------------------------------------------------- |
| `compose.yaml`                             | Add ClickHouse/control init; remove warehouse PostgreSQL at cutover |
| `docker/clickhouse/`                       | New image, entrypoint, and server configuration                     |
| `docker/airflow/`                          | Resolve ClickHouse/control secrets and install dependencies         |
| `infra/clickhouse/`                        | New databases, raw tables, runtime table, grants                    |
| `infra/control-postgres/`                  | Moved and strengthened audit/control DDL                            |
| `pyproject.toml`, `uv.lock`                | Add ClickHouse adapter/client and Elementary extra                  |
| `dbt/olist_analytics/profiles.yml.example` | Add `local_clickhouse`, later remove `local_pg`                     |
| `dbt/olist_analytics/macros/`              | Cross-adapter compatibility and CDC relation macros                 |
| `dbt/olist_analytics/models/`              | Portable SQL and ClickHouse materializations                        |
| `dbt/olist_analytics/tests/`               | Golden leaf tests and target-specific operational tests             |
| `scripts/loading/`                         | Replace PostgreSQL raw loader                                       |
| `scripts/cdc/`                             | Split control and ClickHouse data-plane responsibilities            |
| `scripts/orchestration/`                   | Use explicit control PostgreSQL repository                          |
| `scripts/quality/`                         | Add Python control-state gates                                      |
| `airflow/dags/`                            | ClickHouse target, commands, tags, and quality ordering             |
| `observability/`                           | ClickHouse scrape, dashboards, rules, exporter settings             |
| `.github/workflows/`                       | Candidate, parity, cutover, and final ClickHouse jobs               |
| `docs/`                                    | Architecture, runbooks, CI, and operations updates                  |

## 23. Completion Checklist

### Infrastructure

- [ ] ClickHouse uses the pinned full version tag.
- [ ] ClickHouse initializes correctly on a new and existing volume.
- [ ] `olist_control` initializes correctly on a new and existing Airflow
      PostgreSQL volume.
- [ ] ClickHouse and control credentials use Docker secrets.
- [ ] Host ports do not conflict with MinIO.
- [ ] Default Compose no longer starts an analytical PostgreSQL service.

### Data plane

- [ ] All batch raw entities load through atomic partition replacement.
- [ ] All eight CDC entities load through deterministic, deduplicated inserts.
- [ ] CDC staging reads are logically deduplicated.
- [ ] Cross-store crash windows are covered by integration tests.
- [ ] Existing local data is reproducibly rebuilt from source artifacts.

### dbt

- [ ] One shared project serves ClickHouse and Redshift.
- [ ] All leaf models have golden unit coverage.
- [ ] Shared model SQL contains no forbidden PostgreSQL dialect.
- [ ] Stable surrogate hashes match across targets.
- [ ] Snapshots pass rerun and correction scenarios.
- [ ] Facts and realtime marts use complete-partition replacement.
- [ ] ClickHouse does not use `merge` or mutable delete pre-hooks.
- [ ] Elementary runs against ClickHouse.

### Control plane and orchestration

- [ ] Airflow metadata and `olist_control` use different databases and roles.
- [ ] Batch and CDC control state uses only `CONTROL_POSTGRES_*`.
- [ ] Operational quality checks run in Python.
- [ ] Transform selection is projected into ClickHouse with a deterministic
      digest.
- [ ] Checkpoints commit only after ClickHouse validation.

### CI and operations

- [ ] Cross-engine comparator reports zero semantic mismatches.
- [ ] Two consecutive full ClickHouse candidate runs pass.
- [ ] ClickHouse-only CI passes after oracle removal.
- [ ] Redshift validation remains green.
- [ ] ClickHouse Prometheus metrics and alerts work.
- [ ] OLTP PostgreSQL monitoring remains intact.
- [ ] Windows and macOS/Linux runbooks reproduce the stack.

### Cleanup

- [ ] `local_pg` is removed.
- [ ] The analytical PostgreSQL service and exporter are removed.
- [ ] The old PostgreSQL loader and raw DDL are removed.
- [ ] The direct `dbt-postgres` dependency is removed.
- [ ] No active documentation describes PostgreSQL as the local warehouse.
- [ ] Old warehouse volume cleanup is documented but not automatic.
