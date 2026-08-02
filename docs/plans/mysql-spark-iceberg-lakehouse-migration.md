# Olist MDS: прямая миграция на MySQL, Spark Structured Streaming и Apache Iceberg

## 0. Управление документом

| Поле | Значение |
| --- | --- |
| Статус | Wave 1/J1, Wave 2/J2, Stage E, Stage V завершены (`Stage V ACCEPTANCE PASS`) |
| Последнее обновление | 2026-08-02 |
| Базовый commit текущей архитектуры | `c18766c276ef4edc828ccb0f46ea64460cd33a41` |
| Ветка реализации | `feature/mysql-spark-iceberg` |
| Evidence J1 | [docs/reports/mysql-spark-iceberg-wave1-j1-validation.md](../reports/mysql-spark-iceberg-wave1-j1-validation.md) |
| Evidence J2 | [docs/reports/mysql-spark-iceberg-wave2-j2-validation.md](../reports/mysql-spark-iceberg-wave2-j2-validation.md) |
| Evidence Stage E | [docs/reports/mysql-spark-iceberg-stage-e-validation.md](../reports/mysql-spark-iceberg-stage-e-validation.md) |
| Evidence Stage V | [docs/reports/mysql-spark-iceberg-stage-v-validation.md](../reports/mysql-spark-iceberg-stage-v-validation.md) |
| Основная аудитория | ИИ-агенты реализации и maintainers |
| Финальный fixture | `tests/fixtures/olist_small/olist_small.zip` |
| SHA-256 fixture | `5cf2ff7a104cae75d8a56cf8c6e00959894154a8d55aed2ddf0e3fa133a13976` |
| Cloud deployment | Вне локальной программы (см. [Deferred GCP plan](gcp-spark-iceberg-bigquery-migration.md)) |

---

## 1. Цель и целевая архитектура

Миграция заменяет исходный контур PostgreSQL/NiFi/ClickHouse на современный локальный Lakehouse-стек:

```text
MySQL OLTP
  → Debezium MySQL / Kafka Connect
  → Kafka + Apicurio Registry (Confluent-framed Avro)
  → Spark Structured Streaming (Scala data plane)
  → Apache Iceberg на MinIO через Polaris REST Catalog
      ├── Bronze raw Kafka records
      ├── Silver typed changes & current state
      ├── transaction & audit tables
      └── immutable reference data
  → finite ClickHouse serving sync
  → native ClickHouse MergeTree/ReplacingMergeTree
  → отдельный dbt-clickhouse project (Gold)
```

```mermaid
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
```

---

## 2. Системные инварианты

- **MySQL** — единственная авторитетная OLTP СУБД источника данных бизнеса.
- **Kafka** — ограниченный по времени хранения буфер транспортировки и повтора (retention 7 дней).
- **Iceberg** — каноническое хранилище слоев Bronze, Silver, аудита и справочников.
- **ClickHouse** — полностью перестраиваемый слой витрин (serving layer).
- **PostgreSQL** — ограничен исключительно служебным control plane (Airflow, Polaris, Apicurio, `olist_control`).
- **Airflow и ClickHouse не входят в durability path**. При их сбое транспортировка из MySQL в Iceberg продолжается.

### Явно исключенные решения

- Параллельное ведение теневой базы PostgreSQL/MySQL;
- Адаптация NiFi под MySQL;
- Сохранение или перенос старых томов Docker;
- Откат runtime обратно на PostgreSQL;
- Введение нескольких несогласованных поколений `source_epoch`;
- Повторный батчевый импорт 8 CDC-таблиц;
- Таблицы Gold в Iceberg;
- Потоковое чтение (`readStream`) из таблиц Silver;
- GCP/Terraform ресурсы в текущей ветке.

---

## 3. Матрица статуса стадий программы

| Стадия | Статус | Планы и инструкции | Подтверждение (Evidence) |
| --- | --- | --- | --- |
| **Wave 1 / J1** | Complete | [lakehouse/completed/wave-1-j1-runbook.md](lakehouse/completed/wave-1-j1-runbook.md) | [J1 report](../reports/mysql-spark-iceberg-wave1-j1-validation.md) |
| **Wave 2 / J2** | Complete | [lakehouse/completed/wave-2-j2-runbook.md](lakehouse/completed/wave-2-j2-runbook.md) | [J2 report](../reports/mysql-spark-iceberg-wave2-j2-validation.md) |
| **E / Serving integration** | Complete | [lakehouse/active/stage-e-serving-integration.md](lakehouse/active/stage-e-serving-integration.md) | [Stage E report](../reports/mysql-spark-iceberg-stage-e-validation.md) |
| **V / Candidate E2E** | Complete | [lakehouse/active/stage-v-candidate-e2e-validation.md](lakehouse/active/stage-v-candidate-e2e-validation.md) | [Stage V report](../reports/mysql-spark-iceberg-stage-v-validation.md) |
| **L / Legacy removal** | Next (после V PASS) | [lakehouse/active/serving-cutover.md](lakehouse/active/serving-cutover.md) | — |
| **F / Final parity** | Pending (после L) | [lakehouse/active/serving-cutover.md](lakehouse/active/serving-cutover.md) + [lakehouse/contracts/final-parity.md](lakehouse/contracts/final-parity.md) | — |

Граф последовательности стадий:

```text
Wave 1 / J1 (Complete) → Wave 2 / J2 (Complete) → Stage E (Complete) → Stage V (Complete) → Stage L (Next) → Stage F
```

---

## 4. Навигация по документации программы

Документация миграции разделена на нормативные контракты, завершенные исторические прогоны и активный операционный план:

| Категория | Документ | Назначение |
| --- | --- | --- |
| **Contracts** | [architecture-and-runtime.md](lakehouse/contracts/architecture-and-runtime.md) | Целевая архитектура, зафиксированные версии компонентов, правила Git и интерфейс CLI (`local_lab.py`). |
| **Contracts** | [mysql-kafka-avro.md](lakehouse/contracts/mysql-kafka-avro.md) | Контракт источника MySQL, конфигурация Debezium, инвентарь топиков Kafka и правила Avro/Apicurio. |
| **Contracts** | [iceberg-data-model.md](lakehouse/contracts/iceberg-data-model.md) | Схемы таблиц Iceberg (Bronze, Silver, Audit, Reference), каталоги Polaris и бакеты MinIO. |
| **Contracts** | [spark-streaming.md](lakehouse/contracts/spark-streaming.md) | Спецификация движка Spark Structured Streaming на Scala, алгоритмы декодирования и коммитов в Iceberg. |
| **Contracts** | [serving-and-recovery.md](lakehouse/contracts/serving-and-recovery.md) | Интеграция ClickHouse, витрины dbt-clickhouse Gold, регламенты Airflow и обработка сбоев. |
| **Contracts** | [validation-and-ci.md](lakehouse/contracts/validation-and-ci.md) | Автоматические тесты, структура проверок CI и защитные барьеры. |
| **Contracts** | [final-parity.md](lakehouse/contracts/final-parity.md) | Контракт и алгоритм итогового сравнения паритета между legacy и candidate. |
| **Completed** | [wave-1-j1-runbook.md](lakehouse/completed/wave-1-j1-runbook.md) | Завершенный исторический runbook интеграции Wave 1 / J1 (зафиксирован). |
| **Completed** | [wave-2-j2-runbook.md](lakehouse/completed/wave-2-j2-runbook.md) | Завершенный исторический runbook Scala data plane Wave 2 / J2 (зафиксирован). |
| **Active** | [serving-cutover.md](lakehouse/active/serving-cutover.md) | Активный операционный план реализации стадий E, V, L и F. |
| **Deferred** | [gcp-spark-iceberg-bigquery-migration.md](gcp-spark-iceberg-bigquery-migration.md) | Отложенная программа облачной миграции на GCP / BigQuery (out of local scope). |

---

## 5. Роли документов и порядок авторитетности

При возникновении разночтений между документами действует следующий приоритет:

1. **Действующие контракты (`lakehouse/contracts/`)** определят действующее нормативное поведение системы.
2. **Активный план (`lakehouse/active/serving-cutover.md`)** определяет порядок невыполненных стадий (E/V/L/F).
3. **Отчеты о валидации (`docs/reports/`)** подтверждают фактически выполненные проверки и достигнутые результаты.
4. **Завершенные runbooks (`lakehouse/completed/`)** хранят исторический контекст выполнения и не используются как активные инструкции.

---

## 6. Общий Definition of Done программы

Миграция признается полностью завершенной только если:
- Вся реализация находится в ветке `feature/mysql-spark-iceberg`;
- Слой Wave 1/J1 и Wave 2/J2 полностью функционируют и подтверждены отчетами;
- Реализована транзакционная публикация в ClickHouse (Stage E);
- Проведен чистый сквозной тест кандидата (Stage V);
- Все компоненты устаревшего контура PostgreSQL/NiFi удалены из кода (Stage L);
- Итоговый тест паритета `run_mysql_iceberg_final_parity.py` имеет статус **PASS** без расхождений по колонкам (Stage F).
