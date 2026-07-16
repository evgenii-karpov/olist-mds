# CDC warehouse ingest runbook

Run commands from the repository root. PowerShell examples use the committed
development secret files; replace them with environment-specific secret mounts
outside local development.

## Bootstrap and start

```powershell
docker compose build airflow
docker compose --profile realtime-core up -d --wait `
  postgres minio minio-init cdc-warehouse-init airflow
```

Unpause `olist_cdc_ingest_local` only after NiFi is producing normalized and
coverage manifests. The DAG runs every two minutes and has one active run.

## Manual ingest

```powershell
uv run python scripts/cdc/warehouse_ingest.py `
  --password-file docker/secrets/dev/postgres_password.txt `
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
  --password-file docker/secrets/dev/postgres_password.txt `
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
verified tombstone coverage and relies on `_event_id` dedupe.

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
stages it again, and commits without manual table cleanup.

## Metrics

Prometheus scrapes `cdc-pipeline-exporter:9107`. Important metrics include
`olist_cdc_pipeline_up`, `olist_cdc_offset_gaps`,
`olist_cdc_offset_coverage_ranges`, `olist_cdc_last_contiguous_offset`,
`olist_cdc_last_loaded_event_offset`, raw freshness, duplicates, reconciliation,
and last successful ingest time.
