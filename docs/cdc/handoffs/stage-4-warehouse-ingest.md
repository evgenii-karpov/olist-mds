# Handoff: Stage 4 — idempotent warehouse ingest

## Mission

Implement Phase 4 from the approved CDC plan. Load only closed normalized
Parquet objects whose immutable manifests exist into PostgreSQL `raw_cdc`, and
record every claim, attempt, reconciliation result, offset interval, watermark,
and replay request in `cdc_audit`.

## Upstream contract

- Bucket: `olist-cdc` on `http://minio:9000` inside Compose.
- Data: `stage/cdc/table=<table>/event_date=<date>/hour=<hour>/*.parquet`.
- Commit marker: matching
  `manifests/cdc/kind=normalized/table=<table>/ingest_date=<date>/hour=<hour>/*.manifest.json`.
- Offset classification marker:
  `manifests/cdc/kind=coverage/table=<table>/ingest_date=<date>/hour=<hour>/*.coverage.json`.
  It is published after the referenced landing object and landing manifest and
  contains exact consumed, business-event, and tombstone ranges.
- `_event_id=<topic>:<partition>:<offset>` is the immutable deduplication key.
- Manifests contain row count, SHA-256, schema ID, object key, topic,
  partition, exact offset ranges, operation counts, and event-time bounds.
- Deletes are ordinary normalized `op=d` rows populated from Debezium `before`;
  tombstones never appear in normalized Parquet.

## Required boundary

Add bootstrap SQL for `raw_cdc` and `cdc_audit`, transactional file claiming,
Parquet staging, conflict-safe `_event_id` insertion, exact reconciliation,
gap-aware contiguous watermarks, metrics, a scheduled local Airflow ingest DAG,
and table/date/object replay. Do not build realtime dbt models in this stage.

Warehouse continuity is strictly
`NORMALIZED_LOADED union TOMBSTONE_AUDITED`. Coverage business ranges never
advance a raw watermark until the matching normalized records commit to
PostgreSQL.
Persist consumed source ranges separately so missing business events are
visible even at the current tail. Replay claims must remain bound to their
idempotent request ID and unavailable to scheduled claims.
