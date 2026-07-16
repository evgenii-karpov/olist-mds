# Phase 4: Idempotent warehouse ingest and audit

Status: implemented and verified on 2026-07-16.

## Delivered contract

- `infra/postgres/006_create_cdc_tables.sql` creates eight append-only typed
  `raw_cdc` event tables and durable `cdc_audit` state for runs, files, claims,
  attempts, coverage, reconciliation, replay, watermarks, dead letters, and
  future mart freshness.
- `scripts/cdc/warehouse_ingest.py` discovers only closed normalized Parquet
  manifests, validates immutable identities and exact row/operation/offset
  reconciliation, claims files transactionally, stages Parquet in PostgreSQL,
  inserts unseen `_event_id` values, and commits file/audit/watermark state in
  the same transaction.
- Coverage manifests are independently verified against their immutable landing
  object and landing manifest. Exact intervals are recorded as either
  `SOURCE_CONSUMED`, `NORMALIZED_LOADED`, or `TOMBSTONE_AUDITED`. The first is
  an expected source horizon, not proof that a warehouse row was loaded.
- `last_contiguous_offset` is computed from the union of those two interval
  classes. `last_loaded_event_offset` separately records the highest normalized
  business event committed to `raw_cdc`. Landing business coverage alone cannot
  advance the warehouse watermark.
- `airflow/dags/olist_cdc_local.py` provides the two-minute
  `olist_cdc_ingest_local` DAG and manual `olist_cdc_backfill_local` DAG. The raw
  CDC Asset is emitted only when new rows commit.
- `scripts/cdc/pipeline_metrics.py` exports low-cardinality freshness, event,
  file, duplicate, reconciliation, coverage, watermark, gap, and run metrics
  from read-only transactions.
- MinIO provisions a separate read-only `olist_cdc_loader` identity; the NiFi
  writer remains independent.

## Effectively-once boundary

Transport remains at least once. Warehouse results are effectively once through
immutable object identity, transactional claims, `_event_id` conflict handling,
exact reconciliation, and durable replay requests. Replaying normalized files
does not remove or recreate coverage and does not duplicate raw rows.
Replay selection is request-bound (`REPLAY_REQUESTED`) so scheduled ingestion
cannot steal replay work; repeating the same request ID is idempotent.

## Verification

- Unit tests validate normalized and coverage contracts, exact classification,
  layout confinement, event identity, range merging, replay selectors, SQL
  bootstrap, DAG configuration, and least-privilege object access.
- The isolated MinIO/PostgreSQL integration check proves an observed gap,
  closure by later verified tombstone coverage without raw inserts, transient
  object-read failure and retry, detection of missing business coverage at the
  source tail, exact PASS reconciliation, and duplicate-only replay.
- Full Ruff, formatting, Pyright, Python unit, Compose configuration, and
  Airflow DAG import gates pass.

## Operational boundary

Phase 4 does not build current-state, history, fact, or mart models. Those begin
in Phase 5 and consume only committed `raw_cdc` events and durable watermarks.
