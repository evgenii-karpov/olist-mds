# Runbook: Lakehouse Iceberg Maintenance

## 1. Overview
The `olist_iceberg_maintenance` DAG runs daily at 03:00 UTC to execute data file compaction, manifest rewriting, snapshot expiration, and orphan file cleanup on Iceberg tables.

## 2. Operation
To trigger maintenance manually:
```powershell
python scripts/cdc/local_lab.py run-maintenance [--run-id <id>]
```
