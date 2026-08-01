# Детальный план реализации Stage E: Serving Integration

- **Статус документа**: Active implementation plan
- **Стадия**: E — Serving Integration
- **Дата фиксации решений**: 2026-08-01
- **Предшествующие стадии**: Wave 1 / J1 и Wave 2 / J2
- **Следующая стадия**: V — Candidate E2E Validation
- **Назначение**: дать исполнителю полностью определённую последовательность реализации транзакционно завершённой публикации Iceberg → ClickHouse → dbt Gold, её обслуживания, восстановления и наблюдаемости.
- **Порядок авторитетности**: normative contracts из `docs/plans/lakehouse/contracts/` → этот implementation plan → validation report → runbooks.

---

## 1. Итоговое решение

Stage E должна превратить уже существующие заготовки ClickHouse и `dbt/olist_clickhouse` в конечный, повторяемый и восстанавливаемый serving-контур:

```text
Iceberg Silver + audit
        ↓ frozen transaction-complete plan
Airflow finite serving run
        ↓
ClickHouse unpublished candidate partitions
        ↓
dbt Gold candidate + tests
        ↓ PUBLISHED marker — единственная точка публикации
stable serving_cdc / gold views
```

Реализация обязана удовлетворять следующим инвариантам:

1. ClickHouse и Airflow не входят в durability path CDC. Каноническими данными остаются Iceberg tables.
2. Витрины никогда не показывают часть исходной MySQL-транзакции.
3. `OPEN` и `REJECTED` transaction не публикуются, а последующие transaction не пересекают такую границу.
4. Любой кандидат полностью невидим до вставки одного `PUBLISHED` marker.
5. Повтор после сбоя до marker переиспользует тот же `sync_run_seq` и безопасно перестраивает только его partitions.
6. Повтор после marker не материализует данные заново, а завершает control/audit metadata.
7. Потерянный ClickHouse полностью восстанавливается из Iceberg командой `rebuild-serving --yes`.
8. Iceberg maintenance не получает доступ к Spark checkpoint bucket.
9. Legacy-контур не удаляется и не меняет роль до успешного завершения Stage V.

### 1.1 Зафиксированные продуктовые решения

| Решение | Зафиксированное поведение |
| --- | --- |
| PostgreSQL control state | Узкий ledger в новой схеме `olist_control.serving`; отдельный PostgreSQL не создаётся |
| Transaction policy | Строгий barrier: не пересекать `OPEN`/`REJECTED` |
| Serving cadence | Sync каждые 5 минут, quality ежечасно, maintenance ежедневно |
| Активация schedules | Первый успешный ручной `sync-serving` снимает pause с трёх scheduled DAG |
| Rebuild | Только вручную, двойной guard: CLI `--yes` и DAG conf `confirm_destructive=true` |
| Timezone | UTC во всех timestamps, DAG schedules, reports и comparisons |
| ClickHouse publication | Marker-based; experimental multi-table transaction не используется |
| Gold retention | Сохранять текущий и предыдущий опубликованный Gold run; CDC event history не удалять |

### 1.2 Почему `olist_control.serving` необходима и где заканчивается её scope

Схема управления нужна не ради копирования данных, а для координации операций, которые затрагивают несколько независимых систем и не имеют общей транзакции:

- выделить монотонный `sync_run_seq`;
- пережить Airflow task/DagRun retry;
- один раз заморозить transaction boundary, Kafka offsets и Iceberg snapshot IDs;
- отличить unpublished candidate от уже опубликованного, но ещё не финализированного run;
- сериализовать sync, rebuild и maintenance;
- восстановить control cursor после сбоя между ClickHouse marker и записью отчёта.

В PostgreSQL запрещено хранить:

- business rows;
- CDC payload, Avro payload или before/after images;
- копию ClickHouse event/current/gold tables;
- сырые credentials или тексты ошибок, способные содержать payload/secret.

Airflow XCom используется только для коротких ID и branch result. Он очищается при task retry и не является долговременным ledger: [Airflow 3.2 XCom](https://airflow.apache.org/docs/apache-airflow/3.2.1/core-concepts/xcoms.html).

ClickHouse marker выбран вместо multi-table transaction, потому что полные транзакции ClickHouse experimental, требуют Keeper/ZooKeeper и не соответствуют текущей локальной топологии: [ClickHouse transactions](https://clickhouse.com/docs/concepts/features/operations/insert/transactions).

### 1.3 В scope Stage E

- Обязательное восстановление недостающих J2 audit/progress механизмов, без которых строгая граница невозможна.
- PostgreSQL serving ledger и reconciliation.
- Полная реализация finite Airflow DAG для serving sync.
- Интеграция существующих ClickHouse tables/views.
- Исправление изоляции unpublished current candidates.
- Интеграция существующего `dbt/olist_clickhouse` в publication flow.
- Quality DAG, Iceberg maintenance DAG и ClickHouse rebuild DAG.
- CLI `sync-serving`, `rebuild-serving`, `run-maintenance`, serving status/validate.
- Метрики, alerts, dashboard и runbooks Stage E.
- Static/component/clean-domain validation и Stage E report.

### 1.4 Вне scope Stage E

- Удаление PostgreSQL/NiFi/старых DAG/dbt-компонентов — только Stage L после Stage V.
- Полный 14-шаговый CRUD/restart/schema-evolution сценарий — Stage V.
- Финальное сравнение candidate с historical baseline — Stage F.
- Обновление версий PostgreSQL, Airflow, Spark, Iceberg, ClickHouse или dbt.
- Новая бизнес-логика Gold и изменение публичного grain существующих восьми моделей.
- Новая distributed transaction layer, Keeper или ZooKeeper.

---

## 2. Фактическая исходная точка и обязательные исправления контрактов

### 2.1 Что уже существует

- `platform-postgres` уже содержит отдельную БД/роль `olist_control`.
- В `olist_control` уже создаются legacy-схемы `audit` и `cdc_audit`.
- `scripts/orchestration/control_postgres.py` уже реализует file-secret connection helper.
- ClickHouse DDL уже создаёт `serving_cdc`, `serving_control`, `gold_store`, `gold`.
- Уже существуют восемь `<entity>_events`, восемь `<entity>_current_versions` и восемь `<entity>_current` views.
- `serving_control.published_runs` и `published_runs_current` уже существуют.
- `dbt/olist_clickhouse` уже содержит восемь физических Gold models, candidate vars, tests и stable public views.
- Polaris уже создаёт `spark_writer`, `clickhouse_reader` и `airflow_maintenance`; последний имеет table read/write для maintenance.
- Airflow и ClickHouse уже входят в Compose profile `serving`.

### 2.2 Разрывы, которые реализация обязана закрыть

1. `SilverBatchWriter` не материализует полный Silver changes/current contract и не пишет `audit.silver_progress`.
2. `audit.mysql_transactions` не формируется отдельным transaction query.
3. Bronze/Silver status публикует пустые `partition_offsets`.
4. `wait-caught-up` считает состояние READY без сравнения с captured Kafka targets.
5. CLI Stage E пока возвращает `not_available_until`.
6. `status` не имеет корректного `streaming` выбора и не выполняет serving semantic checks.
7. Airflow image копирует только `dbt/olist_analytics`, а `DBT_PROFILES_DIR` указывает на legacy project.
8. Airflow image не содержит Spark client/provider для finite maintenance jobs.
9. DAG Stage E отсутствуют.
10. Observability configs ссылаются на отсутствующие или legacy exporters.
11. CI проверяет преимущественно legacy path и не имеет bounded serving component gate.
12. `current_versions` используют `PARTITION BY tuple()` и `ORDER BY business PK`: merge unpublished candidate способен вытеснить published version того же PK.

### 2.3 Обязательные правки нормативных документов

До реализации поведения обновить contracts так, чтобы код не расходился с более авторитетным текстом:

- В `serving-and-recovery.md` закрепить фактические имена `<entity>_events`, `<entity>_current_versions`, `<entity>_current`.
- Для current tables закрепить `ReplacingMergeTree(kafka_offset)`, `PARTITION BY sync_run_seq`, `ORDER BY (sync_run_seq, business PK)`.
- В `architecture-and-runtime.md` закрепить `rebuild-serving --yes`, `status --require streaming|serving` и три serving schedules.
- В `validation-and-ci.md` добавить Stage E component gate, не смешивая его с полным Stage V E2E.
- В `serving-cutover.md` заменить абстрактную «реализацию БД управления» на ссылку на узкую схему, описанную здесь.

---

## 3. E0 — обязательный J2 contract repair

Stage E не должна рассчитывать transaction boundary до прохождения этого блока. Если E0 не проходит, serving implementation останавливается; fallback на `silver.current`, wall-clock timestamp или непроверенные status-файлы запрещён.

### 3.1 Целевой runtime Silver

В одном `spark-silver` application должны работать десять именованных streaming queries:

1. `bronze_to_silver_customers`
2. `bronze_to_silver_orders`
3. `bronze_to_silver_order_items`
4. `bronze_to_silver_order_payments`
5. `bronze_to_silver_order_reviews`
6. `bronze_to_silver_products`
7. `bronze_to_silver_sellers`
8. `bronze_to_silver_product_category_translation`
9. `capture_avro_schemas`
10. `normalize_mysql_transactions`

Все query используют стабильные имена и отдельные checkpoint paths с contract version. Изменение query name/checkpoint path считается несовместимой миграцией и требует полного disposable reset.

### 3.2 Entity normalization

Для каждой entity query реализовать общий `EntityBatchProcessor`:

1. Отфильтровать ровно один business topic согласно contract manifest.
2. Проверить/deduplicate `event_id`; conflicting metadata по одному ID — fatal `event_identity_collision`.
3. Отделить tombstones. Tombstone не создаёт changes/current row, но его offset обязан войти в progress.
4. Получить key/value schema metadata только из `bronze.avro_schemas`; прямой registry access из entity query запрещён.
5. Проверить writer fingerprints против v2 contract.
6. Выполнить bounded Avro pre-validation, затем FAILFAST decode.
7. Проверить envelope, op, entity/topic, PK, exact types/nullability и entity rules.
8. Сформировать полный row `<entity>_changes`, включая:
   - `event_id`, `op`, `is_snapshot`, `is_deleted`;
   - `apply_status`, fixed `error_code/error_message`;
   - nullable business columns;
   - source/binlog/GTID metadata;
   - transaction ID и orders;
   - Kafka topic/partition/offset/timestamp;
   - schema IDs/fingerprint/contract version;
   - before/after/row hashes;
   - Bronze/normalization timestamps.
9. Разделить applied/rejected rows без утечки payload в logs/audit.
10. Выполнить commit protocol из следующего пункта.

Permanent validation error записывает rejected changes row и позволяет checkpoint advance. Unexpected exception всегда fatal и не превращается в permanent record.

### 3.3 Идемпотентный commit protocol

Порядок commit неизменяем:

```text
changes → normalization_errors/schema_violations → current → silver_progress
```

Требования:

- Changes MERGE key — только `event_id`.
- Exact retry — no-op, первоначальный `normalized_at` сохраняется.
- Applied row нельзя переписать с отличающимися immutable provenance fields.
- Разрешённая finite replay correction меняет только rejected → applied mutable fields.
- Current обновляется только applied row с более новым offset в той же Kafka partition.
- Equal offset + same event ID — no-op; equal offset + другой event ID — fatal.
- Delete envelope создаёт soft-delete current row; следующий tombstone current не меняет.
- `silver_progress` записывается последним и только после фактического commit changes/current.
- Progress MERGE key:

```text
query_name, entity, contract_version, source_topic,
kafka_partition, spark_batch_id
```

- `changes_snapshot_id` читается после commit changes.
- `current_snapshot_id` содержит новый snapshot ID либо NULL, если current не изменился.
- `last_kafka_offset` включает tombstone offset.
- Status: `COMMITTED` или `COMMITTED_WITH_REJECTIONS`.

Общие audit tables защищаются driver-local fair lock на fully-qualified table. Lock не держится во время registry I/O/decode, одновременно удерживается не более одного table lock.

### 3.4 Transaction metadata query

`normalize_mysql_transactions` обрабатывает только `olist_cdc.transaction`:

- actual writer schema архивируется и проверяется structural reader contract;
- BEGIN создаёт/подтверждает immutable `OPEN` row;
- logical duplicate BEGIN/END схлопывается;
- conflicting BEGIN/END — fatal `transaction_metadata_conflict`;
- END offset обязан быть больше BEGIN offset;
- transaction topic имеет одну partition, но DataFrame row order не считается сохранённым.

END может перейти в финальный status только после пяти проверок:

1. `event_count` равен distinct Silver changes rows с этим `transaction_id`.
2. Counts каждой declared `data_collection` совпадают; collection name exact-map'ится на одну из восьми entities.
3. `transaction_total_order` образует `1..event_count`; per-collection order также непрерывен.
4. Latest committed `silver_progress` involved partitions покрывает максимальный offset transaction rows.
5. Каждый event имеет ровно один effective outcome: applied либо rejected.

Если rows/progress ещё не готовы, вернуть transient `transaction_not_ready` и не продвигать checkpoint. Extra rows, gaps, unknown collection или conflicting END — fatal contract error.

Финальный status:

- `COMPLETE`, если все rows applied;
- `REJECTED`, если хотя бы одна row rejected;
- `rejected_event_ids` сортируются лексикографически;
- допустимый replay transition — только `REJECTED → COMPLETE`;
- `COMPLETE` никогда не понижается;
- snapshot rows с `transaction_id=NULL` не создают synthetic transaction.

После transaction commit записать progress с `entity='__transactions__'`, где `changes_snapshot_id` — snapshot `audit.mysql_transactions`, а `current_snapshot_id=NULL`.

### 3.5 Реальный status и caught-up barrier

Bronze и Silver status JSON должны содержать:

- application name и contract version;
- stable query names/IDs;
- state и last batch ID;
- last progress timestamp;
- реальную карту `topic:partition → last processed offset`;
- fixed error class/code без payload;
- atomic file replacement.

`wait-caught-up --timeout`:

1. Через `confluent-kafka` один раз фиксирует high watermark каждой partition 11 external topics.
2. Target равен `high - 1`, для empty partition `-1`.
3. Targets не пересчитываются во время polling.
4. Ждёт Bronze coverage всех targets.
5. Ждёт `__schemas__` progress всех external partitions.
6. Ждёт entity progress business partitions.
7. Ждёт `__transactions__` progress transaction topic и отсутствие OPEN transaction в target range.
8. Записывает target JSON в non-secret temporary file.
9. Запускает finite `LakehouseStatusMain`.
10. Возвращает один sanitized JSON result.

Finite validator проверяет фактический Iceberg state:

- progress offset coverage;
- snapshot IDs существуют и читаются;
- duplicate `event_id=0`;
- current PK uniqueness;
- changes outcome counts;
- schema archive coverage;
- transaction state/count/order invariants;
- rejected rows/transactions внутри captured target как отдельный boundary signal.

Результат обязан разделять два измерения:

- `coverage_state=READY|NOT_CAUGHT_UP`: все captured offsets и snapshot IDs фактически покрыты;
- `boundary_state=READY|OPEN|REJECTED|INVARIANT_VIOLATION`: можно ли публиковать весь captured range.

`wait-caught-up` CLI возвращает overall `READY` только при `coverage_state=READY` и `boundary_state=READY`. При покрытом, но rejected/open range он возвращает code 2 и JSON `coverage_state=READY` с соответствующим boundary state. Serving planner использует structured result: он требует `coverage_state=READY`, затем сам выбирает COMPLETE-prefix до OPEN/REJECTED. Для initial snapshot любая rejection остаётся безусловным `SNAPSHOT_REJECTED` blocker.

Exit codes:

| Code | Значение |
| --- | --- |
| `0` | `READY` |
| `2` | `NOT_CAUGHT_UP` либо transient `BLOCKED` |
| `3` | `INVARIANT_VIOLATION` |
| `1` | `EXECUTION_ERROR` |

### 3.6 E0 stop/go acceptance

E0 считается завершённым только при наличии automated evidence:

- initial snapshot покрыт непустыми offsets и snapshot IDs;
- multi-table transaction становится COMPLETE только после всех entity progress;
- rejected event переводит transaction в REJECTED;
- finite replay переводит её в COMPLETE без duplicate event/current/error rows;
- rejected test возвращает `coverage_state=READY`, `boundary_state=REJECTED`, а не маскируется как transport lag;
- simultaneous Bronze/Silver restart восстанавливается с checkpoint;
- `wait-caught-up` не возвращает READY раньше target coverage;
- status JSON не содержит business values или credentials.

---

## 4. PostgreSQL serving ledger

### 4.1 Миграция и privileges

Добавить следующую idempotent migration после существующих `infra/control-postgres/initdb/00x_*` и обновить grants migration:

- bootstrap/admin role владеет схемой и objects;
- runtime role `olist_control` получает `USAGE` на schema;
- runtime получает `SELECT, INSERT, UPDATE, DELETE` на три tables;
- runtime получает `USAGE, SELECT` на sequence;
- runtime не получает `CREATE` на schema `serving`;
- legacy schemas/grants не изменяются до Stage L.

Миграция обязана выполняться как на новом volume, так и повторным `platform-postgres-bootstrap` на существующем volume.

### 4.2 Точная логическая схема

#### `serving.sync_run_seq`

```sql
CREATE SEQUENCE serving.sync_run_seq AS bigint START WITH 1 INCREMENT BY 1;
```

Sequence может иметь gaps после rollback/no-op. Единственное требование — монотонность и отсутствие повторного использования номера.

#### `serving.sync_runs`

| Column | Type / constraint | Назначение |
| --- | --- | --- |
| `sync_run_seq` | `bigint PK default nextval(...)` | Publication/candidate sequence |
| `sync_run_id` | generated unique text | `sync-` + 20-digit seq |
| `operation_type` | `SYNC|REBUILD` | Тип логического run |
| `status` | fixed CHECK set | State machine |
| `status_reason` | nullable fixed text | Ровно одно из `NONE`, `NO_NEW_TRANSACTION`, `SOURCE_NOT_CAUGHT_UP`, `OPEN_TRANSACTION`, `OPEN_TRANSACTION_STALE`, `REJECTED_TRANSACTION`, `SNAPSHOT_REJECTED`, `ACTIVE_LEASE`, `MATERIALIZATION_MISMATCH`, `PUBLICATION_DRIFT`, `INVARIANT_FAILURE`, `EXECUTION_FAILURE` |
| `current_airflow_dag_run_id` | nullable text | Последний DagRun, исполняющий logical run |
| `attempt_count` | integer >= 0 | Количество захватов run |
| `is_noop` | boolean | Нет ClickHouse candidate/marker |
| `previous_transaction_id` | nullable text | Предыдущая published boundary |
| `previous_transaction_end_offset` | nullable bigint | Позиция в transaction topic |
| `target_transaction_id` | nullable text | Последняя transaction candidate prefix |
| `target_transaction_end_offset` | nullable bigint | Frozen target position |
| `source_snapshot_completed` | boolean | Initial snapshot gate |
| `target_offsets_json` | JSON object | Frozen business/transaction offsets |
| `iceberg_snapshot_ids_json` | JSON object | Frozen per-table snapshot IDs |
| `expected_event_count` | bigint >= 0 | План |
| `materialized_event_count` | bigint >= 0 | Факт |
| `expected_entity_counts_json` | JSON object | План по entity |
| `materialized_entity_counts_json` | JSON object | Факт по entity |
| `report_json` | JSON object | Sanitized immutable publication report |
| `error_details_json` | JSON object | Sanitized error class/code/context |
| `started_at` | timestamptz | Начало logical run |
| `updated_at` | timestamptz | Последний state transition |
| `published_at` | nullable timestamptz | Deterministic marker timestamp |
| `completed_at` | nullable timestamptz | Terminal state |

Для всех JSON columns добавить `jsonb_typeof(value)='object'`. Business payload и unbounded exception string запрещены.

`report_json` сериализуется канонически: UTF-8, keys recursively sorted, separators `,`/`:` без пробелов, timestamps в UTC ISO-8601 с microseconds, decimals строкой fixed scale. `report_sha256` вычисляется как lowercase SHA-256 этих bytes и хранится внутри report; при вычислении hash поле `report_sha256` временно исключается. Один и тот же logical report обязан давать одинаковые bytes/hash в Python, ClickHouse marker и Iceberg audit.

#### `serving.sync_entity_results`

| Column | Type / constraint |
| --- | --- |
| `sync_run_seq` | FK → `sync_runs`, часть PK |
| `entity` | одна из восьми entities, часть PK |
| `status` | `PLANNED|MATERIALIZED|VALIDATED|FAILED` |
| `expected_event_count` | bigint >= 0 |
| `materialized_event_count` | bigint >= 0 |
| `affected_key_count` | bigint >= 0 |
| `candidate_current_count` | bigint >= 0 |
| `event_checksum` | nullable lowercase SHA-256 |
| `error_code` | nullable fixed code |
| `updated_at` | timestamptz |

`event_checksum` вычисляется одинаково planner и materializer: для каждой selected row построить UTF-8 строку `event_id|row_hash-or-<null>|transaction_id-or-<snapshot>`, отсортировать строки побайтово по `event_id`, соединить `\n` без завершающего newline и взять lowercase SHA-256. Business values в checksum input не включаются.

#### `serving.runtime_state`

Singleton row с `singleton_key=1`:

| Column | Назначение |
| --- | --- |
| `last_published_sync_run_seq` | Последний согласованный PUBLISHED marker |
| `last_published_transaction_id/end_offset` | Serving transaction cursor |
| `last_published_target_offsets_json` | Published business offsets |
| `source_snapshot_completed` | Snapshot уже опубликован |
| `lease_owner_id` | Logical operation ID |
| `lease_owner_sync_run_seq` | Nullable seq для sync/rebuild |
| `lease_operation` | `SYNC|REBUILD|MAINTENANCE` |
| `lease_acquired_at/heartbeat_at/expires_at` | Durable lease lifecycle |
| `schedules_activated_at` | Первый successful manual sync |
| `row_version` | Optimistic update counter |
| `updated_at` | Audit timestamp |

### 4.3 State machine

```text
PLANNING
 ├─→ NOOP
 ├─→ WAITING
 ├─→ BLOCKED
 └─→ MATERIALIZING
       └─→ VALIDATING
             └─→ READY_TO_PUBLISH
                   └─→ PUBLISHED_PENDING_FINALIZATION
                         └─→ SUCCEEDED
```

Из любого pre-publish state допустим переход в `FAILED_RETRYABLE` либо `FAILED_TERMINAL`.

Правила:

- `FAILED_RETRYABLE`, `MATERIALIZING`, `VALIDATING`, `READY_TO_PUBLISH` возобновляются с тем же seq.
- `PUBLISHED_PENDING_FINALIZATION` никогда не возвращается к materialization.
- `SUCCEEDED`, `NOOP`, `WAITING`, `BLOCKED`, `FAILED_TERMINAL` — terminal logical run.
- Следующий scheduled DagRun может создать новый seq после terminal run.
- State update обязан указывать допустимый previous status в `WHERE`; update zero rows означает concurrency/invariant error.
- `published_at` задаётся один раз до marker и не меняется при retry.

### 4.4 Global operation lease

- Lease serializes sync, rebuild и maintenance across разные DAG.
- Airflow pool остаётся дополнительным ограничением ресурсов, но не authoritative lock.
- Default TTL — 30 минут.
- Каждая длительная task обновляет heartbeat до и после external operation.
- Scheduled sync, встретив активную чужую lease, завершается `WAITING`, а не занимает worker до освобождения.
- Просроченная lease захватывается только после reconciliation PostgreSQL ↔ ClickHouse.
- Quality DAG не захватывает mutation lease; при любой активной mutation lease он не читает serving databases, отмечает run `WAITING` и завершается без alert о качестве.

### 4.5 Reconciliation и восстановление ledger

Перед каждым sync/rebuild:

1. Прочитать `runtime_state` под row lock.
2. Прочитать latest effective row `serving_control.published_runs_current`.
3. Прочитать latest successful `audit.serving_sync_reports` через Iceberg/ClickHouse catalog.
4. Сравнить seq, run ID, transaction boundary и report hash.

Матрица:

| PostgreSQL | ClickHouse | Iceberg report | Действие |
| --- | --- | --- | --- |
| Совпадает | Совпадает | Совпадает/ещё pending | Продолжить; при pending дописать report |
| Старее | Marker новее | Marker report валиден | Восстановить cursor, дописать Iceberg report |
| Новее | Marker отсутствует/старее | Любое | Fail closed; считать ClickHouse потерянным, требовать rebuild |
| Пуст | Marker + report согласованы | Есть | Импортировать completed summary, `setval(max_seq)`, восстановить cursor |
| Пуст | Marker отсутствует | Есть | Только rebuild; обычный sync запрещён |
| Расходятся ID/hash/boundary | Любое | Любое | Terminal invariant failure, никакой автоматической публикации |

После потери PostgreSQL неопубликованные ClickHouse partitions, seq которых нет среди markers/reports, считаются orphan candidates и удаляются до нового run.

---

## 5. Frozen transaction-complete serving plan

### 5.1 Предварительные проверки

Planner запускается только если:

- Compose profile `platform` healthy;
- `spark-bronze` и `spark-silver` active и без FATAL query;
- caught-up helper вернул captured target и `coverage_state=READY`; `boundary_state=OPEN|REJECTED` допустим как вход planner и обрабатывается строгим barrier;
- ClickHouse DataLakeCatalog читает required Iceberg tables;
- PostgreSQL migration/current row существуют;
- dbt project parseable;
- нет несовместимого активного lease.

Scheduled run ждёт caught-up не более 180 секунд. Первый ручной `sync-serving` передаёт 1200 секунд. Timeout scheduled run даёт `WAITING/SOURCE_NOT_CAUGHT_UP`, не failure.

### 5.2 Первичная публикация snapshot

Если `runtime_state.source_snapshot_completed=false`:

1. Debezium connector должен быть RUNNING и не находиться в snapshot phase.
2. Captured Kafka targets должны быть покрыты Bronze/Silver progress.
3. Все восемь entity changes snapshots должны существовать.
4. В captured range не должно быть rejected snapshot rows.
5. В candidate включаются applied rows с `is_snapshot=true`.
6. Одновременно допускается включить последующий maximal COMPLETE transaction prefix, если он уже полностью покрыт.
7. `source_snapshot_completed=true` записывается только в PUBLISHED marker/cursor, не во время planning.

Если snapshot event rejected, run становится `BLOCKED`; частичная первичная публикация запрещена.

### 5.3 Выбор transaction prefix

Использовать latest effective transaction rows, начиная после `previous_transaction_end_offset`:

1. Упорядочить по `end_kafka_offset` transaction topic.
2. Проверить уникальность позиции и immutable metadata.
3. Идти последовательно до первой непубликуемой transaction.
4. `COMPLETE` включается только после повторной проверки event/collection/order/progress counts.
5. Первый `OPEN` останавливает prefix.
6. Первый `REJECTED` останавливает prefix и переводит run в `BLOCKED`.
7. Более поздние COMPLETE после OPEN/REJECTED не рассматриваются.
8. OPEN младше 10 минут считается normal waiting; старше 10 минут дополнительно поднимает alert.
9. Если streaming status утверждает caught-up, но COMPLETE counts не сходятся, это invariant failure, а не waiting.

### 5.4 Frozen per-entity snapshots

Для каждой entity:

- найти latest committed `silver_progress`, покрывающий максимальный required Kafka offset;
- сохранить `changes_snapshot_id` под ключом `silver.<entity>_changes`;
- не использовать меняющийся current snapshot для materialization;
- запросить frozen changes table через ClickHouse `SETTINGS iceberg_snapshot_id=<id>`;
- повторно посчитать selected events и checksum;
- сохранить expected count/checksum в PostgreSQL.

Snapshot может содержать события после target boundary; они исключаются exact transaction ID/offset filter. Использование «всех rows snapshot» запрещено.

### 5.5 No-op и blocked semantics

- Snapshot уже опубликован и новых COMPLETE transactions нет: `NOOP`, marker/cursor не меняются.
- Следующая transaction OPEN: `WAITING`.
- Следующая transaction REJECTED: `BLOCKED` и critical metric/alert.
- Iceberg snapshot/progress временно не покрывает selected COMPLETE: `WAITING`, только если Kafka/Silver ещё не caught up.
- Любое расхождение после подтверждённого caught-up: `FAILED_TERMINAL`.

No-op/WAITING/BLOCKED run может иметь выделенный seq; gaps среди PUBLISHED seq допустимы.

### 5.6 Повторная проверка перед marker

После candidate/dbt tests и непосредственно перед публикацией:

- перечитать latest effective status всех selected transactions;
- убедиться, что ни одна не стала REJECTED;
- повторить expected/materialized count comparison;
- убедиться, что candidate seq ещё не опубликован другим attempt;
- убедиться, что previous marker/cursor не изменился;
- обновить `READY_TO_PUBLISH → PUBLISHED_PENDING_FINALIZATION` только после успешной вставки marker.

---

## 6. ClickHouse serving materialization

### 6.1 Исправление current table isolation

Во всех восьми `<entity>_current_versions` изменить DDL на:

```sql
ENGINE = ReplacingMergeTree(kafka_offset)
PARTITION BY sync_run_seq
ORDER BY (sync_run_seq, <business primary key>)
```

Composite keys сохраняются в contract order. Существующий pre-Stage-E disposable domain пересоздаётся; online ALTER/migration старых local data не требуется.

Обязательный learning regression:

1. Вставить published seq 1 для PK.
2. Вставить unpublished seq 2 для того же PK.
3. Выполнить `OPTIMIZE TABLE ... FINAL`.
4. Stable view обязана всё ещё вернуть seq 1.
5. Вставить PUBLISHED marker seq 2.
6. Stable view обязана вернуть seq 2.

### 6.2 Единый entity registry

Создать один Python `ServingEntitySpec` registry со следующими fields:

- entity name;
- source changes relation;
- ClickHouse event/current relation;
- ordered business columns;
- ordered primary key;
- explicit ClickHouse cast expressions;
- contract version;
- expected topic/data collection names.

Registry строится/проверяется против v2 manifest и `table_specs.py`. Запрещено иметь отдельные несогласованные списки entities в planner, DAG, DDL generator и tests.

### 6.3 Event candidate task

Одна mapped task на entity:

1. Assert global lease owner и run state `MATERIALIZING`.
2. Проверить отсутствие PUBLISHED marker для seq.
3. `ALTER TABLE <events> DROP PARTITION <seq>` только для unpublished seq; отсутствие partition — no-op.
4. Вставить frozen selected events через `INSERT … SELECT`.
5. Заполнить `sync_run_seq`, `sync_run_id`, immutable provenance и contract columns.
6. Проверить:
   - row count = expected;
   - distinct `event_id` = row count;
   - все rows `apply_status='applied'`;
   - transaction IDs входят в frozen prefix либо row — разрешённый initial snapshot;
   - checksum совпадает с frozen plan.
7. Записать фактический result в `sync_entity_results`.

Повтор task сначала удаляет только partition своего seq. Published partition удалять запрещено.

### 6.4 Current candidate task

Для затронутых business keys:

1. Взять latest candidate event по deterministic order `(source_ts, kafka_topic, kafka_partition, kafka_offset)`.
2. Для `c/r/u` сформировать current row из after/business values.
3. Для `d` сформировать soft-delete row с `is_deleted=true`, business values из before event и `deleted_at=source_ts`.
4. Вставить одну row на affected PK в partition seq.
5. Не копировать все неизменившиеся published rows в новый partition.
6. Stable/current-state SQL объединяет published runs + current candidate и rank'ит latest version.

Candidate validation выполняет `FINAL` для проверки физических duplicates, но public query не должна зависеть от merge timing.

### 6.5 PUBLISHED marker

`serving_control.published_runs` остаётся маленьким `ReplacingMergeTree(published_at)` keyed by seq. Marker содержит:

- seq/run ID;
- previous/target transaction ID;
- `publication_status='PUBLISHED'`;
- snapshot-completed flag;
- deterministic `published_at`;
- canonical compact JSON report.

Idempotent publish:

- marker отсутствует — вставить;
- effective marker полностью совпадает — no-op;
- marker seq существует с другим run ID/report hash/boundary — terminal invariant failure.

Planning/candidate/failed statuses в ClickHouse не вставляются.

### 6.6 Cleanup policy

- Unpublished candidate partitions удаляются при retry или terminal pre-publish cleanup.
- Published event/current partitions сохраняются без Stage E TTL: SCD2 использует event history.
- `gold_store` хранит минимум два последних PUBLISHED seq.
- Cleanup никогда не использует «max seq» без проверки PUBLISHED marker.

---

## 7. dbt Gold integration

### 7.1 Сохраняемый публичный интерфейс

Не создавать новые Gold business models. Использовать существующие:

- `dim_date`
- `dim_order_status`
- `dim_seller`
- `dim_customer_scd2`
- `dim_product_scd2`
- `fact_order_items`
- `mart_daily_revenue`
- `mart_monthly_arpu`

Их public grain и columns не меняются. Physical rows остаются в `gold_store.<model>` partitioned by `sync_run_seq`; `gold.<model>` остаётся stable view последнего PUBLISHED seq.

### 7.2 Airflow/dbt runtime wiring

- Airflow image копирует `dbt/olist_clickhouse` вместе с dependencies.
- Serving tasks используют отдельный `DBT_PROFILES_DIR` этого project; legacy DAG сохраняет свой profiles path до Stage L.
- Run context всегда передаёт положительный `sync_run_seq` и непустой `sync_run_id`.
- Candidate rebuild одного seq использует существующую `insert_overwrite` semantics.
- dbt invocation выполняется через программный `dbtRunner`, а не shell с динамически собранной строкой.
- Selector ограничен candidate Gold graph/tests; не запускать legacy Redshift/BigQuery project.

### 7.3 Последовательность dbt checks

1. До runtime: `dbt deps`, `dbt parse`, `dbt ls` с candidate vars.
2. После ClickHouse candidate: bounded `dbt show --limit` для critical staging/current relations.
3. `dbt build` candidate graph с explicit selector и vars.
4. Запустить declared structural/data/unit tests.
5. Дополнительно проверить:
   - каждая physical model содержит только expected candidate seq для этого build;
   - primary grain unique;
   - FK/relationship tests не создают orphans;
   - SCD2 windows не overlap;
   - facts/marts содержат только candidate seq;
   - до marker public Gold остаётся на предыдущем seq.
6. После marker проверить, что все восемь public views одновременно указывают на новый max PUBLISHED seq.

Новые tests добавлять только для значимых invariants: PK/grain, required relationships, SCD2 windows и publication boundary. Не добавлять `not_null` на каждый nullable business column.

### 7.4 Gold cleanup

После successful publication/maintenance вызвать существующий `cleanup_gold_partitions`:

- `keep_published=2`;
- сначала dry-run и validate exact partition list;
- затем actual drop;
- active candidate seq не удалять;
- cleanup до двух успешных published runs не выполнять.

---

## 8. Airflow DAGs

Использовать Airflow 3 `airflow.sdk` imports, TaskFlow API, dynamic task mapping и provider operator для Spark. В DAG module запрещены network/database calls и чтение secrets на parse time.

### 8.1 Общая конфигурация

| Параметр | Значение |
| --- | --- |
| Timezone | UTC |
| `catchup` | `False` |
| New DAG paused | `True` до первого successful manual sync |
| Mutation pool | `olist_serving_mutation`, 1 slot |
| Default retries | 2 |
| Retry delay | 60 seconds, exponential backoff |
| Sync DAG timeout | 30 minutes |
| Quality timeout | 15 minutes |
| Maintenance timeout | 90 minutes |
| Rebuild timeout | 90 minutes |
| `max_active_runs` | 1 на каждый DAG |

### 8.2 `olist_lakehouse_serving_sync`

- Schedule: `*/5 * * * *`.
- `max_active_tasks=4` для восьми mapped entity tasks.

Task graph и exact responsibilities:

1. `preflight`
   - live platform/streaming/ClickHouse/PostgreSQL checks;
   - никаких mutation.
2. `acquire_or_resume_run`
   - reconciliation;
   - lease acquire;
   - allocate или resume logical seq;
   - XCom: только seq/run ID.
3. `plan_boundary`
   - caught-up target;
   - strict transaction prefix;
   - frozen snapshots/counts;
   - authoritative plan сохраняется в PostgreSQL.
4. `route_plan`
   - `NOOP`, `WAITING`, `BLOCKED` или `MATERIALIZE`.
5. `finish_non_materializing_run`
   - terminal status/report без ClickHouse mutation.
6. `materialize_entity.expand(entity=ENTITY_NAMES)`
   - event/current partition replacement;
   - per-entity validation.
7. `validate_serving_candidate`
   - global counts, checksums, view invisibility.
8. `build_gold_candidate`
   - dbtRunner candidate build.
9. `validate_gold_candidate`
   - dbt tests + explicit publication checks.
10. `publish_marker`
    - final transaction revalidation;
    - deterministic marker insert.
11. `finalize_postgres`
    - cursor/state update.
12. `write_iceberg_report`
    - Spark finite idempotent MERGE.
13. `mark_success`
    - terminal status.
14. `release_lease`
    - teardown with `all_done`; не стирает evidence.

Failure callback:

- пишет fixed error class/code и task ID;
- не сохраняет traceback целиком в ledger;
- если marker уже существует, status становится `PUBLISHED_PENDING_FINALIZATION`, а не FAILED;
- lease остаётся recoverable по expiry, teardown пытается корректно освободить её.

### 8.3 `olist_lakehouse_serving_quality`

- Schedule: `7 * * * *`.
- Read-only проверки:
  - PG cursor = latest ClickHouse marker;
  - marker/report hash consistency;
  - latest public current/gold seq;
  - no duplicate effective PK/event ID;
  - event/current/gold row counts;
  - no stale unpublished candidate;
  - next transaction boundary status;
  - source→serving lag;
  - latest maintenance freshness.
- При active mutation lease не читает partially rebuilt DB; завершает run как skipped/WAITING и не создаёт false alert.

### 8.4 `olist_lakehouse_iceberg_maintenance`

- Schedule: `0 3 * * *`.
- Захватывает mutation lease.
- Получает inventory из `table_specs.py`.
- Dynamic mapping выполняется последовательно (`max_active_tis_per_dag=1`) из-за локального Spark worker.
- На table выполняет procedures в порядке:
  1. `rewrite_data_files`;
  2. `rewrite_manifests`;
  3. `expire_snapshots`;
  4. `remove_orphan_files`.
- Каждый procedure имеет отдельный audit result.
- После Iceberg procedures запускается Gold cleanup.

### 8.5 `olist_clickhouse_rebuild`

- `schedule=None`.
- Первый task проверяет `dag_run.conf.confirm_destructive is True`.
- Freeze Iceberg plan происходит до удаления ClickHouse databases.
- Пересоздаются только `serving_cdc`, `serving_control`, `gold_store`, `gold`.
- Далее используется тот же entity/dbt/publication code path с `operation_type=REBUILD`.
- Не использовать отдельный альтернативный SQL path, который может разойтись с sync.

### 8.6 Airflow image/init

- Добавить совместимый `apache-airflow-providers-apache-spark` в locked dependencies.
- Добавить Spark 4.1.3 client и project JAR в Airflow image через воспроизводимый build stage.
- Build order обязан гарантировать, что Spark artifact существует до Airflow image.
- One-shot `airflow-init` выполняет DB migration и создаёт pool `olist_serving_mutation`.
- One-shot создаёт non-secret connection `spark_lakehouse` со значением `spark://spark-master:7077?deploy-mode=client`; все `SparkSubmitOperator` используют ровно `conn_id='spark_lakehouse'`.
- Airflow runtime использует `LocalExecutor` как сейчас.
- REST API authentication использует existing Simple Auth secret/file; token хранится только в памяти CLI.
- Не обращаться к Airflow metadata tables напрямую.

---

## 9. Publication и failure recovery

### 9.1 Точный порядок publication

1. В PostgreSQL сохранить final canonical report и один `published_at`.
2. Проверить previous marker/cursor.
3. Вставить ClickHouse PUBLISHED marker.
4. Считать marker обратно и сравнить все immutable fields/hash.
5. В одной PostgreSQL transaction:
   - обновить `runtime_state` cursor;
   - перевести run в `PUBLISHED_PENDING_FINALIZATION`.
6. Выполнить Iceberg `MERGE` report по `sync_run_id`.
7. Перевести run в `SUCCEEDED`.
8. Освободить lease.

### 9.2 Failure matrix

| Точка сбоя | Видимость | Повтор |
| --- | --- | --- |
| До plan commit | Старый run | Создать/возобновить plan |
| После plan, до first entity | Старый run | Тот же seq |
| В середине entity tasks | Старый run | Drop/rebuild partitions того же seq |
| После entities, до dbt | Старый run | Validate/rebuild candidate, тот же seq |
| После dbt, до marker | Старый run | Rebuild candidate/dbt того же seq |
| После marker, до PG cursor | Новый run видим | Reconcile marker, materialization запрещена |
| После PG cursor, до Iceberg report | Новый run видим | Только idempotent report MERGE |
| После report, до success status | Новый run видим | Mark success/release |
| Потеря ClickHouse | Serving недоступен | Только guarded rebuild |
| Потеря control schema | Marker может быть видим | Reconstruct из marker/report; при CH loss rebuild |

### 9.3 Failpoints

Добавить test-only failpoints, disabled by default:

- `after_plan_commit`;
- `after_first_entity_materialized`;
- `after_all_entities_validated`;
- `after_dbt_before_marker`;
- `after_marker_before_postgres`;
- `after_postgres_before_iceberg_report`.

Failpoint name допускается только из fixed allowlist, не активируется произвольным shell/code payload и отражается в sanitized report.

---

## 10. Spark finite operations и maintenance security

### 10.1 Config split

Текущий `SparkPlatformConfig` требует checkpoint credentials для любого Spark job. Разделить его на:

- `SparkCatalogConfig`: Polaris REST catalog, warehouse, OAuth principal, vended credentials, S3 endpoint/region, redaction;
- `SparkCheckpointConfig`: строго `s3a://olist-checkpoints` и static MinIO checkpoint credentials;
- streaming mode = catalog + checkpoint;
- maintenance mode = только catalog.

Renderer принимает exact `--mode streaming|maintenance`. Неизвестный mode — configuration error.

Maintenance properties не должны содержать:

- `spark.olist.checkpoint.root`;
- `fs.s3a.access.key/secret.key` checkpoint user;
- любой path внутри `olist-checkpoints`.

### 10.2 `LakehouseOpsMain`

Один Scala entry point с subcommands:

```text
record-serving-report --input-file <0600-json>
maintenance --run-id <id> --procedure <allowlisted> --table <fqtn> --options-file <0600-json>
```

Требования:

- table сверяется с migration/table-spec inventory;
- procedure — только fixed allowlist;
- options schema валидируется до SparkSession mutation;
- output — один sanitized JSON object;
- report/maintenance writes используют Iceberg MERGE key;
- temporary files удаляются в `finally`;
- secrets не передаются в application args.

### 10.3 Maintenance defaults

| Procedure | Default |
| --- | --- |
| `rewrite_data_files` | Target из table property `write.target-file-size-bytes`, иначе 134217728 bytes (128 MiB) |
| `rewrite_manifests` | После data-file rewrite |
| `expire_snapshots` | Older than 7 days, retain last 20 |
| `remove_orphan_files` | Older than 72 hours, explicit table location only |

Orphan interval не сокращать: слишком раннее удаление может удалить файлы незавершённой записи — [Iceberg maintenance](https://iceberg.apache.org/docs/latest/maintenance/).

Каждый result в `audit.maintenance_runs` содержит run ID, procedure, namespace/table, status, timestamps, sanitized options/result/error.

Scheduled DAG вызывает `rewrite_data_files` для каждой поддерживаемой table и принимает штатный Iceberg no-op как success. Никакие внешние эвристики не решают, пропустить ли процедуру: необходимость rewrite определяет сам Iceberg action с указанным target size.

---

## 11. Rebuild contract

### 11.1 Guards

- CLI без `--yes` возвращает code 1 до обращения к Airflow.
- DAG без exact boolean `confirm_destructive=true` завершается до lease/mutation.
- В report перечисляются ровно четыре target databases.
- Любой target вне allowlist — fatal configuration error.

### 11.2 Алгоритм

1. Проверить Iceberg catalog и required tables.
2. Захватить global lease.
3. Выполнить reconciliation и выделить/resume rebuild seq.
4. Заморозить full plan: initial applied snapshot rows + maximal COMPLETE transaction prefix до текущей boundary.
5. Проверить counts/snapshots до destructive step.
6. Drop/recreate только четыре derived ClickHouse databases.
7. Применить актуальный ClickHouse DDL/catalog bootstrap.
8. Materialize полный event ledger по frozen snapshots.
9. Materialize current rows.
10. Выполнить dbt build/tests.
11. Вставить initial rebuilt PUBLISHED marker.
12. Обновить PostgreSQL cursor и Iceberg report.
13. Выполнить serving quality checks.

### 11.3 Запрещённые действия rebuild

- `docker compose down -v`;
- reset MySQL/Kafka/Polaris/MinIO;
- удаление Iceberg namespaces/tables/data files;
- удаление Spark checkpoints;
- mutation source data;
- reuse unfrozen «latest» snapshots после начала rebuild.

---

## 12. CLI contract

### 12.1 `sync-serving`

```text
python scripts/cdc/local_lab.py sync-serving \
  [--run-id <id>] [--timeout <seconds>]
```

Поведение:

1. Проверяет/start'ит required profiles без reset.
2. Ждёт Airflow health и наличие DAG.
3. Получает short-lived bearer token.
4. POST'ит `/api/v2/dags/olist_lakehouse_serving_sync/dagRuns`.
5. Duplicate run ID присоединяется к существующему DagRun.
6. Poll'ит stable REST API до terminal state.
7. Читает authoritative result через serving report API/helper, не Airflow metadata SQL.
8. После первого successful/no-op run, когда уже существует published snapshot, PATCH'ит три scheduled DAG в unpaused state и устанавливает `schedules_activated_at`.
9. Если `schedules_activated_at` уже задан, deliberate operator pause не отменяется.

Использовать официальный Airflow API contract: [Stable REST API](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html).

### 12.2 `rebuild-serving`

```text
python scripts/cdc/local_lab.py rebuild-serving --yes \
  [--run-id <id>] [--timeout <seconds>]
```

Передаёт `confirm_destructive=true`, ждёт DAG и возвращает rebuilt report.

### 12.3 `run-maintenance`

```text
python scripts/cdc/local_lab.py run-maintenance \
  [--run-id <id>] [--timeout <seconds>]
```

Default — полный inventory/all procedures. Не добавлять произвольные SQL/procedure args в public CLI Stage E.

### 12.4 Status/validate

```text
status --require platform|streaming|serving
validate --scope platform|streaming|serving
```

`status --require serving` проверяет:

- Compose long-running/one-shot inventory;
- Airflow API и четыре DAG;
- PostgreSQL migration, lease, latest run/cursor;
- ClickHouse databases/tables/views/catalog;
- marker/cursor/report consistency;
- current/gold view mapping;
- stale unpublished candidates;
- latest quality/maintenance status.

`validate --scope serving` read-only. Он не запускает sync, rebuild, maintenance или cleanup.

### 12.5 JSON result и exit codes

Успешный sync result содержит:

```json
{
  "command": "sync-serving",
  "status": "succeeded",
  "dag_run_id": "manual__...",
  "sync_run_id": "sync-00000000000000000042",
  "sync_run_seq": 42,
  "is_noop": false,
  "previous_transaction_id": "...",
  "target_transaction_id": "...",
  "expected_event_count": 7,
  "materialized_event_count": 7,
  "published_at": "...Z",
  "schedules_activated": true
}
```

Exit codes:

- `0`: READY, SUCCEEDED или NOOP;
- `2`: WAITING, BLOCKED или NOT_CAUGHT_UP;
- `1`: execution, configuration или invariant failure.

`final-parity` остаётся deferred до Stage F; исправить его текущую ошибочную phase label E на F.

---

## 13. Observability

### 13.1 Exporter

Добавить low-cardinality serving exporter, который read-only собирает:

- PostgreSQL run/cursor/lease;
- ClickHouse marker/row counts;
- next Iceberg transaction boundary;
- Iceberg snapshot/file statistics;
- latest maintenance report;
- component health.

Exporter возвращает failure metric и продолжает отдавать последние safe observations при временной недоступности одного backend. Он не логирует queries с secrets и не экспортирует business values.

### 13.2 Метрики

| Metric | Labels |
| --- | --- |
| `olist_serving_sync_runs_total` | bounded `result` |
| `olist_serving_sync_duration_seconds` | none/result histogram |
| `olist_serving_last_attempt_timestamp_seconds` | none |
| `olist_serving_last_publication_timestamp_seconds` | none |
| `olist_serving_source_to_publication_lag_seconds` | none |
| `olist_serving_next_boundary_status` | bounded `status` |
| `olist_serving_unpublished_candidate_age_seconds` | none |
| `olist_serving_watermark_drift` | none, 0/1 |
| `olist_serving_event_rows` | `entity` |
| `olist_serving_current_rows` | `entity` |
| `olist_serving_gold_rows` | `model` |
| `olist_iceberg_snapshots` | `table` |
| `olist_iceberg_data_files` | `table` |
| `olist_iceberg_average_data_file_bytes` | `table` |
| `olist_iceberg_maintenance_last_success_timestamp_seconds` | `procedure` |

Запрещённые labels: transaction ID, event ID, run ID, error message, topic offset.

### 13.3 Alerts

| Alert | Условие |
| --- | --- |
| `ServingSyncStalled` | Новая COMPLETE boundary есть, успешного/no-op sync > 10 минут |
| `ServingRejectedBoundary` | Следующая непубликованная transaction REJECTED |
| `ServingPublicationDrift` | PG cursor и CH marker расходятся > 2 минут |
| `ServingCandidateStale` | Unpublished nonterminal candidate > 20 минут |
| `ServingMaterializationMismatch` | expected != materialized |
| `ServingQualityFailed` | Последний hourly quality DAG failed |
| `IcebergMaintenanceStale` | Нет daily success > 36 часов |
| `IcebergSmallFiles` | `data_files > 100` либо одновременно `data_files > 10` и average size `< 1048576` bytes в течение 10 минут |
| `ServingComponentUnavailable` | ClickHouse/Airflow/Spark/exporter unavailable |

### 13.4 Grafana dashboard

Один Stage E dashboard должен содержать:

- component health;
- Kafka/Silver/serving offsets и lag;
- current run state/duration;
- last published transaction/age без high-cardinality label;
- event/current counts по entity;
- Gold counts по model;
- candidate visibility/drift;
- maintenance duration/status;
- Iceberg snapshot/file count/average size;
- последние active alerts.

Prometheus scrape config и Compose services должны совпадать: dangling targets запрещены. Legacy dashboards/rules сохраняются до Stage L, но не должны ломать health нового profile.

---

## 14. Security и secret handling

- Все passwords/OAuth credentials читаются только из `*_FILE`.
- Dynamic command strings не содержат secrets.
- Spark properties file создаётся `0600` и удаляется после task.
- Airflow XCom/report содержит только IDs/counts/boundaries/snapshot IDs.
- PostgreSQL `error_details_json` хранит fixed code/class/task ID, не raw exception/payload.
- ClickHouse `report_json` canonical и sanitized.
- Maintenance principal имеет warehouse table write, но не checkpoint bucket access.
- ClickHouse DataLakeCatalog principal остаётся read-only к Iceberg.
- Logs проходят существующую redaction regex и отдельные negative tests.
- API bearer token живёт только в памяти CLI и не записывается в JSON result.

---

## 15. Тестовая стратегия

### 15.1 Fast/static CI

Обязательные checks:

- `uv lock --check`;
- Python lint/format/type/unit tests relevant paths;
- Scala compile, scalafmt check и unit tests;
- generated schema/contracts `--check`;
- Compose config всех profiles;
- PostgreSQL migration application/idempotency/grants;
- ClickHouse DDL and learning tests;
- Airflow DAG import/errors/warnings/graph assertions;
- dbt deps/parse/ls с candidate vars;
- Prometheus `promtool check config/rules`;
- Grafana provisioning JSON/YAML validation;
- `git diff --check`.

Не запускать весь dbt project без selector; Stage E CI ограничивается `olist_clickhouse` candidate graph.

### 15.2 Unit/contract matrix

#### PostgreSQL

- sequence monotonicity и допустимые gaps;
- allowed/forbidden state transitions;
- concurrent acquire: один winner;
- lease heartbeat/expiry/steal;
- resume того же seq;
- marker-ahead reconciliation;
- cursor-ahead fail closed;
- reconstruction from marker/report;
- JSON/error redaction.

#### Boundary planner

- initial snapshot only;
- snapshot + complete prefix;
- single/multi-entity transaction;
- multiple consecutive COMPLETE;
- OPEN first/inside range;
- REJECTED first/inside range;
- COMPLETE после REJECTED не включается;
- declared count mismatch;
- collection mismatch/unknown collection;
- transaction order gap;
- missing progress snapshot;
- stale progress vs caught-up contradiction;
- no-op;
- status changed to REJECTED immediately before marker.

#### ClickHouse

- event idempotency;
- partition retry cleanup;
- composite PK current ranking;
- delete visibility;
- candidate invisible before marker;
- previous published row survives physical merge unpublished candidate;
- marker idempotency/conflict;
- all eight Gold views switch only after marker.

#### dbt

- positive run context required;
- each model grain unique;
- required relationships;
- SCD2 no overlap/current window rules;
- fact grain;
- candidate partition overwrite;
- public view previous/new publication boundary.

#### Airflow

- no top-level network access;
- exact schedule/timezone/catchup/retries/timeouts;
- dynamic map exactly eight entities;
- task dependency graph;
- failure callback before/after marker;
- XCom payload restricted to small IDs;
- rebuild conf guard;
- first-sync unpause idempotency;
- manual operator pause preserved after activation.

#### Maintenance/rebuild

- table/procedure allowlists;
- root/bucket/checkpoint path rejection;
- exact retention defaults;
- audit MERGE retry;
- rebuild target database allowlist;
- rebuild leaves MySQL/Kafka/Iceberg/checkpoints untouched.

### 15.3 Bounded serving component test

Отдельный CI/manual job использует small fixture и поднимает только необходимые profiles:

1. Clean platform/bootstrap.
2. Initial snapshot и real caught-up barrier.
3. Initial serving sync.
4. One multi-table COMPLETE transaction.
5. One NOOP sync.
6. Failpoint before marker + same-seq retry.
7. Failpoint after marker + metadata-only retry.
8. One targeted maintenance procedure.
9. Serving status/validate.

Этот job не заменяет Stage V: не выполняет полный CRUD/restart/additive-schema сценарий.

### 15.4 Clean-domain Stage E acceptance

Командная последовательность:

```powershell
python scripts/cdc/local_lab.py reset --yes
python scripts/cdc/local_lab.py bootstrap --run-id stage_e_clean
python scripts/cdc/local_lab.py start-streaming
python scripts/cdc/local_lab.py wait-caught-up --timeout 1200
python scripts/cdc/local_lab.py sync-serving --run-id stage_e_initial --timeout 1800
python scripts/cdc/local_lab.py status --require serving
python scripts/cdc/local_lab.py validate --scope serving
python scripts/cdc/local_lab.py run-maintenance --run-id stage_e_maintenance --timeout 5400
python scripts/cdc/local_lab.py rebuild-serving --yes --run-id stage_e_rebuild --timeout 5400
python scripts/cdc/local_lab.py validate --scope serving
```

После initial sync:

- fixture manifest counts совпадают в Silver/current/serving/gold;
- PG cursor, CH marker и Iceberg report совпадают;
- candidate partitions опубликованы одним seq;
- три scheduled DAG unpaused, rebuild manual;
- public views возвращают expected rows;
- no secrets в reports/logs.

Дополнительно выполнить transaction/rejected/failpoint scenarios из acceptance harness.

---

## 16. Validation report

Создать `docs/reports/mysql-spark-iceberg-stage-e-validation.md` только после фактического выполнения.

Report должен содержать:

- implementation commit SHA и dirty-state statement;
- pinned component versions;
- clean reset/bootstrap evidence;
- E0 query inventory, captured targets и snapshot coverage;
- initial/no-op/transaction sync summaries;
- PG/CH/Iceberg seq and boundary equality;
- candidate-before-marker invisibility evidence;
- before-marker и after-marker failpoint recovery;
- dbt command/selector и test totals;
- maintenance procedures/results;
- rebuild scope и post-rebuild parity counts;
- Prometheus targets/alerts/dashboard evidence;
- secret-redaction/checkpoint-denial evidence;
- final `status --require serving` и `validate --scope serving` JSON;
- итоговый `PASS|FAIL`.

Stage E можно отметить завершённой только при `PASS` и отсутствии unresolved blockers.

---

## 17. Порядок реализации и контрольные точки

### E0 — J2 repair

- Полный Silver normalization/audit/progress/transaction contract.
- Реальный offset-based caught-up.
- Stop/go tests.

**Gate**: serving code не начинает materialization без E0 PASS.

### E1 — Contracts и control schema

- Синхронизировать normative docs.
- Добавить PostgreSQL migration/repository/state machine/lease/reconciliation.

**Gate**: migration, concurrency и recovery tests PASS.

### E2 — ClickHouse atomic candidate storage

- Исправить current partitions/order.
- Добавить registry и event/current materializer.
- Добавить marker publisher.

**Gate**: unpublished merge regression и idempotent retry PASS.

### E3 — dbt candidate integration

- Airflow image/project wiring.
- Candidate selector/build/tests/publication checks.

**Gate**: candidate полностью невидим до marker, public Gold переключается после marker.

### E4 — Airflow serving sync

- Init/pool/Spark provider.
- Sync DAG и crash finalization.

**Gate**: initial/no-op/before-marker/after-marker component tests PASS.

### E5 — Quality, maintenance и rebuild

- Три дополнительных DAG.
- Spark config split и `LakehouseOpsMain`.
- Safe cleanup/rebuild.

**Gate**: no checkpoint access, maintenance audit и derived-only rebuild PASS.

### E6 — CLI и observability

- REST orchestration, status/validate, activation semantics.
- Exporter, metrics, alerts, dashboard, runbooks.

**Gate**: CLI contract и monitoring validation PASS.

### E7 — Clean-domain acceptance

- Полная Stage E command sequence.
- Validation report.
- Roadmap/status update.

**Gate**: report `PASS`; после этого разрешена Stage V.

---

## 18. Ожидаемая карта изменений

Исполнитель следует этой карте имён, чтобы не создавать альтернативные packages/DAG IDs/migrations.

### 18.1 Документы

- Этот файл — единственный детальный active implementation plan Stage E.
- `docs/plans/lakehouse/active/serving-cutover.md` — ссылка и high-level gate, без дублирования деталей.
- Contracts в `docs/plans/lakehouse/contracts/` — нормативные уточнения table/CLI/runtime/CI semantics.
- Новые runbooks:
  - `docs/runbooks/lakehouse-serving-sync.md`;
  - `docs/runbooks/lakehouse-serving-rejected-boundary.md`;
  - `docs/runbooks/lakehouse-iceberg-maintenance.md`;
  - `docs/runbooks/lakehouse-clickhouse-rebuild.md`.
- Итоговый report: `docs/reports/mysql-spark-iceberg-stage-e-validation.md`.

### 18.2 J2 repair / Spark streaming

Refactor existing:

- `streaming/spark/scala/src/main/scala/com/olist/mds/spark/app/BronzeMain.scala`;
- `streaming/spark/scala/src/main/scala/com/olist/mds/spark/app/SilverMain.scala`;
- `streaming/spark/scala/src/main/scala/com/olist/mds/spark/bronze/BronzeBatchWriter.scala`;
- `streaming/spark/scala/src/main/scala/com/olist/mds/spark/silver/SilverBatchWriter.scala`;
- `streaming/spark/scala/src/main/scala/com/olist/mds/spark/supervisor/StatusPublisher.scala`;
- `streaming/spark/scala/src/main/scala/com/olist/mds/spark/operational/LakehouseStatusMain.scala`.

Создать packages/classes:

- `silver/EntityBatchProcessor.scala` — общий decode/validation/commit flow;
- `silver/SilverProgressWriter.scala` — progress MERGE/snapshot IDs;
- `silver/IcebergCommitCoordinator.scala` — fair per-audit-table locks;
- `schema/SchemaArchiveWriter.scala` — `capture_avro_schemas`;
- `transaction/TransactionBatchWriter.scala` — BEGIN/END validation и transaction states;
- `operational/LakehouseOpsMain.scala` и `app/LakehouseOpsMain.scala` — finite report/maintenance entry point.

Не создавать отдельные восемь copy-paste writers; entity-specific rules остаются в существующем entity registry/modules.

### 18.3 PostgreSQL/control package

- `infra/control-postgres/initdb/005_create_serving_control_tables.sql` — schema/sequence/tables/indexes/singleton row.
- `infra/control-postgres/initdb/999_grant_control_role.sql` — serving DML/sequence grants.
- `scripts/serving/__init__.py`.
- `scripts/serving/models.py` — enums/dataclasses/canonical report/checksum.
- `scripts/serving/control.py` — repository, state machine, lease и reconciliation.
- `scripts/serving/boundary.py` — caught-up target и strict transaction planner.
- `scripts/serving/entities.py` — единственный `ServingEntitySpec` registry.
- `scripts/serving/clickhouse.py` — materialization/validation/marker/rebuild helpers.
- `scripts/serving/dbt_runner.py` — bounded programmatic dbt invocation.
- `scripts/serving/airflow_api.py` — token/trigger/poll/unpause client.
- `scripts/serving/metrics.py` — read-only Prometheus exporter.

Public CLI остаётся в `scripts/cdc/local_lab.py`; он вызывает package API и не содержит вторую реализацию planner/materializer.

### 18.4 ClickHouse

- Изменить `infra/clickhouse/lakehouse/004_create_current_version_tables.sql`.
- `infra/clickhouse/lakehouse/005_create_stable_current_views.sql` сохраняет текущие public columns/ranking; его SQL не переписывать, а проверить новым regression после изменения physical partitioning.
- Создать `infra/clickhouse/lakehouse/tests/002_unpublished_current_isolation.sql` для обязательного published/unpublished/OPTIMIZE regression; существующий learning test оставить отдельным.
- `init.sh` остаётся единственным ordered DDL entry point и используется sync bootstrap/rebuild.

### 18.5 Airflow и images

- `airflow/dags/olist_lakehouse_serving.py` определяет только sync и quality DAG.
- `airflow/dags/olist_lakehouse_maintenance.py` определяет только maintenance и rebuild DAG.
- Общие business/control функции импортируются из `scripts.serving`; DAG files не содержат SQL builders.
- `docker/airflow/Dockerfile` копирует `dbt/olist_clickhouse`, Spark client/JAR и locked provider.
- `docker/airflow/load-env-and-run.sh` сохраняет file-secret loading; dynamic secrets в environment values не разворачивать.
- `compose.yaml` добавляет `airflow-init`, serving exporter и exact profile dependencies/healthchecks.

### 18.6 Spark config и build

- Refactor `streaming/spark/platform/config.py` на catalog/checkpoint config.
- Расширить `streaming/spark/platform/render_spark_properties.py` exact mode flag.
- `docker/spark/run-with-platform-config.sh` явно вызывает streaming mode.
- Airflow SparkSubmitOperator явно использует maintenance mode properties.
- `streaming/spark/scala/build.sbt` получает только необходимые compile/test dependencies; runtime Spark/Iceberg artifacts остаются Provided.

### 18.7 dbt

- Существующие SQL models в `dbt/olist_clickhouse/models/` изменять только при доказанном test failure.
- Сохранить `macros/run_context.sql`, `source_state.sql`, `cleanup_gold_partitions.sql` как единый candidate/publication interface; изменения сопровождаются downstream `dbt ls` impact check.
- Создать `dbt/olist_clickhouse/selectors.yml` с selector `serving_candidate`, включающим восемь physical models, ancestors и их tests.
- Airflow запускает только selector `serving_candidate` с explicit vars.

### 18.8 Observability

- `observability/prometheus/prometheus.yml` — exact active scrape inventory.
- `observability/prometheus/rules/lakehouse-serving-alerts.yml` — Stage E alerts.
- `observability/prometheus/rules/lakehouse-serving-recording.yml` — bounded recording rules.
- `observability/grafana/provisioning/dashboards/lakehouse.yml` — provider entry.
- `observability/grafana/dashboards/lakehouse-serving.json` — dashboard.
- Legacy files остаются на месте до Stage L, но активные rules не ссылаются на отсутствующие services/runbooks.

### 18.9 Tests и CI

- Python unit tests: `tests/serving/` с отдельными files для control, boundary, ClickHouse SQL, CLI/API, metrics/redaction.
- Scala tests расширяют существующие Bronze/Silver suites и добавляют transaction/progress/ops suites.
- Airflow contract tests проверяют два новых DAG modules через существующий `scripts/ci/check_airflow_dag_imports.py`.
- ClickHouse runtime checks добавляются в `scripts/ci/` как bounded Stage E checks, а не в legacy warehouse scripts.
- `.github/workflows/ci.yml` получает отдельные named steps/jobs `serving-static` и `serving-component`; полный Candidate E2E остаётся Stage V/manual gate.

---

## 19. Definition of Done

- [ ] E0 J2 repair прошёл отдельный stop/go gate.
- [ ] `olist_control.serving` содержит только control metadata и восстанавливается из marker/report.
- [ ] Current candidates физически изолированы по `sync_run_seq`.
- [ ] `olist_lakehouse_serving_sync` публикует только maximal COMPLETE prefix.
- [ ] OPEN/REJECTED transaction не пересекается.
- [ ] Initial snapshot публикуется только целиком.
- [ ] Candidate невидим до marker.
- [ ] Retry до marker использует тот же seq и не создаёт duplicates.
- [ ] Retry после marker только финализирует metadata.
- [ ] Все восемь dbt Gold models/tests встроены в candidate flow.
- [ ] Первый successful manual sync активирует три schedules ровно один раз.
- [ ] Maintenance использует Airflow Polaris principal без checkpoint access.
- [ ] `rebuild-serving --yes` восстанавливает только derived ClickHouse databases.
- [ ] `status --require serving` и `validate --scope serving` возвращают READY на clean domain.
- [ ] Prometheus/Grafana/alerts работают без dangling targets.
- [ ] Validation report имеет статус PASS.
- [ ] Legacy-контур не удалён и Stage V остаётся отдельной следующей стадией.

---

## 20. Связанные документы

- [Дорожная карта миграции](../../mysql-spark-iceberg-lakehouse-migration.md)
- [Операционный cutover-план E → V → L → F](serving-cutover.md)
- [Контракт Serving & Recovery](../contracts/serving-and-recovery.md)
- [Контракт Spark Structured Streaming](../contracts/spark-streaming.md)
- [Контракт Iceberg data model](../contracts/iceberg-data-model.md)
- [Контракт architecture/runtime](../contracts/architecture-and-runtime.md)
- [Контракт validation/CI](../contracts/validation-and-ci.md)
