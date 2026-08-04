# Technical Contract: ClickHouse Serving, dbt Gold and Recovery Scenarios (Serving and Recovery)

- **Status**: Active normative contract
- **Purpose**: Define ClickHouse serving models, dbt-clickhouse Gold structure, Airflow maintenance tasks and failure-handling contracts.
- **Authority**: Defines the current normative requirements for the analytical serving layer and resilience mechanisms.

---

## 1. ClickHouse serving layer

### 1.1 Iceberg DataLakeCatalog integration

ClickHouse creates a `lakehouse` database for direct read-only access to Iceberg tables:

```sql
SET allow_database_iceberg = 1;
CREATE DATABASE lakehouse
ENGINE = DataLakeCatalog('http://polaris:8181/api/catalog', 'spark', 'vended-credentials')
SETTINGS catalog_type = 'rest', warehouse = 'olist_lakehouse';
```

The ClickHouse account uses vended credentials from Polaris and has read-only access to Iceberg metadata and files.

### 1.2 Native ClickHouse databases and tables

ClickHouse creates the following databases:
- `serving_cdc`: CDC events in MergeTree / ReplacingMergeTree format.
- `serving_control`: published transaction and run tracking.
- `gold_store`: physical mart storage partitioned by `sync_run_seq`.
- `gold`: stable views over the latest successfully published run.

`serving_cdc` tables:
- 8 event-ledger tables `<entity>_events` (`ENGINE = MergeTree`).
- 8 current-version tables `<entity>_current_versions` (`ENGINE = ReplacingMergeTree(kafka_offset)` with `PARTITION BY sync_run_seq` and `ORDER BY (sync_run_seq, <business primary key>)`).
- 8 stable views `<entity>_current` filtering deleted rows (`is_deleted = 0`) and unpublished runs.

---

## 2. Physical dbt-clickhouse Gold layer

The separate dbt project is located at `dbt/olist_clickhouse`. The project contains no Redshift or BigQuery branches.

Physical Gold models:
- `dim_date`
- `dim_order_status`
- `dim_seller`
- `dim_customer_scd2`
- `dim_product_scd2`
- `fact_order_items`
- `mart_daily_revenue`
- `mart_monthly_arpu`

Models are materialized in `gold_store.<model>` partitioned by `PARTITION BY sync_run_seq`. Public interfaces in `gold.<model>` are stable views over the latest published `sync_run_seq` partition.

Run dbt transformations only with explicit run variables:

```powershell
dbt build --project-dir dbt/olist_clickhouse --vars '{"sync_run_seq": <n>, "sync_run_id": "<id>"}'
```

---

## 3. Airflow maintenance tasks and Iceberg maintenance

### 3.1 Airflow boundary

Airflow **does not start** or restart continuous Spark streaming processes (`spark-bronze`, `spark-silver`).
Airflow contains only finite DAGs:
- `olist_lakehouse_serving_sync`: periodic synchronization of transaction-complete data from Iceberg to ClickHouse.
- `olist_iceberg_maintenance`: Iceberg snapshot optimization and cleanup procedures.
- `olist_clickhouse_rebuild`: full rebuild of the ClickHouse analytical layer from Iceberg.
- `olist_lakehouse_quality`: data-quality and parity checks.

### 3.2 Iceberg maintenance

Periodic Iceberg optimization procedures include:
- `rewrite_data_files` (compact small files);
- `rewrite_manifests` (optimize manifests);
- `expire_snapshots` (7-day snapshot retention, preserving at least the 20 latest);
- `remove_orphan_files` (minimum orphan-file age of 72 hours).

Maintenance tools receive only an explicit Iceberg table path and have no access to the `olist-checkpoints` bucket.

---

## 4. Failure and recovery contract

| Failure | Required system behavior |
| --- | --- |
| MySQL temporarily unavailable | Debezium retries; downstream processes the accumulated backlog. |
| Kafka unavailable | The connector and Spark Bronze retry. |
| `spark-bronze` failure | Kafka buffers messages within its retention period (7 days). |
| One `spark-silver` query fails | Bronze and the other Silver entities continue processing. The query enters `FATAL` state. |
| Temporary Apicurio Registry failure | Previously archived schemas continue processing. New schemas wait for registry recovery. |
| Incompatible Avro schema | The affected entity query stops in `FATAL` state (fail-closed). |
| Polaris / MinIO unavailable | Spark retries; Kafka serves as the buffer. |
| Airflow stopped | CDC writes from MySQL to Iceberg continue. ClickHouse data is temporarily not updated. |
| ClickHouse unavailable or lost | CDC writes to Iceberg continue. `rebuild-serving` fully restores ClickHouse from Iceberg. |
| Kafka retention exceeded during failure | Full domain reset (`reset --yes`) and a new `bootstrap`. |
| Spark checkpoint lost | Full domain reset (`reset --yes`) and a new `bootstrap`. |
| Polaris database or MinIO data lost | Full domain reset (`reset --yes`) and a new `bootstrap`. |
| Any authoritative volume removed | Partial repair is forbidden; run full `reset --yes` and `bootstrap`. |
| ClickHouse publisher fails before publication | New data remains hidden from `gold`; retry reuses the same `sync_run_seq`. |

---

## 5. Related documents

- [Migration roadmap](../../mysql-spark-iceberg-lakehouse-migration.md)
- [Architecture and runtime contract](architecture-and-runtime.md)
- [Iceberg data model contract](iceberg-data-model.md)
- [Spark Structured Streaming contract](spark-streaming.md)
- [Validation and CI contract](validation-and-ci.md)
