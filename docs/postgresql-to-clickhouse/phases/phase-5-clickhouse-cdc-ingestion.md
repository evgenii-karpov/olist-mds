# Phase 5: Implement ClickHouse CDC ingestion

Status: completed on 2026-07-23.

## Delivered contract

- Split `scripts/cdc/warehouse_ingest.py` into an explicit raw CDC data-plane
  sink and PostgreSQL control-plane finalization. `ClickHouseRawCdcSink` is now
  the default ingest sink, while `PostgresRawCdcSink` remains available behind
  `--warehouse-type postgres` for the temporary oracle period.
- Added deterministic ClickHouse CDC insert tokens derived from immutable
  manifest/object identity, topic, partition, and offset ranges.
- Added ClickHouse `FINAL` readback for loaded CDC offsets so retries,
  duplicate delivery, and lost insert acknowledgement windows reconcile against
  one logical event per topic, partition, and offset.
- Added existing-payload validation before and after ClickHouse insert. A
  repeated object with identical coordinates but different payload fails
  instead of being hidden by `ReplacingMergeTree` replacement behavior.
- Kept claims, attempts, leases, file status, offset coverage, watermarks,
  reconciliation, replay requests, and run summaries in PostgreSQL
  `olist_control`.
- Added CDC failure-injection points for:
  - `after_clickhouse_insert_before_control_commit`;
  - `after_clickhouse_insert_acknowledgement_lost`.
- Updated `olist_cdc_ingest_local` and `olist_cdc_backfill_local` to call
  `warehouse_ingest.py --warehouse-type clickhouse`, while tagging both DAGs
  as ClickHouse plus control PostgreSQL workflows.
- Changed the realtime-core `cdc-warehouse-init` helper so it no longer
  bootstraps analytical PostgreSQL raw CDC tables. It now waits for
  `clickhouse-init` and `control-db-init`.
- Added the Phase 5 runtime transform selection projection:
  `realtime_transform.py prepare` mirrors immutable selected object URIs into
  ClickHouse `pipeline_runtime.cdc_transform_run_files` when
  `DBT_TARGET=local_clickhouse`.
- Updated `cdc_selected_file_predicate` with adapter dispatch. PostgreSQL and
  Redshift continue to use `cdc_audit` control sources; ClickHouse uses the
  short-lived `pipeline_runtime` projection.
- Added focused Phase 5 contract tests for deterministic tokens, logical
  duplicate counting, payload mismatch detection, DAG wiring, Compose wiring,
  and runtime projection.
- Fixed a ClickHouse batch graph regression discovered during the Phase 5
  handoff verification: `fact_order_items` now aliases qualified
  `fact_base.*` output columns explicitly so ClickHouse does not materialize
  dotted column names such as `fact_base.customer_unique_id`.

## Verification evidence

Passed:

- `docker compose config --quiet`;
- `docker compose up -d airflow-postgres control-db-init clickhouse clickhouse-init minio kafka kafka-connect`;
- `docker compose ps`;
- `uv run python -m unittest discover -s tests -p "test_clickhouse_phase5_cdc_ingestion.py" -v`;
- `uv run python -m unittest discover -s tests -p "test_clickhouse*phase*.py" -v`;
- `uv run python -m unittest discover -s tests -p "test_*control*.py" -v`;
- `uv run python -m unittest discover -s tests -p "test_stage4_contracts.py" -v`;
- `uv run python -m unittest discover -s tests -p "test_stage5_contracts.py" -v`;
- `uv run ruff check scripts/cdc/warehouse_ingest.py scripts/cdc/realtime_transform.py airflow/dags/olist_cdc_local.py tests/test_clickhouse_phase5_cdc_ingestion.py tests/test_clickhouse_phase4_dbt_graph.py`;
- `uv run pyright scripts/cdc/warehouse_ingest.py scripts/cdc/realtime_transform.py tests/test_clickhouse_phase5_cdc_ingestion.py`;
- `uv run dbt parse --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --no-partial-parse --quiet`;
- `uv run dbt parse --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_pg --no-partial-parse --quiet`;
- `uv run dbt build --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --selector batch --full-refresh --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'`;
- `uv run dbt build --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --selector batch --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'`.

Notes:

- An initial non-full-refresh ClickHouse batch build exposed stale/bad local
  `fact_order_items` column names from a prior run. The explicit alias fix and
  a full-refresh rebuilt the relation, after which the original non-full-refresh
  handoff command passed.
- A mistaken `ruff check` invocation against a dbt `.sql` file failed because
  Ruff parsed Jinja SQL as Python. The corrected Ruff invocation against Python
  files passed.
- No full Debezium/NiFi CDC object production run was executed in this phase
  document. The implemented ClickHouse sink behavior is covered by focused unit
  tests and the local service startup/dbt checks above.

## Phase boundary

No local PostgreSQL oracle support was removed. Realtime dbt model porting,
ClickHouse realtime quality checks, batch-to-realtime parity, publication
approval migration, observability cutover, and PostgreSQL oracle removal remain
outside Phase 5.
