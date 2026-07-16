# Handoff: Stage 5 — realtime dbt and DAG separation

## Mission

Implement Phase 5 from the approved CDC plan. Build ordered realtime event
staging, current state, history, changed keys, dimensions, facts, marts,
asset-triggered transforms, scheduled quality checks, parity reports, and
reversible publication views.

## Verified upstream contract

- Eight append-only typed event tables exist in `raw_cdc` and are unique by
  `_event_id=<topic>:<partition>:<offset>`.
- Source ordering metadata is preserved: `_source_lsn`, `_tx_id`, `_tx_order`,
  `_partition`, and `_offset`. Warehouse load timestamps are not business order.
- Deletes are ordinary `_op='d'` rows populated from Debezium `before` values;
  tombstones do not create raw rows.
- `cdc_audit.cdc_offset_coverage` distinguishes `NORMALIZED_LOADED` from
  `TOMBSTONE_AUDITED` exact ranges.
- `cdc_audit.cdc_partition_watermarks.last_contiguous_offset` accounts for both
  committed events and verified tombstones, while `last_loaded_event_offset`
  identifies the highest committed business event.
- `olist_cdc_ingest_local` emits `olist://cdc/raw/local` only when new raw rows
  commit. Duplicate-only scheduled or replay runs do not emit the Asset.
- File and event replay are idempotent and do not require raw-table cleanup.

## Required boundary

Create only Phase 5 realtime dbt models and transform/quality orchestration.
Do not reinterpret coverage manifests as business events, union batch and CDC
copies, or order current state by ingestion timestamps.

## Delivery status

Implemented on 2026-07-16. The delivered contract and verification evidence are
recorded in `docs/cdc/phases/phase-5-realtime-dbt.md`. Phase 6 must retain the
immutable transform membership and operator-approved publication gate.
