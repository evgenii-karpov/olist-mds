# Local secret rotation

Local credentials are supplied through Docker secret files or the corresponding
`*_FILE` settings. Never put a resolved value in a command, log, issue
or evidence file.

1. Identify the service and credential file without opening the value.
2. Replace the file with restrictive permissions.
3. Recreate only the clients that use the credential:

   ```powershell
   docker compose up -d --force-recreate <service>
   ```

4. Verify MySQL, Kafka Connect, Apicurio, MinIO, Polaris, Spark, ClickHouse
   and Airflow authentication as applicable.
5. Confirm the related observability alert resolves.

If the Polaris catalog or object-store identities are inconsistent, use
`local_lab.py reset --yes` so the local credential projections and
catalog identities are created together.
