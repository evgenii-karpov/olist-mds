# ClickHouse serving rebuild

The rebuild recreates the ClickHouse serving projection from the Iceberg tables.
It does not change MySQL, Kafka or Spark checkpoints.

Run it only for the disposable local project:

```powershell
uv run python scripts/cdc/local_lab.py rebuild-serving --yes --run-id local-rebuild
uv run python scripts/cdc/local_lab.py validate-rebuild --sync-run-seq <sync_run_seq> --sync-run-id <sync_run_id>
uv run python scripts/cdc/local_lab.py validate --scope serving
```

Use the `sync_run_seq` and `sync_run_id` values returned by the rebuild
command.

Inspect the rebuild result with:

```powershell
uv run python scripts/cdc/local_lab.py status --require serving
```
