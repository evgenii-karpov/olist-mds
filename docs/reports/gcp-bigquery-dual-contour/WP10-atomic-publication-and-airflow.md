# WP10 — Atomic Publication and GCP DAG

Date: 2026-08-07
Branch: `gcp-bigquery-dual-contour`

## Status

**Credential-free publication foundation implemented; WP10 is not fully
closed.**

The local work adds the SQL-owned Gold current state and the versioned
publication procedure. No BigQuery job, GCP resource, Airflow run, or cloud
credential was used. The GCP DAG, restricted Docker API invocation, failure
injection, compensation-run, and real retry/conflict acceptance remain
pending.

## Implemented

- Added `V005__gold_current_and_publication.sql` with eight explicit
  `olist_gold_store.<model>__current` schemas.
- Added stable `olist_gold.<model>` views over the current tables.
- Added `olist_serving_control.publish_gcp_run(sync_run_seq,
  expected_active_sync_run_seq)`.
- The procedure checks run readiness and all eight model/entity result sets,
  handles already-active idempotency, rejects stale predecessors, applies
  replace-grain and merge operations inside one BigQuery transaction, and
  advances both publication pointers only after a compare-and-set row-count
  check.
- A failed compare-and-set rolls back candidate/current mutations and records
  a terminal publication-drift conflict without overwriting a newer active
  sequence.
- Current facts and marts have explicit date partitioning and business-key
  clustering; small dimensions are clustered by their serving key.

## Static evidence

```text
uv run pytest tests/gcp/test_migrations.py -q
9 passed, 1 warning

uv run sqlfluff parse sql/bigquery/migrations/V005__gold_current_and_publication.sql \
  --templater raw --dialect bigquery
SQLFLUFF_PARSE_OK

uv run dbt parse --project-dir dbt/olist_bigquery \
  --profiles-dir dbt/olist_bigquery --no-partial-parse
dbt=1.11.8; adapter bigquery=1.11.3; parse passed

uv run ruff check tests/gcp/test_migrations.py
All checks passed!

uv run pyright tests/gcp/test_migrations.py
0 errors, 0 warnings, 0 informations

uv run python scripts/lab.py gcp migrate status
5 ordered migrations; status=ready; cloud_execution=NOT_RUN
```

The pytest warning is the existing Windows cache-directory permission
warning. It does not affect test execution.

## Documentation basis

The procedure syntax and transaction safeguards were checked against the
Google Developer Knowledge MCP documentation for [multi-statement
transactions](https://docs.cloud.google.com/bigquery/docs/transactions), the
[procedural language](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language),
[`@@row_count`](https://docs.cloud.google.com/bigquery/docs/reference/system-variables),
and [clustered and partitioned table DDL](https://docs.cloud.google.com/bigquery/docs/creating-clustered-tables).

## Required cloud closeout

Before WP10 can be marked fully complete, execute and record:

1. V001–V005 application and migration-ledger evidence in the real project;
2. procedure execution for initial, incremental, same-run retry, stale
   predecessor, injected DML failure, and compensating-run cases;
3. proof that a failed transaction leaves every current table, pointer, and
   status unchanged except for the explicitly recorded failure/conflict row;
4. implementation and import/run evidence for `olist_gcp_serving`;
5. restricted Docker API and dbt artifact collection evidence, with no
   long-lived streaming owned by Airflow.

No cloud run ID exists because GCP access was intentionally unavailable.
