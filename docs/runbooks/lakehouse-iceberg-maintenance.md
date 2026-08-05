# Iceberg maintenance

Run the local maintenance operation after the serving services are healthy:

```powershell
uv run python scripts/cdc/local_lab.py run-maintenance --run-id local-maintenance
uv run python scripts/cdc/local_lab.py status --require serving
```

Review the operation result and Spark logs before removing any local volume.
Keep Spark checkpoints and table locations together.
