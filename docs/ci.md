# CI and local validation

CI checks the local CDC runtime in small, focused jobs. Each job uses the
repository files and pinned service images.

## Automatic workflows

- `ci.yml` runs repository contracts, Python quality, unit tests, the Spark
  checks, the Airflow import check and dbt static checks.
- `lakehouse-components.yml` checks the Spark image, Airflow runtime and
  observability configuration.
- `lakehouse-cdc.yml` checks the CDC component contracts.
- `lakehouse-serving.yml` checks ClickHouse serving and serving operations.

The component workflows use Compose only for the services required by the job.
The dbt static job starts ClickHouse directly and does not start the rest of
the Compose project.

## Manual acceptance

`lakehouse-acceptance.yml` is started manually with a candidate commit and an
explicit confirmation for disposable Compose reset. Its
`local-cdc-acceptance` suite runs the complete local acceptance path. The job
uploads raw JSON, logs, and reports as workflow artifacts.

The acceptance runner and the observability job are independent. The runner
does not start observability services; `lakehouse-components.yml` validates
their configuration and tests separately.

## Local checks

```powershell
uv run ruff check .
uv run ruff format --check .
uv run pyright
$env:PYTHONPATH='.'
uv run pytest -q
uv run python scripts/ci/check_repository_contracts.py
uv run python scripts/ci/check_dbt_clickhouse_contract.py
uv run python scripts/ci/validate_observability_contract.py
```

Validate the committed fixture directly:

```powershell
uv run python scripts/utilities/validate_source_contract.py --archive tests/fixtures/olist_small/olist_small.zip --profile tests/fixtures/olist_small/source_profile_small.json
```

Acceptance evidence belongs under `data/` and must not contain secret values.
Use a distinct `COMPOSE_PROJECT_NAME` for concurrent local runs.
