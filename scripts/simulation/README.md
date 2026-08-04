# Deterministic MySQL workload simulator

The package exposes five stable commands through
`python -m scripts.simulation`: `seed`, `run`, `replay`, `status`, and `stop`.
All mutating commands persist their effective configuration in
`olist_simulator.simulation_runs`. Lifecycle decisions, identifiers, replay
timestamp mappings, and the logical clock are derived from the supplied random
seed and configuration rather than wall-clock scheduling.

Seed the small fixture after the MySQL platform service is healthy:

```text
uv run python -m scripts.simulation seed \
  --archive tests/fixtures/olist_small/olist_small.zip \
  --random-seed 101 \
  --password-file /run/secrets/mysql_simulator_password
```

Generate a finite deterministic workload:

```text
uv run python -m scripts.simulation run \
  --random-seed 20260716 --event-limit 20 --rate 5 \
  --password-file /run/secrets/mysql_simulator_password
```

Connection defaults come from `MYSQL_HOST`, `MYSQL_PORT`, and
`MYSQL_DATABASE`; the credential is read only from `MYSQL_PASSWORD_FILE` (or
the explicit `--password-file` path). That file is mandatory, must be readable,
and must contain exactly one non-empty password line (with an optional final
line ending). Plaintext password settings and CLI arguments are not supported.
Every log line is JSON, and secret values are never emitted.

Each lifecycle step is its own explicit MySQL transaction. A stop request is
observed between those transactions, and an injected failure during graph
creation rolls back the complete order/customer/item/payment unit. Seed data is
loaded in FK order, in batches of 5,000, with one transaction per entity.
Unhandled run/replay failures roll back the active transaction and persist a
terminal `failed` state. Terminal timestamps never precede the latest committed
lifecycle, review, correction, or hard-delete logical timestamp.

`tests/mysql/test_mysql_integration.py` is an authored, opt-in acceptance
scaffold. `OLIST_RUN_MYSQL_INTEGRATION=1` enables schema checks against an
already provisioned instance. The mutating repeated-seed check additionally
requires `OLIST_MYSQL_INTEGRATION_DISPOSABLE=1` and refuses to touch non-empty
business tables. The target runtime image supplies `mysql-connector-python`.
