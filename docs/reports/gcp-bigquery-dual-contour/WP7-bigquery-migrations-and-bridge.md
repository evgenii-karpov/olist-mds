# WP7 — BigQuery Migrations and Bridge Report

Date: 2026-08-07
Branch: `gcp-bigquery-dual-contour`

## Status

**Cloud execution is pending WP5 and GCP access.**

The credential-free migration/bridge foundation is implemented. This stage is
not claimed fully closed because WP5 has not produced the required
`GO`/`GO-WITH-CONSTRAINTS` decision and no BigQuery job has verified the
P.C.N.T source relation or the native bridge views.

## Implemented

- Added `V002__bridge_views.sql` with four native, read-only BigQuery views:

  - `olist_lakehouse_bridge.bronze_mysql_cdc_records`;
  - `olist_lakehouse_bridge.silver_order_items_changes`;
  - `olist_lakehouse_bridge.reference_geolocation`;
  - `olist_lakehouse_bridge.audit_silver_progress`.

- Added `V003__gold_source_bridge_views.sql` with seven additional native,
  read-only views for the remaining `silver.*_changes` entities needed by the
  independent BigQuery Gold project. The existing V002 order-item view is
  intentionally not redefined.

- Each view uses explicit casts for UTC timestamps, `INT64`, `NUMERIC`,
  `BIGNUMERIC`, `BYTES` and the Bronze nested header array. It never writes to
  the Lakehouse source and never references Iceberg metadata tables.
- Added `scripts/gcp/migrations.py` for ordered migration discovery,
  contiguous-version validation, source SHA-256 manifests and strict local
  rendering of `project_id`/`catalog_id` placeholders.
- Added `lab.py gcp migrate status|render|apply`. `status` and `render` are
  cloud-independent; `apply` fails closed until a real GCP preflight and
  operator-approved cloud run are available.
- Documented SQL ownership and the required post-apply direct-vs-bridge
  checks in `sql/bigquery/migrations/README.md`.

The bridge syntax and transaction conventions were checked against Google
Developer Knowledge MCP documentation:

- [BigQuery data definition language](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/data-definition-language)
- [BigQuery procedural language](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/procedural-language)
- [Query Iceberg tables with Lakehouse](https://docs.cloud.google.com/lakehouse/docs/query-iceberg-tables-with-lakehouse)

The Google documentation confirms native BigQuery `CREATE OR REPLACE VIEW`
syntax and multi-statement transaction syntax. It did not independently
confirm the four-part P.C.N.T identifier inside a native view definition, so
that exact compatibility remains an explicit WP5 cloud gate rather than an
assumption.

## Evidence without GCP

```text
uv run python scripts/lab.py gcp migrate status
status: ready
migrations: V001__control_tables, V002__bridge_views, V003__gold_source_bridge_views
cloud_execution: NOT_RUN

uv run python scripts/lab.py gcp migrate render \
  --project-id demo-project \
  --catalog-id demo-lakehouse-catalog \
  --output data/acceptance/gcp/rendered-migrations
status: accepted

uv run sqlfluff parse data/acceptance/gcp/rendered-migrations/V002__bridge_views.sql \
  --templater raw --dialect bigquery
BigQuery bridge SQL parsed

uv run pytest -q tests/gcp tests/serving tests/lakehouse_platform tests/orchestration
120 passed, 1 skipped
```

Static tests also verify migration order/checksums, placeholder safety, all
four source relations, explicit cast presence, read-only behavior and absence
of `.snapshots`/`.files` references.

## Required cloud closeout

After WP5 accepts the direct P.C.N.T path, render with real IDs, apply V001–V003
through the future BigQuery job runner, record migration-ledger rows and
job IDs, then compare direct and bridge schemas, counts, null/deletion
semantics, timestamps, decimals, binary and nested fields during Spark
commits. Only then can the stage be marked complete.
