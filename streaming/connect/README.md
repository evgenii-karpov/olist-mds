# Local Debezium Connect contract

The local image is built from immutable Debezium digest
`sha256:d574a7c9575ed78e2349a034ebdf57a99c516771b3dddb7bbeeb44f912a36e22`.
The base contains PostgreSQL connector 3.6.0.Final and Apicurio converter 3.2.5.
The Dockerfile verifies the primary JAR checksums at build time and downloads
nothing at container startup.

`olist-postgres-cdc.json` is secret-free. The administration command reads the
CDC password from a file, renders it only in memory, and creates or updates the
connector without printing the resolved configuration:

```text
python scripts/cdc/stage2_admin.py register-connector \
  --password-file docker/secrets/dev/postgres_password.txt
python scripts/cdc/stage2_admin.py connector-status
```

Registration is idempotent and refuses a FAILED connector/task. After the
underlying dependency is healthy, restart only failed work explicitly:

```text
python scripts/cdc/stage2_admin.py restart-failed
```

Neither path deletes Connect offsets, drops `olist_cdc_slot`, or triggers a
resnapshot. A controlled resnapshot is intentionally not an ordinary update.
