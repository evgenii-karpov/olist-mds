# Near-Realtime CDC Implementation Plan

## Document Control

| Field             | Value                                                             |
| ----------------- | ----------------------------------------------------------------- |
| Status            | Approved implementation plan                                      |
| Last updated      | 2026-07-16                                                        |
| Repository        | `olist-mds`                                                       |
| Primary audience  | AI implementation agents and maintainers                          |
| Delivery strategy | Complete the local path first, then build an independent AWS path |
| Target latency    | p95 PostgreSQL commit-to-mart latency of at most 5 minutes        |
| Event format      | Avro with a schema registry                                       |

This document is the source of truth for adding a near-realtime data path to the
project. It is intentionally self-contained. An implementation agent must be
able to execute any phase without access to the conversation that produced this
plan.

The plan does not replace the existing batch architecture. It adds a second,
isolated ingestion and transformation path and defines how the two paths are
validated, published, operated, and compared.

## 1. Executive Summary

The project currently implements on-demand batch ingestion of the static Olist
dataset into PostgreSQL locally or S3 and Redshift on AWS, followed by dbt. The
new capability will add a production-oriented change data capture path:

1. A dedicated PostgreSQL OLTP database contains Olist-shaped tables.
2. A deterministic workload simulator seeds the database and generates inserts,
   updates, and deletes.
3. Debezium reads PostgreSQL WAL through Kafka Connect.
4. Kafka stores keyed Avro change events.
5. Apache NiFi continuously consumes Kafka, validates and batches events, and
   writes immutable Avro and normalized Parquet objects.
6. Airflow loads closed Parquet objects into an append-only warehouse CDC layer
   every two minutes.
7. An Airflow Asset event triggers incremental dbt current-state, history, fact,
   and mart models.
8. Prometheus and Grafana expose component health and end-to-end data latency.
   Loki is added after the metrics baseline. Tempo is a later learning exercise,
   not a core acceptance requirement.

The local and AWS deployments must never depend on one another. They share
source code and logical contracts, but not databases, buckets, topics, secrets,
state, or runtime services.

## 2. Current Repository Baseline

Implementation must preserve these existing behaviors unless a phase explicitly
changes them:

- `compose.yaml` runs PostgreSQL for the local warehouse, a separate Airflow
  metadata PostgreSQL database, and Airflow with LocalExecutor.
- `airflow/dags/olist_modern_data_stack_local.py` is a manual batch DAG for local
  files, PostgreSQL, dbt, and Elementary.
- `airflow/dags/olist_modern_data_stack_aws.py` is a manual batch DAG for S3,
  Redshift, dbt, and Elementary.
- Existing raw data is append-only and identified by `_batch_id`, `_loaded_at`,
  `_source_file`, and `_source_system`.
- Existing dbt staging models deduplicate batch rows by load metadata.
- Existing customer and product SCD2 models use dbt snapshots and deterministic
  correction feeds.
- Existing marts are `mart_daily_revenue` and `mart_monthly_arpu`.
- Existing CI runs lint, Python tests, dbt parsing, Airflow import checks, and a
  local fixture integration pipeline.
- The repository has SQL bootstrap directories for PostgreSQL and Redshift but
  no Terraform infrastructure and no Kafka, Debezium, NiFi, MinIO, Prometheus,
  Grafana, Loki, or workload simulator.

Existing batch schemas remain unchanged:

- `raw_data`
- `staging`
- `intermediate`
- `snapshots`
- `core`
- `marts`
- `audit`

The realtime path must use separate schemas and must not reinterpret batch load
timestamps as CDC ordering metadata.

## 3. Goals and Success Criteria

### 3.1 Goals

- Demonstrate realistic PostgreSQL log-based CDC, Kafka operations, NiFi data
  movement, object-storage landing, warehouse micro-batching, and incremental
  dbt modeling.
- Preserve inserts, updates, hard deletes, transaction metadata, primary keys,
  schema versions, source ordering, and Kafka offsets.
- Achieve an effectively-once warehouse outcome on top of at-least-once
  delivery.
- Meet a p95 commit-to-published-mart latency of 5 minutes under the reference
  workload.
- Support deterministic replay, reconciliation, recovery, and controlled
  resnapshot procedures.
- Make failures observable through metrics, dashboards, logs, audit tables, and
  actionable alerts.
- Keep the local environment reproducible on Docker Compose and the AWS
  environment reproducible through Terraform.
- Retain the existing batch path as a backfill, regression, and comparison
  workflow.

### 3.2 Core acceptance criteria

The implementation is complete only when all of the following are true:

- An initial Debezium snapshot produces warehouse current state equivalent to
  the seeded OLTP state.
- Inserts, multiple updates, and hard deletes reach realtime marts correctly.
- Replaying Kafka records, object files, or Airflow runs does not duplicate
  warehouse events or mart rows.
- Reordering object arrival does not produce stale current state.
- Restarting Kafka Connect, NiFi, or Airflow does not lose committed source
  changes.
- Offset gaps, duplicate events, quarantined records, source-to-mart latency, and
  mart freshness are visible in audit tables and Grafana.
- A backward-compatible nullable column can be introduced without interruption.
- A breaking Avro schema change is rejected by CI or registry compatibility
  rules before it reaches production data.
- The existing batch fixture integration tests continue to pass.
- The local path meets the latency SLO at 5 simulated order lifecycles per second
  for 30 minutes, including a 20 lifecycles per second burst.
- The AWS path passes the same logical contract tests without accessing local
  infrastructure.

### 3.3 Non-goals

- Sub-second analytical serving.
- End-to-end exactly-once guarantees across PostgreSQL, Kafka, NiFi, S3, Airflow,
  Redshift, and dbt.
- Replacing Kafka or NiFi with AWS-native alternatives.
- Running NiFi on EKS in the initial AWS implementation.
- Building a highly available NiFi cluster in the initial implementation.
- Merging duplicate batch and CDC copies of the same Olist records.
- Replacing the existing batch DAGs.
- Capturing the large geolocation reference table in the first CDC release.

## 4. Target Architecture

### 4.1 Logical flow

The logical flow is:

`PostgreSQL OLTP -> Debezium/PostgreSQL connector -> Kafka -> NiFi -> object storage -> warehouse raw CDC -> dbt realtime models -> published analytics views`

Continuous services are PostgreSQL, Kafka, Kafka Connect, schema registry, NiFi,
and telemetry collectors. Airflow does not host or supervise those services. It
orchestrates finite, idempotent micro-batches after NiFi has closed object files.

### 4.2 Environment mapping

| Capability       | Local implementation                            | AWS implementation                                   |
| ---------------- | ----------------------------------------------- | ---------------------------------------------------- |
| OLTP source      | Dedicated PostgreSQL container                  | Amazon RDS for PostgreSQL                            |
| CDC runtime      | Distributed Kafka Connect                       | Amazon MSK Connect                                   |
| CDC connector    | Debezium PostgreSQL connector                   | Same Debezium connector as a versioned custom plugin |
| Kafka            | Apache Kafka in KRaft mode                      | Amazon MSK Provisioned                               |
| Schema registry  | Apicurio Registry with Confluent-compatible wire format | AWS Glue Schema Registry                        |
| NiFi             | One Docker container with persistent volumes    | One private EC2 instance with persistent EBS         |
| Object storage   | MinIO                                           | Amazon S3                                            |
| Warehouse        | Existing local PostgreSQL, separate CDC schemas | Amazon Redshift Serverless                           |
| Orchestration    | Docker Compose Airflow                          | Amazon MWAA                                          |
| Metrics          | Prometheus, Alertmanager, Grafana               | CloudWatch plus Grafana Cloud                        |
| Collection agent | Grafana Alloy where needed                      | Alloy on the NiFi EC2 host                           |
| Logs             | Loki after the metrics milestone                | Grafana Cloud Logs and selected CloudWatch logs      |
| Secrets          | Docker secrets and ignored local files          | AWS Secrets Manager and IAM roles                    |

### 4.3 Latency budget

The 5-minute p95 SLO is allocated as follows:

| Stage                                 | Maximum expected wait under normal load |
| ------------------------------------- | --------------------------------------- |
| PostgreSQL commit to Kafka            | 15 seconds                              |
| Kafka to closed NiFi object           | 60 seconds                              |
| Closed object to Airflow ingest start | 120 seconds                             |
| Warehouse load and reconciliation     | 60 seconds                              |
| Asset-triggered dbt transformation    | 45 seconds                              |
| Scheduling and operational margin     | 60 seconds                              |

The individual values are operational targets, not separate hard SLOs. The
authoritative SLO is measured end to end from source change timestamp to the
timestamp at which the corresponding published mart row is committed.

### 4.4 Initial version baseline

Use this baseline as of the document date. Phase 0 must confirm compatibility
before implementation. Pin exact images and artifacts; do not silently move to
newer releases during later phases.

| Component                        | Baseline                                                                                  |
| -------------------------------- | ----------------------------------------------------------------------------------------- |
| PostgreSQL                       | 18.4 locally; an RDS PostgreSQL version supported by the selected Debezium release on AWS |
| Apache Kafka                     | 4.3.1 locally                                                                             |
| Debezium                         | 3.6.0.Final                                                                               |
| Apache NiFi                      | 2.10.0                                                                                    |
| Apicurio Registry                | 3.3.0                                                                                     |
| Apache Airflow                   | 3.2.1 for local and MWAA parity                                                           |
| Python                           | 3.12 for the shared Airflow/runtime package                                               |
| dbt Core                         | Existing 1.11.x line, initially 1.11.8                                                    |
| dbt PostgreSQL/Redshift adapters | Existing compatible 1.10.x lines                                                          |
| MSK Connect worker               | AWS-supported Kafka Connect 3.7.x worker, validated against the Debezium plugin           |

If a baseline combination proves incompatible, amend the relevant ADR with the
test evidence and select one explicitly pinned replacement. Do not resolve a
compatibility failure by using floating tags.

## 5. Architecture Decision Records

### ADR-001: Use Debezium for PostgreSQL CDC

**Status:** Accepted.

**Context:** The project must teach PostgreSQL log-based CDC, Kafka, and Kafka
Connect. Polling on `updated_at` misses deletes and can miss intermediate
updates. AWS DMS is operationally useful but hides much of Kafka Connect and
Debezium behavior.

**Decision:** Use the Debezium PostgreSQL connector with `pgoutput`, a dedicated
replication user, an explicitly managed publication and replication slot,
initial snapshot mode, transaction metadata, and heartbeats.

**Consequences:** Agents must handle WAL retention, replication slot monitoring,
delete semantics, schema history, connector compatibility, and controlled
resnapshot operations. AWS DMS is reserved for an optional comparison exercise.

**Rejected alternatives:** JDBC timestamp polling, NiFi-based database polling,
and AWS DMS as the primary implementation.

### ADR-002: Treat OLTP plus Debezium snapshot as the realtime source of truth

**Status:** Accepted.

**Context:** The CSV batch data and OLTP seed can represent the same Olist
business records. Loading both into one model would duplicate data and create
ambiguous ownership.

**Decision:** The realtime path starts from a Debezium initial snapshot of the
new OLTP database and continues with CDC. The existing CSV pipeline remains a
separate batch/backfill/regression path. Batch and realtime data use separate
warehouse schemas. They are compared, never unioned.

**Consequences:** A parity gate is required before realtime models become the
published consumer interface. Existing batch models remain supported.

### ADR-003: Use near-realtime micro-batches for Redshift and dbt

**Status:** Accepted.

**Context:** Kafka and NiFi are continuous systems, while Redshift and dbt are
most naturally operated in bounded batches. Rebuilding marts for every event is
inefficient and difficult to recover.

**Decision:** NiFi closes event files within 60 seconds. Airflow ingests closed
files every two minutes. A successful load emits an Airflow Asset event that
triggers an incremental dbt DAG. Full quality and Elementary checks run less
frequently.

**Consequences:** The result is near-realtime, not per-event streaming. A future
Redshift streaming-ingestion experiment must remain separate because it bypasses
the required NiFi-to-S3 path.

### ADR-004: Use Avro and environment-native schema registries

**Status:** Accepted.

**Context:** Schema-aware events and evolution checks are required. The user has
selected Avro. Running Apicurio in AWS adds unnecessary operational work, while
using Glue locally would couple the local path to AWS.

**Decision:** Use Apicurio Registry locally and AWS Glue Schema Registry on AWS.
Both enforce backward-transitive compatibility and represent the same logical
Kafka Connect schemas. Locally, the Debezium converters register through the
Apicurio v2 API and emit Confluent-compatible framing; consumers resolve the
numeric content ID through the ccompat v7 API. Environment adapters may use
different wire framing.

**Consequences:** NiFi reader configuration is environment-specific, while the
normalized event contract is shared. Apicurio content IDs are registry state,
not portable logical schema versions. CI must test logical compatibility rather
than byte-for-byte registry framing.

### ADR-005: Keep streaming services outside Airflow and split CDC DAGs

**Status:** Accepted.

**Context:** Airflow is not a service supervisor or stream processor. A single
large DAG would couple unrelated schedules, failure domains, and recovery paths.

**Decision:** Compose and Terraform manage Kafka, Connect, NiFi, telemetry, and
registries. Airflow provides separate ingest, transform, quality, and manual
backfill DAGs per environment.

**Consequences:** Service readiness and deployment are handled by infrastructure
automation and health checks. DAGs remain finite, idempotent, observable, and
independently retryable.

### ADR-006: Use at-least-once transport and effectively-once warehouse writes

**Status:** Accepted.

**Context:** End-to-end exactly-once across all selected systems cannot be
claimed honestly. Retries can duplicate Kafka consumption, object writes, and
warehouse load attempts.

**Decision:** Define `_event_id` as `topic:partition:offset`. Maintain immutable
object manifests, a warehouse file ledger, partition watermarks, and event-level
deduplication. Current state is ordered by source LSN and transaction order,
then Kafka offset, never by ingestion time.

**Consequences:** Replay is safe and measurable. Redshift constraints are not
trusted for enforcement; dbt and loader tests verify uniqueness.

### ADR-007: Keep NiFi simple on AWS

**Status:** Accepted.

**Context:** The project is educational and cost-sensitive. The user already
learns EKS elsewhere. A production-grade NiFi cluster on EKS would dominate the
scope and cost before the data semantics are proven.

**Decision:** Run one NiFi node on a private EC2 instance with persistent EBS,
TLS, SSM access, backups, metrics, and restart automation. Do not expose a public
IP. Stop the instance outside learning sessions when appropriate.

**Consequences:** This deployment is not highly available. Kafka retention and
S3 durability protect data during NiFi downtime. NiFi clustering is a documented
future exercise, not a hidden assumption.

### ADR-008: Metrics first, logs second, traces last

**Status:** Accepted.

**Context:** Prometheus and Grafana are mandatory. Centralized logs materially
improve troubleshooting. Distributed traces have lower immediate value because
Debezium, Kafka, and NiFi do not automatically propagate one end-to-end trace
context through this data flow.

**Decision:** Implement Prometheus, Grafana, Alertmanager, dashboards, and SLO
metrics alongside the local data path. Add Loki and Alloy during hardening. Add
Tempo only as a later proof of concept for custom Python components.

**Consequences:** Tempo is not a release gate. Correlation identifiers are still
preserved in event metadata, audit rows, and structured logs.

### ADR-009: Build local first and keep AWS independent

**Status:** Accepted.

**Context:** Debugging data correctness and cloud infrastructure simultaneously
would slow learning and make failures ambiguous.

**Decision:** Complete and stabilize the local end-to-end path before creating
AWS resources. The AWS path reuses contracts and application artifacts but has
its own state, endpoints, storage, secrets, and tests.

**Consequences:** No AWS phase may require a running local container. No local
phase may require AWS credentials.

### ADR-010: Align the shared Airflow code with MWAA

**Status:** Accepted with a verification gate.

**Context:** The repository currently targets Airflow 3.3.0 and Python 3.13,
while the current MWAA target is Airflow 3.2.1 and Python 3.12.

**Decision:** During Phase 0, prove the existing DAGs and dependencies on Airflow
3.2.1 and Python 3.12, then use that combination for the shared runtime. Change
the project Python range to include 3.12. Do not use Airflow 3.3-only APIs in
shared DAG code. If AWS adds a newer supported version before implementation,
record an ADR amendment and use one version in both local and MWAA.

**Consequences:** Runtime parity is prioritized over using the newest local
Airflow release. The existing batch pipeline must pass before the version change
is accepted. For this implementation workspace, the current local PostgreSQL
18.4 analytics volume and Airflow metadata volume are disposable and may be
deleted when changing the shared runtime or resetting integration tests. No
existing local rows or Airflow history need to be migrated or preserved. This
permission does not extend to future immutable CDC landing objects, AWS state,
or any environment explicitly designated as non-disposable.

## 6. Source OLTP Contract

### 6.1 Database isolation

The OLTP source must be a distinct PostgreSQL database or service from both the
local analytics warehouse and Airflow metadata database. Reusing the warehouse
would create a feedback loop and invalidate CDC lineage.

Use business columns from `docs/source_contract.md`, but apply OLTP-appropriate
types, primary keys, foreign keys, and indexes. Preserve leading-zero zip prefixes
as strings.

### 6.2 Entity keys and initial CDC scope

| Entity                         | Primary key                      | Important foreign keys             | Initial CDC               |
| ------------------------------ | -------------------------------- | ---------------------------------- | ------------------------- |
| `customers`                    | `customer_id`                    | none                               | Yes                       |
| `orders`                       | `order_id`                       | `customer_id -> customers`         | Yes                       |
| `order_items`                  | `(order_id, order_item_id)`      | order, product, seller             | Yes                       |
| `order_payments`               | `(order_id, payment_sequential)` | order                              | Yes                       |
| `order_reviews`                | `(review_id, order_id)`          | order                              | Yes                       |
| `products`                     | `product_id`                     | category translation where present | Yes                       |
| `sellers`                      | `seller_id`                      | none                               | Yes                       |
| `product_category_translation` | `product_category_name`          | none                               | Yes                       |
| `geolocation`                  | generated `geolocation_id`       | none                               | No; seeded reference only |

All original dataset columns must remain available. The generated geolocation
key is technical and exists because the source dataset has no stable unique key.

Indexes must support all foreign keys and generator lookup paths. Constraints
must reject invalid state instead of relying only on simulator correctness.

### 6.3 Simulator control schema

Create a separate non-captured schema for:

- simulation runs and random seeds;
- generated entity identifiers;
- scheduled future lifecycle transitions;
- simulator heartbeat and current run state;
- replay source timestamp mappings.

Do not add simulator-only ownership columns to Olist business tables. Synthetic
IDs may use a stable prefix that fits the source column types.

### 6.4 Workload simulator interface

The simulator must expose these stable commands:

- `seed`: load reference entities and the initial OLTP baseline in FK-safe order;
- `replay`: reconstruct inferred Olist order lifecycles with shifted timestamps
  and a configurable speed multiplier;
- `run`: continuously generate new business activity;
- `status`: report run identity, seed, rate, pending transitions, and last commit;
- `stop`: request a graceful stop after the current transaction.

Every mutating command accepts a stable random seed. Replay and finite run modes
must accept a duration or event limit. Continuous mode accepts target lifecycle
rate and bounded probabilities for cancellation, correction, review, and hard
delete.

The generated lifecycle is:

1. Select or create customer, product, and seller references.
2. In one transaction, create an order and its items and payment records.
3. Schedule realistic transitions from `created` to `approved`, `shipped`, and
   `delivered`, or to `canceled`/`unavailable`.
4. Optionally add a review after delivery.
5. Occasionally correct mutable customer or product attributes.
6. Rarely hard-delete only simulator-owned records in FK-safe order.

The simulator must never alter or delete seeded historical records in destructive
test scenarios. A fixed seed and configuration must produce the same sequence of
business decisions and identifiers.

## 7. CDC and Kafka Contract

### 7.1 Debezium requirements

- Use `pgoutput` and a manually named publication and replication slot.
- Use a dedicated replication role with only required source-table access.
- Set `snapshot.mode=initial` for normal bootstrap.
- Capture transaction metadata and source timestamps.
- Include only initial CDC-scope tables.
- Use `REPLICA IDENTITY FULL` on captured tables for reliable before images and
  deletes in this educational workload.
- Enable tombstones. They remain null values on the source topic after the
  `op=d` business event; downstream consumers must not normalize them as a
  second delete.
- Configure periodic heartbeats and a heartbeat action query that advances WAL
  during otherwise idle periods.
- Set `tasks.max=1`; a PostgreSQL logical stream is not parallelized by adding
  connector tasks.
- Do not let the connector auto-create source topics in production-like modes.
- Persist and monitor schema history and Connect internal topics.

### 7.2 Topic naming and sizing

Source topics use `olist_cdc.public.<table>`. Additional topics include:

- `olist_cdc.dlq.<table>` for records rejected before successful NiFi landing;
- compacted Connect config, offset, status, and Debezium schema-history topics;
- `olist_cdc.transaction` for transaction boundary metadata;
- `olist_cdc.heartbeat` for consumer-facing heartbeat records. Debezium derives
  `<heartbeat-prefix>.<topic-prefix>` first; a heartbeat-only predicate and
  `RegexRouter` map that derived name to the fixed topic without changing
  business topics.

Local default:

- one Kafka broker in KRaft mode;
- replication factor 1;
- three partitions for orders, items, payments, and reviews;
- one partition for customer, product, seller, and translation topics.

AWS lab default:

- two MSK Provisioned `kafka.t3.small` brokers across two Availability Zones;
- replication factor 2 and minimum in-sync replicas 1;
- the same partition counts as local.

The project must document that the AWS lab profile is cost-conscious, not a
production HA profile. Kafka retention is 7 days for source, heartbeat,
transaction, and reserved DLQ topics. Internal and schema-history topics use
compaction and unlimited logical retention. The version-controlled local
manifest contains 22 explicit topics; auto-creation is disabled. Phase 2 only
reserves the eight table DLQs, and Phase 3 owns their first producer.

### 7.3 Local Avro wire contract

Keys and non-null values use Confluent-compatible framing: magic byte `0`, a
four-byte big-endian numeric Apicurio content ID, then Avro payload bytes.
Resolve the content ID through ccompat `/schemas/ids/<id>` and recursively
resolve schema references before decoding. Main subjects use `<topic>-key` and
`<topic>-value`; referenced Debezium table `Value`, PostgreSQL `Source`, and
transaction record subjects are expected registry state. Tombstones have a null
value and therefore no value schema framing.

### 7.4 Event identity and order

The immutable event identifier is:

`<topic>:<partition>:<offset>`

Business ordering is determined by the following tuple, in order:

1. source LSN;
2. `source.txId` and Debezium transaction event order when present;
3. Kafka partition offset.

With Debezium 3.6 PostgreSQL events, `source.txId` is the shared PostgreSQL
transaction identity. The envelope transaction ID contains an event-specific
LSN and must not be used by itself to group all events from one transaction.

Warehouse ingestion timestamps are never used to decide which source row is
current. Kafka keys must be derived from source primary keys so all changes for
one source key remain ordered within a partition.

### 7.5 Schema evolution

- Registry compatibility is backward-transitive.
- Adding a nullable field with a default is allowed.
- Removing or renaming fields and incompatible type changes require a migration
  plan and must fail compatibility checks.
- NiFi groups records by source table, Kafka partition, and schema identifier so
  one output file never silently mixes incompatible schemas.
- Wire schema identifiers are retained in object and warehouse metadata for
  decoding and audit, but registry-assigned IDs must not be treated as logical
  schema versions across resets or environments.

## 8. NiFi and Object Storage Contract

### 8.1 Flow behavior

Use one version-controlled, parameterized NiFi process group for both local and
AWS. Environment parameter contexts provide bootstrap servers, registry details,
bucket names, credentials or IAM integration, TLS material, and path prefixes.

For every consumed event, the NiFi session must complete both branches before
the Kafka offset is committed:

1. Preserve the complete Debezium envelope in the immutable landing zone.
2. Produce a typed normalized record for warehouse loading.

For create, read-snapshot, and update events, normalized business columns come
from `after`. For delete events, they come from `before`. Tombstones are counted
and audited but do not produce a second normalized delete.

### 8.2 Normalized event fields

Every normalized table record contains typed source business columns plus:

| Field              | Meaning                                               |
| ------------------ | ----------------------------------------------------- |
| `_event_id`        | Kafka topic, partition, and offset identity           |
| `_op`              | Debezium operation: `r`, `c`, `u`, or `d`             |
| `_source_ts`       | Source change/commit timestamp supplied by Debezium   |
| `_source_lsn`      | PostgreSQL WAL position                               |
| `_tx_id`           | Source transaction identifier when available          |
| `_tx_order`        | Position inside the source transaction when available |
| `_topic`           | Kafka topic                                           |
| `_partition`       | Kafka partition                                       |
| `_offset`          | Kafka offset                                          |
| `_kafka_ts`        | Kafka record timestamp                                |
| `_schema_id`       | Registry schema identifier                            |
| `_nifi_written_at` | Timestamp at which NiFi finalized the record batch    |

### 8.3 Object layouts

Use the same logical paths in MinIO and S3:

- `landing/debezium/table=<table>/event_date=<date>/hour=<hour>/...avro`
- `stage/cdc/table=<table>/ingest_date=<date>/hour=<hour>/...parquet`
- `quarantine/stage=<stage>/reason=<reason>/event_date=<date>/...`

File names include topic, partition, minimum offset, maximum offset, schema ID,
and a collision-resistant suffix. Objects are immutable and never overwritten.

Target file size is 32-64 MB. To meet the latency SLO, a bin closes after 60
seconds even if it is small. Monitor small-file rate and compact only into a
separate query-optimized prefix; never replace files referenced by the warehouse
ingest ledger.

### 8.4 Failure handling

- Transient Kafka, registry, or object-storage failures use bounded exponential
  backoff and NiFi backpressure.
- Invalid data and incompatible schemas go to a quarantine object prefix and a
  DLQ topic with reason, processor, schema ID, and original Kafka coordinates.
- Stock NiFi `ConsumeKafka` commits after the consumed FlowFile is durably
  accepted by the NiFi repositories; it cannot defer that commit until an
  arbitrary downstream S3 branch completes. Failed object writes therefore
  remain replayable in the persistent FlowFile/content repositories, and
  backpressure must stop further consumption before repository exhaustion.
- NiFi provenance remains enabled with bounded retention.
- Persistent repositories survive container or EC2 restarts.
- The deployment defines disk thresholds before NiFi repositories can exhaust
  the host filesystem.

## 9. Warehouse and dbt Contract

### 9.1 Realtime warehouse schemas

Add these schemas without renaming existing batch schemas:

- `raw_cdc`: append-only typed CDC events, one table per captured entity;
- `realtime_staging`: normalized event, current-state, and changed-key models;
- `realtime_core`: CDC-derived dimensions, facts, and histories;
- `realtime_marts`: near-realtime business marts;
- `cdc_audit`: file, run, watermark, reconciliation, latency, and error state;
- `analytics`: stable published views created only after parity approval.

### 9.2 Audit model

At minimum, create these logical audit tables:

- `cdc_ingest_runs`: run ID, DAG/run metadata, start/end, status, counts, and
  failure summary;
- `cdc_files`: object URI, object version or ETag, table, partition, offset range,
  schema ID, row count, status, first/last attempt, and ingest run ID;
- `cdc_partition_watermarks`: topic, partition, last contiguous offset, source
  LSN, source timestamp, and update time;
- `cdc_reconciliation`: source/object/warehouse counts, duplicates, gaps, and
  pass/fail result;
- `cdc_dead_letters`: Kafka coordinates, stage, reason, schema ID, object URI,
  and resolution status;
- `cdc_mart_freshness`: model, maximum represented source timestamp, build time,
  latency, and build run ID.

The loader claims files through the ledger, loads an immutable manifest, inserts
only unseen `_event_id` values, validates offset continuity, and commits ledger
status and watermarks only after data commit. A failed run must be safely
retryable.

The local adapter loads Parquet records into PostgreSQL staging tables and then
performs the transactional ledger/deduplication step. The AWS adapter creates an
immutable S3 manifest and uses Redshift `COPY` from Parquet into temporary or
run-scoped staging tables before the same logical ledger/deduplication step.
Redshift `COPY JOB` and Auto Copy are not part of the primary implementation;
they remain Phase 8 comparison topics so Airflow retains explicit ownership of
idempotency, reconciliation, and Asset emission.

### 9.3 dbt realtime model behavior

- Event staging models preserve all CDC metadata and validate operation values.
- Current-state models select the latest ordered event per source primary key and
  exclude keys whose latest operation is `d`.
- History models derive SCD2 intervals from every ordered CDC event, not dbt
  snapshot execution times. They expose `valid_from`, `valid_to`, `is_current`,
  and `is_deleted`, plus ordering columns for equal timestamps.
- Changed-key models identify impacted order, customer, product, and date keys
  between committed watermarks.
- Facts use merge or delete-plus-insert for affected natural keys. A hard delete
  removes the current fact while remaining visible in history and audit data.
- Marts recalculate only impacted date/month partitions or business keys.
- The existing batch snapshot models remain unchanged.
- Shared calculation macros should be extracted where batch and realtime
  business logic is identical; do not copy complex revenue/allocation logic into
  two divergent implementations.

### 9.4 Publication and parity

Before publication, compare the Debezium initial snapshot result with the
existing batch result at equivalent grains:

- current entity counts and primary-key checksums;
- fact grain and allocated payment totals;
- customer/product current attributes;
- daily revenue and monthly ARPU within documented numeric tolerances.

Once parity passes, create `analytics` views that point to realtime marts. Do not
rename or drop batch marts. Publication must be reversible by changing views.

## 10. Airflow Contract

Create environment-specific DAG IDs through shared factories or shared task
modules. Environment-specific logic is limited to storage and warehouse
adapters.

| DAG                                                     | Trigger             | Responsibility                                                                                                                  |
| ------------------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `olist_cdc_ingest_local` / `olist_cdc_ingest_aws`       | Every 2 minutes     | Discover closed files, claim manifest, load, deduplicate, reconcile, update watermarks, emit Asset only when data was committed |
| `olist_cdc_transform_local` / `olist_cdc_transform_aws` | Airflow Asset event | Build changed-key models, realtime core, affected marts, focused tests, and freshness audit                                     |
| `olist_cdc_quality_local` / `olist_cdc_quality_aws`     | Hourly              | Freshness, offset continuity, reconciliation, current-key integrity; midnight run also executes full dbt tests and Elementary   |
| `olist_cdc_backfill_local` / `olist_cdc_backfill_aws`   | Manual              | Replay selected table/date/object ranges from immutable storage without resetting Debezium                                      |

All CDC DAGs use `catchup=False`, `max_active_runs=1`, explicit pools, finite
timeouts, bounded retries, and failure callbacks that update `cdc_audit` without
masking the original exception.

Infrastructure bootstrap, connector registration, NiFi deployment, topic
creation, and destructive resnapshot are not normal DAG responsibilities. They
belong to Compose, Terraform, deployment scripts, and explicit runbooks.

## 11. Observability Contract

### 11.1 Local telemetry

Prometheus must scrape:

- Kafka broker JMX exporter;
- Kafka Connect and Debezium JMX metrics;
- source and warehouse PostgreSQL exporters;
- NiFi 2 REST metrics endpoint at `/nifi-api/flow/metrics/prometheus` using a
  read-only service identity;
- Airflow StatsD through `statsd_exporter`;
- MinIO native metrics;
- container and host metrics through cAdvisor/node exporter where practical;
- a small read-only pipeline exporter backed by `cdc_audit` tables.

Do not restore the removed NiFi 1.x `PrometheusReportingTask`.

The pipeline exporter exposes low-cardinality metrics for:

- stage and end-to-end latency;
- maximum source timestamp represented in raw/current/mart layers;
- event counts by table and operation;
- file count and size distributions;
- duplicates, offset gaps, DLQ, and quarantine counts;
- ingest and transform success timestamps;
- reconciliation status.

Allowed labels include environment, table, stage, operation, and status. Never
use order ID, event ID, run ID, object URI, or error text as Prometheus labels.

### 11.2 Dashboards

Provision dashboards from version-controlled definitions:

1. End-to-end SLO, throughput, freshness, and error budget.
2. PostgreSQL WAL, replication slot, simulator, and Debezium status.
3. Kafka broker, partitions, consumer lag, and Connect tasks.
4. NiFi queue depth, bytes, backpressure, processor errors, repository disk, and
   object file output.
5. Airflow ingest/transform duration, dbt status, warehouse load, and mart
   freshness.
6. Host/container capacity and AWS cost/resource overview.

### 11.3 Initial alert policy

- Connector or source task not running for 2 minutes.
- Debezium heartbeat absent for 3 minutes while the stack is expected to run.
- Retained WAL exceeds 512 MB and increases for 15 minutes.
- Any offset gap, DLQ record, or quarantined record.
- NiFi queue remains above 70% of its backpressure threshold for 5 minutes.
- p95 commit-to-mart latency exceeds 5 minutes for 10 minutes.
- New source events exist but no successful load or transform completes for 10
  minutes.
- More than 100 CDC files per table per hour or median file size below 1 MB after
  normal traffic is established.
- Airflow DAG failure, dbt test failure, or stale mart.

Thresholds must be tuned using benchmark evidence, but changes require a short
reason in observability documentation.

### 11.4 Logs and traces

During hardening, use Grafana Alloy to collect structured logs into Loki. Include
environment, service, table where relevant, `simulation_run_id`, `_event_id`, and
`cdc_run_id` in log bodies. Keep high-cardinality correlation values out of Loki
labels.

Tempo is implemented only after the core path. Instrument custom simulator,
loader, and dbt-wrapper code with OpenTelemetry and send spans through Alloy.
Do not claim a complete trace across uninstrumented Debezium, Kafka, and NiFi
boundaries.

## 12. Security and Secrets

### 12.1 Local

- Use Docker secrets or ignored environment files; commit only examples.
- Use a dedicated PostgreSQL replication account and separate warehouse account.
- Enable Kafka authentication/TLS and NiFi HTTPS during the hardening phase.
- Protect NiFi metrics and administration APIs with separate least-privilege
  identities.
- Never print connection strings, passwords, tokens, Avro registry credentials,
  or raw secret values in logs.

### 12.2 AWS

- Put RDS, MSK, Redshift, MWAA, and NiFi in private subnets.
- Access NiFi and private administration endpoints through SSM Session Manager;
  do not assign NiFi a public IP.
- Encrypt RDS, EBS, S3, MSK, Redshift, and secrets with KMS-supported mechanisms.
- Use IAM roles for S3, MSK, Glue, CloudWatch, and Redshift access.
- Use Secrets Manager backend prefixes for Airflow connections and variables.
- Use the MSK Connect Secrets Manager configuration provider for database
  credentials.
- Use the NiFi AWS Secrets Manager parameter provider for secrets that cannot use
  IAM directly.
- Scope Grafana Cloud access through delegated IAM roles. Store Grafana Cloud
  write credentials in Secrets Manager, not Terraform variables or outputs.
- Configure secret rotation and a tested connector/NiFi restart procedure.

## 13. AWS Infrastructure Profile

Create an independent Terraform root for the realtime AWS path with its own
remote state and environment naming. At minimum it provisions:

- a VPC spanning two Availability Zones, private subnets, routing, security
  groups, and required VPC endpoints;
- RDS PostgreSQL with a parameter group enabling logical replication;
- MSK Provisioned with two `kafka.t3.small` brokers for the lab profile;
- MSK Connect with one Debezium custom plugin artifact and autoscaling from one
  to two MCUs;
- Glue Schema Registry and compatibility configuration;
- versioned, encrypted S3 buckets for landing, stage, quarantine, artifacts, and
  MWAA;
- Redshift Serverless with explicit usage limits;
- MWAA using the shared supported Airflow/Python version;
- one private `t3.large` NiFi EC2 instance with separate persistent gp3 storage
  for critical repositories, automatic restart, backup, and SSM;
- CloudWatch log groups, alarms, retention, and dashboards or integration data;
- Grafana Cloud role delegation and Alloy configuration;
- AWS Budget alerts based on a required `monthly_budget_usd` input;
- mandatory project, environment, owner, and cost-center tags.

The default is a disposable lab environment. Documentation must identify which
resources continue to cost money while idle. The runbook must provide ordered
startup, shutdown, and teardown procedures and require a final RDS snapshot only
when explicitly requested.

Do not use MSK Serverless as the default: its permanent cluster-hour charge is
poorly matched to a small intermittent lab. Do not use EKS for NiFi in this
implementation.

## 14. Implementation Phases

Each phase is a separate deliverable. An agent must not start a later phase until
the previous phase exit criteria are met and documented.

Implementation status as of 2026-07-16:

| Phase | Status | Evidence and handoff |
| --- | --- | --- |
| 0 | Complete | `docs/cdc/phases/phase-0-baseline.md` |
| 1 | Complete | `docs/cdc/phases/phase-1-oltp-simulator.md`, `docs/cdc/handoffs/stage-2-kafka-debezium.md` |
| 2 | Complete | `docs/cdc/phases/phase-2-kafka-debezium.md`, `docs/cdc/handoffs/stage-3-nifi-minio.md` |
| 3-8 | Not started | Start only from the preceding phase handoff and current contracts in this plan |

Phase reports are the evidence record for completed work. This plan remains the
normative cross-phase contract; when verified implementation reveals a contract
detail that affects later phases, update both this plan and the relevant report
or handoff.

### Phase 0: Contracts, compatibility, and repository scaffolding

**Objectives**

- Lock terminology, runtime compatibility, directory ownership, and CI gates
  before introducing services.

**Required work**

- Validate Airflow 3.2.1/Python 3.12 against existing DAGs, scripts, dbt, and CI.
- Pin Kafka, Debezium, NiFi, registry, exporter, and telemetry images by exact
  version or digest; never use `latest`.
- Add Compose profiles for batch, realtime core, observability, and logs without
  changing the default batch start behavior.
- Establish directories for streaming assets, simulator code, observability,
  realtime SQL, and later AWS Terraform.
- Add schema compatibility checks and configuration validation stubs to CI.
- Record any necessary amendment to ADR-010 before changing runtime versions.

**Verification**

- Existing batch CI and fixture integration pass unchanged.
- Reset disposable local analytics and Airflow metadata volumes before the
  compatibility run; no Airflow 3.3.0 metadata migration is required.
- `docker compose config` passes for every profile combination.
- Airflow imports both existing batch DAGs under the chosen shared runtime.

**Exit criteria**

- Version matrix and directory map are documented.
- No existing batch behavior regresses.

### Phase 1: OLTP database and deterministic simulator

**Objectives**

- Establish a realistic source system independent of the analytics warehouse.

**Required work**

- Implement OLTP DDL, constraints, indexes, roles, control schema, and bootstrap.
- Implement idempotent seeding from the Olist archive and small CI fixture.
- Implement simulator seed, replay, finite run, continuous run, status, and stop
  interfaces.
- Implement realistic order lifecycle scheduling and rare controlled deletes.
- Add simulator metrics and structured logs.

**Verification**

- Seed is idempotent and FK-valid.
- Same seed/configuration produces identical business decisions and identifiers.
- Transaction rollback leaves no partial order graph.
- Historical seeded records cannot be deleted by destructive simulator scenarios.
- Unit tests cover every lifecycle branch and composite key.

**Exit criteria**

- A finite fixture workload can generate create, update, cancel, deliver, review,
  correction, and delete operations predictably.

### Phase 2: Local Kafka, registry, Connect, and Debezium

**Objectives**

- Produce durable, schema-aware CDC events locally.

**Required work**

- Add Kafka KRaft, Apicurio, and distributed Kafka Connect services.
- Persist Apicurio state in its KafkaSQL journal and enforce global
  `BACKWARD_TRANSITIVE` compatibility explicitly; the image default is not the
  project contract.
- Build a reproducible Connect image/plugin layer containing the pinned Debezium
  connector and Avro converter.
- Create topics explicitly with the defined partitions and policies.
- Configure publication, slot, heartbeat, table include list, and connector.
- Version connector and topic configuration templates without secrets.
- Add readiness, connector-status, and schema compatibility checks.

**Verification**

- Initial snapshot emits one current source record per seeded OLTP row in scope.
- Insert/update/delete sequences preserve keys, before/after images, LSN, and
  transaction metadata.
- Multiple changes in one transaction are ordered.
- Connector restart resumes from offsets without a second initial snapshot.
- Kafka and Apicurio restart retain broker data, schemas, subjects, and registry
  compatibility configuration.
- A compatible schema addition succeeds and an incompatible change fails.
- WAL retention remains bounded during idle heartbeat operation.

**Exit criteria**

- Kafka contains validated Avro CDC for every initial-scope table and all
  Debezium/Connect health checks pass.
- The committed Phase 2 report records snapshot counts, composite-key decoding,
  delete/tombstone behavior, transaction ordering, dependency-restart recovery,
  schema compatibility, and regression-test evidence.

### Phase 3: NiFi to MinIO

**Objectives**

- Land durable, replayable, warehouse-ready CDC objects.

**Required work**

- Add MinIO and NiFi with persistent storage.
- Create the shared parameterized NiFi process group.
- Implement envelope landing, typed normalization, binning, Parquet writing,
  quarantine, DLQ, retry, and backpressure.
- Version the NiFi flow and environment parameter templates.
- Add deterministic object naming and offset-range metadata.
- Add initial Prometheus/Grafana services and scrape NiFi/Kafka/Connect/source
  metrics.

**Verification**

- Every non-tombstone Kafka event appears in both landing and normalized storage.
- Deletes use `before` values and are represented once.
- Duplicate consumption creates no ambiguous object identity.
- NiFi restart preserves queued data and resumes consumption.
- Object-store outage retains accepted FlowFiles in persistent NiFi
  repositories, applies backpressure, and stops further Kafka consumption.
- Invalid records go to quarantine/DLQ while healthy partitions continue.

**Exit criteria**

- Closed normalized files are available within 60 seconds under reference load,
  and component health is visible in Grafana.

### Phase 4: Idempotent warehouse ingest and audit

**Objectives**

- Load normalized CDC into PostgreSQL with durable control state.

**Required work**

- Add local `raw_cdc` and `cdc_audit` bootstrap SQL.
- Implement object discovery, immutable manifests, file claiming, staging load,
  `_event_id` deduplication, offset continuity, reconciliation, and watermarks.
- Implement the scheduled local ingest DAG.
- Implement read-only pipeline metrics from audit state.
- Add manual replay by table/date/object range.

**Verification**

- Repeating the same file and DAG run leaves event counts unchanged.
- Loading files out of order preserves all events and reports contiguous/gapped
  watermarks correctly.
- Failed loads can be retried without manual table cleanup.
- Object row counts, warehouse inserted counts, duplicates, and rejected counts
  reconcile.
- Metrics expose raw-layer freshness and failure state.

**Exit criteria**

- The append-only warehouse event layer is complete, idempotent, reconciled, and
  replayable.

### Phase 5: Realtime dbt models and Airflow DAG separation

**Objectives**

- Produce correct current state, history, facts, and marts within the SLO.

**Required work**

- Implement realtime dbt sources, event staging, current-state, history, and
  changed-key models.
- Reuse shared batch business calculations where semantics are identical.
- Implement incremental realtime dimensions, fact, daily revenue, and monthly
  ARPU.
- Implement Asset-triggered transform and scheduled quality DAGs.
- Implement focused per-micro-batch tests and nightly full tests/Elementary.
- Implement parity reports and reversible `analytics` publication views.

**Verification**

- Multiple updates between transformations produce complete history.
- Hard deletes disappear from current/fact/mart outputs and remain in history.
- Late and out-of-order files cannot overwrite newer source state.
- Only impacted keys/periods are rebuilt.
- Initial snapshot parity with batch passes.
- Existing batch snapshots, facts, marts, and fixture tests still pass.

**Exit criteria**

- p95 commit-to-realtime-mart latency is at most 5 minutes under reference load.
- Realtime marts are safely publishable through `analytics` views.

### Phase 6: Local hardening, logs, alerts, and recovery

**Objectives**

- Turn the functional local pipeline into an operable production-like lab.

**Required work**

- Enable local TLS/authentication and least-privilege service accounts.
- Complete all dashboards and alert rules.
- Add Loki and Alloy structured log collection.
- Add disk, WAL, lag, small-file, freshness, and error-budget monitoring.
- Write and exercise runbooks for service restart, Kafka replay, object replay,
  rebuild from landing, connector resnapshot, schema migration, and secret
  rotation.
- Add failure-injection scenarios to nightly/manual CI.

**Verification**

- Each required alert fires under a controlled fault and resolves afterward.
- Connector downtime grows WAL visibly and recovery clears the condition.
- NiFi outage accumulates Kafka backlog and later drains without loss.
- Warehouse can be rebuilt from immutable object storage.
- Logs can be correlated across simulator, Connect, NiFi, Airflow, and dbt.

**Exit criteria**

- The local stack has tested recovery procedures, actionable alerts, and no
  plaintext committed secrets.

### Phase 7: Independent AWS implementation

**Objectives**

- Reproduce the logical contracts with managed AWS services and production-like
  security while controlling cost.

**Required work**

- Implement the Terraform root and remote state.
- Provision networking, RDS, MSK, MSK Connect, Glue registry, S3, Redshift
  Serverless, MWAA, private NiFi EC2/EBS, Secrets Manager, IAM, CloudWatch,
  Grafana Cloud integration, and AWS Budgets.
- Build and version the MSK Connect custom plugin artifact.
- Deploy the same logical NiFi flow with AWS parameter context.
- Package DAG, Python, and dbt artifacts for MWAA without local filesystem
  assumptions.
- Implement AWS ingest, transform, quality, and backfill DAGs.
- Add ordered startup, stop, teardown, backup, and cost runbooks.

**Verification**

- Terraform fmt, validate, lint, and security checks pass.
- No AWS component requires a local service endpoint.
- IAM policies are least-privilege and no long-lived AWS keys are used.
- AWS initial snapshot, CRUD, replay, schema evolution, parity, and latency tests
  pass.
- Grafana Cloud shows CloudWatch service metrics plus private NiFi/pipeline
  metrics and logs.
- Destroy planning identifies all retained state and expected post-destroy cost.

**Exit criteria**

- The AWS path independently satisfies the same data contract and SLO as local.

### Phase 8: Optional comparative learning extensions

These tasks start only after Phase 7 and are not core release gates:

- Compare Debezium with AWS DMS on one isolated table, documenting delete
  semantics, schema evolution, latency, operational visibility, and cost.
- Instrument simulator, loader, and dbt wrapper with OpenTelemetry and evaluate
  Tempo/Grafana Cloud Traces.
- Evaluate a highly available NiFi deployment on EKS or multiple EC2 nodes.
- Compare Airflow-owned Redshift loading with Redshift COPY JOB.
- Compare the required S3 path with Redshift streaming ingestion for a separate
  low-latency serving experiment.

## 15. Testing Strategy

### 15.1 Pull-request gates

- Python lint, typing, and unit tests.
- SQLFluff and dbt parse/compile.
- dbt unit tests for current, history, delete, and changed-key behavior.
- Airflow import tests for every local and AWS DAG without live external calls.
- Docker Compose configuration validation for all profiles.
- Avro compatibility tests.
- Connector and NiFi flow configuration validation.
- Terraform fmt/validate/lint/security checks after AWS files exist.
- Existing batch fixture integration test.

### 15.2 Local integration suite

The small fixture suite must exercise:

- initial snapshot;
- create, read, update, delete, and tombstone events;
- composite keys;
- multiple updates in one transaction and between dbt runs;
- duplicate Kafka/file/DAG replay;
- out-of-order file arrival;
- connector, NiFi, object storage, and warehouse interruptions;
- poison record and incompatible schema;
- source-to-object-to-raw reconciliation;
- current-state and SCD2 correctness;
- fact/mart corrections and hard-delete propagation;
- batch-versus-realtime parity.

### 15.3 Benchmark and soak tests

- Reference: 5 order lifecycles per second for 30 minutes.
- Burst: 20 order lifecycles per second for 10 minutes.
- Soak: lower sustained rate for at least 4 hours.
- Measure p50, p95, and p99 latency at each stage and end to end.
- Require p95 end-to-end latency no greater than 5 minutes, zero unexplained
  offset gaps, zero lost events, and zero duplicate current keys.
- Record CPU, memory, disk, WAL, Kafka lag, NiFi queue, object count, warehouse
  duration, and dbt duration to support threshold tuning.

### 15.4 AWS validation

AWS end-to-end tests are manual or scheduled against an explicitly provisioned
ephemeral environment, not required for every pull request. The test report must
record resource configuration, runtime, estimated cost, data counts, latency,
and cleanup result.

## 16. Recovery and Operational Procedures

Runbooks must cover these scenarios:

- **Kafka Connect restart:** retain the existing slot and offsets; verify no new
  snapshot and confirm WAL decreases after recovery.
- **Registry outage during production:** `errors.tolerance=none` is intentional.
  If converter retries are exhausted, restore registry health, inspect connector
  and task status, and explicitly restart failed tasks without deleting Connect
  offsets, the publication, or the PostgreSQL slot. Verify that no new snapshot
  occurs.
- **NiFi restart:** preserve repositories, resume the consumer group, and verify
  no missing offset ranges.
- **Kafka backlog:** keep NiFi stopped, generate data, restart it, and observe lag
  drain within retention.
- **Object replay:** reset only file-ledger state selected by the operator; rely
  on `_event_id` deduplication.
- **Warehouse rebuild:** recreate realtime schemas from immutable normalized
  objects; if necessary regenerate normalized objects from landing Avro.
- **Controlled resnapshot:** pause simulator writes, record watermarks, stop the
  connector, create a new explicitly named slot/topic prefix, snapshot into a
  new isolated load boundary, validate, and switch only after reconciliation.
- **Breaking schema migration:** introduce a new schema version and warehouse
  columns through an explicit expand/backfill/contract sequence.
- **Secret rotation:** update the secret provider, restart or reload only affected
  clients, and verify without logging values.
- **AWS teardown:** stop generators first, drain NiFi, complete warehouse loads,
  retain only explicitly requested backups, then destroy in dependency order.

## 17. Risks and Mitigations

| Risk                                             | Mitigation                                                                             |
| ------------------------------------------------ | -------------------------------------------------------------------------------------- |
| WAL fills source storage while connector is down | Heartbeats, retained-WAL metrics, alerts, connector runbook                            |
| Small files degrade warehouse load               | 60-second bounded binning, size metrics, manifest batching, separate compaction prefix |
| Duplicate or replayed delivery                   | Immutable event ID, file ledger, manifests, warehouse dedupe                           |
| Late object arrival produces stale current state | Order by LSN/transaction/offset, never ingestion time                                  |
| Deletes disappear downstream                     | Preserve before image, explicit delete model tests, SCD2 deleted state                 |
| Batch and CDC duplicate one another              | Separate schemas and parity comparison; never union copies                             |
| NiFi EC2 fails                                   | Kafka retention, persistent EBS, restart automation, backups, replay                   |
| Schema evolution breaks NiFi or warehouse        | Registry compatibility, CI checks, schema-aware binning, quarantine                    |
| AWS lab cost grows while idle                    | Provisioned lab sizing, usage limits, budgets, stop/teardown runbooks                  |
| MWAA runtime diverges from local                 | Shared Airflow/Python baseline and dual DAG import checks                              |
| Metrics create high cardinality                  | Strict label policy; correlation IDs stay in logs/audit rows                           |

## 18. Expected Repository Organization

Agents may refine names only when required by existing conventions, but the
separation of responsibilities must remain clear:

- `docs/plans/`: approved implementation plans and ADR-containing specifications;
- `docs/cdc/phases/`: implementation records and verification evidence for each
  completed CDC phase;
- `docs/cdc/handoffs/`: bounded instructions and verified upstream contracts for
  the next CDC phase;
- `docs/runbooks/`: new CDC operations, recovery, AWS startup/teardown, and cost;
  existing root-level runbooks do not need to move as part of this work;
- `infra/oltp/`: shared OLTP schema and bootstrap assets;
- `infra/postgres/`: local warehouse CDC bootstrap additions;
- `infra/redshift/`: Redshift CDC bootstrap additions;
- `infra/aws/realtime/`: independent Terraform root;
- `streaming/kafka/`: topic and local broker configuration;
- `streaming/connect/`: connector templates and plugin build assets;
- `streaming/nifi/`: versioned flow and parameter-context templates;
- `observability/`: Prometheus, Grafana, Alertmanager, Alloy, and Loki assets;
- `scripts/simulation/`: deterministic OLTP workload simulator;
- `scripts/cdc/`: shared object-manifest, loading, reconciliation, and metrics logic;
- `dbt/olist_analytics/models/realtime/`: realtime dbt sources and models;
- `airflow/dags/`: thin DAG definitions backed by shared orchestration modules.

Do not place generated secrets, Kafka data, NiFi repositories, MinIO objects,
Terraform state, rendered reports, or simulator runtime state under version
control.

## 19. Agent Execution Rules

1. Read this entire document and the existing architecture, source contract,
   data model, CI guide, and relevant runbook before starting a phase.
2. Implement only one phase or one explicitly bounded slice at a time.
3. Preserve unrelated user changes and existing batch behavior.
4. Do not silently change an accepted ADR. Add an amendment with context,
   decision, consequences, and migration impact.
5. Add tests and documentation in the same change as the behavior they cover.
6. Run the phase verification commands and record results in the handoff.
7. Do not start the next phase while an exit criterion is unmet.
8. Do not claim exactly-once delivery, production HA, or a 5-minute SLO without
   the defined evidence.
9. Never expose secret values in code, configuration examples, logs, test output,
   Terraform state outputs, or documentation.
10. When local and AWS adapters differ, preserve the shared logical event,
    audit, dbt, and Airflow contracts.

## 20. Authoritative References

- Debezium PostgreSQL connector:
  <https://debezium.io/documentation/reference/stable/connectors/postgresql.html>
- Debezium Avro serialization:
  <https://debezium.io/documentation/reference/stable/configuration/avro.html>
- Apache Kafka Connect:
  <https://kafka.apache.org/documentation/#connect>
- Apache NiFi user guide:
  <https://nifi.apache.org/nifi-docs/user-guide.html>
- Apache NiFi REST API:
  <https://nifi.apache.org/nifi-docs/rest-api.html>
- Airflow Asset scheduling:
  <https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/asset-scheduling.html>
- dbt incremental models:
  <https://docs.getdbt.com/docs/build/incremental-models>
- dbt microbatch strategy:
  <https://docs.getdbt.com/docs/build/incremental-microbatch>
- Amazon MSK Connect:
  <https://docs.aws.amazon.com/msk/latest/developerguide/msk-connect.html>
- AWS Glue Schema Registry:
  <https://docs.aws.amazon.com/glue/latest/dg/schema-registry.html>
- Amazon MWAA supported versions:
  <https://docs.aws.amazon.com/mwaa/latest/userguide/airflow-versions.html>
- Grafana Cloud AWS observability:
  <https://grafana.com/docs/grafana-cloud/monitor-infrastructure/monitor-cloud-provider/aws/>
- Grafana Alloy:
  <https://grafana.com/docs/alloy/latest/introduction/>
