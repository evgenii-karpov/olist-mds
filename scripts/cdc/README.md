# Local CDC lifecycle

`local_lab.py` is the lifecycle entry point for the local Compose
runtime:

```text
MySQL -> Debezium / Kafka Connect -> Kafka + Apicurio
      -> Spark Bronze/Silver -> Iceberg through Polaris and MinIO
      -> ClickHouse serving -> Airflow and dbt
```

It owns service startup, fixture bootstrap, connector registration, readiness
checks, serving sync, rebuild and maintenance commands. Each command emits one
redacted JSON result.

The main commands are `doctor`, `reset`, `up`, `down`,
`bootstrap`, `status`, `validate`, `start-streaming`,
`wait-caught-up`, `start-serving`, `sync-serving`,
`rebuild-serving` and `run-maintenance`.

Typical fixture run:

```powershell
uv run python scripts/cdc/local_lab.py reset --yes
uv run python scripts/cdc/local_lab.py bootstrap --archive tests/fixtures/olist_small/olist_small.zip --run-id local-seed
uv run python scripts/cdc/local_lab.py start-streaming --wait-ready
uv run python scripts/cdc/local_lab.py start-serving-observer
uv run python scripts/cdc/local_lab.py wait-caught-up
uv run python scripts/cdc/local_lab.py sync-serving --run-id local-serving-sync
```

The acceptance runner is
`scripts/validation/stage_v_candidate_e2e.py`. Use it for a clean
end-to-end check and keep its evidence under `data/`.

`stage2_admin.py` contains the Debezium connector registration helper.
`failure_injection.py` exercises the local alert transitions.
