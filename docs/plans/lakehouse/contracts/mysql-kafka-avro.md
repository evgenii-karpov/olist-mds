# Technical Contract: MySQL, Kafka and Avro (Source and Transport Contract)

- **Status**: Active normative contract
- **Purpose**: Define the MySQL source database contract, Debezium connector parameters, Kafka topic structure and Avro/Apicurio compatibility rules.
- **Authority**: Defines the current normative requirements for the OLTP source and transport layer.

---

## 1. MySQL Source Contract

### 1.1 Databases and users

The single MySQL instance contains:
- `olist_oltp` — business tables only;
- `olist_simulator` — simulator control tables.

User accounts:
- `olist_admin`: schema bootstrap and migrations;
- `olist_simulator`: business/control-table DML;
- `olist_cdc_reader`: Debezium privileges and SELECT;
- `olist_spark_reference_reader`: read-only access to `geolocation` through Spark JDBC;
- `root`: entrypoint/bootstrap only.

Minimum `olist_cdc_reader` privileges:

```sql
GRANT RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.*
    TO 'olist_cdc_reader'@'%';
GRANT SELECT, LOCK TABLES ON olist_oltp.* TO 'olist_cdc_reader'@'%';
GRANT INSERT, UPDATE ON olist_simulator.heartbeats TO 'olist_cdc_reader'@'%';
```

`olist_spark_reference_reader` privileges:

```sql
GRANT SELECT ON olist_oltp.geolocation
    TO 'olist_spark_reference_reader'@'%';
```

This user has no SELECT rights on other tables, global privileges or DML. The password is supplied through `MYSQL_REFERENCE_READER_PASSWORD_FILE`.

### 1.2 MySQL server settings

```text
character-set-server=utf8mb4
collation-server=utf8mb4_0900_bin
default-time-zone=+00:00
sql_mode=STRICT_TRANS_TABLES,ONLY_FULL_GROUP_BY,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION
server-id=18401
log-bin=mysql-bin
binlog_format=ROW
binlog_row_image=FULL
binlog_row_metadata=FULL
gtid_mode=ON
enforce_gtid_consistency=ON
binlog_expire_logs_seconds=604800
sync_binlog=1
innodb_flush_log_at_trx_commit=1
```

All tables use the InnoDB engine.

### 1.3 Business tables and column contracts

| Entity | Primary key (PK) | Business columns | CDC capture |
| --- | --- | --- | --- |
| `customers` | `customer_id` | `customer_unique_id`, `customer_zip_code_prefix`, `customer_city`, `customer_state` | Yes |
| `orders` | `order_id` | `customer_id`, `order_status`, 5 timestamps | Yes |
| `order_items` | `order_id, order_item_id` | `product_id`, `seller_id`, `shipping_limit_date`, `price`, `freight_value` | Yes |
| `order_payments` | `order_id, payment_sequential` | `payment_type`, `payment_installments`, `payment_value` | Yes |
| `order_reviews` | `review_id, order_id` | `review_score`, `review_comment_title`, `review_comment_message`, `review_creation_date`, `review_answer_timestamp` | Yes |
| `products` | `product_id` | `product_category_name`, 7 product attributes | Yes |
| `sellers` | `seller_id` | `seller_zip_code_prefix`, `seller_city`, `seller_state` | Yes |
| `product_category_translation` | `product_category_name` | `product_category_name_english` | Yes |
| `geolocation` | `geolocation_id` | `geolocation_zip_code_prefix`, `geolocation_lat`, `geolocation_lng`, `geolocation_city`, `geolocation_state` | No |

Exact column types and constraints match `infra/mysql/initdb/020_create_business_schema.sql`. Monetary values and coordinates use `DECIMAL(18,2)` and `DECIMAL(18,14)`, respectively (`FLOAT` is forbidden).

---

## 2. Debezium, Kafka and Avro contract

### 2.1 Connector configuration (`olist-mysql-cdc`)

Debezium Connector parameters:

```text
connector.class=io.debezium.connector.mysql.MySqlConnector
tasks.max=1
database.hostname=mysql
database.port=3306
database.user=olist_cdc_reader
database.server.id=18402
database.include.list=olist_oltp
table.include.list=olist_oltp.customers,olist_oltp.orders,olist_oltp.order_items,olist_oltp.order_payments,olist_oltp.order_reviews,olist_oltp.products,olist_oltp.sellers,olist_oltp.product_category_translation
topic.prefix=olist_cdc
snapshot.mode=initial
include.schema.changes=true
provide.transaction.metadata=true
tombstones.on.delete=true
decimal.handling.mode=precise
time.precision.mode=adaptive_time_microseconds
binary.handling.mode=bytes
schema.history.internal.kafka.topic=olist_cdc.schema_history
schema.history.internal.kafka.bootstrap.servers=kafka:29092
heartbeat.interval.ms=10000
heartbeat.action.query=INSERT INTO olist_simulator.heartbeats (heartbeat_id, heartbeat_ts) VALUES (1, NOW(6)) ON DUPLICATE KEY UPDATE heartbeat_ts=VALUES(heartbeat_ts)
topic.heartbeat.prefix=olist_cdc.heartbeat
predicates=isDerivedHeartbeat
predicates.isDerivedHeartbeat.type=org.apache.kafka.connect.transforms.predicates.TopicNameMatches
predicates.isDerivedHeartbeat.pattern=olist_cdc\.heartbeat\.olist_cdc
transforms=routeHeartbeat
transforms.routeHeartbeat.type=org.apache.kafka.connect.transforms.RegexRouter
transforms.routeHeartbeat.regex=olist_cdc\.heartbeat\.olist_cdc
transforms.routeHeartbeat.replacement=olist_cdc.heartbeat
transforms.routeHeartbeat.predicate=isDerivedHeartbeat
errors.tolerance=none
```

The Debezium unwrap SMT is **forbidden**. Bronze receives the complete envelope with `before`, `after`, `source`, `op` and `transaction` fields. The only allowed SMT is heartbeat routing.

### 2.2 Kafka topic inventory

| Topic | Partitions | Cleanup / Retention | Purpose |
| --- | ---: | --- | --- |
| `olist_cdc.olist_oltp.customers` | 1 | `delete`, 7 days | CDC business entity |
| `olist_cdc.olist_oltp.orders` | 3 | `delete`, 7 days | CDC business entity |
| `olist_cdc.olist_oltp.order_items` | 3 | `delete`, 7 days | CDC business entity |
| `olist_cdc.olist_oltp.order_payments` | 3 | `delete`, 7 days | CDC business entity |
| `olist_cdc.olist_oltp.order_reviews` | 3 | `delete`, 7 days | CDC business entity |
| `olist_cdc.olist_oltp.products` | 1 | `delete`, 7 days | CDC business entity |
| `olist_cdc.olist_oltp.sellers` | 1 | `delete`, 7 days | CDC business entity |
| `olist_cdc.olist_oltp.product_category_translation` | 1 | `delete`, 7 days | CDC business entity |
| `olist_cdc.transaction` | 1 | `delete`, 7 days | Transaction metadata |
| `olist_cdc.heartbeat` | 1 | `delete`, 7 days | Operational heartbeat |
| `olist_cdc` | 1 | `delete`, unlimited | Schema changes |
| `olist_cdc.schema_history` | 1 | `delete`, unlimited | Debezium history |
| `olist_connect_configs` | 1 | `compact`, unlimited | Internal Connect |
| `olist_connect_offsets` | 25 | `compact`, unlimited | Internal Connect |
| `olist_connect_status` | 5 | `compact`, unlimited | Internal Connect |

Automatic broker topic creation is disabled (`auto.create.topics.enable=false`). Bootstrap creates the complete inventory before Connect starts.

### 2.3 Apicurio Registry settings

The Registry uses a PostgreSQL-backed SQL store:

```text
APICURIO_STORAGE_KIND=sql
APICURIO_STORAGE_SQL_KIND=postgresql
APICURIO_DATASOURCE_URL=jdbc:postgresql://platform-postgres:5432/apicurio
```

The schema-registry compatibility rule is `BACKWARD_TRANSITIVE`.
Kafka Connect converters must use Confluent Avro format (`as-confluent=true`, magic byte `0`, 4-byte big-endian schema ID).

Schema-evolution rules:
- Adding nullable fields with default `null` is allowed;
- in-place renames, field removal, type narrowing and primary-key changes are forbidden;
- an unknown fingerprint stops processing for the affected entity until the contract is updated;
- any key-schema or partition-count change requires a full (`reset`) reset.

---

## 3. Related documents

- [Migration roadmap](../../mysql-spark-iceberg-lakehouse-migration.md)
- [Architecture and runtime contract](architecture-and-runtime.md)
- [Iceberg data model contract](iceberg-data-model.md)
- [Spark Structured Streaming contract](spark-streaming.md)
