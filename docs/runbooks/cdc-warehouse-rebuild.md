# Target ClickHouse serving rebuild

ClickHouse is a disposable serving projection. Iceberg and the serving control
ledger remain authoritative during a rebuild.

```powershell
uv run python scripts/cdc/local_lab.py rebuild-serving `
  --yes `
  --run-id manual-serving-rebuild
uv run python scripts/cdc/local_lab.py validate-rebuild `
  --sync-run-seq <seq> `
  --sync-run-id <run-id>
```

Do not delete MySQL, Kafka, Polaris or MinIO volumes as part of a serving-only
rebuild. Use `reset --yes` only for an explicitly destructive full-lab replay.
