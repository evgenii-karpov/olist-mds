# Handoff: Phase 7 - Migrate CI, observability, and documentation

## Mission

Implement Phase 7 of
`docs/plans/local-clickhouse-warehouse-migration-plan.md`: move local CI,
observability, runbooks, and candidate workflow evidence onto ClickHouse while
keeping the PostgreSQL oracle available until the approved cutover gate.

## Verified Phase 6 baseline

- `local_clickhouse` parses and compiles the realtime transform and parity
  selectors.
- `local_pg` still compiles the realtime transform and parity selectors for the
  temporary oracle period.
- The ClickHouse realtime transform graph builds successfully against the local
  ClickHouse server with `--exclude-resource-type unit_test`.
- Realtime staging, history, current-state, dimensions, fact, marts, and parity
  SQL no longer use PostgreSQL-only casts, `to_char`, `date_trunc`, implicit
  `UNION`, `string_agg`, `filter`, mutable `merge`, or delete pre-hooks.
- Mutable realtime dimensions, fact, and marts are full-table materializations
  for the first parity pass.
- Operational reconciliation, freshness, and offset-continuity checks for
  `local_clickhouse` are executed in Python from
  `scripts/cdc/realtime_transform.py`, not through ClickHouse queries against
  PostgreSQL control tables.
- `record-parity` reads ClickHouse `cdc_audit` parity relations when
  `DBT_TARGET=local_clickhouse`.
- `publish` creates ClickHouse `analytics` views for `local_clickhouse` while
  publication approval state remains in PostgreSQL `olist_control`.
- Phase 6 contract tests pass under
  `tests/test_clickhouse_phase6_realtime_dbt_quality.py`.

## Required boundary

- Do not remove `local_pg`, the analytical `postgres` service, or the
  PostgreSQL oracle in Phase 7.
- Do not remove `PostgresRawCdcSink`; it remains the oracle sink until Phase 8.
- Do not make ClickHouse the default `DBT_TARGET` until the Phase 8 cutover.
- Do not claim realtime parity from the current workstation volume. Use a clean
  deterministic candidate stack.
- Preserve PostgreSQL control authority for file claims, transform runs,
  reconciliation, watermarks, mart freshness, and publication approval.
- Preserve Redshift parse/compile validation.

## Implementation notes

- Add ClickHouse jobs to the affected GitHub workflows:
  `.github/workflows/ci.yml`,
  `.github/workflows/batch-cdc-parity.yml`, and
  `.github/workflows/cdc-stage6-operations.yml`.
- Run the canonical cross-engine manifest comparator against isolated
  PostgreSQL oracle and ClickHouse candidate Compose projects.
- Replace the warehouse PostgreSQL exporter with ClickHouse metrics while
  keeping OLTP PostgreSQL metrics intact.
- Update alerts, Grafana dashboards, and Stage 6 validation to use ClickHouse
  warehouse health and query metrics.
- Update README, architecture docs, Windows and macOS/Linux runbooks, CI docs,
  CDC operations docs, observability docs, `.env.example`, and dbt profile
  examples.
- Run two consecutive full-stack ClickHouse candidate workflows before moving
  to Phase 8.

## Suggested verification

Run at minimum:

```powershell
docker compose config --quiet
uv run python -m unittest discover -s tests -p "test_clickhouse*phase*.py" -v
uv run dbt compile --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --selector realtime_transform --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'
uv run dbt compile --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --selector realtime_parity --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'
uv run dbt compile --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_pg --selector realtime_parity --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'
```

Then run clean isolated PostgreSQL oracle and ClickHouse candidate stacks for
the full batch-to-realtime parity workflow.

## Exit gate

- Required CI jobs are green twice consecutively.
- Prometheus reports ClickHouse healthy and the warehouse PostgreSQL exporter is
  absent from the ClickHouse candidate path.
- Runbooks reproduce batch and realtime flows from a clean machine.
- The full deterministic ClickHouse candidate workflow produces zero semantic
  comparator mismatches.
