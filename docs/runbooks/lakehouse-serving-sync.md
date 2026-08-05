# Serving sync

The serving sync reads the completed Iceberg transaction boundary, materializes
ClickHouse serving tables and publishes the dbt views for that sync.

Start the serving services:

```powershell
uv run python scripts/cdc/local_lab.py start-serving --build
```

Run a named sync:

```powershell
uv run python scripts/cdc/local_lab.py sync-serving --run-id local-serving-sync
```

Check the result:

```powershell
uv run python scripts/cdc/local_lab.py status --require serving
uv run python scripts/cdc/local_lab.py validate --scope serving
```

The control schema records the sync state, entity results and publication
boundary. A retry with the same run identifier must not expose an incomplete
or rejected source transaction.
