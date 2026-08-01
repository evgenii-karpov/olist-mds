# Технический контракт: Слой публикаций ClickHouse, dbt Gold и сценарии восстановления (Serving & Recovery)

- **Статус**: Действующий нормативный контракт (Active normative contract)
- **Назначение**: Описание организации витрин ClickHouse serving, структуры dbt-clickhouse Gold, регламентных задач Airflow и контракта обработки сбоев.
- **Порядок авторитетности**: Определяет действующие нормативные требования к аналитическому слою публикаций и механизмам отказоустойчивости.

---

## 1. Слой витрин ClickHouse Serving

### 1.1 Интеграция с каталогом Iceberg через DataLakeCatalog

В ClickHouse создается база данных `lakehouse` для прямого чтения таблиц Iceberg только для чтения (read-only):

```sql
SET allow_database_iceberg = 1;
CREATE DATABASE lakehouse
ENGINE = DataLakeCatalog('http://polaris:8181/api/catalog', 'spark', 'vended-credentials')
SETTINGS catalog_type = 'rest', warehouse = 'olist_lakehouse';
```

Учетная запись ClickHouse использует vended-credentials от Polaris и имеет права только на чтение метаданных и файлов Iceberg.

### 1.2 Нативные базы данных и таблицы ClickHouse

В ClickHouse создаются следующие базы данных:
- `serving_cdc`: события CDC в формате MergeTree / ReplacingMergeTree.
- `serving_control`: отслеживание опубликованных транзакций и запусков.
- `gold_store`: физическое хранилище витрин данных, партиционированное по `sync_run_seq`.
- `gold`: стабильные представления (views) над последним успешно опубликованным прогоном.

Таблицы `serving_cdc`:
- 8 таблиц журналов событий `events_<entity>` (`ENGINE = MergeTree`).
- 8 таблиц текущих версий `current_<entity>` (`ENGINE = ReplacingMergeTree(last_source_ts)`).
- 8 стабильных представлений `v_<entity>`, фильтрующих удаленные записи (`is_deleted = 0`) и неопубликованные запуски.

---

## 2. Физический слой dbt-clickhouse Gold

Отдельный dbt-проект располагается по пути `dbt/olist_clickhouse`. Проект не содержит веток для Redshift или BigQuery.

Физические модели слоя Gold:
- `dim_date`
- `dim_order_status`
- `dim_seller`
- `dim_customer_scd2`
- `dim_product_scd2`
- `fact_order_items`
- `mart_daily_revenue`
- `mart_monthly_arpu`

Модели физически сохраняются в `gold_store.<model>` с партиционированием `PARTITION BY sync_run_seq`. Публичные интерфейсы в базе `gold.<model>` представляют собой стабильные представления над последней опубликованной партицией `sync_run_seq`.

Запуск трансформаций dbt выполняется строго с указанием переменных прогона:

```powershell
dbt build --project-dir dbt/olist_clickhouse --vars '{"sync_run_seq": <n>, "sync_run_id": "<id>"}'
```

---

## 3. Регламентные задачи Airflow и обслуживание Iceberg

### 3.1 Границы Airflow

Airflow **не запускает** и не перезапускает непрерывные стриминг-процессы Spark (`spark-bronze`, `spark-silver`).
В Airflow содержатся только конечные (finite) DAGs:
- `olist_lakehouse_serving_sync`: периодическая синхронизация транзакционно-завершенных данных из Iceberg в ClickHouse.
- `olist_iceberg_maintenance`: процедуры оптимизации и очистки снимков Iceberg.
- `olist_clickhouse_rebuild`: полное перестроение аналитического слоя ClickHouse из Iceberg.
- `olist_lakehouse_quality`: проверки качества и паритета данных.

### 3.2 Обслуживание Iceberg (Maintenance)

Периодические процедуры оптимизации Iceberg включают:
- `rewrite_data_files` (уплотнение мелких файлов);
- `rewrite_manifests` (оптимизация манифестов);
- `expire_snapshots` (срок хранения снимков 7 дней, сохранение минимум 20 последних);
- `remove_orphan_files` (минимальный возраст осиротевших файлов 72 часа).

Инструменты обслуживания получают только явный путь к таблице Iceberg и не имеют доступа к бакету чекпоинтов `olist-checkpoints`.

---

## 4. Контракт обработки сбоев и восстановления (Failure & Recovery Contract)

| Сбой | Обязательное поведение системы |
| --- | --- |
| MySQL временно недоступен | Коннектор Debezium выполняет повторные попытки (retry); downstream обрабатывает накопленный backlog. |
| Kafka недоступна | Коннектор и Spark Bronze выполняют retry. |
| Сбой `spark-bronze` | Kafka буферизует сообщения в рамках срока хранения (retention 7 дней). |
| Сбой одного запроса в `spark-silver` | Обработка Bronze и остальных сущностей в Silver продолжается. Запрос переходит в статус `FATAL`. |
| Временный сбой Apicurio Registry | Обработка ранее заархивированных схем продолжается. Новые схемы ждут восстановления реестра. |
| Несовместимая схема Avro | Запрос конкретной сущности останавливается в статусе `FATAL` (fail-closed). |
| Polaris / MinIO недоступен | Spark выполняет retry; Kafka служит буфером. |
| Airflow остановлен | Запись CDC из MySQL в Iceberg продолжается. Данные в ClickHouse временно не обновляются. |
| ClickHouse недоступен или потерян | Запись CDC в Iceberg продолжается. Запуск `rebuild-serving` полностью восстанавливает ClickHouse из Iceberg. |
| Превышение retention в Kafka при сбое | Полный сброс контура (`reset --yes`) и повторный `bootstrap`. |
| Потеря чекпоинта Spark | Полный сброс контура (`reset --yes`) и повторный `bootstrap`. |
| Потеря базы Polaris или данных MinIO | Полный сброс контура (`reset --yes`) и повторный `bootstrap`. |
| Удален любой authoritative volume | Частичный ремонт запрещен; выполняется полный `reset --yes` и `bootstrap`. |
| Сбой публикатора ClickHouse до публикации | Новые данные скрыты от витрин (`gold`); повторный запуск переиспользует тот же `sync_run_seq`. |

---

## 5. Связанные документы

- [Дорожная карта миграции (Roadmap)](../../mysql-spark-iceberg-lakehouse-migration.md)
- [Контракт архитектуры и runtime](architecture-and-runtime.md)
- [Контракт модели данных Iceberg](iceberg-data-model.md)
- [Контракт Spark Structured Streaming](spark-streaming.md)
- [Контракт валидации и CI](validation-and-ci.md)
