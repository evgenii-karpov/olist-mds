# Target serving ingestion

Spark writes the Iceberg Bronze/Silver tables and their audit evidence. The
serving boundary reads completed Iceberg state and publishes a finite
ClickHouse candidate through the Airflow serving DAG.

Start the bounded path:

```powershell
uv run python scripts/cdc/local_lab.py start-streaming --wait-ready
uv run python scripts/cdc/local_lab.py start-serving-observer
uv run python scripts/cdc/local_lab.py wait-caught-up
uv run python scripts/cdc/local_lab.py sync-serving --run-id manual-serving-sync
```

An unresolved `OPEN` transaction or effective `REJECTED` transaction must stop
the serving boundary. Inspect `audit.mysql_transactions`,
`audit.normalization_errors` and `audit.schema_violations`; repair the source
or replay through the target Spark path before retrying publication.
