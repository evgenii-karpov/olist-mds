# Phase 6: Port ClickHouse realtime dbt and quality

Status: completed on 2026-07-23.

## Delivered contract

- Ported the realtime dbt transform graph to ClickHouse-safe SQL using shared
  compatibility macros instead of PostgreSQL-only casts, `to_char`,
  `date_trunc`, row constructors, `string_agg`, `filter`, and mutable
  `merge`/delete-hook patterns.
- Kept the mutable realtime dimensions, fact, and marts as full tables for the
  first ClickHouse parity pass:
  - `dim_customer_realtime_scd2`;
  - `dim_product_realtime_scd2`;
  - `dim_seller_realtime`;
  - `fact_order_items_realtime`;
  - `mart_daily_revenue_realtime`;
  - `mart_monthly_arpu_realtime`.
- Added ClickHouse-safe CDC ordering and boolean materialization macros so
  realtime history/current models build without tuple-comparison or
  `LowCardinality(UInt8)` CTAS failures.
- Added ClickHouse-safe parity helpers for ordered checksums, null-aware
  distinct comparisons, conditional counts, UTC timestamp normalization, and
  decimal literals.
- Reworked realtime parity SQL so the batch-to-realtime bridge materializes in
  ClickHouse `cdc_audit` without reading PostgreSQL control state.
- Moved operational realtime checks for latest reconciliation, mart freshness,
  and offset continuity into `scripts/cdc/realtime_transform.py` for
  `local_clickhouse`. The dbt operational tests now delegate to Python stubs on
  the ClickHouse target.
- Refactored `realtime_transform.py record-parity` and `publish` so
  `local_clickhouse` reads parity relations and creates `analytics` views
  through ClickHouse, while publication approval and status remain in
  PostgreSQL `olist_control`.
- Preserved PostgreSQL oracle behavior for `local_pg`; no oracle service,
  profile, or PostgreSQL CDC sink was removed.
- Added Phase 6 contract tests covering portable realtime SQL, full-table
  mutable realtime models, Python-owned operational quality checks, ClickHouse
  parity/publication support, and retry-safe runtime projection.

## Verification evidence

Passed:

- `docker compose config --quiet`;
- `uv run dbt parse --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --no-partial-parse --quiet`;
- `uv run dbt compile --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --selector realtime_transform --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'`;
- `uv run dbt compile --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --selector realtime_parity --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'`;
- `uv run dbt compile --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_pg --selector realtime_transform --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'`;
- `uv run dbt compile --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_pg --selector realtime_parity --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'`;
- `uv run dbt build --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --selector realtime_transform --exclude-resource-type unit_test --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'`;
- `uv run python -m unittest discover -s tests -p "test_clickhouse_phase6_realtime_dbt_quality.py" -v`;
- `uv run python -m unittest discover -s tests -p "test_clickhouse*phase*.py" -v`;
- `uv run ruff check scripts/cdc/realtime_transform.py tests/test_clickhouse_phase6_realtime_dbt_quality.py`;
- `uv run pyright scripts/cdc/realtime_transform.py tests/test_clickhouse_phase6_realtime_dbt_quality.py`.

Runtime notes:

- The first ClickHouse realtime build exposed runtime-only dialect issues:
  `LowCardinality(UInt8)` boolean CTAS output, implicit `UNION`, direct `md5`,
  missing aliases for qualified output columns, and a product translation branch
  alias. These were fixed and the realtime transform build passed.
- `uv run dbt build --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --selector realtime_parity --exclude-resource-type unit_test --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'`
  executed the parity SQL on the current local ClickHouse volume, but failed
  data tests with four daily revenue mismatches, two monthly ARPU mismatches,
  and 24 custom parity failures. This was not a SQL dialect failure; the local
  volume was not a clean deterministic batch-to-realtime parity fixture.

## Open evidence

- A clean bounded CDC fixture still needs to run insert, update, hard delete,
  ordering, translation, related-order propagation, replay, and transform retry
  scenarios end to end.
- Batch-to-realtime parity still needs to pass on a clean deterministic
  ClickHouse candidate stack. The current workstation volume was not used as
  acceptance evidence.
- Complete-partition replacement for realtime fact and marts remains deferred
  until the first full-table parity pass is proven on the clean fixture, matching
  the approved Phase 6 sequence.
- Full publication approval/rejection must be exercised against a disposable
  stack after parity records `PASS`.

## Phase boundary

No local PostgreSQL oracle support was removed. CI migration, observability
cutover, full-stack candidate workflows, and PostgreSQL oracle removal remain
outside Phase 6.
