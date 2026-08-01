# ClickHouse Gold model plan

The project builds a complete candidate projection for one immutable
`sync_run_seq`. Candidate rows live in `gold_store`; the `gold` views expose
only the latest sequence recorded as `PUBLISHED` in
`serving_control.published_runs`.

| Model | Grain / primary key | Candidate storage order |
| --- | --- | --- |
| `dim_date` | one row per `date_day` | `date_key` |
| `dim_order_status` | one row per `order_status` | `order_status` |
| `dim_seller` | one row per `seller_id` | `seller_id` |
| `dim_customer_scd2` | one visible version per customer business interval | `customer_unique_id, valid_from` |
| `dim_product_scd2` | one visible version per product business interval | `product_id, valid_from` |
| `fact_order_items` | `order_id, order_item_id` | `order_id, order_item_id` |
| `mart_daily_revenue` | `order_purchase_date` | `order_purchase_date` |
| `mart_monthly_arpu` | `order_month` | `order_month` |

Every physical table is a `MergeTree` partitioned by `sync_run_seq`. The same
sequence is rebuilt with `insert_overwrite`, which keeps Airflow retries
idempotent. SCD2 opening rows use `1900-01-01 00:00:00 UTC` for Debezium
snapshot events; later versions use source event time and deterministic Kafka
ordering.

The fact output preserves the parity-facing business columns and formulas:
item gross value, proportional order-payment allocation, delivery duration,
delivery delay, and the late-delivery flag. The two marts preserve the closed
published column contracts from the migration plan.
