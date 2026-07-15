# Isolated Olist OLTP source

This directory contains the PostgreSQL initialization assets for the Stage 1
source system. Docker Compose mounts `initdb/` into the dedicated `olist-oltp`
container. The database is intentionally separate from the analytics warehouse
and Airflow metadata database.

The source exposes the nine Olist entities with OLTP keys, foreign keys,
constraints, and lookup indexes. `simulator_control` is a non-business schema
used for deterministic run configuration, synthetic-record ownership, pending
transitions, replay timestamp mappings, seed identity, heartbeats, and graceful
stop requests. It must not be added to the Debezium publication in Stage 2.

Roles are created at first database initialization:

- the Compose `POSTGRES_USER` is the bootstrap/admin owner;
- `olist_simulator` can mutate business data and control state;
- `olist_cdc_reader` can read business tables, but has no control-schema access
  and does not receive replication/publication privileges until Stage 2.

Passwords are read from Docker secret files. The committed development secret
is reused by default to preserve the repository's existing zero-setup local
workflow; override the `OLTP_*_PASSWORD_SOURCE_FILE` variables with ignored
files for any shared environment.

Reset the reproducible lab database with:

```text
docker compose down -v
docker compose --profile realtime-core up -d --wait oltp-postgres
```
