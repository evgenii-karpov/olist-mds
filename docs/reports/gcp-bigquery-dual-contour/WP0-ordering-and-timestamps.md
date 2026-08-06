# WP0 — Ordering and timestamp implementation report

Date: 2026-08-07
Branch: `gcp-bigquery-dual-contour`
Baseline: `10454a7fa935078a1f037f66091e0114637f10cf` (`docs: add GCP BigQuery dual-contour implementation plan`)

## Status

**WP0 is complete for the checks available without GCP access.**

The fail-closed source-ordering contract, timestamp contract, Spark/ClickHouse
consumers, local serving path, and destructive local acceptance flow are
implemented and verified. Cloud-specific BigQuery/Iceberg checks remain
pending until GCP credentials and resources are available.

## Implemented

- Python validation for snapshot, live non-transactional, and live
  transactional records, including strict binlog filename/index parsing,
  required-field checks, conflicting-coordinate detection, and canonical
  ordering tuple construction.
- UTC normalization for source wall-clock values through `SOURCE_TIME_ZONE`,
  defaulting to `America/Sao_Paulo`.
- Scala validation and canonical ordering in `SourceOrdering`; Silver now
  persists the parsed binlog file index and source-order fields in the
  current-state table.
- Repository Iceberg contracts migrated from `TIMESTAMP_NTZ` to
  `TIMESTAMP_LTZ` for repository-owned timestamp fields.
- ClickHouse current-version DDL, current materialization, stable views, the
  ClickHouse dbt project, and the local acceptance probe use the canonical
  source tuple rather than Kafka offset/timestamp-only latest-row selection.
- Current-state source-order columns and refreshed Scala contract checksum.
- Explicit `toInt64` normalization for nullable transaction-order fields in
  ClickHouse ordering expressions, required by ClickHouse 26.3 to avoid
  `Variant`/`Dynamic` ORDER BY keys.
- SCD2 CTE projections now carry every canonical ordering field through the
  customer and product version pipelines, including the event identifier
  used by the final tuple tie-breaker.
- Spark builder line-ending normalization and CRLF-safe JAR manifest parsing
  for Windows checkouts.

## Static and local evidence

### Static checks

Passed in the acceptance preflight and in the focused rerun:

```text
uv run pre-commit run --all-files
all configured hooks passed, including Ruff, Ruff format, Pyright and dbt parse

uv run pytest tests/cdc_contracts tests/lakehouse_platform tests/mysql \
  tests/dbt_clickhouse tests/serving tests/local_cdc_acceptance
233 passed, 3 skipped

uv run dbt test --resource-type unit_test \
  --vars '{"sync_run_seq": 1, "sync_run_id": "wp0-model-fix"}'
4 passed
```

The pytest run reports only the existing Windows Airflow platform warning and
pytest cache-permission warning; neither is a failed check.

### Spark Docker build

Passed:

```text
docker build --progress=plain --target runtime \
  --tag olist-spark:4.1.3-iceberg1.11.0 \
  --file docker/spark/Dockerfile .
```

The pinned JAR download/checksum contract passed; Scala formatting, compile,
tests (`10 passed, 0 failed`) and package steps completed, and the runtime
image verification succeeded.

### Full local CDC acceptance

Evidence:

- Run ID: `wp0-local-acceptance-r5`
- Report: `data/acceptance/local-cdc/wp0-local-acceptance-r5/report.md`
- Compose project: `olist_local_cdc_acceptance`
- Result: `11/11` mandatory gates passed
- Started: `2026-08-07T01:05:54.326374+00:00`
- Finished: `2026-08-07T01:23:13.433559+00:00`

The gates covered clean bootstrap, initial snapshot, CRUD/restart, catch-up,
serving sync, dbt and stable views, additive schema evolution, rebuild, and
the final consistency checks. The acceptance project was subsequently
stopped with its project-specific Docker volumes removed.

## Remaining checks

The following are intentionally not claimed as complete:

1. GCP authentication, Terraform apply/plan against a real project, and
   BigQuery/Iceberg REST catalog operations.
2. Cloud contour acceptance and parity against a real BigQuery dataset.
3. Production-scale performance and cost validation.

No GCP credentials, cloud resources, BigQuery jobs, or GCP Lakehouse reads
were used in this report.
