# Source contract

This document describes the local Olist archive used to seed MySQL.
The committed small fixture follows the same file and header contract.

Source archive: `olist.zip`

## File summary

| Entity | File | Rows | Columns |
| --- | --- | --- | --- |
| customers | `olist_customers_dataset.csv` | 99441 | 5 |
| geolocation | `olist_geolocation_dataset.csv` | 1000163 | 5 |
| order_items | `olist_order_items_dataset.csv` | 112650 | 7 |
| order_payments | `olist_order_payments_dataset.csv` | 103886 | 5 |
| order_reviews | `olist_order_reviews_dataset.csv` | 99224 | 7 |
| orders | `olist_orders_dataset.csv` | 99441 | 8 |
| products | `olist_products_dataset.csv` | 32951 | 9 |
| sellers | `olist_sellers_dataset.csv` | 3095 | 4 |
| product_category_translation | `product_category_name_translation.csv` | 71 | 2 |

## Entity columns

Column names are preserved when the source schema is created in MySQL.
The raw type is the documented source-facing type for the MySQL source schema.

### customers

File: olist_customers_dataset.csv

| Column | Source type |
| --- | --- |
| customer_id | varchar(256) |
| customer_unique_id | varchar(256) |
| customer_zip_code_prefix | varchar(16) |
| customer_city | varchar(256) |
| customer_state | varchar(256) |

### geolocation

File: olist_geolocation_dataset.csv

| Column | Source type |
| --- | --- |
| geolocation_zip_code_prefix | varchar(16) |
| geolocation_lat | decimal(18, 14) |
| geolocation_lng | decimal(18, 14) |
| geolocation_city | varchar(256) |
| geolocation_state | varchar(256) |

### order_items

File: olist_order_items_dataset.csv

| Column | Source type |
| --- | --- |
| order_id | varchar(256) |
| order_item_id | integer |
| product_id | varchar(256) |
| seller_id | varchar(256) |
| shipping_limit_date | timestamp |
| price | decimal(18, 2) |
| freight_value | decimal(18, 2) |

### order_payments

File: olist_order_payments_dataset.csv

| Column | Source type |
| --- | --- |
| order_id | varchar(256) |
| payment_sequential | integer |
| payment_type | varchar(256) |
| payment_installments | integer |
| payment_value | decimal(18, 2) |

### order_reviews

File: olist_order_reviews_dataset.csv

| Column | Source type |
| --- | --- |
| review_id | varchar(256) |
| order_id | varchar(256) |
| review_score | integer |
| review_comment_title | varchar(1024) |
| review_comment_message | varchar(65535) |
| review_creation_date | timestamp |
| review_answer_timestamp | timestamp |

### orders

File: olist_orders_dataset.csv

| Column | Source type |
| --- | --- |
| order_id | varchar(256) |
| customer_id | varchar(256) |
| order_status | varchar(256) |
| order_purchase_timestamp | timestamp |
| order_approved_at | timestamp |
| order_delivered_carrier_date | timestamp |
| order_delivered_customer_date | timestamp |
| order_estimated_delivery_date | timestamp |

### products

File: olist_products_dataset.csv

| Column | Source type |
| --- | --- |
| product_id | varchar(256) |
| product_category_name | varchar(256) |
| product_name_lenght | integer |
| product_description_lenght | integer |
| product_photos_qty | integer |
| product_weight_g | integer |
| product_length_cm | integer |
| product_height_cm | integer |
| product_width_cm | integer |

### sellers

File: olist_sellers_dataset.csv

| Column | Source type |
| --- | --- |
| seller_id | varchar(256) |
| seller_zip_code_prefix | varchar(16) |
| seller_city | varchar(256) |
| seller_state | varchar(256) |

### product_category_translation

File: product_category_name_translation.csv

| Column | Source type |
| --- | --- |
| product_category_name | varchar(256) |
| product_category_name_english | varchar(256) |

## Rules

- The archive must contain every expected source file.
- Header names and order must match this contract.
- Nullable source values remain nullable in MySQL and CDC records.
- Zip-code prefixes remain strings so leading zeroes are preserved.
- Timestamps use the source timezone semantics defined by the MySQL schema.
- Source changes are transported through Debezium and the versioned Avro contracts.
