# J1 runbook: финализация MySQL → Kafka → Spark/Iceberg Wave 1

Статус документа: инструкция следующему integration agent.

Основной архитектурный источник:
[`mysql-spark-iceberg-lakehouse-migration.md`](mysql-spark-iceberg-lakehouse-migration.md).
При противоречии основной план имеет приоритет. Этот документ описывает
фактическое состояние репозитория после Parallel Wave 1 и конкретный порядок
J1-сведения с реальными Docker-проверками.

## 1. Миссия J1

Нужно завершить **только J1**:

1. Зафиксировать уже написанные component changes потоков A-D.
2. Один раз объединить shared dependencies и обновить `uv.lock`.
3. Собрать новый platform runtime в `compose.yaml`.
4. Перевести `scripts/cdc/local_lab.py` на Wave 1 lifecycle.
5. Поднять чистый disposable Docker consistency domain.
6. Проверить MySQL, Kafka, Connect, Apicurio, MinIO, Polaris, Spark/Iceberg и
   ClickHouse реальными component smoke tests.
7. Получить из работающего Debezium/Apicurio все реальные writer schemas,
   сохранить evidence bundle и выпустить contract version `v2`.
8. Зафиксировать общий Spark normalization API для будущих Wave 2 agents, но
   не реализовывать entity normalizers.
9. Сохранить validation report без секретов и создать тематические commits.

J1 **не является** Wave 2, serving integration `E` или final parity. Нельзя
объявлять готовыми:

- Bronze/Silver streaming implementation;
- entity decoders/normalizers и Silver MERGE;
- Airflow publication/sync-serving;
- полный business E2E или final parity;
- удаление всех legacy-файлов.

Если Docker, реальные images, Registry, STS или component smoke недоступны,
J1 не завершён. Статических тестов в этом случае недостаточно.

## 2. Исходное состояние

Перед началом перепроверь, а не предполагай:

```powershell
git branch --show-current
git log -1 --oneline
git status --short
git diff --check
```

Ожидаемая ветка: `feature/mysql-spark-iceberg`.

P0 уже зафиксирован коммитом:

```text
685cd6f docs: add mysql spark iceberg migration plans
```

Component code A-D намеренно оставлен в working tree для J1. Не применять
`git reset`, `git checkout --`, массовое удаление, auto-stash или иной способ,
который может потерять эти изменения. Не запускать параллельные agents во
время staging/commit или инструмент, который временно stash'ит working tree.

Текущие owned surfaces:

| Поток | Пути | Результат Wave 1 |
| --- | --- | --- |
| A | `infra/mysql/**`, `scripts/simulation/**`, `tests/mysql/**` | MySQL DDL/users, seed, simulator |
| B | `streaming/kafka/**`, `streaming/connect/**`, `streaming/schemas/**`, `tests/cdc_contracts/**` | topics, connector, Registry и schema contracts |
| C | `docker/spark/**`, `infra/polaris/**`, `streaming/spark/platform/**`, `tests/lakehouse_platform/**` | Spark image, Polaris/MinIO, 26 Iceberg tables |
| D | `infra/clickhouse/lakehouse/**`, `dbt/olist_clickhouse/**`, `tests/dbt_clickhouse/**` | native ClickHouse DDL, DataLakeCatalog и dbt skeleton |

До J1 не менялись shared files:

```text
compose.yaml
pyproject.toml
uv.lock
scripts/cdc/local_lab.py
README.md
docs/architecture.md
```

Теперь ими владеет только J1 integration agent.

### 2.1 Последний известный non-Docker baseline

- MySQL: 42 passed, 2 opt-in integration tests skipped; legacy simulator —
  ещё 9 passed.
- CDC contracts: 51 passed; Ruff, Pyright, Bash и generators прошли.
- Lakehouse platform: 28 passed; Ruff и Bash syntax прошли.
- ClickHouse/dbt: 15 passed, включая настоящий `dbt parse`; Ruff и Bash
  syntax прошли.
- `git diff --check` прошёл.

Это только отправная точка. J1 должен повторить проверки после интеграции.

### 2.2 Известные намеренно незавершённые состояния

1. В `pyproject.toml` ещё нет `mysql-connector-python==9.7.0`.
2. `compose.yaml` всё ещё описывает legacy PostgreSQL/NiFi runtime.
3. `local_lab.py` всё ещё управляет legacy path.
4. `streaming/schemas/captured-writer-schemas/manifest.json` содержит ровно
   16 `pending_runtime_capture` slots.
5. В contract `v1` writer fingerprint allowlists пусты.
6. Numeric UID/GID pinned Polaris/Spark/ClickHouse/Airflow images ещё не
   доказаны реальным Docker runtime.
7. Polaris CLI JSON-lines contract и MinIO STS vending ещё не доказаны.
8. ClickHouse DataLakeCatalog smoke ещё не запускался против реального Polaris.

## 3. Непереговорные правила

1. Все persisted services входят в один disposable consistency domain:
   MySQL, Kafka/Connect, Apicurio, MinIO/Iceberg, Polaris DB, Spark checkpoints,
   ClickHouse и control PostgreSQL.
2. Потеря/рассогласование authoritative volume требует полного
   `reset --yes`; частичный repair запрещён. Исключение — производный
   ClickHouse, который позже сможет `rebuild-serving`.
3. Все пароли, tokens, client secrets и access keys передаются через `*_FILE`.
   Не помещать значения в Compose environment, command args, JSON, logs или
   validation report.
4. Не ослаблять fail-closed checks ради запуска стенда.
5. Не выдавать Spark или ClickHouse статический MinIO warehouse credential.
   Warehouse access идёт только через Polaris `vended-credentials`.
6. Не запускать runtime containers с `user: root` для обхода file permissions.
7. Не менять topic partition counts, primary keys, type mappings, catalog,
   namespace, database или service names.
8. Не генерировать writer fingerprints из reader schemas и не использовать
   Registry `latest` вместо ID, реально встреченного в Kafka record.
9. Не сохранять Kafka payloads или строки fixture в schema evidence bundle.
10. Не добавлять dummy `sleep`, always-healthy контейнеры или заглушки,
    создающие ложную готовность Spark Bronze/Silver.

## 4. Обязательные deliverables

К завершению J1 должны существовать:

1. Обновлённые `pyproject.toml` и `uv.lock`.
2. Валидный `compose.yaml` с profiles `platform`, `streaming`, `serving`,
   `observability` и без фиксированных `container_name`.
3. Полный Wave 1 lifecycle в `scripts/cdc/local_lab.py`.
4. Platform PostgreSQL init для databases/users `airflow`, `olist_control`,
   `polaris`, `apicurio`.
5. Пять изолированных Polaris credential projections.
6. Реально применённая Iceberg migration `0001_initial_lakehouse`.
7. Реально созданный ClickHouse DataLakeCatalog `lakehouse`.
8. Полный checked-in writer-schema evidence repository и contract `v2`.
9. Зафиксированный common Spark normalization API contract.
10. Validation report, например
    `docs/reports/mysql-spark-iceberg-wave1-j1-validation.md`.
11. Один или несколько тематических commits; working tree должен быть чистым
    либо содержать только явно перечисленный пользовательский work.

## 5. Фаза 0 — сохранить и проверить component baseline

### 5.1 Проверить ownership

Сопоставь каждый изменённый файл с таблицей owned surfaces. Shared files пока
не должны содержать случайных component edits.

```powershell
git status --short
git diff --name-only
git ls-files --others --exclude-standard
```

Если найдено неизвестное изменение, не перезаписывай его. Определи владельца
или остановись с точным blocker report.

### 5.2 Повторить быстрые проверки

```powershell
uv sync --all-groups

uv run python -m unittest discover -s tests/mysql -v
uv run python -m pytest -p no:cacheprovider tests/test_simulation.py -q

uv run python -m unittest discover -s tests/cdc_contracts -v
uv run python -m pytest -p no:cacheprovider tests/lakehouse_platform -q
uv run python -m unittest discover -s tests/dbt_clickhouse -v

uv run ruff check scripts/simulation streaming tests/mysql tests/cdc_contracts tests/lakehouse_platform tests/dbt_clickhouse
uv run ruff format --check scripts/simulation streaming tests/mysql tests/cdc_contracts tests/lakehouse_platform tests/dbt_clickhouse
uv run pyright scripts/simulation tests/mysql streaming/kafka streaming/connect streaming/schemas tests/cdc_contracts tests/dbt_clickhouse

uv run python -m streaming.schemas.generate_contracts --check
uv run python -m streaming.schemas.writer_schemas validate
uv run python -m streaming.schemas.contracts
```

До runtime capture следующая команда обязана завершаться non-zero:

```powershell
uv run python -m streaming.schemas.writer_schemas validate --require-captured
```

### 5.3 Сделать component commits до рискованной интеграции

После зелёного baseline закоммить A-D явными path groups. Не использовать
слепой `git add -A`, пока не проверен diff каждого потока. Рекомендуемая
структура:

```text
feat(mysql): add deterministic MySQL source and simulator
feat(cdc): add MySQL Debezium and schema contracts
feat(lakehouse): add Spark Iceberg and Polaris platform
feat(analytics): add ClickHouse lakehouse dbt skeleton
```

Runtime-derived schema evidence лучше коммитить отдельно после capture.

## 6. Фаза 1 — dependencies и lock

Добавь ровно:

```text
mysql-connector-python==9.7.0
```

Не добавляй новый HTTP/Avro dependency только ради J1: CDC bootstrap и
contract tools уже используют stdlib/существующие packages.

Обнови lock один раз:

```powershell
uv lock
uv sync --all-groups
uv lock --check
```

После этого повтори MySQL unit tests и Pyright. Opt-in integration пока не
включай, пока disposable MySQL не поднят.

## 7. Фаза 2 — Compose integration

### 7.1 Версии

Не менять зафиксированные версии:

| Компонент | Версия/image |
| --- | --- |
| MySQL | `mysql:8.4.10` |
| PostgreSQL control | `postgres:17.10` |
| Kafka | `apache/kafka:4.3.1` |
| Debezium | `3.6.0.Final` |
| Apicurio | `3.3.0` |
| Spark | `4.1.3`, Scala `2.13`, Java `17`, Python `3.12` |
| Iceberg | `1.11.0` |
| Polaris | `1.6.0` |
| ClickHouse | `26.3.17.4` |
| Airflow | `3.2.1` |
| dbt-clickhouse | `1.10.1` |

### 7.2 Публичные service names

Сохрани имена из основного плана:

```text
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
```

Дополнительные one-shot names для admin, migration и credential projection
допустимы, если они однозначны. Не возвращать `container_name`: project names
нужны для изолированных smoke/parity runs.

`spark-bronze` и `spark-silver` не должны считаться ready до Wave 2. Можно
заранее описать их wiring только при наличии реального entrypoint; нельзя
подменять отсутствующий streaming code заглушкой.

### 7.3 Profiles

- `platform`: platform-postgres, MySQL, Kafka/topics, Apicurio, Connect,
  MinIO/init, Polaris helpers/server/bootstrap, Spark master/worker и Iceberg
  migration.
- `streaming`: будущие `spark-bronze`, `spark-silver`.
- `serving`: ClickHouse/init и Airflow.
- `observability`: существующие exporters/Prometheus/Grafana/Loki.

Legacy PostgreSQL/NiFi assets ещё нужны для позднего parity и не удаляются из
репозитория в J1. Они не должны автоматически стартовать в новом candidate
profile. Не смешивать их volumes с новым consistency domain.

### 7.4 Platform PostgreSQL

Переименуй/consolidate текущий `airflow-postgres` в `platform-postgres` и
создай отдельные databases/users:

```text
airflow
olist_control
polaris
apicurio
```

Business tables в PostgreSQL запрещены. Подключи
`infra/polaris/postgres/010_create_polaris_database.sh` и добавь эквивалентный
idempotent init для Apicurio. Airflow/control initialization должен остаться
рабочим.

### 7.5 MySQL

Service `mysql`:

- image `mysql:8.4.10`;
- read-only mount `infra/mysql/conf.d/olist.cnf`;
- read-only mount `infra/mysql/initdb/` в `/docker-entrypoint-initdb.d/`;
- отдельный named volume;
- UTC/utf8mb4/binlog settings берутся из checked-in config;
- secrets:
  `mysql_root_password`, `mysql_admin_password`,
  `mysql_simulator_password`, `mysql_cdc_reader_password`;
- root credential только через `MYSQL_ROOT_PASSWORD_FILE`;
- host port открывать только для local integration test.

### 7.6 Kafka, Apicurio и Connect

1. Отключи broker topic auto-creation.
2. `kafka-topics` монтирует `streaming/kafka/topics.json` и
   `create-topics.sh`, завершается только после exact topic bootstrap.
3. `apicurio-registry` использует SQL/PostgreSQL storage и `_FILE` wrapper
   `streaming/connect/apicurio-file-env.sh`.
4. `kafka-connect` собирается из `streaming/connect/Dockerfile`; в image не
   должно остаться PostgreSQL connector inventory.
5. Connect service стартует после Kafka topics и Apicurio readiness, но сам
   connector регистрируется **после seed**.
6. Connector password монтируется файлом; в Compose environment значения нет.

### 7.7 MinIO, Polaris и credential projections

Root producer volume с generated Polaris/MinIO credentials никогда не
монтируется напрямую в runtime services.

Создай отдельные target volumes:

```text
polaris_admin_credentials
polaris_server_credentials
spark_credentials
clickhouse_polaris_credentials
airflow_polaris_credentials
```

Источником истины является
`infra/polaris/credentials/projection-contract.json`:

| Consumer | Доступные файлы |
| --- | --- |
| `polaris-admin` | bootstrap admin pair |
| `polaris-server` | bootstrap admin pair + MinIO warehouse pair |
| `spark` | Spark Polaris pair + checkpoint-only MinIO pair |
| `clickhouse` | ClickHouse Polaris pair |
| `airflow` | Airflow Polaris pair |

Каждый projector:

- source volume read-only в `/run/polaris-credentials`;
- ровно один target volume read-write в `/run/projected-credentials`;
- `CREDENTIAL_CONSUMER` из контракта;
- numeric `CREDENTIAL_TARGET_UID/GID` реального image user;
- `condition: service_completed_successfully` перед consumer start.

UID/GID нельзя угадывать. После pull/build выполни эквивалент:

```powershell
docker run --rm --entrypoint id apache/polaris:1.6.0 -u polaris
docker run --rm --entrypoint id apache/polaris:1.6.0 -g polaris
docker run --rm --entrypoint id olist-spark:4.1.3-iceberg1.11.0 -u spark
docker run --rm --entrypoint id clickhouse/clickhouse-server:26.3.17.4 -u clickhouse
docker run --rm --entrypoint id olist-airflow:local -u airflow
```

Если конкретный image использует другое имя или команда недоступна, выясни
фактический numeric user через image inspection. Doctor должен сверять эти
значения и завершаться ошибкой при drift.

Обязательный Polaris порядок:

1. prepare root credential volume;
2. project `polaris-admin`;
3. создать Polaris database/user в platform-postgres;
4. выполнить JDBC admin bootstrap;
5. поднять MinIO и выполнить `minio-init`;
6. project `polaris-server`;
7. поднять Polaris server;
8. выполнить `polaris-bootstrap` с exact RBAC verification и runtime auth
   probes;
9. project Spark, ClickHouse и Airflow credentials;
10. только затем запускать consumers.

Не заменять STS static key fallback. В catalog config должны остаться:

```text
endpoint=http://minio:9000
endpoint_internal=http://minio:9000
sts_endpoint=http://minio:9000
```

`sts_unavailable` запрещён, так как Spark и ClickHouse требуют scoped vended
credentials. Кратковременный argv exposure, неизбежный для поддерживаемого
`mc admin user add`, допустим только внутри изолированного one-shot container:
контейнер не должен оставаться running, shell tracing выключен, private
`MC_CONFIG_DIR` удаляется trap'ом, logs не содержат значения.

### 7.8 Spark и Iceberg migration

Собери `docker/spark/Dockerfile` без runtime downloads. Build обязан проверить
все SHA-256 и Hadoop/Spark/Scala versions.

Подними standalone master/worker. Для migration используй реальный wrapper:

```text
/usr/local/bin/run-with-platform-config.sh \
  /opt/olist/streaming/spark/platform/migrate.py
```

Migration должна:

- создать ровно namespaces `bronze`, `silver`, `reference`, `audit`;
- создать ровно 26 Iceberg tables;
- проверить schemas, required/nullability, partitions и properties;
- записать `audit.schema_migrations` version 1;
- пройти повторно без нового conflicting record.

Запись migration history является первым реальным Spark write через Polaris
vended credentials. Если она не проходит, J1 блокирован; не выдавай Spark
warehouse static key.

### 7.9 ClickHouse

`clickhouse-init` должен последовательно применить:

```text
infra/clickhouse/lakehouse/001_create_databases.sql
infra/clickhouse/lakehouse/002_create_serving_control.sql
infra/clickhouse/lakehouse/003_create_event_tables.sql
infra/clickhouse/lakehouse/004_create_current_version_tables.sql
infra/clickhouse/lakehouse/005_create_stable_current_views.sql
```

После Polaris bootstrap, ClickHouse projection и Iceberg migration выполни
`infra/clickhouse/lakehouse/bootstrap-catalog.sh`. Credential передаётся через
stdin-generated SQL и file secrets, не через args.

Airflow publication в J1 не реализовывать.

### 7.10 Healthchecks и dependencies

Каждый long-running service получает bounded healthcheck. One-shots должны
использовать `condition: service_completed_successfully`; long-running
dependencies — `condition: service_healthy`.

Не считать readiness по открытому TCP-порту, если компонент имеет собственный
health/readiness API. Все retry loops bounded.

## 8. Фаза 3 — `local_lab.py`

`scripts/cdc/local_lab.py` остаётся единственной documented CLI точкой.
Сохрани command names основного плана:

```text
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
```

### 8.1 Реализовать в J1

- `doctor`: Docker/Compose availability, pinned images, secret files,
  archive, ports, UID/GID contracts и Compose config.
- `reset --yes`: только scoped
  `docker compose down -v --remove-orphans`; никаких host-directory deletes.
- `up`/`down`: новый profile-aware platform lifecycle; `down` сохраняет
  volumes.
- `seed`: MySQL simulator, обязательный random seed и file password.
- `bootstrap`: clean-domain checks, platform one-shots, MySQL seed, connector
  registration, writer-schema capture и Iceberg migration. Он должен явно
  вернуть readiness level `wave1_platform`, а не заявлять готовность Wave 2.
- `status`: Compose, MySQL counts, topics, connector/task, Registry rule,
  capture state, Polaris/RBAC, Iceberg migration/table count и ClickHouse
  catalog status.
- `validate`: все реальные Wave 1 checks из этого runbook; final state с
  pending writer schemas является failure.

### 8.2 Не изображать готовыми

Пока Wave 2/E отсутствуют, команды `start-streaming`, `wait-caught-up`,
`sync-serving`, `rebuild-serving`, `run-maintenance` и `final-parity` должны
возвращать структурированный non-zero `not_available_until` с конкретной
phase, а не молча завершаться успешно. Не переименовывай и не удаляй команды:
их surface уже зафиксирован.

Все команды:

- имеют bounded timeout;
- печатают JSON result/status;
- редактируют secret values и JSON-escaped variants;
- не выводят secret file contents;
- различают `failed`, `blocked`, `not_available_until` и `ready`.

## 9. Фаза 4 — clean real runtime bootstrap

Используй отдельный project name, например:

```powershell
$env:COMPOSE_PROJECT_NAME = 'olist_wave1_j1'
```

### 9.1 Начать с clean domain

```powershell
python scripts/cdc/local_lab.py doctor
python scripts/cdc/local_lab.py reset --yes
docker compose config --quiet
```

Проверь, что удаляются только volumes этого Compose project.

### 9.2 Platform bootstrap order

Рекомендуемая последовательность orchestration:

1. platform-postgres + DB init;
2. MySQL;
3. Kafka + exact topic bootstrap;
4. Apicurio SQL Registry;
5. Kafka Connect service без зарегистрированного connector;
6. MinIO/Polaris credential preparation и admin bootstrap;
7. MinIO init, Polaris server/bootstrap и projections;
8. Spark master/worker;
9. Iceberg migration;
10. seed small fixture в MySQL;
11. зарегистрировать `olist-mysql-cdc`;
12. дождаться connector и task 0 `RUNNING`;
13. дождаться initial snapshot records и Registry artifacts;
14. capture writer schemas;
15. ClickHouse native/catalog init;
16. Wave 1 validate.

Seed обязан выполняться до connector registration. Если connector уже
зарегистрирован или business tables непусты, seed должен отказать.

## 10. Фаза 5 — реальные MySQL проверки

На clean MySQL запусти opt-in scaffold. Укажи simulator user и host-mounted
secret file:

```powershell
$env:OLIST_RUN_MYSQL_INTEGRATION = '1'
$env:OLIST_MYSQL_INTEGRATION_DISPOSABLE = '1'
$env:MYSQL_HOST = '127.0.0.1'
$env:MYSQL_PORT = '3306'
$env:MYSQL_DATABASE = 'olist_oltp'
$env:MYSQL_USER = 'olist_simulator'
$env:MYSQL_PASSWORD_FILE = '<absolute path to simulator password file>'

uv run python -m unittest tests.mysql.test_mysql_integration -v
```

Scaffold проверяет exact information_schema, empty precondition, fixture
counts и повторный idempotent seed. После него ожидаются:

```text
customers                         8
orders                           12
order_items                      16
order_payments                   14
order_reviews                    12
products                          8
sellers                           4
product_category_translation      5
geolocation                       6
```

Business CDC total без geolocation: **79 rows**.

Дополнительно проверь:

- binlog format/image/row metadata из `olist.cnf`;
- grants трёх application users;
- heartbeat UPSERT от CDC user;
- password files односложные, непустые и не попали в logs.

## 11. Фаза 6 — Kafka/Connect/Apicurio smoke

1. Запусти live topic validator:

   ```text
   python /contract/validate_topics.py --bootstrap-server kafka:29092
   ```

2. Убедись, что managed set содержит ровно 15 topics, partition counts и
   configs совпадают с `topics.json`, auto-create выключен.
3. Проверь group `olist_cdc` и group rule
   `COMPATIBILITY=BACKWARD_TRANSITIVE` через Registry API.
4. Зарегистрируй connector только через:

   ```text
   python -m streaming.connect.bootstrap \
     --password-file /run/secrets/mysql_cdc_reader_password
   ```

5. Дождись `RUNNING` у connector и task 0.
6. Проверь, что captured table set — ровно восемь business tables;
   geolocation/control DB исключены.
7. Проверь initial snapshot count 79 по business topics. Считать records, а не
   только Kafka offsets; tombstones и metadata topics учитывать отдельно.
8. Повторный bootstrap должен быть idempotent. Non-secret drift обязан
   завершаться ошибкой, а не скрытым PUT/resnapshot.
9. В logs не должно быть `database.password` value или response body
   secret-bearing request.

## 12. Фаза 7 — capture реальных writer schemas

Это блокирующий J1 deliverable.

### 12.1 Источник schema ID

Для каждого из восьми business topics:

1. Прочитай snapshot record с `auto.offset.reset=earliest`, unique consumer
   group, `enable.auto.commit=false` и без сохранения payload.
2. Возьми key и non-null value bytes.
3. Проверь Confluent framing через `streaming.schemas.avro`.
4. Используй content/schema ID из первых пяти bytes. Не используй artifact
   `latest` как источник истины.
5. Получи schema и reference closure из живого Apicurio Registry.
6. Сформируй self-contained Avro writer schema, реально соответствующий bytes.
7. Не печатай и не сохраняй business payload.

Если в одном consistency domain реально встречаются несколько schema IDs для
entity/kind, сохрани каждый уникальный writer schema. Нельзя удалять ранее
разрешённые fingerprints.

### 12.2 Evidence bundle

Bundle должен повторять layout
`streaming/schemas/captured-writer-schemas/`:

```text
manifest.json
<entity>/key/<schema>.avsc
<entity>/value/<schema>.avsc
```

Для каждого schema manifest требует:

```text
path
sha256
provenance.registry_url
provenance.registry_group = olist_cdc
provenance.artifact_id
provenance.artifact_version
provenance.schema_id
provenance.captured_at_utc (UTC ISO-8601)
provenance.connector_name = olist-mysql-cdc
provenance.topic
```

Все 16 entity/kind sections должны перейти в `captured`. Partial capture не
активирует allowlists.

### 12.3 Импорт и v2

```powershell
uv run python -m streaming.schemas.writer_schemas capture-bundle --bundle <runtime-export-directory>
uv run python -m streaming.schemas.writer_schemas validate --require-captured

uv run python -m streaming.schemas.generate_contracts --write --new-version 2
uv run python -m streaming.schemas.generate_contracts --check
uv run python -m streaming.schemas.contracts --require-captured-writers
```

Не переписывай `v1.json`. Перед commit проверь:

```powershell
git diff -- streaming/schemas/contracts/*/v1.json
```

Diff должен быть пустым. В `v2` allowlists должны ссылаться только на
checked-in `.avsc` и manifest provenance. Просканируй bundle на credentials и
payload fragments до staging.

## 13. Фаза 8 — Polaris/Spark/Iceberg real smoke

### 13.1 Polaris bootstrap

`polaris-bootstrap` должен реально подтвердить:

- exact principal roles;
- exact catalog-role assignments;
- exact grants из `expected-rbac.json`;
- runtime login Spark/ClickHouse/Airflow pairs;
- чтение catalog и namespace каждым principal согласно роли.

Если Polaris CLI 1.6 возвращает другой JSON-lines shape, сохрани
**санитизированный** пример в validation report и исправь parser. Не удаляй
exact verification и не заменяй его проверкой exit code `setup apply`.

Проверь mounts через `docker inspect`:

- runtime consumer видит только свой projection volume;
- root producer volume не смонтирован;
- projected directory `0700`, files `0600`, owner соответствует image user;
- нет `user: root` override.

### 13.2 Spark migration smoke

1. Первый migration run создаёт 4 namespaces, 26 tables и одну APPLIED запись
   migration history.
2. Второй run возвращает тот же checksum и не создаёт duplicate/conflict.
3. Проверь `SHOW CREATE TABLE`, properties и partitions минимум для одного
   Bronze, одного Silver changes/current, reference и audit table.
4. Проверь запись/чтение `audit.schema_migrations`. Это доказывает реальные
   vended MinIO STS credentials.
5. Проверь, что Spark config содержит checkpoint static credential только для
   `s3a://olist-checkpoints`, а warehouse static key отсутствует.
6. Убедись, что Spark event/log output не содержит catalog credential или
   временные STS credentials.

### 13.3 Failure rule

Если STS/vending не работает:

- не ставить `sts_unavailable`;
- не передавать warehouse access key Spark/ClickHouse;
- не расширять ClickHouse RBAC;
- диагностировать MinIO STS endpoint, Polaris storage config, policy и header
  `X-Iceberg-Access-Delegation=vended-credentials`.

## 14. Фаза 9 — ClickHouse/dbt real smoke

### 14.1 Native DDL

На реальном ClickHouse:

1. Примени `001`-`005` дважды; повтор должен быть idempotent.
2. Запусти
   `infra/clickhouse/lakehouse/tests/001_replacing_merge_tree_learning.sql`.
3. Проверь exact 8 event tables, 8 current-version tables и 8 stable views.
4. Убедись, что unpublished runs и deletes скрыты.

### 14.2 DataLakeCatalog

Для fixed-snapshot smoke нужен реальный snapshot у
`silver.customers_current`. На отдельном disposable J1 smoke project:

1. Через Spark вставь одну синтетическую contract-valid row.
2. Получи её Iceberg snapshot ID через Spark metadata table/API.
3. Передай ID как `ICEBERG_CUSTOMERS_SNAPSHOT_ID` и запусти
   `infra/clickhouse/lakehouse/tests/run-catalog-smoke.sh`.
4. Проверь current read и fixed snapshot read.
5. После smoke выполни полный reset этого project; не оставляй synthetic row в
   финальном clean domain.

Не передавай Polaris credential в ClickHouse args. ClickHouse projection
должен содержать только read-only Polaris pair.

### 14.3 dbt

Минимум:

```powershell
uv run dbt parse --project-dir dbt/olist_clickhouse --profiles-dir <temp-profile-dir> --target local_clickhouse --vars '{sync_run_seq: 9001, sync_run_id: "j1-wave1-smoke"}'
```

Затем выполни реальный `dbt build` против пустого или синтетического native
serving fixture с теми же run vars. Цель J1 — доказать ClickHouse syntax,
materializations, tests и publication isolation, а не построить production
serving sync.

Проверь:

- candidate rows пишутся в partition `sync_run_seq=9001`;
- public views не показывают unpublished candidate;
- unit/data tests реально исполняются адаптером;
- `cleanup_gold_partitions` по умолчанию dry-run.

Airflow publication и production `sync-serving` остаются этапом E.

## 15. Фаза 10 — common Spark normalization API

J1 должен зафиксировать интерфейс для Wave 2, но не писать entity business
transforms. Добавь importable contract и targeted tests либо явный API
document рядом с `streaming/spark/platform`.

Интерфейс обязан зафиксировать:

- entity/contract version и writer fingerprint как вход;
- canonical event metadata и `event_id=topic:partition:offset`;
- schema resolver boundary;
- common Debezium envelope decode result;
- entity normalizer Protocol/call signature;
- changes append и current MERGE executor boundary;
- same-key ordering/dedupe contract;
- audit/error writer boundary;
- checkpoint/query naming из `topology.py`;
- запрет entity agents менять common modules.

Не добавлять восемь normalizers и не запускать `spark-bronze/silver` как ready.
API должен быть достаточно конкретным, чтобы S1-S4 могли работать только в
своих entity paths без изменения common surface.

## 16. Фаза 11 — полный validation matrix

### 16.1 Static/unit

Повтори все команды фазы 0, затем:

```powershell
uv lock --check
uv run dbt parse --project-dir dbt/olist_clickhouse --profiles-dir <temp-profile-dir> --target local_clickhouse --vars '{sync_run_seq: 9001, sync_run_id: "j1-wave1-smoke"}'
docker compose config --quiet
git diff --check
```

### 16.2 Compose/images

```powershell
docker compose --profile platform --profile serving config
docker compose --profile platform --profile serving build
docker compose --profile platform --profile serving up -d --wait
docker compose ps -a
```

Проверь, что:

- все one-shots завершились code 0;
- все long-running services healthy;
- images действительно pinned;
- Spark runtime verifier прошёл;
- повторный bootstrap idempotent;
- обычный restart сохраняет state;
- bounded readiness не зависает.

### 16.3 Secret leak checks

Добавь автоматическую проверку, которая читает secret values в память,
сравнивает их с Compose logs/config/inspect output, но при совпадении печатает
только label, не само значение.

Проверь:

- `docker compose config`;
- `docker inspect ... Config.Env`;
- container command/args;
- sanitized logs всех services;
- generated validation report.

Также проверь, что stopped MinIO init container не содержит оставшийся private
`MC_CONFIG_DIR`, а generated credential source volume недоступен runtime
containers.

### 16.4 Wave 1 restart smoke

Один раз одновременно перезапусти platform services, которые уже существуют в
Wave 1, затем проверь:

- MySQL data сохранились;
- connector/task вернулись в RUNNING;
- topic/config validation проходит;
- Polaris RBAC/projections валидны;
- повторная Iceberg migration идемпотентна;
- ClickHouse catalog снова читает Iceberg.

Не заявляй catch-up/Silver correctness: streaming foundation ещё не написан.

## 17. Failure policy

| Симптом | Действие |
| --- | --- |
| Topic partition/config drift | Полный reset; не alter partition count |
| MySQL schema/fixture mismatch | Исправить integration seam или вернуть finding потоку A |
| Connector config drift | Не PUT secret-bearing config; fail и reset/явная миграция |
| Writer schema не совпал с reader contract | Не whitelist; сохранить evidence и вернуть contract finding потоку B |
| Partial 16-slot capture | J1 blocked; contract остаётся fail-closed |
| Polaris DB/credential volume mismatch | Полный reset consistency domain |
| Polaris CLI output shape иной | Исправить bounded parser, не отключать exact check |
| Projected secret не читается | Исправить UID/GID/projection; не запускать consumer root |
| MinIO STS/vending не работает | Исправить STS/storage config; не раздавать static warehouse key |
| Iceberg schema/property/partition drift | J1 blocked; не выполнять silent ALTER |
| ClickHouse DataLakeCatalog не читает snapshot | Исправить integration seam/версию; не ослаблять read-only RBAC |
| Docker unavailable | J1 blocked; не объявлять Wave 1 финализированной |

## 18. Validation report

Создай report с:

- date/time и commit SHA;
- Docker/Compose versions;
- exact image IDs/digests;
- resolved UID/GID без secret values;
- команды и exit codes;
- MySQL table counts;
- Kafka topics/partitions/config result;
- sanitized connector/task status;
- Registry rule и 16 captured schema IDs/fingerprints;
- Iceberg namespaces/table count/migration checksum;
- Polaris exact RBAC result;
- ClickHouse native/catalog/dbt results;
- restart result;
- известные deferred Wave 2/E items.

Не вставляй raw Docker inspect/log dumps, Kafka payloads, passwords, client
secrets, access keys, OAuth tokens или STS credentials.

## 19. Commit strategy

После component commits рекомендуются отдельные commits:

```text
feat(platform): integrate wave1 compose and local lab
feat(cdc): capture runtime writer schema contracts
test(platform): validate wave1 docker components
docs: record wave1 j1 validation
```

Перед каждым commit:

```powershell
git diff --cached --stat
git diff --cached --check
git status --short
```

Не смешивай unrelated пользовательские изменения. Не force-push и не создавай
PR без отдельного запроса пользователя.

## 20. Definition of Done

J1 завершён только если одновременно истинны все пункты:

- [ ] Shared files сведены одним integration agent.
- [ ] `mysql-connector-python==9.7.0` locked и импортируется.
- [ ] Compose config валиден, fixed `container_name` отсутствуют.
- [ ] Clean `platform` profile поднимается из пустых volumes.
- [ ] MySQL opt-in schema/reseed integration tests прошли.
- [ ] Exact 15 Kafka topics прошли live validation.
- [ ] Connector и task 0 реально RUNNING.
- [ ] Apicurio реально использует PostgreSQL и BACKWARD_TRANSITIVE.
- [ ] Все 16 writer schema slots captured из Kafka/Registry evidence.
- [ ] Writer repository и contract `v2` проходят require-captured validation.
- [ ] Пять Polaris projections изолированы, modes/owners проверены.
- [ ] Polaris exact RBAC и runtime auth probes прошли.
- [ ] Spark получил usable vended MinIO STS credentials.
- [ ] Iceberg migration создала и повторно проверила 26 tables.
- [ ] ClickHouse native DDL и ReplacingMergeTree learning test прошли.
- [ ] ClickHouse DataLakeCatalog current/fixed-snapshot smoke прошёл.
- [ ] dbt parse и реальный adapter build/tests прошли.
- [ ] `local_lab doctor/status/validate/reset/up/down/seed/bootstrap` работают
      с bounded JSON contract.
- [ ] Отсутствующие Wave 2/E команды честно возвращают structured non-zero.
- [ ] Secret leak scan прошёл.
- [ ] Restart smoke прошёл.
- [ ] Static/unit/format/type checks и `git diff --check` прошли.
- [ ] Validation report сохранён без секретов.
- [ ] Тематические commits созданы; handoff перечисляет deferred work.

## 21. Финальный handoff следующего agent

В ответе пользователю перечисли:

1. Созданные commits.
2. Изменённые shared files.
3. Реальные Docker/component проверки и точные результаты.
4. Writer schema IDs/fingerprints без schema payloads.
5. Polaris UID/GID, RBAC и STS smoke result без credentials.
6. Iceberg/ClickHouse/dbt smoke result.
7. Какие пункты остаются строго для Wave 2, J2 и E.
8. Любой blocker, который не позволил честно выполнить Definition of Done.

Не использовать формулировки «полный pipeline готов» или «E2E готов», пока не
завершены Wave 2, J2 и serving integration E.
