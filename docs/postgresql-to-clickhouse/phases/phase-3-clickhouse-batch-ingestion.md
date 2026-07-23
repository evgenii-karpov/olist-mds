# Phase 3: Implement ClickHouse batch ingestion

Status: completed on 2026-07-23.

## Delivered contract

- Added `scripts/loading/load_raw_to_clickhouse.py` as a separate ClickHouse
  raw batch loader. The PostgreSQL loader remains unchanged and available for
  the oracle path.
- Implemented deterministic ClickHouse staging table names under `raw_data`.
  Each entity load drops any stale staging table, creates a fresh staging table
  from the target raw table, loads prepared gzip CSV with `CSVWithNames`,
  validates staging row counts, replaces the `_batch_id` partition atomically,
  reads the target count back, and only then records success in
  `olist_control.audit.load_runs`.
- Added failure injection points around the required Phase 3 windows:
  `before_staging_insert`, `after_staging_insert`,
  `after_staging_validation`, `after_partition_replacement`,
  `after_target_readback`, and `before_control_success`.
- Kept dead-letter audit and load-run audit in `olist_control`; ClickHouse does
  not query PostgreSQL control tables.
- Extended `scripts/quality/reconcile_batch.py` with
  `--warehouse-type clickhouse`, preserving PostgreSQL as the default.
  ClickHouse reconciliation counts raw rows from `raw_data` and writes
  reconciliation results to `olist_control`.
- Updated `olist_modern_data_stack_local` with explicit candidate parameters:
  `warehouse_target` defaults to `postgres` and can be set to `clickhouse`;
  `run_dbt` defaults to `true` and can be disabled for Phase 3 raw-load
  candidate runs until Phase 4 ports the dbt batch graph.
- Added focused Phase 3 tests for staging naming, schema drift detection,
  ClickHouse CSV insert settings, ClickHouse row-count reconciliation, failure
  point coverage, and candidate DAG wiring.

## Verification evidence

Passed:

- `docker compose config --quiet`;
- `docker compose up -d postgres airflow-postgres control-db-init clickhouse clickhouse-init`;
- `docker compose build airflow`, after the existing local image was found to
  be stale and missing the Phase 1 ClickHouse Python dependency;
- small fixture preparation with
  `scripts/ingestion/prepare_olist_raw_files.py`;
- correction feed generation with
  `scripts/ingestion/generate_correction_feeds.py`;
- first ClickHouse load of all 11 `raw_data` batch tables from the small
  fixture;
- ClickHouse reconciliation reporting `11/11` entities passed;
- a second identical ClickHouse load of the same batch;
- a second reconciliation reporting `11/11` entities passed;
- direct ClickHouse row-count read-back after the repeated run:
  - `customers`: 8;
  - `geolocation`: 6;
  - `order_items`: 16;
  - `order_payments`: 14;
  - `order_reviews`: 12;
  - `orders`: 12;
  - `products`: 8;
  - `sellers`: 4;
  - `product_category_translation`: 5;
  - `customer_profile_changes`: 6;
  - `product_attribute_changes`: 8;
- injected failure at `after_partition_replacement`, followed by a normal
  retry without manual ClickHouse cleanup and a final reconciliation reporting
  `11/11` entities passed;
- `uv run python -m unittest discover -s tests -p "test_clickhouse*phase*.py" -v`;
- `uv run python -m unittest discover -s tests -p "test_control_postgres_phase2.py" -v`;
- targeted `uv run ruff check` over changed Python and DAG files.

Notes:

- The Windows host cannot connect to `olist_control` through `localhost:5432`
  while the analytical PostgreSQL oracle owns that port. Containerized smoke
  commands were run through the `airflow` service so `CONTROL_POSTGRES_HOST`
  resolves to the internal `airflow-postgres` service.
- The Phase 3 candidate DAG is raw-load capable, but dbt remains disabled for
  ClickHouse candidate runs until Phase 4 ports the batch graph.

## Phase boundary

No shared dbt model SQL was ported, `local_pg` remains the default dbt target,
the analytical PostgreSQL service remains the oracle, and CDC raw event writes
remain PostgreSQL-backed. Phase 3 only adds ClickHouse batch raw ingestion,
ClickHouse raw row-count reconciliation, candidate DAG wiring, and focused
failure/idempotency coverage.
