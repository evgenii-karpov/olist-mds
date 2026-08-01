# Spark Structured Streaming data-plane contract

- **Статус**: Действующий нормативный контракт (Active normative contract)
- **Назначение**: Фиксация технической спецификации движка обработки Spark Structured Streaming, правил сборки Scala-проекта, алгоритмов декодирования CDC, фиксации пакетов в Iceberg и обработки ошибок.
- **Порядок авторитетности**: Определяет действующие нормативные требования к реализации уровня обработки данных (data plane).

---

## 1. Сборка Scala-проекта и требования к артефакту

Единственный корень сборки:

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

Параметры сборки:
- `organization := "com.olist.mds"`
- `name := "olist-spark-jobs"`
- `version := "0.1.0"`
- `scalaVersion := "2.13.17"`
- `sbt.version=1.12.11`

Сборка генерирует один тонкий (thin) JAR `olist-spark-jobs_2.13-0.1.0.jar`, который размещается в образе по пути `/opt/olist/jars/olist-spark-jobs.jar`.

Точки входа (Entrypoints):
- `com.olist.mds.spark.app.BronzeMain`
- `com.olist.mds.spark.app.SilverMain`
- `com.olist.mds.spark.app.ReplayMain`
- `com.olist.mds.spark.app.GeolocationMain`
- `com.olist.mds.spark.app.LakehouseStatusMain`

---

## 2. Структура пакетов и общий Scala API

Пакеты приложения:
- `com.olist.mds.spark.app`: главные классы и разбор аргументов CLI.
- `com.olist.mds.spark.config`: конфигурация и фабрика `SparkSession`.
- `com.olist.mds.spark.contract`: загрузчик ресурсов контрактов и валидатор.
- `com.olist.mds.spark.avro`: проверки Confluent framing, клиент Apicurio CCompat.
- `com.olist.mds.spark.bronze`: проекция и запись в Bronze.
- `com.olist.mds.spark.normalize`: общий декодер и `EntityBatchProcessor`.
- `com.olist.mds.spark.entity`: 8 сущностных модулей и `EntityRegistry`.
- `com.olist.mds.spark.iceberg`: координатор коммитов и райтеры в Iceberg.
- `com.olist.mds.spark.supervisor`: супервизор стриминг-запросов и статус.
- `com.olist.mds.spark.ops`: конечные операции повтора (replay), загрузчик геопозиций.

Обработка данных выполняется строго через `DataFrame` / `Column` выражения Spark SQL. Использование построчных UDF обработки бизнеса, `collect()` бизнес-строк на драйвере или RDD API для данных payload **запрещено**.

Порядок сущностей в `EntityRegistry`:
1. `customers`
2. `orders`
3. `order_items`
4. `order_payments`
5. `order_reviews`
6. `products`
7. `sellers`
8. `product_category_translation`

---

## 3. Названия стриминг-запросов и чекпоинты

В `BronzeMain` запускается один запрос:
- Имя: `kafka_to_bronze`
- Путь чекпоинта: `s3a://olist-checkpoints/kafka_to_bronze/contract-v2/`

В `SilverMain` в одном JVM запускаются 10 независимо контролируемых запросов:
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

Чекпоинт каждого запроса Silver: `s3a://olist-checkpoints/<query-name>/contract-v2/`. Использование общего чекпоинта несколькими запросами запрещено.

Триггер интервал обработки: `Trigger.ProcessingTime("60 seconds")` (или отрегулированный для тестов).

---

## 4. Алгоритм работы Kafka-to-Bronze

1. Источник Kafka считывает списочный состав из `topics.json`.
2. Заголовки (headers), ключи и значения сохраняются в сыром бинарном виде без декодирования бизнес-данных.
3. Проверяется 5-байтовое обрамление Confluent Avro (magic byte `0` и 4-байтовый ID схемы).
4. Ошибки обрамления фиксируются в `framing_error`, бинарные данные сохраняются в любом случае.
5. Запись в `bronze.mysql_cdc_records` выполняется через `foreachBatch` с левосторонним анти-соединением (left-anti join) по `event_id` для обеспечения идемпотентности при повторах батча. Операции `MERGE` или `UPDATE` к Bronze **запрещены**.

---

## 5. Алгоритм нормализации и запись в Silver/Audit

### 5.1 Последовательность коммитов в микробатче

Обработка батча в Silver выполняет коммиты строго в следующем порядке:

```text
changes → normalization_errors/schema audit → current → silver_progress
```

`silver_progress` коммитится **строго последним**.

### 5.2 Идемпотентный MERGE в `changes`

Ключ объединения MERGE для `changes` — строго `event_id`.
Правила обработки дубликатов:
1. Если запись с таким `event_id` уже существует и все поля совпадают — повтор признается идемпотентным no-op (поле `normalized_at` не обновляется).
2. Если существующая запись имеет статус `rejected`, а входящая — `applied` при совпадении всех неизменяемых метаданных в режиме `FiniteReplay` — разрешается обновление только изменяемых бизнес-колонок и статуса.
3. Попытка перезаписи ранее примененной записи (`applied`) с другими данными вызывает фатальную ошибку `applied_event_rewrite`.
4. Расхождение неизменяемых метаданных вызывает фатальную ошибку `ledger_transport_mismatch`.

### 5.3 Идемпотентный MERGE в `current`

В `current` попадает только последнее по смещению Kafka событие для каждого бизнес-ключа внутри батча. MERGE обновляет или вставляет запись только если новое смещение Kafka строго больше записанного `last_kafka_offset`. Отклоненные события (`rejected`) и tombstone не меняют таблицу `current`.

---

## 6. Классификация ошибок и супервизор

Ошибки разделяются на три класса:
1. `TransientFailure`: временные сетевые сбои, таймауты Polaris/Registry, конфликты оптимистичных коммитов Iceberg. Вызывают автоматический повтор с экспоненциальной задержкой.
2. `PermanentRecordFailure`: некорректные бинарные данные, нарушения валидации схемы или правил сущности. Генерируют отклоненную запись (`apply_status=rejected`) и запись в `audit.normalization_errors`, не останавливая поток.
3. `FatalContractFailure`: несовместимость контрактов, попытка перезаписи примененных событий, расхождение гидратации транзакций. Завершают работу конкретного запроса в статусе `FATAL`.

Супервизор `SilverMain` изолирует ошибки отдельных сущностей: остановка одного запроса в `FATAL` переводит общую готовность приложения в `DEGRADED`, но остальные 9 запросов продолжают обработку.

---

## 7. Конечный повтор (Finite Replay)

Приложение `ReplayMain` предоставляет управляемый процесс повторной нормализации ранее отклоненных событий из Bronze:

```text
ReplayMain --entity <entity> --topic <topic> --partition <p> --from-offset-inclusive <offset1> --to-offset-inclusive <offset2> --contract-version 2
```

Требования к выполнению Replay:
1. Перед запуском Replay контейнер `spark-silver` должен быть остановлен.
2. Replay считывает данные строго из Bronze.
3. Выполняются только разрешенные переходы статусов (`rejected → applied`). Изменение метаданных происхождения событий запрещено.

---

## 8. Связанные документы

- [Дорожная карта миграции (Roadmap)](../../mysql-spark-iceberg-lakehouse-migration.md)
- [Контракт архитектуры и runtime](architecture-and-runtime.md)
- [Контракт MySQL, Kafka и Avro](mysql-kafka-avro.md)
- [Контракт модели данных Iceberg](iceberg-data-model.md)
- [Контракт Serving layer и восстановления](serving-and-recovery.md)
