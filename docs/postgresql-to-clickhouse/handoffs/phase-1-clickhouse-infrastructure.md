# Handoff: Phase 1 — ClickHouse dependencies and infrastructure

## Mission

Implement Phase 1 of
`docs/plans/local-clickhouse-warehouse-migration-plan.md`: add the pinned
ClickHouse dependencies, service/configuration, initialization DDL, and
`local_clickhouse` dbt/Elementary outputs while retaining `local_pg` as the
default oracle.

## Verified upstream contract

- The PostgreSQL batch fixture passes two consecutive idempotency DAG runs.
- Synthetic Stage 5 passes source ordering, translation history, related-order
  propagation, hard delete, publication, and parity-sensitivity checks.
- All 13 terminal project models have dbt unit coverage; all 21 unit tests are
  green.
- The two committed oracle manifests cover eight batch/snapshot relations and
  seven realtime/parity relations. Independent regenerations are byte-identical.
- Canonical values distinguish null and empty string, preserve string content,
  serialize decimals at declared scale, normalize timestamps to UTC microseconds,
  and hash rows after sorting columns and relations by declared grain.
- Snapshot adapter/runtime identifiers and timestamps are intentionally outside
  the parity surface; business-effective versions are authoritative.

## Required boundary

- Pin `clickhouse/clickhouse-server:26.3.17.4`,
  `dbt-clickhouse==1.10.1`, and `clickhouse-connect==1.5.0`; update
  `pyproject.toml` and `uv.lock` together.
- Keep the PostgreSQL warehouse and `local_pg` output available and default.
- Do not port shared model SQL, move control state, or change batch/CDC writes in
  Phase 1.
- Do not weaken, regenerate with different semantics, or special-case the Phase
  0 unit tests and manifests to make ClickHouse pass.
- Use a ClickHouse native host port that does not conflict with MinIO host port
  9000, and keep ClickHouse UTC with `DateTime64(6, 'UTC')` for analytical
  timestamps.
- Initialization must be idempotent on both new and existing volumes and must
  use the plan's database ownership and Docker-secret contracts.

## Acceptance evidence to produce

- Compose validation for the default and affected profiles;
- ClickHouse health and version output on the pinned image;
- repeated initialization against the same volume;
- `dbt debug --target local_clickhouse` and a trivial connection smoke query;
- dbt parse/compile for the retained PostgreSQL and Redshift profiles;
- all Phase 0 Python and dbt unit tests still green.

## Useful Phase 0 commands

```powershell
uv run python -m unittest discover -s tests -p test_postgres_oracle_export.py -v
uv run dbt test --select "test_type:unit" --threads 1
uv run python scripts/ci/check_stage5_cdc_integration.py
```

Run dbt commands from `dbt/olist_analytics` with `DBT_PROFILES_DIR` pointing to
that directory. The compact inventory and oracle artifacts live under
`tests/fixtures/postgresql_oracle/`.
