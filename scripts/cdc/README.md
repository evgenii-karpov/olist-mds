# Target CDC lifecycle helpers

`local_lab.py` is the lifecycle entry point for the target local runtime:

```text
MySQL -> Debezium/Kafka Connect -> Kafka + Apicurio
      -> Spark Bronze/Silver -> Iceberg/Polaris/MinIO
      -> ClickHouse serving -> Airflow publication
```

The helper emits one redacted JSON result per command. It owns the disposable
Compose project, target bootstrap, connector registration, bounded Spark
readiness, serving sync/rebuild and maintenance operations. It does not own
business transformations or a second raw-file loader.

Typical local validation:

```powershell
uv run python scripts/cdc/local_lab.py reset --yes
uv run python scripts/cdc/local_lab.py bootstrap `
  --archive tests/fixtures/olist_small/olist_small.zip `
  --run-id local-small-seed
uv run python scripts/cdc/local_lab.py status --require platform
uv run python scripts/cdc/local_lab.py start-streaming --wait-ready
uv run python scripts/cdc/local_lab.py start-serving-observer
uv run python scripts/cdc/local_lab.py wait-caught-up
uv run python scripts/cdc/local_lab.py sync-serving --run-id local-serving-sync
```

`stage_v_candidate_e2e.py` is the authoritative full acceptance runner. Use
this module for bounded lifecycle actions and diagnostics; do not use it to
bypass Stage V gates or to mutate frozen F0 evidence.

`stage2_admin.py` owns the secret-free Debezium connector template and status
operations. `failure_injection.py` exercises bounded target availability
scenarios for the observability contract.
