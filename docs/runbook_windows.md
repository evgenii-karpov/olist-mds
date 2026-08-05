# Windows local runbook

Run PowerShell from the repository root. Docker Desktop and `uv` must be
installed. Development secret files under `docker/secrets/dev/` are used
by the local Compose project; do not print their contents.

## Setup

```powershell
uv sync --all-groups
uv run python scripts/cdc/local_lab.py doctor --archive tests/fixtures/olist_small/olist_small.zip
uv run ruff check airflow/dags scripts tests
uv run ruff format --check airflow/dags scripts tests
```

## Start the local CDC path

```powershell
uv run python scripts/cdc/local_lab.py reset --yes
uv run python scripts/cdc/local_lab.py bootstrap --archive tests/fixtures/olist_small/olist_small.zip --run-id windows-seed
uv run python scripts/cdc/local_lab.py start-streaming --wait-ready
uv run python scripts/cdc/local_lab.py start-serving-observer
uv run python scripts/cdc/local_lab.py wait-caught-up --timeout 1800
uv run python scripts/cdc/local_lab.py start-serving --build
uv run python scripts/cdc/local_lab.py sync-serving --run-id windows-serving
uv run python scripts/cdc/local_lab.py validate --scope serving
```

For the complete local acceptance check:

```powershell
uv run python scripts/validation/stage_v_candidate_e2e.py run --run-id windows-acceptance --evidence-dir data/acceptance/windows-acceptance --confirm-reset
```

## Observability

```powershell
docker compose --profile platform --profile streaming --profile serving --profile observability --profile logs up -d --build --wait
uv run python scripts/ci/validate_observability_contract.py
$env:PYTHONPATH='.'
uv run pytest -q tests/observability
```

## Cleanup

```powershell
uv run python scripts/cdc/local_lab.py down
uv run python scripts/cdc/local_lab.py reset --yes
```
