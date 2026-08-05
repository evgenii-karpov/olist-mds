# Local CDC acceptance

This runbook checks the complete local path:

```text
MySQL -> Debezium / Kafka Connect -> Kafka + Apicurio
      -> Spark Bronze/Silver -> Iceberg through Polaris and MinIO
      -> ClickHouse serving -> Airflow and dbt
```

Run a clean local check with the committed fixture:

```powershell
uv run python scripts/cdc/local_lab.py reset --yes
uv run python scripts/cdc/local_lab.py bootstrap --archive tests/fixtures/olist_small/olist_small.zip --run-id local-seed
uv run python scripts/cdc/local_lab.py start-streaming --wait-ready
uv run python scripts/cdc/local_lab.py start-serving-observer
uv run python scripts/cdc/local_lab.py wait-caught-up --timeout 1800
uv run python scripts/cdc/local_lab.py start-serving --build
uv run python scripts/cdc/local_lab.py sync-serving --run-id local-serving
uv run python scripts/cdc/local_lab.py validate --scope serving
```

For the complete acceptance runner:

```powershell
uv run python scripts/validation/stage_v_candidate_e2e.py run --run-id local-acceptance --evidence-dir data/acceptance/local-acceptance --confirm-reset
```

Inspect the resulting status without reading secrets:

```powershell
uv run python scripts/cdc/local_lab.py status --require serving
```

Telemetry is independent of this check. Use the observability runbook when
metrics and alert transitions are part of the validation.
