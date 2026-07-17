# CDC alert testing and benchmark

Run fault injection only against a disposable local stack. The helper stops one
named service, never removes volumes, waits for `firing`, restores the service,
and waits for resolution:

```powershell
uv run python scripts/cdc/failure_injection.py --scenario connect --execute
uv run python scripts/cdc/failure_injection.py --scenario nifi --execute
uv run python scripts/cdc/failure_injection.py --scenario minio --execute
```

Store generated evidence under ignored `data/reports/`. Confirm every alert
links to a specific runbook and avoid shortening production rule `for:` values
merely to make a test fast.

The formal SLO commands are:

```powershell
uv run python scripts/cdc/benchmark_local.py --profile reference --execute
uv run python scripts/cdc/benchmark_local.py --profile burst --execute
uv run python scripts/cdc/benchmark_local.py --profile soak --execute
```

Reference is 5 lifecycles/s for 30 minutes, burst is 20/s for 10 minutes, and
soak is 2/s for four hours. A report passes only with latency observations,
p95 at most 300 seconds, and zero offset gaps. Also review DLQ, lag, queue,
CPU/memory/disk, lost-event reconciliation, and duplicate current-key tests
before accepting an SLO result. Pass
`--verified-no-lost-events --verified-no-duplicate-current-keys` only after
those independent checks succeed; without both flags the report cannot PASS.
