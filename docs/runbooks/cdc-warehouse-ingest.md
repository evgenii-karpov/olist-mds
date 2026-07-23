# CDC warehouse ingest runbook

Run commands from the repository root. PowerShell examples use the committed
development-only Docker secret files; replace them with environment-specific
secret mounts outside local development.

## Bootstrap and start

```powershell
docker compose build airflow
docker compose --profile realtime-core up -d --wait `
  airflow-postgres control-db-init clickhouse clickhouse-init minio airflow
docker compose --profile realtime-core run --rm --no-deps minio-init
docker compose --profile realtime-core run --rm --no-deps cdc-warehouse-init
```

Unpause `olist_cdc_ingest_local` only after NiFi is producing normalized and
coverage manifests. The DAG runs every two minutes and has one active run.

## Manual ingest

```powershell
uv run python scripts/cdc/warehouse_ingest.py `
  --warehouse-type clickhouse `
  --clickhouse-password-file docker/secrets/dev/clickhouse_password.txt `
  ingest `
  --s3-endpoint http://localhost:9000 `
  --s3-secret-file docker/secrets/dev/airflow_api_secret_key.txt `
  --ingest-run-id manual_cdc_ingest `
  --run-kind MANUAL
```

## Replay

Select at least one table, ingest-date, or object substring:

```powershell
uv run python scripts/cdc/warehouse_ingest.py `
  --warehouse-type clickhouse `
  --clickhouse-password-file docker/secrets/dev/clickhouse_password.txt `
  replay `
  --replay-request-id replay_orders_20260716 `
  --requested-by operator `
  --table orders `
  --date-from 2026-07-16 `
  --date-to 2026-07-16
```

Then run ingest with the same selectors and `--run-kind REPLAY`, or trigger
`olist_cdc_backfill_local`. A CLI replay ingest must also pass the same
`--replay-request-id`. Replay moves selected files to request-bound
`REPLAY_REQUESTED`; scheduled runs cannot claim them. It retains raw events and
verified tombstone coverage and relies on deterministic ClickHouse insert
tokens plus `FINAL` logical readback for topic/partition/offset dedupe.

## Diagnose gaps

Inspect `cdc_audit.cdc_partition_watermarks` and
`cdc_audit.cdc_offset_coverage`. A contiguous watermark can advance only through:

- normalized ranges whose files are `LOADED`;
- tombstone ranges whose coverage and landing references are verified.

`SOURCE_CONSUMED` defines how far the source has been observed. It does not
advance continuity, so a business offset lacking normalized data appears as a
gap even when it is the latest observed offset.

If a gap remains, compare the range against normalized and coverage manifests.
Do not manually invent coverage or advance a watermark. Restore/replay the
missing immutable object or repair the NiFi publication fault.

## Failed file recovery

A failed file remains `FAILED` with a durable attempt and error. Restore object
storage or correct the loader, then rerun the DAG. The loader reclaims the file,
uses the same deterministic ClickHouse insert token, validates existing logical
events with `FINAL`, and commits without manual table cleanup.

## Metrics

Prometheus scrapes ClickHouse directly at `clickhouse:9363` and the custom
pipeline exporter at `cdc-pipeline-exporter:9107`. Important metrics include
`up{job="clickhouse"}`, `ClickHouseAsyncMetrics_Uptime`,
`ClickHouseProfileEvents_FailedQuery`, `olist_cdc_pipeline_up`,
`olist_cdc_offset_gaps`,
`olist_cdc_offset_coverage_ranges`, `olist_cdc_last_contiguous_offset`,
`olist_cdc_last_loaded_event_offset`, raw freshness, duplicates, reconciliation,
and last successful ingest time.

The pipeline exporter reads raw CDC freshness and event counts from ClickHouse
when `CDC_WAREHOUSE_TYPE=clickhouse`, while claims, watermarks,
reconciliations, and publication state remain in PostgreSQL `olist_control`.
