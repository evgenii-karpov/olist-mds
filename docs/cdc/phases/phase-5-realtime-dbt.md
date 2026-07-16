# Phase 5: Realtime dbt models and DAG separation

Status: implemented and semantically verified on 2026-07-16. The formal
30-minute reference-load end-to-end SLO benchmark remains a manual/nightly gate
and is not claimed by the bounded integration run.

## Delivered contract

- Eight `raw_cdc` sources feed lossless event views, source-ordered current
  views, and complete histories. Current/history use `_source_lsn`, transaction
  order, partition, and offset; load timestamps do not decide business state.
- `cdc_transform_runs` and `cdc_transform_run_files` capture exact immutable
  manifest membership. Membership remains owned across failures, retries reuse
  it, and a session advisory lock serializes dbt through the completion
  checkpoint. `dbt_completed_at` prevents completion after a failed invocation.
- Changed-key propagation covers direct order/item/payment and indirect
  customer/product/seller/category changes. Old and new dates/months come from
  event history.
- Realtime dimensions, current order-item fact, daily revenue, and monthly ARPU
  use separate schemas. Payment allocation is shared with batch through one
  macro.
- `olist_cdc_transform_local` is Asset-triggered;
  `olist_cdc_quality_local` runs hourly and adds full dbt/Elementary at midnight.
- Parity reports compare counts, PK checksums, current attributes, fact/payment
  totals, daily revenue, and monthly revenue with `0.01` monetary tolerance.
  `analytics` views switch only through an explicit parity-gated command.
- This phase ships the local PostgreSQL/Airflow adapter. The independent
  AWS/Redshift DAGs and packaging remain Phase 7 work under ADR-009.

## Verification evidence

- dbt parse/compile passed with dbt Core 1.11.8 and dbt-postgres 1.10.0.
- Full-refresh realtime build passed all 135 selected operations: 35 models,
  94 data tests, 4 unit tests, and 2 hooks (dbt Core 1.11.8/Postgres adapter
  1.10.0).
- The disposable integration executed three real manifest-bounded transforms:
  seven snapshot files, three order updates (including a later warehouse arrival
  with older source LSN), and one hard delete. It verified source-latest state,
  four retained order history rows, fact/mart deletion, delete history, and the
  reversible `realtime -> batch` publication round trip.
- The product SCD2 unit fixture proves that a later translation cannot restore
  an obsolete category or resurrect a deleted product.
- Python tests passed (68, with 1 intentional skip); Ruff, formatting, Pyright,
  and full dbt-templated SQLFluff passed.
- The integration used the healthy Compose PostgreSQL service and a disposable
  database; all three dbt micro-batches succeeded and cleanup completed.
- An independent Docker check confirmed Docker Engine 29.6.1/Desktop 4.82.0
  and 9 healthy Compose services. `docker compose config --quiet` passed, and
  the Airflow container import check loaded all 6 repository DAGs.

## Remaining operational evidence

The 5 lifecycles/second 30-minute reference workload, burst workload, and p95
commit-to-published-mart measurement require the full continuous stack. They
remain a release gate; this record does not infer the SLO from dbt runtime.

## Commands

```powershell
$env:UV_CACHE_DIR="$PWD\.uv-cache"
uv run python scripts/ci/check_stage5_cdc_integration.py
uv run python scripts/cdc/realtime_transform.py record-parity
uv run python scripts/cdc/realtime_transform.py publish `
  --target realtime --approved-by operator
```
