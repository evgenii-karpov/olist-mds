# Runbook: Lakehouse Serving Sync

## 1. Overview
The `olist_lakehouse_serving_sync` Airflow DAG publishes transaction-complete Iceberg data into ClickHouse and dbt Gold when triggered manually.

## 2. Operation
Start the serving profile and wait for its dependencies before triggering a sync:
```powershell
python scripts/cdc/local_lab.py start-serving [--build] [--timeout <seconds>]
```

The command starts the Compose `platform` and `serving` profiles and verifies
healthy `clickhouse`/`airflow` containers plus successful serving bootstrap
jobs.

To trigger serving sync manually:
```powershell
python scripts/cdc/local_lab.py sync-serving [--run-id <id>]
```

Serving, quality, maintenance and rebuild DAGs are manual-only (`schedule=None`)
and are created unpaused. This prevents the scheduler from creating a
competing boundary while a validation run is in progress.

To validate the published candidate and stable interfaces after a successful
non-NOOP sync:
```powershell
python scripts/cdc/local_lab.py validate-serving `
  --sync-run-seq <seq> `
  --sync-run-id <sync-run-id>
```

## 3. Verification
Check status:
```powershell
python scripts/cdc/local_lab.py status --require serving
```
