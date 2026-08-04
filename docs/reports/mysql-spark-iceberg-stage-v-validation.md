# Stage V Candidate E2E Validation Report

- **Status**: `PASS`
- **Run ID**: `stage_l4_20260805_f0_restored`
- **Compose Project**: `olist_stage_v`
- **Started At**: `2026-08-04T22:36:45.873168+00:00`
- **Finished At**: `2026-08-04T23:00:17.644487+00:00`

---

## 1. Final Verdict

Stage V validation completed with status `PASS`.

All mandatory gates passed in a single clean-domain run.

- **Stage L Authorization**: `AUTHORIZED` (allowed to proceed to Stage L)

---

## 2. Gate Execution Results (V0 - V10)

| Gate | Name | Status | Duration (s) |
| --- | --- | --- | ---: |
| `00-preflight` | 00-preflight | `PASS` | 144.899 |
| `01-harness-ready` | 01-harness-ready | `PASS` | 0.0 |
| `02-clean-bootstrap` | 02-clean-bootstrap | `PASS` | 296.637 |
| `03-initial-snapshot` | 03-initial-snapshot | `PASS` | 266.449 |
| `04-crud-and-restart` | 04-crud-and-restart | `PASS` | 150.528 |
| `05-caught-up` | 05-caught-up | `PASS` | 99.843 |
| `06-serving-sync` | 06-serving-sync | `PASS` | 310.47 |
| `07-dbt-and-stable-views` | 07-dbt-and-stable-views | `PASS` | 5.388 |
| `08-additive-schema` | 08-additive-schema | `PASS` | 69.002 |
| `09-rebuild` | 09-rebuild | `PASS` | 28.221 |
| `10-final` | 10-final | `PASS` | 5.78 |

---

## 3. Evidence-Derived Assertions

The following machine-readable block is rendered directly from the persisted
gate summaries. Counts, IDs, command output and parity details are not
reconstructed from static claims.

- **Passed mandatory gates**: `11/11`

```json
{
  "gate_count": 11,
  "gates": {
    "00-preflight": {
      "assertions": [
        {
          "detail": "COMPOSE_PROJECT_NAME=olist_stage_v",
          "name": "compose_project_name_check",
          "status": "PASS"
        },
        {
          "detail": {
            "expected": {
              "AIRFLOW_URL": "http://127.0.0.1:8080",
              "APICURIO_CCOMPAT_URL": "http://127.0.0.1:8081/apis/ccompat/v7",
              "APICURIO_REGISTRY_URL": "http://127.0.0.1:8081/apis/registry/v3",
              "CLICKHOUSE_HOST": "127.0.0.1",
              "CLICKHOUSE_PORT": "8123",
              "COMPOSE_FILE": "C:\\Users\\fyujv\\source\\repos\\olist-mds\\compose.yaml",
              "KAFKA_BOOTSTRAP_SERVERS": "127.0.0.1:9092",
              "KAFKA_CONNECT_URL": "http://127.0.0.1:8083",
              "MYSQL_HOST": "127.0.0.1",
              "MYSQL_HOST_PORT": "3306"
            },
            "mismatches": {}
          },
          "name": "endpoint_provenance",
          "status": "PASS"
        },
        {
          "detail": "All pre-commit hooks passed cleanly",
          "name": "pre_commit_check",
          "status": "PASS"
        },
        {
          "detail": {
            "captured_after_pre_commit": true,
            "changed_paths": [
              ".dockerignore",
              ".env.example",
              ".github/workflows/ci.yml",
              ".gitignore",
              ".sqlfluff",
              ".sqlfluffignore",
              "README.md",
              "airflow/dags/olist_cdc_dbt_local.py",
              "airflow/dags/olist_cdc_local.py",
              "airflow/dags/olist_modern_data_stack_aws.py",
              "airflow/dags/olist_modern_data_stack_local.py",
              "dbt/olist_analytics/analyses/batch_reconciliation.sql",
              "dbt/olist_analytics/analyses/batch_runs.sql",
              "dbt/olist_analytics/analyses/daily_revenue_by_seller_state.sql",
              "dbt/olist_analytics/analyses/dead_letter_events.sql",
              "dbt/olist_analytics/analyses/dead_letter_replays.sql",
              "dbt/olist_analytics/analyses/monthly_category_arpu.sql",
              "dbt/olist_analytics/dbt_project.yml",
              "dbt/olist_analytics/macros/business_calculations.sql",
              "dbt/olist_analytics/macros/clickhouse_incremental_partition_replacement.sql",
              "dbt/olist_analytics/macros/elementary_materialization.sql",
              "dbt/olist_analytics/macros/generate_schema_name.sql",
              "dbt/olist_analytics/macros/incremental_fact_maintenance.sql",
              "dbt/olist_analytics/macros/realtime_cdc.sql",
              "dbt/olist_analytics/macros/rounding.sql",
              "dbt/olist_analytics/macros/warehouse_compat.sql",
              "dbt/olist_analytics/models/_groups.yml",
              "dbt/olist_analytics/models/core/dim_customer_scd2.sql",
              "dbt/olist_analytics/models/core/dim_date.sql",
              "dbt/olist_analytics/models/core/dim_order_status.sql",
              "dbt/olist_analytics/models/core/dim_product_scd2.sql",
              "dbt/olist_analytics/models/core/dim_seller.sql",
              "dbt/olist_analytics/models/core/fact_order_items.sql",
              "dbt/olist_analytics/models/core/schema.yml",
              "dbt/olist_analytics/models/intermediate/int_customer_current_attributes.sql",
              "dbt/olist_analytics/models/intermediate/int_order_payment_allocations.sql",
              "dbt/olist_analytics/models/intermediate/int_product_current_attributes.sql",
              "dbt/olist_analytics/models/intermediate/schema.yml",
              "dbt/olist_analytics/models/marts/mart_daily_revenue.sql",
              "dbt/olist_analytics/models/marts/mart_monthly_arpu.sql",
              "dbt/olist_analytics/models/marts/schema.yml",
              "dbt/olist_analytics/models/parity/realtime_parity_checksums.sql",
              "dbt/olist_analytics/models/parity/realtime_parity_daily_revenue_batch.sql",
              "dbt/olist_analytics/models/parity/realtime_parity_daily_revenue_realtime.sql",
              "dbt/olist_analytics/models/parity/realtime_parity_grain_diffs.sql",
              "dbt/olist_analytics/models/parity/realtime_parity_monthly_arpu_batch.sql",
              "dbt/olist_analytics/models/parity/realtime_parity_monthly_arpu_realtime.sql",
              "dbt/olist_analytics/models/parity/realtime_parity_report.sql",
              "dbt/olist_analytics/models/parity/schema.yml",
              "dbt/olist_analytics/models/realtime/core/_realtime_core__models.yml",
              "dbt/olist_analytics/models/realtime/core/dim_customer_realtime_scd2.sql",
              "dbt/olist_analytics/models/realtime/core/dim_date_realtime.sql",
              "dbt/olist_analytics/models/realtime/core/dim_order_status_realtime.sql",
              "dbt/olist_analytics/models/realtime/core/dim_product_realtime_scd2.sql",
              "dbt/olist_analytics/models/realtime/core/dim_seller_realtime.sql",
              "dbt/olist_analytics/models/realtime/core/fact_order_items_realtime.sql",
              "dbt/olist_analytics/models/realtime/core/hist_cdc__customers.sql",
              "dbt/olist_analytics/models/realtime/core/hist_cdc__order_items.sql",
              "dbt/olist_analytics/models/realtime/core/hist_cdc__order_payments.sql",
              "dbt/olist_analytics/models/realtime/core/hist_cdc__order_reviews.sql",
              "dbt/olist_analytics/models/realtime/core/hist_cdc__orders.sql",
              "dbt/olist_analytics/models/realtime/core/hist_cdc__product_category_translation.sql",
              "dbt/olist_analytics/models/realtime/core/hist_cdc__products.sql",
              "dbt/olist_analytics/models/realtime/core/hist_cdc__sellers.sql",
              "dbt/olist_analytics/models/realtime/core/int_realtime_order_payment_allocations.sql",
              "dbt/olist_analytics/models/realtime/marts/_realtime_marts__models.yml",
              "dbt/olist_analytics/models/realtime/marts/mart_daily_revenue_realtime.sql",
              "dbt/olist_analytics/models/realtime/marts/mart_monthly_arpu_realtime.sql",
              "dbt/olist_analytics/models/realtime/staging/_realtime__models.yml",
              "dbt/olist_analytics/models/realtime/staging/_realtime__sources.yml",
              "dbt/olist_analytics/models/realtime/staging/int_cdc__changed_order_ids.sql",
              "dbt/olist_analytics/models/realtime/staging/int_cdc__changed_periods.sql",
              "dbt/olist_analytics/models/realtime/staging/stg_cdc__customers_current.sql",
              "dbt/olist_analytics/models/realtime/staging/stg_cdc__customers_events.sql",
              "dbt/olist_analytics/models/realtime/staging/stg_cdc__order_items_current.sql",
              "dbt/olist_analytics/models/realtime/staging/stg_cdc__order_items_events.sql",
              "dbt/olist_analytics/models/realtime/staging/stg_cdc__order_payments_current.sql",
              "dbt/olist_analytics/models/realtime/staging/stg_cdc__order_payments_events.sql",
              "dbt/olist_analytics/models/realtime/staging/stg_cdc__order_reviews_current.sql",
              "dbt/olist_analytics/models/realtime/staging/stg_cdc__order_reviews_events.sql",
              "dbt/olist_analytics/models/realtime/staging/stg_cdc__orders_current.sql",
              "dbt/olist_analytics/models/realtime/staging/stg_cdc__orders_events.sql",
              "dbt/olist_analytics/models/realtime/staging/stg_cdc__product_category_translation_current.sql",
              "dbt/olist_analytics/models/realtime/staging/stg_cdc__product_category_translation_events.sql",
              "dbt/olist_analytics/models/realtime/staging/stg_cdc__products_current.sql",
              "dbt/olist_analytics/models/realtime/staging/stg_cdc__products_events.sql",
              "dbt/olist_analytics/models/realtime/staging/stg_cdc__sellers_current.sql",
              "dbt/olist_analytics/models/realtime/staging/stg_cdc__sellers_events.sql",
              "dbt/olist_analytics/models/staging/audit/_audit__sources.yml",
              "dbt/olist_analytics/models/staging/olist/_olist__models.yml",
              "dbt/olist_analytics/models/staging/olist/_olist__sources.yml",
              "dbt/olist_analytics/models/staging/olist/stg_olist__customer_profile_changes.sql",
              "dbt/olist_analytics/models/staging/olist/stg_olist__customers.sql",
              "dbt/olist_analytics/models/staging/olist/stg_olist__geolocation.sql",
              "dbt/olist_analytics/models/staging/olist/stg_olist__order_items.sql",
              "dbt/olist_analytics/models/staging/olist/stg_olist__order_payments.sql",
              "dbt/olist_analytics/models/staging/olist/stg_olist__order_reviews.sql",
              "dbt/olist_analytics/models/staging/olist/stg_olist__orders.sql",
              "dbt/olist_analytics/models/staging/olist/stg_olist__product_attribute_changes.sql",
              "dbt/olist_analytics/models/staging/olist/stg_olist__product_category_translation.sql",
              "dbt/olist_analytics/models/staging/olist/stg_olist__products.sql",
              "dbt/olist_analytics/models/staging/olist/stg_olist__sellers.sql",
              "dbt/olist_analytics/models/unit_tests_phase0.yml",
              "dbt/olist_analytics/package-lock.yml",
              "dbt/olist_analytics/packages.yml",
              "dbt/olist_analytics/profiles.yml.example",
              "dbt/olist_analytics/seeds/.gitkeep",
              "dbt/olist_analytics/selectors.yml",
              "dbt/olist_analytics/snapshots/snap_customers.sql",
              "dbt/olist_analytics/snapshots/snap_products.sql",
              "dbt/olist_analytics/tests/assert_batch_reconciliation_passed.sql",
              "dbt/olist_analytics/tests/assert_customer_scd2_windows_are_positive.sql",
              "dbt/olist_analytics/tests/assert_daily_revenue_components_match.sql",
              "dbt/olist_analytics/tests/assert_fact_order_items_matches_staging_grain.sql",
              "dbt/olist_analytics/tests/assert_monthly_arpu_calculation.sql",
              "dbt/olist_analytics/tests/assert_no_overlapping_customer_scd2_windows.sql",
              "dbt/olist_analytics/tests/assert_no_overlapping_product_scd2_windows.sql",
              "dbt/olist_analytics/tests/assert_one_current_customer_scd2_row.sql",
              "dbt/olist_analytics/tests/assert_one_current_product_scd2_row.sql",
              "dbt/olist_analytics/tests/assert_order_payment_allocations_balance.sql",
              "dbt/olist_analytics/tests/assert_product_scd2_windows_are_positive.sql",
              "dbt/olist_analytics/tests/assert_realtime_latest_reconciliation_passed.sql",
              "dbt/olist_analytics/tests/assert_realtime_mart_freshness.sql",
              "dbt/olist_analytics/tests/assert_realtime_offset_continuity.sql",
              "dbt/olist_analytics/tests/assert_realtime_parity_passed.sql",
              "dbt/olist_analytics/tests/generic/_generic__tests.yml",
              "dbt/olist_analytics/tests/generic/test_non_negative.sql",
              "dbt/olist_analytics/tests/generic/test_unique_combination_of_columns.sql",
              "dbt/olist_clickhouse/README.md",
              "docker/airflow/load-env-and-run.sh",
              "docker/secrets/dev/mysql_spark_reference_reader_password.txt",
              "docker/secrets/dev/postgres_password.txt",
              "docker/secrets/dev/redshift_password.txt",
              "docker/spark/status/bronze/.gitkeep",
              "docker/spark/status/silver/.gitkeep",
              "docs/architecture.md",
              "docs/ci.md",
              "docs/data_model.md",
              "docs/diagrams.md",
              "docs/plans/lakehouse/contracts/final-parity.md",
              "docs/plans/lakehouse/contracts/legacy-disposition-register.md",
              "docs/plans/lakehouse/contracts/mysql-kafka-avro.md",
              "docs/plans/lakehouse/contracts/testing-and-evidence.md",
              "docs/runbook_macos.md",
              "docs/runbook_windows.md",
              "docs/runbooks/cdc-alert-testing.md",
              "docs/runbooks/cdc-connector-resnapshot.md",
              "docs/runbooks/cdc-kafka-replay.md",
              "docs/runbooks/cdc-local-end-to-end-validation.md",
              "docs/runbooks/cdc-realtime-dbt.md",
              "docs/runbooks/cdc-rebuild-from-landing.md",
              "docs/runbooks/cdc-schema-migration.md",
              "docs/runbooks/cdc-secret-rotation.md",
              "docs/runbooks/cdc-service-restart.md",
              "docs/runbooks/cdc-warehouse-ingest.md",
              "docs/runbooks/cdc-warehouse-rebuild.md",
              "docs/source_contract.md",
              "infra/aws/realtime/README.md",
              "infra/clickhouse/initdb/001_create_databases.sql",
              "infra/clickhouse/initdb/002_create_raw_batch_tables.sql",
              "infra/clickhouse/initdb/003_create_raw_cdc_tables.sql",
              "infra/clickhouse/initdb/004_create_pipeline_runtime_tables.sql",
              "infra/control-postgres/init-control-db.sh",
              "infra/control-postgres/initdb/001_create_schemas.sql",
              "infra/control-postgres/initdb/002_create_batch_control_tables.sql",
              "infra/control-postgres/initdb/003_create_cdc_control_tables.sql",
              "infra/control-postgres/initdb/004_create_cdc_transform_control_tables.sql",
              "infra/control-postgres/initdb/999_grant_control_role.sql",
              "infra/oltp/README.md",
              "infra/oltp/initdb/010_create_roles.sh",
              "infra/oltp/initdb/020_create_oltp_schema.sql",
              "infra/oltp/initdb/030_configure_cdc.sql",
              "infra/redshift/001_create_schemas.sql",
              "infra/redshift/002_create_raw_tables.sql",
              "infra/redshift/003_create_audit_tables.sql",
              "infra/redshift/004_copy_raw_tables_template.sql",
              "infra/redshift/005_create_correction_tables.sql",
              "infra/redshift/realtime/README.md",
              "observability/README.md",
              "pyproject.toml",
              "scripts/cdc/README.md",
              "scripts/cdc/avro_wire.py",
              "scripts/cdc/benchmark_local.py",
              "scripts/cdc/local_lab.py",
              "scripts/cdc/pipeline_metrics.py",
              "scripts/cdc/realtime_transform.py",
              "scripts/cdc/warehouse_ingest.py",
              "scripts/ci/check_batch_cdc_parity_integration.py",
              "scripts/ci/check_clickhouse_cdc_ingest_resilience.py",
              "scripts/ci/check_clickhouse_fact_insert_overwrite_edges.py",
              "scripts/ci/check_clickhouse_smoke.py",
              "scripts/ci/check_dbt_selector_boundaries.py",
              "scripts/ci/check_fixture_pipeline_idempotency.py",
              "scripts/ci/check_oltp_cdc_configuration.py",
              "scripts/ci/check_oltp_simulator_integration.py",
              "scripts/ci/check_stage2_cdc_integration.py",
              "scripts/ci/pipeline_helpers.py",
              "scripts/ci/validate_nifi_flow.py",
              "scripts/ci/validate_realtime_configuration.py",
              "scripts/ci/validate_stage6_configuration.py",
              "scripts/ingestion/__init__.py",
              "scripts/ingestion/correction_specs.py",
              "scripts/ingestion/generate_correction_feeds.py",
              "scripts/ingestion/ingest_olist_to_s3.py",
              "scripts/ingestion/local_storage.py",
              "scripts/ingestion/prepare_olist_raw_files.py",
              "scripts/ingestion/raw_files.py",
              "scripts/ingestion/record_validation.py",
              "scripts/ingestion/s3_storage.py",
              "scripts/loading/__init__.py",
              "scripts/loading/load_raw_to_clickhouse.py",
              "scripts/loading/load_raw_to_redshift.py",
              "scripts/loading/raw_batch.py",
              "scripts/loading/replay_dead_letters.py",
              "scripts/orchestration/__init__.py",
              "scripts/orchestration/batch_control.py",
              "scripts/orchestration/control_postgres.py",
              "scripts/parity/canonical_stage5_relations.json",
              "scripts/quality/__init__.py",
              "scripts/quality/reconcile_batch.py",
              "scripts/serving/control.py",
              "scripts/utilities/create_dead_letter_demo_archive.py",
              "scripts/utilities/fetch_aws_secret.py",
              "scripts/utilities/generate_redshift_raw_ddl.py",
              "scripts/utilities/profile_olist_zip.py",
              "scripts/validation/stage_v_probes.py",
              "streaming/kafka/README.md",
              "streaming/minio/README.md",
              "streaming/minio/cdc-loader-policy.json",
              "streaming/minio/init.sh",
              "streaming/minio/nifi-policy.json",
              "streaming/nifi/Dockerfile",
              "streaming/nifi/README.md",
              "streaming/nifi/component_metrics.py",
              "streaming/nifi/deploy_flow.py",
              "streaming/nifi/flow/olist-cdc-v1.json",
              "streaming/nifi/metrics_proxy.py",
              "streaming/nifi/parameters/local.template.json",
              "streaming/nifi/python/BuildCdcAvro.py",
              "streaming/nifi/python/BuildDlqEnvelope.py",
              "streaming/nifi/python/DescribeAvroBatch.py",
              "streaming/nifi/python/PutImmutableS3Object.py",
              "streaming/nifi/python/__init__.py",
              "streaming/nifi/python/cdc_common.py",
              "streaming/nifi/python/requirements.txt",
              "streaming/nifi/start.sh",
              "streaming/runtime-versions.json",
              "streaming/schemas/README.md",
              "streaming/schemas/cdc-coverage/v1.schema.json",
              "streaming/schemas/cdc-landing/v1.avsc",
              "streaming/schemas/normalized/customers/v1.avsc",
              "streaming/schemas/normalized/order_items/v1.avsc",
              "streaming/schemas/normalized/order_payments/v1.avsc",
              "streaming/schemas/normalized/order_reviews/v1.avsc",
              "streaming/schemas/normalized/orders/v1.avsc",
              "streaming/schemas/normalized/product_category_translation/v1.avsc",
              "streaming/schemas/normalized/products/v1.avsc",
              "streaming/schemas/normalized/sellers/v1.avsc",
              "tests/cdc_contracts/test_connector_bootstrap.py",
              "tests/dbt_clickhouse/test_project_contract.py",
              "tests/fixtures/postgresql_oracle/dbt_inventory.json",
              "tests/fixtures/postgresql_oracle/postgres_batch_oracle.json",
              "tests/fixtures/postgresql_oracle/postgres_stage5_oracle.json",
              "tests/lakehouse_platform/test_l1_runtime_contracts.py",
              "tests/mysql/test_seeding.py",
              "tests/mysql/test_source_schema.py",
              "tests/observability/test_ci_contract.py",
              "tests/serving/test_control.py",
              "tests/stage_v/test_stage_v_harness.py",
              "tests/test_airflow_secret_bootstrap.py",
              "tests/test_avro_schema_compatibility.py",
              "tests/test_batch_cdc_parity_integration.py",
              "tests/test_ci_data_quality_failures.py",
              "tests/test_clickhouse_batch_phase3.py",
              "tests/test_clickhouse_phase1_contracts.py",
              "tests/test_clickhouse_phase4_dbt_graph.py",
              "tests/test_clickhouse_phase5_cdc_ingestion.py",
              "tests/test_clickhouse_phase6_realtime_dbt_quality.py",
              "tests/test_clickhouse_phase7_ci_observability.py",
              "tests/test_control_postgres_phase2.py",
              "tests/test_dead_letter_pipeline.py",
              "tests/test_nifi_optimization.py",
              "tests/test_oltp_seed_contracts.py",
              "tests/test_postgres_oracle_export.py",
              "tests/test_stage2_configuration.py",
              "tests/test_stage3_configuration.py",
              "tests/test_stage3_contracts.py",
              "tests/test_stage4_contracts.py",
              "tests/test_stage5_contracts.py",
              "tests/test_stage6_contracts.py",
              "uv.lock",
              "docs/reports/lakehouse-stage-l4.md",
              "scripts/ci/check_legacy_orphans.py",
              "tests/cdc_contracts/test_schema_evolution.py",
              "tests/cdc_contracts/test_target_connector_contract.py",
              "tests/lakehouse_platform/test_control_postgres_contract.py",
              "tests/lakehouse_platform/test_secret_bootstrap.py",
              "tests/lakehouse_platform/test_source_contract.py",
              "tests/mysql/test_schema_contract.py",
              "tests/observability/test_contract.py",
              "tests/stage_v/test_f0_parity_contracts.py"
            ],
            "commands_ok": true,
            "diagnostics": "",
            "dirty": true,
            "head": "4060845b6911b0166ff3785a166df22c5d4991c4",
            "worktree_digest": "b271fbfefdfb63ac07da89d5cc630a24425dafa681e74d4c79b5d9ade6995e8b"
          },
          "name": "source_tree_identity",
          "status": "PASS"
        },
        {
          "detail": "uv.lock is consistent",
          "name": "uv_lock_check",
          "status": "PASS"
        },
        {
          "detail": "Python test suites passed",
          "name": "python_tests_check",
          "status": "PASS"
        },
        {
          "detail": "Scala sbt scalafmtCheckAll and test suite passed",
          "name": "scala_sbt_build_check",
          "status": "PASS"
        }
      ],
      "command": [
        [
          "uv",
          "run",
          "pre-commit",
          "run",
          "--all-files"
        ],
        [
          "git",
          "rev-parse",
          "HEAD"
        ],
        [
          "git",
          "status",
          "--porcelain=v1",
          "--untracked-files=all"
        ],
        [
          "git",
          "diff",
          "--binary",
          "HEAD",
          "--"
        ],
        [
          "git",
          "ls-files",
          "--others",
          "--exclude-standard",
          "-z"
        ],
        [
          "uv",
          "lock",
          "--check"
        ],
        [
          "uv",
          "run",
          "pytest",
          "tests/cdc_contracts",
          "tests/lakehouse_platform",
          "tests/mysql",
          "tests/dbt_clickhouse",
          "tests/serving",
          "tests/stage_v"
        ],
        [
          "docker",
          "build",
          "--target",
          "scala-builder",
          "-f",
          "docker/spark/Dockerfile",
          "."
        ]
      ],
      "command_results": [
        {
          "args": [
            "uv",
            "run",
            "pre-commit",
            "run",
            "--all-files"
          ],
          "duration_seconds": 26.594,
          "exit_code": 0,
          "stderr": "",
          "stdout": "trim trailing whitespace.................................................Passed\nfix end of files.........................................................Passed\ncheck yaml...............................................................Passed\ncheck toml...............................................................Passed\nruff check...............................................................Passed\nruff format..............................................................Passed\npyright..................................................................Passed\ndbt-parse................................................................Passed\n",
          "timed_out": false
        },
        {
          "args": [
            "git",
            "rev-parse",
            "HEAD"
          ],
          "duration_seconds": 0.031,
          "exit_code": 0,
          "stderr": "",
          "stdout": "4060845b6911b0166ff3785a166df22c5d4991c4\n",
          "timed_out": false
        },
        {
          "args": [
            "git",
            "status",
            "--porcelain=v1",
            "--untracked-files=all"
          ],
          "duration_seconds": 0.063,
          "exit_code": 0,
          "stderr": "",
          "stdout": ".sql\n D dbt/olist_analytics/models/realtime/core/hist_cdc__products.sql\n D dbt/olist_analytics/models/realtime/core/hist_cdc__sellers.sql\n D dbt/olist_analytics/models/realtime/core/int_realtime_order_payment_allocations.sql\n D dbt/olist_analytics/models/realtime/marts/_realtime_marts__models.yml\n D dbt/olist_analytics/models/realtime/marts/mart_daily_revenue_realtime.sql\n D dbt/olist_analytics/models/realtime/marts/mart_monthly_arpu_realtime.sql\n D dbt/olist_analytics/models/realtime/staging/_realtime__models.yml\n D dbt/olist_analytics/models/realtime/staging/_realtime__sources.yml\n D dbt/olist_analytics/models/realtime/staging/int_cdc__changed_order_ids.sql\n D dbt/olist_analytics/models/realtime/staging/int_cdc__changed_periods.sql\n D dbt/olist_analytics/models/realtime/staging/stg_cdc__customers_current.sql\n D dbt/olist_analytics/models/realtime/staging/stg_cdc__customers_events.sql\n D dbt/olist_analytics/models/realtime/staging/stg_cdc__order_items_current.sql\n D dbt/olist_analytics/models/realtime/staging/stg_cdc__order_items_events.sql\n D dbt/olist_analytics/models/realtime/staging/stg_cdc__order_payments_current.sql\n D dbt/olist_analytics/models/realtime/staging/stg_cdc__order_payments_events.sql\n D dbt/olist_analytics/models/realtime/staging/stg_cdc__order_reviews_current.sql\n D dbt/olist_analytics/models/realtime/staging/stg_cdc__order_reviews_events.sql\n D dbt/olist_analytics/models/realtime/staging/stg_cdc__orders_current.sql\n D dbt/olist_analytics/models/realtime/staging/stg_cdc__orders_events.sql\n D dbt/olist_analytics/models/realtime/staging/stg_cdc__product_category_translation_current.sql\n D dbt/olist_analytics/models/realtime/staging/stg_cdc__product_category_translation_events.sql\n D dbt/olist_analytics/models/realtime/staging/stg_cdc__products_current.sql\n D dbt/olist_analytics/models/realtime/staging/stg_cdc__products_events.sql\n D dbt/olist_analytics/models/realtime/staging/stg_cdc__sellers_current.sql\n D dbt/olist_analytics/models/realtime/staging/stg_cdc__sellers_events.sql\n D dbt/olist_analytics/models/staging/audit/_audit__sources.yml\n D dbt/olist_analytics/models/staging/olist/_olist__models.yml\n D dbt/olist_analytics/models/staging/olist/_olist__sources.yml\n D dbt/olist_analytics/models/staging/olist/stg_olist__customer_profile_changes.sql\n D dbt/olist_analytics/models/staging/olist/stg_olist__customers.sql\n D dbt/olist_analytics/models/staging/olist/stg_olist__geolocation.sql\n D dbt/olist_analytics/models/staging/olist/stg_olist__order_items.sql\n D dbt/olist_analytics/models/staging/olist/stg_olist__order_payments.sql\n D dbt/olist_analytics/models/staging/olist/stg_olist__order_reviews.sql\n D dbt/olist_analytics/models/staging/olist/stg_olist__orders.sql\n D dbt/olist_analytics/models/staging/olist/stg_olist__product_attribute_changes.sql\n D dbt/olist_analytics/models/staging/olist/stg_olist__product_category_translation.sql\n D dbt/olist_analytics/models/staging/olist/stg_olist__products.sql\n D dbt/olist_analytics/models/staging/olist/stg_olist__sellers.sql\n D dbt/olist_analytics/models/unit_tests_phase0.yml\n D dbt/olist_analytics/package-lock.yml\n D dbt/olist_analytics/packages.yml\n D dbt/olist_analytics/profiles.yml.example\n D dbt/olist_analytics/seeds/.gitkeep\n D dbt/olist_analytics/selectors.yml\n D dbt/olist_analytics/snapshots/snap_customers.sql\n D dbt/olist_analytics/snapshots/snap_products.sql\n D dbt/olist_analytics/tests/assert_batch_reconciliation_passed.sql\n D dbt/olist_analytics/tests/assert_customer_scd2_windows_are_positive.sql\n D dbt/olist_analytics/tests/assert_daily_revenue_components_match.sql\n D dbt/olist_analytics/tests/assert_fact_order_items_matches_staging_grain.sql\n D dbt/olist_analytics/tests/assert_monthly_arpu_calculation.sql\n D dbt/olist_analytics/tests/assert_no_overlapping_customer_scd2_windows.sql\n D dbt/olist_analytics/tests/assert_no_overlapping_product_scd2_windows.sql\n D dbt/olist_analytics/tests/assert_one_current_customer_scd2_row.sql\n D dbt/olist_analytics/tests/assert_one_current_product_scd2_row.sql\n D dbt/olist_analytics/tests/assert_order_payment_allocations_balance.sql\n D dbt/olist_analytics/tests/assert_product_scd2_windows_are_positive.sql\n D dbt/olist_analytics/tests/assert_realtime_latest_reconciliation_passed.sql\n D dbt/olist_analytics/tests/assert_realtime_mart_freshness.sql\n D dbt/olist_analytics/tests/assert_realtime_offset_continuity.sql\n D dbt/olist_analytics/tests/assert_realtime_parity_passed.sql\n D dbt/olist_analytics/tests/generic/_generic__tests.yml\n D dbt/olist_analytics/tests/generic/test_non_negative.sql\n D dbt/olist_analytics/tests/generic/test_unique_combination_of_columns.sql\n M dbt/olist_clickhouse/README.md\n M docker/airflow/load-env-and-run.sh\n M docker/secrets/dev/mysql_spark_reference_reader_password.txt\n D docker/secrets/dev/postgres_password.txt\n D docker/secrets/dev/redshift_password.txt\n M docker/spark/status/bronze/.gitkeep\n M docker/spark/status/silver/.gitkeep\n M docs/architecture.md\n M docs/ci.md\n M docs/data_model.md\n M docs/diagrams.md\n M docs/plans/lakehouse/contracts/final-parity.md\n M docs/plans/lakehouse/contracts/legacy-disposition-register.md\n M docs/plans/lakehouse/contracts/mysql-kafka-avro.md\n M docs/plans/lakehouse/contracts/testing-and-evidence.md\n M docs/runbook_macos.md\n M docs/runbook_windows.md\n M docs/runbooks/cdc-alert-testing.md\n M docs/runbooks/cdc-connector-resnapshot.md\n M docs/runbooks/cdc-kafka-replay.md\n M docs/runbooks/cdc-local-end-to-end-validation.md\n M docs/runbooks/cdc-realtime-dbt.md\n M docs/runbooks/cdc-rebuild-from-landing.md\n M docs/runbooks/cdc-schema-migration.md\n M docs/runbooks/cdc-secret-rotation.md\n M docs/runbooks/cdc-service-restart.md\n M docs/runbooks/cdc-warehouse-ingest.md\n M docs/runbooks/cdc-warehouse-rebuild.md\n M docs/source_contract.md\n D infra/aws/realtime/README.md\n D infra/clickhouse/initdb/001_create_databases.sql\n D infra/clickhouse/initdb/002_create_raw_batch_tables.sql\n D infra/clickhouse/initdb/003_create_raw_cdc_tables.sql\n D infra/clickhouse/initdb/004_create_pipeline_runtime_tables.sql\n M infra/control-postgres/init-control-db.sh\n M infra/control-postgres/initdb/001_create_schemas.sql\n D infra/control-postgres/initdb/002_create_batch_control_tables.sql\n D infra/control-postgres/initdb/003_create_cdc_control_tables.sql\n D infra/control-postgres/initdb/004_create_cdc_transform_control_tables.sql\n M infra/control-postgres/initdb/999_grant_control_role.sql\n D infra/oltp/README.md\n D infra/oltp/initdb/010_create_roles.sh\n D infra/oltp/initdb/020_create_oltp_schema.sql\n D infra/oltp/initdb/030_configure_cdc.sql\n D infra/redshift/001_create_schemas.sql\n D infra/redshift/002_create_raw_tables.sql\n D infra/redshift/003_create_audit_tables.sql\n D infra/redshift/004_copy_raw_tables_template.sql\n D infra/redshift/005_create_correction_tables.sql\n D infra/redshift/realtime/README.md\n M observability/README.md\n M pyproject.toml\n M scripts/cdc/README.md\n D scripts/cdc/avro_wire.py\n D scripts/cdc/benchmark_local.py\n M scripts/cdc/local_lab.py\n D scripts/cdc/pipeline_metrics.py\n D scripts/cdc/realtime_transform.py\n D scripts/cdc/warehouse_ingest.py\n D scripts/ci/check_batch_cdc_parity_integration.py\n D scripts/ci/check_clickhouse_cdc_ingest_resilience.py\n D scripts/ci/check_clickhouse_fact_insert_overwrite_edges.py\n D scripts/ci/check_clickhouse_smoke.py\n D scripts/ci/check_dbt_selector_boundaries.py\n D scripts/ci/check_fixture_pipeline_idempotency.py\n D scripts/ci/check_oltp_cdc_configuration.py\n D scripts/ci/check_oltp_simulator_integration.py\n D scripts/ci/check_stage2_cdc_integration.py\n D scripts/ci/pipeline_helpers.py\n D scripts/ci/validate_nifi_flow.py\n D scripts/ci/validate_realtime_configuration.py\n D scripts/ci/validate_stage6_configuration.py\n D scripts/ingestion/__init__.py\n D scripts/ingestion/correction_specs.py\n D scripts/ingestion/generate_correction_feeds.py\n D scripts/ingestion/ingest_olist_to_s3.py\n D scripts/ingestion/local_storage.py\n D scripts/ingestion/prepare_olist_raw_files.py\n D scripts/ingestion/raw_files.py\n D scripts/ingestion/record_validation.py\n D scripts/ingestion/s3_storage.py\n D scripts/loading/__init__.py\n D scripts/loading/load_raw_to_clickhouse.py\n D scripts/loading/load_raw_to_redshift.py\n D scripts/loading/raw_batch.py\n D scripts/loading/replay_dead_letters.py\n D scripts/orchestration/__init__.py\n D scripts/orchestration/batch_control.py\n D scripts/orchestration/control_postgres.py\n D scripts/parity/canonical_stage5_relations.json\n D scripts/quality/__init__.py\n D scripts/quality/reconcile_batch.py\n M scripts/serving/control.py\n D scripts/utilities/create_dead_letter_demo_archive.py\n D scripts/utilities/fetch_aws_secret.py\n D scripts/utilities/generate_redshift_raw_ddl.py\n M scripts/utilities/profile_olist_zip.py\n M scripts/validation/stage_v_probes.py\n M streaming/kafka/README.md\n M streaming/minio/README.md\n D streaming/minio/cdc-loader-policy.json\n D streaming/minio/init.sh\n D streaming/minio/nifi-policy.json\n D streaming/nifi/Dockerfile\n D streaming/nifi/README.md\n D streaming/nifi/component_metrics.py\n D streaming/nifi/deploy_flow.py\n D streaming/nifi/flow/olist-cdc-v1.json\n D streaming/nifi/metrics_proxy.py\n D streaming/nifi/parameters/local.template.json\n D streaming/nifi/python/BuildCdcAvro.py\n D streaming/nifi/python/BuildDlqEnvelope.py\n D streaming/nifi/python/DescribeAvroBatch.py\n D streaming/nifi/python/PutImmutableS3Object.py\n D streaming/nifi/python/__init__.py\n D streaming/nifi/python/cdc_common.py\n D streaming/nifi/python/requirements.txt\n D streaming/nifi/start.sh\n M streaming/runtime-versions.json\n M streaming/schemas/README.md\n D streaming/schemas/cdc-coverage/v1.schema.json\n D streaming/schemas/cdc-landing/v1.avsc\n D streaming/schemas/normalized/customers/v1.avsc\n D streaming/schemas/normalized/order_items/v1.avsc\n D streaming/schemas/normalized/order_payments/v1.avsc\n D streaming/schemas/normalized/order_reviews/v1.avsc\n D streaming/schemas/normalized/orders/v1.avsc\n D streaming/schemas/normalized/product_category_translation/v1.avsc\n D streaming/schemas/normalized/products/v1.avsc\n D streaming/schemas/normalized/sellers/v1.avsc\n M tests/cdc_contracts/test_connector_bootstrap.py\n M tests/dbt_clickhouse/test_project_contract.py\n D tests/fixtures/postgresql_oracle/dbt_inventory.json\n D tests/fixtures/postgresql_oracle/postgres_batch_oracle.json\n D tests/fixtures/postgresql_oracle/postgres_stage5_oracle.json\n M tests/lakehouse_platform/test_l1_runtime_contracts.py\n M tests/mysql/test_seeding.py\n M tests/mysql/test_source_schema.py\n M tests/observability/test_ci_contract.py\n M tests/serving/test_control.py\n M tests/stage_v/test_stage_v_harness.py\n D tests/test_airflow_secret_bootstrap.py\n D tests/test_avro_schema_compatibility.py\n D tests/test_batch_cdc_parity_integration.py\n D tests/test_ci_data_quality_failures.py\n D tests/test_clickhouse_batch_phase3.py\n D tests/test_clickhouse_phase1_contracts.py\n D tests/test_clickhouse_phase4_dbt_graph.py\n D tests/test_clickhouse_phase5_cdc_ingestion.py\n D tests/test_clickhouse_phase6_realtime_dbt_quality.py\n D tests/test_clickhouse_phase7_ci_observability.py\n D tests/test_control_postgres_phase2.py\n D tests/test_dead_letter_pipeline.py\n D tests/test_nifi_optimization.py\n D tests/test_oltp_seed_contracts.py\n D tests/test_postgres_oracle_export.py\n D tests/test_stage2_configuration.py\n D tests/test_stage3_configuration.py\n D tests/test_stage3_contracts.py\n D tests/test_stage4_contracts.py\n D tests/test_stage5_contracts.py\n D tests/test_stage6_contracts.py\n M uv.lock\n?? docs/reports/lakehouse-stage-l4.md\n?? scripts/ci/check_legacy_orphans.py\n?? tests/cdc_contracts/test_schema_evolution.py\n?? tests/cdc_contracts/test_target_connector_contract.py\n?? tests/lakehouse_platform/test_control_postgres_contract.py\n?? tests/lakehouse_platform/test_secret_bootstrap.py\n?? tests/lakehouse_platform/test_source_contract.py\n?? tests/mysql/test_schema_contract.py\n?? tests/observability/test_contract.py\n?? tests/stage_v/test_f0_parity_contracts.py\n",
          "timed_out": false
        },
        {
          "args": [
            "git",
            "diff",
            "--binary",
            "HEAD",
            "--"
          ],
          "duration_seconds": 0.218,
          "exit_code": 0,
          "stderr": "",
          "stdout": "841c366620e906d54430817531b877ba646310296df42ef697308c2705/pyarrow-23.0.1-cp312-cp312-manylinux_2_28_aarch64.whl\", hash = \"sha256:86ff03fb9f1a320266e0de855dee4b17da6794c595d207f89bba40d16b5c78b9\", size = 44470940, upload-time = \"2026-02-16T10:10:10.704Z\" },\n-    { url = \"https://files.pythonhosted.org/packages/2c/a5/da83046273d990f256cb79796a190bbf7ec999269705ddc609403f8c6b06/pyarrow-23.0.1-cp312-cp312-manylinux_2_28_x86_64.whl\", hash = \"sha256:813d99f31275919c383aab17f0f455a04f5a429c261cc411b1e9a8f5e4aaaa05\", size = 47586063, upload-time = \"2026-02-16T10:10:17.95Z\" },\n-    { url = \"https://files.pythonhosted.org/packages/5b/3c/b7d2ebcff47a514f47f9da1e74b7949138c58cfeb108cdd4ee62f43f0cf3/pyarrow-23.0.1-cp312-cp312-musllinux_1_2_aarch64.whl\", hash = \"sha256:bf5842f960cddd2ef757d486041d57c96483efc295a8c4a0e20e704cbbf39c67\", size = 48173045, upload-time = \"2026-02-16T10:10:25.363Z\" },\n-    { url = \"https://files.pythonhosted.org/packages/43/b2/b40961262213beaba6acfc88698eb773dfce32ecdf34d19291db94c2bd73/pyarrow-23.0.1-cp312-cp312-musllinux_1_2_x86_64.whl\", hash = \"sha256:564baf97c858ecc03ec01a41062e8f4698abc3e6e2acd79c01c2e97880a19730\", size = 50621741, upload-time = \"2026-02-16T10:10:33.477Z\" },\n-    { url = \"https://files.pythonhosted.org/packages/f6/70/1fdda42d65b28b078e93d75d371b2185a61da89dda4def8ba6ba41ebdeb4/pyarrow-23.0.1-cp312-cp312-win_amd64.whl\", hash = \"sha256:07deae7783782ac7250989a7b2ecde9b3c343a643f82e8a4df03d93b633006f0\", size = 27620678, upload-time = \"2026-02-16T10:10:39.31Z\" },\n-]\n-\n-[[package]]\n-name = \"pyasn1\"\n-version = \"0.6.3\"\n-source = { registry = \"https://pypi.org/simple\" }\n-sdist = { url = \"https://files.pythonhosted.org/packages/5c/5f/6583902b6f79b399c9c40674ac384fd9cd77805f9e6205075f828ef11fb2/pyasn1-0.6.3.tar.gz\", hash = \"sha256:697a8ecd6d98891189184ca1fa05d1bb00e2f84b5977c481452050549c8a72cf\", size = 148685, upload-time = \"2026-03-17T01:06:53.382Z\" }\n-wheels = [\n-    { url = \"https://files.pythonhosted.org/packages/5d/a0/7d793dce3fa811fe047d6ae2431c672364b462850c6235ae306c0efd025f/pyasn1-0.6.3-py3-none-any.whl\", hash = \"sha256:a80184d120f0864a52a073acc6fc642847d0be408e7c7252f31390c0f4eadcde\", size = 83997, upload-time = \"2026-03-17T01:06:52.036Z\" },\n-]\n-\n-[[package]]\n-name = \"pyasn1-modules\"\n-version = \"0.4.2\"\n-source = { registry = \"https://pypi.org/simple\" }\n-dependencies = [\n-    { name = \"pyasn1\" },\n-]\n-sdist = { url = \"https://files.pythonhosted.org/packages/e9/e6/78ebbb10a8c8e4b61a59249394a4a594c1a7af95593dc933a349c8d00964/pyasn1_modules-0.4.2.tar.gz\", hash = \"sha256:677091de870a80aae844b1ca6134f54652fa2c8c5a52aa396440ac3106e941e6\", size = 307892, upload-time = \"2025-03-28T02:41:22.17Z\" }\n-wheels = [\n-    { url = \"https://files.pythonhosted.org/packages/47/8d/d529b5d697919ba8c11ad626e835d4039be708a35b0d22de83a269a6682c/pyasn1_modules-0.4.2-py3-none-any.whl\", hash = \"sha256:29253a9207ce32b64c3ac6600edc75368f98473906e8fd1043bd6b5b1de2c14a\", size = 181259, upload-time = \"2025-03-28T02:41:19.028Z\" },\n-]\n-\n [[package]]\n name = \"pycparser\"\n version = \"3.0\"\n@@ -2270,18 +1819,6 @@ wheels = [\n     { url = \"https://files.pythonhosted.org/packages/e5/7a/8dd906bd22e79e47397a61742927f6747fe93242ef86645ee9092e610244/pyjwt-2.12.1-py3-none-any.whl\", hash = \"sha256:28ca37c070cad8ba8cd9790cd940535d40274d22f80ab87f3ac6a713e6e8454c\", size = 29726, upload-time = \"2026-03-13T19:27:35.677Z\" },\n ]\n \n-[[package]]\n-name = \"pymsteams\"\n-version = \"0.2.5\"\n-source = { registry = \"https://pypi.org/simple\" }\n-dependencies = [\n-    { name = \"requests\" },\n-]\n-sdist = { url = \"https://files.pythonhosted.org/packages/d9/f5/8b9b9572d4f582e5a3a135110c07218cd43ad6d067a986576d0467bf6251/pymsteams-0.2.5.tar.gz\", hash = \"sha256:9f76ca3a3de17b49ce3c5c314ee0e88b8bd2be78fc66f693ade1b7cabf23af70\", size = 88943, upload-time = \"2025-01-07T23:59:10.763Z\" }\n-wheels = [\n-    { url = \"https://files.pythonhosted.org/packages/77/55/2f83baa2a9d1eada20f41dcced4d4fb7ba14d864b160be812786802e39c3/pymsteams-0.2.5-py3-none-any.whl\", hash = \"sha256:bda78f36c4a59baa10fa21928980349a841b03c78dc7d6020f230aea4aeab2b7\", size = 14684, upload-time = \"2025-01-07T23:59:08.351Z\" },\n-]\n-\n [[package]]\n name = \"pyright\"\n version = \"1.1.409\"\n@@ -2414,31 +1951,6 @@ wheels = [\n     { url = \"https://files.pythonhosted.org/packages/1a/08/67bd04656199bbb51dbed1439b7f27601dfb576fb864099c7ef0c3e55531/pyyaml-6.0.3-cp312-cp312-win_arm64.whl\", hash = \"sha256:64386e5e707d03a7e172c0701abfb7e10f0fb753ee1d773128192742712a98fd\", size = 140344, upload-time = \"2025-09-25T21:32:22.617Z\" },\n ]\n \n-[[package]]\n-name = \"ratelimit\"\n-version = \"2.2.1\"\n-source = { registry = \"https://pypi.org/simple\" }\n-sdist = { url = \"https://files.pythonhosted.org/packages/ab/38/ff60c8fc9e002d50d48822cc5095deb8ebbc5f91a6b8fdd9731c87a147c9/ratelimit-2.2.1.tar.gz\", hash = \"sha256:af8a9b64b821529aca09ebaf6d8d279100d766f19e90b5059ac6a718ca6dee42\", size = 5251, upload-time = \"2018-12-17T18:55:49.675Z\" }\n-\n-[[package]]\n-name = \"redshift-connector\"\n-version = \"2.1.13\"\n-source = { registry = \"https://pypi.org/simple\" }\n-dependencies = [\n-    { name = \"beautifulsoup4\" },\n-    { name = \"boto3\" },\n-    { name = \"botocore\" },\n-    { name = \"lxml\" },\n-    { name = \"packaging\" },\n-    { name = \"pytz\" },\n-    { name = \"requests\" },\n-    { name = \"scramp\" },\n-    { name = \"setuptools\" },\n-]\n-wheels = [\n-    { url = \"https://files.pythonhosted.org/packages/10/34/70b2a5e47c246955e06aae93071112c8ce5a2d58ea72160478e9a544ea52/redshift_connector-2.1.13-py3-none-any.whl\", hash = \"sha256:f9bffcd359d7205964355e571963daa99e81fc9fdcca5e360076dbaabac838e4\", size = 156887, upload-time = \"2026-03-31T00:49:00.757Z\" },\n-]\n-\n [[package]]\n name = \"referencing\"\n version = \"0.37.0\"\n@@ -2554,15 +2066,6 @@ wheels = [\n     { url = \"https://files.pythonhosted.org/packages/f3/d2/b91dc748126c1559042cfe41990deb92c4ee3e2b415f6b5234969ffaf0cc/rpds_py-0.30.0-cp312-cp312-win_arm64.whl\", hash = \"sha256:669b1805bd639dd2989b281be2cfd951c6121b65e729d9b843e9639ef1fd555e\", size = 230868, upload-time = \"2025-11-30T20:22:40.493Z\" },\n ]\n \n-[[package]]\n-name = \"ruamel-yaml\"\n-version = \"0.19.1\"\n-source = { registry = \"https://pypi.org/simple\" }\n-sdist = { url = \"https://files.pythonhosted.org/packages/c7/3b/ebda527b56beb90cb7652cb1c7e4f91f48649fbcd8d2eb2fb6e77cd3329b/ruamel_yaml-0.19.1.tar.gz\", hash = \"sha256:53eb66cd27849eff968ebf8f0bf61f46cdac2da1d1f3576dd4ccee9b25c31993\", size = 142709, upload-time = \"2026-01-02T16:50:31.84Z\" }\n-wheels = [\n-    { url = \"https://files.pythonhosted.org/packages/b8/0c/51f6841f1d84f404f92463fc2b1ba0da357ca1e3db6b7fbda26956c3b82a/ruamel_yaml-0.19.1-py3-none-any.whl\", hash = \"sha256:27592957fedf6e0b62f281e96effd28043345e0e66001f97683aa9a40c667c93\", size = 118102, upload-time = \"2026-01-02T16:50:29.201Z\" },\n-]\n-\n [[package]]\n name = \"ruff\"\n version = \"0.15.12\"\n@@ -2588,30 +2091,6 @@ wheels = [\n     { url = \"https://files.pythonhosted.org/packages/c0/98/6beb4b351e472e5f4c4613f7c35a5290b8be2497e183825310c4c3a3984b/ruff-0.15.12-py3-none-win_arm64.whl\", hash = \"sha256:a538f7a82d061cee7be55542aca1d86d1393d55d81d4fcc314370f4340930d4f\", size = 11120821, upload-time = \"2026-04-24T18:16:57.979Z\" },\n ]\n \n-[[package]]\n-name = \"s3transfer\"\n-version = \"0.16.1\"\n-source = { registry = \"https://pypi.org/simple\" }\n-dependencies = [\n-    { name = \"botocore\" },\n-]\n-sdist = { url = \"https://files.pythonhosted.org/packages/46/29/af14f4ef3c11a50435308660e2cc68761c9a7742475e0585cd4396b91777/s3transfer-0.16.1.tar.gz\", hash = \"sha256:8e424355754b9ccb32467bdc568edf55be82692ef2002d934b1311dbb3b9e524\", size = 154801, upload-time = \"2026-04-22T20:36:06.475Z\" }\n-wheels = [\n-    { url = \"https://files.pythonhosted.org/packages/03/19/90d7d4ed51932c022d53f1d02d564b62d10e272692a1f9b76425c1ad2a02/s3transfer-0.16.1-py3-none-any.whl\", hash = \"sha256:61bcd00ccb83b21a0fe7e91a553fff9729d46c83b4e0106e7c314a733891f7c2\", size = 86825, upload-time = \"2026-04-22T20:36:04.992Z\" },\n-]\n-\n-[[package]]\n-name = \"scramp\"\n-version = \"1.4.8\"\n-source = { registry = \"https://pypi.org/simple\" }\n-dependencies = [\n-    { name = \"asn1crypto\" },\n-]\n-sdist = { url = \"https://files.pythonhosted.org/packages/98/52/a866f1ac9ae9025ec7f9bea803bba9d54796f8a84236165a700831f61b27/scramp-1.4.8.tar.gz\", hash = \"sha256:bd018fabfe46343cceeb9f1c3e8d23f55770271e777e3accbfaee3ff0a316e71\", size = 16630, upload-time = \"2026-01-06T21:01:01.083Z\" }\n-wheels = [\n-    { url = \"https://files.pythonhosted.org/packages/90/07/a962d2477331abfdb2c6a8251b65c673dbb07ad707d1882d61562b8b9147/scramp-1.4.8-py3-none-any.whl\", hash = \"sha256:87c2f15976845a2872fe5490a06097f0d01813cceb53774ea168c911f2ad025c\", size = 13121, upload-time = \"2026-01-06T21:00:59.474Z\" },\n-]\n-\n [[package]]\n name = \"setproctitle\"\n version = \"1.3.7\"\n@@ -2630,15 +2109,6 @@ wheels = [\n     { url = \"https://files.pythonhosted.org/packages/e2/5b/a9fe517912cd6e28cf43a212b80cb679ff179a91b623138a99796d7d18a0/setproctitle-1.3.7-cp312-cp312-win_amd64.whl\", hash = \"sha256:9888ceb4faea3116cf02a920ff00bfbc8cc899743e4b4ac914b03625bdc3c300\", size = 13247, upload-time = \"2025-09-05T12:49:49.16Z\" },\n ]\n \n-[[package]]\n-name = \"setuptools\"\n-version = \"82.0.1\"\n-source = { registry = \"https://pypi.org/simple\" }\n-sdist = { url = \"https://files.pythonhosted.org/packages/4f/db/cfac1baf10650ab4d1c111714410d2fbb77ac5a616db26775db562c8fab2/setuptools-82.0.1.tar.gz\", hash = \"sha256:7d872682c5d01cfde07da7bccc7b65469d3dca203318515ada1de5eda35efbf9\", size = 1152316, upload-time = \"2026-03-09T12:47:17.221Z\" }\n-wheels = [\n-    { url = \"https://files.pythonhosted.org/packages/9d/76/f789f7a86709c6b087c5a2f52f911838cad707cc613162401badc665acfe/setuptools-82.0.1-py3-none-any.whl\", hash = \"sha256:a59e362652f08dcd477c78bb6e7bd9d80a7995bc73ce773050228a348ce2e5bb\", size = 1006223, upload-time = \"2026-03-09T12:47:15.026Z\" },\n-]\n-\n [[package]]\n name = \"shellingham\"\n version = \"1.5.4\"\n@@ -2657,15 +2127,6 @@ wheels = [\n     { url = \"https://files.pythonhosted.org/packages/b7/ce/149a00dd41f10bc29e5921b496af8b574d8413afcd5e30dfa0ed46c2cc5e/six-1.17.0-py2.py3-none-any.whl\", hash = \"sha256:4721f391ed90541fddacab5acf947aa0d3dc7d27b2e1e8eda2be8970586c3274\", size = 11050, upload-time = \"2024-12-04T17:35:26.475Z\" },\n ]\n \n-[[package]]\n-name = \"slack-sdk\"\n-version = \"3.41.0\"\n-source = { registry = \"https://pypi.org/simple\" }\n-sdist = { url = \"https://files.pythonhosted.org/packages/22/35/fc009118a13187dd9731657c60138e5a7c2dea88681a7f04dc406af5da7d/slack_sdk-3.41.0.tar.gz\", hash = \"sha256:eb61eb12a65bebeca9cb5d36b3f799e836ed2be21b456d15df2627cfe34076ca\", size = 250568, upload-time = \"2026-03-12T16:10:11.381Z\" }\n-wheels = [\n-    { url = \"https://files.pythonhosted.org/packages/a1/df/2e4be347ff98281b505cc0ccf141408cdd25eb5ca9f3830deb361b2472d3/slack_sdk-3.41.0-py2.py3-none-any.whl\", hash = \"sha256:bb18dcdfff1413ec448e759cf807ec3324090993d8ab9111c74081623b692a89\", size = 313885, upload-time = \"2026-03-12T16:10:09.811Z\" },\n-]\n-\n [[package]]\n name = \"sniffio\"\n version = \"1.3.1\"\n@@ -2688,15 +2149,6 @@ wheels = [\n     { url = \"https://files.pythonhosted.org/packages/78/10/1c76269cbf2d6e127f4415044d9ddb0295858230678bbf4bfba905593c82/snowplow_tracker-1.1.0-py3-none-any.whl\", hash = \"sha256:24ea32ddac9cca547421bf9ab162f5f33c00711c6ef118ad5f78093cee962224\", size = 44128, upload-time = \"2025-02-21T10:58:45.818Z\" },\n ]\n \n-[[package]]\n-name = \"soupsieve\"\n-version = \"2.8.3\"\n-source = { registry = \"https://pypi.org/simple\" }\n-sdist = { url = \"https://files.pythonhosted.org/packages/7b/ae/2d9c981590ed9999a0d91755b47fc74f74de286b0f5cee14c9269041e6c4/soupsieve-2.8.3.tar.gz\", hash = \"sha256:3267f1eeea4251fb42728b6dfb746edc9acaffc4a45b27e19450b676586e8349\", size = 118627, upload-time = \"2026-01-20T04:27:02.457Z\" }\n-wheels = [\n-    { url = \"https://files.pythonhosted.org/packages/46/2c/1462b1d0a634697ae9e55b3cecdcb64788e8b7d63f54d923fcd0bb140aed/soupsieve-2.8.3-py3-none-any.whl\", hash = \"sha256:ed64f2ba4eebeab06cc4962affce381647455978ffc1e36bb79a545b91f45a95\", size = 37016, upload-time = \"2026-01-20T04:27:01.012Z\" },\n-]\n-\n [[package]]\n name = \"sqlalchemy\"\n version = \"2.0.49\"\n",
          "timed_out": false
        },
        {
          "args": [
            "git",
            "ls-files",
            "--others",
            "--exclude-standard",
            "-z"
          ],
          "duration_seconds": 0.047,
          "exit_code": 0,
          "stderr": "",
          "stdout": "docs/reports/lakehouse-stage-l4.md\u0000scripts/ci/check_legacy_orphans.py\u0000tests/cdc_contracts/test_schema_evolution.py\u0000tests/cdc_contracts/test_target_connector_contract.py\u0000tests/lakehouse_platform/test_control_postgres_contract.py\u0000tests/lakehouse_platform/test_secret_bootstrap.py\u0000tests/lakehouse_platform/test_source_contract.py\u0000tests/mysql/test_schema_contract.py\u0000tests/observability/test_contract.py\u0000tests/stage_v/test_f0_parity_contracts.py\u0000",
          "timed_out": false
        },
        {
          "args": [
            "uv",
            "lock",
            "--check"
          ],
          "duration_seconds": 0.063,
          "exit_code": 0,
          "stderr": "Resolved 177 packages in 1ms\n",
          "stdout": "",
          "timed_out": false
        },
        {
          "args": [
            "uv",
            "run",
            "pytest",
            "tests/cdc_contracts",
            "tests/lakehouse_platform",
            "tests/mysql",
            "tests/dbt_clickhouse",
            "tests/serving",
            "tests/stage_v"
          ],
          "duration_seconds": 14.797,
          "exit_code": 0,
          "stderr": "",
          "stdout": "============================= test session starts =============================\nplatform win32 -- Python 3.12.13, pytest-9.0.3, pluggy-1.6.0\nrootdir: C:\\Users\\fyujv\\source\\repos\\olist-mds\nconfigfile: pyproject.toml\nplugins: anyio-4.13.0\ncollected 232 items\n\ntests\\cdc_contracts\\test_avro_helpers.py ..........                      [  4%]\ntests\\cdc_contracts\\test_connector_bootstrap.py ................         [ 11%]\ntests\\cdc_contracts\\test_entity_contracts.py ..............              [ 17%]\ntests\\cdc_contracts\\test_schema_evolution.py .....                       [ 19%]\ntests\\cdc_contracts\\test_target_connector_contract.py ............       [ 24%]\ntests\\cdc_contracts\\test_topics.py .......                               [ 27%]\ntests\\cdc_contracts\\test_writer_schemas.py ....                          [ 29%]\ntests\\lakehouse_platform\\test_control_postgres_contract.py ...           [ 30%]\ntests\\lakehouse_platform\\test_l1_runtime_contracts.py ......             [ 33%]\ntests\\lakehouse_platform\\test_local_lab_live_readiness.py ....           [ 34%]\ntests\\lakehouse_platform\\test_local_lab_profile_boundaries.py .....      [ 37%]\ntests\\lakehouse_platform\\test_normalization_api.py ...                   [ 38%]\ntests\\lakehouse_platform\\test_polaris_admin_minio_contract.py ..         [ 39%]\ntests\\lakehouse_platform\\test_polaris_contract.py .......                [ 42%]\ntests\\lakehouse_platform\\test_polaris_credentials_projection.py ...      [ 43%]\ntests\\lakehouse_platform\\test_secret_bootstrap.py s                      [ 43%]\ntests\\lakehouse_platform\\test_source_contract.py ..                      [ 44%]\ntests\\lakehouse_platform\\test_spark_config.py ....                       [ 46%]\ntests\\lakehouse_platform\\test_spark_image_contract.py .....              [ 48%]\ntests\\lakehouse_platform\\test_table_contracts.py .......                 [ 51%]\ntests\\mysql\\test_cli.py .......                                          [ 54%]\ntests\\mysql\\test_mysql_integration.py ss                                 [ 55%]\ntests\\mysql\\test_repository.py .................                         [ 62%]\ntests\\mysql\\test_schema_contract.py .                                    [ 63%]\ntests\\mysql\\test_seeding.py ......                                       [ 65%]\ntests\\mysql\\test_source_schema.py ............                           [ 71%]\ntests\\dbt_clickhouse\\test_dbt_parse.py .                                 [ 71%]\ntests\\dbt_clickhouse\\test_native_ddl_contract.py ........                [ 75%]\ntests\\dbt_clickhouse\\test_project_contract.py ......                     [ 77%]\ntests\\serving\\test_airflow_api.py .....                                  [ 79%]\ntests\\serving\\test_boundary.py ...........                               [ 84%]\ntests\\serving\\test_control.py ..                                         [ 85%]\ntests\\serving\\test_dbt_runner.py .                                       [ 85%]\ntests\\serving\\test_entities.py ...                                       [ 87%]\ntests\\stage_v\\test_f0_parity_contracts.py .....                          [ 89%]\ntests\\stage_v\\test_stage_v_harness.py .....................              [ 98%]\ntests\\stage_v\\test_stage_v_oracles.py ....                               [100%]\n\n============================== warnings summary ===============================\n.venv\\Lib\\site-packages\\airflow\\__init__.py:47\n  C:\\Users\\fyujv\\source\\repos\\olist-mds\\.venv\\Lib\\site-packages\\airflow\\__init__.py:47: RuntimeWarning: Airflow currently can be run on POSIX-compliant Operating Systems. For development, it is regularly tested on fairly modern Linux Distros and recent versions of macOS. On Windows you can run it via WSL2 (Windows Subsystem for Linux 2) or via Linux Containers. The work to add Windows support is tracked via https://github.com/apache/airflow/issues/10388, but it is not a high priority.\n    warnings.warn(\n\n.venv\\Lib\\site-packages\\_pytest\\cacheprovider.py:475\n  C:\\Users\\fyujv\\source\\repos\\olist-mds\\.venv\\Lib\\site-packages\\_pytest\\cacheprovider.py:475: PytestCacheWarning: cache could not write path C:\\Users\\fyujv\\source\\repos\\olist-mds\\.pytest_cache\\v\\cache\\nodeids: [Errno 13] Permission denied: 'C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.pytest_cache\\\\v\\\\cache\\\\nodeids'\n    config.cache.set(\"cache/nodeids\", sorted(self.cached_nodeids))\n\n-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html\n================= 229 passed, 3 skipped, 2 warnings in 12.97s =================\n",
          "timed_out": false
        },
        {
          "args": [
            "docker",
            "build",
            "--target",
            "scala-builder",
            "-f",
            "docker/spark/Dockerfile",
            "."
          ],
          "duration_seconds": 103.078,
          "exit_code": 0,
          "stderr": "#0 building with \"desktop-linux\" instance using docker driver\n\n#1 [internal] load build definition from Dockerfile\n#1 transferring dockerfile: 2.73kB 0.0s done\n#1 DONE 0.1s\n\n#2 resolve image config for docker-image://docker.io/docker/dockerfile:1.7\n#2 DONE 2.3s\n\n#3 docker-image://docker.io/docker/dockerfile:1.7@sha256:a57df69d0ea827fb7266491f2813635de6f17269be881f696fbfdf2d83dda33e\n#3 CACHED\n\n#4 [internal] load metadata for docker.io/library/alpine:3.22.1\n#4 DONE 0.0s\n\n#5 [internal] load metadata for docker.io/apache/spark:4.1.3-scala2.13-java17-python3-ubuntu\n#5 DONE 0.0s\n\n#6 [internal] load .dockerignore\n#6 transferring context: 987B done\n#6 DONE 0.0s\n\n#7 [sbt-downloader 1/5] FROM docker.io/library/alpine:3.22.1\n#7 DONE 0.0s\n\n#8 [scala-builder 1/6] FROM docker.io/apache/spark:4.1.3-scala2.13-java17-python3-ubuntu\n#8 DONE 0.0s\n\n#9 [internal] load build context\n#9 transferring context: 92.03kB 0.2s done\n#9 DONE 0.3s\n\n#10 [sbt-downloader 2/5] RUN apk add --no-cache ca-certificates wget\n#10 CACHED\n\n#11 [artifact-downloader 3/5] COPY docker/spark/jars.sha256 /tmp/jars.sha256\n#11 CACHED\n\n#12 [artifact-downloader 5/5] RUN chmod 0555 /usr/local/bin/download-jars     && /usr/local/bin/download-jars /tmp/jars.sha256 /opt/olist/jars\n#12 CACHED\n\n#13 [scala-builder 2/6] COPY --from=artifact-downloader /opt/olist/jars/ /opt/spark/jars/\n#13 CACHED\n\n#14 [artifact-downloader 4/5] COPY docker/spark/download-jars.sh /usr/local/bin/download-jars\n#14 CACHED\n\n#15 [sbt-downloader 3/5] COPY docker/spark/sbt-launch.sha256 /tmp/sbt-launch.sha256\n#15 CACHED\n\n#16 [sbt-downloader 4/5] COPY docker/spark/download-sbt-launch.sh /usr/local/bin/download-sbt-launch\n#16 CACHED\n\n#17 [sbt-downloader 5/5] RUN chmod 0555 /usr/local/bin/download-sbt-launch     && /usr/local/bin/download-sbt-launch /tmp/sbt-launch.sha256 /tmp/sbt-launcher\n#17 CACHED\n\n#18 [scala-builder 3/6] COPY --from=sbt-downloader /tmp/sbt-launcher/sbt-launch.jar /tmp/sbt-launch.jar\n#18 CACHED\n\n#19 [scala-builder 4/6] COPY streaming /tmp/streaming\n#19 DONE 0.7s\n\n#20 [scala-builder 5/6] WORKDIR /tmp/streaming/spark/scala\n#20 DONE 0.1s\n\n#21 [scala-builder 6/6] RUN java -jar /tmp/sbt-launch.jar scalafmtCheckAll scalafmtSbtCheck Test/compile test package\n#21 0.944 [info] [launcher] getting org.scala-sbt sbt 1.12.11  (this may take some time)...\n#21 11.74 [info] [launcher] getting Scala 2.12.21 (for sbt)...\n#21 12.66 [info] welcome to sbt 1.12.11 (Eclipse Adoptium Java 17.0.19)\n#21 15.50 [info] loading settings for project scala-build from plugins.sbt...\n#21 16.39 [info] loading project definition from /tmp/streaming/spark/scala/project\n#21 22.99 [info] loading settings for project scala from build.sbt...\n#21 23.15 [info] set current project to olist-spark-jobs (in build file:/tmp/streaming/spark/scala/)\n#21 26.77 [info] scalafmt: Checking 4 Scala sources (/tmp/streaming/spark/scala)...\n#21 26.77 [info] scalafmt: Checking 30 Scala sources (/tmp/streaming/spark/scala)...\n#21 30.09 [success] Total time: 7 s, completed Aug 4, 2026, 10:38:02 PM\n#21 30.21 [info] scalafmt: Checking 2 Scala sources (/tmp/streaming/spark/scala)...\n#21 30.29 [success] Total time: 0 s, completed Aug 4, 2026, 10:38:02 PM\n#21 86.54 [info] compiling 5 Scala sources to /tmp/streaming/spark/scala/target/scala-2.13/classes ...\n#21 92.03 [info] done compiling\n#21 92.27 [info] compiling 1 Scala source to /tmp/streaming/spark/scala/target/scala-2.13/test-classes ...\n#21 93.27 [info] done compiling\n#21 93.83 [success] Total time: 64 s (0:01:04.0), completed Aug 4, 2026, 10:39:06 PM\n#21 94.96 [info] BronzeSpec:\n#21 95.05 [info] - ConfluentFrame inspect correctly classifies framing error codes\n#21 95.11 [info] ContractLoaderSpec:\n#21 95.33 [info] - LakehouseSchemaContract checksum matches J1 expected SHA-256\n#21 95.53 [info] - ContractLoader loads manifest and all 8 entity contracts successfully\n#21 95.54 [info] SilverSpec:\n#21 95.58 [info] - ContractLoader loads contracts for Silver engine\n#21 95.59 [info] TransactionStateSpec:\n#21 95.60 [info] - BEGIN and END observations split across batches become COMPLETE\n#21 95.60 [info] - an unresolved BEGIN remains visible as OPEN\n#21 95.60 [info] - a later COMPLETE replaces a REJECTED observation\n#21 95.61 [info] - duplicate END observations are idempotent\n#21 95.61 [info] - effective transactions are ordered by Kafka offset\n#21 95.71 [info] Run completed in 1 second, 501 milliseconds.\n#21 95.71 [info] Total number of tests run: 9\n#21 95.71 [info] Suites: completed 4, aborted 0\n#21 95.71 [info] Tests: succeeded 9, failed 0, canceled 0, ignored 0, pending 0\n#21 95.71 [info] All tests passed.\n#21 95.72 [success] Total time: 2 s, completed Aug 4, 2026, 10:39:08 PM\n#21 95.80 [warn] multiple main classes detected: run 'show discoveredMainClasses' to see the list\n#21 95.91 [success] Total time: 0 s, completed Aug 4, 2026, 10:39:08 PM\n#21 DONE 96.5s\n\n#22 exporting to image\n#22 exporting layers\n#22 exporting layers 1.8s done\n#22 writing image sha256:3795bf51823a4b66c2e4c42bab43bb52bee3e24b0c6dcdc7d9e3f20dee6ec2f8 done\n#22 DONE 1.8s\n\nView build details: docker-desktop://dashboard/build/desktop-linux/desktop-linux/pn27n8nqcixp76uafv58jn8ft\n",
          "stdout": "",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 144.899,
      "gate": "00-preflight",
      "status": "PASS",
      "timestamp": "2026-08-04T22:39:10.773047+00:00"
    },
    "01-harness-ready": {
      "assertions": [
        {
          "detail": "C:\\Users\\fyujv\\source\\repos\\olist-mds\\tests\\stage_v\\fixtures\\insert.sql",
          "name": "fixture_insert.sql_exists",
          "status": "PASS"
        },
        {
          "detail": "C:\\Users\\fyujv\\source\\repos\\olist-mds\\tests\\stage_v\\fixtures\\update.sql",
          "name": "fixture_update.sql_exists",
          "status": "PASS"
        },
        {
          "detail": "C:\\Users\\fyujv\\source\\repos\\olist-mds\\tests\\stage_v\\fixtures\\delete.sql",
          "name": "fixture_delete.sql_exists",
          "status": "PASS"
        },
        {
          "detail": "C:\\Users\\fyujv\\source\\repos\\olist-mds\\tests\\stage_v\\fixtures\\add_nullable_column.sql",
          "name": "fixture_add_nullable_column.sql_exists",
          "status": "PASS"
        },
        {
          "detail": "C:\\Users\\fyujv\\source\\repos\\olist-mds\\tests\\stage_v\\fixtures\\emit_nullable_event.sql",
          "name": "fixture_emit_nullable_event.sql_exists",
          "status": "PASS"
        },
        {
          "detail": {
            "path": "C:\\Users\\fyujv\\source\\repos\\olist-mds\\tests\\stage_v\\oracles\\initial_counts.json",
            "phases": [
              "crud_delta",
              "initial_snapshot",
              "post_crud",
              "post_schema"
            ],
            "sha256": "727d50e8ef67705a1f23ddccb46dcb7e7cc970668f168949d053726e36c6f1f4"
          },
          "name": "oracle_file_exists",
          "status": "PASS"
        }
      ],
      "command": [],
      "command_results": [],
      "details": {},
      "duration_seconds": 0.0,
      "gate": "01-harness-ready",
      "status": "PASS",
      "timestamp": "2026-08-04T22:39:10.773047+00:00"
    },
    "02-clean-bootstrap": {
      "assertions": [
        {
          "detail": "{\"command\": \"reset\", \"scoped_to\": \"olist_stage_v\", \"status\": \"ready\"}",
          "name": "lab_reset",
          "status": "PASS"
        },
        {
          "detail": "{\"capture\": {\"capture_state\": \"captured\", \"contract_version\": 2}, \"command\": \"bootstrap\", \"readiness_level\": \"wave1_platform\", \"seed\": {\"archive\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\tests\\\\fixtures\\\\olist_small\\\\olist_small.zip\", \"exit_code\": 0, \"row_counts\": {\"customers\": 8, \"geolocation\": 6, \"order_items\": 16, \"order_payments\": 14, \"order_reviews\": 12, \"orders\": 12, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"run_id\": \"stage_l4_20260805_f0_restored_seed_cbba942ffa86\"}, \"status\": \"ready\", \"validation\": {\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 177 packages in 1ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}], \"status\": \"ready\"}}",
          "name": "lab_bootstrap_seed",
          "status": "PASS"
        }
      ],
      "command": [
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "reset",
          "--yes"
        ],
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "bootstrap",
          "--run-id",
          "stage_l4_20260805_f0_restored_seed_cbba942ffa86",
          "--random-seed",
          "20260801"
        ]
      ],
      "command_results": [
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "reset",
            "--yes"
          ],
          "duration_seconds": 0.562,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"reset\", \"scoped_to\": \"olist_stage_v\", \"status\": \"ready\"}\n",
          "timed_out": false
        },
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "bootstrap",
            "--run-id",
            "stage_l4_20260805_f0_restored_seed_cbba942ffa86",
            "--random-seed",
            "20260801"
          ],
          "duration_seconds": 296.078,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"capture\": {\"capture_state\": \"captured\", \"contract_version\": 2}, \"command\": \"bootstrap\", \"readiness_level\": \"wave1_platform\", \"seed\": {\"archive\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\tests\\\\fixtures\\\\olist_small\\\\olist_small.zip\", \"exit_code\": 0, \"row_counts\": {\"customers\": 8, \"geolocation\": 6, \"order_items\": 16, \"order_payments\": 14, \"order_reviews\": 12, \"orders\": 12, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"run_id\": \"stage_l4_20260805_f0_restored_seed_cbba942ffa86\"}, \"status\": \"ready\", \"validation\": {\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 177 packages in 1ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}], \"status\": \"ready\"}}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 296.637,
      "gate": "02-clean-bootstrap",
      "status": "PASS",
      "timestamp": "2026-08-04T22:44:07.411688+00:00"
    },
    "03-initial-snapshot": {
      "assertions": [
        {
          "detail": "{\"command\": \"start-streaming\", \"freshness_basis\": \"initial_start\", \"freshness_verified\": false, \"new_query_ids\": {\"bronze\": \"25a059e7-e20e-47bc-8956-3fa946633f9f\", \"silver\": \"1ec5b0e6-a4b8-4ac8-a65f-97d46e52264b,488ba534-eeb7-43a6-9a4c-b66aa1ac4d7c,4cda13ac-e050-4aeb-a959-518545c2fa9d,56244440-ffb8-41e8-8f6a-d20a8563d099,8f6cc820-634e-4cf2-a2b7-68dee065aa56,bedc3874-98b7-4ebf-b949-7fd547e9ace2,d741bdb0-7078-4a6f-a8a3-e1dbce0e7882,de8efbe6-2cb9-42e0-bbcb-f5461cf0826e,e9939bc0-a07a-4f8e-b8b3-49fd888d8c9e,e9caa021-28d3-4ceb-bf65-c55fb951c3cf\"}, \"old_query_ids\": {}, \"restart_barrier_at_utc\": null, \"status\": \"ready\", \"status_files\": {\"bronze\": {\"query_count\": 1, \"updated_at_utc\": \"2026-08-04T22:46:09.485650572Z\"}, \"silver\": {\"query_count\": 10, \"updated_at_utc\": \"2026-08-04T22:46:25.579309087Z\"}}}",
          "name": "start_streaming",
          "status": "PASS"
        },
        {
          "detail": "{\"airflow_started\": false, \"command\": \"start-serving-observer\", \"services\": [\"clickhouse\", \"clickhouse-init\"], \"status\": \"ready\"}",
          "name": "start_serving_observer",
          "status": "PASS"
        },
        {
          "detail": "{\"command\": \"wait-caught-up\", \"status\": \"ready\"}",
          "name": "initial_snapshot_caught_up",
          "status": "PASS"
        },
        {
          "detail": {
            "checks": {
              "canonical_manifest_deleted_parity": true,
              "canonical_manifest_physical_parity": true,
              "canonical_manifest_visible_parity": true,
              "duplicate_event_ids": true,
              "entity_changes": true,
              "entity_visible_current": true,
              "geolocation": true,
              "rejected": true,
              "schema_violations": true,
              "silver_progress": true,
              "total_applied_changes": true,
              "total_deleted_current": true,
              "total_physical_current": true,
              "total_visible_current": true
            },
            "observed": {
              "deleted_current": {
                "customers": 0,
                "order_items": 0,
                "order_payments": 0,
                "order_reviews": 0,
                "orders": 0,
                "product_category_translation": 0,
                "products": 0,
                "sellers": 0
              },
              "duplicate_event_id_groups": 0,
              "entity_changes": {
                "customers": 8,
                "order_items": 16,
                "order_payments": 14,
                "order_reviews": 12,
                "orders": 12,
                "product_category_translation": 5,
                "products": 8,
                "sellers": 4
              },
              "entity_visible_current": {
                "customers": 8,
                "order_items": 16,
                "order_payments": 14,
                "order_reviews": 12,
                "orders": 12,
                "product_category_translation": 5,
                "products": 8,
                "sellers": 4
              },
              "manifest_deleted_counts": {
                "customers": 0,
                "order_items": 0,
                "order_payments": 0,
                "order_reviews": 0,
                "orders": 0,
                "product_category_translation": 0,
                "products": 0,
                "sellers": 0
              },
              "manifest_physical_counts": {
                "customers": 8,
                "order_items": 16,
                "order_payments": 14,
                "order_reviews": 12,
                "orders": 12,
                "product_category_translation": 5,
                "products": 8,
                "sellers": 4
              },
              "manifest_visible_counts": {
                "customers": 8,
                "order_items": 16,
                "order_payments": 14,
                "order_reviews": 12,
                "orders": 12,
                "product_category_translation": 5,
                "products": 8,
                "sellers": 4
              },
              "manifests": {
                "customers": {
                  "manifest_sha256": "c1fef870f6eb0e1dd4ce2ce7af65f770eb29eca80847d74c5336af42b455df6c",
                  "row_count": 8
                },
                "order_items": {
                  "manifest_sha256": "4d2f3be1a355423419962d298176bf1d35a7aa694cfc601899923fa438ce4443",
                  "row_count": 16
                },
                "order_payments": {
                  "manifest_sha256": "be28da72fc666143459ef1968f05d1ef235d1b26513b442bbc7175f46ab9705b",
                  "row_count": 14
                },
                "order_reviews": {
                  "manifest_sha256": "3d9a9aae5ab8350b3fb47c0b06167fe33f208736b38fbfba05e9af034f3c566d",
                  "row_count": 12
                },
                "orders": {
                  "manifest_sha256": "3d4f839f09b98b862d423a6f3c584c9b0e1bc154135020261d43fbc7178bb0cb",
                  "row_count": 12
                },
                "product_category_translation": {
                  "manifest_sha256": "b756ba5dc8a525f9abcd22ed07f0d6b2075d14f0593d95271fc34b6ccb40e3e2",
                  "row_count": 5
                },
                "products": {
                  "manifest_sha256": "959a1a0429eb04ecd116dd0158499c43ac9061b7eee4b2d38731cfd8f5c4fcd2",
                  "row_count": 8
                },
                "sellers": {
                  "manifest_sha256": "4c7b24450f2c8669497272153d45c3a3db5213eda363f23f876212e8c7662d9e",
                  "row_count": 4
                }
              },
              "operation_counts": {
                "c": 0,
                "d": 0,
                "r": 79,
                "u": 0
              },
              "phase": "initial_snapshot",
              "physical_current": {
                "customers": 8,
                "order_items": 16,
                "order_payments": 14,
                "order_reviews": 12,
                "orders": 12,
                "product_category_translation": 5,
                "products": 8,
                "sellers": 4
              },
              "rejected": 0,
              "schema_violations": 0,
              "silver_progress": {
                "customers": {
                  "changes_snapshot_id": 6357949159994066740,
                  "entity": "customers",
                  "last_kafka_offset": 7,
                  "status": "COMMITTED"
                },
                "order_items": {
                  "changes_snapshot_id": 7148453174623489302,
                  "entity": "order_items",
                  "last_kafka_offset": 3,
                  "status": "COMMITTED"
                },
                "order_payments": {
                  "changes_snapshot_id": 1389368697410847812,
                  "entity": "order_payments",
                  "last_kafka_offset": 4,
                  "status": "COMMITTED"
                },
                "order_reviews": {
                  "changes_snapshot_id": 6832862774312988623,
                  "entity": "order_reviews",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "orders": {
                  "changes_snapshot_id": 3286243361490749543,
                  "entity": "orders",
                  "last_kafka_offset": 1,
                  "status": "COMMITTED"
                },
                "product_category_translation": {
                  "changes_snapshot_id": 2493780499513490015,
                  "entity": "product_category_translation",
                  "last_kafka_offset": 4,
                  "status": "COMMITTED"
                },
                "products": {
                  "changes_snapshot_id": 7672100197799865306,
                  "entity": "products",
                  "last_kafka_offset": 7,
                  "status": "COMMITTED"
                },
                "sellers": {
                  "changes_snapshot_id": 9125635543796638711,
                  "entity": "sellers",
                  "last_kafka_offset": 3,
                  "status": "COMMITTED"
                }
              },
              "source_counts": {
                "geolocation": 6
              },
              "total_applied_changes": 79,
              "total_deleted_current": 0,
              "total_physical_current": 79,
              "total_visible_current": 79
            },
            "phase": "initial_snapshot",
            "status": "VERIFIED"
          },
          "name": "initial_snapshot_exact_oracle",
          "status": "PASS"
        }
      ],
      "command": [
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "start-streaming",
          "--wait-ready",
          "--timeout",
          "600"
        ],
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "start-serving-observer"
        ],
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "wait-caught-up",
          "--timeout",
          "1200"
        ]
      ],
      "command_results": [
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "start-streaming",
            "--wait-ready",
            "--timeout",
            "600"
          ],
          "duration_seconds": 140.375,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"start-streaming\", \"freshness_basis\": \"initial_start\", \"freshness_verified\": false, \"new_query_ids\": {\"bronze\": \"25a059e7-e20e-47bc-8956-3fa946633f9f\", \"silver\": \"1ec5b0e6-a4b8-4ac8-a65f-97d46e52264b,488ba534-eeb7-43a6-9a4c-b66aa1ac4d7c,4cda13ac-e050-4aeb-a959-518545c2fa9d,56244440-ffb8-41e8-8f6a-d20a8563d099,8f6cc820-634e-4cf2-a2b7-68dee065aa56,bedc3874-98b7-4ebf-b949-7fd547e9ace2,d741bdb0-7078-4a6f-a8a3-e1dbce0e7882,de8efbe6-2cb9-42e0-bbcb-f5461cf0826e,e9939bc0-a07a-4f8e-b8b3-49fd888d8c9e,e9caa021-28d3-4ceb-bf65-c55fb951c3cf\"}, \"old_query_ids\": {}, \"restart_barrier_at_utc\": null, \"status\": \"ready\", \"status_files\": {\"bronze\": {\"query_count\": 1, \"updated_at_utc\": \"2026-08-04T22:46:09.485650572Z\"}, \"silver\": {\"query_count\": 10, \"updated_at_utc\": \"2026-08-04T22:46:25.579309087Z\"}}}\n",
          "timed_out": false
        },
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "start-serving-observer"
          ],
          "duration_seconds": 95.86,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"airflow_started\": false, \"command\": \"start-serving-observer\", \"services\": [\"clickhouse\", \"clickhouse-init\"], \"status\": \"ready\"}\n",
          "timed_out": false
        },
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "wait-caught-up",
            "--timeout",
            "1200"
          ],
          "duration_seconds": 26.703,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"wait-caught-up\", \"status\": \"ready\"}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 266.449,
      "gate": "03-initial-snapshot",
      "status": "PASS",
      "timestamp": "2026-08-04T22:48:33.863371+00:00"
    },
    "04-crud-and-restart": {
      "assertions": [
        {
          "detail": "{\"command\": \"stop-streaming\", \"old_query_ids\": {\"bronze\": \"25a059e7-e20e-47bc-8956-3fa946633f9f\", \"silver\": \"1ec5b0e6-a4b8-4ac8-a65f-97d46e52264b,488ba534-eeb7-43a6-9a4c-b66aa1ac4d7c,4cda13ac-e050-4aeb-a959-518545c2fa9d,56244440-ffb8-41e8-8f6a-d20a8563d099,8f6cc820-634e-4cf2-a2b7-68dee065aa56,bedc3874-98b7-4ebf-b949-7fd547e9ace2,d741bdb0-7078-4a6f-a8a3-e1dbce0e7882,de8efbe6-2cb9-42e0-bbcb-f5461cf0826e,e9939bc0-a07a-4f8e-b8b3-49fd888d8c9e,e9caa021-28d3-4ceb-bf65-c55fb951c3cf\"}, \"status\": \"ready\", \"status_files_removed\": true}",
          "name": "stop_spark_streaming",
          "status": "PASS"
        },
        {
          "detail": "Executed insert (8 statements), update (5 statements), delete (4 statements)",
          "name": "execute_crud_fixtures",
          "status": "PASS"
        },
        {
          "detail": "{\"command\": \"start-streaming\", \"freshness_basis\": \"status_updated_at_after_restart_barrier\", \"freshness_verified\": true, \"new_query_ids\": {\"bronze\": \"25a059e7-e20e-47bc-8956-3fa946633f9f\", \"silver\": \"1ec5b0e6-a4b8-4ac8-a65f-97d46e52264b,488ba534-eeb7-43a6-9a4c-b66aa1ac4d7c,4cda13ac-e050-4aeb-a959-518545c2fa9d,56244440-ffb8-41e8-8f6a-d20a8563d099,8f6cc820-634e-4cf2-a2b7-68dee065aa56,bedc3874-98b7-4ebf-b949-7fd547e9ace2,d741bdb0-7078-4a6f-a8a3-e1dbce0e7882,de8efbe6-2cb9-42e0-bbcb-f5461cf0826e,e9939bc0-a07a-4f8e-b8b3-49fd888d8c9e,e9caa021-28d3-4ceb-bf65-c55fb951c3cf\"}, \"old_query_ids\": {\"bronze\": \"25a059e7-e20e-47bc-8956-3fa946633f9f\", \"silver\": \"1ec5b0e6-a4b8-4ac8-a65f-97d46e52264b,488ba534-eeb7-43a6-9a4c-b66aa1ac4d7c,4cda13ac-e050-4aeb-a959-518545c2fa9d,56244440-ffb8-41e8-8f6a-d20a8563d099,8f6cc820-634e-4cf2-a2b7-68dee065aa56,bedc3874-98b7-4ebf-b949-7fd547e9ace2,d741bdb0-7078-4a6f-a8a3-e1dbce0e7882,de8efbe6-2cb9-42e0-bbcb-f5461cf0826e,e9939bc0-a07a-4f8e-b8b3-49fd888d8c9e,e9caa021-28d3-4ceb-bf65-c55fb951c3cf\"}, \"restart_barrier_at_utc\": \"2026-08-04T22:48:44.838906+00:00\", \"status\": \"ready\", \"status_files\": {\"bronze\": {\"query_count\": 1, \"updated_at_utc\": \"2026-08-04T22:50:54.347054040Z\"}, \"silver\": {\"query_count\": 10, \"updated_at_utc\": \"2026-08-04T22:51:01.881920616Z\"}}}",
          "name": "start_spark_streaming_recovery",
          "status": "PASS"
        }
      ],
      "command": [
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "stop-streaming"
        ],
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "start-streaming",
          "--wait-ready",
          "--timeout",
          "600"
        ]
      ],
      "command_results": [
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "stop-streaming"
          ],
          "duration_seconds": 11.0,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"stop-streaming\", \"old_query_ids\": {\"bronze\": \"25a059e7-e20e-47bc-8956-3fa946633f9f\", \"silver\": \"1ec5b0e6-a4b8-4ac8-a65f-97d46e52264b,488ba534-eeb7-43a6-9a4c-b66aa1ac4d7c,4cda13ac-e050-4aeb-a959-518545c2fa9d,56244440-ffb8-41e8-8f6a-d20a8563d099,8f6cc820-634e-4cf2-a2b7-68dee065aa56,bedc3874-98b7-4ebf-b949-7fd547e9ace2,d741bdb0-7078-4a6f-a8a3-e1dbce0e7882,de8efbe6-2cb9-42e0-bbcb-f5461cf0826e,e9939bc0-a07a-4f8e-b8b3-49fd888d8c9e,e9caa021-28d3-4ceb-bf65-c55fb951c3cf\"}, \"status\": \"ready\", \"status_files_removed\": true}\n",
          "timed_out": false
        },
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "start-streaming",
            "--wait-ready",
            "--timeout",
            "600"
          ],
          "duration_seconds": 139.266,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"start-streaming\", \"freshness_basis\": \"status_updated_at_after_restart_barrier\", \"freshness_verified\": true, \"new_query_ids\": {\"bronze\": \"25a059e7-e20e-47bc-8956-3fa946633f9f\", \"silver\": \"1ec5b0e6-a4b8-4ac8-a65f-97d46e52264b,488ba534-eeb7-43a6-9a4c-b66aa1ac4d7c,4cda13ac-e050-4aeb-a959-518545c2fa9d,56244440-ffb8-41e8-8f6a-d20a8563d099,8f6cc820-634e-4cf2-a2b7-68dee065aa56,bedc3874-98b7-4ebf-b949-7fd547e9ace2,d741bdb0-7078-4a6f-a8a3-e1dbce0e7882,de8efbe6-2cb9-42e0-bbcb-f5461cf0826e,e9939bc0-a07a-4f8e-b8b3-49fd888d8c9e,e9caa021-28d3-4ceb-bf65-c55fb951c3cf\"}, \"old_query_ids\": {\"bronze\": \"25a059e7-e20e-47bc-8956-3fa946633f9f\", \"silver\": \"1ec5b0e6-a4b8-4ac8-a65f-97d46e52264b,488ba534-eeb7-43a6-9a4c-b66aa1ac4d7c,4cda13ac-e050-4aeb-a959-518545c2fa9d,56244440-ffb8-41e8-8f6a-d20a8563d099,8f6cc820-634e-4cf2-a2b7-68dee065aa56,bedc3874-98b7-4ebf-b949-7fd547e9ace2,d741bdb0-7078-4a6f-a8a3-e1dbce0e7882,de8efbe6-2cb9-42e0-bbcb-f5461cf0826e,e9939bc0-a07a-4f8e-b8b3-49fd888d8c9e,e9caa021-28d3-4ceb-bf65-c55fb951c3cf\"}, \"restart_barrier_at_utc\": \"2026-08-04T22:48:44.838906+00:00\", \"status\": \"ready\", \"status_files\": {\"bronze\": {\"query_count\": 1, \"updated_at_utc\": \"2026-08-04T22:50:54.347054040Z\"}, \"silver\": {\"query_count\": 10, \"updated_at_utc\": \"2026-08-04T22:51:01.881920616Z\"}}}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 150.528,
      "gate": "04-crud-and-restart",
      "status": "PASS",
      "timestamp": "2026-08-04T22:51:04.393464+00:00"
    },
    "05-caught-up": {
      "assertions": [
        {
          "detail": "{\"command\": \"wait-caught-up\", \"status\": \"ready\"}",
          "name": "crud_caught_up",
          "status": "PASS"
        },
        {
          "detail": {
            "checks": {
              "canonical_manifest_deleted_parity": true,
              "canonical_manifest_physical_parity": true,
              "canonical_manifest_visible_parity": true,
              "crud_operation_counts": true,
              "duplicate_event_ids": true,
              "entity_changes": true,
              "entity_visible_current": true,
              "geolocation": true,
              "rejected": true,
              "schema_violations": true,
              "silver_progress": true,
              "total_applied_changes": true,
              "total_deleted_current": true,
              "total_physical_current": true,
              "total_visible_current": true
            },
            "observed": {
              "deleted_current": {
                "customers": 0,
                "order_items": 0,
                "order_payments": 0,
                "order_reviews": 1,
                "orders": 0,
                "product_category_translation": 0,
                "products": 0,
                "sellers": 0
              },
              "duplicate_event_id_groups": 0,
              "entity_changes": {
                "customers": 9,
                "order_items": 19,
                "order_payments": 16,
                "order_reviews": 14,
                "orders": 14,
                "product_category_translation": 5,
                "products": 8,
                "sellers": 4
              },
              "entity_visible_current": {
                "customers": 9,
                "order_items": 18,
                "order_payments": 16,
                "order_reviews": 12,
                "orders": 13,
                "product_category_translation": 5,
                "products": 8,
                "sellers": 4
              },
              "manifest_deleted_counts": {
                "customers": 0,
                "order_items": 0,
                "order_payments": 0,
                "order_reviews": 1,
                "orders": 0,
                "product_category_translation": 0,
                "products": 0,
                "sellers": 0
              },
              "manifest_physical_counts": {
                "customers": 9,
                "order_items": 18,
                "order_payments": 16,
                "order_reviews": 13,
                "orders": 13,
                "product_category_translation": 5,
                "products": 8,
                "sellers": 4
              },
              "manifest_visible_counts": {
                "customers": 9,
                "order_items": 18,
                "order_payments": 16,
                "order_reviews": 12,
                "orders": 13,
                "product_category_translation": 5,
                "products": 8,
                "sellers": 4
              },
              "manifests": {
                "customers": {
                  "manifest_sha256": "347e556d6a1f3933b1cb2f9d1f630f4335bc1653b480d9cf16979971a60eec4e",
                  "row_count": 9
                },
                "order_items": {
                  "manifest_sha256": "33fc0f9d03756a9935f7443627a081547b44f9a8e637d1a2b40e8f05c765f7fe",
                  "row_count": 18
                },
                "order_payments": {
                  "manifest_sha256": "a969573b38a2f1d5b615b8e6ea10652be48a686ec0dfbd17ce4c158dba0ee14e",
                  "row_count": 16
                },
                "order_reviews": {
                  "manifest_sha256": "253f2c14c91e90f002d8a3c5cd7ee4ea8e751f0fbfa5f0942c28ae31c1ab5493",
                  "row_count": 13
                },
                "orders": {
                  "manifest_sha256": "235cbdd08c9ff3348ee768abb343e856069db671688920b60eacc652170ed430",
                  "row_count": 13
                },
                "product_category_translation": {
                  "manifest_sha256": "b756ba5dc8a525f9abcd22ed07f0d6b2075d14f0593d95271fc34b6ccb40e3e2",
                  "row_count": 5
                },
                "products": {
                  "manifest_sha256": "959a1a0429eb04ecd116dd0158499c43ac9061b7eee4b2d38731cfd8f5c4fcd2",
                  "row_count": 8
                },
                "sellers": {
                  "manifest_sha256": "4c7b24450f2c8669497272153d45c3a3db5213eda363f23f876212e8c7662d9e",
                  "row_count": 4
                }
              },
              "operation_counts": {
                "c": 7,
                "d": 1,
                "r": 79,
                "u": 2
              },
              "phase": "post_crud",
              "physical_current": {
                "customers": 9,
                "order_items": 18,
                "order_payments": 16,
                "order_reviews": 13,
                "orders": 13,
                "product_category_translation": 5,
                "products": 8,
                "sellers": 4
              },
              "rejected": 0,
              "schema_violations": 0,
              "silver_progress": {
                "customers": {
                  "changes_snapshot_id": 1590334755227274135,
                  "entity": "customers",
                  "last_kafka_offset": 8,
                  "status": "COMMITTED"
                },
                "order_items": {
                  "changes_snapshot_id": 6104085289137992191,
                  "entity": "order_items",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "order_payments": {
                  "changes_snapshot_id": 4402592427034762001,
                  "entity": "order_payments",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "order_reviews": {
                  "changes_snapshot_id": 1998650664707823942,
                  "entity": "order_reviews",
                  "last_kafka_offset": 2,
                  "status": "COMMITTED"
                },
                "orders": {
                  "changes_snapshot_id": 8715658499880008100,
                  "entity": "orders",
                  "last_kafka_offset": 3,
                  "status": "COMMITTED"
                },
                "product_category_translation": {
                  "changes_snapshot_id": 2493780499513490015,
                  "entity": "product_category_translation",
                  "last_kafka_offset": 4,
                  "status": "COMMITTED"
                },
                "products": {
                  "changes_snapshot_id": 7672100197799865306,
                  "entity": "products",
                  "last_kafka_offset": 7,
                  "status": "COMMITTED"
                },
                "sellers": {
                  "changes_snapshot_id": 9125635543796638711,
                  "entity": "sellers",
                  "last_kafka_offset": 3,
                  "status": "COMMITTED"
                }
              },
              "source_counts": {},
              "total_applied_changes": 89,
              "total_deleted_current": 1,
              "total_physical_current": 86,
              "total_visible_current": 85
            },
            "phase": "post_crud",
            "status": "VERIFIED"
          },
          "name": "post_crud_exact_oracle",
          "status": "PASS"
        },
        {
          "detail": {
            "command": "start-streaming",
            "freshness_basis": "status_updated_at_after_restart_barrier",
            "freshness_verified": true,
            "new_query_ids": {
              "bronze": "25a059e7-e20e-47bc-8956-3fa946633f9f",
              "silver": "1ec5b0e6-a4b8-4ac8-a65f-97d46e52264b,488ba534-eeb7-43a6-9a4c-b66aa1ac4d7c,4cda13ac-e050-4aeb-a959-518545c2fa9d,56244440-ffb8-41e8-8f6a-d20a8563d099,8f6cc820-634e-4cf2-a2b7-68dee065aa56,bedc3874-98b7-4ebf-b949-7fd547e9ace2,d741bdb0-7078-4a6f-a8a3-e1dbce0e7882,de8efbe6-2cb9-42e0-bbcb-f5461cf0826e,e9939bc0-a07a-4f8e-b8b3-49fd888d8c9e,e9caa021-28d3-4ceb-bf65-c55fb951c3cf"
            },
            "old_query_ids": {
              "bronze": "25a059e7-e20e-47bc-8956-3fa946633f9f",
              "silver": "1ec5b0e6-a4b8-4ac8-a65f-97d46e52264b,488ba534-eeb7-43a6-9a4c-b66aa1ac4d7c,4cda13ac-e050-4aeb-a959-518545c2fa9d,56244440-ffb8-41e8-8f6a-d20a8563d099,8f6cc820-634e-4cf2-a2b7-68dee065aa56,bedc3874-98b7-4ebf-b949-7fd547e9ace2,d741bdb0-7078-4a6f-a8a3-e1dbce0e7882,de8efbe6-2cb9-42e0-bbcb-f5461cf0826e,e9939bc0-a07a-4f8e-b8b3-49fd888d8c9e,e9caa021-28d3-4ceb-bf65-c55fb951c3cf"
            },
            "restart_barrier_at_utc": "2026-08-04T22:48:44.838906+00:00",
            "status": "ready",
            "status_files": {
              "bronze": {
                "query_count": 1,
                "updated_at_utc": "2026-08-04T22:50:54.347054040Z"
              },
              "silver": {
                "query_count": 10,
                "updated_at_utc": "2026-08-04T22:51:01.881920616Z"
              }
            }
          },
          "name": "restart_freshness",
          "status": "PASS"
        }
      ],
      "command": [
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "wait-caught-up",
          "--timeout",
          "1200"
        ]
      ],
      "command_results": [
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "wait-caught-up",
            "--timeout",
            "1200"
          ],
          "duration_seconds": 96.906,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"wait-caught-up\", \"status\": \"ready\"}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 99.843,
      "gate": "05-caught-up",
      "status": "PASS",
      "timestamp": "2026-08-04T22:52:44.239330+00:00"
    },
    "06-serving-sync": {
      "assertions": [
        {
          "detail": "{\"command\": \"start-serving\", \"profiles\": [\"platform\", \"serving\"], \"required_services\": [\"clickhouse\", \"airflow\"], \"status\": \"ready\"}",
          "name": "start_serving",
          "status": "PASS"
        },
        {
          "detail": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_l4_20260805_f0_restored_crud_publish_cbba942ffa86\", \"dbt_result\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 1, \\\"sync_run_id\\\": \\\"sync-00000000000000000001\\\"}\"], \"exception\": null, \"results\": [{\"execution_time\": 0.28551650047302246, \"node\": \"stg_customers_current\", \"status\": \"success\"}, {\"execution_time\": 0.23459386825561523, \"node\": \"stg_customers_events\", \"status\": \"success\"}, {\"execution_time\": 0.09164547920227051, \"node\": \"stg_order_items_current\", \"status\": \"success\"}, {\"execution_time\": 0.0914454460144043, \"node\": \"stg_order_payments_current\", \"status\": \"success\"}, {\"execution_time\": 0.0767526626586914, \"node\": \"stg_orders_current\", \"status\": \"success\"}, {\"execution_time\": 0.08890676498413086, \"node\": \"stg_product_category_translation_events\", \"status\": \"success\"}, {\"execution_time\": 0.10743331909179688, \"node\": \"stg_products_events\", \"status\": \"success\"}, {\"execution_time\": 0.11120939254760742, \"node\": \"stg_sellers_current\", \"status\": \"success\"}, {\"execution_time\": 0.7228751182556152, \"node\": \"customer_scd2_collapses_identical_update_and_closes_on_delete\", \"status\": \"pass\"}, {\"execution_time\": 0.5220811367034912, \"node\": \"dim_customer_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.4344956874847412, \"node\": \"zero_gross_order_has_null_payment_allocation\", \"status\": \"pass\"}, {\"execution_time\": 0.8066186904907227, \"node\": \"payment_allocation_is_proportional_at_item_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.19350957870483398, \"node\": \"dim_date\", \"status\": \"success\"}, {\"execution_time\": 0.1250150203704834, \"node\": \"dim_order_status\", \"status\": \"success\"}, {\"execution_time\": 0.7755992412567139, \"node\": \"product_translation_does_not_resurrect_an_old_category\", \"status\": \"pass\"}, {\"execution_time\": 0.229705810546875, \"node\": \"dim_product_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.14237070083618164, \"node\": \"dim_seller\", \"status\": \"success\"}, {\"execution_time\": 0.1107935905456543, \"node\": \"assert_customer_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.058177947998046875, \"node\": \"candidate_not_null_dim_customer_scd2_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05281829833984375, \"node\": \"candidate_not_null_dim_customer_scd2_customer_unique_id\", \"status\": \"pass\"}, {\"execution_time\": 0.05875563621520996, \"node\": \"candidate_not_null_dim_customer_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.06799173355102539, \"node\": \"unique_combination_of_columns_dim_customer_scd2_sync_run_seq__customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.10114479064941406, \"node\": \"assert_payment_allocations_balance\", \"status\": \"pass\"}, {\"execution_time\": 0.06736516952514648, \"node\": \"candidate_not_null_dim_date_date_day\", \"status\": \"pass\"}, {\"execution_time\": 0.07120966911315918, \"node\": \"candidate_not_null_dim_date_date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.049056053161621094, \"node\": \"candidate_not_null_dim_date_sync_run_seq\", \"status\": \"pass\"}, {\"execution_time\": 0.06695294380187988, \"node\": \"unique_combination_of_columns_dim_date_sync_run_seq__date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05046963691711426, \"node\": \"candidate_not_null_dim_order_status_order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.055203914642333984, \"node\": \"candidate_not_null_dim_order_status_order_status_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05322861671447754, \"node\": \"unique_combination_of_columns_dim_order_status_sync_run_seq__order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.08980894088745117, \"node\": \"assert_product_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.07047033309936523, \"node\": \"candidate_not_null_dim_product_scd2_product_id\", \"status\": \"pass\"}, {\"execution_time\": 0.15107297897338867, \"node\": \"candidate_not_null_dim_product_scd2_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.07464456558227539, \"node\": \"candidate_not_null_dim_product_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.07457947731018066, \"node\": \"unique_combination_of_columns_dim_product_scd2_sync_run_seq__product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.051256418228149414, \"node\": \"candidate_not_null_dim_seller_seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.06155514717102051, \"node\": \"candidate_not_null_dim_seller_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.0530095100402832, \"node\": \"unique_combination_of_columns_dim_seller_sync_run_seq__seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.7950906753540039, \"node\": \"fact_order_items\", \"status\": \"success\"}, {\"execution_time\": 0.2387866973876953, \"node\": \"assert_fact_order_items_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.06770586967468262, \"node\": \"candidate_not_null_fact_order_items_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.06282544136047363, \"node\": \"candidate_not_null_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.052703142166137695, \"node\": \"candidate_not_null_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.06620168685913086, \"node\": \"candidate_not_null_fact_order_items_order_item_key\", \"status\": \"pass\"}, {\"execution_time\": 0.054347991943359375, \"node\": \"candidate_not_null_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.05778980255126953, \"node\": \"candidate_not_null_fact_order_items_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04939413070678711, \"node\": \"candidate_not_null_fact_order_items_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04846787452697754, \"node\": \"candidate_relationships_fact_order_items_customer_key__customer_key__ref_dim_customer_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.05672192573547363, \"node\": \"candidate_relationships_fact_order_items_product_key__product_key__ref_dim_product_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.07136154174804688, \"node\": \"candidate_relationships_fact_order_items_seller_key__seller_key__ref_dim_seller_\", \"status\": \"pass\"}, {\"execution_time\": 0.05767226219177246, \"node\": \"non_negative_fact_order_items_allocated_payment_value\", \"status\": \"pass\"}, {\"execution_time\": 0.04929804801940918, \"node\": \"non_negative_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.04581093788146973, \"node\": \"non_negative_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.05122780799865723, \"node\": \"non_negative_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.049762725830078125, \"node\": \"unique_combination_of_columns_fact_order_items_sync_run_seq__order_id__order_item_id\", \"status\": \"pass\"}, {\"execution_time\": 0.19202423095703125, \"node\": \"mart_daily_revenue\", \"status\": \"success\"}, {\"execution_time\": 0.15273523330688477, \"node\": \"mart_monthly_arpu\", \"status\": \"success\"}, {\"execution_time\": 0.06784319877624512, \"node\": \"assert_daily_revenue_components\", \"status\": \"pass\"}, {\"execution_time\": 0.07770442962646484, \"node\": \"candidate_not_null_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.09391021728515625, \"node\": \"candidate_not_null_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.06119537353515625, \"node\": \"candidate_not_null_mart_daily_revenue_order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.06480169296264648, \"node\": \"candidate_not_null_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.06537485122680664, \"node\": \"non_negative_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.05692028999328613, \"node\": \"non_negative_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.06562328338623047, \"node\": \"non_negative_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.06049513816833496, \"node\": \"unique_combination_of_columns_mart_daily_revenue_sync_run_seq__order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.07088708877563477, \"node\": \"assert_monthly_arpu_formulas\", \"status\": \"pass\"}, {\"execution_time\": 0.06801652908325195, \"node\": \"candidate_not_null_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.0953683853149414, \"node\": \"candidate_not_null_mart_monthly_arpu_order_month\", \"status\": \"pass\"}, {\"execution_time\": 0.09770750999450684, \"node\": \"candidate_not_null_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.06728339195251465, \"node\": \"candidate_not_null_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.06760382652282715, \"node\": \"non_negative_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.09058475494384766, \"node\": \"non_negative_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.08213686943054199, \"node\": \"non_negative_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.08391809463500977, \"node\": \"unique_combination_of_columns_mart_monthly_arpu_sync_run_seq__order_month\", \"status\": \"pass\"}], \"selector\": \"serving_candidate\", \"status_counts\": {\"pass\": 59, \"success\": 16}, \"success\": true, \"vars\": {\"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1}}, \"expected_entity_counts\": {\"customers\": 9, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 89, \"iceberg_snapshot_ids\": {\"customers\": 1590334755227274135, \"order_items\": 6104085289137992191, \"order_payments\": 4402592427034762001, \"order_reviews\": 1998650664707823942, \"orders\": 8715658499880008100, \"product_category_translation\": 2493780499513490015, \"products\": 7672100197799865306, \"sellers\": 9125635543796638711}, \"is_noop\": false, \"materialized_entity_counts\": {\"customers\": 9, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"materialized_event_count\": 89, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1, \"sync_run_status\": \"SUCCEEDED\", \"target_offsets\": {\"olist_cdc.olist_oltp.customers:0\": 8, \"olist_cdc.olist_oltp.order_items:0\": 5, \"olist_cdc.olist_oltp.order_items:1\": 5, \"olist_cdc.olist_oltp.order_items:2\": 6, \"olist_cdc.olist_oltp.order_payments:0\": 5, \"olist_cdc.olist_oltp.order_payments:1\": 4, \"olist_cdc.olist_oltp.order_payments:2\": 4, \"olist_cdc.olist_oltp.order_reviews:0\": 5, \"olist_cdc.olist_oltp.order_reviews:1\": 4, \"olist_cdc.olist_oltp.order_reviews:2\": 2, \"olist_cdc.olist_oltp.orders:0\": 3, \"olist_cdc.olist_oltp.orders:1\": 4, \"olist_cdc.olist_oltp.orders:2\": 4, \"olist_cdc.olist_oltp.product_category_translation:0\": 4, \"olist_cdc.olist_oltp.products:0\": 7, \"olist_cdc.olist_oltp.sellers:0\": 3}, \"target_transaction_id\": \"file=binlog.000002,pos=17771\"}",
          "name": "sync_serving_crud",
          "status": "PASS"
        },
        {
          "detail": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_l4_20260805_f0_restored_crud_repeat_cbba942ffa86\", \"dbt_result\": null, \"expected_entity_counts\": {\"customers\": 0, \"order_items\": 0, \"order_payments\": 0, \"order_reviews\": 0, \"orders\": 0, \"product_category_translation\": 0, \"products\": 0, \"sellers\": 0}, \"expected_event_count\": 0, \"iceberg_snapshot_ids\": {\"customers\": 1590334755227274135, \"order_items\": 6104085289137992191, \"order_payments\": 4402592427034762001, \"order_reviews\": 1998650664707823942, \"orders\": 8715658499880008100, \"product_category_translation\": 2493780499513490015, \"products\": 7672100197799865306, \"sellers\": 9125635543796638711}, \"is_noop\": true, \"materialized_entity_counts\": {\"customers\": 0, \"order_items\": 0, \"order_payments\": 0, \"order_reviews\": 0, \"orders\": 0, \"product_category_translation\": 0, \"products\": 0, \"sellers\": 0}, \"materialized_event_count\": 0, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000002\", \"sync_run_seq\": 2, \"sync_run_status\": \"NOOP\", \"target_offsets\": {}, \"target_transaction_id\": \"file=binlog.000002,pos=17771\"}",
          "name": "sync_serving_crud_repeat_noop",
          "status": "PASS"
        }
      ],
      "command": [
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "start-serving",
          "--build",
          "--timeout",
          "1800"
        ],
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "sync-serving",
          "--run-id",
          "stage_l4_20260805_f0_restored_crud_publish_cbba942ffa86",
          "--timeout",
          "1800"
        ],
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "sync-serving",
          "--run-id",
          "stage_l4_20260805_f0_restored_crud_repeat_cbba942ffa86",
          "--timeout",
          "1800"
        ]
      ],
      "command_results": [
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "start-serving",
            "--build",
            "--timeout",
            "1800"
          ],
          "duration_seconds": 250.187,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"start-serving\", \"profiles\": [\"platform\", \"serving\"], \"required_services\": [\"clickhouse\", \"airflow\"], \"status\": \"ready\"}\n",
          "timed_out": false
        },
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "sync-serving",
            "--run-id",
            "stage_l4_20260805_f0_restored_crud_publish_cbba942ffa86",
            "--timeout",
            "1800"
          ],
          "duration_seconds": 48.984,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_l4_20260805_f0_restored_crud_publish_cbba942ffa86\", \"dbt_result\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 1, \\\"sync_run_id\\\": \\\"sync-00000000000000000001\\\"}\"], \"exception\": null, \"results\": [{\"execution_time\": 0.28551650047302246, \"node\": \"stg_customers_current\", \"status\": \"success\"}, {\"execution_time\": 0.23459386825561523, \"node\": \"stg_customers_events\", \"status\": \"success\"}, {\"execution_time\": 0.09164547920227051, \"node\": \"stg_order_items_current\", \"status\": \"success\"}, {\"execution_time\": 0.0914454460144043, \"node\": \"stg_order_payments_current\", \"status\": \"success\"}, {\"execution_time\": 0.0767526626586914, \"node\": \"stg_orders_current\", \"status\": \"success\"}, {\"execution_time\": 0.08890676498413086, \"node\": \"stg_product_category_translation_events\", \"status\": \"success\"}, {\"execution_time\": 0.10743331909179688, \"node\": \"stg_products_events\", \"status\": \"success\"}, {\"execution_time\": 0.11120939254760742, \"node\": \"stg_sellers_current\", \"status\": \"success\"}, {\"execution_time\": 0.7228751182556152, \"node\": \"customer_scd2_collapses_identical_update_and_closes_on_delete\", \"status\": \"pass\"}, {\"execution_time\": 0.5220811367034912, \"node\": \"dim_customer_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.4344956874847412, \"node\": \"zero_gross_order_has_null_payment_allocation\", \"status\": \"pass\"}, {\"execution_time\": 0.8066186904907227, \"node\": \"payment_allocation_is_proportional_at_item_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.19350957870483398, \"node\": \"dim_date\", \"status\": \"success\"}, {\"execution_time\": 0.1250150203704834, \"node\": \"dim_order_status\", \"status\": \"success\"}, {\"execution_time\": 0.7755992412567139, \"node\": \"product_translation_does_not_resurrect_an_old_category\", \"status\": \"pass\"}, {\"execution_time\": 0.229705810546875, \"node\": \"dim_product_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.14237070083618164, \"node\": \"dim_seller\", \"status\": \"success\"}, {\"execution_time\": 0.1107935905456543, \"node\": \"assert_customer_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.058177947998046875, \"node\": \"candidate_not_null_dim_customer_scd2_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05281829833984375, \"node\": \"candidate_not_null_dim_customer_scd2_customer_unique_id\", \"status\": \"pass\"}, {\"execution_time\": 0.05875563621520996, \"node\": \"candidate_not_null_dim_customer_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.06799173355102539, \"node\": \"unique_combination_of_columns_dim_customer_scd2_sync_run_seq__customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.10114479064941406, \"node\": \"assert_payment_allocations_balance\", \"status\": \"pass\"}, {\"execution_time\": 0.06736516952514648, \"node\": \"candidate_not_null_dim_date_date_day\", \"status\": \"pass\"}, {\"execution_time\": 0.07120966911315918, \"node\": \"candidate_not_null_dim_date_date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.049056053161621094, \"node\": \"candidate_not_null_dim_date_sync_run_seq\", \"status\": \"pass\"}, {\"execution_time\": 0.06695294380187988, \"node\": \"unique_combination_of_columns_dim_date_sync_run_seq__date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05046963691711426, \"node\": \"candidate_not_null_dim_order_status_order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.055203914642333984, \"node\": \"candidate_not_null_dim_order_status_order_status_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05322861671447754, \"node\": \"unique_combination_of_columns_dim_order_status_sync_run_seq__order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.08980894088745117, \"node\": \"assert_product_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.07047033309936523, \"node\": \"candidate_not_null_dim_product_scd2_product_id\", \"status\": \"pass\"}, {\"execution_time\": 0.15107297897338867, \"node\": \"candidate_not_null_dim_product_scd2_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.07464456558227539, \"node\": \"candidate_not_null_dim_product_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.07457947731018066, \"node\": \"unique_combination_of_columns_dim_product_scd2_sync_run_seq__product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.051256418228149414, \"node\": \"candidate_not_null_dim_seller_seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.06155514717102051, \"node\": \"candidate_not_null_dim_seller_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.0530095100402832, \"node\": \"unique_combination_of_columns_dim_seller_sync_run_seq__seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.7950906753540039, \"node\": \"fact_order_items\", \"status\": \"success\"}, {\"execution_time\": 0.2387866973876953, \"node\": \"assert_fact_order_items_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.06770586967468262, \"node\": \"candidate_not_null_fact_order_items_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.06282544136047363, \"node\": \"candidate_not_null_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.052703142166137695, \"node\": \"candidate_not_null_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.06620168685913086, \"node\": \"candidate_not_null_fact_order_items_order_item_key\", \"status\": \"pass\"}, {\"execution_time\": 0.054347991943359375, \"node\": \"candidate_not_null_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.05778980255126953, \"node\": \"candidate_not_null_fact_order_items_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04939413070678711, \"node\": \"candidate_not_null_fact_order_items_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04846787452697754, \"node\": \"candidate_relationships_fact_order_items_customer_key__customer_key__ref_dim_customer_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.05672192573547363, \"node\": \"candidate_relationships_fact_order_items_product_key__product_key__ref_dim_product_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.07136154174804688, \"node\": \"candidate_relationships_fact_order_items_seller_key__seller_key__ref_dim_seller_\", \"status\": \"pass\"}, {\"execution_time\": 0.05767226219177246, \"node\": \"non_negative_fact_order_items_allocated_payment_value\", \"status\": \"pass\"}, {\"execution_time\": 0.04929804801940918, \"node\": \"non_negative_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.04581093788146973, \"node\": \"non_negative_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.05122780799865723, \"node\": \"non_negative_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.049762725830078125, \"node\": \"unique_combination_of_columns_fact_order_items_sync_run_seq__order_id__order_item_id\", \"status\": \"pass\"}, {\"execution_time\": 0.19202423095703125, \"node\": \"mart_daily_revenue\", \"status\": \"success\"}, {\"execution_time\": 0.15273523330688477, \"node\": \"mart_monthly_arpu\", \"status\": \"success\"}, {\"execution_time\": 0.06784319877624512, \"node\": \"assert_daily_revenue_components\", \"status\": \"pass\"}, {\"execution_time\": 0.07770442962646484, \"node\": \"candidate_not_null_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.09391021728515625, \"node\": \"candidate_not_null_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.06119537353515625, \"node\": \"candidate_not_null_mart_daily_revenue_order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.06480169296264648, \"node\": \"candidate_not_null_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.06537485122680664, \"node\": \"non_negative_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.05692028999328613, \"node\": \"non_negative_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.06562328338623047, \"node\": \"non_negative_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.06049513816833496, \"node\": \"unique_combination_of_columns_mart_daily_revenue_sync_run_seq__order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.07088708877563477, \"node\": \"assert_monthly_arpu_formulas\", \"status\": \"pass\"}, {\"execution_time\": 0.06801652908325195, \"node\": \"candidate_not_null_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.0953683853149414, \"node\": \"candidate_not_null_mart_monthly_arpu_order_month\", \"status\": \"pass\"}, {\"execution_time\": 0.09770750999450684, \"node\": \"candidate_not_null_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.06728339195251465, \"node\": \"candidate_not_null_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.06760382652282715, \"node\": \"non_negative_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.09058475494384766, \"node\": \"non_negative_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.08213686943054199, \"node\": \"non_negative_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.08391809463500977, \"node\": \"unique_combination_of_columns_mart_monthly_arpu_sync_run_seq__order_month\", \"status\": \"pass\"}], \"selector\": \"serving_candidate\", \"status_counts\": {\"pass\": 59, \"success\": 16}, \"success\": true, \"vars\": {\"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1}}, \"expected_entity_counts\": {\"customers\": 9, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 89, \"iceberg_snapshot_ids\": {\"customers\": 1590334755227274135, \"order_items\": 6104085289137992191, \"order_payments\": 4402592427034762001, \"order_reviews\": 1998650664707823942, \"orders\": 8715658499880008100, \"product_category_translation\": 2493780499513490015, \"products\": 7672100197799865306, \"sellers\": 9125635543796638711}, \"is_noop\": false, \"materialized_entity_counts\": {\"customers\": 9, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"materialized_event_count\": 89, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1, \"sync_run_status\": \"SUCCEEDED\", \"target_offsets\": {\"olist_cdc.olist_oltp.customers:0\": 8, \"olist_cdc.olist_oltp.order_items:0\": 5, \"olist_cdc.olist_oltp.order_items:1\": 5, \"olist_cdc.olist_oltp.order_items:2\": 6, \"olist_cdc.olist_oltp.order_payments:0\": 5, \"olist_cdc.olist_oltp.order_payments:1\": 4, \"olist_cdc.olist_oltp.order_payments:2\": 4, \"olist_cdc.olist_oltp.order_reviews:0\": 5, \"olist_cdc.olist_oltp.order_reviews:1\": 4, \"olist_cdc.olist_oltp.order_reviews:2\": 2, \"olist_cdc.olist_oltp.orders:0\": 3, \"olist_cdc.olist_oltp.orders:1\": 4, \"olist_cdc.olist_oltp.orders:2\": 4, \"olist_cdc.olist_oltp.product_category_translation:0\": 4, \"olist_cdc.olist_oltp.products:0\": 7, \"olist_cdc.olist_oltp.sellers:0\": 3}, \"target_transaction_id\": \"file=binlog.000002,pos=17771\"}\n",
          "timed_out": false
        },
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "sync-serving",
            "--run-id",
            "stage_l4_20260805_f0_restored_crud_repeat_cbba942ffa86",
            "--timeout",
            "1800"
          ],
          "duration_seconds": 11.281,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_l4_20260805_f0_restored_crud_repeat_cbba942ffa86\", \"dbt_result\": null, \"expected_entity_counts\": {\"customers\": 0, \"order_items\": 0, \"order_payments\": 0, \"order_reviews\": 0, \"orders\": 0, \"product_category_translation\": 0, \"products\": 0, \"sellers\": 0}, \"expected_event_count\": 0, \"iceberg_snapshot_ids\": {\"customers\": 1590334755227274135, \"order_items\": 6104085289137992191, \"order_payments\": 4402592427034762001, \"order_reviews\": 1998650664707823942, \"orders\": 8715658499880008100, \"product_category_translation\": 2493780499513490015, \"products\": 7672100197799865306, \"sellers\": 9125635543796638711}, \"is_noop\": true, \"materialized_entity_counts\": {\"customers\": 0, \"order_items\": 0, \"order_payments\": 0, \"order_reviews\": 0, \"orders\": 0, \"product_category_translation\": 0, \"products\": 0, \"sellers\": 0}, \"materialized_event_count\": 0, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000002\", \"sync_run_seq\": 2, \"sync_run_status\": \"NOOP\", \"target_offsets\": {}, \"target_transaction_id\": \"file=binlog.000002,pos=17771\"}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 310.47,
      "gate": "06-serving-sync",
      "status": "PASS",
      "timestamp": "2026-08-04T22:57:54.718078+00:00"
    },
    "07-dbt-and-stable-views": {
      "assertions": [
        {
          "detail": "{\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 177 packages in 1ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"All checks passed!\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"73 files already formatted\", \"exit_code\": 0, \"status\": \"passed\"}], \"command\": \"validate\", \"status\": \"ready\"}",
          "name": "serving_static_validation",
          "status": "PASS"
        },
        {
          "detail": {
            "command": "validate-serving",
            "current_views": {
              "customers": 9,
              "order_items": 18,
              "order_payments": 16,
              "order_reviews": 12,
              "orders": 13,
              "product_category_translation": 5,
              "products": 8,
              "sellers": 4
            },
            "dbt": {
              "command": [
                "build",
                "--project-dir",
                "/opt/airflow/project/dbt/olist_clickhouse",
                "--profiles-dir",
                "/opt/airflow/project/dbt/olist_clickhouse",
                "--selector",
                "serving_candidate",
                "--vars",
                "{\"sync_run_seq\": 1, \"sync_run_id\": \"sync-00000000000000000001\"}"
              ],
              "result_count": 75,
              "status_counts": {
                "pass": 59,
                "success": 16
              }
            },
            "gold_views": {
              "dim_customer_scd2": {
                "candidate": 7,
                "stable": 7
              },
              "dim_date": {
                "candidate": 46,
                "stable": 46
              },
              "dim_order_status": {
                "candidate": 2,
                "stable": 2
              },
              "dim_product_scd2": {
                "candidate": 8,
                "stable": 8
              },
              "dim_seller": {
                "candidate": 4,
                "stable": 4
              },
              "fact_order_items": {
                "candidate": 18,
                "stable": 18
              },
              "mart_daily_revenue": {
                "candidate": 13,
                "stable": 13
              },
              "mart_monthly_arpu": {
                "candidate": 7,
                "stable": 7
              }
            },
            "static_validation": {
              "checks": [
                {
                  "command": "uv lock --check",
                  "diagnostic": "Resolved 177 packages in 1ms",
                  "exit_code": 0,
                  "status": "passed"
                },
                {
                  "command": "C:\\Users\\fyujv\\source\\repos\\olist-mds\\.venv\\Scripts\\python.exe -m streaming.schemas.generate_contracts",
                  "diagnostic": "Eight versioned entity contract chains are current",
                  "exit_code": 0,
                  "status": "passed"
                },
                {
                  "command": "C:\\Users\\fyujv\\source\\repos\\olist-mds\\.venv\\Scripts\\python.exe -m streaming.schemas.writer_schemas",
                  "diagnostic": "captured writer schema repository is valid: captured",
                  "exit_code": 0,
                  "status": "passed"
                },
                {
                  "command": "C:\\Users\\fyujv\\source\\repos\\olist-mds\\.venv\\Scripts\\python.exe -m streaming.schemas.contracts",
                  "diagnostic": "CDC entity contracts are valid: eight entities, writers=captured",
                  "exit_code": 0,
                  "status": "passed"
                },
                {
                  "command": "docker compose --profile",
                  "diagnostic": "",
                  "exit_code": 0,
                  "status": "passed"
                },
                {
                  "command": "git diff --check",
                  "diagnostic": "",
                  "exit_code": 0,
                  "status": "passed"
                },
                {
                  "command": "uv run ruff",
                  "diagnostic": "All checks passed!",
                  "exit_code": 0,
                  "status": "passed"
                },
                {
                  "command": "uv run ruff",
                  "diagnostic": "73 files already formatted",
                  "exit_code": 0,
                  "status": "passed"
                }
              ],
              "status": "ready"
            },
            "status": "ready",
            "sync_run_id": "sync-00000000000000000001",
            "sync_run_seq": 1
          },
          "name": "dbt_and_stable_views_validation",
          "status": "PASS"
        }
      ],
      "command": [
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "validate",
          "--scope",
          "serving"
        ],
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "validate-serving",
          "--sync-run-seq",
          "1",
          "--sync-run-id",
          "sync-00000000000000000001"
        ]
      ],
      "command_results": [
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "validate",
            "--scope",
            "serving"
          ],
          "duration_seconds": 2.047,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 177 packages in 1ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"All checks passed!\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"73 files already formatted\", \"exit_code\": 0, \"status\": \"passed\"}], \"command\": \"validate\", \"status\": \"ready\"}\n",
          "timed_out": false
        },
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "validate-serving",
            "--sync-run-seq",
            "1",
            "--sync-run-id",
            "sync-00000000000000000001"
          ],
          "duration_seconds": 3.344,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"validate-serving\", \"current_views\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"dbt\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 1, \\\"sync_run_id\\\": \\\"sync-00000000000000000001\\\"}\"], \"result_count\": 75, \"status_counts\": {\"pass\": 59, \"success\": 16}}, \"gold_views\": {\"dim_customer_scd2\": {\"candidate\": 7, \"stable\": 7}, \"dim_date\": {\"candidate\": 46, \"stable\": 46}, \"dim_order_status\": {\"candidate\": 2, \"stable\": 2}, \"dim_product_scd2\": {\"candidate\": 8, \"stable\": 8}, \"dim_seller\": {\"candidate\": 4, \"stable\": 4}, \"fact_order_items\": {\"candidate\": 18, \"stable\": 18}, \"mart_daily_revenue\": {\"candidate\": 13, \"stable\": 13}, \"mart_monthly_arpu\": {\"candidate\": 7, \"stable\": 7}}, \"static_validation\": {\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 177 packages in 1ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"All checks passed!\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"73 files already formatted\", \"exit_code\": 0, \"status\": \"passed\"}], \"status\": \"ready\"}, \"status\": \"ready\", \"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 5.388,
      "gate": "07-dbt-and-stable-views",
      "status": "PASS",
      "timestamp": "2026-08-04T22:58:00.111613+00:00"
    },
    "08-additive-schema": {
      "assertions": [
        {
          "detail": {
            "add_column": {
              "fixture": "add_nullable_column.sql",
              "path": "C:\\Users\\fyujv\\source\\repos\\olist-mds\\tests\\stage_v\\fixtures\\add_nullable_column.sql",
              "statements_count": 1,
              "status": "EXECUTED"
            },
            "emit_event": {
              "fixture": "emit_nullable_event.sql",
              "path": "C:\\Users\\fyujv\\source\\repos\\olist-mds\\tests\\stage_v\\fixtures\\emit_nullable_event.sql",
              "statements_count": 4,
              "status": "EXECUTED"
            }
          },
          "name": "execute_nullable_schema_fixtures",
          "status": "PASS"
        },
        {
          "detail": {
            "column": {
              "column_default": null,
              "column_name": "stage_v_optional_note",
              "is_nullable": "YES"
            },
            "source_row": {
              "customer_city": "sao paulo stage v",
              "customer_id": "wave2_customer_001",
              "optional_value": null
            },
            "status": "VERIFIED"
          },
          "name": "mysql_nullable_source_contract",
          "status": "PASS"
        },
        {
          "detail": "{\"command\": \"wait-caught-up\", \"status\": \"ready\"}",
          "name": "schema_evolution_caught_up",
          "status": "PASS"
        },
        {
          "detail": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_l4_20260805_f0_restored_schema_publish_cbba942ffa86\", \"dbt_result\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 3, \\\"sync_run_id\\\": \\\"sync-00000000000000000003\\\"}\"], \"exception\": null, \"results\": [{\"execution_time\": 0.18923354148864746, \"node\": \"stg_customers_current\", \"status\": \"success\"}, {\"execution_time\": 0.06692266464233398, \"node\": \"stg_customers_events\", \"status\": \"success\"}, {\"execution_time\": 0.07703447341918945, \"node\": \"stg_order_items_current\", \"status\": \"success\"}, {\"execution_time\": 0.07261848449707031, \"node\": \"stg_order_payments_current\", \"status\": \"success\"}, {\"execution_time\": 0.07366943359375, \"node\": \"stg_orders_current\", \"status\": \"success\"}, {\"execution_time\": 0.1144568920135498, \"node\": \"stg_product_category_translation_events\", \"status\": \"success\"}, {\"execution_time\": 0.0919194221496582, \"node\": \"stg_products_events\", \"status\": \"success\"}, {\"execution_time\": 0.07204008102416992, \"node\": \"stg_sellers_current\", \"status\": \"success\"}, {\"execution_time\": 0.4036226272583008, \"node\": \"customer_scd2_collapses_identical_update_and_closes_on_delete\", \"status\": \"pass\"}, {\"execution_time\": 0.39864063262939453, \"node\": \"dim_customer_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.35738277435302734, \"node\": \"zero_gross_order_has_null_payment_allocation\", \"status\": \"pass\"}, {\"execution_time\": 0.3075089454650879, \"node\": \"payment_allocation_is_proportional_at_item_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.473691463470459, \"node\": \"dim_date\", \"status\": \"success\"}, {\"execution_time\": 0.2477567195892334, \"node\": \"dim_order_status\", \"status\": \"success\"}, {\"execution_time\": 0.5458254814147949, \"node\": \"product_translation_does_not_resurrect_an_old_category\", \"status\": \"pass\"}, {\"execution_time\": 0.38053202629089355, \"node\": \"dim_product_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.22447848320007324, \"node\": \"dim_seller\", \"status\": \"success\"}, {\"execution_time\": 0.11423039436340332, \"node\": \"assert_customer_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.056618452072143555, \"node\": \"candidate_not_null_dim_customer_scd2_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.08435845375061035, \"node\": \"candidate_not_null_dim_customer_scd2_customer_unique_id\", \"status\": \"pass\"}, {\"execution_time\": 0.04756045341491699, \"node\": \"candidate_not_null_dim_customer_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.046881675720214844, \"node\": \"unique_combination_of_columns_dim_customer_scd2_sync_run_seq__customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.07678842544555664, \"node\": \"assert_payment_allocations_balance\", \"status\": \"pass\"}, {\"execution_time\": 0.0732264518737793, \"node\": \"candidate_not_null_dim_date_date_day\", \"status\": \"pass\"}, {\"execution_time\": 0.05823111534118652, \"node\": \"candidate_not_null_dim_date_date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05543637275695801, \"node\": \"candidate_not_null_dim_date_sync_run_seq\", \"status\": \"pass\"}, {\"execution_time\": 0.05640292167663574, \"node\": \"unique_combination_of_columns_dim_date_sync_run_seq__date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05327749252319336, \"node\": \"candidate_not_null_dim_order_status_order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.06299304962158203, \"node\": \"candidate_not_null_dim_order_status_order_status_key\", \"status\": \"pass\"}, {\"execution_time\": 0.14159440994262695, \"node\": \"unique_combination_of_columns_dim_order_status_sync_run_seq__order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.049057960510253906, \"node\": \"assert_product_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.04716134071350098, \"node\": \"candidate_not_null_dim_product_scd2_product_id\", \"status\": \"pass\"}, {\"execution_time\": 0.05328226089477539, \"node\": \"candidate_not_null_dim_product_scd2_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.0770115852355957, \"node\": \"candidate_not_null_dim_product_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.07761955261230469, \"node\": \"unique_combination_of_columns_dim_product_scd2_sync_run_seq__product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05180859565734863, \"node\": \"candidate_not_null_dim_seller_seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.04743242263793945, \"node\": \"candidate_not_null_dim_seller_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.050107479095458984, \"node\": \"unique_combination_of_columns_dim_seller_sync_run_seq__seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.43926525115966797, \"node\": \"fact_order_items\", \"status\": \"success\"}, {\"execution_time\": 0.0388188362121582, \"node\": \"assert_fact_order_items_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.04075765609741211, \"node\": \"candidate_not_null_fact_order_items_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.041478633880615234, \"node\": \"candidate_not_null_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.04004216194152832, \"node\": \"candidate_not_null_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.03718829154968262, \"node\": \"candidate_not_null_fact_order_items_order_item_key\", \"status\": \"pass\"}, {\"execution_time\": 0.06575703620910645, \"node\": \"candidate_not_null_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.05698442459106445, \"node\": \"candidate_not_null_fact_order_items_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04902815818786621, \"node\": \"candidate_not_null_fact_order_items_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05975699424743652, \"node\": \"candidate_relationships_fact_order_items_customer_key__customer_key__ref_dim_customer_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.058623552322387695, \"node\": \"candidate_relationships_fact_order_items_product_key__product_key__ref_dim_product_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.05007052421569824, \"node\": \"candidate_relationships_fact_order_items_seller_key__seller_key__ref_dim_seller_\", \"status\": \"pass\"}, {\"execution_time\": 0.0444028377532959, \"node\": \"non_negative_fact_order_items_allocated_payment_value\", \"status\": \"pass\"}, {\"execution_time\": 0.04632067680358887, \"node\": \"non_negative_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.04568648338317871, \"node\": \"non_negative_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.050699472427368164, \"node\": \"non_negative_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.06188154220581055, \"node\": \"unique_combination_of_columns_fact_order_items_sync_run_seq__order_id__order_item_id\", \"status\": \"pass\"}, {\"execution_time\": 0.23674297332763672, \"node\": \"mart_daily_revenue\", \"status\": \"success\"}, {\"execution_time\": 0.19597530364990234, \"node\": \"mart_monthly_arpu\", \"status\": \"success\"}, {\"execution_time\": 0.09894013404846191, \"node\": \"assert_daily_revenue_components\", \"status\": \"pass\"}, {\"execution_time\": 0.04483485221862793, \"node\": \"candidate_not_null_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04931807518005371, \"node\": \"candidate_not_null_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04435229301452637, \"node\": \"candidate_not_null_mart_daily_revenue_order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.04689526557922363, \"node\": \"candidate_not_null_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.03920626640319824, \"node\": \"non_negative_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04008817672729492, \"node\": \"non_negative_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04088306427001953, \"node\": \"non_negative_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.03925776481628418, \"node\": \"unique_combination_of_columns_mart_daily_revenue_sync_run_seq__order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.04035830497741699, \"node\": \"assert_monthly_arpu_formulas\", \"status\": \"pass\"}, {\"execution_time\": 0.04799318313598633, \"node\": \"candidate_not_null_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.04437088966369629, \"node\": \"candidate_not_null_mart_monthly_arpu_order_month\", \"status\": \"pass\"}, {\"execution_time\": 0.05274462699890137, \"node\": \"candidate_not_null_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.04369664192199707, \"node\": \"candidate_not_null_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04208683967590332, \"node\": \"non_negative_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.04451465606689453, \"node\": \"non_negative_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.0991511344909668, \"node\": \"non_negative_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.09580445289611816, \"node\": \"unique_combination_of_columns_mart_monthly_arpu_sync_run_seq__order_month\", \"status\": \"pass\"}], \"selector\": \"serving_candidate\", \"status_counts\": {\"pass\": 59, \"success\": 16}, \"success\": true, \"vars\": {\"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3}}, \"expected_entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 90, \"iceberg_snapshot_ids\": {\"customers\": 4667963551008397841, \"order_items\": 6104085289137992191, \"order_payments\": 4402592427034762001, \"order_reviews\": 1998650664707823942, \"orders\": 8715658499880008100, \"product_category_translation\": 2493780499513490015, \"products\": 7672100197799865306, \"sellers\": 9125635543796638711}, \"is_noop\": false, \"materialized_entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"materialized_event_count\": 90, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3, \"sync_run_status\": \"SUCCEEDED\", \"target_offsets\": {\"olist_cdc.olist_oltp.customers:0\": 9, \"olist_cdc.olist_oltp.order_items:0\": 5, \"olist_cdc.olist_oltp.order_items:1\": 5, \"olist_cdc.olist_oltp.order_items:2\": 6, \"olist_cdc.olist_oltp.order_payments:0\": 5, \"olist_cdc.olist_oltp.order_payments:1\": 4, \"olist_cdc.olist_oltp.order_payments:2\": 4, \"olist_cdc.olist_oltp.order_reviews:0\": 5, \"olist_cdc.olist_oltp.order_reviews:1\": 4, \"olist_cdc.olist_oltp.order_reviews:2\": 2, \"olist_cdc.olist_oltp.orders:0\": 3, \"olist_cdc.olist_oltp.orders:1\": 4, \"olist_cdc.olist_oltp.orders:2\": 4, \"olist_cdc.olist_oltp.product_category_translation:0\": 4, \"olist_cdc.olist_oltp.products:0\": 7, \"olist_cdc.olist_oltp.sellers:0\": 3}, \"target_transaction_id\": \"file=binlog.000002,pos=22417\"}",
          "name": "additive_schema_publish",
          "status": "PASS"
        },
        {
          "detail": {
            "audit": {
              "normalization_errors": 0,
              "schema_violations": 0
            },
            "bronze": {
              "event_id": "olist_cdc.olist_oltp.customers:0:9",
              "is_tombstone": false,
              "key_framing_valid": true,
              "key_schema_id": 7,
              "offset": 9,
              "partition": 0,
              "topic": "olist_cdc.olist_oltp.customers",
              "value_framing_valid": true,
              "value_schema_id": 37
            },
            "customer_id": "wave2_customer_001",
            "event_id": "olist_cdc.olist_oltp.customers:0:9",
            "serving": {
              "customer_city": "sao paulo stage v",
              "customer_id": "wave2_customer_001",
              "optional_value": null
            },
            "silver": {
              "apply_status": "APPLIED",
              "customer_city": "sao paulo stage v",
              "customer_id": "wave2_customer_001",
              "event_id": "olist_cdc.olist_oltp.customers:0:9",
              "is_deleted": false,
              "kafka_offset": 9,
              "kafka_partition": 0,
              "kafka_topic": "olist_cdc.olist_oltp.customers",
              "key_schema_id": 7,
              "optional_value": null,
              "transaction_id": "file=binlog.000002,pos=22417",
              "value_schema_id": 37
            },
            "status": "VERIFIED",
            "writer_schema": {
              "fingerprint_sha256": "241c102de5caac89194592a7d3ba02450529f73ad093f03e91495ca2ddab0891",
              "legacy_fields": [
                "customer_city",
                "customer_id",
                "customer_state",
                "customer_unique_id",
                "customer_zip_code_prefix"
              ],
              "nullable_field": "stage_v_optional_note",
              "schema_id": 37,
              "subject": "olist_cdc.olist_oltp.customers"
            }
          },
          "name": "nullable_avro_bronze_silver_serving_propagation",
          "status": "PASS"
        },
        {
          "detail": {
            "checks": {
              "canonical_manifest_deleted_parity": true,
              "canonical_manifest_physical_parity": true,
              "canonical_manifest_visible_parity": true,
              "duplicate_event_ids": true,
              "entity_changes": true,
              "entity_visible_current": true,
              "geolocation": true,
              "rejected": true,
              "schema_violations": true,
              "silver_progress": true,
              "total_applied_changes": true,
              "total_deleted_current": true,
              "total_physical_current": true,
              "total_visible_current": true
            },
            "observed": {
              "deleted_current": {
                "customers": 0,
                "order_items": 0,
                "order_payments": 0,
                "order_reviews": 1,
                "orders": 0,
                "product_category_translation": 0,
                "products": 0,
                "sellers": 0
              },
              "duplicate_event_id_groups": 0,
              "entity_changes": {
                "customers": 10,
                "order_items": 19,
                "order_payments": 16,
                "order_reviews": 14,
                "orders": 14,
                "product_category_translation": 5,
                "products": 8,
                "sellers": 4
              },
              "entity_visible_current": {
                "customers": 9,
                "order_items": 18,
                "order_payments": 16,
                "order_reviews": 12,
                "orders": 13,
                "product_category_translation": 5,
                "products": 8,
                "sellers": 4
              },
              "manifest_deleted_counts": {
                "customers": 0,
                "order_items": 0,
                "order_payments": 0,
                "order_reviews": 1,
                "orders": 0,
                "product_category_translation": 0,
                "products": 0,
                "sellers": 0
              },
              "manifest_physical_counts": {
                "customers": 9,
                "order_items": 18,
                "order_payments": 16,
                "order_reviews": 13,
                "orders": 13,
                "product_category_translation": 5,
                "products": 8,
                "sellers": 4
              },
              "manifest_visible_counts": {
                "customers": 9,
                "order_items": 18,
                "order_payments": 16,
                "order_reviews": 12,
                "orders": 13,
                "product_category_translation": 5,
                "products": 8,
                "sellers": 4
              },
              "manifests": {
                "customers": {
                  "manifest_sha256": "37a48ceec785df33d81180415487eec1e4e85bc45a35fbaf35dda6c65dc0cdd7",
                  "row_count": 9
                },
                "order_items": {
                  "manifest_sha256": "33fc0f9d03756a9935f7443627a081547b44f9a8e637d1a2b40e8f05c765f7fe",
                  "row_count": 18
                },
                "order_payments": {
                  "manifest_sha256": "a969573b38a2f1d5b615b8e6ea10652be48a686ec0dfbd17ce4c158dba0ee14e",
                  "row_count": 16
                },
                "order_reviews": {
                  "manifest_sha256": "253f2c14c91e90f002d8a3c5cd7ee4ea8e751f0fbfa5f0942c28ae31c1ab5493",
                  "row_count": 13
                },
                "orders": {
                  "manifest_sha256": "235cbdd08c9ff3348ee768abb343e856069db671688920b60eacc652170ed430",
                  "row_count": 13
                },
                "product_category_translation": {
                  "manifest_sha256": "b756ba5dc8a525f9abcd22ed07f0d6b2075d14f0593d95271fc34b6ccb40e3e2",
                  "row_count": 5
                },
                "products": {
                  "manifest_sha256": "959a1a0429eb04ecd116dd0158499c43ac9061b7eee4b2d38731cfd8f5c4fcd2",
                  "row_count": 8
                },
                "sellers": {
                  "manifest_sha256": "4c7b24450f2c8669497272153d45c3a3db5213eda363f23f876212e8c7662d9e",
                  "row_count": 4
                }
              },
              "operation_counts": {
                "c": 7,
                "d": 1,
                "r": 79,
                "u": 3
              },
              "phase": "post_schema",
              "physical_current": {
                "customers": 9,
                "order_items": 18,
                "order_payments": 16,
                "order_reviews": 13,
                "orders": 13,
                "product_category_translation": 5,
                "products": 8,
                "sellers": 4
              },
              "rejected": 0,
              "schema_violations": 0,
              "silver_progress": {
                "customers": {
                  "changes_snapshot_id": 4667963551008397841,
                  "entity": "customers",
                  "last_kafka_offset": 9,
                  "status": "COMMITTED"
                },
                "order_items": {
                  "changes_snapshot_id": 6104085289137992191,
                  "entity": "order_items",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "order_payments": {
                  "changes_snapshot_id": 4402592427034762001,
                  "entity": "order_payments",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "order_reviews": {
                  "changes_snapshot_id": 1998650664707823942,
                  "entity": "order_reviews",
                  "last_kafka_offset": 2,
                  "status": "COMMITTED"
                },
                "orders": {
                  "changes_snapshot_id": 8715658499880008100,
                  "entity": "orders",
                  "last_kafka_offset": 3,
                  "status": "COMMITTED"
                },
                "product_category_translation": {
                  "changes_snapshot_id": 2493780499513490015,
                  "entity": "product_category_translation",
                  "last_kafka_offset": 4,
                  "status": "COMMITTED"
                },
                "products": {
                  "changes_snapshot_id": 7672100197799865306,
                  "entity": "products",
                  "last_kafka_offset": 7,
                  "status": "COMMITTED"
                },
                "sellers": {
                  "changes_snapshot_id": 9125635543796638711,
                  "entity": "sellers",
                  "last_kafka_offset": 3,
                  "status": "COMMITTED"
                }
              },
              "source_counts": {},
              "total_applied_changes": 90,
              "total_deleted_current": 1,
              "total_physical_current": 86,
              "total_visible_current": 85
            },
            "phase": "post_schema",
            "status": "VERIFIED"
          },
          "name": "post_schema_exact_oracle",
          "status": "PASS"
        },
        {
          "detail": {
            "command": "validate-serving",
            "current_views": {
              "customers": 9,
              "order_items": 18,
              "order_payments": 16,
              "order_reviews": 12,
              "orders": 13,
              "product_category_translation": 5,
              "products": 8,
              "sellers": 4
            },
            "dbt": {
              "command": [
                "build",
                "--project-dir",
                "/opt/airflow/project/dbt/olist_clickhouse",
                "--profiles-dir",
                "/opt/airflow/project/dbt/olist_clickhouse",
                "--selector",
                "serving_candidate",
                "--vars",
                "{\"sync_run_seq\": 3, \"sync_run_id\": \"sync-00000000000000000003\"}"
              ],
              "result_count": 75,
              "status_counts": {
                "pass": 59,
                "success": 16
              }
            },
            "gold_views": {
              "dim_customer_scd2": {
                "candidate": 8,
                "stable": 8
              },
              "dim_date": {
                "candidate": 46,
                "stable": 46
              },
              "dim_order_status": {
                "candidate": 2,
                "stable": 2
              },
              "dim_product_scd2": {
                "candidate": 8,
                "stable": 8
              },
              "dim_seller": {
                "candidate": 4,
                "stable": 4
              },
              "fact_order_items": {
                "candidate": 18,
                "stable": 18
              },
              "mart_daily_revenue": {
                "candidate": 13,
                "stable": 13
              },
              "mart_monthly_arpu": {
                "candidate": 7,
                "stable": 7
              }
            },
            "static_validation": {
              "checks": [
                {
                  "command": "uv lock --check",
                  "diagnostic": "Resolved 177 packages in 1ms",
                  "exit_code": 0,
                  "status": "passed"
                },
                {
                  "command": "C:\\Users\\fyujv\\source\\repos\\olist-mds\\.venv\\Scripts\\python.exe -m streaming.schemas.generate_contracts",
                  "diagnostic": "Eight versioned entity contract chains are current",
                  "exit_code": 0,
                  "status": "passed"
                },
                {
                  "command": "C:\\Users\\fyujv\\source\\repos\\olist-mds\\.venv\\Scripts\\python.exe -m streaming.schemas.writer_schemas",
                  "diagnostic": "captured writer schema repository is valid: captured",
                  "exit_code": 0,
                  "status": "passed"
                },
                {
                  "command": "C:\\Users\\fyujv\\source\\repos\\olist-mds\\.venv\\Scripts\\python.exe -m streaming.schemas.contracts",
                  "diagnostic": "CDC entity contracts are valid: eight entities, writers=captured",
                  "exit_code": 0,
                  "status": "passed"
                },
                {
                  "command": "docker compose --profile",
                  "diagnostic": "",
                  "exit_code": 0,
                  "status": "passed"
                },
                {
                  "command": "git diff --check",
                  "diagnostic": "",
                  "exit_code": 0,
                  "status": "passed"
                },
                {
                  "command": "uv run ruff",
                  "diagnostic": "All checks passed!",
                  "exit_code": 0,
                  "status": "passed"
                },
                {
                  "command": "uv run ruff",
                  "diagnostic": "73 files already formatted",
                  "exit_code": 0,
                  "status": "passed"
                }
              ],
              "status": "ready"
            },
            "status": "ready",
            "sync_run_id": "sync-00000000000000000003",
            "sync_run_seq": 3
          },
          "name": "post_schema_candidate_dbt_and_stable_parity",
          "status": "PASS"
        }
      ],
      "command": [
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "wait-caught-up",
          "--timeout",
          "1200"
        ],
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "sync-serving",
          "--run-id",
          "stage_l4_20260805_f0_restored_schema_publish_cbba942ffa86",
          "--timeout",
          "1800"
        ],
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "validate-serving",
          "--sync-run-seq",
          "3",
          "--sync-run-id",
          "sync-00000000000000000003"
        ]
      ],
      "command_results": [
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "wait-caught-up",
            "--timeout",
            "1200"
          ],
          "duration_seconds": 36.344,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"wait-caught-up\", \"status\": \"ready\"}\n",
          "timed_out": false
        },
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "sync-serving",
            "--run-id",
            "stage_l4_20260805_f0_restored_schema_publish_cbba942ffa86",
            "--timeout",
            "1800"
          ],
          "duration_seconds": 26.266,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_l4_20260805_f0_restored_schema_publish_cbba942ffa86\", \"dbt_result\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 3, \\\"sync_run_id\\\": \\\"sync-00000000000000000003\\\"}\"], \"exception\": null, \"results\": [{\"execution_time\": 0.18923354148864746, \"node\": \"stg_customers_current\", \"status\": \"success\"}, {\"execution_time\": 0.06692266464233398, \"node\": \"stg_customers_events\", \"status\": \"success\"}, {\"execution_time\": 0.07703447341918945, \"node\": \"stg_order_items_current\", \"status\": \"success\"}, {\"execution_time\": 0.07261848449707031, \"node\": \"stg_order_payments_current\", \"status\": \"success\"}, {\"execution_time\": 0.07366943359375, \"node\": \"stg_orders_current\", \"status\": \"success\"}, {\"execution_time\": 0.1144568920135498, \"node\": \"stg_product_category_translation_events\", \"status\": \"success\"}, {\"execution_time\": 0.0919194221496582, \"node\": \"stg_products_events\", \"status\": \"success\"}, {\"execution_time\": 0.07204008102416992, \"node\": \"stg_sellers_current\", \"status\": \"success\"}, {\"execution_time\": 0.4036226272583008, \"node\": \"customer_scd2_collapses_identical_update_and_closes_on_delete\", \"status\": \"pass\"}, {\"execution_time\": 0.39864063262939453, \"node\": \"dim_customer_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.35738277435302734, \"node\": \"zero_gross_order_has_null_payment_allocation\", \"status\": \"pass\"}, {\"execution_time\": 0.3075089454650879, \"node\": \"payment_allocation_is_proportional_at_item_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.473691463470459, \"node\": \"dim_date\", \"status\": \"success\"}, {\"execution_time\": 0.2477567195892334, \"node\": \"dim_order_status\", \"status\": \"success\"}, {\"execution_time\": 0.5458254814147949, \"node\": \"product_translation_does_not_resurrect_an_old_category\", \"status\": \"pass\"}, {\"execution_time\": 0.38053202629089355, \"node\": \"dim_product_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.22447848320007324, \"node\": \"dim_seller\", \"status\": \"success\"}, {\"execution_time\": 0.11423039436340332, \"node\": \"assert_customer_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.056618452072143555, \"node\": \"candidate_not_null_dim_customer_scd2_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.08435845375061035, \"node\": \"candidate_not_null_dim_customer_scd2_customer_unique_id\", \"status\": \"pass\"}, {\"execution_time\": 0.04756045341491699, \"node\": \"candidate_not_null_dim_customer_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.046881675720214844, \"node\": \"unique_combination_of_columns_dim_customer_scd2_sync_run_seq__customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.07678842544555664, \"node\": \"assert_payment_allocations_balance\", \"status\": \"pass\"}, {\"execution_time\": 0.0732264518737793, \"node\": \"candidate_not_null_dim_date_date_day\", \"status\": \"pass\"}, {\"execution_time\": 0.05823111534118652, \"node\": \"candidate_not_null_dim_date_date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05543637275695801, \"node\": \"candidate_not_null_dim_date_sync_run_seq\", \"status\": \"pass\"}, {\"execution_time\": 0.05640292167663574, \"node\": \"unique_combination_of_columns_dim_date_sync_run_seq__date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05327749252319336, \"node\": \"candidate_not_null_dim_order_status_order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.06299304962158203, \"node\": \"candidate_not_null_dim_order_status_order_status_key\", \"status\": \"pass\"}, {\"execution_time\": 0.14159440994262695, \"node\": \"unique_combination_of_columns_dim_order_status_sync_run_seq__order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.049057960510253906, \"node\": \"assert_product_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.04716134071350098, \"node\": \"candidate_not_null_dim_product_scd2_product_id\", \"status\": \"pass\"}, {\"execution_time\": 0.05328226089477539, \"node\": \"candidate_not_null_dim_product_scd2_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.0770115852355957, \"node\": \"candidate_not_null_dim_product_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.07761955261230469, \"node\": \"unique_combination_of_columns_dim_product_scd2_sync_run_seq__product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05180859565734863, \"node\": \"candidate_not_null_dim_seller_seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.04743242263793945, \"node\": \"candidate_not_null_dim_seller_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.050107479095458984, \"node\": \"unique_combination_of_columns_dim_seller_sync_run_seq__seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.43926525115966797, \"node\": \"fact_order_items\", \"status\": \"success\"}, {\"execution_time\": 0.0388188362121582, \"node\": \"assert_fact_order_items_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.04075765609741211, \"node\": \"candidate_not_null_fact_order_items_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.041478633880615234, \"node\": \"candidate_not_null_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.04004216194152832, \"node\": \"candidate_not_null_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.03718829154968262, \"node\": \"candidate_not_null_fact_order_items_order_item_key\", \"status\": \"pass\"}, {\"execution_time\": 0.06575703620910645, \"node\": \"candidate_not_null_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.05698442459106445, \"node\": \"candidate_not_null_fact_order_items_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04902815818786621, \"node\": \"candidate_not_null_fact_order_items_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05975699424743652, \"node\": \"candidate_relationships_fact_order_items_customer_key__customer_key__ref_dim_customer_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.058623552322387695, \"node\": \"candidate_relationships_fact_order_items_product_key__product_key__ref_dim_product_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.05007052421569824, \"node\": \"candidate_relationships_fact_order_items_seller_key__seller_key__ref_dim_seller_\", \"status\": \"pass\"}, {\"execution_time\": 0.0444028377532959, \"node\": \"non_negative_fact_order_items_allocated_payment_value\", \"status\": \"pass\"}, {\"execution_time\": 0.04632067680358887, \"node\": \"non_negative_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.04568648338317871, \"node\": \"non_negative_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.050699472427368164, \"node\": \"non_negative_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.06188154220581055, \"node\": \"unique_combination_of_columns_fact_order_items_sync_run_seq__order_id__order_item_id\", \"status\": \"pass\"}, {\"execution_time\": 0.23674297332763672, \"node\": \"mart_daily_revenue\", \"status\": \"success\"}, {\"execution_time\": 0.19597530364990234, \"node\": \"mart_monthly_arpu\", \"status\": \"success\"}, {\"execution_time\": 0.09894013404846191, \"node\": \"assert_daily_revenue_components\", \"status\": \"pass\"}, {\"execution_time\": 0.04483485221862793, \"node\": \"candidate_not_null_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04931807518005371, \"node\": \"candidate_not_null_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04435229301452637, \"node\": \"candidate_not_null_mart_daily_revenue_order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.04689526557922363, \"node\": \"candidate_not_null_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.03920626640319824, \"node\": \"non_negative_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04008817672729492, \"node\": \"non_negative_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04088306427001953, \"node\": \"non_negative_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.03925776481628418, \"node\": \"unique_combination_of_columns_mart_daily_revenue_sync_run_seq__order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.04035830497741699, \"node\": \"assert_monthly_arpu_formulas\", \"status\": \"pass\"}, {\"execution_time\": 0.04799318313598633, \"node\": \"candidate_not_null_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.04437088966369629, \"node\": \"candidate_not_null_mart_monthly_arpu_order_month\", \"status\": \"pass\"}, {\"execution_time\": 0.05274462699890137, \"node\": \"candidate_not_null_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.04369664192199707, \"node\": \"candidate_not_null_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04208683967590332, \"node\": \"non_negative_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.04451465606689453, \"node\": \"non_negative_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.0991511344909668, \"node\": \"non_negative_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.09580445289611816, \"node\": \"unique_combination_of_columns_mart_monthly_arpu_sync_run_seq__order_month\", \"status\": \"pass\"}], \"selector\": \"serving_candidate\", \"status_counts\": {\"pass\": 59, \"success\": 16}, \"success\": true, \"vars\": {\"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3}}, \"expected_entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 90, \"iceberg_snapshot_ids\": {\"customers\": 4667963551008397841, \"order_items\": 6104085289137992191, \"order_payments\": 4402592427034762001, \"order_reviews\": 1998650664707823942, \"orders\": 8715658499880008100, \"product_category_translation\": 2493780499513490015, \"products\": 7672100197799865306, \"sellers\": 9125635543796638711}, \"is_noop\": false, \"materialized_entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"materialized_event_count\": 90, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3, \"sync_run_status\": \"SUCCEEDED\", \"target_offsets\": {\"olist_cdc.olist_oltp.customers:0\": 9, \"olist_cdc.olist_oltp.order_items:0\": 5, \"olist_cdc.olist_oltp.order_items:1\": 5, \"olist_cdc.olist_oltp.order_items:2\": 6, \"olist_cdc.olist_oltp.order_payments:0\": 5, \"olist_cdc.olist_oltp.order_payments:1\": 4, \"olist_cdc.olist_oltp.order_payments:2\": 4, \"olist_cdc.olist_oltp.order_reviews:0\": 5, \"olist_cdc.olist_oltp.order_reviews:1\": 4, \"olist_cdc.olist_oltp.order_reviews:2\": 2, \"olist_cdc.olist_oltp.orders:0\": 3, \"olist_cdc.olist_oltp.orders:1\": 4, \"olist_cdc.olist_oltp.orders:2\": 4, \"olist_cdc.olist_oltp.product_category_translation:0\": 4, \"olist_cdc.olist_oltp.products:0\": 7, \"olist_cdc.olist_oltp.sellers:0\": 3}, \"target_transaction_id\": \"file=binlog.000002,pos=22417\"}\n",
          "timed_out": false
        },
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "validate-serving",
            "--sync-run-seq",
            "3",
            "--sync-run-id",
            "sync-00000000000000000003"
          ],
          "duration_seconds": 2.625,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"validate-serving\", \"current_views\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"dbt\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 3, \\\"sync_run_id\\\": \\\"sync-00000000000000000003\\\"}\"], \"result_count\": 75, \"status_counts\": {\"pass\": 59, \"success\": 16}}, \"gold_views\": {\"dim_customer_scd2\": {\"candidate\": 8, \"stable\": 8}, \"dim_date\": {\"candidate\": 46, \"stable\": 46}, \"dim_order_status\": {\"candidate\": 2, \"stable\": 2}, \"dim_product_scd2\": {\"candidate\": 8, \"stable\": 8}, \"dim_seller\": {\"candidate\": 4, \"stable\": 4}, \"fact_order_items\": {\"candidate\": 18, \"stable\": 18}, \"mart_daily_revenue\": {\"candidate\": 13, \"stable\": 13}, \"mart_monthly_arpu\": {\"candidate\": 7, \"stable\": 7}}, \"static_validation\": {\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 177 packages in 1ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"All checks passed!\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"73 files already formatted\", \"exit_code\": 0, \"status\": \"passed\"}], \"status\": \"ready\"}, \"status\": \"ready\", \"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 69.002,
      "gate": "08-additive-schema",
      "status": "PASS",
      "timestamp": "2026-08-04T22:59:09.119444+00:00"
    },
    "09-rebuild": {
      "assertions": [
        {
          "detail": {
            "command": "rebuild-serving",
            "dag_run_id": "stage_l4_20260805_f0_restored_rebuild_cbba942ffa86",
            "entity_counts": {
              "customers": 10,
              "order_items": 19,
              "order_payments": 16,
              "order_reviews": 14,
              "orders": 14,
              "product_category_translation": 5,
              "products": 8,
              "sellers": 4
            },
            "expected_event_count": 90,
            "iceberg_snapshot_ids": {
              "customers": 4667963551008397841,
              "order_items": 6104085289137992191,
              "order_payments": 4402592427034762001,
              "order_reviews": 1998650664707823942,
              "orders": 8715658499880008100,
              "product_category_translation": 2493780499513490015,
              "products": 7672100197799865306,
              "sellers": 9125635543796638711
            },
            "materialized_event_count": 90,
            "status": "succeeded",
            "sync_run_id": "sync-00000000000000000004",
            "sync_run_seq": 4
          },
          "name": "rebuild_serving_from_iceberg",
          "status": "PASS"
        },
        {
          "detail": {
            "candidate_current_counts": {
              "customers": 9,
              "order_items": 18,
              "order_payments": 16,
              "order_reviews": 12,
              "orders": 13,
              "product_category_translation": 5,
              "products": 8,
              "sellers": 4
            },
            "command": "validate-rebuild",
            "dbt": {
              "command": [
                "build",
                "--project-dir",
                "/opt/airflow/project/dbt/olist_clickhouse",
                "--profiles-dir",
                "/opt/airflow/project/dbt/olist_clickhouse",
                "--selector",
                "serving_candidate",
                "--vars",
                "{\"sync_run_seq\": 4, \"sync_run_id\": \"sync-00000000000000000004\"}"
              ],
              "result_count": 75,
              "status_counts": {
                "pass": 59,
                "success": 16
              }
            },
            "expected_event_count": 90,
            "gold_views": {
              "dim_customer_scd2": {
                "candidate": 8,
                "stable": 8
              },
              "dim_date": {
                "candidate": 46,
                "stable": 46
              },
              "dim_order_status": {
                "candidate": 2,
                "stable": 2
              },
              "dim_product_scd2": {
                "candidate": 8,
                "stable": 8
              },
              "dim_seller": {
                "candidate": 4,
                "stable": 4
              },
              "fact_order_items": {
                "candidate": 18,
                "stable": 18
              },
              "mart_daily_revenue": {
                "candidate": 13,
                "stable": 13
              },
              "mart_monthly_arpu": {
                "candidate": 7,
                "stable": 7
              }
            },
            "iceberg_current_counts": {
              "customers": 9,
              "order_items": 18,
              "order_payments": 16,
              "order_reviews": 12,
              "orders": 13,
              "product_category_translation": 5,
              "products": 8,
              "sellers": 4
            },
            "iceberg_snapshot_ids": {
              "customers": 4667963551008397841,
              "order_items": 6104085289137992191,
              "order_payments": 4402592427034762001,
              "order_reviews": 1998650664707823942,
              "orders": 8715658499880008100,
              "product_category_translation": 2493780499513490015,
              "products": 7672100197799865306,
              "sellers": 9125635543796638711
            },
            "materialized_event_count": 90,
            "row_manifests": {
              "candidate_physical": {
                "customers": {
                  "manifest_sha256": "bc9c042a90199accd2c8b6545ee4c1b3015b556dfbffd8a54a21c3ed4a48d4c1",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "c8215415f5236d27f71cd836daaefda158598e9f2fed41d6d62e640d9945effe"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "64d9c2cdd88f51d85d3fe7445154ac99ef6735fb56262de8f7d3214c05de44f9"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "e553baa7a4a5579b541aa1b8fd500391074b9a999b41deac0142880b71929018"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "9c28bbf645cbfa9c1db42a585757632205ba7b54473a522b2faf68b7816cc9b3"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "cea8b62418507e021e8a8e01485bb769015d0c81525db8a106173b9dda09472b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "977c38faff0ead04b7517382031c765a03476b7c12f9d2a471b8aedfb098afef"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "9f9040e360dca3eed6784be4dee5482e1af319b3dd69ba43dbe4627227a2690a"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "9d46cb8a8302603ac19146611affc3b2f6a8e28547f328544d19172ba9d52bd5"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "665d49e1871c07b02542feb2d4dec0a60fe5daaeb41751a5f14873f0510b69e9"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "9118a9283a524a0cc9ced2e67b2f1e08c89dd4706446c7c8046b89680685373f",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "7f18d5b67cd21bcf6dcf1c5797cf551fb7f23af9e98a0a24a36ae7257d0a4d75"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "23c757304da7dbcb1a517a8439cc72c145499b3a4212099d258f9f9e464a26a6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "fdfcfa2002bfdb68f5f3fe77e8df2ac67b8ff393c5dfdd4bba4f6e0dcfd6031f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "35c2597b7ead114ee297450bd48f0a20ab8ab96e70a9dac377609e35cba89f5f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "5d1c447e84b8c9d1a69f2485c910130001abbf69a5cfcd018b808c752a4acde0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "c17d98504fac48f278c77e74499bdf38da0fada6e47f12b8c15769d1ff06a9fd"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "b66f46824ab6da07736d07ab773697e1ff0761c9b33aeae1e54ee788681b51b3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "711510d9f0b3bae7d3499a55f865224d50d7dbef8ccfd4fbe33849899c610966"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "f79a72600db6d5d40788c7759d230f59d952b38c98f60d73fe4f77c2711b4b5b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "d6785a7a29c0a1d3ce6e6434ae4fd068b0ea0e70591fe20f5427e574e23a3b97"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "06a8c1986113b42d7d8ad6d0635aa60c83a05a84e704337751593eb5022cac21"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "08b3e25eac812a60d04197110fefa464079fc2a9d48ab2373f5cbeb96bee426d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "9f937a3373161b7c672f1ba8fa3d885498ae747f504d3a04bfa8a4ee8cb09e1d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "cb6b300ccc0d96f835b9c1d0f21d2c3a997caeda6324702bb8f6df252ddfe244"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fc80978f39a749817341146eabe53f6205ef06048d6e64aa911c73d659884d30"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5ebdf9587ead2590b005815d16734c36b9e1ba790a2b05997532e0fecc93314b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "38fbc91331ab21a153ba710afee80d3a7750a2a9f76f536c2937be68e982d217"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "332b3f3b32ec36cb67b8efb5867cf685887d93f049eecdb9365a5979931901bf"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f4c1898e1d30a6b1dc0a5f24e9d5ca875427669fb3db7678745936dcc1198567",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "c45444db18bdc311e663290ef083891ee0501afe11526c18033b8002f85ba26b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "fa3adf19f6121207611d32090adac8f0f05e943889f8c4d20af5e53e6fae3b2d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "4860a72381018d6591e245e870826d159c1fe59aeca2312adf81154cc620a917"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "f9ecb675b3889ce0ec239fd35a018a7bdb82b0463918b89cbc4561333e022baf"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "e5b0a92b89449573b20f90081b4e850e7739040d06ee1545c0d1a06f45b549f0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "5b694cd07195cc2a4fa60ffb92f51da74edf7d41df6c7936b4165cb0f9f078bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "f495da08c39bf33c473f25a2488c05adfd7e3dc92d0b836d7ee4af17e4644b22"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "d85e7108a23e17fe719c1223c88e48282c66b440f0fcb9bfe318617ef098d147"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "4d2ab0de9af96f944aa7b9a14040236c8e43d25a3c75125d1222c9f0200ea929"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "59fc1194e6e1cae2daaa5211e75c3008949edf539caa6d07997dd86087878c02"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "72d6fcd90b71a371c2ea13aaf35b256a7f9dbbbc204e8bba3b0b6da1071c85ba"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "8c40d12e7bb42486aeae733142c57513dc74f18a21bd4c5a7eb99a165aa3d1ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "9c594e6034d98e2048224368b7c68a34f3c09e276e0676443876b50dda22abf1"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "36ef4a81c8ab19c15d02c9eb3ca0d66ea325cef6679013efe40cc21e38637041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "9c1c7aaa288007ebd2f875f6a2e0b9e139be2c3d2769ac891c5a3ca059ee0041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "a5ad08ef2c99a3a13d99c013d9ea91ba6325a7239a312f6c36f6de162f905575"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "7f8bd7ceedd836351e7a2c8d030874dd7c340899954552deb522ea1fcbde182a",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "a04092d3189e793b4a9d5d9280ae820ce2836c1fa2a314d69d000f1fed428fee"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "5810f829f64827be40dc102c84eb90da86a1f7ab2dee59a2974dd2b6057280ab"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "32b0bad94856a8a09383f38d365c0c48a4690c5507bef5b9493fe8bbb7d8ebed"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "4931125f09d6c89b2c3139869b1f01b94bad451cedd296dfb0d26223b68d4d0d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "b5417e80a64bb6948b5ddc0b4396d620df143031acaaf7ed105fef3e9c940dc6"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "875c4f72924a004955fdff0e3c281cad64350cb9b8f5f407beabeb9425a3c231"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "6a7fa2ea4d0406720724b11bc1c9c34929eac64ef29b50ee26ee243aee1bfae1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "0b0aff0918cd501bbedb86c183ca69c84f0fddcb8f60fe8bf2f6551002894e94"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "fdc801df7a94125624670c1bf72bb45b85c6a33f963ff864bbaa8f12e3e0ae8a"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "8f5ee1e0a47cad8d30b99a752083652783eb138a7d16a29709f153b8b3a23f3f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "b838dbfd73e3a6a2ca7130095a308f2fe2dad6bf1d1027f007237430b5a06c24"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "3137bf0b91bd3334f1657e14e454a8b1afe842f7d2d0a1449e625bddba11c2df"
                    },
                    {
                      "is_deleted": true,
                      "review_id": "wave2_review_001",
                      "row_hash": "3254b0fe5706ca8e888cd955049960ef953c10460c412dcfb538807f72bba6bc"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "3040ad58ffdc7f70682550830b67ec1fab9dc265ac1554759c8580a09a6c687c",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "407c87766b37dc3485b3825a9efca0d20f8084d8671fe61acfc265e1e5abdac3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "642cf66a70dc0a60d327e8e290cc7aabfa12b24716a5f615fd922179412f9f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "b7ff53576ed4193a464cb842cb84df66801cf1660b92a2931aca42b50ada8bfa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "f705453b64d1cbbae1661099e8e447a185de939f94d0407c2b942fcf0907bcc4"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "db2e14d54dcf3e9455b489750d4dd7606dd9c41e975f30c44d9fcaef2130e8f9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "45cad2e9dfea14756fa071558a67a1ecbe81f6e4fda253ba33953eb192437fe2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "63853bf6c354eed16bdc991d89bfebd42bd6aa871887bca8c3876faf45460553"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "89e1dc65ca868af3bce6c0c73eb157d9cfce2d2748a3bef2b9b2d6054a59045a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "2fe3d6d121df8aeb4f96c0fb5118d53c675756d0ccb615a8af44a525717016a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "628760995eda638bb712cf64431ddaecfd4b6905433f14269da8db724b409382"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "d0bf951786e21c749941582ac452beaeeed237cbf8d3e5dcee6c09d5029a49bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "6dbaa0e36b7446220f83b50da4e19911104326d0cb51f35188a46c85b5cddf03"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "c1a41a5261b75f0b71ecf5ad829928bac35b7c7a67a491eee7d13f5965ed788c"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61f157a1cbedeea8f214219ffa2f90fe5ac2f3d5b9ce0f4c0fa46e325c54a157",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e085cf609c78b0c0fe900014743119497829e5a6d120d5b54310fe4393dcf67b"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "73b84ffda407d572c90e810ffedbe2d98aba4bf6d184790b78fc4b9c9b306ef5"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "b759d00fcca6316ae9a16d619e31083ae2082d244762f561cc4b4d7448f96015"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "73ba7905776d6af74dec4df8b1537ee4821dd2a749cb63497fa1d4f9d5c7be9d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "7b9d78a70259211cdc9503bb1619cd68784dafdbddd3dd0b438d30a2f7c511e7"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1fb130cbaa8ff2f1338382868f7050c6103ebadaefc9dae92b21dcd3c95f2477",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "e34df2daef40e596732c0796a08514f4ed41812f4c609bf8a70d683126911d52"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f3c664b16958b91957fad0e0c3387d4496ccd27b2520598611ebf3ee3c7f4b"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "93ed5b1658dd42c3623275e89715327a622e2b64cef16820ecfab9378435baeb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "89a7c3b6b41d92ccd10c826898c1a2fa7a87e42813d5d228d210e4cb3a2b2ef4"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "270bc944c4a03c0ec4873dedc68aaf5216620736d6c4e94d4c0e01ce75e879e6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "cb3a5dd2a945ae9b8f73ea9bfe452b0b58fceb0a0c46fec82637d97728ae2e35"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "c2d40c4d0507d71755ffbe7548c54865272f7172eb5497f3498f1ff3fe366944"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "c5478414bc21d3d22782baf85adc57d5cf8db792c0f88cc742130cd1b6ad8c42"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "dfa115195e9fd45cfd4f04e1ee64d4e1b8e080aed21717b79a82a9f7b651ef98",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "13b4f5314cf3797a91b51df01383224a5f94b2dd84479f46df686910e1ddfa7f",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6a893717586f34c0d890b901c89c4f54a1f92abb4fa3e7ad84f74c978cee9928",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "ccceb257820f2ec09e89c00dfb67017f44018f987c314f7abab10b57b71fcb6c",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5285104caa341f9ce197d99d6d57f9a0ef09671e0284e8003697d00e3f2ad991",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "candidate_visible": {
                "customers": {
                  "manifest_sha256": "bc9c042a90199accd2c8b6545ee4c1b3015b556dfbffd8a54a21c3ed4a48d4c1",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "c8215415f5236d27f71cd836daaefda158598e9f2fed41d6d62e640d9945effe"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "64d9c2cdd88f51d85d3fe7445154ac99ef6735fb56262de8f7d3214c05de44f9"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "e553baa7a4a5579b541aa1b8fd500391074b9a999b41deac0142880b71929018"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "9c28bbf645cbfa9c1db42a585757632205ba7b54473a522b2faf68b7816cc9b3"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "cea8b62418507e021e8a8e01485bb769015d0c81525db8a106173b9dda09472b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "977c38faff0ead04b7517382031c765a03476b7c12f9d2a471b8aedfb098afef"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "9f9040e360dca3eed6784be4dee5482e1af319b3dd69ba43dbe4627227a2690a"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "9d46cb8a8302603ac19146611affc3b2f6a8e28547f328544d19172ba9d52bd5"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "665d49e1871c07b02542feb2d4dec0a60fe5daaeb41751a5f14873f0510b69e9"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "9118a9283a524a0cc9ced2e67b2f1e08c89dd4706446c7c8046b89680685373f",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "7f18d5b67cd21bcf6dcf1c5797cf551fb7f23af9e98a0a24a36ae7257d0a4d75"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "23c757304da7dbcb1a517a8439cc72c145499b3a4212099d258f9f9e464a26a6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "fdfcfa2002bfdb68f5f3fe77e8df2ac67b8ff393c5dfdd4bba4f6e0dcfd6031f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "35c2597b7ead114ee297450bd48f0a20ab8ab96e70a9dac377609e35cba89f5f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "5d1c447e84b8c9d1a69f2485c910130001abbf69a5cfcd018b808c752a4acde0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "c17d98504fac48f278c77e74499bdf38da0fada6e47f12b8c15769d1ff06a9fd"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "b66f46824ab6da07736d07ab773697e1ff0761c9b33aeae1e54ee788681b51b3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "711510d9f0b3bae7d3499a55f865224d50d7dbef8ccfd4fbe33849899c610966"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "f79a72600db6d5d40788c7759d230f59d952b38c98f60d73fe4f77c2711b4b5b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "d6785a7a29c0a1d3ce6e6434ae4fd068b0ea0e70591fe20f5427e574e23a3b97"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "06a8c1986113b42d7d8ad6d0635aa60c83a05a84e704337751593eb5022cac21"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "08b3e25eac812a60d04197110fefa464079fc2a9d48ab2373f5cbeb96bee426d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "9f937a3373161b7c672f1ba8fa3d885498ae747f504d3a04bfa8a4ee8cb09e1d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "cb6b300ccc0d96f835b9c1d0f21d2c3a997caeda6324702bb8f6df252ddfe244"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fc80978f39a749817341146eabe53f6205ef06048d6e64aa911c73d659884d30"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5ebdf9587ead2590b005815d16734c36b9e1ba790a2b05997532e0fecc93314b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "38fbc91331ab21a153ba710afee80d3a7750a2a9f76f536c2937be68e982d217"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "332b3f3b32ec36cb67b8efb5867cf685887d93f049eecdb9365a5979931901bf"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f4c1898e1d30a6b1dc0a5f24e9d5ca875427669fb3db7678745936dcc1198567",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "c45444db18bdc311e663290ef083891ee0501afe11526c18033b8002f85ba26b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "fa3adf19f6121207611d32090adac8f0f05e943889f8c4d20af5e53e6fae3b2d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "4860a72381018d6591e245e870826d159c1fe59aeca2312adf81154cc620a917"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "f9ecb675b3889ce0ec239fd35a018a7bdb82b0463918b89cbc4561333e022baf"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "e5b0a92b89449573b20f90081b4e850e7739040d06ee1545c0d1a06f45b549f0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "5b694cd07195cc2a4fa60ffb92f51da74edf7d41df6c7936b4165cb0f9f078bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "f495da08c39bf33c473f25a2488c05adfd7e3dc92d0b836d7ee4af17e4644b22"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "d85e7108a23e17fe719c1223c88e48282c66b440f0fcb9bfe318617ef098d147"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "4d2ab0de9af96f944aa7b9a14040236c8e43d25a3c75125d1222c9f0200ea929"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "59fc1194e6e1cae2daaa5211e75c3008949edf539caa6d07997dd86087878c02"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "72d6fcd90b71a371c2ea13aaf35b256a7f9dbbbc204e8bba3b0b6da1071c85ba"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "8c40d12e7bb42486aeae733142c57513dc74f18a21bd4c5a7eb99a165aa3d1ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "9c594e6034d98e2048224368b7c68a34f3c09e276e0676443876b50dda22abf1"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "36ef4a81c8ab19c15d02c9eb3ca0d66ea325cef6679013efe40cc21e38637041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "9c1c7aaa288007ebd2f875f6a2e0b9e139be2c3d2769ac891c5a3ca059ee0041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "a5ad08ef2c99a3a13d99c013d9ea91ba6325a7239a312f6c36f6de162f905575"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "504c4f2b3722be480505f21e90c657e0fb1bd2183be054e2ab72de60113f40de",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "a04092d3189e793b4a9d5d9280ae820ce2836c1fa2a314d69d000f1fed428fee"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "5810f829f64827be40dc102c84eb90da86a1f7ab2dee59a2974dd2b6057280ab"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "32b0bad94856a8a09383f38d365c0c48a4690c5507bef5b9493fe8bbb7d8ebed"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "4931125f09d6c89b2c3139869b1f01b94bad451cedd296dfb0d26223b68d4d0d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "b5417e80a64bb6948b5ddc0b4396d620df143031acaaf7ed105fef3e9c940dc6"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "875c4f72924a004955fdff0e3c281cad64350cb9b8f5f407beabeb9425a3c231"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "6a7fa2ea4d0406720724b11bc1c9c34929eac64ef29b50ee26ee243aee1bfae1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "0b0aff0918cd501bbedb86c183ca69c84f0fddcb8f60fe8bf2f6551002894e94"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "fdc801df7a94125624670c1bf72bb45b85c6a33f963ff864bbaa8f12e3e0ae8a"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "8f5ee1e0a47cad8d30b99a752083652783eb138a7d16a29709f153b8b3a23f3f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "b838dbfd73e3a6a2ca7130095a308f2fe2dad6bf1d1027f007237430b5a06c24"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "3137bf0b91bd3334f1657e14e454a8b1afe842f7d2d0a1449e625bddba11c2df"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "3040ad58ffdc7f70682550830b67ec1fab9dc265ac1554759c8580a09a6c687c",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "407c87766b37dc3485b3825a9efca0d20f8084d8671fe61acfc265e1e5abdac3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "642cf66a70dc0a60d327e8e290cc7aabfa12b24716a5f615fd922179412f9f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "b7ff53576ed4193a464cb842cb84df66801cf1660b92a2931aca42b50ada8bfa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "f705453b64d1cbbae1661099e8e447a185de939f94d0407c2b942fcf0907bcc4"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "db2e14d54dcf3e9455b489750d4dd7606dd9c41e975f30c44d9fcaef2130e8f9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "45cad2e9dfea14756fa071558a67a1ecbe81f6e4fda253ba33953eb192437fe2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "63853bf6c354eed16bdc991d89bfebd42bd6aa871887bca8c3876faf45460553"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "89e1dc65ca868af3bce6c0c73eb157d9cfce2d2748a3bef2b9b2d6054a59045a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "2fe3d6d121df8aeb4f96c0fb5118d53c675756d0ccb615a8af44a525717016a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "628760995eda638bb712cf64431ddaecfd4b6905433f14269da8db724b409382"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "d0bf951786e21c749941582ac452beaeeed237cbf8d3e5dcee6c09d5029a49bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "6dbaa0e36b7446220f83b50da4e19911104326d0cb51f35188a46c85b5cddf03"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "c1a41a5261b75f0b71ecf5ad829928bac35b7c7a67a491eee7d13f5965ed788c"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61f157a1cbedeea8f214219ffa2f90fe5ac2f3d5b9ce0f4c0fa46e325c54a157",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e085cf609c78b0c0fe900014743119497829e5a6d120d5b54310fe4393dcf67b"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "73b84ffda407d572c90e810ffedbe2d98aba4bf6d184790b78fc4b9c9b306ef5"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "b759d00fcca6316ae9a16d619e31083ae2082d244762f561cc4b4d7448f96015"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "73ba7905776d6af74dec4df8b1537ee4821dd2a749cb63497fa1d4f9d5c7be9d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "7b9d78a70259211cdc9503bb1619cd68784dafdbddd3dd0b438d30a2f7c511e7"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1fb130cbaa8ff2f1338382868f7050c6103ebadaefc9dae92b21dcd3c95f2477",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "e34df2daef40e596732c0796a08514f4ed41812f4c609bf8a70d683126911d52"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f3c664b16958b91957fad0e0c3387d4496ccd27b2520598611ebf3ee3c7f4b"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "93ed5b1658dd42c3623275e89715327a622e2b64cef16820ecfab9378435baeb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "89a7c3b6b41d92ccd10c826898c1a2fa7a87e42813d5d228d210e4cb3a2b2ef4"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "270bc944c4a03c0ec4873dedc68aaf5216620736d6c4e94d4c0e01ce75e879e6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "cb3a5dd2a945ae9b8f73ea9bfe452b0b58fceb0a0c46fec82637d97728ae2e35"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "c2d40c4d0507d71755ffbe7548c54865272f7172eb5497f3498f1ff3fe366944"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "c5478414bc21d3d22782baf85adc57d5cf8db792c0f88cc742130cd1b6ad8c42"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "dfa115195e9fd45cfd4f04e1ee64d4e1b8e080aed21717b79a82a9f7b651ef98",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "13b4f5314cf3797a91b51df01383224a5f94b2dd84479f46df686910e1ddfa7f",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6a893717586f34c0d890b901c89c4f54a1f92abb4fa3e7ad84f74c978cee9928",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "ccceb257820f2ec09e89c00dfb67017f44018f987c314f7abab10b57b71fcb6c",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5285104caa341f9ce197d99d6d57f9a0ef09671e0284e8003697d00e3f2ad991",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "iceberg_physical": {
                "customers": {
                  "manifest_sha256": "bc9c042a90199accd2c8b6545ee4c1b3015b556dfbffd8a54a21c3ed4a48d4c1",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "c8215415f5236d27f71cd836daaefda158598e9f2fed41d6d62e640d9945effe"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "64d9c2cdd88f51d85d3fe7445154ac99ef6735fb56262de8f7d3214c05de44f9"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "e553baa7a4a5579b541aa1b8fd500391074b9a999b41deac0142880b71929018"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "9c28bbf645cbfa9c1db42a585757632205ba7b54473a522b2faf68b7816cc9b3"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "cea8b62418507e021e8a8e01485bb769015d0c81525db8a106173b9dda09472b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "977c38faff0ead04b7517382031c765a03476b7c12f9d2a471b8aedfb098afef"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "9f9040e360dca3eed6784be4dee5482e1af319b3dd69ba43dbe4627227a2690a"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "9d46cb8a8302603ac19146611affc3b2f6a8e28547f328544d19172ba9d52bd5"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "665d49e1871c07b02542feb2d4dec0a60fe5daaeb41751a5f14873f0510b69e9"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "9118a9283a524a0cc9ced2e67b2f1e08c89dd4706446c7c8046b89680685373f",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "7f18d5b67cd21bcf6dcf1c5797cf551fb7f23af9e98a0a24a36ae7257d0a4d75"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "23c757304da7dbcb1a517a8439cc72c145499b3a4212099d258f9f9e464a26a6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "fdfcfa2002bfdb68f5f3fe77e8df2ac67b8ff393c5dfdd4bba4f6e0dcfd6031f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "35c2597b7ead114ee297450bd48f0a20ab8ab96e70a9dac377609e35cba89f5f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "5d1c447e84b8c9d1a69f2485c910130001abbf69a5cfcd018b808c752a4acde0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "c17d98504fac48f278c77e74499bdf38da0fada6e47f12b8c15769d1ff06a9fd"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "b66f46824ab6da07736d07ab773697e1ff0761c9b33aeae1e54ee788681b51b3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "711510d9f0b3bae7d3499a55f865224d50d7dbef8ccfd4fbe33849899c610966"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "f79a72600db6d5d40788c7759d230f59d952b38c98f60d73fe4f77c2711b4b5b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "d6785a7a29c0a1d3ce6e6434ae4fd068b0ea0e70591fe20f5427e574e23a3b97"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "06a8c1986113b42d7d8ad6d0635aa60c83a05a84e704337751593eb5022cac21"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "08b3e25eac812a60d04197110fefa464079fc2a9d48ab2373f5cbeb96bee426d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "9f937a3373161b7c672f1ba8fa3d885498ae747f504d3a04bfa8a4ee8cb09e1d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "cb6b300ccc0d96f835b9c1d0f21d2c3a997caeda6324702bb8f6df252ddfe244"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fc80978f39a749817341146eabe53f6205ef06048d6e64aa911c73d659884d30"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5ebdf9587ead2590b005815d16734c36b9e1ba790a2b05997532e0fecc93314b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "38fbc91331ab21a153ba710afee80d3a7750a2a9f76f536c2937be68e982d217"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "332b3f3b32ec36cb67b8efb5867cf685887d93f049eecdb9365a5979931901bf"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f4c1898e1d30a6b1dc0a5f24e9d5ca875427669fb3db7678745936dcc1198567",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "c45444db18bdc311e663290ef083891ee0501afe11526c18033b8002f85ba26b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "fa3adf19f6121207611d32090adac8f0f05e943889f8c4d20af5e53e6fae3b2d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "4860a72381018d6591e245e870826d159c1fe59aeca2312adf81154cc620a917"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "f9ecb675b3889ce0ec239fd35a018a7bdb82b0463918b89cbc4561333e022baf"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "e5b0a92b89449573b20f90081b4e850e7739040d06ee1545c0d1a06f45b549f0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "5b694cd07195cc2a4fa60ffb92f51da74edf7d41df6c7936b4165cb0f9f078bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "f495da08c39bf33c473f25a2488c05adfd7e3dc92d0b836d7ee4af17e4644b22"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "d85e7108a23e17fe719c1223c88e48282c66b440f0fcb9bfe318617ef098d147"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "4d2ab0de9af96f944aa7b9a14040236c8e43d25a3c75125d1222c9f0200ea929"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "59fc1194e6e1cae2daaa5211e75c3008949edf539caa6d07997dd86087878c02"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "72d6fcd90b71a371c2ea13aaf35b256a7f9dbbbc204e8bba3b0b6da1071c85ba"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "8c40d12e7bb42486aeae733142c57513dc74f18a21bd4c5a7eb99a165aa3d1ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "9c594e6034d98e2048224368b7c68a34f3c09e276e0676443876b50dda22abf1"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "36ef4a81c8ab19c15d02c9eb3ca0d66ea325cef6679013efe40cc21e38637041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "9c1c7aaa288007ebd2f875f6a2e0b9e139be2c3d2769ac891c5a3ca059ee0041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "a5ad08ef2c99a3a13d99c013d9ea91ba6325a7239a312f6c36f6de162f905575"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "7f8bd7ceedd836351e7a2c8d030874dd7c340899954552deb522ea1fcbde182a",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "a04092d3189e793b4a9d5d9280ae820ce2836c1fa2a314d69d000f1fed428fee"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "5810f829f64827be40dc102c84eb90da86a1f7ab2dee59a2974dd2b6057280ab"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "32b0bad94856a8a09383f38d365c0c48a4690c5507bef5b9493fe8bbb7d8ebed"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "4931125f09d6c89b2c3139869b1f01b94bad451cedd296dfb0d26223b68d4d0d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "b5417e80a64bb6948b5ddc0b4396d620df143031acaaf7ed105fef3e9c940dc6"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "875c4f72924a004955fdff0e3c281cad64350cb9b8f5f407beabeb9425a3c231"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "6a7fa2ea4d0406720724b11bc1c9c34929eac64ef29b50ee26ee243aee1bfae1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "0b0aff0918cd501bbedb86c183ca69c84f0fddcb8f60fe8bf2f6551002894e94"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "fdc801df7a94125624670c1bf72bb45b85c6a33f963ff864bbaa8f12e3e0ae8a"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "8f5ee1e0a47cad8d30b99a752083652783eb138a7d16a29709f153b8b3a23f3f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "b838dbfd73e3a6a2ca7130095a308f2fe2dad6bf1d1027f007237430b5a06c24"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "3137bf0b91bd3334f1657e14e454a8b1afe842f7d2d0a1449e625bddba11c2df"
                    },
                    {
                      "is_deleted": true,
                      "review_id": "wave2_review_001",
                      "row_hash": "3254b0fe5706ca8e888cd955049960ef953c10460c412dcfb538807f72bba6bc"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "3040ad58ffdc7f70682550830b67ec1fab9dc265ac1554759c8580a09a6c687c",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "407c87766b37dc3485b3825a9efca0d20f8084d8671fe61acfc265e1e5abdac3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "642cf66a70dc0a60d327e8e290cc7aabfa12b24716a5f615fd922179412f9f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "b7ff53576ed4193a464cb842cb84df66801cf1660b92a2931aca42b50ada8bfa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "f705453b64d1cbbae1661099e8e447a185de939f94d0407c2b942fcf0907bcc4"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "db2e14d54dcf3e9455b489750d4dd7606dd9c41e975f30c44d9fcaef2130e8f9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "45cad2e9dfea14756fa071558a67a1ecbe81f6e4fda253ba33953eb192437fe2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "63853bf6c354eed16bdc991d89bfebd42bd6aa871887bca8c3876faf45460553"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "89e1dc65ca868af3bce6c0c73eb157d9cfce2d2748a3bef2b9b2d6054a59045a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "2fe3d6d121df8aeb4f96c0fb5118d53c675756d0ccb615a8af44a525717016a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "628760995eda638bb712cf64431ddaecfd4b6905433f14269da8db724b409382"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "d0bf951786e21c749941582ac452beaeeed237cbf8d3e5dcee6c09d5029a49bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "6dbaa0e36b7446220f83b50da4e19911104326d0cb51f35188a46c85b5cddf03"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "c1a41a5261b75f0b71ecf5ad829928bac35b7c7a67a491eee7d13f5965ed788c"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61f157a1cbedeea8f214219ffa2f90fe5ac2f3d5b9ce0f4c0fa46e325c54a157",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e085cf609c78b0c0fe900014743119497829e5a6d120d5b54310fe4393dcf67b"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "73b84ffda407d572c90e810ffedbe2d98aba4bf6d184790b78fc4b9c9b306ef5"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "b759d00fcca6316ae9a16d619e31083ae2082d244762f561cc4b4d7448f96015"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "73ba7905776d6af74dec4df8b1537ee4821dd2a749cb63497fa1d4f9d5c7be9d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "7b9d78a70259211cdc9503bb1619cd68784dafdbddd3dd0b438d30a2f7c511e7"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1fb130cbaa8ff2f1338382868f7050c6103ebadaefc9dae92b21dcd3c95f2477",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "e34df2daef40e596732c0796a08514f4ed41812f4c609bf8a70d683126911d52"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f3c664b16958b91957fad0e0c3387d4496ccd27b2520598611ebf3ee3c7f4b"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "93ed5b1658dd42c3623275e89715327a622e2b64cef16820ecfab9378435baeb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "89a7c3b6b41d92ccd10c826898c1a2fa7a87e42813d5d228d210e4cb3a2b2ef4"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "270bc944c4a03c0ec4873dedc68aaf5216620736d6c4e94d4c0e01ce75e879e6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "cb3a5dd2a945ae9b8f73ea9bfe452b0b58fceb0a0c46fec82637d97728ae2e35"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "c2d40c4d0507d71755ffbe7548c54865272f7172eb5497f3498f1ff3fe366944"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "c5478414bc21d3d22782baf85adc57d5cf8db792c0f88cc742130cd1b6ad8c42"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "dfa115195e9fd45cfd4f04e1ee64d4e1b8e080aed21717b79a82a9f7b651ef98",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "13b4f5314cf3797a91b51df01383224a5f94b2dd84479f46df686910e1ddfa7f",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6a893717586f34c0d890b901c89c4f54a1f92abb4fa3e7ad84f74c978cee9928",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "ccceb257820f2ec09e89c00dfb67017f44018f987c314f7abab10b57b71fcb6c",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5285104caa341f9ce197d99d6d57f9a0ef09671e0284e8003697d00e3f2ad991",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "iceberg_visible": {
                "customers": {
                  "manifest_sha256": "bc9c042a90199accd2c8b6545ee4c1b3015b556dfbffd8a54a21c3ed4a48d4c1",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "c8215415f5236d27f71cd836daaefda158598e9f2fed41d6d62e640d9945effe"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "64d9c2cdd88f51d85d3fe7445154ac99ef6735fb56262de8f7d3214c05de44f9"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "e553baa7a4a5579b541aa1b8fd500391074b9a999b41deac0142880b71929018"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "9c28bbf645cbfa9c1db42a585757632205ba7b54473a522b2faf68b7816cc9b3"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "cea8b62418507e021e8a8e01485bb769015d0c81525db8a106173b9dda09472b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "977c38faff0ead04b7517382031c765a03476b7c12f9d2a471b8aedfb098afef"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "9f9040e360dca3eed6784be4dee5482e1af319b3dd69ba43dbe4627227a2690a"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "9d46cb8a8302603ac19146611affc3b2f6a8e28547f328544d19172ba9d52bd5"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "665d49e1871c07b02542feb2d4dec0a60fe5daaeb41751a5f14873f0510b69e9"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "9118a9283a524a0cc9ced2e67b2f1e08c89dd4706446c7c8046b89680685373f",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "7f18d5b67cd21bcf6dcf1c5797cf551fb7f23af9e98a0a24a36ae7257d0a4d75"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "23c757304da7dbcb1a517a8439cc72c145499b3a4212099d258f9f9e464a26a6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "fdfcfa2002bfdb68f5f3fe77e8df2ac67b8ff393c5dfdd4bba4f6e0dcfd6031f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "35c2597b7ead114ee297450bd48f0a20ab8ab96e70a9dac377609e35cba89f5f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "5d1c447e84b8c9d1a69f2485c910130001abbf69a5cfcd018b808c752a4acde0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "c17d98504fac48f278c77e74499bdf38da0fada6e47f12b8c15769d1ff06a9fd"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "b66f46824ab6da07736d07ab773697e1ff0761c9b33aeae1e54ee788681b51b3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "711510d9f0b3bae7d3499a55f865224d50d7dbef8ccfd4fbe33849899c610966"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "f79a72600db6d5d40788c7759d230f59d952b38c98f60d73fe4f77c2711b4b5b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "d6785a7a29c0a1d3ce6e6434ae4fd068b0ea0e70591fe20f5427e574e23a3b97"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "06a8c1986113b42d7d8ad6d0635aa60c83a05a84e704337751593eb5022cac21"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "08b3e25eac812a60d04197110fefa464079fc2a9d48ab2373f5cbeb96bee426d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "9f937a3373161b7c672f1ba8fa3d885498ae747f504d3a04bfa8a4ee8cb09e1d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "cb6b300ccc0d96f835b9c1d0f21d2c3a997caeda6324702bb8f6df252ddfe244"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fc80978f39a749817341146eabe53f6205ef06048d6e64aa911c73d659884d30"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5ebdf9587ead2590b005815d16734c36b9e1ba790a2b05997532e0fecc93314b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "38fbc91331ab21a153ba710afee80d3a7750a2a9f76f536c2937be68e982d217"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "332b3f3b32ec36cb67b8efb5867cf685887d93f049eecdb9365a5979931901bf"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f4c1898e1d30a6b1dc0a5f24e9d5ca875427669fb3db7678745936dcc1198567",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "c45444db18bdc311e663290ef083891ee0501afe11526c18033b8002f85ba26b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "fa3adf19f6121207611d32090adac8f0f05e943889f8c4d20af5e53e6fae3b2d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "4860a72381018d6591e245e870826d159c1fe59aeca2312adf81154cc620a917"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "f9ecb675b3889ce0ec239fd35a018a7bdb82b0463918b89cbc4561333e022baf"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "e5b0a92b89449573b20f90081b4e850e7739040d06ee1545c0d1a06f45b549f0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "5b694cd07195cc2a4fa60ffb92f51da74edf7d41df6c7936b4165cb0f9f078bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "f495da08c39bf33c473f25a2488c05adfd7e3dc92d0b836d7ee4af17e4644b22"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "d85e7108a23e17fe719c1223c88e48282c66b440f0fcb9bfe318617ef098d147"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "4d2ab0de9af96f944aa7b9a14040236c8e43d25a3c75125d1222c9f0200ea929"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "59fc1194e6e1cae2daaa5211e75c3008949edf539caa6d07997dd86087878c02"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "72d6fcd90b71a371c2ea13aaf35b256a7f9dbbbc204e8bba3b0b6da1071c85ba"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "8c40d12e7bb42486aeae733142c57513dc74f18a21bd4c5a7eb99a165aa3d1ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "9c594e6034d98e2048224368b7c68a34f3c09e276e0676443876b50dda22abf1"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "36ef4a81c8ab19c15d02c9eb3ca0d66ea325cef6679013efe40cc21e38637041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "9c1c7aaa288007ebd2f875f6a2e0b9e139be2c3d2769ac891c5a3ca059ee0041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "a5ad08ef2c99a3a13d99c013d9ea91ba6325a7239a312f6c36f6de162f905575"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "504c4f2b3722be480505f21e90c657e0fb1bd2183be054e2ab72de60113f40de",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "a04092d3189e793b4a9d5d9280ae820ce2836c1fa2a314d69d000f1fed428fee"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "5810f829f64827be40dc102c84eb90da86a1f7ab2dee59a2974dd2b6057280ab"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "32b0bad94856a8a09383f38d365c0c48a4690c5507bef5b9493fe8bbb7d8ebed"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "4931125f09d6c89b2c3139869b1f01b94bad451cedd296dfb0d26223b68d4d0d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "b5417e80a64bb6948b5ddc0b4396d620df143031acaaf7ed105fef3e9c940dc6"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "875c4f72924a004955fdff0e3c281cad64350cb9b8f5f407beabeb9425a3c231"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "6a7fa2ea4d0406720724b11bc1c9c34929eac64ef29b50ee26ee243aee1bfae1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "0b0aff0918cd501bbedb86c183ca69c84f0fddcb8f60fe8bf2f6551002894e94"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "fdc801df7a94125624670c1bf72bb45b85c6a33f963ff864bbaa8f12e3e0ae8a"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "8f5ee1e0a47cad8d30b99a752083652783eb138a7d16a29709f153b8b3a23f3f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "b838dbfd73e3a6a2ca7130095a308f2fe2dad6bf1d1027f007237430b5a06c24"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "3137bf0b91bd3334f1657e14e454a8b1afe842f7d2d0a1449e625bddba11c2df"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "3040ad58ffdc7f70682550830b67ec1fab9dc265ac1554759c8580a09a6c687c",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "407c87766b37dc3485b3825a9efca0d20f8084d8671fe61acfc265e1e5abdac3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "642cf66a70dc0a60d327e8e290cc7aabfa12b24716a5f615fd922179412f9f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "b7ff53576ed4193a464cb842cb84df66801cf1660b92a2931aca42b50ada8bfa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "f705453b64d1cbbae1661099e8e447a185de939f94d0407c2b942fcf0907bcc4"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "db2e14d54dcf3e9455b489750d4dd7606dd9c41e975f30c44d9fcaef2130e8f9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "45cad2e9dfea14756fa071558a67a1ecbe81f6e4fda253ba33953eb192437fe2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "63853bf6c354eed16bdc991d89bfebd42bd6aa871887bca8c3876faf45460553"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "89e1dc65ca868af3bce6c0c73eb157d9cfce2d2748a3bef2b9b2d6054a59045a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "2fe3d6d121df8aeb4f96c0fb5118d53c675756d0ccb615a8af44a525717016a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "628760995eda638bb712cf64431ddaecfd4b6905433f14269da8db724b409382"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "d0bf951786e21c749941582ac452beaeeed237cbf8d3e5dcee6c09d5029a49bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "6dbaa0e36b7446220f83b50da4e19911104326d0cb51f35188a46c85b5cddf03"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "c1a41a5261b75f0b71ecf5ad829928bac35b7c7a67a491eee7d13f5965ed788c"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61f157a1cbedeea8f214219ffa2f90fe5ac2f3d5b9ce0f4c0fa46e325c54a157",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e085cf609c78b0c0fe900014743119497829e5a6d120d5b54310fe4393dcf67b"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "73b84ffda407d572c90e810ffedbe2d98aba4bf6d184790b78fc4b9c9b306ef5"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "b759d00fcca6316ae9a16d619e31083ae2082d244762f561cc4b4d7448f96015"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "73ba7905776d6af74dec4df8b1537ee4821dd2a749cb63497fa1d4f9d5c7be9d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "7b9d78a70259211cdc9503bb1619cd68784dafdbddd3dd0b438d30a2f7c511e7"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1fb130cbaa8ff2f1338382868f7050c6103ebadaefc9dae92b21dcd3c95f2477",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "e34df2daef40e596732c0796a08514f4ed41812f4c609bf8a70d683126911d52"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f3c664b16958b91957fad0e0c3387d4496ccd27b2520598611ebf3ee3c7f4b"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "93ed5b1658dd42c3623275e89715327a622e2b64cef16820ecfab9378435baeb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "89a7c3b6b41d92ccd10c826898c1a2fa7a87e42813d5d228d210e4cb3a2b2ef4"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "270bc944c4a03c0ec4873dedc68aaf5216620736d6c4e94d4c0e01ce75e879e6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "cb3a5dd2a945ae9b8f73ea9bfe452b0b58fceb0a0c46fec82637d97728ae2e35"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "c2d40c4d0507d71755ffbe7548c54865272f7172eb5497f3498f1ff3fe366944"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "c5478414bc21d3d22782baf85adc57d5cf8db792c0f88cc742130cd1b6ad8c42"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "dfa115195e9fd45cfd4f04e1ee64d4e1b8e080aed21717b79a82a9f7b651ef98",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "13b4f5314cf3797a91b51df01383224a5f94b2dd84479f46df686910e1ddfa7f",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6a893717586f34c0d890b901c89c4f54a1f92abb4fa3e7ad84f74c978cee9928",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "ccceb257820f2ec09e89c00dfb67017f44018f987c314f7abab10b57b71fcb6c",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5285104caa341f9ce197d99d6d57f9a0ef09671e0284e8003697d00e3f2ad991",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "stable_visible": {
                "customers": {
                  "manifest_sha256": "bc9c042a90199accd2c8b6545ee4c1b3015b556dfbffd8a54a21c3ed4a48d4c1",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "c8215415f5236d27f71cd836daaefda158598e9f2fed41d6d62e640d9945effe"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "64d9c2cdd88f51d85d3fe7445154ac99ef6735fb56262de8f7d3214c05de44f9"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "e553baa7a4a5579b541aa1b8fd500391074b9a999b41deac0142880b71929018"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "9c28bbf645cbfa9c1db42a585757632205ba7b54473a522b2faf68b7816cc9b3"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "cea8b62418507e021e8a8e01485bb769015d0c81525db8a106173b9dda09472b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "977c38faff0ead04b7517382031c765a03476b7c12f9d2a471b8aedfb098afef"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "9f9040e360dca3eed6784be4dee5482e1af319b3dd69ba43dbe4627227a2690a"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "9d46cb8a8302603ac19146611affc3b2f6a8e28547f328544d19172ba9d52bd5"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "665d49e1871c07b02542feb2d4dec0a60fe5daaeb41751a5f14873f0510b69e9"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "9118a9283a524a0cc9ced2e67b2f1e08c89dd4706446c7c8046b89680685373f",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "7f18d5b67cd21bcf6dcf1c5797cf551fb7f23af9e98a0a24a36ae7257d0a4d75"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "23c757304da7dbcb1a517a8439cc72c145499b3a4212099d258f9f9e464a26a6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "fdfcfa2002bfdb68f5f3fe77e8df2ac67b8ff393c5dfdd4bba4f6e0dcfd6031f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "35c2597b7ead114ee297450bd48f0a20ab8ab96e70a9dac377609e35cba89f5f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "5d1c447e84b8c9d1a69f2485c910130001abbf69a5cfcd018b808c752a4acde0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "c17d98504fac48f278c77e74499bdf38da0fada6e47f12b8c15769d1ff06a9fd"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "b66f46824ab6da07736d07ab773697e1ff0761c9b33aeae1e54ee788681b51b3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "711510d9f0b3bae7d3499a55f865224d50d7dbef8ccfd4fbe33849899c610966"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "f79a72600db6d5d40788c7759d230f59d952b38c98f60d73fe4f77c2711b4b5b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "d6785a7a29c0a1d3ce6e6434ae4fd068b0ea0e70591fe20f5427e574e23a3b97"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "06a8c1986113b42d7d8ad6d0635aa60c83a05a84e704337751593eb5022cac21"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "08b3e25eac812a60d04197110fefa464079fc2a9d48ab2373f5cbeb96bee426d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "9f937a3373161b7c672f1ba8fa3d885498ae747f504d3a04bfa8a4ee8cb09e1d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "cb6b300ccc0d96f835b9c1d0f21d2c3a997caeda6324702bb8f6df252ddfe244"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fc80978f39a749817341146eabe53f6205ef06048d6e64aa911c73d659884d30"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5ebdf9587ead2590b005815d16734c36b9e1ba790a2b05997532e0fecc93314b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "38fbc91331ab21a153ba710afee80d3a7750a2a9f76f536c2937be68e982d217"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "332b3f3b32ec36cb67b8efb5867cf685887d93f049eecdb9365a5979931901bf"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f4c1898e1d30a6b1dc0a5f24e9d5ca875427669fb3db7678745936dcc1198567",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "c45444db18bdc311e663290ef083891ee0501afe11526c18033b8002f85ba26b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "fa3adf19f6121207611d32090adac8f0f05e943889f8c4d20af5e53e6fae3b2d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "4860a72381018d6591e245e870826d159c1fe59aeca2312adf81154cc620a917"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "f9ecb675b3889ce0ec239fd35a018a7bdb82b0463918b89cbc4561333e022baf"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "e5b0a92b89449573b20f90081b4e850e7739040d06ee1545c0d1a06f45b549f0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "5b694cd07195cc2a4fa60ffb92f51da74edf7d41df6c7936b4165cb0f9f078bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "f495da08c39bf33c473f25a2488c05adfd7e3dc92d0b836d7ee4af17e4644b22"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "d85e7108a23e17fe719c1223c88e48282c66b440f0fcb9bfe318617ef098d147"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "4d2ab0de9af96f944aa7b9a14040236c8e43d25a3c75125d1222c9f0200ea929"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "59fc1194e6e1cae2daaa5211e75c3008949edf539caa6d07997dd86087878c02"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "72d6fcd90b71a371c2ea13aaf35b256a7f9dbbbc204e8bba3b0b6da1071c85ba"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "8c40d12e7bb42486aeae733142c57513dc74f18a21bd4c5a7eb99a165aa3d1ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "9c594e6034d98e2048224368b7c68a34f3c09e276e0676443876b50dda22abf1"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "36ef4a81c8ab19c15d02c9eb3ca0d66ea325cef6679013efe40cc21e38637041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "9c1c7aaa288007ebd2f875f6a2e0b9e139be2c3d2769ac891c5a3ca059ee0041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "a5ad08ef2c99a3a13d99c013d9ea91ba6325a7239a312f6c36f6de162f905575"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "504c4f2b3722be480505f21e90c657e0fb1bd2183be054e2ab72de60113f40de",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "a04092d3189e793b4a9d5d9280ae820ce2836c1fa2a314d69d000f1fed428fee"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "5810f829f64827be40dc102c84eb90da86a1f7ab2dee59a2974dd2b6057280ab"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "32b0bad94856a8a09383f38d365c0c48a4690c5507bef5b9493fe8bbb7d8ebed"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "4931125f09d6c89b2c3139869b1f01b94bad451cedd296dfb0d26223b68d4d0d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "b5417e80a64bb6948b5ddc0b4396d620df143031acaaf7ed105fef3e9c940dc6"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "875c4f72924a004955fdff0e3c281cad64350cb9b8f5f407beabeb9425a3c231"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "6a7fa2ea4d0406720724b11bc1c9c34929eac64ef29b50ee26ee243aee1bfae1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "0b0aff0918cd501bbedb86c183ca69c84f0fddcb8f60fe8bf2f6551002894e94"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "fdc801df7a94125624670c1bf72bb45b85c6a33f963ff864bbaa8f12e3e0ae8a"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "8f5ee1e0a47cad8d30b99a752083652783eb138a7d16a29709f153b8b3a23f3f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "b838dbfd73e3a6a2ca7130095a308f2fe2dad6bf1d1027f007237430b5a06c24"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "3137bf0b91bd3334f1657e14e454a8b1afe842f7d2d0a1449e625bddba11c2df"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "3040ad58ffdc7f70682550830b67ec1fab9dc265ac1554759c8580a09a6c687c",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "407c87766b37dc3485b3825a9efca0d20f8084d8671fe61acfc265e1e5abdac3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "642cf66a70dc0a60d327e8e290cc7aabfa12b24716a5f615fd922179412f9f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "b7ff53576ed4193a464cb842cb84df66801cf1660b92a2931aca42b50ada8bfa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "f705453b64d1cbbae1661099e8e447a185de939f94d0407c2b942fcf0907bcc4"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "db2e14d54dcf3e9455b489750d4dd7606dd9c41e975f30c44d9fcaef2130e8f9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "45cad2e9dfea14756fa071558a67a1ecbe81f6e4fda253ba33953eb192437fe2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "63853bf6c354eed16bdc991d89bfebd42bd6aa871887bca8c3876faf45460553"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "89e1dc65ca868af3bce6c0c73eb157d9cfce2d2748a3bef2b9b2d6054a59045a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "2fe3d6d121df8aeb4f96c0fb5118d53c675756d0ccb615a8af44a525717016a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "628760995eda638bb712cf64431ddaecfd4b6905433f14269da8db724b409382"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "d0bf951786e21c749941582ac452beaeeed237cbf8d3e5dcee6c09d5029a49bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "6dbaa0e36b7446220f83b50da4e19911104326d0cb51f35188a46c85b5cddf03"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "c1a41a5261b75f0b71ecf5ad829928bac35b7c7a67a491eee7d13f5965ed788c"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61f157a1cbedeea8f214219ffa2f90fe5ac2f3d5b9ce0f4c0fa46e325c54a157",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e085cf609c78b0c0fe900014743119497829e5a6d120d5b54310fe4393dcf67b"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "73b84ffda407d572c90e810ffedbe2d98aba4bf6d184790b78fc4b9c9b306ef5"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "b759d00fcca6316ae9a16d619e31083ae2082d244762f561cc4b4d7448f96015"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "73ba7905776d6af74dec4df8b1537ee4821dd2a749cb63497fa1d4f9d5c7be9d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "7b9d78a70259211cdc9503bb1619cd68784dafdbddd3dd0b438d30a2f7c511e7"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1fb130cbaa8ff2f1338382868f7050c6103ebadaefc9dae92b21dcd3c95f2477",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "e34df2daef40e596732c0796a08514f4ed41812f4c609bf8a70d683126911d52"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f3c664b16958b91957fad0e0c3387d4496ccd27b2520598611ebf3ee3c7f4b"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "93ed5b1658dd42c3623275e89715327a622e2b64cef16820ecfab9378435baeb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "89a7c3b6b41d92ccd10c826898c1a2fa7a87e42813d5d228d210e4cb3a2b2ef4"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "270bc944c4a03c0ec4873dedc68aaf5216620736d6c4e94d4c0e01ce75e879e6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "cb3a5dd2a945ae9b8f73ea9bfe452b0b58fceb0a0c46fec82637d97728ae2e35"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "c2d40c4d0507d71755ffbe7548c54865272f7172eb5497f3498f1ff3fe366944"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "c5478414bc21d3d22782baf85adc57d5cf8db792c0f88cc742130cd1b6ad8c42"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "dfa115195e9fd45cfd4f04e1ee64d4e1b8e080aed21717b79a82a9f7b651ef98",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "13b4f5314cf3797a91b51df01383224a5f94b2dd84479f46df686910e1ddfa7f",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6a893717586f34c0d890b901c89c4f54a1f92abb4fa3e7ad84f74c978cee9928",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "ccceb257820f2ec09e89c00dfb67017f44018f987c314f7abab10b57b71fcb6c",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5285104caa341f9ce197d99d6d57f9a0ef09671e0284e8003697d00e3f2ad991",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              }
            },
            "runtime": {
              "last_published_sync_run_seq": 4,
              "lease_owner_id": null,
              "source_snapshot_completed": true
            },
            "stable_current_counts": {
              "customers": 9,
              "order_items": 18,
              "order_payments": 16,
              "order_reviews": 12,
              "orders": 13,
              "product_category_translation": 5,
              "products": 8,
              "sellers": 4
            },
            "status": "ready",
            "sync_run_id": "sync-00000000000000000004",
            "sync_run_seq": 4
          },
          "name": "rebuild_iceberg_current_gold_and_dbt_parity",
          "status": "PASS"
        }
      ],
      "command": [
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "rebuild-serving",
          "--yes",
          "--run-id",
          "stage_l4_20260805_f0_restored_rebuild_cbba942ffa86",
          "--timeout",
          "5400"
        ],
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "validate-rebuild",
          "--sync-run-seq",
          "4",
          "--sync-run-id",
          "sync-00000000000000000004"
        ]
      ],
      "command_results": [
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "rebuild-serving",
            "--yes",
            "--run-id",
            "stage_l4_20260805_f0_restored_rebuild_cbba942ffa86",
            "--timeout",
            "5400"
          ],
          "duration_seconds": 26.218,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"rebuild-serving\", \"dag_run_id\": \"stage_l4_20260805_f0_restored_rebuild_cbba942ffa86\", \"entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 90, \"iceberg_snapshot_ids\": {\"customers\": 4667963551008397841, \"order_items\": 6104085289137992191, \"order_payments\": 4402592427034762001, \"order_reviews\": 1998650664707823942, \"orders\": 8715658499880008100, \"product_category_translation\": 2493780499513490015, \"products\": 7672100197799865306, \"sellers\": 9125635543796638711}, \"materialized_event_count\": 90, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000004\", \"sync_run_seq\": 4}\n",
          "timed_out": false
        },
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "validate-rebuild",
            "--sync-run-seq",
            "4",
            "--sync-run-id",
            "sync-00000000000000000004"
          ],
          "duration_seconds": 2.016,
          "exit_code": 0,
          "stderr": "",
          "stdout": "14873f0510b69e9\"}]}, \"order_items\": {\"manifest_sha256\": \"9118a9283a524a0cc9ced2e67b2f1e08c89dd4706446c7c8046b89680685373f\", \"row_count\": 18, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"order_item_id\": 1, \"row_hash\": \"7f18d5b67cd21bcf6dcf1c5797cf551fb7f23af9e98a0a24a36ae7257d0a4d75\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"order_item_id\": 1, \"row_hash\": \"23c757304da7dbcb1a517a8439cc72c145499b3a4212099d258f9f9e464a26a6\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"order_item_id\": 1, \"row_hash\": \"fdfcfa2002bfdb68f5f3fe77e8df2ac67b8ff393c5dfdd4bba4f6e0dcfd6031f\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"order_item_id\": 2, \"row_hash\": \"35c2597b7ead114ee297450bd48f0a20ab8ab96e70a9dac377609e35cba89f5f\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"order_item_id\": 1, \"row_hash\": \"5d1c447e84b8c9d1a69f2485c910130001abbf69a5cfcd018b808c752a4acde0\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"order_item_id\": 1, \"row_hash\": \"c17d98504fac48f278c77e74499bdf38da0fada6e47f12b8c15769d1ff06a9fd\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"order_item_id\": 1, \"row_hash\": \"b66f46824ab6da07736d07ab773697e1ff0761c9b33aeae1e54ee788681b51b3\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"order_item_id\": 2, \"row_hash\": \"711510d9f0b3bae7d3499a55f865224d50d7dbef8ccfd4fbe33849899c610966\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"order_item_id\": 1, \"row_hash\": \"f79a72600db6d5d40788c7759d230f59d952b38c98f60d73fe4f77c2711b4b5b\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"order_item_id\": 1, \"row_hash\": \"d6785a7a29c0a1d3ce6e6434ae4fd068b0ea0e70591fe20f5427e574e23a3b97\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"order_item_id\": 1, \"row_hash\": \"06a8c1986113b42d7d8ad6d0635aa60c83a05a84e704337751593eb5022cac21\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"order_item_id\": 2, \"row_hash\": \"08b3e25eac812a60d04197110fefa464079fc2a9d48ab2373f5cbeb96bee426d\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"order_item_id\": 1, \"row_hash\": \"9f937a3373161b7c672f1ba8fa3d885498ae747f504d3a04bfa8a4ee8cb09e1d\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"order_item_id\": 1, \"row_hash\": \"cb6b300ccc0d96f835b9c1d0f21d2c3a997caeda6324702bb8f6df252ddfe244\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"order_item_id\": 1, \"row_hash\": \"fc80978f39a749817341146eabe53f6205ef06048d6e64aa911c73d659884d30\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"order_item_id\": 2, \"row_hash\": \"5ebdf9587ead2590b005815d16734c36b9e1ba790a2b05997532e0fecc93314b\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"order_item_id\": 1, \"row_hash\": \"38fbc91331ab21a153ba710afee80d3a7750a2a9f76f536c2937be68e982d217\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"order_item_id\": 2, \"row_hash\": \"332b3f3b32ec36cb67b8efb5867cf685887d93f049eecdb9365a5979931901bf\"}]}, \"order_payments\": {\"manifest_sha256\": \"f4c1898e1d30a6b1dc0a5f24e9d5ca875427669fb3db7678745936dcc1198567\", \"row_count\": 16, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"payment_sequential\": 1, \"row_hash\": \"c45444db18bdc311e663290ef083891ee0501afe11526c18033b8002f85ba26b\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"payment_sequential\": 1, \"row_hash\": \"fa3adf19f6121207611d32090adac8f0f05e943889f8c4d20af5e53e6fae3b2d\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"payment_sequential\": 1, \"row_hash\": \"4860a72381018d6591e245e870826d159c1fe59aeca2312adf81154cc620a917\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"payment_sequential\": 1, \"row_hash\": \"f9ecb675b3889ce0ec239fd35a018a7bdb82b0463918b89cbc4561333e022baf\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"payment_sequential\": 2, \"row_hash\": \"e5b0a92b89449573b20f90081b4e850e7739040d06ee1545c0d1a06f45b549f0\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"payment_sequential\": 1, \"row_hash\": \"5b694cd07195cc2a4fa60ffb92f51da74edf7d41df6c7936b4165cb0f9f078bb\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"payment_sequential\": 1, \"row_hash\": \"f495da08c39bf33c473f25a2488c05adfd7e3dc92d0b836d7ee4af17e4644b22\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"payment_sequential\": 1, \"row_hash\": \"d85e7108a23e17fe719c1223c88e48282c66b440f0fcb9bfe318617ef098d147\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"payment_sequential\": 1, \"row_hash\": \"4d2ab0de9af96f944aa7b9a14040236c8e43d25a3c75125d1222c9f0200ea929\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"payment_sequential\": 2, \"row_hash\": \"59fc1194e6e1cae2daaa5211e75c3008949edf539caa6d07997dd86087878c02\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"payment_sequential\": 1, \"row_hash\": \"72d6fcd90b71a371c2ea13aaf35b256a7f9dbbbc204e8bba3b0b6da1071c85ba\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"payment_sequential\": 1, \"row_hash\": \"8c40d12e7bb42486aeae733142c57513dc74f18a21bd4c5a7eb99a165aa3d1ab\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"payment_sequential\": 1, \"row_hash\": \"9c594e6034d98e2048224368b7c68a34f3c09e276e0676443876b50dda22abf1\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"payment_sequential\": 1, \"row_hash\": \"36ef4a81c8ab19c15d02c9eb3ca0d66ea325cef6679013efe40cc21e38637041\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"payment_sequential\": 1, \"row_hash\": \"9c1c7aaa288007ebd2f875f6a2e0b9e139be2c3d2769ac891c5a3ca059ee0041\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"payment_sequential\": 2, \"row_hash\": \"a5ad08ef2c99a3a13d99c013d9ea91ba6325a7239a312f6c36f6de162f905575\"}]}, \"order_reviews\": {\"manifest_sha256\": \"504c4f2b3722be480505f21e90c657e0fb1bd2183be054e2ab72de60113f40de\", \"row_count\": 12, \"rows\": [{\"is_deleted\": false, \"review_id\": \"review_001\", \"row_hash\": \"a04092d3189e793b4a9d5d9280ae820ce2836c1fa2a314d69d000f1fed428fee\"}, {\"is_deleted\": false, \"review_id\": \"review_002\", \"row_hash\": \"5810f829f64827be40dc102c84eb90da86a1f7ab2dee59a2974dd2b6057280ab\"}, {\"is_deleted\": false, \"review_id\": \"review_003\", \"row_hash\": \"32b0bad94856a8a09383f38d365c0c48a4690c5507bef5b9493fe8bbb7d8ebed\"}, {\"is_deleted\": false, \"review_id\": \"review_004\", \"row_hash\": \"4931125f09d6c89b2c3139869b1f01b94bad451cedd296dfb0d26223b68d4d0d\"}, {\"is_deleted\": false, \"review_id\": \"review_005\", \"row_hash\": \"b5417e80a64bb6948b5ddc0b4396d620df143031acaaf7ed105fef3e9c940dc6\"}, {\"is_deleted\": false, \"review_id\": \"review_006\", \"row_hash\": \"875c4f72924a004955fdff0e3c281cad64350cb9b8f5f407beabeb9425a3c231\"}, {\"is_deleted\": false, \"review_id\": \"review_007\", \"row_hash\": \"6a7fa2ea4d0406720724b11bc1c9c34929eac64ef29b50ee26ee243aee1bfae1\"}, {\"is_deleted\": false, \"review_id\": \"review_008\", \"row_hash\": \"0b0aff0918cd501bbedb86c183ca69c84f0fddcb8f60fe8bf2f6551002894e94\"}, {\"is_deleted\": false, \"review_id\": \"review_009\", \"row_hash\": \"fdc801df7a94125624670c1bf72bb45b85c6a33f963ff864bbaa8f12e3e0ae8a\"}, {\"is_deleted\": false, \"review_id\": \"review_010\", \"row_hash\": \"8f5ee1e0a47cad8d30b99a752083652783eb138a7d16a29709f153b8b3a23f3f\"}, {\"is_deleted\": false, \"review_id\": \"review_011\", \"row_hash\": \"b838dbfd73e3a6a2ca7130095a308f2fe2dad6bf1d1027f007237430b5a06c24\"}, {\"is_deleted\": false, \"review_id\": \"review_012\", \"row_hash\": \"3137bf0b91bd3334f1657e14e454a8b1afe842f7d2d0a1449e625bddba11c2df\"}]}, \"orders\": {\"manifest_sha256\": \"3040ad58ffdc7f70682550830b67ec1fab9dc265ac1554759c8580a09a6c687c\", \"row_count\": 13, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"row_hash\": \"407c87766b37dc3485b3825a9efca0d20f8084d8671fe61acfc265e1e5abdac3\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"row_hash\": \"642cf66a70dc0a60d327e8e290cc7aabfa12b24716a5f615fd922179412f9f4d\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"row_hash\": \"b7ff53576ed4193a464cb842cb84df66801cf1660b92a2931aca42b50ada8bfa\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"row_hash\": \"f705453b64d1cbbae1661099e8e447a185de939f94d0407c2b942fcf0907bcc4\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"row_hash\": \"db2e14d54dcf3e9455b489750d4dd7606dd9c41e975f30c44d9fcaef2130e8f9\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"row_hash\": \"45cad2e9dfea14756fa071558a67a1ecbe81f6e4fda253ba33953eb192437fe2\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"row_hash\": \"63853bf6c354eed16bdc991d89bfebd42bd6aa871887bca8c3876faf45460553\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"row_hash\": \"89e1dc65ca868af3bce6c0c73eb157d9cfce2d2748a3bef2b9b2d6054a59045a\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"row_hash\": \"2fe3d6d121df8aeb4f96c0fb5118d53c675756d0ccb615a8af44a525717016a0\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"row_hash\": \"628760995eda638bb712cf64431ddaecfd4b6905433f14269da8db724b409382\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"row_hash\": \"d0bf951786e21c749941582ac452beaeeed237cbf8d3e5dcee6c09d5029a49bb\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"row_hash\": \"6dbaa0e36b7446220f83b50da4e19911104326d0cb51f35188a46c85b5cddf03\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"row_hash\": \"c1a41a5261b75f0b71ecf5ad829928bac35b7c7a67a491eee7d13f5965ed788c\"}]}, \"product_category_translation\": {\"manifest_sha256\": \"61f157a1cbedeea8f214219ffa2f90fe5ac2f3d5b9ce0f4c0fa46e325c54a157\", \"row_count\": 5, \"rows\": [{\"is_deleted\": false, \"product_category_name\": \"beleza_saude\", \"row_hash\": \"e085cf609c78b0c0fe900014743119497829e5a6d120d5b54310fe4393dcf67b\"}, {\"is_deleted\": false, \"product_category_name\": \"informatica_acessorios\", \"row_hash\": \"73b84ffda407d572c90e810ffedbe2d98aba4bf6d184790b78fc4b9c9b306ef5\"}, {\"is_deleted\": false, \"product_category_name\": \"moveis_decoracao\", \"row_hash\": \"b759d00fcca6316ae9a16d619e31083ae2082d244762f561cc4b4d7448f96015\"}, {\"is_deleted\": false, \"product_category_name\": \"telefonia\", \"row_hash\": \"73ba7905776d6af74dec4df8b1537ee4821dd2a749cb63497fa1d4f9d5c7be9d\"}, {\"is_deleted\": false, \"product_category_name\": \"utilidades_domesticas\", \"row_hash\": \"7b9d78a70259211cdc9503bb1619cd68784dafdbddd3dd0b438d30a2f7c511e7\"}]}, \"products\": {\"manifest_sha256\": \"1fb130cbaa8ff2f1338382868f7050c6103ebadaefc9dae92b21dcd3c95f2477\", \"row_count\": 8, \"rows\": [{\"is_deleted\": false, \"product_id\": \"product_001\", \"row_hash\": \"e34df2daef40e596732c0796a08514f4ed41812f4c609bf8a70d683126911d52\"}, {\"is_deleted\": false, \"product_id\": \"product_002\", \"row_hash\": \"e2f3c664b16958b91957fad0e0c3387d4496ccd27b2520598611ebf3ee3c7f4b\"}, {\"is_deleted\": false, \"product_id\": \"product_003\", \"row_hash\": \"93ed5b1658dd42c3623275e89715327a622e2b64cef16820ecfab9378435baeb\"}, {\"is_deleted\": false, \"product_id\": \"product_004\", \"row_hash\": \"89a7c3b6b41d92ccd10c826898c1a2fa7a87e42813d5d228d210e4cb3a2b2ef4\"}, {\"is_deleted\": false, \"product_id\": \"product_005\", \"row_hash\": \"270bc944c4a03c0ec4873dedc68aaf5216620736d6c4e94d4c0e01ce75e879e6\"}, {\"is_deleted\": false, \"product_id\": \"product_006\", \"row_hash\": \"cb3a5dd2a945ae9b8f73ea9bfe452b0b58fceb0a0c46fec82637d97728ae2e35\"}, {\"is_deleted\": false, \"product_id\": \"product_007\", \"row_hash\": \"c2d40c4d0507d71755ffbe7548c54865272f7172eb5497f3498f1ff3fe366944\"}, {\"is_deleted\": false, \"product_id\": \"product_008\", \"row_hash\": \"c5478414bc21d3d22782baf85adc57d5cf8db792c0f88cc742130cd1b6ad8c42\"}]}, \"sellers\": {\"manifest_sha256\": \"dfa115195e9fd45cfd4f04e1ee64d4e1b8e080aed21717b79a82a9f7b651ef98\", \"row_count\": 4, \"rows\": [{\"is_deleted\": false, \"row_hash\": \"13b4f5314cf3797a91b51df01383224a5f94b2dd84479f46df686910e1ddfa7f\", \"seller_id\": \"seller_001\"}, {\"is_deleted\": false, \"row_hash\": \"6a893717586f34c0d890b901c89c4f54a1f92abb4fa3e7ad84f74c978cee9928\", \"seller_id\": \"seller_002\"}, {\"is_deleted\": false, \"row_hash\": \"ccceb257820f2ec09e89c00dfb67017f44018f987c314f7abab10b57b71fcb6c\", \"seller_id\": \"seller_003\"}, {\"is_deleted\": false, \"row_hash\": \"5285104caa341f9ce197d99d6d57f9a0ef09671e0284e8003697d00e3f2ad991\", \"seller_id\": \"seller_004\"}]}}}, \"runtime\": {\"last_published_sync_run_seq\": 4, \"lease_owner_id\": null, \"source_snapshot_completed\": true}, \"stable_current_counts\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"status\": \"ready\", \"sync_run_id\": \"sync-00000000000000000004\", \"sync_run_seq\": 4}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 28.221,
      "gate": "09-rebuild",
      "status": "PASS",
      "timestamp": "2026-08-04T22:59:37.342831+00:00"
    },
    "10-final": {
      "assertions": [
        {
          "detail": {
            "candidate_current_counts": {
              "customers": 9,
              "order_items": 18,
              "order_payments": 16,
              "order_reviews": 12,
              "orders": 13,
              "product_category_translation": 5,
              "products": 8,
              "sellers": 4
            },
            "command": "validate-rebuild",
            "dbt": {
              "command": [
                "build",
                "--project-dir",
                "/opt/airflow/project/dbt/olist_clickhouse",
                "--profiles-dir",
                "/opt/airflow/project/dbt/olist_clickhouse",
                "--selector",
                "serving_candidate",
                "--vars",
                "{\"sync_run_seq\": 4, \"sync_run_id\": \"sync-00000000000000000004\"}"
              ],
              "result_count": 75,
              "status_counts": {
                "pass": 59,
                "success": 16
              }
            },
            "expected_event_count": 90,
            "gold_views": {
              "dim_customer_scd2": {
                "candidate": 8,
                "stable": 8
              },
              "dim_date": {
                "candidate": 46,
                "stable": 46
              },
              "dim_order_status": {
                "candidate": 2,
                "stable": 2
              },
              "dim_product_scd2": {
                "candidate": 8,
                "stable": 8
              },
              "dim_seller": {
                "candidate": 4,
                "stable": 4
              },
              "fact_order_items": {
                "candidate": 18,
                "stable": 18
              },
              "mart_daily_revenue": {
                "candidate": 13,
                "stable": 13
              },
              "mart_monthly_arpu": {
                "candidate": 7,
                "stable": 7
              }
            },
            "iceberg_current_counts": {
              "customers": 9,
              "order_items": 18,
              "order_payments": 16,
              "order_reviews": 12,
              "orders": 13,
              "product_category_translation": 5,
              "products": 8,
              "sellers": 4
            },
            "iceberg_snapshot_ids": {
              "customers": 4667963551008397841,
              "order_items": 6104085289137992191,
              "order_payments": 4402592427034762001,
              "order_reviews": 1998650664707823942,
              "orders": 8715658499880008100,
              "product_category_translation": 2493780499513490015,
              "products": 7672100197799865306,
              "sellers": 9125635543796638711
            },
            "materialized_event_count": 90,
            "row_manifests": {
              "candidate_physical": {
                "customers": {
                  "manifest_sha256": "bc9c042a90199accd2c8b6545ee4c1b3015b556dfbffd8a54a21c3ed4a48d4c1",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "c8215415f5236d27f71cd836daaefda158598e9f2fed41d6d62e640d9945effe"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "64d9c2cdd88f51d85d3fe7445154ac99ef6735fb56262de8f7d3214c05de44f9"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "e553baa7a4a5579b541aa1b8fd500391074b9a999b41deac0142880b71929018"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "9c28bbf645cbfa9c1db42a585757632205ba7b54473a522b2faf68b7816cc9b3"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "cea8b62418507e021e8a8e01485bb769015d0c81525db8a106173b9dda09472b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "977c38faff0ead04b7517382031c765a03476b7c12f9d2a471b8aedfb098afef"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "9f9040e360dca3eed6784be4dee5482e1af319b3dd69ba43dbe4627227a2690a"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "9d46cb8a8302603ac19146611affc3b2f6a8e28547f328544d19172ba9d52bd5"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "665d49e1871c07b02542feb2d4dec0a60fe5daaeb41751a5f14873f0510b69e9"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "9118a9283a524a0cc9ced2e67b2f1e08c89dd4706446c7c8046b89680685373f",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "7f18d5b67cd21bcf6dcf1c5797cf551fb7f23af9e98a0a24a36ae7257d0a4d75"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "23c757304da7dbcb1a517a8439cc72c145499b3a4212099d258f9f9e464a26a6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "fdfcfa2002bfdb68f5f3fe77e8df2ac67b8ff393c5dfdd4bba4f6e0dcfd6031f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "35c2597b7ead114ee297450bd48f0a20ab8ab96e70a9dac377609e35cba89f5f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "5d1c447e84b8c9d1a69f2485c910130001abbf69a5cfcd018b808c752a4acde0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "c17d98504fac48f278c77e74499bdf38da0fada6e47f12b8c15769d1ff06a9fd"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "b66f46824ab6da07736d07ab773697e1ff0761c9b33aeae1e54ee788681b51b3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "711510d9f0b3bae7d3499a55f865224d50d7dbef8ccfd4fbe33849899c610966"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "f79a72600db6d5d40788c7759d230f59d952b38c98f60d73fe4f77c2711b4b5b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "d6785a7a29c0a1d3ce6e6434ae4fd068b0ea0e70591fe20f5427e574e23a3b97"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "06a8c1986113b42d7d8ad6d0635aa60c83a05a84e704337751593eb5022cac21"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "08b3e25eac812a60d04197110fefa464079fc2a9d48ab2373f5cbeb96bee426d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "9f937a3373161b7c672f1ba8fa3d885498ae747f504d3a04bfa8a4ee8cb09e1d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "cb6b300ccc0d96f835b9c1d0f21d2c3a997caeda6324702bb8f6df252ddfe244"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fc80978f39a749817341146eabe53f6205ef06048d6e64aa911c73d659884d30"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5ebdf9587ead2590b005815d16734c36b9e1ba790a2b05997532e0fecc93314b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "38fbc91331ab21a153ba710afee80d3a7750a2a9f76f536c2937be68e982d217"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "332b3f3b32ec36cb67b8efb5867cf685887d93f049eecdb9365a5979931901bf"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f4c1898e1d30a6b1dc0a5f24e9d5ca875427669fb3db7678745936dcc1198567",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "c45444db18bdc311e663290ef083891ee0501afe11526c18033b8002f85ba26b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "fa3adf19f6121207611d32090adac8f0f05e943889f8c4d20af5e53e6fae3b2d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "4860a72381018d6591e245e870826d159c1fe59aeca2312adf81154cc620a917"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "f9ecb675b3889ce0ec239fd35a018a7bdb82b0463918b89cbc4561333e022baf"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "e5b0a92b89449573b20f90081b4e850e7739040d06ee1545c0d1a06f45b549f0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "5b694cd07195cc2a4fa60ffb92f51da74edf7d41df6c7936b4165cb0f9f078bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "f495da08c39bf33c473f25a2488c05adfd7e3dc92d0b836d7ee4af17e4644b22"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "d85e7108a23e17fe719c1223c88e48282c66b440f0fcb9bfe318617ef098d147"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "4d2ab0de9af96f944aa7b9a14040236c8e43d25a3c75125d1222c9f0200ea929"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "59fc1194e6e1cae2daaa5211e75c3008949edf539caa6d07997dd86087878c02"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "72d6fcd90b71a371c2ea13aaf35b256a7f9dbbbc204e8bba3b0b6da1071c85ba"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "8c40d12e7bb42486aeae733142c57513dc74f18a21bd4c5a7eb99a165aa3d1ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "9c594e6034d98e2048224368b7c68a34f3c09e276e0676443876b50dda22abf1"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "36ef4a81c8ab19c15d02c9eb3ca0d66ea325cef6679013efe40cc21e38637041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "9c1c7aaa288007ebd2f875f6a2e0b9e139be2c3d2769ac891c5a3ca059ee0041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "a5ad08ef2c99a3a13d99c013d9ea91ba6325a7239a312f6c36f6de162f905575"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "7f8bd7ceedd836351e7a2c8d030874dd7c340899954552deb522ea1fcbde182a",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "a04092d3189e793b4a9d5d9280ae820ce2836c1fa2a314d69d000f1fed428fee"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "5810f829f64827be40dc102c84eb90da86a1f7ab2dee59a2974dd2b6057280ab"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "32b0bad94856a8a09383f38d365c0c48a4690c5507bef5b9493fe8bbb7d8ebed"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "4931125f09d6c89b2c3139869b1f01b94bad451cedd296dfb0d26223b68d4d0d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "b5417e80a64bb6948b5ddc0b4396d620df143031acaaf7ed105fef3e9c940dc6"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "875c4f72924a004955fdff0e3c281cad64350cb9b8f5f407beabeb9425a3c231"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "6a7fa2ea4d0406720724b11bc1c9c34929eac64ef29b50ee26ee243aee1bfae1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "0b0aff0918cd501bbedb86c183ca69c84f0fddcb8f60fe8bf2f6551002894e94"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "fdc801df7a94125624670c1bf72bb45b85c6a33f963ff864bbaa8f12e3e0ae8a"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "8f5ee1e0a47cad8d30b99a752083652783eb138a7d16a29709f153b8b3a23f3f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "b838dbfd73e3a6a2ca7130095a308f2fe2dad6bf1d1027f007237430b5a06c24"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "3137bf0b91bd3334f1657e14e454a8b1afe842f7d2d0a1449e625bddba11c2df"
                    },
                    {
                      "is_deleted": true,
                      "review_id": "wave2_review_001",
                      "row_hash": "3254b0fe5706ca8e888cd955049960ef953c10460c412dcfb538807f72bba6bc"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "3040ad58ffdc7f70682550830b67ec1fab9dc265ac1554759c8580a09a6c687c",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "407c87766b37dc3485b3825a9efca0d20f8084d8671fe61acfc265e1e5abdac3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "642cf66a70dc0a60d327e8e290cc7aabfa12b24716a5f615fd922179412f9f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "b7ff53576ed4193a464cb842cb84df66801cf1660b92a2931aca42b50ada8bfa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "f705453b64d1cbbae1661099e8e447a185de939f94d0407c2b942fcf0907bcc4"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "db2e14d54dcf3e9455b489750d4dd7606dd9c41e975f30c44d9fcaef2130e8f9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "45cad2e9dfea14756fa071558a67a1ecbe81f6e4fda253ba33953eb192437fe2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "63853bf6c354eed16bdc991d89bfebd42bd6aa871887bca8c3876faf45460553"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "89e1dc65ca868af3bce6c0c73eb157d9cfce2d2748a3bef2b9b2d6054a59045a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "2fe3d6d121df8aeb4f96c0fb5118d53c675756d0ccb615a8af44a525717016a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "628760995eda638bb712cf64431ddaecfd4b6905433f14269da8db724b409382"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "d0bf951786e21c749941582ac452beaeeed237cbf8d3e5dcee6c09d5029a49bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "6dbaa0e36b7446220f83b50da4e19911104326d0cb51f35188a46c85b5cddf03"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "c1a41a5261b75f0b71ecf5ad829928bac35b7c7a67a491eee7d13f5965ed788c"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61f157a1cbedeea8f214219ffa2f90fe5ac2f3d5b9ce0f4c0fa46e325c54a157",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e085cf609c78b0c0fe900014743119497829e5a6d120d5b54310fe4393dcf67b"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "73b84ffda407d572c90e810ffedbe2d98aba4bf6d184790b78fc4b9c9b306ef5"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "b759d00fcca6316ae9a16d619e31083ae2082d244762f561cc4b4d7448f96015"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "73ba7905776d6af74dec4df8b1537ee4821dd2a749cb63497fa1d4f9d5c7be9d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "7b9d78a70259211cdc9503bb1619cd68784dafdbddd3dd0b438d30a2f7c511e7"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1fb130cbaa8ff2f1338382868f7050c6103ebadaefc9dae92b21dcd3c95f2477",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "e34df2daef40e596732c0796a08514f4ed41812f4c609bf8a70d683126911d52"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f3c664b16958b91957fad0e0c3387d4496ccd27b2520598611ebf3ee3c7f4b"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "93ed5b1658dd42c3623275e89715327a622e2b64cef16820ecfab9378435baeb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "89a7c3b6b41d92ccd10c826898c1a2fa7a87e42813d5d228d210e4cb3a2b2ef4"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "270bc944c4a03c0ec4873dedc68aaf5216620736d6c4e94d4c0e01ce75e879e6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "cb3a5dd2a945ae9b8f73ea9bfe452b0b58fceb0a0c46fec82637d97728ae2e35"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "c2d40c4d0507d71755ffbe7548c54865272f7172eb5497f3498f1ff3fe366944"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "c5478414bc21d3d22782baf85adc57d5cf8db792c0f88cc742130cd1b6ad8c42"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "dfa115195e9fd45cfd4f04e1ee64d4e1b8e080aed21717b79a82a9f7b651ef98",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "13b4f5314cf3797a91b51df01383224a5f94b2dd84479f46df686910e1ddfa7f",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6a893717586f34c0d890b901c89c4f54a1f92abb4fa3e7ad84f74c978cee9928",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "ccceb257820f2ec09e89c00dfb67017f44018f987c314f7abab10b57b71fcb6c",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5285104caa341f9ce197d99d6d57f9a0ef09671e0284e8003697d00e3f2ad991",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "candidate_visible": {
                "customers": {
                  "manifest_sha256": "bc9c042a90199accd2c8b6545ee4c1b3015b556dfbffd8a54a21c3ed4a48d4c1",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "c8215415f5236d27f71cd836daaefda158598e9f2fed41d6d62e640d9945effe"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "64d9c2cdd88f51d85d3fe7445154ac99ef6735fb56262de8f7d3214c05de44f9"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "e553baa7a4a5579b541aa1b8fd500391074b9a999b41deac0142880b71929018"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "9c28bbf645cbfa9c1db42a585757632205ba7b54473a522b2faf68b7816cc9b3"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "cea8b62418507e021e8a8e01485bb769015d0c81525db8a106173b9dda09472b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "977c38faff0ead04b7517382031c765a03476b7c12f9d2a471b8aedfb098afef"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "9f9040e360dca3eed6784be4dee5482e1af319b3dd69ba43dbe4627227a2690a"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "9d46cb8a8302603ac19146611affc3b2f6a8e28547f328544d19172ba9d52bd5"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "665d49e1871c07b02542feb2d4dec0a60fe5daaeb41751a5f14873f0510b69e9"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "9118a9283a524a0cc9ced2e67b2f1e08c89dd4706446c7c8046b89680685373f",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "7f18d5b67cd21bcf6dcf1c5797cf551fb7f23af9e98a0a24a36ae7257d0a4d75"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "23c757304da7dbcb1a517a8439cc72c145499b3a4212099d258f9f9e464a26a6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "fdfcfa2002bfdb68f5f3fe77e8df2ac67b8ff393c5dfdd4bba4f6e0dcfd6031f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "35c2597b7ead114ee297450bd48f0a20ab8ab96e70a9dac377609e35cba89f5f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "5d1c447e84b8c9d1a69f2485c910130001abbf69a5cfcd018b808c752a4acde0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "c17d98504fac48f278c77e74499bdf38da0fada6e47f12b8c15769d1ff06a9fd"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "b66f46824ab6da07736d07ab773697e1ff0761c9b33aeae1e54ee788681b51b3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "711510d9f0b3bae7d3499a55f865224d50d7dbef8ccfd4fbe33849899c610966"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "f79a72600db6d5d40788c7759d230f59d952b38c98f60d73fe4f77c2711b4b5b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "d6785a7a29c0a1d3ce6e6434ae4fd068b0ea0e70591fe20f5427e574e23a3b97"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "06a8c1986113b42d7d8ad6d0635aa60c83a05a84e704337751593eb5022cac21"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "08b3e25eac812a60d04197110fefa464079fc2a9d48ab2373f5cbeb96bee426d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "9f937a3373161b7c672f1ba8fa3d885498ae747f504d3a04bfa8a4ee8cb09e1d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "cb6b300ccc0d96f835b9c1d0f21d2c3a997caeda6324702bb8f6df252ddfe244"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fc80978f39a749817341146eabe53f6205ef06048d6e64aa911c73d659884d30"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5ebdf9587ead2590b005815d16734c36b9e1ba790a2b05997532e0fecc93314b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "38fbc91331ab21a153ba710afee80d3a7750a2a9f76f536c2937be68e982d217"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "332b3f3b32ec36cb67b8efb5867cf685887d93f049eecdb9365a5979931901bf"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f4c1898e1d30a6b1dc0a5f24e9d5ca875427669fb3db7678745936dcc1198567",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "c45444db18bdc311e663290ef083891ee0501afe11526c18033b8002f85ba26b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "fa3adf19f6121207611d32090adac8f0f05e943889f8c4d20af5e53e6fae3b2d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "4860a72381018d6591e245e870826d159c1fe59aeca2312adf81154cc620a917"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "f9ecb675b3889ce0ec239fd35a018a7bdb82b0463918b89cbc4561333e022baf"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "e5b0a92b89449573b20f90081b4e850e7739040d06ee1545c0d1a06f45b549f0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "5b694cd07195cc2a4fa60ffb92f51da74edf7d41df6c7936b4165cb0f9f078bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "f495da08c39bf33c473f25a2488c05adfd7e3dc92d0b836d7ee4af17e4644b22"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "d85e7108a23e17fe719c1223c88e48282c66b440f0fcb9bfe318617ef098d147"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "4d2ab0de9af96f944aa7b9a14040236c8e43d25a3c75125d1222c9f0200ea929"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "59fc1194e6e1cae2daaa5211e75c3008949edf539caa6d07997dd86087878c02"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "72d6fcd90b71a371c2ea13aaf35b256a7f9dbbbc204e8bba3b0b6da1071c85ba"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "8c40d12e7bb42486aeae733142c57513dc74f18a21bd4c5a7eb99a165aa3d1ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "9c594e6034d98e2048224368b7c68a34f3c09e276e0676443876b50dda22abf1"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "36ef4a81c8ab19c15d02c9eb3ca0d66ea325cef6679013efe40cc21e38637041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "9c1c7aaa288007ebd2f875f6a2e0b9e139be2c3d2769ac891c5a3ca059ee0041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "a5ad08ef2c99a3a13d99c013d9ea91ba6325a7239a312f6c36f6de162f905575"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "504c4f2b3722be480505f21e90c657e0fb1bd2183be054e2ab72de60113f40de",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "a04092d3189e793b4a9d5d9280ae820ce2836c1fa2a314d69d000f1fed428fee"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "5810f829f64827be40dc102c84eb90da86a1f7ab2dee59a2974dd2b6057280ab"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "32b0bad94856a8a09383f38d365c0c48a4690c5507bef5b9493fe8bbb7d8ebed"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "4931125f09d6c89b2c3139869b1f01b94bad451cedd296dfb0d26223b68d4d0d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "b5417e80a64bb6948b5ddc0b4396d620df143031acaaf7ed105fef3e9c940dc6"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "875c4f72924a004955fdff0e3c281cad64350cb9b8f5f407beabeb9425a3c231"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "6a7fa2ea4d0406720724b11bc1c9c34929eac64ef29b50ee26ee243aee1bfae1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "0b0aff0918cd501bbedb86c183ca69c84f0fddcb8f60fe8bf2f6551002894e94"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "fdc801df7a94125624670c1bf72bb45b85c6a33f963ff864bbaa8f12e3e0ae8a"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "8f5ee1e0a47cad8d30b99a752083652783eb138a7d16a29709f153b8b3a23f3f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "b838dbfd73e3a6a2ca7130095a308f2fe2dad6bf1d1027f007237430b5a06c24"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "3137bf0b91bd3334f1657e14e454a8b1afe842f7d2d0a1449e625bddba11c2df"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "3040ad58ffdc7f70682550830b67ec1fab9dc265ac1554759c8580a09a6c687c",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "407c87766b37dc3485b3825a9efca0d20f8084d8671fe61acfc265e1e5abdac3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "642cf66a70dc0a60d327e8e290cc7aabfa12b24716a5f615fd922179412f9f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "b7ff53576ed4193a464cb842cb84df66801cf1660b92a2931aca42b50ada8bfa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "f705453b64d1cbbae1661099e8e447a185de939f94d0407c2b942fcf0907bcc4"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "db2e14d54dcf3e9455b489750d4dd7606dd9c41e975f30c44d9fcaef2130e8f9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "45cad2e9dfea14756fa071558a67a1ecbe81f6e4fda253ba33953eb192437fe2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "63853bf6c354eed16bdc991d89bfebd42bd6aa871887bca8c3876faf45460553"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "89e1dc65ca868af3bce6c0c73eb157d9cfce2d2748a3bef2b9b2d6054a59045a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "2fe3d6d121df8aeb4f96c0fb5118d53c675756d0ccb615a8af44a525717016a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "628760995eda638bb712cf64431ddaecfd4b6905433f14269da8db724b409382"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "d0bf951786e21c749941582ac452beaeeed237cbf8d3e5dcee6c09d5029a49bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "6dbaa0e36b7446220f83b50da4e19911104326d0cb51f35188a46c85b5cddf03"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "c1a41a5261b75f0b71ecf5ad829928bac35b7c7a67a491eee7d13f5965ed788c"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61f157a1cbedeea8f214219ffa2f90fe5ac2f3d5b9ce0f4c0fa46e325c54a157",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e085cf609c78b0c0fe900014743119497829e5a6d120d5b54310fe4393dcf67b"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "73b84ffda407d572c90e810ffedbe2d98aba4bf6d184790b78fc4b9c9b306ef5"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "b759d00fcca6316ae9a16d619e31083ae2082d244762f561cc4b4d7448f96015"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "73ba7905776d6af74dec4df8b1537ee4821dd2a749cb63497fa1d4f9d5c7be9d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "7b9d78a70259211cdc9503bb1619cd68784dafdbddd3dd0b438d30a2f7c511e7"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1fb130cbaa8ff2f1338382868f7050c6103ebadaefc9dae92b21dcd3c95f2477",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "e34df2daef40e596732c0796a08514f4ed41812f4c609bf8a70d683126911d52"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f3c664b16958b91957fad0e0c3387d4496ccd27b2520598611ebf3ee3c7f4b"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "93ed5b1658dd42c3623275e89715327a622e2b64cef16820ecfab9378435baeb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "89a7c3b6b41d92ccd10c826898c1a2fa7a87e42813d5d228d210e4cb3a2b2ef4"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "270bc944c4a03c0ec4873dedc68aaf5216620736d6c4e94d4c0e01ce75e879e6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "cb3a5dd2a945ae9b8f73ea9bfe452b0b58fceb0a0c46fec82637d97728ae2e35"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "c2d40c4d0507d71755ffbe7548c54865272f7172eb5497f3498f1ff3fe366944"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "c5478414bc21d3d22782baf85adc57d5cf8db792c0f88cc742130cd1b6ad8c42"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "dfa115195e9fd45cfd4f04e1ee64d4e1b8e080aed21717b79a82a9f7b651ef98",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "13b4f5314cf3797a91b51df01383224a5f94b2dd84479f46df686910e1ddfa7f",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6a893717586f34c0d890b901c89c4f54a1f92abb4fa3e7ad84f74c978cee9928",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "ccceb257820f2ec09e89c00dfb67017f44018f987c314f7abab10b57b71fcb6c",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5285104caa341f9ce197d99d6d57f9a0ef09671e0284e8003697d00e3f2ad991",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "iceberg_physical": {
                "customers": {
                  "manifest_sha256": "bc9c042a90199accd2c8b6545ee4c1b3015b556dfbffd8a54a21c3ed4a48d4c1",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "c8215415f5236d27f71cd836daaefda158598e9f2fed41d6d62e640d9945effe"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "64d9c2cdd88f51d85d3fe7445154ac99ef6735fb56262de8f7d3214c05de44f9"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "e553baa7a4a5579b541aa1b8fd500391074b9a999b41deac0142880b71929018"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "9c28bbf645cbfa9c1db42a585757632205ba7b54473a522b2faf68b7816cc9b3"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "cea8b62418507e021e8a8e01485bb769015d0c81525db8a106173b9dda09472b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "977c38faff0ead04b7517382031c765a03476b7c12f9d2a471b8aedfb098afef"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "9f9040e360dca3eed6784be4dee5482e1af319b3dd69ba43dbe4627227a2690a"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "9d46cb8a8302603ac19146611affc3b2f6a8e28547f328544d19172ba9d52bd5"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "665d49e1871c07b02542feb2d4dec0a60fe5daaeb41751a5f14873f0510b69e9"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "9118a9283a524a0cc9ced2e67b2f1e08c89dd4706446c7c8046b89680685373f",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "7f18d5b67cd21bcf6dcf1c5797cf551fb7f23af9e98a0a24a36ae7257d0a4d75"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "23c757304da7dbcb1a517a8439cc72c145499b3a4212099d258f9f9e464a26a6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "fdfcfa2002bfdb68f5f3fe77e8df2ac67b8ff393c5dfdd4bba4f6e0dcfd6031f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "35c2597b7ead114ee297450bd48f0a20ab8ab96e70a9dac377609e35cba89f5f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "5d1c447e84b8c9d1a69f2485c910130001abbf69a5cfcd018b808c752a4acde0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "c17d98504fac48f278c77e74499bdf38da0fada6e47f12b8c15769d1ff06a9fd"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "b66f46824ab6da07736d07ab773697e1ff0761c9b33aeae1e54ee788681b51b3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "711510d9f0b3bae7d3499a55f865224d50d7dbef8ccfd4fbe33849899c610966"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "f79a72600db6d5d40788c7759d230f59d952b38c98f60d73fe4f77c2711b4b5b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "d6785a7a29c0a1d3ce6e6434ae4fd068b0ea0e70591fe20f5427e574e23a3b97"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "06a8c1986113b42d7d8ad6d0635aa60c83a05a84e704337751593eb5022cac21"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "08b3e25eac812a60d04197110fefa464079fc2a9d48ab2373f5cbeb96bee426d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "9f937a3373161b7c672f1ba8fa3d885498ae747f504d3a04bfa8a4ee8cb09e1d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "cb6b300ccc0d96f835b9c1d0f21d2c3a997caeda6324702bb8f6df252ddfe244"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fc80978f39a749817341146eabe53f6205ef06048d6e64aa911c73d659884d30"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5ebdf9587ead2590b005815d16734c36b9e1ba790a2b05997532e0fecc93314b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "38fbc91331ab21a153ba710afee80d3a7750a2a9f76f536c2937be68e982d217"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "332b3f3b32ec36cb67b8efb5867cf685887d93f049eecdb9365a5979931901bf"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f4c1898e1d30a6b1dc0a5f24e9d5ca875427669fb3db7678745936dcc1198567",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "c45444db18bdc311e663290ef083891ee0501afe11526c18033b8002f85ba26b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "fa3adf19f6121207611d32090adac8f0f05e943889f8c4d20af5e53e6fae3b2d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "4860a72381018d6591e245e870826d159c1fe59aeca2312adf81154cc620a917"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "f9ecb675b3889ce0ec239fd35a018a7bdb82b0463918b89cbc4561333e022baf"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "e5b0a92b89449573b20f90081b4e850e7739040d06ee1545c0d1a06f45b549f0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "5b694cd07195cc2a4fa60ffb92f51da74edf7d41df6c7936b4165cb0f9f078bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "f495da08c39bf33c473f25a2488c05adfd7e3dc92d0b836d7ee4af17e4644b22"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "d85e7108a23e17fe719c1223c88e48282c66b440f0fcb9bfe318617ef098d147"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "4d2ab0de9af96f944aa7b9a14040236c8e43d25a3c75125d1222c9f0200ea929"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "59fc1194e6e1cae2daaa5211e75c3008949edf539caa6d07997dd86087878c02"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "72d6fcd90b71a371c2ea13aaf35b256a7f9dbbbc204e8bba3b0b6da1071c85ba"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "8c40d12e7bb42486aeae733142c57513dc74f18a21bd4c5a7eb99a165aa3d1ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "9c594e6034d98e2048224368b7c68a34f3c09e276e0676443876b50dda22abf1"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "36ef4a81c8ab19c15d02c9eb3ca0d66ea325cef6679013efe40cc21e38637041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "9c1c7aaa288007ebd2f875f6a2e0b9e139be2c3d2769ac891c5a3ca059ee0041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "a5ad08ef2c99a3a13d99c013d9ea91ba6325a7239a312f6c36f6de162f905575"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "7f8bd7ceedd836351e7a2c8d030874dd7c340899954552deb522ea1fcbde182a",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "a04092d3189e793b4a9d5d9280ae820ce2836c1fa2a314d69d000f1fed428fee"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "5810f829f64827be40dc102c84eb90da86a1f7ab2dee59a2974dd2b6057280ab"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "32b0bad94856a8a09383f38d365c0c48a4690c5507bef5b9493fe8bbb7d8ebed"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "4931125f09d6c89b2c3139869b1f01b94bad451cedd296dfb0d26223b68d4d0d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "b5417e80a64bb6948b5ddc0b4396d620df143031acaaf7ed105fef3e9c940dc6"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "875c4f72924a004955fdff0e3c281cad64350cb9b8f5f407beabeb9425a3c231"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "6a7fa2ea4d0406720724b11bc1c9c34929eac64ef29b50ee26ee243aee1bfae1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "0b0aff0918cd501bbedb86c183ca69c84f0fddcb8f60fe8bf2f6551002894e94"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "fdc801df7a94125624670c1bf72bb45b85c6a33f963ff864bbaa8f12e3e0ae8a"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "8f5ee1e0a47cad8d30b99a752083652783eb138a7d16a29709f153b8b3a23f3f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "b838dbfd73e3a6a2ca7130095a308f2fe2dad6bf1d1027f007237430b5a06c24"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "3137bf0b91bd3334f1657e14e454a8b1afe842f7d2d0a1449e625bddba11c2df"
                    },
                    {
                      "is_deleted": true,
                      "review_id": "wave2_review_001",
                      "row_hash": "3254b0fe5706ca8e888cd955049960ef953c10460c412dcfb538807f72bba6bc"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "3040ad58ffdc7f70682550830b67ec1fab9dc265ac1554759c8580a09a6c687c",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "407c87766b37dc3485b3825a9efca0d20f8084d8671fe61acfc265e1e5abdac3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "642cf66a70dc0a60d327e8e290cc7aabfa12b24716a5f615fd922179412f9f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "b7ff53576ed4193a464cb842cb84df66801cf1660b92a2931aca42b50ada8bfa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "f705453b64d1cbbae1661099e8e447a185de939f94d0407c2b942fcf0907bcc4"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "db2e14d54dcf3e9455b489750d4dd7606dd9c41e975f30c44d9fcaef2130e8f9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "45cad2e9dfea14756fa071558a67a1ecbe81f6e4fda253ba33953eb192437fe2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "63853bf6c354eed16bdc991d89bfebd42bd6aa871887bca8c3876faf45460553"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "89e1dc65ca868af3bce6c0c73eb157d9cfce2d2748a3bef2b9b2d6054a59045a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "2fe3d6d121df8aeb4f96c0fb5118d53c675756d0ccb615a8af44a525717016a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "628760995eda638bb712cf64431ddaecfd4b6905433f14269da8db724b409382"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "d0bf951786e21c749941582ac452beaeeed237cbf8d3e5dcee6c09d5029a49bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "6dbaa0e36b7446220f83b50da4e19911104326d0cb51f35188a46c85b5cddf03"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "c1a41a5261b75f0b71ecf5ad829928bac35b7c7a67a491eee7d13f5965ed788c"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61f157a1cbedeea8f214219ffa2f90fe5ac2f3d5b9ce0f4c0fa46e325c54a157",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e085cf609c78b0c0fe900014743119497829e5a6d120d5b54310fe4393dcf67b"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "73b84ffda407d572c90e810ffedbe2d98aba4bf6d184790b78fc4b9c9b306ef5"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "b759d00fcca6316ae9a16d619e31083ae2082d244762f561cc4b4d7448f96015"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "73ba7905776d6af74dec4df8b1537ee4821dd2a749cb63497fa1d4f9d5c7be9d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "7b9d78a70259211cdc9503bb1619cd68784dafdbddd3dd0b438d30a2f7c511e7"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1fb130cbaa8ff2f1338382868f7050c6103ebadaefc9dae92b21dcd3c95f2477",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "e34df2daef40e596732c0796a08514f4ed41812f4c609bf8a70d683126911d52"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f3c664b16958b91957fad0e0c3387d4496ccd27b2520598611ebf3ee3c7f4b"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "93ed5b1658dd42c3623275e89715327a622e2b64cef16820ecfab9378435baeb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "89a7c3b6b41d92ccd10c826898c1a2fa7a87e42813d5d228d210e4cb3a2b2ef4"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "270bc944c4a03c0ec4873dedc68aaf5216620736d6c4e94d4c0e01ce75e879e6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "cb3a5dd2a945ae9b8f73ea9bfe452b0b58fceb0a0c46fec82637d97728ae2e35"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "c2d40c4d0507d71755ffbe7548c54865272f7172eb5497f3498f1ff3fe366944"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "c5478414bc21d3d22782baf85adc57d5cf8db792c0f88cc742130cd1b6ad8c42"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "dfa115195e9fd45cfd4f04e1ee64d4e1b8e080aed21717b79a82a9f7b651ef98",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "13b4f5314cf3797a91b51df01383224a5f94b2dd84479f46df686910e1ddfa7f",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6a893717586f34c0d890b901c89c4f54a1f92abb4fa3e7ad84f74c978cee9928",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "ccceb257820f2ec09e89c00dfb67017f44018f987c314f7abab10b57b71fcb6c",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5285104caa341f9ce197d99d6d57f9a0ef09671e0284e8003697d00e3f2ad991",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "iceberg_visible": {
                "customers": {
                  "manifest_sha256": "bc9c042a90199accd2c8b6545ee4c1b3015b556dfbffd8a54a21c3ed4a48d4c1",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "c8215415f5236d27f71cd836daaefda158598e9f2fed41d6d62e640d9945effe"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "64d9c2cdd88f51d85d3fe7445154ac99ef6735fb56262de8f7d3214c05de44f9"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "e553baa7a4a5579b541aa1b8fd500391074b9a999b41deac0142880b71929018"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "9c28bbf645cbfa9c1db42a585757632205ba7b54473a522b2faf68b7816cc9b3"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "cea8b62418507e021e8a8e01485bb769015d0c81525db8a106173b9dda09472b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "977c38faff0ead04b7517382031c765a03476b7c12f9d2a471b8aedfb098afef"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "9f9040e360dca3eed6784be4dee5482e1af319b3dd69ba43dbe4627227a2690a"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "9d46cb8a8302603ac19146611affc3b2f6a8e28547f328544d19172ba9d52bd5"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "665d49e1871c07b02542feb2d4dec0a60fe5daaeb41751a5f14873f0510b69e9"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "9118a9283a524a0cc9ced2e67b2f1e08c89dd4706446c7c8046b89680685373f",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "7f18d5b67cd21bcf6dcf1c5797cf551fb7f23af9e98a0a24a36ae7257d0a4d75"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "23c757304da7dbcb1a517a8439cc72c145499b3a4212099d258f9f9e464a26a6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "fdfcfa2002bfdb68f5f3fe77e8df2ac67b8ff393c5dfdd4bba4f6e0dcfd6031f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "35c2597b7ead114ee297450bd48f0a20ab8ab96e70a9dac377609e35cba89f5f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "5d1c447e84b8c9d1a69f2485c910130001abbf69a5cfcd018b808c752a4acde0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "c17d98504fac48f278c77e74499bdf38da0fada6e47f12b8c15769d1ff06a9fd"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "b66f46824ab6da07736d07ab773697e1ff0761c9b33aeae1e54ee788681b51b3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "711510d9f0b3bae7d3499a55f865224d50d7dbef8ccfd4fbe33849899c610966"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "f79a72600db6d5d40788c7759d230f59d952b38c98f60d73fe4f77c2711b4b5b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "d6785a7a29c0a1d3ce6e6434ae4fd068b0ea0e70591fe20f5427e574e23a3b97"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "06a8c1986113b42d7d8ad6d0635aa60c83a05a84e704337751593eb5022cac21"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "08b3e25eac812a60d04197110fefa464079fc2a9d48ab2373f5cbeb96bee426d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "9f937a3373161b7c672f1ba8fa3d885498ae747f504d3a04bfa8a4ee8cb09e1d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "cb6b300ccc0d96f835b9c1d0f21d2c3a997caeda6324702bb8f6df252ddfe244"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fc80978f39a749817341146eabe53f6205ef06048d6e64aa911c73d659884d30"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5ebdf9587ead2590b005815d16734c36b9e1ba790a2b05997532e0fecc93314b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "38fbc91331ab21a153ba710afee80d3a7750a2a9f76f536c2937be68e982d217"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "332b3f3b32ec36cb67b8efb5867cf685887d93f049eecdb9365a5979931901bf"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f4c1898e1d30a6b1dc0a5f24e9d5ca875427669fb3db7678745936dcc1198567",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "c45444db18bdc311e663290ef083891ee0501afe11526c18033b8002f85ba26b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "fa3adf19f6121207611d32090adac8f0f05e943889f8c4d20af5e53e6fae3b2d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "4860a72381018d6591e245e870826d159c1fe59aeca2312adf81154cc620a917"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "f9ecb675b3889ce0ec239fd35a018a7bdb82b0463918b89cbc4561333e022baf"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "e5b0a92b89449573b20f90081b4e850e7739040d06ee1545c0d1a06f45b549f0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "5b694cd07195cc2a4fa60ffb92f51da74edf7d41df6c7936b4165cb0f9f078bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "f495da08c39bf33c473f25a2488c05adfd7e3dc92d0b836d7ee4af17e4644b22"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "d85e7108a23e17fe719c1223c88e48282c66b440f0fcb9bfe318617ef098d147"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "4d2ab0de9af96f944aa7b9a14040236c8e43d25a3c75125d1222c9f0200ea929"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "59fc1194e6e1cae2daaa5211e75c3008949edf539caa6d07997dd86087878c02"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "72d6fcd90b71a371c2ea13aaf35b256a7f9dbbbc204e8bba3b0b6da1071c85ba"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "8c40d12e7bb42486aeae733142c57513dc74f18a21bd4c5a7eb99a165aa3d1ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "9c594e6034d98e2048224368b7c68a34f3c09e276e0676443876b50dda22abf1"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "36ef4a81c8ab19c15d02c9eb3ca0d66ea325cef6679013efe40cc21e38637041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "9c1c7aaa288007ebd2f875f6a2e0b9e139be2c3d2769ac891c5a3ca059ee0041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "a5ad08ef2c99a3a13d99c013d9ea91ba6325a7239a312f6c36f6de162f905575"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "504c4f2b3722be480505f21e90c657e0fb1bd2183be054e2ab72de60113f40de",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "a04092d3189e793b4a9d5d9280ae820ce2836c1fa2a314d69d000f1fed428fee"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "5810f829f64827be40dc102c84eb90da86a1f7ab2dee59a2974dd2b6057280ab"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "32b0bad94856a8a09383f38d365c0c48a4690c5507bef5b9493fe8bbb7d8ebed"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "4931125f09d6c89b2c3139869b1f01b94bad451cedd296dfb0d26223b68d4d0d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "b5417e80a64bb6948b5ddc0b4396d620df143031acaaf7ed105fef3e9c940dc6"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "875c4f72924a004955fdff0e3c281cad64350cb9b8f5f407beabeb9425a3c231"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "6a7fa2ea4d0406720724b11bc1c9c34929eac64ef29b50ee26ee243aee1bfae1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "0b0aff0918cd501bbedb86c183ca69c84f0fddcb8f60fe8bf2f6551002894e94"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "fdc801df7a94125624670c1bf72bb45b85c6a33f963ff864bbaa8f12e3e0ae8a"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "8f5ee1e0a47cad8d30b99a752083652783eb138a7d16a29709f153b8b3a23f3f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "b838dbfd73e3a6a2ca7130095a308f2fe2dad6bf1d1027f007237430b5a06c24"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "3137bf0b91bd3334f1657e14e454a8b1afe842f7d2d0a1449e625bddba11c2df"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "3040ad58ffdc7f70682550830b67ec1fab9dc265ac1554759c8580a09a6c687c",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "407c87766b37dc3485b3825a9efca0d20f8084d8671fe61acfc265e1e5abdac3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "642cf66a70dc0a60d327e8e290cc7aabfa12b24716a5f615fd922179412f9f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "b7ff53576ed4193a464cb842cb84df66801cf1660b92a2931aca42b50ada8bfa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "f705453b64d1cbbae1661099e8e447a185de939f94d0407c2b942fcf0907bcc4"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "db2e14d54dcf3e9455b489750d4dd7606dd9c41e975f30c44d9fcaef2130e8f9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "45cad2e9dfea14756fa071558a67a1ecbe81f6e4fda253ba33953eb192437fe2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "63853bf6c354eed16bdc991d89bfebd42bd6aa871887bca8c3876faf45460553"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "89e1dc65ca868af3bce6c0c73eb157d9cfce2d2748a3bef2b9b2d6054a59045a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "2fe3d6d121df8aeb4f96c0fb5118d53c675756d0ccb615a8af44a525717016a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "628760995eda638bb712cf64431ddaecfd4b6905433f14269da8db724b409382"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "d0bf951786e21c749941582ac452beaeeed237cbf8d3e5dcee6c09d5029a49bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "6dbaa0e36b7446220f83b50da4e19911104326d0cb51f35188a46c85b5cddf03"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "c1a41a5261b75f0b71ecf5ad829928bac35b7c7a67a491eee7d13f5965ed788c"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61f157a1cbedeea8f214219ffa2f90fe5ac2f3d5b9ce0f4c0fa46e325c54a157",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e085cf609c78b0c0fe900014743119497829e5a6d120d5b54310fe4393dcf67b"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "73b84ffda407d572c90e810ffedbe2d98aba4bf6d184790b78fc4b9c9b306ef5"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "b759d00fcca6316ae9a16d619e31083ae2082d244762f561cc4b4d7448f96015"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "73ba7905776d6af74dec4df8b1537ee4821dd2a749cb63497fa1d4f9d5c7be9d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "7b9d78a70259211cdc9503bb1619cd68784dafdbddd3dd0b438d30a2f7c511e7"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1fb130cbaa8ff2f1338382868f7050c6103ebadaefc9dae92b21dcd3c95f2477",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "e34df2daef40e596732c0796a08514f4ed41812f4c609bf8a70d683126911d52"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f3c664b16958b91957fad0e0c3387d4496ccd27b2520598611ebf3ee3c7f4b"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "93ed5b1658dd42c3623275e89715327a622e2b64cef16820ecfab9378435baeb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "89a7c3b6b41d92ccd10c826898c1a2fa7a87e42813d5d228d210e4cb3a2b2ef4"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "270bc944c4a03c0ec4873dedc68aaf5216620736d6c4e94d4c0e01ce75e879e6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "cb3a5dd2a945ae9b8f73ea9bfe452b0b58fceb0a0c46fec82637d97728ae2e35"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "c2d40c4d0507d71755ffbe7548c54865272f7172eb5497f3498f1ff3fe366944"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "c5478414bc21d3d22782baf85adc57d5cf8db792c0f88cc742130cd1b6ad8c42"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "dfa115195e9fd45cfd4f04e1ee64d4e1b8e080aed21717b79a82a9f7b651ef98",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "13b4f5314cf3797a91b51df01383224a5f94b2dd84479f46df686910e1ddfa7f",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6a893717586f34c0d890b901c89c4f54a1f92abb4fa3e7ad84f74c978cee9928",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "ccceb257820f2ec09e89c00dfb67017f44018f987c314f7abab10b57b71fcb6c",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5285104caa341f9ce197d99d6d57f9a0ef09671e0284e8003697d00e3f2ad991",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "stable_visible": {
                "customers": {
                  "manifest_sha256": "bc9c042a90199accd2c8b6545ee4c1b3015b556dfbffd8a54a21c3ed4a48d4c1",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "c8215415f5236d27f71cd836daaefda158598e9f2fed41d6d62e640d9945effe"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "64d9c2cdd88f51d85d3fe7445154ac99ef6735fb56262de8f7d3214c05de44f9"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "e553baa7a4a5579b541aa1b8fd500391074b9a999b41deac0142880b71929018"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "9c28bbf645cbfa9c1db42a585757632205ba7b54473a522b2faf68b7816cc9b3"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "cea8b62418507e021e8a8e01485bb769015d0c81525db8a106173b9dda09472b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "977c38faff0ead04b7517382031c765a03476b7c12f9d2a471b8aedfb098afef"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "9f9040e360dca3eed6784be4dee5482e1af319b3dd69ba43dbe4627227a2690a"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "9d46cb8a8302603ac19146611affc3b2f6a8e28547f328544d19172ba9d52bd5"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "665d49e1871c07b02542feb2d4dec0a60fe5daaeb41751a5f14873f0510b69e9"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "9118a9283a524a0cc9ced2e67b2f1e08c89dd4706446c7c8046b89680685373f",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "7f18d5b67cd21bcf6dcf1c5797cf551fb7f23af9e98a0a24a36ae7257d0a4d75"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "23c757304da7dbcb1a517a8439cc72c145499b3a4212099d258f9f9e464a26a6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "fdfcfa2002bfdb68f5f3fe77e8df2ac67b8ff393c5dfdd4bba4f6e0dcfd6031f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "35c2597b7ead114ee297450bd48f0a20ab8ab96e70a9dac377609e35cba89f5f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "5d1c447e84b8c9d1a69f2485c910130001abbf69a5cfcd018b808c752a4acde0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "c17d98504fac48f278c77e74499bdf38da0fada6e47f12b8c15769d1ff06a9fd"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "b66f46824ab6da07736d07ab773697e1ff0761c9b33aeae1e54ee788681b51b3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "711510d9f0b3bae7d3499a55f865224d50d7dbef8ccfd4fbe33849899c610966"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "f79a72600db6d5d40788c7759d230f59d952b38c98f60d73fe4f77c2711b4b5b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "d6785a7a29c0a1d3ce6e6434ae4fd068b0ea0e70591fe20f5427e574e23a3b97"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "06a8c1986113b42d7d8ad6d0635aa60c83a05a84e704337751593eb5022cac21"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "08b3e25eac812a60d04197110fefa464079fc2a9d48ab2373f5cbeb96bee426d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "9f937a3373161b7c672f1ba8fa3d885498ae747f504d3a04bfa8a4ee8cb09e1d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "cb6b300ccc0d96f835b9c1d0f21d2c3a997caeda6324702bb8f6df252ddfe244"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fc80978f39a749817341146eabe53f6205ef06048d6e64aa911c73d659884d30"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5ebdf9587ead2590b005815d16734c36b9e1ba790a2b05997532e0fecc93314b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "38fbc91331ab21a153ba710afee80d3a7750a2a9f76f536c2937be68e982d217"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "332b3f3b32ec36cb67b8efb5867cf685887d93f049eecdb9365a5979931901bf"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f4c1898e1d30a6b1dc0a5f24e9d5ca875427669fb3db7678745936dcc1198567",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "c45444db18bdc311e663290ef083891ee0501afe11526c18033b8002f85ba26b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "fa3adf19f6121207611d32090adac8f0f05e943889f8c4d20af5e53e6fae3b2d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "4860a72381018d6591e245e870826d159c1fe59aeca2312adf81154cc620a917"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "f9ecb675b3889ce0ec239fd35a018a7bdb82b0463918b89cbc4561333e022baf"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "e5b0a92b89449573b20f90081b4e850e7739040d06ee1545c0d1a06f45b549f0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "5b694cd07195cc2a4fa60ffb92f51da74edf7d41df6c7936b4165cb0f9f078bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "f495da08c39bf33c473f25a2488c05adfd7e3dc92d0b836d7ee4af17e4644b22"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "d85e7108a23e17fe719c1223c88e48282c66b440f0fcb9bfe318617ef098d147"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "4d2ab0de9af96f944aa7b9a14040236c8e43d25a3c75125d1222c9f0200ea929"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "59fc1194e6e1cae2daaa5211e75c3008949edf539caa6d07997dd86087878c02"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "72d6fcd90b71a371c2ea13aaf35b256a7f9dbbbc204e8bba3b0b6da1071c85ba"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "8c40d12e7bb42486aeae733142c57513dc74f18a21bd4c5a7eb99a165aa3d1ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "9c594e6034d98e2048224368b7c68a34f3c09e276e0676443876b50dda22abf1"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "36ef4a81c8ab19c15d02c9eb3ca0d66ea325cef6679013efe40cc21e38637041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "9c1c7aaa288007ebd2f875f6a2e0b9e139be2c3d2769ac891c5a3ca059ee0041"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "a5ad08ef2c99a3a13d99c013d9ea91ba6325a7239a312f6c36f6de162f905575"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "504c4f2b3722be480505f21e90c657e0fb1bd2183be054e2ab72de60113f40de",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "a04092d3189e793b4a9d5d9280ae820ce2836c1fa2a314d69d000f1fed428fee"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "5810f829f64827be40dc102c84eb90da86a1f7ab2dee59a2974dd2b6057280ab"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "32b0bad94856a8a09383f38d365c0c48a4690c5507bef5b9493fe8bbb7d8ebed"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "4931125f09d6c89b2c3139869b1f01b94bad451cedd296dfb0d26223b68d4d0d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "b5417e80a64bb6948b5ddc0b4396d620df143031acaaf7ed105fef3e9c940dc6"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "875c4f72924a004955fdff0e3c281cad64350cb9b8f5f407beabeb9425a3c231"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "6a7fa2ea4d0406720724b11bc1c9c34929eac64ef29b50ee26ee243aee1bfae1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "0b0aff0918cd501bbedb86c183ca69c84f0fddcb8f60fe8bf2f6551002894e94"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "fdc801df7a94125624670c1bf72bb45b85c6a33f963ff864bbaa8f12e3e0ae8a"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "8f5ee1e0a47cad8d30b99a752083652783eb138a7d16a29709f153b8b3a23f3f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "b838dbfd73e3a6a2ca7130095a308f2fe2dad6bf1d1027f007237430b5a06c24"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "3137bf0b91bd3334f1657e14e454a8b1afe842f7d2d0a1449e625bddba11c2df"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "3040ad58ffdc7f70682550830b67ec1fab9dc265ac1554759c8580a09a6c687c",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "407c87766b37dc3485b3825a9efca0d20f8084d8671fe61acfc265e1e5abdac3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "642cf66a70dc0a60d327e8e290cc7aabfa12b24716a5f615fd922179412f9f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "b7ff53576ed4193a464cb842cb84df66801cf1660b92a2931aca42b50ada8bfa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "f705453b64d1cbbae1661099e8e447a185de939f94d0407c2b942fcf0907bcc4"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "db2e14d54dcf3e9455b489750d4dd7606dd9c41e975f30c44d9fcaef2130e8f9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "45cad2e9dfea14756fa071558a67a1ecbe81f6e4fda253ba33953eb192437fe2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "63853bf6c354eed16bdc991d89bfebd42bd6aa871887bca8c3876faf45460553"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "89e1dc65ca868af3bce6c0c73eb157d9cfce2d2748a3bef2b9b2d6054a59045a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "2fe3d6d121df8aeb4f96c0fb5118d53c675756d0ccb615a8af44a525717016a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "628760995eda638bb712cf64431ddaecfd4b6905433f14269da8db724b409382"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "d0bf951786e21c749941582ac452beaeeed237cbf8d3e5dcee6c09d5029a49bb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "6dbaa0e36b7446220f83b50da4e19911104326d0cb51f35188a46c85b5cddf03"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "c1a41a5261b75f0b71ecf5ad829928bac35b7c7a67a491eee7d13f5965ed788c"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61f157a1cbedeea8f214219ffa2f90fe5ac2f3d5b9ce0f4c0fa46e325c54a157",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e085cf609c78b0c0fe900014743119497829e5a6d120d5b54310fe4393dcf67b"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "73b84ffda407d572c90e810ffedbe2d98aba4bf6d184790b78fc4b9c9b306ef5"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "b759d00fcca6316ae9a16d619e31083ae2082d244762f561cc4b4d7448f96015"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "73ba7905776d6af74dec4df8b1537ee4821dd2a749cb63497fa1d4f9d5c7be9d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "7b9d78a70259211cdc9503bb1619cd68784dafdbddd3dd0b438d30a2f7c511e7"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1fb130cbaa8ff2f1338382868f7050c6103ebadaefc9dae92b21dcd3c95f2477",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "e34df2daef40e596732c0796a08514f4ed41812f4c609bf8a70d683126911d52"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f3c664b16958b91957fad0e0c3387d4496ccd27b2520598611ebf3ee3c7f4b"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "93ed5b1658dd42c3623275e89715327a622e2b64cef16820ecfab9378435baeb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "89a7c3b6b41d92ccd10c826898c1a2fa7a87e42813d5d228d210e4cb3a2b2ef4"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "270bc944c4a03c0ec4873dedc68aaf5216620736d6c4e94d4c0e01ce75e879e6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "cb3a5dd2a945ae9b8f73ea9bfe452b0b58fceb0a0c46fec82637d97728ae2e35"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "c2d40c4d0507d71755ffbe7548c54865272f7172eb5497f3498f1ff3fe366944"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "c5478414bc21d3d22782baf85adc57d5cf8db792c0f88cc742130cd1b6ad8c42"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "dfa115195e9fd45cfd4f04e1ee64d4e1b8e080aed21717b79a82a9f7b651ef98",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "13b4f5314cf3797a91b51df01383224a5f94b2dd84479f46df686910e1ddfa7f",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6a893717586f34c0d890b901c89c4f54a1f92abb4fa3e7ad84f74c978cee9928",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "ccceb257820f2ec09e89c00dfb67017f44018f987c314f7abab10b57b71fcb6c",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5285104caa341f9ce197d99d6d57f9a0ef09671e0284e8003697d00e3f2ad991",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              }
            },
            "runtime": {
              "last_published_sync_run_seq": 4,
              "lease_owner_id": null,
              "source_snapshot_completed": true
            },
            "stable_current_counts": {
              "customers": 9,
              "order_items": 18,
              "order_payments": 16,
              "order_reviews": 12,
              "orders": 13,
              "product_category_translation": 5,
              "products": 8,
              "sellers": 4
            },
            "status": "ready",
            "sync_run_id": "sync-00000000000000000004",
            "sync_run_seq": 4
          },
          "name": "final_rebuild_current_and_gold_parity",
          "status": "PASS"
        },
        {
          "detail": {
            "active_runs": [],
            "command": "validate-final",
            "gold_views": {
              "dim_customer_scd2": 8,
              "dim_date": 46,
              "dim_order_status": 2,
              "dim_product_scd2": 8,
              "dim_seller": 4,
              "fact_order_items": 18,
              "mart_daily_revenue": 13,
              "mart_monthly_arpu": 7
            },
            "iceberg_current_counts": {
              "customers": 9,
              "order_items": 18,
              "order_payments": 16,
              "order_reviews": 12,
              "orders": 13,
              "product_category_translation": 5,
              "products": 8,
              "sellers": 4
            },
            "open_or_rejected_transactions": [],
            "publication_marker": {
              "publication_status": "PUBLISHED",
              "sync_run_id": "sync-00000000000000000004",
              "sync_run_seq": 4
            },
            "runtime": {
              "last_published_sync_run_seq": 4,
              "lease_operation": null,
              "lease_owner_id": null
            },
            "stable_current_counts": {
              "customers": 9,
              "order_items": 18,
              "order_payments": 16,
              "order_reviews": 12,
              "orders": 13,
              "product_category_translation": 5,
              "products": 8,
              "sellers": 4
            },
            "status": "ready",
            "sync_run_id": "sync-00000000000000000004",
            "sync_run_seq": 4
          },
          "name": "final_independent_control_plane_check",
          "status": "PASS"
        },
        {
          "detail": {
            "clickhouse": 200,
            "command": "status",
            "compose": [
              {
                "exit_code": 0,
                "health": "healthy",
                "service": "airflow",
                "state": "running"
              },
              {
                "exit_code": 0,
                "health": "",
                "service": "airflow-projector",
                "state": "exited"
              },
              {
                "exit_code": 0,
                "health": "healthy",
                "service": "apicurio-registry",
                "state": "running"
              },
              {
                "exit_code": 0,
                "health": "healthy",
                "service": "clickhouse",
                "state": "running"
              },
              {
                "exit_code": 0,
                "health": "",
                "service": "clickhouse-init",
                "state": "exited"
              },
              {
                "exit_code": 0,
                "health": "",
                "service": "clickhouse-projector",
                "state": "exited"
              },
              {
                "exit_code": 0,
                "health": "",
                "service": "iceberg-migration",
                "state": "exited"
              },
              {
                "exit_code": 0,
                "health": "healthy",
                "service": "kafka",
                "state": "running"
              },
              {
                "exit_code": 0,
                "health": "healthy",
                "service": "kafka-connect",
                "state": "running"
              },
              {
                "exit_code": 0,
                "health": "",
                "service": "kafka-topics",
                "state": "exited"
              },
              {
                "exit_code": 0,
                "health": "healthy",
                "service": "minio",
                "state": "running"
              },
              {
                "exit_code": 0,
                "health": "",
                "service": "minio-init",
                "state": "exited"
              },
              {
                "exit_code": 0,
                "health": "healthy",
                "service": "mysql",
                "state": "running"
              },
              {
                "exit_code": 0,
                "health": "healthy",
                "service": "platform-postgres",
                "state": "running"
              },
              {
                "exit_code": 0,
                "health": "",
                "service": "platform-postgres-bootstrap",
                "state": "exited"
              },
              {
                "exit_code": 0,
                "health": "healthy",
                "service": "polaris",
                "state": "running"
              },
              {
                "exit_code": 0,
                "health": "",
                "service": "polaris-admin",
                "state": "exited"
              },
              {
                "exit_code": 0,
                "health": "",
                "service": "polaris-admin-projector",
                "state": "exited"
              },
              {
                "exit_code": 0,
                "health": "",
                "service": "polaris-bootstrap",
                "state": "exited"
              },
              {
                "exit_code": 0,
                "health": "",
                "service": "polaris-credentials-prepare",
                "state": "exited"
              },
              {
                "exit_code": 0,
                "health": "",
                "service": "polaris-server-projector",
                "state": "exited"
              },
              {
                "exit_code": 0,
                "health": "",
                "service": "spark-bronze",
                "state": "running"
              },
              {
                "exit_code": 0,
                "health": "",
                "service": "spark-geolocation",
                "state": "exited"
              },
              {
                "exit_code": 0,
                "health": "healthy",
                "service": "spark-master",
                "state": "running"
              },
              {
                "exit_code": 0,
                "health": "",
                "service": "spark-ops",
                "state": "exited"
              },
              {
                "exit_code": 0,
                "health": "",
                "service": "spark-projector",
                "state": "exited"
              },
              {
                "exit_code": 0,
                "health": "",
                "service": "spark-silver",
                "state": "running"
              },
              {
                "exit_code": 0,
                "health": "",
                "service": "spark-worker",
                "state": "running"
              }
            ],
            "connector": {
              "connector_state": "RUNNING",
              "registered": true,
              "task_0_state": "RUNNING"
            },
            "iceberg": {
              "contract_version": 2,
              "queries_count": 10,
              "status": "READY",
              "updated_at": "2026-08-04T22:59:02.610344398Z"
            },
            "mysql": {
              "customers": 9,
              "geolocation": 6,
              "order_items": 18,
              "order_payments": 16,
              "order_reviews": 12,
              "orders": 13,
              "product_category_translation": 5,
              "products": 8,
              "sellers": 4
            },
            "polaris": 200,
            "project": "olist_stage_v",
            "registry": {
              "compatibility": "BACKWARD_TRANSITIVE",
              "status_code": 200
            },
            "status": "ready",
            "writer_schema_capture": "captured"
          },
          "name": "final_serving_status_check",
          "status": "PASS"
        }
      ],
      "command": [
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "validate-rebuild",
          "--sync-run-seq",
          "4",
          "--sync-run-id",
          "sync-00000000000000000004"
        ],
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "validate-final",
          "--sync-run-seq",
          "4",
          "--sync-run-id",
          "sync-00000000000000000004"
        ],
        [
          "uv",
          "run",
          "python",
          "scripts/cdc/local_lab.py",
          "status",
          "--require",
          "serving"
        ]
      ],
      "command_results": [
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "validate-rebuild",
            "--sync-run-seq",
            "4",
            "--sync-run-id",
            "sync-00000000000000000004"
          ],
          "duration_seconds": 1.891,
          "exit_code": 0,
          "stderr": "",
          "stdout": "14873f0510b69e9\"}]}, \"order_items\": {\"manifest_sha256\": \"9118a9283a524a0cc9ced2e67b2f1e08c89dd4706446c7c8046b89680685373f\", \"row_count\": 18, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"order_item_id\": 1, \"row_hash\": \"7f18d5b67cd21bcf6dcf1c5797cf551fb7f23af9e98a0a24a36ae7257d0a4d75\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"order_item_id\": 1, \"row_hash\": \"23c757304da7dbcb1a517a8439cc72c145499b3a4212099d258f9f9e464a26a6\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"order_item_id\": 1, \"row_hash\": \"fdfcfa2002bfdb68f5f3fe77e8df2ac67b8ff393c5dfdd4bba4f6e0dcfd6031f\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"order_item_id\": 2, \"row_hash\": \"35c2597b7ead114ee297450bd48f0a20ab8ab96e70a9dac377609e35cba89f5f\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"order_item_id\": 1, \"row_hash\": \"5d1c447e84b8c9d1a69f2485c910130001abbf69a5cfcd018b808c752a4acde0\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"order_item_id\": 1, \"row_hash\": \"c17d98504fac48f278c77e74499bdf38da0fada6e47f12b8c15769d1ff06a9fd\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"order_item_id\": 1, \"row_hash\": \"b66f46824ab6da07736d07ab773697e1ff0761c9b33aeae1e54ee788681b51b3\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"order_item_id\": 2, \"row_hash\": \"711510d9f0b3bae7d3499a55f865224d50d7dbef8ccfd4fbe33849899c610966\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"order_item_id\": 1, \"row_hash\": \"f79a72600db6d5d40788c7759d230f59d952b38c98f60d73fe4f77c2711b4b5b\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"order_item_id\": 1, \"row_hash\": \"d6785a7a29c0a1d3ce6e6434ae4fd068b0ea0e70591fe20f5427e574e23a3b97\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"order_item_id\": 1, \"row_hash\": \"06a8c1986113b42d7d8ad6d0635aa60c83a05a84e704337751593eb5022cac21\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"order_item_id\": 2, \"row_hash\": \"08b3e25eac812a60d04197110fefa464079fc2a9d48ab2373f5cbeb96bee426d\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"order_item_id\": 1, \"row_hash\": \"9f937a3373161b7c672f1ba8fa3d885498ae747f504d3a04bfa8a4ee8cb09e1d\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"order_item_id\": 1, \"row_hash\": \"cb6b300ccc0d96f835b9c1d0f21d2c3a997caeda6324702bb8f6df252ddfe244\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"order_item_id\": 1, \"row_hash\": \"fc80978f39a749817341146eabe53f6205ef06048d6e64aa911c73d659884d30\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"order_item_id\": 2, \"row_hash\": \"5ebdf9587ead2590b005815d16734c36b9e1ba790a2b05997532e0fecc93314b\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"order_item_id\": 1, \"row_hash\": \"38fbc91331ab21a153ba710afee80d3a7750a2a9f76f536c2937be68e982d217\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"order_item_id\": 2, \"row_hash\": \"332b3f3b32ec36cb67b8efb5867cf685887d93f049eecdb9365a5979931901bf\"}]}, \"order_payments\": {\"manifest_sha256\": \"f4c1898e1d30a6b1dc0a5f24e9d5ca875427669fb3db7678745936dcc1198567\", \"row_count\": 16, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"payment_sequential\": 1, \"row_hash\": \"c45444db18bdc311e663290ef083891ee0501afe11526c18033b8002f85ba26b\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"payment_sequential\": 1, \"row_hash\": \"fa3adf19f6121207611d32090adac8f0f05e943889f8c4d20af5e53e6fae3b2d\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"payment_sequential\": 1, \"row_hash\": \"4860a72381018d6591e245e870826d159c1fe59aeca2312adf81154cc620a917\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"payment_sequential\": 1, \"row_hash\": \"f9ecb675b3889ce0ec239fd35a018a7bdb82b0463918b89cbc4561333e022baf\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"payment_sequential\": 2, \"row_hash\": \"e5b0a92b89449573b20f90081b4e850e7739040d06ee1545c0d1a06f45b549f0\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"payment_sequential\": 1, \"row_hash\": \"5b694cd07195cc2a4fa60ffb92f51da74edf7d41df6c7936b4165cb0f9f078bb\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"payment_sequential\": 1, \"row_hash\": \"f495da08c39bf33c473f25a2488c05adfd7e3dc92d0b836d7ee4af17e4644b22\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"payment_sequential\": 1, \"row_hash\": \"d85e7108a23e17fe719c1223c88e48282c66b440f0fcb9bfe318617ef098d147\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"payment_sequential\": 1, \"row_hash\": \"4d2ab0de9af96f944aa7b9a14040236c8e43d25a3c75125d1222c9f0200ea929\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"payment_sequential\": 2, \"row_hash\": \"59fc1194e6e1cae2daaa5211e75c3008949edf539caa6d07997dd86087878c02\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"payment_sequential\": 1, \"row_hash\": \"72d6fcd90b71a371c2ea13aaf35b256a7f9dbbbc204e8bba3b0b6da1071c85ba\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"payment_sequential\": 1, \"row_hash\": \"8c40d12e7bb42486aeae733142c57513dc74f18a21bd4c5a7eb99a165aa3d1ab\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"payment_sequential\": 1, \"row_hash\": \"9c594e6034d98e2048224368b7c68a34f3c09e276e0676443876b50dda22abf1\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"payment_sequential\": 1, \"row_hash\": \"36ef4a81c8ab19c15d02c9eb3ca0d66ea325cef6679013efe40cc21e38637041\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"payment_sequential\": 1, \"row_hash\": \"9c1c7aaa288007ebd2f875f6a2e0b9e139be2c3d2769ac891c5a3ca059ee0041\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"payment_sequential\": 2, \"row_hash\": \"a5ad08ef2c99a3a13d99c013d9ea91ba6325a7239a312f6c36f6de162f905575\"}]}, \"order_reviews\": {\"manifest_sha256\": \"504c4f2b3722be480505f21e90c657e0fb1bd2183be054e2ab72de60113f40de\", \"row_count\": 12, \"rows\": [{\"is_deleted\": false, \"review_id\": \"review_001\", \"row_hash\": \"a04092d3189e793b4a9d5d9280ae820ce2836c1fa2a314d69d000f1fed428fee\"}, {\"is_deleted\": false, \"review_id\": \"review_002\", \"row_hash\": \"5810f829f64827be40dc102c84eb90da86a1f7ab2dee59a2974dd2b6057280ab\"}, {\"is_deleted\": false, \"review_id\": \"review_003\", \"row_hash\": \"32b0bad94856a8a09383f38d365c0c48a4690c5507bef5b9493fe8bbb7d8ebed\"}, {\"is_deleted\": false, \"review_id\": \"review_004\", \"row_hash\": \"4931125f09d6c89b2c3139869b1f01b94bad451cedd296dfb0d26223b68d4d0d\"}, {\"is_deleted\": false, \"review_id\": \"review_005\", \"row_hash\": \"b5417e80a64bb6948b5ddc0b4396d620df143031acaaf7ed105fef3e9c940dc6\"}, {\"is_deleted\": false, \"review_id\": \"review_006\", \"row_hash\": \"875c4f72924a004955fdff0e3c281cad64350cb9b8f5f407beabeb9425a3c231\"}, {\"is_deleted\": false, \"review_id\": \"review_007\", \"row_hash\": \"6a7fa2ea4d0406720724b11bc1c9c34929eac64ef29b50ee26ee243aee1bfae1\"}, {\"is_deleted\": false, \"review_id\": \"review_008\", \"row_hash\": \"0b0aff0918cd501bbedb86c183ca69c84f0fddcb8f60fe8bf2f6551002894e94\"}, {\"is_deleted\": false, \"review_id\": \"review_009\", \"row_hash\": \"fdc801df7a94125624670c1bf72bb45b85c6a33f963ff864bbaa8f12e3e0ae8a\"}, {\"is_deleted\": false, \"review_id\": \"review_010\", \"row_hash\": \"8f5ee1e0a47cad8d30b99a752083652783eb138a7d16a29709f153b8b3a23f3f\"}, {\"is_deleted\": false, \"review_id\": \"review_011\", \"row_hash\": \"b838dbfd73e3a6a2ca7130095a308f2fe2dad6bf1d1027f007237430b5a06c24\"}, {\"is_deleted\": false, \"review_id\": \"review_012\", \"row_hash\": \"3137bf0b91bd3334f1657e14e454a8b1afe842f7d2d0a1449e625bddba11c2df\"}]}, \"orders\": {\"manifest_sha256\": \"3040ad58ffdc7f70682550830b67ec1fab9dc265ac1554759c8580a09a6c687c\", \"row_count\": 13, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"row_hash\": \"407c87766b37dc3485b3825a9efca0d20f8084d8671fe61acfc265e1e5abdac3\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"row_hash\": \"642cf66a70dc0a60d327e8e290cc7aabfa12b24716a5f615fd922179412f9f4d\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"row_hash\": \"b7ff53576ed4193a464cb842cb84df66801cf1660b92a2931aca42b50ada8bfa\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"row_hash\": \"f705453b64d1cbbae1661099e8e447a185de939f94d0407c2b942fcf0907bcc4\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"row_hash\": \"db2e14d54dcf3e9455b489750d4dd7606dd9c41e975f30c44d9fcaef2130e8f9\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"row_hash\": \"45cad2e9dfea14756fa071558a67a1ecbe81f6e4fda253ba33953eb192437fe2\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"row_hash\": \"63853bf6c354eed16bdc991d89bfebd42bd6aa871887bca8c3876faf45460553\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"row_hash\": \"89e1dc65ca868af3bce6c0c73eb157d9cfce2d2748a3bef2b9b2d6054a59045a\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"row_hash\": \"2fe3d6d121df8aeb4f96c0fb5118d53c675756d0ccb615a8af44a525717016a0\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"row_hash\": \"628760995eda638bb712cf64431ddaecfd4b6905433f14269da8db724b409382\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"row_hash\": \"d0bf951786e21c749941582ac452beaeeed237cbf8d3e5dcee6c09d5029a49bb\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"row_hash\": \"6dbaa0e36b7446220f83b50da4e19911104326d0cb51f35188a46c85b5cddf03\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"row_hash\": \"c1a41a5261b75f0b71ecf5ad829928bac35b7c7a67a491eee7d13f5965ed788c\"}]}, \"product_category_translation\": {\"manifest_sha256\": \"61f157a1cbedeea8f214219ffa2f90fe5ac2f3d5b9ce0f4c0fa46e325c54a157\", \"row_count\": 5, \"rows\": [{\"is_deleted\": false, \"product_category_name\": \"beleza_saude\", \"row_hash\": \"e085cf609c78b0c0fe900014743119497829e5a6d120d5b54310fe4393dcf67b\"}, {\"is_deleted\": false, \"product_category_name\": \"informatica_acessorios\", \"row_hash\": \"73b84ffda407d572c90e810ffedbe2d98aba4bf6d184790b78fc4b9c9b306ef5\"}, {\"is_deleted\": false, \"product_category_name\": \"moveis_decoracao\", \"row_hash\": \"b759d00fcca6316ae9a16d619e31083ae2082d244762f561cc4b4d7448f96015\"}, {\"is_deleted\": false, \"product_category_name\": \"telefonia\", \"row_hash\": \"73ba7905776d6af74dec4df8b1537ee4821dd2a749cb63497fa1d4f9d5c7be9d\"}, {\"is_deleted\": false, \"product_category_name\": \"utilidades_domesticas\", \"row_hash\": \"7b9d78a70259211cdc9503bb1619cd68784dafdbddd3dd0b438d30a2f7c511e7\"}]}, \"products\": {\"manifest_sha256\": \"1fb130cbaa8ff2f1338382868f7050c6103ebadaefc9dae92b21dcd3c95f2477\", \"row_count\": 8, \"rows\": [{\"is_deleted\": false, \"product_id\": \"product_001\", \"row_hash\": \"e34df2daef40e596732c0796a08514f4ed41812f4c609bf8a70d683126911d52\"}, {\"is_deleted\": false, \"product_id\": \"product_002\", \"row_hash\": \"e2f3c664b16958b91957fad0e0c3387d4496ccd27b2520598611ebf3ee3c7f4b\"}, {\"is_deleted\": false, \"product_id\": \"product_003\", \"row_hash\": \"93ed5b1658dd42c3623275e89715327a622e2b64cef16820ecfab9378435baeb\"}, {\"is_deleted\": false, \"product_id\": \"product_004\", \"row_hash\": \"89a7c3b6b41d92ccd10c826898c1a2fa7a87e42813d5d228d210e4cb3a2b2ef4\"}, {\"is_deleted\": false, \"product_id\": \"product_005\", \"row_hash\": \"270bc944c4a03c0ec4873dedc68aaf5216620736d6c4e94d4c0e01ce75e879e6\"}, {\"is_deleted\": false, \"product_id\": \"product_006\", \"row_hash\": \"cb3a5dd2a945ae9b8f73ea9bfe452b0b58fceb0a0c46fec82637d97728ae2e35\"}, {\"is_deleted\": false, \"product_id\": \"product_007\", \"row_hash\": \"c2d40c4d0507d71755ffbe7548c54865272f7172eb5497f3498f1ff3fe366944\"}, {\"is_deleted\": false, \"product_id\": \"product_008\", \"row_hash\": \"c5478414bc21d3d22782baf85adc57d5cf8db792c0f88cc742130cd1b6ad8c42\"}]}, \"sellers\": {\"manifest_sha256\": \"dfa115195e9fd45cfd4f04e1ee64d4e1b8e080aed21717b79a82a9f7b651ef98\", \"row_count\": 4, \"rows\": [{\"is_deleted\": false, \"row_hash\": \"13b4f5314cf3797a91b51df01383224a5f94b2dd84479f46df686910e1ddfa7f\", \"seller_id\": \"seller_001\"}, {\"is_deleted\": false, \"row_hash\": \"6a893717586f34c0d890b901c89c4f54a1f92abb4fa3e7ad84f74c978cee9928\", \"seller_id\": \"seller_002\"}, {\"is_deleted\": false, \"row_hash\": \"ccceb257820f2ec09e89c00dfb67017f44018f987c314f7abab10b57b71fcb6c\", \"seller_id\": \"seller_003\"}, {\"is_deleted\": false, \"row_hash\": \"5285104caa341f9ce197d99d6d57f9a0ef09671e0284e8003697d00e3f2ad991\", \"seller_id\": \"seller_004\"}]}}}, \"runtime\": {\"last_published_sync_run_seq\": 4, \"lease_owner_id\": null, \"source_snapshot_completed\": true}, \"stable_current_counts\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"status\": \"ready\", \"sync_run_id\": \"sync-00000000000000000004\", \"sync_run_seq\": 4}\n",
          "timed_out": false
        },
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "validate-final",
            "--sync-run-seq",
            "4",
            "--sync-run-id",
            "sync-00000000000000000004"
          ],
          "duration_seconds": 1.984,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"active_runs\": [], \"command\": \"validate-final\", \"gold_views\": {\"dim_customer_scd2\": 8, \"dim_date\": 46, \"dim_order_status\": 2, \"dim_product_scd2\": 8, \"dim_seller\": 4, \"fact_order_items\": 18, \"mart_daily_revenue\": 13, \"mart_monthly_arpu\": 7}, \"iceberg_current_counts\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"open_or_rejected_transactions\": [], \"publication_marker\": {\"publication_status\": \"PUBLISHED\", \"sync_run_id\": \"sync-00000000000000000004\", \"sync_run_seq\": 4}, \"runtime\": {\"last_published_sync_run_seq\": 4, \"lease_operation\": null, \"lease_owner_id\": null}, \"stable_current_counts\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"status\": \"ready\", \"sync_run_id\": \"sync-00000000000000000004\", \"sync_run_seq\": 4}\n",
          "timed_out": false
        },
        {
          "args": [
            "uv",
            "run",
            "python",
            "scripts/cdc/local_lab.py",
            "status",
            "--require",
            "serving"
          ],
          "duration_seconds": 1.906,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"clickhouse\": 200, \"command\": \"status\", \"compose\": [{\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"airflow\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"airflow-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"apicurio-registry\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"clickhouse\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"clickhouse-init\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"clickhouse-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"iceberg-migration\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"kafka\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"kafka-connect\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"kafka-topics\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"minio\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"minio-init\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"mysql\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"platform-postgres\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"platform-postgres-bootstrap\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"polaris\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-admin\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-admin-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-bootstrap\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-credentials-prepare\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-server-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-bronze\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-geolocation\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"spark-master\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-ops\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-silver\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-worker\", \"state\": \"running\"}], \"connector\": {\"connector_state\": \"RUNNING\", \"registered\": true, \"task_0_state\": \"RUNNING\"}, \"iceberg\": {\"contract_version\": 2, \"queries_count\": 10, \"status\": \"READY\", \"updated_at\": \"2026-08-04T22:59:02.610344398Z\"}, \"mysql\": {\"customers\": 9, \"geolocation\": 6, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"polaris\": 200, \"project\": \"olist_stage_v\", \"registry\": {\"compatibility\": \"BACKWARD_TRANSITIVE\", \"status_code\": 200}, \"status\": \"ready\", \"writer_schema_capture\": \"captured\"}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 5.78,
      "gate": "10-final",
      "status": "PASS",
      "timestamp": "2026-08-04T22:59:43.130408+00:00"
    }
  },
  "mandatory_gates": [
    "00-preflight",
    "01-harness-ready",
    "02-clean-bootstrap",
    "03-initial-snapshot",
    "04-crud-and-restart",
    "05-caught-up",
    "06-serving-sync",
    "07-dbt-and-stable-views",
    "08-additive-schema",
    "09-rebuild",
    "10-final"
  ],
  "passed_gate_count": 11
}
```

---

## 4. Evidence Artifacts

Raw evidence persisted in `data/stage-v-evidence/stage_l4_20260805_f0_restored/`.
