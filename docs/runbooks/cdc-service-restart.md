# Target CDC service restart

Use this procedure for MySQL, Kafka Connect, Apicurio, Spark, Polaris or MinIO
availability alerts.

1. Record the alert, connector/task state, Kafka lag, Spark status files and
   target-probe output.
2. Inspect bounded logs: `docker compose logs --no-color --tail=300 <service>`.
3. Restart only the affected target service using its Compose profile and
   preserve volumes/checkpoints.
4. Re-run the relevant readiness command:

   ```powershell
   uv run python scripts/cdc/local_lab.py status --require platform
   uv run python scripts/cdc/local_lab.py start-streaming --wait-ready
   ```

5. Confirm lag drains, Spark status is fresh, and the relevant alert resolves.

Exercise bounded failure/resolve behavior with
`uv run python scripts/cdc/failure_injection.py --scenario connect --execute`.
