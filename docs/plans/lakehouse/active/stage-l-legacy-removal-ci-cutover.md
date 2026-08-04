# Детальный план Stage L: поэтапный target cutover

- Статус: ACTIVE.
- Цель: перевести репозиторий с legacy PostgreSQL/NiFi/старого raw batch/realtime pipeline на согласованный MySQL → Debezium → Kafka → Spark/Iceberg → ClickHouse serving stack, сохранив проверяемость каждого перехода.
- Ограничение: Stage L не считается завершённой по декларации. Каждый gate закрывается raw evidence, привязанным к candidate commit SHA.

## 1. Правила выполнения

1. Перед началом реализации рабочее дерево возвращается к чистому baseline после отдельного подтверждения destructive rollback. Handoff, незавершённые удаления и неподтверждённые отчёты не являются источником истины.
2. После каждой подстадии L1–L4 обязателен полный clean Stage V E2E V0–V10. Evidence сохраняется в data/stage-l-evidence/<substage>/<run-id>/.
3. Зеленый unit/contract CI не заменяет runtime E2E. Пропущенный обязательный gate означает FAIL.
4. Тесты нельзя удалять для уменьшения testpaths или получения зелёного CI. Сначала должен существовать target replacement либо должен быть удалён весь код, который тест проверял.
5. Frozen F0 oracle, его metadata и reader не изменяются и не удаляются.
6. Любой runtime, exporter, DAG, schema или workflow должен иметь один явный owner и один проверяемый contract.

## 2. Target inventory и invariants

Cloud boundary: AWS/Redshift cloud artifacts are removed in L4; GCP/BigQuery is a separate future program described in [GCP migration plan](../../gcp-spark-iceberg-bigquery-migration.md) and is not implemented by Stage L. Local MinIO S3-compatible endpoints, `s3a://` paths and the Iceberg S3 adapter remain where they are the target object-store implementation; they are not AWS cloud infrastructure.

Нормативные артефакты L0:

- [Отчёт baseline L0](../../../reports/lakehouse-stage-l0-baseline.md) — фактический rollback, запуск E2E и static findings; статус обновляется после завершения процесса.
- [Реестр disposition legacy-артефактов](../contracts/legacy-disposition-register.md) — построчное решение `KEEP`, `REWRITE`, `REPLACE` или `DELETE` и условие удаления.
- [Контракт target observability](../contracts/observability.md) — producer/exporter/scrape/rule/dashboard/evidence chain и текущие phantom-target gaps.
- [Контракт target tests и evidence](../contracts/testing-and-evidence.md) — обязательные suites, transfer rules и разделение baseline diagnostic от acceptance evidence.
- [Контракт validation и CI](../contracts/validation-and-ci.md) — required common/bounded/manual workflows и запрет skipped/missing acceptance jobs.

Должны сохраниться и проходить проверки:

- MySQL 8.4 source: базы olist_oltp и olist_simulator, binlog ROW/GTID, точная source schema и file-only secrets.
- Target Debezium/Kafka Connect bootstrap, MySQL connector contract, Apicurio compatibility и Kafka topic manifest.
- Kafka, Apicurio Registry 3.3.0, MinIO, Polaris, Spark master/worker/bronze/silver/geolocation/ops, ClickHouse serving и Airflow.
- Target serving control PostgreSQL и только target DAG inventory: два target-файла `olist_lakehouse_maintenance.py` и `olist_lakehouse_serving.py`, экспортирующие ровно четыре DAG ID: `olist_lakehouse_maintenance`, `olist_lakehouse_serving_sync`, `olist_lakehouse_quality`, `olist_lakehouse_serving_rebuild`.
- dbt/olist_clickhouse, scripts/serving и final parity/F0 readers.
- ScalaTest и target suites tests/mysql, tests/cdc_contracts, tests/lakehouse_platform, tests/dbt_clickhouse, tests/serving и tests/stage_v.
- Actual observability chain: metric producer → Compose service/exporter → Prometheus scrape job → recording/alert rule → dashboard/runbook → acceptance check.

Текущий runtime contract указывает Debezium Connect 3.6.0.Final в streaming/runtime-versions.json и architecture/runtime contracts. Версию нельзя понижать до 3.0.0.Final без отдельного изменения contract, image/plugin inventory и тестов.

## 3. L0 — baseline reset и inventory review

Это подготовительный gate, а не реализация нового runtime.

- Rollback текущего незавершённого набора изменений выполнен к чистому дереву на baseline commit `9214cd1de05ab37cdeae27a1a0b633963e8ae8d6`; committed plan Stage L сохранён.
- Сразу после rollback запущен baseline Stage V E2E `stage_l0_baseline_20260804`; он прошёл V0–V9 и упал на V10 из-за raw-vs-effective transaction-state проверки. Команда и evidence root зафиксированы в [реестре disposition](../contracts/legacy-disposition-register.md); этот failure является baseline diagnostic, а не acceptance evidence.
- После анализа выполнен отдельный clean corrective run `stage_l0_v10fix_20260804`: targeted `validate-final` effective-state fix дал V0–V10 `PASS`, без ручной мутации данных. Этот результат не закрывает обязательные L1 writer/materializer/planner regression work.
- Зафиксированы baseline commit, fixture SHA-256, target inventory, legacy inventory и исходный Stage V E2E run в [реестре disposition](../contracts/legacy-disposition-register.md).
- Каждый legacy workflow, script, test, fixture и secret template сопоставлен ровно с одним из четырёх disposition: `KEEP`, `REWRITE`, `REPLACE` или `DELETE`. AWS/Redshift не являются совместимым или отложенным scope: для них зафиксирован только `DELETE`. Четыре решения фиксируют целевую судьбу артефакта, но не утверждают реализацию будущей стадии.
- Проверить, что план Stage L находится в active, а serving-cutover и master plan не объявляют L complete.

Disposition register для L0 должен содержать path, роль артефакта, найденных consumers, target contract, выбранное disposition, подстадию-владельца, replacement test/evidence и условие удаления. Неопределённый или неподтверждённый DELETE запрещён; новые исключения из четырёх решений требуют отдельного consumer evidence и не могут использоваться для сохранения AWS/Redshift.

Exit criteria:

- чистое baseline дерево;
- inventory review с зафиксированными consumers и явными orphan-scan gates перед каждым DELETE;
- согласованный disposition register без неподтверждённых DELETE;
- F0 oracle/readers не изменены;
- известные baseline failures записаны отдельно от acceptance evidence;
- baseline и corrective E2E outcomes дописаны в register/report; их статусы не подменяются декларацией о завершении Stage L.

## 4. L1 — target contracts, tests и runtime repair

Сначала восстанавливается проверяемость target stack, затем чинятся дефекты, обнаруженные ревью.

### Обязательное тестовое покрытие

Восстановить или перенести, не обязательно сохраняя старые имена:

- tests/mysql/test_cli.py, test_mysql_integration.py, test_repository.py и test_seeding.py;
- tests/cdc_contracts/test_connector_bootstrap.py;
- tests/test_simulation.py и tests/test_oltp_seed_contracts.py;
- tests/test_stage2_configuration.py;
- tests/test_control_postgres_phase2.py;
- tests/test_airflow_secret_bootstrap.py;
- tests/test_avro_schema_compatibility.py;
- data-quality/dead-letter invariants из tests/test_ci_data_quality_failures.py и tests/test_dead_letter_pipeline.py, если соответствующий ingestion/loading code остаётся;
- observability invariants из tests/test_clickhouse_phase7_ci_observability.py в target lakehouse suite.

Оставшийся tests/mysql/test_source_schema.py должен проверять как schema, так и отсутствие plaintext password state и MySQL-specific DML invariants. Текущий testpath не должен скрывать root tests до переноса их общих invariants.

### Runtime fixes

- Переписать seed полностью на mysql.connector и MySQL SQL: квалификация olist_oltp/olist_simulator, ON DUPLICATE KEY UPDATE, корректный composite-key upsert, Decimal conversion, batch contract 5000, seed idempotency и transaction-per-entity.
- Убрать PostgreSQL execute_values, ON CONFLICT, public.*, simulator_control и ::jsonb из target simulator.
- Вернуть явные transaction boundaries, rollback/commit, failure persistence, graceful stop и Decimal-compatible replay speed. Не вводить plaintext --password/state в CLI или DatabaseSettings.
- Вернуть target streaming/connect bootstrap и MySQL connector template, которые вызываются из local_lab. Удаление всего streaming/connect недопустимо.
- Переписать `stage2_admin` на MySQL connector name/plugin/topic contract; его текущие `local_lab`/CDC consumers не удаляются в рамках этой стадии.
- Перевести `docs/source_profile.json`, `tests/fixtures/olist_small/source_profile_small.json` и fixture generator на target-neutral metadata: активные `redshift_raw_type` поля не должны пережить L1.
- Переписать `infra/control-postgres` bootstrap и `scripts/serving/control.py` на target-owned `serving.*` schema checks; legacy `audit`/`cdc_audit` migrations остаются до L4 только при наличии replacement evidence.
- Разобрать failure baseline E2E: в run `stage_l0_baseline_20260804` все V0–V9 прошли, но V10/`10-final` увидел одну сырую `OPEN` audit observation. L0 diagnostic run `stage_l0_v10fix_20260804` подтвердил effective-state explanation и получил новый clean PASS без ручного SQL; L1 всё равно обязан закрепить это поведение в writer/materializer/planner contracts и regression tests.
- Зафиксировать transaction-state invariant как отдельный L1 deliverable: `audit.mysql_transactions` может быть append-only observation history, но serving planner и V10 обязаны читать effective state. BEGIN и END, разделённые micro-batches, должны схлопываться в `COMPLETE`; настоящий незавершённый BEGIN не может исчезать из planner только потому, что у него `end_kafka_offset IS NULL`. Добавить regression coverage для split BEGIN/END, unresolved OPEN, `REJECTED → COMPLETE`, duplicate END и offset/order checks в Scala/serving tests.
- Для этого адресно переписать `TransactionBatchWriter.scala`, `scripts/serving/clickhouse.py`, `scripts/serving/boundary.py`, target serving DAG и `local_lab.py`; остальные target data-plane/serving файлы не являются кандидатами на массовое удаление.
- Устранить побочный эффект `_capture_and_contracts`: baseline/E2E capture не должен перезаписывать tracked `streaming/schemas/captured-writer-schemas/**` динамическими timestamp/provenance. Runtime capture должен оставаться в temp/evidence, а изменение frozen writer bundle допускается только отдельным contract-driven commit.
- Согласовать Compose image, runtime-versions и contract versions; не делать silent Debezium downgrade.
- Исправить env names: KAFKA_CONNECT_HOST_PORT должен совпадать с Compose, а все используемые secret source variables должны быть документированы.

Exit criteria:

- target contract/unit suites проходят;
- local_lab import/bootstrap paths не ссылаются на отсутствующие файлы;
- clean Stage V E2E V0–V10 PASS;
- raw evidence и checksum сохранены в data/stage-l-evidence/L1/.

### L1 implementation result (2026-08-04)

- [Stage L1 implementation report](../../../reports/lakehouse-stage-l1.md)
  records the completed target-runtime repairs and the diagnostic history.
- Clean acceptance evidence is in
  `data/stage-l-evidence/L1/stage_l1_20260804_v6/`; run
  `stage_l1_20260804_v6` passed every Stage V gate V0-V10.
- The preceding v3, v4 and v5 failures were diagnosed and fixed: probe
  identity, candidate-tree formatting, and the simulator/admin credential
  split for additive DDL.
- No tests were deleted. Legacy control migrations remain during the
  compatibility window and are owned by L4 removal evidence. AWS/Redshift
  artifacts have disposition `DELETE`; they are not deferred, while
  GCP/BigQuery remains a separate future program.
- L1 completion means that the repaired target candidate is green under the
  full runtime gate. It does not close Stage L; L2 observability, L3 CI and
  L4 legacy removal still require their own changes and clean V0-V10 evidence.

## 5. L2 — observability для нового стека

Observability является обязательной частью миграции. Её можно реализовать отдельным этапом, но Stage L нельзя объявлять complete с phantom targets или legacy alerts.

### Runtime mapping

Для каждого target job сначала зафиксировать producer, endpoint, Compose service и healthcheck. Допустимы два решения: добавить pinned exporter service либо настроить реальный metrics endpoint существующего компонента. Нельзя оставлять ссылки на несуществующие services вроде mysql-exporter, spark-iceberg, cdc-component-exporter, cdc-pipeline-exporter, kafka-exporter, statsd-exporter, node-exporter или cadvisor без соответствующих Compose definitions.

Для Alertmanager и Alloy решение уже принято: L2 добавляет реальные pinned services, потому что они входят в target alert/log chain. Для Airflow старый StatsD mapping заменяется health/API probe; нереализованный target нельзя оставить в контракте без owner, endpoint и acceptance evidence.

Минимальный target coverage:

- MySQL availability/binlog/replication health;
- Debezium Connect REST, connector/task state и heartbeat;
- Kafka broker/topic/consumer lag с фильтрацией только target consumer groups;
- Spark Bronze/Silver/ops health и streaming progress;
- MinIO/Polaris/ClickHouse serving;
- Airflow/serving/control-plane metrics;
- Prometheus/Grafana/Loki/Alloy self-health.

### Cleanup и contracts

- Удалить или переписать NiFi dashboards, queue metrics, NiFi-specific MinIO policy/secret и PostgreSQL WAL alerts.
- Удалить CdcRetainedWalHighAndGrowing и другие PostgreSQL source alerts, если их нельзя доказать на target source.
- Не заменять scoped Kafka lag на sum всех kafka_consumergroup_lag; selector должен ограничивать target groups/topics.
- Проверять YAML/JSON schema, target host existence, alert metric existence, dashboard query references и runbook links.
- Chaos commands должны использовать реальные Compose service names и уникальный project name. Например, kafka-connect, spark-bronze/spark-silver или выделенный target Spark service, а не fictitious debezium и spark-iceberg.

Exit criteria:

- все configured scrape targets существуют и проверяемо UP в healthy stack;
- target alerts fire and resolve на bounded fault injection;
- Grafana dashboards не содержат 404/phantom metric panels;
- clean Stage V E2E V0–V10 PASS плюс observability acceptance evidence в data/stage-l-evidence/L2/.

## 6. L3 — CI и acceptance cutover

### Required common CI

Обязательные jobs:

- docs/repository contracts: YAML/TOML/Markdown links, compileall, expanded legacy guard и F0 validation;
- python-quality: ruff check, ruff format --check, pyright;
- python-contract-tests: explicit target suites, JUnit artifact и fail при zero collection;
- scala-fast: scalafmt, Test/compile, ScalaTest, package и JAR content/dependency contract;
- compose-contract: all relevant profiles, exact service inventory, no container_name, image/config/secret assertions;
- airflow-dag-imports: build target Airflow image, exact DAG inventory и dbt path contract;
- dbt-clickhouse-static: deps, parse, compile, selector/source/model contract;
- ci-success: if always(), fail on failed или skipped required jobs.

Каждый job получает timeout, lockfile cache, pinned major actions, read-only permissions и failure artifacts/JUnit. Compose config alone не считается service inventory check.

### Bounded component CI

Сохраняются четыре реальных bounded jobs: spark-image-contract, cdc-component, serving-component и airflow-runtime. Observability contract checks добавляются как отдельная bounded часть либо в cdc/serving component, но не заменяются echo-only summary.

Path filters не должны позволять component-summary объявить успех при пропущенном или failed component. Manual component input airflow обязан запускать airflow-runtime.

### Manual acceptance

- preflight проверяет полный candidate SHA, fixture/oracle checksums, inputs, capacity и уникальный Compose project;
- stage-v-e2e запускает полный scripts/validation/stage_v_candidate_e2e.py, а не только tests/stage_v;
- final-parity сравнивает candidate-only output с frozen F0 oracle;
- publish-evidence загружает raw JSON, Markdown, JUnit, selected logs и итоговый failure status;
- F0 никогда не регенерируется acceptance workflow.

Exit criteria:

- common CI и релевантные bounded jobs зелёные на candidate;
- manual acceptance preflight и полный Stage V E2E PASS;
- clean Stage V E2E V0–V10 PASS после CI changes;
- evidence сохранён в data/stage-l-evidence/L3/.

## 7. L4 — legacy removal

Удаление выполняется только после L1–L3 и mapping review.

### Разрешённые удаления после проверки consumers

- старый PostgreSQL OLTP infra и старые PostgreSQL source secrets;
- NiFi runtime, NiFi workflows/scripts/tests, NiFi-specific MinIO assets и runtime-version entries;
- старые PostgreSQL/legacy DAGs;
- dbt/olist_analytics и связанные old batch/realtime selectors;
- Redshift infra, Redshift-only utilities/dependencies и old raw batch paths, поскольку AWS/Redshift полностью выводятся из программы; будущий GCP stack является отдельным cloud-планом;
- legacy control PostgreSQL `audit`/`cdc_audit` DDL после переноса их проверяемых invariants в Spark/serving target owners;
- старые ClickHouse raw CDC/batch/runtime paths, если target dbt/serving paths не используют их;
- deleted legacy GitHub workflows и их orphan CI scripts;
- old PostgreSQL oracle fixtures после принятия F0 и подтверждения отсутствия consumers.

### Обязательная orphan scan перед delete

Нужно отдельно проверить и затем удалить или переписать текущие остатки:

- scripts/cdc/realtime_transform.py и scripts/ci/check_dbt_selector_boundaries.py;
- scripts/cdc/warehouse_ingest.py и pipeline_metrics.py;
- scripts/utilities/generate_redshift_raw_ddl.py;
- unused streaming/minio/init.sh, stale MinIO policies and old README instructions; retain only the target `streaming/minio/Dockerfile`/`start.sh` plus `infra/polaris/minio/**` initializer and policies;
- streaming/runtime-versions.json entries for NiFi;
- _nifi_written_at в active schemas/ClickHouse raw DDL;
- old connector names, old DBT paths, redshift/public/simulator_control references.

### Что сохраняется

- target serving control PostgreSQL с только target-owned schema/migrations;
- target MySQL infra/schema/simulator;
- target Debezium/Kafka Connect bootstrap and MySQL contract;
- target Kafka/Apicurio/Spark/Iceberg/Polaris/ClickHouse serving/Airflow;
- target observability;
- F0 oracle/readers and final-parity fixture;
- all target test suites and Scala tests.

Exit criteria:

- expanded guard and independent rg scan find zero disallowed active references outside explicit historical allowlist;
- exact DAG/service/dbt inventory matches target architecture;
- clean Stage V E2E V0–V10 PASS;
- evidence сохранён в data/stage-l-evidence/L4/.

## 8. L5 — final Stage L gate

Stage L получает COMPLETE только если одновременно выполнены:

- L1, L2, L3 и L4 gates PASS;
- common CI, bounded component workflows и manual acceptance PASS;
- observability normal scrape и fire/resolve evidence PASS;
- target tests retained/migrated, а удалённые тесты имеют mapping;
- legacy runtime/config/dependencies/secrets/active CI references отсутствуют;
- F0 oracle/readers unchanged;
- candidate и evidence привязаны к точным SHA.

Только после этого serving-cutover переводится с L ACTIVE на L COMPLETE, а Stage F1 становится NEXT.

## 9. Что делать точно не нужно

- Не удалять target tests только потому, что они лежат в tests/test_*.py.
- Не удалять весь streaming/connect: там находятся target Debezium/MySQL bootstrap и contract artifacts.
- Не переписывать simulator semantics в рамках cleanup без contract-driven tests.
- Не понижать pinned runtime version без обновления всех contracts и acceptance checks.
- Не переносить AWS/Redshift runtime в GCP автоматически в рамках Stage L: GCP — отдельная программа с собственными контрактами и consumer review.
- Не добавлять plaintext secrets, --password CLI или password fields в state objects.
- Не добавлять Prometheus targets, dashboards или chaos commands для несуществующих services.
- Не удалять локальный MinIO S3-compatible adapter только из-за имён `AWS`/`S3` в библиотечном/API слое; удаляются AWS cloud/Redshift consumers, а не необходимый target object-store protocol.
- Не объявлять Stage L complete при failed/missing E2E gates, только на основании handoff или локального unit-test count.
