# CDC Ordering and Serving-Boundary Contract

## 1. Event categories

The implementation must classify each record as one of:

1. snapshot event;
2. live non-transactional CDC event;
3. live transactional CDC event.

Required fields differ by category; optionality is explicit rather than inferred through fallback sorting.

## 2. Canonical source-version tuple

Ascending logical order:

```text
is_non_snapshot
source_binlog_file_index
source_binlog_pos
source_row
transaction_total_order
transaction_data_collection_order
source_ts
kafka_partition
kafka_offset
event_id
```

The implementation must define null placement by category and reuse one generated/helper representation in Spark, ClickHouse, BigQuery, and parity code.

### Snapshot requirements

- snapshot marker/category;
- Kafka topic, partition, offset;
- deterministic event ID;
- source table/key information.

Binlog and transaction fields may be null.

### Live non-transactional requirements

- validated binlog filename/index;
- binlog position and row;
- Kafka topic, partition, offset;
- event ID.

Transaction-order fields are null by contract.

### Live transactional requirements

All live coordinates plus:

- transaction identifier;
- transaction total order;
- transaction data-collection order;
- complete transaction metadata linkage.

## 3. Fail-closed behavior

The following are blocking data-quality failures:

- malformed or missing binlog filename/index for live CDC;
- missing mandatory binlog position/row;
- missing required transaction-order fields for transactional events;
- incomplete Debezium transaction metadata;
- conflicting duplicate source coordinates;
- non-deterministic tie after all tuple fields.

The event is retained in audit/quarantine evidence, the affected Silver/current update is not accepted, and serving publication is blocked. Timestamp-only or idle-time fallback is forbidden.

## 4. Timestamp contract

Source fields without embedded zone information are interpreted in `SOURCE_TIME_ZONE` (default `America/Sao_Paulo`) and converted to UTC instants before storage. Event/source timestamps are observability/tie-break fields only after stronger source coordinates; they are not the primary version order.

## 5. Transaction-complete boundary

A serving planner:

1. reads Debezium transaction metadata and per-topic/partition progress;
2. identifies the last fully completed source transaction visible across all relevant entity topics;
3. freezes target offsets per topic-partition at a prefix that does not split that transaction;
4. records transaction identity/evidence and the predecessor active run;
5. waits until `audit.silver_progress` proves every source table has processed the frozen offsets;
6. creates a serving run only after the proof succeeds.

If transaction metadata is unavailable or incomplete, the planner fails closed. It must not fall back to current Kafka end offsets or an arbitrary idle pause.

## 6. Source consistency during dbt

Every BigQuery model reads immutable `silver.*_changes` through bridge views and filters by the run's frozen offsets. The model does not depend on mutable `*_current` tables for historical reconstruction.

Before build:

- all progress rows are at or beyond the boundary;
- boundary and predecessor state are immutable for the run;
- the exact changed interval `(previous_boundary, current_boundary]` is persisted.

After build:

- source-progress evidence is revalidated;
- candidate/history counts and checksums are recorded;
- an incompatible progress or schema change fails the run and permits a same-sequence rebuild from the same boundary.

## 7. Run identity and retry

`sync_run_seq` is the stable identity of one frozen source interval. A retry of an unpublished run does not allocate a new sequence. It deletes all per-model candidate/history rows for that sequence, resets model results, and rebuilds from the same boundary.
