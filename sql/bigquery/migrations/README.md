# BigQuery migration bundle

The files in this directory are ordered, repository-owned SQL migrations.
Terraform provisions datasets only; it does not create application tables or
views.

`scripts.gcp.migrations` provides the credential-free part of the runner:

```text
uv run python scripts/lab.py gcp migrate status
uv run python scripts/lab.py gcp migrate render \
  --project-id PROJECT_ID \
  --catalog-id CATALOG_ID \
  --output data/acceptance/gcp/rendered-migrations
```

Rendering validates identifiers, substitutes only `project_id` and
`catalog_id`, preserves source SHA-256 checksums and refuses unresolved
placeholders. `gcp migrate apply` remains blocked until a real GCP execution
with the migration ledger and BigQuery job evidence is available.

`V002__bridge_views.sql` is intentionally read-only. It creates native
BigQuery views over the four WP5 source relations and applies explicit
timestamp, decimal, binary and nested-field casts. `V003__gold_source_bridge_views.sql`
adds the remaining Silver change streams required by the independent Gold
project. Applying either bridge migration requires the WP5 vertical-slice
decision and must be followed by direct-vs-bridge schema and row-count checks.

`V004__transaction_boundary_bridge.sql` adds the normalized, read-only
`audit_mysql_transactions` view used by the transaction-complete boundary
planner. It exposes Debezium begin/end offsets and transaction status without
inventing a boundary from Kafka end offsets or idle time.

`V005__gold_current_and_publication.sql` owns the eight Gold current tables,
stable `olist_gold` views, and `publish_gcp_run` procedure. The procedure
checks model/entity evidence and the active predecessor, handles stale and
already-active runs, applies history operations and replacement grains in one
BigQuery transaction, and advances the GCP publication state atomically.
