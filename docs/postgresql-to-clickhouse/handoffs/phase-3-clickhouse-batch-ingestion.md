# Handoff: Phase 3 - Implement ClickHouse batch ingestion

## Mission

Implement Phase 3 of
`docs/plans/local-clickhouse-warehouse-migration-plan.md`: add the local
ClickHouse batch raw loader, staging lifecycle, atomic partition replacement,
ClickHouse row-count reconciliation, candidate DAG wiring, failure injection,
and idempotency tests while keeping the PostgreSQL oracle available.

## Verified Phase 2 baseline

- `control-db-init` provisions `olist_control` and the `olist_control` role on
  the existing `airflow-postgres` service.
- Airflow metadata and pipeline control state use different PostgreSQL
  databases and roles on the same server.
- Batch control defaults resolve from `CONTROL_POSTGRES_*`, not analytical
  warehouse `POSTGRES_*`.
- Local batch raw loading and reconciliation use analytical PostgreSQL for raw
  table operations and `olist_control` for mutable audit/control state.
- CDC ingest and realtime transform control state now use `olist_control`.
- Analytical PostgreSQL, `local_pg`, and existing PostgreSQL raw/CDC DDL remain
  available as the oracle.
- ClickHouse Phase 1 infrastructure remains initialized through
  `clickhouse-init`.

## Required boundary

- Do not port shared dbt model SQL in Phase 3 except for loader-adjacent
  source/reconciliation plumbing that is strictly required.
- Do not remove `local_pg`, the analytical `postgres` service, or the
  PostgreSQL oracle.
- Do not move CDC raw event writes to ClickHouse in Phase 3.
- Do not query PostgreSQL control tables from ClickHouse or dbt.
- Keep all batch run status transitions in `olist_control`.
- Treat ClickHouse and PostgreSQL control commits as cross-store operations:
  write deterministic ClickHouse data, read it back, then commit control
  success.

## Implementation notes

- Add a ClickHouse batch loader under `scripts/loading` rather than modifying
  the PostgreSQL loader in place.
- Use deterministic staging table names or a bounded staging namespace keyed by
  batch/run/entity.
- Load prepared gzip CSV/correction files into ClickHouse staging tables,
  validate row counts and schemas, then replace the target raw partition
  atomically.
- Keep batch raw tables in `raw_data` and use the Phase 1 ClickHouse DDL as the
  target contract.
- Add ClickHouse reconciliation queries in Python. Do not expose
  `olist_control.audit` through a ClickHouse PostgreSQL table engine.
- Wire the local batch DAG behind explicit candidate configuration so the
  PostgreSQL oracle path remains runnable.
- Add failure injection around staging insert, staging validation, partition
  replacement, target read-back, and PostgreSQL control success update.
- Add focused tests proving identical ClickHouse batch reruns leave identical
  logical raw counts.

## Suggested verification

Run at minimum:

```powershell
docker compose config --quiet
docker compose up -d postgres airflow-postgres control-db-init clickhouse clickhouse-init
uv run python -m unittest discover -s tests -p "test_*clickhouse*batch*.py" -v
uv run python -m unittest discover -s tests -p "test_*control*.py" -v
uv run dbt test --select "test_type:unit" --threads 1
```

When the candidate DAG is wired, also run the bounded small-fixture candidate
twice and record the raw ClickHouse counts after each run.

## Exit gate

- The small batch fixture loads into ClickHouse raw tables.
- Two identical ClickHouse candidate runs produce identical logical raw counts.
- A failed candidate run can resume without manual ClickHouse table cleanup.
- Batch status and reconciliation state are committed only to `olist_control`.
- The PostgreSQL oracle remains runnable for comparison.
