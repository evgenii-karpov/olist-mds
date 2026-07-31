# Olist MDS: прямая миграция на MySQL, Spark Structured Streaming и Apache Iceberg

## 0. Управление документом

| Поле | Значение |
| --- | --- |
| Статус | Готов к реализации |
| Последнее обновление | 2026-07-31 |
| Базовый commit текущей архитектуры | 1400d08345ad81a0121f0ee85ee9ae81cd575a73e |
| Ветка реализации | feature/mysql-spark-iceberg |
| Основная аудитория | ИИ-агенты реализации и maintainers |
| Финальный fixture | tests/fixtures/olist_small/olist_small.zip |
| SHA-256 fixture | 5cf2ff7a104cae75d8a56cf8c6e00959894154a8d55aed2ddf0e3fa133a13976 |
| Полный parity-test | Один раз в финальном gate; после исправления ошибки повторять до PASS |
| Cloud deployment | Вне этого плана |

Этот документ полностью заменяет прежний план из 36 разделов. Старые phase
numbers, повторяющиеся acceptance gates, PostgreSQL/MySQL shadow-mode,
сохранение локальных volume и встроенная программа GCP/Terraform больше не
являются частью миграции.

Все решения ниже обязательны. Агент реализации не должен выбирать альтернативу,
если документ прямо не называет действие механическим выбором, например
получением digest уже зафиксированного image tag.

---

## 1. Цель и конечное состояние

Текущий локальный путь:

~~~text
PostgreSQL OLTP
  → Debezium PostgreSQL
  → Kafka + Apicurio
  → NiFi
  → MinIO landing/normalized objects
  → Airflow manifest ingestion
  → Python ClickHouse loader
  → ClickHouse raw_cdc
  → dbt batch/realtime models
~~~

должен быть заменён на:

~~~text
MySQL OLTP
  → Debezium MySQL
  → Kafka + Apicurio, Confluent-framed Avro
  → Spark Structured Streaming
  → Apache Iceberg на MinIO через Polaris REST Catalog
      ├── Bronze raw Kafka records
      ├── Silver typed changes
      ├── Silver current state
      ├── transaction/audit tables
      └── immutable reference data
  → finite ClickHouse serving sync
  → native ClickHouse MergeTree/ReplacingMergeTree
  → отдельный dbt-clickhouse project
  → физический ClickHouse Gold
~~~

### 1.1 Целевая архитектура

~~~mermaid
flowchart LR
    M["MySQL 8.4 OLTP"] --> D["Debezium MySQL / Kafka Connect"]
    D --> K["Kafka: Avro CDC topics"]
    A["Apicurio Registry"] <--> D
    K --> B["Spark: Kafka to Bronze"]
    B --> I1["Iceberg Bronze raw records"]
    I1 --> S["Spark: Bronze to Silver"]
    S --> I2["Iceberg Silver changes/current"]
    S --> IA["Iceberg audit/transactions"]
    P["Polaris REST Catalog"] --- I1
    P --- I2
    O["MinIO object storage"] --- P

    I2 --> C0["ClickHouse DataLakeCatalog read-only"]
    I2 --> C1["Finite serving sync"]
    IA --> C1
    C1 --> CE["ClickHouse MergeTree events"]
    C1 --> CC["ClickHouse ReplacingMergeTree current"]
    CE --> DBT["dbt-clickhouse"]
    CC --> DBT
    DBT --> G["Physical ClickHouse Gold"]

    AF["Airflow finite orchestration"] --> C1
    AF --> DBT
    AF --> IM["Iceberg maintenance"]

    PG["PostgreSQL control plane"] --- AF
    PG --- P
    PG --- A
~~~

Durability path заканчивается в Iceberg:

~~~text
MySQL → Debezium → Kafka → Spark → Iceberg
~~~

Airflow и ClickHouse не входят в durability path. Если они остановлены,
MySQL-to-Iceberg продолжает работать. После восстановления serving layer
дочитывает накопленный Iceberg Silver event ledger.

### 1.2 Авторитетность слоёв

| Слой | Ответственность |
| --- | --- |
| MySQL | Единственный authoritative OLTP |
| Kafka | Ограниченный retention transport и replay buffer |
| Apicurio | Wire schemas, schema IDs и compatibility rules |
| Iceberg Bronze | Неизменённые Kafka key/value bytes и transport metadata |
| Iceberg Silver changes | Канонический нормализованный CDC event ledger |
| Iceberg Silver current | Каноническое текущее состояние |
| Iceberg audit/reference | Transactions, errors, progress, geolocation |
| ClickHouse native CDC | Полностью перестраиваемая serving-копия |
| ClickHouse Gold | Физические локальные аналитические модели |
| PostgreSQL control plane | Только Airflow, Polaris и serving-run metadata |

### 1.3 Явно исключённые решения

Не строить:

- параллельный PostgreSQL/MySQL source shadow;
- MySQL-адаптацию NiFi;
- миграцию старых PostgreSQL, Kafka, MinIO, ClickHouse или других Docker
  volume;
- runtime rollback с MySQL обратно на PostgreSQL;
- source_epoch и поддержку нескольких несогласованных local generations;
- второй batch-ingestion восьми CDC-таблиц: historical bootstrap выполняет
  Debezium initial snapshot;
- Gold tables в Iceberg;
- streaming reads из Silver changes/current;
- универсальный dbt project для ClickHouse и BigQuery;
- GCP или Terraform resources в этой ветке;
- полный parity-test на каждой стадии;
- exhaustive restart/chaos matrix.

---

## 2. Зафиксированные технологические версии

| Компонент | Версия |
| --- | --- |
| MySQL | mysql:8.4.10 |
| MySQL Connector/Python | 9.7.0 |
| MySQL Connector/J | 9.7.0 |
| PostgreSQL control plane | postgres:17.10 |
| Kafka | apache/kafka:4.3.1 |
| Debezium | 3.6.0.Final |
| Apicurio Registry | 3.3.0 |
| Spark | 4.1.3, Scala 2.13, Java 17, Python 3.12 |
| Iceberg | 1.11.0 |
| Polaris | 1.6.0 |
| ClickHouse | 26.3.17.4 |
| Airflow | 3.2.1 |
| dbt-clickhouse | 1.10.1 |
| MinIO | Существующий pinned image проекта; latest запрещён |

Использовать Spark 4.1, а не Spark 4.2: Iceberg 1.11.0 публикует runtime для
Spark 4.1/Scala 2.13, но не для Spark 4.2.

Обязательные Spark artifacts:

~~~text
org.apache.iceberg:iceberg-spark-runtime-4.1_2.13:1.11.0
org.apache.iceberg:iceberg-aws-bundle:1.11.0
org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.3
org.apache.spark:spark-avro_2.13:4.1.3
com.mysql:mysql-connector-j:9.7.0
~~~

Источники version decisions:

- Spark 4.1.3: https://spark.apache.org/documentation
- Iceberg 1.11.0 runtime matrix:
  https://iceberg.apache.org/releases/
- Polaris 1.6.0: https://polaris.apache.org/downloads/
- MySQL 8.4 LTS release notes:
  https://dev.mysql.com/doc/relnotes/mysql/8.4/en/

MinIO остаётся только локальным S3-compatible storage. Это не cloud
recommendation: Polaris прямо отмечает MinIO OSS как local-testing dependency
в maintenance mode:
https://polaris.apache.org/guides/minio/

---

## 3. Git и параллельная работа агентов

### 3.1 Ветка

Вся итоговая реализация находится в одной ветке:

~~~text
feature/mysql-spark-iceberg
~~~

Ветка создаётся от:

~~~text
1400d08345ad81a0121f0ee85ee9ae81cd575a73e
~~~

Первый commit ветки должен содержать только этот утверждённый план и deferred
GCP plan. Дальнейшие commits группируются по work packages из раздела 13.

Не создавать long-lived integration и feature branches. Параллельные агенты
работают в одном workspace только по непересекающимся ownership paths и не
выполняют git commit, rebase, checkout или repo-wide formatter. Integration
agent собирает их изменения и создаёт commits после join point.

Если платформа запускает агентов в отдельных worktree, разрешены временные
worktree branches, но они не являются частью delivery topology: integration
agent cherry-pick'ает bounded commits в feature/mysql-spark-iceberg и удаляет
временные branches после merge.

### 3.2 Shared-file rule

До первого integration join только integration agent имеет право изменять:

~~~text
compose.yaml
pyproject.toml
uv.lock
scripts/cdc/local_lab.py
README.md
docs/architecture.md
~~~

Parallel agents обязаны перечислить необходимые изменения shared files в своём
handoff, но не вносить их самостоятельно. Это предотвращает конфликтующие
Compose services, dependency locks и CLI contracts.

### 3.3 Parallel Wave 1

После короткого последовательного шага P0 четыре потока выполняются параллельно.

| Поток | Владелец файлов | Результат | Не изменяет |
| --- | --- | --- | --- |
| A. MySQL source | infra/mysql, scripts/simulation, tests/mysql | DDL, users, seed, simulator MySQL adapter | Compose, dependency lock |
| B. Kafka/CDC contracts | streaming/kafka, streaming/connect, streaming/schemas, tests/cdc_contracts | Topics, connector config, Avro contracts | MySQL implementation, Compose |
| C. Lakehouse platform | docker/spark, infra/polaris, streaming/spark/platform, tests/lakehouse_platform | Spark image, Polaris bootstrap, Iceberg table migrations | Compose, entity normalizers |
| D. ClickHouse/dbt skeleton | infra/clickhouse/lakehouse, dbt/olist_clickhouse, tests/dbt_clickhouse | Native DDL, project graph, source interfaces, business SQL port | Airflow sync, shared dependencies |

Фиксированные interfaces, позволяющие начать параллельно:

~~~text
MySQL service DNS:          mysql
MySQL business database:   olist_oltp
MySQL control database:    olist_simulator
Kafka service DNS:         kafka:29092
Topic prefix:              olist_cdc
Registry DNS:              apicurio-registry:8080
Polaris REST URI:          http://polaris:8181/api/catalog
Catalog name:              olist_lakehouse
Spark catalog alias:       lakehouse
Iceberg namespaces:        bronze, silver, reference, audit
ClickHouse Iceberg DB:     lakehouse
ClickHouse native DBs:     serving_cdc, serving_control, gold_store, gold
~~~

Каждый поток обязан:

1. Работать только в owned paths.
2. Добавить targeted tests рядом с компонентом.
3. Не вводить альтернативных имен или type mappings.
4. Вернуть integration agent список созданных файлов, tests и необходимых
   shared-file changes.
5. Не объявлять end-to-end готовность.

### 3.4 Join J1

Integration agent после завершения A-D:

1. Проверяет, что ownership не нарушен.
2. Добавляет dependencies в pyproject.toml и один раз обновляет uv.lock.
3. Интегрирует services в compose.yaml.
4. Добавляет CLI bootstrap/status contract.
5. Запускает static/unit/Compose checks.
6. Исправляет только integration seams; component logic возвращает владельцу
   соответствующего потока.
7. Создаёт один или несколько тематических commits в основной ветке.

### 3.5 Parallel Wave 2

После J1 и фиксации общего Spark normalization API entity implementations
можно делить между четырьмя агентами:

| Поток | Entities |
| --- | --- |
| S1 | customers, sellers |
| S2 | products, product_category_translation |
| S3 | orders, order_items |
| S4 | order_payments, order_reviews |

Каждый S-agent владеет только:

~~~text
streaming/spark/contracts/<owned-entity>
streaming/spark/normalizers/<owned-entity>
tests/spark_entities/<owned-entity>
~~~

Общими modules, SparkSession builder, schema resolver, MERGE executor и audit
writer владеет один Spark foundation agent. Entity agents не изменяют common
API; необходимое изменение оформляется handoff request.

Параллельно dbt work допускается разделить:

- D1: dimensions и SCD2;
- D2: fact и payment allocation;
- D3: marts и dbt tests.

Join J2 выполняет integration agent вместе со Spark foundation owner. После J2
начинаются serial end-to-end stages; до этого момента полный stack не является
обязательным.

### 3.6 Запрещённая псевдопараллельность

Не назначать разным агентам одновременно:

- compose.yaml;
- один и тот же Spark common module;
- Airflow serving DAG и его PostgreSQL control schema;
- dbt project configuration и generate_schema_name macro;
- final parity runner и canonical comparator;
- массовое удаление legacy paths.

---

## 4. Runtime и lifecycle contract

### 4.1 Compose profiles

Удалить фиксированные container_name, чтобы Compose project names и финальные
sequential parity runs не конфликтовали.

Использовать profiles:

- platform: control PostgreSQL, MySQL, Kafka, topic bootstrap, Apicurio, Kafka
  Connect, MinIO, Polaris, Spark master/worker;
- streaming: Bronze и Silver Spark drivers;
- serving: ClickHouse и Airflow;
- observability: exporters, Prometheus, Grafana, Loki.

Service names:

~~~text
platform-postgres
mysql
kafka
kafka-topics
apicurio-registry
kafka-connect
minio
minio-init
polaris
polaris-bootstrap
spark-master
spark-worker
spark-bronze
spark-silver
clickhouse
clickhouse-init
airflow
~~~

Spark запускается как standalone cluster: один master, один worker с defaults
4 cores / 6 GiB. Bronze получает один executor core, Silver два; один core
остаётся finite jobs. Значения переопределяются environment variables.

### 4.2 Единственный local CLI

Адаптировать scripts/cdc/local_lab.py и сделать его единственной documented
точкой управления:

~~~text
doctor
reset --yes
bootstrap --archive <zip>
up
down
seed --archive <zip> --run-id <id> --random-seed <n>
start-streaming
wait-caught-up --timeout <seconds>
sync-serving
rebuild-serving
run-maintenance
status
validate
final-parity --confirm-destructive
~~~

Command contract:

- reset --yes выполняет только проверенный docker compose down -v
  --remove-orphans; host directories не удаляются;
- bootstrap не удаляет volume, требует пустой consistency domain, запускает
  platform, создаёт catalog/tables, seed'ит MySQL, регистрирует connector и
  запускает streaming/serving;
- seed отказывается работать, если connector зарегистрирован или business
  tables непусты;
- down сохраняет volume;
- rebuild-serving удаляет и перестраивает только ClickHouse derived state;
- команды имеют bounded timeout, secret redaction и JSON result/status.

Happy path:

~~~powershell
uv sync --all-groups
python scripts/cdc/local_lab.py doctor
python scripts/cdc/local_lab.py reset --yes
python scripts/cdc/local_lab.py bootstrap --archive tests/fixtures/olist_small/olist_small.zip
python scripts/cdc/local_lab.py wait-caught-up --timeout 1200
python scripts/cdc/local_lab.py sync-serving
python scripts/cdc/local_lab.py validate
~~~

### 4.3 Disposable-state policy

В единый consistency domain входят:

~~~text
MySQL
Kafka и Kafka Connect state
Apicurio state
MinIO/Iceberg objects
Polaris metadata
Spark checkpoints
ClickHouse
Airflow/control PostgreSQL
~~~

Все Docker volume полностью disposable. Существующие PostgreSQL, Kafka, MinIO,
ClickHouse и другие volume не переносятся.

Обычный restart сохраняет volume. Если потерян или вручную удалён любой
authoritative volume, checkpoint, catalog metadata или Kafka offsets стали
старше retention, частичный recovery запрещён: выполнить reset --yes и
deterministic bootstrap.

Единственное исключение — ClickHouse: он производный и восстанавливается через
rebuild-serving.

Следствия:

- source_epoch не существует;
- event_id равен topic:partition:offset внутри одного lab generation;
- Kafka reset требует сброса всего consistency domain;
- изменение topic partition count или key schema требует полного reset;
- Git branch является rollback boundary до merge;
- runtime rollback на PostgreSQL не проектируется.

### 4.4 Configuration interface

Core applications читают configuration только через:

~~~text
MYSQL_HOST
MYSQL_PORT
MYSQL_DATABASE
KAFKA_BOOTSTRAP_SERVERS
APICURIO_REGISTRY_URL
ICEBERG_CATALOG_URI
ICEBERG_CATALOG_NAME
ICEBERG_WAREHOUSE
OBJECT_STORE_ENDPOINT
OBJECT_STORE_REGION
OBJECT_STORE_PATH_STYLE
OBJECT_STORE_CREDENTIAL_PROVIDER
SPARK_CHECKPOINT_ROOT
CLICKHOUSE_HOST
CLICKHOUSE_PORT
DBT_PROJECT_DIR
DBT_TARGET
~~~

Secrets внутри containers передаются через переменные с суффиксом _FILE.
Plaintext passwords/tokens в Compose environment, logs, exceptions и reports
запрещены.

---

## 5. MySQL source contract

### 5.1 Databases и users

В одном MySQL instance создать:

~~~text
olist_oltp       — только business tables
olist_simulator  — simulation/control tables
~~~

Users:

- olist_admin: schema bootstrap и migrations;
- olist_simulator: DML business/control;
- olist_cdc_reader: Debezium privileges и SELECT;
- root: только entrypoint/bootstrap.

Минимальные grants для olist_cdc_reader:

~~~sql
GRANT RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.*
    TO 'olist_cdc_reader'@'%';
GRANT SELECT, LOCK TABLES ON olist_oltp.* TO 'olist_cdc_reader'@'%';
GRANT INSERT, UPDATE ON olist_simulator.heartbeats TO 'olist_cdc_reader'@'%';
~~~

Последний grant нужен heartbeat.action.query; других DML-прав на control database
у Debezium нет.

### 5.2 MySQL server settings

~~~text
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
~~~

Все tables используют InnoDB.

### 5.3 Business tables

| Entity | Primary key | Business columns | CDC |
| --- | --- | --- | --- |
| customers | customer_id | customer_unique_id, zip, city, state | Да |
| orders | order_id | customer_id, status, пять timestamps | Да |
| order_items | order_id, order_item_id | product_id, seller_id, shipping timestamp, price, freight | Да |
| order_payments | order_id, payment_sequential | type, installments, value | Да |
| order_reviews | review_id, order_id | score, title, message, creation/answer timestamps | Да |
| products | product_id | category и семь product attributes | Да |
| sellers | seller_id | zip, city, state | Да |
| product_category_translation | product_category_name | English name | Да |
| geolocation | generated geolocation_id | zip, lat, lng, city, state | Нет |

Имена колонок являются wire contract и не исправляются даже при наличии опечатки:

| Entity | Точный column contract |
| --- | --- |
| customers | customer_id VARCHAR(64) PK; customer_unique_id VARCHAR(64) NOT NULL; customer_zip_code_prefix VARCHAR(16) NOT NULL; customer_city VARCHAR(256) NOT NULL; customer_state VARCHAR(2) NOT NULL CHECK REGEXP `^[A-Z]{2}$` |
| sellers | seller_id VARCHAR(64) PK; seller_zip_code_prefix VARCHAR(16) NOT NULL; seller_city VARCHAR(256) NOT NULL; seller_state VARCHAR(2) NOT NULL CHECK REGEXP `^[A-Z]{2}$` |
| product_category_translation | product_category_name VARCHAR(256) PK; product_category_name_english VARCHAR(256) NOT NULL |
| products | product_id VARCHAR(64) PK; product_category_name VARCHAR(256) NULL FK; product_name_lenght, product_description_lenght, product_photos_qty, product_weight_g, product_length_cm, product_height_cm, product_width_cm — nullable INT CHECK >= 0 |
| orders | order_id VARCHAR(64) PK; customer_id VARCHAR(64) NOT NULL FK; order_status VARCHAR(32) enum-check; order_purchase_timestamp DATETIME(6) NOT NULL; order_approved_at, order_delivered_carrier_date, order_delivered_customer_date nullable DATETIME(6); order_estimated_delivery_date DATETIME(6) NOT NULL |
| order_items | order_id VARCHAR(64), order_item_id INT > 0 composite PK; product_id/seller_id VARCHAR(64) FK; shipping_limit_date DATETIME(6); price/freight_value DECIMAL(18,2) CHECK >= 0; все NOT NULL |
| order_payments | order_id VARCHAR(64), payment_sequential INT > 0 composite PK; payment_type VARCHAR(32) enum-check; payment_installments INT CHECK >= 0; payment_value DECIMAL(18,2) CHECK >= 0; все NOT NULL |
| order_reviews | review_id VARCHAR(64), order_id VARCHAR(64) composite PK; review_score INT CHECK 1..5; review_comment_title VARCHAR(1024) NULL; review_comment_message TEXT NULL; review_creation_date/review_answer_timestamp DATETIME(6) NOT NULL и answer >= creation |
| geolocation | geolocation_id BIGINT AUTO_INCREMENT PK; geolocation_zip_code_prefix VARCHAR(16); geolocation_lat/geolocation_lng DECIMAL(18,14); geolocation_city VARCHAR(256); geolocation_state VARCHAR(2); business columns NOT NULL, coordinate/state checks сохранены |

Enum-checks переносятся дословно из infra/oltp/initdb/020_create_oltp_schema.sql.
Foreign keys остаются, но DEFERRABLE удаляется как неподдерживаемый MySQL синтаксис.

Сохранить существующие business checks и foreign keys, кроме PostgreSQL-specific
DEFERRABLE.

Seed order:

~~~text
product_category_translation
customers
sellers
products
orders
order_items
order_payments
order_reviews
geolocation
~~~

### 5.4 Type mapping

| Логический тип | MySQL | Spark/Iceberg | ClickHouse |
| --- | --- | --- | --- |
| ID/text | VARCHAR(n), TEXT | string | String |
| Counter | INT | int | Int32 |
| Generated ID | BIGINT AUTO_INCREMENT | long | Int64 |
| Money | DECIMAL(18,2) | decimal(18,2) | Decimal(18,2) |
| Coordinates | DECIMAL(18,14) | decimal(18,14) | Decimal(18,14) |
| Business time | DATETIME(6), UTC semantics | microsecond timestamp | DateTime64(6, UTC) |
| Operational time | UTC timestamp | Iceberg timestamptz | DateTime64(6, UTC) |
| Control JSON | JSON | Не входит в business Silver | Audit String only |

FLOAT запрещён для денег и координат.

### 5.5 Simulator port

Перенести существующие simulator control tables и state machine в
olist_simulator.

Обязательные изменения:

- ON CONFLICT заменить на INSERT ON DUPLICATE KEY UPDATE или INSERT IGNORE;
- jsonb заменить на JSON;
- PostgreSQL sequence/identity заменить на AUTO_INCREMENT или deterministic
  application IDs;
- использовать mysql-connector-python и зафиксировать dependency в uv.lock;
- удалить dual-source adapter и PostgreSQL simulator implementation;
- сохранить transaction-boundary stop, deterministic random seed, replay
  timestamp mapping и injected transaction rollback;
- выполнять seed batches по 5 000 rows, одной transaction на entity.

Small fixture counts:

~~~text
customers                        8
orders                          12
order_items                     16
order_payments                  14
order_reviews                   12
products                         8
sellers                          4
product_category_translation     5
geolocation                      6
~~~

---

## 6. Debezium, Kafka и Avro contract

### 6.1 Connector

Создать connector olist-mysql-cdc:

~~~text
connector.class=io.debezium.connector.mysql.MySqlConnector
tasks.max=1
database.hostname=mysql
database.port=3306
database.user=olist_cdc_reader
database.server.id=18402
database.include.list=olist_oltp
table.include.list=<ровно 8 CDC tables>
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
~~~

Debezium unwrap SMT запрещён. Bronze получает полный envelope с before, after,
source, op и transaction. Единственный разрешённый SMT — приведённый выше
router, нормализующий generated heartbeat topic в olist_cdc.heartbeat.

Heartbeat action обновляет olist_simulator.heartbeats через ON DUPLICATE KEY
UPDATE. Control database и geolocation не входят в captured table list.

Connector bootstrap читает пароль из Docker secret, подставляет
database.password только в тело POST /connectors и редактирует это поле во всех
логах/diagnostic dumps. Пароль не хранится в JSON, environment или Git.

### 6.2 Topics

| Topic | Partitions | Назначение |
| --- | ---: | --- |
| olist_cdc.olist_oltp.customers | 1 | Business CDC |
| olist_cdc.olist_oltp.orders | 3 | Business CDC |
| olist_cdc.olist_oltp.order_items | 3 | Business CDC |
| olist_cdc.olist_oltp.order_payments | 3 | Business CDC |
| olist_cdc.olist_oltp.order_reviews | 3 | Business CDC |
| olist_cdc.olist_oltp.products | 1 | Business CDC |
| olist_cdc.olist_oltp.sellers | 1 | Business CDC |
| olist_cdc.olist_oltp.product_category_translation | 1 | Business CDC |
| olist_cdc.transaction | 1 | BEGIN/END metadata |
| olist_cdc.heartbeat | 1 | Operational heartbeat |
| olist_cdc | 1 | External schema-change events |
| olist_cdc.schema_history | 1 | Internal Debezium history |
| olist_connect_configs | 1 | Internal Connect config state |
| olist_connect_offsets | 25 | Internal Connect offset state |
| olist_connect_status | 5 | Internal Connect status state |

Replication factor локально равен 1. Business, transaction и heartbeat topics:
cleanup.policy=delete, retention.ms=604800000. olist_cdc и
olist_cdc.schema_history: одна partition, cleanup.policy=delete,
retention.ms=-1, retention.bytes=-1; internal schema history нельзя compact.
Три Connect internal topics: cleanup.policy=compact, retention.ms=-1. Auto topic
creation отключён; bootstrap создаёт весь список до запуска Connect.

DLQ topics старого NiFi-контура удалить. Permanent normalization errors
хранятся в Iceberg audit, raw payload — в Bronze.

### 6.3 Apicurio settings

Registry использует control PostgreSQL, а не KafkaSQL, чтобы не добавлять
скрытые Kafka topics вне topic manifest:

~~~text
APICURIO_STORAGE_KIND=sql
APICURIO_STORAGE_SQL_KIND=postgresql
APICURIO_DATASOURCE_URL=jdbc:postgresql://platform-postgres:5432/apicurio
APICURIO_DATASOURCE_USERNAME_FILE=/run/secrets/apicurio_db_user
APICURIO_DATASOURCE_PASSWORD_FILE=/run/secrets/apicurio_db_password
~~~

До регистрации connector bootstrap создаёт registry group/compatibility rule
BACKWARD_TRANSITIVE. В connector JSON дословно задать для key и value:

~~~text
key.converter=io.apicurio.registry.utils.converter.AvroConverter
key.converter.apicurio.registry.url=http://apicurio-registry:8080/apis/registry/v2
key.converter.apicurio.registry.auto-register=true
key.converter.apicurio.registry.find-latest=true
key.converter.apicurio.registry.as-confluent=true
key.converter.apicurio.use-id=contentId
key.converter.apicurio.registry.headers.enabled=false
key.converter.schemas.enable=false
key.converter.apicurio.registry.artifact-resolver-strategy=io.apicurio.registry.serde.strategy.TopicIdStrategy
value.converter=io.apicurio.registry.utils.converter.AvroConverter
value.converter.apicurio.registry.url=http://apicurio-registry:8080/apis/registry/v2
value.converter.apicurio.registry.auto-register=true
value.converter.apicurio.registry.find-latest=true
value.converter.apicurio.registry.as-confluent=true
value.converter.apicurio.use-id=contentId
value.converter.apicurio.registry.headers.enabled=false
value.converter.schemas.enable=false
value.converter.apicurio.registry.artifact-resolver-strategy=io.apicurio.registry.serde.strategy.TopicIdStrategy
schema.name.adjustment.mode=avro
~~~

Если выбранный Apicurio image не обрабатывает *_FILE сам, entrypoint обязан
считать secret files и экспортировать значения только в process environment;
compose config и logs всё равно не должны содержать credentials.

Numeric schema IDs ephemeral. Durable schema identity — canonical SHA-256
fingerprint.

Для каждой entity versioned contract содержит:

~~~text
topic
primary key
MySQL column contract
allowed key/value Avro fingerprints
Spark reader schema
Iceberg projection
nullable/additive evolution rules
contract_version
~~~

Evolution policy:

- nullable field с default null разрешён;
- rename, drop, narrowing и PK/key-schema change запрещены in-place;
- неизвестный fingerprint останавливает affected Silver query до новой contract
  version;
- incompatible registry registration останавливает connector;
- key-schema или partition-count change требует reset.

Debezium/Apicurio Avro reference:
https://debezium.io/documentation/reference/stable/configuration/avro.html

Spark from_avro требует явную writer schema и не разрешает registry schema ID
автоматически:
https://spark.apache.org/docs/latest/sql-data-sources-avro.html

---

## 7. Polaris, MinIO и Iceberg

### 7.1 Control PostgreSQL

platform-postgres содержит отдельные databases/users:

~~~text
airflow
olist_control
polaris
apicurio
~~~

Business data в PostgreSQL запрещены.

### 7.2 Catalog и buckets

Создать Polaris catalog:

~~~text
catalog resource / REST warehouse parameter: olist_lakehouse
default-base-location: s3://olist-lakehouse/warehouse
REST URI: http://polaris:8181/api/catalog
S3 endpoint и endpoint-internal: http://minio:9000
S3 region: us-east-1
~~~

MinIO buckets:

~~~text
olist-lakehouse
olist-checkpoints
~~~

Checkpoints физически отделены от Iceberg warehouse. Iceberg maintenance не
получает checkpoint bucket/prefix.

polaris-bootstrap идемпотентно создаёт:

- Spark writer principal;
- ClickHouse read-only principal;
- Airflow maintenance principal;
- bootstrap administrator;
- catalog roles и grants.

Generated runtime credentials сохраняются в ephemeral credentials volume с
mode 0600 и не коммитятся. Рассогласование credential volume и Polaris DB
требует полного reset.

### 7.3 Namespaces и properties

Namespaces:

~~~text
bronze
silver
reference
audit
~~~

Gold namespace в Iceberg не создавать.

Общие table properties:

~~~text
format-version=2
write.format.default=parquet
write.parquet.compression-codec=zstd
write.target-file-size-bytes=134217728
write.metadata.delete-after-commit.enabled=true
write.metadata.previous-versions-max=20
~~~

Partitioning:

- bronze.mysql_cdc_records: days(ingested_at);
- bronze.avro_schemas: unpartitioned;
- silver entity changes: days(source_ts);
- silver entity current: unpartitioned;
- reference.geolocation: unpartitioned;
- growing audit tables: days(recorded_at).

### 7.4 Bronze records

bronze.mysql_cdc_records хранит external Debezium topics, но не Connect internal
topics и не schema_history.

Columns:

~~~text
event_id
record_kind
topic
partition
offset
kafka_timestamp
kafka_timestamp_type
headers
key_bytes
value_bytes
is_tombstone
key_schema_id
value_schema_id
key_sha256
value_sha256
key_framing_valid
value_framing_valid
framing_error
ingest_batch_id
spark_query_id
ingested_at
~~~

record_kind:

~~~text
data
tombstone
transaction
heartbeat
schema_change
~~~

Bronze не декодирует Debezium source fields. Допустима только проверка
Confluent framing byte и извлечение 4-byte schema ID. Malformed record всё
равно сохраняется.

event_id равен topic:partition:offset. Raw bytes не преобразуются.

### 7.5 Schema archive

bronze.avro_schemas:

~~~text
schema_id
fingerprint_sha256
subject
registry_version
schema_json
references_json
spark_self_contained_schema_json
first_seen_at
last_verified_at
~~~

Один numeric ID с двумя fingerprints внутри lab generation считается fatal
registry corruption.

### 7.6 Silver changes

Для каждой из восьми entity создать:

~~~text
silver.<entity>_changes
silver.<entity>_current
~~~

Common changes columns:

~~~text
event_id
op
is_snapshot
is_deleted
apply_status
error_code
error_message
<business columns>
source_ts
source_server_id
source_gtid
source_binlog_file
source_binlog_file_index
source_binlog_pos
source_row
transaction_id
transaction_total_order
transaction_data_collection_order
kafka_topic
kafka_partition
kafka_offset
kafka_timestamp
key_schema_id
value_schema_id
schema_fingerprint
contract_version
before_row_hash
after_row_hash
row_hash
bronze_ingested_at
normalized_at
~~~

Business columns представляют:

- after для valid r, c, u;
- before для d;
- NULL для rejected non-tombstone event;
- tombstone не создаёт business change.

apply_status имеет только applied или rejected. error_code/error_message равны
NULL для applied и содержат стабильный machine code/короткое redacted описание
для rejected.

Changes — логически immutable event ledger, но физически пишутся insert-only
MERGE ON event_id. Это обеспечивает idempotency при partial micro-batch retry.

### 7.7 Silver current

Current содержит business columns плюс:

~~~text
is_deleted
deleted_at
last_event_id
last_source_ts
last_transaction_id
last_kafka_partition
last_kafka_offset
last_row_hash
contract_version
updated_at
~~~

Micro-batch algorithm:

1. Decode и validate events.
2. Deduplicate по event_id.
3. Insert-only MERGE changes.
4. Выбрать последнюю event per business key внутри batch.
5. Проверить, что versions одного key имеют один partition.
6. MERGE current только при incoming offset больше stored offset.
7. После обоих commits обновить audit progress.

Если changes commit прошёл, а current/progress нет, retry безопасен. Старое
событие не перезаписывает новое.

Kafka offset является row version: stable key schema сохраняет один business
key в одном partition. MySQL binlog coordinates сохраняются для audit, но не
используются как глобальный порядок.

### 7.8 Audit tables

Создать:

~~~text
audit.mysql_transactions
audit.silver_progress
audit.normalization_errors
audit.schema_violations
audit.maintenance_runs
audit.serving_sync_reports
audit.schema_migrations
~~~

Permanent malformed/business-invalid event:

- остаётся в Bronze;
- получает idempotent changes row с apply_status=rejected и audit row;
- не обновляет current;
- позволяет query продвинуть checkpoint.

Transaction с rejected event получает status=REJECTED в
audit.mysql_transactions. Serving sync не публикует эту transaction и не
переходит её boundary; report выводит точные entity/event_id/error_code. После
исправления contract/code finite replay заменяет rejected outcome на applied.
Rejected event во время initial snapshot является bootstrap-fatal: snapshot не
считается завершённым.

Transient registry/catalog/storage error не продвигает checkpoint.

Contract incompatibility фиксируется и останавливает только affected entity
query.

### 7.9 Geolocation

geolocation остаётся в MySQL, но исключена из Debezium. После seed one-shot
Spark JDBC job пишет reference.geolocation:

~~~text
business columns
source_archive_sha256
source_row_number
loaded_at
~~~

В v1 geolocation immutable и не входит в финальный parity.

---

## 8. Spark Structured Streaming

### 8.1 Image

Создать olist-spark:4.1.3-iceberg1.11.0 на основе exact image
apache/spark:4.1.3-scala2.13-java17-python3-ubuntu.

Все jars скачиваются на build stage, проверяются SHA-256 и сохраняются в image.
Runtime download запрещён.

Для S3A checkpoint access добавить hadoop-aws той же версии, что Hadoop
libraries Spark image. Docker build автоматически проверяет совпадение и
завершается ошибкой при mismatch.

Spark configuration:

~~~text
spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions
spark.sql.catalog.lakehouse=org.apache.iceberg.spark.SparkCatalog
spark.sql.catalog.lakehouse.type=rest
spark.sql.catalog.lakehouse.uri=http://polaris:8181/api/catalog
spark.sql.catalog.lakehouse.warehouse=olist_lakehouse
spark.sql.catalog.lakehouse.credential=<spark-principal-id>:<spark-principal-secret>
spark.sql.catalog.lakehouse.scope=PRINCIPAL_ROLE:ALL
spark.sql.catalog.lakehouse.oauth2-server-uri=http://polaris:8181/api/catalog/v1/oauth/tokens
spark.sql.catalog.lakehouse.header.X-Iceberg-Access-Delegation=vended-credentials
spark.sql.catalog.lakehouse.token-refresh-enabled=false
spark.sql.catalog.lakehouse.io-impl=org.apache.iceberg.aws.s3.S3FileIO
spark.sql.session.timeZone=UTC
spark.sql.shuffle.partitions=4
~~~

Bootstrap генерирует Spark properties file mode 0600 из Docker secrets. Ни
principal credential, ни временные S3 credentials не передаются через CLI и не
печатаются в Spark event logs.

### 8.2 Streaming topology

kafka_to_bronze:

- одна query;
- один checkpoint;
- 8 business topics плюс transaction, heartbeat и schema-change;
- includeHeaders=true;
- append write только в bronze.mysql_cdc_records;
- processing trigger 60 seconds;
- stable query name/checkpoint path.

spark-silver содержит десять независимых queries:

1. Generic schema capture.
2. Transaction metadata normalization.
3. Customers.
4. Orders.
5. Order items.
6. Order payments.
7. Order reviews.
8. Products.
9. Sellers.
10. Product category translation.

Checkpoint path:

~~~text
s3a://olist-checkpoints/<query-name>/contract-v<version>/
~~~

### 8.3 Query supervisor

Silver app не завершает все queries после первой termination.

Supervisor:

- отслеживает каждую query;
- перезапускает transient failure с bounded exponential backoff;
- сохраняет остальные queries active;
- не перезапускает fatal contract violation до новой contract version;
- публикует state, last progress и error class;
- container health считается degraded, если entity query остановлена, но
  container остаётся запущен для остальных entities.

### 8.4 Dynamic Avro decoding

Для micro-batch:

1. Получить distinct key/value schema ID pairs.
2. Дождаться schemas в bronze.avro_schemas.
3. Рекурсивно разрешить Apicurio references.
4. Использовать self-contained writer schema.
5. Отфильтровать records schema pair.
6. Удалить 5-byte Confluent prefix.
7. Декодировать Spark from_avro в FAILFAST mode.
8. Применить evolved reader schema из entity contract.
9. Объединить groups через unionByName с missing columns.
10. Проверить op, PK, decimal scale, time и topic/entity mapping.
11. Выполнить changes/current algorithm.

Maximum 32 distinct schema pairs per micro-batch. Превышение считается schema
storm и останавливает affected query.

### 8.5 Запрет Silver streaming reads

Не использовать readStream для Silver changes/current. MERGE создаёт
overwrite/delete snapshots, а Iceberg streaming read поддерживает только append
snapshots:
https://iceberg.apache.org/docs/latest/spark-structured-streaming/

ClickHouse serving и dbt читают Silver только finite batch.

### 8.6 Finite replay

Общие pure transform/apply functions должны принимать:

- streaming micro-batch DataFrame;
- finite Bronze DataFrame с явным offset range.

Finite replay выполняет те же idempotent MERGE. Отдельную batch business logic
не создавать.

---

## 9. ClickHouse serving

### 9.1 Read-only Iceberg catalog

Создать ClickHouse DataLakeCatalog database lakehouse для Polaris REST.

~~~sql
SET allow_database_iceberg = 1;
CREATE DATABASE lakehouse
ENGINE = DataLakeCatalog('http://polaris:8181/api/catalog')
SETTINGS catalog_type = 'rest',
         warehouse = 'olist_lakehouse',
         catalog_credential = '<clickhouse-principal-id>:<secret>',
         storage_endpoint = 'http://minio:9000/olist-lakehouse';
~~~

Init shell читает credential из Docker secret и выполняет ephemeral SQL с
отключённым query logging; SQL с plaintext secret не коммитится. Acceptance
smoke обязан перечислить silver.customers_current, выполнить count и прочитать
зафиксированный Iceberg snapshot/time-travel.

Он используется для:

- zero-copy Bronze/Silver inspection;
- serving sync;
- snapshot/time-travel smoke;
- ClickHouse rebuild.

ClickHouse не пишет Iceberg.

Reference:
https://clickhouse.com/blog/query-your-catalog-clickhouse-cloud

### 9.2 Native CDC tables

Для каждой entity:

~~~text
serving_cdc.<entity>_events
serving_cdc.<entity>_current_versions
~~~

Events:

~~~sql
ENGINE = MergeTree
PARTITION BY sync_run_seq
ORDER BY (kafka_partition, kafka_offset)
~~~

Current versions:

~~~sql
ENGINE = ReplacingMergeTree(kafka_offset)
PARTITION BY tuple()
ORDER BY (<business primary key>)
~~~

Каждая current version хранит sync_run_seq, is_deleted и полный row state.
Stable views учитывают только published sync runs.

Обязательные learning tests:

- plain SELECT может видеть несколько versions;
- SELECT FINAL возвращает latest version;
- argMax возвращает тот же logical result;
- deleted latest version исключается только после deduplication;
- scheduled OPTIMIZE TABLE FINAL отсутствует.

ClickHouse guidance:
https://clickhouse.com/resources/engineering/clickhouse-optimize-table-final

### 9.3 Serving sync boundary

Airflow DAG olist_lakehouse_serving_sync:

1. В PostgreSQL olist_control выделяет monotonic sync_run_seq и deterministic
   sync_run_id.
2. Для первого run ждёт завершения Debezium snapshot и initial offsets.
3. Для следующих run выбирает последний последовательный transaction END, для
   которого Silver содержит все заявленные events.
4. Фиксирует previous/target transaction boundary и partition offsets.
5. Materializes exact event set из Iceberg changes.
6. Проверяет counts, event_id uniqueness и entity set.
7. Перезаписывает event partitions только данного sync_run_seq.
8. Добавляет current versions.
9. Запускает dbt candidate build.
10. После dbt tests вставляет publication row в
    serving_control.published_runs.
11. После publication обновляет PostgreSQL watermarks.
12. Сохраняет report и удаляет staging.

Все candidate data записываются до publication. Stable views включают только
run sequences из published_runs. Crash до publication не показывает partial
Gold/current. Retry переиспользует тот же sync_run_seq.

Если complete transactions отсутствуют, DAG завершается successful no-op.

### 9.4 Rebuild

rebuild-serving:

1. Проверяет доступность Polaris/Iceberg.
2. Удаляет только ClickHouse serving_cdc, serving_control, gold_store и gold.
3. Читает полный Silver event ledger.
4. Перестраивает MergeTree events/current versions.
5. Запускает полный dbt build.
6. Публикует initial rebuilt run.
7. Не изменяет MySQL, Kafka, Iceberg или Spark checkpoints.

---

## 10. Отдельный dbt-clickhouse Gold

Создать dbt/olist_clickhouse. В проекте отсутствуют Redshift/BigQuery branches
и adapter-dispatch compatibility macros.

Физические models:

~~~text
dim_date
dim_order_status
dim_seller
dim_customer_scd2
dim_product_scd2
fact_order_items
mart_daily_revenue
mart_monthly_arpu
~~~

Storage:

~~~text
gold_store.<model>
ENGINE = MergeTree
PARTITION BY sync_run_seq
ORDER BY <natural grain>
~~~

Public interface:

~~~text
gold.<model>
~~~

gold models являются stable views последнего published run. Хранить current и
previous Gold partitions; более старые удаляет finite cleanup.

Run contract:

~~~text
dbt build
  --project-dir dbt/olist_clickhouse
  --vars sync_run_seq=<n>,sync_run_id=<id>
~~~

Каждый run строит полную analytical projection для Olist-size data. Старые
manifest changed-key macros и incremental partition widening удалить.

### 10.1 SCD2

Customer business key: customer_unique_id.

Product business key: product_id.

Rules:

- consecutive identical row hashes collapse;
- snapshot op=r открывает initial version в 1900-01-01 00:00:00 UTC;
- последующие valid_from используют source event timestamp;
- timestamp ties разрешает полный event order: topic, partition, offset;
- delete закрывает active version и не создаёт visible dimension row;
- surrogate key детерминированно хэширует business key и opening event_id;
- customer_unique_id collapse детерминированно выбирает последнее событие, затем
  customer_id как tie-breaker;
- изменение product_category_translation закрывает/открывает product SCD2
  versions для всех текущих products этой category;
- technical SCD windows не входят в legacy parity.

### 10.2 Fact и marts

Fact grain:

~~~text
order_id, order_item_id
~~~

Сохранить business formulas. Payment allocation считается на item grain как
round(sum(order_payments.payment_value) * (price + freight_value) /
sum(price + freight_value) over order, 2); при нулевом denominator результат
NULL. Остальные обязательные formulas:

- payment allocation;
- gross item amount;
- delivery days/delay;
- late delivery flag;
- daily revenue;
- monthly ARPU и repeat customer rate.

Будущий dbt-bigquery является отдельным проектом. Общими остаются только:

- business grains;
- metric definitions;
- test fixture;
- canonical parity contract.

---

## 11. Airflow, maintenance и observability

### 11.1 Airflow boundary

Airflow не запускает и не рестартует continuous Spark queries.

Оставить finite DAGs:

~~~text
olist_lakehouse_serving_sync
olist_iceberg_maintenance
olist_clickhouse_rebuild
olist_lakehouse_quality
~~~

Continuous services управляются Compose restart policy и Spark supervisor.

### 11.2 Iceberg maintenance

Finite Spark procedures:

~~~text
rewrite_data_files
rewrite_manifests
expire_snapshots
remove_orphan_files
~~~

Defaults:

- snapshot retention 7 дней;
- retain_last 20;
- orphan minimum age 72 часа;
- table location передаётся явно;
- bucket root не передаётся;
- checkpoint bucket недоступен maintenance principal.

### 11.3 Metrics

Обязательные metrics:

- Debezium connector/snapshot state;
- Kafka end offsets и Bronze lag;
- Spark query state, batch ID, input rows, processing time, failure class;
- age последнего Bronze snapshot;
- per-entity Silver offsets/lag;
- schema capture lag;
- normalization/schema violations;
- last complete source transaction;
- last published serving run/freshness;
- ClickHouse duplicate versions before FINAL;
- Iceberg file count, average file size, snapshot count;
- maintenance result/duration.

Удалить NiFi metrics и PostgreSQL OLTP exporter. Добавить MySQL exporter и Spark
metrics endpoint. Observability failure не останавливает data path.

---

## 12. Failure и recovery contract

| Failure | Обязательное поведение |
| --- | --- |
| MySQL временно недоступен | Connector retry; downstream обрабатывает backlog |
| Kafka недоступен | Connector и Bronze retry |
| Bronze остановлен | Kafka буферизует до retention |
| Silver entity остановлен | Bronze и остальные entities продолжают |
| Registry transient failure | Известные archived schemas продолжают работать; новый ID ждёт registry |
| Incompatible schema | Только affected entity останавливается fail-closed |
| Polaris/MinIO недоступен | Spark retry; Kafka остаётся buffer |
| Airflow остановлен | Iceberg CDC работает; serving freshness растёт |
| ClickHouse остановлен/потерян | Iceberg работает; rebuild-serving восстанавливает |
| Kafka retention превысил lag | Полный reset/reseed |
| Потерян Spark checkpoint | Полный reset/reseed |
| Потерян Polaris DB/MinIO warehouse | Полный reset/reseed |
| Удалён authoritative volume | Не чинить частично; полный reset/reseed |
| Serving упал до publication | Candidate hidden; retry того же run |
| Serving упал после publication до PG update | Retry завершает metadata без повторной публикации |

---

## 13. Delivery work packages

### P0 — последовательная фиксация interfaces

1. Создать feature/mysql-spark-iceberg от baseline commit.
2. Добавить этот план.
3. Добавить deferred GCP plan.
4. Зафиксировать ownership и shared-file rule.
5. Не запускать legacy full stack.

После P0 стартуют A-D из Parallel Wave 1.

### A — MySQL source

1. Создать MySQL config/init/users.
2. Перенести business DDL.
3. Перенести simulator control schema.
4. Портировать simulator/seeding.
5. Добавить exact type/constraint/fixture tests.
6. Вернуть dependency/shared-config handoff.

### B — CDC contracts

1. Создать topic script.
2. Создать MySQL connector config.
3. Зафиксировать Apicurio settings.
4. Создать eight entity contracts.
5. Адаптировать Avro compatibility checks.
6. Добавить connector/topic/schema tests.

### C — Lakehouse platform

1. Создать Spark image.
2. Добавить Polaris JDBC/bootstrap resources.
3. Добавить MinIO bucket/policy resources.
4. Создать Iceberg migration definitions.
5. Добавить Spark/Polaris/table contract tests.
6. Не реализовывать entity business transforms.

### D — Analytics skeleton

1. Создать ClickHouse DataLakeCatalog/native DDL.
2. Создать dbt/olist_clickhouse project.
3. Зафиксировать source interfaces.
4. Портировать adapter-independent business SQL в ClickHouse-only form.
5. Добавить dbt parse/unit/DDL tests.
6. Не реализовывать Airflow publication.

### J1 — integration join

1. Объединить dependencies и обновить uv.lock один раз.
2. Интегрировать Compose services.
3. Реализовать local_lab platform/bootstrap/status.
4. Выполнить static, unit, Compose и component smoke tests.
5. Зафиксировать common Spark normalization API.

### S — Parallel Wave 2

1. Spark foundation owner реализует Bronze, schema capture, transaction query,
   common decoder/MERGE/audit/supervisor.
2. S1-S4 реализуют entity normalizers по ownership table.
3. D1-D3 реализуют dimensions, fact/marts и tests.
4. Ни один entity/dbt agent не меняет common interfaces.

### J2 — Spark/dbt join

1. Собрать all entity queries.
2. Проверить schema/type consistency.
3. Создать Iceberg tables.
4. Выполнить component-level fixture transform tests.
5. Зафиксировать interface для serving sync.

### E — serial serving integration

1. Реализовать control PostgreSQL schema.
2. Реализовать transaction-complete Airflow sync.
3. Интегрировать ClickHouse events/current.
4. Интегрировать dbt candidate/publication.
5. Реализовать rebuild и maintenance.
6. Добавить observability.

### L — legacy removal

После успешного candidate E2E удалить:

- PostgreSQL OLTP service, DDL, connector и simulator adapter;
- NiFi, bootstrap, repositories, processors, metrics и secrets;
- old MinIO landing/normalized/coverage protocol;
- manifest discovery/loader;
- Kafka DLQ topics;
- raw_cdc ClickHouse ingestion;
- legacy continuous-ingest DAGs;
- legacy realtime dbt models/macros;
- старый cross-adapter dbt/olist_analytics;
- зависимый active AWS/Redshift runtime, поскольку будущий cloud target вынесен
  в GCP plan;
- obsolete tests, dashboards и runbooks.

Baseline остаётся доступен через exact Git commit.

### V — candidate E2E

На clean volumes:

1. Seed small fixture.
2. Debezium initial snapshot.
3. Проверить 79 business snapshot rows в Silver current.
4. Проверить 6 geolocation reference rows.
5. Выполнить multi-table create transaction.
6. Выполнить update.
7. Выполнить delete envelope и tombstone.
8. Один раз одновременно restart Bronze/Silver.
9. Дождаться catch-up без duplicate event_id.
10. Выполнить serving sync.
11. Выполнить dbt build/tests.
12. Проверить FINAL/argMax и Gold.
13. Выполнить один nullable additive schema scenario.
14. Перестроить ClickHouse только из Iceberg.

Это единственный comprehensive candidate E2E до final parity.

### F — final parity

Выполнить разделы 15-16. Этот этап serial и не делится между агентами.

---

## 14. Fast tests и CI

PR CI не запускает full parity.

Обязательные fast checks:

- MySQL DDL и eight-table capture contract;
- seed order, constraints и fixture counts;
- topics, partitions и connector properties;
- Avro framing/schema ID extraction;
- recursive Apicurio reference resolution;
- BACKWARD_TRANSITIVE compatibility;
- nullable additive evolution и forbidden rename/drop/narrowing;
- Debezium op/tombstone mapping;
- event_id, PK и same-key partition invariant;
- multiple events одного key в micro-batch;
- older offset cannot replace newer current;
- retry после partial MERGE;
- transient registry versus contract violation;
- Iceberg table schema/partition/properties;
- checkpoint/warehouse isolation;
- dbt parse, graph и unit/data tests;
- MergeTree/ReplacingMergeTree DDL;
- plain SELECT versus FINAL/argMax;
- publication hides incomplete run;
- Compose config и Airflow DAG imports;
- secret redaction;
- comparator sensitivity.

Ни один checksum не заменяет row-level equality.

---

## 15. Финальный parity runner

Создать:

~~~text
scripts/parity/run_mysql_iceberg_final_parity.py
~~~

Algorithm:

1. Проверить candidate worktree и fixture SHA-256.
2. Создать temporary worktree baseline commit.
3. Запустить legacy stack с COMPOSE_PROJECT_NAME=olist_parity_legacy.
4. Выполнить существующий full batch-versus-CDC path.
5. Экспортировать canonical legacy JSON.
6. Выполнить legacy docker compose down -v.
7. Запустить cleaned candidate с
   COMPOSE_PROJECT_NAME=olist_parity_candidate.
8. Seed того же fixture.
9. Дождаться snapshot/Silver и выполнить serving sync/dbt.
10. Экспортировать candidate canonical JSON.
11. Сравнить и записать report.
12. Выполнить candidate docker compose down -v.
13. Удалить temporary worktree.

Legacy и candidate запускаются последовательно, не одновременно.

Runner требует --confirm-destructive, потому что удаляет только собственные
Compose project volumes.

---

## 16. Parity contract

### 16.1 Current state

Сравнить все business columns:

| Entity | Grain |
| --- | --- |
| customers | customer_id |
| orders | order_id |
| order_items | order_id, order_item_id |
| order_payments | order_id, payment_sequential |
| order_reviews | review_id, order_id |
| products | product_id |
| sellers | seller_id |
| product_category_translation | product_category_name |

Стороны сравнения:

~~~text
baseline:  connection=oltp-postgres, database=olist_oltp, schema=public,
           table=<entity>
candidate: silver.<entity>_current where is_deleted=false
~~~

Transport/source/load metadata не сравниваются.

### 16.2 Fact

Сравнить baseline core.fact_order_items и candidate gold.fact_order_items на
grain:

~~~text
order_id, order_item_id
~~~

Сравнить все nontechnical business columns:

~~~text
customer_id
customer_unique_id
product_id
seller_id
order_status
order_purchase_timestamp
order_approved_at
order_delivered_carrier_date
order_delivered_customer_date
order_estimated_delivery_date
shipping_limit_date
price
freight_value
gross_item_amount
allocated_payment_value
delivery_days
delivery_delay_days
is_delivered_late
~~~

Не сравнивать surrogate/date keys, batch IDs и load timestamps.

### 16.3 Marts

Сравнить baseline marts.<model> и candidate gold.<model>. Перечень published
columns закрытый; агент не может silently исключить колонку:

~~~text
mart_daily_revenue
  grain: order_purchase_date
  columns: order_purchase_date, gross_revenue, allocated_payment_revenue,
           product_revenue, freight_revenue, orders_count, customers_count,
           items_count, average_order_value, average_paid_order_value,
           average_delivery_days, late_deliveries_count

mart_monthly_arpu
  grain: order_month
  columns: order_month, active_customers, total_revenue, arpu, orders_count,
           orders_per_customer, average_order_value, repeat_customer_rate
~~~

### 16.4 Canonicalization

Разрешены только:

- timestamp → UTC ISO-8601 с шестью fractional digits;
- decimal → fixed contract scale;
- boolean → true/false;
- stable sort natural grain;
- deterministic JSON key order.

Запрещены:

- trim/case normalization;
- null/default substitution;
- дополнительное округление;
- исключение mismatch rows;
- checksum-only acceptance.

Strings, dates, integers и Decimal(18,2) сравниваются точно.

Не сравнивать:

- geolocation;
- полную SCD2 history;
- surrogate keys;
- technical validity/snapshot windows;
- Kafka/Iceberg/ClickHouse metadata.

### 16.5 Report

Report содержит:

~~~text
baseline commit
candidate commit
fixture path/SHA-256
component versions
start/end timestamps
relation/grain
row counts
missing/extra keys
column mismatch counts
до 100 deterministic mismatch samples
overall PASS/FAIL
~~~

Успех: exit code 0 и отсутствие row/column mismatches.

Если parity выявил ошибку, исправить candidate и повторить final gate. Не
добавлять промежуточный shadow или stage-by-stage parity.

---

## 17. Отдельный GCP plan и portability

Создать deferred:

~~~text
docs/plans/gcp-spark-iceberg-bigquery-migration.md
~~~

Текущий план не содержит Terraform phases или GCP Definition of Done.

Future plan обязан:

- выбрать Spark-writable Iceberg REST catalog;
- использовать GCS вместо MinIO;
- создать отдельный dbt-bigquery;
- провести отдельный local-versus-GCP parity;
- не позволять Spark писать в BigQuery-managed Iceberg tables.

References:

- https://docs.cloud.google.com/lakehouse/docs/use-lakehouse-metastore-iceberg-rest-catalog
- https://docs.cloud.google.com/bigquery/docs/biglake-iceberg-tables-in-bigquery

---

## 18. Definition of Done

Миграция завершена только если:

- вся итоговая реализация находится в feature/mysql-spark-iceberg;
- MySQL является единственным business OLTP;
- PostgreSQL обслуживает только Airflow/Polaris/control plane;
- существующие Docker volume не нужны;
- clean reset → bootstrap воспроизводит stack;
- ровно восемь business tables захватываются Debezium;
- geolocation исключена из CDC и загружена как reference;
- Avro + Apicurio schema contract и schema archive работают;
- Bronze сохраняет raw bytes, tombstones и external operational records;
- Silver changes/current типизированы и idempotent;
- older event не может заменить newer state;
- transaction-complete serving boundary определён;
- Iceberg является canonical Bronze/Silver/history storage;
- continuous Spark не управляется Airflow;
- ClickHouse восстанавливается только из Iceberg;
- MergeTree и ReplacingMergeTree покрыты correctness tests;
- dbt Gold физически хранится в ClickHouse;
- dbt/olist_clickhouse не содержит cloud adapter branches;
- NiFi, manifest loader, PostgreSQL OLTP и legacy CDC runtime удалены;
- Iceberg maintenance не касается checkpoints;
- candidate E2E проходит после clean reset;
- final legacy-versus-candidate parity report имеет PASS;
- документация описывает только работающий target;
- GCP/Terraform остаётся отдельной deferred программой.
