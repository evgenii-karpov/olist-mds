# Connector resnapshot

Use a resnapshot when the local MySQL-to-Kafka boundary must be recreated.
This operation resets the disposable local state.

1. Record connector status and the local run identifier.
2. Stop streaming:

   ```powershell
   uv run python scripts/cdc/local_lab.py stop-streaming
   ```

3. Recreate MySQL, Kafka, the catalog, checkpoints and serving state:

   ```powershell
   uv run python scripts/cdc/local_lab.py reset --yes
   uv run python scripts/cdc/local_lab.py bootstrap --archive tests/fixtures/olist_small/olist_small.zip --run-id local-resnapshot
   ```

4. Start CDC and wait for the source to catch up:

   ```powershell
   uv run python scripts/cdc/local_lab.py start-streaming --wait-ready
   uv run python scripts/cdc/local_lab.py wait-caught-up --timeout 1800
   ```

5. Run the serving sync and validation before using the local result.

The reset is intentional: the local project has no supported in-place
resnapshot that preserves previous offsets and checkpoints.
