# Olist ClickHouse Gold

This is the local ClickHouse-only dbt project for the Iceberg serving path. It
does not contain unrelated adapters, realtime widening, or manifest-based
incremental logic.

Each invocation must identify the finite serving candidate:

```text
dbt build --project-dir dbt/olist_clickhouse \
  --vars '{sync_run_seq: 42, sync_run_id: "sync-000042"}'
```

All physical rows are written to `gold_store` in the `sync_run_seq` partition.
The post-hooks create `gold` views, but those views continue to select the
latest sequence whose `serving_control.published_runs_current` status is
`PUBLISHED`. Building or testing a candidate therefore cannot expose it.

Inside containers, invoke `bin/run-dbt.sh`; it consumes
`CLICKHOUSE_PASSWORD_FILE`, disables shell tracing, and exports the password
only to the dbt process. `profiles.yml.example` documents the resulting dbt
profile interface and contains no credential.

After publication, old partitions can be inspected safely with:

```text
dbt run-operation cleanup_gold_partitions \
  --args '{keep_published: 2, dry_run: true}'
```

Only a finite orchestration task may repeat it with `dry_run: false`.
