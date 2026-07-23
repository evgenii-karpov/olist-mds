# Handoff: Phase 4 - Port the dbt batch graph

## Mission

Implement Phase 4 of
`docs/plans/local-clickhouse-warehouse-migration-plan.md`: make the batch dbt
graph compile and build against `local_clickhouse`, keep PostgreSQL as the
oracle, compare published batch outputs across engines, and defer performance
tuning until semantic parity is proven.

## Verified Phase 3 baseline

- ClickHouse infrastructure from Phase 1 is active and initializes
  `raw_data`, `raw_cdc`, and `pipeline_runtime`.
- `olist_control` from Phase 2 remains the authoritative store for batch audit,
  dead-letter audit, reconciliation, and batch status.
- `scripts/loading/load_raw_to_clickhouse.py` loads all 11 batch raw entities
  into ClickHouse through deterministic staging tables and atomic
  `_batch_id` partition replacement.
- `scripts/quality/reconcile_batch.py --warehouse-type clickhouse` reconciles
  prepared raw files against ClickHouse raw counts while writing results only
  to `olist_control`.
- `olist_modern_data_stack_local` has explicit candidate parameters:
  `warehouse_target=clickhouse` for raw loading and `run_dbt=false` for the
  Phase 3 candidate boundary.
- The PostgreSQL oracle path remains runnable through the default
  `warehouse_target=postgres`, `run_dbt=true`, and `DBT_TARGET=local_pg`.
- Small fixture evidence exists for:
  - initial ClickHouse raw load;
  - identical rerun with identical logical raw counts;
  - injected failure after partition replacement followed by retry without
    manual table cleanup.

## Required boundary

- Do not remove `local_pg`, the analytical `postgres` service, or the
  PostgreSQL oracle in Phase 4.
- Do not move CDC raw event writes or realtime dbt models to ClickHouse in
  Phase 4.
- Do not query `olist_control` from ClickHouse or dbt.
- Keep `fact_order_items` as a full table until parity is proven.
- Avoid ClickHouse-specific performance features such as projections, codecs,
  materialized views, or denormalized tables unless the migration plan is
  amended.
- Preserve the Redshift target and keep shared SQL adapter-dispatched rather
  than forking the dbt project.

## Implementation notes

- Start by running `dbt parse` and `dbt compile` for `local_clickhouse` to
  classify dialect failures.
- Add adapter-dispatched macros for casts, timestamps, date arithmetic,
  string aggregation, hashing, and target-specific relation behavior.
- Replace PostgreSQL-only syntax in batch-selected models and tests with
  shared macros or adapter-specific macro implementations.
- Revisit materializations for the known Phase 4 decision points:
  `fact_order_items`, snapshots, marts, and any incremental models with
  PostgreSQL `DELETE` pre-hooks or unsupported `merge` behavior.
- Keep ClickHouse operational checks in Python when they need control state;
  dbt models and tests should read ClickHouse analytical relations only.
- Compare ClickHouse batch leaf outputs against PostgreSQL oracle outputs with
  row counts, grain-key checks, and canonical hashes before changing
  materialization strategies.
- Once the graph builds, update the local DAG so `warehouse_target=clickhouse`
  can run dbt with `DBT_TARGET=local_clickhouse` instead of requiring
  `run_dbt=false`.

## Suggested verification

Run at minimum:

```powershell
docker compose config --quiet
docker compose up -d postgres airflow-postgres control-db-init clickhouse clickhouse-init
docker compose build airflow
uv run python -m unittest discover -s tests -p "test_clickhouse*phase*.py" -v
uv run python -m unittest discover -s tests -p "test_*control*.py" -v
docker compose run --rm --no-deps airflow dbt --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics parse --target local_clickhouse --no-partial-parse
docker compose run --rm --no-deps airflow dbt --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics compile --target local_clickhouse
```

After the first successful compile/build, run the small fixture once through
the PostgreSQL oracle and once through the ClickHouse candidate, then compare
the batch leaf outputs before broadening the fixture scope.

## Exit gate

- Batch-selected dbt models, snapshots, unit tests, data tests, and Elementary
  run against ClickHouse.
- PostgreSQL oracle batch outputs and ClickHouse candidate batch outputs match
  on row counts, grain keys, and canonical hashes.
- Repeated ClickHouse batch builds are stable.
- `fact_order_items` remains a full table unless the plan's monthly
  `insert_overwrite` validation is complete.
- Redshift parse/compile remains green.
