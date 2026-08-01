# Технический контракт: MySQL, Kafka и Avro (Source & Transport Contract)

- **Статус**: Действующий нормативный контракт (Active normative contract)
- **Назначение**: Описание контракта источниковой БД MySQL, параметров Debezium connector, структуры Kafka топиков и правил совместимости Avro/Apicurio.
- **Порядок авторитетности**: Определяет действующие нормативные требования к OLTP источнику и транспортному слою.

---

## 1. MySQL Source Contract

### 1.1 Базы данных и пользователи

В единственном инстансе MySQL содержатся:
- `olist_oltp` — только бизнес-таблицы;
- `olist_simulator` — управляющие таблицы симулятора.

Учетные записи пользователей:
- `olist_admin`: bootstrap схемы и миграции;
- `olist_simulator`: DML бизнес/управляющих таблиц;
- `olist_cdc_reader`: Debezium привилегии и SELECT;
- `olist_spark_reference_reader`: строго чтение таблицы `geolocation` через Spark JDBC;
- `root`: только entrypoint/bootstrap.

Минимальные права `olist_cdc_reader`:

```sql
GRANT RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.*
    TO 'olist_cdc_reader'@'%';
GRANT SELECT, LOCK TABLES ON olist_oltp.* TO 'olist_cdc_reader'@'%';
GRANT INSERT, UPDATE ON olist_simulator.heartbeats TO 'olist_cdc_reader'@'%';
```

Права `olist_spark_reference_reader`:

```sql
GRANT SELECT ON olist_oltp.geolocation
    TO 'olist_spark_reference_reader'@'%';
```

Этот пользователь не имеет прав SELECT на другие таблицы, глобальных прав или DML. Пароль передается через `MYSQL_REFERENCE_READER_PASSWORD_FILE`.

### 1.2 Настройки сервера MySQL

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

Все таблицы используют движок InnoDB.

### 1.3 Бизнес-таблицы и контракты колонок

| Сущность | Первичный ключ (PK) | Бизнес-колонки | CDC Захват |
| --- | --- | --- | --- |
| `customers` | `customer_id` | `customer_unique_id`, `customer_zip_code_prefix`, `customer_city`, `customer_state` | Да |
| `orders` | `order_id` | `customer_id`, `order_status`, 5 timestamps | Да |
| `order_items` | `order_id, order_item_id` | `product_id`, `seller_id`, `shipping_limit_date`, `price`, `freight_value` | Да |
| `order_payments` | `order_id, payment_sequential` | `payment_type`, `payment_installments`, `payment_value` | Да |
| `order_reviews` | `review_id, order_id` | `review_score`, `review_comment_title`, `review_comment_message`, `review_creation_date`, `review_answer_timestamp` | Да |
| `products` | `product_id` | `product_category_name`, 7 атрибутов товара | Да |
| `sellers` | `seller_id` | `seller_zip_code_prefix`, `seller_city`, `seller_state` | Да |
| `product_category_translation` | `product_category_name` | `product_category_name_english` | Да |
| `geolocation` | `geolocation_id` | `geolocation_zip_code_prefix`, `geolocation_lat`, `geolocation_lng`, `geolocation_city`, `geolocation_state` | Нет |

Точные типы и ограничения колонок переносятся дословно из `infra/oltp/initdb/020_create_oltp_schema.sql`. Денежные величины и координаты используют `DECIMAL(18,2)` и `DECIMAL(18,14)` соответственно (`FLOAT` запрещен).

---

## 2. Debezium, Kafka и Avro Contract

### 2.1 Конфигурация коннектора (`olist-mysql-cdc`)

Параметры Debezium Connector:

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

SNT-трансформация unwrap в Debezium **запрещена**. Bronze получает полный envelope с полями `before`, `after`, `source`, `op` и `transaction`. Единственный разрешенный SMT — маршрутизация heartbeat.

### 2.2 Инвентарь топиков Kafka

| Топик | Партиции | Очистка / Retention | Назначение |
| --- | ---: | --- | --- |
| `olist_cdc.olist_oltp.customers` | 1 | `delete`, 7 дней | CDC бизнес-сущности |
| `olist_cdc.olist_oltp.orders` | 3 | `delete`, 7 дней | CDC бизнес-сущности |
| `olist_cdc.olist_oltp.order_items` | 3 | `delete`, 7 дней | CDC бизнес-сущности |
| `olist_cdc.olist_oltp.order_payments` | 3 | `delete`, 7 дней | CDC бизнес-сущности |
| `olist_cdc.olist_oltp.order_reviews` | 3 | `delete`, 7 дней | CDC бизнес-сущности |
| `olist_cdc.olist_oltp.products` | 1 | `delete`, 7 дней | CDC бизнес-сущности |
| `olist_cdc.olist_oltp.sellers` | 1 | `delete`, 7 дней | CDC бизнес-сущности |
| `olist_cdc.olist_oltp.product_category_translation` | 1 | `delete`, 7 дней | CDC бизнес-сущности |
| `olist_cdc.transaction` | 1 | `delete`, 7 дней | Метаданные транзакций |
| `olist_cdc.heartbeat` | 1 | `delete`, 7 дней | Служебный heartbeat |
| `olist_cdc` | 1 | `delete`, unlim | Схемные изменения |
| `olist_cdc.schema_history` | 1 | `delete`, unlim | История Debezium |
| `olist_connect_configs` | 1 | `compact`, unlim | Внутренний Connect |
| `olist_connect_offsets` | 25 | `compact`, unlim | Внутренний Connect |
| `olist_connect_status` | 5 | `compact`, unlim | Внутренний Connect |

Автоматическое создание топиков брокером выключено (`auto.create.topics.enable=false`). Bootstrap создаёт весь списочный состав перед запуском Connect.

### 2.3 Настройки Apicurio Registry

Registry использует SQL-хранилище на базе PostgreSQL:

```text
APICURIO_STORAGE_KIND=sql
APICURIO_STORAGE_SQL_KIND=postgresql
APICURIO_DATASOURCE_URL=jdbc:postgresql://platform-postgres:5432/apicurio
```

Правило совместимости для реестра схем: `BACKWARD_TRANSITIVE`.
Конвертеры Kafka Connect в обязательном порядке используют формат Confluent Avro (`as-confluent=true`, magic byte `0`, 4-byte big-endian schema ID).

Правила эволюции схем:
- Разрешено добавление nullable полей с дефолтом `null`;
- Запрещены in-place переименования, удаление полей, сужение типов и изменения первичного ключа;
- Неизвестный fingerprint останавливает обработку соответствующей сущности до обновления контракта;
- Любое изменение схемы ключа или количества партиций требует полного сброса (`reset`).

---

## 3. Связанные документы

- [Дорожная карта миграции (Roadmap)](../../mysql-spark-iceberg-lakehouse-migration.md)
- [Контракт архитектуры и runtime](architecture-and-runtime.md)
- [Контракт модели данных Iceberg](iceberg-data-model.md)
- [Контракт Spark Structured Streaming](spark-streaming.md)
