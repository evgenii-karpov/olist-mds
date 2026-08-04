# Технический контракт: Validation & CI

- **Статус**: Действующий нормативный контракт целевой архитектуры.
- **Назначение**: определить обязательные автоматические проверки, bounded integrations и ручные acceptance-прогоны после отказа от PostgreSQL OLTP/NiFi/старого dbt.

---

## 1. Уровни проверки

| Уровень | Workflow | Trigger | Обязательность |
| --- | --- | --- | --- |
| Fast/common | `.github/workflows/ci.yml` | каждый PR, push в `main` | required branch protection |
| Bounded component contracts | `.github/workflows/lakehouse-components.yml` | PR/push по target path filters | быстрые contract jobs обязательны для релевантных изменений |
| Bounded CDC runtime | `.github/workflows/lakehouse-cdc.yml` | только `workflow_dispatch` | ручной bounded CDC acceptance |
| Bounded serving runtime | `.github/workflows/lakehouse-serving.yml` | только `workflow_dispatch` | ручной bounded serving acceptance |
| Full acceptance | `.github/workflows/lakehouse-acceptance.yml` | только `workflow_dispatch` | перед контрольными переходами, не на каждый PR |

Frozen baseline F0 создаётся одноразово и не регенерируется CI.

CI-only реализация L3 не требует запуска полного Stage V E2E: manual acceptance
остаётся отдельным dispatch-only gate. Если изменение L3 затрагивает Compose,
runtime, DAG, dbt-проект, fixture или Stage V runner, граница меняется и решение
о полном прогоне принимается отдельно до его запуска.

---

## 2. Общий CI (`ci.yml`)

Workflow содержит стабильный агрегирующий check `ci-success` и следующие jobs:

1. `docs-and-repository-contracts` — syntax/link checks, compileall, fixture/oracle metadata, active legacy references and the independent L4 orphan inventory (`scripts/ci/check_legacy_orphans.py`).
2. `python-quality` — Ruff lint/format и Pyright по target paths.
3. `python-contract-tests` — pytest только по `tests/mysql`, `tests/cdc_contracts`, `tests/lakehouse_platform`, `tests/dbt_clickhouse`, `tests/serving`, `tests/stage_v`; нулевая коллекция является ошибкой.
4. `scala-fast` — scalafmt, compile, ScalaTest, package и проверка содержимого JAR.
5. `compose-contract` — `docker compose config` и статические инварианты services/profiles/images/secrets.
6. `airflow-dag-imports` — сборка целевого образа, отсутствие import errors, exact allowlist четырёх target DAG IDs (`olist_lakehouse_maintenance`, `olist_lakehouse_serving_sync`, `olist_lakehouse_quality`, `olist_lakehouse_serving_rebuild`) из двух target-файлов (`airflow/dags/olist_lakehouse_maintenance.py` и `airflow/dags/olist_lakehouse_serving.py`) и отсутствие old dbt path.
7. `dbt-clickhouse-static` — deps, parse, compile и model/source/selector contracts проекта `dbt/olist_clickhouse`.

Нельзя использовать `python -m unittest discover` как единственный test runner: он не гарантирует сбор module-level pytest tests.

---

## 3. Bounded component contracts (`lakehouse-components.yml`)

Этот workflow содержит только быстрые PR/push-проверки:

1. `spark-image-contract` — pinned image, offline entrypoint help, JAR/resources/classes, filesystem permissions и secret leakage;
2. `airflow-runtime` — запуск того же Airflow image, exact DAG inventory и bounded task path;
3. `observability-contract` — Compose/config/contract checks для target observability;
4. `component-summary` — итог только по реально запущенным contract jobs.

В workflow нет manual-only jobs и job-level условий, превращающих обязательную
проверку в `skipped`. Он использует path filters, отдельные Compose project
names, жёсткие timeouts и cleanup в `always()`. Полный V0–V10 или F1 он не
выполняет.

---

## 4. Bounded runtime acceptance

Тяжёлые runtime-проверки намеренно вынесены в отдельные workflow, чтобы они не
создавали `skipped` jobs в PR CI и запускались независимо:

1. `.github/workflows/lakehouse-cdc.yml` — `cdc-component`: bounded MySQL → Debezium → Kafka/Apicurio → Bronze/Silver, initial snapshot, catch-up и restart;
2. `.github/workflows/lakehouse-serving.yml` — `serving-component`: bounded input, Silver catch-up, finite serving sync, authoritative no-op retry, rebuild и maintenance path.

Оба workflow запускаются только через `workflow_dispatch`, используют малый
fixture, уникальный Compose project, bounded timeouts, failure diagnostics,
artifact evidence и cleanup в `always()`. В каждом workflow единственный
runtime job является обязательным: отсутствие его успеха означает failure.

## 5. Manual acceptance (`lakehouse-acceptance.yml`)

Workflow принимает `suite=candidate-e2e|final-parity|all`, полный `candidate_sha` и явное destructive confirmation.

Jobs:

1. `preflight`;
2. `stage-v-e2e` — полный clean V0–V10;
3. `final-parity` — candidate-only F1 против frozen oracle;
4. `publish-evidence` — выполняется всегда и не скрывает failure upstream job.

Destructive jobs используют protected environment и общий concurrency lock. F1 не запускает legacy; F0 oracle не изменяется этим workflow.

---

## 6. Обязательные свойства всех workflows

- `permissions: contents: read`, если job явно не требует большего;
- фиксированные версии actions и dependency caches, привязанные к lockfiles;
- job-level `timeout-minutes`;
- уникальный `COMPOSE_PROJECT_NAME` на run/attempt;
- загрузка JUnit/raw JSON/ограниченных логов при ошибке;
- очистка Docker resources при `always()`;
- отсутствие секретов в command output, artifacts и image metadata;
- итоговый статус вычисляется из фактических проверок; missing/skipped mandatory check не равен `PASS`. Автоматический component-contract workflow не содержит manual-only runtime jobs, а каждый dispatch-only bounded runtime workflow завершается failure, если его component job не завершился успешно.

---

## 7. Минимальное функциональное покрытие

### Python contracts

- MySQL DDL, users/grants, deterministic seed и fixture SHA;
- 8 CDC topics, Debezium MySQL connector и Apicurio compatibility;
- Polaris/Iceberg tables, migrations, Spark config/image и CLI JSON/redaction;
- Compose profile boundaries и readiness failures;
- serving boundary, transaction state, no-op/retry/rebuild semantics;
- dbt-clickhouse project и native ClickHouse DDL;
- Stage V gate registry, fail-fast и report integrity.

### Scala

- Confluent framing/schema IDs/references/fingerprints;
- 8 entity contracts и Debezium `c/r/u/d/tombstone`;
- UTC/microseconds/decimal normalization;
- event ID/dedup/order rules;
- idempotent MERGE, partial commits, transaction states и atomic status output.

### Repository architecture

- нет runtime references на NiFi, PostgreSQL OLTP, AWS cloud services/Redshift, old dbt project и old Compose profiles; локальные S3-compatible MinIO endpoints, `s3a://` paths и Iceberg S3 adapters разрешены как часть target object-store implementation;
- разрешены только документированные historical/provenance references;
- Airflow, dbt, Compose и documentation используют одинаковые target identifiers.

---

## 8. Выведенные из эксплуатации workflows

После CI cutover удаляются:

- `.github/workflows/batch-cdc-parity.yml`;
- `.github/workflows/cdc-stage2-kafka-debezium.yml`;
- `.github/workflows/cdc-stage6-operations.yml`.

Их PostgreSQL/NiFi/raw-CDC сценарии не должны сохраняться как необязательные зелёные проверки. Актуальные инварианты переносятся в target contract/component suites до удаления.

---

## 9. Связанные документы

- [Детальный план Stage L и CI cutover](../active/stage-l-legacy-removal-ci-cutover.md)
- [Реестр disposition legacy-артефактов](legacy-disposition-register.md)
- [Контракт target observability](observability.md)
- [Контракт target tests и evidence](testing-and-evidence.md)
- [План повторной приёмки E/V](../completed/stage-ev-validation-repair.md)
- [Контракт финального паритета](final-parity.md)
- [Контракт Spark](spark-streaming.md)
- [Контракт serving/recovery](serving-and-recovery.md)
