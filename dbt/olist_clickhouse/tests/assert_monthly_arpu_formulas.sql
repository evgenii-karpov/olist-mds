SELECT *
FROM {{ ref('mart_monthly_arpu') }}
WHERE
    (active_customers > 0 AND arpu != round(total_revenue / active_customers, 2))
    OR (orders_count > 0 AND average_order_value != round(total_revenue / orders_count, 2))
    OR repeat_customer_rate < 0
    OR repeat_customer_rate > 1
