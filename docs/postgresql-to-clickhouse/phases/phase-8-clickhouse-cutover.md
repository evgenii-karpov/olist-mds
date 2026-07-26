# Phase 8: ClickHouse Local Warehouse Cutover

Status: completed on 2026-07-26.

## Delivered contract

- Switched the local analytical warehouse default from PostgreSQL to
  ClickHouse-only:
  - `DBT_TARGET` now defaults to `local_clickhouse`;
  - the local Airflow batch DAG exposes only the ClickHouse warehouse target;
  - local dbt and Elementary profiles no longer define `local_pg`.
- Removed the local analytical PostgreSQL service, volume, password secret,
  bootstrap DDL, raw batch loader, CDC raw sink, PostgreSQL oracle exporter,
  and PostgreSQL oracle Stage 4/5 CI scripts.
- Kept PostgreSQL where it still belongs:
  - Airflow metadata database;
  - dedicated `olist_control` control-plane database;
  - OLTP source database for Debezium;
  - Redshift production-style batch path.
- Refactored raw batch helpers so ClickHouse and Redshift share common manifest
  and audit utilities without retaining a local PostgreSQL warehouse loader.
- Moved dead-letter replay to ClickHouse raw tables while keeping replay audit
  state in PostgreSQL `olist_control`.
- Made realtime transform publication and parity ClickHouse-only. PostgreSQL
  control checks still gate mart freshness, offset continuity, reconciliation,
  and publication state.
- Made CDC raw metrics and local CDC benchmark evidence read raw CDC events from
  ClickHouse and control state from PostgreSQL `olist_control`.
- Replaced PostgreSQL oracle manifest naming with canonical manifest contracts
  and shared canonicalization helpers.
- Rationalized GitHub Actions after cutover:
  - `clickhouse-runtime-contract` is the regular ClickHouse compile/smoke and
    canonical comparator contract job;
  - `cdc-clickhouse-ingest-resilience` replaces the old PostgreSQL Stage 4
    oracle job with a ClickHouse-native bounded retry, coverage, watermark, and
    replay check;
  - the manual `Batch and CDC parity integration` workflow now only runs the
    full-stack cutover/release parity path;
  - the duplicate optional ClickHouse candidate evidence matrix was removed
    from the manual workflow;
  - source capture and operational drill workflow display names now describe
    the subsystem they validate instead of historical implementation stages.
- Updated README, CI documentation, architecture notes, runbooks, environment
  examples, and contract tests to describe the ClickHouse-only local warehouse.

## Verification evidence

Passed locally:

- `docker compose config --quiet`;
- `uv run ruff check ...` for the changed CDC, loading, parity, CI helper, and
  test files;
- `uv run python -m compileall ...` for the changed scripts;
- `uv run dbt parse --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --no-partial-parse --quiet`;
- `uv run dbt compile --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --selector batch --no-partial-parse --quiet`;
- `uv run dbt compile --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --selector realtime_transform --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'`;
- `uv run dbt compile --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --selector realtime_parity --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'`;
- `uv run dbt parse --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target redshift --no-partial-parse --quiet` with dummy Redshift connection environment;
- `uv run python -m unittest discover -s tests -p "test_clickhouse*.py" -v`;
- `uv run python -m unittest discover -s tests -p "test_stage*_contracts.py" -v`;
- `uv run python -m unittest discover -s tests -p "test_postgres_oracle_export.py" -v`;
- `uv run python -m unittest discover -s tests -p "test_dead_letter_pipeline.py" -v`;
- `uv run python -m unittest discover -s tests -p "test_ci_data_quality_failures.py" -v`;
- `uv run python -m unittest discover -s tests -p "test_control_postgres_phase2.py" -v`;
- `uv run python scripts/ci/validate_realtime_configuration.py`;
- `uv run python scripts/ci/validate_stage6_configuration.py`.
- `uv run pyright scripts/ci/check_clickhouse_cdc_ingest_resilience.py`;
- all workflow YAML files parse with `yaml.safe_load`;
- `docker compose --profile realtime-core --profile observability --profile logs config --quiet`.

Additional local service evidence:

- `docker compose up -d --wait clickhouse`;
- `docker compose run --rm clickhouse-init`;
- ClickHouse dbt `batch`, `realtime_transform`, and `realtime_parity` selector
  compiles against the initialized local ClickHouse service.
- Minimal ClickHouse CDC ingest resilience smoke:
  - `docker compose --profile realtime-core up -d --wait clickhouse airflow-postgres minio`;
  - `docker compose run --rm clickhouse-init`;
  - `docker compose run --rm control-db-init`;
  - `docker compose --profile realtime-core run --rm minio-init`;
  - `docker compose --profile realtime-core run --rm --no-deps airflow python scripts/ci/check_clickhouse_cdc_ingest_resilience.py --s3-write-access-key olist_nifi --s3-write-secret-file docker/secrets/dev/airflow_api_secret_key.txt --report data/reports/clickhouse-cdc-ingest-resilience.json`;
  - result: `status: PASS`, `failed_file_attempts: 1`, retry duplicates `4`,
    replay duplicates `4`, and ClickHouse raw rows remained `4`.

Known local limitation:

- `uv run python scripts/ci/check_airflow_dag_imports.py` on native Windows
  fails before project DAG import because Airflow imports POSIX-only `fcntl`.
  The CI path runs this check inside Linux containers.

## Phase boundary

- Phase 8 removes the local PostgreSQL analytical warehouse path. It does not
  remove PostgreSQL as a control plane, Airflow metadata store, or OLTP CDC
  source.
- Historical Phase 0-7 documents may still mention PostgreSQL oracle evidence
  because they describe prior migration stages. Active local runtime,
  workflows, runbooks, and examples now use ClickHouse for the analytical
  warehouse.
