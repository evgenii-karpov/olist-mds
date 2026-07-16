# Handoff: Stage 3 — NiFi to MinIO

## Mission

Implement Phase 3 from `docs/plans/near-realtime-cdc-implementation-plan.md`.
Land every non-tombstone CDC event as immutable Avro and normalized Parquet in
MinIO, with deterministic offset-range identity, quarantine/DLQ behavior,
backpressure, restart safety, and the first Prometheus/Grafana baseline. Do not
add warehouse ingest, realtime dbt models, CDC Airflow DAGs, or AWS resources.

Read the approved plan, `docs/cdc/phases/phase-2-kafka-debezium.md`, this handoff,
the topic manifest, connector template, and the Stage 2 decoder before editing.

## Upstream endpoints and wire contract

| Capability | Stage 2 value |
| --- | --- |
| Kafka bootstrap in Compose | `kafka:29092` |
| Kafka bootstrap from host | `localhost:9092` |
| Registry native API | `http://apicurio-registry:8080/apis/registry/v3` |
| Registry ccompat API | `http://apicurio-registry:8080/apis/ccompat/v7` |
| Host ccompat API | `http://localhost:8081/apis/ccompat/v7` |
| Compatibility | global `BACKWARD_TRANSITIVE` |
| Connector | `olist-postgres-cdc` |
| Consumer-facing heartbeat | `olist_cdc.heartbeat` |
| Transaction metadata | `olist_cdc.transaction` |

Kafka values and keys are Confluent-framed Avro: byte `0`, four-byte big-endian
numeric content ID, then Avro bytes. Resolve that ID through ccompat
`/schemas/ids/<id>` and recursively resolve its `references`. Do not treat the
payload as JSON. Main subjects are `<topic>-key` and `<topic>-value`; referenced
table Value, Source, and transaction record subjects are normal Apicurio state.
Do not persist registry IDs as logical versions.

The canonical topic list, partitions, cleanup policy, and retention live in
`streaming/kafka/topics.json`. Source topics are:

- one partition: customers, products, sellers, category translation;
- three partitions: orders, items, payments, reviews.

Every source table has a reserved `olist_cdc.dlq.<table>` topic with matching
partition count and seven-day delete retention. Stage 2 produces nothing to
those DLQs; Stage 3 owns the first producer and must document whether the
original key/value bytes or a versioned error envelope is written.

## Event semantics NiFi can rely on

- Source primary-key Avro is preserved for all keys, including items
  `(order_id, order_item_id)`, payments `(order_id, payment_sequential)`, and
  reviews `(review_id, order_id)`.
- `c`, `u`, `d`, and snapshot `r` records have Debezium before/after envelopes.
  A hard delete is one `op=d` business event followed by a null tombstone.
  Tombstones must not become a second normalized delete.
- The immutable downstream ID remains `<topic>:<partition>:<offset>`.
- Current ordering is source LSN, source transaction/order, then Kafka offset.
  Do not use NiFi receipt time. For PostgreSQL, `source.txId` is the shared
  transaction identity; Debezium 3.6 envelope transaction IDs contain an
  event-specific LSN.
- Heartbeats are routed only to `olist_cdc.heartbeat`. The RegexRouter predicate
  does not alter source topics. Transaction boundary records use
  `olist_cdc.transaction`.
- Geolocation and all `simulator_control` tables are excluded.

## Recovery evidence and required consumer behavior

The initial fixture snapshot reconciled exactly. Connect downtime retained WAL,
then resumed from stored offsets and delivered the committed change without a
second snapshot. Kafka and Apicurio volumes retained old messages, schemas,
subjects, and the compatibility rule across restarts. When Apicurio is
deliberately unavailable long enough to exhaust converter retries, the strict
connector task fails visibly; after registry recovery,
`python scripts/cdc/stage2_admin.py restart-failed` resumes it without deleting
offsets or the PostgreSQL slot.

NiFi must use its own stable consumer group and preserve topic/partition/offset
plus key/value schema IDs. In stock NiFi 2.10, `ConsumeKafka` commits after
durable FlowFile repository acceptance, not after an arbitrary downstream S3
branch. A MinIO outage must therefore retain accepted FlowFiles in persistent
repositories and apply backpressure until further Kafka consumption stops.
Replay and duplicate delivery must remain safe through immutable event/object
identity. NiFi restart must preserve repositories and resume the same group.

## Phase 3 acceptance boundary

Add MinIO and NiFi only to `realtime-core`, with persistent volumes and
versioned parameter/flow templates. Implement raw Avro landing, typed
normalization, Parquet binning closed within 60 seconds, deterministic object
names and manifests, quarantine/DLQ, retries, and backpressure. Add the first
Prometheus/Grafana services and expose Kafka/Connect/source/NiFi health.

Verify every non-tombstone appears once in each logical landing/normalized
contract, deletes use `before`, duplicates have unambiguous object identity,
invalid records do not stop healthy partitions, and restart/outage scenarios
preserve data. Stop before warehouse schemas or Airflow CDC orchestration.
