# Target CDC end-to-end validation

This runbook validates the target path:

```text
MySQL -> Debezium/Kafka Connect -> Kafka + Apicurio
      -> Spark Bronze/Silver -> Iceberg/Polaris/MinIO
      -> ClickHouse serving -> Airflow publication
```

For a destructive, reproducible run:

```powershell
uv run python scripts/cdc/local_lab.py reset --yes
uv run python scripts/cdc/local_lab.py bootstrap `
  --archive tests/fixtures/olist_small/olist_small.zip `
  --run-id target-cdc-small
uv run python scripts/cdc/local_lab.py start-streaming --wait-ready
uv run python scripts/cdc/local_lab.py start-serving-observer
uv run python scripts/cdc/local_lab.py wait-caught-up
uv run python scripts/cdc/local_lab.py sync-serving --run-id target-serving-sync
```

The full V0–V10 acceptance runner is the authoritative check. Save its raw
JSON and logs under `data/stage-l-evidence/`; a component check is not a
substitute for the full gate registry.

Inspect bounded status with:

```powershell
uv run python scripts/cdc/local_lab.py status --require serving
uv run python scripts/cdc/local_lab.py validate --scope serving
```

Run observability separately through `lakehouse-components.yml` or the target
Compose profiles. The Stage V runner intentionally remains independent of
observability services.
