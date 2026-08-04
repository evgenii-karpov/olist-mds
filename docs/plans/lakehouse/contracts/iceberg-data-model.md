# Technical Contract: Iceberg, Polaris and MinIO Data Model

- **Status**: Active normative contract
- **Purpose**: Define the Iceberg catalog structure, MinIO buckets, namespaces, Bronze/Silver/Audit/Reference table schemas and table properties.
- **Authority**: Defines the current normative requirements for Lakehouse data structures and schemas.

---

## 1. Polaris catalog and MinIO bucket boundary

### 1.1 Polaris Catalog parameters

- Catalog / REST warehouse parameter: `olist_lakehouse`
- Default base location: `s3://olist-lakehouse/warehouse`
- REST URI: `http://polaris:8181/api/catalog`
- S3 endpoint: `http://minio:9000`
- S3 region: `us-east-1`

### 1.2 MinIO buckets

1. `olist-lakehouse`: Iceberg table data (warehouse).
2. `olist-checkpoints`: Spark Structured Streaming checkpoints.

Checkpoints are physically isolated from the warehouse. Iceberg maintenance tools do not have access to the checkpoint bucket.

### 1.3 Namespaces and table properties

The catalog contains four namespaces:
- `bronze`
- `silver`
- `reference`
- `audit`

Common Iceberg table properties:

```text
format-version=2
write.format.default=parquet
write.parquet.compression-codec=zstd
write.target-file-size-bytes=134217728
write.metadata.delete-after-commit.enabled=true
write.metadata.previous-versions-max=20
```

Partitioning:
- `bronze.mysql_cdc_records`: `days(ingested_at)`;
- `bronze.avro_schemas`: unpartitioned;
- `silver.<entity>_changes`: `days(source_ts)`;
- `silver.<entity>_current`: unpartitioned;
- `reference.geolocation`: unpartitioned;
- Growing `audit` tables: `days(recorded_at)`.

---

## 2. Bronze raw-layer schemas

### 2.1 Table `bronze.mysql_cdc_records`

Stores external Kafka CDC topics in their original binary form (without decoding the payload).

| Column | Type | Purpose |
| --- | --- | --- |
| `event_id` | `string` | Composite ID (`topic:partition:offset`) |
| `record_kind` | `string` | `data`, `tombstone`, `transaction`, `heartbeat`, `schema_change` |
| `topic` | `string` | Kafka topic name |
| `partition` | `int` | Kafka partition number |
| `offset` | `long` | Offset within the partition |
| `kafka_timestamp` | `timestamptz` | Timestamp from Kafka |
| `kafka_timestamp_type` | `string` | Kafka timestamp type |
| `headers` | `map<string, binary>` | Kafka message headers |
| `key_bytes` | `binary` | Raw key bytes |
| `value_bytes` | `binary` | Raw value bytes |
| `is_tombstone` | `boolean` | `true` for a null value on a business topic |
| `key_schema_id` | `int` | Extracted 4-byte key schema ID |
| `value_schema_id` | `int` | Extracted 4-byte value schema ID |
| `key_sha256` | `string` | SHA-256 key hash |
| `value_sha256` | `string` | SHA-256 value hash |
| `key_framing_valid` | `boolean` | Confluent Avro key framing validity |
| `value_framing_valid` | `boolean` | Confluent Avro value framing validity |
| `framing_error` | `string` | Framing error code, if any |
| `ingest_batch_id` | `long` | Spark micro-batch ID |
| `spark_query_id` | `string` | Stable streaming-query ID |
| `ingested_at` | `timestamptz` | Bronze write timestamp |

### 2.2 Table `bronze.avro_schemas`

Archive of all registered and observed Avro schemas.

Columns: `schema_id` (int), `fingerprint_sha256` (string), `subject` (string), `registry_version` (int), `schema_json` (string), `references_json` (string), `spark_self_contained_schema_json` (string), `first_seen_at` (timestamptz), `last_verified_at` (timestamptz).

---

## 3. Silver-layer schemas

Two tables are created for each of the eight business entities:
1. `silver.<entity>_changes` — immutable business-event ledger.
2. `silver.<entity>_current` — current entity snapshot.

### 3.1 Fields of `silver.<entity>_changes`

- Operational identifiers and status: `event_id`, `op` (`c/r/u/d`), `is_snapshot`, `is_deleted`, `apply_status` (`applied` / `rejected`), `error_code`, `error_message`.
- Entity business columns according to MySQL types, normalized to UTC/NTZ.
- Binlog source metadata: `source_ts`, `source_server_id`, `source_gtid`, `source_binlog_file`, `source_binlog_file_index`, `source_binlog_pos`, `source_row`.
- Transaction and Kafka metadata: `transaction_id`, `transaction_total_order`, `transaction_data_collection_order`, `kafka_topic`, `kafka_partition`, `kafka_offset`, `kafka_timestamp`.
- Hashes and versions: `key_schema_id`, `value_schema_id`, `schema_fingerprint`, `contract_version`, `before_row_hash`, `after_row_hash`, `row_hash`, `bronze_ingested_at`, `normalized_at`.

### 3.2 Fields of `silver.<entity>_current`

Entity business columns plus version metadata: `is_deleted`, `deleted_at`, `last_event_id`, `last_source_ts`, `last_transaction_id`, `last_kafka_partition`, `last_kafka_offset`, `last_row_hash`, `contract_version`, `updated_at`.

---

## 4. Audit and reference table schemas

The `audit` namespace contains:
- `audit.mysql_transactions`: transaction status and boundary tracking (`OPEN`, `COMPLETE`, `REJECTED`).
- `audit.silver_progress`: detailed processing progress by entity, partition and offset.
- `audit.normalization_errors`: normalization and business-validation error log.
- `audit.schema_violations`: schema-contract violation log.
- `audit.maintenance_runs`: Iceberg maintenance procedure log.
- `audit.serving_sync_reports`: ClickHouse serving synchronization reports.
- `audit.schema_migrations`: applied Iceberg schema migration version.

The `reference` namespace contains:
- `reference.geolocation`: immutable geolocation reference data loaded by a one-shot scheduled process from MySQL.

---

## 5. Related documents

- [Migration roadmap](../../mysql-spark-iceberg-lakehouse-migration.md)
- [Architecture and runtime contract](architecture-and-runtime.md)
- [MySQL, Kafka and Avro contract](mysql-kafka-avro.md)
- [Spark Structured Streaming contract](spark-streaming.md)
