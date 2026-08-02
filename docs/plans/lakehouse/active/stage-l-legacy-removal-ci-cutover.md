# Детальный план Stage L: legacy removal и CI cutover

- **Статус**: `PENDING`, выполняется только после F0 `PASS`.
- **Назначение**: удалить runtime и тестовый долг старой PostgreSQL/NiFi/Redshift архитектуры и одновременно заменить CI так, чтобы защищалась только целевая lakehouse-архитектура.

---

## 1. Preconditions

1. Повторная приёмка E/V завершена.
2. Frozen oracle F0 принят и сохранён.
3. Удаляемые пути не используются целевым Compose, Airflow, Spark, dbt-clickhouse или parity reader.
4. Для каждого удаляемого legacy CI-сценария указано: replacement test либо обоснованное `DROP`.

---

## 2. Удаление legacy по пакетам

### L1 — runtime и инфраструктура

Удалить после проверки ссылок:

- PostgreSQL OLTP (`infra/oltp` и связанные simulator/load scripts); control PostgreSQL сохранить;
- `streaming/nifi`, NiFi bootstrap, processors, parameters, policies и secrets;
- старые MinIO landing/normalized/NiFi/CDC-loader init assets;
- старые ClickHouse `raw_batch`, `raw_cdc` и pipeline runtime init scripts;
- неиспользуемые локальной программой `infra/aws`, `infra/redshift` и Redshift loaders;
- legacy Compose profiles, services, volumes, healthchecks и environment variables.

### L2 — orchestration, dbt и observability

Удалить legacy DAGs:

- `olist_modern_data_stack_local.py`;
- `olist_modern_data_stack_aws.py`;
- `olist_cdc_local.py`;
- `olist_cdc_dbt_local.py`.

Сохранить только четыре целевых lakehouse DAG ID, перечисленных в плане E/V. Удалить `dbt/olist_analytics`; оставить `dbt/olist_clickhouse`. Удалить legacy Prometheus scrape targets, rules и Grafana dashboards для NiFi/PostgreSQL OLTP/старого CDC, сохранив lakehouse serving telemetry.

### L3 — зависимости, secrets и конфигурация разработчика

- удалить `dbt-redshift`, Redshift extra для Elementary, AWS SDK и иные пакеты только после доказательства отсутствия импортов;
- добавить явную pytest dependency/config и ограничить `testpaths`, чтобы не собирать `dbt_packages`;
- обновить `.pre-commit-config.yaml`, `.dockerignore`, Dockerfiles, README и примеры env на `dbt/olist_clickhouse`;
- удалить legacy secret templates (`postgres_password`, `redshift_password` и NiFi-specific), не выводя их содержимое;
- сузить control-postgres migrations/grants до фактически оставшихся consumers.

### L4 — тестовый инвентарь

Сохранить и сделать основой CI:

- `tests/mysql`;
- `tests/cdc_contracts`;
- `tests/lakehouse_platform`;
- `tests/dbt_clickhouse`;
- `tests/serving`;
- `tests/stage_v`;
- ScalaTest под `streaming/spark/scala/src/test`;
- неизменяемый fixture и новый `tests/fixtures/final_parity`.

Корневые legacy тесты `tests/test_*.py` удаляются после mapping review. Проверки, относящиеся к общим инвариантам (секреты, Avro compatibility, data-quality failure semantics), сначала переносятся в целевые suites; проверки NiFi, PostgreSQL OLTP, old batch/realtime dbt, Redshift и старого ClickHouse ingest удаляются без переноса. Старые PostgreSQL oracle-файлы удаляются после принятия F0, если не осталось явного consumer.

### L5 — repository guard

Добавить проверку запрещённых runtime-ссылок. Allowlist допускает упоминания legacy только в исторических completed plans/reports, migration rationale и provenance F0. Запрещены ссылки из Compose, Dockerfiles, scripts, active DAGs, dependency manifests, pre-commit и GitHub workflows.

---

## 3. Итоговая архитектура GitHub Actions

### 3.1 `.github/workflows/ci.yml` — обязательный общий CI

**Триггеры**: `pull_request`; `push` в `main`; на время миграции также `push` в `feature/mysql-spark-iceberg`. Это единственный required workflow для каждого PR. `workflow_dispatch` не нужен.

| Job | Что выполняет | Target / критерий |
| --- | --- | --- |
| `docs-and-repository-contracts` | YAML/TOML/Markdown links, compileall, legacy-reference guard, fixture/oracle metadata validation | всегда |
| `python-quality` | `ruff check`, `ruff format --check`, `pyright` | всегда, только целевые Python paths |
| `python-contract-tests` | pytest по шести целевым каталогам с JUnit; fail при 0 collected tests | всегда; не использовать `unittest discover` |
| `scala-fast` | scalafmt, `Test/compile`, ScalaTest, package и JAR content/dependency contract | всегда |
| `compose-contract` | `docker compose config`, service/profile inventory, no `container_name`, image/config/secret assertions | всегда, без поднятия полного стека |
| `airflow-dag-imports` | build Airflow image, import errors, exact DAG inventory и dbt path contract | всегда |
| `dbt-clickhouse-static` | `dbt deps`, `dbt parse`, `dbt compile`, selector/source/model contract | всегда; project `dbt/olist_clickhouse` |
| `ci-success` | агрегирует обязательные jobs для стабильного branch-protection check | `if: always()`, fail при любом failed/cancelled dependency |

Общие требования: минимальные `permissions: contents: read`, pinned major actions, `concurrency` с отменой устаревшего PR run, job timeouts, dependency caches по lockfiles, upload логов/JUnit при `failure()`, cleanup Docker при `always()`.

### 3.2 `.github/workflows/lakehouse-components.yml` — автоматические bounded integrations

**Триггеры**:

- `pull_request` и `push` в `main` с path filters для `compose.yaml`, `docker/**`, `infra/**`, `streaming/**`, `scripts/cdc/**`, `scripts/serving/**`, `airflow/**`, `dbt/olist_clickhouse/**` и соответствующих тестов;
- `workflow_dispatch` для повторного запуска конкретного компонента (`component=all|spark|cdc|serving`).

Workflow не заменяет required `ci.yml`; при нерелевантном PR он может не создаваться.

| Job | Сценарий | Максимальная граница |
| --- | --- | --- |
| `spark-image-contract` | build pinned Spark image, offline `--help` пяти main classes, JAR/runtime/permissions/secrets checks | без внешней сети на runtime step |
| `cdc-component` | MySQL → Debezium → Kafka/Apicurio → Bronze → Silver на small fixture; restart/replay | без ClickHouse/Airflow |
| `serving-component` | control migration 005, finite boundary, candidate publish, dbt build, stable switch, no-op retry и failpoints | bounded fixture, жёсткий timeout |
| `airflow-runtime` | запуск целевого Airflow image, exact DAG inventory и test одного bounded task path | без полного Stage V |
| `component-summary` | агрегирует фактически запущенные jobs и публикует артефакты | cleanup всегда |

### 3.3 `.github/workflows/lakehouse-acceptance.yml` — ручная полная приёмка

**Триггер**: только `workflow_dispatch`.

Inputs:

- `suite`: `candidate-e2e`, `final-parity` или `all`;
- `candidate_sha`: обязательный полный commit SHA;
- `confirm_destructive`: обязательное значение `true`;
- `artifact_retention_days`: ограниченное число дней.

| Job | Условие | Назначение |
| --- | --- | --- |
| `preflight` | всегда | проверка SHA, fixture/oracle checksums, runner capacity, unique Compose project и inputs |
| `stage-v-e2e` | `candidate-e2e`/`all` | полный clean V0–V10; не является PR check |
| `final-parity` | `final-parity`/`all` | candidate-only F1 против frozen oracle; не запускает legacy |
| `publish-evidence` | `always()` | raw JSON, Markdown report, JUnit, selected logs и итоговый статус без сокрытия failures |

Для destructive jobs задаются `environment: lakehouse-acceptance`, `concurrency: lakehouse-acceptance` и запрет параллельных запусков. F0 oracle этим workflow не регенерируется.

---

## 4. Судьба существующих workflows и jobs

### Workflows

| Текущий файл | Решение | Причина / replacement |
| --- | --- | --- |
| `.github/workflows/ci.yml` | `REWRITE` | все текущие jobs привязаны к legacy; итоговая структура описана выше |
| `batch-cdc-parity.yml` | `DELETE` | old batch/NiFi parity заменён frozen F0 + ручным candidate-only F1 |
| `cdc-stage2-kafka-debezium.yml` | `DELETE` | PostgreSQL source drill заменён `cdc-component` с MySQL |
| `cdc-stage6-operations.yml` | `DELETE` | NiFi failure injection заменён bounded CDC/serving restart и failpoint checks |

### Jobs старого `ci.yml`

| Текущий job | Решение |
| --- | --- |
| `static-analysis` | разделить на `python-quality` и `dbt-clickhouse-static`; убрать old dbt/Elementary steps |
| `python-unit` | заменить `python-contract-tests` с pytest и явными target directories |
| `airflow-imports` | переписать как exact lakehouse DAG inventory |
| `clickhouse-incremental-edges` | перенести актуальные Gold assertions в `serving-component`, legacy вариант удалить |
| `clickhouse-runtime-contract` | заменить dbt-clickhouse static + serving component checks |
| `cdc-clickhouse-ingest-resilience` | удалить raw CDC path; перенести общую retry semantics в target component tests |
| `cdc-source-oltp-simulator` | удалить; seed/MySQL contracts покрываются `tests/mysql` и `cdc-component` |
| `batch-fixture-idempotency` | заменить Stage V no-op/replay и bounded component assertions |

---

## 5. Порядок внедрения CI без слепой зоны

1. Добавить/исправить target tests и pytest configuration.
2. Переписать `ci.yml`; добиться зелёного результата на candidate.
3. Добавить `lakehouse-components.yml`; добиться зелёного релевантного запуска.
4. Добавить `lakehouse-acceptance.yml`; выполнить smoke preflight, не повторяя F0.
5. Только после этого удалить три legacy workflows и их scripts/tests.
6. Повторно запустить общий CI и релевантные component jobs на уже очищенном дереве.
7. Проверить branch protection: required check — стабильный `CI / ci-success`, а не имена динамически пропускаемых jobs.

---

## 6. Критерии завершения Stage L

- legacy runtime, configs, dependencies, secrets templates и active CI references отсутствуют;
- общий CI и все релевантные bounded component jobs проходят на очищенном дереве;
- ручной acceptance workflow проходит `preflight` и способен выбрать F1;
- exact DAG/service/dbt inventory соответствует целевой архитектуре;
- repository guard не находит запрещённых ссылок вне allowlist;
- frozen F0 oracle и его reader сохранены;
- после этого разрешён Stage F1.

---

## 7. Связанные документы

- [Контракт Validation & CI](../contracts/validation-and-ci.md)
- [План Stage F1](stage-f1-final-parity.md)
- [Координационный план](serving-cutover.md)
