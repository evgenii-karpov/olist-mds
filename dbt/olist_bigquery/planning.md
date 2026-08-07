# BigQuery Gold model plan

| Model | Grain | Incremental impact | Operation semantics |
| --- | --- | --- | --- |
| `dim_date` | `date_day` | dates from changed orders | `REPLACE_GRAIN` |
| `dim_order_status` | `order_status` | statuses from changed orders | `REPLACE_GRAIN` |
| `dim_seller` | `seller_id` | changed seller keys | `UPSERT` / `DELETE` |
| `dim_customer_scd2` | customer version | changed customer timelines | `INSERT` / `CLOSE` / `DELETE` |
| `dim_product_scd2` | product version | product and translation impacts | `INSERT` / `CLOSE` / `DELETE` |
| `fact_order_items` | `order_id`, `order_item_id` | changed order/item keys | `UPSERT` / `DELETE` |
| `mart_daily_revenue` | purchase date | dates from impacted facts | `REPLACE_GRAIN` |
| `mart_monthly_arpu` | order month | months from impacted facts | `REPLACE_GRAIN` |

Every model writes a run-scoped history row with `sync_run_seq`,
`sync_run_id`, `operation_type`, boundary identifiers, and `built_at`. The
same-run pre-hook removes only that sequence before rebuilding. Publication
and current-state mutation remain outside dbt and are handled by a future
versioned BigQuery procedure.
