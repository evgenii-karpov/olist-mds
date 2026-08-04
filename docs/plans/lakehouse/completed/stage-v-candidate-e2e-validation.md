# Detailed Stage V plan: Candidate E2E Validation

- **Status**: Completed / Frozen — clean V0–V10 PASS.
- **Execution commit**: `e113c552cca990636f426b827456a77ddc9d594b` (`dirty=false`).
- **Run ID**: `stage_v_clean_e113c55`.
- **Evidence**: `data/stage-v-evidence/stage_v_clean_e113c55/`.
- **Goal**: prove on one clean and isolated environment that the candidate
  `MySQL -> Debezium -> Kafka -> Spark Bronze/Silver -> Iceberg -> ClickHouse -> dbt Gold`
  correctly handles the initial snapshot, transactional CRUD, tombstones,
  simultaneous Bronze/Silver restart, additive nullable schema, and full
  ClickHouse recovery from Iceberg only.
- **Previous stage**: Stage E, status `PASS` in the
  [Stage E report](../../../reports/mysql-spark-iceberg-stage-e-validation.md).
- **Parent stage order**:
  [serving-cutover.md](../active/serving-cutover.md), strictly `E -> V -> L -> F`.
- **Authority order**: active contracts from
  `docs/plans/lakehouse/contracts/` -> this plan -> actual machine-readable
  evidence -> final validation report.

---

## 1. Expected result

Stage V ends with exactly one of three outcomes:

| Outcome | Meaning |
| --- | --- |
| `PASS` | All V0–V10 gates pass in one clean-domain run, evidence is complete, and Stage L may begin. |
| `FAIL` | The candidate violates a checked invariant; Stage L is forbidden. |
| `BLOCKED` | A reliable result cannot be obtained because of a Stage E, environment, or validation-harness defect; Stage L is forbidden. |

Success is not merely a set of zero exit codes. The agent must prove:

1. the original 79 business rows and 6 geolocations reach the target tables;
2. three CRUD transactions produce exactly 10 business CDC events;
3. delete produces one delete envelope and one subsequent tombstone;
4. checkpoints continue after restart rather than being recreated;
5. `event_id` values are unique, and business keys/values match row by row;
6. only a completed transaction boundary is published;
7. the PostgreSQL cursor, ClickHouse marker, and Iceberg report describe one run;
8. stable `serving_cdc.*_current` and `gold.*` views do not see unpublished data;
9. nullable additive evolution does not stop the compatible stream;
10. ClickHouse is fully restored from Iceberg without reading MySQL/Kafka;
11. canonical manifests before and after rebuild match;
12. legacy components are not removed and Stage F is not run.

---

## 2. Scope and explicit prohibitions

### 2.1 In scope

- Implementation of a reproducible Stage V acceptance harness.
- Validation-only SQL fixtures and read-only probes for all layers.
- One full run on a new Compose project and clean volumes.
- Initial snapshot, deterministic CRUD, tombstone, and restart drill.
- Serving-candidate publication and dbt candidate-graph checks.
- Controlled additive nullable schema evolution.
- Guarded ClickHouse rebuild and row-level manifest comparison.
- Collection of sanitized evidence and creation of the Stage V report.
- Fixes limited to validation-harness defects before the final clean run.

### 2.2 Out of scope

- Removal of legacy PostgreSQL, NiFi, old DAGs, or other Stage L components.
- Running final parity or changing its contract — that is Stage F.
- Changing Kafka retention, topology, partition count, or primary keys.
- Testing incompatible schema evolution: rename, drop, type change, or a
  non-nullable column without a default.
- Performance/SLO benchmarks and long soak tests.
- Maintenance not required for the rebuild check.
- Manually modifying data directly in Iceberg or ClickHouse.
- Weakening contracts, tests, lint/type rules, or acceptance thresholds to
  obtain `PASS`.

### 2.3 Agent prohibitions

- Do not run `docker compose down -v` directly. The only permitted cleanup is
  `python scripts/cdc/local_lab.py reset --yes` after checking
  `COMPOSE_PROJECT_NAME`.
- Do not remove individual authoritative volumes, checkpoint paths, Iceberg
  snapshots, or control-ledger rows.
- Do not run `sync-serving`, `rebuild-serving`, and maintenance in parallel.
- Do not continue an acceptance run after an invariant violation. First preserve
  evidence, classify the cause, and finish the run as `FAIL`/`BLOCKED`.
- Do not consider rerunning one failed step sufficient for `PASS`. After a
  production-code fix, a new full clean-domain run is required.
- Do not print secret-file contents, connection strings, bearer tokens, or
  passwords in the command line, stdout, JSON, or Markdown.
- Do not create a `PASS` report before V10 actually completes.

---

## 3. Starting point and mandatory Stage E reconciliation

### 3.1 What already exists

- Deterministic small fixture:
  `tests/fixtures/olist_small/olist_small.zip`.
- Source oracle:
  `tests/fixtures/olist_small/source_profile_small.json`.
- CRUD fixture:
  `tests/spark_integration/fixtures/wave2_crud.sql`.
- Lifecycle CLI: `scripts/cdc/local_lab.py` with `reset`, `bootstrap`,
  `start-streaming`, `wait-caught-up`, `status`, `validate`, `sync-serving`, and
  `rebuild-serving`.
- Normative contracts:
  [Spark streaming](../contracts/spark-streaming.md),
  [Iceberg data model](../contracts/iceberg-data-model.md),
  [Serving and recovery](../contracts/serving-and-recovery.md) and
  [Validation and CI](../contracts/validation-and-ci.md).
- Serving/rebuild runbooks in `docs/runbooks/`.

### 3.2 Why Stage E `PASS` is rechecked

Stage V does not reopen Stage E without cause, but it must check its entry gate
against the current execution commit. Logs attached to the task show that in one
previous tree state, pre-commit changed whitespace/EOF/format and then reported
Ruff and Pyright errors. These logs are not a fresh result and do not change the
Stage E status automatically, but a costly E2E run must not start without a new
green V0.

The agent must also verify that the current implementation actually fulfills the
contract rather than merely exposing the required command names. In particular,
a fresh audit must confirm:

- the boundary planner receives real `audit.mysql_transactions`, progress, and
  Iceberg snapshot IDs rather than empty collections;
- the materializer filters `*_changes` by the frozen boundary for the specific run;
- `*_current_versions` are built from the latest version of each business key and
  retain real Kafka offsets, delete state, and row hashes;
- `status --require serving` checks marker/cursor/report, DAG inventory, stale
  candidates, and quality state, not only HTTP health;
- `validate --scope serving` performs the declared read-only serving checks;
- the CLI returns the complete authoritative Stage E result contract, including
  `sync_run_id`, boundaries, event counts, and publication metadata;
- rebuild does not use MySQL, Kafka, or Spark checkpoints as a data source.

If any item is not confirmed, the V0 result is `BLOCKED_BY_E_REGRESSION`.
The fix is recorded as a Stage E defect, after which V0 and the full clean-domain
run are restarted. The agent may not replace missing production semantics with
validation-harness logic.

---

## 4. Run identity and evidence contract

### 4.1 Isolation

Before mutating commands, the agent sets once:

```powershell
$env:COMPOSE_PROJECT_NAME = "olist_stage_v"
$StageVRunId = "stage_v_<UTC timestamp>_<short commit>"
$StageVEvidence = "data/stage-v-evidence/$StageVRunId"
```

Requirements:

- `COMPOSE_PROJECT_NAME` must be exactly `olist_stage_v`;
- no other Stage V run may execute alongside it;
- all mutating run IDs begin with `$StageVRunId`;
- the execution commit SHA is recorded before `reset`;
- the tracked worktree is clean; only ignored runtime/evidence files are allowed;
- changing the execution commit or tracked files invalidates the current run.

### 4.2 Evidence structure

The harness creates a directory under `data/`, which is already excluded from Git:

```text
data/stage-v-evidence/<run-id>/
  run-manifest.json
  00-preflight/
  01-clean-bootstrap/
  02-initial-snapshot/
  03-crud-and-restart/
  04-caught-up/
  05-serving-sync/
  06-dbt-and-stable-views/
  07-additive-schema/
  08-rebuild/
  09-final/
  checksums.json
  summary.json
```

Each gate stores:

- `started_at`, `finished_at`, duration, and execution commit;
- sanitized argv without secret values;
- exit code and bounded stdout/stderr;
- input and output snapshot/offset/run identifiers;
- canonical query results in JSON;
- an assertion list with `PASS|FAIL|BLOCKED` and diagnostic code;
- SHA-256 for every evidence file.

`run-manifest.json` is immutable after V2 starts, except for adding terminal status
and `finished_at`. It must contain:

- OS, Docker/Compose, and component image versions;
- commit SHA and the result of `git status --porcelain`;
- fixture SHA-256 and expected-count manifest;
- Compose project name;
- random seed `20260801` and start time `2020-01-01T00:00:00`;
- list of gates and their terminal status;
- redaction-scan result;
- links to final canonical manifests.

### 4.3 Rerun rules

- A read-only probe may be repeated in the same run while preserving the attempt number.
- `bootstrap`, CRUD, schema mutation, publication, and rebuild may be repeated in
  the same run only when the operation contract is explicitly idempotent and the
  first call has a known terminal state.
- An unknown terminal state for a mutating operation means `BLOCKED`; do not guess
  the result or create a new run ID on the same volumes.
- After any production fix, perform a new `reset --yes`, new run ID, and full V2–V10 path.

---

## 5. Validation harness to implement before the acceptance run

### 5.1 Files

Recommended change map:

```text
scripts/validation/stage_v_candidate_e2e.py
scripts/validation/stage_v_probes.py
tests/stage_v/fixtures/insert.sql
tests/stage_v/fixtures/update.sql
tests/stage_v/fixtures/delete.sql
tests/stage_v/fixtures/add_nullable_column.sql
tests/stage_v/fixtures/emit_nullable_event.sql
tests/stage_v/oracles/initial_counts.json
tests/stage_v/test_stage_v_harness.py
tests/stage_v/test_stage_v_oracles.py
  docs/reports/mysql-spark-iceberg-stage-v-validation.md  # after the run only
```

`wave2_crud.sql` may be reused, but three separate fixtures with the same
statements and fixed IDs are preferable for the restart barrier. Do not change
the business semantics of the accepted Wave 2 scenario.

### 5.2 Public harness interface

```text
uv run python scripts/validation/stage_v_candidate_e2e.py prepare \
  --run-id <id> --evidence-dir <path>

uv run python scripts/validation/stage_v_candidate_e2e.py run \
  --run-id <id> --evidence-dir <path> --confirm-reset

uv run python scripts/validation/stage_v_candidate_e2e.py report \
  --evidence-dir <path>
```

- `prepare` runs only V0–V1 and does not change runtime data.
- `run` is the only documented orchestration of V2–V10.
- `report` reads existing evidence, starts nothing, and cannot promote terminal status.
- `--confirm-reset` is not passed to an embedded arbitrary shell payload.
- Every command emits one bounded JSON result and the correct non-zero exit code.

### 5.3 Probe adapters

The harness must use separate typed adapters:

1. **MySQL probe** — read-only queries through the existing Python connector and
   password file; the fixture executor has an allowlist of only five Stage V SQL statements.
2. **Kafka probe** — topic/partition beginning/end offsets and selective
   key/value/tombstone checks without changing consumer offsets for production groups.
3. **Iceberg probe** — finite Spark job with a fixed report allowlist. Do not add
   public arbitrary SQL execution.
4. **PostgreSQL control probe** — read-only retrieval of the latest run, entity results,
   runtime cursor, and lease.
5. **ClickHouse probe** — parameterized read-only queries; DDL is allowed only in
   the production rebuild DAG.
6. **Airflow probe** — stable REST API, DAG/run/task state, and sanitized logs.

If the existing `LakehouseStatusMain` does not produce the required row-level
hashes, add a finite `StageVValidationMain` that accepts only the name of a
predefined report and output path. Do not add a universal `--sql`.

### 5.4 Canonical manifests

Each entity manifest contains:

- business primary key in stable tuple order;
- all contractual business columns;
- `is_deleted`;
- last transaction/event/Kafka position;
- canonical row hash;
- source layer and snapshot/run identifiers.

Value normalization:

- timestamps — UTC ISO-8601 with microseconds;
- decimals — fixed scale, without float conversion;
- strings — UTF-8 without trim/case conversion;
- `null` — JSON `null`;
- rows are sorted bytewise by canonical primary-key representation.

Comparison is performed by keys and every business column. Row counts or an
aggregate checksum alone do not replace a row-level diff. The final SHA-256 is a
compact reference to the already stored full manifest.

### 5.5 Harness tests

Unit tests must prove:

- prohibition on starting without the exact Compose project and `--confirm-reset`;
- redaction of secrets and URL credentials;
- bounded stdout/stderr;
- correct distinction between `FAIL`, `BLOCKED`, timeout, and unknown terminal state;
- inability to promote a failed result while generating a report;
- deterministic canonicalization decimal/timestamp/null/composite PK;
- detection of missing/extra keys, value mismatches, and duplicate `event_id`;
- prohibition on arbitrary SQL, service names, paths, and shell fragments;
- expected-count oracle validation;
- safe resumption of read-only probes and prohibition of unsafe mutating resume.

---

## 6. Deterministic oracle

### 6.1 Initial snapshot

| Entity | Initial applied changes | Initial visible current |
| --- | ---: | ---: |
| `customers` | 8 | 8 |
| `orders` | 12 | 12 |
| `order_items` | 16 | 16 |
| `order_payments` | 14 | 14 |
| `order_reviews` | 12 | 12 |
| `products` | 8 | 8 |
| `sellers` | 4 | 4 |
| `product_category_translation` | 5 | 5 |
| **Total** | **79** | **79** |

Additionally:

- `reference.geolocation = 6`;
- `rejected = 0` and `schema_violations = 0`;
- 79 distinct business `event_id`;
- all initial business events have snapshot operation `r`/`is_snapshot=true`;
- MySQL and Silver current match row by row.

### 6.2 CRUD delta

The semantics of `wave2_crud.sql` are used:

| Transaction | Operations | Business events |
| --- | --- | ---: |
| INSERT | customer 1, order 1, items 2, payments 2, review 1 | 7 |
| UPDATE | order status 1, item price 1 | 2 |
| DELETE | review 1 | 1 |
| **Total** |  | **10** |

After CRUD and caught-up:

| Entity | Applied changes total | Visible current | Physical current | Deleted current |
| --- | ---: | ---: | ---: | ---: |
| `customers` | 9 | 9 | 9 | 0 |
| `orders` | 14 | 13 | 13 | 0 |
| `order_items` | 19 | 18 | 18 | 0 |
| `order_payments` | 16 | 16 | 16 | 0 |
| `order_reviews` | 14 | 12 | 13 | 1 |
| `products` | 8 | 8 | 8 | 0 |
| `sellers` | 4 | 4 | 4 | 0 |
| `product_category_translation` | 5 | 5 | 5 | 0 |
| **Total** | **89** | **85** | **86** | **1** |

Expected operation breakdown: `r=79`, `c=7`, `u=2`, `d=1`.

Delete acceptance:

- changes contains one `d` envelope for `wave2_review_001`;
- current contains one latest soft-delete version;
- stable current does not return the deleted review;
- Bronze contains the subsequent tombstone for the same key;
- the tombstone does not create a second changes/current row;
- the tombstone offset is included in `silver_progress`.

### 6.3 Exact value assertions

- `wave2_order_001.order_status = 'approved'`;
- `wave2_order_001.order_approved_at = 2018-09-01T10:05:00.123456`;
- item `(wave2_order_001, 2).price = 19.99`;
- item `(wave2_order_001, 1).price = 10.00`;
- two payments have values `12.50` and `23.50`;
- `wave2_review_001` is absent from visible current;
- all other initial rows are bytewise equivalent to the fixture oracle.

### 6.4 Insufficient oracle substitutes

The following are not sufficient evidence:

- only `status: ready`;
- only totals 79/89/85;
- `SELECT count(*)` without distinct keys and a row-level manifest;
- one aggregate checksum without the saved canonical input;
- dbt `PASS` without publication-boundary checks;
- a Kafka tombstone without proof of progress and absence of a second business row;
- a successful rebuild without prohibiting source-system reads and comparing manifests.

---

## 7. Detailed execution order

### V0 — Entry gate and Stage E reconciliation

#### Actions

1. Record the commit SHA, branch, `git status --porcelain`, and versions.
2. Check the SHA-256 values of the small fixture, source profile, and CRUD fixture.
3. Run `pre-commit run --all-files`.
4. Run `uv lock --check`.
5. Run the relevant Python suites:
   `tests/cdc_contracts`, `tests/lakehouse_platform`, `tests/mysql`,
   `tests/dbt_clickhouse`, `tests/serving`, and `tests/stage_v`.
6. In `streaming/spark/scala`, run:
   `sbt scalafmtCheckAll scalafmtSbtCheck Test/compile test package`.
7. Check Compose config for profiles `platform`, `streaming`, `serving`, and
   `observability`.
8. Check Airflow DAG imports and dbt parse/selector boundaries.
9. Perform the code/contract audit from section 3.2.
10. Run `git diff --check` after all automated hooks.

#### Stop/go

- Any failed check blocks V2.
- An auto-fix hook means V0 restarts from the beginning.
- A production gap from section 3.2 produces `BLOCKED_BY_E_REGRESSION` even if
  lint/tests are green.
- `GO` is possible only with complete machine-readable V0 evidence.

### V1 — Validation-harness readiness

#### Actions

1. Implement the files and adapters from section 5.
2. Split the CRUD fixture into three transaction files or prove safe statement
   boundaries in the existing file.
3. Prepare canonical queries and expected manifests.
4. Prepare the nullable schema fixture from V8.
5. Run negative harness tests without starting the runtime.
6. Verify that `prepare` did not create/change Docker resources.
7. Freeze the implementation commit for the acceptance run.

#### Stop/go

- The harness cannot declare a gate `PASS` without the required evidence file.
- SQL/path/service allowlists and redaction tests are mandatory.
- Run V0 again after changing the harness.

### V2 — Clean domain and seed (original step 1)

#### Actions

1. Check exact `COMPOSE_PROJECT_NAME=olist_stage_v`.
2. Save the pre-reset Compose inventory; do not touch other projects.
3. Run `local_lab.py reset --yes`.
4. Prove that no volumes/containers remain for the current project.
5. Run bootstrap with:
   `--run-id <stage-v-id>_seed --random-seed 20260801`.
6. Save the bootstrap JSON and MySQL row-level manifest.
7. Verify that serving/streaming profiles were not started prematurely after
   bootstrap when required by the lifecycle contract.

#### Assertions

- Seed counts match the source profile: 79 business + 6 geolocation.
- The Debezium connector is created only after seed.
- There are no bootstrap, schema-capture, or contract-generation errors.
- Evidence/logs contain no secrets.

### V3 — Initial snapshot and Silver baseline (original steps 2–4)

#### Actions

1. Run `start-streaming`.
2. Record container IDs, start timestamps, checkpoint inventory, and Kafka
   beginning/end offsets.
3. Run `wait-caught-up --timeout 1200`.
4. Wait for two consecutive READY observations with unchanged source end offsets
   and Silver progress.
5. Capture MySQL, Bronze, Silver changes/current, audit, and reference manifests.
6. Perform the initial row-level diff.

#### Assertions

- The table in section 6.1 matches completely.
- The eight entity queries and service Silver queries are READY.
- Snapshot is complete for every entity; a partial snapshot is not accepted.
- `event_id` duplicate/collision count is zero.
- `normalization_errors` and `schema_violations` are empty.
- Geolocation contains exactly six correct rows and is not mixed with CDC entities.

### V4 — Transactional CRUD, tombstone, and controlled restart (steps 5–8)

#### Actions

1. Save baseline Kafka offsets, Iceberg snapshot IDs, and checkpoint hashes.
2. Stop `spark-bronze` and `spark-silver` with one scoped Compose command,
   without removing containers or volumes.
3. Verify that Kafka Connect remains RUNNING.
4. Run the INSERT fixture in one MySQL transaction and record the commit ID.
5. Run the UPDATE fixture in one transaction.
6. Run the DELETE fixture in one transaction.
7. Confirm Kafka end offsets increase and backlog exists while Spark is stopped.
8. Start Bronze and Silver with one Compose command; this is the restart barrier.
9. Record new container IDs/start timestamps and the previous checkpoint inventory.
10. Do not rerun SQL fixtures in this run.

#### Assertions

- MySQL commits: exactly three, with no autocommit between fixture statements.
- Business event counts by transaction: 7, 2, and 1.
- Delete connector config retains `tombstones.on.delete=true`.
- Both Spark services actually completed stop/start.
- Kafka, MySQL, Polaris, MinIO, and checkpoints were not restarted/cleared.
- Backlog existed before restart, so the drill checks recovery, not only process liveness.

### V5 — Catch-up, replay safety, and CRUD oracle (original step 9)

#### Actions

1. Run `wait-caught-up --timeout 1200`.
2. Wait for two stable READY observations.
3. Capture manifests and transaction/progress reports.
4. Compare with sections 6.2–6.3.
5. Perform a second read-only caught-up observation without new source writes.
6. Compare Iceberg snapshots/row counts between the two observations.

#### Assertions

- The three transactions are `COMPLETE`; `OPEN`/`REJECTED` are absent.
- `changes=89`, distinct `event_id=89`, duplicate count `0`.
- Visible/physical/deleted current totals: `85/86/1`.
- One tombstone is counted only in Bronze/progress.
- Exact values from 6.3 match.
- Reprocessing the checkpoint adds no changes rows and does not change applied business state.
- No query is in `FATAL`.

### V6 — Transaction-complete serving sync (original step 10)

#### Actions

1. Save pre-sync public-view manifests and control state.
2. Run
   `sync-serving --run-id <stage-v-id>_crud_publish --timeout 1800`.
3. Obtain the authoritative result through the serving report API/helper.
4. Capture PostgreSQL run/entity results/runtime cursor.
5. Capture the ClickHouse marker/candidate partitions.
6. Capture the Iceberg serving report.
7. Build the cross-system publication tuple.

#### Required publication tuple

```text
(sync_run_seq,
 sync_run_id,
 previous_transaction_id,
 target_transaction_id,
 target_offsets,
 source_snapshot_ids,
 expected_event_count,
 materialized_event_count,
 event_checksum,
 published_at)
```

#### Assertions

- Sync terminal status is `SUCCEEDED`, not a silent skip.
- The target boundary ends with the DELETE transaction and does not include OPEN data.
- `expected_event_count = materialized_event_count = 89` for the complete initial +
  CRUD event ledger.
- Per-entity counts match the applied changes in section 6.2.
- The tuple is identical in PostgreSQL, the ClickHouse marker, and the Iceberg report.
- One published seq is visible as a whole; no entity is partially published.
- No unpublished/stale candidate partitions exist.
- The first publication activated only the intended schedules.

If the production contract counts the initial snapshot separately from the event
ledger, the agent must not change the expected number arbitrarily: record the
contract formula, compare it with the frozen boundary, and preserve the complete
list of selected `event_id` values. The absence of such an unambiguous formula is
`BLOCKED_BY_E_CONTRACT_GAP`.

### V7 — dbt build and stable ClickHouse interfaces (steps 11–12)

#### Actions

1. From Airflow evidence, obtain the exact dbt command, vars, and selector run within sync.
2. Confirm that it is a `dbt build` candidate graph, not only `dbt run`.
3. Save `PASS/WARN/ERROR/SKIP` totals and the node/test list.
4. Perform a row-level diff from Silver current to ClickHouse stable current.
5. Check `FINAL` on version tables and public stable views without `FINAL`.
6. Check the eight `gold.*` interfaces and dbt business tests.
7. Check that public views contain no rows from another/unpublished `sync_run_seq`.

#### Assertions

- dbt `ERROR=0`, `SKIP=0`; warnings are allowed only from a pre-recorded
  allowlist, with `WARN=0` by default.
- All eight Gold models and their tests run with a positive published seq and
  non-empty run ID.
- `serving_cdc.*_current` matches Silver visible current: 85 rows and exact
  key/value parity.
- `fact_order_items` has grain `(order_id, order_item_id)` without duplicates and
  contains 18 visible items.
- SCD2 windows do not overlap; exactly one current version exists per business key.
- Payment allocations are balanced; daily/monthly mart formulas pass tests.
- Repeated queries of the stable view before/after `OPTIMIZE ... FINAL` return one
  logical result.

### V8 — Additive nullable schema evolution (original step 13)

#### Test change

Use one validation-only source column in `customers`:

```sql
ALTER TABLE olist_oltp.customers
ADD COLUMN stage_v_optional_note VARCHAR(64) NULL DEFAULT NULL;
```

Then update an existing row by changing one real business column while leaving
the new column `NULL`, so Debezium definitely emits a data event with the new
writer schema:

```sql
UPDATE olist_oltp.customers
SET customer_city = 'sao paulo stage v',
    stage_v_optional_note = NULL
WHERE customer_id = 'wave2_customer_001';
```

The column checks source/writer compatibility and does not become a new public
Gold field. If the active contract requires an explicit reader-contract version
and allowlisted writer fingerprint, prepare that version and review it before the
clean acceptance run. Do not dynamically allow an unknown fingerprint during the run.

#### Actions

1. Before V2, check the migration fixture, nullable/default contract, and expected
   schema fingerprint transition.
2. At V8, apply only the allowlisted `ALTER`.
3. Wait for registration/archiving of the new writer schema.
4. Run one allowlisted UPDATE transaction.
5. Wait for caught-up and capture schema/changes/current/audit evidence.
6. Run a second serving sync with run ID `<stage-v-id>_schema_publish`.
7. Repeat dbt/stable-view checks for the new published seq.

#### Assertions

 - Registry accepts the new schema under `BACKWARD_TRANSITIVE`.
- The new writer schema ID/fingerprint is archived and unambiguously linked to
  `customers`.
- The new column is nullable with default `null`; existing fields/PK are unchanged.
- The event is applied, and `stage_v_optional_note` is decoded as `null` or safely
  ignored by the reader contract according to the pre-approved decision.
- `normalization_errors=0`, `schema_violations=0`, and the query does not enter `FATAL`.
- Customers changes increase from 9 to 10; total applied changes increase from 89 to 90.
- Current row counts do not change; the city in the newest version equals
  `sao paulo stage v`.
- The second serving candidate contains exactly one new business event; the
  published event ledger contains 90 distinct `event_id` values and all stable
  views switch under one marker.
- The old 79 snapshot events, CRUD events, and rows with the previous writer
  schema remain readable.

If the nullable change requires a production repair, the current run ends
`FAIL_SCHEMA_EVOLUTION`. Apply the fix and contract version separately, then
repeat full V2–V10 from a clean domain.

### V9 — Guarded ClickHouse rebuild from Iceberg only (original step 14)

#### Actions

1. Stop scheduled serving/quality triggers or obtain an operation lease without
   stopping Bronze/Silver.
2. Capture final pre-rebuild manifests for all stable current and Gold interfaces,
   marker/cursor/report, and their SHA-256 values.
3. Record MySQL counts, Kafka offsets, Iceberg snapshot IDs, and checkpoint inventory.
4. During rebuild, technically deny Airflow tasks access to MySQL/Kafka when this
   can be done with a scoped network/credential guard without changing source data.
   At minimum, prove from the DAG graph, process/network logs, and credentials that
   rebuild used only Iceberg/Polaris/MinIO and control metadata.
5. Run
   `rebuild-serving --yes --run-id <stage-v-id>_rebuild --timeout 5400`.
6. Capture post-rebuild manifests and publication metadata.
7. Perform the exact pre/post row-level diff.
8. Run `status --require serving` and `validate --scope serving`.

#### Assertions

- Rebuild would refuse to start without `--yes`/`confirm_destructive=true`.
- Only derived ClickHouse databases/partitions changed.
- MySQL counts, Kafka offsets, Iceberg snapshot IDs, and Spark checkpoint inventory
  did not change because of rebuild.
- Pre/post stable-current and Gold manifests match by keys and values.
- After rebuild: 90 distinct event rows, 85 visible current, 86 physical current,
  and one deleted key.
- Marker/cursor/report remain consistent; no dangling candidate partitions exist.
- dbt tests, serving status, and serving validation are green.
- Bronze/Silver continued running and were not restarted by Airflow.

### V10 — Final acceptance and report

#### Actions

1. Repeat read-only probes for all layers.
2. Check that no OPEN/REJECTED/stale candidate/active lease exists.
3. Run the final static smoke: `git diff --check`, contract checks, and a redaction
   scan of evidence/logs.
4. Build `checksums.json` and `summary.json`.
5. Verify that all V0–V10 belong to one run ID, commit, and Compose project.
6. Create `docs/reports/mysql-spark-iceberg-stage-v-validation.md`.
7. Do not change `serving-cutover.md` or begin Stage L in the same change.

#### Final verdict

`PASS` is allowed only if:

- all gates have `PASS`;
- there is no missing evidence or redaction violation;
- no assertion was downgraded/waived;
- the run passed V2–V10 without a production fix or new bootstrap;
- the report contains evidence hashes and the exact execution commit;
- after the report, the tracked worktree contains only the expected Markdown report.

---

## 8. Failure classification and agent actions

| Code | Example | Action |
| --- | --- | --- |
| `BLOCKED_BY_E_REGRESSION` | serving CLI/DAG does not implement the Stage E contract | Preserve evidence, stop V, and fix as a Stage E defect. |
| `BLOCKED_ENVIRONMENT` | Docker/WSL resource failure before data mutation | Preserve diagnostics; after repairing the environment, start a new clean run. |
| `BLOCKED_UNKNOWN_STATE` | mutating-operation timeout without authoritative terminal state | Do not retry on the same volumes; investigate read-only. |
| `FAIL_DATA_LOSS` | missing key/event or offset gap | Stop the run; no serving publish/rebuild. |
| `FAIL_DUPLICATE` | duplicate/colliding `event_id` | Stop the run; preserve conflicting metadata without payload secrets. |
| `FAIL_TRANSACTION_BOUNDARY` | OPEN/partial transaction was published | Stop the run; Stage L is forbidden. |
| `FAIL_RESTART_RECOVERY` | checkpoint reset or replay changed state | Stop the run; preserve before/after checkpoint evidence. |
| `FAIL_SERVING_ATOMICITY` | marker/cursor/report diverge | Stop publish/rebuild; follow the recovery contract. |
| `FAIL_DBT_QUALITY` | dbt error, skip, or business-test failure | Preserve target artifacts/logs; Stage L is forbidden. |
| `FAIL_SCHEMA_EVOLUTION` | compatible nullable schema stopped an entity | Fix the contract/runtime separately and repeat the full run. |
| `FAIL_REBUILD_PARITY` | post-rebuild manifest differs | Do not restore manually from MySQL/Kafka; investigate Iceberg/rebuild. |
| `FAIL_EVIDENCE` | required raw/canonical artifact is missing | The result cannot be `PASS`, even if the runtime appears healthy. |

The agent must tell the user the first violated gate, diagnostic code, expected and
actual value, path to sanitized evidence, and the safe next step. Do not continue
the remaining mutating gates merely to accumulate more errors.

---

## 9. Stage V validation report requirements

The report is created only from `summary.json` and verified raw evidence. It contains:

1. verdict `PASS|FAIL|BLOCKED`, date, and execution commit;
2. dirty-state statement and Compose project;
3. pinned component versions;
4. fixture/oracle/evidence SHA-256;
5. V0 static/build/test totals;
6. clean reset/bootstrap proof;
7. initial per-entity 79/79/0 and geolocation 6;
8. CRUD transaction IDs, counts 7/2/1, and tombstone proof;
9. restart timestamps, container IDs, and checkpoint continuity proof;
10. post-CRUD 89 changes / 85 visible / 86 physical / 1 deleted;
11. duplicate/collision counts and row-level parity summary;
12. publication tuple and PG/CH/Iceberg equality;
13. dbt command, vars, selector, node/test totals;
14. stable current/Gold manifests and business assertions;
15. nullable schema old/new IDs/fingerprints, event proof, and 90-event total;
16. rebuild isolation proof and exact pre/post manifest hashes;
17. final `status --require serving` and `validate --scope serving` JSON;
18. redaction result, known limitations, and unresolved blockers;
19. explicit decision: `Stage L is authorized` only with `PASS`.

UI screenshots are not evidence by themselves; they are allowed only as a supplement
to API, JSON, SQL results, and logs.

---

## 10. Traceability matrix for the original 14 steps

| Original `serving-cutover.md` step | Gate in this plan | Primary evidence |
| --- | --- | --- |
| 1. Seed | V2 | Fixture hash, MySQL manifest 79+6 |
| 2. Debezium initial snapshot | V3 | Snapshot completion, offsets, 79 events |
| 3. Silver current 79 | V3 | Per-entity row-level manifest |
| 4. Geolocation 6 | V3 | Reference manifest |
| 5. Multi-table create | V4 | COMPLETE transaction, 7 events |
| 6. Update | V4-V5 | COMPLETE transaction, 2 events, exact values |
| 7. Delete+tombstone | V4-V5 | 1 delete, 1 tombstone, progress coverage |
| 8. Restart Bronze/Silver | V4 | Stop/start evidence and checkpoint continuity |
| 9. Caught-up/no duplicates | V5 | Stable progress, 89 distinct IDs |
| 10. `sync-serving` | V6 | Publication tuple equality |
| 11. `dbt build` | V7 | Command/vars/selector and test totals |
| 12. `FINAL`/`gold` | V7 | Stable manifests and dbt assertions |
| 13. Nullable additive schema | V8 | Schema IDs/fingerprints, null event, 90 IDs |
| 14. `rebuild-serving` | V9 | Source isolation and exact pre/post parity |

---

## 11. Definition of Done

- [x] V0 confirmed a fresh green Stage E entry gate.
- [x] The validation harness has allowlists, redaction, and unit tests.
- [x] One clean-domain run is tied to one commit and Compose project.
- [x] Initial snapshot: 79 applied/current, 0 rejected, 6 geolocation.
- [x] CRUD produced exactly 7 create, 2 update, and 1 delete events.
- [x] The tombstone exists, is included in progress, and created no business duplicate.
- [x] Bronze/Silver restarted while preserving checkpoints.
- [x] After catch-up: 89 distinct changes, 85 visible current, 1 deleted.
- [x] MySQL and Silver match row by row for business keys/values.
- [x] The serving publication tuple is identical in PG/CH/Iceberg.
- [x] The candidate was published atomically for all eight entities.
- [x] dbt candidate build and all tests passed without errors/skips.
- [x] Stable current and Gold do not see unpublished rows.
- [x] Nullable schema was registered, archived, and processed without errors.
- [x] After the schema event, 90 distinct applied events exist.
- [x] Rebuild used Iceberg as the only data source.
- [x] Pre/post rebuild manifests match row by row.
- [x] Final serving status/validate are ready and evidence redaction is clean.
- [x] The validation report was created with status `PASS` and evidence hashes.
- [x] Legacy was not removed; final parity was not run.
- [x] Stage L is explicitly authorized only after `PASS`.

---

## 12. Related documents

- [Operational cutover E -> V -> L -> F](../active/serving-cutover.md)
- [Detailed Stage E plan](stage-e-serving-integration.md)
- [Stage E report](../../../reports/mysql-spark-iceberg-stage-e-validation.md)
- [Spark Structured Streaming contract](../contracts/spark-streaming.md)
- [Iceberg data model contract](../contracts/iceberg-data-model.md)
- [Serving and recovery contract](../contracts/serving-and-recovery.md)
- [Validation and CI contract](../contracts/validation-and-ci.md)
- [MySQL, Kafka and Avro contract](../contracts/mysql-kafka-avro.md)
- [Serving sync runbook](../../../runbooks/lakehouse-serving-sync.md)
- [ClickHouse rebuild runbook](../../../runbooks/lakehouse-clickhouse-rebuild.md)
