# Target observability alert testing

Observability is a separate target contract. It is not started or validated by
the Stage V runner.

Validate the static inventory first:

```powershell
uv run python scripts/ci/validate_observability_contract.py
uv run pytest -q tests/observability
```

For bounded local transitions, use the target failure injector:

```powershell
uv run python scripts/cdc/failure_injection.py --scenario connect --execute
uv run python scripts/cdc/failure_injection.py --scenario minio --execute
uv run python scripts/cdc/failure_injection.py --scenario target-probe --execute
```

Capture alert state, bounded logs and the resolve result. Never treat a
dashboard screenshot without a firing and resolved alert transition as
evidence.
