# Детальный план Stage V: Candidate E2E Validation

- **Статус**: Completed / Frozen — clean V0–V10 PASS.
- **Execution commit**: `e113c552cca990636f426b827456a77ddc9d594b` (`dirty=false`).
- **Run ID**: `stage_v_clean_e113c55`.
- **Evidence**: `data/stage-v-evidence/stage_v_clean_e113c55/`.
- **Цель**: доказать на одном чистом и изолированном стенде, что кандидат
  `MySQL -> Debezium -> Kafka -> Spark Bronze/Silver -> Iceberg -> ClickHouse -> dbt Gold`
  корректно обрабатывает initial snapshot, транзакционный CRUD, tombstone,
  одновременный перезапуск Bronze/Silver, аддитивную nullable-схему и полное
  восстановление ClickHouse только из Iceberg.
- **Предыдущая стадия**: Stage E, статус `PASS` в
  [отчёте Stage E](../../../reports/mysql-spark-iceberg-stage-e-validation.md).
- **Родительский порядок стадий**:
  [serving-cutover.md](../active/serving-cutover.md), строго `E -> V -> L -> F`.
- **Порядок авторитетности**: действующие контракты из
  `docs/plans/lakehouse/contracts/` -> этот план -> фактические machine-readable
  evidence -> итоговый validation report.

---

## 1. Ожидаемый результат

Stage V завершается только одним из трёх итогов:

| Итог | Значение |
| --- | --- |
| `PASS` | Все ворота V0-V10 пройдены в одном clean-domain run, доказательства полны, можно начинать Stage L. |
| `FAIL` | Кандидат нарушил проверяемый инвариант; Stage L запрещена. |
| `BLOCKED` | Нельзя получить достоверный результат из-за дефекта Stage E, среды или validation harness; Stage L запрещена. |

Успешный результат — не просто нулевые exit codes. Агент обязан доказать:

1. исходные 79 бизнес-записей и 6 геопозиций дошли до целевых таблиц;
2. три CRUD-транзакции дали ровно 10 business CDC events;
3. delete дал одну delete envelope и один следующий tombstone;
4. после перезапуска чекпоинты продолжены, а не созданы заново;
5. `event_id` уникальны, бизнес-ключи и значения совпадают построчно;
6. опубликована только завершённая транзакционная граница;
7. PostgreSQL cursor, ClickHouse marker и Iceberg report описывают один run;
8. стабильные `serving_cdc.*_current` и `gold.*` не видят unpublished data;
9. nullable additive evolution не останавливает совместимый поток;
10. ClickHouse полностью восстанавливается из Iceberg без чтения MySQL/Kafka;
11. после rebuild канонические manifests до и после совпадают;
12. legacy-компоненты не удалены и Stage F не запускалась.

---

## 2. Scope и явные запреты

### 2.1 В scope

- Реализация воспроизводимого Stage V acceptance harness.
- Validation-only SQL fixtures и read-only probes для всех слоёв.
- Один полный прогон на новом Compose project и чистых volumes.
- Initial snapshot, deterministic CRUD, tombstone и restart drill.
- Публикация serving candidate и проверка dbt candidate graph.
- Контролируемая аддитивная nullable-эволюция схемы.
- Guarded ClickHouse rebuild и построчное сравнение manifests.
- Сбор sanitized evidence и создание отчёта Stage V.
- Исправление исключительно дефектов самого validation harness до начала
  финального clean run.

### 2.2 Вне scope

- Удаление PostgreSQL legacy, NiFi, старых DAGs или иных компонентов Stage L.
- Запуск final parity или изменение его контракта — это Stage F.
- Изменение Kafka retention, topology, partition count или primary keys.
- Проверка несовместимой schema evolution: rename, drop, type change,
  non-nullable column без default.
- Performance/SLO benchmark и длительный soak test.
- Maintenance, не необходимый для rebuild-проверки.
- Ручное исправление данных напрямую в Iceberg или ClickHouse.
- Ослабление контрактов, тестов, lint/type rules или acceptance thresholds ради
  получения `PASS`.

### 2.3 Запрещённые действия агента

- Не выполнять `docker compose down -v` напрямую. Единственная допустимая
  очистка — `python scripts/cdc/local_lab.py reset --yes` после проверки
  `COMPOSE_PROJECT_NAME`.
- Не удалять отдельные authoritative volumes, checkpoint paths, Iceberg
  snapshots или строки control ledger.
- Не запускать `sync-serving`, `rebuild-serving` и maintenance параллельно.
- Не продолжать acceptance run после нарушения инварианта. Сначала сохранить
  evidence, классифицировать причину и завершить run как `FAIL`/`BLOCKED`.
- Не считать повторный прогон отдельного упавшего шага достаточным для `PASS`.
  После исправления production-кода обязателен новый полный clean-domain run.
- Не печатать содержимое secret files, connection strings, bearer tokens или
  пароли в командной строке, stdout, JSON и Markdown.
- Не создавать отчёт со статусом `PASS` до фактического завершения V10.

---

## 3. Исходная точка и обязательная сверка Stage E

### 3.1 Что уже существует

- Детерминированный small fixture:
  `tests/fixtures/olist_small/olist_small.zip`.
- Source oracle:
  `tests/fixtures/olist_small/source_profile_small.json`.
- CRUD fixture:
  `tests/spark_integration/fixtures/wave2_crud.sql`.
- Lifecycle CLI: `scripts/cdc/local_lab.py` с командами `reset`, `bootstrap`,
  `start-streaming`, `wait-caught-up`, `status`, `validate`, `sync-serving` и
  `rebuild-serving`.
- Нормативные контракты:
  [Spark streaming](../contracts/spark-streaming.md),
  [Iceberg data model](../contracts/iceberg-data-model.md),
  [Serving and recovery](../contracts/serving-and-recovery.md) и
  [Validation and CI](../contracts/validation-and-ci.md).
- Runbooks serving/rebuild в `docs/runbooks/`.

### 3.2 Почему Stage E `PASS` перепроверяется

Stage V не переоткрывает Stage E без причины, но обязана проверить свой entry
gate на текущем execution commit. Приложенные к задаче логи показывают, что на
одном из предыдущих состояний дерева pre-commit изменял whitespace/EOF/format,
после чего ещё сообщал ruff и pyright errors. Эти логи не являются свежим
результатом и не меняют статус Stage E автоматически, однако запрещено начинать
дорогой E2E-прогон без нового зелёного V0.

Агент также обязан проверить, что текущая реализация действительно выполняет
контракт, а не только имеет нужные имена команд. В частности, свежий аудит
должен подтвердить следующее:

- boundary planner получает реальные `audit.mysql_transactions`, progress и
  Iceberg snapshot IDs, а не пустые collections;
- materializer фильтрует `*_changes` по frozen boundary конкретного run;
- `*_current_versions` строятся по последней версии каждого business key и
  сохраняют реальные Kafka offsets, delete state и row hashes;
- `status --require serving` проверяет marker/cursor/report, DAG inventory,
  stale candidates и quality state, а не только HTTP health;
- `validate --scope serving` выполняет заявленные read-only serving checks;
- CLI возвращает полный authoritative result contract из Stage E, включая
  `sync_run_id`, границы, event counts и publication metadata;
- rebuild не использует MySQL, Kafka и Spark checkpoints как источник данных.

Если любой пункт не подтверждён, результат V0 — `BLOCKED_BY_E_REGRESSION`.
Исправление оформляется как устранение дефекта Stage E, после чего V0 и весь
clean-domain run запускаются заново. Агент не имеет права подменять отсутствующую
production-семантику логикой validation harness.

---

## 4. Идентичность прогона и evidence contract

### 4.1 Изоляция

Перед mutating-командами агент один раз задаёт:

```powershell
$env:COMPOSE_PROJECT_NAME = "olist_stage_v"
$StageVRunId = "stage_v_<UTC timestamp>_<short commit>"
$StageVEvidence = "data/stage-v-evidence/$StageVRunId"
```

Требования:

- `COMPOSE_PROJECT_NAME` должен быть ровно `olist_stage_v`;
- рядом не должен исполняться другой Stage V run;
- все mutating run IDs начинаются с `$StageVRunId`;
- execution commit SHA фиксируется до `reset`;
- tracked worktree чистый; допускаются только ignored runtime/evidence files;
- изменение execution commit или tracked files аннулирует текущий run.

### 4.2 Структура evidence

Harness создаёт каталог под `data/`, уже исключённый из Git:

```text
data/stage-v-evidence/<run-id>/
  run-manifest.json
  00-preflight/
  01-clean-bootstrap/
  02-initial-snapshot/
  03-crud-and-restart/
  04-caught-up/
  05-serving-sync/
  06-dbt-and-stable-views/
  07-additive-schema/
  08-rebuild/
  09-final/
  checksums.json
  summary.json
```

Каждый gate сохраняет:

- `started_at`, `finished_at`, duration и execution commit;
- sanitized argv без secret values;
- exit code и bounded stdout/stderr;
- входные и выходные snapshot/offset/run identifiers;
- canonical query results в JSON;
- assertion list с `PASS|FAIL|BLOCKED` и diagnostic code;
- SHA-256 каждого evidence-файла.

`run-manifest.json` неизменяем после начала V2, кроме добавления terminal status
и `finished_at`. В нём обязательны:

- OS, Docker/Compose и component image versions;
- commit SHA и результат `git status --porcelain`;
- fixture SHA-256 и expected-count manifest;
- Compose project name;
- random seed `20260801` и start time `2020-01-01T00:00:00`;
- список gates и их terminal status;
- факт redaction scan;
- ссылки на final canonical manifests.

### 4.3 Правила повторного запуска

- Read-only probe можно повторить в том же run, сохранив номер attempt.
- `bootstrap`, CRUD, schema mutation, publication и rebuild повторяются в том
  же run только если контракт операции явно идемпотентен и первый вызов имеет
  известный terminal state.
- Неизвестный terminal state mutating-операции означает `BLOCKED`; запрещено
  угадывать результат и создавать новый run ID на тех же volumes.
- После любого production fix выполняются новый `reset --yes`, новый run ID и
  полный путь V2-V10.

---

## 5. Validation harness, который нужно реализовать до acceptance run

### 5.1 Файлы

Рекомендуемая карта изменений:

```text
scripts/validation/stage_v_candidate_e2e.py
scripts/validation/stage_v_probes.py
tests/stage_v/fixtures/insert.sql
tests/stage_v/fixtures/update.sql
tests/stage_v/fixtures/delete.sql
tests/stage_v/fixtures/add_nullable_column.sql
tests/stage_v/fixtures/emit_nullable_event.sql
tests/stage_v/oracles/initial_counts.json
tests/stage_v/test_stage_v_harness.py
tests/stage_v/test_stage_v_oracles.py
docs/reports/mysql-spark-iceberg-stage-v-validation.md  # только после run
```

Можно переиспользовать `wave2_crud.sql`, но для restart barrier лучше иметь три
отдельных fixtures с теми же statements и фиксированными IDs. Нельзя менять
бизнес-семантику уже принятого Wave 2 сценария.

### 5.2 Public interface harness

```text
uv run python scripts/validation/stage_v_candidate_e2e.py prepare \
  --run-id <id> --evidence-dir <path>

uv run python scripts/validation/stage_v_candidate_e2e.py run \
  --run-id <id> --evidence-dir <path> --confirm-reset

uv run python scripts/validation/stage_v_candidate_e2e.py report \
  --evidence-dir <path>
```

- `prepare` выполняет только V0-V1 и не меняет runtime data.
- `run` — единственная документированная оркестрация V2-V10.
- `report` читает готовые evidence, ничего не запускает и не может повысить
  terminal status.
- `--confirm-reset` не передаётся вложенным arbitrary shell payload.
- Любая команда выдаёт один bounded JSON result и корректный non-zero exit code.

### 5.3 Адаптеры probes

Harness должен использовать отдельные typed adapters:

1. **MySQL probe** — read-only queries через существующий Python connector и
   password file; fixture executor имеет allowlist только для пяти Stage V SQL.
2. **Kafka probe** — topic/partition beginning/end offsets и выборочная проверка
   key/value/tombstone без изменения consumer offsets production groups.
3. **Iceberg probe** — finite Spark job с фиксированным allowlist отчётов. Не
   добавлять public arbitrary SQL execution.
4. **PostgreSQL control probe** — read-only выборка latest run, entity results,
   runtime cursor и lease.
5. **ClickHouse probe** — parameterized read-only queries; DDL разрешён только
   production rebuild DAG.
6. **Airflow probe** — stable REST API, DAG/run/task state и sanitized logs.

Если существующий `LakehouseStatusMain` не выдаёт нужные row-level hashes,
добавить finite `StageVValidationMain`, который принимает только имя заранее
определённого отчёта и output path. Нельзя добавлять универсальный `--sql`.

### 5.4 Canonical manifests

Для каждой entity manifest содержит:

- business primary key в стабильном tuple order;
- все контрактные business columns;
- `is_deleted`;
- last transaction/event/Kafka position;
- canonical row hash;
- source layer и snapshot/run identifiers.

Нормализация значений:

- timestamps — UTC ISO-8601 с микросекундами;
- decimals — fixed scale, без float conversion;
- strings — UTF-8 без trim/case conversion;
- `null` — JSON `null`;
- строки сортируются побайтово по canonical primary-key representation.

Сравнение выполняется по keys и по каждой business column. Одни row counts или
агрегированные checksum не заменяют row-level diff. Итоговый SHA-256 используется
как компактная ссылка на уже сохранённый полный manifest.

### 5.5 Tests harness

Unit tests обязаны доказать:

- запрет запуска без exact Compose project и `--confirm-reset`;
- redaction secrets и URL credentials;
- bounded stdout/stderr;
- корректное различение `FAIL`, `BLOCKED`, timeout и unknown terminal state;
- невозможность повысить упавший result при генерации отчёта;
- deterministic canonicalization decimal/timestamp/null/composite PK;
- обнаружение missing/extra keys, value mismatch и duplicate `event_id`;
- запрет arbitrary SQL, service name, path и shell fragments;
- проверку expected-count oracle;
- устойчивое возобновление read-only probes и запрет опасного mutating resume.

---

## 6. Детерминированный oracle

### 6.1 Initial snapshot

| Entity | Initial applied changes | Initial visible current |
| --- | ---: | ---: |
| `customers` | 8 | 8 |
| `orders` | 12 | 12 |
| `order_items` | 16 | 16 |
| `order_payments` | 14 | 14 |
| `order_reviews` | 12 | 12 |
| `products` | 8 | 8 |
| `sellers` | 4 | 4 |
| `product_category_translation` | 5 | 5 |
| **Total** | **79** | **79** |

Дополнительно:

- `reference.geolocation = 6`;
- `rejected = 0` и `schema_violations = 0`;
- 79 distinct business `event_id`;
- все initial business events имеют snapshot operation `r`/`is_snapshot=true`;
- MySQL и Silver current совпадают построчно.

### 6.2 CRUD delta

Используется семантика `wave2_crud.sql`:

| Transaction | Operations | Business events |
| --- | --- | ---: |
| INSERT | customer 1, order 1, items 2, payments 2, review 1 | 7 |
| UPDATE | order status 1, item price 1 | 2 |
| DELETE | review 1 | 1 |
| **Total** |  | **10** |

После CRUD и caught-up:

| Entity | Applied changes total | Visible current | Physical current | Deleted current |
| --- | ---: | ---: | ---: | ---: |
| `customers` | 9 | 9 | 9 | 0 |
| `orders` | 14 | 13 | 13 | 0 |
| `order_items` | 19 | 18 | 18 | 0 |
| `order_payments` | 16 | 16 | 16 | 0 |
| `order_reviews` | 14 | 12 | 13 | 1 |
| `products` | 8 | 8 | 8 | 0 |
| `sellers` | 4 | 4 | 4 | 0 |
| `product_category_translation` | 5 | 5 | 5 | 0 |
| **Total** | **89** | **85** | **86** | **1** |

Ожидаемый operation breakdown: `r=79`, `c=7`, `u=2`, `d=1`.

Delete acceptance:

- changes содержит одну `d` envelope для `wave2_review_001`;
- current содержит одну latest soft-delete version;
- stable current не возвращает удалённый review;
- Bronze содержит следующий tombstone того же key;
- tombstone не создаёт вторую changes/current row;
- tombstone offset учтён в `silver_progress`.

### 6.3 Exact value assertions

- `wave2_order_001.order_status = 'approved'`;
- `wave2_order_001.order_approved_at = 2018-09-01T10:05:00.123456`;
- item `(wave2_order_001, 2).price = 19.99`;
- item `(wave2_order_001, 1).price = 10.00`;
- две payments имеют values `12.50` и `23.50`;
- `wave2_review_001` отсутствует в visible current;
- все прочие initial rows побайтово эквивалентны fixture oracle.

### 6.4 Неподходящие замены oracle

Нельзя принимать как достаточное доказательство:

- только `status: ready`;
- только totals 79/89/85;
- `SELECT count(*)` без distinct keys и row-level manifest;
- один общий checksum без сохранённого canonical input;
- dbt `PASS` без publication boundary checks;
- наличие tombstone в Kafka без подтверждения progress и отсутствия второй
  business row;
- успешный rebuild без запрета чтения source systems и diff manifests.

---

## 7. Подробный порядок выполнения

### V0 — Entry gate и reconciliation Stage E

#### Действия

1. Зафиксировать commit SHA, branch, `git status --porcelain` и versions.
2. Проверить SHA-256 small fixture, source profile и CRUD fixture.
3. Выполнить `pre-commit run --all-files`.
4. Выполнить `uv lock --check`.
5. Выполнить релевантные Python suites:
   `tests/cdc_contracts`, `tests/lakehouse_platform`, `tests/mysql`,
   `tests/dbt_clickhouse`, `tests/serving` и `tests/stage_v`.
6. В `streaming/spark/scala` выполнить:
   `sbt scalafmtCheckAll scalafmtSbtCheck Test/compile test package`.
7. Проверить Compose config profiles `platform`, `streaming`, `serving`,
   `observability`.
8. Проверить Airflow DAG imports и dbt parse/selector boundaries.
9. Выполнить code/contract audit пунктов из раздела 3.2.
10. Выполнить `git diff --check` после всех автоматических hooks.

#### Stop/go

- Любой failed check блокирует V2.
- Auto-fix hook означает, что V0 запускается повторно с самого начала.
- Production gap из раздела 3.2 даёт `BLOCKED_BY_E_REGRESSION`, даже если
  lint/tests зелёные.
- `GO` возможен только при полном машинно-читаемом V0 evidence.

### V1 — Готовность validation harness

#### Действия

1. Реализовать файлы и adapters из раздела 5.
2. Разделить CRUD fixture на три транзакционных файла или доказать безопасные
   statement boundaries существующего файла.
3. Подготовить canonical queries и expected manifests.
4. Подготовить nullable schema fixture из V8.
5. Запустить negative tests harness без поднятия runtime.
6. Проверить, что `prepare` не создал/не изменил Docker resources.
7. Заморозить implementation commit для acceptance run.

#### Stop/go

- Harness не может объявить gate `PASS` без обязательного evidence-файла.
- SQL/path/service allowlists и redaction tests обязательны.
- После изменения harness снова выполняется V0.

### V2 — Чистый домен и seed (исходный шаг 1)

#### Действия

1. Проверить exact `COMPOSE_PROJECT_NAME=olist_stage_v`.
2. Сохранить pre-reset Compose inventory; чужие projects не трогать.
3. Выполнить `local_lab.py reset --yes`.
4. Доказать отсутствие volumes/containers текущего project.
5. Выполнить bootstrap с:
   `--run-id <stage-v-id>_seed --random-seed 20260801`.
6. Сохранить JSON bootstrap и MySQL row-level manifest.
7. Проверить, что после bootstrap serving/streaming profiles не были запущены
   преждевременно, если этого требует lifecycle contract.

#### Assertions

- Seed counts равны source profile: 79 business + 6 geolocation.
- Debezium connector создан только после seed.
- Нет ошибок bootstrap, schema capture и contract generation.
- В evidence/logs отсутствуют secrets.

### V3 — Initial snapshot и Silver baseline (исходные шаги 2-4)

#### Действия

1. Запустить `start-streaming`.
2. Зафиксировать container IDs, start timestamps, checkpoint inventory и Kafka
   beginning/end offsets.
3. Выполнить `wait-caught-up --timeout 1200`.
4. Дождаться двух последовательных READY observations с неизменными source end
   offsets и Silver progress.
5. Снять MySQL, Bronze, Silver changes/current, audit и reference manifests.
6. Выполнить initial row-level diff.

#### Assertions

- Таблица из раздела 6.1 совпадает полностью.
- Восемь entity queries и служебные Silver queries находятся в READY.
- Snapshot завершён для всех entity; частичный snapshot не принимается.
- `event_id` duplicate/collision count равен нулю.
- `normalization_errors` и `schema_violations` пусты.
- Geolocation содержит ровно 6 правильных строк и не смешана с CDC entities.

### V4 — Транзакционный CRUD, tombstone и контролируемый restart (шаги 5-8)

#### Действия

1. Сохранить baseline Kafka offsets, Iceberg snapshot IDs и checkpoint hashes.
2. Остановить `spark-bronze` и `spark-silver` одной scoped Compose-командой,
   не удаляя containers или volumes.
3. Убедиться, что Kafka Connect остаётся RUNNING.
4. Выполнить INSERT fixture одной MySQL transaction и зафиксировать commit ID.
5. Выполнить UPDATE fixture одной transaction.
6. Выполнить DELETE fixture одной transaction.
7. Подтвердить рост Kafka end offsets и наличие backlog, пока Spark остановлен.
8. Запустить Bronze и Silver одной Compose-командой; это restart barrier.
9. Зафиксировать новые container IDs/start timestamps и прежний checkpoint
   inventory.
10. Не выполнять повторно SQL fixtures в этом run.

#### Assertions

- MySQL commits: ровно три, без autocommit между statements fixture.
- Business event counts по транзакциям: 7, 2 и 1.
- Delete connector config сохраняет `tombstones.on.delete=true`.
- Оба Spark service действительно прошли stop/start.
- Kafka, MySQL, Polaris, MinIO и checkpoints не перезапускались/не очищались.
- Backlog существовал до restart, поэтому drill проверяет recovery, а не только
  process liveness.

### V5 — Catch-up, replay safety и CRUD oracle (исходный шаг 9)

#### Действия

1. Выполнить `wait-caught-up --timeout 1200`.
2. Дождаться двух стабильных READY observations.
3. Снять manifests и transaction/progress reports.
4. Сравнить с разделами 6.2-6.3.
5. Выполнить второй read-only caught-up observation без новых source writes.
6. Сравнить Iceberg snapshots/row counts между двумя observations.

#### Assertions

- Три транзакции имеют `COMPLETE`; `OPEN`/`REJECTED` отсутствуют.
- `changes=89`, distinct `event_id=89`, duplicate count `0`.
- Visible/physical/deleted current totals: `85/86/1`.
- Один tombstone учтён только в Bronze/progress.
- Exact values из 6.3 совпадают.
- Повторная обработка checkpoint не добавляет changes rows и не изменяет
  applied business state.
- Ни один query не находится в `FATAL`.

### V6 — Transaction-complete serving sync (исходный шаг 10)

#### Действия

1. Сохранить pre-sync public-view manifests и control state.
2. Запустить
   `sync-serving --run-id <stage-v-id>_crud_publish --timeout 1800`.
3. Получить authoritative result через serving report API/helper.
4. Снять PostgreSQL run/entity results/runtime cursor.
5. Снять ClickHouse marker/candidate partitions.
6. Снять Iceberg serving report.
7. Построить cross-system publication tuple.

#### Обязательный publication tuple

```text
(sync_run_seq,
 sync_run_id,
 previous_transaction_id,
 target_transaction_id,
 target_offsets,
 source_snapshot_ids,
 expected_event_count,
 materialized_event_count,
 event_checksum,
 published_at)
```

#### Assertions

- Sync terminal status — `SUCCEEDED`, не silent skip.
- Target boundary заканчивается DELETE transaction и не включает OPEN data.
- `expected_event_count = materialized_event_count = 89` для полного initial +
  CRUD event ledger.
- Per-entity counts совпадают с applied changes в разделе 6.2.
- Tuple идентичен в PostgreSQL, ClickHouse marker и Iceberg report.
- Один published seq видим целиком; нет частичной публикации entity.
- Unpublished/stale candidate partitions отсутствуют.
- Первый publish корректно активировал только предусмотренные schedules.

Если production contract считает initial snapshot отдельно от event ledger,
agent не меняет ожидаемое число произвольно: он фиксирует формулу контракта,
сверяет её с frozen boundary и сохраняет полный список selected `event_id`.
Отсутствие такой однозначной формулы — `BLOCKED_BY_E_CONTRACT_GAP`.

### V7 — dbt build и стабильные ClickHouse interfaces (шаги 11-12)

#### Действия

1. Из Airflow evidence получить точную команду dbt, vars и selector,
   выполненные внутри sync.
2. Подтвердить, что это `dbt build` candidate graph, а не только `dbt run`.
3. Сохранить totals `PASS/WARN/ERROR/SKIP` и список nodes/tests.
4. Выполнить row-level diff Silver current -> ClickHouse stable current.
5. Проверить `FINAL` на version tables и public stable views без `FINAL`.
6. Проверить восемь `gold.*` interfaces и dbt business tests.
7. Проверить отсутствие rows другого/unpublished `sync_run_seq` в public views.

#### Assertions

- dbt `ERROR=0`, `SKIP=0`; warnings допускаются только из заранее
  зафиксированного allowlist, по умолчанию `WARN=0`.
- Все eight Gold models и их tests выполнены с положительным published seq и
  непустым run ID.
- `serving_cdc.*_current` совпадает с Silver visible current: 85 строк и exact
  key/value parity.
- `fact_order_items` имеет grain `(order_id, order_item_id)` без duplicates и
  содержит 18 visible items.
- SCD2 windows не пересекаются, ровно одна current version на business key.
- Payment allocations balanced; daily/monthly mart formulas проходят tests.
- Query stable view несколько раз до/после `OPTIMIZE ... FINAL` возвращает один
  логический результат.

### V8 — Additive nullable schema evolution (исходный шаг 13)

#### Тестовое изменение

Использовать одну validation-only source column в `customers`:

```sql
ALTER TABLE olist_oltp.customers
ADD COLUMN stage_v_optional_note VARCHAR(64) NULL DEFAULT NULL;
```

Затем обновить существующую строку, изменив одну реальную business column, но
оставив новую колонку `NULL`, чтобы Debezium гарантированно выпустил data event с
новой writer schema:

```sql
UPDATE olist_oltp.customers
SET customer_city = 'sao paulo stage v',
    stage_v_optional_note = NULL
WHERE customer_id = 'wave2_customer_001';
```

Колонка проверяет source/writer compatibility и не становится новым публичным
полем Gold. Если действующий контракт требует явной версии reader contract и
allowlisted writer fingerprint, такая версия должна быть подготовлена и пройти
review до clean acceptance run. Нельзя динамически разрешать неизвестный
fingerprint во время прогона.

#### Действия

1. До V2 проверить migration fixture, nullable/default contract и expected
   schema fingerprint transition.
2. На V8 применить только allowlisted `ALTER`.
3. Дождаться регистрации/архивации новой writer schema.
4. Выполнить одну allowlisted UPDATE transaction.
5. Дождаться caught-up и снять schema/changes/current/audit evidence.
6. Выполнить второй serving sync с run ID `<stage-v-id>_schema_publish`.
7. Повторить dbt/stable-view checks для нового published seq.

#### Assertions

- Registry принимает новую schema при `BACKWARD_TRANSITIVE`.
- Новый writer schema ID/fingerprint архивирован и однозначно связан с
  `customers`.
- Новая колонка nullable с default `null`; existing fields/PK не изменились.
- Событие применено, `stage_v_optional_note` декодировано как `null` либо
  безопасно проигнорировано reader contract согласно заранее принятому решению.
- `normalization_errors=0`, `schema_violations=0`, query не переходит в `FATAL`.
- Customers changes увеличивается с 9 до 10; общий applied changes с 89 до 90.
- Current row counts не меняются; city новой latest version равен
  `sao paulo stage v`.
- Второй serving candidate содержит ровно одно новое business event; суммарный
  опубликованный event ledger содержит 90 distinct `event_id` и все стабильные
  views переключаются одним marker.
- Старые 79 snapshot events, CRUD events и rows с предыдущей writer schema
  остаются читаемыми.

Если nullable change требует production repair, текущий run завершается
`FAIL_SCHEMA_EVOLUTION`. Fix и contract version выполняются отдельно, затем
повторяется полный V2-V10 с чистого домена.

### V9 — Guarded ClickHouse rebuild только из Iceberg (исходный шаг 14)

#### Действия

1. Остановить scheduled serving/quality triggers или получить operation lease,
   не останавливая Bronze/Silver.
2. Снять final pre-rebuild manifests всех stable current и Gold interfaces,
   marker/cursor/report и их SHA-256.
3. Зафиксировать MySQL counts, Kafka offsets, Iceberg snapshot IDs и checkpoint
   inventory.
4. На время rebuild технически запретить Airflow task доступ к MySQL/Kafka, если
   это можно сделать scoped network/credential guard без изменения source data.
   Минимум — доказать по DAG graph, process/network logs и credentials, что
   rebuild использовал только Iceberg/Polaris/MinIO и control metadata.
5. Выполнить
   `rebuild-serving --yes --run-id <stage-v-id>_rebuild --timeout 5400`.
6. Снять post-rebuild manifests и publication metadata.
7. Выполнить exact pre/post row-level diff.
8. Выполнить `status --require serving` и `validate --scope serving`.

#### Assertions

- Rebuild отказался бы запускаться без `--yes`/`confirm_destructive=true`.
- Изменялись только derived ClickHouse databases/partitions.
- MySQL counts, Kafka offsets, Iceberg snapshot IDs и Spark checkpoint inventory
  не изменились из-за rebuild.
- Pre/post manifests stable current и Gold совпадают по keys и values.
- После rebuild: 90 distinct event rows, 85 visible current, 86 physical current,
  один deleted key.
- Marker/cursor/report остаются согласованы; нет dangling candidate partitions.
- dbt tests, serving status и serving validation зелёные.
- Bronze/Silver продолжали работу и не были перезапущены Airflow.

### V10 — Финальная приёмка и report

#### Действия

1. Повторить read-only probes всех слоёв.
2. Проверить отсутствие OPEN/REJECTED/stale candidate/active lease.
3. Выполнить final static smoke: `git diff --check`, contract checks и redaction
   scan evidence/logs.
4. Построить `checksums.json` и `summary.json`.
5. Проверить, что все V0-V10 принадлежат одному run ID, commit и Compose project.
6. Создать `docs/reports/mysql-spark-iceberg-stage-v-validation.md`.
7. Не изменять `serving-cutover.md` и не начинать Stage L в этом же изменении.

#### Итоговый verdict

`PASS` разрешён только если:

- все gates имеют `PASS`;
- нет missing evidence и redaction violations;
- ни один assertion не был downgraded/waived;
- run прошёл V2-V10 без production fix и нового bootstrap;
- отчёт содержит evidence hashes и точный execution commit;
- tracked worktree после report содержит только ожидаемый Markdown report.

---

## 8. Failure classification и действия агента

| Code | Пример | Действие |
| --- | --- | --- |
| `BLOCKED_BY_E_REGRESSION` | serving CLI/DAG не реализует Stage E contract | Сохранить evidence, остановить V, исправлять как Stage E defect. |
| `BLOCKED_ENVIRONMENT` | Docker/WSL resource failure до data mutation | Сохранить diagnostics; после ремонта среды начать новый clean run. |
| `BLOCKED_UNKNOWN_STATE` | timeout mutating operation без authoritative terminal state | Не повторять на тех же volumes; исследовать read-only. |
| `FAIL_DATA_LOSS` | missing key/event или offset gap | Остановить run; никакого serving publish/rebuild. |
| `FAIL_DUPLICATE` | duplicate/colliding `event_id` | Остановить run; сохранить конфликтующие metadata без payload secrets. |
| `FAIL_TRANSACTION_BOUNDARY` | OPEN/partial transaction опубликована | Остановить run; Stage L запрещена. |
| `FAIL_RESTART_RECOVERY` | checkpoint reset или replay изменил state | Остановить run; сохранить before/after checkpoint evidence. |
| `FAIL_SERVING_ATOMICITY` | marker/cursor/report расходятся | Остановить publish/rebuild; следовать recovery contract. |
| `FAIL_DBT_QUALITY` | dbt error, skip или business-test failure | Сохранить target artifacts/logs; Stage L запрещена. |
| `FAIL_SCHEMA_EVOLUTION` | compatible nullable schema остановила entity | Исправить contract/runtime отдельно и повторить весь run. |
| `FAIL_REBUILD_PARITY` | post-rebuild manifest отличается | Не восстанавливать вручную из MySQL/Kafka; расследовать Iceberg/rebuild. |
| `FAIL_EVIDENCE` | отсутствует обязательный raw/canonical artifact | Результат не может быть `PASS`, даже если runtime выглядит исправным. |

Агент обязан сообщить пользователю первый нарушенный gate, diagnostic code,
ожидаемое и фактическое значение, путь к sanitized evidence и безопасный
следующий шаг. Не нужно продолжать остальные mutating gates ради накопления
дополнительных ошибок.

---

## 9. Требования к Stage V validation report

Отчёт создаётся только из `summary.json` и проверенных raw evidence. Он содержит:

1. verdict `PASS|FAIL|BLOCKED`, дату и execution commit;
2. dirty-state statement и Compose project;
3. pinned component versions;
4. fixture/oracle/evidence SHA-256;
5. V0 static/build/test totals;
6. clean reset/bootstrap proof;
7. initial per-entity 79/79/0 и geolocation 6;
8. CRUD transaction IDs, counts 7/2/1 и tombstone proof;
9. restart timestamps, container IDs и checkpoint continuity proof;
10. post-CRUD 89 changes / 85 visible / 86 physical / 1 deleted;
11. duplicate/collision counts и row-level parity summary;
12. publication tuple и equality PG/CH/Iceberg;
13. dbt command, vars, selector, node/test totals;
14. stable current/Gold manifests и business assertions;
15. nullable schema old/new IDs/fingerprints, event proof и 90-event total;
16. rebuild isolation proof и exact pre/post manifest hashes;
17. final `status --require serving` и `validate --scope serving` JSON;
18. redaction result, known limitations и unresolved blockers;
19. явное решение: `Stage L is authorized` только при `PASS`.

Скриншоты UI сами по себе не являются evidence; допустимы как дополнение к API,
JSON, SQL results и logs.

---

## 10. Матрица трассировки исходных 14 шагов

| Исходный шаг `serving-cutover.md` | Gate этого плана | Главное доказательство |
| --- | --- | --- |
| 1. Seed | V2 | Fixture hash, MySQL manifest 79+6 |
| 2. Debezium initial snapshot | V3 | Snapshot completion, offsets, 79 events |
| 3. Silver current 79 | V3 | Per-entity row-level manifest |
| 4. Geolocation 6 | V3 | Reference manifest |
| 5. Multi-table create | V4 | COMPLETE transaction, 7 events |
| 6. Update | V4-V5 | COMPLETE transaction, 2 events, exact values |
| 7. Delete+tombstone | V4-V5 | 1 delete, 1 tombstone, progress coverage |
| 8. Restart Bronze/Silver | V4 | Stop/start evidence and checkpoint continuity |
| 9. Caught-up/no duplicates | V5 | Stable progress, 89 distinct IDs |
| 10. `sync-serving` | V6 | Publication tuple equality |
| 11. `dbt build` | V7 | Command/vars/selector and test totals |
| 12. `FINAL`/`gold` | V7 | Stable manifests and dbt assertions |
| 13. Nullable additive schema | V8 | Schema IDs/fingerprints, null event, 90 IDs |
| 14. `rebuild-serving` | V9 | Source isolation and exact pre/post parity |

---

## 11. Definition of Done

- [x] V0 подтвердил свежий зелёный entry gate Stage E.
- [x] Validation harness имеет allowlists, redaction и unit tests.
- [x] Один clean-domain run связан с одним commit и Compose project.
- [x] Initial snapshot: 79 applied/current, 0 rejected, 6 geolocation.
- [x] CRUD дал ровно 7 create, 2 update и 1 delete events.
- [x] Tombstone существует, учтён progress и не создал business duplicate.
- [x] Bronze/Silver перезапущены с сохранением checkpoints.
- [x] После catch-up: 89 distinct changes, 85 visible current, 1 deleted.
- [x] MySQL и Silver совпадают построчно по business keys/values.
- [x] Serving publication tuple идентичен в PG/CH/Iceberg.
- [x] Candidate опубликован атомарно для всех восьми entities.
- [x] dbt candidate build и все tests прошли без errors/skips.
- [x] Stable current и Gold не видят unpublished rows.
- [x] Nullable schema зарегистрирована, архивирована и обработана без ошибок.
- [x] После schema event существует 90 distinct applied events.
- [x] Rebuild использовал Iceberg как единственный data source.
- [x] Pre/post rebuild manifests совпадают построчно.
- [x] Final serving status/validate готовы и evidence redaction чист.
- [x] Validation report создан со статусом `PASS` и evidence hashes.
- [x] Legacy не удалён, final parity не запускался.
- [x] Stage L разрешена явно и только после `PASS`.

---

## 12. Связанные документы

- [Операционный cutover E -> V -> L -> F](../active/serving-cutover.md)
- [Детальный план Stage E](stage-e-serving-integration.md)
- [Отчёт Stage E](../../../reports/mysql-spark-iceberg-stage-e-validation.md)
- [Spark Structured Streaming contract](../contracts/spark-streaming.md)
- [Iceberg data model contract](../contracts/iceberg-data-model.md)
- [Serving and recovery contract](../contracts/serving-and-recovery.md)
- [Validation and CI contract](../contracts/validation-and-ci.md)
- [MySQL, Kafka and Avro contract](../contracts/mysql-kafka-avro.md)
- [Serving sync runbook](../../../runbooks/lakehouse-serving-sync.md)
- [ClickHouse rebuild runbook](../../../runbooks/lakehouse-clickhouse-rebuild.md)
