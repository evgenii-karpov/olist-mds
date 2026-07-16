# CDC realtime dbt runbook

## Transform state

Inspect `cdc_audit.cdc_transform_runs` and
`cdc_audit.cdc_transform_run_files`. Retry a failed run with the same transform
run ID; its manifest membership remains fixed. Never mark a run successful
manually or delete membership to skip an event.

## Semantic integration

```powershell
$env:UV_CACHE_DIR="$PWD\.uv-cache"
uv run python scripts/ci/check_stage5_cdc_integration.py `
  --password-file docker/secrets/dev/postgres_password.txt
```

The script creates and drops only a database prefixed
`olist_cdc_phase5_test_`.

## Parity and publication

After both equivalent initial states are built:

```powershell
uv run python scripts/cdc/realtime_transform.py record-parity
uv run python scripts/cdc/realtime_transform.py publish `
  --target realtime --approved-by operator
```

Rollback changes only the two stable views:

```powershell
uv run python scripts/cdc/realtime_transform.py publish `
  --target batch --approved-by operator
```

## Quality

The hourly DAG checks gaps, latest reconciliation, mart freshness, and model
keys. Its midnight logical run also runs full realtime tests and Elementary.
Repair missing raw coverage through the Phase 4 ingest ledger; never advance
transform state around missing events.
