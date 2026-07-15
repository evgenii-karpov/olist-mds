# Deterministic OLTP workload simulator

The package exposes five stable commands through
`python -m scripts.simulation`: `seed`, `run`, `replay`, `status`, and `stop`.
All mutating commands persist their effective configuration in
`simulator_control.simulation_runs`; lifecycle decisions, identifiers, and the
logical clock are derived only from the supplied seed and configuration.

Start only the Stage 1 dependency and seed the small fixture:

```text
docker compose --profile realtime-core up -d --wait oltp-postgres
uv run python -m scripts.simulation seed \
  --archive tests/fixtures/olist_small/olist_small.zip \
  --seed 101 \
  --password-file docker/secrets/dev/postgres_password.txt
```

Generate a finite deterministic workload:

```text
uv run python -m scripts.simulation run \
  --seed 20260716 --event-limit 20 --rate 5 \
  --password-file docker/secrets/dev/postgres_password.txt
```

Every log line is JSON. Connection strings and secret values are never emitted.
`status` reports the persisted run state, pending transition count, counters,
and last committed logical source timestamp. `stop` sets a database flag; a
running process observes it between transactions and exits gracefully.

Run the bounded Stage 1 integration check with:

```text
uv run python scripts/ci/check_oltp_simulator_integration.py \
  --password-file docker/secrets/dev/postgres_password.txt
```
