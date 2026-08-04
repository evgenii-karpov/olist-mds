# Rebuild target Bronze/Silver state

The target source of truth is the immutable Kafka/Iceberg boundary. A serving
rebuild must not invent rows or advance a control watermark manually.

For a local clean replay, remove only the project-owned resources and rerun
the target bootstrap:

```powershell
uv run python scripts/cdc/local_lab.py reset --yes
uv run python scripts/cdc/local_lab.py bootstrap `
  --archive tests/fixtures/olist_small/olist_small.zip `
  --run-id rebuild-small
uv run python scripts/cdc/local_lab.py start-streaming --wait-ready
uv run python scripts/cdc/local_lab.py wait-caught-up
```

For a serving-only rebuild after Iceberg remains authoritative, use
`rebuild-serving --yes` and retain the resulting control/evidence JSON.
