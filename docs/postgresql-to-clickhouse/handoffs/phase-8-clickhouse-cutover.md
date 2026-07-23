# Handoff: Phase 8 - Cut Over and Remove the PostgreSQL Oracle

## Mission

Implement Phase 8 of
`docs/plans/local-clickhouse-warehouse-migration-plan.md`: make ClickHouse the
default and only supported local analytical warehouse after the candidate gate
has passed, then remove the local PostgreSQL analytical oracle and unused
PostgreSQL warehouse code.

## Verified Phase 7 baseline

- `local_clickhouse` has dedicated CI compile/smoke coverage for batch,
  realtime transform, and realtime parity selectors.
- The manual parity workflow emits PostgreSQL oracle/comparator artifacts and
  has a two-run ClickHouse candidate evidence matrix.
- Prometheus scrapes ClickHouse directly through `clickhouse:9363`.
- The warehouse PostgreSQL exporter is absent from the ClickHouse
  observability path.
- The OLTP PostgreSQL exporter remains present for Debezium source health.
- `cdc-pipeline-exporter` supports `CDC_WAREHOUSE_TYPE=clickhouse`, reading raw
  CDC metrics from ClickHouse and control-state metrics from PostgreSQL
  `olist_control`.
- Alerting and Grafana include ClickHouse scrape health, uptime, query, failed
  query, raw freshness, and existing CDC freshness/reconciliation signals.
- Phase 7 contract tests pass under
  `tests/test_clickhouse_phase7_ci_observability.py`.

## Required boundary

- Preserve `airflow-postgres`, `oltp-postgres`, and PostgreSQL control-plane
  code.
- Preserve Redshift parse/compile validation and AWS batch behavior.
- Treat current local Docker volumes as ephemeral. Phase 8 validation may use
  `docker compose down -v` or targeted volume removal whenever a clean
  candidate/cutover run is simpler than preserving local state.

## Implementation notes

- Set the default local `DBT_TARGET` to `local_clickhouse`.
- Make ClickHouse the default local analytical path in docs, DAG defaults, CI,
  and examples.
- Remove the analytical `postgres` Compose service and active
  `olist_postgres_data` usage after the final ClickHouse-only smoke run.
- Remove `local_pg` dbt outputs and direct local analytical PostgreSQL
  dependencies/tests.
- Remove the old PostgreSQL raw loader and raw warehouse DDL only where they no
  longer serve the oracle.
- Keep `psycopg2-binary` and PostgreSQL control repositories because
  `olist_control`, Airflow metadata, and OLTP CDC source remain PostgreSQL.
- Run repository-wide searches for active local analytical PostgreSQL
  references and classify remaining hits as control, OLTP, Airflow metadata,
  Redshift, or historical docs.
- Prefer clean disposable Compose projects and volumes for the final
  ClickHouse-only smoke run; no local volume contents need to be migrated or
  preserved.

## Suggested verification

Run at minimum:

```powershell
docker compose config --quiet
uv run python -m unittest discover -s tests -p "test_clickhouse*phase*.py" -v
uv run dbt parse --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --no-partial-parse --quiet
uv run dbt compile --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --selector batch --no-partial-parse --quiet
uv run dbt compile --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --selector realtime_transform --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'
uv run dbt compile --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target redshift --no-partial-parse --quiet
```

Then run one final clean ClickHouse-only batch and realtime smoke test, plus
the canonical comparator against the latest accepted oracle/candidate manifests.

## Exit gate

- ClickHouse-only local CI is green.
- Redshift validation remains green.
- Repository search finds no active local analytical PostgreSQL path.
- Documentation describes PostgreSQL only for Airflow metadata, OLTP CDC
  source, and `olist_control`.
- Local cleanup instructions may remove obsolete warehouse and candidate
  volumes directly because current volumes are treated as disposable.
