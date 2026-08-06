# Repository Baseline and Required Refactors

## 1. Baseline

The plan is pinned to commit `1fe78c4b1d827e2d17fc604be39b6c227a2488ce`. The repository currently implements:

```text
MySQL -> Debezium/Kafka Connect -> Kafka/Apicurio
      -> Spark Structured Streaming
      -> Polaris REST catalog / MinIO Iceberg
      -> ClickHouse -> dbt-clickhouse Gold
```

The current Iceberg namespace contract is:

```text
bronze
silver
reference
audit
```

## 2. Iceberg table inventory

```text
bronze.mysql_cdc_records
bronze.avro_schemas

silver.customers_changes
silver.customers_current
silver.orders_changes
silver.orders_current
silver.order_items_changes
silver.order_items_current
silver.order_payments_changes
silver.order_payments_current
silver.order_reviews_changes
silver.order_reviews_current
silver.products_changes
silver.products_current
silver.sellers_changes
silver.sellers_current
silver.product_category_translation_changes
silver.product_category_translation_current

reference.geolocation

audit.mysql_transactions
audit.silver_progress
audit.normalization_errors
audit.schema_violations
audit.maintenance_runs
audit.serving_sync_reports
audit.schema_migrations
```

## 3. Gold model inventory

```text
dim_date
dim_order_status
dim_seller
dim_customer_scd2
dim_product_scd2
fact_order_items
mart_daily_revenue
mart_monthly_arpu
```

The BigQuery implementation preserves these logical model names and business contracts.

## 4. Mandatory corrections before cloud work

### 4.1 Source ordering

The reviewed `SilverBatchWriter.scala` behavior does not yet implement the required global ordering contract: `source_binlog_file_index` is written as null and latest-row selection relies primarily on timestamp/event ID. WP0 must:

- parse and validate binlog file indexes;
- centralize the canonical tuple;
- apply it consistently in Spark, ClickHouse, BigQuery, and parity extraction;
- distinguish snapshot, live non-transactional, and transactional required fields;
- quarantine invalid events and fail closed;
- rebuild local Silver/current/Gold fixtures after the semantic change.

### 4.2 Timestamp semantics

Repository-owned Iceberg specifications using `TIMESTAMP_NTZ` must migrate to timezone-aware instant semantics. Because the local data is treated as ephemeral, use a destructive reset rather than a compatibility migration. Interpret source wall-clock values using `SOURCE_TIME_ZONE` and store UTC instants.

### 4.3 Compose bootstrap coupling

The current platform PostgreSQL/bootstrap path includes Polaris-specific initialization. Split it into:

- common PostgreSQL bootstrap for Airflow, Apicurio, and serving-control needs;
- Polaris-specific database/credentials/bootstrap under `lakehouse-local` only.

A rendered GCP profile must not require Polaris secrets, databases, volumes, or health checks.

### 4.4 Serving-state placement

Do not generalize the local PostgreSQL ledger into a shared cross-cloud database. Preserve:

- local ledger in PostgreSQL;
- GCP ledger in `olist_serving_control` BigQuery tables.

Share domain models and state-transition rules in Python, but use separate persistence adapters.

### 4.5 Gold publication architecture

Remove the old full-candidate snapshot/pointer plan from all design and implementation artifacts. The accepted design is:

```text
per-model run history/deltas
  -> one all-model BigQuery transaction
  -> materialized per-model current state
  -> stable serving views
```

### 4.6 Configuration compatibility

Use this compatibility contract:

```text
catalog alias = ICEBERG_SPARK_CATALOG_ALIAS
             -> ICEBERG_CATALOG_NAME
             -> lakehouse

warehouse     = ICEBERG_WAREHOUSE
```

Do not introduce an immediate breaking rename for the local contour.

## 5. Refactoring strategy

Prefer narrow extraction around existing code:

- runtime configuration and backend adapter;
- common Spark session/table-spec helpers;
- source-order utility;
- provider-independent boundary domain model;
- local PostgreSQL and GCP BigQuery control adapters;
- target-specific dbt projects and DAGs.

Do not rewrite the functioning local path merely to make the cloud path look symmetrical.
