# Handoff: Phase 2 - Separate control PostgreSQL

## Mission

Implement Phase 2 of
`docs/plans/local-clickhouse-warehouse-migration-plan.md`: provision the
dedicated `olist_control` database and role on `airflow-postgres`, split
mutable audit/control DDL out of the analytical PostgreSQL warehouse, and move
batch/CDC control clients to explicit `CONTROL_POSTGRES_*` configuration
without changing warehouse writes yet.

## Verified Phase 1 baseline

- ClickHouse server is pinned to
  `clickhouse/clickhouse-server:26.3.17.4`.
- Python/dbt dependencies are pinned in `pyproject.toml` and `uv.lock`:
  `dbt-clickhouse==1.10.1` and `clickhouse-connect==1.5.0`.
- `clickhouse` and `clickhouse-init` are valid in default Compose and affected
  profiles.
- `clickhouse-init` is idempotent on an existing volume.
- ClickHouse reports version `26.3.17.4` and timezone `UTC`.
- `raw_data`, `raw_cdc`, and `pipeline_runtime` Phase 1 tables initialize.
- `dbt debug --target local_clickhouse` succeeds from the committed
  `profiles.yml.example`.
- `local_pg` remains the default dbt target and PostgreSQL oracle.
- Phase 0 unit/oracle checks and synthetic Stage 5 remain green.

## Required boundary

- Do not port dbt model SQL in Phase 2.
- Do not change batch raw loading or CDC warehouse writes yet.
- Do not remove `local_pg`, the analytical `postgres` service, or the
  PostgreSQL oracle.
- Do not overload analytical `POSTGRES_*` variables to mean control state.
  Use only explicit `CONTROL_POSTGRES_*` variables for new control clients.
- Keep Airflow metadata and `olist_control` on the same
  `airflow-postgres` server but in different databases and roles.
- Keep ClickHouse free of PostgreSQL table engines and external PostgreSQL
  credentials.

## Implementation notes

- Add `CONTROL_POSTGRES_HOST`, `CONTROL_POSTGRES_PORT`,
  `CONTROL_POSTGRES_DB`, `CONTROL_POSTGRES_USER`, and
  `CONTROL_POSTGRES_PASSWORD_FILE` to `.env.example`, Compose, Airflow, and CI
  command environments.
- Add `control_postgres_password` to Docker secrets and support
  `CONTROL_POSTGRES_PASSWORD_SOURCE_FILE`.
- Add a `control-db-init` one-shot service that waits for
  `airflow-postgres`, creates the `olist_control` database/role
  idempotently, and applies split control DDL.
- Move mutable control/audit tables from `infra/postgres` into
  `infra/control-postgres` without changing their semantics.
- Add focused tests proving Airflow metadata and control connections point to
  different databases and roles.
- Preserve the existing analytical PostgreSQL DDL needed by the oracle until
  the later cutover/removal phases.

## Suggested verification

Run at minimum:

```powershell
docker compose config --quiet
docker compose --profile realtime-core config --quiet
docker compose up -d airflow-postgres control-db-init
docker compose up -d --force-recreate control-db-init
uv run python -m unittest discover -s tests -p "test_*control*.py" -v
uv run python -m unittest discover -s tests -p test_postgres_oracle_export.py -v
uv run dbt test --select "test_type:unit" --threads 1
uv run python scripts/ci/check_stage5_cdc_integration.py
```

## Exit gate

- Existing PostgreSQL analytical path still works.
- All mutable control state has a home in `olist_control`.
- Batch and CDC control code no longer relies on warehouse `POSTGRES_*`.
- Tests prove Airflow metadata and control connections are separated.
