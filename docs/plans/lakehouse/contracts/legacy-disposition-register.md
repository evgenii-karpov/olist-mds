# L0: Реестр решений по legacy-артефактам

- **Статус**: действующий реестр Stage L, зафиксирован на L0.
- **Назначение**: сохранить проверяемое решение о судьбе каждого runtime/CI/test/fixture/secret артефакта, который относится к удаляемому PostgreSQL/NiFi/Redshift/старому raw batch или старому dbt контуру.
- **Граница**: исторические планы, handoff-документы и отчёты не являются runtime-артефактами этого реестра. Они сохраняются как provenance, если на них нет требования удалить устаревшую активную инструкцию.
- **Cloud boundary**: AWS/Redshift не являются deferred target и удаляются в L4; будущий GCP/BigQuery stack описан отдельно в [GCP migration plan](../../gcp-spark-iceberg-bigquery-migration.md). Это не запрещает локальный S3-compatible путь через MinIO и нужные для него Iceberg `S3FileIO`/S3A adapters: они не являются AWS cloud runtime и не должны быть удалены механически.
- **Порядок авторитетности**: для disposition используется этот реестр; реализационные детали и gate-порядок находятся в [плане Stage L](../active/stage-l-legacy-removal-ci-cutover.md), а target contracts имеют приоритет над историческими документами.

## 1. Правила disposition

| Решение | Смысл на L0 | Условие перехода к удалению/замене |
| --- | --- | --- |
| `KEEP` | Артефакт уже принадлежит target-стеку или является frozen provenance/F0 input. | Не удалять в Stage L; изменения допускаются только contract-driven. |
| `REWRITE` | Путь и роль полезны, но реализация содержит legacy semantics, имена, endpoints или границы. | Переписать на указанного target owner и покрыть target test/evidence. |
| `REPLACE` | Старый артефакт не должен сохраняться, но его проверяемая ответственность нужна target-стеку. | Сначала добавить/принять replacement, затем удалить старый путь после orphan scan. |
| `DELETE` | У артефакта нет target ответственности; он не является F0/F1 provenance. | Удалять только после указанного consumer/removal check. |

Этот реестр намеренно использует только четыре решения. В нём нет статусов `HOLD` или `DEFER`: AWS/Redshift имеют только `DELETE`, а будущий GCP/BigQuery stack ведётся отдельной программой.

`DELETE` в этом документе означает решение о целевой судьбе, а не разрешение удалить файл немедленно. До L4 запрещено удалять строку из реестра или сам файл без выполнения условия удаления.

## 2. Baseline L0

| Поле | Значение |
| --- | --- |
| Baseline commit | `9214cd1de05ab37cdeae27a1a0b633963e8ae8d6` (`docs(lakehouse): sequence Stage L into gated cutover stages`) |
| Working tree | Чистое после возврата tracked и untracked изменений к baseline; committed Stage L plan сохранён. |
| Frozen F0 source | `1400d08345ad81a0121f0ee85ee9ae81cd575a73` |
| Frozen fixture | `tests/fixtures/olist_small/olist_small.zip` |
| Fixture SHA-256 | `5cf2ff7a104cae75d8a56cf8c6e00959894154a8d55aed2ddf0e3fa133a13976` |
| Baseline E2E run | `stage_l0_baseline_20260804` |
| E2E command | `uv run python scripts/validation/stage_v_candidate_e2e.py run --run-id stage_l0_baseline_20260804 --evidence-dir data/stage-l0-baseline-e2e --confirm-reset` |
| E2E evidence root | `data/stage-l0-baseline-e2e/` |
| E2E result | `FAIL`; `00-preflight`–`09-rebuild` `PASS`, first failed gate `10-final`; the raw final audit query reported one `OPEN` observation, without a transaction ID. Evidence: `data/stage-l0-baseline-e2e/`; runner cleanup was `SKIPPED` for diagnostics, then the exact `olist_stage_v` project was manually cleaned. |
| Corrective V10 run | `stage_l0_v10fix_20260804`; evidence `data/stage-l0-v10fix-e2e/`; same clean-reset runner after a targeted effective-state `validate-final` query fix. |
| Corrective V10 result | `PASS`; `00-preflight`–`10-final` passed, `open_or_rejected_transactions` was empty, and the runner completed normal cleanup. This is diagnostic evidence for the validator/history mismatch, not completion of L1 transaction-lifecycle work. |
| Target test collection at L0 | 188 tests collected from the explicit target suite paths; collection-only command completed successfully. |
| Target suite baseline at L0 | `186 passed, 2 skipped, 86 subtests passed`; no legacy tests were needed to obtain this result. |

Этот baseline run отделён от будущего acceptance evidence. Если baseline E2E не проходит, failure фиксируется как baseline diagnostic и не превращается в acceptance `PASS`.

## 3. Workflows и DAGs

| Path | Текущая роль и consumers | Target contract / replacement evidence | Disposition | Owner stage | Условие удаления |
| --- | --- | --- | --- | --- | --- |
| `.github/workflows/ci.yml` | Старый монолит: `dbt/olist_analytics`, NiFi, realtime-core и raw batch jobs; branch-protection entry point. | [Validation & CI](validation-and-ci.md): `ci-success`, repository contracts, target Python/Scala/Compose/Airflow/dbt-clickhouse jobs. | `REWRITE` | L3 | Старые jobs перенесены в target matrix, zero skipped required jobs доказан. |
| `.github/workflows/batch-cdc-parity.yml` | Manual batch + NiFi/raw CDC parity workflow. | `lakehouse-components.yml` `cdc-component`/`serving-component` и manual Stage V/F1 acceptance. | `REPLACE` | L3 | Replacement workflow зелёный и все non-legacy invariants имеют target test/evidence. |
| `.github/workflows/cdc-stage2-kafka-debezium.yml` | PostgreSQL/NiFi-era CDC capture drill. | Target MySQL → Debezium → Kafka/Apicurio bounded `cdc-component`. | `REPLACE` | L3 | Target connector/CRUD/restart checks green; legacy workflow has no consumer. |
| `.github/workflows/cdc-stage6-operations.yml` | Phase 6 alert/failure-injection workflow с NiFi/PostgreSQL metrics. | [Observability contract](observability.md) и target bounded observability acceptance. | `REPLACE` | L2/L3 | Target fire/resolve evidence опубликован; old alert names and service references absent. |
| `.github/workflows/lakehouse-components.yml` | Missing target bounded-component workflow required by the CI contract. | [Validation & CI](validation-and-ci.md): Spark, CDC, serving, Airflow and observability bounded jobs. | `REPLACE` | L3 | Add and pass the target workflow before deleting its legacy predecessors. |
| `.github/workflows/lakehouse-acceptance.yml` | Missing target manual full-acceptance workflow required by the CI contract. | [Validation & CI](validation-and-ci.md): preflight, full Stage V E2E, F1 and evidence publication. | `REPLACE` | L3 | Add and pass the target workflow before deleting legacy manual acceptance paths. |
| `airflow/dags/olist_cdc_local.py` | NiFi/raw CDC ingest and backfill DAGs. | `olist_lakehouse_serving.py` + Spark continuous services; Airflow boundary in `serving-and-recovery.md`. | `DELETE` | L4 | Exact target DAG inventory passes and no workflow/script/doc runtime consumer remains. |
| `airflow/dags/olist_cdc_dbt_local.py` | Old realtime dbt transform/quality DAGs. | Target finite serving/quality DAGs and Scala Spark Silver. | `DELETE` | L4 | Target DAG import check passes; old dbt project/selectors have no consumers. |
| `airflow/dags/olist_modern_data_stack_local.py` | Old local raw batch pipeline. | Target `olist_lakehouse_serving.py` and `olist_lakehouse_maintenance.py`. | `DELETE` | L4 | Batch raw DAG path and its scripts are removed/replaced; exact DAG allowlist passes. |
| `airflow/dags/olist_modern_data_stack_aws.py` | AWS/Redshift raw batch pipeline; AWS is explicitly out of the target architecture. | No target replacement in local Stage L; future cloud stack is GCP and is a separate program. | `DELETE` | L4 | Remove the DAG and all active AWS/Redshift consumers; retain only historical provenance in Git history. |

## 4. CDC, simulator и orchestration scripts

| Path | Текущая роль и consumers | Target contract / replacement evidence | Disposition | Owner stage | Условие удаления |
| --- | --- | --- | --- | --- | --- |
| `scripts/cdc/local_lab.py` | Главный local target CLI, но содержит старые defaults/профили и является consumer bootstrap; его V10 final check должен проверять effective transaction state, а не исторические OPEN observations. | `architecture-and-runtime.md`, Stage V V0–V10, `tests/lakehouse_platform`, Stage E latest-effective transaction contract. | `REWRITE` | L1 | Local CLI contract, effective OPEN/REJECTED diagnostic and clean Stage V E2E PASS. |
| `scripts/cdc/stage2_admin.py` | Регистрация connector; сейчас ссылается на PostgreSQL connector template/name. | `streaming/connect/olist-mysql-cdc.json`, `tests/cdc_contracts/test_connector_bootstrap.py`. | `REWRITE` | L1 | MySQL connector/topic contract и runtime status checks green. |
| `scripts/cdc/avro_wire.py` | Старый helper, consumer только old Stage 2 integration. | `streaming.schemas.avro`/registry helpers и `tests/cdc_contracts`. | `REPLACE` | L1 | Target helper/tests cover framing, schema IDs and tombstones. |
| `scripts/cdc/benchmark_local.py` | Benchmark old raw ingest/realtime transform latency. | Target observability/latency evidence from `observability.md`; no legacy warehouse query. | `REPLACE` | L2 | Target benchmark/probe exists or bounded observability suite owns the metric. |
| `scripts/cdc/failure_injection.py` | Compose failure drills use old service names and old alert model. | Target service names and fire/resolve checks in `observability.md`. | `REWRITE` | L2 | All scenarios use real target services and target alert identities. |
| `scripts/cdc/pipeline_metrics.py` | Prometheus exporter for old raw CDC/warehouse/control tables. | Target Spark/Iceberg/serving metrics producer or explicit bounded exporter. | `REPLACE` | L2 | Every retained metric has a real producer and target scrape owner. |
| `scripts/cdc/realtime_transform.py` | Old dbt realtime transform over `dbt/olist_analytics` and control state. | Spark Silver is the transform owner; target dbt project is `dbt/olist_clickhouse`. | `DELETE` | L4 | Old DAG/selectors/project have no consumers and target serving evidence is green. |
| `scripts/cdc/warehouse_ingest.py` | NiFi/MinIO Parquet manifest loader into raw ClickHouse. | Spark Bronze/Silver and target serving sync; `spark-streaming.md`, `serving-and-recovery.md`. | `DELETE` | L4 | Old ingest DAG, S3 layouts, tests and metrics replacement are all complete; orphan scan clean. |
| `scripts/__init__.py` | Python package marker for repository automation. | Target scripts package imports. | `KEEP` | L1–L4 | Retain while target scripts remain in the repository. |
| `scripts/cdc/README.md` | Documentation still describes the removed Phase 5 raw ClickHouse/PostgreSQL control path. | Target MySQL/Debezium/Kafka/Spark/Iceberg CDC path and `observability.md`. | `REWRITE` | L1/L2 | Rewrite commands and ownership before legacy CDC files are removed. |
| `scripts/ingestion/__init__.py` | Package marker for the legacy raw-file ingestion family. | No target package owner after Bronze/MySQL replacement. | `DELETE` | L4 | Remove with the last legacy `scripts.ingestion` consumer after orphan scan. |
| `scripts/loading/__init__.py` | Package marker for the legacy raw-batch loading family. | Target serving/Spark paths. | `DELETE` | L4 | Remove with the last legacy `scripts.loading` consumer after replacement evidence. |
| `scripts/orchestration/__init__.py` | Package marker shared by legacy batch orchestration modules. | Target serving control client is owned by `scripts/serving/control.py`. | `DELETE` | L4 | Remove after legacy orchestration modules and imports are gone. |
| `scripts/quality/__init__.py` | Package marker for legacy raw-batch quality modules. | Target quality DAG, Stage V and F1 evidence. | `DELETE` | L4 | Remove after target quality replacement and orphan scan. |
| `scripts/ci/pipeline_helpers.py` | Shared helpers for old CI integrations and control/warehouse clients. | Target workflow-local helpers and repository contracts from `validation-and-ci.md`. | `REPLACE` | L3 | All active workflows use target helpers; no import remains. |
| `scripts/ci/check_batch_cdc_parity_integration.py` | Full old batch-vs-NiFi/realtime integration runner. | Target bounded components + Stage V/F1; preserve only explicit invariants. | `REPLACE` | L3 | Invariants mapped to target tests/evidence; no old runner consumer. |
| `scripts/ci/check_clickhouse_cdc_ingest_resilience.py` | Raw CDC S3/ClickHouse ingest resilience. | Target Spark/Iceberg durability and serving recovery checks. | `REPLACE` | L2/L3 | Target failure/replay evidence exists; old raw schema not referenced. |
| `scripts/ci/check_clickhouse_fact_insert_overwrite_edges.py` | Old batch dbt/ClickHouse partition edge runner. | `tests/dbt_clickhouse`, `tests/serving`, target serving-component job. | `REPLACE` | L1/L3 | Target partition/publication invariants pass. |
| `scripts/ci/check_clickhouse_smoke.py` | Smoke check coupled to old ClickHouse/dbt profile. | Target ClickHouse serving health and `dbt/olist_clickhouse` static/runtime checks. | `REWRITE` | L3 | Target database/service contract is explicit and smoke check has no old profile. |
| `scripts/ci/check_dbt_selector_boundaries.py` | Enforces old `batch`, `realtime_transform`, `realtime_quality`, `realtime_parity` selectors. | Target dbt-clickhouse selectors and model graph tests. | `REPLACE` | L3 | Target selector contract covers the same required boundary; old project removed. |
| `scripts/ci/check_fixture_pipeline_idempotency.py` | Idempotency check for old Airflow raw batch DAG. | Target serving sync/rebuild no-op semantics and Stage V replay gates. | `REPLACE` | L1/L3 | Target idempotency test/evidence exists and old DAG is gone. |
| `scripts/ci/check_oltp_cdc_configuration.py` | PostgreSQL OLTP publication/CDC configuration check. | MySQL binlog/GTID + Debezium connector contract. | `REPLACE` | L1 | MySQL source and connector tests pass. |
| `scripts/ci/check_oltp_simulator_integration.py` | Integration runner for old OLTP simulator path. | MySQL simulator integration and `tests/mysql`/L1 seed tests. | `REWRITE` | L1 | Uses MySQL only, file-only secrets and target simulator schema. |
| `scripts/ci/check_stage2_cdc_integration.py` | Old Stage 2 PostgreSQL/Kafka/Avro runner. | Target `cdc-component` plus `tests/cdc_contracts`. | `REPLACE` | L1/L3 | Target bounded CDC runner replaces all required assertions. |
| `scripts/ci/validate_nifi_flow.py` | Static NiFi flow/schema validator. | Target Spark schema/writer/Scala contracts. | `DELETE` | L4 | NiFi tree and all consumers removed; no target test needs flow JSON. |
| `scripts/ci/validate_realtime_configuration.py` | Old realtime-core/NiFi/dbt configuration guard. | Target repository/Compose/Scala/Airflow/dbt-clickhouse contracts. | `REPLACE` | L3 | New guards cover target service/DAG/dbt inventories. |
| `scripts/ci/validate_stage6_configuration.py` | Old observability dashboard/rule/alert validator. | [Observability contract](observability.md) and target observability test. | `REPLACE` | L2/L3 | Target mapping, metric existence and fire/resolve checks pass. |
| `scripts/ingestion/correction_specs.py` | Raw S3 correction-feed definitions. | Target rejected-event/replay contract in Spark Bronze/Silver. | `REPLACE` | L1/L4 | Target replay fixture owns the required correction semantics. |
| `scripts/ingestion/generate_correction_feeds.py` | Generates old S3 correction feeds. | Target `ReplayMain`/bounded Bronze replay fixture. | `DELETE` | L4 | No active workflow or test consumes correction-feed files. |
| `scripts/ingestion/ingest_olist_to_s3.py` | Old source-to-S3 raw ingestion. | MySQL seeding + Spark Bronze durability path. | `DELETE` | L4 | Source contract is validated by MySQL seed and Stage V. |
| `scripts/ingestion/local_storage.py` | Old raw file/manifests/dead-letter storage helper. | Target Iceberg audit/rejected-event records and fixture contract tests. | `REPLACE` | L1 | Target rejected-record test has equivalent assertions. |
| `scripts/ingestion/prepare_olist_raw_files.py` | Prepares old S3 raw files. | `scripts/simulation/seeding.py` and source fixture contract. | `DELETE` | L4 | No target path reads prepared raw files. |
| `scripts/ingestion/raw_files.py` | Old raw file discovery and row preparation. | MySQL source schema/seed and target event validation. | `REPLACE` | L1 | Required schema/row invariants transferred to target tests. |
| `scripts/ingestion/record_validation.py` | Old raw batch validation/dead-letter thresholds. | Target `PermanentRecordFailure`/`normalization_errors` contract. | `REWRITE` | L1 | Validation is expressed against target event/partition semantics. |
| `scripts/ingestion/s3_storage.py` | Old S3 raw upload client. | Polaris/MinIO/Iceberg storage path; no raw upload. | `DELETE` | L4 | No target workflow or test imports the client. |
| `scripts/loading/load_raw_to_clickhouse.py` | Old CSV/raw batch loader into ClickHouse. | Finite `scripts/serving` sync + dbt-clickhouse serving component. | `DELETE` | L4 | Target serving path passes and old raw tables are removed. |
| `scripts/loading/load_raw_to_redshift.py` | Redshift raw loader. | No target replacement; the future cloud stack is GCP, not Redshift. | `DELETE` | L4 | Remove after the AWS DAG and Redshift consumers are gone. |
| `scripts/loading/raw_batch.py` | Shared old raw-batch schema/control/dead-letter model. | Target fixture/source/serving/replay contracts. | `REPLACE` | L1/L4 | All consumers moved and target tests cover required data-quality invariants. |
| `scripts/loading/replay_dead_letters.py` | Replays old raw S3 dead letters. | Spark Bronze replay and Iceberg rejected-event ledger. | `REPLACE` | L1/L2 | Target replay command/evidence is accepted. |
| `scripts/orchestration/batch_control.py` | Old raw batch status state machine. | Target serving/control transaction state in `scripts/serving/control.py`. | `REPLACE` | L1/L4 | Serving control tests cover status transitions and no-op/retry semantics. |
| `scripts/orchestration/control_postgres.py` | Generic PostgreSQL control client shared by old paths. | PostgreSQL remains target control plane, but file-only credentials and target consumers must be explicit. | `REWRITE` | L1 | Rewrite it as the single hardened target control-plane client; no parallel legacy client remains. |
| `scripts/quality/reconcile_batch.py` | Raw batch/Redshift/ClickHouse reconciliation. | Stage V/F1 parity and target serving quality DAG. | `REPLACE` | L1/L3 | Target quality evidence covers source/current/fact/mart acceptance. |
| `scripts/simulation/README.md` | Target simulator documentation, but it still contains stale J1/secret wording. | Target MySQL simulator secret and Stage V command contract. | `REWRITE` | L1/L3 | Align commands, secret names and integration prerequisites with the target stack. |
| `scripts/simulation/__init__.py` | Target simulator package marker and public exports. | Target MySQL simulator package. | `KEEP` | L1 | Retain package API while hardening implementation. |
| `scripts/simulation/__main__.py` | Target `python -m scripts.simulation` entry point. | Target simulator CLI contract. | `KEEP` | L1/L3 | Retain and cover the entry point in target CLI checks. |
| `scripts/utilities/create_dead_letter_demo_archive.py` | Creates old raw-file corruption archive. | Target rejected-event/replay fixture. | `REWRITE` | L1 | Fixture is target-specific and contains no raw S3/NiFi assumptions. |
| `scripts/utilities/fetch_aws_secret.py` | AWS-only secret helper with no target consumer. | Local target uses file-only secrets; future cloud stack is GCP. | `DELETE` | L4 | Remove after an active-consumer scan proves no GCP or local code imports it. |
| `scripts/utilities/generate_redshift_raw_ddl.py` | Generates Redshift raw DDL. | No target replacement; the future cloud stack is GCP, not Redshift. | `DELETE` | L4 | Remove with Redshift infra and the AWS DAG. |
| `scripts/utilities/profile_olist_zip.py` | Profiles source archive, but currently emits `redshift_raw_type` and warehouse-oriented metadata. | Target-neutral source/fixture contract and F0/F1 provenance. | `REWRITE` | L1 | Preserve deterministic read-only profiling, replace Redshift-specific field names/types with target-neutral source metadata, and update consumers before removing the old output shape. |
| `scripts/utilities/validate_source_contract.py` | Validates committed source fixture. | MySQL seed and Stage V preflight. | `KEEP` | L1/L3 | Keep as target fixture preflight; update only if target schema changes. |
| `scripts/testing/create_small_fixture_dataset.py` | Creates/maintains bounded source fixture, but currently writes `redshift_raw_type` into the profile. | Stage V bounded fixture contract with target-neutral metadata. | `REWRITE` | L1/L3 | Keep deterministic fixture generation; remove Redshift-specific profile fields, then update the committed profile checksum under explicit fixture review. |
| `docs/source_contract.md` | Active source contract documentation still describes old raw/warehouse metadata. | Target-neutral MySQL source and bounded fixture contract. | `REWRITE` | L1/L3 | Keep the source contract only after removing raw-loader/Redshift terminology and aligning it with the target source schema and fixture. |
| `docs/source_profile.json` | Full source profile consumed by old raw-batch workflows and source utilities; includes Redshift-specific field names. | Target-neutral source profile, or explicit F0 provenance if no runtime consumer remains. | `REWRITE` | L1/L4 | Remove the Redshift-specific schema from active consumers; retain only if the rewritten source-contract path still needs the full profile. |

## 5. Legacy and target tests

The target suites below are not candidates for bulk deletion. Root tests with old names are mapped individually so that useful invariants are transferred before cleanup.

| Path | Что реально проверяет / current consumer | Target owner and replacement evidence | Disposition | Owner stage | Условие удаления/замены |
| --- | --- | --- | --- | --- | --- |
| `tests/mysql/test_cli.py` | Simulator CLI parsing, redaction and bounded options. | `tests/mysql` target suite; MySQL file-secret CLI contract. | `REWRITE` | L1 | Target CLI tests pass; do not remove by testpath narrowing. |
| `tests/mysql/test_mysql_integration.py` | MySQL schema/user/seed integration. | `tests/mysql` + Stage V bootstrap evidence. | `REWRITE` | L1 | Target MySQL integration is green. |
| `tests/mysql/test_repository.py` | Repository DML/idempotency/transaction behavior. | `tests/mysql`, target `SimulatorRepository`. | `REWRITE` | L1 | MySQL transaction and failure semantics are covered. |
| `tests/mysql/test_seeding.py` | Seed conversion, batching and upsert SQL. | `tests/mysql`, target MySQL `ON DUPLICATE KEY UPDATE`. | `REWRITE` | L1 | No PostgreSQL SQL or plaintext password state remains. |
| `tests/mysql/test_source_schema.py` | Source DDL and secret/schema assertions. | `tests/mysql` and `mysql-kafka-avro.md`. | `REWRITE` | L1 | Restore MySQL DML, file-only secret and exact grant invariants. |
| `tests/cdc_contracts/test_connector_bootstrap.py` | Target MySQL connector template, topic/schema configuration. | `streaming/connect/olist-mysql-cdc.json`, bounded CDC job. | `REWRITE` | L1 | Test remains target-specific and passes against actual template. |
| `tests/test_airflow_secret_bootstrap.py` | File-secret normalization in Airflow wrapper. | `tests/lakehouse_platform`/serving secret contract. | `REWRITE` | L1 | Move/rename only after target file-only behavior is covered. |
| `tests/test_avro_schema_compatibility.py` | Backward-compatible Avro evolution rules. | `tests/cdc_contracts`, `mysql-kafka-avro.md`, Scala contract tests. | `REPLACE` | L1 | All compatibility cases have target suite ownership. |
| `tests/test_batch_cdc_parity_integration.py` | Old batch vs CDC runner, status and parity gates. | Stage V/F1 and target component workflows. | `REPLACE` | L3 | Assertions mapped to candidate-only target evidence. |
| `tests/test_ci_data_quality_failures.py` | Fixture contract/dead-letter/reconciliation failure behavior. | Target source/rejected-event/quality contracts. | `REWRITE` | L1/L3 | Preserve failure thresholds and report integrity with target storage. |
| `tests/test_clickhouse_batch_phase3.py` | CSV/raw batch staging and old local DAG. | `tests/dbt_clickhouse`, `tests/serving`, target serving component. | `REPLACE` | L1/L3 | Only target serving/partition invariants survive. |
| `tests/test_clickhouse_phase1_contracts.py` | Old ClickHouse/analytics db bootstrap and dbt profile. | `tests/dbt_clickhouse` and Compose/serving contracts. | `REPLACE` | L1/L3 | Target native DDL, secret and serving database checks pass. |
| `tests/test_clickhouse_phase4_dbt_graph.py` | Old `dbt/olist_analytics` batch/realtime graph. | `tests/dbt_clickhouse`, `serving-and-recovery.md`. | `REPLACE` | L1/L3 | Target model graph/selectors cover business invariants. |
| `tests/test_clickhouse_phase5_cdc_ingestion.py` | NiFi/S3/raw ClickHouse ingest and old local lab. | `tests/cdc_contracts`, `tests/lakehouse_platform`, Stage V. | `REPLACE` | L1/L3 | Transport/storage invariants moved to target stack. |
| `tests/test_clickhouse_phase6_realtime_dbt_quality.py` | Old realtime dbt project quality/retry behavior. | Scala Spark tests + `tests/dbt_clickhouse` + serving tests. | `REPLACE` | L1/L3 | Target Silver/serving quality evidence is green. |
| `tests/test_clickhouse_phase7_ci_observability.py` | Old ClickHouse/NiFi/PostgreSQL exporter/rule/workflow assumptions. | New target observability contract and acceptance test. | `REWRITE` | L2/L3 | Rewrite to actual producer→scrape→rule→dashboard chain. |
| `tests/test_control_postgres_phase2.py` | Control DB separation and old batch-control integration. | `tests/lakehouse_platform`/serving control contract. | `REWRITE` | L1 | Target control PostgreSQL remains and raw warehouse is excluded. |
| `tests/test_dead_letter_pipeline.py` | Old raw-file dead-letter/replay and batch status. | Target rejected records, Spark ReplayMain and serving quality. | `REWRITE` | L1/L2 | Preserve classification/replay/report assertions in target form. |
| `tests/test_nifi_optimization.py` | NiFi processor/flow loading, codecs and fanout. | No target equivalent; Spark data plane owns the path. | `DELETE` | L4 | Delete only with `streaming/nifi/**` and old flow consumers. |
| `tests/test_oltp_seed_contracts.py` | Source schema edge cases for old OLTP seed. | `tests/mysql`, MySQL DDL and seed contract. | `REWRITE` | L1 | Assertions run against MySQL target schema. |
| `tests/test_postgres_oracle_export.py` | Canonical hash helpers plus old PostgreSQL/dbt inventory expectations. | New parity test for frozen F0/F1 artifacts. | `REPLACE` | L1/L4 | Keep hash semantics, drop old project assertions, preserve F0 oracle readers. |
| `tests/test_simulation.py` | Workload planning, composite keys and graceful stop. | `tests/mysql`/simulation target tests. | `REWRITE` | L1 | Keep semantic coverage under target database contract. |
| `tests/test_stage2_configuration.py` | Old Stage 2 PostgreSQL connector/status/topic assumptions. | `tests/cdc_contracts/test_connector_bootstrap.py` and target topics. | `REPLACE` | L1 | All target connector assertions transferred. |
| `tests/test_stage3_configuration.py` | NiFi profile, MinIO raw bucket and flow configuration. | Target MinIO/Polaris/Spark platform contracts. | `REWRITE` | L1/L2 | Retain only target storage/security assertions. |
| `tests/test_stage3_contracts.py` | NiFi landing/coverage manifest and raw bytes model. | Spark Bronze/Silver/transaction contracts and Scala tests. | `REPLACE` | L1 | No landing/coverage test is deleted before its target invariant is mapped. |
| `tests/test_stage4_contracts.py` | Raw S3 manifest/offset reconciliation and old warehouse loader. | Iceberg Bronze/Silver progress/audit and target serving. | `REPLACE` | L1 | Target audit/progress contract has equivalent failure coverage. |
| `tests/test_stage5_contracts.py` | Old realtime dbt model/publication graph. | Spark Silver + ClickHouse serving/dbt-clickhouse tests. | `REPLACE` | L1/L3 | Target graph/publication checks pass. |
| `tests/test_stage6_contracts.py` | Old dashboards, alert rules and Loki/metrics labels. | `observability.md` and target observability contract test. | `REWRITE` | L2 | New chain is tested with real target names/metrics. |

### Target suites explicitly retained

`tests/cdc_contracts/**`, `tests/dbt_clickhouse/**`, `tests/lakehouse_platform/**`, `tests/mysql/**`, `tests/serving/**`, `tests/stage_v/**` and `streaming/spark/scala/src/test/**` are `KEEP`. Their test collection must remain explicit in CI, and a zero-collection result is a failure. `tests/mysql/test_source_schema.py` is `REWRITE`, but the directory itself is not disposable.

## 6. Fixtures and schema assets

| Path | Role / consumer | Target contract / replacement evidence | Disposition | Owner stage | Условие удаления |
| --- | --- | --- | --- | --- | --- |
| `tests/fixtures/olist_small/olist_small.zip` | Frozen bounded source archive used by Stage V/F0. | Stage V and F0/F1 fixture contract. | `KEEP` | L0/F1 | Never replace without checksum-governed review. |
| `tests/fixtures/olist_small/source/**` | Reviewable uncompressed copy of the bounded source CSVs. | Stage V source fixture contract. | `KEEP` | L0/F1 | Keep content aligned with the frozen archive; changes require checksum-governed fixture review. |
| `tests/fixtures/olist_small/source_profile_small.json` | Bounded source profile used by legacy CI utilities; currently uses `redshift_raw_type`. | Target-neutral Stage V source profile. | `REWRITE` | L1/L3 | Rewrite field names/metadata and update the dependent validator/generator; do not change the archive without explicit fixture review. |
| `tests/fixtures/olist_small/README.md` | Fixture usage/provenance documentation. | Target source/fixture contract. | `REWRITE` | L1/L3 | Keep provenance and regeneration instructions, but remove old ingestion/warehouse claims. |
| `tests/fixtures/final_parity/main-1400d08.json` | Frozen F0 oracle. | `final-parity.md`. | `KEEP` | F1 | Immutable; no cleanup may regenerate or remove it. |
| `tests/fixtures/final_parity/main-1400d08.metadata.json` | Frozen F0 provenance/checksums. | `final-parity.md`. | `KEEP` | F1 | Immutable and validated by preflight. |
| `tests/fixtures/postgresql_oracle/dbt_inventory.json` | Old dbt/PostgreSQL oracle inventory. | Frozen F0 metadata and target dbt-clickhouse inventory. | `DELETE` | L4 | `test_postgres_oracle_export.py` replacement passes and no consumer remains. |
| `tests/fixtures/postgresql_oracle/postgres_batch_oracle.json` | Old batch oracle. | Frozen final-parity oracle. | `DELETE` | L4 | F0/F1 readers do not reference it. |
| `tests/fixtures/postgresql_oracle/postgres_stage5_oracle.json` | Old realtime/PostgreSQL oracle. | Frozen final-parity oracle. | `DELETE` | L4 | Old realtime tests/project are gone and no reader remains. |
| `tests/spark_integration/fixtures/wave2_crud.sql` | Target MySQL CRUD/transaction fixture used by Wave 2/Spark tests. | Spark/CDC contracts and Stage V. | `KEEP` | L1 | Keep checksum/semantics stable. |
| `tests/stage_v/fixtures/*.sql` | Target bounded insert/update/delete/schema-evolution events. | Stage V V0–V10. | `KEEP` | L1/L2 | Do not remove to shorten E2E. |
| `tests/stage_v/oracles/initial_counts.json` | Target Stage V initial row-count oracle. | Stage V harness. | `KEEP` | L1 | Update only with explicit fixture contract change. |
| `olist.zip` | Full source archive for manual/local source validation; not a legacy runtime. | Source contract utilities and full-run provenance documentation. | `KEEP` | L0/L1 | Keep as provenance; target E2E uses bounded fixture. |
| `streaming/nifi/flow/olist-cdc-v1.json` | NiFi flow fixture. | Spark Scala data-plane contract. | `DELETE` | L4 | NiFi runtime and all flow consumers removed. |
| `streaming/nifi/parameters/local.template.json` | NiFi parameter template. | Target Compose/env/secret contracts. | `DELETE` | L4 | No target workflow consumes it. |
| `streaming/schemas/normalized/**` | Old NiFi normalized Avro assets. | Target captured writer schemas and Spark contracts. | `DELETE` | L4 | No active code/test reads the directory. |
| `streaming/schemas/cdc-landing/v1.avsc` | Old NiFi landing schema. | Target Bronze raw record contract. | `REPLACE` | L1/L4 | Bronze contract/test owns raw bytes/tombstone semantics. |
| `streaming/schemas/cdc-coverage/v1.schema.json` | Old NiFi coverage manifest schema. | Target Spark transaction/progress/audit tables. | `REPLACE` | L1/L4 | Equivalent target progress contract is accepted. |
| `streaming/schemas/captured-writer-schemas/**` | Captured Debezium/Apicurio writer schemas used by Scala and CDC contracts. | `mysql-kafka-avro.md`, `tests/cdc_contracts`. | `KEEP` | L1 | Frozen provenance; no rewrite during legacy cleanup. E2E capture must not mutate this path; a new bundle needs an explicit reviewed commit. |

## 7. Secret templates and secret sources

| Path / variable | Current role or defect | Target contract / replacement evidence | Disposition | Owner stage | Условие удаления/замены |
| --- | --- | --- | --- | --- | --- |
| `docker/secrets/dev/airflow_api_secret_key.txt` | Airflow API secret; also incorrectly used as current MinIO password default. | File-only target secrets; dedicated MinIO secret must be separate. | `KEEP` | L1 | Keep for Airflow; remove cross-service default. |
| `docker/secrets/dev/airflow_postgres_password.txt` | Airflow metadata DB password. | Target Airflow/control plane. | `KEEP` | L1 | Keep file-only. |
| `docker/secrets/dev/apicurio_db_user.txt` | Apicurio DB bootstrap user. | Target platform PostgreSQL/Apicurio. | `KEEP` | L1 | Keep with explicit owner. |
| `docker/secrets/dev/clickhouse_password.txt` | ClickHouse serving credential. | Target serving contract. | `KEEP` | L1 | Keep file-only. |
| `docker/secrets/dev/control_postgres_password.txt` | Target control-plane password. | `architecture-and-runtime.md`, `serving-and-recovery.md`. | `KEEP` | L1 | Keep; never reuse as source/MySQL password by implicit fallback. |
| `docker/secrets/dev/minio_root_user.txt` | Target MinIO root user. | Polaris/MinIO target storage. | `KEEP` | L1 | Keep with dedicated root password. |
| `docker/secrets/dev/mysql_spark_reference_reader_password.txt` | Target read-only Spark JDBC credential. | `mysql-kafka-avro.md` least-privilege grant. | `KEEP` | L1 | Keep and test SELECT-only grant. |
| `docker/secrets/dev/polaris_db_user.txt` | Polaris DB user. | Target Polaris control plane. | `KEEP` | L1 | Keep. |
| `docker/secrets/dev/polaris_db_password.txt` | Missing dedicated Polaris database password; Compose currently falls back to the control-PostgreSQL password. | Target Polaris relational database role and file-only bootstrap. | `REPLACE` | L1 | Add the dedicated template and remove the shared-password fallback. |
| `docker/secrets/dev/apicurio_db_password.txt` | Missing dedicated Apicurio database password; Compose currently falls back to the control-PostgreSQL password. | Target Apicurio relational database role and file-only bootstrap. | `REPLACE` | L1 | Add the dedicated template and remove the shared-password fallback. |
| `docker/secrets/dev/postgres_password.txt` | Legacy PostgreSQL source secret and current accidental default for several MySQL secrets. | Dedicated MySQL role files and explicit Compose source variables. | `DELETE` | L4 | Add and wire all dedicated target role files, remove every fallback/CI reference, and delete the old PostgreSQL source path after the orphan scan. |
| `docker/secrets/dev/redshift_password.txt` | Redshift-only credential for the removed AWS DAG. | No target consumer; future cloud stack is GCP. | `DELETE` | L4 | Remove after the AWS DAG and all Redshift secret references are gone. |
| `docker/secrets/dev/mysql_root_password.txt` | Missing target role-specific template required by Compose contract. | MySQL file-only bootstrap. | `REPLACE` | L1 | Add and wire explicit source variable. |
| `docker/secrets/dev/mysql_admin_password.txt` | Missing target role-specific template. | MySQL schema/migration owner. | `REPLACE` | L1 | Add and wire explicit source variable. |
| `docker/secrets/dev/mysql_simulator_password.txt` | Missing target role-specific template. | MySQL simulator DML owner. | `REPLACE` | L1 | Add and wire explicit source variable. |
| `docker/secrets/dev/mysql_cdc_reader_password.txt` | Missing target Debezium reader template. | MySQL CDC grants and connector. | `REPLACE` | L1 | Add and wire explicit source variable. |
| `docker/secrets/dev/minio_root_password.txt` | Missing dedicated MinIO root password. | Target MinIO/Polaris storage. | `REPLACE` | L1/L2 | Add; remove Airflow/NiFi password fallback. |
| `MINIO_NIFI_PASSWORD_SOURCE_FILE`, `MINIO_CDC_LOADER_PASSWORD_SOURCE_FILE`, `NIFI_ADMIN_PASSWORD_SOURCE_FILE` | Legacy secret interfaces in `.env.example`/MinIO/NiFi docs. | No target user identity; Polaris-projected credentials own target access. | `DELETE` | L4 | Remove only after MinIO init and docs are rewritten. |

## 8. Supporting runtime/observability assets

| Path / asset family | Target decision | Owner stage | Removal/rewrite condition |
| --- | --- | --- | --- |
| `infra/oltp/**` | `DELETE` | L4 | MySQL schema/users/CDC tests pass and no source consumer remains. |
| `infra/redshift/**` | `DELETE` | L4 | Remove with the AWS DAG, Redshift utilities and active secret/config references; GCP is a separate future program. |
| `infra/aws/realtime/**` | `DELETE` | L4 | AWS runtime is not a supported target; retain only historical provenance in Git history. |
| `dbt/olist_analytics/**` | `DELETE` | L4 | `dbt/olist_clickhouse` graph/CI/F1 replacement is green and no active selector/profile remains. |
| `streaming/nifi/**` | `DELETE` | L4 | Target Spark/Scala/observability tests replace all required invariants. |
| `streaming/minio/init.sh` | `DELETE` | L4 | This old init script is not used by the current Compose service; target bucket/policy initialization is owned by `infra/polaris/minio/init.sh`. |
| `streaming/minio/README.md` | `REWRITE` | L1/L2 | Keep only image/build ownership and target MinIO usage; remove the obsolete `olist-cdc`, NiFi and loader identity instructions. |
| `streaming/minio/nifi-policy.json` | `DELETE` | L4 | No NiFi or old raw S3 consumer remains. |
| `streaming/minio/cdc-loader-policy.json` | `DELETE` | L4 | No target service uses the old CDC loader identity; target access policies already live under `infra/polaris/minio/**`. |
| `streaming/minio/Dockerfile` | `KEEP` | L1/L2 | Target MinIO server image build; preserve pinned security release and non-root runtime. |
| `streaming/minio/start.sh` | `KEEP` | L1 | Target MinIO file-secret entrypoint; retain redaction/file-only behavior. |
| `streaming/runtime-versions.json` | `REWRITE` | L1/L4 | Remove NiFi/old exporters and keep Debezium `3.6.0.Final` aligned with Compose/contracts. |
| `compose.yaml` | `REWRITE` | L1/L2/L3 | Preserve target profiles/services; fix secret/env defaults, actual exporter inventory and version alignment. |
| `.env.example` | `REWRITE` | L1/L2/L3 | Remove `OLTP_*`, `NIFI_*`, `MINIO_*_NIFI/CDC_LOADER`, legacy Redshift/AWS and other old source/profile interfaces; document target `MYSQL_*`, `POLARIS_*`, `APICURIO_*`, `MINIO_ROOT_*`; GCP variables belong to a separate cloud plan. |
| `pyproject.toml` | `REWRITE` | L3/L4 | Remove unused Redshift/AWS/old-dbt dependencies after the local consumer scan; retain PostgreSQL for the target control plane and do not introduce GCP dependencies until the separate cloud program. |
| `uv.lock` | `REWRITE` | L3/L4 | Regenerate only from the accepted target `pyproject.toml`; never hand-edit to hide an import. |
| `docker/airflow/load-env-and-run.sh` | `REWRITE` | L1/L3 | Keep Airflow file-secret bootstrap, remove old warehouse/source defaults and retain target control/serving configuration. |
| `infra/clickhouse/initdb/001_create_databases.sql` | `DELETE` | L4 | The current Compose path mounts `infra/clickhouse/lakehouse`, not this legacy init directory; target databases are created by the lakehouse bootstrap. |
| `infra/clickhouse/initdb/002_create_raw_batch_tables.sql` | `DELETE` | L4 | Target serving uses `infra/clickhouse/lakehouse`; no raw-batch table consumer remains. |
| `infra/clickhouse/initdb/003_create_raw_cdc_tables.sql` | `DELETE` | L4 | Target serving reads Iceberg and writes native serving event/current tables; old raw CDC schema has no target owner. |
| `infra/clickhouse/initdb/004_create_pipeline_runtime_tables.sql` | `DELETE` | L4 | No active target consumer reads `pipeline_runtime.cdc_transform_run_files`; serving/control ownership is under `infra/clickhouse/lakehouse` and target control code. |
| `infra/clickhouse/lakehouse/**` | `KEEP` | L1/L3 | Target native serving DDL, publication views and recovery smoke tests. |
| `dbt/olist_clickhouse/**` | `KEEP` | L1/L3 | Only active Gold project; all legacy dbt assertions map here or to explicit serving tests. |
| `observability/grafana/dashboards/cdc-nifi-storage.json` | `DELETE` | L2 | Target dashboard replacement is valid and no NiFi metric appears. |
| `observability/grafana/dashboards/cdc-source-debezium.json` | `REWRITE` | L2 | Replace PostgreSQL slot/WAL panels with MySQL/binlog and real Connect metrics. |
| `observability/grafana/dashboards/cdc-kafka-connect.json` | `REWRITE` | L2 | Scope lag to target consumer groups/topics and real exporter/source. |
| `observability/grafana/dashboards/cdc-slo.json` | `REWRITE` | L2 | Use target durability/serving SLO metrics with producer ownership. |
| `observability/grafana/dashboards/cdc-airflow-warehouse.json` | `REWRITE` | L2 | Rename raw warehouse panels to target Iceberg/serving/Airflow metrics. |
| `observability/grafana/dashboards/cdc-capacity-logs.json` | `REWRITE` | L2 | Use actual target service labels and configured Loki/Prometheus sources. |
| `observability/grafana/dashboards/lakehouse-serving.json` | `REWRITE` | L2 | Preserve serving visibility, but verify every query against a real target producer and publication metric. |
| `observability/grafana/provisioning/**` | `REWRITE` | L2 | Keep provisioning ownership, but align dashboard discovery, datasources and alerting with the actual target services. |
| `observability/grafana/README.md` | `REWRITE` | L2 | Document only target dashboards, datasources, credentials and evidence commands. |
| `observability/prometheus/rules/cdc-component-alerts.yml` | `REWRITE` | L2 | Remove PostgreSQL WAL/NiFi/raw-loader alerts; prove every target metric exists. |
| `observability/prometheus/rules/cdc-slo-recording.yml` | `REWRITE` | L2 | Replace NiFi consumer group and unscoped lag with target selectors. |
| `observability/prometheus/rules/lakehouse-serving-alerts.yml` | `REWRITE` | L2 | Keep serving intent, align metric names and runbooks with target producer. |
| `observability/prometheus/prometheus.yml` | `REWRITE` | L2 | Every scrape target must be a real Compose service/exporter and healthy in acceptance. |
| `observability/prometheus/README.md` | `REWRITE` | L2 | Document actual scrape inventory and target metric ownership; remove exporter names that are not deployed. |
| `observability/postgres/oltp-queries.yml` | `DELETE` | L2 | This is an old PostgreSQL-OLTP query pack with no target consumer; control-plane health is owned by the target control probe/exporter contract. |
| `observability/alertmanager/**` | `REWRITE` | L2 | Add a pinned Alertmanager service to the target observability profile because Prometheus currently routes alerts to it and the target contract requires fire/resolve evidence; preserve secret-free runbook annotations. |
| `observability/alloy/**` | `REWRITE` | L2 | Add a pinned Alloy service to the target logs profile with a read-only Docker socket, real Loki path and bounded labels; do not leave the config as an unowned file. |
| `observability/statsd/**` | `REPLACE` | L2 | Remove the old StatsD mapping and replace its Airflow signal responsibility with the target Airflow health/API probe; do not add a phantom `statsd-exporter` scrape job. |
| `observability/loki/**` | `REWRITE` | L2 | Retain target log storage only with actual Loki/Alloy wiring, bounded labels, retention and evidence checks. |
| `observability/README.md` | `REWRITE` | L2 | Replace the current PostgreSQL/NiFi/exporter inventory and commands with the target observability contract. |
| `README.md` | `REWRITE` | L3/L4 | Active operator commands must describe only target Compose profiles, MySQL source and target DAGs; historical migration context may remain linked. |
| `docs/architecture.md` | `REWRITE` | L4 | Active architecture statements must match target durability/serving path; old phase history stays in historical docs. |
| `docs/runbook_windows.md` | `REWRITE` | L4 | Replace old raw batch/PostgreSQL commands with target local_lab commands. |
| `docs/runbook_macos.md` | `REWRITE` | L4 | Replace old raw batch/PostgreSQL commands with target local_lab commands. |
| `docs/runbooks/cdc-local-end-to-end-validation.md` | `REWRITE` | L4 | Active validation runbook must use MySQL/Debezium/Spark/Iceberg/serving path or be explicitly archived. |

## 9. Target artifacts explicitly protected

These paths are not legacy deletion candidates. Some have a `REWRITE` disposition because L1 must harden an existing target implementation; that is different from removing the target responsibility.

| Path / family | Current role | Target contract / replacement evidence | Disposition | Owner stage | Protection rule |
| --- | --- | --- | --- | --- | --- |
| `infra/mysql/**` | Authoritative MySQL source schema, users and server configuration. | `architecture-and-runtime.md` | `KEEP` | L1 | Never replace with PostgreSQL or a second source DB. |
| `infra/platform-postgres/**` | Target shared platform database bootstrap for Airflow, Polaris and Apicurio. | `architecture-and-runtime.md` | `KEEP` | L1 | Preserve separate platform roles/databases and file-only password inputs. |
| `infra/control-postgres/initdb/001_create_schemas.sql` | Creates legacy `audit`/`cdc_audit` schemas for raw batch/CDC paths. | Target serving control schema and explicit target grants. | `REWRITE` | L1 | Remove schemas with no target owner and retain only schemas required by the target serving control contract. |
| `infra/control-postgres/initdb/002_create_batch_control_tables.sql` | Raw batch/load/dead-letter audit tables. | Target ClickHouse/Iceberg serving and rejected-event evidence. | `DELETE` | L4 | Delete after batch-control/reconciliation invariants are owned by target serving/Spark tests and no consumer remains. |
| `infra/control-postgres/initdb/003_create_cdc_control_tables.sql` | NiFi/raw-file CDC ingest, coverage and dead-letter tables. | Spark Bronze/Silver audit/progress and target CDC contracts. | `DELETE` | L4 | Delete after target CDC progress/replay/rejected-event evidence is green and no old loader imports remain. |
| `infra/control-postgres/initdb/004_create_cdc_transform_control_tables.sql` | Old realtime dbt transform/publication state. | Spark Silver and ClickHouse serving control. | `DELETE` | L4 | Delete after old transform/dbt consumers and their tests are replaced. |
| `infra/control-postgres/initdb/005_create_serving_control_tables.sql` | Target finite serving sync/rebuild ledger and runtime state. | `scripts/serving/control.py`, serving DAGs and Stage V. | `KEEP` | L1 | Preserve target serving state machine and migration contract. |
| `infra/control-postgres/initdb/999_grant_control_role.sql` | Grants both legacy audit schemas and target serving schema. | Target serving control grants. | `REWRITE` | L1 | Remove grants for deleted schemas and keep least-privilege target grants. |
| `infra/control-postgres/init-control-db.sh` | Applies all control migrations, including legacy raw batch/CDC tables. | Target control bootstrap. | `REWRITE` | L1/L4 | Apply only target-owned migrations after replacement review; preserve idempotency and file-only credentials. |
| `infra/polaris/**` | Target Polaris catalog, credentials projection, MinIO policies and bootstrap. | `architecture-and-runtime.md` | `KEEP` | L1/L2 | Preserve catalog/RBAC/credential and physically isolated storage contracts. |
| `streaming/connect/**` | Target Debezium MySQL connector image, template, bootstrap and plugin inventory. | `mysql-kafka-avro.md` | `KEEP` | L1 | Do not delete; `local_lab.py` and CDC contract tests consume it. |
| `streaming/kafka/**` | Target topic manifest/bootstrap/validator. | `mysql-kafka-avro.md` | `KEEP` | L1 | Preserve eight target CDC topics and internal topic contract. |
| `streaming/schemas/contracts/**` | Versioned target entity contracts. | `mysql-kafka-avro.md` | `KEEP` | L1 | No cleanup based on historical `normalized/` assets may remove these. |
| `streaming/schemas/captured-writer-schemas/**` | Frozen target writer schema provenance used by Scala. | `testing-and-evidence.md` | `KEEP` | L1 | Fingerprints and paths are contract inputs. |
| `streaming/spark/**` | Target Scala Bronze/Silver/ops/replay data plane and platform config. | `spark-streaming.md` | `KEEP` | L1/L2 | Preserve data-plane ownership; observability may add metrics without changing durability semantics. |
| `streaming/spark/scala/src/main/scala/com/olist/mds/spark/transaction/TransactionBatchWriter.scala` | Target transaction metadata writer, but it emits immutable observations per micro-batch without a dedicated cross-batch effective-state test. | Stage E transaction audit/effective-state contract. | `REWRITE` | L1 | Preserve append-only evidence while validating split BEGIN/END, duplicate/replay and offset/order transitions before serving publication. |
| `scripts/simulation/seeding.py` | Target MySQL fixture seeding and idempotent upsert conversion. | `tests/mysql`, `architecture-and-runtime.md` | `REWRITE` | L1 | Keep role; harden MySQL SQL, composite keys, batching and transaction evidence. |
| `scripts/simulation/database.py` | Target MySQL simulator repository and transaction boundary. | `tests/mysql`, `architecture-and-runtime.md` | `REWRITE` | L1 | Keep role; remove unsafe autocommit/plaintext state and preserve rollback/failure behavior. |
| `scripts/simulation/domain.py` | Target deterministic workload semantics. | `tests/mysql` | `KEEP` | L1 | Do not change simulation semantics during legacy cleanup. |
| `scripts/simulation/engine.py` | Target graceful-stop/replay engine. | `tests/mysql` | `REWRITE` | L1 | Keep semantics and add failure persistence evidence. |
| `scripts/simulation/cli.py` | Target redacted simulator CLI. | `tests/mysql` | `REWRITE` | L1 | Keep file-only secret/redaction contract. |
| `scripts/serving/**` | Target ClickHouse serving boundary, control, metrics, entities and dbt runner. | `serving-and-recovery.md` | `KEEP` | L1/L2/L3 | Do not replace with old raw loader/realtime dbt path. |
| `scripts/serving/control.py` | Target serving control repository, but its schema verification still lists legacy migrations/tables and an absent `audit.pipeline_events` table. | Target `serving.*` control ledger and Stage V final-control checks. | `REWRITE` | L1 | Verify only target-owned schema/table invariants and remove legacy `audit`/`cdc_audit` assumptions before deleting their DDL. |
| `scripts/serving/metrics.py` | Target serving metric producer exists, but no Compose endpoint currently owns or exposes it. | Target serving observability producer and real scrape owner. | `REWRITE` | L2 | Wire it to a real bounded service/endpoint or remove it with evidence that the target serving probe owns every required signal. |
| `scripts/serving/clickhouse.py` | Target materializer reads transaction audit history, but its current fetch path drops `OPEN` observations without an end offset and can hide an unresolved boundary. | Effective transaction history and frozen serving boundary contract. | `REWRITE` | L1 | Preserve complete physical boundaries while exposing unresolved effective `OPEN`/`REJECTED` state to the planner. |
| `scripts/serving/boundary.py` | Target boundary planner has the right state vocabulary, but its correctness depends on the materializer not discarding unresolved observations. | Stage E effective transaction/boundary contract. | `REWRITE` | L1 | Add explicit effective-state and rejected/open regression cases without weakening prefix blocking. |
| `scripts/parity/**` | F0 validation and candidate-only F1 comparator/export readers. | `final-parity.md` | `KEEP` | F1 | F0 oracle/readers are immutable inputs; no regular F0 regeneration. |
| `scripts/validation/stage_v_candidate_e2e.py` | Full target V0–V10 acceptance runner. | `testing-and-evidence.md` | `KEEP` | L1–L4 | Every substage must run the full runner, not only `tests/stage_v`. |
| `tests/cdc_contracts/**` | Target CDC contract suite. | `testing-and-evidence.md` | `KEEP` | L1/L3 | Explicit CI collection; zero collection fails. |
| `tests/dbt_clickhouse/**` | Target dbt-clickhouse contract suite. | `testing-and-evidence.md` | `KEEP` | L1/L3 | Explicit CI collection; old dbt tests map here. |
| `tests/lakehouse_platform/**` | Target Compose/Polaris/Spark/platform suite. | `testing-and-evidence.md` | `KEEP` | L1/L2/L3 | Explicit CI collection; no deletion for test-count reduction. |
| `tests/mysql/**` | Target source/simulator suite. | `testing-and-evidence.md` | `KEEP` | L1/L3 | Explicit CI collection; individual files may be rewritten only with replacement coverage. |
| `tests/serving/**` | Target serving/recovery suite. | `testing-and-evidence.md` | `KEEP` | L1/L3 | Boundary/retry/rebuild behavior remains required. |
| `tests/stage_v/**` | Full E2E harness/oracles/fixtures. | `testing-and-evidence.md` | `KEEP` | L1–L4 | Run after every substage. |
| `streaming/spark/scala/src/test/**` | Target ScalaTest data-plane suite. | `testing-and-evidence.md` | `KEEP` | L1/L3 | Must remain in Scala CI and JAR contract. |
| `airflow/dags/olist_lakehouse_maintenance.py` | Target finite maintenance DAG. | `validation-and-ci.md` | `KEEP` | L3/L4 | Exact target DAG inventory must retain and import it. |
| `airflow/dags/olist_lakehouse_serving.py` | Target finite serving DAG, but current boundary invocation hardcodes `boundary_state="READY"` and depends on the incomplete transaction-row fetch path. | Effective transaction/boundary contract and Stage V serving acceptance. | `REWRITE` | L1/L3 | Retain exact DAG IDs and orchestration role; derive/propagate effective boundary state and preserve blocked OPEN/REJECTED semantics. |
| `scripts/ci/check_airflow_dag_imports.py` | Target DAG import check, but current implementation does not enforce the exact four-DAG-ID target allowlist from the two target files. | `validation-and-ci.md` | `REWRITE` | L3 | Keep import checking and add exact target DAG inventory/no-old-dbT path assertions. |
| `scripts/ci/check_apicurio_compatibility.py` | Target registry compatibility validator. | `validation-and-ci.md` | `KEEP` | L1/L3 | Keep as a required CDC contract check. |
| `scripts/ci/check_avro_schema_compatibility.py` | Target schema evolution validator. | `validation-and-ci.md` | `KEEP` | L1/L3 | Keep with target captured-writer/schema contracts. |
| `scripts/utilities/airflow_config_cmd.py` | Target Airflow wrapper, but it currently permits plaintext environment/default fallbacks. | `validation-and-ci.md` | `REWRITE` | L1/L3 | Require file-only secrets, remove plaintext defaults and preserve import/config coverage. |
| `scripts/validation/stage_v_probes.py` | Target Stage V probe module, but its default MySQL password path still uses the legacy `postgres_password.txt`. | `testing-and-evidence.md` | `REWRITE` | L1 | Use the dedicated target reader/simulator secret contract without changing probe semantics. |

## 10. L0 decision summary

1. Target MySQL, Debezium/Kafka Connect, Apicurio, Spark/Scala, Iceberg/Polaris, ClickHouse serving, Airflow control plane, F0/F1 readers and target test suites are `KEEP`/`REWRITE`; they are not cleanup casualties.
2. Old PostgreSQL OLTP, NiFi, Redshift, raw S3/Parquet loader and `dbt/olist_analytics` paths are `DELETE` or `REPLACE`, but only after their invariants have a named target owner.
3. Observability is not optional cleanup: old dashboards/rules are `REWRITE`/`DELETE`, and no phantom exporter/metric/service is accepted as a target.
4. `tests/fixtures/postgresql_oracle/**` is not interchangeable with the frozen `tests/fixtures/final_parity/**`; the former is disposable only after F0 readers and test mappings are verified.
5. The accidental use of `postgres_password.txt` and `airflow_api_secret_key.txt` as defaults for target MySQL/MinIO credentials is a target configuration defect, not a reason to delete target secret tests.
