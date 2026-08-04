# Spark Structured Streaming data-plane contract

- **Status**: Active normative contract
- **Purpose**: Define the technical specification for the Spark Structured Streaming processing engine, Scala project build rules, CDC decoding algorithms, Iceberg batch commits, and error handling.
- **Authority**: Defines the current normative requirements for the data-plane implementation.

---

## 1. Scala project build and artifact requirements

The only build root is:

```text
streaming/spark/scala/
  build.sbt
  project/build.properties
  project/plugins.sbt
  .scalafmt.conf
  src/main/scala/com/olist/mds/spark/
  src/main/resources/contracts/
  src/main/resources/topics.json
  src/test/scala/com/olist/mds/spark/
```

Build parameters:
- `organization := "com.olist.mds"`
- `name := "olist-spark-jobs"`
- `version := "0.1.0"`
- `scalaVersion := "2.13.17"`
- `sbt.version=1.12.11`

The build generates one thin JAR, `olist-spark-jobs_2.13-0.1.0.jar`, which is placed in the image at `/opt/olist/jars/olist-spark-jobs.jar`.

Entrypoints:
- `com.olist.mds.spark.app.BronzeMain`
- `com.olist.mds.spark.app.SilverMain`
- `com.olist.mds.spark.app.ReplayMain`
- `com.olist.mds.spark.app.GeolocationMain`
- `com.olist.mds.spark.app.LakehouseStatusMain`

---

## 2. Package structure and shared Scala API

Application packages:
- `com.olist.mds.spark.app`: main classes and CLI argument parsing.
- `com.olist.mds.spark.config`: configuration and `SparkSession` factory.
- `com.olist.mds.spark.contract`: contract resource loader and validator.
- `com.olist.mds.spark.avro`: Confluent framing checks and Apicurio CCompat client.
- `com.olist.mds.spark.bronze`: Bronze projection and writer.
- `com.olist.mds.spark.normalize`: shared decoder and `EntityBatchProcessor`.
- `com.olist.mds.spark.entity`: eight entity modules and `EntityRegistry`.
- `com.olist.mds.spark.iceberg`: commit coordinator and Iceberg writers.
- `com.olist.mds.spark.supervisor`: streaming-query supervisor and status reporting.
- `com.olist.mds.spark.ops`: finite replay operations and geolocation loader.

Data processing must use Spark SQL `DataFrame` / `Column` expressions only. Row-wise business UDFs, collecting business rows to the driver with `collect()`, and the RDD API for payload data are **forbidden**.

Entity order in `EntityRegistry`:
1. `customers`
2. `orders`
3. `order_items`
4. `order_payments`
5. `order_reviews`
6. `products`
7. `sellers`
8. `product_category_translation`

---

## 3. Streaming query names and checkpoints

`BronzeMain` starts one query:
- Name: `kafka_to_bronze`
- Checkpoint path: `s3a://olist-checkpoints/kafka_to_bronze/contract-v2/`

`SilverMain` starts ten independently controlled queries in one JVM:
- `capture_avro_schemas`
- `normalize_mysql_transactions`
- `normalize_customers`
- `normalize_orders`
- `normalize_order_items`
- `normalize_order_payments`
- `normalize_order_reviews`
- `normalize_products`
- `normalize_sellers`
- `normalize_product_category_translation`

Each Silver query uses `s3a://olist-checkpoints/<query-name>/contract-v2/` as its checkpoint. Sharing one checkpoint between queries is forbidden.

The processing trigger is `Trigger.ProcessingTime("60 seconds")` (or a test-adjusted interval).

---

## 4. Kafka-to-Bronze algorithm

1. The Kafka source reads the topic list from `topics.json`.
2. Headers, keys, and values are stored as raw binary data without decoding business payloads.
3. The five-byte Confluent Avro framing (magic byte `0` and four-byte schema ID) is validated.
4. Framing errors are recorded in `framing_error`; binary data is retained in all cases.
5. Writes to `bronze.mysql_cdc_records` use `foreachBatch` with a left-anti join on `event_id` to make batch retries idempotent. `MERGE` and `UPDATE` operations on Bronze are **forbidden**.

---

## 5. Normalization algorithm and Silver/Audit writes

### 5.1 Micro-batch commit order

Silver batch processing commits in exactly this order:

```text
changes → normalization_errors/schema audit → current → silver_progress
```

`silver_progress` is committed **strictly last**.

### 5.2 Idempotent MERGE into `changes`

The `changes` MERGE key is strictly `event_id`.
Duplicate handling rules:
1. If a row with the same `event_id` already exists and all fields match, the retry is an idempotent no-op (`normalized_at` is not updated).
2. If the existing row is `rejected` and the incoming row is `applied`, and all immutable metadata matches in `FiniteReplay` mode, only mutable business columns and status may be updated.
3. Attempting to overwrite an existing `applied` row with different data raises the fatal `applied_event_rewrite` error.
4. A mismatch in immutable metadata raises the fatal `ledger_transport_mismatch` error.

### 5.3 Idempotent MERGE into `current`

`current` receives only the event with the greatest Kafka offset for each business key within a batch. MERGE updates or inserts a row only when the new Kafka offset is strictly greater than the stored `last_kafka_offset`. Rejected events (`rejected`) and tombstones do not change `current`.

---

## 6. Error classification and supervisor

Errors are divided into three classes:
1. `TransientFailure`: temporary network failures, Polaris/Registry timeouts, and optimistic Iceberg commit conflicts. These trigger automatic retries with exponential backoff.
2. `PermanentRecordFailure`: invalid binary data or violations of schema or entity rules. These generate a rejected row (`apply_status=rejected`) and an `audit.normalization_errors` row without stopping the stream.
3. `FatalContractFailure`: contract incompatibility, attempts to overwrite applied events, or transaction hydration mismatches. These terminate the affected query with status `FATAL`.

The `SilverMain` supervisor isolates failures by entity: if one query stops in `FATAL`, overall application readiness becomes `DEGRADED`, while the other nine queries continue processing.

---

## 7. Finite Replay

`ReplayMain` provides a controlled process for re-normalizing previously rejected Bronze events:

```text
ReplayMain --entity <entity> --topic <topic> --partition <p> --from-offset-inclusive <offset1> --to-offset-inclusive <offset2> --contract-version 2
```

Replay requirements:
1. The `spark-silver` container must be stopped before Replay starts.
2. Replay reads data from Bronze only.
3. Only the permitted status transition (`rejected → applied`) is performed. Changing event-provenance metadata is forbidden.

---

## 8. Related documents

- [Migration roadmap](../../mysql-spark-iceberg-lakehouse-migration.md)
- [Architecture and runtime contract](architecture-and-runtime.md)
- [MySQL, Kafka, and Avro contract](mysql-kafka-avro.md)
- [Iceberg data model contract](iceberg-data-model.md)
- [Serving and recovery contract](serving-and-recovery.md)
