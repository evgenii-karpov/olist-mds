# L0: Legacy artifact disposition register

- **Status**: active Stage L register, recorded at L0.
- **Purpose**: preserve a verifiable decision for every runtime/CI/test/fixture/secret artifact related to the PostgreSQL/NiFi/Redshift/old raw-batch or old dbt paths being removed.
- **Boundary**: historical plans, handoff documents, and reports are not runtime artifacts in this register. They are retained as provenance unless an explicit requirement removes an obsolete active instruction.
- **Cloud boundary**: AWS/Redshift are not a deferred target and are removed in L4; the future GCP/BigQuery stack is described separately in the [GCP migration plan](../../gcp-spark-iceberg-bigquery-migration.md). This does not prohibit the local S3-compatible MinIO path or its required Iceberg `S3FileIO`/S3A adapters: they are not AWS cloud runtime and must not be removed mechanically.
- **Authority**: this register controls dispositions; implementation details and gate ordering are in the [Stage L plan](../completed/stage-l-legacy-removal-ci-cutover.md), while target contracts take precedence over historical documents.

## 1. Disposition rules

| Decision | Meaning at L0 | Condition for removal/replacement |
| --- | --- | --- |
| `KEEP` | The artifact already belongs to the target stack or is frozen provenance/F0 input. | Do not remove it in Stage L; changes are allowed only when contract-driven. |
| `REWRITE` | The path and role are useful, but the implementation contains legacy semantics, names, endpoints, or boundaries. | Rewrite it for the named target owner and cover it with target tests/evidence. |
| `REPLACE` | The old artifact must not remain, but its verifiable responsibility is still needed by the target stack. | Add and accept the replacement first, then remove the old path after an orphan scan. |
| `DELETE` | The artifact has no target responsibility and is not F0/F1 provenance. | Remove it only after the specified consumer/removal check. |

This register intentionally uses only four decisions. It has no `HOLD` or `DEFER` statuses: AWS/Redshift are `DELETE` only, and the future GCP/BigQuery stack is handled by a separate program.

In this document, `DELETE` is a decision about the target disposition, not permission to remove a file immediately. Before L4, neither a register row nor the file itself may be removed without satisfying the removal condition.

## 2. Baseline L0

| Field | Value |
| --- | --- |
| Baseline commit | `9214cd1de05ab37cdeae27a1a0b633963e8ae8d6` (`docs(lakehouse): sequence Stage L into gated cutover stages`) |
| Working tree | Clean after tracked and untracked changes were returned to baseline; the committed Stage L plan was preserved. |
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

This baseline run is separate from future acceptance evidence. If the baseline E2E fails, the failure is recorded as a baseline diagnostic and does not become an acceptance `PASS`.

## 3. Workflows and DAGs

| Path | Current role and consumers | Target contract / replacement evidence | Disposition | Owner stage | Removal condition |
| --- | --- | --- | --- | --- | --- |
| `.github/workflows/ci.yml` | Old monolith: `dbt/olist_analytics`, NiFi, realtime-core, and raw-batch jobs; branch-protection entry point. | [Validation & CI](validation-and-ci.md): `ci-success`, repository contracts, target Python/Scala/Compose/Airflow/dbt-clickhouse jobs. | `REWRITE` | L3 | Old jobs are transferred to the target matrix, and zero skipped required jobs is proven. |
| `.github/workflows/batch-cdc-parity.yml` | Manual batch + NiFi/raw CDC parity workflow. | Dispatch-only `lakehouse-cdc.yml`, `lakehouse-serving.yml`, and manual Stage V/F1 acceptance. | `REPLACE` | L3 | Replacement workflows are green and all non-legacy invariants have target tests/evidence. |
| `.github/workflows/cdc-stage2-kafka-debezium.yml` | PostgreSQL/NiFi-era CDC capture drill. | Target MySQL → Debezium → Kafka/Apicurio dispatch-only bounded `lakehouse-cdc.yml`. | `REPLACE` | L3 | Target connector/CRUD/restart checks green; legacy workflow has no consumer. |
| `.github/workflows/cdc-stage6-operations.yml` | Phase 6 alert/failure-injection workflow with NiFi/PostgreSQL metrics. | [Observability contract](observability.md) and target bounded observability acceptance. | `REPLACE` | L2/L3 | Target fire/resolve evidence is published; old alert names and service references are absent. |
| `.github/workflows/lakehouse-components.yml` | Target fast bounded component-contract workflow. | [Validation & CI](validation-and-ci.md): Spark image, Airflow and observability contract jobs. | `REPLACE` | L3 | Automatic contract workflow passes without skipped manual-only jobs. |
| `.github/workflows/lakehouse-cdc.yml` | Target dispatch-only bounded CDC acceptance workflow. | [Validation & CI](validation-and-ci.md): bounded MySQL → Debezium → Kafka/Apicurio → Spark CDC runtime. | `KEEP` | L3 | Manual CDC workflow passes and publishes bounded evidence. |
| `.github/workflows/lakehouse-serving.yml` | Target dispatch-only bounded serving acceptance workflow. | [Validation & CI](validation-and-ci.md): bounded Silver/ClickHouse serving sync, retry, rebuild and maintenance runtime. | `KEEP` | L3 | Manual serving workflow passes and publishes bounded evidence. |
| `.github/workflows/lakehouse-acceptance.yml` | Missing target manual full-acceptance workflow required by the CI contract. | [Validation & CI](validation-and-ci.md): preflight, full Stage V E2E, F1 and evidence publication. | `REPLACE` | L3 | Add and pass the target workflow before deleting legacy manual acceptance paths. |
| `airflow/dags/olist_cdc_local.py` | NiFi/raw CDC ingest and backfill DAGs. | `olist_lakehouse_serving.py` + Spark continuous services; Airflow boundary in `serving-and-recovery.md`. | `DELETE` | L4 | Exact target DAG inventory passes and no workflow/script/doc runtime consumer remains. |
| `airflow/dags/olist_cdc_dbt_local.py` | Old realtime dbt transform/quality DAGs. | Target finite serving/quality DAGs and Scala Spark Silver. | `DELETE` | L4 | Target DAG import check passes; old dbt project/selectors have no consumers. |
| `airflow/dags/olist_modern_data_stack_local.py` | Old local raw batch pipeline. | Target `olist_lakehouse_serving.py` and `olist_lakehouse_maintenance.py`. | `DELETE` | L4 | Batch raw DAG path and its scripts are removed/replaced; exact DAG allowlist passes. |
| `airflow/dags/olist_modern_data_stack_aws.py` | AWS/Redshift raw batch pipeline; AWS is explicitly out of the target architecture. | No target replacement in local Stage L; future cloud stack is GCP and is a separate program. | `DELETE` | L4 | Remove the DAG and all active AWS/Redshift consumers; retain only historical provenance in Git history. |

## 4. CDC, simulator, and orchestration scripts

| Path | Current role and consumers | Target contract / replacement evidence | Disposition | Owner stage | Removal condition |
| --- | --- | --- | --- | --- | --- |
| `scripts/cdc/local_lab.py` | Main local target CLI, but it contains old defaults/profiles and is a consumer bootstrap; its V10 final check must validate effective transaction state rather than historical OPEN observations. | `architecture-and-runtime.md`, Stage V V0–V10, `tests/lakehouse_platform`, Stage E latest-effective transaction contract. | `REWRITE` | L1 | Local CLI contract, effective OPEN/REJECTED diagnostic, and clean Stage V E2E PASS. |
| `scripts/cdc/stage2_admin.py` | Connector registration; currently refers to a PostgreSQL connector template/name. | `streaming/connect/olist-mysql-cdc.json`, `tests/cdc_contracts/test_connector_bootstrap.py`. | `REWRITE` | L1 | MySQL connector/topic contract and runtime status checks are green. |
| `scripts/cdc/avro_wire.py` | Old helper consumed only by the old Stage 2 integration. | `streaming.schemas.avro`/registry helpers and `tests/cdc_contracts`. | `REPLACE` | L1 | Target helpers/tests cover framing, schema IDs, and tombstones; old helper is removed in L4. |
| `scripts/cdc/benchmark_local.py` | Benchmark old raw ingest/realtime transform latency. | Target observability/latency evidence from `observability.md`; no legacy warehouse query. | `DELETE` | L4 | No target consumer remains; bounded observability tests own only the retained contract metrics. |
| `scripts/cdc/failure_injection.py` | Compose failure drills use old service names and old alert model. | Target service names and fire/resolve checks in `observability.md`. | `REWRITE` | L2 | All scenarios use real target services and target alert identities. |
| `scripts/cdc/pipeline_metrics.py` | Prometheus exporter for old raw CDC/warehouse/control tables. | Target Spark/Iceberg/serving metrics producers and bounded observability contract. | `DELETE` | L4 | The exporter had no target consumer; retained metrics are produced by target services and checked by the observability contract. |
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
| `scripts/ci/check_clickhouse_smoke.py` | Smoke check coupled to old ClickHouse/dbt profile. | Target ClickHouse serving health and `dbt/olist_clickhouse` static/runtime checks. | `DELETE` | L4 | dbt/serving contract jobs own the target checks; no separate legacy smoke runner remains. |
| `scripts/ci/check_dbt_selector_boundaries.py` | Enforces old `batch`, `realtime_transform`, `realtime_quality`, `realtime_parity` selectors. | Target dbt-clickhouse selectors and model graph tests. | `REPLACE` | L3 | Target selector contract covers the same required boundary; old project removed. |
| `scripts/ci/check_fixture_pipeline_idempotency.py` | Idempotency check for old Airflow raw batch DAG. | Target serving sync/rebuild no-op semantics and Stage V replay gates. | `REPLACE` | L1/L3 | Target idempotency test/evidence exists and old DAG is gone. |
| `scripts/ci/check_oltp_cdc_configuration.py` | PostgreSQL OLTP publication/CDC configuration check. | MySQL binlog/GTID + Debezium connector contract. | `REPLACE` | L1 | MySQL source and connector tests pass. |
| `scripts/ci/check_oltp_simulator_integration.py` | Integration runner for old OLTP simulator path. | MySQL simulator integration and `tests/mysql`/L1 seed tests. | `REWRITE` | L1 | Uses MySQL only, file-only secrets and target simulator schema. |
| `scripts/ci/check_stage2_cdc_integration.py` | Old Stage 2 PostgreSQL/Kafka/Avro runner. | Target `cdc-component` plus `tests/cdc_contracts`. | `REPLACE` | L1/L3 | Target bounded CDC runner replaces all required assertions. |
| `scripts/ci/validate_nifi_flow.py` | Static NiFi flow/schema validator. | Target Spark schema/writer/Scala contracts. | `DELETE` | L4 | NiFi tree and all consumers removed; no target test needs flow JSON. |
| `scripts/ci/validate_realtime_configuration.py` | Old realtime-core/NiFi/dbt configuration guard. | Target repository/Compose/Scala/Airflow/dbt-clickhouse contracts. | `REPLACE` | L3 | New guards cover target service/DAG/dbt inventories. |
| `scripts/ci/validate_stage6_configuration.py` | Old observability dashboard/rule/alert validator. | [Observability contract](observability.md) and target observability test. | `REPLACE` | L2/L3 | Target mapping, metric existence and fire/resolve checks pass. |
| `scripts/ingestion/correction_specs.py` | Raw S3 correction-feed definitions. | Target rejected-event/replay contract in Spark Bronze/Silver. | `DELETE` | L4 | Target rejection, replay and serving-boundary tests own the required semantics; no old correction-feed API remains. |
| `scripts/ingestion/generate_correction_feeds.py` | Generates old S3 correction feeds. | Target `ReplayMain`/bounded Bronze replay fixture. | `DELETE` | L4 | No active workflow or test consumes correction-feed files. |
| `scripts/ingestion/ingest_olist_to_s3.py` | Old source-to-S3 raw ingestion. | MySQL seeding + Spark Bronze durability path. | `DELETE` | L4 | Source contract is validated by MySQL seed and Stage V. |
| `scripts/ingestion/local_storage.py` | Old raw file/manifests/dead-letter storage helper. | Target Iceberg audit/rejected-event records and fixture contract tests. | `DELETE` | L4 | Target rejected-event tables and Spark/serving tests own the persisted evidence; no old storage API remains. |
| `scripts/ingestion/prepare_olist_raw_files.py` | Prepares old S3 raw files. | `scripts/simulation/seeding.py` and source fixture contract. | `DELETE` | L4 | No target path reads prepared raw files. |
| `scripts/ingestion/raw_files.py` | Old raw file discovery and row preparation. | MySQL source schema/seed and target event validation. | `DELETE` | L4 | Source/seed and target event contracts own the required schema/row invariants; no old file-preparation API remains. |
| `scripts/ingestion/record_validation.py` | Old raw batch validation/dead-letter thresholds. | Target `PermanentRecordFailure`/`normalization_errors` contract. | `DELETE` | L4 | Spark normalization/rejection and serving-boundary tests own target failure semantics; the old batch validator had no target consumer. |
| `scripts/ingestion/s3_storage.py` | Old S3 raw upload client. | Polaris/MinIO/Iceberg storage path; no raw upload. | `DELETE` | L4 | No target workflow or test imports the client. |
| `scripts/loading/load_raw_to_clickhouse.py` | Old CSV/raw batch loader into ClickHouse. | Finite `scripts/serving` sync + dbt-clickhouse serving component. | `DELETE` | L4 | Target serving path passes and old raw tables are removed. |
| `scripts/loading/load_raw_to_redshift.py` | Redshift raw loader. | No target replacement; the future cloud stack is GCP, not Redshift. | `DELETE` | L4 | Remove after the AWS DAG and Redshift consumers are gone. |
| `scripts/loading/raw_batch.py` | Shared old raw-batch schema/control/dead-letter model. | Target fixture/source/serving/replay contracts. | `DELETE` | L4 | All target consumers use explicit target contracts; no old raw-batch API remains. |
| `scripts/loading/replay_dead_letters.py` | Replays old raw S3 dead letters. | Spark Bronze replay and Iceberg rejected-event ledger. | `DELETE` | L4 | Spark replay and serving-quality tests own target rejection/replay semantics; the old command had no consumer. |
| `scripts/orchestration/batch_control.py` | Old raw batch status state machine. | Target serving/control transaction state in `scripts/serving/control.py`. | `DELETE` | L4 | Serving control tests cover target status transitions; the old batch state machine is removed. |
| `scripts/orchestration/control_postgres.py` | Generic PostgreSQL control client shared by old paths. | PostgreSQL remains target control plane through explicit serving consumers. | `DELETE` | L4 | Target control access is owned by the serving/control path; no parallel legacy client remains. |
| `scripts/quality/reconcile_batch.py` | Raw batch/Redshift/ClickHouse reconciliation. | Stage V/F1 parity and target serving quality DAG. | `REPLACE` | L1/L3 | Target quality evidence covers source/current/fact/mart acceptance. |
| `scripts/simulation/README.md` | Target simulator documentation, but it still contains stale J1/secret wording. | Target MySQL simulator secret and Stage V command contract. | `REWRITE` | L1/L3 | Align commands, secret names and integration prerequisites with the target stack. |
| `scripts/simulation/__init__.py` | Target simulator package marker and public exports. | Target MySQL simulator package. | `KEEP` | L1 | Retain package API while hardening implementation. |
| `scripts/simulation/__main__.py` | Target `python -m scripts.simulation` entry point. | Target simulator CLI contract. | `KEEP` | L1/L3 | Retain and cover the entry point in target CLI checks. |
| `scripts/utilities/create_dead_letter_demo_archive.py` | Creates old raw-file corruption archive. | Target rejected-event/replay fixture and Spark/serving contract tests. | `DELETE` | L4 | Target rejection fixtures are owned by the committed bounded fixture and Scala/serving tests; no archive helper is consumed. |
| `scripts/utilities/fetch_aws_secret.py` | AWS-only secret helper with no target consumer. | Local target uses file-only secrets; future cloud stack is GCP. | `DELETE` | L4 | Remove after an active-consumer scan proves no GCP or local code imports it. |
| `scripts/utilities/generate_redshift_raw_ddl.py` | Generates Redshift raw DDL. | No target replacement; the future cloud stack is GCP, not Redshift. | `DELETE` | L4 | Remove with Redshift infra and the AWS DAG. |
| `scripts/utilities/profile_olist_zip.py` | Profiles source archive and emits target-neutral source type metadata. | Target-neutral source/fixture contract and F0/F1 provenance. | `REWRITE` | L1 | Preserve deterministic read-only profiling; generated documentation now describes source/seed metadata and target transformation ownership. |
| `scripts/utilities/validate_source_contract.py` | Validates committed source fixture. | MySQL seed and Stage V preflight. | `KEEP` | L1/L3 | Keep as target fixture preflight; update only if target schema changes. |
| `scripts/testing/create_small_fixture_dataset.py` | Creates/maintains bounded source fixture and target-neutral type metadata. | Stage V bounded fixture contract with target-neutral metadata. | `REWRITE` | L1/L3 | Keep deterministic fixture generation; the committed profile remains checksum-governed and contains no cloud-specific type field. |
| `docs/source_contract.md` | Active source contract documentation. | Target-neutral MySQL source and bounded fixture contract. | `REWRITE` | L1/L3 | Source/seed metadata and target transformation ownership are now explicit; archive and profile remain unchanged. |
| `docs/source_profile.json` | Full source profile consumed by source-contract validation. | Target-neutral source profile and F0/F1 provenance. | `KEEP` | L1 | `raw_type` is a target-neutral source/seed type field; no cloud-specific field or consumer remains. |

## 5. Legacy and target tests

The target suites below are not candidates for bulk deletion. Root tests with old names are mapped individually so that useful invariants are transferred before cleanup.

| Path | What it actually checks / current consumer | Target owner and replacement evidence | Disposition | Owner stage | Removal/replacement condition |
| --- | --- | --- | --- | --- | --- |
| `tests/mysql/test_cli.py` | Simulator CLI parsing, redaction and bounded options. | `tests/mysql` target suite; MySQL file-secret CLI contract. | `REWRITE` | L1 | Target CLI tests pass; do not remove by testpath narrowing. |
| `tests/mysql/test_mysql_integration.py` | MySQL schema/user/seed integration. | `tests/mysql` + Stage V bootstrap evidence. | `REWRITE` | L1 | Target MySQL integration is green. |
| `tests/mysql/test_repository.py` | Repository DML/idempotency/transaction behavior. | `tests/mysql`, target `SimulatorRepository`. | `REWRITE` | L1 | MySQL transaction and failure semantics are covered. |
| `tests/mysql/test_seeding.py` | Seed conversion, batching and upsert SQL. | `tests/mysql`, target MySQL `ON DUPLICATE KEY UPDATE`. | `REWRITE` | L1 | No PostgreSQL SQL or plaintext password state remains. |
| `tests/mysql/test_source_schema.py` | Source DDL and secret/schema assertions. | `tests/mysql` and `mysql-kafka-avro.md`. | `REWRITE` | L1 | Restore MySQL DML, file-only secret and exact grant invariants. |
| `tests/cdc_contracts/test_connector_bootstrap.py` | Target MySQL connector template, topic/schema configuration. | `streaming/connect/olist-mysql-cdc.json`, bounded CDC job. | `REWRITE` | L1 | Test remains target-specific and passes against actual template. |
| `tests/test_airflow_secret_bootstrap.py` | File-secret normalization in Airflow wrapper. | `tests/lakehouse_platform/test_secret_bootstrap.py`/serving secret contract. | `REWRITE` | L1 | Renamed target suite covers file-only behavior; old path removed in L4. |
| `tests/test_avro_schema_compatibility.py` | Backward-compatible Avro evolution rules. | `tests/cdc_contracts/test_schema_evolution.py`, `test_avro_helpers.py`, Scala contract tests. | `REPLACE` | L1 | All compatibility cases have target suite ownership; old path removed in L4. |
| `tests/test_batch_cdc_parity_integration.py` | Old batch vs CDC runner, status and parity gates. | Stage V/F1 and target component workflows. | `REPLACE` | L3 | Assertions are owned by candidate-only target evidence; old integration runner removed in L4. |
| `tests/test_ci_data_quality_failures.py` | Fixture contract/dead-letter/reconciliation failure behavior coupled to deleted raw helpers. | `tests/lakehouse_platform/test_source_contract.py`, target normalization/table contracts, serving boundary and Scala transaction tests. | `REPLACE` | L1/L3 | Source failure, rejection state and transaction-boundary invariants have target owners; old raw-helper suite removed in L4. |
| `tests/test_clickhouse_batch_phase3.py` | CSV/raw batch staging and old local DAG. | `tests/dbt_clickhouse`, `tests/serving`, target serving component. | `REPLACE` | L1/L3 | Only target serving/partition invariants survive; old path removed in L4. |
| `tests/test_clickhouse_phase1_contracts.py` | Old ClickHouse/analytics db bootstrap and dbt profile. | `tests/dbt_clickhouse` and Compose/serving contracts. | `REPLACE` | L1/L3 | Target native DDL, secret and serving database checks pass; old path removed in L4. |
| `tests/test_clickhouse_phase4_dbt_graph.py` | Old `dbt/olist_analytics` batch/realtime graph. | `tests/dbt_clickhouse`, `serving-and-recovery.md`. | `REPLACE` | L1/L3 | Target model graph/selectors cover business invariants; old path removed in L4. |
| `tests/test_clickhouse_phase5_cdc_ingestion.py` | NiFi/S3/raw ClickHouse ingest and old local lab. | `tests/cdc_contracts`, `tests/lakehouse_platform`, Stage V. | `REPLACE` | L1/L3 | Transport/storage invariants moved to target stack; old path removed in L4. |
| `tests/test_clickhouse_phase6_realtime_dbt_quality.py` | Old realtime dbt project quality/retry behavior. | Scala Spark tests + `tests/dbt_clickhouse` + serving tests. | `REPLACE` | L1/L3 | Target Silver/serving quality evidence is green; old path removed in L4. |
| `tests/test_clickhouse_phase7_ci_observability.py` | Old ClickHouse/NiFi/PostgreSQL exporter/rule/workflow assumptions. | `tests/observability/test_contract.py`, `test_ci_contract.py` and observability CI job. | `REWRITE` | L2/L3 | Target producer→scrape→rule→dashboard chain is tested; old path removed in L4. |
| `tests/test_control_postgres_phase2.py` | Control DB separation and old batch-control integration. | `tests/lakehouse_platform/test_control_postgres_contract.py`/serving control contract. | `REWRITE` | L1 | Target control PostgreSQL remains and raw warehouse is excluded; old path removed in L4. |
| `tests/test_dead_letter_pipeline.py` | Old raw-file dead-letter/replay and batch status. | Target rejected records, Spark transaction state, normalization/table contracts and serving quality. | `REPLACE` | L1/L2 | Target rejection/replay boundary invariants have owners; old raw-file suite removed in L4. |
| `tests/test_nifi_optimization.py` | NiFi processor/flow loading, codecs and fanout. | No target equivalent; Spark data plane owns the path. | `DELETE` | L4 | Delete only with `streaming/nifi/**` and old flow consumers. |
| `tests/test_oltp_seed_contracts.py` | Source schema edge cases for old OLTP seed. | `tests/mysql/test_schema_contract.py`, MySQL DDL and seed contract. | `REWRITE` | L1 | Assertions run against MySQL target schema; old path removed in L4. |
| `tests/test_postgres_oracle_export.py` | Canonical hash helpers plus old PostgreSQL/dbt inventory expectations. | `tests/stage_v/test_f0_parity_contracts.py` and frozen F0/F1 artifacts. | `REPLACE` | L1/L4 | Hash semantics and F0 oracle readers are retained; old path removed in L4. |
| `tests/test_simulation.py` | Workload planning, composite keys and graceful stop. | `tests/mysql`/simulation target tests. | `REWRITE` | L1 | Keep semantic coverage under target database contract. |
| `tests/test_stage2_configuration.py` | Old Stage 2 PostgreSQL connector/status/topic assumptions. | `tests/cdc_contracts/test_target_connector_contract.py` and target topics. | `REPLACE` | L1 | All target connector assertions transferred; old path removed in L4. |
| `tests/test_stage3_configuration.py` | NiFi profile, MinIO raw bucket and flow configuration. | Target MinIO/Polaris/Spark platform contracts. | `REWRITE` | L1/L2 | Retain only target storage/security assertions. |
| `tests/test_stage3_contracts.py` | NiFi landing/coverage manifest and raw bytes model. | Spark Bronze/Silver/transaction contracts and Scala tests. | `REPLACE` | L1 | No landing/coverage test is deleted before its target invariant is mapped. |
| `tests/test_stage4_contracts.py` | Raw S3 manifest/offset reconciliation and old warehouse loader. | Iceberg Bronze/Silver progress/audit and target serving. | `REPLACE` | L1 | Target audit/progress contract has equivalent failure coverage. |
| `tests/test_stage5_contracts.py` | Old realtime dbt model/publication graph. | Spark Silver + ClickHouse serving/dbt-clickhouse tests. | `REPLACE` | L1/L3 | Target graph/publication checks pass. |
| `tests/test_stage6_contracts.py` | Old dashboards, alert rules and Loki/metrics labels. | `observability.md`, `tests/observability/test_contract.py` and target CI contract. | `REWRITE` | L2 | New chain is tested with real target names/metrics; old path removed in L4. |

### Target suites explicitly retained

`tests/cdc_contracts/**`, `tests/dbt_clickhouse/**`, `tests/lakehouse_platform/**`, `tests/mysql/**`, `tests/observability/**`, `tests/serving/**`, `tests/stage_v/**` and `streaming/spark/scala/src/test/**` are `KEEP`. Their test collection must remain explicit in CI, and a zero-collection result is a failure. `tests/mysql/test_source_schema.py` is `REWRITE`, but the directory itself is not disposable. Observability tests run in the dedicated observability component job, not in the Stage V runner.

## 6. Fixtures and schema assets

| Path | Role / consumer | Target contract / replacement evidence | Disposition | Owner stage | Removal condition |
| --- | --- | --- | --- | --- | --- |
| `tests/fixtures/olist_small/olist_small.zip` | Frozen bounded source archive used by Stage V/F0. | Stage V and F0/F1 fixture contract. | `KEEP` | L0/F1 | Never replace without checksum-governed review. |
| `tests/fixtures/olist_small/source/**` | Reviewable uncompressed copy of the bounded source CSVs. | Stage V source fixture contract. | `KEEP` | L0/F1 | Keep content aligned with the frozen archive; changes require checksum-governed fixture review. |
| `tests/fixtures/olist_small/source_profile_small.json` | Bounded source profile used by Stage V source validation; uses target-neutral `raw_type` metadata. | Target-neutral Stage V source profile. | `KEEP` | L1/L3 | Keep the profile and archive checksum stable; changes require explicit fixture review. |
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
| `streaming/schemas/cdc-landing/v1.avsc` | Old NiFi landing schema. | Target Bronze record/table contract and Scala tests. | `DELETE` | L4 | Bronze table/schema contracts own bytes/tombstone semantics; no old landing-schema consumer remains. |
| `streaming/schemas/cdc-coverage/v1.schema.json` | Old NiFi coverage manifest schema. | Target Spark transaction/progress/audit tables and Stage V harness. | `DELETE` | L4 | Target progress and transaction contracts own coverage semantics; no old manifest consumer remains. |
| `streaming/schemas/captured-writer-schemas/**` | Captured Debezium/Apicurio writer schemas used by Scala and CDC contracts. | `mysql-kafka-avro.md`, `tests/cdc_contracts`. | `KEEP` | L1 | Frozen provenance; no rewrite during legacy cleanup. E2E capture must not mutate this path; a new bundle needs an explicit reviewed commit. |

## 7. Secret templates and secret sources

| Path / variable | Current role or defect | Target contract / replacement evidence | Disposition | Owner stage | Removal/replacement condition |
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
| `scripts/parity/export_f0_baseline.py` | One-shot F0/F1 parity-support exporter for controlled source-baseline regeneration and diagnostics. | Frozen `tests/fixtures/final_parity/**` and `validate_f0_oracle.py`. | `KEEP` | F1 | Retain until F1 parity is PASS and reviewed; remove only in a later cleanup if no further baseline regeneration or diagnostic use is required. |
| `scripts/parity/final_parity_contract.json` | Relation manifest required by the retained one-shot F0/F1 parity exporter. | Frozen F0 oracle metadata and target candidate manifest. | `KEEP` | F1 | Retain with the exporter until F1 parity is PASS and reviewed; remove only together with the exporter in a later cleanup. |
| `scripts/parity/canonical_stage5_relations.json` | Retired Stage 5 realtime relation manifest, including the old control audit relation. | Target F0/F1 manifest and Stage V contracts. | `DELETE` | L4 | No target exporter, workflow or runtime reads this manifest. |
| `scripts/parity/{__init__.py,canonical_manifest.py,canonical_batch_relations.json,compare_manifests.py,export_clickhouse_candidate.py,validate_f0_oracle.py}` | F0 validation and candidate-only F1 comparator/export readers. | `final-parity.md` | `KEEP` | F1 | F0 oracle/readers are immutable inputs; no regular baseline regeneration. |
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
| `scripts/validation/stage_v_probes.py` | Target Stage V probe module with dedicated MySQL source and control-plane probes. | `testing-and-evidence.md` | `KEEP` | L1–L4 | Keep the dedicated MySQL reader/simulator secret contract and target control-plane checks. |

## 10. L0 decision summary

1. Target MySQL, Debezium/Kafka Connect, Apicurio, Spark/Scala, Iceberg/Polaris, ClickHouse serving, Airflow control plane, F0/F1 readers and target test suites are `KEEP`/`REWRITE`; they are not cleanup casualties.
2. Old PostgreSQL OLTP, NiFi, Redshift, raw S3/Parquet loader and `dbt/olist_analytics` paths are `DELETE` or `REPLACE`, but only after their invariants have a named target owner.
3. Observability is not optional cleanup: old dashboards/rules are `REWRITE`/`DELETE`, and no phantom exporter/metric/service is accepted as a target.
4. `tests/fixtures/postgresql_oracle/**` is not interchangeable with the frozen `tests/fixtures/final_parity/**`; the former is disposable only after F0 readers and test mappings are verified.
5. The accidental use of `postgres_password.txt` and `airflow_api_secret_key.txt` as defaults for target MySQL/MinIO credentials is a target configuration defect, not a reason to delete target secret tests.
