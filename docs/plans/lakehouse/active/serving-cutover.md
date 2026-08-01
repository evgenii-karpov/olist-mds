# Операционный план: Переключение витрин, сквозная валидация, удаление устаревших компонентов и итоговый паритет (E → V → L → F)

- **Статус**: Активный операционный план (Active operational plan)
- **Назначение**: Описание порядка выполнения оставшихся последовательных стадий миграции: E (Serving integration), V (Candidate E2E validation), L (Legacy removal) и F (Final parity).
- **Порядок авторитетности**: Определяет порядок выполнения нереализованных стадий. Не дублирует полные технические контракты; при реализации ссылается на файлы из `lakehouse/contracts/`.

---

## Последовательность стадий

```text
E (Serving Integration) → V (Candidate E2E) → L (Legacy Removal) → F (Final Parity)
```

Каждая стадия начинается строго после полного выполнения критериев приемки предыдущей стадии.

---

## 1. Стадия E — Интеграция витрин публикаций (Serving Integration)

### 1.1 Preconditions
- Успешное завершение Wave 1 / J1 и Wave 2 / J2 ([J2 report](../../../reports/mysql-spark-iceberg-wave2-j2-validation.md)).
- Прохождение `status --require streaming` и `validate --scope streaming` со статусом `READY`.

### 1.2 Scope
- Реализация схемы базы данных управления в PostgreSQL (`olist_control`).
- Реализация транзакционно-завершенной синхронизации Airflow (`olist_lakehouse_serving_sync`).
- Интеграция таблиц событий и текущего состояния ClickHouse (`serving_cdc`).
- Интеграция витрин dbt-clickhouse (`gold_store` / `gold`).
- Реализация механизмов очистки и перестроения (`rebuild-serving`, `run-maintenance`).
- Подключение экспортеров метрик и мониторинга (Prometheus / Grafana).

### 1.3 Deliverables
- Исполняемые DAGs Airflow для синхронизации и обслуживания.
- Полностью работающий CLI функционал `local_lab.py sync-serving`, `rebuild-serving`, `run-maintenance`.
- Валидный статус `status --require serving` и `validate --scope serving`.

### 1.4 Applicable Contracts

- [Детальный план реализации Stage E](stage-e-serving-integration.md)
- [Контракт слоя публикаций и восстановления](../contracts/serving-and-recovery.md)
- [Контракт модели данных Iceberg](../contracts/iceberg-data-model.md)

### 1.5 Forbidden Premature Work
- Запрещено удалять legacy-компоненты (PostgreSQL OLTP, NiFi) до успешной сквозной проверки кандидата (стадия V).
- Запрещено публиковать транзакции со статусом `REJECTED` или `OPEN` в ClickHouse.

### 1.6 Condition to proceed to V
- Успешное прохождение `validate --scope serving` в чистом домене Docker Compose.

---

## 2. Стадия V — Сквозная валидация кандидата (Candidate E2E Validation)

### 2.1 Preconditions
- Успешное завершение и приемка стадии E.

### 2.2 Scope & Scenario
На чистом объеме Docker volumes (`reset --yes`):
1. Загрузка небольшого набора фикстур (`seed`).
2. Первоначальный снимок Debezium initial snapshot.
3. Проверка 79 записей бизнес-сущностей в Silver current.
4. Проверка 6 записей справочника геопозиций.
5. Выполнение транзакции создание записей в нескольких таблицах.
6. Выполнение транзакции обновления.
7. Выполнение удаления и отправка tombstone.
8. Одновременный перезапуск Bronze и Silver.
9. Достижение состояния догона без дубликатов `event_id`.
10. Выполнение синхронизации слоя витрин (`sync-serving`).
11. Выполнение сборки и тестов `dbt build`.
12. Проверка работы стабильных витрин ClickHouse (`FINAL` / `gold`).
13. Проверка сценария аддитивного изменения схемы с `null`.
14. Выполнение полного перестроения ClickHouse строго из Iceberg (`rebuild-serving`).

### 2.3 Deliverables
- Отчет о сквозной валидации целевой системы со статусом `PASS`.

### 2.4 Condition to proceed to L
- Полный проход всех 14 шагов сквозного сценария на чистом стенде.

---

## 3. Стадия L — Удаление устаревших компонентов (Legacy Removal)

### 3.1 Preconditions
- Успешная сквозная валидация кандидата на стадии V.

### 3.2 Scope
Удаление всех компонентов устаревшего контура:
- Контейнеры, схемы и адаптеры PostgreSQL OLTP;
- Процессоры, скрипты, инвентарь и секреты NiFi;
- Старые протоколы загрузки MinIO (landing/normalized);
- Поисковики и загрузчики манифестов;
- Топики Kafka DLQ;
- Загрузка `raw_cdc` в ClickHouse;
- Устаревшие DAGs непрерывной загрузки Airflow;
- Устаревшие модели и макросы dbt в `dbt/olist_analytics`;
- Неактивные компоненты AWS/Redshift (поскольку облачная программа вынесена в GCP plan).

### 3.3 Deliverables
- Чистое дерево исходного кода без устаревших файлов NiFi, PostgreSQL OLTP и старых DAGs.
- Обновленные конфигурационные файлы и CI-пайплайны.

### 3.4 Forbidden Premature Work
- Запрещено удалять исходные исторические коммиты из истории Git.

### 3.5 Condition to proceed to F
- Чистая сборка проекта, отсутствие неиспользуемых файлов, прохождение всех быстрых тестов CI.

---

## 4. Стадия F — Финальный паритетный тест (Final Parity)

### 4.1 Preconditions
- Успешное завершение удаления устаревших компонентов (стадия L).

### 4.2 Scope
- Последовательный запуск исходного (baseline из исторического Git commit) и целевого (candidate) контуров с помощью скрипта `scripts/parity/run_mysql_iceberg_final_parity.py --confirm-destructive`.
- Построчное сравнение текущего состояния сущностей, таблиц фактов и витрин данных.

### 4.3 Applicable Contracts
- [Контракт финального паритета](../contracts/final-parity.md)

### 4.4 Acceptance Criteria
- Нулевое количество отсутствующих или лишних ключей.
- Нулевое количество расхождений по колонкам бизнес-данных.
- Статус отчета: `PASS`.

---

## 5. Связанные документы

- [Дорожная карта миграции (Roadmap)](../../mysql-spark-iceberg-lakehouse-migration.md)
- [Контракт слоя публикаций и восстановления](../contracts/serving-and-recovery.md)
- [Контракт итогового паритета](../contracts/final-parity.md)
