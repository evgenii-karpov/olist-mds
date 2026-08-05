# Local CDC data model

## Source and transport

MySQL owns the Olist source tables. Debezium publishes the eight keyed source
entities as Avro-framed Kafka records. Apicurio Registry owns the schema
versions and compatibility rules.

Bronze stores the transport identity, schema information, source metadata and
raw framed record. Silver stores normalized entity records and the current
source projection. Transaction observations and processing outcomes are
append-only evidence for the serving boundary.

## Iceberg tables

- `bronze.events` stores captured CDC records.
- `bronze.avro_schemas` stores schema material used to decode records.
- `silver.<entity>_events` stores normalized entity records.
- `silver.<entity>_current` stores the latest non-deleted source state.
- `audit.mysql_transactions` stores transaction observations and effective
  transaction state.
- `audit.silver_progress` stores entity progress.
- `audit.normalization_errors` and `audit.schema_violations` store rejected
  records and contract failures.
- `serving.serving_sync_reports` stores serving operation results.

Column definitions, partitions and table properties are defined in
`streaming/spark/platform/table_specs.py`.

## ClickHouse serving

ClickHouse receives a serving projection from Iceberg. The serving schemas are
`serving_cdc`, `serving_control`, `gold_store` and `gold`.

The dbt project in `dbt/olist_clickhouse` builds candidate models in
`gold_store` and exposes approved views in `gold`:

- `fact_order_items` at `order_id + order_item_id` grain;
- `dim_customer_scd2` and `dim_product_scd2` with effective intervals;
- `dim_seller`, `dim_date` and `dim_order_status`;
- `mart_daily_revenue` by purchase date;
- `mart_monthly_arpu` by month.

Airflow coordinates the serving operation. Spark owns CDC decoding and
Iceberg writes; ClickHouse and dbt own the serving projection.

## Invariants

- Source column names and nullability follow the MySQL contract.
- Kafka event identity is preserved through Bronze and Silver.
- A newer Kafka position cannot be replaced by an older position.
- A rejected or incomplete transaction cannot be published.
- A serving retry is idempotent for the same serving boundary.
- dbt models preserve their declared grain and measure formulas.
