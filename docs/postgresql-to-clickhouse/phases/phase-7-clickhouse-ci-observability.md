# Phase 7: Migrate ClickHouse CI, Observability, and Documentation

Status: completed on 2026-07-23; parity workflow contract corrected and clean
cutover evidence captured on 2026-07-26.

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

GitHub Actions evidence captured on 2026-07-26:

- CI run
  [30200994501](https://github.com/evgenii-karpov/olist-mds/actions/runs/30200994501)
  passed on `f23e3312d7b66b3da1fa99def0c3bd2bc238a811`.
- CI run
  [30202035677](https://github.com/evgenii-karpov/olist-mds/actions/runs/30202035677)
  passed on `c61171964095827d0ea1c3cb8310bd1cdda1f334`.
- Manual `Batch and CDC parity integration` run
  [30202045079](https://github.com/evgenii-karpov/olist-mds/actions/runs/30202045079)
  passed on `c61171964095827d0ea1c3cb8310bd1cdda1f334`.
- Manual `Batch and CDC parity integration` run
  [30202839894](https://github.com/evgenii-karpov/olist-mds/actions/runs/30202839894)
  passed on `c61171964095827d0ea1c3cb8310bd1cdda1f334`.

The two manual parity runs published `batch-cdc-parity-report`,
`clickhouse-candidate-run-1`, and `clickhouse-candidate-run-2` artifacts. The
primary `batch-cdc-parity-report` artifact contains
`postgres-oracle-manifest.json`, `clickhouse-candidate-manifest.json`, and
`cross-engine-comparator.json`.

The archived reports from the latest manual run, 30202839894, record:

- `cross-engine-comparator.json`: `dataset: olist_small`, `status: PASS`,
  `mismatch_count: 0`, and `mismatches: []`;
- `batch-cdc-parity.json`: `status: PASS`, `overall_parity_status: PASS`,
  `acceptance_failures: []`, `batch_airflow_state: success`,
  `ingest_airflow_state: success`, `transform_airflow_state: success`,
  `source_contract_valid: true`, and ClickHouse as the observed analytical
  warehouse type;
- `batch_reconciliation.passed: true`, with 11 reconciled raw batch entities;
- `audit.transform.status: SUCCEEDED`, with 16 files and 79 events selected;
- `parity.parity_status: PASS`, `parity.dbt_exit_code: 0`,
  `parity.command_exit_code: 0`, and `parity.failed_metrics: 0`;
- `kafka_lag.total_lag: 0` and `kafka_lag.max_lag: 0`;
- `clickhouse-candidate-1-comparator-contract.json` and
  `clickhouse-candidate-2-comparator-contract.json`: `dataset: olist_small`,
  `status: PASS`, `mismatch_count: 0`, and `mismatches: []`.

The primary workflow only succeeds when `cross-engine-comparator.json` has
`status: PASS` and `mismatch_count: 0`; otherwise
`scripts/parity/compare_manifests.py` exits non-zero.

## Open evidence

- The PostgreSQL oracle used by this workflow is the committed accepted oracle
  fixture from Phase 0. If the deterministic fixture or oracle contract
  changes, regenerate that fixture before treating a ClickHouse comparison as
  cutover evidence.

## Phase boundary

No `local_pg` profile, analytical PostgreSQL service, PostgreSQL oracle sink,
or PostgreSQL oracle documentation was removed. Phase 8 owns the default target
switch and oracle cleanup after the approved cutover gate is satisfied.
