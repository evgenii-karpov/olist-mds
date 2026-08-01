# Wave 2 / J2 runbook: Scala data plane и интеграция

- **Status**: Completed / Frozen
- **Purpose**: Historical execution and acceptance runbook for Wave 2/J2
- **Active instruction**: No
- **Evidence**: [docs/reports/mysql-spark-iceberg-wave2-j2-validation.md](../../../reports/mysql-spark-iceberg-wave2-j2-validation.md)
- **Implementation commit**: `33a34de87250a9e34b320e9698764b23d6eaef37`

---

## 1. Назначение и рамки Wave 2 / J2

Wave 2 реализует движок потоковой обработки CDC на базе Spark Structured Streaming и Scala 2.13.17.
Основные компоненты:
- Потоковые процессоры Bronze (`BronzeMain`) и Silver (`SilverMain`);
- Автоматическая архивация и резолюция Avro-схем в Apicurio;
- Общий движок нормализации данных 8 бизнес-сущностей (`EntityBatchProcessor`);
- Идемпотентные райтеры для таблиц `changes`, `current` и `audit` в Iceberg;
- Супервизор запросов с обработкой transient/fatal ошибок;
- Инструменты конечного повтора (`ReplayMain`) и разовой загрузки справочника геопозиций (`GeolocationMain`).

Действующие нормативные контракты слоя данных:
- [Контракт Spark Structured Streaming](../contracts/spark-streaming.md)
- [Контракт модели данных Iceberg](../contracts/iceberg-data-model.md)
- [Контракт архитектуры и runtime](../contracts/architecture-and-runtime.md)

---

## 2. Историческая структура пакетов S0–S8

1. **S0 — Фиксация baseline**: проверка 26 таблиц Iceberg, чексуммы миграции и контракта v2.
2. **S1 — Scala foundation**: создание единого корня сборки `streaming/spark/scala` (sbt 1.12.11, Scala 2.13.17), генерация ресурсов контрактов и пяти главных точек входа.
3. **S2 — Bronze engine**: реализация записи сырых байтов Kafka в `bronze.mysql_cdc_records` с проверкой обрамления Confluent Avro и анти-соединением по `event_id`.
4. **S3 — Schema archive**: реализация `capture_avro_schemas` и регистратора схем из Apicurio в `bronze.avro_schemas`.
5. **S4 — Common normalization engine**: 11-шаговый пайплайн декодирования, валидация Avro в FAILFAST, вычисление детерминированных хэшей колонок.
6. **S5 — Восемь entity modules**: валидационные правила для `customers`, `orders`, `order_items`, `order_payments`, `order_reviews`, `products`, `sellers`, `product_category_translation`.
7. **S6 — Idempotent writers**: последовательный коммит `changes → errors → current → progress` с блокировкой на уровне таблиц аудита.
8. **S7 — Supervisor & Ops**: обработчик сбоев с экспоненциальным backoff, `ReplayMain`, `GeolocationMain`, `LakehouseStatusMain`.
9. **S8 — Image & CLI**: сборка единого образа `olist-spark:4.1.3-iceberg1.11.0`, интеграция команд `start-streaming` и `wait-caught-up` в `local_lab.py`.

---

## 3. Критерии приемки J2 (J2.1 – J2.7)

- **J2.1 Static & Build gate**: успешное выполнение `sbt test package`, `uv lock --check`, `ruff`, `pyright`, pytest тестов.
- **J2.2 Clean Bootstrap & Initial Snapshot**: запуск с чистого домена, первоначальный импорт 79 записей snapshot без потерь данных.
- **J2.3 CRUD / Transaction scenario**: обработка транзакционных сценариев INSERT, UPDATE, DELETE с валидацией версионности в `current` и `changes`.
- **J2.4 Retry & Isolation drills**: проверка устойчивости при сбоях после коммитов и изоляции падений отдельных запросов.
- **J2.5 Replay proof**: подтверждение корректности работы ReplayMain (`rejected → applied`).
- **J2.6 dbt regression boundary**: подтверждение прохождения тестов dbt-clickhouse (`PASS=78`) без обратных зависимостей.
- **J2.7 Report**: финальный отчет со статусом `J2 ACCEPTANCE PASS`.

---

## 4. Результат приемки

Все критерии приемки Wave 2 / J2 выполнена полностью. Итоговый отчет приемки зафиксирован в [docs/reports/mysql-spark-iceberg-wave2-j2-validation.md](../../../reports/mysql-spark-iceberg-wave2-j2-validation.md).

**Статус**: COMPLETE (`J2 ACCEPTANCE PASS`)
