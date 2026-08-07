# Local CDC lifecycle

`scripts/lab.py` is the normative target-scoped lifecycle entry point. The
legacy `local_lab.py` remains the compatibility implementation used by the
existing local acceptance harness and detailed local runbooks.

The local runtime is:

```text
MySQL -> Debezium / Kafka Connect -> Kafka + Apicurio
      -> Spark Bronze/Silver -> Iceberg through Polaris and MinIO
      -> ClickHouse serving -> Airflow and dbt
```

The compatibility implementation owns service startup, fixture bootstrap,
connector registration, readiness checks, serving sync, rebuild and
maintenance commands. Each command emits one redacted JSON result.

Target-scoped commands include:

```powershell
uv run python scripts/lab.py doctor
uv run python scripts/lab.py local up
uv run python scripts/lab.py local streaming start --wait-ready
uv run python scripts/lab.py local serving
uv run python scripts/lab.py gcp preflight
uv run python scripts/lab.py gcp up
```

`gcp up` is intentionally blocked until project, region, ADC, `gcloud` and
the remaining cloud prerequisites are available; `gcp streaming start` is
reserved for the GCP Spark driver package in WP4. Neither command contacts
GCP during import or static validation.

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
`scripts/validation/local_cdc_acceptance.py`. Use it for a clean end-to-end
check and keep its evidence under `data/acceptance/`.

`cdc_admin.py` contains the Debezium connector registration helper.
`failure_injection.py` exercises the local alert transitions.
