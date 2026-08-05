# ClickHouse model catalog

The project builds one serving projection for a sync sequence. Physical tables
are stored in `gold_store`; stable views in `gold` expose the
published sequence.

| Model | Grain | Ordering |
| --- | --- | --- |
| `dim_date` | one row per `date_day` | `date_key` |
| `dim_order_status` | one row per status | `order_status` |
| `dim_seller` | one row per seller | `seller_id` |
| `dim_customer_scd2` | customer version interval | `customer_unique_id, valid_from` |
| `dim_product_scd2` | product version interval | `product_id, valid_from` |
| `fact_order_items` | `order_id, order_item_id` | `order_id, order_item_id` |
| `mart_daily_revenue` | purchase date | `order_purchase_date` |
| `mart_monthly_arpu` | month | `order_month` |

The fact model preserves item value, freight, allocated payment value,
delivery duration, delivery delay and the late-delivery flag. The two marts
preserve their declared revenue and customer-value formulas.
