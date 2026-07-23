# Handoff: Phase 6 - Port ClickHouse realtime dbt and quality

## Mission

Implement Phase 6 of
`docs/plans/local-clickhouse-warehouse-migration-plan.md`: port the realtime dbt
graph, realtime quality checks, transform checkpoint flow, and parity checks to
ClickHouse while keeping PostgreSQL `olist_control` authoritative for transform
state and publication approval.

## Verified Phase 5 baseline

- `warehouse_ingest.py` defaults to `--warehouse-type clickhouse` and writes
  typed raw CDC events into ClickHouse `raw_cdc`.
- PostgreSQL `olist_control` still owns file claims, attempts, leases,
  watermarks, offset coverage, reconciliation, replay requests, and ingest run
  summaries.
- `PostgresRawCdcSink` remains available behind `--warehouse-type postgres` for
  the temporary oracle period; do not remove it in Phase 6.
- ClickHouse CDC inserts use deterministic `insert_deduplication_token` values
  derived from immutable manifest/object identity and selected offsets.
- ClickHouse raw CDC retry validation uses `FINAL` readback and rejects an
  existing event identity when the payload differs.
- The ingest and backfill DAGs explicitly call
  `warehouse_ingest.py --warehouse-type clickhouse`.
- `cdc-warehouse-init` no longer bootstraps analytical PostgreSQL raw CDC DDL;
  it waits for ClickHouse and control PostgreSQL initialization.
- `realtime_transform.py prepare` can mirror immutable selected object URIs into
  ClickHouse `pipeline_runtime.cdc_transform_run_files` when
  `DBT_TARGET=local_clickhouse`.
- `cdc_selected_file_predicate` is adapter-dispatched. ClickHouse reads
  `pipeline_runtime`; PostgreSQL/Redshift continue to read `cdc_audit`.
- `fact_order_items` now aliases qualified `fact_base.*` output columns
  explicitly, preventing ClickHouse dotted output column names.
- `local_clickhouse` and `local_pg` both parse after the Phase 5 macro/source
  changes.
- ClickHouse batch `dbt build --selector batch` passes after a full-refresh and
  again as a normal incremental build.

## Required boundary

- Do not remove `local_pg`, the analytical `postgres` service, or the
  PostgreSQL oracle in Phase 6.
- Do not query PostgreSQL control tables from ClickHouse dbt models or tests.
  Use Python for operational control checks.
- Keep publication approval and transform checkpoint authority in PostgreSQL.
- Keep the seven mutable realtime models as full tables for the first
  ClickHouse parity pass:
  - `dim_customer_realtime_scd2`;
  - `dim_product_realtime_scd2`;
  - `dim_seller_realtime`;
  - `fact_order_items_realtime`;
  - `mart_daily_revenue_realtime`;
  - `mart_monthly_arpu_realtime`;
  - any associated current-state model that still depends on mutable merge
    semantics.
- Do not introduce projections, codecs, materialized views, denormalized
  ClickHouse redesigns, Keeper, replication, or sharding.
- Preserve Redshift parse/compile.

## Implementation notes

- Start by running `dbt parse` and `dbt compile` for `local_clickhouse` with the
  realtime selectors to classify dialect failures.
- Port realtime staging, history, current-state, dimensions, fact, marts, and
  parity SQL through adapter-dispatched macros rather than target-specific model
  forks.
- Replace PostgreSQL tuple comparisons, boolean expressions, timestamp casts,
  intervals, and delete pre-hooks in realtime SQL with portable macros or
  ClickHouse-specific dispatched implementations.
- Move dbt tests that depend on `cdc_audit` operational state to Python control
  checks. ClickHouse dbt should only read ClickHouse analytical/runtime
  relations.
- Refactor `realtime_transform.py` so:
  - prepare commits PostgreSQL selection first;
  - projection into `pipeline_runtime` is deterministic and retry-safe;
  - dbt build runs against `local_clickhouse`;
  - finish commits PostgreSQL checkpoints only after ClickHouse dbt and quality
    checks pass.
- Implement ClickHouse reads for custom parity reports and publication view
  updates where `realtime_transform.py` currently uses a PostgreSQL warehouse
  cursor.
- Prove transform retries are idempotent when failure occurs after projection,
  after dbt build, and before PostgreSQL finish/checkpoint.
- After parity is proven with full-table realtime models, introduce
  complete-partition replacement for realtime fact and marts.

## Suggested verification

Run at minimum:

```powershell
docker compose config --quiet
docker compose up -d airflow-postgres control-db-init clickhouse clickhouse-init minio kafka kafka-connect
uv run python -m unittest discover -s tests -p "test_clickhouse*phase*.py" -v
uv run python -m unittest discover -s tests -p "test_*control*.py" -v
uv run dbt parse --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --no-partial-parse --quiet
uv run dbt compile --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --selector realtime_transform --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'
uv run dbt compile --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_pg --selector realtime_transform --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'
```

After the graph compiles, run a bounded CDC fixture through initial snapshot,
update, hard delete, duplicate delivery, replay, transform retry, realtime
quality, and batch-to-realtime parity.

## Exit gate

- Insert, update, hard-delete, ordering, translation, and related-order realtime
  tests pass on ClickHouse.
- ClickHouse realtime transform retries are idempotent.
- Batch-to-realtime parity passes in ClickHouse.
- No ClickHouse dbt query reads PostgreSQL control state.
- Publication approval semantics remain in PostgreSQL.
- Redshift parse/compile remains green.
