# Phase 4: Port the ClickHouse batch dbt graph

Status: completed on 2026-07-23.

## Delivered contract

- Added adapter-dispatched compatibility macros in
  `dbt/olist_analytics/macros/warehouse_compat.sql` for portable casts,
  timestamp/date literals, nullable window values, date arithmetic, date parts,
  month starts, date keys, month labels, and stable hash keys.
- Ported batch-selected staging, intermediate, core, mart, snapshot-dependent,
  and batch quality SQL away from direct PostgreSQL syntax. The shared batch
  SQL now avoids direct `::`, `to_char`, `extract`, `date_trunc`, and `md5`
  usage in the batch graph.
- Moved `fact_order_items` from the temporary full-table ClickHouse parity
  materialization to incremental `insert_overwrite` partition replacement,
  while preserving the existing PostgreSQL/Redshift incremental `delete+insert`
  path and pre-hook.
- Added a project-level ClickHouse partition replacement override for
  `fact_order_items` so affected non-empty partitions are replaced and affected
  target partitions that become empty are explicitly dropped.
- Fixed ClickHouse-specific SCD2 behavior by making `lead(valid_from)` operate
  on nullable window values, so final SCD2 rows keep `valid_to = null` instead
  of ClickHouse's non-null timestamp default.
- Normalized payment allocation decimals to `decimal(18, 2)` so ClickHouse
  marts can safely coalesce allocated payment value with gross item amount.
- Removed `target.database` from dbt source definitions so `local_clickhouse`
  can parse; schemas still resolve to `raw_data` and `audit`.
- Kept operational batch reconciliation out of ClickHouse dbt. The
  ClickHouse branch of `assert_batch_reconciliation_passed` is a no-row
  analytical placeholder, while authoritative reconciliation remains in
  `scripts/quality/reconcile_batch.py` and `olist_control`.
- Updated `olist_modern_data_stack_local` so `warehouse_target=clickhouse`
  runs dbt and Elementary with `DBT_TARGET=local_clickhouse`; PostgreSQL
  remains the default oracle path.
- Added `scripts/parity/export_clickhouse_candidate.py` to export canonical
  ClickHouse manifests using the existing PostgreSQL oracle relation contract.
- Added `scripts/parity/compare_manifests.py` to compare oracle and candidate
  manifests on relation presence, semantic column contracts, row count,
  duplicate grain count, grain keys, per-row hashes, aggregate hashes, and
  metrics.
- Added focused Phase 4 tests for batch SQL portability, fact incremental
  materialization boundaries, DAG dbt target routing, ClickHouse semantic type
  mapping, and manifest comparator failures.

## Verification evidence

Passed:

- `uv run dbt parse --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --no-partial-parse`;
- `docker compose up -d clickhouse clickhouse-init`;
- `uv run dbt build --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --selector batch --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'`;
- `uv run dbt build --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --selector batch --full-refresh --vars '{"batch_date":"2018-09-01","lookback_days":3}' --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'`;
- `uv run dbt build --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --selector batch --vars '{"batch_date":"2018-09-01","lookback_days":3}' --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'`;
- `uv run python -m unittest discover -s tests -p "test_clickhouse_phase4_dbt_graph.py" -v`;
- `uv run python -m unittest discover -s tests -p "test_clickhouse_batch_phase3.py" -v`;
- `uv run ruff check airflow/dags/olist_modern_data_stack_local.py scripts/parity/export_clickhouse_candidate.py scripts/parity/compare_manifests.py tests/test_clickhouse_phase4_dbt_graph.py tests/test_clickhouse_batch_phase3.py`;
- `uv run dbt parse --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_pg --no-partial-parse --quiet`;
- `docker compose up -d postgres`;
- `uv run dbt compile --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_pg --selector batch --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'`.
- clean `olist_small` PostgreSQL oracle run:
  - prepared source and correction files under
    `data/ci/raw/phase4-parity-clean`;
  - loaded all 11 raw entities into analytical PostgreSQL;
  - reconciled `11/11` entities with
    `scripts/quality/reconcile_batch.py --warehouse-type postgres`;
  - `uv run dbt build --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_pg --selector batch --vars '{"batch_date":"2018-09-01","lookback_days":3}' --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'`;
  - exported `data/reports/postgres_batch_oracle_phase4.json`;
- clean `olist_small` ClickHouse candidate run:
  - prepared the same source and correction fixture under the ClickHouse run id;
  - loaded all 11 raw entities into ClickHouse `raw_data`;
  - reconciled `11/11` entities with
    `scripts/quality/reconcile_batch.py --warehouse-type clickhouse`;
  - `uv run dbt build --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --selector batch --vars '{"batch_date":"2018-09-01","lookback_days":3}' --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'`;
  - exported `data/reports/clickhouse_batch_candidate_phase4.json`;
- `uv run python scripts/parity/compare_manifests.py --oracle data/reports/postgres_batch_oracle_phase4.json --candidate data/reports/clickhouse_batch_candidate_phase4.json --output data/reports/batch_phase4_compare.json`;
- `data/reports/batch_phase4_compare.json` reported
  `status=PASS`, `mismatch_count=0`, and no mismatches.
- after the ClickHouse incremental conversion, direct ClickHouse inspection
  confirmed `core.fact_order_items` uses `MergeTree`, partitions by
  `toYYYYMM(coalesce(toDate(order_purchase_timestamp), toDate('1900-01-01')))`,
  orders by `order_purchase_timestamp, order_id, order_item_id`, and leaves no
  `core.fact_order_items__affected_partitions` helper table after cleanup;
- direct ClickHouse DDL validation confirmed `DROP PARTITION ID` works for
  retry-safe empty affected partition cleanup, which the override executes per
  affected partition;
- `uv run python scripts/ci/check_clickhouse_fact_insert_overwrite_edges.py`
  passed against local ClickHouse. The fixture builds a baseline
  `fact_order_items` table with January and February purchase partitions, then
  moves one order into February and removes the only January-only order before
  an ordinary incremental build. The final assertion verifies only active
  partition `201802` remains, stale fact rows are gone, and the affected
  partitions helper table is cleaned up.
- Added the `clickhouse-incremental-edges` job to the regular `CI` workflow so
  the destructive local ClickHouse edge fixture runs on pull requests and pushes
  to `main`/`master`.
- post-review parity hardening added `core.dim_date` to the oracle/candidate
  relation contract and made the comparator validate semantic column contracts;
  the refreshed `data/reports/batch_phase4_compare.json` still reports
  `status=PASS` and `mismatch_count=0`.

Notes:

- The local ignored `dbt/olist_analytics/profiles.yml` was patched to include
  `local_clickhouse` for verification. The committed source of truth remains
  `profiles.yml.example`.
- The first parity comparison exposed surrogate-key and decimal-scale
  mismatches. The final run passed after normalizing timestamp strings used in
  SCD2 hash keys and explicitly casting derived decimal measures.
- Existing local ClickHouse `fact_order_items` tables created during the
  temporary full-table parity implementation need one `--full-refresh` after
  this change so their sorting key matches the incremental replacement staging
  table. Normal reruns use `insert_overwrite`.

## Follow-up parity runbook

To reproduce the final comparison after both targets are built from the same
deterministic fixture, run:

```powershell
uv run python scripts/parity/export_postgres_oracle.py --output data/reports/postgres_batch_oracle_phase4.json
uv run python scripts/parity/export_clickhouse_candidate.py --password-file docker/secrets/dev/clickhouse_password.txt --output data/reports/clickhouse_batch_candidate_phase4.json
uv run python scripts/parity/compare_manifests.py --oracle data/reports/postgres_batch_oracle_phase4.json --candidate data/reports/clickhouse_batch_candidate_phase4.json --output data/reports/batch_phase4_compare.json
```

To reproduce the destructive local ClickHouse incremental edge fixture, run:

```powershell
uv run python scripts/ci/check_clickhouse_fact_insert_overwrite_edges.py
```

This script resets local ClickHouse raw and derived databases before building
its minimal moved/deleted/empty-partition fixture.

The same fixture is part of the regular GitHub Actions `CI` workflow through
the `clickhouse-incremental-edges` job.

## Phase boundary

No local PostgreSQL oracle support was removed. CDC ingestion and realtime dbt
remain outside the Phase 4 implementation boundary. ClickHouse performance
tuning, projections, codecs, and denormalized table redesigns remain deferred.
