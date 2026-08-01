SELECT *
FROM {{ ref('mart_daily_revenue') }}
WHERE gross_revenue != product_revenue + freight_revenue
