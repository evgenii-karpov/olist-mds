# Kafka consumer recovery

The local runtime keeps Kafka topics and Spark checkpoints during a normal
service restart. Use this procedure when a consumer needs to resume from its
configured checkpoint.

1. Record the topic, partition, consumer group and current position.
2. Stop only the Spark streaming services:

   ```powershell
   uv run python scripts/cdc/local_lab.py stop-streaming
   ```

3. Correct the selected consumer position with the Kafka administration tool
   for the active Compose project. Do not delete Connect internal topics or
   the source database.
4. Start streaming and wait for the source to catch up:

   ```powershell
   uv run python scripts/cdc/local_lab.py start-streaming --wait-ready
   uv run python scripts/cdc/local_lab.py wait-caught-up --timeout 1800
   uv run python scripts/cdc/local_lab.py validate --scope serving
   ```

If a checkpoint or topic cannot be trusted, use the clean connector
resnapshot runbook instead of changing multiple offsets manually.
