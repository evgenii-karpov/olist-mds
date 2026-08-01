# Olist MDS: прямая миграция на MySQL, Spark Structured Streaming и Apache Iceberg

## 0. Управление документом

| Поле | Значение |
| --- | --- |
| Статус | Wave 1 и J1 завершены; Wave 2 и J2 готовы к реализации |
| Последнее обновление | 2026-08-01 |
| Базовый commit текущей архитектуры | 1400d08345ad81a0121f0ee85ee9ae81cd575a73e |
| Ветка реализации | feature/mysql-spark-iceberg |
| Evidence J1 | docs/reports/mysql-spark-iceberg-wave1-j1-validation.md |
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
| Spark runtime | 4.1.3, Scala 2.13.17, Java 17.0.19 |
| Spark application language | Scala 2.13.17 для всего нового Wave 2 data plane |
| Spark build | sbt 1.12.11, Scalafmt 3.11.5, sbt-scalafmt 2.6.2 |
| Spark tests | ScalaTest 3.2.19 |
| Python | 3.12, только существующий control plane и J1 Iceberg migration |
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

## 3. Git и организация работы агентов

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

### 3.4 Join J1 — выполнен

J1 завершён и повторно проверен на disposable stack. Авторитетный отчёт:
`docs/reports/mysql-spark-iceberg-wave1-j1-validation.md`. Реализация находится
в commits `6088ebe3dcaee0345bedfb0524caa4aa96842e50` и
`b1cd1ab1b6f59166aa6dfad60bc02419bd0bfcf8`. Состояние J1 не пересобирать в
Wave 2 без обнаруженного дефекта: 26 Iceberg tables, Spark/Polaris/MinIO seam,
v2 entity contracts, captured writer schemas и dbt-clickhouse project уже
прошли validation.

Integration agent после завершения A-D:

1. Проверяет, что ownership не нарушен.
2. Добавляет dependencies в pyproject.toml и один раз обновляет uv.lock.
3. Интегрирует services в compose.yaml.
4. Добавляет CLI bootstrap/status contract.
5. Запускает static/unit/Compose checks.
6. Исправляет только integration seams; component logic возвращает владельцу
   соответствующего потока.
7. Создаёт один или несколько тематических commits в основной ветке.

### 3.5 Wave 2 — Scala data plane и Join J2

Wave 2 реализует отсутствующий MySQL-to-Iceberg data plane. Новые Spark jobs,
общий normalization runtime, entity modules, replay и geolocation loader должны
быть написаны на Scala. PySpark разрешён только для уже проверенной J1 migration
`streaming/spark/platform/migrate.py`; переносить её на Scala в Wave 2 не нужно.
Python остаётся control plane для `scripts/cdc/local_lab.py`, генерации Spark
properties и bounded lifecycle/status orchestration. Scala runtime не импортирует
Python modules и не запускает Python subprocesses.

Единственный новый build root:

~~~text
streaming/spark/scala/
  build.sbt
  project/build.properties
  project/plugins.sbt
  .scalafmt.conf
  .gitignore
  src/main/scala/com/olist/mds/spark/
  src/main/resources/contracts/
  src/main/resources/topics.json
  src/test/scala/com/olist/mds/spark/
  src/test/resources/golden/
~~~

Он выпускает один thin JAR `olist-spark-jobs_2.13-0.1.0.jar`, который Docker
build копирует в runtime image как `/opt/olist/jars/olist-spark-jobs.jar`.
В JAR находятся пять entrypoints:

~~~text
com.olist.mds.spark.app.BronzeMain
com.olist.mds.spark.app.SilverMain
com.olist.mds.spark.app.ReplayMain
com.olist.mds.spark.app.GeolocationMain
com.olist.mds.spark.app.LakehouseStatusMain
~~~

Порядок реализации задаёт раздел 13, а алгоритмы и интерфейсы — раздел 8.
Разделение работы между агентами допустимо только после появления компилируемого
common Scala API и golden tests. Независимо от числа агентов итог должен иметь
один `EntityRegistry`, один decoder, один set writers и один error taxonomy;
копии shared logic внутри entity packages запрещены.

Работу D1-D3 не выполнять. J1 уже содержит законченный `dbt/olist_clickhouse`
graph: dimensions/SCD2, fact/payment allocation, marts и tests прошли реальный
`dbt build` с `PASS=78`. В J2 dbt только повторно проверяет потребительский
Silver interface; изменение business SQL выходит за scope Wave 2.

После успешного J2 начинаются serial end-to-end stages E, L, V и F. J2 не
реализует serving publication, Airflow maintenance, legacy deletion или полный
legacy-versus-candidate parity.

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
  Connect, MinIO, Polaris, Spark master/worker и one-shot geolocation loader;
- streaming: Bronze/Silver Spark drivers и one-shot replay/status ops;
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
spark-geolocation
spark-ops
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
  platform, создаёт catalog/tables, seed'ит MySQL, загружает geolocation и
  регистрирует connector; continuous Spark запускается только отдельной
  `start-streaming`, serving — только командами стадии E;
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
python scripts/cdc/local_lab.py start-streaming
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
APICURIO_CCOMPAT_URL
ICEBERG_CATALOG_URI
ICEBERG_CATALOG_NAME
ICEBERG_WAREHOUSE
OBJECT_STORE_ENDPOINT
OBJECT_STORE_REGION
OBJECT_STORE_PATH_STYLE
OBJECT_STORE_CREDENTIAL_PROVIDER
SPARK_CHECKPOINT_ROOT
SPARK_CONTRACT_VERSION
SPARK_STATUS_DIR
SPARK_RUNTIME_MODE
MYSQL_REFERENCE_READER_USERNAME
MYSQL_REFERENCE_READER_PASSWORD_FILE
CLICKHOUSE_HOST
CLICKHOUSE_PORT
DBT_PROJECT_DIR
DBT_TARGET
~~~

Secrets внутри containers передаются через переменные с суффиксом _FILE.
Plaintext passwords/tokens в Compose environment, logs, exceptions и reports
запрещены.

Base Compose фиксирует `SPARK_RUNTIME_MODE=local`. Значение `integration-test`
допустимо только в committed test override из J2; любое другое значение или
test hook в `local` mode завершает Scala application до Spark query start.

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
- olist_spark_reference_reader: только Spark JDBC read geolocation;
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

Минимальный grant для one-shot reference loader:

~~~sql
GRANT SELECT ON olist_oltp.geolocation
    TO 'olist_spark_reference_reader'@'%';
~~~

Этот user не получает SELECT на остальные business tables, global grants,
LOCK TABLES или DML. Пароль поступает только через
`MYSQL_REFERENCE_READER_PASSWORD_FILE`.

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

Changes — логически immutable event ledger. Обычный streaming path использует
insert-only `MERGE ON event_id`: новый `event_id` вставляется, точный retry
является no-op. Единственное разрешённое изменение существующей строки —
защищённая finite-replay коррекция `apply_status: rejected → applied` при полном
совпадении immutable transport/source metadata. Уже applied row никогда не
переписывается; `rejected → rejected`, `applied → rejected` и изменение metadata
считаются fatal ledger corruption. Точные guards перечислены в разделе 8.

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

Permanent malformed/business-invalid non-tombstone event:

- остаётся в Bronze;
- получает idempotent changes row с apply_status=rejected и audit row;
- не обновляет current;
- позволяет query продвинуть checkpoint.

Tombstone никогда не создаёт changes row; invalid/missing tombstone key создаёт
только idempotent normalization error и progress, как определено в разделе 8.

Transaction с rejected event получает status=REJECTED в
audit.mysql_transactions. Serving sync не публикует эту transaction и не
переходит её boundary; report выводит точные entity/event_id/error_code. После
исправления contract/code finite replay может заменить только rejected outcome
на applied по guards раздела 8; transport/source metadata остаются неизменными.
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

## 8. Spark Structured Streaming — обязательная реализация Wave 2

Этот раздел является implementation contract, а не набором вариантов. Если
описание расходится с прежним Python `normalization_api.py`, для нового Wave 2
runtime авторитетен этот раздел и Scala API. Python API сохраняется как J1
interface evidence и источник cross-language golden invariants; удалять или
превращать его в runtime dependency нельзя.

### 8.1 Scala project, build и runtime artifact

Создать `streaming/spark/scala` как один sbt project со следующими фиксированными
значениями:

~~~text
organization := "com.olist.mds"
name := "olist-spark-jobs"
version := "0.1.0"
scalaVersion := "2.13.17"
sbt.version=1.12.11
scalafmt.version=3.11.5
sbt-scalafmt.version=2.6.2
scalatest.version=3.2.19
~~~

Spark SQL, Structured Streaming, Kafka source, Spark Avro и Iceberg compile
dependencies объявить в `provided` scope с версиями раздела 2. ScalaTest и
Spark local-test classpath объявить только в `Test`. Не добавлять Akka, cats,
http4s, circe, shaded Spark/Iceberg или второй logging implementation. Для HTTP
использовать Java 17 `java.net.http.HttpClient`, для JSON — Jackson из Spark
classpath, для Avro pre-validation — Avro classes из Spark runtime.

Обязательные sbt commands из корня Scala project:

~~~text
sbt scalafmtCheckAll scalafmtSbtCheck
sbt Test/compile
sbt test
sbt package
~~~

`build.sbt` должен включить `Test / fork := true`, `Test / parallelExecution :=
false`, `spark.master=local[2]` и UTC для test JVM. Тесты не должны зависеть от
порядка, локального timezone или уже запущенного Compose project.

Compile options фиксированы:
`-deprecation -feature -unchecked -Werror -Wunused:imports`; dynamic versions
(`+`, `latest.*`, snapshots) и additional resolvers кроме Maven Central
запрещены. Test JVM получает `-Duser.timezone=UTC`.

Dockerfile получает отдельный Scala builder stage. Он запускает pinned sbt
launcher, выполняет `scalafmtCheckAll scalafmtSbtCheck Test/compile test package`
и копирует только thin application JAR в runtime stage. Sbt launcher скачивается
отдельным `docker/spark/download-sbt-launch.sh` по manifest
`docker/spark/sbt-launch.sha256`, разрешающему ровно Maven Central URL и один
SHA-256-checked file; launcher не попадает в runtime. Sbt dependencies имеют
только exact coordinates из `build.sbt`; вычисление digest опубликованного
launcher является механическим действием, выбор другой version — нет. Runtime
image остаётся
`olist-spark:4.1.3-iceberg1.11.0` на базе
`apache/spark:4.1.3-scala2.13-java17-python3-ubuntu`.

Все Spark/Iceberg/Kafka/Avro/MySQL jars скачиваются только на build stage,
проверяются SHA-256 и находятся в image. `spark-submit --packages`, Ivy cache,
Coursier resolution и любой network download при старте container запрещены.
`docker/spark/verify-runtime.sh` дополнительно проверяет:

- полную Scala version `2.13.17`, а не только binary version `2.13`;
- наличие ровно одного `/opt/olist/jars/olist-spark-jobs.jar`;
- отсутствие Spark/Iceberg/Kafka/Avro classes внутри application JAR;
- наличие всех runtime jars из раздела 2 и совпадение Hadoop `3.4.2` для S3A.

Runtime stage заранее создаёт `/var/run/olist-spark/{bronze,silver,failpoints}`
с owner Spark `185:185` и mode `0750`, чтобы first-use named status volume был
writable без root entrypoint. Status/failpoint files создаются mode `0640`.

Spark properties остаются сгенерированным mode `0600` файлом:

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

Ни principal credential, ни временные S3 credentials не передаются как CLI
arguments и не печатаются в Spark event logs. Main-классы получают секреты
только через уже существующий properties renderer и `_FILE` variables.

### 8.2 Package layout и общий Scala API

Создать пакеты, не меняя названия:

~~~text
com.olist.mds.spark.app          main classes и argument parsing
com.olist.mds.spark.config       immutable runtime config и SparkSession factory
com.olist.mds.spark.contract     resource loader и EntityContract
com.olist.mds.spark.avro         framing, registry client, reference resolver
com.olist.mds.spark.bronze       Bronze projection и append writer
com.olist.mds.spark.normalize    общий decoder и EntityBatchProcessor
com.olist.mds.spark.entity       восемь entity modules и EntityRegistry
com.olist.mds.spark.iceberg      changes/current/audit writers и commit coordinator
com.olist.mds.spark.supervisor   query lifecycle, failure classification, status
com.olist.mds.spark.ops          replay, geolocation и finite status logic
~~~

Data-plane code использует Spark `DataFrame`/`Column` expressions. Row-by-row
business UDF, `collect()` business rows на driver, RDD API и Dataset encoders для
payload data запрещены. Единственное разрешённое payload UDF — bounded Avro
pre-validator из пункта 8.7; он возвращает только valid/error marker и никогда
не возвращает/логирует raw payload.

Common API должен содержать эти типы и одну реализацию каждого writer:

~~~scala
sealed trait BatchMode
case object StreamingBatch extends BatchMode
case object FiniteReplay extends BatchMode

final case class BatchContext(
  queryName: String,
  entity: String,
  contractVersion: Int,
  sparkQueryId: String,
  sparkBatchId: Long,
  mode: BatchMode
)

final case class BusinessColumn(
  name: String,
  sparkType: DataType,
  nullable: Boolean,
  primaryKeyOrdinal: Option[Int]
)

final case class EntityContract(
  entity: String,
  topic: String,
  topicPartitions: Int,
  primaryKey: Vector[String],
  businessColumns: Vector[BusinessColumn],
  keyReaderSchema: String,
  valueReaderSchema: String,
  allowedKeyFingerprints: Set[String],
  allowedValueFingerprints: Set[String]
)

final case class ResolvedSchema(
  schemaId: Int,
  subject: String,
  registryVersion: Int,
  fingerprintSha256: String,
  schemaJson: String,
  referencesJson: String,
  selfContainedSchemaJson: String
)

final case class ValidationRule(
  ordinal: Int,
  code: String,
  redactedMessage: String,
  invalidWhen: Column
)

trait EntityModule {
  def contract: EntityContract
  def validationRules(row: Column): Vector[ValidationRule]
}

final case class NormalizationResult(
  changes: DataFrame,
  currentCandidates: DataFrame,
  errors: DataFrame,
  partitionProgress: DataFrame
)

final case class TableCommit(snapshotId: Long, changed: Boolean)

trait SchemaResolver {
  def resolve(schemaId: Int, expectedSubject: String): ResolvedSchema
}

trait ChangesWriter {
  def commit(rows: DataFrame, context: BatchContext): TableCommit
}

trait CurrentWriter {
  def commit(rows: DataFrame, context: BatchContext): Option[TableCommit]
}

trait AuditWriter {
  def commitErrors(rows: DataFrame, context: BatchContext): Option[TableCommit]
  def commitProgress(
    rows: DataFrame,
    changes: TableCommit,
    current: Option[TableCommit],
    context: BatchContext
  ): TableCommit
}

trait TransactionWriter {
  def commit(rows: DataFrame, context: BatchContext): TableCommit
}
~~~

`EntityBatchProcessor.process(bronzeBatch, module, context)` является
единственной общей точкой decode/validate/hash/apply. Она возвращает named
DataFrames `changes`, `currentCandidates`, `errors` и `partitionProgress` и
затем вызывает writers в порядке пункта 8.9. `ReplayMain` вызывает тот же
processor с `FiniteReplay`; отдельные replay projections, validation rules или
MERGE SQL запрещены.

`EntityRegistry.all` содержит ровно восемь modules в фиксированном порядке:

~~~text
customers
orders
order_items
order_payments
order_reviews
products
sellers
product_category_translation
~~~

При старте `SilverMain` registry проверяет уникальность entity/topic,
соответствие query names из J1 `topology.py` и полный набор восьми entities.
Missing/extra/duplicate module является fatal `contract_resource_mismatch` до
запуска любой query.

`LakehouseSchemaContract` является единственным Scala описанием common
Bronze/Silver/audit columns и строит entity table schemas из `EntityContract`.
Entity modules не объявляют `StructType`. Golden test сериализует Scala surface
и сравнивает её с canonical JSON, полученным read-only вызовом J1
`table_specs.py`; checksum обязан оставаться
`d3bf55d90fbfe953cfbc74eef83e6d83f91ce1986cfb85c849da2c3e788b3d8d`.

### 8.3 Contract resources и startup validation

Sbt `resourceGenerators` копирует в JAR, без ручного дублирования:

- `streaming/schemas/contracts/manifest.json`;
- только восемь referenced `v2.json`, но не v1 runtime contracts;
- `streaming/kafka/topics.json`.

Ресурсы располагаются как `contracts/manifest.json`,
`contracts/<entity>/v2.json` и `topics.json`. Build завершается ошибкой, если
source resource отсутствует. CI распаковывает JAR и сравнивает bytes каждого
resource с repository source.

Manifest сохраняет historical `versions[]` entries на v1, но runtime loader не
пытается открыть их paths: он читает только top-level active `path` с
`contract_version=2`. Historical v1 остаётся repository validation input, не
Wave 2 runtime resource.

`ContractLoader` при каждом application start выполняет fail-closed checks:

1. `manifest_version=1`, `entity_count=8`, у всех entries
   `contract_version=2`.
2. SHA-256 bytes каждого v2 file равен `contract_sha256` из manifest.
3. Entity name, topic, topic partition count, primary key, business column
   order/type/nullability и Iceberg table names совпадают между contract,
   topic manifest и J1 table surface.
4. `wire_format=confluent`, magic byte `0`, prefix `5`, fingerprint algorithm
   `sha256-canonical-json-v1`, `from_avro_mode=FAILFAST`.
5. Allowed key/value fingerprint sets непустые и состоят из lowercase SHA-256.
6. Contract evolution запрещает key/PK change, rename, drop и narrowing.
7. Runtime `CONTRACT_VERSION` равен `2`; другое значение нельзя silently
   подставить через environment.

После создания SparkSession, но до streaming start,
`LakehouseContractValidator` требует migration 1 с указанным checksum и
сравнивает фактические 26 Iceberg table names, ordered fields/types/nullability,
partition transforms и mandatory properties с `LakehouseSchemaContract`.
Отсутствие/drift — fatal `contract_resource_mismatch`; application не выполняет
DDL/ALTER самостоятельно.

Scala type mapping фиксирован: business MySQL `DATETIME(6)`/contract
`timestamp` проецируется в Spark `TimestampNTZType` и Iceberg `timestamp` без
timezone shift; operational Kafka/source/audit instants используют Spark
`TimestampType` и Iceberg `timestamptz` при session timezone UTC. Money — только
`DecimalType(18,2)`, coordinates — `DecimalType(18,14)`. Generic cast в string,
double или JVM local time запрещён.

Canonical schema JSON строится так же, как J1 Python helper: UTF-8 JSON, object
keys lexicographically sorted, no insignificant whitespace, Unicode не
ASCII-escaped, NaN/Infinity запрещены. SHA-256 берётся от этих bytes. Scala и
Python implementations проверяются одними golden files. Любое расхождение до
начала streaming — fatal `contract_resource_mismatch`.

### 8.4 Applications, query names и checkpoints

`BronzeMain` запускает ровно одну query:

~~~text
kafka_to_bronze
s3a://olist-checkpoints/kafka_to_bronze/contract-v2/
~~~

`SilverMain` в одном JVM запускает ровно десять independently supervised
queries:

~~~text
capture_avro_schemas
normalize_mysql_transactions
normalize_customers
normalize_orders
normalize_order_items
normalize_order_payments
normalize_order_reviews
normalize_products
normalize_sellers
normalize_product_category_translation
~~~

Checkpoint каждой Silver query:

~~~text
s3a://olist-checkpoints/<query-name>/contract-v2/
~~~

Query name и checkpoint path не конфигурируются независимо. Общая функция
принимает только known query name и contract version, нормализует
`SPARK_CHECKPOINT_ROOT`, требует точное `s3a://olist-checkpoints` и строит path.
Переиспользование checkpoint между queries или contract versions запрещено.

Внутри каждого `foreachBatch` helper `ActiveQueryIdentity.require(queryName)`
ищет ровно одну active query по name в `spark.streams.active` и берёт её stable
`id`; zero/multiple matches — fatal. Не захватывать ещё не присвоенную
`StreamingQuery` variable в closure и не использовать per-run `runId`.

Все Silver queries читают только append-only
`lakehouse.bronze.mysql_cdc_records` через Iceberg `readStream`, начиная с
исторических snapshots (`stream-from-timestamp=0`). Каждая query сразу фильтрует
собственные `record_kind`/topic rows. Bronze никогда не создаёт overwrite/delete
snapshot: это обязательное условие работоспособности этих reads.

Для Bronze и Silver использовать `Trigger.ProcessingTime("60 seconds")`.
`availableNow`, continuous-processing mode и manual Kafka commits не применять.
Finite jobs не создают streaming checkpoint.

### 8.5 Kafka-to-Bronze: точный алгоритм

Kafka source читает explicit comma-separated `subscribe` из `topics.json`:
восемь `business_cdc` topics, `olist_cdc.transaction`, `olist_cdc.heartbeat` и
schema-change topic `olist_cdc`. `olist_cdc.schema_history`, три Connect internal
topics и broker-managed topics исключаются. Options фиксированы:

~~~text
kafka.bootstrap.servers=${KAFKA_BOOTSTRAP_SERVERS}
startingOffsets=earliest
failOnDataLoss=true
includeHeaders=true
~~~

Не задавать `kafka.group.id`, не вызывать consumer commit API и не включать
`maxOffsetsPerTrigger` для local contract. Structured Streaming checkpoint —
единственный source progress mechanism.

Bronze projection сохраняет Kafka `key` и `value` как binary bytes без decode,
re-encode или UTF-8 conversion. Поля вычисляются следующим образом:

- `event_id = concat(topic, ':', partition, ':', offset)`;
- `record_kind=data` для non-null value business topic;
- `record_kind=tombstone` для null value business topic;
- `record_kind=transaction|heartbeat|schema_change` по purpose topic manifest;
- `is_tombstone=true` только для business topic с null value;
- `headers` сохраняет исходный порядок и nullable binary values;
- `key_sha256`/`value_sha256` — lowercase SHA-256 raw bytes, NULL для absent side;
- `ingest_batch_id` — `foreachBatch` batch ID;
- `spark_query_id` — stable StreamingQuery ID из active query, не run ID;
- `ingested_at` — один UTC instant, вычисленный один раз на micro-batch;
- Kafka timestamp и timestamp type переносятся без бизнес-интерпретации.

Framing inspector допускает только magic byte `0`, 4-byte big-endian schema ID
и payload. Bytes сначала читаются unsigned, затем ID обязан находиться в
`1..2147483647`, потому что J1 Iceberg columns имеют Spark `INT`; `0` и high-bit
values получают `invalid_schema_id`. Absent side считается framing-valid со
schema ID NULL; это необходимо для tombstone value и допустимого null
operational key.
Malformed bytes не отбрасываются. `framing_error` содержит первый код в порядке
key before value:

~~~text
key_frame_too_short
key_invalid_magic_byte
key_invalid_schema_id
value_frame_too_short
value_invalid_magic_byte
value_invalid_schema_id
~~~

Текст с фактическим byte, length, schema ID или payload в Bronze не сохранять;
`framing_error` — только code. `key_framing_valid` и `value_framing_valid`
обязательны, а schema ID выставляется только для valid present frame.

Bronze sink реализовать через `foreachBatch`, потому что retry после Iceberg
commit предшествует checkpoint commit. Для каждого batch:

1. Проверить uniqueness `event_id` внутри batch. Exact duplicate с одинаковыми
   topic/partition/offset, raw hashes и Kafka metadata схлопнуть; любое отличие
   для одного ID завершает query fatal `event_identity_collision`.
2. Прочитать из target только ID в затронутых topic/partition offset ranges и
   сравнить их immutable metadata/hashes с incoming.
3. Existing exact rows считать retry no-op. Existing row с тем же ID и другим
   metadata/hash завершает query `event_identity_collision`.
4. Выполнить left-anti join по `event_id` и обычный Iceberg append только новых
   rows. Пустой anti-join не создаёт искусственный snapshot.
5. После append прочитать latest Bronze snapshot ID и максимальный committed
   offset по каждой затронутой partition для status JSON.

Для collision equality сравниваются все Bronze columns, кроме attempt-local
`ingest_batch_id`, `spark_query_id`, `ingested_at`; existing values этих трёх
полей всегда сохраняются. В частности сравнение включает headers, Kafka
timestamp/type, both raw hashes, schema IDs, framing flags/error, record kind и
tombstone flag.

Для Bronze запрещены `MERGE`, `UPDATE`, `DELETE`, overwrite и compaction во
время Wave 2. Crash после append безопасен: повтор того же Spark batch увидит
existing IDs, ничего не добавит, после чего checkpoint сможет продвинуться.

### 8.6 Schema capture и Apicurio resolver

`capture_avro_schemas` читает distinct non-null valid key/value schema IDs из
Bronze для всех 11 external topics. Для каждого ID resolver использует
`APICURIO_CCOMPAT_URL`, фиксированный внутри Compose как
`http://apicurio-registry:8080/apis/ccompat/v7`, с connect/read timeout 15
seconds и не более четырёх concurrent requests.

Для root schema выполнить:

1. `GET /schemas/ids/{id}`.
2. `GET /schemas/ids/{id}/subjects` и потребовать expected
   `<topic>-key`/`<topic>-value` subject для соответствующей side.
3. `GET /schemas/ids/{id}/versions`, выбрать greatest numeric version именно
   expected subject и получить его через
   `/subjects/{url-encoded-subject}/versions/{version}`.
4. Убедиться, что canonical fingerprint root schema из ID и subject/version
   одинаков.
5. Рекурсивно загрузить references `(name, subject, version)`, обнаруживать
   cycles и alias conflicts, затем один раз inline каждое named definition.

Поведение reference fallback портировать без расширения из
`streaming/schemas/registry.py`: если CCompat subject/version reference вернул
404, заменить suffix `.Key → -key` или `.Value → -value` и прочитать exact
artifact/version из native endpoint
`/apis/registry/v2/groups/olist_cdc/artifacts/<artifact>/versions/<version>`.
На другие HTTP 4xx fallback не применять.

Resolved row MERGE'ится в `bronze.avro_schemas` по `schema_id`:

- not matched — insert schema, references, self-contained schema, provenance и
  обе timestamps;
- matched с тем же fingerprint — не менять schema/provenance, обновить только
  `last_verified_at`;
- matched с другим fingerprint — fatal `schema_id_fingerprint_conflict`.

Schema JSON и references хранятся canonical/minified; secrets и response
headers не архивируются. Missing ID/subject, HTTP 408/425/429/5xx, timeout и
connection error считаются transient: resolver повторяет до 120 seconds, затем
micro-batch завершается transient error без checkpoint advance. Invalid JSON,
reference cycle/alias conflict, root/subject mismatch и остальные HTTP 4xx
являются fatal contract errors. HTTP response body в exception/log не включать.

Entity query не обращается к registry напрямую. Она ждёт required schema IDs в
`bronze.avro_schemas` максимум 120 seconds с polling 2 seconds. После появления
проверяет key/value fingerprints по allowed lists entity v2 contract. Unknown
writer fingerprint записывает idempotent `audit.schema_violations` с code
`unknown_writer_fingerprint` и останавливает только affected entity query.

`violation_id=sha256(entity + '|' + event_id + '|' + schema_kind + '|' +
schema_id + '|' + fingerprint + '|' + contract_version + '|' +
violation_code)`. Row содержит fingerprint/IDs и fixed redacted message, но
`details_json=NULL`. Если audit commit transient-fails, query retry'ит и не
переходит в FATAL до успешной записи violation; exact retry row — no-op.

Maximum distinct `(key_schema_id, value_schema_id)` pairs одного entity
micro-batch равен 32. Проверка происходит до driver `collect` schema metadata;
реализация выполняет `distinct.limit(33).collect()`, и result size 33 означает
fatal `schema_storm` affected query. Raw business rows на driver не collect'ятся.

`capture_avro_schemas` пишет `audit.silver_progress` после schema archive commit
для каждой processed topic/partition. Для этой query `entity='__schemas__'`,
`changes_snapshot_id` означает latest `bronze.avro_schemas` snapshot,
`current_snapshot_id=NULL`.

### 8.7 Общий decode и normalization pipeline

Каждая entity query получает только свой business topic. Один micro-batch
обрабатывается строго в следующем порядке; перестановка commit-affecting шагов
запрещена:

1. Проверить/deduplicate `event_id` и применить collision guard из Bronze.
2. Отделить tombstones. Tombstone не создаёт Silver changes/current row, но его
   offset обязан попасть в progress. Malformed/null key tombstone создаёт
   idempotent `normalization_errors` с `primary_key_null`, не останавливает
   query и всё равно продвигает progress.
3. Для non-tombstone rows получить distinct schema pairs, дождаться archive и
   проверить allowed fingerprints.
4. Удалить ровно первые пять framing bytes в отдельных binary payload columns.
5. До `from_avro` прогнать каждый payload через bounded Avro pre-validator:
   `GenericDatumReader` с actual self-contained writer schema должен полностью
   прочитать payload без trailing bytes. UDF возвращает только boolean и fixed
   `avro_payload_invalid`; exception/payload не попадают в log.
6. Отделить invalid payload rows как permanent rejected. Только validated
   subset декодировать `from_avro(payload, actualWriterSchema, options)` с
   `mode=FAILFAST` и contract reader schema в option `avroSchema`.
7. Декодировать key и value отдельно, затем объединить schema-pair groups через
   `unionByName(allowMissingColumns=true)` в contract column order.
8. Проверить envelope shape, `op`, topic/entity, PK, exact types/nullability и
   entity rules.
9. Построить deterministic metadata/hashes и разделить applied/rejected.
10. Передать результат общему commit protocol из пункта 8.9.

Envelope rules:

- допустимы только `op=c|r|u|d`;
- `c` и `r` требуют non-null `after`; `u` требует non-null `before` и `after`;
  `d` требует non-null `before` и null `after`;
- business row равен `after` для `c/r/u` и `before` для `d`;
- decoded key должен содержать каждый PK и совпасть с business row, включая
  composite key order;
- silent cast string↔numeric, truncation decimal/timestamp и timezone conversion
  запрещены;
- `is_deleted=true` только для `d`; current soft delete сохраняет business
  columns из `before` и ставит `deleted_at=source_ts`;
- `is_snapshot=true`, если `op=r` или `source.snapshot` равно `true`, `last` либо
  `incremental`;
- rejected non-tombstone всегда имеет NULL во всех projected business columns и
  `row_hash=NULL`; если envelope decoded, сохранить valid `op`, derived
  `is_snapshot`/`is_deleted`, source/transaction metadata и available
  before/after hashes; если decode невозможен, использовать `op='unknown'`,
  `is_snapshot=false`, `is_deleted=false`, NULL source/transaction/hash fields и
  `source_ts=kafka_timestamp`.

Source timestamp выбирается: `source.ts_us`, затем `source.ts_ns` с truncation
до microseconds, затем `source.ts_ms`; Kafka timestamp используется только для
undecodable rejected row. `source_binlog_file_index` — integer suffix после
последней точки в `source.file`, иначе NULL. Остальные source/transaction fields
переносятся без переименования semantics. `schema_fingerprint` в changes равен
value writer fingerprint; key provenance восстанавливается по `key_schema_id`
из archive.

Hash canonicalization общая для всех entities. `before_row_hash` и
`after_row_hash` считаются от соответствующей decoded business row; absent row
даёт NULL. Canonical payload — UTF-8 JSON object с keys строго в порядке
`iceberg_projection.business_columns`, с сохранёнными NULL. Strings JSON-escaped,
integers — base-10 JSON numbers, decimals — quoted fixed-scale strings,
timestamps — quoted UTC `yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'`. NaN, Infinity,
scientific decimal notation и local timezone запрещены. `row_hash` равен after
hash для `c/r/u`, before hash для `d`, NULL для rejected. Использовать SHA-256
lowercase hex.

`normalized_at` — один UTC instant текущей processing attempt. Он не является
event identity: при exact streaming retry existing value сохраняется и incoming
attempt timestamp игнорируется; только разрешённая replay correction заменяет
его временем correction. Все provenance/order/hash fields остаются строго
сравниваемыми.

Permanent row validation выбирает один `error_code` по первому нарушению в
этом fixed order:

~~~text
key_frame_too_short
key_invalid_magic_byte
key_invalid_schema_id
value_frame_too_short
value_invalid_magic_byte
value_invalid_schema_id
avro_payload_invalid
invalid_envelope
invalid_op
topic_entity_mismatch
primary_key_null
primary_key_mismatch
required_field_null
type_contract_violation
<entity rule by ordinal>
~~~

`error_message` для любого permanent code строится только общей функцией и
дословно равен `Normalization rejected event: <error_code>.`. Entity modules не
пишут собственный текст. Для `audit.schema_violations` использовать
`Schema contract violation: <violation_code>.`. Эти strings не содержат raw
value, byte length, schema JSON, registry response, SQL fragment или credential.
Все permanent codes создают `apply_status=rejected`, не обновляют current и
позволяют checkpoint advance.

### 8.8 Восемь entity modules

Business column order/type/nullability всегда берётся из v2 resource; modules
не дублируют schema JSON. Они добавляют только следующие rules/codes в указанном
порядке:

| Entity | Primary key | Дополнительные ordered validation rules |
| --- | --- | --- |
| customers | `customer_id` | `customers_state_invalid`: `customer_state` не соответствует `^[A-Z]{2}$` |
| sellers | `seller_id` | `sellers_state_invalid`: `seller_state` не соответствует `^[A-Z]{2}$` |
| orders | `order_id` | `orders_status_invalid`; `orders_approval_before_purchase`; `orders_delivery_before_purchase` для customer delivery timestamp |
| order_items | `order_id, order_item_id` | `order_item_id_non_positive`; `order_item_price_negative`; `order_item_freight_value_negative` |
| order_payments | `order_id, payment_sequential` | `payment_sequential_non_positive`; `payment_type_invalid`; `payment_installments_negative`; `payment_value_negative` |
| order_reviews | `review_id, order_id` | `review_score_out_of_range`; `review_answer_before_creation` |
| products | `product_id` | `product_name_lenght_negative`; `product_description_lenght_negative`; `product_photos_qty_negative`; `product_weight_g_negative`; `product_length_cm_negative`; `product_height_cm_negative`; `product_width_cm_negative` |
| product_category_translation | `product_category_name` | Нет rules сверх common required/type/PK checks |

Allowed order statuses и payment types брать как exact constants из v2 checks:

~~~text
orders: created, approved, invoiced, processing, shipped, delivered, unavailable, canceled
payments: credit_card, boleto, voucher, debit_card, not_defined
~~~

Nullable temporal/measurement fields проходят rule, когда NULL. Не добавлять
foreign-key lookups в Silver: source MySQL уже обеспечивает referential
constraints, а lookup сделал бы entity query зависимой от Silver current.

Для каждого module создать tests из всех captured key/value writer schemas,
snapshot `r`, `c`, `u`, `d`, tombstone, nullable fields, каждое rule boundary и
composite-key mismatch. Общий registry test обязан вызвать все восемь modules на
одинаковом framework; восемь copy-paste test harnesses запрещены.

### 8.9 Changes/current/audit commit protocol

Один `EntityBatchProcessor` выполняет commits последовательно:

~~~text
changes → normalization_errors/schema audit → current → silver_progress
~~~

`silver_progress` всегда последний. Между этими commits не существует общей
Iceberg transaction, поэтому каждый writer обязан быть idempotent при повторе
всего batch.

Changes MERGE key — только `event_id`. Перед MERGE incoming содержит максимум
одну строку на ID. Поведение matched rows:

1. Все columns, кроме attempt-local `normalized_at`, byte/logically equal —
   retry no-op; existing `normalized_at` не обновляется.
2. Existing `rejected`, incoming `applied`, `BatchMode=FiniteReplay` и все
   immutable columns equal — обновить только mutable correction columns.
3. Existing `applied` при любом неравенстве — fatal `applied_event_rewrite`.
4. Existing `rejected`, incoming `rejected` с любым неравенством — fatal
   `rejected_event_reclassification`.
5. Любое immutable mismatch — fatal `ledger_transport_mismatch`.

Immutable columns:

~~~text
event_id
source_ts, source_server_id, source_gtid, source_binlog_file,
source_binlog_file_index, source_binlog_pos, source_row
transaction_id, transaction_total_order, transaction_data_collection_order
kafka_topic, kafka_partition, kafka_offset, kafka_timestamp
key_schema_id, value_schema_id, schema_fingerprint
contract_version, bronze_ingested_at
~~~

Mutable только для разрешённой correction:

~~~text
op, is_snapshot, is_deleted, apply_status
error_code, error_message
all business columns
before_row_hash, after_row_hash, row_hash
normalized_at
~~~

Если исправленный decoder впервые получил source metadata, которая была NULL в
rejected row, guard не пропускает correction: это metadata mismatch и требует
полного disposable reset. Replay предназначен для исправления validation или
contract interpretation при уже зафиксированной provenance, а не для
переписывания происхождения события.

`audit.normalization_errors` MERGE key:
`error_id=sha256(event_id + '|' + contract_version + '|' + error_code)`.
Not matched вставляет occurrence count `1`; exact retry ничего не обновляет и не
увеличивает count. Успешная replay correction ставит `resolved_at` всем
unresolved errors этого event/contract; повтор correction — no-op. Raw key/value
и business values в audit не писать.

Для current сначала оставить только applied rows. По business key выбрать
greatest Kafka offset внутри batch; tie одного offset с разным event ID fatal.
Все events одного key внутри batch обязаны иметь один Kafka partition. Incoming
partition должен совпадать с existing `last_kafka_partition`; иначе fatal
`key_partition_changed`. Current MERGE обновляет/вставляет только если incoming
offset строго больше `last_kafka_offset`. Equal offset с exact same
`last_event_id` — retry no-op; equal offset с другим ID — fatal. Rejected row и
tombstone current не меняют.

После changes/current commits writers читают фактические latest Iceberg snapshot
IDs. `audit.silver_progress` содержит одну row на затронутую
query/entity/topic/partition/batch и MERGE'ится по:

~~~text
query_name, entity, contract_version, source_topic,
kafka_partition, spark_batch_id
~~~

Для partition записываются maximum processed offset/event ID, source timestamp,
stable Spark query ID, batch ID и snapshot IDs. Status равен `COMMITTED`, если
rejections не было, иначе `COMMITTED_WITH_REJECTIONS`. `changes_snapshot_id` —
latest changes snapshot после batch; `current_snapshot_id` — snapshot созданного
current commit или NULL, если current не менялся. Tombstone offset включается.
Если changes table ещё не имеет snapshot для orphan initial tombstone, query
останавливается fatal `orphan_tombstone`; нормальный Debezium delete envelope
всегда предшествует tombstone в той же partition.

Десять Silver queries пишут общие audit tables из одного JVM. Реализовать
driver-local `IcebergCommitCoordinator` с fair lock per fully-qualified audit
table; каждый audit/schema/transaction/progress writer обязан проходить через
него. Lock не держать во время registry I/O или decode. Iceberg commit conflict,
возникший несмотря на lock, классифицировать transient и повторять весь batch.
Одновременно держать только один table lock и освободить его до следующего
writer, чтобы исключить lock-order deadlock. Entity changes/current tables
различны и не требуют global lock.

Crash cases обязаны иметь следующий результат:

- после changes: retry видит exact changes no-op, затем выполняет current и
  progress;
- после errors: retry не дублирует error, затем выполняет current/progress;
- после current: retry не откатывает newer current и затем пишет progress;
- после progress до checkpoint: все четыре stages exact no-op, checkpoint
  продвигается;
- progress никогда не свидетельствует о незавершённом changes/current commit.

### 8.10 Transaction metadata query

`normalize_mysql_transactions` обрабатывает только
`olist_cdc.transaction`, используя тот же schema archive/resolver. Debezium
records `status=BEGIN|END`, `id`, `event_count` и `data_collections` декодируются
из actual writer schema. Не строить transaction boundary по MySQL binlog file,
timestamp или соседству Kafka offsets.

Для operational transaction topic нет entity allowed-fingerprint list.
`TransactionQuery` валидирует structural reader contract до decode: root Avro
record обязан содержать string `status`, string `id`, long/null `event_count`,
array/null `data_collections` из records со string `data_collection` и long
`event_count`, а также nullable timestamp metadata. Допустимы только additive
nullable fields; missing/renamed/narrowed required fields дают fatal
`transaction_schema_incompatible`. После проверки actual self-contained writer
schema используется с минимальным reader schema этих полей и тем же
pre-validator/FAILFAST path, что entity decoder. Fingerprint всё равно
архивируется как provenance.

BEGIN выполняет idempotent MERGE по `transaction_id` и создаёт status `OPEN` с
immutable begin metadata. Exact duplicate — no-op; conflicting begin — fatal
`transaction_metadata_conflict`.

Topic имеет одну partition, но DataFrame row order не считать сохранённым.
Query группирует metadata по transaction ID и Kafka offset: допускается ровно
один logical BEGIN и один logical END, END offset строго больше BEGIN; exact
retry duplicates схлопываются. BEGIN может находиться в previous batch/existing
OPEN row. Проверки/count joins выполняются set-based; decoded business rows на
driver не collect'ятся.

При END query не checkpoint'ит batch, пока не выполнены все условия:

1. END `event_count` равен количеству distinct Silver changes rows данного
   `transaction_id`.
2. Для каждой declared `data_collection` количество changes совпадает, names
   однозначно map'ятся через EntityRegistry, total равен `event_count`.
   Допустимы только exact names `olist_oltp.<mysql_table>` из v2 contracts;
   suffix/fuzzy matching запрещён.
3. `transaction_total_order` образует exact sequence `1..event_count`; внутри
   каждой collection `transaction_data_collection_order` также непрерывна.
4. Latest committed `audit.silver_progress` каждой involved topic/partition
   покрывает maximum Kafka offset соответствующих transaction rows.
5. Все counted rows имеют один effective outcome: row может быть applied или
   rejected, но не отсутствовать и не конфликтовать по event ID.

Недостающие rows/progress означают transient `transaction_not_ready`: backoff и
повтор без checkpoint. Count больше declared, duplicate/gapped order,
неизвестная collection или conflicting END — fatal transaction contract error.

После выполнения условий status становится `COMPLETE`, если все changes applied,
иначе `REJECTED`; `rejected_event_ids` сортируются lexicographically. Transaction
row commit выполняется последним действием transaction batch, после чего его
progress записывается с `entity='__transactions__'`, а
`changes_snapshot_id` означает latest `audit.mysql_transactions` snapshot и
`current_snapshot_id=NULL`. Serving boundary принимает только `COMPLETE`.

Replay, исправивший последний rejected event transaction, повторно проверяет
те же пять условий и допускает только `REJECTED → COMPLETE`. `COMPLETE` никогда
не понижается и не переписывается. Transaction без metadata, включая initial
snapshot events, остаётся с `transaction_id=NULL` и не создаёт synthetic
transaction row.

### 8.11 Failure classes, supervisor и status files

Использовать sealed classes `TransientFailure`, `PermanentRecordFailure` и
`FatalContractFailure`. Unexpected exception не превращать в permanent record:
она получает fatal code `unexpected_runtime_failure`, чтобы не потерять batch.

Transient failures:

- registry timeout/connection/HTTP 408, 425, 429 или 5xx;
- Polaris/MinIO timeout, temporary authorization refresh или network error;
- Iceberg optimistic commit conflict;
- `transaction_not_ready` и schema-not-yet-archived до/после 120-second wait.

Permanent failures — только codes пункта 8.7 и entity rules пункта 8.8. Они
порождают rejected row, но не terminate query.

Fatal codes включают как минимум:

~~~text
contract_resource_mismatch
schema_storm
schema_id_fingerprint_conflict
schema_reference_cycle
schema_reference_alias_conflict
unknown_writer_fingerprint
event_identity_collision
key_partition_changed
ledger_transport_mismatch
applied_event_rewrite
rejected_event_reclassification
orphan_tombstone
transaction_schema_incompatible
transaction_metadata_conflict
transaction_event_count_mismatch
unexpected_runtime_failure
~~~

`SilverMain` supervisor хранит десять query handles отдельно. Transient query
перезапускается с deterministic delays `5, 10, 20, 40, 60, 60, ...` seconds;
counter сбрасывается после первого успешно committed batch. Fatal query остаётся
остановленной, остальные продолжают работать. Process не вызывает global
`spark.streams.awaitAnyTermination()` как exit policy и не завершает JVM из-за
одной entity query. Bronze использует тот же classifier, но имеет одну query и
остаётся process-alive в fatal state для диагностики.

Каждое application атомарно пишет temp+rename JSON:

~~~text
/var/run/olist-spark/bronze/status.json
/var/run/olist-spark/silver/status.json
~~~

Schema: `application`, `contract_version`, `overall_state`, `updated_at_utc` и
sorted `queries[]` с `name`, stable `query_id`, `state`, `last_batch_id`,
`last_progress_at_utc`, `partition_offsets`, `error_class`, `error_code`.
Allowed query states: `STARTING`, `RUNNING`, `RETRYING`, `FATAL`, `STOPPED`;
overall: `STARTING`, `READY`, `DEGRADED`, `UNHEALTHY`, `STOPPED`. Error message,
stack trace, SQL, schema/body и secret values в status JSON запрещены.

Docker health is successful только при `READY`. Silver с одной fatal query имеет
`DEGRADED` и non-zero healthcheck, но container process остаётся запущенным.
Transient retry дольше startup grace даёт `UNHEALTHY`; восстановившийся
application возвращается в `READY` без container recreate.

### 8.12 Finite replay

`ReplayMain` — internal bounded Spark operation с exact interface:

~~~text
--entity <one of eight>
--topic <entity contract topic>
--partition <0..topic_partitions-1>
--from-offset-inclusive <non-negative long>
--to-offset-inclusive <long >= from>
--contract-version 2
~~~

Перед запуском `scripts/cdc/local_lab.py` обязан остановить весь `spark-silver`
container и подтвердить, что его process отсутствует; Bronze может продолжать
append. Это исключает cross-process Iceberg writers, которые JVM-local commit
coordinator не сериализует. Replay читает один fixed Bronze snapshot и только
заданный inclusive range, проверяет отсутствие gaps среди реально выбранных
rows и exact entity topic.

Preflight требует, чтобы у каждого non-tombstone selected event уже была
existing changes row с `apply_status=rejected`; missing row или applied row в
range завершает operation без writes (`replay_source_not_rejected`). Tombstones
разрешены как context, но ничего не меняют. Затем вызывается тот же
`EntityBatchProcessor` и тот же decoder/rules/hashes.

Replay `BatchContext` использует `sparkQueryId=SparkContext.applicationId`,
`sparkBatchId=0` и `FiniteReplay`; один process обрабатывает ровно один range и
не принимает несколько entity/ranges за invocation.

Replay допускает только guards пункта 8.9:

- transport/source/schema metadata должны полностью совпасть;
- rejected result обязан стать applied;
- updates ограничены mutable correction columns;
- current применяет corrected event только если его offset новее stored;
- соответствующие normalization errors получают `resolved_at`;
- affected transactions могут перейти только `REJECTED → COMPLETE`.

Replay не создаёт/изменяет Structured Streaming checkpoint и не понижает
`silver_progress`; streaming query уже обработала эти offsets как rejected.
После success CLI снова запускает `spark-silver`, ждёт `READY` и возвращает JSON
с range, selected/corrected/tombstone counts, affected transaction IDs и before/
after Iceberg snapshot IDs. Raw data в result запрещены. При любой ошибке Silver
остаётся остановленным, а оператор получает явный bounded failure; automatic
restart после неизвестного partial replay запрещён до status verification.

### 8.13 Geolocation reference loader

Добавить MySQL user `olist_spark_reference_reader` с единственным grant
`SELECT ON olist_oltp.geolocation`. Создать `_FILE` secret
`mysql_spark_reference_reader_password`; его mount получает только one-shot
geolocation service, не Bronze/Silver/Replay. Запрещено повторно использовать
`olist_admin`, simulator или Debezium reader.

Compose source variable:
`MYSQL_SPARK_REFERENCE_READER_PASSWORD_SOURCE_FILE` с dev default
`./docker/secrets/dev/mysql_spark_reference_reader_password.txt`; это отдельный
non-committed secret, значение других MySQL users не переиспользовать. Target
`/run/secrets/mysql_spark_reference_reader_password`, application variable
`MYSQL_REFERENCE_READER_PASSWORD_FILE` указывает на этот target. Значение не
копируется в environment.

`GeolocationMain` принимает mandatory
`--source-archive-sha256 <64 lowercase hex>`, читает JDBC table с explicit
column projection и ordered `geolocation_id`, затем пишет
`lakehouse.reference.geolocation`:

- `source_archive_sha256` равен аргументу для каждой row;
- `source_row_number=geolocation_id` в contract v1;
- decimals приводятся ровно к `DECIMAL(18,14)` без rounding;
- `loaded_at` — один UTC instant на job.

Если target пуст, выполнить один append. Если target непуст, сравнить exact
business rows, source hash и row numbers: полное совпадение — no-op, любое
расхождение или partial target — fatal `geolocation_reference_drift`; append/
overwrite существующей reference запрещён. После write повторно прочитать target
и проверить row count, uniqueness `geolocation_id` и canonical row hashes.

`bootstrap --archive` запускает loader после MySQL seed и Iceberg migration, до
`start-streaming`, передавая уже вычисленный SHA-256 archive без секретных CLI
arguments. На small fixture J2 требует ровно 6 rows.

### 8.14 Compose и lifecycle integration

`docker/spark/run-with-platform-config.sh` остаётся единственным Spark wrapper.
Заменить Wave 2 stubs на:

~~~text
spark-bronze:
  run-with-platform-config.sh --master spark://spark-master:7077
  --class com.olist.mds.spark.app.BronzeMain
  /opt/olist/jars/olist-spark-jobs.jar

spark-silver:
  run-with-platform-config.sh --master spark://spark-master:7077
  --class com.olist.mds.spark.app.SilverMain
  /opt/olist/jars/olist-spark-jobs.jar
~~~

Оба services имеют `restart: unless-stopped`, status volume, Spark credential
projection, explicit resources из раздела 4.1 и healthcheck пункта 8.11.
Bronze зависит от completed Iceberg migration/projector, healthy Kafka/topic
bootstrap и Spark master/worker. Silver дополнительно зависит от healthy Bronze
и Apicurio. Не mount'ить repository source поверх application JAR.

Local `spark-submit` resource flags фиксированы: Bronze
`spark.cores.max=1`, `spark.executor.cores=1`, `spark.executor.memory=1g`;
Silver `spark.cores.max=2`, `spark.executor.cores=2`,
`spark.executor.memory=3g`; each one-shot ops/geolocation
`spark.cores.max=1`, `spark.executor.cores=1`, `spark.executor.memory=1g`.
Dynamic allocation выключен. Environment может менять только worker total
resources, но не относительный per-application allocation в J2.

Build stanza остаётся только у `spark-master`; worker, migration, Bronze,
Silver и one-shot services используют тот же exact
`olist-spark:4.1.3-iceberg1.11.0` image. Не создавать несколько расходящихся
Spark images/build contexts.

Добавить one-shot services:

- `spark-geolocation` — только `GeolocationMain`, Spark/Polaris credentials и
  MySQL reference-reader secret;
- `spark-ops` — `ReplayMain` или `LakehouseStatusMain` по CLI override, Spark
  credentials, без MySQL secret.

`start-streaming` в `scripts/cdc/local_lab.py` больше не deferred. Он:

1. Проверяет J1 platform readiness, migration checksum
   `d3bf55d90fbfe953cfbc74eef83e6d83f91ce1986cfb85c849da2c3e788b3d8d` и
   geolocation status.
2. Запускает Bronze, bounded ждёт `READY`.
3. Запускает Silver, bounded ждёт все десять queries `READY`.
4. Возвращает JSON inventory из 11 query names, stable IDs, exact checkpoint
   paths, contract version и application JAR SHA-256.

`wait-caught-up --timeout` также становится реальным. Python control plane один
раз в начале фиксирует Kafka high watermark каждой partition 11 external topics
через `confluent-kafka`; target offset равен `high-1`, для empty partition `-1`.
Targets после этого не двигаются. Polling читает sanitized status files и ждёт:

- Bronze coverage всех targets;
- `__schemas__` progress всех external topic partitions;
- entity progress каждого business topic;
- `__transactions__` progress transaction topic и отсутствие OPEN transaction,
  относящейся к target range.

После coverage CLI один раз запускает `LakehouseStatusMain` с target JSON в
non-secret mounted file. Main finite-read'ит Iceberg и подтверждает offsets,
snapshot IDs, duplicate `event_id=0`, current uniqueness, changes outcome counts,
schema archive и transaction states. Exit codes: `0=READY`,
`2=NOT_CAUGHT_UP`, `3=INVARIANT_VIOLATION`, `1=EXECUTION_ERROR`; stdout всегда
один redacted JSON object. Python преобразует его без потери fields в итог
`ready|blocked|timeout` result.

`READY` требует zero unresolved rejected changes/errors внутри captured target
и zero `REJECTED` transactions; initial snapshot rejection поэтому возвращает
`blocked`, хотя offsets/checkpoints покрыты. JSON перечисляет только
entity/event_id/error_code, не business row.

`status` включает Bronze/Silver overall/query states и last offsets, но не
запускает дорогое full table scan. `validate` вызывает finite status check.
Все команды имеют bounded timeout и не печатают command environment, registry
schema/payload или credentials.

### 8.15 Запрет Silver streaming reads

Не использовать `readStream` для Silver changes/current. Их guarded MERGE
создаёт overwrite/delete snapshots, а Iceberg streaming read поддерживает только
append snapshots:
https://iceberg.apache.org/docs/latest/spark-structured-streaming/

ClickHouse serving, dbt, `LakehouseStatusMain` и будущая maintenance читают
Silver только finite batch. Единственный Iceberg streaming source Wave 2 —
append-only Bronze.

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

Пакеты P0, A, B, C, D и J1 ниже завершены и оставлены как historical scope.
Wave 2 agent проверяет их regressions, но не выполняет заново.

### P0 — последовательная фиксация interfaces — выполнен

1. Создать feature/mysql-spark-iceberg от baseline commit.
2. Добавить этот план.
3. Добавить deferred GCP plan.
4. Зафиксировать ownership и shared-file rule.
5. Не запускать legacy full stack.

После P0 стартуют A-D из Parallel Wave 1.

### A — MySQL source — выполнен

1. Создать MySQL config/init/users.
2. Перенести business DDL.
3. Перенести simulator control schema.
4. Портировать simulator/seeding.
5. Добавить exact type/constraint/fixture tests.
6. Вернуть dependency/shared-config handoff.

### B — CDC contracts — выполнен

1. Создать topic script.
2. Создать MySQL connector config.
3. Зафиксировать Apicurio settings.
4. Создать eight entity contracts.
5. Адаптировать Avro compatibility checks.
6. Добавить connector/topic/schema tests.

### C — Lakehouse platform — выполнен

1. Создать Spark image.
2. Добавить Polaris JDBC/bootstrap resources.
3. Добавить MinIO bucket/policy resources.
4. Создать Iceberg migration definitions.
5. Добавить Spark/Polaris/table contract tests.
6. Не реализовывать entity business transforms.

### D — Analytics skeleton — выполнен

1. Создать ClickHouse DataLakeCatalog/native DDL.
2. Создать dbt/olist_clickhouse project.
3. Зафиксировать source interfaces.
4. Портировать adapter-independent business SQL в ClickHouse-only form.
5. Добавить dbt parse/unit/DDL tests.
6. Не реализовывать Airflow publication.

### J1 — integration join — выполнен

1. Объединить dependencies и обновить uv.lock один раз.
2. Интегрировать Compose services.
3. Реализовать local_lab platform/bootstrap/status.
4. Выполнить static, unit, Compose и component smoke tests.
5. Зафиксировать common Spark normalization API.

### S — Wave 2 Scala data plane

Работу выполнять в порядке S0-S8. Следующий шаг начинается только после tests
предыдущего; это dependency order, а не требование назначить отдельного агента.

#### S0 — зафиксировать baseline и не переделывать J1

1. Проверить branch `feature/mysql-spark-iceberg` и отсутствие чужих изменений
   в owned files.
2. Прочитать J1 report и зафиксировать как precondition: 26 tables, migration
   checksum, contract v2, 16 captured business schemas и `dbt build PASS=78`.
3. Запустить существующие `tests/lakehouse_platform`, `tests/cdc_contracts` и
   `tests/dbt_clickhouse`; failures сначала классифицировать как baseline либо
   regression.
4. Не менять business/Iceberg schemas из `table_specs.py` в Wave 2. Если runtime
   обнаружил невозможность использовать существующую schema, остановить работу
   и оформить отдельную migration вместо silent ALTER.
5. Не переносить PySpark migration/config renderer на Scala и не начинать D1-D3.

#### S1 — создать компилируемый Scala foundation

Создать минимум эти files:

~~~text
streaming/spark/scala/build.sbt
streaming/spark/scala/project/build.properties
streaming/spark/scala/project/plugins.sbt
streaming/spark/scala/.scalafmt.conf
streaming/spark/scala/.gitignore
streaming/spark/scala/src/main/scala/com/olist/mds/spark/config/RuntimeConfig.scala
streaming/spark/scala/src/main/scala/com/olist/mds/spark/config/SparkSessionFactory.scala
streaming/spark/scala/src/main/scala/com/olist/mds/spark/contract/ContractLoader.scala
streaming/spark/scala/src/main/scala/com/olist/mds/spark/contract/EntityContract.scala
streaming/spark/scala/src/main/scala/com/olist/mds/spark/contract/LakehouseSchemaContract.scala
streaming/spark/scala/src/main/scala/com/olist/mds/spark/contract/LakehouseContractValidator.scala
streaming/spark/scala/src/main/scala/com/olist/mds/spark/entity/EntityModule.scala
streaming/spark/scala/src/main/scala/com/olist/mds/spark/entity/EntityRegistry.scala
streaming/spark/scala/src/main/scala/com/olist/mds/spark/normalize/BatchContext.scala
streaming/spark/scala/src/main/scala/com/olist/mds/spark/normalize/Failure.scala
~~~

Project `.gitignore` содержит только sbt/IDE outputs: `target/`,
`project/target/`, `project/project/`, `.bsp/`, `.metals/` и `.idea/`. Dependency
caches и compiled JAR не коммитить.

1. Реализовать exact versions/build scopes и resource generation пункта 8.1.
2. Реализовать strict env/file configuration: required value missing, unknown
   contract version, unsafe URL/path или direct secret value дают startup error
   без echo value.
3. Реализовать contract/topic loading и all startup validations пункта 8.3.
4. Создать пустые five main classes, которые parse'ят только documented args,
   строят SparkSession и завершаются structured error до появления runtime.
5. Добавить golden tests для J1 event ID/checkpoint/order constants, canonical
   schema fingerprint и resource SHA. Python и Scala результаты должны
   совпадать byte-for-byte.
6. Gate: format, compile, unit tests и package проходят; JAR содержит resources
   и не содержит provided dependencies.

#### S2 — реализовать Bronze

Создать:

~~~text
.../avro/ConfluentFrame.scala
.../bronze/BronzeProjection.scala
.../bronze/BronzeBatchWriter.scala
.../app/BronzeMain.scala
.../supervisor/StatusPublisher.scala
~~~

1. Реализовать exact topic selection/options, framing projection и record-kind
   mapping пункта 8.5 только Spark expressions.
2. Реализовать collision check, target-range lookup, left-anti append и retry
   semantics. Никогда не применять MERGE к Bronze.
3. Реализовать atomic status JSON и single-query supervision.
4. Unit tests: null sides, all six framing codes, big-endian ID boundaries
   `0/1/2147483647/2147483648`,
   raw hash, headers, record-kind mapping, exact duplicate и collision.
5. Local Spark/Iceberg component test: один batch append, повтор того же batch,
   новый offset; rows должны быть `N`, `N`, `N+1`, все snapshots append-only.
6. Gate: Kafka fixture доходит до Bronze с byte-for-byte key/value equality и
   restart не создаёт duplicate event IDs.

#### S3 — реализовать schema archive

Создать:

~~~text
.../avro/ApicurioCCompatClient.scala
.../avro/RecursiveSchemaResolver.scala
.../avro/SchemaFingerprint.scala
.../iceberg/SchemaArchiveWriter.scala
.../normalize/SchemaCaptureQuery.scala
~~~

1. Портировать exact J1 Python canonicalization/reference fallback, не вызывая
   Python.
2. Реализовать ID subject/version provenance, recursive inline, cycle/alias
   detection и bounded retry пункта 8.6.
3. Реализовать guarded archive MERGE и `__schemas__` progress-last.
4. Tests используют in-process fake HTTP server для success, recursive refs,
   duplicate refs, cycle, alias conflict, 404 native fallback, 429/5xx retry,
   invalid JSON и same-ID/different-fingerprint.
5. Golden test разрешает все 16 captured business schemas и получает exact
   fingerprints из J1 report/contracts.
6. Gate: live Registry IDs архивируются; повтор capture меняет только
   `last_verified_at`, row count не растёт.

#### S4 — реализовать common normalization engine

Создать:

~~~text
.../avro/AvroPayloadValidator.scala
.../normalize/DebeziumDecoder.scala
.../normalize/EntityBatchProcessor.scala
.../normalize/ErrorCodes.scala
.../normalize/RowCanonicalizer.scala
.../normalize/NormalizationResult.scala
~~~

1. Реализовать exact 11-step pipeline пункта 8.7.
2. Avro UDF использовать только как pre-validator; actual decode выполнять
   Spark `from_avro` в FAILFAST с writer+reader schemas.
3. Реализовать envelope/source/op/PK/type/null validation и fixed precedence.
4. Реализовать canonical row hashes с UTC microseconds/fixed decimal scale.
5. Добавить fail-closed integration-test hook forced rejection из J2.5; вне
   двух explicit test guard variables он недоступен.
6. Tests покрывают c/r/u/d, tombstone, undecodable fallback, duplicate event,
   composite PK, source timestamp precedence и одинаковые hashes при разном JVM
   timezone.
7. Gate: common processor принимает synthetic module и выдаёт four output
   DataFrames с exact J1 Iceberg schemas.

#### S5 — реализовать восемь entity modules

Создать по одному file, не создавая отдельные decoders/writers:

~~~text
.../entity/CustomersModule.scala
.../entity/OrdersModule.scala
.../entity/OrderItemsModule.scala
.../entity/OrderPaymentsModule.scala
.../entity/OrderReviewsModule.scala
.../entity/ProductsModule.scala
.../entity/SellersModule.scala
.../entity/ProductCategoryTranslationModule.scala
~~~

1. Каждый module загружает свой `EntityContract` из registry и объявляет только
   ordered validation rules пункта 8.8.
2. Business columns проектируются общим contract-driven helper; ручной schema
   literal в module запрещён.
3. Создать table-driven ScalaTest suite, использующий captured writers и
   contract reader. Для каждого rule проверить valid boundary, invalid boundary,
   code/precedence и отсутствие raw value в message.
4. Выполнить initial-snapshot golden normalization всех 79 fixture business
   rows: counts `8/12/16/14/12/8/4/5`, rejected `0`.
5. Gate: `EntityRegistry` содержит exact ordered set, все tables/PK/topics/types
   совпадают с J1 migration и v2 manifest.

#### S6 — реализовать idempotent writers и transactions

Создать:

~~~text
.../iceberg/IcebergCommitCoordinator.scala
.../iceberg/ChangesWriter.scala
.../iceberg/CurrentWriter.scala
.../iceberg/AuditWriter.scala
.../iceberg/ProgressWriter.scala
.../iceberg/TransactionWriter.scala
.../normalize/TransactionQuery.scala
~~~

1. Реализовать exact guards/commit order пункта 8.9 через generated, quoted
   Iceberg MERGE SQL; entity/table identifiers могут происходить только из
   validated registry, не из raw CLI.
2. Реализовать per-audit-table locks и transient commit retry.
3. Реализовать transaction BEGIN/END readiness и progress coverage пункта 8.10.
4. Создать writer fakes/fail-once hook для tests после changes и после current;
   повтор одного batch должен давать same ledger/current/progress.
5. Component tests проверяют rejected → applied replay guard, запрет applied
   rewrite, transport mismatch, stale offset, partition change, exact error
   resolution и REJECTED → COMPLETE transaction.
6. Gate: crash после каждого commit boundary не оставляет duplicate event ID,
   stale current или premature progress/COMPLETE transaction.

#### S7 — собрать Silver supervisor и operational jobs

Создать:

~~~text
.../supervisor/FailureClassifier.scala
.../supervisor/QuerySupervisor.scala
.../app/SilverMain.scala
.../app/ReplayMain.scala
.../app/GeolocationMain.scala
.../app/LakehouseStatusMain.scala
~~~

1. Запустить ten fixed query factories, independent backoff/state и atomic
   status пункта 8.11.
2. Реализовать ReplayMain guards и stopped-Silver precondition пункта 8.12.
3. Реализовать least-privilege geolocation load/drift checks пункта 8.13.
4. Реализовать finite status checks/exit codes пункта 8.14.
5. Unit tests используют fake query handles/clock: delays exact
   `5,10,20,40,60`, success reset, fatal isolation, atomic status and redaction.
6. Gate: fatal one entity leaves nine other queries running и status
   `DEGRADED`; transient recovery возвращает `READY`.

#### S8 — image, Compose, CLI и документация

Shared integration edits ограничены этим списком:

~~~text
docker/spark/Dockerfile
docker/spark/download-sbt-launch.sh
docker/spark/sbt-launch.sha256
docker/spark/verify-runtime.sh
docker/spark/run-with-platform-config.sh
compose.yaml
infra/mysql/initdb/040_create_users.sh
infra/mysql/README.md
scripts/cdc/local_lab.py
tests/lakehouse_platform/
tests/mysql/
tests/spark_integration/
README.md
docs/architecture.md
~~~

1. Интегрировать builder/JAR verification в `docker/spark/Dockerfile`; не менять
   J1 Python migration entrypoint.
2. Заменить `streaming_not_available` у Bronze/Silver, добавить health/status
   volume, dependencies, resources, `spark-geolocation` и `spark-ops`.
3. Добавить MySQL reference-reader user/grant/secret и targeted security tests.
4. Реализовать `start-streaming` и `wait-caught-up`; другие deferred commands
   остаются `not_available_until=E`.
5. Обновить README/architecture только фактическими commands/status schemas;
   не объявлять serving или migration полностью завершённой.
6. Gate: Compose config, secret scan, Docker build без runtime downloads,
   CLI JSON contract и existing Python tests проходят.

### J2 — Wave 2 integration join и acceptance

J2 объединяет только завершённые S0-S8 и создаёт
`docs/reports/mysql-spark-iceberg-wave2-j2-validation.md`. Исправления во время
join допускаются в integration seams; обнаруженный defect common/entity logic
исправляется в соответствующем Scala package вместе с targeted regression test.

#### J2.1 Static/build gate

В clean checkout выполнить и записать exit/results:

~~~text
cd streaming/spark/scala
sbt scalafmtCheckAll scalafmtSbtCheck Test/compile test package
cd ../../..
uv lock --check
uv run ruff check streaming/spark scripts/cdc tests
uv run ruff format --check streaming/spark scripts/cdc tests
uv run pyright
uv run python -m unittest discover -s tests/cdc_contracts -v
uv run python -m pytest -p no:cacheprovider tests/lakehouse_platform -q
uv run python -m unittest discover -s tests/dbt_clickhouse -v
docker compose --profile platform --profile streaming config --quiet
docker compose build spark-master
~~~

Если repository CI использует более узкие ruff paths, сохранить существующий
canonical invocation и отдельно проверить новые Python seams. Нельзя
"исправлять" pre-existing unrelated lint массовым reformat.

Проверить application JAR: SHA-256 записан, five main classes и contract
resources присутствуют, provided runtime classes отсутствуют. Docker runtime
запускается с network disabled после image build и не пытается скачать jars.

#### J2.2 Clean bootstrap и initial snapshot

Использовать отдельный Compose project name `olist_wave2_j2` и disposable
volumes:

~~~powershell
$env:COMPOSE_PROJECT_NAME = 'olist_wave2_j2'
python scripts/cdc/local_lab.py doctor
python scripts/cdc/local_lab.py reset --yes
python scripts/cdc/local_lab.py bootstrap --archive tests/fixtures/olist_small/olist_small.zip
python scripts/cdc/local_lab.py start-streaming
python scripts/cdc/local_lab.py wait-caught-up --timeout 1200
python scripts/cdc/local_lab.py validate
~~~

Acceptance после captured initial targets:

| Entity | applied changes | current rows | rejected |
| --- | ---: | ---: | ---: |
| customers | 8 | 8 | 0 |
| orders | 12 | 12 | 0 |
| order_items | 16 | 16 | 0 |
| order_payments | 14 | 14 | 0 |
| order_reviews | 12 | 12 | 0 |
| products | 8 | 8 | 0 |
| sellers | 4 | 4 | 0 |
| product_category_translation | 5 | 5 | 0 |

Итого: `79` applied changes, `79` current, `0` rejected,
`audit.normalization_errors=0`, `reference.geolocation=6`. Все initial business
rows имеют snapshot semantics, correct contract version/hashes и unique event
ID/PK. Archive содержит как минимум exact 16 key/value fingerprints из J1
report; operational schemas архивируются, если наблюдались до captured target.
Не фиксировать exact total Bronze/schema count, зависящий от heartbeat timing.

#### J2.3 Deterministic CRUD/transaction scenario

Добавить `tests/spark_integration/fixtures/wave2_crud.sql`, выполняемый MySQL
admin test harness, с exact identifiers:

~~~text
customer: wave2_customer_001 / wave2_unique_001
order: wave2_order_001
items: (wave2_order_001, 1), (wave2_order_001, 2)
payments: (wave2_order_001, 1), (wave2_order_001, 2)
review: (wave2_review_001, wave2_order_001)
referenced existing products: product_001, product_002
referenced existing sellers: seller_001, seller_002
~~~

SQL fixture фиксирован; агент не генерирует другие business values:

~~~sql
SET time_zone = '+00:00';

START TRANSACTION;
INSERT INTO olist_oltp.customers VALUES
  ('wave2_customer_001', 'wave2_unique_001', '09999', 'sao paulo', 'SP');
INSERT INTO olist_oltp.orders VALUES
  ('wave2_order_001', 'wave2_customer_001', 'created',
   '2018-09-01 10:00:00.123456', NULL, NULL, NULL,
   '2018-09-10 00:00:00.000000');
INSERT INTO olist_oltp.order_items VALUES
  ('wave2_order_001', 1, 'product_001', 'seller_001',
   '2018-09-03 12:00:00.000001', 10.00, 2.50),
  ('wave2_order_001', 2, 'product_002', 'seller_002',
   '2018-09-03 12:00:00.000002', 20.00, 3.50);
INSERT INTO olist_oltp.order_payments VALUES
  ('wave2_order_001', 1, 'credit_card', 1, 12.50),
  ('wave2_order_001', 2, 'voucher', 1, 23.50);
INSERT INTO olist_oltp.order_reviews VALUES
  ('wave2_review_001', 'wave2_order_001', 5, 'wave2', 'wave2 review',
   '2018-09-02 08:00:00.000001', '2018-09-02 09:00:00.000001');
COMMIT;

START TRANSACTION;
UPDATE olist_oltp.orders
SET order_status = 'approved',
    order_approved_at = '2018-09-01 10:05:00.123456'
WHERE order_id = 'wave2_order_001';
UPDATE olist_oltp.order_items
SET price = 19.99
WHERE order_id = 'wave2_order_001' AND order_item_id = 2;
COMMIT;

START TRANSACTION;
DELETE FROM olist_oltp.order_reviews
WHERE review_id = 'wave2_review_001'
  AND order_id = 'wave2_order_001';
COMMIT;
~~~

Первая explicit transaction даёт ровно 7 CDC business events в нескольких
collections. После catch-up transaction имеет `event_count=7`, continuous
total/data-collection order, status `COMPLETE`; seven changes applied и все
current rows присутствуют.

Вторая transaction даёт ровно 2 events и обновляет order `created → approved`
и price второго item; оба current rows получают newer offsets, первая item row
не меняется. Третья transaction даёт один delete event и удаляет review.
Проверить applied delete row,
soft-deleted current с сохранёнными before business columns, следующий Kafka
tombstone в Bronze, отсутствие отдельной tombstone changes row и progress offset,
покрывающий tombstone.

После сценария выполнить `wait-caught-up` с новыми once-captured targets и
проверить, что composite keys не схлопнулись, transaction rows не стали COMPLETE
раньше entity progress и rejected/errors остались zero.

#### J2.4 Retry, restart и isolation drills

В отдельном disposable consistency domain выполнить bounded drills, не полный
chaos matrix:

Сначала выполнить `down` для `olist_wave2_j2` с сохранением его volumes, затем
установить `COMPOSE_PROJECT_NAME=olist_wave2_j2_faults`, сделать clean
reset/bootstrap/start-streaming. Все fault/replay drills J2.4-J2.5 выполняются
последовательно только в этом project; parallel projects с одинаковыми host
ports запрещены.

1. Test-only fail-once после changes commit одного known event; retry обязан
   закончить current/progress без duplicate changes.
2. Test-only fail-once после current commit другого event; retry обязан оставить
   ровно один changes row, newer current и один progress key.
3. Перезапустить Bronze и Silver containers с сохранёнными volumes/checkpoints,
   добавить ещё один valid update и доказать catch-up/no duplicates/no stale
   overwrite.
4. Зарегистрировать/произвести один syntactically valid, но отсутствующий в v2
   allowed fingerprints writer для customers. `normalize_customers` должен стать
   `FATAL`, `audit.schema_violations` получить redacted row, остальные девять
   Silver queries продолжить; overall state `DEGRADED`.

Fail-once hook разрешён только test Compose override, с target event ID и atomic
fired marker в status volume. Production/default Compose не содержит failpoint
environment. После isolation drill consistency domain сбрасывается; неизвестный
fingerprint не переносится в основной J2 run.

Все integration hooks требуют одновременно
`SPARK_RUNTIME_MODE=integration-test` и
`SPARK_TEST_HOOKS_ENABLED=true`; при любом другом mode наличие hook variable —
startup fatal. Кроме two commit failpoints разрешён один
`SPARK_TEST_FORCE_REJECT_EVENT_ID`: после полного successful decode/provenance
он выдаёт fixed `forced_test_rejection`, не меняя metadata. Base Compose и
production status никогда не устанавливают эти variables.

#### J2.5 Replay proof

После J2.4 выполнить `reset --yes` fault project и новый clean bootstrap, чтобы
unknown writer schema/checkpoints не попали в replay proof. Запустить только
Bronze, оставить Silver остановленным, выполнить следующую valid transaction,
дождаться Bronze и получить её exact event ID. Затем запустить Silver через test
override с `SPARK_TEST_FORCE_REJECT_EVENT_ID=<полученный ID>`. Дождаться changes
`forced_test_rejection` с полностью декодированной provenance и checkpoint
advance. После этого снова остановить `spark-silver`, убрать test hook и
запустить production `ReplayMain` на exact entity/topic/partition/range.
Проверить:

~~~sql
START TRANSACTION;
INSERT INTO olist_oltp.customers VALUES
  ('wave2_replay_customer_001', 'wave2_replay_unique_001',
   '08888', 'recife', 'PE');
COMMIT;
~~~

- одна existing row перешла `rejected → applied`;
- immutable columns до/после byte/logically equal;
- error получил `resolved_at`, current обновился по offset;
- affected transaction перешла `REJECTED → COMPLETE`;
- повтор replay завершается `replay_source_not_rejected` без writes;
- попытка replay applied row или metadata mismatch не меняет таблицы.

После verification удалить test override environment/marker, пересоздать
`spark-silver` в normal mode и доказать `READY`. Production contract/code при
этом не изменяются. Затем полностью удалить fault project, вернуть
`COMPOSE_PROJECT_NAME=olist_wave2_j2`, выполнить `up`, `start-streaming`,
`wait-caught-up` по новым targets и оставить основной project в final `READY`.

#### J2.6 dbt regression boundary

Не реализовывать D1-D3 и не запускать production serving sync. Повторить
`dbt parse` и real adapter `dbt build` против пустого native fixture с
unpublished `sync_run_seq=9002`, `sync_run_id='j2-wave2-regression'`.
Ожидать `PASS=78 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=78`, отсутствие publication
и прежние Silver source names/types. Любое изменение model graph/business SQL
требует отдельного объяснённого defect fix, а не расширения Wave 2.

Для этого gate отдельно поднять только `clickhouse`/`clickhouse-init`, применить
existing native DDL, оставить восемь serving event/current tables пустыми и
запустить `bin/run-dbt.sh` с указанными vars. Не копировать Silver rows и не
создавать serving run. После build проверить candidate partition `9002`, что
public views её не показывают без `PUBLISHED`, затем удалить disposable Gold
candidate перед final J2 status.

#### J2.7 Report и exit criteria

J2 report должен содержать только sanitized evidence:

- Git commit(s), UTC timestamps, exact commands/exit codes;
- sbt/Scala/Spark/Java versions, application JAR SHA-256, Docker image ID;
- 11 query names/IDs/checkpoints и final states;
- captured Kafka targets и Bronze/Silver progress без payload;
- per-entity changes/current/rejected counts, duplicate checks, snapshot IDs;
- schema IDs/fingerprints/provenance без schema bodies;
- transaction/restart/failpoint/replay outcomes;
- geolocation count/source archive SHA;
- dbt regression result;
- secret scan scope/result;
- explicit deferred scope E/L/V/F.

J2 PASS только если все J2.1-J2.6 gates прошли в текущем implementation commit,
final `local_lab status`/`validate` возвращают ready, `git diff --check` проходит,
а report не содержит credential, raw Kafka bytes, decoded business payload или
schema JSON. При failed gate report имеет status FAIL/BLOCKED; нельзя объявлять
Wave 2 завершённой по unit tests без clean component run.

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

PR CI не запускает full parity, full candidate E2E или unbounded Compose stack.
Он обязан запускать следующие независимые jobs.

### 14.1 Scala fast job

Рабочая директория `streaming/spark/scala`, dependency cache key включает
`build.sbt`, `project/build.properties`, `project/plugins.sbt` и
`.scalafmt.conf`. Команды:

~~~text
sbt scalafmtCheckAll scalafmtSbtCheck
sbt Test/compile
sbt test
sbt package
~~~

После package CI:

1. Проверяет единственность application JAR и stable artifact name.
2. Распаковывает JAR и проверяет five main classes, manifest/topics/v2 resources.
3. Byte-сравнивает packaged resources с repository originals и их SHA-256.
4. Завершает job ошибкой при bundled `org/apache/spark`,
   `org/apache/iceberg`, `org/apache/kafka` или `org/apache/avro` classes.
5. Публикует только JAR SHA-256/test reports, не JAR с contract data как public
   release artifact.

ScalaTest suite обязательно покрывает:

- all Confluent framing branches и unsigned schema ID;
- canonical schema fingerprint parity с Python golden;
- CCompat subject/version provenance, recursive references, fallback и cycles;
- contract manifest/resources/query/checkpoint inventory;
- all eight captured key/value schemas;
- Debezium c/r/u/d/tombstone и invalid envelope;
- fixed error precedence и redacted messages;
- all entity rules/boundaries;
- deterministic business hashes, decimals, UTC microseconds и NULL;
- event ID dedupe versus collision;
- same key/multiple events/composite keys;
- stale/equal/newer current ordering и partition invariant;
- exact duplicate MERGE, rejected correction guards и applied rewrite refusal;
- retry после each partial commit boundary;
- error resolution и transaction COMPLETE/REJECTED transitions;
- transient/fatal classification, backoff reset и one-query isolation;
- atomic/redacted status output;
- geolocation empty/idempotent/drift behavior;
- replay argument/preflight/range behavior.

Spark tests работают `local[2]` с temporary warehouse/checkpoint directories и
не требуют Docker/network. Golden files хранят IDs/hashes/expected rows, но не
credentials или production payload dumps.

### 14.2 Existing Python/contracts regression job

Сохранить canonical repository lint/type/test invocations. Минимальный Wave 2
набор:

- MySQL DDL/users/grants, seed order, constraints и fixture counts;
- exact eight-table capture, topics/partitions и connector properties;
- BACKWARD_TRANSITIVE compatibility и evolution policy;
- J1 table schemas/partition/properties/migration checksum;
- Python normalization API/event ID/checkpoint golden parity со Scala;
- `local_lab` bounded JSON, deferred E commands и secret redaction;
- dbt parse, graph, unit/data contract и ClickHouse DDL regressions;
- Compose config, healthchecks и отсутствие fixed `container_name`;
- Airflow import tests для неизменённой части проекта;
- comparator sensitivity.

Wave 2 agents не удаляют Python tests только потому, что data plane стал Scala.
Python control-plane regression обязателен.

### 14.3 Image contract job

Собрать `olist-spark:4.1.3-iceberg1.11.0`, выполнить runtime verifier и затем
запустить five main classes с `--help`/invalid config при disabled network.
Проверить, что:

- image build выполнил Scala tests и скопировал exact thin JAR;
- runtime versions равны разделу 2;
- ни один main не пытается resolve package/download artifact;
- properties/credential files имеют требуемые permissions;
- logs и image metadata не содержат secret values;
- invalid config завершается fixed code/message без echo входного value.

### 14.4 Bounded component job

Docker component job можно не запускать на каждом documentation-only PR, но он
обязателен для изменений Scala runtime, contracts, Spark image, Compose или
`local_lab.py` и всегда обязателен в J2. Он использует small fixture и bounded
timeouts, но не ClickHouse serving/final parity.

Проверки:

- real Kafka → Bronze raw byte equality и append-only snapshot history;
- real Apicurio → schema archive с 16 known business fingerprints;
- Bronze → eight Silver changes/current exact 79/79/0 counts;
- geolocation exact 6/idempotent;
- transaction completeness и progress-last;
- one Bronze/Silver restart с persistent checkpoints;
- fail-once after changes/current;
- one fatal fingerprint isolation scenario;
- finite replay one-way correction;
- `LakehouseStatusMain` ready/not-caught-up/invariant exit codes.

Component artifacts — sanitized JSON/counts/snapshot IDs only. Kafka bytes,
decoded business rows, schema JSON, Docker inspect и secret-bearing environment
не сохранять.

### 14.5 Scope guard

Ни checksum, aggregate count или successful checkpoint не заменяет row-level
equality там, где J2 требует exact fixture rows. Одновременно fast/J2 checks не
должны преждевременно выполнять serving publication, legacy deletion,
comprehensive candidate E2E или final legacy parity.

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
- все новые Wave 2 Spark data-plane jobs собраны из Scala 2.13.17 одним pinned
  sbt project; Python используется только в оговорённом control plane/J1 path;
- J2 validation report имеет PASS и содержит доказательства build, initial
  snapshot, CRUD/transactions, retry/restart/isolation и guarded replay;
- ровно восемь business tables захватываются Debezium;
- geolocation исключена из CDC и загружена как reference;
- Avro + Apicurio schema contract и schema archive работают;
- Bronze сохраняет raw bytes, tombstones и external operational records;
- Silver changes/current типизированы и idempotent;
- changes ledger запрещает applied rewrite и допускает только guarded
  `rejected → applied` finite correction без изменения provenance;
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
