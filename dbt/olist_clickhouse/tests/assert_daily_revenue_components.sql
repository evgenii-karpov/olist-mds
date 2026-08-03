SELECT *
FROM {{ ref('mart_daily_revenue') }}
WHERE
    sync_run_seq = {{ sync_run_seq_sql() }}
    AND gross_revenue != product_revenue + freight_revenue
