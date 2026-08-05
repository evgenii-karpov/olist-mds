# CDC service restart

Use this procedure when a local MySQL, Kafka Connect, Apicurio, Kafka, Spark,
Polaris or MinIO service is unhealthy.

1. Record the service status and the current connector, consumer-position and
   Spark readiness output.
2. Inspect bounded logs:

   ```powershell
   docker compose logs --no-color --tail=300 <service>
   ```

3. Restart only the affected service. Preserve volumes and checkpoints:

   ```powershell
   docker compose restart <service>
   ```

4. Re-run the relevant readiness command:

   ```powershell
   uv run python scripts/cdc/local_lab.py status --require platform
   uv run python scripts/cdc/local_lab.py start-streaming --wait-ready
   ```

5. Confirm that CDC positions advance, Spark status is fresh and the related
   alert resolves.

If the service state cannot be trusted, stop the project and follow the clean
bootstrap in the local acceptance runbook.
