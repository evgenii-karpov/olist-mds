# WP8 — Transaction-Complete Boundary Planner Report

Date: 2026-08-07
Branch: `gcp-bigquery-dual-contour`

## Status

**Credential-free implementation complete; cloud closeout pending.**

The planner and BigQuery control adapter now contain the local, statically
verifiable part of WP8. No GCP credentials, BigQuery jobs, or cloud resources
were used in this work. The stage is not marked fully closed because the
transaction metadata bridge, multi-statement transactions, and Silver
progress must still be executed against the real Lakehouse catalog.

## Implemented

- Added `V004__transaction_boundary_bridge.sql`, a read-only BigQuery view over
  `audit.mysql_transactions` with explicit casts for transaction status,
  offsets, timestamps, nested collection counts, and rejected event IDs.
- Added `BigQueryServingControlRepository.fetch_transaction_rows()` as the
  Debezium transaction-metadata reader.
- Added `check_silver_progress()` and `revalidate_silver_progress()`. They
  select the latest row per source topic/partition and return `WAITING` unless
  every requested partition is `COMMITTED` at or beyond its frozen offset.
  Entity/topic filters use named array parameters with `IN UNNEST(@param)`.
- Added atomic boundary persistence. It records the predecessor, transaction
  coordinates, per-topic/partition previous and target offsets, snapshot IDs,
  and deterministic boundary IDs, and changes a GCP run from `PLANNING` to
  `MATERIALIZING` only when the expected predecessor still matches.
- Boundary persistence is idempotent for the same boundary and does not delete
  or replace an already persisted interval. A conflicting boundary ID fails the
  guarded update and rolls back the transaction.
- Removed the old planner fallback that represented a boundary as a single
  transaction-topic end offset. Missing per-topic/partition progress now fails
  closed with `INVARIANT_FAILURE`.
- Extended same-sequence retry cleanup to all eight BigQuery Gold history
  tables as well as entity and model result rows; the frozen boundary remains
  intact.

## Static evidence

```text
uv run pytest tests/serving/test_boundary.py tests/serving/test_bigquery_control.py tests/gcp/test_migrations.py -q
31 passed, 1 warning

uv run ruff check scripts/serving/boundary.py scripts/serving/bigquery_control.py tests/serving/test_boundary.py tests/serving/test_bigquery_control.py tests/gcp/test_migrations.py
All checks passed!

uv run pyright scripts/serving/boundary.py scripts/serving/bigquery_control.py tests/serving/test_boundary.py tests/serving/test_bigquery_control.py
0 errors, 0 warnings, 0 informations

uv run sqlfluff parse sql/bigquery/migrations/V004__transaction_boundary_bridge.sql --templater raw --dialect bigquery
BigQuery SQL parsed
```

The warning is the existing Windows pytest-cache permission warning; it did
not affect test execution.

## Documentation basis

The SQL contracts were checked against the Google Developer Knowledge MCP
documentation for [multi-statement transactions](https://docs.cloud.google.com/bigquery/docs/transactions),
the [procedural language and transaction statements](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language),
the [read-only `@@row_count` system variable](https://docs.cloud.google.com/bigquery/docs/reference/system-variables),
[array query parameters](https://docs.cloud.google.com/bigquery/docs/parameterized-queries),
and [`PARSE_JSON`](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/json_functions).

## Required cloud closeout

Before this stage can be marked fully complete, run and record:

1. V001–V004 rendering/application in the real GCP project and migration-ledger
   job IDs;
2. direct-versus-bridge schema, nested-array, nullability, timestamp, and row
   count checks for `audit.mysql_transactions` and `audit.silver_progress`;
3. a multi-topic/multi-partition transaction fixture proving that frozen
   offsets do not split a source transaction;
4. a real `audit.silver_progress` catch-up and post-build revalidation;
5. same-sequence retry and stale-predecessor conflict execution through the
   official BigQuery client.

No cloud run ID exists yet because GCP access was intentionally unavailable.
