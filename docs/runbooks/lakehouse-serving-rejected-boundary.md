# Rejected serving boundary

The serving planner stops at a source transaction that contains a rejected
record or a contract failure. The boundary remains visible in the serving
control state and is not published.

1. Check the local status and bounded service logs:

   ```powershell
   uv run python scripts/cdc/local_lab.py status --require serving
   docker compose logs --no-color --tail=300 spark-bronze spark-silver clickhouse
   ```

2. Inspect the normalization and schema-violation records in the Iceberg audit
   tables.
3. Correct the source or the contract in the local project.
4. Wait for CDC to catch up and run serving sync again:

   ```powershell
   uv run python scripts/cdc/local_lab.py wait-caught-up --timeout 1800
   uv run python scripts/cdc/local_lab.py sync-serving --run-id rejected-boundary-retry
   uv run python scripts/cdc/local_lab.py validate --scope serving
   ```

Do not publish across an `OPEN` or `REJECTED` transaction.
