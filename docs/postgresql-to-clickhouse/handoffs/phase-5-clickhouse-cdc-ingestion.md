# Handoff: Phase 5 - Implement ClickHouse CDC ingestion

## Mission

Implement Phase 5 of
`docs/plans/local-clickhouse-warehouse-migration-plan.md`: move typed raw CDC
business events to ClickHouse while keeping PostgreSQL `olist_control` as the
authoritative store for file claims, attempts, watermarks, reconciliation, and
control-state transitions.

## Verified Phase 4 baseline

- `local_clickhouse` parses and builds the batch-selected dbt graph, snapshots,
  data tests, unit tests, and Elementary package models.
- Batch dbt SQL uses shared compatibility macros rather than direct
  PostgreSQL-specific syntax.
- `fact_order_items` uses ClickHouse incremental `insert_overwrite` partition
  replacement. PostgreSQL and Redshift keep the existing incremental
  `delete+insert` path.
- The Phase 4 ClickHouse partition replacement override drops affected target
  partitions that become empty after the new staging result is built.
- `scripts/ci/check_clickhouse_fact_insert_overwrite_edges.py` covers the
  Phase 4 moved-key, stale-key, and empty-partition runtime edge cases against
  local ClickHouse.
- The regular GitHub Actions `CI` workflow runs that edge fixture in the
  `clickhouse-incremental-edges` job on pull requests and pushes to
  `main`/`master`.
- ClickHouse dbt does not read `olist_control`; batch reconciliation remains a
  Python/control-plane check.
- `olist_modern_data_stack_local` can route dbt and Elementary to
  `local_clickhouse` when `warehouse_target=clickhouse`.
- Canonical ClickHouse manifest export and oracle/candidate comparison CLIs
  exist under `scripts/parity`.
- The clean `olist_small` PostgreSQL oracle and ClickHouse candidate Phase 4
  manifests compare with `status=PASS` and `mismatch_count=0` in
  `data/reports/batch_phase4_compare.json`.
- PostgreSQL `local_pg` remains available as the oracle target.

## Required boundary

- Do not remove `local_pg`, the analytical `postgres` service, or the
  PostgreSQL oracle in Phase 5.
- Do not port realtime dbt models, realtime marts, publication approval, or
  batch-to-realtime parity in Phase 5 except where a small runtime selection
  projection is required for the next phase.
- Do not replace the Phase 4 batch `fact_order_items` partition-replacement
  contract with row-level ClickHouse deletes or `ReplacingMergeTree` dedup
  semantics.
- Do not query PostgreSQL control tables from ClickHouse or dbt.
- Keep claims, attempts, leases, offsets, watermarks, and reconciliation writes
  in `olist_control`.
- Treat a ClickHouse insert followed by a failed PostgreSQL control update as a
  recoverable retry window, not as a manual repair condition.

## Implementation notes

- Split `scripts/cdc/warehouse_ingest.py` so PostgreSQL control operations and
  ClickHouse raw CDC writes are separate responsibilities.
- Insert typed CDC events into `raw_cdc` with deterministic insert
  deduplication tokens derived from immutable object identity and selected
  offsets.
- Read ClickHouse raw CDC state with logical deduplication behavior suitable
  for retries and duplicate deliveries.
- Preserve existing manifest validation, schema validation, payload checks,
  offset continuity checks, and reconciliation semantics.
- Project only immutable transform run selection metadata into
  `pipeline_runtime`; PostgreSQL remains authoritative for transform state.
- Add failure injection or tests for ambiguous insert acknowledgement and
  failure after ClickHouse insert but before PostgreSQL `LOADED` commit.

## Suggested verification

Run at minimum:

```powershell
docker compose config --quiet
docker compose up -d airflow-postgres control-db-init clickhouse clickhouse-init minio kafka kafka-connect
uv run python -m unittest discover -s tests -p "test_clickhouse*phase*.py" -v
uv run python -m unittest discover -s tests -p "test_*control*.py" -v
uv run dbt build --project-dir dbt/olist_analytics --profiles-dir dbt/olist_analytics --target local_clickhouse --selector batch --no-partial-parse --quiet --warn-error-options '{"error": ["NoNodesForSelectionCriteria"]}'
```

After implementing CDC writes, run duplicate delivery, replay, offset-gap, and
ambiguous-insert retry scenarios before moving to realtime dbt.

## Exit gate

- Initial CDC ingest, replay, duplicate delivery, and offset checks pass.
- Logical `raw_cdc` state contains one event per topic, partition, and offset.
- A crash after ClickHouse insert and before PostgreSQL control commit
  self-recovers on retry.
- PostgreSQL control state remains authoritative and isolated from ClickHouse
  analytical queries.
