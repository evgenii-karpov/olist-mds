# CDC secret rotation

The local lab uses stable committed development-only Docker secret files.
Use this procedure for non-local credentials or an explicitly configured local
override. Never paste resolved values into commands, logs, issues, or reports.

1. Inventory clients of the identity and capture health without reading the
   current secret value.
2. Generate a new value in the secret provider and update the server identity.
3. Replace only the affected secret file with restrictive permissions.
4. Recreate only affected clients with `docker compose up -d --force-recreate`.
5. Verify authentication, connector/NiFi health, ingest, transform, and alert
   resolution. Search bounded logs for accidental credential output.
6. Revoke the old value after all clients use the replacement.

Kafka TLS/auth and generated local PKI remain a documented follow-up from Phase
6; rotate them only after the broker and every client migrate together.
