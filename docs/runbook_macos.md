# macOS and Linux local runbook

Run shell commands from the repository root. Docker Desktop and `uv` must
be installed. Development secret files under `docker/secrets/dev/` are used
by the local Compose project; do not print their contents.

## Setup

```bash
uv sync --all-groups
uv run python scripts/cdc/local_lab.py doctor --archive tests/fixtures/olist_small/olist_small.zip
uv run ruff check airflow/dags scripts tests
uv run ruff format --check airflow/dags scripts tests
```

## Start the local CDC path

```bash
uv run python scripts/cdc/local_lab.py reset --yes
uv run python scripts/cdc/local_lab.py bootstrap --archive tests/fixtures/olist_small/olist_small.zip --run-id unix-seed
uv run python scripts/cdc/local_lab.py start-streaming --wait-ready
uv run python scripts/cdc/local_lab.py start-serving-observer
uv run python scripts/cdc/local_lab.py wait-caught-up --timeout 1800
uv run python scripts/cdc/local_lab.py start-serving --build
uv run python scripts/cdc/local_lab.py sync-serving --run-id unix-serving
uv run python scripts/cdc/local_lab.py validate --scope serving
```

For the complete local acceptance check:

```bash
uv run python scripts/validation/local_cdc_acceptance.py run --run-id unix-acceptance --evidence-dir data/acceptance/local-cdc/unix-acceptance --confirm-reset
```

## Observability

```bash
docker compose --profile platform --profile streaming --profile serving --profile observability --profile logs up -d --build --wait
uv run python scripts/ci/validate_observability_contract.py
export PYTHONPATH=.
uv run pytest -q tests/observability
```

## Cleanup

```bash
uv run python scripts/cdc/local_lab.py down
uv run python scripts/cdc/local_lab.py reset --yes
```
