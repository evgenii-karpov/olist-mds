# Detailed Stage E implementation plan: Serving Integration

- **Document status**: Completed / Frozen
- **Execution commit**: `e113c552cca990636f426b827456a77ddc9d594b`.
- **Acceptance evidence**: clean Stage V run `stage_v_clean_e113c55`; Stage E report `PASS`.
- **Stage**: E — Serving Integration
- **Decision date**: 2026-08-01
- **Preceding stages**: Wave 1 / J1 and Wave 2 / J2
- **Next stage**: F0 after accepted E/V revalidation
- **Purpose**: give the implementer a fully specified sequence for transaction-complete Iceberg → ClickHouse → dbt Gold publication, maintenance, recovery, and observability.

> **Final implementation note.** The original design sections below describe
> scheduled-DAG activation as a candidate approach. The accepted implementation
> uses manual-only serving, quality, maintenance and rebuild DAGs with
> `schedule=None` and `is_paused_upon_creation=False`; validation triggers the
> required DAGs explicitly and never races the scheduler.
- **Authority order**: normative contracts in `docs/plans/lakehouse/contracts/` → this implementation plan → validation report → runbooks.

---

## 1. Final decision

Stage E must turn the existing ClickHouse and `dbt/olist_clickhouse` scaffolding into a final, repeatable, and recoverable serving path:

```text
Iceberg Silver + audit
        ↓ frozen transaction-complete plan
Airflow finite serving run
        ↓
ClickHouse unpublished candidate partitions
        ↓
dbt Gold candidate + tests
        ↓ PUBLISHED marker — the only publication point
stable serving_cdc / gold views
```

The implementation must satisfy these invariants:

1. ClickHouse and Airflow are not in the CDC durability path. Iceberg tables remain canonical.
2. Serving views never expose only part of an original MySQL transaction.
3. `OPEN` and `REJECTED` transactions are not published, and later transactions do not cross such a boundary.
4. Every candidate remains completely invisible until one `PUBLISHED` marker is inserted.
5. A retry after failure before the marker reuses the same `sync_run_seq` and safely rebuilds only its partitions.
6. A retry after the marker does not rematerialize data; it finalizes control/audit metadata.
7. A lost ClickHouse instance is fully restored from Iceberg with `rebuild-serving --yes`.
8. Iceberg maintenance has no access to the Spark checkpoint bucket.
9. The legacy path is not removed or repurposed until Stage L after F0.

### 1.1 Recorded product decisions

| Decision | Recorded behavior |
| --- | --- |
| PostgreSQL control state | Narrow ledger in the new `olist_control.serving` schema; no separate PostgreSQL instance is created |
| Transaction policy | Strict barrier: do not cross `OPEN`/`REJECTED` |
| Serving cadence | Serving, quality, and maintenance DAGs are launched manually; scheduler cadence is not used |
| Schedule activation | Not used: serving DAGs are manually triggered and created unpaused |
| Rebuild | Manual only, with a double guard: CLI `--yes` and DAG conf `confirm_destructive=true` |
| Timezone | UTC for all timestamps, DAG schedules, reports, and comparisons |
| ClickHouse publication | Marker-based; experimental multi-table transactions are not used |
| Gold retention | Retain the current and previous published Gold run; do not delete CDC event history |

### 1.2 Why `olist_control.serving` is required and where its scope ends

The control schema is not for copying data; it coordinates operations that touch several independent systems without a shared transaction:

- allocate a monotonic `sync_run_seq`;
- survive Airflow task/DagRun retries;
- freeze the transaction boundary, Kafka offsets, and Iceberg snapshot IDs once;
- distinguish an unpublished candidate from a published but not yet finalized run;
- serialize sync, rebuild, and maintenance;
- restore the control cursor after a failure between the ClickHouse marker and report write.

PostgreSQL must not store:

- business rows;
- CDC or Avro payloads, or before/after images;
- copies of ClickHouse event/current/gold tables;
- raw credentials or error text that could contain a payload/secret.

Airflow XCom is used only for short IDs and branch results. It is cleared on task retry and is not a durable ledger: [Airflow 3.2 XCom](https://airflow.apache.org/docs/apache-airflow/3.2.1/core-concepts/xcoms.html).

The ClickHouse marker is used instead of a multi-table transaction because full ClickHouse transactions are experimental, require Keeper/ZooKeeper, and do not fit the current local topology: [ClickHouse transactions](https://clickhouse.com/docs/concepts/features/operations/insert/transactions).

### 1.3 In Stage E scope

- Required restoration of the missing J2 audit/progress mechanisms without which a strict boundary is impossible.
- PostgreSQL serving ledger and reconciliation.
- Full implementation of the finite Airflow DAG for serving sync.
- Integration of the existing ClickHouse tables/views.
- Isolation of unpublished current candidates.
- Integration of the existing `dbt/olist_clickhouse` project into the publication flow.
- Quality, Iceberg maintenance, and ClickHouse rebuild DAGs.
- `sync-serving`, `rebuild-serving`, and `run-maintenance` CLIs, plus serving status/validate.
- Stage E metrics, alerts, dashboard, and runbooks.
- Static/component/clean-domain validation and the Stage E report.

### 1.4 Out of Stage E scope

- Removal of PostgreSQL/NiFi/old DAG/dbt components — Stage L after Stage V only.
- The full 14-step CRUD/restart/schema-evolution scenario — Stage V.
- Final candidate comparison with the historical baseline — Stage F.
- Version upgrades for PostgreSQL, Airflow, Spark, Iceberg, ClickHouse, or dbt.
- New Gold business logic or changes to the public grain of the eight existing models.
- A new distributed transaction layer, Keeper, or ZooKeeper.

---

## 2. Actual starting point and required contract repairs

### 2.1 What already exists

- `platform-postgres` already contains a separate `olist_control` database/role.
- `olist_control` already creates the legacy `audit` and `cdc_audit` schemas.
- `scripts/orchestration/control_postgres.py` already provides a file-secret connection helper.
- ClickHouse DDL already creates `serving_cdc`, `serving_control`, `gold_store`, and `gold`.
- Eight `<entity>_events`, eight `<entity>_current_versions`, and eight `<entity>_current` views already exist.
- `serving_control.published_runs` and `published_runs_current` already exist.
- `dbt/olist_clickhouse` already contains eight physical Gold models, candidate vars, tests, and stable public views.
- Polaris already creates `spark_writer`, `clickhouse_reader`, and `airflow_maintenance`; the latter has table read/write access for maintenance.
- Airflow and ClickHouse are already in the `serving` Compose profile.

### 2.2 Gaps the implementation must close

1. `SilverBatchWriter` does not materialize the full Silver changes/current contract and does not write `audit.silver_progress`.
2. `audit.mysql_transactions` is not produced by a separate transaction query.
3. Bronze/Silver status publishes empty `partition_offsets`.
4. `wait-caught-up` reports READY without comparing against captured Kafka targets.
5. The Stage E CLI currently returns `not_available_until`.
6. `status` has no correct `streaming` selection and does not perform serving semantic checks.
7. The Airflow image copies only `dbt/olist_analytics`, and `DBT_PROFILES_DIR` points to the legacy project.
8. The Airflow image lacks the Spark client/provider for finite maintenance jobs.
9. Stage E DAGs are missing.
10. Observability configs refer to missing or legacy exporters.
11. CI primarily checks the legacy path and has no bounded serving component gate.
12. `current_versions` uses `PARTITION BY tuple()` and `ORDER BY business PK`; merging an unpublished candidate can displace the published version for the same PK.

### 2.3 Required normative-document updates

Before implementing behavior, update the contracts so the code does not diverge from the more authoritative text:

- In `serving-and-recovery.md`, record the actual names `<entity>_events`, `<entity>_current_versions`, and `<entity>_current`.
- For current tables, record `ReplacingMergeTree(kafka_offset)`, `PARTITION BY sync_run_seq`, and `ORDER BY (sync_run_seq, business PK)`.
- In `architecture-and-runtime.md`, record `rebuild-serving --yes`, `status --require streaming|serving`, and manual-only serving DAGs.
- In `validation-and-ci.md`, add a Stage E component gate without mixing it with full Stage V E2E.
- In `serving-cutover.md`, replace the abstract “control database implementation” with a reference to the narrow schema described here.

---

## 3. E0 — required J2 contract repair

Stage E must not calculate the transaction boundary until this block passes. If E0 fails, serving implementation stops; fallback to `silver.current`, wall-clock timestamps, or unverified status files is forbidden.

### 3.1 Target Silver runtime

One `spark-silver` application must run ten named streaming queries:

1. `bronze_to_silver_customers`
2. `bronze_to_silver_orders`
3. `bronze_to_silver_order_items`
4. `bronze_to_silver_order_payments`
5. `bronze_to_silver_order_reviews`
6. `bronze_to_silver_products`
7. `bronze_to_silver_sellers`
8. `bronze_to_silver_product_category_translation`
9. `capture_avro_schemas`
10. `normalize_mysql_transactions`

All queries use stable names and separate checkpoint paths with a contract version. Changing a query name or checkpoint path is an incompatible migration and requires a full disposable reset.

### 3.2 Entity normalization

Implement a shared `EntityBatchProcessor` for every entity query:

1. Filter exactly one business topic according to the contract manifest.
2. Check/deduplicate `event_id`; conflicting metadata for one ID is fatal `event_identity_collision`.
3. Separate tombstones. A tombstone creates no changes/current row, but its offset must enter progress.
4. Obtain key/value schema metadata only from `bronze.avro_schemas`; direct registry access from an entity query is forbidden.
5. Check writer fingerprints against the v2 contract.
6. Perform bounded Avro pre-validation, then FAILFAST decode.
7. Check the envelope, op, entity/topic, PK, exact types/nullability, and entity rules.
8. Build the complete `<entity>_changes` row, including:
   - `event_id`, `op`, `is_snapshot`, `is_deleted`;
   - `apply_status`, fixed `error_code/error_message`;
   - nullable business columns;
   - source/binlog/GTID metadata;
   - transaction ID and order values;
   - Kafka topic/partition/offset/timestamp;
   - schema IDs/fingerprint/contract version;
   - before/after/row hashes;
   - Bronze/normalization timestamps.
9. Separate applied/rejected rows without leaking payload into logs/audit.
10. Execute the commit protocol in the next section.

A permanent validation error writes a rejected changes row and allows checkpoint advancement. An unexpected exception is always fatal and does not become a permanent record.

### 3.3 Idempotent commit protocol

The commit order is immutable:

```text
changes → normalization_errors/schema_violations → current → silver_progress
```

Requirements:

- Changes MERGE key — `event_id` only.
- Exact retry — no-op; the original `normalized_at` is preserved.
- An applied row must not be overwritten with different immutable provenance fields.
- An allowed finite replay correction changes only rejected → applied mutable fields.
- Current is updated only by an applied row with a newer offset in the same Kafka partition.
- Equal offset + same event ID — no-op; equal offset + different event ID — fatal.
- A delete envelope creates a soft-delete current row; a following tombstone does not change current.
- `silver_progress` is written last and only after the changes/current commits actually complete.
- Progress MERGE key:

```text
query_name, entity, contract_version, source_topic,
kafka_partition, spark_batch_id
```

- `changes_snapshot_id` is read after the changes commit.
- `current_snapshot_id` contains the new snapshot ID or NULL when current did not change.
- `last_kafka_offset` includes the tombstone offset.
- Status: `COMMITTED` or `COMMITTED_WITH_REJECTIONS`.

Shared audit tables are protected by a driver-local fair lock per fully qualified table. The lock is not held during registry I/O/decode, and no more than one table lock is held at a time.

### 3.4 Transaction metadata query

`normalize_mysql_transactions` processes only `olist_cdc.transaction`:

- the actual writer schema is archived and checked against the structural reader contract;
- BEGIN creates/confirms an immutable `OPEN` row;
- logical duplicate BEGIN/END records collapse;
- conflicting BEGIN/END is fatal `transaction_metadata_conflict`;
- END offset must be greater than BEGIN offset;
- the transaction topic has one partition, but DataFrame row order is not considered preserved.

END may enter a final status only after five checks:

1. `event_count` equals the distinct Silver changes rows with this `transaction_id`.
2. Counts for every declared `data_collection` match; the collection name maps exactly to one of the eight entities.
3. `transaction_total_order` forms `1..event_count`; per-collection order is also continuous.
4. The latest committed `silver_progress` for involved partitions covers the maximum offset of the transaction rows.
5. Every event has exactly one effective outcome: applied or rejected.

If rows/progress are not ready, return transient `transaction_not_ready` and do not advance the checkpoint. Extra rows, gaps, unknown collections, or conflicting END are fatal contract errors.

Final status:

- `COMPLETE` when all rows are applied;
- `REJECTED` when at least one row is rejected;
- `rejected_event_ids` are sorted lexicographically;
- the only permitted replay transition is `REJECTED → COMPLETE`;
- `COMPLETE` never regresses;
- snapshot rows with `transaction_id=NULL` do not create a synthetic transaction.

After the transaction commit, write progress with `entity='__transactions__'`, where `changes_snapshot_id` is the `audit.mysql_transactions` snapshot and `current_snapshot_id=NULL`.

### 3.5 Actual status and caught-up barrier

Bronze and Silver status JSON must contain:

- application name and contract version;
- stable query names/IDs;
- state and last batch ID;
- last progress timestamp;
- the actual `topic:partition → last processed offset` map;
- fixed error class/code without a payload;
- atomic file replacement.

`wait-caught-up --timeout`:

1. Use `confluent-kafka` once to record the high watermark for every partition of the 11 external topics.
2. The target is `high - 1`, or `-1` for an empty partition.
3. Do not recalculate targets during polling.
4. Wait for Bronze coverage of all targets.
5. Wait for `__schemas__` progress for all external partitions.
6. Wait for entity progress on business partitions.
7. Wait for `__transactions__` progress on the transaction topic and no OPEN transaction in the target range.
8. Write target JSON to a non-secret temporary file.
9. Start finite `LakehouseStatusMain`.
10. Return one sanitized JSON result.

The finite validator checks the actual Iceberg state:

- progress offset coverage;
- snapshot IDs exist and can be read;
- duplicate `event_id=0`;
- current PK uniqueness;
- changes outcome counts;
- schema archive coverage;
- transaction state/count/order invariants;
- rejected rows/transactions inside the captured target as a separate boundary signal.

The result must separate two dimensions:

- `coverage_state=READY|NOT_CAUGHT_UP`: all captured offsets and snapshot IDs are actually covered;
- `boundary_state=READY|OPEN|REJECTED|INVARIANT_VIOLATION`: whether the entire captured range can be published.

The `wait-caught-up` CLI returns overall `READY` only when `coverage_state=READY` and `boundary_state=READY`. For a covered but rejected/open range it returns code 2 and JSON with `coverage_state=READY` and the corresponding boundary state. The serving planner uses the structured result: it requires `coverage_state=READY`, then selects the COMPLETE prefix up to OPEN/REJECTED. For the initial snapshot, any rejection remains an unconditional `SNAPSHOT_REJECTED` blocker.

Exit codes:

| Code | Meaning |
| --- | --- |
| `0` | `READY` |
| `2` | `NOT_CAUGHT_UP` or transient `BLOCKED` |
| `3` | `INVARIANT_VIOLATION` |
| `1` | `EXECUTION_ERROR` |

### 3.6 E0 stop/go acceptance

E0 is complete only when automated evidence shows:

- initial snapshot is covered by non-empty offsets and snapshot IDs;
- a multi-table transaction becomes COMPLETE only after all entity progress is present;
- a rejected event moves the transaction to REJECTED;
- finite replay moves it to COMPLETE without duplicate event/current/error rows;
- the rejected test returns `coverage_state=READY`, `boundary_state=REJECTED`, rather than masking it as transport lag;
- a simultaneous Bronze/Silver restart recovers from checkpoints;
- `wait-caught-up` does not return READY before target coverage;
- status JSON contains no business values or credentials.

---

## 4. PostgreSQL serving ledger

### 4.1 Migration and privileges

Add the following idempotent migration after the existing `infra/control-postgres/initdb/00x_*` migrations and update the grants migration:

- the bootstrap/admin role owns the schema and objects;
- runtime role `olist_control` receives `USAGE` on the schema;
- runtime receives `SELECT, INSERT, UPDATE, DELETE` on the three tables;
- runtime receives `USAGE, SELECT` on the sequence;
- runtime does not receive `CREATE` on the `serving` schema;
- legacy schemas/grants are not changed before Stage L.

The migration must run both on a new volume and when `platform-postgres-bootstrap` is rerun against an existing volume.

### 4.2 Exact logical schema

#### `serving.sync_run_seq`

```sql
CREATE SEQUENCE serving.sync_run_seq AS bigint START WITH 1 INCREMENT BY 1;
```

The sequence may have gaps after rollback/no-op. The only requirements are monotonicity and never reusing a number.

#### `serving.sync_runs`

| Column | Type / constraint | Purpose |
| --- | --- | --- |
| `sync_run_seq` | `bigint PK default nextval(...)` | Publication/candidate sequence |
| `sync_run_id` | generated unique text | `sync-` + 20-digit seq |
| `operation_type` | `SYNC|REBUILD` | Logical run type |
| `status` | fixed CHECK set | State machine |
| `status_reason` | nullable fixed text | Exactly one of `NONE`, `NO_NEW_TRANSACTION`, `SOURCE_NOT_CAUGHT_UP`, `OPEN_TRANSACTION`, `OPEN_TRANSACTION_STALE`, `REJECTED_TRANSACTION`, `SNAPSHOT_REJECTED`, `ACTIVE_LEASE`, `MATERIALIZATION_MISMATCH`, `PUBLICATION_DRIFT`, `INVARIANT_FAILURE`, `EXECUTION_FAILURE` |
| `current_airflow_dag_run_id` | nullable text | Latest DagRun executing the logical run |
| `attempt_count` | integer >= 0 | Number of run acquisitions |
| `is_noop` | boolean | No ClickHouse candidate/marker |
| `previous_transaction_id` | nullable text | Previous published boundary |
| `previous_transaction_end_offset` | nullable bigint | Position in the transaction topic |
| `target_transaction_id` | nullable text | Last transaction in the candidate prefix |
| `target_transaction_end_offset` | nullable bigint | Frozen target position |
| `source_snapshot_completed` | boolean | Initial snapshot gate |
| `target_offsets_json` | JSON object | Frozen business/transaction offsets |
| `iceberg_snapshot_ids_json` | JSON object | Frozen per-table snapshot IDs |
| `expected_event_count` | bigint >= 0 | Plan |
| `materialized_event_count` | bigint >= 0 | Actual |
| `expected_entity_counts_json` | JSON object | Plan by entity |
| `materialized_entity_counts_json` | JSON object | Actual by entity |
| `report_json` | JSON object | Sanitized immutable publication report |
| `error_details_json` | JSON object | Sanitized error class/code/context |
| `started_at` | timestamptz | Logical run start |
| `updated_at` | timestamptz | Last state transition |
| `published_at` | nullable timestamptz | Deterministic marker timestamp |
| `completed_at` | nullable timestamptz | Terminal state |

Add `jsonb_typeof(value)='object'` checks to all JSON columns. Business payloads and unbounded exception strings are forbidden.

`report_json` is serialized canonically: UTF-8, recursively sorted keys, `,`/`:` separators without spaces, UTC ISO-8601 timestamps with microseconds, and decimals as fixed-scale strings. `report_sha256` is the lowercase SHA-256 of these bytes and is stored inside the report; the `report_sha256` field is temporarily excluded while computing the hash. The same logical report must produce identical bytes/hash in Python, the ClickHouse marker, and Iceberg audit.

#### `serving.sync_entity_results`

| Column | Type / constraint |
| --- | --- |
| `sync_run_seq` | FK → `sync_runs`, part of PK |
| `entity` | one of eight entities, part of PK |
| `status` | `PLANNED|MATERIALIZED|VALIDATED|FAILED` |
| `expected_event_count` | bigint >= 0 |
| `materialized_event_count` | bigint >= 0 |
| `affected_key_count` | bigint >= 0 |
| `candidate_current_count` | bigint >= 0 |
| `event_checksum` | nullable lowercase SHA-256 |
| `error_code` | nullable fixed code |
| `updated_at` | timestamptz |

`event_checksum` is computed identically by the planner and materializer: build the UTF-8 string `event_id|row_hash-or-<null>|transaction_id-or-<snapshot>` for every selected row, sort the strings bytewise by `event_id`, join with `\n` without a trailing newline, and take the lowercase SHA-256. Business values are not included in the checksum input.

#### `serving.runtime_state`

Singleton row with `singleton_key=1`:

| Column | Purpose |
| --- | --- |
| `last_published_sync_run_seq` | Last reconciled PUBLISHED marker |
| `last_published_transaction_id/end_offset` | Serving transaction cursor |
| `last_published_target_offsets_json` | Published business offsets |
| `source_snapshot_completed` | Snapshot has already been published |
| `lease_owner_id` | Logical operation ID |
| `lease_owner_sync_run_seq` | Nullable seq for sync/rebuild |
| `lease_operation` | `SYNC|REBUILD|MAINTENANCE` |
| `lease_acquired_at/heartbeat_at/expires_at` | Durable lease lifecycle |
| `schedules_activated_at` | Not used in the accepted manual-only DAG flow |
| `row_version` | Optimistic update counter |
| `updated_at` | Audit timestamp |

### 4.3 State machine

```text
PLANNING
 ├─→ NOOP
 ├─→ WAITING
 ├─→ BLOCKED
 └─→ MATERIALIZING
       └─→ VALIDATING
             └─→ READY_TO_PUBLISH
                   └─→ PUBLISHED_PENDING_FINALIZATION
                         └─→ SUCCEEDED
```

Any pre-publish state may transition to `FAILED_RETRYABLE` or `FAILED_TERMINAL`.

Rules:

- `FAILED_RETRYABLE`, `MATERIALIZING`, `VALIDATING`, and `READY_TO_PUBLISH` resume with the same seq.
- `PUBLISHED_PENDING_FINALIZATION` never returns to materialization.
- `SUCCEEDED`, `NOOP`, `WAITING`, `BLOCKED`, `FAILED_TERMINAL` — terminal logical run.
- The next scheduled DagRun may create a new seq after a terminal run.
- A state update must specify the permitted previous status in `WHERE`; an update of zero rows means a concurrency/invariant error.
- `published_at` is assigned once before the marker and does not change on retry.

### 4.4 Global operation lease

- The lease serializes sync, rebuild, and maintenance across different DAGs.
- The Airflow pool remains an additional resource constraint, not the authoritative lock.
- Default TTL — 30 minutes.
- Every long-running task updates the heartbeat before and after an external operation.
- When scheduled sync encounters another active lease, it ends `WAITING` rather than occupying a worker until release.
- An expired lease is acquired only after PostgreSQL ↔ ClickHouse reconciliation.
- The quality DAG does not acquire a mutation lease; while any mutation lease is active, it does not read serving databases, marks the run `WAITING`, and ends without a quality alert.

### 4.5 Reconciliation and ledger recovery

Before every sync/rebuild:

1. Read `runtime_state` under a row lock.
2. Read the latest effective row from `serving_control.published_runs_current`.
3. Read the latest successful `audit.serving_sync_reports` through the Iceberg/ClickHouse catalog.
4. Compare seq, run ID, transaction boundary, and report hash.

Matrix:

| PostgreSQL | ClickHouse | Iceberg report | Action |
| --- | --- | --- | --- |
| Matches | Matches | Matches/still pending | Continue; append the report when pending |
| Older | Marker is newer | Marker report is valid | Restore the cursor and append the Iceberg report |
| Newer | Marker missing/older | Any | Fail closed; treat ClickHouse as lost and require rebuild |
| Empty | Marker + report agree | Present | Import the completed summary, `setval(max_seq)`, and restore the cursor |
| Empty | Marker missing | Present | Rebuild only; normal sync is forbidden |
| ID/hash/boundary diverge | Any | Any | Terminal invariant failure; no automatic publication |

After PostgreSQL loss, unpublished ClickHouse partitions whose seq is absent from markers/reports are treated as orphan candidates and removed before a new run.

---

## 5. Frozen transaction-complete serving plan

### 5.1 Preconditions

The planner runs only when:

- Compose profile `platform` is healthy;
- `spark-bronze` and `spark-silver` are active with no FATAL query;
- caught-up helper returned the captured target and `coverage_state=READY`; `boundary_state=OPEN|REJECTED` is allowed as planner input and is handled by the strict barrier;
- ClickHouse DataLakeCatalog reads the required Iceberg tables;
- the PostgreSQL migration/current row exists;
- dbt project parseable;
- no incompatible active lease exists.

Scheduled runs wait for caught-up for no more than 180 seconds. The first manual `sync-serving` passes 1200 seconds. A scheduled-run timeout produces `WAITING/SOURCE_NOT_CAUGHT_UP`, not failure.

### 5.2 Initial snapshot publication

If `runtime_state.source_snapshot_completed=false`:

1. The Debezium connector must be RUNNING and not in snapshot phase.
2. Captured Kafka targets must be covered by Bronze/Silver progress.
3. All eight entity changes snapshots must exist.
4. The captured range must contain no rejected snapshot rows.
5. The candidate includes applied rows with `is_snapshot=true`.
6. A subsequent maximal COMPLETE transaction prefix may also be included if it is already fully covered.
7. `source_snapshot_completed=true` is written only in the PUBLISHED marker/cursor, not during planning.

If a snapshot event is rejected, the run becomes `BLOCKED`; partial initial publication is forbidden.

### 5.3 Transaction-prefix selection

Use the latest effective transaction rows beginning after `previous_transaction_end_offset`:

1. Order by `end_kafka_offset` on the transaction topic.
2. Check position uniqueness and immutable metadata.
3. Proceed sequentially to the first non-publishable transaction.
4. Include `COMPLETE` only after rechecking event/collection/order/progress counts.
5. The first `OPEN` stops the prefix.
6. The first `REJECTED` stops the prefix and moves the run to `BLOCKED`.
7. Later COMPLETE transactions after OPEN/REJECTED are not considered.
8. An OPEN younger than 10 minutes is normal waiting; an older one also raises an alert.
9. If streaming status says caught-up but COMPLETE counts do not match, this is an invariant failure, not waiting.

### 5.4 Frozen per-entity snapshots

For each entity:

- find the latest committed `silver_progress` covering the maximum required Kafka offset;
- store `changes_snapshot_id` under the key `silver.<entity>_changes`;
- do not use a changing current snapshot for materialization;
- query the frozen changes table through ClickHouse `SETTINGS iceberg_snapshot_id=<id>`;
- recalculate selected events and the checksum;
- store the expected count/checksum in PostgreSQL.

The snapshot may contain events after the target boundary; exclude them with an exact transaction ID/offset filter. Using “all snapshot rows” is forbidden.

### 5.5 No-op and blocked semantics

- Snapshot is already published and there are no new COMPLETE transactions: `NOOP`; marker/cursor do not change.
- Next transaction is OPEN: `WAITING`.
- Next transaction is REJECTED: `BLOCKED` with a critical metric/alert.
- Iceberg snapshot/progress temporarily does not cover the selected COMPLETE: `WAITING`, only if Kafka/Silver is not yet caught up.
- Any divergence after caught-up is confirmed: `FAILED_TERMINAL`.

An NOOP/WAITING/BLOCKED run may have an allocated seq; gaps among PUBLISHED seq values are allowed.

### 5.6 Recheck before the marker

After candidate/dbt tests and immediately before publication:

- reread the latest effective status of all selected transactions;
- verify that none became REJECTED;
- repeat the expected/materialized count comparison;
- verify that the candidate seq was not published by another attempt;
- verify that the previous marker/cursor did not change;
- update `READY_TO_PUBLISH → PUBLISHED_PENDING_FINALIZATION` only after the marker is inserted successfully.

---

## 6. ClickHouse serving materialization

### 6.1 Fix current-table isolation

Change the DDL for all eight `<entity>_current_versions` tables to:

```sql
ENGINE = ReplacingMergeTree(kafka_offset)
PARTITION BY sync_run_seq
ORDER BY (sync_run_seq, <business primary key>)
```

Composite keys remain in contract order. Recreate the existing pre-Stage-E disposable domain; no online ALTER/migration of old local data is required.

Required learning regression:

1. Insert published seq 1 for a PK.
2. Insert unpublished seq 2 for the same PK.
3. Run `OPTIMIZE TABLE ... FINAL`.
4. The stable view must still return seq 1.
5. Insert the PUBLISHED marker for seq 2.
6. The stable view must return seq 2.

### 6.2 Unified entity registry

Create one Python `ServingEntitySpec` registry with these fields:

- entity name;
- source changes relation;
- ClickHouse event/current relation;
- ordered business columns;
- ordered primary key;
- explicit ClickHouse cast expressions;
- contract version;
- expected topic/data collection names.

Build/check the registry against the v2 manifest and `table_specs.py`. Separate inconsistent entity lists in the planner, DAG, DDL generator, and tests are forbidden.

### 6.3 Event candidate task

One mapped task per entity:

1. Assert the global lease owner and run state `MATERIALIZING`.
2. Check that no PUBLISHED marker exists for the seq.
3. Run `ALTER TABLE <events> DROP PARTITION <seq>` only for an unpublished seq; a missing partition is a no-op.
4. Insert frozen selected events through `INSERT … SELECT`.
5. Populate `sync_run_seq`, `sync_run_id`, immutable provenance, and contract columns.
6. Check:
   - row count = expected;
   - distinct `event_id` = row count;
   - all rows have `apply_status='applied'`;
   - transaction IDs belong to the frozen prefix, or the row is an allowed initial snapshot;
   - the checksum matches the frozen plan.
7. Write the actual result to `sync_entity_results`.

On retry, the task first removes only its own seq partition. Removing a published partition is forbidden.

### 6.4 Current candidate task

For affected business keys:

1. Take the latest candidate event by deterministic order `(source_ts, kafka_topic, kafka_partition, kafka_offset)`.
2. For `c/r/u`, build the current row from after/business values.
3. For `d`, build a soft-delete row with `is_deleted=true`, business values from the before event, and `deleted_at=source_ts`.
4. Insert one row per affected PK into the seq partition.
5. Do not copy all unchanged published rows into the new partition.
6. Stable/current-state SQL combines published runs with the current candidate and ranks the latest version.

Candidate validation uses `FINAL` to check physical duplicates, but public queries must not depend on merge timing.

### 6.5 PUBLISHED marker

`serving_control.published_runs` remains a small `ReplacingMergeTree(published_at)` keyed by seq. The marker contains:

- seq/run ID;
- previous/target transaction ID;
- `publication_status='PUBLISHED'`;
- snapshot-completed flag;
- deterministic `published_at`;
- canonical compact JSON report.

Idempotent publication:

- marker is absent — insert it;
- effective marker fully matches — no-op;
- marker seq exists with a different run ID/report hash/boundary — terminal invariant failure.

Planning/candidate/failed statuses are not inserted into ClickHouse.

### 6.6 Cleanup policy

- Unpublished candidate partitions are removed on retry or terminal pre-publish cleanup.
- Published event/current partitions are retained without a Stage E TTL: SCD2 uses event history.
- `gold_store` retains at least the two latest PUBLISHED seq values.
- Cleanup never uses “max seq” without checking the PUBLISHED marker.

---

## 7. dbt Gold integration

### 7.1 Preserved public interface

Do not create new Gold business models. Use the existing models:

- `dim_date`
- `dim_order_status`
- `dim_seller`
- `dim_customer_scd2`
- `dim_product_scd2`
- `fact_order_items`
- `mart_daily_revenue`
- `mart_monthly_arpu`

Their public grain and columns do not change. Physical rows remain in `gold_store.<model>` partitioned by `sync_run_seq`; `gold.<model>` remains a stable view of the latest PUBLISHED seq.

### 7.2 Airflow/dbt runtime wiring

- The Airflow image copies `dbt/olist_clickhouse` with its dependencies.
- Serving tasks use this project's separate `DBT_PROFILES_DIR`; the legacy DAG keeps its profiles path until Stage L.
- Run context always passes a positive `sync_run_seq` and a non-empty `sync_run_id`.
- Rebuilding one candidate seq uses the existing `insert_overwrite` semantics.
- dbt invocation uses the programmatic `dbtRunner`, not a shell with a dynamically assembled string.
- The selector is limited to the candidate Gold graph/tests; do not run the legacy Redshift/BigQuery project.

### 7.3 dbt check sequence

1. Before runtime: `dbt deps`, `dbt parse`, `dbt ls` with candidate vars.
2. After the ClickHouse candidate: bounded `dbt show --limit` for critical staging/current relations.
3. Run `dbt build` for the candidate graph with an explicit selector and vars.
4. Run declared structural/data/unit tests.
5. Also check:
   - each physical model contains only the expected candidate seq for this build;
   - primary grain unique;
   - FK/relationship tests create no orphans;
   - SCD2 windows do not overlap;
   - facts/marts contain only the candidate seq;
   - before the marker, public Gold remains on the previous seq.
6. After the marker, verify that all eight public views point to the new max PUBLISHED seq simultaneously.

Add new tests only for material invariants: PK/grain, required relationships, SCD2 windows, and the publication boundary. Do not add `not_null` to every nullable business column.

### 7.4 Gold cleanup

After successful publication/maintenance, call the existing `cleanup_gold_partitions`:

- `keep_published=2`;
- first perform a dry run and validate the exact partition list;
- then perform the actual drop;
- do not remove the active candidate seq;
- do not run cleanup until two successful published runs exist.

---

## 8. Airflow DAGs

Use Airflow 3 `airflow.sdk` imports, the TaskFlow API, dynamic task mapping, and the Spark provider operator. Network/database calls and reading secrets at parse time are forbidden in DAG modules.

### 8.1 Shared configuration

| Parameter | Value |
| --- | --- |
| Timezone | UTC |
| `catchup` | `False` |
| New DAG paused | `False`; all serving DAGs are launched manually only |
| Mutation pool | `olist_serving_mutation`, 1 slot |
| Default retries | 0; terminal failures are recorded in the control plane |
| Retry delay | 60 seconds, exponential backoff |
| Sync DAG timeout | 30 minutes |
| Quality timeout | 15 minutes |
| Maintenance timeout | 90 minutes |
| Rebuild timeout | 90 minutes |
| `max_active_runs` | 1 per DAG |

### 8.2 `olist_lakehouse_serving_sync`

- Schedule: `None`; sync is launched manually.
- `max_active_tasks=4` for the eight mapped entity tasks.

Task graph and exact responsibilities:

1. `preflight`
   - live platform/streaming/ClickHouse/PostgreSQL checks;
   - no mutations.
2. `acquire_or_resume_run`
   - reconciliation;
   - lease acquisition;
   - allocate or resume the logical seq;
   - XCom: seq/run ID only.
3. `plan_boundary`
   - caught-up target;
   - strict transaction prefix;
   - frozen snapshots/counts;
   - the authoritative plan is stored in PostgreSQL.
4. `route_plan`
   - `NOOP`, `WAITING`, `BLOCKED`, or `MATERIALIZE`.
5. `finish_non_materializing_run`
   - terminal status/report without ClickHouse mutation.
6. `materialize_entity.expand(entity=ENTITY_NAMES)`
   - event/current partition replacement;
   - per-entity validation.
7. `validate_serving_candidate`
   - global counts, checksums, and view invisibility.
8. `build_gold_candidate`
   - dbtRunner candidate build.
9. `validate_gold_candidate`
   - dbt tests + explicit publication checks.
10. `publish_marker`
   - final transaction revalidation;
   - deterministic marker insert.
11. `finalize_postgres`
   - cursor/state update.
12. `write_iceberg_report`
   - Spark finite idempotent MERGE.
13. `mark_success`
   - terminal status.
14. `release_lease`
   - teardown with `all_done`; does not erase evidence.

Failure callback:

- writes the fixed error class/code and task ID;
- does not store the full traceback in the ledger;
- if the marker already exists, status becomes `PUBLISHED_PENDING_FINALIZATION`, not FAILED;
- the lease remains recoverable after expiry, and teardown attempts to release it cleanly.

### 8.3 `olist_lakehouse_serving_quality`

- Schedule: `None`; quality is launched manually.
- Read-only checks:
  - PG cursor = latest ClickHouse marker;
  - marker/report hash consistency;
  - latest public current/gold seq;
  - no duplicate effective PK/event ID;
  - event/current/gold row counts;
  - no stale unpublished candidate;
  - next transaction boundary status;
  - source→serving lag;
  - latest maintenance freshness.
- With an active mutation lease, it does not read a partially rebuilt database; it ends the run as skipped/WAITING and does not create a false alert.

### 8.4 `olist_lakehouse_iceberg_maintenance`

- Schedule: `None`; maintenance is launched manually.
- Acquires the mutation lease.
- Gets the inventory from `table_specs.py`.
- Dynamic mapping runs sequentially (`max_active_tis_per_dag=1`) because of the local Spark worker.
- For each table, runs procedures in this order:
  1. `rewrite_data_files`;
  2. `rewrite_manifests`;
  3. `expire_snapshots`;
  4. `remove_orphan_files`.
- Each procedure has a separate audit result.
- Gold cleanup runs after the Iceberg procedures.

### 8.5 `olist_clickhouse_rebuild`

- `schedule=None`.
- The first task checks `dag_run.conf.confirm_destructive is True`.
- The Iceberg plan is frozen before ClickHouse databases are removed.
- Only `serving_cdc`, `serving_control`, `gold_store`, and `gold` are recreated.
- The same entity/dbt/publication code path is then used with `operation_type=REBUILD`.
- Do not use a separate alternative SQL path that could diverge from sync.

### 8.6 Airflow image/init

- Add a compatible `apache-airflow-providers-apache-spark` to locked dependencies.
- Add the Spark 4.1.3 client and project JAR to the Airflow image through a reproducible build stage.
- Build order must guarantee that the Spark artifact exists before the Airflow image is built.
- One-shot `airflow-init` applies the DB migration and creates the `olist_serving_mutation` pool.
- One-shot init creates the non-secret `spark_lakehouse` connection with value `spark://spark-master:7077?deploy-mode=client`; all `SparkSubmitOperator` tasks use exactly `conn_id='spark_lakehouse'`.
- Airflow runtime continues to use `LocalExecutor`.
- REST API authentication uses the existing Simple Auth secret/file; the token is kept only in CLI memory.
- Do not access Airflow metadata tables directly.

---

## 9. Publication and failure recovery

### 9.1 Exact publication order

1. Store the final canonical report and one `published_at` in PostgreSQL.
2. Check the previous marker/cursor.
3. Insert the ClickHouse PUBLISHED marker.
4. Read the marker back and compare all immutable fields/hash values.
5. In one PostgreSQL transaction:
   - update the `runtime_state` cursor;
   - move the run to `PUBLISHED_PENDING_FINALIZATION`.
6. Execute the Iceberg report `MERGE` by `sync_run_id`.
7. Move the run to `SUCCEEDED`.
8. Release the lease.

### 9.2 Failure matrix

| Failure point | Visibility | Retry |
| --- | --- | --- |
| Before plan commit | Old run | Create/resume the plan |
| After plan, before first entity | Old run | Same seq |
| During entity tasks | Old run | Drop/rebuild partitions for the same seq |
| After entities, before dbt | Old run | Validate/rebuild the candidate with the same seq |
| After dbt, before marker | Old run | Rebuild candidate/dbt with the same seq |
| After marker, before PG cursor | New run visible | Reconcile marker; materialization forbidden |
| After PG cursor, before Iceberg report | New run visible | Idempotent report MERGE only |
| After report, before success status | New run visible | Mark success/release |
| ClickHouse loss | Serving unavailable | Guarded rebuild only |
| Control-schema loss | Marker may be visible | Reconstruct from marker/report; rebuild on CH loss |

### 9.3 Failpoints

Add test-only failpoints, disabled by default:

- `after_plan_commit`;
- `after_first_entity_materialized`;
- `after_all_entities_validated`;
- `after_dbt_before_marker`;
- `after_marker_before_postgres`;
- `after_postgres_before_iceberg_report`.

Failpoint names may come only from a fixed allowlist, cannot activate arbitrary shell/code payloads, and are recorded in the sanitized report.

---

## 10. Spark finite operations and maintenance security

### 10.1 Config split

The current `SparkPlatformConfig` requires checkpoint credentials for every Spark job. Split it into:

- `SparkCatalogConfig`: Polaris REST catalog, warehouse, OAuth principal, vended credentials, S3 endpoint/region, redaction;
- `SparkCheckpointConfig`: exactly `s3a://olist-checkpoints` and static MinIO checkpoint credentials;
- streaming mode = catalog + checkpoint;
- maintenance mode = catalog only.

The renderer accepts exact `--mode streaming|maintenance`. An unknown mode is a configuration error.

Maintenance properties must not contain:

- `spark.olist.checkpoint.root`;
- `fs.s3a.access.key/secret.key` checkpoint user;
- any path inside `olist-checkpoints`.

### 10.2 `LakehouseOpsMain`

One Scala entry point with subcommands:

```text
record-serving-report --input-file <0600-json>
maintenance --run-id <id> --procedure <allowlisted> --table <fqtn> --options-file <0600-json>
```

Requirements:

- table is checked against the migration/table-spec inventory;
- procedure is limited to a fixed allowlist;
- the options schema is validated before SparkSession mutation;
- output is one sanitized JSON object;
- report/maintenance writes use the Iceberg MERGE key;
- temporary files are removed in `finally`;
- secrets are not passed in application args.

### 10.3 Maintenance defaults

| Procedure | Default |
| --- | --- |
| `rewrite_data_files` | Target from the table property `write.target-file-size-bytes`, otherwise 134217728 bytes (128 MiB) |
| `rewrite_manifests` | After data-file rewrite |
| `expire_snapshots` | Older than 7 days, retain the last 20 |
| `remove_orphan_files` | Older than 72 hours, explicit table location only |

Do not shorten the orphan interval: removing files too early can delete files from an incomplete write — [Iceberg maintenance](https://iceberg.apache.org/docs/latest/maintenance/).

Each result in `audit.maintenance_runs` contains the run ID, procedure, namespace/table, status, timestamps, and sanitized options/result/error.

The scheduled DAG calls `rewrite_data_files` for every supported table and accepts the standard Iceberg no-op as success. No external heuristic decides whether to skip the procedure: the Iceberg action itself determines whether a rewrite is needed for the specified target size.

---

## 11. Rebuild contract

### 11.1 Guards

- CLI without `--yes` returns code 1 before contacting Airflow.
- DAG without exact boolean `confirm_destructive=true` ends before lease/mutation.
- The report lists exactly four target databases.
- Any target outside the allowlist is a fatal configuration error.

### 11.2 Algorithm

1. Check the Iceberg catalog and required tables.
2. Acquire the global lease.
3. Reconcile and allocate/resume the rebuild seq.
4. Freeze the full plan: initial applied snapshot rows plus the maximal COMPLETE transaction prefix up to the current boundary.
5. Check counts/snapshots before the destructive step.
6. Drop/recreate only the four derived ClickHouse databases.
7. Apply the current ClickHouse DDL/catalog bootstrap.
8. Materialize the full event ledger from the frozen snapshots.
9. Materialize current rows.
10. Run dbt build/tests.
11. Insert the initial rebuilt PUBLISHED marker.
12. Update the PostgreSQL cursor and Iceberg report.
13. Run serving quality checks.

### 11.3 Forbidden rebuild actions

- `docker compose down -v`;
- reset MySQL/Kafka/Polaris/MinIO;
- deleting Iceberg namespaces/tables/data files;
- deleting Spark checkpoints;
- mutation source data;
- reuse unfrozen “latest” snapshots after rebuild begins.

---

## 12. CLI contract

### 12.1 `sync-serving`

```text
python scripts/cdc/local_lab.py sync-serving \
  [--run-id <id>] [--timeout <seconds>]
```

Behavior:

1. Checks/starts required profiles without reset.
2. Waits for Airflow health and DAG availability.
3. Obtains a short-lived bearer token.
4. POSTs to `/api/v2/dags/olist_lakehouse_serving_sync/dagRuns`.
5. A duplicate run ID attaches to the existing DagRun.
6. Polls the stable REST API until a terminal state.
7. Reads the authoritative result through the serving report API/helper, not Airflow metadata SQL.
8. Does not change pause state or activate schedules: all serving DAGs are manual-only.
9. Duplicate/stale DagRuns are not reused; a manual run must have a unique run ID.

Use the official Airflow API contract: [Stable REST API](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html).

### 12.2 `rebuild-serving`

```text
python scripts/cdc/local_lab.py rebuild-serving --yes \
  [--run-id <id>] [--timeout <seconds>]
```

Passes `confirm_destructive=true`, waits for the DAG, and returns the rebuilt report.

### 12.3 `run-maintenance`

```text
python scripts/cdc/local_lab.py run-maintenance \
  [--run-id <id>] [--timeout <seconds>]
```

Default — the full inventory/all procedures. Do not add arbitrary SQL/procedure args to the public Stage E CLI.

### 12.4 Status/validate

```text
status --require platform|streaming|serving
validate --scope platform|streaming|serving
```

`status --require serving` checks:

- Compose long-running/one-shot inventory;
- Airflow API and four DAGs;
- PostgreSQL migration, lease, latest run/cursor;
- ClickHouse databases/tables/views/catalog;
- marker/cursor/report consistency;
- current/gold view mapping;
- stale unpublished candidates;
- latest quality/maintenance status.

`validate --scope serving` is read-only. It does not start sync, rebuild, maintenance, or cleanup.

### 12.5 JSON result and exit codes

Successful sync results contain:

```json
{
  "command": "sync-serving",
  "status": "succeeded",
  "dag_run_id": "manual__...",
  "sync_run_id": "sync-00000000000000000042",
  "sync_run_seq": 42,
  "is_noop": false,
  "previous_transaction_id": "...",
  "target_transaction_id": "...",
  "expected_event_count": 7,
  "materialized_event_count": 7,
  "published_at": "...Z",
  "schedules_activated": true
}
```

Exit codes:

- `0`: READY, SUCCEEDED, or NOOP;
- `2`: WAITING, BLOCKED, or NOT_CAUGHT_UP;
- `1`: execution, configuration, or invariant failure.

`final-parity` remains deferred until Stage F; change its currently incorrect phase label from E to F.

---

## 13. Observability

### 13.1 Exporter

Add a low-cardinality serving exporter that collects read-only:

- PostgreSQL run/cursor/lease;
- ClickHouse marker/row counts;
- next Iceberg transaction boundary;
- Iceberg snapshot/file statistics;
- latest maintenance report;
- component health.

The exporter exposes a failure metric and continues serving the latest safe observations when one backend is temporarily unavailable. It does not log queries containing secrets or export business values.

### 13.2 Metrics

| Metric | Labels |
| --- | --- |
| `olist_serving_sync_runs_total` | bounded `result` |
| `olist_serving_sync_duration_seconds` | none/result histogram |
| `olist_serving_last_attempt_timestamp_seconds` | none |
| `olist_serving_last_publication_timestamp_seconds` | none |
| `olist_serving_source_to_publication_lag_seconds` | none |
| `olist_serving_next_boundary_status` | bounded `status` |
| `olist_serving_unpublished_candidate_age_seconds` | none |
| `olist_serving_watermark_drift` | none, 0/1 |
| `olist_serving_event_rows` | `entity` |
| `olist_serving_current_rows` | `entity` |
| `olist_serving_gold_rows` | `model` |
| `olist_iceberg_snapshots` | `table` |
| `olist_iceberg_data_files` | `table` |
| `olist_iceberg_average_data_file_bytes` | `table` |
| `olist_iceberg_maintenance_last_success_timestamp_seconds` | `procedure` |

Forbidden labels: transaction ID, event ID, run ID, error message, topic offset.

### 13.3 Alerts

| Alert | Condition |
| --- | --- |
| `ServingSyncStalled` | A new COMPLETE boundary exists and successful/no-op sync is older than 10 minutes |
| `ServingRejectedBoundary` | The next unpublished transaction is REJECTED |
| `ServingPublicationDrift` | PG cursor and CH marker diverge for more than 2 minutes |
| `ServingCandidateStale` | Unpublished nonterminal candidate is older than 20 minutes |
| `ServingMaterializationMismatch` | expected != materialized |
| `ServingQualityFailed` | The latest hourly quality DAG failed |
| `IcebergMaintenanceStale` | No daily success for more than 36 hours |
| `IcebergSmallFiles` | `data_files > 100`, or both `data_files > 10` and average size `< 1048576` bytes for 10 minutes |
| `ServingComponentUnavailable` | ClickHouse/Airflow/Spark/exporter unavailable |

### 13.4 Grafana dashboard

One Stage E dashboard must contain:

- component health;
- Kafka/Silver/serving offsets and lag;
- current run state/duration;
- last published transaction/age without a high-cardinality label;
- event/current counts by entity;
- Gold counts by model;
- candidate visibility/drift;
- maintenance duration/status;
- Iceberg snapshot/file count/average size;
- latest active alerts.

Prometheus scrape config and Compose services must match: dangling targets are forbidden. Legacy dashboards/rules remain until Stage L but must not break the health of the new profile.

---

## 14. Security and secret handling

- All passwords/OAuth credentials are read only from `*_FILE`.
- Dynamic command strings contain no secrets.
- The Spark properties file is created with `0600` and removed after the task.
- Airflow XCom/report contains only IDs/counts/boundaries/snapshot IDs.
- PostgreSQL `error_details_json` stores a fixed code/class/task ID, not a raw exception/payload.
- ClickHouse `report_json` is canonical and sanitized.
- The maintenance principal has warehouse table write access but no checkpoint-bucket access.
- The ClickHouse DataLakeCatalog principal remains read-only to Iceberg.
- Logs pass the existing redaction regex and separate negative tests.
- The API bearer token lives only in CLI memory and is not written to JSON results.

---

## 15. Test strategy

### 15.1 Fast/static CI

Required checks:

- `uv lock --check`;
- Python lint/format/type/unit tests relevant paths;
- Scala compile, scalafmt check, and unit tests;
- generated schema/contracts `--check`;
- Compose config for all profiles;
- PostgreSQL migration application/idempotency/grants;
- ClickHouse DDL and learning tests;
- Airflow DAG import/errors/warnings/graph assertions;
- dbt deps/parse/ls with candidate vars;
- Prometheus `promtool check config/rules`;
- Grafana provisioning JSON/YAML validation;
- `git diff --check`.

Do not run the entire dbt project without a selector; Stage E CI is limited to the `olist_clickhouse` candidate graph.

### 15.2 Unit/contract matrix

#### PostgreSQL

- sequence monotonicity and permitted gaps;
- allowed/forbidden state transitions;
- concurrent acquire: one winner;
- lease heartbeat/expiry/steal;
- resume of the same seq;
- marker-ahead reconciliation;
- cursor-ahead fail closed;
- reconstruction from marker/report;
- JSON/error redaction.

#### Boundary planner

- initial snapshot only;
- snapshot + complete prefix;
- single/multi-entity transaction;
- multiple consecutive COMPLETE;
- OPEN first/inside range;
- REJECTED first/inside range;
- COMPLETE after REJECTED is not included;
- declared count mismatch;
- collection mismatch/unknown collection;
- transaction order gap;
- missing progress snapshot;
- stale progress vs caught-up contradiction;
- no-op;
- status changed to REJECTED immediately before marker.

#### ClickHouse

- event idempotency;
- partition retry cleanup;
- composite PK current ranking;
- delete visibility;
- candidate invisible before marker;
- previous published row survives physical merge unpublished candidate;
- marker idempotency/conflict;
- all eight Gold views switch only after marker.

#### dbt

- positive run context required;
- each model grain unique;
- required relationships;
- SCD2 no overlap/current window rules;
- fact grain;
- candidate partition overwrite;
- public view previous/new publication boundary.

#### Airflow

- no top-level network access;
- exact schedule/timezone/catchup/retries/timeouts;
- dynamic map exactly eight entities;
- task dependency graph;
- failure callback before/after marker;
- XCom payload restricted to small IDs;
- rebuild conf guard;
- first-sync unpause idempotency;
- manual operator pause preserved after activation.

#### Maintenance/rebuild

- table/procedure allowlists;
- root/bucket/checkpoint path rejection;
- exact retention defaults;
- audit MERGE retry;
- rebuild target database allowlist;
- rebuild leaves MySQL/Kafka/Iceberg/checkpoints untouched.

### 15.3 Bounded serving component test

A separate CI/manual job uses a small fixture and starts only the required profiles:

1. Clean platform/bootstrap.
2. Initial snapshot and real caught-up barrier.
3. Initial serving sync.
4. One multi-table COMPLETE transaction.
5. One NOOP sync.
6. Failpoint before marker + same-seq retry.
7. Failpoint after marker + metadata-only retry.
8. One targeted maintenance procedure.
9. Serving status/validate.

This job does not replace Stage V: it does not run the full CRUD/restart/additive-schema scenario.

### 15.4 Clean-domain Stage E acceptance

Command sequence:

```powershell
python scripts/cdc/local_lab.py reset --yes
python scripts/cdc/local_lab.py bootstrap --run-id stage_e_clean
python scripts/cdc/local_lab.py start-streaming
python scripts/cdc/local_lab.py wait-caught-up --timeout 1200
python scripts/cdc/local_lab.py sync-serving --run-id stage_e_initial --timeout 1800
python scripts/cdc/local_lab.py status --require serving
python scripts/cdc/local_lab.py validate --scope serving
python scripts/cdc/local_lab.py run-maintenance --run-id stage_e_maintenance --timeout 5400
python scripts/cdc/local_lab.py rebuild-serving --yes --run-id stage_e_rebuild --timeout 5400
python scripts/cdc/local_lab.py validate --scope serving
```

After initial sync:

- fixture manifest counts match in Silver/current/serving/gold;
- PG cursor, CH marker, and Iceberg report match;
- candidate partitions are published under one seq;
- the four serving DAGs are manual-only, `schedule=None`, `is_paused=false`;
- public views return the expected rows;
- no secrets appear in reports/logs.

Also run the transaction/rejected/failpoint scenarios from the acceptance harness.

---

## 16. Validation report

Create `docs/reports/mysql-spark-iceberg-stage-e-validation.md` only after actual execution.

The report must contain:

- implementation commit SHA and dirty-state statement;
- pinned component versions;
- clean reset/bootstrap evidence;
- E0 query inventory, captured targets, and snapshot coverage;
- initial/no-op/transaction sync summaries;
- PG/CH/Iceberg seq and boundary equality;
- candidate-before-marker invisibility evidence;
- before-marker and after-marker failpoint recovery;
- dbt command/selector and test totals;
- maintenance procedures/results;
- rebuild scope and post-rebuild parity counts;
- Prometheus targets/alerts/dashboard evidence;
- secret-redaction/checkpoint-denial evidence;
- final `status --require serving` and `validate --scope serving` JSON;
- final `PASS|FAIL`.

Stage E may be marked complete only with `PASS` and no unresolved blockers.

---

## 17. Implementation order and checkpoints

### E0 — J2 repair

- Full Silver normalization/audit/progress/transaction contract.
- Real offset-based caught-up.
- Stop/go tests.

**Gate**: serving code does not begin materialization without E0 PASS.

### E1 — Contracts and control schema

- Synchronize normative docs.
- Add PostgreSQL migration/repository/state machine/lease/reconciliation.

**Gate**: migration, concurrency, and recovery tests PASS.

### E2 — ClickHouse atomic candidate storage

- Fix current partitions/order.
- Add the registry and event/current materializer.
- Add the marker publisher.

**Gate**: unpublished merge regression and idempotent retry PASS.

### E3 — dbt candidate integration

- Airflow image/project wiring.
- Candidate selector/build/tests/publication checks.

**Gate**: the candidate is completely invisible before the marker, and public Gold switches after the marker.

### E4 — Airflow serving sync

- Init/pool/Spark provider.
- Sync DAG and crash finalization.

**Gate**: initial/no-op/before-marker/after-marker component tests PASS.

### E5 — Quality, maintenance, and rebuild

- Three additional DAGs.
- Spark config split and `LakehouseOpsMain`.
- Safe cleanup/rebuild.

**Gate**: no checkpoint access, maintenance audit, and derived-only rebuild PASS.

### E6 — CLI and observability

- REST orchestration, status/validate, activation semantics.
- Exporter, metrics, alerts, dashboard, runbooks.

**Gate**: CLI contract and monitoring validation PASS.

### E7 — Clean-domain acceptance

- Full Stage E command sequence.
- Validation report.
- Roadmap/status update.

**Gate**: report `PASS`; Stage V is permitted afterward.

---

## 18. Expected change map

The implementer follows this name map to avoid creating alternative packages/DAG IDs/migrations.

### 18.1 Documents

- This file is the only detailed active Stage E implementation plan.
- `docs/plans/lakehouse/active/serving-cutover.md` is the link and high-level gate, without duplicating details.
- Contracts in `docs/plans/lakehouse/contracts/` provide normative table/CLI/runtime/CI semantics.
- New runbooks:
  - `docs/runbooks/lakehouse-serving-sync.md`;
  - `docs/runbooks/lakehouse-serving-rejected-boundary.md`;
  - `docs/runbooks/lakehouse-iceberg-maintenance.md`;
  - `docs/runbooks/lakehouse-clickhouse-rebuild.md`.
- Final report: `docs/reports/mysql-spark-iceberg-stage-e-validation.md`.

### 18.2 J2 repair / Spark streaming

Refactor existing:

- `streaming/spark/scala/src/main/scala/com/olist/mds/spark/app/BronzeMain.scala`;
- `streaming/spark/scala/src/main/scala/com/olist/mds/spark/app/SilverMain.scala`;
- `streaming/spark/scala/src/main/scala/com/olist/mds/spark/bronze/BronzeBatchWriter.scala`;
- `streaming/spark/scala/src/main/scala/com/olist/mds/spark/silver/SilverBatchWriter.scala`;
- `streaming/spark/scala/src/main/scala/com/olist/mds/spark/supervisor/StatusPublisher.scala`;
- `streaming/spark/scala/src/main/scala/com/olist/mds/spark/operational/LakehouseStatusMain.scala`.

Create packages/classes:

- `silver/EntityBatchProcessor.scala` — shared decode/validation/commit flow;
- `silver/SilverProgressWriter.scala` — progress MERGE/snapshot IDs;
- `silver/IcebergCommitCoordinator.scala` — fair per-audit-table locks;
- `schema/SchemaArchiveWriter.scala` — `capture_avro_schemas`;
- `transaction/TransactionBatchWriter.scala` — BEGIN/END validation and transaction states;
- `operational/LakehouseOpsMain.scala` and `app/LakehouseOpsMain.scala` — finite report/maintenance entry point.

Do not create eight separate copy-paste writers; entity-specific rules remain in the existing entity registry/modules.

### 18.3 PostgreSQL/control package

- `infra/control-postgres/initdb/005_create_serving_control_tables.sql` — schema/sequence/tables/indexes/singleton row.
- `infra/control-postgres/initdb/999_grant_control_role.sql` — serving DML/sequence grants.
- `scripts/serving/__init__.py`.
- `scripts/serving/models.py` — enums/dataclasses/canonical report/checksum.
- `scripts/serving/control.py` — repository, state machine, lease, and reconciliation.
- `scripts/serving/boundary.py` — caught-up target and strict transaction planner.
- `scripts/serving/entities.py` — the only `ServingEntitySpec` registry.
- `scripts/serving/clickhouse.py` — materialization/validation/marker/rebuild helpers.
- `scripts/serving/dbt_runner.py` — bounded programmatic dbt invocation.
- `scripts/serving/airflow_api.py` — token/trigger/poll/unpause client.
- `scripts/serving/metrics.py` — read-only Prometheus exporter.

The public CLI remains in `scripts/cdc/local_lab.py`; it calls the package API and does not contain a second planner/materializer implementation.

### 18.4 ClickHouse

- Change `infra/clickhouse/lakehouse/004_create_current_version_tables.sql`.
- `infra/clickhouse/lakehouse/005_create_stable_current_views.sql` preserves the current public columns/ranking; do not rewrite its SQL, but check it with a new regression after changing physical partitioning.
- Create `infra/clickhouse/lakehouse/tests/002_unpublished_current_isolation.sql` for the required published/unpublished/OPTIMIZE regression; keep the existing learning test separate.
- `init.sh` remains the only ordered DDL entry point and is used by sync bootstrap/rebuild.

### 18.5 Airflow and images

- `airflow/dags/olist_lakehouse_serving.py` defines only the sync and quality DAGs.
- `airflow/dags/olist_lakehouse_maintenance.py` defines only the maintenance and rebuild DAGs.
- Shared business/control functions are imported from `scripts.serving`; DAG files contain no SQL builders.
- `docker/airflow/Dockerfile` copies `dbt/olist_clickhouse`, the Spark client/JAR, and the locked provider.
- `docker/airflow/load-env-and-run.sh` preserves file-secret loading; do not expand dynamic secrets into environment values.
- `compose.yaml` adds `airflow-init`, the serving exporter, and exact profile dependencies/healthchecks.

### 18.6 Spark config and build

- Refactor `streaming/spark/platform/config.py` to catalog/checkpoint config.
- Extend `streaming/spark/platform/render_spark_properties.py` with an exact mode flag.
- `docker/spark/run-with-platform-config.sh` explicitly invokes streaming mode.
- The Airflow SparkSubmitOperator explicitly uses maintenance-mode properties.
- `streaming/spark/scala/build.sbt` receives only the required compile/test dependencies; runtime Spark/Iceberg artifacts remain Provided.

### 18.7 dbt

- Change existing SQL models in `dbt/olist_clickhouse/models/` only for a proven test failure.
- Preserve `macros/run_context.sql`, `source_state.sql`, and `cleanup_gold_partitions.sql` as the unified candidate/publication interface; accompany changes with a downstream `dbt ls` impact check.
- Create `dbt/olist_clickhouse/selectors.yml` with a `serving_candidate` selector including the eight physical models, ancestors, and their tests.
- Airflow runs only selector `serving_candidate` with explicit vars.

### 18.8 Observability

- `observability/prometheus/prometheus.yml` — exact active scrape inventory.
- `observability/prometheus/rules/lakehouse-serving-alerts.yml` — Stage E alerts.
- `observability/prometheus/rules/lakehouse-serving-recording.yml` — bounded recording rules.
- `observability/grafana/provisioning/dashboards/lakehouse.yml` — provider entry.
- `observability/grafana/dashboards/lakehouse-serving.json` — dashboard.
- Legacy files remain in place until Stage L, but active rules do not reference missing services/runbooks.

### 18.9 Tests and CI

- Python unit tests: `tests/serving/` with separate files for control, boundary, ClickHouse SQL, CLI/API, and metrics/redaction.
- Scala tests extend the existing Bronze/Silver suites and add transaction/progress/ops suites.
- Airflow contract tests check the two new DAG modules through the existing `scripts/ci/check_airflow_dag_imports.py`.
- ClickHouse runtime checks are added under `scripts/ci/` as bounded Stage E checks, not legacy warehouse scripts.
- `.github/workflows/ci.yml` receives separate named `serving-static` and `serving-component` steps/jobs; full Candidate E2E remains a Stage V/manual gate.

---

## 19. Definition of Done

- [x] E0 J2 repair passed a separate stop/go gate.
- [x] `olist_control.serving` contains only control metadata and can be recovered from marker/report.
- [x] Current candidates are physically isolated by `sync_run_seq`.
- [x] `olist_lakehouse_serving_sync` publishes only the maximal COMPLETE prefix.
- [x] OPEN/REJECTED transactions are not crossed.
- [x] The initial snapshot is published only as a whole.
- [x] The candidate is invisible before the marker.
- [x] Retry before the marker uses the same seq and creates no duplicates.
- [x] Retry after the marker only finalizes metadata.
- [x] All eight dbt Gold models/tests are integrated into the candidate flow.
- [x] Serving, quality, maintenance, and rebuild DAGs are manual-only, `schedule=None`, `is_paused=false`.
- [x] Maintenance uses the Airflow Polaris principal without checkpoint access.
- [x] `rebuild-serving --yes` restores only derived ClickHouse databases.
- [x] `status --require serving` and `validate --scope serving` return READY on a clean domain.
- [x] Prometheus/Grafana/alerts work without dangling targets.
- [x] The validation report has status PASS.
- [x] The legacy path is not removed; Stage L remains the next stage after F0.

---

## 20. Related documents

- [Migration roadmap](../../mysql-spark-iceberg-lakehouse-migration.md)
- [E/V repair → F0 → L → F1 coordination plan](../active/serving-cutover.md)
- [Serving & Recovery contract](../contracts/serving-and-recovery.md)
- [Spark Structured Streaming contract](../contracts/spark-streaming.md)
- [Iceberg data model contract](../contracts/iceberg-data-model.md)
- [Architecture/runtime contract](../contracts/architecture-and-runtime.md)
- [Validation/CI contract](../contracts/validation-and-ci.md)
