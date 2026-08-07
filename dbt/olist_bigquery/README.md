# `olist_bigquery`

This is the independent `dbt-bigquery` contour. It does not import the
ClickHouse project or a provider-neutral SQL layer.

The project reads immutable `silver.*_changes` streams only through native
views in `olist_lakehouse_bridge`. A run's exact Kafka interval comes from
`olist_serving_control.boundary_offsets`:

```text
(previous_offset, target_offset]
```

The initial run uses a null previous offset and therefore reconstructs the
complete bounded state. Later runs propagate only keys and aggregate grains
observed in that exact interval. Physical dbt outputs are per-model
`<model>__history` candidates; current tables, stable views, and publication
are owned by versioned BigQuery migrations.

Credential-free validation:

```text
uv run dbt parse \
  --project-dir dbt/olist_bigquery \
  --profiles-dir dbt/olist_bigquery \
  --target local_static \
  --vars '{"sync_run_seq": 1, "sync_run_id": "parse", "build_mode": "initial"}' \
  --no-partial-parse
```

No `dbt compile`, `dbt build`, or online adapter query is required for the
static project check.
