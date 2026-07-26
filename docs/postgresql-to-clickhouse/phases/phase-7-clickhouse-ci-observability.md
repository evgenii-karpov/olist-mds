# Phase 7: Migrate ClickHouse CI, Observability, and Documentation

Status: completed on 2026-07-23; parity workflow contract corrected on
2026-07-26.

## Delivered contract

- Added a `local_clickhouse` CI candidate job that starts isolated ClickHouse,
  initializes schemas, runs the ClickHouse smoke check, compiles the batch,
  realtime transform, and realtime parity selectors, and validates the
  canonical manifest comparator artifact contract.
- Extended the manual batch-versus-CDC parity workflow so the primary job runs
  the full-stack ClickHouse candidate path, stages the accepted PostgreSQL
  oracle manifest, exports a real ClickHouse candidate manifest, and compares
  those two artifacts with the canonical comparator.
- Kept the two-run ClickHouse candidate evidence matrix as compile/smoke/CLI
  validation only; it is not the semantic cutover gate.
- Updated the Stage 6 operational drill workflow to run with
  `DBT_TARGET=local_clickhouse` and `CDC_WAREHOUSE_TYPE=clickhouse`.
- Replaced the warehouse PostgreSQL exporter in the observability path with
  ClickHouse native Prometheus metrics at `clickhouse:9363`.
- Kept the OLTP PostgreSQL exporter intact for Debezium source health.
- Refactored `scripts/cdc/pipeline_metrics.py` so raw CDC metrics can be read
  from ClickHouse while file claims, watermarks, reconciliation, transform
  state, mart freshness, and publication state remain in PostgreSQL
  `olist_control`.
- Added the `CdcClickHouseUnavailable` alert and updated the Airflow/dbt
  warehouse dashboard to show ClickHouse scrape health, uptime, query rate,
  failed query rate, raw CDC freshness, ingest/transform duration, and mart
  freshness.
- Added Phase 7 contract tests covering CI workflow hooks, exporter topology,
  Prometheus scrape config, alerts, dashboard queries, and the absence of the
  warehouse PostgreSQL exporter.
- Updated CI, observability, CDC warehouse ingest, Windows, macOS, README, and
  `.env.example` documentation for the ClickHouse candidate path.

## Verification evidence

Passed:

- `docker compose config --quiet`;
- `uv run python -m unittest discover -s tests -p "test_clickhouse_phase7_ci_observability.py" -v`;
- `uv run python -m unittest discover -s tests -p "test_stage6_contracts.py" -v`;
- `uv run python scripts/ci/validate_stage6_configuration.py`;
- `uv run python -m compileall scripts/cdc/pipeline_metrics.py scripts/ci/validate_stage6_configuration.py`;
- `uv run ruff check scripts/cdc/pipeline_metrics.py scripts/ci/validate_stage6_configuration.py tests/test_clickhouse_phase7_ci_observability.py tests/test_stage6_contracts.py`;
- `uv run pyright scripts/cdc/pipeline_metrics.py scripts/ci/validate_stage6_configuration.py tests/test_clickhouse_phase7_ci_observability.py tests/test_stage6_contracts.py`.

## Open evidence

- Two full deterministic ClickHouse candidate workflows still need to be run in
  GitHub Actions or another clean disposable environment before Phase 8
  cutover. The primary manual parity workflow now enforces the required
  oracle-vs-candidate comparison, but this document does not claim two green
  runs from the current workstation volume.
- The PostgreSQL oracle used by this workflow is the committed accepted oracle
  fixture from Phase 0. If the deterministic fixture or oracle contract
  changes, regenerate that fixture before treating a ClickHouse comparison as
  cutover evidence.

## Phase boundary

No `local_pg` profile, analytical PostgreSQL service, PostgreSQL oracle sink,
or PostgreSQL oracle documentation was removed. Phase 8 owns the default target
switch and oracle cleanup after the approved cutover gate is satisfied.
