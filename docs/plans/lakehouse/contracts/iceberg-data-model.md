# Технический контракт: Модель данных Iceberg, Polaris и MinIO

- **Статус**: Действующий нормативный контракт (Active normative contract)
- **Назначение**: Фиксация структуры каталога Iceberg, бакетов MinIO, пространств имен (namespaces), схем таблиц Bronze/Silver/Audit/Reference и свойств таблиц.
- **Порядок авторитетности**: Определяет действующие нормативные требования к структуре и схемам данных на уровне Lakehouse.

---

## 1. Контур каталога Polaris и бакетов MinIO

### 1.1 Параметры Polaris Catalog

- Каталог / параметр REST warehouse: `olist_lakehouse`
- Базовый путь (default-base-location): `s3://olist-lakehouse/warehouse`
- REST URI: `http://polaris:8181/api/catalog`
- S3 endpoint: `http://minio:9000`
- S3 region: `us-east-1`

### 1.2 Бакеты MinIO

1. `olist-lakehouse`: Хранение данных таблиц Iceberg (warehouse).
2. `olist-checkpoints`: Хранение чекпоинтов Spark Structured Streaming.

Чекпоинты физически изолированы от warehouse. Инструменты обслуживания Iceberg (maintenance) не имеют доступа к бакету чекпоинтов.

### 1.3 Пространства имен (Namespaces) и свойства таблиц

В каталоге создаются 4 пространства имен:
- `bronze`
- `silver`
- `reference`
- `audit`

Общие свойства таблиц Iceberg:

```text
format-version=2
write.format.default=parquet
write.parquet.compression-codec=zstd
write.target-file-size-bytes=134217728
write.metadata.delete-after-commit.enabled=true
write.metadata.previous-versions-max=20
```

Партиционирование:
- `bronze.mysql_cdc_records`: `days(ingested_at)`;
- `bronze.avro_schemas`: без партиционирования;
- `silver.<entity>_changes`: `days(source_ts)`;
- `silver.<entity>_current`: без партиционирования;
- `reference.geolocation`: без партиционирования;
- Растущие таблицы `audit`: `days(recorded_at)`.

---

## 2. Схемы сырого слоя Bronze

### 2.1 Таблица `bronze.mysql_cdc_records`

Хранит внешние CDC-топики Kafka в исходном бинарном виде (без декодирования payload).

| Колонка | Тип | Назначение |
| --- | --- | --- |
| `event_id` | `string` | Составной ID (`topic:partition:offset`) |
| `record_kind` | `string` | `data`, `tombstone`, `transaction`, `heartbeat`, `schema_change` |
| `topic` | `string` | Имя топика Kafka |
| `partition` | `int` | Номер партиции Kafka |
| `offset` | `long` | Смещение в партиции Kafka |
| `kafka_timestamp` | `timestamptz` | Метка времени из Kafka |
| `kafka_timestamp_type` | `string` | Тип метки времени Kafka |
| `headers` | `map<string, binary>` | Заголовки сообщения Kafka |
| `key_bytes` | `binary` | Сырые байты ключа |
| `value_bytes` | `binary` | Сырые байты значения |
| `is_tombstone` | `boolean` | `true` при null value для бизнес-топика |
| `key_schema_id` | `int` | Извлеченный 4-байтовый ID схемы ключа |
| `value_schema_id` | `int` | Извлеченный 4-байтовый ID схемы значения |
| `key_sha256` | `string` | SHA-256 хэш ключа |
| `value_sha256` | `string` | SHA-256 хэш значения |
| `key_framing_valid` | `boolean` | Валидность обрамления Confluent Avro ключа |
| `value_framing_valid` | `boolean` | Валидность обрамления Confluent Avro значения |
| `framing_error` | `string` | Код ошибки фрейминга (если есть) |
| `ingest_batch_id` | `long` | ID микробатча Spark |
| `spark_query_id` | `string` | Устойчивый ID стриминг-запроса |
| `ingested_at` | `timestamptz` | Метка времени записи в Bronze |

### 2.2 Таблица `bronze.avro_schemas`

Архив всех зарегистрированных и встреченных Avro-схем.

Колонки: `schema_id` (int), `fingerprint_sha256` (string), `subject` (string), `registry_version` (int), `schema_json` (string), `references_json` (string), `spark_self_contained_schema_json` (string), `first_seen_at` (timestamptz), `last_verified_at` (timestamptz).

---

## 3. Схемы слоя Silver

Для каждой из 8 бизнес-сущностей создаются две таблицы:
1. `silver.<entity>_changes` — неизменяемый журнал бизнес-событий (event ledger).
2. `silver.<entity>_current` — текущее срезовое состояние сущностей.

### 3.1 Поля таблицы `silver.<entity>_changes`

- Служебные идентификаторы и статус: `event_id`, `op` (`c/r/u/d`), `is_snapshot`, `is_deleted`, `apply_status` (`applied` / `rejected`), `error_code`, `error_message`.
- Бизнес-колонки сущности (согласно типу MySQL, приведение к UTC/NTZ).
- Метаданные источника binlog: `source_ts`, `source_server_id`, `source_gtid`, `source_binlog_file`, `source_binlog_file_index`, `source_binlog_pos`, `source_row`.
- Метаданные транзакции и Kafka: `transaction_id`, `transaction_total_order`, `transaction_data_collection_order`, `kafka_topic`, `kafka_partition`, `kafka_offset`, `kafka_timestamp`.
- Хэши и версии: `key_schema_id`, `value_schema_id`, `schema_fingerprint`, `contract_version`, `before_row_hash`, `after_row_hash`, `row_hash`, `bronze_ingested_at`, `normalized_at`.

### 3.2 Поля таблицы `silver.<entity>_current`

Бизнес-колонки сущности плюс метаданные версии: `is_deleted`, `deleted_at`, `last_event_id`, `last_source_ts`, `last_transaction_id`, `last_kafka_partition`, `last_kafka_offset`, `last_row_hash`, `contract_version`, `updated_at`.

---

## 4. Схемы служебных таблиц (Audit & Reference)

В пространстве имен `audit` содержатся:
- `audit.mysql_transactions`: отслеживание статуса и границ транзакций (`OPEN`, `COMPLETE`, `REJECTED`).
- `audit.silver_progress`: детальный прогресс обработки по сущностям, партициям и смещениям.
- `audit.normalization_errors`: журнал ошибок нормализации и бизнес-валидации.
- `audit.schema_violations`: журнал нарушений контрактов схем.
- `audit.maintenance_runs`: журнал процедур обслуживания Iceberg.
- `audit.serving_sync_reports`: отчеты о синхронизации с ClickHouse serving.
- `audit.schema_migrations`: версия примененных миграций схемы Iceberg.

В пространстве имен `reference` содержится:
- `reference.geolocation`: неизменяемый справочник геопозиций, загружаемый разовым плановым процессом из MySQL.

---

## 5. Связанные документы

- [Дорожная карта миграции (Roadmap)](../../mysql-spark-iceberg-lakehouse-migration.md)
- [Контракт архитектуры и runtime](architecture-and-runtime.md)
- [Контракт MySQL, Kafka и Avro](mysql-kafka-avro.md)
- [Контракт Spark Structured Streaming](spark-streaming.md)
