# Runbook: Lakehouse ClickHouse Rebuild

## 1. Overview
Rebuilds all four derived ClickHouse databases (`serving_cdc`, `serving_control`, `gold_store`, `gold`) strictly from Iceberg tables without affecting source MySQL, Kafka, Polaris, MinIO, or Spark checkpoints.

## 2. Operation
```powershell
python scripts/cdc/local_lab.py rebuild-serving --yes [--run-id <id>]
```
Note: `--yes` flag is mandatory.
