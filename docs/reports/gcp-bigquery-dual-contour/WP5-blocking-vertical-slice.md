# WP5 — Blocking GCP Vertical Slice Report

Date: 2026-08-07
Branch: `gcp-bigquery-dual-contour`

## Status

**Not closed: `PENDING_GCP_ACCESS`.**

The cloud-independent probe matrix and operator command surface are complete.
The mandatory decision is intentionally not marked `GO`, `GO-WITH-CONSTRAINTS`
or `NO-GO`, because no GCP project, BigLake catalog, BigQuery job runner or
Spark ADC is available in this environment. No full table/model port starts
before the cloud run produces one of those decisions.

## Implemented locally

- Added `scripts/gcp/vertical_slice.py`, which derives a deterministic plan
  from the repository-owned Iceberg table specs for exactly:

  - `bronze.mysql_cdc_records`;
  - `silver.order_items_changes`;
  - `reference.geolocation`;
  - `audit.silver_progress`.

- Added direct BigQuery P.C.N.T identifiers and stable native bridge-view
  identifiers. The bridge view convention is
  `olist_lakehouse_bridge.<namespace>_<table>`.
- Added `TYPEOF` schema/type probes, zero-row schema probes, direct/bridge
  reads, duplicate/retry aggregates and the concurrent-commit checkpoint
  checklist. Iceberg metadata tables such as `.snapshots` and `.files` are
  explicitly excluded.
- Added static mappings based on the current Google documentation:

  | Iceberg field | Expected BigQuery type | Slice |
  | --- | --- | --- |
  | `TIMESTAMP_LTZ` | `TIMESTAMP` | Bronze, Silver, Audit |
  | `DECIMAL(18,2)` | `NUMERIC` | `silver.order_items_changes` |
  | `DECIMAL(18,14)` | `BIGNUMERIC` | `reference.geolocation` |
  | `BINARY` | `BYTES` | `bronze.mysql_cdc_records` |
  | `ARRAY<STRUCT<key: STRING, value: BINARY>>` | `ARRAY<STRUCT<key STRING, value BYTES>>` | Bronze |

- Added `lab.py gcp vertical-slice run|report`. It writes a reproducible JSON
  plan for a future cloud execution but fails closed with
  `PENDING_GCP_ACCESS`; it does not silently turn a static plan into a GO
  decision.

The matrix follows the Google Developer Knowledge MCP documentation:

- [Query Iceberg tables with Lakehouse](https://docs.cloud.google.com/lakehouse/docs/query-iceberg-tables-with-lakehouse)
- [About Lakehouse catalogs](https://docs.cloud.google.com/lakehouse/docs/about-lakehouse-catalogs)
- [BigQuery utility functions (`TYPEOF`)](https://cloud.google.com/bigquery/docs/reference/standard-sql/utility-functions)

The documented cloud constraints to verify during the run include Iceberg V2,
Parquet-only files, the `metadata.json` size limit, no BigQuery Storage Read
API assumption, regional catalog visibility, and the inability to query
Iceberg metadata tables through the BigQuery P.C.N.T surface.

## Required cloud run

After WP3 infrastructure and WP4 ADC/image setup are available:

1. Run `lab.py gcp preflight` and record project, catalog, region, ADC role and
   exact image digest.
2. Run the GCP migration and reference-load services, then start only the GCP
   streaming contour.
3. Generate the plan with the real project and catalog IDs:

   ```text
   uv run python scripts/lab.py gcp vertical-slice run \
     --project-id PROJECT_ID \
     --catalog-id CATALOG_ID \
     --output data/acceptance/gcp/wp5-vertical-slice-plan.json
   ```

4. Execute the four Spark writes, restart from GCS checkpoints, run all direct
   and bridge queries, and capture BigQuery job IDs, bytes processed/billed,
   latency, errors, row counts, query schemas and largest metadata JSON size.
5. Repeat a duplicate/retry input and query while additional Spark commits
   are occurring. Verify the progress proof and checkpoint resume behavior.
6. Append the result as exactly `GO`, `GO-WITH-CONSTRAINTS` or `NO-GO` and
   preserve the generated plan and raw job evidence.

## Evidence available without GCP

```text
uv run ruff check scripts/gcp scripts/lab.py tests/gcp
All checks passed

uv run pytest -q tests/gcp tests/lakehouse_platform tests/orchestration
71 passed, 1 skipped

uv run python scripts/lab.py gcp vertical-slice run \
  --project-id demo-project --catalog-id demo-lakehouse-catalog \
  --allow-missing-auth --output <temporary-plan>
status: blocked
cloud_execution: PENDING_GCP_ACCESS

uv run python scripts/lab.py gcp vertical-slice report --output <temporary-plan>
status: blocked
errors: []
decision: null
```

The placeholder plan used for static validation is not a cloud acceptance
run. No BigQuery query, Spark GCP job, checkpoint restart or billing event was
performed.
