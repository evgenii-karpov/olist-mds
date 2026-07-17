# Batch-to-Realtime CDC Parity Integration Test Plan

## Document Control

| Field            | Value                                                                  |
| ---------------- | ---------------------------------------------------------------------- |
| Status           | Implemented                                           |
| Last updated     | 2026-07-17                                                             |
| Repository       | `olist-mds`                                                            |
| Primary audience | AI implementation agents and maintainers                               |
| Parent plan      | `docs/plans/near-realtime-cdc-implementation-plan.md`                  |
| Test dataset     | `tests/fixtures/olist_small/olist_small.zip`                           |
| CI strategy      | Full test nightly and on demand; fast contract checks on pull requests |

## 1. Purpose

Add a deterministic integration test proving that the same Olist source data
produces equivalent analytical results when loaded through:

1. the existing batch pipeline; and
2. the local near-realtime CDC pipeline using a Debezium initial snapshot.

The full path under test is:

```text
                                      +-> batch ingestion -> batch dbt models --------+
olist_small.zip ----------------------+                                             |
                                      +-> simulator seed -> OLTP PostgreSQL           |
                                                            -> Debezium               |
                                                            -> Kafka                  +-> parity
                                                            -> NiFi                   |
                                                            -> MinIO                  |
                                                            -> Airflow CDC ingest     |
                                                            -> realtime dbt models ---+
```

The test must use both the project's existing parity audit models and the
standard `dbt_utils.equality` data test. The two mechanisms are complementary:

- the existing models remain the authoritative, publication-aware diagnostic
  contract and identify failed metrics and business-grain keys;
- `dbt_utils.equality` demonstrates a standard dbt package comparison and
  provides an independent relation-equality assertion.

This plan is self-contained. An implementation agent must not need the
conversation that produced it.

## 2. Current Repository Baseline

The implementation must build on the following existing behavior:

- The local batch DAG is
  `airflow/dags/olist_modern_data_stack_local.py`.
- The committed small fixture is
  `tests/fixtures/olist_small/olist_small.zip`, with its matching source profile
  at `tests/fixtures/olist_small/source_profile_small.json`.
- `scripts/ci/check_fixture_pipeline_idempotency.py` already runs the batch DAG
  on the small fixture and validates replay stability.
- `scripts/simulation/` provides `seed`, `run`, `replay`, `status`, and `stop`.
  Its `seed` command loads an Olist archive into the OLTP database in
  foreign-key-safe order.
- The CDC capture set contains eight business tables:
  `customers`, `orders`, `order_items`, `order_payments`, `order_reviews`,
  `products`, `sellers`, and `product_category_translation`.
- `geolocation` is intentionally excluded from the first CDC release.
- The complete local CDC path already exists:
  OLTP PostgreSQL, Debezium, Kafka, Apicurio, NiFi, MinIO, warehouse ingestion,
  Airflow, and realtime dbt models.
- The CDC DAGs are `olist_cdc_ingest_local`,
  `olist_cdc_transform_local`, `olist_cdc_backfill_local`, and
  `olist_cdc_quality_local`.
- A successful ingest that inserts new raw events emits
  `olist://cdc/raw/local`; this Asset triggers the transform DAG.
- NiFi closes small bins after 45 seconds in the current local parameter
  context.
- The only consumer-facing marts are:
  `mart_daily_revenue` and `mart_monthly_arpu`, with realtime equivalents
  suffixed by `_realtime`.
- Existing parity resources are:
  `realtime_parity_report`, `realtime_parity_checksums`,
  `realtime_parity_grain_diffs`, and
  `assert_realtime_parity_passed`.
- `scripts/cdc/realtime_transform.py record-parity` builds the
  `realtime_parity` selector and records the result in
  `cdc_audit.cdc_publication_state`.
- Only resources under `models/parity` may bridge batch and realtime model
  groups.
- `dbt_utils` version `1.3.3` currently appears in `package-lock.yml` as a
  transitive dependency of Elementary, but it is not declared directly in
  `packages.yml`.
- The Stage 5 integration test injects synthetic events directly into
  `raw_cdc`. It proves realtime ordering, history, incremental rebuild, delete,
  and publication behavior, but it does not exercise Debezium, Kafka, NiFi, or
  MinIO and therefore is not the parity test defined here.

## 3. Decision and Scope

### 3.1 Use the Debezium initial snapshot only

The parity test must:

1. load `olist_small.zip` through the batch pipeline;
2. seed the OLTP database from that exact same archive;
3. register Debezium only after seeding; and
4. compare the resulting batch and realtime analytical state.

Do not run the simulator's `run` or `replay` commands in this test. Those
commands create new synthetic entity identifiers and lifecycle changes that do
not exist in the batch archive. Including them would compare different source
states unless a separate OLTP-to-batch export contract were designed. That is
outside this plan.

The `seed` implementation is suitable for this test because it reads the same
archive format as the batch pipeline, validates headers, converts source types,
loads in foreign-key-safe order, and is already covered by simulator unit and
integration tests.

### 3.2 CI cadence

The complete test must run:

- nightly on GitHub Actions; and
- through `workflow_dispatch`.

It must not be a required pull-request gate. Starting the full Compose stack,
waiting for the Debezium snapshot, allowing NiFi bins to close, and running
Airflow/dbt makes it materially slower and more susceptible to infrastructure
timing than the existing bounded PR jobs.

Pull requests must still run fast static, unit, compilation, selector-boundary,
and comparator-sensitivity checks defined later in this plan.

### 3.3 In scope

- One clean, local PostgreSQL-based execution using the small fixture.
- The real batch Airflow DAG.
- The real Debezium, Kafka, NiFi, MinIO, warehouse-ingest, Airflow Asset, and
  realtime dbt path.
- Complete comparison of both marts.
- Business-column comparison of the item-grain fact.
- Business-column comparison of all eight captured current-state source
  projections.
- Existing count, checksum, aggregate, and grain-difference reports.
- Additional `dbt_utils.equality` assertions for the two marts.
- Machine-readable results and bounded failure diagnostics.

### 3.4 Out of scope

- The full `olist.zip`.
- Synthetic `run` or `replay` workload parity.
- CRUD, hard-delete, recovery, replay, schema-evolution, benchmark, burst, or
  soak testing; those remain covered by their existing dedicated tests and
  Phase 6 operational gates.
- AWS or Redshift execution.
- `geolocation` parity.
- Exact equality of batch and realtime SCD2 history tables.
- A latency-SLO claim. Passing this test does not prove the five-minute p95 SLO.
- Publishing the realtime marts to `analytics`; parity recording is sufficient.

## 4. Comparison Contract

### 4.1 Archive identity

Before either load begins, calculate SHA-256 for the fixture archive. Record the
same digest as the source identity for both branches in the final test report.
Fail before comparison if the two branches are configured with different
archive paths or identities.

The source profile must be validated before either load. The batch and CDC
branches must use the same committed archive without extracting, filtering, or
regenerating it differently for either path.

### 4.2 Current-state source parity

Compare every business column for all eight captured tables. Exclude batch load
metadata and CDC transport metadata.

| Source entity                | Business key                     |
| ---------------------------- | -------------------------------- |
| customers                    | `customer_id`                    |
| orders                       | `order_id`                       |
| order_items                  | `(order_id, order_item_id)`      |
| order_payments               | `(order_id, payment_sequential)` |
| order_reviews                | `(review_id, order_id)`          |
| products                     | `product_id`                     |
| sellers                      | `seller_id`                      |
| product_category_translation | `product_category_name`          |

The comparison must normalize semantically equivalent PostgreSQL types where
the two staging paths expose different timestamp timezone or numeric scale
representations. It must not normalize case, trim strings, replace nulls, or
otherwise hide a source-value difference.

Keep the existing primary-key checksums as a fast diagnostic, but do not treat a
checksum match as sufficient. Attribute comparison is authoritative.

### 4.3 Fact parity

Compare `core.fact_order_items` with
`realtime_core.fact_order_items_realtime` at
`(order_id, order_item_id)` grain.

Compare business identifiers and measures, including:

- `customer_id`;
- `product_id`;
- `seller_id`;
- `order_status`;
- order purchase date;
- `price`;
- `freight_value`;
- gross item amount; and
- allocated payment value.

Do not compare pipeline-specific surrogate keys, snapshot identifiers,
validity timestamps, load timestamps, or CDC ordering columns.

### 4.4 Mart parity

Compare every published column in both mart pairs:

- `marts.mart_daily_revenue` against
  `realtime_marts.mart_daily_revenue_realtime`, keyed by
  `order_purchase_date`;
- `marts.mart_monthly_arpu` against
  `realtime_marts.mart_monthly_arpu_realtime`, keyed by `order_month`.

The existing custom grain-difference model must continue to show the mart name
and grain key for each mismatch. Dates and integer counts must compare exactly.
Existing model output for monetary and ratio values must compare exactly in the
custom grain-level report. The existing aggregate report may retain its
documented `0.01` monetary tolerance.

The `dbt_utils.equality` assertions must compare normalized parity projections
with numeric `precision: 2`. Both the custom comparison and dbt-utils tests must
pass; the less strict dbt-utils precision must never override a custom failure.

### 4.5 SCD2 boundary

Do not compare the complete batch and realtime customer/product SCD2 histories.
The batch path generates correction feeds and uses dbt snapshots, while the CDC
initial snapshot contains only the seeded OLTP state. Their technical validity
windows and surrogate keys are intentionally different.

Compare the source current attributes that feed those dimensions and the
business identifiers/measures produced by the fact and marts. This proves
analytical equivalence without asserting that two different history mechanisms
have identical technical records.

## 5. dbt Implementation

### 5.1 Direct dbt-utils dependency

Add `dbt-labs/dbt_utils` version `1.3.3` as a direct dependency in
`dbt/olist_analytics/packages.yml`. Regenerate `package-lock.yml` through
`dbt deps`. Pin the existing resolved version rather than relying on
Elementary's transitive dependency.

### 5.2 Existing custom parity resources

Retain the existing parity resource names and the
`realtime_parity` selector. Extend the custom parity models so that:

- every captured current-state business column is compared;
- fact comparison uses the business projection defined in section 4.3;
- both marts compare every published column at their natural grains;
- failures retain `metric_name` and `grain_key`;
- the existing report and checksum output schemas remain compatible with
  `realtime_transform.py record-parity`;
- `assert_realtime_parity_passed` still fails when any report, checksum, or
  grain difference fails.

Do not move cross-boundary references out of `models/parity`.

### 5.3 dbt-utils projection pairs

Create four lightweight views under `models/parity`:

- normalized batch daily revenue;
- normalized realtime daily revenue;
- normalized batch monthly ARPU; and
- normalized realtime monthly ARPU.

Each pair must expose the same column names, order, and PostgreSQL data types.
The projections may cast date/timestamp and numeric types, but must not filter
rows or change business values.

Attach one `dbt_utils.equality` generic data test to each batch projection with:

- the corresponding realtime projection as `compare_model`;
- an explicit `compare_columns` list containing every mart column;
- `precision: 2`; and
- tag `realtime_parity`.

Give the tests stable names that identify the mart and comparison method, for
example:

- `dbt_utils_equality_daily_revenue`;
- `dbt_utils_equality_monthly_arpu`.

Update the selector-boundary validator to allow these two tests and the four
parity views while continuing to reject any non-parity model or unrelated test.

### 5.4 Parity status behavior

`record-parity` must report the outcomes of the custom and dbt-utils mechanisms
separately. It must record overall `PASS` only when both mechanisms pass.

On failure:

- overall publication parity status must become `FAIL`, not remain `PENDING`;
- the command must return a non-zero exit code after recording the failure;
- its JSON output must include custom failed-metric count and the names of
  failed dbt-utils tests;
- no realtime publication switch may occur.

Preserve the existing successful response fields where possible and add fields
rather than renaming them.

## 6. Integration Test Orchestrator

Add:

```text
scripts/ci/check_batch_cdc_parity_integration.py
```

### 6.1 Command-line interface

The script must support:

```text
--archive
--profile
--timeout-seconds
--poll-seconds
--report
```

Defaults:

```text
--archive tests/fixtures/olist_small/olist_small.zip
--profile tests/fixtures/olist_small/source_profile_small.json
--timeout-seconds 1200
--poll-seconds 2
--report data/reports/batch-cdc-parity.json
```

The script must assume that the required Compose services are already built and
started. It must not run `docker compose down`, delete volumes, or delete
arbitrary local paths. The owning CI workflow is responsible for disposable
environment lifecycle.

### 6.2 Execution sequence

The orchestrator must perform these steps in order:

1. Validate the archive/profile source contract and calculate archive SHA-256.
2. Verify that required Compose services and bootstrap containers are healthy
   or successfully completed.
3. Verify Airflow DAG imports and registration.
4. Run the batch DAG once with the fixture, `full_refresh=true`, the existing
   fixture batch date, and an isolated raw directory.
5. Wait for batch DAG success and verify its existing reconciliation result.
6. Configure Apicurio compatibility and validate the topic inventory.
7. Run `python -m scripts.simulation seed` with the same archive and a fixed
   seed/run ID.
8. Register the Debezium connector only after seed completion.
9. Wait for the connector and task to be `RUNNING`.
10. Wait until the initial snapshot has produced closed normalized and coverage
    manifests for all eight captured tables.
11. Verify that the NiFi consumer group lag reaches zero and that NiFi queues
    drain without processor errors.
12. Unpause the transform DAG before triggering ingest.
13. Trigger one `olist_cdc_ingest_local` run and wait for success.
14. Identify and wait for the Asset-triggered `olist_cdc_transform_local` run;
    do not trigger the transform directly.
15. Verify ingest/transform audit state, reconciliation, offset continuity,
    duplicate handling, DLQ state, and expected current row counts.
16. Run `realtime_transform.py record-parity`.
17. Read both custom parity relations and dbt-utils test results.
18. Write the final JSON report and return success only when every acceptance
    condition passes.

Refactor reusable, non-Airflow-specific helpers from
`check_fixture_pipeline_idempotency.py` rather than copying its DAG polling and
relation fingerprint logic. Preserve the existing script's default two-run
idempotency behavior. If it gains a single-run option for reuse, that option
must be additive and its original defaults must remain unchanged.

### 6.3 Observable waits

Do not use a fixed sleep as evidence of completion. Poll explicit conditions:

- Compose service health;
- connector/task state;
- expected normalized and coverage manifests;
- Kafka consumer lag;
- NiFi queue and processor state;
- Airflow DAG run state;
- warehouse audit status; and
- expected raw/current row counts.

A short poll interval is acceptable. Every wait must share the command's
overall deadline or use a bounded sub-deadline. Timeout errors must identify the
condition that remained unmet and include the last observed value.

### 6.4 Result format

The JSON report must contain:

- test status and timing;
- archive path and SHA-256;
- batch and CDC run identifiers;
- connector and Airflow terminal states;
- per-source batch/current row counts;
- ingest and transform audit summaries;
- gap, duplicate, rejected, quarantine, and DLQ counts;
- custom report/checksum/grain-difference results;
- each dbt-utils test status;
- overall parity status; and
- bounded failure details.

Do not include passwords, connection strings containing credentials, secret
file contents, or unbounded component logs.

## 7. CI Integration

Add a dedicated GitHub Actions workflow, or a clearly isolated job in the
existing operational workflow, with:

- nightly schedule;
- `workflow_dispatch`;
- job timeout of 30 minutes;
- `UV_CACHE_DIR` in the workspace;
- fixed fixture archive/profile inputs; and
- `OLIST_AIRFLOW_RETRIES=0` for deterministic failure behavior.

The job must:

1. check out the repository;
2. install Python and locked runtime dependencies;
3. prepare writable mounted Airflow/dbt/data directories;
4. build `airflow`, `kafka-connect`, `minio`, and `nifi`;
5. copy the example local dbt profile and run `dbt deps`;
6. start a clean stack with the `batch` and `realtime-core` profiles;
7. run the parity integration orchestrator;
8. upload the JSON report on success or failure;
9. print bounded logs for Airflow, Connect, NiFi, MinIO, and both PostgreSQL
   services on failure; and
10. always run `docker compose down -v --remove-orphans`.

Do not start the observability or logs profiles for this test. Their behavior is
covered separately and they add resource cost without contributing to parity.

## 8. Pull-Request Test Coverage

The following remain required on pull requests:

- Python lint, format check, typing, and unit tests;
- dbt dependency resolution, parse, and compile;
- dbt selector-boundary validation;
- Airflow import checks;
- existing batch fixture idempotency test;
- existing Stage 1 through Stage 6 bounded tests.

Add focused unit tests for:

- archive identity mismatch rejection;
- parsing connector and Airflow states;
- polling success and timeout behavior;
- missing table manifest detection;
- non-zero Kafka lag handling;
- failed Asset-triggered transform detection;
- secret redaction in the JSON report; and
- aggregation of custom and dbt-utils results into overall status.

Add a comparator-sensitivity test in the disposable Stage 5 database:

1. create matching batch and realtime mart rows;
2. prove both custom parity and dbt-utils equality pass;
3. change one realtime mart metric;
4. prove the custom comparator returns the expected grain key;
5. prove the corresponding dbt-utils equality test fails;
6. prove overall parity status becomes `FAIL`; and
7. restore or discard the disposable database.

The negative test must not mutate a shared developer warehouse.

## 9. Acceptance Criteria

Implementation is complete only when all of the following are true:

- Batch and CDC branches record the same fixture SHA-256.
- The source profile validation passes before either load.
- The batch branch completes through the real batch Airflow DAG.
- The CDC branch completes through OLTP PostgreSQL, Debezium, Kafka, NiFi,
  MinIO, Airflow ingest, the Asset-triggered transform, and realtime dbt models.
- All eight captured current-state business projections match.
- The item-grain business fact projection matches.
- Every row and published column of both marts matches.
- Existing custom parity reports contain no failed metric, checksum, or grain
  difference.
- Both `dbt_utils.equality` tests pass.
- Warehouse reconciliation passes with zero unexplained offset gaps, rejected
  records, quarantined records, or open DLQ records.
- A deliberate mart mutation is detected by both comparison mechanisms.
- A parity failure is durably recorded as `FAIL` and cannot authorize realtime
  publication.
- Existing batch fixture, Stage 2 through Stage 6, Airflow import, and selector
  boundary tests continue to pass.
- The nightly/manual workflow always publishes a bounded report and cleans up
  disposable volumes.

## 10. Risks and Mitigations

| Risk                                                        | Mitigation                                                                                                 |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Full-stack test is slow or timing-sensitive                 | Keep it nightly/manual and poll observable state with bounded deadlines                                    |
| NiFi small bins are not closed when ingest starts           | Wait for normalized and coverage manifests, not elapsed time                                               |
| Airflow scheduled timing makes the test nondeterministic    | Trigger ingest explicitly after manifests close, while preserving the Asset-triggered transform            |
| Simulator workload produces data absent from batch          | Use `seed` only; exclude `run` and `replay`                                                                |
| SCD implementations create legitimate technical differences | Compare current business attributes and downstream business facts, not technical history rows              |
| dbt-utils is removed by a transitive package change         | Declare and lock it as a direct dependency                                                                 |
| Two parity mechanisms disagree                              | Require both to pass and report them independently; custom publication-aware failure remains authoritative |
| Checksums conceal attribute differences                     | Retain checksums only as diagnostics and add full business-column comparisons                              |
| Test failure leaves local state behind                      | CI owns a disposable stack and always executes `down -v --remove-orphans`                                  |
| Failure logs expose credentials                             | Emit bounded structured diagnostics and prohibit secret values in the report                               |

## 11. Implementation Order

Implement in this sequence:

1. Add the direct dbt-utils dependency and parity projection models.
2. Add the two dbt-utils equality tests and update selector boundaries.
3. Expand custom current, fact, and mart parity coverage.
4. Make `record-parity` persist and report combined custom/dbt-utils outcomes.
5. Add comparator-sensitivity and orchestration unit tests.
6. Extract reusable batch/Airflow polling helpers without changing existing
   fixture-test defaults.
7. Implement the full-stack parity orchestrator and JSON report.
8. Add the nightly/manual workflow and failure artifacts.
9. Update the local CDC validation runbook and Phase 6 implementation record
   with the new command and the exact claim it proves.
10. Run all existing bounded checks plus one clean full-stack parity execution
    and record the evidence.

Do not claim completion from dbt-only comparison or synthetic `raw_cdc`
insertion. The defining acceptance evidence is one clean run through both real
ingestion paths from the same committed archive.
