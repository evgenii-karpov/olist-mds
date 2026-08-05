# Observability alert testing

Start the runtime and telemetry profiles:

```powershell
docker compose --profile platform --profile streaming --profile serving --profile observability --profile logs up -d --build --wait
```

Validate the static contract and alert test suite:

```powershell
uv run python scripts/ci/validate_observability_contract.py
$env:PYTHONPATH='.'
uv run pytest -q tests/observability
```

Exercise one local failure at a time:

```powershell
uv run python scripts/cdc/failure_injection.py --scenario connect --execute
uv run python scripts/cdc/failure_injection.py --scenario minio --execute
uv run python scripts/cdc/failure_injection.py --scenario target-probe --execute
```

For each scenario, record the firing alert, bounded logs and the resolved
alert. A dashboard view alone is not a validation result.
