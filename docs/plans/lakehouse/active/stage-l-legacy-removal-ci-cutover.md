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

Должны сохраниться и проходить проверки:

- MySQL 8.4 source: базы olist_oltp и olist_simulator, binlog ROW/GTID, точная source schema и file-only secrets.
- Target Debezium/Kafka Connect bootstrap, MySQL connector contract, Apicurio compatibility и Kafka topic manifest.
- Kafka, Apicurio Registry 3.3.0, MinIO, Polaris, Spark master/worker/bronze/silver/geolocation/ops, ClickHouse serving и Airflow.
- Control PostgreSQL и только target DAG inventory: olist_lakehouse_maintenance.py и olist_lakehouse_serving.py.
- dbt/olist_clickhouse, scripts/serving и final parity/F0 readers.
- ScalaTest и target suites tests/mysql, tests/cdc_contracts, tests/lakehouse_platform, tests/dbt_clickhouse, tests/serving и tests/stage_v.
- Actual observability chain: metric producer → Compose service/exporter → Prometheus scrape job → recording/alert rule → dashboard/runbook → acceptance check.

Текущий runtime contract указывает Debezium Connect 3.6.0.Final в streaming/runtime-versions.json и architecture/runtime contracts. Версию нельзя понижать до 3.0.0.Final без отдельного изменения contract, image/plugin inventory и тестов.

## 3. L0 — baseline reset и inventory review

Это подготовительный gate, а не реализация нового runtime.

- После явного подтверждения выполнить rollback текущего незавершённого набора изменений к чистому рабочему дереву.
- Зафиксировать baseline commit, список целевых файлов, список legacy файлов и исходный Stage V E2E результат.
- Сопоставить каждый legacy workflow, script, test, fixture и secret template с disposition KEEP, REWRITE, REPLACE, DELETE или HOLD/DEFER. Четыре первых решения фиксируют целевую судьбу артефакта, но не требуют заранее детализировать реализацию; HOLD/DEFER используется, когда сначала нужен дополнительный runtime или consumer evidence.
- Проверить, что план Stage L находится в active, а serving-cutover и master plan не объявляют L complete.

Disposition register для L0 должен содержать path, роль артефакта, найденных consumers, target contract, выбранное disposition, подстадию-владельца, replacement test/evidence и условие удаления. Неопределённый или неподтверждённый DELETE запрещён; HOLD/DEFER должен быть разрешён до L4.

Exit criteria:

- чистое baseline дерево;
- inventory review с отсутствующими orphan consumers;
- согласованный disposition register без неподтверждённых DELETE;
- F0 oracle/readers не изменены;
- известные baseline failures записаны отдельно от acceptance evidence.

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
- Переписать stage2_admin на MySQL connector name/plugin/topic contract либо удалить его только вместе с доказанным отсутствием consumers.
- Согласовать Compose image, runtime-versions и contract versions; не делать silent Debezium downgrade.
- Исправить env names: KAFKA_CONNECT_HOST_PORT должен совпадать с Compose, а все используемые secret source variables должны быть документированы.

Exit criteria:

- target contract/unit suites проходят;
- local_lab import/bootstrap paths не ссылаются на отсутствующие файлы;
- clean Stage V E2E V0–V10 PASS;
- raw evidence и checksum сохранены в data/stage-l-evidence/L1/.

## 5. L2 — observability для нового стека

Observability является обязательной частью миграции. Её можно реализовать отдельным этапом, но Stage L нельзя объявлять complete с phantom targets или legacy alerts.

### Runtime mapping

Для каждого target job сначала зафиксировать producer, endpoint, Compose service и healthcheck. Допустимы два решения: добавить pinned exporter service либо настроить реальный metrics endpoint существующего компонента. Нельзя оставлять ссылки на несуществующие services вроде mysql-exporter, spark-iceberg, cdc-component-exporter, cdc-pipeline-exporter, kafka-exporter, statsd-exporter, node-exporter или cadvisor без соответствующих Compose definitions.

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
- Redshift infra, Redshift-only utilities/dependencies и old raw batch paths;
- старые ClickHouse raw CDC/batch/runtime paths, если target dbt/serving paths не используют их;
- deleted legacy GitHub workflows и их orphan CI scripts;
- old PostgreSQL oracle fixtures после принятия F0 и подтверждения отсутствия consumers.

### Обязательная orphan scan перед delete

Нужно отдельно проверить и затем удалить или переписать текущие остатки:

- scripts/cdc/realtime_transform.py и scripts/ci/check_dbt_selector_boundaries.py;
- scripts/cdc/warehouse_ingest.py и pipeline_metrics.py;
- scripts/utilities/generate_redshift_raw_ddl.py;
- streaming/minio/init.sh, streaming/minio/README.md и nifi-policy;
- streaming/runtime-versions.json entries for NiFi;
- _nifi_written_at в active schemas/ClickHouse raw DDL;
- old connector names, old DBT paths, redshift/public/simulator_control references.

### Что сохраняется

- control PostgreSQL;
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
- Не добавлять plaintext secrets, --password CLI или password fields в state objects.
- Не добавлять Prometheus targets, dashboards или chaos commands для несуществующих services.
- Не объявлять Stage L complete при failed/missing E2E gates, только на основании handoff или локального unit-test count.
