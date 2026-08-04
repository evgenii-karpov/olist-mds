# Windows local runbook

Run PowerShell commands from the repository root. Docker Desktop and `uv` are
required. Development-only secret files under `docker/secrets/dev/` are used
by default; do not print their contents.

## Setup and checks

```powershell
uv sync --all-groups
uv run python scripts/cdc/local_lab.py doctor
uv run pytest -q tests/mysql tests/cdc_contracts tests/lakehouse_platform tests/dbt_clickhouse tests/serving tests/stage_v
uv run ruff check airflow/dags scripts tests
uv run ruff format --check airflow/dags scripts tests
```

## Clean target bootstrap

```powershell
uv run python scripts/cdc/local_lab.py reset --yes
uv run python scripts/cdc/local_lab.py bootstrap `
  --archive tests/fixtures/olist_small/olist_small.zip `
  --run-id windows-small-seed
uv run python scripts/cdc/local_lab.py status --require platform
```

Start the bounded streaming and serving path:

```powershell
uv run python scripts/cdc/local_lab.py start-streaming --wait-ready
uv run python scripts/cdc/local_lab.py start-serving-observer
uv run python scripts/cdc/local_lab.py wait-caught-up
uv run python scripts/cdc/local_lab.py start-serving --build
uv run python scripts/cdc/local_lab.py sync-serving --run-id windows-serving-sync
```

For the complete clean acceptance run, use the Stage V runner and retain its
evidence under `data/stage-l-evidence/`:

```powershell
uv run python scripts/validation/stage_v_candidate_e2e.py run `
  --run-id windows-stage-v `
  --evidence-dir data/stage-l-evidence/manual/windows-stage-v `
  --confirm-reset
```

## dbt and observability contracts

```powershell
uv run dbt parse --project-dir dbt/olist_clickhouse --profiles-dir dbt/olist_clickhouse --target local_clickhouse
uv run python scripts/ci/check_dbt_clickhouse_contract.py
uv run python scripts/ci/validate_observability_contract.py
```

The Stage V runner does not start observability services. Run the observability
contract workflow or the documented Compose profiles separately when that
contract is the subject of the check.

## Cleanup

```powershell
uv run python scripts/cdc/local_lab.py down
uv run python scripts/cdc/local_lab.py reset --yes
```
