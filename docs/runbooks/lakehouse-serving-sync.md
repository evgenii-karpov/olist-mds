# Runbook: Lakehouse Serving Sync

## 1. Overview
The `olist_lakehouse_serving_sync` Airflow DAG periodically (every 5 minutes) publishes transaction-complete Iceberg data into ClickHouse and dbt Gold.

## 2. Operation
To trigger serving sync manually:
```powershell
python scripts/cdc/local_lab.py sync-serving [--run-id <id>]
```

## 3. Verification
Check status:
```powershell
python scripts/cdc/local_lab.py status --require serving
```
