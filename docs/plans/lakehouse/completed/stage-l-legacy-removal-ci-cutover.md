# Detailed Stage L Plan: Phased Target Cutover

- Status: COMPLETE.
- Goal: move the repository from the legacy PostgreSQL/NiFi/old raw batch and realtime pipeline to the agreed MySQL → Debezium → Kafka → Spark/Iceberg → ClickHouse serving stack while preserving verifiable evidence for every transition.
- Scope rule: Stage L is complete only when every gate is closed by raw evidence tied to the candidate commit.

## 1. Execution rules

1. Before implementation, return the working tree to a clean baseline after separately confirming the destructive rollback. Handoffs, unfinished deletions and unverified reports are not sources of truth.
2. After runtime-affecting substages L1, L2 and L4, run the complete clean Stage V E2E V0–V10; store evidence in `data/stage-l-evidence/<substage>/<run-id>/`. L3 is CI/workflow-only: when it does not change Compose, runtime, DAGs, the dbt project, fixtures or the Stage V runner, a full E2E run is not a required gate. If such files change, stop and obtain a separate decision before running the full test.
3. Green unit/contract CI does not replace runtime E2E. A missing mandatory gate is a FAIL.
4. Do not delete tests to reduce test paths or obtain a green CI result. A target replacement must exist first, or all code covered by the test must be removed.
5. Do not modify or delete the frozen F0 oracle, its metadata or its readers.
6. Every runtime, exporter, DAG, schema and workflow must have one explicit owner and one verifiable contract.

## 2. Target inventory and invariants

Cloud boundary: AWS/Redshift cloud artifacts are removed in L4; GCP/BigQuery is a separate future program described in [GCP migration plan](../../gcp-spark-iceberg-bigquery-migration.md) and is not implemented by Stage L. Local MinIO S3-compatible endpoints, `s3a://` paths and the Iceberg S3 adapter remain where they are the target object-store implementation; they are not AWS cloud infrastructure.

Normative L0 artifacts:

- [L0 baseline report](../../../reports/lakehouse-stage-l0-baseline.md) — actual rollback, E2E run and static findings; update the status after the process is complete.
- [Legacy artifact disposition register](../contracts/legacy-disposition-register.md) — one-line `KEEP`, `REWRITE`, `REPLACE` or `DELETE` decision and deletion condition.
- [Target observability contract](../contracts/observability.md) — producer/exporter/scrape/rule/dashboard/evidence chain and known phantom-target gaps.
- [Target tests and evidence contract](../contracts/testing-and-evidence.md) — required suites, transfer rules and the boundary between baseline diagnostics and acceptance evidence.
- [Validation and CI contract](../contracts/validation-and-ci.md) — required common/bounded/manual workflows and the prohibition on skipped or missing acceptance jobs.

The following must remain and pass validation:

- MySQL 8.4 source: `olist_oltp` and `olist_simulator` databases, ROW/GTID binlog, exact source schema and file-only secrets.
- Target Debezium/Kafka Connect bootstrap, MySQL connector contract, Apicurio compatibility and Kafka topic manifest.
- Kafka, Apicurio Registry 3.3.0, MinIO, Polaris, Spark master/worker/bronze/silver/geolocation/ops, ClickHouse serving and Airflow.
- Target serving control PostgreSQL and the target DAG inventory only: `olist_lakehouse_maintenance.py` and `olist_lakehouse_serving.py`, exporting exactly four DAG IDs: `olist_lakehouse_maintenance`, `olist_lakehouse_serving_sync`, `olist_lakehouse_quality`, `olist_lakehouse_serving_rebuild`.
- `dbt/olist_clickhouse`, `scripts/serving` and final parity/F0 readers.
- ScalaTest and target suites `tests/mysql`, `tests/cdc_contracts`, `tests/lakehouse_platform`, `tests/dbt_clickhouse`, `tests/observability`, `tests/serving` and `tests/stage_v`.
- Actual observability chain: metric producer → Compose service/exporter → Prometheus scrape job → recording/alert rule → dashboard/runbook → acceptance check.

The current runtime contract specifies Debezium Connect 3.6.0.Final in `streaming/runtime-versions.json` and the architecture/runtime contracts. Do not downgrade to 3.0.0.Final without a separate contract, image/plugin inventory and test change.

## 3. L0 — baseline reset and inventory review

This was a preparation gate, not a new-runtime implementation.

- The unfinished change set was rolled back to a clean tree at baseline commit `9214cd1de05ab37cdeae27a1a0b633963e8ae8d6`; the committed Stage L plan was preserved.
- Immediately after rollback, baseline Stage V E2E `stage_l0_baseline_20260804` ran through V0–V9 and failed at V10 because of the raw-versus-effective transaction-state check. The command and evidence root are recorded in the [disposition register](../contracts/legacy-disposition-register.md); this failure is baseline diagnostic evidence, not acceptance evidence.
- After analysis, a separate clean corrective run `stage_l0_v10fix_20260804` passed V0–V10 with a targeted effective-state `validate-final` fix and no manual data mutation. That result did not close the required L1 writer/materializer/planner regression work.
- The baseline commit, fixture SHA-256, target inventory, legacy inventory and original Stage V E2E run were recorded in the [disposition register](../contracts/legacy-disposition-register.md).
- Every legacy workflow, script, test, fixture and secret template was mapped to exactly one of four dispositions: `KEEP`, `REWRITE`, `REPLACE` or `DELETE`. AWS/Redshift are neither compatible nor deferred scope: only `DELETE` is recorded for them. The four decisions define the target fate of each artifact without claiming that a future stage has already been implemented.
- At L0, the Stage L plan was active and neither `serving-cutover` nor the master plan declared L complete.

The L0 disposition register had to contain the path, artifact role, discovered consumers, target contract, selected disposition, owning substage, replacement test/evidence and deletion condition. An undefined or unverified `DELETE` was prohibited; new exceptions to the four decisions required separate consumer evidence and could not be used to retain AWS/Redshift.

Exit criteria:

- clean baseline tree;
- inventory review with recorded consumers and explicit orphan-scan gates before every `DELETE`;
- an agreed disposition register without unverified `DELETE` decisions;
- unchanged F0 oracle/readers;
- known baseline failures recorded separately from acceptance evidence;
- baseline and corrective E2E outcomes added to the register/report without presenting their statuses as Stage L completion.

## 4. L1 — target contracts, tests and runtime repair

First restore target-stack verifiability, then fix defects discovered during review.

### Required test coverage

Restore or transfer the following coverage; preserving the old names is optional:

- `tests/mysql/test_cli.py`, `test_mysql_integration.py`, `test_repository.py` and `test_seeding.py`;
- tests/cdc_contracts/test_connector_bootstrap.py;
- `tests/test_simulation.py` and `tests/test_oltp_seed_contracts.py`;
- tests/test_stage2_configuration.py;
- tests/test_control_postgres_phase2.py;
- tests/test_airflow_secret_bootstrap.py;
- tests/test_avro_schema_compatibility.py;
- data-quality/dead-letter invariants from `tests/test_ci_data_quality_failures.py` and `tests/test_dead_letter_pipeline.py` when the corresponding ingestion/loading code remains;
- observability invariants from `tests/test_clickhouse_phase7_ci_observability.py` in the target lakehouse suite.

The remaining `tests/mysql/test_source_schema.py` must check both the schema and the absence of plaintext password state and must preserve MySQL-specific DML invariants. The current test path must not hide root tests before their shared invariants are transferred.

### Runtime fixes

- Rewrite seeding fully to `mysql.connector` and MySQL SQL: qualify `olist_oltp`/`olist_simulator`, use `ON DUPLICATE KEY UPDATE`, implement correct composite-key upserts, Decimal conversion, batch contract 5000, seed idempotency and one transaction per entity.
- Remove PostgreSQL `execute_values`, `ON CONFLICT`, `public.*`, `simulator_control` and `::jsonb` from the target simulator.
- Restore explicit transaction boundaries, rollback/commit, failure persistence, graceful stop and Decimal-compatible replay speed. Do not introduce plaintext `--password`/state in the CLI or `DatabaseSettings`.
- Restore the target streaming/connect bootstrap and MySQL connector template called by `local_lab`. Removing all of `streaming/connect` is not allowed.
- Rewrite `stage2_admin` around the MySQL connector name/plugin/topic contract; its current `local_lab`/CDC consumers are not removed in this stage.
- Convert `docs/source_profile.json`, `tests/fixtures/olist_small/source_profile_small.json` and the fixture generator to target-neutral metadata; active `redshift_raw_type` fields must not survive L1.
- Rewrite the `infra/control-postgres` bootstrap and `scripts/serving/control.py` around target-owned `serving.*` schema checks; retain legacy `audit`/`cdc_audit` migrations until L4 only when replacement evidence exists.
- Analyze the baseline E2E failure: run `stage_l0_baseline_20260804` passed V0–V9, but V10/`10-final` saw one raw `OPEN` audit observation. The L0 diagnostic run `stage_l0_v10fix_20260804` confirmed the effective-state explanation and produced a clean PASS without manual SQL; L1 must still encode this behavior in writer/materializer/planner contracts and regression tests.
- Record the transaction-state invariant as a separate L1 deliverable: `audit.mysql_transactions` may be append-only observation history, but the serving planner and V10 must read effective state. BEGIN and END split across micro-batches must collapse to `COMPLETE`; a genuinely unresolved BEGIN must not disappear from the planner merely because `end_kafka_offset IS NULL`. Add regression coverage for split BEGIN/END, unresolved OPEN, `REJECTED → COMPLETE`, duplicate END and offset/order checks in Scala/serving tests.
- Rewrite `TransactionBatchWriter.scala`, `scripts/serving/clickhouse.py`, `scripts/serving/boundary.py`, the target serving DAG and `local_lab.py` narrowly for this behavior; other target data-plane/serving files are not candidates for mass deletion.
- Remove the `_capture_and_contracts` side effect: baseline/E2E capture must not overwrite tracked `streaming/schemas/captured-writer-schemas/**` with dynamic timestamps/provenance. Runtime capture must remain in temporary evidence, and changing the frozen writer bundle requires a separate contract-driven commit.
- Align Compose images, runtime versions and contract versions; do not silently downgrade Debezium.
- Fix environment names: `KAFKA_CONNECT_HOST_PORT` must match Compose, and every used secret-source variable must be documented.

Exit criteria:

- target contract/unit suites pass;
- `local_lab` import/bootstrap paths do not reference missing files;
- clean Stage V E2E V0–V10 PASS;
- raw evidence and checksums are stored in `data/stage-l-evidence/L1/`.

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

## 5. L2 — observability for the new stack

Observability is a mandatory part of the migration. It may be implemented as a separate stage, but Stage L cannot be declared complete with phantom targets or legacy alerts.

### Runtime mapping

For each target job, first record the producer, endpoint, Compose service and healthcheck. Two solutions are allowed: add a pinned exporter service or configure a real metrics endpoint on an existing component. References to nonexistent services such as `mysql-exporter`, `spark-iceberg`, `cdc-component-exporter`, `cdc-pipeline-exporter`, `kafka-exporter`, `statsd-exporter`, `node-exporter` or `cadvisor` are not allowed without matching Compose definitions.

For Alertmanager and Alloy, the decision is already made: L2 adds real pinned services because they are part of the target alert/log chain. For Airflow, the old StatsD mapping is replaced by a health/API probe; an unimplemented target cannot remain in the contract without an owner, endpoint and acceptance evidence.

Minimum target coverage:

- MySQL availability/binlog/replication health;
- Debezium Connect REST, connector/task state and heartbeat;
- Kafka broker/topic end offsets and checkpoint-derived consumer lag with bounded topic ownership;
- Spark Bronze/Silver/ops health and streaming progress;
- MinIO/Polaris/ClickHouse serving;
- Airflow/serving/control-plane metrics;
- Prometheus/Grafana/Loki/Alloy self-health.

### Cleanup and contracts

- Delete or rewrite NiFi dashboards, queue metrics, the NiFi-specific MinIO policy/secret and PostgreSQL WAL alerts.
- Delete `CdcRetainedWalHighAndGrowing` and other PostgreSQL source alerts when they cannot be proven against the target source.
- Do not use raw `kafka_consumergroup_lag` as the lag source for Spark Structured Streaming: its offsets live in checkpoints, not in a normal committed consumer group. Use the real Kafka partition end offset, the published Bronze checkpoint offset and explicit target topic/owner selectors.
- Validate YAML/JSON schemas, target host existence, alert metric existence, dashboard query references and runbook links.
- Chaos commands must use real Compose service names and a unique project name. For example, use `kafka-connect`, `spark-bronze`/`spark-silver` or a dedicated target Spark service, not fictitious `debezium` or `spark-iceberg` services.

Exit criteria:

- all configured scrape targets exist and are verifiably UP in a healthy stack;
- target alerts fire and resolve during bounded fault injection;
- Grafana dashboards contain no 404 or phantom metric panels;
- observability acceptance evidence is stored in `data/stage-l-evidence/L2/`;
- the Stage V E2E script is unchanged and is not run in L2. Its independent V0–V10 acceptance is checked by a separate gate in L3.

### L2 implementation result (2026-08-04)

- [Stage L2 implementation report](../../../reports/lakehouse-stage-l2.md)
  records the target observability implementation, runtime diagnostics and
  evidence paths. At that time Stage L remained `ACTIVE`; this was not a Stage L
  completion claim.
- The bounded acceptance run
  `data/stage-l-evidence/L2/stage_l2_20260804_full/observability-acceptance-final.json`
  passed. It verified 18 Prometheus jobs, 10 target probes, 23 alert rules,
  Grafana dashboards/datasources, Loki labels/log query and Alertmanager
  webhook delivery metrics.
- `failure-connect.json` and `failure-minio.json` both proved `FIRING →
  RESOLVED` transitions against real Compose services. The live stack also
  confirmed the fresh-catalog `spark-ops` path after its self-creating status
  table fix.
- Kafka lag is deliberately implemented as a join of Kafka exporter partition
  end offsets with Spark Bronze checkpoint progress. The plan does not treat a
  synthetic or empty ordinary consumer-group lag metric as Spark truth.
- `scripts/validation/stage_v_candidate_e2e.py` was not modified and the Stage
  V E2E was not run. Its independent V0–V10 gate remains L3 scope.

## 6. L3 — CI and acceptance cutover

### Required common CI

Required jobs:

- docs/repository contracts: YAML/TOML/Markdown links, compileall, expanded legacy guard and F0 validation;
- python-quality: ruff check, ruff format --check, pyright;
- python-contract-tests: explicit target suites, JUnit artifact and failure on zero collection;
- scala-fast: scalafmt, Test/compile, ScalaTest, package and JAR content/dependency contract;
- compose-contract: all relevant profiles, exact service inventory, no container_name, image/config/secret assertions;
- airflow-dag-imports: build target Airflow image, exact DAG inventory and dbt path contract;
- dbt-clickhouse-static: deps, parse, compile, selector/source/model contract;
- ci-success: with `if: always()`, fail on failed or skipped required jobs.

Each job receives a timeout, lockfile cache, pinned major actions, read-only permissions and failure artifacts/JUnit. Compose config alone is not a service-inventory check.

### Bounded component CI

Bounded CI is split by launch mode and ownership:

- `.github/workflows/lakehouse-components.yml` contains only fast
  PR/push checks for the Spark image, Airflow runtime and observability contract;
- `.github/workflows/lakehouse-cdc.yml` contains the dispatch-only bounded
  `cdc-component` with initial snapshot, catch-up and restart;
- `.github/workflows/lakehouse-serving.yml` contains the dispatch-only bounded
  `serving-component` with finite sync, authoritative no-op retry, rebuild and
  maintenance paths.

Manual-only runtime jobs are not embedded in the PR workflow through a job-level
`if`: that created misleading `skipped` jobs. Each dispatch-only workflow has
one required runtime job, diagnostics, evidence and cleanup in `always()`.
Path filters and summaries must not allow success when an automatic contract job
is missing or failed.

### Manual acceptance

- preflight checks the full candidate SHA, fixture/oracle checksums, inputs, capacity and a unique Compose project;
- stage-v-e2e runs the complete `scripts/validation/stage_v_candidate_e2e.py`, not only `tests/stage_v`;
- final-parity compares candidate-only output with the frozen F0 oracle;
- publish-evidence uploads raw JSON, Markdown, JUnit, selected logs and the final failure status;
- F0 is never regenerated by the acceptance workflow.

Exit criteria:

- common CI and relevant bounded workflow definitions pass local contract checks;
- the automatic component-contract workflow contains only fast bounded Spark,
  Airflow and observability jobs and no manual-only `skipped` jobs;
- CDC and serving are represented by separate dispatch-only workflows that can
  be selected and launched independently from the Actions page;
- the manual acceptance workflow is dispatch-only and publishes upstream evidence even on failure;
- static L3 evidence is stored in `data/stage-l-evidence/L3/`;
- the full Stage V E2E for CI-only L3 is not run automatically and is not a mandatory condition of this substage.

### L3 implementation result (2026-08-04)

Status: **CI/workflow cutover implemented; Stage L was still ACTIVE at this point**. The implementation was limited to CI-owned files:

- `.github/workflows/ci.yml` was replaced with target common CI containing `ci-success`, explicit target test paths, the Scala image/JAR contract, Compose profile checks, exact Airflow DAG inventory and the dbt-clickhouse static contract;
- `.github/workflows/lakehouse-components.yml` was added with fast bounded
  Spark, Airflow and observability contract jobs;
- dispatch-only `.github/workflows/lakehouse-cdc.yml` and
  `.github/workflows/lakehouse-serving.yml` were added so that heavy runtime
  checks do not appear as `skipped` jobs in the PR workflow and can run independently;
- dispatch-only `.github/workflows/lakehouse-acceptance.yml` was added with candidate SHA, destructive confirmation, candidate E2E/F1 job definitions and always-run evidence publication;
- only the three legacy workflows explicitly listed in the CI contract were removed: `batch-cdc-parity.yml`, `cdc-stage2-kafka-debezium.yml` and `cdc-stage6-operations.yml`;
- CI validators `check_repository_contracts.py` and `check_dbt_clickhouse_contract.py` were added, and `check_airflow_dag_imports.py` was strengthened to use the exact target DAG allowlist;
- CI/observability contract tests were updated. No tests under `tests/` were deleted.

Local L3 checks: repository contract `PASS`, dbt contract `PASS` (20 models, sources `serving_cdc`/`serving_control`), 19 observability/CI tests `PASS`, Ruff check/format `PASS` and Pyright `PASS`. The full Stage V runner was not changed or run because L3 did not change Compose/runtime/DAG/dbt/fixture files.

Known boundary: `scripts/cdc/local_lab.py final-parity` remained a pre-existing `not_available` stub on that candidate and accepted only the old hidden `--phase` interface, while the normative F1 CLI requires `--run-id`, `--oracle` and `--timeout`. Therefore the manual F1 workflow was described as a target gate, but no actual F1 PASS was claimed; F1 runtime implementation belongs to the separate Stage F1 work.

Details and evidence paths are recorded in the [L3 report](../../../reports/lakehouse-stage-l3.md).

## 7. L4 — legacy removal

Deletion is performed only after L1–L3 and the mapping review.

### Deletions allowed after consumer review

- the old PostgreSQL OLTP infrastructure and old PostgreSQL source secrets;
- NiFi runtime, NiFi workflows/scripts/tests, NiFi-specific MinIO assets and runtime-version entries;
- old PostgreSQL/legacy DAGs;
- `dbt/olist_analytics` and its old batch/realtime selectors;
- Redshift infrastructure, Redshift-only utilities/dependencies and old raw batch paths because AWS/Redshift are fully removed from the program; the future GCP stack has a separate cloud plan;
- legacy control PostgreSQL `audit`/`cdc_audit` DDL after their verifiable invariants move to Spark/serving target owners;
- old ClickHouse raw CDC/batch/runtime paths when target dbt/serving paths do not use them;
- deleted legacy GitHub workflows and their orphan CI scripts;
- old PostgreSQL oracle fixtures after F0 acceptance and confirmation that no consumers remain.

### Mandatory orphan scan before deletion

Review each remaining item separately, then delete or rewrite it:

- `scripts/cdc/realtime_transform.py` and `scripts/ci/check_dbt_selector_boundaries.py`;
- `scripts/cdc/warehouse_ingest.py` and `pipeline_metrics.py`;
- scripts/utilities/generate_redshift_raw_ddl.py;
- unused streaming/minio/init.sh, stale MinIO policies and old README instructions; retain only the target `streaming/minio/Dockerfile`/`start.sh` plus `infra/polaris/minio/**` initializer and policies;
- streaming/runtime-versions.json entries for NiFi;
- `_nifi_written_at` in active schemas/ClickHouse raw DDL;
- old connector names, old DBT paths, redshift/public/simulator_control references.

### What remains

- target serving control PostgreSQL with target-owned schemas/migrations only;
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
- evidence is stored in `data/stage-l-evidence/L4/`.

### L4 implementation result (2026-08-05)

Implementation is complete. The candidate removed the legacy
PostgreSQL OLTP, Redshift/AWS, NiFi, old raw ClickHouse, old dbt and legacy
control-migration families after the disposition review. It also removes the
legacy DAGs, obsolete CI runners, old secret templates, old oracle fixtures and
legacy root tests whose target ownership is recorded in the disposition
register. The retained tests were moved into explicit target suite owners;
observability tests remain a separate component suite and are not coupled to
the Stage V runner.

The candidate also adds an independent legacy-orphan guard, makes the control
PostgreSQL bootstrap target-only, removes legacy runtime dependencies and
updates active documentation/runbooks to the MySQL → Debezium → Kafka →
Spark/Iceberg → serving path. AWS/Redshift is a definitive `DELETE` decision;
no cloud runtime is deferred by L4, and GCP remains a separate future program.

Final L4 status is **PASS** for the current candidate: the orphan guard,
complete target static checks and clean Stage V V0–V10 run all pass. The run
`stage_l4_20260805_f0_restored` completed all mandatory gates and normal scoped
runtime cleanup; evidence is recorded in [the L4 report](../../../reports/lakehouse-stage-l4.md)
and `data/stage-l-evidence/L4/stage_l4_20260805_f0_restored/`. Stage L is now
**COMPLETE**; Stage F1 is the next remaining program stage.

## 8. L5 — final Stage L gate

Stage L is COMPLETE because the following conditions are satisfied:

- L1, L2, L3 and L4 gates PASS;
- common CI, bounded component workflows and manual acceptance pass;
- observability normal-scrape and fire/resolve evidence pass;
- target tests are retained or migrated, and deleted tests have explicit mappings;
- legacy runtime/configuration/dependencies/secrets/active CI references are absent;
- F0 oracle/readers unchanged;
- the candidate and evidence are tied to exact source, fixture and oracle identities.

The `serving-cutover` plan now records the completed L boundary, while Stage F1 becomes NEXT.

## 9. What must not be done

- Do not delete target tests merely because they are located in `tests/test_*.py`.
- Do not delete all of `streaming/connect`; it contains the target Debezium/MySQL bootstrap and contract artifacts.
- Do not rewrite simulator semantics during cleanup without contract-driven tests.
- Do not downgrade a pinned runtime version without updating all contracts and acceptance checks.
- Do not move AWS/Redshift runtime to GCP automatically within Stage L: GCP is a separate program with its own contracts and consumer review.
- Do not add plaintext secrets, a `--password` CLI option or password fields to state objects.
- Do not add Prometheus targets, dashboards or chaos commands for nonexistent services.
- Do not delete the local MinIO S3-compatible adapter merely because `AWS`/`S3` names appear in a library/API layer; delete AWS cloud/Redshift consumers, not the required target object-store protocol.
- Do not declare Stage L complete with failed/missing E2E gates or solely on the basis of a handoff or local unit-test count.
