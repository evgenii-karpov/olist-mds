# WP9 — `dbt-bigquery` Incremental Gold

Date: 2026-08-07
Branch: `gcp-bigquery-dual-contour`

## Status

The credential-free implementation is complete for static validation. The
stage is not fully closed: real GCP execution is still required to prove
bridge schemas, BigQuery job behavior, exact candidate counts, publication,
and retry/conflict semantics.

## Implemented

- Added the independent `dbt/olist_bigquery` project with eight Gold models,
  ephemeral staging/intermediate layers, documentation, selectors, source
  contracts, data tests, and two unit-test definitions.
- Added a boundary-driven source macro. Every Silver input is read through a
  native bridge source and joined to `olist_serving_control.boundary_offsets`
  using the exact `(previous_offset, target_offset]` interval for the run.
  There is no fixed `updated_at` lookback.
- Added canonical source-order fields to latest-key propagation and retained
  run metadata, boundary IDs, operation type, and build timestamp on every
  history candidate.
- Added model-specific history aliases and operation types:
  `INSERT`/`CLOSE`/`DELETE` for SCD2, `UPSERT`/`DELETE` for dimensions/facts,
  and `REPLACE_GRAIN` for date and aggregate models.
- Added same-run cleanup hook that deletes only the current `sync_run_seq`
  before an incremental rebuild. Current tables, stable views, and atomic
  publication remain migration/procedure responsibilities.
- Aligned the dbt Gold target with the migration-owned `olist_gold_store`
  dataset by removing the extra custom schema suffix; the history relations
  now resolve to the exact names consumed by V005.
- Added pinned dependency `dbt-bigquery==1.11.3` and a dedicated
  `dbt-bigquery` Compose service/image. The service has no dependency on the
  Airflow image and exposes only its project files plus a future ADC mount.

## Exact versions and local evidence

- `dbt-core 1.11.8`;
- `dbt-bigquery 1.11.3`;
- image tag `olist-dbt-bigquery:1.11.3`;
- image ID from the local build: `sha256:d707c9be7998926b181d3343bea85fd3f2b8488fa742760a9ea446bad5164ef9`;
- dbt parse: 25 models, 44 data tests, 16 sources, 2 unit tests;
- host parse passed with `--no-partial-parse`;
- container parse passed with the same project and no ADC/GCP access;
- contract checker passed: 8 Gold models and 10 bridge sources;
- Compose render passed for `core + lakehouse-gcp`;
- pre-commit passed, including the new `dbt-bigquery-parse` hook;
- static Python contract tests cover model inventory, run-scoped history,
  exact interval predicates, and forbidden local/metadata references.

## Cloud closeout still required

After WP5 produces an accepted vertical-slice decision, a real GCP run must:

1. apply V001–V003 and record migration-ledger/job evidence;
2. run the initial Gold build with a frozen boundary and compare direct/bridge
   schemas and row counts;
3. run an incremental interval with impacted-key propagation and verify that
   untouched keys/grains are not rewritten;
4. retry the same unpublished sequence and verify sequence-local history
   cleanup;
5. execute publication and verify current/stable view state, job labels,
   bytes processed/billed, and model-result control rows.
