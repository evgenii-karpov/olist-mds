# Stage V Candidate E2E Validation Report

- **Status**: `PASS`
- **Run ID**: `stage_v_final_candidate_retry`
- **Compose Project**: `olist_stage_v`
- **Started At**: `2026-08-03T17:44:12.190104+00:00`
- **Finished At**: `2026-08-03T18:05:27.871364+00:00`

---

## 1. Final Verdict

Stage V validation completed with status `PASS`.

All mandatory gates passed in a single clean-domain run.

- **Stage L Authorization**: `AUTHORIZED` (allowed to proceed to Stage L)

---

## 2. Gate Execution Results (V0 - V10)

| Gate | Name | Status | Duration (s) |
| --- | --- | --- | ---: |
| `00-preflight` | 00-preflight | `PASS` | 49.758 |
| `01-harness-ready` | 01-harness-ready | `PASS` | 0.001 |
| `02-clean-bootstrap` | 02-clean-bootstrap | `PASS` | 412.166 |
| `03-initial-snapshot` | 03-initial-snapshot | `PASS` | 257.226 |
| `04-crud-and-restart` | 04-crud-and-restart | `PASS` | 147.655 |
| `05-caught-up` | 05-caught-up | `PASS` | 94.199 |
| `06-serving-sync` | 06-serving-sync | `PASS` | 189.629 |
| `07-dbt-and-stable-views` | 07-dbt-and-stable-views | `PASS` | 3.71 |
| `08-additive-schema` | 08-additive-schema | `PASS` | 60.944 |
| `09-rebuild` | 09-rebuild | `PASS` | 22.632 |
| `10-final` | 10-final | `PASS` | 4.269 |

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
              ".gitignore",
              ".pre-commit-config.yaml",
              "airflow/dags/olist_lakehouse_maintenance.py",
              "airflow/dags/olist_lakehouse_serving.py",
              "compose.yaml",
              "dbt/olist_clickhouse/macros/source_state.sql",
              "dbt/olist_clickhouse/macros/tests.sql",
              "dbt/olist_clickhouse/models/_models.yml",
              "dbt/olist_clickhouse/models/gold/dim_product_scd2.sql",
              "dbt/olist_clickhouse/profiles.yml.example",
              "dbt/olist_clickhouse/selectors.yml",
              "dbt/olist_clickhouse/tests/assert_customer_scd2_windows.sql",
              "dbt/olist_clickhouse/tests/assert_daily_revenue_components.sql",
              "dbt/olist_clickhouse/tests/assert_fact_order_items_grain.sql",
              "dbt/olist_clickhouse/tests/assert_monthly_arpu_formulas.sql",
              "dbt/olist_clickhouse/tests/assert_product_scd2_windows.sql",
              "docker/airflow/Dockerfile",
              "docker/airflow/load-env-and-run.sh",
              "docker/spark/status/bronze/.gitkeep",
              "docker/spark/status/silver/.gitkeep",
              "docs/plans/lakehouse/active/stage-ev-validation-repair.md",
              "docs/plans/lakehouse/contracts/architecture-and-runtime.md",
              "docs/reports/mysql-spark-iceberg-stage-v-validation.md",
              "docs/runbooks/lakehouse-serving-sync.md",
              "infra/control-postgres/init-control-db.sh",
              "scripts/cdc/local_lab.py",
              "scripts/serving/airflow_api.py",
              "scripts/serving/boundary.py",
              "scripts/serving/clickhouse.py",
              "scripts/serving/control.py",
              "scripts/serving/dbt_runner.py",
              "scripts/serving/models.py",
              "scripts/validation/stage_v_candidate_e2e.py",
              "scripts/validation/stage_v_probes.py",
              "streaming/connect/bootstrap.py",
              "streaming/schemas/capture_runtime.py",
              "streaming/schemas/captured-writer-schemas/customers/value/schema-10-d622022d67322c94.avsc",
              "streaming/schemas/captured-writer-schemas/manifest.json",
              "streaming/schemas/captured-writer-schemas/order_items/value/schema-16-4aa4857dfbae2506.avsc",
              "streaming/schemas/captured-writer-schemas/order_payments/value/schema-19-c444ba8de505fbfb.avsc",
              "streaming/schemas/captured-writer-schemas/order_reviews/value/schema-22-97d410a2eaad8459.avsc",
              "streaming/schemas/captured-writer-schemas/orders/value/schema-13-27ab76afddf19535.avsc",
              "streaming/schemas/captured-writer-schemas/product_category_translation/value/schema-31-d0d04df645b86090.avsc",
              "streaming/schemas/captured-writer-schemas/products/value/schema-25-c526d8632f372065.avsc",
              "streaming/schemas/captured-writer-schemas/sellers/value/schema-28-53bf2a40e7c25964.avsc",
              "streaming/schemas/contracts/customers/v2.json",
              "streaming/schemas/contracts/manifest.json",
              "streaming/schemas/contracts/order_items/v2.json",
              "streaming/schemas/contracts/order_payments/v2.json",
              "streaming/schemas/contracts/order_reviews/v2.json",
              "streaming/schemas/contracts/orders/v2.json",
              "streaming/schemas/contracts/product_category_translation/v2.json",
              "streaming/schemas/contracts/products/v2.json",
              "streaming/schemas/contracts/sellers/v2.json",
              "streaming/schemas/registry.py",
              "streaming/spark/scala/build.sbt",
              "streaming/spark/scala/src/main/scala/com/olist/mds/spark/app/SilverMain.scala",
              "streaming/spark/scala/src/main/scala/com/olist/mds/spark/bronze/BronzeBatchWriter.scala",
              "streaming/spark/scala/src/main/scala/com/olist/mds/spark/contract/ContractLoader.scala",
              "streaming/spark/scala/src/main/scala/com/olist/mds/spark/contract/EntityContract.scala",
              "streaming/spark/scala/src/main/scala/com/olist/mds/spark/schema/SchemaArchiveWriter.scala",
              "streaming/spark/scala/src/main/scala/com/olist/mds/spark/silver/SilverBatchWriter.scala",
              "streaming/spark/scala/src/main/scala/com/olist/mds/spark/silver/SilverDecoder.scala",
              "streaming/spark/scala/src/main/scala/com/olist/mds/spark/silver/SilverProgressWriter.scala",
              "streaming/spark/scala/src/main/scala/com/olist/mds/spark/transaction/TransactionBatchWriter.scala",
              "tests/lakehouse_platform/test_local_lab_live_readiness.py",
              "tests/lakehouse_platform/test_local_lab_profile_boundaries.py",
              "tests/serving/test_boundary.py",
              "tests/stage_v/test_stage_v_harness.py",
              "dbt/olist_clickhouse/profiles.yml",
              "docs/plans/lakehouse/active/stage-ev-handoff.md",
              "streaming/schemas/captured-writer-schemas/customers/value/schema-10-86778e42358beb24.avsc",
              "streaming/schemas/captured-writer-schemas/order_items/value/schema-16-405694a7e8a40115.avsc",
              "streaming/schemas/captured-writer-schemas/order_payments/value/schema-19-5788388ef63117c7.avsc",
              "streaming/schemas/captured-writer-schemas/order_reviews/value/schema-22-60bc008106640ed5.avsc",
              "streaming/schemas/captured-writer-schemas/orders/value/schema-13-36873a348c768312.avsc",
              "streaming/schemas/captured-writer-schemas/product_category_translation/value/schema-31-6b9036c22e2ff6f4.avsc",
              "streaming/schemas/captured-writer-schemas/products/value/schema-25-5518567779fd234c.avsc",
              "streaming/schemas/captured-writer-schemas/sellers/value/schema-28-6b66dd6e45a4170d.avsc",
              "streaming/spark/scala/src/main/scala/com/olist/mds/spark/avro/RegistrySchemaResolver.scala",
              "tests/serving/test_airflow_api.py",
              "tests/serving/test_dbt_runner.py"
            ],
            "commands_ok": true,
            "diagnostics": "g: in the working copy of 'streaming/spark/scala/src/main/scala/com/olist/mds/spark/bronze/BronzeBatchWriter.scala', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/spark/scala/src/main/scala/com/olist/mds/spark/contract/ContractLoader.scala', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/spark/scala/src/main/scala/com/olist/mds/spark/contract/EntityContract.scala', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/spark/scala/src/main/scala/com/olist/mds/spark/schema/SchemaArchiveWriter.scala', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/spark/scala/src/main/scala/com/olist/mds/spark/silver/SilverBatchWriter.scala', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/spark/scala/src/main/scala/com/olist/mds/spark/silver/SilverDecoder.scala', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/spark/scala/src/main/scala/com/olist/mds/spark/silver/SilverProgressWriter.scala', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/spark/scala/src/main/scala/com/olist/mds/spark/transaction/TransactionBatchWriter.scala', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/lakehouse_platform/test_local_lab_live_readiness.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/lakehouse_platform/test_local_lab_profile_boundaries.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it\n",
            "dirty": true,
            "head": "bf9fac7bdfe9f844298ef1b99fdf2bd0efd421ea",
            "worktree_digest": "0c05ddaf9a18def50f35a391d9ef62b1c325218a2833b30760fb5ba179f72045"
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
          "duration_seconds": 28.844,
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
          "stdout": "bf9fac7bdfe9f844298ef1b99fdf2bd0efd421ea\n",
          "timed_out": false
        },
        {
          "args": [
            "git",
            "status",
            "--porcelain=v1",
            "--untracked-files=all"
          ],
          "duration_seconds": 0.078,
          "exit_code": 0,
          "stderr": "",
          "stdout": " M .dockerignore\n M .gitignore\n M .pre-commit-config.yaml\n M airflow/dags/olist_lakehouse_maintenance.py\n M airflow/dags/olist_lakehouse_serving.py\n M compose.yaml\n M dbt/olist_clickhouse/macros/source_state.sql\n M dbt/olist_clickhouse/macros/tests.sql\n M dbt/olist_clickhouse/models/_models.yml\n M dbt/olist_clickhouse/models/gold/dim_product_scd2.sql\n M dbt/olist_clickhouse/profiles.yml.example\n M dbt/olist_clickhouse/selectors.yml\n M dbt/olist_clickhouse/tests/assert_customer_scd2_windows.sql\n M dbt/olist_clickhouse/tests/assert_daily_revenue_components.sql\n M dbt/olist_clickhouse/tests/assert_fact_order_items_grain.sql\n M dbt/olist_clickhouse/tests/assert_monthly_arpu_formulas.sql\n M dbt/olist_clickhouse/tests/assert_product_scd2_windows.sql\n M docker/airflow/Dockerfile\n M docker/airflow/load-env-and-run.sh\n D docker/spark/status/bronze/.gitkeep\n D docker/spark/status/silver/.gitkeep\n M docs/plans/lakehouse/active/stage-ev-validation-repair.md\n M docs/plans/lakehouse/contracts/architecture-and-runtime.md\n M docs/reports/mysql-spark-iceberg-stage-v-validation.md\n M docs/runbooks/lakehouse-serving-sync.md\n M infra/control-postgres/init-control-db.sh\n M scripts/cdc/local_lab.py\n M scripts/serving/airflow_api.py\n M scripts/serving/boundary.py\n M scripts/serving/clickhouse.py\n M scripts/serving/control.py\n M scripts/serving/dbt_runner.py\n M scripts/serving/models.py\n M scripts/validation/stage_v_candidate_e2e.py\n M scripts/validation/stage_v_probes.py\n M streaming/connect/bootstrap.py\n M streaming/schemas/capture_runtime.py\n D streaming/schemas/captured-writer-schemas/customers/value/schema-10-d622022d67322c94.avsc\n M streaming/schemas/captured-writer-schemas/manifest.json\n D streaming/schemas/captured-writer-schemas/order_items/value/schema-16-4aa4857dfbae2506.avsc\n D streaming/schemas/captured-writer-schemas/order_payments/value/schema-19-c444ba8de505fbfb.avsc\n D streaming/schemas/captured-writer-schemas/order_reviews/value/schema-22-97d410a2eaad8459.avsc\n D streaming/schemas/captured-writer-schemas/orders/value/schema-13-27ab76afddf19535.avsc\n D streaming/schemas/captured-writer-schemas/product_category_translation/value/schema-31-d0d04df645b86090.avsc\n D streaming/schemas/captured-writer-schemas/products/value/schema-25-c526d8632f372065.avsc\n D streaming/schemas/captured-writer-schemas/sellers/value/schema-28-53bf2a40e7c25964.avsc\n M streaming/schemas/contracts/customers/v2.json\n M streaming/schemas/contracts/manifest.json\n M streaming/schemas/contracts/order_items/v2.json\n M streaming/schemas/contracts/order_payments/v2.json\n M streaming/schemas/contracts/order_reviews/v2.json\n M streaming/schemas/contracts/orders/v2.json\n M streaming/schemas/contracts/product_category_translation/v2.json\n M streaming/schemas/contracts/products/v2.json\n M streaming/schemas/contracts/sellers/v2.json\n M streaming/schemas/registry.py\n M streaming/spark/scala/build.sbt\n M streaming/spark/scala/src/main/scala/com/olist/mds/spark/app/SilverMain.scala\n M streaming/spark/scala/src/main/scala/com/olist/mds/spark/bronze/BronzeBatchWriter.scala\n M streaming/spark/scala/src/main/scala/com/olist/mds/spark/contract/ContractLoader.scala\n M streaming/spark/scala/src/main/scala/com/olist/mds/spark/contract/EntityContract.scala\n M streaming/spark/scala/src/main/scala/com/olist/mds/spark/schema/SchemaArchiveWriter.scala\n M streaming/spark/scala/src/main/scala/com/olist/mds/spark/silver/SilverBatchWriter.scala\n M streaming/spark/scala/src/main/scala/com/olist/mds/spark/silver/SilverDecoder.scala\n M streaming/spark/scala/src/main/scala/com/olist/mds/spark/silver/SilverProgressWriter.scala\n M streaming/spark/scala/src/main/scala/com/olist/mds/spark/transaction/TransactionBatchWriter.scala\n M tests/lakehouse_platform/test_local_lab_live_readiness.py\n M tests/lakehouse_platform/test_local_lab_profile_boundaries.py\n M tests/serving/test_boundary.py\n M tests/stage_v/test_stage_v_harness.py\n?? dbt/olist_clickhouse/profiles.yml\n?? docs/plans/lakehouse/active/stage-ev-handoff.md\n?? streaming/schemas/captured-writer-schemas/customers/value/schema-10-86778e42358beb24.avsc\n?? streaming/schemas/captured-writer-schemas/order_items/value/schema-16-405694a7e8a40115.avsc\n?? streaming/schemas/captured-writer-schemas/order_payments/value/schema-19-5788388ef63117c7.avsc\n?? streaming/schemas/captured-writer-schemas/order_reviews/value/schema-22-60bc008106640ed5.avsc\n?? streaming/schemas/captured-writer-schemas/orders/value/schema-13-36873a348c768312.avsc\n?? streaming/schemas/captured-writer-schemas/product_category_translation/value/schema-31-6b9036c22e2ff6f4.avsc\n?? streaming/schemas/captured-writer-schemas/products/value/schema-25-5518567779fd234c.avsc\n?? streaming/schemas/captured-writer-schemas/sellers/value/schema-28-6b66dd6e45a4170d.avsc\n?? streaming/spark/scala/src/main/scala/com/olist/mds/spark/avro/RegistrySchemaResolver.scala\n?? tests/serving/test_airflow_api.py\n?? tests/serving/test_dbt_runner.py\n",
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
          "duration_seconds": 0.156,
          "exit_code": 0,
          "stderr": "warning: in the working copy of '.dockerignore', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of '.pre-commit-config.yaml', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'airflow/dags/olist_lakehouse_maintenance.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'airflow/dags/olist_lakehouse_serving.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'compose.yaml', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'dbt/olist_clickhouse/macros/source_state.sql', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'dbt/olist_clickhouse/macros/tests.sql', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'dbt/olist_clickhouse/models/_models.yml', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'dbt/olist_clickhouse/models/gold/dim_product_scd2.sql', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'dbt/olist_clickhouse/profiles.yml.example', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'dbt/olist_clickhouse/selectors.yml', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'dbt/olist_clickhouse/tests/assert_customer_scd2_windows.sql', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'dbt/olist_clickhouse/tests/assert_daily_revenue_components.sql', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'dbt/olist_clickhouse/tests/assert_fact_order_items_grain.sql', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'dbt/olist_clickhouse/tests/assert_monthly_arpu_formulas.sql', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'dbt/olist_clickhouse/tests/assert_product_scd2_windows.sql', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'docker/airflow/Dockerfile', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'docs/plans/lakehouse/active/stage-ev-validation-repair.md', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'docs/plans/lakehouse/contracts/architecture-and-runtime.md', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'docs/reports/mysql-spark-iceberg-stage-v-validation.md', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'docs/runbooks/lakehouse-serving-sync.md', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'scripts/cdc/local_lab.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'scripts/serving/airflow_api.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'scripts/serving/boundary.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'scripts/serving/clickhouse.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'scripts/serving/control.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'scripts/serving/dbt_runner.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'scripts/serving/models.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'scripts/validation/stage_v_candidate_e2e.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'scripts/validation/stage_v_probes.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/connect/bootstrap.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/schemas/capture_runtime.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/schemas/captured-writer-schemas/manifest.json', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/schemas/contracts/customers/v2.json', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/schemas/contracts/manifest.json', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/schemas/contracts/order_items/v2.json', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/schemas/contracts/order_payments/v2.json', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/schemas/contracts/order_reviews/v2.json', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/schemas/contracts/orders/v2.json', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/schemas/contracts/product_category_translation/v2.json', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/schemas/contracts/products/v2.json', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/schemas/contracts/sellers/v2.json', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/schemas/registry.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/spark/scala/build.sbt', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/spark/scala/src/main/scala/com/olist/mds/spark/app/SilverMain.scala', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/spark/scala/src/main/scala/com/olist/mds/spark/bronze/BronzeBatchWriter.scala', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/spark/scala/src/main/scala/com/olist/mds/spark/contract/ContractLoader.scala', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/spark/scala/src/main/scala/com/olist/mds/spark/contract/EntityContract.scala', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/spark/scala/src/main/scala/com/olist/mds/spark/schema/SchemaArchiveWriter.scala', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/spark/scala/src/main/scala/com/olist/mds/spark/silver/SilverBatchWriter.scala', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/spark/scala/src/main/scala/com/olist/mds/spark/silver/SilverDecoder.scala', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/spark/scala/src/main/scala/com/olist/mds/spark/silver/SilverProgressWriter.scala', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/spark/scala/src/main/scala/com/olist/mds/spark/transaction/TransactionBatchWriter.scala', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/lakehouse_platform/test_local_lab_live_readiness.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/lakehouse_platform/test_local_lab_profile_boundaries.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it\n",
          "stdout": "rall_status\": \"PASS\",\n+            \"mandatory_gates\": list(MANDATORY_GATES),\n+            \"missing_gates\": [],\n+            \"failed_or_skipped_gates\": [],\n+            \"gates\": {\n+                gate: {\n+                    \"gate\": gate,\n+                    \"status\": \"PASS\",\n+                    \"assertions\": [\n+                        {\"name\": name, \"status\": \"PASS\"}\n+                        for name in REQUIRED_ASSERTIONS[gate]\n+                    ],\n+                }\n+                for gate in MANDATORY_GATES\n+            },\n+            \"runtime_cleanup\": {\"status\": \"PASS\"},\n+        }\n+        self.assertEqual(validate_acceptance_summary(summary), [])\n+\n+    def test_acceptance_summary_rejects_generic_assertions(self) -> None:\n+        summary = {\n+            \"run_id\": \"test\",\n+            \"overall_status\": \"PASS\",\n+            \"mandatory_gates\": list(MANDATORY_GATES),\n+            \"missing_gates\": [],\n+            \"failed_or_skipped_gates\": [],\n+            \"gates\": {\n+                gate: {\n+                    \"gate\": gate,\n+                    \"status\": \"PASS\",\n+                    \"assertions\": [{\"name\": \"check\", \"status\": \"PASS\"}],\n+                }\n+                for gate in MANDATORY_GATES\n+            },\n+            \"runtime_cleanup\": {\"status\": \"PASS\"},\n+        }\n+        errors = validate_acceptance_summary(summary)\n+        self.assertTrue(any(\"unexpected assertions\" in error for error in errors))\n+\n+    @patch(\"scripts.serving.clickhouse.clickhouse_query\")\n+    def test_clickhouse_nullable_probe_requires_full_path_evidence(\n+        self, mock_clickhouse_query: MagicMock\n+    ) -> None:\n+        writer_schema = {\n+            \"type\": \"record\",\n+            \"name\": \"Value\",\n+            \"fields\": [\n+                {\"name\": \"customer_id\", \"type\": \"string\"},\n+                {\"name\": \"customer_unique_id\", \"type\": \"string\"},\n+                {\"name\": \"customer_zip_code_prefix\", \"type\": \"string\"},\n+                {\"name\": \"customer_city\", \"type\": \"string\"},\n+                {\"name\": \"customer_state\", \"type\": \"string\"},\n+                {\n+                    \"name\": \"stage_v_optional_note\",\n+                    \"type\": [\"null\", \"string\"],\n+                    \"default\": None,\n+                },\n+            ],\n+        }\n+        mock_clickhouse_query.side_effect = [\n+            [\n+                {\n+                    \"event_id\": \"event-001\",\n+                    \"customer_id\": \"wave2_customer_001\",\n+                    \"customer_city\": \"sao paulo stage v\",\n+                    \"optional_value\": None,\n+                    \"apply_status\": \"APPLIED\",\n+                    \"is_deleted\": 0,\n+                    \"kafka_topic\": \"olist_cdc.olist_oltp.customers\",\n+                    \"kafka_partition\": 0,\n+                    \"kafka_offset\": 10,\n+                    \"key_schema_id\": 7,\n+                    \"value_schema_id\": 37,\n+                    \"transaction_id\": \"tx-001\",\n+                }\n+            ],\n+            [\n+                {\n+                    \"event_id\": \"event-001\",\n+                    \"topic\": \"olist_cdc.olist_oltp.customers\",\n+                    \"partition\": 0,\n+                    \"offset\": 10,\n+                    \"is_tombstone\": 0,\n+                    \"key_schema_id\": 7,\n+                    \"value_schema_id\": 37,\n+                    \"key_framing_valid\": 1,\n+                    \"value_framing_valid\": 1,\n+                }\n+            ],\n+            [\n+                {\n+                    \"schema_id\": 37,\n+                    \"fingerprint_sha256\": \"a\" * 64,\n+                    \"subject\": \"olist_cdc.olist_oltp.customers-value\",\n+                    \"schema_json\": \"{}\",\n+                    \"spark_self_contained_schema_json\": json.dumps(writer_schema),\n+                }\n+            ],\n+            [{\"error_count\": 0}],\n+            [{\"error_count\": 0}],\n+            [\n+                {\n+                    \"customer_id\": \"wave2_customer_001\",\n+                    \"customer_city\": \"sao paulo stage v\",\n+                    \"optional_value\": None,\n+                }\n+            ],\n+        ]\n+\n+        result = ClickHouseProbe().inspect_nullable_event(\n+            \"wave2_customer_001\", \"sao paulo stage v\"\n+        )\n+\n+        self.assertEqual(result[\"status\"], \"VERIFIED\")\n+        self.assertEqual(result[\"event_id\"], \"event-001\")\n+        self.assertEqual(mock_clickhouse_query.call_count, 6)\n+\n+    @patch(\"scripts.serving.clickhouse.clickhouse_query\")\n+    def test_entity_metrics_are_bounded_to_complete_transaction_prefix(\n+        self, mock_clickhouse_query: MagicMock\n+    ) -> None:\n+        from scripts.serving.clickhouse import ClickHouseServingMaterializer\n+\n+        mock_clickhouse_query.return_value = []\n+\n+        result = ClickHouseServingMaterializer.fetch_entity_metrics(42)\n+\n+        self.assertEqual(result[\"customers\"][\"event_count\"], 0)\n+        self.assertEqual(mock_clickhouse_query.call_count, 8)\n+        queries = [call.args[0] for call in mock_clickhouse_query.call_args_list]\n+        self.assertTrue(\n+            all(\n+                \"transaction_id IS NULL\" in query\n+                and \"status = 'COMPLETE'\" in query\n+                and \"end_kafka_offset <= 42\" in query\n+                for query in queries\n+            )\n+        )\n+\n+    @patch(\"scripts.serving.clickhouse.clickhouse_query\")\n+    def test_silver_progress_excludes_internal_transaction_row(\n+        self, mock_clickhouse_query: MagicMock\n+    ) -> None:\n+        from scripts.serving.clickhouse import ClickHouseServingMaterializer\n+\n+        mock_clickhouse_query.return_value = [\n+            {\n+                \"entity\": \"customers\",\n+                \"last_kafka_offset\": 7,\n+                \"changes_snapshot_id\": 123,\n+                \"status\": \"COMMITTED\",\n+            },\n+            {\n+                \"entity\": \"__transactions__\",\n+                \"last_kafka_offset\": 19,\n+                \"changes_snapshot_id\": 456,\n+                \"status\": \"COMMITTED\",\n+            },\n+        ]\n+\n+        result = ClickHouseServingMaterializer.fetch_silver_progress()\n+\n+        self.assertEqual(set(result), {\"customers\"})\n+        query = mock_clickhouse_query.call_args.args[0]\n+        self.assertIn(\"WHERE entity IN\", query)\n+        self.assertIn(\"argMax(changes_snapshot_id, recorded_at)\", query)\n+\n+    @patch(\"scripts.serving.clickhouse.clickhouse_query\")\n+    def test_iceberg_snapshots_use_latest_progress_row(\n+        self, mock_clickhouse_query: MagicMock\n+    ) -> None:\n+        from scripts.serving.clickhouse import ClickHouseServingMaterializer\n+\n+        mock_clickhouse_query.return_value = [\n+            {\"entity\": entity, \"snapshot_id\": index + 1}\n+            for index, entity in enumerate(\n+                (\n+                    \"customers\",\n+                    \"orders\",\n+                    \"order_items\",\n+                    \"order_payments\",\n+                    \"order_reviews\",\n+                    \"products\",\n+                    \"sellers\",\n+                    \"product_category_translation\",\n+                )\n+            )\n+        ]\n+\n+        result = ClickHouseServingMaterializer.fetch_iceberg_snapshots()\n+\n+        self.assertEqual(result[\"customers\"], 1)\n+        query = mock_clickhouse_query.call_args.args[0]\n+        self.assertIn(\"argMax(changes_snapshot_id, recorded_at)\", query)\n+        self.assertIn(\"WHERE entity IN\", query)\n+        self.assertNotIn(\"max(changes_snapshot_id)\", query)\n+\n+    @patch(\"scripts.serving.clickhouse.clickhouse_execute\")\n+    @patch(\"scripts.serving.clickhouse.clickhouse_query\")\n+    def test_additive_columns_refresh_stable_current_view(\n+        self,\n+        mock_clickhouse_query: MagicMock,\n+        mock_clickhouse_execute: MagicMock,\n+    ) -> None:\n+        from scripts.serving.clickhouse import ClickHouseServingMaterializer\n+        from scripts.serving.entities import get_entity_spec\n+\n+        mock_clickhouse_query.return_value = [\n+            {\"name\": \"customer_id\", \"type\": \"String\"},\n+            {\"name\": \"stage_v_optional_note\", \"type\": \"Nullable(String)\"},\n+        ]\n+\n+        columns = ClickHouseServingMaterializer._serving_business_columns(\n+            get_entity_spec(\"customers\")\n+        )\n+\n+        self.assertIn(\"stage_v_optional_note\", columns)\n+        statements = [call.args[0] for call in mock_clickhouse_execute.call_args_list]\n+        self.assertTrue(\n+            any(\n+                \"ALTER TABLE serving_cdc.customers_current_versions\" in statement\n+                for statement in statements\n+            )\n+        )\n+        self.assertTrue(\n+            any(\n+                \"CREATE OR REPLACE VIEW serving_cdc.customers_current\" in statement\n+                and \"published_runs_current\" in statement\n+                for statement in statements\n+            )\n+        )\n+\n+    @patch(\"scripts.serving.clickhouse.clickhouse_query\")\n+    def test_publish_marker_preserves_nested_json_escapes(\n+        self, mock_clickhouse_query: MagicMock\n+    ) -> None:\n+        from scripts.serving.clickhouse import ClickHouseServingMaterializer\n+        from scripts.serving.models import ServingSyncReport\n+\n+        report = ServingSyncReport(\n+            sync_run_seq=7,\n+            sync_run_id=\"sync-00000000000000000007\",\n+            operation_type=\"SYNC\",\n+            status=\"SUCCEEDED\",\n+            status_reason=\"NONE\",\n+            is_noop=False,\n+            previous_transaction_id=None,\n+            target_transaction_id=\"tx-7\",\n+            expected_event_count=1,\n+            materialized_event_count=1,\n+            entity_counts={\"customers\": 1},\n+            published_at=\"2026-08-03T00:00:00+00:00\",\n+            dbt_result={\n+                \"command\": [\"--vars\", '{\"sync_run_seq\": 7, \"sync_run_id\": \"x\"}']\n+            },\n+        )\n+\n+        ClickHouseServingMaterializer.publish_marker(report)\n+\n+        insert_sql = mock_clickhouse_query.call_args.args[0]\n+        self.assertIn(r'{\\\\\"sync_run_seq\\\\\": 7', insert_sql)\n+\n     @patch.object(StageVOrchestrator, \"run_cmd\")\n     def test_orchestrator_prepare_creates_evidence_dirs(\n         self, mock_run_cmd: MagicMock\n@@ -80,6 +449,39 @@ class StageVHarnessUnitTests(unittest.TestCase):\n             self.assertTrue((ev_dir / \"00-preflight\" / \"summary.json\").exists())\n             self.assertTrue((ev_dir / \"01-harness-ready\" / \"summary.json\").exists())\n \n+    def test_checksums_include_nested_gate_summaries(self) -> None:\n+        with tempfile.TemporaryDirectory() as tmp_dir:\n+            ev_dir = Path(tmp_dir) / \"evidence\"\n+            gate_summary = ev_dir / \"00-preflight\" / \"summary.json\"\n+            gate_summary.parent.mkdir(parents=True)\n+            gate_summary.write_text(\"{}\", encoding=\"utf-8\")\n+            (ev_dir / \"summary.json\").write_text(\"{}\", encoding=\"utf-8\")\n+\n+            checksums = StageVOrchestrator(\"test_run_002\", ev_dir).generate_checksums()\n+\n+            self.assertIn(\"00-preflight/summary.json\", checksums)\n+            self.assertNotIn(\"summary.json\", checksums)\n+            self.assertTrue((ev_dir / \"checksums.json\").exists())\n+\n+    def test_failed_run_preserves_runtime_for_diagnostics(self) -> None:\n+        with tempfile.TemporaryDirectory() as tmp_dir:\n+            ev_dir = Path(tmp_dir) / \"evidence\"\n+            orchestrator = StageVOrchestrator(\"failed_run\", ev_dir)\n+\n+            orchestrator.preserve_runtime_for_diagnostics(\n+                {\"status\": \"FAIL\", \"gate\": \"03-initial-snapshot\"}\n+            )\n+\n+            cleanup = json.loads(\n+                (ev_dir / \"runtime_cleanup.json\").read_text(encoding=\"utf-8\")\n+            )\n+            self.assertEqual(cleanup[\"status\"], \"SKIPPED\")\n+            self.assertEqual(\n+                cleanup[\"reason\"],\n+                \"E2E_FAILED_RUNTIME_PRESERVED_FOR_DIAGNOSTICS\",\n+            )\n+            self.assertEqual(cleanup[\"failed_gate\"], \"03-initial-snapshot\")\n+\n \n if __name__ == \"__main__\":\n     unittest.main()\n",
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
          "duration_seconds": 0.079,
          "exit_code": 0,
          "stderr": "",
          "stdout": "dbt/olist_clickhouse/profiles.yml\u0000docs/plans/lakehouse/active/stage-ev-handoff.md\u0000streaming/schemas/captured-writer-schemas/customers/value/schema-10-86778e42358beb24.avsc\u0000streaming/schemas/captured-writer-schemas/order_items/value/schema-16-405694a7e8a40115.avsc\u0000streaming/schemas/captured-writer-schemas/order_payments/value/schema-19-5788388ef63117c7.avsc\u0000streaming/schemas/captured-writer-schemas/order_reviews/value/schema-22-60bc008106640ed5.avsc\u0000streaming/schemas/captured-writer-schemas/orders/value/schema-13-36873a348c768312.avsc\u0000streaming/schemas/captured-writer-schemas/product_category_translation/value/schema-31-6b9036c22e2ff6f4.avsc\u0000streaming/schemas/captured-writer-schemas/products/value/schema-25-5518567779fd234c.avsc\u0000streaming/schemas/captured-writer-schemas/sellers/value/schema-28-6b66dd6e45a4170d.avsc\u0000streaming/spark/scala/src/main/scala/com/olist/mds/spark/avro/RegistrySchemaResolver.scala\u0000tests/serving/test_airflow_api.py\u0000tests/serving/test_dbt_runner.py\u0000",
          "timed_out": false
        },
        {
          "args": [
            "uv",
            "lock",
            "--check"
          ],
          "duration_seconds": 0.047,
          "exit_code": 0,
          "stderr": "Resolved 216 packages in 1ms\n",
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
          "duration_seconds": 13.797,
          "exit_code": 0,
          "stderr": "",
          "stdout": "============================= test session starts =============================\nplatform win32 -- Python 3.12.13, pytest-9.0.3, pluggy-1.6.0\nrootdir: C:\\Users\\fyujv\\source\\repos\\olist-mds\nconfigfile: pyproject.toml\nplugins: anyio-4.13.0\ncollected 188 items\n\ntests\\cdc_contracts\\test_avro_helpers.py ..........                      [  5%]\ntests\\cdc_contracts\\test_connector_bootstrap.py ................         [ 13%]\ntests\\cdc_contracts\\test_entity_contracts.py ..............              [ 21%]\ntests\\cdc_contracts\\test_topics.py .......                               [ 25%]\ntests\\cdc_contracts\\test_writer_schemas.py ....                          [ 27%]\ntests\\lakehouse_platform\\test_local_lab_live_readiness.py ...            [ 28%]\ntests\\lakehouse_platform\\test_local_lab_profile_boundaries.py .....      [ 31%]\ntests\\lakehouse_platform\\test_normalization_api.py ...                   [ 32%]\ntests\\lakehouse_platform\\test_polaris_admin_minio_contract.py ..         [ 34%]\ntests\\lakehouse_platform\\test_polaris_contract.py .......                [ 37%]\ntests\\lakehouse_platform\\test_polaris_credentials_projection.py ...      [ 39%]\ntests\\lakehouse_platform\\test_spark_config.py ....                       [ 41%]\ntests\\lakehouse_platform\\test_spark_image_contract.py .....              [ 44%]\ntests\\lakehouse_platform\\test_table_contracts.py .......                 [ 47%]\ntests\\mysql\\test_cli.py .......                                          [ 51%]\ntests\\mysql\\test_mysql_integration.py ss                                 [ 52%]\ntests\\mysql\\test_repository.py .................                         [ 61%]\ntests\\mysql\\test_seeding.py ......                                       [ 64%]\ntests\\mysql\\test_source_schema.py ............                           [ 71%]\ntests\\dbt_clickhouse\\test_dbt_parse.py .                                 [ 71%]\ntests\\dbt_clickhouse\\test_native_ddl_contract.py ........                [ 76%]\ntests\\dbt_clickhouse\\test_project_contract.py ......                     [ 79%]\ntests\\serving\\test_airflow_api.py .....                                  [ 81%]\ntests\\serving\\test_boundary.py .......                                   [ 85%]\ntests\\serving\\test_dbt_runner.py .                                       [ 86%]\ntests\\serving\\test_entities.py ...                                       [ 87%]\ntests\\stage_v\\test_stage_v_harness.py ...................                [ 97%]\ntests\\stage_v\\test_stage_v_oracles.py ....                               [100%]\n\n============================== warnings summary ===============================\n.venv\\Lib\\site-packages\\airflow\\__init__.py:47\n  C:\\Users\\fyujv\\source\\repos\\olist-mds\\.venv\\Lib\\site-packages\\airflow\\__init__.py:47: RuntimeWarning: Airflow currently can be run on POSIX-compliant Operating Systems. For development, it is regularly tested on fairly modern Linux Distros and recent versions of macOS. On Windows you can run it via WSL2 (Windows Subsystem for Linux 2) or via Linux Containers. The work to add Windows support is tracked via https://github.com/apache/airflow/issues/10388, but it is not a high priority.\n    warnings.warn(\n\n.venv\\Lib\\site-packages\\_pytest\\cacheprovider.py:475\n  C:\\Users\\fyujv\\source\\repos\\olist-mds\\.venv\\Lib\\site-packages\\_pytest\\cacheprovider.py:475: PytestCacheWarning: could not create cache path C:\\Users\\fyujv\\source\\repos\\olist-mds\\.pytest_cache\\v\\cache\\nodeids: [WinError 5] Access is denied: 'C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.pytest_cache\\\\v\\\\cache'\n    config.cache.set(\"cache/nodeids\", sorted(self.cached_nodeids))\n\n-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html\n================= 186 passed, 2 skipped, 2 warnings in 12.02s =================\n",
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
          "duration_seconds": 6.687,
          "exit_code": 0,
          "stderr": "#0 building with \"desktop-linux\" instance using docker driver\n\n#1 [internal] load build definition from Dockerfile\n#1 transferring dockerfile: 2.73kB 0.0s done\n#1 DONE 0.0s\n\n#2 resolve image config for docker-image://docker.io/docker/dockerfile:1.7\n#2 DONE 1.6s\n\n#3 docker-image://docker.io/docker/dockerfile:1.7@sha256:a57df69d0ea827fb7266491f2813635de6f17269be881f696fbfdf2d83dda33e\n#3 CACHED\n\n#4 [internal] load metadata for docker.io/library/alpine:3.22.1\n#4 DONE 0.0s\n\n#5 [internal] load metadata for docker.io/apache/spark:4.1.3-scala2.13-java17-python3-ubuntu\n#5 DONE 0.0s\n\n#6 [internal] load .dockerignore\n#6 transferring context: 1.65kB done\n#6 DONE 0.0s\n\n#7 [sbt-downloader 1/5] FROM docker.io/library/alpine:3.22.1\n#7 DONE 0.0s\n\n#8 [scala-builder 1/6] FROM docker.io/apache/spark:4.1.3-scala2.13-java17-python3-ubuntu\n#8 DONE 0.0s\n\n#9 [internal] load build context\n#9 transferring context: 88.01kB 0.2s done\n#9 DONE 0.2s\n\n#10 [artifact-downloader 3/5] COPY docker/spark/jars.sha256 /tmp/jars.sha256\n#10 CACHED\n\n#11 [scala-builder 5/6] WORKDIR /tmp/streaming/spark/scala\n#11 CACHED\n\n#12 [sbt-downloader 3/5] COPY docker/spark/sbt-launch.sha256 /tmp/sbt-launch.sha256\n#12 CACHED\n\n#13 [scala-builder 2/6] COPY --from=artifact-downloader /opt/olist/jars/ /opt/spark/jars/\n#13 CACHED\n\n#14 [sbt-downloader 5/5] RUN chmod 0555 /usr/local/bin/download-sbt-launch     && /usr/local/bin/download-sbt-launch /tmp/sbt-launch.sha256 /tmp/sbt-launcher\n#14 CACHED\n\n#15 [scala-builder 3/6] COPY --from=sbt-downloader /tmp/sbt-launcher/sbt-launch.jar /tmp/sbt-launch.jar\n#15 CACHED\n\n#16 [scala-builder 4/6] COPY streaming /tmp/streaming\n#16 CACHED\n\n#17 [artifact-downloader 5/5] RUN chmod 0555 /usr/local/bin/download-jars     && /usr/local/bin/download-jars /tmp/jars.sha256 /opt/olist/jars\n#17 CACHED\n\n#18 [artifact-downloader 4/5] COPY docker/spark/download-jars.sh /usr/local/bin/download-jars\n#18 CACHED\n\n#19 [sbt-downloader 4/5] COPY docker/spark/download-sbt-launch.sh /usr/local/bin/download-sbt-launch\n#19 CACHED\n\n#20 [sbt-downloader 2/5] RUN apk add --no-cache ca-certificates wget\n#20 CACHED\n\n#21 [scala-builder 6/6] RUN java -jar /tmp/sbt-launch.jar scalafmtCheckAll scalafmtSbtCheck Test/compile test package\n#21 CACHED\n\n#22 exporting to image\n#22 exporting layers\n#22 exporting layers 3.7s done\n#22 writing image sha256:210e94b76c5bc01c12efb38edb53f4390f1154c5f9ac3c7aa7aa1abb81176a81 done\n#22 DONE 3.8s\n\nView build details: docker-desktop://dashboard/build/desktop-linux/desktop-linux/kpxjtrd1gi39juij3chrfp7hv\n",
          "stdout": "",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 49.758,
      "gate": "00-preflight",
      "status": "PASS",
      "timestamp": "2026-08-03T17:45:01.950157+00:00"
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
      "duration_seconds": 0.001,
      "gate": "01-harness-ready",
      "status": "PASS",
      "timestamp": "2026-08-03T17:45:01.952800+00:00"
    },
    "02-clean-bootstrap": {
      "assertions": [
        {
          "detail": "{\"command\": \"reset\", \"scoped_to\": \"olist_stage_v\", \"status\": \"ready\"}",
          "name": "lab_reset",
          "status": "PASS"
        },
        {
          "detail": "{\"capture\": {\"capture_state\": \"captured\", \"contract_version\": 2}, \"command\": \"bootstrap\", \"readiness_level\": \"wave1_platform\", \"seed\": {\"archive\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\tests\\\\fixtures\\\\olist_small\\\\olist_small.zip\", \"exit_code\": 0, \"row_counts\": {\"customers\": 8, \"geolocation\": 6, \"order_items\": 16, \"order_payments\": 14, \"order_reviews\": 12, \"orders\": 12, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"run_id\": \"stage_v_final_candidate_retry_seed_1061cec69b2a\"}, \"status\": \"ready\", \"validation\": {\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 216 packages in 4ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"m/test_local_lab_live_readiness.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/lakehouse_platform/test_local_lab_profile_boundaries.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it\", \"exit_code\": 0, \"status\": \"passed\"}], \"status\": \"ready\"}}",
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
          "stage_v_final_candidate_retry_seed_1061cec69b2a",
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
          "duration_seconds": 0.531,
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
            "stage_v_final_candidate_retry_seed_1061cec69b2a",
            "--random-seed",
            "20260801"
          ],
          "duration_seconds": 411.625,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"capture\": {\"capture_state\": \"captured\", \"contract_version\": 2}, \"command\": \"bootstrap\", \"readiness_level\": \"wave1_platform\", \"seed\": {\"archive\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\tests\\\\fixtures\\\\olist_small\\\\olist_small.zip\", \"exit_code\": 0, \"row_counts\": {\"customers\": 8, \"geolocation\": 6, \"order_items\": 16, \"order_payments\": 14, \"order_reviews\": 12, \"orders\": 12, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"run_id\": \"stage_v_final_candidate_retry_seed_1061cec69b2a\"}, \"status\": \"ready\", \"validation\": {\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 216 packages in 4ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"m/test_local_lab_live_readiness.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/lakehouse_platform/test_local_lab_profile_boundaries.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it\", \"exit_code\": 0, \"status\": \"passed\"}], \"status\": \"ready\"}}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 412.166,
      "gate": "02-clean-bootstrap",
      "status": "PASS",
      "timestamp": "2026-08-03T17:51:54.120716+00:00"
    },
    "03-initial-snapshot": {
      "assertions": [
        {
          "detail": "{\"command\": \"start-streaming\", \"freshness_basis\": \"initial_start\", \"freshness_verified\": false, \"new_query_ids\": {\"bronze\": \"d2cb4c41-8b21-4c08-a958-f9ce3bca082e\", \"silver\": \"1d222c0b-c1b4-4b58-b53a-bf98377f0383,370efb6b-2b3e-4cca-82c9-8dd88f31c222,42cd65b6-c4d1-4c7e-9861-9300bb90d109,4c2cb83d-bb8c-4365-a430-69698094baaa,5eda7c75-a0d2-45ed-bd65-e4f49ef579dc,66c4be43-fbd7-4859-8943-5d1403b70b0c,6acc1c44-9a75-4954-9dea-fb3cb6bbcab1,92e0546a-1402-42a1-b305-2e2cda3fae3e,af4851ce-95a8-4b73-9c55-d15cfa78c114,ffccf33d-a5e2-4ef2-a942-ac219b28c554\"}, \"old_query_ids\": {}, \"restart_barrier_at_utc\": null, \"status\": \"ready\", \"status_files\": {\"bronze\": {\"query_count\": 1, \"updated_at_utc\": \"2026-08-03T17:53:49.345089686Z\"}, \"silver\": {\"query_count\": 10, \"updated_at_utc\": \"2026-08-03T17:54:00.600491436Z\"}}}",
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
                  "changes_snapshot_id": 1153565293288894621,
                  "entity": "customers",
                  "last_kafka_offset": 7,
                  "status": "COMMITTED"
                },
                "order_items": {
                  "changes_snapshot_id": 6859959852090241277,
                  "entity": "order_items",
                  "last_kafka_offset": 3,
                  "status": "COMMITTED"
                },
                "order_payments": {
                  "changes_snapshot_id": 6170798721512892500,
                  "entity": "order_payments",
                  "last_kafka_offset": 4,
                  "status": "COMMITTED"
                },
                "order_reviews": {
                  "changes_snapshot_id": 4071221208603430991,
                  "entity": "order_reviews",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "orders": {
                  "changes_snapshot_id": 196322019738629920,
                  "entity": "orders",
                  "last_kafka_offset": 1,
                  "status": "COMMITTED"
                },
                "product_category_translation": {
                  "changes_snapshot_id": 2510271481881063845,
                  "entity": "product_category_translation",
                  "last_kafka_offset": 4,
                  "status": "COMMITTED"
                },
                "products": {
                  "changes_snapshot_id": 6434977924513876130,
                  "entity": "products",
                  "last_kafka_offset": 7,
                  "status": "COMMITTED"
                },
                "sellers": {
                  "changes_snapshot_id": 6608875651304288148,
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
          "duration_seconds": 130.422,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"start-streaming\", \"freshness_basis\": \"initial_start\", \"freshness_verified\": false, \"new_query_ids\": {\"bronze\": \"d2cb4c41-8b21-4c08-a958-f9ce3bca082e\", \"silver\": \"1d222c0b-c1b4-4b58-b53a-bf98377f0383,370efb6b-2b3e-4cca-82c9-8dd88f31c222,42cd65b6-c4d1-4c7e-9861-9300bb90d109,4c2cb83d-bb8c-4365-a430-69698094baaa,5eda7c75-a0d2-45ed-bd65-e4f49ef579dc,66c4be43-fbd7-4859-8943-5d1403b70b0c,6acc1c44-9a75-4954-9dea-fb3cb6bbcab1,92e0546a-1402-42a1-b305-2e2cda3fae3e,af4851ce-95a8-4b73-9c55-d15cfa78c114,ffccf33d-a5e2-4ef2-a942-ac219b28c554\"}, \"old_query_ids\": {}, \"restart_barrier_at_utc\": null, \"status\": \"ready\", \"status_files\": {\"bronze\": {\"query_count\": 1, \"updated_at_utc\": \"2026-08-03T17:53:49.345089686Z\"}, \"silver\": {\"query_count\": 10, \"updated_at_utc\": \"2026-08-03T17:54:00.600491436Z\"}}}\n",
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
          "duration_seconds": 99.953,
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
          "duration_seconds": 22.062,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"wait-caught-up\", \"status\": \"ready\"}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 257.226,
      "gate": "03-initial-snapshot",
      "status": "PASS",
      "timestamp": "2026-08-03T17:56:11.349436+00:00"
    },
    "04-crud-and-restart": {
      "assertions": [
        {
          "detail": "{\"command\": \"stop-streaming\", \"old_query_ids\": {\"bronze\": \"d2cb4c41-8b21-4c08-a958-f9ce3bca082e\", \"silver\": \"1d222c0b-c1b4-4b58-b53a-bf98377f0383,370efb6b-2b3e-4cca-82c9-8dd88f31c222,42cd65b6-c4d1-4c7e-9861-9300bb90d109,4c2cb83d-bb8c-4365-a430-69698094baaa,5eda7c75-a0d2-45ed-bd65-e4f49ef579dc,66c4be43-fbd7-4859-8943-5d1403b70b0c,6acc1c44-9a75-4954-9dea-fb3cb6bbcab1,92e0546a-1402-42a1-b305-2e2cda3fae3e,af4851ce-95a8-4b73-9c55-d15cfa78c114,ffccf33d-a5e2-4ef2-a942-ac219b28c554\"}, \"status\": \"ready\", \"status_files_removed\": true}",
          "name": "stop_spark_streaming",
          "status": "PASS"
        },
        {
          "detail": "Executed insert (8 statements), update (5 statements), delete (4 statements)",
          "name": "execute_crud_fixtures",
          "status": "PASS"
        },
        {
          "detail": "{\"command\": \"start-streaming\", \"freshness_basis\": \"status_updated_at_after_restart_barrier\", \"freshness_verified\": true, \"new_query_ids\": {\"bronze\": \"d2cb4c41-8b21-4c08-a958-f9ce3bca082e\", \"silver\": \"1d222c0b-c1b4-4b58-b53a-bf98377f0383,370efb6b-2b3e-4cca-82c9-8dd88f31c222,42cd65b6-c4d1-4c7e-9861-9300bb90d109,4c2cb83d-bb8c-4365-a430-69698094baaa,5eda7c75-a0d2-45ed-bd65-e4f49ef579dc,66c4be43-fbd7-4859-8943-5d1403b70b0c,6acc1c44-9a75-4954-9dea-fb3cb6bbcab1,92e0546a-1402-42a1-b305-2e2cda3fae3e,af4851ce-95a8-4b73-9c55-d15cfa78c114,ffccf33d-a5e2-4ef2-a942-ac219b28c554\"}, \"old_query_ids\": {\"bronze\": \"d2cb4c41-8b21-4c08-a958-f9ce3bca082e\", \"silver\": \"1d222c0b-c1b4-4b58-b53a-bf98377f0383,370efb6b-2b3e-4cca-82c9-8dd88f31c222,42cd65b6-c4d1-4c7e-9861-9300bb90d109,4c2cb83d-bb8c-4365-a430-69698094baaa,5eda7c75-a0d2-45ed-bd65-e4f49ef579dc,66c4be43-fbd7-4859-8943-5d1403b70b0c,6acc1c44-9a75-4954-9dea-fb3cb6bbcab1,92e0546a-1402-42a1-b305-2e2cda3fae3e,af4851ce-95a8-4b73-9c55-d15cfa78c114,ffccf33d-a5e2-4ef2-a942-ac219b28c554\"}, \"restart_barrier_at_utc\": \"2026-08-03T17:56:22.274596+00:00\", \"status\": \"ready\", \"status_files\": {\"bronze\": {\"query_count\": 1, \"updated_at_utc\": \"2026-08-03T17:58:25.643960616Z\"}, \"silver\": {\"query_count\": 10, \"updated_at_utc\": \"2026-08-03T17:58:33.183712041Z\"}}}",
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
          "duration_seconds": 10.953,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"stop-streaming\", \"old_query_ids\": {\"bronze\": \"d2cb4c41-8b21-4c08-a958-f9ce3bca082e\", \"silver\": \"1d222c0b-c1b4-4b58-b53a-bf98377f0383,370efb6b-2b3e-4cca-82c9-8dd88f31c222,42cd65b6-c4d1-4c7e-9861-9300bb90d109,4c2cb83d-bb8c-4365-a430-69698094baaa,5eda7c75-a0d2-45ed-bd65-e4f49ef579dc,66c4be43-fbd7-4859-8943-5d1403b70b0c,6acc1c44-9a75-4954-9dea-fb3cb6bbcab1,92e0546a-1402-42a1-b305-2e2cda3fae3e,af4851ce-95a8-4b73-9c55-d15cfa78c114,ffccf33d-a5e2-4ef2-a942-ac219b28c554\"}, \"status\": \"ready\", \"status_files_removed\": true}\n",
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
          "duration_seconds": 136.407,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"start-streaming\", \"freshness_basis\": \"status_updated_at_after_restart_barrier\", \"freshness_verified\": true, \"new_query_ids\": {\"bronze\": \"d2cb4c41-8b21-4c08-a958-f9ce3bca082e\", \"silver\": \"1d222c0b-c1b4-4b58-b53a-bf98377f0383,370efb6b-2b3e-4cca-82c9-8dd88f31c222,42cd65b6-c4d1-4c7e-9861-9300bb90d109,4c2cb83d-bb8c-4365-a430-69698094baaa,5eda7c75-a0d2-45ed-bd65-e4f49ef579dc,66c4be43-fbd7-4859-8943-5d1403b70b0c,6acc1c44-9a75-4954-9dea-fb3cb6bbcab1,92e0546a-1402-42a1-b305-2e2cda3fae3e,af4851ce-95a8-4b73-9c55-d15cfa78c114,ffccf33d-a5e2-4ef2-a942-ac219b28c554\"}, \"old_query_ids\": {\"bronze\": \"d2cb4c41-8b21-4c08-a958-f9ce3bca082e\", \"silver\": \"1d222c0b-c1b4-4b58-b53a-bf98377f0383,370efb6b-2b3e-4cca-82c9-8dd88f31c222,42cd65b6-c4d1-4c7e-9861-9300bb90d109,4c2cb83d-bb8c-4365-a430-69698094baaa,5eda7c75-a0d2-45ed-bd65-e4f49ef579dc,66c4be43-fbd7-4859-8943-5d1403b70b0c,6acc1c44-9a75-4954-9dea-fb3cb6bbcab1,92e0546a-1402-42a1-b305-2e2cda3fae3e,af4851ce-95a8-4b73-9c55-d15cfa78c114,ffccf33d-a5e2-4ef2-a942-ac219b28c554\"}, \"restart_barrier_at_utc\": \"2026-08-03T17:56:22.274596+00:00\", \"status\": \"ready\", \"status_files\": {\"bronze\": {\"query_count\": 1, \"updated_at_utc\": \"2026-08-03T17:58:25.643960616Z\"}, \"silver\": {\"query_count\": 10, \"updated_at_utc\": \"2026-08-03T17:58:33.183712041Z\"}}}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 147.655,
      "gate": "04-crud-and-restart",
      "status": "PASS",
      "timestamp": "2026-08-03T17:58:39.006545+00:00"
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
                  "changes_snapshot_id": 3770751687399586214,
                  "entity": "customers",
                  "last_kafka_offset": 8,
                  "status": "COMMITTED"
                },
                "order_items": {
                  "changes_snapshot_id": 8333618748302751604,
                  "entity": "order_items",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "order_payments": {
                  "changes_snapshot_id": 2342546804373807134,
                  "entity": "order_payments",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "order_reviews": {
                  "changes_snapshot_id": 1873788046910446323,
                  "entity": "order_reviews",
                  "last_kafka_offset": 2,
                  "status": "COMMITTED"
                },
                "orders": {
                  "changes_snapshot_id": 2860036943269124164,
                  "entity": "orders",
                  "last_kafka_offset": 3,
                  "status": "COMMITTED"
                },
                "product_category_translation": {
                  "changes_snapshot_id": 2510271481881063845,
                  "entity": "product_category_translation",
                  "last_kafka_offset": 4,
                  "status": "COMMITTED"
                },
                "products": {
                  "changes_snapshot_id": 6434977924513876130,
                  "entity": "products",
                  "last_kafka_offset": 7,
                  "status": "COMMITTED"
                },
                "sellers": {
                  "changes_snapshot_id": 6608875651304288148,
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
              "bronze": "d2cb4c41-8b21-4c08-a958-f9ce3bca082e",
              "silver": "1d222c0b-c1b4-4b58-b53a-bf98377f0383,370efb6b-2b3e-4cca-82c9-8dd88f31c222,42cd65b6-c4d1-4c7e-9861-9300bb90d109,4c2cb83d-bb8c-4365-a430-69698094baaa,5eda7c75-a0d2-45ed-bd65-e4f49ef579dc,66c4be43-fbd7-4859-8943-5d1403b70b0c,6acc1c44-9a75-4954-9dea-fb3cb6bbcab1,92e0546a-1402-42a1-b305-2e2cda3fae3e,af4851ce-95a8-4b73-9c55-d15cfa78c114,ffccf33d-a5e2-4ef2-a942-ac219b28c554"
            },
            "old_query_ids": {
              "bronze": "d2cb4c41-8b21-4c08-a958-f9ce3bca082e",
              "silver": "1d222c0b-c1b4-4b58-b53a-bf98377f0383,370efb6b-2b3e-4cca-82c9-8dd88f31c222,42cd65b6-c4d1-4c7e-9861-9300bb90d109,4c2cb83d-bb8c-4365-a430-69698094baaa,5eda7c75-a0d2-45ed-bd65-e4f49ef579dc,66c4be43-fbd7-4859-8943-5d1403b70b0c,6acc1c44-9a75-4954-9dea-fb3cb6bbcab1,92e0546a-1402-42a1-b305-2e2cda3fae3e,af4851ce-95a8-4b73-9c55-d15cfa78c114,ffccf33d-a5e2-4ef2-a942-ac219b28c554"
            },
            "restart_barrier_at_utc": "2026-08-03T17:56:22.274596+00:00",
            "status": "ready",
            "status_files": {
              "bronze": {
                "query_count": 1,
                "updated_at_utc": "2026-08-03T17:58:25.643960616Z"
              },
              "silver": {
                "query_count": 10,
                "updated_at_utc": "2026-08-03T17:58:33.183712041Z"
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
          "duration_seconds": 92.062,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"wait-caught-up\", \"status\": \"ready\"}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 94.199,
      "gate": "05-caught-up",
      "status": "PASS",
      "timestamp": "2026-08-03T18:00:13.206853+00:00"
    },
    "06-serving-sync": {
      "assertions": [
        {
          "detail": "{\"command\": \"start-serving\", \"profiles\": [\"platform\", \"serving\"], \"required_services\": [\"clickhouse\", \"airflow\"], \"status\": \"ready\"}",
          "name": "start_serving",
          "status": "PASS"
        },
        {
          "detail": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_v_final_candidate_retry_crud_publish_1061cec69b2a\", \"dbt_result\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 1, \\\"sync_run_id\\\": \\\"sync-00000000000000000001\\\"}\"], \"exception\": null, \"results\": [{\"execution_time\": 0.09076666831970215, \"node\": \"stg_customers_current\", \"status\": \"success\"}, {\"execution_time\": 0.05254626274108887, \"node\": \"stg_customers_events\", \"status\": \"success\"}, {\"execution_time\": 0.03966331481933594, \"node\": \"stg_order_items_current\", \"status\": \"success\"}, {\"execution_time\": 0.0388026237487793, \"node\": \"stg_order_payments_current\", \"status\": \"success\"}, {\"execution_time\": 0.0357668399810791, \"node\": \"stg_orders_current\", \"status\": \"success\"}, {\"execution_time\": 0.03421139717102051, \"node\": \"stg_product_category_translation_events\", \"status\": \"success\"}, {\"execution_time\": 0.03603053092956543, \"node\": \"stg_products_events\", \"status\": \"success\"}, {\"execution_time\": 0.036414384841918945, \"node\": \"stg_sellers_current\", \"status\": \"success\"}, {\"execution_time\": 0.2738349437713623, \"node\": \"customer_scd2_collapses_identical_update_and_closes_on_delete\", \"status\": \"pass\"}, {\"execution_time\": 0.18772459030151367, \"node\": \"dim_customer_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.18564677238464355, \"node\": \"payment_allocation_is_proportional_at_item_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.20893478393554688, \"node\": \"zero_gross_order_has_null_payment_allocation\", \"status\": \"pass\"}, {\"execution_time\": 0.10658645629882812, \"node\": \"dim_date\", \"status\": \"success\"}, {\"execution_time\": 0.07665824890136719, \"node\": \"dim_order_status\", \"status\": \"success\"}, {\"execution_time\": 0.4323887825012207, \"node\": \"product_translation_does_not_resurrect_an_old_category\", \"status\": \"pass\"}, {\"execution_time\": 0.18606805801391602, \"node\": \"dim_product_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.08812999725341797, \"node\": \"dim_seller\", \"status\": \"success\"}, {\"execution_time\": 0.07069587707519531, \"node\": \"assert_customer_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.043929338455200195, \"node\": \"candidate_not_null_dim_customer_scd2_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04565238952636719, \"node\": \"candidate_not_null_dim_customer_scd2_customer_unique_id\", \"status\": \"pass\"}, {\"execution_time\": 0.04576754570007324, \"node\": \"candidate_not_null_dim_customer_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.04192304611206055, \"node\": \"unique_combination_of_columns_dim_customer_scd2_sync_run_seq__customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.06023144721984863, \"node\": \"assert_payment_allocations_balance\", \"status\": \"pass\"}, {\"execution_time\": 0.03658270835876465, \"node\": \"candidate_not_null_dim_date_date_day\", \"status\": \"pass\"}, {\"execution_time\": 0.04164004325866699, \"node\": \"candidate_not_null_dim_date_date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03860163688659668, \"node\": \"candidate_not_null_dim_date_sync_run_seq\", \"status\": \"pass\"}, {\"execution_time\": 0.04183506965637207, \"node\": \"unique_combination_of_columns_dim_date_sync_run_seq__date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03399014472961426, \"node\": \"candidate_not_null_dim_order_status_order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.03360152244567871, \"node\": \"candidate_not_null_dim_order_status_order_status_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03590726852416992, \"node\": \"unique_combination_of_columns_dim_order_status_sync_run_seq__order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.03888583183288574, \"node\": \"assert_product_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.03624391555786133, \"node\": \"candidate_not_null_dim_product_scd2_product_id\", \"status\": \"pass\"}, {\"execution_time\": 0.061516761779785156, \"node\": \"candidate_not_null_dim_product_scd2_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04764270782470703, \"node\": \"candidate_not_null_dim_product_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.047312259674072266, \"node\": \"unique_combination_of_columns_dim_product_scd2_sync_run_seq__product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.0380091667175293, \"node\": \"candidate_not_null_dim_seller_seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.036692142486572266, \"node\": \"candidate_not_null_dim_seller_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03626227378845215, \"node\": \"unique_combination_of_columns_dim_seller_sync_run_seq__seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.2722947597503662, \"node\": \"fact_order_items\", \"status\": \"success\"}, {\"execution_time\": 0.03653383255004883, \"node\": \"assert_fact_order_items_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.0357973575592041, \"node\": \"candidate_not_null_fact_order_items_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03686046600341797, \"node\": \"candidate_not_null_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.07590508460998535, \"node\": \"candidate_not_null_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.05120134353637695, \"node\": \"candidate_not_null_fact_order_items_order_item_key\", \"status\": \"pass\"}, {\"execution_time\": 0.1313309669494629, \"node\": \"candidate_not_null_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.04657602310180664, \"node\": \"candidate_not_null_fact_order_items_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04918932914733887, \"node\": \"candidate_not_null_fact_order_items_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05025172233581543, \"node\": \"candidate_relationships_fact_order_items_customer_key__customer_key__ref_dim_customer_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.05992579460144043, \"node\": \"candidate_relationships_fact_order_items_product_key__product_key__ref_dim_product_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.052722930908203125, \"node\": \"candidate_relationships_fact_order_items_seller_key__seller_key__ref_dim_seller_\", \"status\": \"pass\"}, {\"execution_time\": 0.04258918762207031, \"node\": \"non_negative_fact_order_items_allocated_payment_value\", \"status\": \"pass\"}, {\"execution_time\": 0.0449070930480957, \"node\": \"non_negative_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.049566030502319336, \"node\": \"non_negative_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.04974722862243652, \"node\": \"non_negative_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.04952359199523926, \"node\": \"unique_combination_of_columns_fact_order_items_sync_run_seq__order_id__order_item_id\", \"status\": \"pass\"}, {\"execution_time\": 0.12252211570739746, \"node\": \"mart_daily_revenue\", \"status\": \"success\"}, {\"execution_time\": 0.09958457946777344, \"node\": \"mart_monthly_arpu\", \"status\": \"success\"}, {\"execution_time\": 0.04856562614440918, \"node\": \"assert_daily_revenue_components\", \"status\": \"pass\"}, {\"execution_time\": 0.06584024429321289, \"node\": \"candidate_not_null_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.06390714645385742, \"node\": \"candidate_not_null_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.10396170616149902, \"node\": \"candidate_not_null_mart_daily_revenue_order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.06387686729431152, \"node\": \"candidate_not_null_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.07967257499694824, \"node\": \"non_negative_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.06560516357421875, \"node\": \"non_negative_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.05800914764404297, \"node\": \"non_negative_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.06991958618164062, \"node\": \"unique_combination_of_columns_mart_daily_revenue_sync_run_seq__order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.0611569881439209, \"node\": \"assert_monthly_arpu_formulas\", \"status\": \"pass\"}, {\"execution_time\": 0.05181431770324707, \"node\": \"candidate_not_null_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.05751800537109375, \"node\": \"candidate_not_null_mart_monthly_arpu_order_month\", \"status\": \"pass\"}, {\"execution_time\": 0.05154538154602051, \"node\": \"candidate_not_null_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.05441999435424805, \"node\": \"candidate_not_null_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.06426048278808594, \"node\": \"non_negative_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.04549860954284668, \"node\": \"non_negative_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.05490517616271973, \"node\": \"non_negative_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.0427403450012207, \"node\": \"unique_combination_of_columns_mart_monthly_arpu_sync_run_seq__order_month\", \"status\": \"pass\"}], \"selector\": \"serving_candidate\", \"status_counts\": {\"pass\": 59, \"success\": 16}, \"success\": true, \"vars\": {\"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1}}, \"expected_entity_counts\": {\"customers\": 9, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 89, \"iceberg_snapshot_ids\": {\"customers\": 3770751687399586214, \"order_items\": 8333618748302751604, \"order_payments\": 2342546804373807134, \"order_reviews\": 1873788046910446323, \"orders\": 2860036943269124164, \"product_category_translation\": 2510271481881063845, \"products\": 6434977924513876130, \"sellers\": 6608875651304288148}, \"is_noop\": false, \"materialized_entity_counts\": {\"customers\": 9, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"materialized_event_count\": 89, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1, \"sync_run_status\": \"SUCCEEDED\", \"target_offsets\": {\"olist_cdc.olist_oltp.customers:0\": 8, \"olist_cdc.olist_oltp.order_items:0\": 5, \"olist_cdc.olist_oltp.order_items:1\": 5, \"olist_cdc.olist_oltp.order_items:2\": 6, \"olist_cdc.olist_oltp.order_payments:0\": 5, \"olist_cdc.olist_oltp.order_payments:1\": 4, \"olist_cdc.olist_oltp.order_payments:2\": 4, \"olist_cdc.olist_oltp.order_reviews:0\": 5, \"olist_cdc.olist_oltp.order_reviews:1\": 4, \"olist_cdc.olist_oltp.order_reviews:2\": 2, \"olist_cdc.olist_oltp.orders:0\": 3, \"olist_cdc.olist_oltp.orders:1\": 4, \"olist_cdc.olist_oltp.orders:2\": 4, \"olist_cdc.olist_oltp.product_category_translation:0\": 4, \"olist_cdc.olist_oltp.products:0\": 7, \"olist_cdc.olist_oltp.sellers:0\": 3}, \"target_transaction_id\": \"file=binlog.000002,pos=18435\"}",
          "name": "sync_serving_crud",
          "status": "PASS"
        },
        {
          "detail": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_v_final_candidate_retry_crud_repeat_1061cec69b2a\", \"dbt_result\": null, \"expected_entity_counts\": {\"customers\": 0, \"order_items\": 0, \"order_payments\": 0, \"order_reviews\": 0, \"orders\": 0, \"product_category_translation\": 0, \"products\": 0, \"sellers\": 0}, \"expected_event_count\": 0, \"iceberg_snapshot_ids\": {\"customers\": 3770751687399586214, \"order_items\": 8333618748302751604, \"order_payments\": 2342546804373807134, \"order_reviews\": 1873788046910446323, \"orders\": 2860036943269124164, \"product_category_translation\": 2510271481881063845, \"products\": 6434977924513876130, \"sellers\": 6608875651304288148}, \"is_noop\": true, \"materialized_entity_counts\": {\"customers\": 0, \"order_items\": 0, \"order_payments\": 0, \"order_reviews\": 0, \"orders\": 0, \"product_category_translation\": 0, \"products\": 0, \"sellers\": 0}, \"materialized_event_count\": 0, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000002\", \"sync_run_seq\": 2, \"sync_run_status\": \"NOOP\", \"target_offsets\": {}, \"target_transaction_id\": \"file=binlog.000002,pos=18435\"}",
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
          "stage_v_final_candidate_retry_crud_publish_1061cec69b2a",
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
          "stage_v_final_candidate_retry_crud_repeat_1061cec69b2a",
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
          "duration_seconds": 157.984,
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
            "stage_v_final_candidate_retry_crud_publish_1061cec69b2a",
            "--timeout",
            "1800"
          ],
          "duration_seconds": 26.016,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_v_final_candidate_retry_crud_publish_1061cec69b2a\", \"dbt_result\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 1, \\\"sync_run_id\\\": \\\"sync-00000000000000000001\\\"}\"], \"exception\": null, \"results\": [{\"execution_time\": 0.09076666831970215, \"node\": \"stg_customers_current\", \"status\": \"success\"}, {\"execution_time\": 0.05254626274108887, \"node\": \"stg_customers_events\", \"status\": \"success\"}, {\"execution_time\": 0.03966331481933594, \"node\": \"stg_order_items_current\", \"status\": \"success\"}, {\"execution_time\": 0.0388026237487793, \"node\": \"stg_order_payments_current\", \"status\": \"success\"}, {\"execution_time\": 0.0357668399810791, \"node\": \"stg_orders_current\", \"status\": \"success\"}, {\"execution_time\": 0.03421139717102051, \"node\": \"stg_product_category_translation_events\", \"status\": \"success\"}, {\"execution_time\": 0.03603053092956543, \"node\": \"stg_products_events\", \"status\": \"success\"}, {\"execution_time\": 0.036414384841918945, \"node\": \"stg_sellers_current\", \"status\": \"success\"}, {\"execution_time\": 0.2738349437713623, \"node\": \"customer_scd2_collapses_identical_update_and_closes_on_delete\", \"status\": \"pass\"}, {\"execution_time\": 0.18772459030151367, \"node\": \"dim_customer_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.18564677238464355, \"node\": \"payment_allocation_is_proportional_at_item_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.20893478393554688, \"node\": \"zero_gross_order_has_null_payment_allocation\", \"status\": \"pass\"}, {\"execution_time\": 0.10658645629882812, \"node\": \"dim_date\", \"status\": \"success\"}, {\"execution_time\": 0.07665824890136719, \"node\": \"dim_order_status\", \"status\": \"success\"}, {\"execution_time\": 0.4323887825012207, \"node\": \"product_translation_does_not_resurrect_an_old_category\", \"status\": \"pass\"}, {\"execution_time\": 0.18606805801391602, \"node\": \"dim_product_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.08812999725341797, \"node\": \"dim_seller\", \"status\": \"success\"}, {\"execution_time\": 0.07069587707519531, \"node\": \"assert_customer_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.043929338455200195, \"node\": \"candidate_not_null_dim_customer_scd2_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04565238952636719, \"node\": \"candidate_not_null_dim_customer_scd2_customer_unique_id\", \"status\": \"pass\"}, {\"execution_time\": 0.04576754570007324, \"node\": \"candidate_not_null_dim_customer_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.04192304611206055, \"node\": \"unique_combination_of_columns_dim_customer_scd2_sync_run_seq__customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.06023144721984863, \"node\": \"assert_payment_allocations_balance\", \"status\": \"pass\"}, {\"execution_time\": 0.03658270835876465, \"node\": \"candidate_not_null_dim_date_date_day\", \"status\": \"pass\"}, {\"execution_time\": 0.04164004325866699, \"node\": \"candidate_not_null_dim_date_date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03860163688659668, \"node\": \"candidate_not_null_dim_date_sync_run_seq\", \"status\": \"pass\"}, {\"execution_time\": 0.04183506965637207, \"node\": \"unique_combination_of_columns_dim_date_sync_run_seq__date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03399014472961426, \"node\": \"candidate_not_null_dim_order_status_order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.03360152244567871, \"node\": \"candidate_not_null_dim_order_status_order_status_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03590726852416992, \"node\": \"unique_combination_of_columns_dim_order_status_sync_run_seq__order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.03888583183288574, \"node\": \"assert_product_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.03624391555786133, \"node\": \"candidate_not_null_dim_product_scd2_product_id\", \"status\": \"pass\"}, {\"execution_time\": 0.061516761779785156, \"node\": \"candidate_not_null_dim_product_scd2_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04764270782470703, \"node\": \"candidate_not_null_dim_product_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.047312259674072266, \"node\": \"unique_combination_of_columns_dim_product_scd2_sync_run_seq__product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.0380091667175293, \"node\": \"candidate_not_null_dim_seller_seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.036692142486572266, \"node\": \"candidate_not_null_dim_seller_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03626227378845215, \"node\": \"unique_combination_of_columns_dim_seller_sync_run_seq__seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.2722947597503662, \"node\": \"fact_order_items\", \"status\": \"success\"}, {\"execution_time\": 0.03653383255004883, \"node\": \"assert_fact_order_items_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.0357973575592041, \"node\": \"candidate_not_null_fact_order_items_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03686046600341797, \"node\": \"candidate_not_null_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.07590508460998535, \"node\": \"candidate_not_null_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.05120134353637695, \"node\": \"candidate_not_null_fact_order_items_order_item_key\", \"status\": \"pass\"}, {\"execution_time\": 0.1313309669494629, \"node\": \"candidate_not_null_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.04657602310180664, \"node\": \"candidate_not_null_fact_order_items_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04918932914733887, \"node\": \"candidate_not_null_fact_order_items_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05025172233581543, \"node\": \"candidate_relationships_fact_order_items_customer_key__customer_key__ref_dim_customer_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.05992579460144043, \"node\": \"candidate_relationships_fact_order_items_product_key__product_key__ref_dim_product_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.052722930908203125, \"node\": \"candidate_relationships_fact_order_items_seller_key__seller_key__ref_dim_seller_\", \"status\": \"pass\"}, {\"execution_time\": 0.04258918762207031, \"node\": \"non_negative_fact_order_items_allocated_payment_value\", \"status\": \"pass\"}, {\"execution_time\": 0.0449070930480957, \"node\": \"non_negative_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.049566030502319336, \"node\": \"non_negative_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.04974722862243652, \"node\": \"non_negative_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.04952359199523926, \"node\": \"unique_combination_of_columns_fact_order_items_sync_run_seq__order_id__order_item_id\", \"status\": \"pass\"}, {\"execution_time\": 0.12252211570739746, \"node\": \"mart_daily_revenue\", \"status\": \"success\"}, {\"execution_time\": 0.09958457946777344, \"node\": \"mart_monthly_arpu\", \"status\": \"success\"}, {\"execution_time\": 0.04856562614440918, \"node\": \"assert_daily_revenue_components\", \"status\": \"pass\"}, {\"execution_time\": 0.06584024429321289, \"node\": \"candidate_not_null_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.06390714645385742, \"node\": \"candidate_not_null_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.10396170616149902, \"node\": \"candidate_not_null_mart_daily_revenue_order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.06387686729431152, \"node\": \"candidate_not_null_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.07967257499694824, \"node\": \"non_negative_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.06560516357421875, \"node\": \"non_negative_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.05800914764404297, \"node\": \"non_negative_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.06991958618164062, \"node\": \"unique_combination_of_columns_mart_daily_revenue_sync_run_seq__order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.0611569881439209, \"node\": \"assert_monthly_arpu_formulas\", \"status\": \"pass\"}, {\"execution_time\": 0.05181431770324707, \"node\": \"candidate_not_null_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.05751800537109375, \"node\": \"candidate_not_null_mart_monthly_arpu_order_month\", \"status\": \"pass\"}, {\"execution_time\": 0.05154538154602051, \"node\": \"candidate_not_null_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.05441999435424805, \"node\": \"candidate_not_null_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.06426048278808594, \"node\": \"non_negative_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.04549860954284668, \"node\": \"non_negative_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.05490517616271973, \"node\": \"non_negative_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.0427403450012207, \"node\": \"unique_combination_of_columns_mart_monthly_arpu_sync_run_seq__order_month\", \"status\": \"pass\"}], \"selector\": \"serving_candidate\", \"status_counts\": {\"pass\": 59, \"success\": 16}, \"success\": true, \"vars\": {\"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1}}, \"expected_entity_counts\": {\"customers\": 9, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 89, \"iceberg_snapshot_ids\": {\"customers\": 3770751687399586214, \"order_items\": 8333618748302751604, \"order_payments\": 2342546804373807134, \"order_reviews\": 1873788046910446323, \"orders\": 2860036943269124164, \"product_category_translation\": 2510271481881063845, \"products\": 6434977924513876130, \"sellers\": 6608875651304288148}, \"is_noop\": false, \"materialized_entity_counts\": {\"customers\": 9, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"materialized_event_count\": 89, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1, \"sync_run_status\": \"SUCCEEDED\", \"target_offsets\": {\"olist_cdc.olist_oltp.customers:0\": 8, \"olist_cdc.olist_oltp.order_items:0\": 5, \"olist_cdc.olist_oltp.order_items:1\": 5, \"olist_cdc.olist_oltp.order_items:2\": 6, \"olist_cdc.olist_oltp.order_payments:0\": 5, \"olist_cdc.olist_oltp.order_payments:1\": 4, \"olist_cdc.olist_oltp.order_payments:2\": 4, \"olist_cdc.olist_oltp.order_reviews:0\": 5, \"olist_cdc.olist_oltp.order_reviews:1\": 4, \"olist_cdc.olist_oltp.order_reviews:2\": 2, \"olist_cdc.olist_oltp.orders:0\": 3, \"olist_cdc.olist_oltp.orders:1\": 4, \"olist_cdc.olist_oltp.orders:2\": 4, \"olist_cdc.olist_oltp.product_category_translation:0\": 4, \"olist_cdc.olist_oltp.products:0\": 7, \"olist_cdc.olist_oltp.sellers:0\": 3}, \"target_transaction_id\": \"file=binlog.000002,pos=18435\"}\n",
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
            "stage_v_final_candidate_retry_crud_repeat_1061cec69b2a",
            "--timeout",
            "1800"
          ],
          "duration_seconds": 5.625,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_v_final_candidate_retry_crud_repeat_1061cec69b2a\", \"dbt_result\": null, \"expected_entity_counts\": {\"customers\": 0, \"order_items\": 0, \"order_payments\": 0, \"order_reviews\": 0, \"orders\": 0, \"product_category_translation\": 0, \"products\": 0, \"sellers\": 0}, \"expected_event_count\": 0, \"iceberg_snapshot_ids\": {\"customers\": 3770751687399586214, \"order_items\": 8333618748302751604, \"order_payments\": 2342546804373807134, \"order_reviews\": 1873788046910446323, \"orders\": 2860036943269124164, \"product_category_translation\": 2510271481881063845, \"products\": 6434977924513876130, \"sellers\": 6608875651304288148}, \"is_noop\": true, \"materialized_entity_counts\": {\"customers\": 0, \"order_items\": 0, \"order_payments\": 0, \"order_reviews\": 0, \"orders\": 0, \"product_category_translation\": 0, \"products\": 0, \"sellers\": 0}, \"materialized_event_count\": 0, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000002\", \"sync_run_seq\": 2, \"sync_run_status\": \"NOOP\", \"target_offsets\": {}, \"target_transaction_id\": \"file=binlog.000002,pos=18435\"}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 189.629,
      "gate": "06-serving-sync",
      "status": "PASS",
      "timestamp": "2026-08-03T18:03:22.839806+00:00"
    },
    "07-dbt-and-stable-views": {
      "assertions": [
        {
          "detail": "{\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 216 packages in 1ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"m/test_local_lab_live_readiness.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/lakehouse_platform/test_local_lab_profile_boundaries.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"All checks passed!\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"91 files already formatted\", \"exit_code\": 0, \"status\": \"passed\"}], \"command\": \"validate\", \"status\": \"ready\"}",
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
                  "diagnostic": "Resolved 216 packages in 1ms",
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
                  "diagnostic": "m/test_local_lab_live_readiness.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/lakehouse_platform/test_local_lab_profile_boundaries.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it",
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
                  "diagnostic": "91 files already formatted",
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
          "duration_seconds": 1.328,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 216 packages in 1ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"m/test_local_lab_live_readiness.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/lakehouse_platform/test_local_lab_profile_boundaries.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"All checks passed!\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"91 files already formatted\", \"exit_code\": 0, \"status\": \"passed\"}], \"command\": \"validate\", \"status\": \"ready\"}\n",
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
          "duration_seconds": 2.39,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"validate-serving\", \"current_views\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"dbt\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 1, \\\"sync_run_id\\\": \\\"sync-00000000000000000001\\\"}\"], \"result_count\": 75, \"status_counts\": {\"pass\": 59, \"success\": 16}}, \"gold_views\": {\"dim_customer_scd2\": {\"candidate\": 7, \"stable\": 7}, \"dim_date\": {\"candidate\": 46, \"stable\": 46}, \"dim_order_status\": {\"candidate\": 2, \"stable\": 2}, \"dim_product_scd2\": {\"candidate\": 8, \"stable\": 8}, \"dim_seller\": {\"candidate\": 4, \"stable\": 4}, \"fact_order_items\": {\"candidate\": 18, \"stable\": 18}, \"mart_daily_revenue\": {\"candidate\": 13, \"stable\": 13}, \"mart_monthly_arpu\": {\"candidate\": 7, \"stable\": 7}}, \"static_validation\": {\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 216 packages in 1ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"m/test_local_lab_live_readiness.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/lakehouse_platform/test_local_lab_profile_boundaries.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"All checks passed!\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"91 files already formatted\", \"exit_code\": 0, \"status\": \"passed\"}], \"status\": \"ready\"}, \"status\": \"ready\", \"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 3.71,
      "gate": "07-dbt-and-stable-views",
      "status": "PASS",
      "timestamp": "2026-08-03T18:03:26.553265+00:00"
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
          "detail": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_v_final_candidate_retry_schema_publish_1061cec69b2a\", \"dbt_result\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 3, \\\"sync_run_id\\\": \\\"sync-00000000000000000003\\\"}\"], \"exception\": null, \"results\": [{\"execution_time\": 0.14066648483276367, \"node\": \"stg_customers_current\", \"status\": \"success\"}, {\"execution_time\": 0.0592503547668457, \"node\": \"stg_customers_events\", \"status\": \"success\"}, {\"execution_time\": 0.05474710464477539, \"node\": \"stg_order_items_current\", \"status\": \"success\"}, {\"execution_time\": 0.059609174728393555, \"node\": \"stg_order_payments_current\", \"status\": \"success\"}, {\"execution_time\": 0.06047320365905762, \"node\": \"stg_orders_current\", \"status\": \"success\"}, {\"execution_time\": 0.05511593818664551, \"node\": \"stg_product_category_translation_events\", \"status\": \"success\"}, {\"execution_time\": 0.052350521087646484, \"node\": \"stg_products_events\", \"status\": \"success\"}, {\"execution_time\": 0.06836223602294922, \"node\": \"stg_sellers_current\", \"status\": \"success\"}, {\"execution_time\": 0.35019588470458984, \"node\": \"customer_scd2_collapses_identical_update_and_closes_on_delete\", \"status\": \"pass\"}, {\"execution_time\": 0.25503063201904297, \"node\": \"dim_customer_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.15116167068481445, \"node\": \"payment_allocation_is_proportional_at_item_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.13418984413146973, \"node\": \"zero_gross_order_has_null_payment_allocation\", \"status\": \"pass\"}, {\"execution_time\": 0.17676115036010742, \"node\": \"dim_date\", \"status\": \"success\"}, {\"execution_time\": 0.14522075653076172, \"node\": \"dim_order_status\", \"status\": \"success\"}, {\"execution_time\": 0.4157271385192871, \"node\": \"product_translation_does_not_resurrect_an_old_category\", \"status\": \"pass\"}, {\"execution_time\": 0.19464731216430664, \"node\": \"dim_product_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.1123666763305664, \"node\": \"dim_seller\", \"status\": \"success\"}, {\"execution_time\": 0.05431675910949707, \"node\": \"assert_customer_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.033476829528808594, \"node\": \"candidate_not_null_dim_customer_scd2_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03480696678161621, \"node\": \"candidate_not_null_dim_customer_scd2_customer_unique_id\", \"status\": \"pass\"}, {\"execution_time\": 0.03325033187866211, \"node\": \"candidate_not_null_dim_customer_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.03436422348022461, \"node\": \"unique_combination_of_columns_dim_customer_scd2_sync_run_seq__customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.061270952224731445, \"node\": \"assert_payment_allocations_balance\", \"status\": \"pass\"}, {\"execution_time\": 0.03578329086303711, \"node\": \"candidate_not_null_dim_date_date_day\", \"status\": \"pass\"}, {\"execution_time\": 0.060128211975097656, \"node\": \"candidate_not_null_dim_date_date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.0366663932800293, \"node\": \"candidate_not_null_dim_date_sync_run_seq\", \"status\": \"pass\"}, {\"execution_time\": 0.034572601318359375, \"node\": \"unique_combination_of_columns_dim_date_sync_run_seq__date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03233909606933594, \"node\": \"candidate_not_null_dim_order_status_order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.03597140312194824, \"node\": \"candidate_not_null_dim_order_status_order_status_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04122519493103027, \"node\": \"unique_combination_of_columns_dim_order_status_sync_run_seq__order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.045701026916503906, \"node\": \"assert_product_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.043515920639038086, \"node\": \"candidate_not_null_dim_product_scd2_product_id\", \"status\": \"pass\"}, {\"execution_time\": 0.04411196708679199, \"node\": \"candidate_not_null_dim_product_scd2_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04121279716491699, \"node\": \"candidate_not_null_dim_product_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.10631299018859863, \"node\": \"unique_combination_of_columns_dim_product_scd2_sync_run_seq__product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03692626953125, \"node\": \"candidate_not_null_dim_seller_seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.035135507583618164, \"node\": \"candidate_not_null_dim_seller_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.039649009704589844, \"node\": \"unique_combination_of_columns_dim_seller_sync_run_seq__seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.3188445568084717, \"node\": \"fact_order_items\", \"status\": \"success\"}, {\"execution_time\": 0.03192329406738281, \"node\": \"assert_fact_order_items_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.03603243827819824, \"node\": \"candidate_not_null_fact_order_items_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.033876895904541016, \"node\": \"candidate_not_null_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.04268217086791992, \"node\": \"candidate_not_null_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.04243040084838867, \"node\": \"candidate_not_null_fact_order_items_order_item_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03702402114868164, \"node\": \"candidate_not_null_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.03337597846984863, \"node\": \"candidate_not_null_fact_order_items_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.037862300872802734, \"node\": \"candidate_not_null_fact_order_items_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04497575759887695, \"node\": \"candidate_relationships_fact_order_items_customer_key__customer_key__ref_dim_customer_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.041362762451171875, \"node\": \"candidate_relationships_fact_order_items_product_key__product_key__ref_dim_product_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.03935861587524414, \"node\": \"candidate_relationships_fact_order_items_seller_key__seller_key__ref_dim_seller_\", \"status\": \"pass\"}, {\"execution_time\": 0.0341184139251709, \"node\": \"non_negative_fact_order_items_allocated_payment_value\", \"status\": \"pass\"}, {\"execution_time\": 0.03432035446166992, \"node\": \"non_negative_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.03993344306945801, \"node\": \"non_negative_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.03924822807312012, \"node\": \"non_negative_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.04311084747314453, \"node\": \"unique_combination_of_columns_fact_order_items_sync_run_seq__order_id__order_item_id\", \"status\": \"pass\"}, {\"execution_time\": 0.12189912796020508, \"node\": \"mart_daily_revenue\", \"status\": \"success\"}, {\"execution_time\": 0.11654090881347656, \"node\": \"mart_monthly_arpu\", \"status\": \"success\"}, {\"execution_time\": 0.0373377799987793, \"node\": \"assert_daily_revenue_components\", \"status\": \"pass\"}, {\"execution_time\": 0.06897139549255371, \"node\": \"candidate_not_null_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.0567021369934082, \"node\": \"candidate_not_null_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.0562434196472168, \"node\": \"candidate_not_null_mart_daily_revenue_order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.04588460922241211, \"node\": \"candidate_not_null_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.03491330146789551, \"node\": \"non_negative_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.03436875343322754, \"node\": \"non_negative_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.036965370178222656, \"node\": \"non_negative_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.03579521179199219, \"node\": \"unique_combination_of_columns_mart_daily_revenue_sync_run_seq__order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.03216671943664551, \"node\": \"assert_monthly_arpu_formulas\", \"status\": \"pass\"}, {\"execution_time\": 0.03233504295349121, \"node\": \"candidate_not_null_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.033797502517700195, \"node\": \"candidate_not_null_mart_monthly_arpu_order_month\", \"status\": \"pass\"}, {\"execution_time\": 0.035668373107910156, \"node\": \"candidate_not_null_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.03580665588378906, \"node\": \"candidate_not_null_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.040764570236206055, \"node\": \"non_negative_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.04141879081726074, \"node\": \"non_negative_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.03847217559814453, \"node\": \"non_negative_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.03774738311767578, \"node\": \"unique_combination_of_columns_mart_monthly_arpu_sync_run_seq__order_month\", \"status\": \"pass\"}], \"selector\": \"serving_candidate\", \"status_counts\": {\"pass\": 59, \"success\": 16}, \"success\": true, \"vars\": {\"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3}}, \"expected_entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 90, \"iceberg_snapshot_ids\": {\"customers\": 8945732834443551666, \"order_items\": 8333618748302751604, \"order_payments\": 2342546804373807134, \"order_reviews\": 1873788046910446323, \"orders\": 2860036943269124164, \"product_category_translation\": 2510271481881063845, \"products\": 6434977924513876130, \"sellers\": 6608875651304288148}, \"is_noop\": false, \"materialized_entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"materialized_event_count\": 90, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3, \"sync_run_status\": \"SUCCEEDED\", \"target_offsets\": {\"olist_cdc.olist_oltp.customers:0\": 9, \"olist_cdc.olist_oltp.order_items:0\": 5, \"olist_cdc.olist_oltp.order_items:1\": 5, \"olist_cdc.olist_oltp.order_items:2\": 6, \"olist_cdc.olist_oltp.order_payments:0\": 5, \"olist_cdc.olist_oltp.order_payments:1\": 4, \"olist_cdc.olist_oltp.order_payments:2\": 4, \"olist_cdc.olist_oltp.order_reviews:0\": 5, \"olist_cdc.olist_oltp.order_reviews:1\": 4, \"olist_cdc.olist_oltp.order_reviews:2\": 2, \"olist_cdc.olist_oltp.orders:0\": 3, \"olist_cdc.olist_oltp.orders:1\": 4, \"olist_cdc.olist_oltp.orders:2\": 4, \"olist_cdc.olist_oltp.product_category_translation:0\": 4, \"olist_cdc.olist_oltp.products:0\": 7, \"olist_cdc.olist_oltp.sellers:0\": 3}, \"target_transaction_id\": \"file=binlog.000002,pos=22085\"}",
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
              "transaction_id": "file=binlog.000002,pos=22085",
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
                  "changes_snapshot_id": 8945732834443551666,
                  "entity": "customers",
                  "last_kafka_offset": 9,
                  "status": "COMMITTED"
                },
                "order_items": {
                  "changes_snapshot_id": 8333618748302751604,
                  "entity": "order_items",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "order_payments": {
                  "changes_snapshot_id": 2342546804373807134,
                  "entity": "order_payments",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "order_reviews": {
                  "changes_snapshot_id": 1873788046910446323,
                  "entity": "order_reviews",
                  "last_kafka_offset": 2,
                  "status": "COMMITTED"
                },
                "orders": {
                  "changes_snapshot_id": 2860036943269124164,
                  "entity": "orders",
                  "last_kafka_offset": 3,
                  "status": "COMMITTED"
                },
                "product_category_translation": {
                  "changes_snapshot_id": 2510271481881063845,
                  "entity": "product_category_translation",
                  "last_kafka_offset": 4,
                  "status": "COMMITTED"
                },
                "products": {
                  "changes_snapshot_id": 6434977924513876130,
                  "entity": "products",
                  "last_kafka_offset": 7,
                  "status": "COMMITTED"
                },
                "sellers": {
                  "changes_snapshot_id": 6608875651304288148,
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
                  "diagnostic": "Resolved 216 packages in 1ms",
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
                  "diagnostic": "m/test_local_lab_live_readiness.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/lakehouse_platform/test_local_lab_profile_boundaries.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it",
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
                  "diagnostic": "91 files already formatted",
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
          "stage_v_final_candidate_retry_schema_publish_1061cec69b2a",
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
          "duration_seconds": 34.266,
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
            "stage_v_final_candidate_retry_schema_publish_1061cec69b2a",
            "--timeout",
            "1800"
          ],
          "duration_seconds": 20.703,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_v_final_candidate_retry_schema_publish_1061cec69b2a\", \"dbt_result\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 3, \\\"sync_run_id\\\": \\\"sync-00000000000000000003\\\"}\"], \"exception\": null, \"results\": [{\"execution_time\": 0.14066648483276367, \"node\": \"stg_customers_current\", \"status\": \"success\"}, {\"execution_time\": 0.0592503547668457, \"node\": \"stg_customers_events\", \"status\": \"success\"}, {\"execution_time\": 0.05474710464477539, \"node\": \"stg_order_items_current\", \"status\": \"success\"}, {\"execution_time\": 0.059609174728393555, \"node\": \"stg_order_payments_current\", \"status\": \"success\"}, {\"execution_time\": 0.06047320365905762, \"node\": \"stg_orders_current\", \"status\": \"success\"}, {\"execution_time\": 0.05511593818664551, \"node\": \"stg_product_category_translation_events\", \"status\": \"success\"}, {\"execution_time\": 0.052350521087646484, \"node\": \"stg_products_events\", \"status\": \"success\"}, {\"execution_time\": 0.06836223602294922, \"node\": \"stg_sellers_current\", \"status\": \"success\"}, {\"execution_time\": 0.35019588470458984, \"node\": \"customer_scd2_collapses_identical_update_and_closes_on_delete\", \"status\": \"pass\"}, {\"execution_time\": 0.25503063201904297, \"node\": \"dim_customer_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.15116167068481445, \"node\": \"payment_allocation_is_proportional_at_item_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.13418984413146973, \"node\": \"zero_gross_order_has_null_payment_allocation\", \"status\": \"pass\"}, {\"execution_time\": 0.17676115036010742, \"node\": \"dim_date\", \"status\": \"success\"}, {\"execution_time\": 0.14522075653076172, \"node\": \"dim_order_status\", \"status\": \"success\"}, {\"execution_time\": 0.4157271385192871, \"node\": \"product_translation_does_not_resurrect_an_old_category\", \"status\": \"pass\"}, {\"execution_time\": 0.19464731216430664, \"node\": \"dim_product_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.1123666763305664, \"node\": \"dim_seller\", \"status\": \"success\"}, {\"execution_time\": 0.05431675910949707, \"node\": \"assert_customer_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.033476829528808594, \"node\": \"candidate_not_null_dim_customer_scd2_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03480696678161621, \"node\": \"candidate_not_null_dim_customer_scd2_customer_unique_id\", \"status\": \"pass\"}, {\"execution_time\": 0.03325033187866211, \"node\": \"candidate_not_null_dim_customer_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.03436422348022461, \"node\": \"unique_combination_of_columns_dim_customer_scd2_sync_run_seq__customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.061270952224731445, \"node\": \"assert_payment_allocations_balance\", \"status\": \"pass\"}, {\"execution_time\": 0.03578329086303711, \"node\": \"candidate_not_null_dim_date_date_day\", \"status\": \"pass\"}, {\"execution_time\": 0.060128211975097656, \"node\": \"candidate_not_null_dim_date_date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.0366663932800293, \"node\": \"candidate_not_null_dim_date_sync_run_seq\", \"status\": \"pass\"}, {\"execution_time\": 0.034572601318359375, \"node\": \"unique_combination_of_columns_dim_date_sync_run_seq__date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03233909606933594, \"node\": \"candidate_not_null_dim_order_status_order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.03597140312194824, \"node\": \"candidate_not_null_dim_order_status_order_status_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04122519493103027, \"node\": \"unique_combination_of_columns_dim_order_status_sync_run_seq__order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.045701026916503906, \"node\": \"assert_product_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.043515920639038086, \"node\": \"candidate_not_null_dim_product_scd2_product_id\", \"status\": \"pass\"}, {\"execution_time\": 0.04411196708679199, \"node\": \"candidate_not_null_dim_product_scd2_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04121279716491699, \"node\": \"candidate_not_null_dim_product_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.10631299018859863, \"node\": \"unique_combination_of_columns_dim_product_scd2_sync_run_seq__product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03692626953125, \"node\": \"candidate_not_null_dim_seller_seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.035135507583618164, \"node\": \"candidate_not_null_dim_seller_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.039649009704589844, \"node\": \"unique_combination_of_columns_dim_seller_sync_run_seq__seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.3188445568084717, \"node\": \"fact_order_items\", \"status\": \"success\"}, {\"execution_time\": 0.03192329406738281, \"node\": \"assert_fact_order_items_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.03603243827819824, \"node\": \"candidate_not_null_fact_order_items_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.033876895904541016, \"node\": \"candidate_not_null_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.04268217086791992, \"node\": \"candidate_not_null_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.04243040084838867, \"node\": \"candidate_not_null_fact_order_items_order_item_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03702402114868164, \"node\": \"candidate_not_null_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.03337597846984863, \"node\": \"candidate_not_null_fact_order_items_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.037862300872802734, \"node\": \"candidate_not_null_fact_order_items_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04497575759887695, \"node\": \"candidate_relationships_fact_order_items_customer_key__customer_key__ref_dim_customer_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.041362762451171875, \"node\": \"candidate_relationships_fact_order_items_product_key__product_key__ref_dim_product_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.03935861587524414, \"node\": \"candidate_relationships_fact_order_items_seller_key__seller_key__ref_dim_seller_\", \"status\": \"pass\"}, {\"execution_time\": 0.0341184139251709, \"node\": \"non_negative_fact_order_items_allocated_payment_value\", \"status\": \"pass\"}, {\"execution_time\": 0.03432035446166992, \"node\": \"non_negative_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.03993344306945801, \"node\": \"non_negative_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.03924822807312012, \"node\": \"non_negative_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.04311084747314453, \"node\": \"unique_combination_of_columns_fact_order_items_sync_run_seq__order_id__order_item_id\", \"status\": \"pass\"}, {\"execution_time\": 0.12189912796020508, \"node\": \"mart_daily_revenue\", \"status\": \"success\"}, {\"execution_time\": 0.11654090881347656, \"node\": \"mart_monthly_arpu\", \"status\": \"success\"}, {\"execution_time\": 0.0373377799987793, \"node\": \"assert_daily_revenue_components\", \"status\": \"pass\"}, {\"execution_time\": 0.06897139549255371, \"node\": \"candidate_not_null_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.0567021369934082, \"node\": \"candidate_not_null_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.0562434196472168, \"node\": \"candidate_not_null_mart_daily_revenue_order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.04588460922241211, \"node\": \"candidate_not_null_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.03491330146789551, \"node\": \"non_negative_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.03436875343322754, \"node\": \"non_negative_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.036965370178222656, \"node\": \"non_negative_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.03579521179199219, \"node\": \"unique_combination_of_columns_mart_daily_revenue_sync_run_seq__order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.03216671943664551, \"node\": \"assert_monthly_arpu_formulas\", \"status\": \"pass\"}, {\"execution_time\": 0.03233504295349121, \"node\": \"candidate_not_null_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.033797502517700195, \"node\": \"candidate_not_null_mart_monthly_arpu_order_month\", \"status\": \"pass\"}, {\"execution_time\": 0.035668373107910156, \"node\": \"candidate_not_null_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.03580665588378906, \"node\": \"candidate_not_null_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.040764570236206055, \"node\": \"non_negative_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.04141879081726074, \"node\": \"non_negative_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.03847217559814453, \"node\": \"non_negative_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.03774738311767578, \"node\": \"unique_combination_of_columns_mart_monthly_arpu_sync_run_seq__order_month\", \"status\": \"pass\"}], \"selector\": \"serving_candidate\", \"status_counts\": {\"pass\": 59, \"success\": 16}, \"success\": true, \"vars\": {\"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3}}, \"expected_entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 90, \"iceberg_snapshot_ids\": {\"customers\": 8945732834443551666, \"order_items\": 8333618748302751604, \"order_payments\": 2342546804373807134, \"order_reviews\": 1873788046910446323, \"orders\": 2860036943269124164, \"product_category_translation\": 2510271481881063845, \"products\": 6434977924513876130, \"sellers\": 6608875651304288148}, \"is_noop\": false, \"materialized_entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"materialized_event_count\": 90, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3, \"sync_run_status\": \"SUCCEEDED\", \"target_offsets\": {\"olist_cdc.olist_oltp.customers:0\": 9, \"olist_cdc.olist_oltp.order_items:0\": 5, \"olist_cdc.olist_oltp.order_items:1\": 5, \"olist_cdc.olist_oltp.order_items:2\": 6, \"olist_cdc.olist_oltp.order_payments:0\": 5, \"olist_cdc.olist_oltp.order_payments:1\": 4, \"olist_cdc.olist_oltp.order_payments:2\": 4, \"olist_cdc.olist_oltp.order_reviews:0\": 5, \"olist_cdc.olist_oltp.order_reviews:1\": 4, \"olist_cdc.olist_oltp.order_reviews:2\": 2, \"olist_cdc.olist_oltp.orders:0\": 3, \"olist_cdc.olist_oltp.orders:1\": 4, \"olist_cdc.olist_oltp.orders:2\": 4, \"olist_cdc.olist_oltp.product_category_translation:0\": 4, \"olist_cdc.olist_oltp.products:0\": 7, \"olist_cdc.olist_oltp.sellers:0\": 3}, \"target_transaction_id\": \"file=binlog.000002,pos=22085\"}\n",
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
          "duration_seconds": 3.125,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"validate-serving\", \"current_views\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"dbt\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 3, \\\"sync_run_id\\\": \\\"sync-00000000000000000003\\\"}\"], \"result_count\": 75, \"status_counts\": {\"pass\": 59, \"success\": 16}}, \"gold_views\": {\"dim_customer_scd2\": {\"candidate\": 8, \"stable\": 8}, \"dim_date\": {\"candidate\": 46, \"stable\": 46}, \"dim_order_status\": {\"candidate\": 2, \"stable\": 2}, \"dim_product_scd2\": {\"candidate\": 8, \"stable\": 8}, \"dim_seller\": {\"candidate\": 4, \"stable\": 4}, \"fact_order_items\": {\"candidate\": 18, \"stable\": 18}, \"mart_daily_revenue\": {\"candidate\": 13, \"stable\": 13}, \"mart_monthly_arpu\": {\"candidate\": 7, \"stable\": 7}}, \"static_validation\": {\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 216 packages in 1ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"m/test_local_lab_live_readiness.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/lakehouse_platform/test_local_lab_profile_boundaries.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"All checks passed!\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"91 files already formatted\", \"exit_code\": 0, \"status\": \"passed\"}], \"status\": \"ready\"}, \"status\": \"ready\", \"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 60.944,
      "gate": "08-additive-schema",
      "status": "PASS",
      "timestamp": "2026-08-03T18:04:27.497064+00:00"
    },
    "09-rebuild": {
      "assertions": [
        {
          "detail": {
            "command": "rebuild-serving",
            "dag_run_id": "stage_v_final_candidate_retry_rebuild_1061cec69b2a",
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
              "customers": 8945732834443551666,
              "order_items": 8333618748302751604,
              "order_payments": 2342546804373807134,
              "order_reviews": 1873788046910446323,
              "orders": 2860036943269124164,
              "product_category_translation": 2510271481881063845,
              "products": 6434977924513876130,
              "sellers": 6608875651304288148
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
              "customers": 8945732834443551666,
              "order_items": 8333618748302751604,
              "order_payments": 2342546804373807134,
              "order_reviews": 1873788046910446323,
              "orders": 2860036943269124164,
              "product_category_translation": 2510271481881063845,
              "products": 6434977924513876130,
              "sellers": 6608875651304288148
            },
            "materialized_event_count": 90,
            "row_manifests": {
              "candidate_physical": {
                "customers": {
                  "manifest_sha256": "c5e9bd8436395273a8e1cd5baee5332af3609387a180503a35ac3d2bb48af6d0",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "0d10cdd2fc05399400d89cdb24746b0b289d78f7a8a4b82598fe21d11ae9b731"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "a8de535a3a12f987810975cb44f3e288ff492e72024588920c5787e2820f2100"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "7e0b4d5d0f516dceaf87941bb8cf52b35111a338776f98346e056a4aa7a3ff5f"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "b7284338d73bb5bf5105d48f16264b2b1855559a24329933c9060f90c0d92bf5"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "7ab42f667edd04e117e4a876cfe7bb28173df733a0b90f16c04a1b7edb11042c"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "987297199383f6a17f975b3cd3d0956a7c161c2c46144f7e190c21db8d377124"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "851f578e9ebb923a9c733f988473dfd5d08a484d9abcccf9677aa79690dbb4b9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "7a28f748bef00843e2255aba1c1b4f7a3616b19f41f04358e706e3729780301a"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "bde17534e3035031a2b4cadf89808ad4be3870b8e431bcb48e1589f3f748f05c"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "fc42d0f5000a46610d7c036934fd58bf11c4b57508806f06e0bc27e268ab2527",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "ec1cc0c3f5db3d730e635fb58079f48ba19bdf7865ef3dfe1fd3981c6f7d723d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "54fa68b1ada8664ca1694f141440421865b55dbfc21e4f43ae9fe894dea3a04e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "3cda1da0d9d949e6d04bcb63c3e7ca7f300d005096eeefc67e7b779baa554a8e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "eca4244589d571813a4bc5bf33c2d024292696ab3fe8c8c83e2ecc673bc31df0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "072c36ff9acbdfe5cfc41bbecb57b119303c6ce70d57bee2a6ae6f3ad85bea99"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "761da00fd9c9353b76334fd593b54ee083ca92f8cf462f8c47ab167c5f4ffd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "a1337cdc1ab4edd0305a707a0d0f934d6b7326225224d530d25315f83584140d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "b023239a3fb52428341c2d0ac83548aa4c5b56d60f782de7af781665b6c70b71"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "78a8a0e8ffbe795b848306775981ea545d9d3a92fca7a0909194b278582c786d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "aa878cb2e01217ebd62810321dce08cdf989e42661b9559d9814579a08f7a61b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "5f7ba42608a1aa3ba365af07dd4732b6d8e317be259e46915f790f1bca3b6838"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "7ae25e4bd73616a2e26f2b64076ac21f70f247d81f86ddf680cb99e00829b5ce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "e403901ebfa72ca8ca4630d58f72880e096dba80fcb0f33fd0680be27cf9b883"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "a9e6f3df1f60da87742d3c7a8e28ee269f222932e6f039b9c97fdd18d90da3aa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "0ed72ee5665c801c07fc4c670959053d3441657b4d83334bf86bbb7b2e7fd733"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5a8a7571c7c04d1c3873f8b5ee587bfd4a5f732493cb11d739691c3880d2fb69"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "4bedd28f6c22c627fd07384225906461f0cf7c2ab94743da271a040ceda886df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "179c496072c4b388cb6095ae0c2d5fec453067cba892912a2e186af2a1164eb6"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "be5bac52cc658a3375f516184f19fe3a2e98cb2a71641dc08bd68c5aa3f84f82",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "8038b580be0b90957066d240104b2b6b9e684108acf5a28b8e47a274db7587d8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "1b19c21b95f5925ba9207a5fd50e79ef03627c3322df76403062066e4ab642cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "478834c48ed92db6b1b68ef5256b686eb63bb1f5a21be323e806616f14cda6ea"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "0bab3e540d8d6d413df39c70ef6e9428ef35d2dd92f8981e536bda699fa38835"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "ea928cb6e0f7daa6019218107d8d984f005ea9d6a26e7aceaecac5d331e1bd55"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "e89ee7a61d31802fa65e8f8a3d32d4b2ecd141dd357789ae4bd7db247131c61a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "37e7a3fcf3b9d4d225e31c1e0a45a457161a6d406a0001dcfff004fd8d670f1a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "6b0241e0ca2965fa965855551332d23c57ad30d89c3e8c62b2705ba1d5aedc06"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "b9e5788236231faa76bd019fbb9d12a39d12b8fe404e47286fbcb598fdfea559"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "502a7400785b00f6ce4c98d733e3d6012e58e6c5936040d6351dcc6da0e087d3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "68884f5576f1982bff730e5010fb6936404d7f2f2d1255091c93661ca391507f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "12b4fb9a2da3a268015967a8ebee50c655ea56b2259d53daefb23549ad5a6d8a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "d6e1d6f6663946ef9055d4f679323eb4275b45aa4ecd551a650a3ce6936a00d7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "f9d55b6e7a4c37398aa4df49485984eb0934ac3f6d6ed89abc871314f4604550"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "dcacadab16a91c1904fca96c9a759b6cc76a7ff0fb0d774fac17528464adf4ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "b6d594e89dbf0b7b6086c9685c5821ab3d1e5ed6fdb92411c7a16214b76c1664"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "972faa1609774f5e100b46b1ea1617ad6335de07b8f0cd7f4fc42c159a45ac2e",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "f4309b0710678605195851312563b40c6b8b5b6f890cd24557fdb7deb886fec2"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "027cff22cbec944d0c76a14d2b20e3da88a763c5d984603603bc49c8f5fea69e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "0b79804194bcfc822cbe62a43e5cf22e9adde42e9be9c3d7599b5aeae5a91043"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "d4571749749e7237e01a6ef3b17e7a57bf2579e5e0c6e5b31f0f8a075f81c8ac"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "a6ab2ddd8458660013f81430f6d960c53f7abda003de194bc8e456f1435a2622"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "19beb53e7304115157c2866b9b661eccd98b92e255ebb38530ccfe95d00a191d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "cd4846b3c8343a749adb33031e900ffab70513fd02439910f94983b73db0ba10"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a7f5e7e70b7d471235fad4108d410ac223410ee89da4a890167054674e2a1bdb"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "b29fb5d7ebe7614170278b592446e0934950c9bea6162ad7024ca6c0cbd0b6a9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "ed564eee994349547da3e832424595f327661b9ca78119ca3b588205ae4904e0"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "973841660aebb81d0b9bb2e554bccb9c42abbc7c78bda6990c392d9a267b60b9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "fca64be024939db3a20d63f7c52937f93bf38e1eaaacd371835a12b85ba2f72e"
                    },
                    {
                      "is_deleted": true,
                      "review_id": "wave2_review_001",
                      "row_hash": "8f42ad9a706ce6d984d1e3438982f61b9621494cbb81e4dbed0f8059113e41d6"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "c1c55bb3d962743a33d334026befb3ecb366df75a20a0b0b34208f7b46b75e29",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "220e0362bb82421af7ff3d4b6c9082a61311aec5b72bc82b9469b541145062ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8767c0257f7efd653535e4c9db000f2fe5079f6b599ab1cc12820304ad684688"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "1cbc420947d42a7eaa25d219d149a424369b095bad7bc2aa9b197d33bca59e16"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "eec3f65bc2dba342ab0f59666133c01bf72b6b5523f0378693885a6a3ddea9df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "9fcae80247c433b267a4a70c65ddb3854cf95ac24a6d1ab7e0263d02e483c3c7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "97464f4d8cb4f96a6f89b53fc0803fd15371c2ea7750ccc9497daeb71515a120"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "4ecf6b3e8f6078e98afdbb3a7d5329ddcfd85f8e03d9c2eb1aeb71093119170e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "cc22a76d426d138662043e0fd0d16efdc091b67c2dd2aa9b6e1d1ab7bda700d9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "a3846bdec5173518c0bd8bb0194228b0dfee503252ba85320b62fb7a3d390948"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "f146faa74b32cd7911707875af68b95764794f0797f8e39512a83cdd48505b3c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "244e4cd989860f4569b6ee65f70015fd8485c274bc44d686f6b9c5f59a74977d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d4497c72599e234bfd23070bf0dc54e0d0fefd9d8ecf58e22b096f7916a52d59"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "f0fb55a395bccc0f01f7ea862c9744ac6f570f3941597337451aafe3f1f23eed"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "d3d962c346c72cb1250bdff82dbb71fb73c68d88c12365605d7bf793d4b6e874",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e221c22f277479a9f68ba82fb38565461388815f577bb51aafbe65c1da5a4417"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "a1d4f9a173d15c2cc89514a2cb060f73075d0bdce3ab76e6ed8e91090cfcdac6"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3a03c0be1cb357fc900a26a018ce2f8f6206e2583b09b7ffd0c923551add4c22"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "87661c86057e4c7a58a76e203b2fa56f1cdb3509c4b38bfd3491cebd82fc2c70"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "b21980549ab439249b5ae24c9788b071f51cbafaba31d6589557d0b29a58c789"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "cbbfdca967c26328c7e7acecd6380582e0e1b345c8790bdd2d9077a9f4ee7983",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "76b84167fae4ddce9de6d8ca02c58ed4721c7a642ac742111e904c792047c8de"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "f7e8852b715c28c023fbe375322474fa02bc65d81ef67579e4541e1920ac863e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "f04a19dc7a53c8d24693ece34ef606f74fed7ab8aa7618ab81f19702015e6abe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "63567922dbc71b63439b1e4a3c938f5eedcfdcee9d6fffde5a864f61f5333819"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "9ea4db91d3a779fa30cfdc8687eb9a2a3869d460dacb70c90777b95309675cb3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4b2d038c9381f4898016eb01a2c76913dcc6a4116f100dd9c8e89ac69ce9f593"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "aa89affbc52a6f241bf07e1be914fb2e842c90ca64aa327c642bb5406ff427fb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "de47d8963e98151f040068e0f034cc51f017ce59b3b90a47be3459618c74e664"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "c07cd48fbb30c66116beea16eef28ba18aee78e8649999c56c865985231d0752",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "33b64f9f4c0ec9b96e7d5a3f8f4b55f73490d61c7ede72c8881e43f38f8406b0",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c280dbc0a622377a6930afad3baedcf4832fda03d4adb50c0b71fbccbe5f0cd9",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "fc5bddb6e146d8a5ca8c213f4709f024c8c4e6394a24d6f33c9770b75304cd84",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "67e669b4b9d32278d7afbb7c518b84dbed53dbc2f84ea9fb5ac83e01cc8c1682",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "candidate_visible": {
                "customers": {
                  "manifest_sha256": "c5e9bd8436395273a8e1cd5baee5332af3609387a180503a35ac3d2bb48af6d0",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "0d10cdd2fc05399400d89cdb24746b0b289d78f7a8a4b82598fe21d11ae9b731"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "a8de535a3a12f987810975cb44f3e288ff492e72024588920c5787e2820f2100"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "7e0b4d5d0f516dceaf87941bb8cf52b35111a338776f98346e056a4aa7a3ff5f"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "b7284338d73bb5bf5105d48f16264b2b1855559a24329933c9060f90c0d92bf5"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "7ab42f667edd04e117e4a876cfe7bb28173df733a0b90f16c04a1b7edb11042c"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "987297199383f6a17f975b3cd3d0956a7c161c2c46144f7e190c21db8d377124"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "851f578e9ebb923a9c733f988473dfd5d08a484d9abcccf9677aa79690dbb4b9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "7a28f748bef00843e2255aba1c1b4f7a3616b19f41f04358e706e3729780301a"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "bde17534e3035031a2b4cadf89808ad4be3870b8e431bcb48e1589f3f748f05c"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "fc42d0f5000a46610d7c036934fd58bf11c4b57508806f06e0bc27e268ab2527",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "ec1cc0c3f5db3d730e635fb58079f48ba19bdf7865ef3dfe1fd3981c6f7d723d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "54fa68b1ada8664ca1694f141440421865b55dbfc21e4f43ae9fe894dea3a04e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "3cda1da0d9d949e6d04bcb63c3e7ca7f300d005096eeefc67e7b779baa554a8e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "eca4244589d571813a4bc5bf33c2d024292696ab3fe8c8c83e2ecc673bc31df0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "072c36ff9acbdfe5cfc41bbecb57b119303c6ce70d57bee2a6ae6f3ad85bea99"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "761da00fd9c9353b76334fd593b54ee083ca92f8cf462f8c47ab167c5f4ffd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "a1337cdc1ab4edd0305a707a0d0f934d6b7326225224d530d25315f83584140d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "b023239a3fb52428341c2d0ac83548aa4c5b56d60f782de7af781665b6c70b71"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "78a8a0e8ffbe795b848306775981ea545d9d3a92fca7a0909194b278582c786d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "aa878cb2e01217ebd62810321dce08cdf989e42661b9559d9814579a08f7a61b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "5f7ba42608a1aa3ba365af07dd4732b6d8e317be259e46915f790f1bca3b6838"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "7ae25e4bd73616a2e26f2b64076ac21f70f247d81f86ddf680cb99e00829b5ce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "e403901ebfa72ca8ca4630d58f72880e096dba80fcb0f33fd0680be27cf9b883"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "a9e6f3df1f60da87742d3c7a8e28ee269f222932e6f039b9c97fdd18d90da3aa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "0ed72ee5665c801c07fc4c670959053d3441657b4d83334bf86bbb7b2e7fd733"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5a8a7571c7c04d1c3873f8b5ee587bfd4a5f732493cb11d739691c3880d2fb69"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "4bedd28f6c22c627fd07384225906461f0cf7c2ab94743da271a040ceda886df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "179c496072c4b388cb6095ae0c2d5fec453067cba892912a2e186af2a1164eb6"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "be5bac52cc658a3375f516184f19fe3a2e98cb2a71641dc08bd68c5aa3f84f82",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "8038b580be0b90957066d240104b2b6b9e684108acf5a28b8e47a274db7587d8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "1b19c21b95f5925ba9207a5fd50e79ef03627c3322df76403062066e4ab642cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "478834c48ed92db6b1b68ef5256b686eb63bb1f5a21be323e806616f14cda6ea"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "0bab3e540d8d6d413df39c70ef6e9428ef35d2dd92f8981e536bda699fa38835"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "ea928cb6e0f7daa6019218107d8d984f005ea9d6a26e7aceaecac5d331e1bd55"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "e89ee7a61d31802fa65e8f8a3d32d4b2ecd141dd357789ae4bd7db247131c61a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "37e7a3fcf3b9d4d225e31c1e0a45a457161a6d406a0001dcfff004fd8d670f1a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "6b0241e0ca2965fa965855551332d23c57ad30d89c3e8c62b2705ba1d5aedc06"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "b9e5788236231faa76bd019fbb9d12a39d12b8fe404e47286fbcb598fdfea559"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "502a7400785b00f6ce4c98d733e3d6012e58e6c5936040d6351dcc6da0e087d3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "68884f5576f1982bff730e5010fb6936404d7f2f2d1255091c93661ca391507f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "12b4fb9a2da3a268015967a8ebee50c655ea56b2259d53daefb23549ad5a6d8a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "d6e1d6f6663946ef9055d4f679323eb4275b45aa4ecd551a650a3ce6936a00d7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "f9d55b6e7a4c37398aa4df49485984eb0934ac3f6d6ed89abc871314f4604550"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "dcacadab16a91c1904fca96c9a759b6cc76a7ff0fb0d774fac17528464adf4ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "b6d594e89dbf0b7b6086c9685c5821ab3d1e5ed6fdb92411c7a16214b76c1664"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "02aac6079fb82f4227af84ae12f77b784b724cbaa56d901c20154fb9829bdd13",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "f4309b0710678605195851312563b40c6b8b5b6f890cd24557fdb7deb886fec2"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "027cff22cbec944d0c76a14d2b20e3da88a763c5d984603603bc49c8f5fea69e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "0b79804194bcfc822cbe62a43e5cf22e9adde42e9be9c3d7599b5aeae5a91043"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "d4571749749e7237e01a6ef3b17e7a57bf2579e5e0c6e5b31f0f8a075f81c8ac"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "a6ab2ddd8458660013f81430f6d960c53f7abda003de194bc8e456f1435a2622"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "19beb53e7304115157c2866b9b661eccd98b92e255ebb38530ccfe95d00a191d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "cd4846b3c8343a749adb33031e900ffab70513fd02439910f94983b73db0ba10"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a7f5e7e70b7d471235fad4108d410ac223410ee89da4a890167054674e2a1bdb"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "b29fb5d7ebe7614170278b592446e0934950c9bea6162ad7024ca6c0cbd0b6a9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "ed564eee994349547da3e832424595f327661b9ca78119ca3b588205ae4904e0"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "973841660aebb81d0b9bb2e554bccb9c42abbc7c78bda6990c392d9a267b60b9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "fca64be024939db3a20d63f7c52937f93bf38e1eaaacd371835a12b85ba2f72e"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "c1c55bb3d962743a33d334026befb3ecb366df75a20a0b0b34208f7b46b75e29",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "220e0362bb82421af7ff3d4b6c9082a61311aec5b72bc82b9469b541145062ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8767c0257f7efd653535e4c9db000f2fe5079f6b599ab1cc12820304ad684688"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "1cbc420947d42a7eaa25d219d149a424369b095bad7bc2aa9b197d33bca59e16"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "eec3f65bc2dba342ab0f59666133c01bf72b6b5523f0378693885a6a3ddea9df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "9fcae80247c433b267a4a70c65ddb3854cf95ac24a6d1ab7e0263d02e483c3c7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "97464f4d8cb4f96a6f89b53fc0803fd15371c2ea7750ccc9497daeb71515a120"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "4ecf6b3e8f6078e98afdbb3a7d5329ddcfd85f8e03d9c2eb1aeb71093119170e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "cc22a76d426d138662043e0fd0d16efdc091b67c2dd2aa9b6e1d1ab7bda700d9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "a3846bdec5173518c0bd8bb0194228b0dfee503252ba85320b62fb7a3d390948"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "f146faa74b32cd7911707875af68b95764794f0797f8e39512a83cdd48505b3c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "244e4cd989860f4569b6ee65f70015fd8485c274bc44d686f6b9c5f59a74977d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d4497c72599e234bfd23070bf0dc54e0d0fefd9d8ecf58e22b096f7916a52d59"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "f0fb55a395bccc0f01f7ea862c9744ac6f570f3941597337451aafe3f1f23eed"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "d3d962c346c72cb1250bdff82dbb71fb73c68d88c12365605d7bf793d4b6e874",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e221c22f277479a9f68ba82fb38565461388815f577bb51aafbe65c1da5a4417"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "a1d4f9a173d15c2cc89514a2cb060f73075d0bdce3ab76e6ed8e91090cfcdac6"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3a03c0be1cb357fc900a26a018ce2f8f6206e2583b09b7ffd0c923551add4c22"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "87661c86057e4c7a58a76e203b2fa56f1cdb3509c4b38bfd3491cebd82fc2c70"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "b21980549ab439249b5ae24c9788b071f51cbafaba31d6589557d0b29a58c789"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "cbbfdca967c26328c7e7acecd6380582e0e1b345c8790bdd2d9077a9f4ee7983",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "76b84167fae4ddce9de6d8ca02c58ed4721c7a642ac742111e904c792047c8de"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "f7e8852b715c28c023fbe375322474fa02bc65d81ef67579e4541e1920ac863e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "f04a19dc7a53c8d24693ece34ef606f74fed7ab8aa7618ab81f19702015e6abe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "63567922dbc71b63439b1e4a3c938f5eedcfdcee9d6fffde5a864f61f5333819"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "9ea4db91d3a779fa30cfdc8687eb9a2a3869d460dacb70c90777b95309675cb3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4b2d038c9381f4898016eb01a2c76913dcc6a4116f100dd9c8e89ac69ce9f593"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "aa89affbc52a6f241bf07e1be914fb2e842c90ca64aa327c642bb5406ff427fb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "de47d8963e98151f040068e0f034cc51f017ce59b3b90a47be3459618c74e664"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "c07cd48fbb30c66116beea16eef28ba18aee78e8649999c56c865985231d0752",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "33b64f9f4c0ec9b96e7d5a3f8f4b55f73490d61c7ede72c8881e43f38f8406b0",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c280dbc0a622377a6930afad3baedcf4832fda03d4adb50c0b71fbccbe5f0cd9",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "fc5bddb6e146d8a5ca8c213f4709f024c8c4e6394a24d6f33c9770b75304cd84",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "67e669b4b9d32278d7afbb7c518b84dbed53dbc2f84ea9fb5ac83e01cc8c1682",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "iceberg_physical": {
                "customers": {
                  "manifest_sha256": "c5e9bd8436395273a8e1cd5baee5332af3609387a180503a35ac3d2bb48af6d0",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "0d10cdd2fc05399400d89cdb24746b0b289d78f7a8a4b82598fe21d11ae9b731"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "a8de535a3a12f987810975cb44f3e288ff492e72024588920c5787e2820f2100"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "7e0b4d5d0f516dceaf87941bb8cf52b35111a338776f98346e056a4aa7a3ff5f"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "b7284338d73bb5bf5105d48f16264b2b1855559a24329933c9060f90c0d92bf5"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "7ab42f667edd04e117e4a876cfe7bb28173df733a0b90f16c04a1b7edb11042c"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "987297199383f6a17f975b3cd3d0956a7c161c2c46144f7e190c21db8d377124"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "851f578e9ebb923a9c733f988473dfd5d08a484d9abcccf9677aa79690dbb4b9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "7a28f748bef00843e2255aba1c1b4f7a3616b19f41f04358e706e3729780301a"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "bde17534e3035031a2b4cadf89808ad4be3870b8e431bcb48e1589f3f748f05c"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "fc42d0f5000a46610d7c036934fd58bf11c4b57508806f06e0bc27e268ab2527",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "ec1cc0c3f5db3d730e635fb58079f48ba19bdf7865ef3dfe1fd3981c6f7d723d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "54fa68b1ada8664ca1694f141440421865b55dbfc21e4f43ae9fe894dea3a04e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "3cda1da0d9d949e6d04bcb63c3e7ca7f300d005096eeefc67e7b779baa554a8e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "eca4244589d571813a4bc5bf33c2d024292696ab3fe8c8c83e2ecc673bc31df0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "072c36ff9acbdfe5cfc41bbecb57b119303c6ce70d57bee2a6ae6f3ad85bea99"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "761da00fd9c9353b76334fd593b54ee083ca92f8cf462f8c47ab167c5f4ffd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "a1337cdc1ab4edd0305a707a0d0f934d6b7326225224d530d25315f83584140d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "b023239a3fb52428341c2d0ac83548aa4c5b56d60f782de7af781665b6c70b71"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "78a8a0e8ffbe795b848306775981ea545d9d3a92fca7a0909194b278582c786d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "aa878cb2e01217ebd62810321dce08cdf989e42661b9559d9814579a08f7a61b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "5f7ba42608a1aa3ba365af07dd4732b6d8e317be259e46915f790f1bca3b6838"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "7ae25e4bd73616a2e26f2b64076ac21f70f247d81f86ddf680cb99e00829b5ce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "e403901ebfa72ca8ca4630d58f72880e096dba80fcb0f33fd0680be27cf9b883"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "a9e6f3df1f60da87742d3c7a8e28ee269f222932e6f039b9c97fdd18d90da3aa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "0ed72ee5665c801c07fc4c670959053d3441657b4d83334bf86bbb7b2e7fd733"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5a8a7571c7c04d1c3873f8b5ee587bfd4a5f732493cb11d739691c3880d2fb69"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "4bedd28f6c22c627fd07384225906461f0cf7c2ab94743da271a040ceda886df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "179c496072c4b388cb6095ae0c2d5fec453067cba892912a2e186af2a1164eb6"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "be5bac52cc658a3375f516184f19fe3a2e98cb2a71641dc08bd68c5aa3f84f82",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "8038b580be0b90957066d240104b2b6b9e684108acf5a28b8e47a274db7587d8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "1b19c21b95f5925ba9207a5fd50e79ef03627c3322df76403062066e4ab642cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "478834c48ed92db6b1b68ef5256b686eb63bb1f5a21be323e806616f14cda6ea"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "0bab3e540d8d6d413df39c70ef6e9428ef35d2dd92f8981e536bda699fa38835"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "ea928cb6e0f7daa6019218107d8d984f005ea9d6a26e7aceaecac5d331e1bd55"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "e89ee7a61d31802fa65e8f8a3d32d4b2ecd141dd357789ae4bd7db247131c61a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "37e7a3fcf3b9d4d225e31c1e0a45a457161a6d406a0001dcfff004fd8d670f1a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "6b0241e0ca2965fa965855551332d23c57ad30d89c3e8c62b2705ba1d5aedc06"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "b9e5788236231faa76bd019fbb9d12a39d12b8fe404e47286fbcb598fdfea559"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "502a7400785b00f6ce4c98d733e3d6012e58e6c5936040d6351dcc6da0e087d3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "68884f5576f1982bff730e5010fb6936404d7f2f2d1255091c93661ca391507f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "12b4fb9a2da3a268015967a8ebee50c655ea56b2259d53daefb23549ad5a6d8a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "d6e1d6f6663946ef9055d4f679323eb4275b45aa4ecd551a650a3ce6936a00d7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "f9d55b6e7a4c37398aa4df49485984eb0934ac3f6d6ed89abc871314f4604550"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "dcacadab16a91c1904fca96c9a759b6cc76a7ff0fb0d774fac17528464adf4ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "b6d594e89dbf0b7b6086c9685c5821ab3d1e5ed6fdb92411c7a16214b76c1664"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "972faa1609774f5e100b46b1ea1617ad6335de07b8f0cd7f4fc42c159a45ac2e",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "f4309b0710678605195851312563b40c6b8b5b6f890cd24557fdb7deb886fec2"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "027cff22cbec944d0c76a14d2b20e3da88a763c5d984603603bc49c8f5fea69e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "0b79804194bcfc822cbe62a43e5cf22e9adde42e9be9c3d7599b5aeae5a91043"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "d4571749749e7237e01a6ef3b17e7a57bf2579e5e0c6e5b31f0f8a075f81c8ac"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "a6ab2ddd8458660013f81430f6d960c53f7abda003de194bc8e456f1435a2622"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "19beb53e7304115157c2866b9b661eccd98b92e255ebb38530ccfe95d00a191d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "cd4846b3c8343a749adb33031e900ffab70513fd02439910f94983b73db0ba10"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a7f5e7e70b7d471235fad4108d410ac223410ee89da4a890167054674e2a1bdb"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "b29fb5d7ebe7614170278b592446e0934950c9bea6162ad7024ca6c0cbd0b6a9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "ed564eee994349547da3e832424595f327661b9ca78119ca3b588205ae4904e0"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "973841660aebb81d0b9bb2e554bccb9c42abbc7c78bda6990c392d9a267b60b9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "fca64be024939db3a20d63f7c52937f93bf38e1eaaacd371835a12b85ba2f72e"
                    },
                    {
                      "is_deleted": true,
                      "review_id": "wave2_review_001",
                      "row_hash": "8f42ad9a706ce6d984d1e3438982f61b9621494cbb81e4dbed0f8059113e41d6"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "c1c55bb3d962743a33d334026befb3ecb366df75a20a0b0b34208f7b46b75e29",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "220e0362bb82421af7ff3d4b6c9082a61311aec5b72bc82b9469b541145062ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8767c0257f7efd653535e4c9db000f2fe5079f6b599ab1cc12820304ad684688"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "1cbc420947d42a7eaa25d219d149a424369b095bad7bc2aa9b197d33bca59e16"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "eec3f65bc2dba342ab0f59666133c01bf72b6b5523f0378693885a6a3ddea9df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "9fcae80247c433b267a4a70c65ddb3854cf95ac24a6d1ab7e0263d02e483c3c7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "97464f4d8cb4f96a6f89b53fc0803fd15371c2ea7750ccc9497daeb71515a120"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "4ecf6b3e8f6078e98afdbb3a7d5329ddcfd85f8e03d9c2eb1aeb71093119170e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "cc22a76d426d138662043e0fd0d16efdc091b67c2dd2aa9b6e1d1ab7bda700d9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "a3846bdec5173518c0bd8bb0194228b0dfee503252ba85320b62fb7a3d390948"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "f146faa74b32cd7911707875af68b95764794f0797f8e39512a83cdd48505b3c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "244e4cd989860f4569b6ee65f70015fd8485c274bc44d686f6b9c5f59a74977d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d4497c72599e234bfd23070bf0dc54e0d0fefd9d8ecf58e22b096f7916a52d59"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "f0fb55a395bccc0f01f7ea862c9744ac6f570f3941597337451aafe3f1f23eed"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "d3d962c346c72cb1250bdff82dbb71fb73c68d88c12365605d7bf793d4b6e874",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e221c22f277479a9f68ba82fb38565461388815f577bb51aafbe65c1da5a4417"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "a1d4f9a173d15c2cc89514a2cb060f73075d0bdce3ab76e6ed8e91090cfcdac6"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3a03c0be1cb357fc900a26a018ce2f8f6206e2583b09b7ffd0c923551add4c22"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "87661c86057e4c7a58a76e203b2fa56f1cdb3509c4b38bfd3491cebd82fc2c70"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "b21980549ab439249b5ae24c9788b071f51cbafaba31d6589557d0b29a58c789"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "cbbfdca967c26328c7e7acecd6380582e0e1b345c8790bdd2d9077a9f4ee7983",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "76b84167fae4ddce9de6d8ca02c58ed4721c7a642ac742111e904c792047c8de"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "f7e8852b715c28c023fbe375322474fa02bc65d81ef67579e4541e1920ac863e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "f04a19dc7a53c8d24693ece34ef606f74fed7ab8aa7618ab81f19702015e6abe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "63567922dbc71b63439b1e4a3c938f5eedcfdcee9d6fffde5a864f61f5333819"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "9ea4db91d3a779fa30cfdc8687eb9a2a3869d460dacb70c90777b95309675cb3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4b2d038c9381f4898016eb01a2c76913dcc6a4116f100dd9c8e89ac69ce9f593"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "aa89affbc52a6f241bf07e1be914fb2e842c90ca64aa327c642bb5406ff427fb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "de47d8963e98151f040068e0f034cc51f017ce59b3b90a47be3459618c74e664"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "c07cd48fbb30c66116beea16eef28ba18aee78e8649999c56c865985231d0752",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "33b64f9f4c0ec9b96e7d5a3f8f4b55f73490d61c7ede72c8881e43f38f8406b0",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c280dbc0a622377a6930afad3baedcf4832fda03d4adb50c0b71fbccbe5f0cd9",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "fc5bddb6e146d8a5ca8c213f4709f024c8c4e6394a24d6f33c9770b75304cd84",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "67e669b4b9d32278d7afbb7c518b84dbed53dbc2f84ea9fb5ac83e01cc8c1682",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "iceberg_visible": {
                "customers": {
                  "manifest_sha256": "c5e9bd8436395273a8e1cd5baee5332af3609387a180503a35ac3d2bb48af6d0",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "0d10cdd2fc05399400d89cdb24746b0b289d78f7a8a4b82598fe21d11ae9b731"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "a8de535a3a12f987810975cb44f3e288ff492e72024588920c5787e2820f2100"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "7e0b4d5d0f516dceaf87941bb8cf52b35111a338776f98346e056a4aa7a3ff5f"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "b7284338d73bb5bf5105d48f16264b2b1855559a24329933c9060f90c0d92bf5"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "7ab42f667edd04e117e4a876cfe7bb28173df733a0b90f16c04a1b7edb11042c"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "987297199383f6a17f975b3cd3d0956a7c161c2c46144f7e190c21db8d377124"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "851f578e9ebb923a9c733f988473dfd5d08a484d9abcccf9677aa79690dbb4b9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "7a28f748bef00843e2255aba1c1b4f7a3616b19f41f04358e706e3729780301a"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "bde17534e3035031a2b4cadf89808ad4be3870b8e431bcb48e1589f3f748f05c"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "fc42d0f5000a46610d7c036934fd58bf11c4b57508806f06e0bc27e268ab2527",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "ec1cc0c3f5db3d730e635fb58079f48ba19bdf7865ef3dfe1fd3981c6f7d723d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "54fa68b1ada8664ca1694f141440421865b55dbfc21e4f43ae9fe894dea3a04e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "3cda1da0d9d949e6d04bcb63c3e7ca7f300d005096eeefc67e7b779baa554a8e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "eca4244589d571813a4bc5bf33c2d024292696ab3fe8c8c83e2ecc673bc31df0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "072c36ff9acbdfe5cfc41bbecb57b119303c6ce70d57bee2a6ae6f3ad85bea99"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "761da00fd9c9353b76334fd593b54ee083ca92f8cf462f8c47ab167c5f4ffd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "a1337cdc1ab4edd0305a707a0d0f934d6b7326225224d530d25315f83584140d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "b023239a3fb52428341c2d0ac83548aa4c5b56d60f782de7af781665b6c70b71"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "78a8a0e8ffbe795b848306775981ea545d9d3a92fca7a0909194b278582c786d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "aa878cb2e01217ebd62810321dce08cdf989e42661b9559d9814579a08f7a61b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "5f7ba42608a1aa3ba365af07dd4732b6d8e317be259e46915f790f1bca3b6838"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "7ae25e4bd73616a2e26f2b64076ac21f70f247d81f86ddf680cb99e00829b5ce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "e403901ebfa72ca8ca4630d58f72880e096dba80fcb0f33fd0680be27cf9b883"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "a9e6f3df1f60da87742d3c7a8e28ee269f222932e6f039b9c97fdd18d90da3aa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "0ed72ee5665c801c07fc4c670959053d3441657b4d83334bf86bbb7b2e7fd733"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5a8a7571c7c04d1c3873f8b5ee587bfd4a5f732493cb11d739691c3880d2fb69"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "4bedd28f6c22c627fd07384225906461f0cf7c2ab94743da271a040ceda886df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "179c496072c4b388cb6095ae0c2d5fec453067cba892912a2e186af2a1164eb6"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "be5bac52cc658a3375f516184f19fe3a2e98cb2a71641dc08bd68c5aa3f84f82",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "8038b580be0b90957066d240104b2b6b9e684108acf5a28b8e47a274db7587d8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "1b19c21b95f5925ba9207a5fd50e79ef03627c3322df76403062066e4ab642cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "478834c48ed92db6b1b68ef5256b686eb63bb1f5a21be323e806616f14cda6ea"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "0bab3e540d8d6d413df39c70ef6e9428ef35d2dd92f8981e536bda699fa38835"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "ea928cb6e0f7daa6019218107d8d984f005ea9d6a26e7aceaecac5d331e1bd55"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "e89ee7a61d31802fa65e8f8a3d32d4b2ecd141dd357789ae4bd7db247131c61a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "37e7a3fcf3b9d4d225e31c1e0a45a457161a6d406a0001dcfff004fd8d670f1a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "6b0241e0ca2965fa965855551332d23c57ad30d89c3e8c62b2705ba1d5aedc06"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "b9e5788236231faa76bd019fbb9d12a39d12b8fe404e47286fbcb598fdfea559"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "502a7400785b00f6ce4c98d733e3d6012e58e6c5936040d6351dcc6da0e087d3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "68884f5576f1982bff730e5010fb6936404d7f2f2d1255091c93661ca391507f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "12b4fb9a2da3a268015967a8ebee50c655ea56b2259d53daefb23549ad5a6d8a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "d6e1d6f6663946ef9055d4f679323eb4275b45aa4ecd551a650a3ce6936a00d7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "f9d55b6e7a4c37398aa4df49485984eb0934ac3f6d6ed89abc871314f4604550"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "dcacadab16a91c1904fca96c9a759b6cc76a7ff0fb0d774fac17528464adf4ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "b6d594e89dbf0b7b6086c9685c5821ab3d1e5ed6fdb92411c7a16214b76c1664"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "02aac6079fb82f4227af84ae12f77b784b724cbaa56d901c20154fb9829bdd13",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "f4309b0710678605195851312563b40c6b8b5b6f890cd24557fdb7deb886fec2"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "027cff22cbec944d0c76a14d2b20e3da88a763c5d984603603bc49c8f5fea69e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "0b79804194bcfc822cbe62a43e5cf22e9adde42e9be9c3d7599b5aeae5a91043"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "d4571749749e7237e01a6ef3b17e7a57bf2579e5e0c6e5b31f0f8a075f81c8ac"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "a6ab2ddd8458660013f81430f6d960c53f7abda003de194bc8e456f1435a2622"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "19beb53e7304115157c2866b9b661eccd98b92e255ebb38530ccfe95d00a191d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "cd4846b3c8343a749adb33031e900ffab70513fd02439910f94983b73db0ba10"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a7f5e7e70b7d471235fad4108d410ac223410ee89da4a890167054674e2a1bdb"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "b29fb5d7ebe7614170278b592446e0934950c9bea6162ad7024ca6c0cbd0b6a9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "ed564eee994349547da3e832424595f327661b9ca78119ca3b588205ae4904e0"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "973841660aebb81d0b9bb2e554bccb9c42abbc7c78bda6990c392d9a267b60b9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "fca64be024939db3a20d63f7c52937f93bf38e1eaaacd371835a12b85ba2f72e"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "c1c55bb3d962743a33d334026befb3ecb366df75a20a0b0b34208f7b46b75e29",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "220e0362bb82421af7ff3d4b6c9082a61311aec5b72bc82b9469b541145062ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8767c0257f7efd653535e4c9db000f2fe5079f6b599ab1cc12820304ad684688"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "1cbc420947d42a7eaa25d219d149a424369b095bad7bc2aa9b197d33bca59e16"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "eec3f65bc2dba342ab0f59666133c01bf72b6b5523f0378693885a6a3ddea9df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "9fcae80247c433b267a4a70c65ddb3854cf95ac24a6d1ab7e0263d02e483c3c7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "97464f4d8cb4f96a6f89b53fc0803fd15371c2ea7750ccc9497daeb71515a120"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "4ecf6b3e8f6078e98afdbb3a7d5329ddcfd85f8e03d9c2eb1aeb71093119170e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "cc22a76d426d138662043e0fd0d16efdc091b67c2dd2aa9b6e1d1ab7bda700d9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "a3846bdec5173518c0bd8bb0194228b0dfee503252ba85320b62fb7a3d390948"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "f146faa74b32cd7911707875af68b95764794f0797f8e39512a83cdd48505b3c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "244e4cd989860f4569b6ee65f70015fd8485c274bc44d686f6b9c5f59a74977d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d4497c72599e234bfd23070bf0dc54e0d0fefd9d8ecf58e22b096f7916a52d59"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "f0fb55a395bccc0f01f7ea862c9744ac6f570f3941597337451aafe3f1f23eed"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "d3d962c346c72cb1250bdff82dbb71fb73c68d88c12365605d7bf793d4b6e874",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e221c22f277479a9f68ba82fb38565461388815f577bb51aafbe65c1da5a4417"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "a1d4f9a173d15c2cc89514a2cb060f73075d0bdce3ab76e6ed8e91090cfcdac6"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3a03c0be1cb357fc900a26a018ce2f8f6206e2583b09b7ffd0c923551add4c22"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "87661c86057e4c7a58a76e203b2fa56f1cdb3509c4b38bfd3491cebd82fc2c70"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "b21980549ab439249b5ae24c9788b071f51cbafaba31d6589557d0b29a58c789"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "cbbfdca967c26328c7e7acecd6380582e0e1b345c8790bdd2d9077a9f4ee7983",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "76b84167fae4ddce9de6d8ca02c58ed4721c7a642ac742111e904c792047c8de"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "f7e8852b715c28c023fbe375322474fa02bc65d81ef67579e4541e1920ac863e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "f04a19dc7a53c8d24693ece34ef606f74fed7ab8aa7618ab81f19702015e6abe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "63567922dbc71b63439b1e4a3c938f5eedcfdcee9d6fffde5a864f61f5333819"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "9ea4db91d3a779fa30cfdc8687eb9a2a3869d460dacb70c90777b95309675cb3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4b2d038c9381f4898016eb01a2c76913dcc6a4116f100dd9c8e89ac69ce9f593"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "aa89affbc52a6f241bf07e1be914fb2e842c90ca64aa327c642bb5406ff427fb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "de47d8963e98151f040068e0f034cc51f017ce59b3b90a47be3459618c74e664"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "c07cd48fbb30c66116beea16eef28ba18aee78e8649999c56c865985231d0752",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "33b64f9f4c0ec9b96e7d5a3f8f4b55f73490d61c7ede72c8881e43f38f8406b0",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c280dbc0a622377a6930afad3baedcf4832fda03d4adb50c0b71fbccbe5f0cd9",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "fc5bddb6e146d8a5ca8c213f4709f024c8c4e6394a24d6f33c9770b75304cd84",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "67e669b4b9d32278d7afbb7c518b84dbed53dbc2f84ea9fb5ac83e01cc8c1682",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "stable_visible": {
                "customers": {
                  "manifest_sha256": "c5e9bd8436395273a8e1cd5baee5332af3609387a180503a35ac3d2bb48af6d0",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "0d10cdd2fc05399400d89cdb24746b0b289d78f7a8a4b82598fe21d11ae9b731"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "a8de535a3a12f987810975cb44f3e288ff492e72024588920c5787e2820f2100"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "7e0b4d5d0f516dceaf87941bb8cf52b35111a338776f98346e056a4aa7a3ff5f"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "b7284338d73bb5bf5105d48f16264b2b1855559a24329933c9060f90c0d92bf5"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "7ab42f667edd04e117e4a876cfe7bb28173df733a0b90f16c04a1b7edb11042c"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "987297199383f6a17f975b3cd3d0956a7c161c2c46144f7e190c21db8d377124"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "851f578e9ebb923a9c733f988473dfd5d08a484d9abcccf9677aa79690dbb4b9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "7a28f748bef00843e2255aba1c1b4f7a3616b19f41f04358e706e3729780301a"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "bde17534e3035031a2b4cadf89808ad4be3870b8e431bcb48e1589f3f748f05c"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "fc42d0f5000a46610d7c036934fd58bf11c4b57508806f06e0bc27e268ab2527",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "ec1cc0c3f5db3d730e635fb58079f48ba19bdf7865ef3dfe1fd3981c6f7d723d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "54fa68b1ada8664ca1694f141440421865b55dbfc21e4f43ae9fe894dea3a04e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "3cda1da0d9d949e6d04bcb63c3e7ca7f300d005096eeefc67e7b779baa554a8e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "eca4244589d571813a4bc5bf33c2d024292696ab3fe8c8c83e2ecc673bc31df0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "072c36ff9acbdfe5cfc41bbecb57b119303c6ce70d57bee2a6ae6f3ad85bea99"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "761da00fd9c9353b76334fd593b54ee083ca92f8cf462f8c47ab167c5f4ffd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "a1337cdc1ab4edd0305a707a0d0f934d6b7326225224d530d25315f83584140d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "b023239a3fb52428341c2d0ac83548aa4c5b56d60f782de7af781665b6c70b71"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "78a8a0e8ffbe795b848306775981ea545d9d3a92fca7a0909194b278582c786d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "aa878cb2e01217ebd62810321dce08cdf989e42661b9559d9814579a08f7a61b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "5f7ba42608a1aa3ba365af07dd4732b6d8e317be259e46915f790f1bca3b6838"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "7ae25e4bd73616a2e26f2b64076ac21f70f247d81f86ddf680cb99e00829b5ce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "e403901ebfa72ca8ca4630d58f72880e096dba80fcb0f33fd0680be27cf9b883"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "a9e6f3df1f60da87742d3c7a8e28ee269f222932e6f039b9c97fdd18d90da3aa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "0ed72ee5665c801c07fc4c670959053d3441657b4d83334bf86bbb7b2e7fd733"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5a8a7571c7c04d1c3873f8b5ee587bfd4a5f732493cb11d739691c3880d2fb69"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "4bedd28f6c22c627fd07384225906461f0cf7c2ab94743da271a040ceda886df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "179c496072c4b388cb6095ae0c2d5fec453067cba892912a2e186af2a1164eb6"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "be5bac52cc658a3375f516184f19fe3a2e98cb2a71641dc08bd68c5aa3f84f82",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "8038b580be0b90957066d240104b2b6b9e684108acf5a28b8e47a274db7587d8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "1b19c21b95f5925ba9207a5fd50e79ef03627c3322df76403062066e4ab642cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "478834c48ed92db6b1b68ef5256b686eb63bb1f5a21be323e806616f14cda6ea"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "0bab3e540d8d6d413df39c70ef6e9428ef35d2dd92f8981e536bda699fa38835"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "ea928cb6e0f7daa6019218107d8d984f005ea9d6a26e7aceaecac5d331e1bd55"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "e89ee7a61d31802fa65e8f8a3d32d4b2ecd141dd357789ae4bd7db247131c61a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "37e7a3fcf3b9d4d225e31c1e0a45a457161a6d406a0001dcfff004fd8d670f1a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "6b0241e0ca2965fa965855551332d23c57ad30d89c3e8c62b2705ba1d5aedc06"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "b9e5788236231faa76bd019fbb9d12a39d12b8fe404e47286fbcb598fdfea559"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "502a7400785b00f6ce4c98d733e3d6012e58e6c5936040d6351dcc6da0e087d3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "68884f5576f1982bff730e5010fb6936404d7f2f2d1255091c93661ca391507f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "12b4fb9a2da3a268015967a8ebee50c655ea56b2259d53daefb23549ad5a6d8a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "d6e1d6f6663946ef9055d4f679323eb4275b45aa4ecd551a650a3ce6936a00d7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "f9d55b6e7a4c37398aa4df49485984eb0934ac3f6d6ed89abc871314f4604550"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "dcacadab16a91c1904fca96c9a759b6cc76a7ff0fb0d774fac17528464adf4ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "b6d594e89dbf0b7b6086c9685c5821ab3d1e5ed6fdb92411c7a16214b76c1664"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "02aac6079fb82f4227af84ae12f77b784b724cbaa56d901c20154fb9829bdd13",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "f4309b0710678605195851312563b40c6b8b5b6f890cd24557fdb7deb886fec2"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "027cff22cbec944d0c76a14d2b20e3da88a763c5d984603603bc49c8f5fea69e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "0b79804194bcfc822cbe62a43e5cf22e9adde42e9be9c3d7599b5aeae5a91043"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "d4571749749e7237e01a6ef3b17e7a57bf2579e5e0c6e5b31f0f8a075f81c8ac"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "a6ab2ddd8458660013f81430f6d960c53f7abda003de194bc8e456f1435a2622"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "19beb53e7304115157c2866b9b661eccd98b92e255ebb38530ccfe95d00a191d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "cd4846b3c8343a749adb33031e900ffab70513fd02439910f94983b73db0ba10"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a7f5e7e70b7d471235fad4108d410ac223410ee89da4a890167054674e2a1bdb"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "b29fb5d7ebe7614170278b592446e0934950c9bea6162ad7024ca6c0cbd0b6a9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "ed564eee994349547da3e832424595f327661b9ca78119ca3b588205ae4904e0"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "973841660aebb81d0b9bb2e554bccb9c42abbc7c78bda6990c392d9a267b60b9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "fca64be024939db3a20d63f7c52937f93bf38e1eaaacd371835a12b85ba2f72e"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "c1c55bb3d962743a33d334026befb3ecb366df75a20a0b0b34208f7b46b75e29",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "220e0362bb82421af7ff3d4b6c9082a61311aec5b72bc82b9469b541145062ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8767c0257f7efd653535e4c9db000f2fe5079f6b599ab1cc12820304ad684688"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "1cbc420947d42a7eaa25d219d149a424369b095bad7bc2aa9b197d33bca59e16"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "eec3f65bc2dba342ab0f59666133c01bf72b6b5523f0378693885a6a3ddea9df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "9fcae80247c433b267a4a70c65ddb3854cf95ac24a6d1ab7e0263d02e483c3c7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "97464f4d8cb4f96a6f89b53fc0803fd15371c2ea7750ccc9497daeb71515a120"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "4ecf6b3e8f6078e98afdbb3a7d5329ddcfd85f8e03d9c2eb1aeb71093119170e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "cc22a76d426d138662043e0fd0d16efdc091b67c2dd2aa9b6e1d1ab7bda700d9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "a3846bdec5173518c0bd8bb0194228b0dfee503252ba85320b62fb7a3d390948"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "f146faa74b32cd7911707875af68b95764794f0797f8e39512a83cdd48505b3c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "244e4cd989860f4569b6ee65f70015fd8485c274bc44d686f6b9c5f59a74977d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d4497c72599e234bfd23070bf0dc54e0d0fefd9d8ecf58e22b096f7916a52d59"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "f0fb55a395bccc0f01f7ea862c9744ac6f570f3941597337451aafe3f1f23eed"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "d3d962c346c72cb1250bdff82dbb71fb73c68d88c12365605d7bf793d4b6e874",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e221c22f277479a9f68ba82fb38565461388815f577bb51aafbe65c1da5a4417"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "a1d4f9a173d15c2cc89514a2cb060f73075d0bdce3ab76e6ed8e91090cfcdac6"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3a03c0be1cb357fc900a26a018ce2f8f6206e2583b09b7ffd0c923551add4c22"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "87661c86057e4c7a58a76e203b2fa56f1cdb3509c4b38bfd3491cebd82fc2c70"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "b21980549ab439249b5ae24c9788b071f51cbafaba31d6589557d0b29a58c789"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "cbbfdca967c26328c7e7acecd6380582e0e1b345c8790bdd2d9077a9f4ee7983",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "76b84167fae4ddce9de6d8ca02c58ed4721c7a642ac742111e904c792047c8de"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "f7e8852b715c28c023fbe375322474fa02bc65d81ef67579e4541e1920ac863e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "f04a19dc7a53c8d24693ece34ef606f74fed7ab8aa7618ab81f19702015e6abe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "63567922dbc71b63439b1e4a3c938f5eedcfdcee9d6fffde5a864f61f5333819"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "9ea4db91d3a779fa30cfdc8687eb9a2a3869d460dacb70c90777b95309675cb3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4b2d038c9381f4898016eb01a2c76913dcc6a4116f100dd9c8e89ac69ce9f593"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "aa89affbc52a6f241bf07e1be914fb2e842c90ca64aa327c642bb5406ff427fb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "de47d8963e98151f040068e0f034cc51f017ce59b3b90a47be3459618c74e664"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "c07cd48fbb30c66116beea16eef28ba18aee78e8649999c56c865985231d0752",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "33b64f9f4c0ec9b96e7d5a3f8f4b55f73490d61c7ede72c8881e43f38f8406b0",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c280dbc0a622377a6930afad3baedcf4832fda03d4adb50c0b71fbccbe5f0cd9",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "fc5bddb6e146d8a5ca8c213f4709f024c8c4e6394a24d6f33c9770b75304cd84",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "67e669b4b9d32278d7afbb7c518b84dbed53dbc2f84ea9fb5ac83e01cc8c1682",
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
          "stage_v_final_candidate_retry_rebuild_1061cec69b2a",
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
            "stage_v_final_candidate_retry_rebuild_1061cec69b2a",
            "--timeout",
            "5400"
          ],
          "duration_seconds": 20.843,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"rebuild-serving\", \"dag_run_id\": \"stage_v_final_candidate_retry_rebuild_1061cec69b2a\", \"entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 90, \"iceberg_snapshot_ids\": {\"customers\": 8945732834443551666, \"order_items\": 8333618748302751604, \"order_payments\": 2342546804373807134, \"order_reviews\": 1873788046910446323, \"orders\": 2860036943269124164, \"product_category_translation\": 2510271481881063845, \"products\": 6434977924513876130, \"sellers\": 6608875651304288148}, \"materialized_event_count\": 90, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000004\", \"sync_run_seq\": 4}\n",
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
          "duration_seconds": 1.782,
          "exit_code": 0,
          "stderr": "",
          "stdout": "e1589f3f748f05c\"}]}, \"order_items\": {\"manifest_sha256\": \"fc42d0f5000a46610d7c036934fd58bf11c4b57508806f06e0bc27e268ab2527\", \"row_count\": 18, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"order_item_id\": 1, \"row_hash\": \"ec1cc0c3f5db3d730e635fb58079f48ba19bdf7865ef3dfe1fd3981c6f7d723d\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"order_item_id\": 1, \"row_hash\": \"54fa68b1ada8664ca1694f141440421865b55dbfc21e4f43ae9fe894dea3a04e\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"order_item_id\": 1, \"row_hash\": \"3cda1da0d9d949e6d04bcb63c3e7ca7f300d005096eeefc67e7b779baa554a8e\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"order_item_id\": 2, \"row_hash\": \"eca4244589d571813a4bc5bf33c2d024292696ab3fe8c8c83e2ecc673bc31df0\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"order_item_id\": 1, \"row_hash\": \"072c36ff9acbdfe5cfc41bbecb57b119303c6ce70d57bee2a6ae6f3ad85bea99\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"order_item_id\": 1, \"row_hash\": \"761da00fd9c9353b76334fd593b54ee083ca92f8cf462f8c47ab167c5f4ffd87\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"order_item_id\": 1, \"row_hash\": \"a1337cdc1ab4edd0305a707a0d0f934d6b7326225224d530d25315f83584140d\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"order_item_id\": 2, \"row_hash\": \"b023239a3fb52428341c2d0ac83548aa4c5b56d60f782de7af781665b6c70b71\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"order_item_id\": 1, \"row_hash\": \"78a8a0e8ffbe795b848306775981ea545d9d3a92fca7a0909194b278582c786d\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"order_item_id\": 1, \"row_hash\": \"aa878cb2e01217ebd62810321dce08cdf989e42661b9559d9814579a08f7a61b\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"order_item_id\": 1, \"row_hash\": \"5f7ba42608a1aa3ba365af07dd4732b6d8e317be259e46915f790f1bca3b6838\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"order_item_id\": 2, \"row_hash\": \"7ae25e4bd73616a2e26f2b64076ac21f70f247d81f86ddf680cb99e00829b5ce\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"order_item_id\": 1, \"row_hash\": \"e403901ebfa72ca8ca4630d58f72880e096dba80fcb0f33fd0680be27cf9b883\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"order_item_id\": 1, \"row_hash\": \"a9e6f3df1f60da87742d3c7a8e28ee269f222932e6f039b9c97fdd18d90da3aa\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"order_item_id\": 1, \"row_hash\": \"0ed72ee5665c801c07fc4c670959053d3441657b4d83334bf86bbb7b2e7fd733\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"order_item_id\": 2, \"row_hash\": \"5a8a7571c7c04d1c3873f8b5ee587bfd4a5f732493cb11d739691c3880d2fb69\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"order_item_id\": 1, \"row_hash\": \"4bedd28f6c22c627fd07384225906461f0cf7c2ab94743da271a040ceda886df\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"order_item_id\": 2, \"row_hash\": \"179c496072c4b388cb6095ae0c2d5fec453067cba892912a2e186af2a1164eb6\"}]}, \"order_payments\": {\"manifest_sha256\": \"be5bac52cc658a3375f516184f19fe3a2e98cb2a71641dc08bd68c5aa3f84f82\", \"row_count\": 16, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"payment_sequential\": 1, \"row_hash\": \"8038b580be0b90957066d240104b2b6b9e684108acf5a28b8e47a274db7587d8\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"payment_sequential\": 1, \"row_hash\": \"1b19c21b95f5925ba9207a5fd50e79ef03627c3322df76403062066e4ab642cb\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"payment_sequential\": 1, \"row_hash\": \"478834c48ed92db6b1b68ef5256b686eb63bb1f5a21be323e806616f14cda6ea\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"payment_sequential\": 1, \"row_hash\": \"0bab3e540d8d6d413df39c70ef6e9428ef35d2dd92f8981e536bda699fa38835\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"payment_sequential\": 2, \"row_hash\": \"ea928cb6e0f7daa6019218107d8d984f005ea9d6a26e7aceaecac5d331e1bd55\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"payment_sequential\": 1, \"row_hash\": \"e89ee7a61d31802fa65e8f8a3d32d4b2ecd141dd357789ae4bd7db247131c61a\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"payment_sequential\": 1, \"row_hash\": \"37e7a3fcf3b9d4d225e31c1e0a45a457161a6d406a0001dcfff004fd8d670f1a\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"payment_sequential\": 1, \"row_hash\": \"6b0241e0ca2965fa965855551332d23c57ad30d89c3e8c62b2705ba1d5aedc06\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"payment_sequential\": 1, \"row_hash\": \"b9e5788236231faa76bd019fbb9d12a39d12b8fe404e47286fbcb598fdfea559\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"payment_sequential\": 2, \"row_hash\": \"502a7400785b00f6ce4c98d733e3d6012e58e6c5936040d6351dcc6da0e087d3\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"payment_sequential\": 1, \"row_hash\": \"68884f5576f1982bff730e5010fb6936404d7f2f2d1255091c93661ca391507f\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"payment_sequential\": 1, \"row_hash\": \"12b4fb9a2da3a268015967a8ebee50c655ea56b2259d53daefb23549ad5a6d8a\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"payment_sequential\": 1, \"row_hash\": \"d6e1d6f6663946ef9055d4f679323eb4275b45aa4ecd551a650a3ce6936a00d7\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"payment_sequential\": 1, \"row_hash\": \"f9d55b6e7a4c37398aa4df49485984eb0934ac3f6d6ed89abc871314f4604550\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"payment_sequential\": 1, \"row_hash\": \"dcacadab16a91c1904fca96c9a759b6cc76a7ff0fb0d774fac17528464adf4ab\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"payment_sequential\": 2, \"row_hash\": \"b6d594e89dbf0b7b6086c9685c5821ab3d1e5ed6fdb92411c7a16214b76c1664\"}]}, \"order_reviews\": {\"manifest_sha256\": \"02aac6079fb82f4227af84ae12f77b784b724cbaa56d901c20154fb9829bdd13\", \"row_count\": 12, \"rows\": [{\"is_deleted\": false, \"review_id\": \"review_001\", \"row_hash\": \"f4309b0710678605195851312563b40c6b8b5b6f890cd24557fdb7deb886fec2\"}, {\"is_deleted\": false, \"review_id\": \"review_002\", \"row_hash\": \"027cff22cbec944d0c76a14d2b20e3da88a763c5d984603603bc49c8f5fea69e\"}, {\"is_deleted\": false, \"review_id\": \"review_003\", \"row_hash\": \"0b79804194bcfc822cbe62a43e5cf22e9adde42e9be9c3d7599b5aeae5a91043\"}, {\"is_deleted\": false, \"review_id\": \"review_004\", \"row_hash\": \"d4571749749e7237e01a6ef3b17e7a57bf2579e5e0c6e5b31f0f8a075f81c8ac\"}, {\"is_deleted\": false, \"review_id\": \"review_005\", \"row_hash\": \"a6ab2ddd8458660013f81430f6d960c53f7abda003de194bc8e456f1435a2622\"}, {\"is_deleted\": false, \"review_id\": \"review_006\", \"row_hash\": \"19beb53e7304115157c2866b9b661eccd98b92e255ebb38530ccfe95d00a191d\"}, {\"is_deleted\": false, \"review_id\": \"review_007\", \"row_hash\": \"cd4846b3c8343a749adb33031e900ffab70513fd02439910f94983b73db0ba10\"}, {\"is_deleted\": false, \"review_id\": \"review_008\", \"row_hash\": \"a7f5e7e70b7d471235fad4108d410ac223410ee89da4a890167054674e2a1bdb\"}, {\"is_deleted\": false, \"review_id\": \"review_009\", \"row_hash\": \"b29fb5d7ebe7614170278b592446e0934950c9bea6162ad7024ca6c0cbd0b6a9\"}, {\"is_deleted\": false, \"review_id\": \"review_010\", \"row_hash\": \"ed564eee994349547da3e832424595f327661b9ca78119ca3b588205ae4904e0\"}, {\"is_deleted\": false, \"review_id\": \"review_011\", \"row_hash\": \"973841660aebb81d0b9bb2e554bccb9c42abbc7c78bda6990c392d9a267b60b9\"}, {\"is_deleted\": false, \"review_id\": \"review_012\", \"row_hash\": \"fca64be024939db3a20d63f7c52937f93bf38e1eaaacd371835a12b85ba2f72e\"}]}, \"orders\": {\"manifest_sha256\": \"c1c55bb3d962743a33d334026befb3ecb366df75a20a0b0b34208f7b46b75e29\", \"row_count\": 13, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"row_hash\": \"220e0362bb82421af7ff3d4b6c9082a61311aec5b72bc82b9469b541145062ae\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"row_hash\": \"8767c0257f7efd653535e4c9db000f2fe5079f6b599ab1cc12820304ad684688\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"row_hash\": \"1cbc420947d42a7eaa25d219d149a424369b095bad7bc2aa9b197d33bca59e16\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"row_hash\": \"eec3f65bc2dba342ab0f59666133c01bf72b6b5523f0378693885a6a3ddea9df\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"row_hash\": \"9fcae80247c433b267a4a70c65ddb3854cf95ac24a6d1ab7e0263d02e483c3c7\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"row_hash\": \"97464f4d8cb4f96a6f89b53fc0803fd15371c2ea7750ccc9497daeb71515a120\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"row_hash\": \"4ecf6b3e8f6078e98afdbb3a7d5329ddcfd85f8e03d9c2eb1aeb71093119170e\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"row_hash\": \"cc22a76d426d138662043e0fd0d16efdc091b67c2dd2aa9b6e1d1ab7bda700d9\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"row_hash\": \"a3846bdec5173518c0bd8bb0194228b0dfee503252ba85320b62fb7a3d390948\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"row_hash\": \"f146faa74b32cd7911707875af68b95764794f0797f8e39512a83cdd48505b3c\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"row_hash\": \"244e4cd989860f4569b6ee65f70015fd8485c274bc44d686f6b9c5f59a74977d\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"row_hash\": \"d4497c72599e234bfd23070bf0dc54e0d0fefd9d8ecf58e22b096f7916a52d59\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"row_hash\": \"f0fb55a395bccc0f01f7ea862c9744ac6f570f3941597337451aafe3f1f23eed\"}]}, \"product_category_translation\": {\"manifest_sha256\": \"d3d962c346c72cb1250bdff82dbb71fb73c68d88c12365605d7bf793d4b6e874\", \"row_count\": 5, \"rows\": [{\"is_deleted\": false, \"product_category_name\": \"beleza_saude\", \"row_hash\": \"e221c22f277479a9f68ba82fb38565461388815f577bb51aafbe65c1da5a4417\"}, {\"is_deleted\": false, \"product_category_name\": \"informatica_acessorios\", \"row_hash\": \"a1d4f9a173d15c2cc89514a2cb060f73075d0bdce3ab76e6ed8e91090cfcdac6\"}, {\"is_deleted\": false, \"product_category_name\": \"moveis_decoracao\", \"row_hash\": \"3a03c0be1cb357fc900a26a018ce2f8f6206e2583b09b7ffd0c923551add4c22\"}, {\"is_deleted\": false, \"product_category_name\": \"telefonia\", \"row_hash\": \"87661c86057e4c7a58a76e203b2fa56f1cdb3509c4b38bfd3491cebd82fc2c70\"}, {\"is_deleted\": false, \"product_category_name\": \"utilidades_domesticas\", \"row_hash\": \"b21980549ab439249b5ae24c9788b071f51cbafaba31d6589557d0b29a58c789\"}]}, \"products\": {\"manifest_sha256\": \"cbbfdca967c26328c7e7acecd6380582e0e1b345c8790bdd2d9077a9f4ee7983\", \"row_count\": 8, \"rows\": [{\"is_deleted\": false, \"product_id\": \"product_001\", \"row_hash\": \"76b84167fae4ddce9de6d8ca02c58ed4721c7a642ac742111e904c792047c8de\"}, {\"is_deleted\": false, \"product_id\": \"product_002\", \"row_hash\": \"f7e8852b715c28c023fbe375322474fa02bc65d81ef67579e4541e1920ac863e\"}, {\"is_deleted\": false, \"product_id\": \"product_003\", \"row_hash\": \"f04a19dc7a53c8d24693ece34ef606f74fed7ab8aa7618ab81f19702015e6abe\"}, {\"is_deleted\": false, \"product_id\": \"product_004\", \"row_hash\": \"63567922dbc71b63439b1e4a3c938f5eedcfdcee9d6fffde5a864f61f5333819\"}, {\"is_deleted\": false, \"product_id\": \"product_005\", \"row_hash\": \"9ea4db91d3a779fa30cfdc8687eb9a2a3869d460dacb70c90777b95309675cb3\"}, {\"is_deleted\": false, \"product_id\": \"product_006\", \"row_hash\": \"4b2d038c9381f4898016eb01a2c76913dcc6a4116f100dd9c8e89ac69ce9f593\"}, {\"is_deleted\": false, \"product_id\": \"product_007\", \"row_hash\": \"aa89affbc52a6f241bf07e1be914fb2e842c90ca64aa327c642bb5406ff427fb\"}, {\"is_deleted\": false, \"product_id\": \"product_008\", \"row_hash\": \"de47d8963e98151f040068e0f034cc51f017ce59b3b90a47be3459618c74e664\"}]}, \"sellers\": {\"manifest_sha256\": \"c07cd48fbb30c66116beea16eef28ba18aee78e8649999c56c865985231d0752\", \"row_count\": 4, \"rows\": [{\"is_deleted\": false, \"row_hash\": \"33b64f9f4c0ec9b96e7d5a3f8f4b55f73490d61c7ede72c8881e43f38f8406b0\", \"seller_id\": \"seller_001\"}, {\"is_deleted\": false, \"row_hash\": \"c280dbc0a622377a6930afad3baedcf4832fda03d4adb50c0b71fbccbe5f0cd9\", \"seller_id\": \"seller_002\"}, {\"is_deleted\": false, \"row_hash\": \"fc5bddb6e146d8a5ca8c213f4709f024c8c4e6394a24d6f33c9770b75304cd84\", \"seller_id\": \"seller_003\"}, {\"is_deleted\": false, \"row_hash\": \"67e669b4b9d32278d7afbb7c518b84dbed53dbc2f84ea9fb5ac83e01cc8c1682\", \"seller_id\": \"seller_004\"}]}}}, \"runtime\": {\"last_published_sync_run_seq\": 4, \"lease_owner_id\": null, \"source_snapshot_completed\": true}, \"stable_current_counts\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"status\": \"ready\", \"sync_run_id\": \"sync-00000000000000000004\", \"sync_run_seq\": 4}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 22.632,
      "gate": "09-rebuild",
      "status": "PASS",
      "timestamp": "2026-08-03T18:04:50.138714+00:00"
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
              "customers": 8945732834443551666,
              "order_items": 8333618748302751604,
              "order_payments": 2342546804373807134,
              "order_reviews": 1873788046910446323,
              "orders": 2860036943269124164,
              "product_category_translation": 2510271481881063845,
              "products": 6434977924513876130,
              "sellers": 6608875651304288148
            },
            "materialized_event_count": 90,
            "row_manifests": {
              "candidate_physical": {
                "customers": {
                  "manifest_sha256": "c5e9bd8436395273a8e1cd5baee5332af3609387a180503a35ac3d2bb48af6d0",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "0d10cdd2fc05399400d89cdb24746b0b289d78f7a8a4b82598fe21d11ae9b731"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "a8de535a3a12f987810975cb44f3e288ff492e72024588920c5787e2820f2100"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "7e0b4d5d0f516dceaf87941bb8cf52b35111a338776f98346e056a4aa7a3ff5f"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "b7284338d73bb5bf5105d48f16264b2b1855559a24329933c9060f90c0d92bf5"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "7ab42f667edd04e117e4a876cfe7bb28173df733a0b90f16c04a1b7edb11042c"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "987297199383f6a17f975b3cd3d0956a7c161c2c46144f7e190c21db8d377124"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "851f578e9ebb923a9c733f988473dfd5d08a484d9abcccf9677aa79690dbb4b9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "7a28f748bef00843e2255aba1c1b4f7a3616b19f41f04358e706e3729780301a"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "bde17534e3035031a2b4cadf89808ad4be3870b8e431bcb48e1589f3f748f05c"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "fc42d0f5000a46610d7c036934fd58bf11c4b57508806f06e0bc27e268ab2527",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "ec1cc0c3f5db3d730e635fb58079f48ba19bdf7865ef3dfe1fd3981c6f7d723d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "54fa68b1ada8664ca1694f141440421865b55dbfc21e4f43ae9fe894dea3a04e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "3cda1da0d9d949e6d04bcb63c3e7ca7f300d005096eeefc67e7b779baa554a8e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "eca4244589d571813a4bc5bf33c2d024292696ab3fe8c8c83e2ecc673bc31df0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "072c36ff9acbdfe5cfc41bbecb57b119303c6ce70d57bee2a6ae6f3ad85bea99"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "761da00fd9c9353b76334fd593b54ee083ca92f8cf462f8c47ab167c5f4ffd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "a1337cdc1ab4edd0305a707a0d0f934d6b7326225224d530d25315f83584140d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "b023239a3fb52428341c2d0ac83548aa4c5b56d60f782de7af781665b6c70b71"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "78a8a0e8ffbe795b848306775981ea545d9d3a92fca7a0909194b278582c786d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "aa878cb2e01217ebd62810321dce08cdf989e42661b9559d9814579a08f7a61b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "5f7ba42608a1aa3ba365af07dd4732b6d8e317be259e46915f790f1bca3b6838"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "7ae25e4bd73616a2e26f2b64076ac21f70f247d81f86ddf680cb99e00829b5ce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "e403901ebfa72ca8ca4630d58f72880e096dba80fcb0f33fd0680be27cf9b883"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "a9e6f3df1f60da87742d3c7a8e28ee269f222932e6f039b9c97fdd18d90da3aa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "0ed72ee5665c801c07fc4c670959053d3441657b4d83334bf86bbb7b2e7fd733"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5a8a7571c7c04d1c3873f8b5ee587bfd4a5f732493cb11d739691c3880d2fb69"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "4bedd28f6c22c627fd07384225906461f0cf7c2ab94743da271a040ceda886df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "179c496072c4b388cb6095ae0c2d5fec453067cba892912a2e186af2a1164eb6"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "be5bac52cc658a3375f516184f19fe3a2e98cb2a71641dc08bd68c5aa3f84f82",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "8038b580be0b90957066d240104b2b6b9e684108acf5a28b8e47a274db7587d8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "1b19c21b95f5925ba9207a5fd50e79ef03627c3322df76403062066e4ab642cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "478834c48ed92db6b1b68ef5256b686eb63bb1f5a21be323e806616f14cda6ea"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "0bab3e540d8d6d413df39c70ef6e9428ef35d2dd92f8981e536bda699fa38835"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "ea928cb6e0f7daa6019218107d8d984f005ea9d6a26e7aceaecac5d331e1bd55"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "e89ee7a61d31802fa65e8f8a3d32d4b2ecd141dd357789ae4bd7db247131c61a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "37e7a3fcf3b9d4d225e31c1e0a45a457161a6d406a0001dcfff004fd8d670f1a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "6b0241e0ca2965fa965855551332d23c57ad30d89c3e8c62b2705ba1d5aedc06"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "b9e5788236231faa76bd019fbb9d12a39d12b8fe404e47286fbcb598fdfea559"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "502a7400785b00f6ce4c98d733e3d6012e58e6c5936040d6351dcc6da0e087d3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "68884f5576f1982bff730e5010fb6936404d7f2f2d1255091c93661ca391507f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "12b4fb9a2da3a268015967a8ebee50c655ea56b2259d53daefb23549ad5a6d8a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "d6e1d6f6663946ef9055d4f679323eb4275b45aa4ecd551a650a3ce6936a00d7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "f9d55b6e7a4c37398aa4df49485984eb0934ac3f6d6ed89abc871314f4604550"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "dcacadab16a91c1904fca96c9a759b6cc76a7ff0fb0d774fac17528464adf4ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "b6d594e89dbf0b7b6086c9685c5821ab3d1e5ed6fdb92411c7a16214b76c1664"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "972faa1609774f5e100b46b1ea1617ad6335de07b8f0cd7f4fc42c159a45ac2e",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "f4309b0710678605195851312563b40c6b8b5b6f890cd24557fdb7deb886fec2"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "027cff22cbec944d0c76a14d2b20e3da88a763c5d984603603bc49c8f5fea69e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "0b79804194bcfc822cbe62a43e5cf22e9adde42e9be9c3d7599b5aeae5a91043"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "d4571749749e7237e01a6ef3b17e7a57bf2579e5e0c6e5b31f0f8a075f81c8ac"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "a6ab2ddd8458660013f81430f6d960c53f7abda003de194bc8e456f1435a2622"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "19beb53e7304115157c2866b9b661eccd98b92e255ebb38530ccfe95d00a191d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "cd4846b3c8343a749adb33031e900ffab70513fd02439910f94983b73db0ba10"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a7f5e7e70b7d471235fad4108d410ac223410ee89da4a890167054674e2a1bdb"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "b29fb5d7ebe7614170278b592446e0934950c9bea6162ad7024ca6c0cbd0b6a9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "ed564eee994349547da3e832424595f327661b9ca78119ca3b588205ae4904e0"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "973841660aebb81d0b9bb2e554bccb9c42abbc7c78bda6990c392d9a267b60b9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "fca64be024939db3a20d63f7c52937f93bf38e1eaaacd371835a12b85ba2f72e"
                    },
                    {
                      "is_deleted": true,
                      "review_id": "wave2_review_001",
                      "row_hash": "8f42ad9a706ce6d984d1e3438982f61b9621494cbb81e4dbed0f8059113e41d6"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "c1c55bb3d962743a33d334026befb3ecb366df75a20a0b0b34208f7b46b75e29",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "220e0362bb82421af7ff3d4b6c9082a61311aec5b72bc82b9469b541145062ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8767c0257f7efd653535e4c9db000f2fe5079f6b599ab1cc12820304ad684688"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "1cbc420947d42a7eaa25d219d149a424369b095bad7bc2aa9b197d33bca59e16"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "eec3f65bc2dba342ab0f59666133c01bf72b6b5523f0378693885a6a3ddea9df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "9fcae80247c433b267a4a70c65ddb3854cf95ac24a6d1ab7e0263d02e483c3c7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "97464f4d8cb4f96a6f89b53fc0803fd15371c2ea7750ccc9497daeb71515a120"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "4ecf6b3e8f6078e98afdbb3a7d5329ddcfd85f8e03d9c2eb1aeb71093119170e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "cc22a76d426d138662043e0fd0d16efdc091b67c2dd2aa9b6e1d1ab7bda700d9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "a3846bdec5173518c0bd8bb0194228b0dfee503252ba85320b62fb7a3d390948"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "f146faa74b32cd7911707875af68b95764794f0797f8e39512a83cdd48505b3c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "244e4cd989860f4569b6ee65f70015fd8485c274bc44d686f6b9c5f59a74977d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d4497c72599e234bfd23070bf0dc54e0d0fefd9d8ecf58e22b096f7916a52d59"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "f0fb55a395bccc0f01f7ea862c9744ac6f570f3941597337451aafe3f1f23eed"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "d3d962c346c72cb1250bdff82dbb71fb73c68d88c12365605d7bf793d4b6e874",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e221c22f277479a9f68ba82fb38565461388815f577bb51aafbe65c1da5a4417"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "a1d4f9a173d15c2cc89514a2cb060f73075d0bdce3ab76e6ed8e91090cfcdac6"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3a03c0be1cb357fc900a26a018ce2f8f6206e2583b09b7ffd0c923551add4c22"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "87661c86057e4c7a58a76e203b2fa56f1cdb3509c4b38bfd3491cebd82fc2c70"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "b21980549ab439249b5ae24c9788b071f51cbafaba31d6589557d0b29a58c789"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "cbbfdca967c26328c7e7acecd6380582e0e1b345c8790bdd2d9077a9f4ee7983",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "76b84167fae4ddce9de6d8ca02c58ed4721c7a642ac742111e904c792047c8de"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "f7e8852b715c28c023fbe375322474fa02bc65d81ef67579e4541e1920ac863e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "f04a19dc7a53c8d24693ece34ef606f74fed7ab8aa7618ab81f19702015e6abe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "63567922dbc71b63439b1e4a3c938f5eedcfdcee9d6fffde5a864f61f5333819"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "9ea4db91d3a779fa30cfdc8687eb9a2a3869d460dacb70c90777b95309675cb3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4b2d038c9381f4898016eb01a2c76913dcc6a4116f100dd9c8e89ac69ce9f593"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "aa89affbc52a6f241bf07e1be914fb2e842c90ca64aa327c642bb5406ff427fb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "de47d8963e98151f040068e0f034cc51f017ce59b3b90a47be3459618c74e664"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "c07cd48fbb30c66116beea16eef28ba18aee78e8649999c56c865985231d0752",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "33b64f9f4c0ec9b96e7d5a3f8f4b55f73490d61c7ede72c8881e43f38f8406b0",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c280dbc0a622377a6930afad3baedcf4832fda03d4adb50c0b71fbccbe5f0cd9",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "fc5bddb6e146d8a5ca8c213f4709f024c8c4e6394a24d6f33c9770b75304cd84",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "67e669b4b9d32278d7afbb7c518b84dbed53dbc2f84ea9fb5ac83e01cc8c1682",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "candidate_visible": {
                "customers": {
                  "manifest_sha256": "c5e9bd8436395273a8e1cd5baee5332af3609387a180503a35ac3d2bb48af6d0",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "0d10cdd2fc05399400d89cdb24746b0b289d78f7a8a4b82598fe21d11ae9b731"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "a8de535a3a12f987810975cb44f3e288ff492e72024588920c5787e2820f2100"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "7e0b4d5d0f516dceaf87941bb8cf52b35111a338776f98346e056a4aa7a3ff5f"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "b7284338d73bb5bf5105d48f16264b2b1855559a24329933c9060f90c0d92bf5"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "7ab42f667edd04e117e4a876cfe7bb28173df733a0b90f16c04a1b7edb11042c"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "987297199383f6a17f975b3cd3d0956a7c161c2c46144f7e190c21db8d377124"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "851f578e9ebb923a9c733f988473dfd5d08a484d9abcccf9677aa79690dbb4b9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "7a28f748bef00843e2255aba1c1b4f7a3616b19f41f04358e706e3729780301a"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "bde17534e3035031a2b4cadf89808ad4be3870b8e431bcb48e1589f3f748f05c"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "fc42d0f5000a46610d7c036934fd58bf11c4b57508806f06e0bc27e268ab2527",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "ec1cc0c3f5db3d730e635fb58079f48ba19bdf7865ef3dfe1fd3981c6f7d723d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "54fa68b1ada8664ca1694f141440421865b55dbfc21e4f43ae9fe894dea3a04e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "3cda1da0d9d949e6d04bcb63c3e7ca7f300d005096eeefc67e7b779baa554a8e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "eca4244589d571813a4bc5bf33c2d024292696ab3fe8c8c83e2ecc673bc31df0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "072c36ff9acbdfe5cfc41bbecb57b119303c6ce70d57bee2a6ae6f3ad85bea99"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "761da00fd9c9353b76334fd593b54ee083ca92f8cf462f8c47ab167c5f4ffd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "a1337cdc1ab4edd0305a707a0d0f934d6b7326225224d530d25315f83584140d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "b023239a3fb52428341c2d0ac83548aa4c5b56d60f782de7af781665b6c70b71"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "78a8a0e8ffbe795b848306775981ea545d9d3a92fca7a0909194b278582c786d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "aa878cb2e01217ebd62810321dce08cdf989e42661b9559d9814579a08f7a61b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "5f7ba42608a1aa3ba365af07dd4732b6d8e317be259e46915f790f1bca3b6838"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "7ae25e4bd73616a2e26f2b64076ac21f70f247d81f86ddf680cb99e00829b5ce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "e403901ebfa72ca8ca4630d58f72880e096dba80fcb0f33fd0680be27cf9b883"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "a9e6f3df1f60da87742d3c7a8e28ee269f222932e6f039b9c97fdd18d90da3aa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "0ed72ee5665c801c07fc4c670959053d3441657b4d83334bf86bbb7b2e7fd733"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5a8a7571c7c04d1c3873f8b5ee587bfd4a5f732493cb11d739691c3880d2fb69"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "4bedd28f6c22c627fd07384225906461f0cf7c2ab94743da271a040ceda886df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "179c496072c4b388cb6095ae0c2d5fec453067cba892912a2e186af2a1164eb6"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "be5bac52cc658a3375f516184f19fe3a2e98cb2a71641dc08bd68c5aa3f84f82",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "8038b580be0b90957066d240104b2b6b9e684108acf5a28b8e47a274db7587d8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "1b19c21b95f5925ba9207a5fd50e79ef03627c3322df76403062066e4ab642cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "478834c48ed92db6b1b68ef5256b686eb63bb1f5a21be323e806616f14cda6ea"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "0bab3e540d8d6d413df39c70ef6e9428ef35d2dd92f8981e536bda699fa38835"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "ea928cb6e0f7daa6019218107d8d984f005ea9d6a26e7aceaecac5d331e1bd55"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "e89ee7a61d31802fa65e8f8a3d32d4b2ecd141dd357789ae4bd7db247131c61a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "37e7a3fcf3b9d4d225e31c1e0a45a457161a6d406a0001dcfff004fd8d670f1a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "6b0241e0ca2965fa965855551332d23c57ad30d89c3e8c62b2705ba1d5aedc06"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "b9e5788236231faa76bd019fbb9d12a39d12b8fe404e47286fbcb598fdfea559"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "502a7400785b00f6ce4c98d733e3d6012e58e6c5936040d6351dcc6da0e087d3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "68884f5576f1982bff730e5010fb6936404d7f2f2d1255091c93661ca391507f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "12b4fb9a2da3a268015967a8ebee50c655ea56b2259d53daefb23549ad5a6d8a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "d6e1d6f6663946ef9055d4f679323eb4275b45aa4ecd551a650a3ce6936a00d7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "f9d55b6e7a4c37398aa4df49485984eb0934ac3f6d6ed89abc871314f4604550"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "dcacadab16a91c1904fca96c9a759b6cc76a7ff0fb0d774fac17528464adf4ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "b6d594e89dbf0b7b6086c9685c5821ab3d1e5ed6fdb92411c7a16214b76c1664"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "02aac6079fb82f4227af84ae12f77b784b724cbaa56d901c20154fb9829bdd13",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "f4309b0710678605195851312563b40c6b8b5b6f890cd24557fdb7deb886fec2"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "027cff22cbec944d0c76a14d2b20e3da88a763c5d984603603bc49c8f5fea69e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "0b79804194bcfc822cbe62a43e5cf22e9adde42e9be9c3d7599b5aeae5a91043"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "d4571749749e7237e01a6ef3b17e7a57bf2579e5e0c6e5b31f0f8a075f81c8ac"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "a6ab2ddd8458660013f81430f6d960c53f7abda003de194bc8e456f1435a2622"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "19beb53e7304115157c2866b9b661eccd98b92e255ebb38530ccfe95d00a191d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "cd4846b3c8343a749adb33031e900ffab70513fd02439910f94983b73db0ba10"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a7f5e7e70b7d471235fad4108d410ac223410ee89da4a890167054674e2a1bdb"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "b29fb5d7ebe7614170278b592446e0934950c9bea6162ad7024ca6c0cbd0b6a9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "ed564eee994349547da3e832424595f327661b9ca78119ca3b588205ae4904e0"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "973841660aebb81d0b9bb2e554bccb9c42abbc7c78bda6990c392d9a267b60b9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "fca64be024939db3a20d63f7c52937f93bf38e1eaaacd371835a12b85ba2f72e"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "c1c55bb3d962743a33d334026befb3ecb366df75a20a0b0b34208f7b46b75e29",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "220e0362bb82421af7ff3d4b6c9082a61311aec5b72bc82b9469b541145062ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8767c0257f7efd653535e4c9db000f2fe5079f6b599ab1cc12820304ad684688"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "1cbc420947d42a7eaa25d219d149a424369b095bad7bc2aa9b197d33bca59e16"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "eec3f65bc2dba342ab0f59666133c01bf72b6b5523f0378693885a6a3ddea9df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "9fcae80247c433b267a4a70c65ddb3854cf95ac24a6d1ab7e0263d02e483c3c7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "97464f4d8cb4f96a6f89b53fc0803fd15371c2ea7750ccc9497daeb71515a120"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "4ecf6b3e8f6078e98afdbb3a7d5329ddcfd85f8e03d9c2eb1aeb71093119170e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "cc22a76d426d138662043e0fd0d16efdc091b67c2dd2aa9b6e1d1ab7bda700d9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "a3846bdec5173518c0bd8bb0194228b0dfee503252ba85320b62fb7a3d390948"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "f146faa74b32cd7911707875af68b95764794f0797f8e39512a83cdd48505b3c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "244e4cd989860f4569b6ee65f70015fd8485c274bc44d686f6b9c5f59a74977d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d4497c72599e234bfd23070bf0dc54e0d0fefd9d8ecf58e22b096f7916a52d59"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "f0fb55a395bccc0f01f7ea862c9744ac6f570f3941597337451aafe3f1f23eed"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "d3d962c346c72cb1250bdff82dbb71fb73c68d88c12365605d7bf793d4b6e874",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e221c22f277479a9f68ba82fb38565461388815f577bb51aafbe65c1da5a4417"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "a1d4f9a173d15c2cc89514a2cb060f73075d0bdce3ab76e6ed8e91090cfcdac6"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3a03c0be1cb357fc900a26a018ce2f8f6206e2583b09b7ffd0c923551add4c22"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "87661c86057e4c7a58a76e203b2fa56f1cdb3509c4b38bfd3491cebd82fc2c70"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "b21980549ab439249b5ae24c9788b071f51cbafaba31d6589557d0b29a58c789"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "cbbfdca967c26328c7e7acecd6380582e0e1b345c8790bdd2d9077a9f4ee7983",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "76b84167fae4ddce9de6d8ca02c58ed4721c7a642ac742111e904c792047c8de"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "f7e8852b715c28c023fbe375322474fa02bc65d81ef67579e4541e1920ac863e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "f04a19dc7a53c8d24693ece34ef606f74fed7ab8aa7618ab81f19702015e6abe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "63567922dbc71b63439b1e4a3c938f5eedcfdcee9d6fffde5a864f61f5333819"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "9ea4db91d3a779fa30cfdc8687eb9a2a3869d460dacb70c90777b95309675cb3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4b2d038c9381f4898016eb01a2c76913dcc6a4116f100dd9c8e89ac69ce9f593"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "aa89affbc52a6f241bf07e1be914fb2e842c90ca64aa327c642bb5406ff427fb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "de47d8963e98151f040068e0f034cc51f017ce59b3b90a47be3459618c74e664"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "c07cd48fbb30c66116beea16eef28ba18aee78e8649999c56c865985231d0752",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "33b64f9f4c0ec9b96e7d5a3f8f4b55f73490d61c7ede72c8881e43f38f8406b0",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c280dbc0a622377a6930afad3baedcf4832fda03d4adb50c0b71fbccbe5f0cd9",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "fc5bddb6e146d8a5ca8c213f4709f024c8c4e6394a24d6f33c9770b75304cd84",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "67e669b4b9d32278d7afbb7c518b84dbed53dbc2f84ea9fb5ac83e01cc8c1682",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "iceberg_physical": {
                "customers": {
                  "manifest_sha256": "c5e9bd8436395273a8e1cd5baee5332af3609387a180503a35ac3d2bb48af6d0",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "0d10cdd2fc05399400d89cdb24746b0b289d78f7a8a4b82598fe21d11ae9b731"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "a8de535a3a12f987810975cb44f3e288ff492e72024588920c5787e2820f2100"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "7e0b4d5d0f516dceaf87941bb8cf52b35111a338776f98346e056a4aa7a3ff5f"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "b7284338d73bb5bf5105d48f16264b2b1855559a24329933c9060f90c0d92bf5"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "7ab42f667edd04e117e4a876cfe7bb28173df733a0b90f16c04a1b7edb11042c"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "987297199383f6a17f975b3cd3d0956a7c161c2c46144f7e190c21db8d377124"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "851f578e9ebb923a9c733f988473dfd5d08a484d9abcccf9677aa79690dbb4b9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "7a28f748bef00843e2255aba1c1b4f7a3616b19f41f04358e706e3729780301a"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "bde17534e3035031a2b4cadf89808ad4be3870b8e431bcb48e1589f3f748f05c"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "fc42d0f5000a46610d7c036934fd58bf11c4b57508806f06e0bc27e268ab2527",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "ec1cc0c3f5db3d730e635fb58079f48ba19bdf7865ef3dfe1fd3981c6f7d723d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "54fa68b1ada8664ca1694f141440421865b55dbfc21e4f43ae9fe894dea3a04e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "3cda1da0d9d949e6d04bcb63c3e7ca7f300d005096eeefc67e7b779baa554a8e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "eca4244589d571813a4bc5bf33c2d024292696ab3fe8c8c83e2ecc673bc31df0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "072c36ff9acbdfe5cfc41bbecb57b119303c6ce70d57bee2a6ae6f3ad85bea99"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "761da00fd9c9353b76334fd593b54ee083ca92f8cf462f8c47ab167c5f4ffd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "a1337cdc1ab4edd0305a707a0d0f934d6b7326225224d530d25315f83584140d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "b023239a3fb52428341c2d0ac83548aa4c5b56d60f782de7af781665b6c70b71"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "78a8a0e8ffbe795b848306775981ea545d9d3a92fca7a0909194b278582c786d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "aa878cb2e01217ebd62810321dce08cdf989e42661b9559d9814579a08f7a61b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "5f7ba42608a1aa3ba365af07dd4732b6d8e317be259e46915f790f1bca3b6838"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "7ae25e4bd73616a2e26f2b64076ac21f70f247d81f86ddf680cb99e00829b5ce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "e403901ebfa72ca8ca4630d58f72880e096dba80fcb0f33fd0680be27cf9b883"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "a9e6f3df1f60da87742d3c7a8e28ee269f222932e6f039b9c97fdd18d90da3aa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "0ed72ee5665c801c07fc4c670959053d3441657b4d83334bf86bbb7b2e7fd733"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5a8a7571c7c04d1c3873f8b5ee587bfd4a5f732493cb11d739691c3880d2fb69"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "4bedd28f6c22c627fd07384225906461f0cf7c2ab94743da271a040ceda886df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "179c496072c4b388cb6095ae0c2d5fec453067cba892912a2e186af2a1164eb6"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "be5bac52cc658a3375f516184f19fe3a2e98cb2a71641dc08bd68c5aa3f84f82",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "8038b580be0b90957066d240104b2b6b9e684108acf5a28b8e47a274db7587d8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "1b19c21b95f5925ba9207a5fd50e79ef03627c3322df76403062066e4ab642cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "478834c48ed92db6b1b68ef5256b686eb63bb1f5a21be323e806616f14cda6ea"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "0bab3e540d8d6d413df39c70ef6e9428ef35d2dd92f8981e536bda699fa38835"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "ea928cb6e0f7daa6019218107d8d984f005ea9d6a26e7aceaecac5d331e1bd55"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "e89ee7a61d31802fa65e8f8a3d32d4b2ecd141dd357789ae4bd7db247131c61a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "37e7a3fcf3b9d4d225e31c1e0a45a457161a6d406a0001dcfff004fd8d670f1a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "6b0241e0ca2965fa965855551332d23c57ad30d89c3e8c62b2705ba1d5aedc06"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "b9e5788236231faa76bd019fbb9d12a39d12b8fe404e47286fbcb598fdfea559"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "502a7400785b00f6ce4c98d733e3d6012e58e6c5936040d6351dcc6da0e087d3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "68884f5576f1982bff730e5010fb6936404d7f2f2d1255091c93661ca391507f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "12b4fb9a2da3a268015967a8ebee50c655ea56b2259d53daefb23549ad5a6d8a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "d6e1d6f6663946ef9055d4f679323eb4275b45aa4ecd551a650a3ce6936a00d7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "f9d55b6e7a4c37398aa4df49485984eb0934ac3f6d6ed89abc871314f4604550"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "dcacadab16a91c1904fca96c9a759b6cc76a7ff0fb0d774fac17528464adf4ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "b6d594e89dbf0b7b6086c9685c5821ab3d1e5ed6fdb92411c7a16214b76c1664"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "972faa1609774f5e100b46b1ea1617ad6335de07b8f0cd7f4fc42c159a45ac2e",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "f4309b0710678605195851312563b40c6b8b5b6f890cd24557fdb7deb886fec2"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "027cff22cbec944d0c76a14d2b20e3da88a763c5d984603603bc49c8f5fea69e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "0b79804194bcfc822cbe62a43e5cf22e9adde42e9be9c3d7599b5aeae5a91043"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "d4571749749e7237e01a6ef3b17e7a57bf2579e5e0c6e5b31f0f8a075f81c8ac"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "a6ab2ddd8458660013f81430f6d960c53f7abda003de194bc8e456f1435a2622"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "19beb53e7304115157c2866b9b661eccd98b92e255ebb38530ccfe95d00a191d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "cd4846b3c8343a749adb33031e900ffab70513fd02439910f94983b73db0ba10"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a7f5e7e70b7d471235fad4108d410ac223410ee89da4a890167054674e2a1bdb"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "b29fb5d7ebe7614170278b592446e0934950c9bea6162ad7024ca6c0cbd0b6a9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "ed564eee994349547da3e832424595f327661b9ca78119ca3b588205ae4904e0"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "973841660aebb81d0b9bb2e554bccb9c42abbc7c78bda6990c392d9a267b60b9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "fca64be024939db3a20d63f7c52937f93bf38e1eaaacd371835a12b85ba2f72e"
                    },
                    {
                      "is_deleted": true,
                      "review_id": "wave2_review_001",
                      "row_hash": "8f42ad9a706ce6d984d1e3438982f61b9621494cbb81e4dbed0f8059113e41d6"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "c1c55bb3d962743a33d334026befb3ecb366df75a20a0b0b34208f7b46b75e29",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "220e0362bb82421af7ff3d4b6c9082a61311aec5b72bc82b9469b541145062ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8767c0257f7efd653535e4c9db000f2fe5079f6b599ab1cc12820304ad684688"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "1cbc420947d42a7eaa25d219d149a424369b095bad7bc2aa9b197d33bca59e16"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "eec3f65bc2dba342ab0f59666133c01bf72b6b5523f0378693885a6a3ddea9df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "9fcae80247c433b267a4a70c65ddb3854cf95ac24a6d1ab7e0263d02e483c3c7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "97464f4d8cb4f96a6f89b53fc0803fd15371c2ea7750ccc9497daeb71515a120"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "4ecf6b3e8f6078e98afdbb3a7d5329ddcfd85f8e03d9c2eb1aeb71093119170e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "cc22a76d426d138662043e0fd0d16efdc091b67c2dd2aa9b6e1d1ab7bda700d9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "a3846bdec5173518c0bd8bb0194228b0dfee503252ba85320b62fb7a3d390948"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "f146faa74b32cd7911707875af68b95764794f0797f8e39512a83cdd48505b3c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "244e4cd989860f4569b6ee65f70015fd8485c274bc44d686f6b9c5f59a74977d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d4497c72599e234bfd23070bf0dc54e0d0fefd9d8ecf58e22b096f7916a52d59"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "f0fb55a395bccc0f01f7ea862c9744ac6f570f3941597337451aafe3f1f23eed"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "d3d962c346c72cb1250bdff82dbb71fb73c68d88c12365605d7bf793d4b6e874",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e221c22f277479a9f68ba82fb38565461388815f577bb51aafbe65c1da5a4417"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "a1d4f9a173d15c2cc89514a2cb060f73075d0bdce3ab76e6ed8e91090cfcdac6"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3a03c0be1cb357fc900a26a018ce2f8f6206e2583b09b7ffd0c923551add4c22"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "87661c86057e4c7a58a76e203b2fa56f1cdb3509c4b38bfd3491cebd82fc2c70"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "b21980549ab439249b5ae24c9788b071f51cbafaba31d6589557d0b29a58c789"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "cbbfdca967c26328c7e7acecd6380582e0e1b345c8790bdd2d9077a9f4ee7983",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "76b84167fae4ddce9de6d8ca02c58ed4721c7a642ac742111e904c792047c8de"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "f7e8852b715c28c023fbe375322474fa02bc65d81ef67579e4541e1920ac863e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "f04a19dc7a53c8d24693ece34ef606f74fed7ab8aa7618ab81f19702015e6abe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "63567922dbc71b63439b1e4a3c938f5eedcfdcee9d6fffde5a864f61f5333819"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "9ea4db91d3a779fa30cfdc8687eb9a2a3869d460dacb70c90777b95309675cb3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4b2d038c9381f4898016eb01a2c76913dcc6a4116f100dd9c8e89ac69ce9f593"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "aa89affbc52a6f241bf07e1be914fb2e842c90ca64aa327c642bb5406ff427fb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "de47d8963e98151f040068e0f034cc51f017ce59b3b90a47be3459618c74e664"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "c07cd48fbb30c66116beea16eef28ba18aee78e8649999c56c865985231d0752",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "33b64f9f4c0ec9b96e7d5a3f8f4b55f73490d61c7ede72c8881e43f38f8406b0",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c280dbc0a622377a6930afad3baedcf4832fda03d4adb50c0b71fbccbe5f0cd9",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "fc5bddb6e146d8a5ca8c213f4709f024c8c4e6394a24d6f33c9770b75304cd84",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "67e669b4b9d32278d7afbb7c518b84dbed53dbc2f84ea9fb5ac83e01cc8c1682",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "iceberg_visible": {
                "customers": {
                  "manifest_sha256": "c5e9bd8436395273a8e1cd5baee5332af3609387a180503a35ac3d2bb48af6d0",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "0d10cdd2fc05399400d89cdb24746b0b289d78f7a8a4b82598fe21d11ae9b731"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "a8de535a3a12f987810975cb44f3e288ff492e72024588920c5787e2820f2100"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "7e0b4d5d0f516dceaf87941bb8cf52b35111a338776f98346e056a4aa7a3ff5f"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "b7284338d73bb5bf5105d48f16264b2b1855559a24329933c9060f90c0d92bf5"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "7ab42f667edd04e117e4a876cfe7bb28173df733a0b90f16c04a1b7edb11042c"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "987297199383f6a17f975b3cd3d0956a7c161c2c46144f7e190c21db8d377124"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "851f578e9ebb923a9c733f988473dfd5d08a484d9abcccf9677aa79690dbb4b9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "7a28f748bef00843e2255aba1c1b4f7a3616b19f41f04358e706e3729780301a"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "bde17534e3035031a2b4cadf89808ad4be3870b8e431bcb48e1589f3f748f05c"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "fc42d0f5000a46610d7c036934fd58bf11c4b57508806f06e0bc27e268ab2527",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "ec1cc0c3f5db3d730e635fb58079f48ba19bdf7865ef3dfe1fd3981c6f7d723d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "54fa68b1ada8664ca1694f141440421865b55dbfc21e4f43ae9fe894dea3a04e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "3cda1da0d9d949e6d04bcb63c3e7ca7f300d005096eeefc67e7b779baa554a8e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "eca4244589d571813a4bc5bf33c2d024292696ab3fe8c8c83e2ecc673bc31df0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "072c36ff9acbdfe5cfc41bbecb57b119303c6ce70d57bee2a6ae6f3ad85bea99"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "761da00fd9c9353b76334fd593b54ee083ca92f8cf462f8c47ab167c5f4ffd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "a1337cdc1ab4edd0305a707a0d0f934d6b7326225224d530d25315f83584140d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "b023239a3fb52428341c2d0ac83548aa4c5b56d60f782de7af781665b6c70b71"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "78a8a0e8ffbe795b848306775981ea545d9d3a92fca7a0909194b278582c786d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "aa878cb2e01217ebd62810321dce08cdf989e42661b9559d9814579a08f7a61b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "5f7ba42608a1aa3ba365af07dd4732b6d8e317be259e46915f790f1bca3b6838"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "7ae25e4bd73616a2e26f2b64076ac21f70f247d81f86ddf680cb99e00829b5ce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "e403901ebfa72ca8ca4630d58f72880e096dba80fcb0f33fd0680be27cf9b883"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "a9e6f3df1f60da87742d3c7a8e28ee269f222932e6f039b9c97fdd18d90da3aa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "0ed72ee5665c801c07fc4c670959053d3441657b4d83334bf86bbb7b2e7fd733"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5a8a7571c7c04d1c3873f8b5ee587bfd4a5f732493cb11d739691c3880d2fb69"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "4bedd28f6c22c627fd07384225906461f0cf7c2ab94743da271a040ceda886df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "179c496072c4b388cb6095ae0c2d5fec453067cba892912a2e186af2a1164eb6"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "be5bac52cc658a3375f516184f19fe3a2e98cb2a71641dc08bd68c5aa3f84f82",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "8038b580be0b90957066d240104b2b6b9e684108acf5a28b8e47a274db7587d8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "1b19c21b95f5925ba9207a5fd50e79ef03627c3322df76403062066e4ab642cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "478834c48ed92db6b1b68ef5256b686eb63bb1f5a21be323e806616f14cda6ea"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "0bab3e540d8d6d413df39c70ef6e9428ef35d2dd92f8981e536bda699fa38835"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "ea928cb6e0f7daa6019218107d8d984f005ea9d6a26e7aceaecac5d331e1bd55"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "e89ee7a61d31802fa65e8f8a3d32d4b2ecd141dd357789ae4bd7db247131c61a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "37e7a3fcf3b9d4d225e31c1e0a45a457161a6d406a0001dcfff004fd8d670f1a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "6b0241e0ca2965fa965855551332d23c57ad30d89c3e8c62b2705ba1d5aedc06"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "b9e5788236231faa76bd019fbb9d12a39d12b8fe404e47286fbcb598fdfea559"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "502a7400785b00f6ce4c98d733e3d6012e58e6c5936040d6351dcc6da0e087d3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "68884f5576f1982bff730e5010fb6936404d7f2f2d1255091c93661ca391507f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "12b4fb9a2da3a268015967a8ebee50c655ea56b2259d53daefb23549ad5a6d8a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "d6e1d6f6663946ef9055d4f679323eb4275b45aa4ecd551a650a3ce6936a00d7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "f9d55b6e7a4c37398aa4df49485984eb0934ac3f6d6ed89abc871314f4604550"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "dcacadab16a91c1904fca96c9a759b6cc76a7ff0fb0d774fac17528464adf4ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "b6d594e89dbf0b7b6086c9685c5821ab3d1e5ed6fdb92411c7a16214b76c1664"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "02aac6079fb82f4227af84ae12f77b784b724cbaa56d901c20154fb9829bdd13",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "f4309b0710678605195851312563b40c6b8b5b6f890cd24557fdb7deb886fec2"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "027cff22cbec944d0c76a14d2b20e3da88a763c5d984603603bc49c8f5fea69e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "0b79804194bcfc822cbe62a43e5cf22e9adde42e9be9c3d7599b5aeae5a91043"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "d4571749749e7237e01a6ef3b17e7a57bf2579e5e0c6e5b31f0f8a075f81c8ac"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "a6ab2ddd8458660013f81430f6d960c53f7abda003de194bc8e456f1435a2622"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "19beb53e7304115157c2866b9b661eccd98b92e255ebb38530ccfe95d00a191d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "cd4846b3c8343a749adb33031e900ffab70513fd02439910f94983b73db0ba10"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a7f5e7e70b7d471235fad4108d410ac223410ee89da4a890167054674e2a1bdb"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "b29fb5d7ebe7614170278b592446e0934950c9bea6162ad7024ca6c0cbd0b6a9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "ed564eee994349547da3e832424595f327661b9ca78119ca3b588205ae4904e0"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "973841660aebb81d0b9bb2e554bccb9c42abbc7c78bda6990c392d9a267b60b9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "fca64be024939db3a20d63f7c52937f93bf38e1eaaacd371835a12b85ba2f72e"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "c1c55bb3d962743a33d334026befb3ecb366df75a20a0b0b34208f7b46b75e29",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "220e0362bb82421af7ff3d4b6c9082a61311aec5b72bc82b9469b541145062ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8767c0257f7efd653535e4c9db000f2fe5079f6b599ab1cc12820304ad684688"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "1cbc420947d42a7eaa25d219d149a424369b095bad7bc2aa9b197d33bca59e16"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "eec3f65bc2dba342ab0f59666133c01bf72b6b5523f0378693885a6a3ddea9df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "9fcae80247c433b267a4a70c65ddb3854cf95ac24a6d1ab7e0263d02e483c3c7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "97464f4d8cb4f96a6f89b53fc0803fd15371c2ea7750ccc9497daeb71515a120"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "4ecf6b3e8f6078e98afdbb3a7d5329ddcfd85f8e03d9c2eb1aeb71093119170e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "cc22a76d426d138662043e0fd0d16efdc091b67c2dd2aa9b6e1d1ab7bda700d9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "a3846bdec5173518c0bd8bb0194228b0dfee503252ba85320b62fb7a3d390948"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "f146faa74b32cd7911707875af68b95764794f0797f8e39512a83cdd48505b3c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "244e4cd989860f4569b6ee65f70015fd8485c274bc44d686f6b9c5f59a74977d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d4497c72599e234bfd23070bf0dc54e0d0fefd9d8ecf58e22b096f7916a52d59"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "f0fb55a395bccc0f01f7ea862c9744ac6f570f3941597337451aafe3f1f23eed"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "d3d962c346c72cb1250bdff82dbb71fb73c68d88c12365605d7bf793d4b6e874",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e221c22f277479a9f68ba82fb38565461388815f577bb51aafbe65c1da5a4417"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "a1d4f9a173d15c2cc89514a2cb060f73075d0bdce3ab76e6ed8e91090cfcdac6"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3a03c0be1cb357fc900a26a018ce2f8f6206e2583b09b7ffd0c923551add4c22"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "87661c86057e4c7a58a76e203b2fa56f1cdb3509c4b38bfd3491cebd82fc2c70"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "b21980549ab439249b5ae24c9788b071f51cbafaba31d6589557d0b29a58c789"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "cbbfdca967c26328c7e7acecd6380582e0e1b345c8790bdd2d9077a9f4ee7983",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "76b84167fae4ddce9de6d8ca02c58ed4721c7a642ac742111e904c792047c8de"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "f7e8852b715c28c023fbe375322474fa02bc65d81ef67579e4541e1920ac863e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "f04a19dc7a53c8d24693ece34ef606f74fed7ab8aa7618ab81f19702015e6abe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "63567922dbc71b63439b1e4a3c938f5eedcfdcee9d6fffde5a864f61f5333819"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "9ea4db91d3a779fa30cfdc8687eb9a2a3869d460dacb70c90777b95309675cb3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4b2d038c9381f4898016eb01a2c76913dcc6a4116f100dd9c8e89ac69ce9f593"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "aa89affbc52a6f241bf07e1be914fb2e842c90ca64aa327c642bb5406ff427fb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "de47d8963e98151f040068e0f034cc51f017ce59b3b90a47be3459618c74e664"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "c07cd48fbb30c66116beea16eef28ba18aee78e8649999c56c865985231d0752",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "33b64f9f4c0ec9b96e7d5a3f8f4b55f73490d61c7ede72c8881e43f38f8406b0",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c280dbc0a622377a6930afad3baedcf4832fda03d4adb50c0b71fbccbe5f0cd9",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "fc5bddb6e146d8a5ca8c213f4709f024c8c4e6394a24d6f33c9770b75304cd84",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "67e669b4b9d32278d7afbb7c518b84dbed53dbc2f84ea9fb5ac83e01cc8c1682",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "stable_visible": {
                "customers": {
                  "manifest_sha256": "c5e9bd8436395273a8e1cd5baee5332af3609387a180503a35ac3d2bb48af6d0",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "0d10cdd2fc05399400d89cdb24746b0b289d78f7a8a4b82598fe21d11ae9b731"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "a8de535a3a12f987810975cb44f3e288ff492e72024588920c5787e2820f2100"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "7e0b4d5d0f516dceaf87941bb8cf52b35111a338776f98346e056a4aa7a3ff5f"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "b7284338d73bb5bf5105d48f16264b2b1855559a24329933c9060f90c0d92bf5"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "7ab42f667edd04e117e4a876cfe7bb28173df733a0b90f16c04a1b7edb11042c"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "987297199383f6a17f975b3cd3d0956a7c161c2c46144f7e190c21db8d377124"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "851f578e9ebb923a9c733f988473dfd5d08a484d9abcccf9677aa79690dbb4b9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "7a28f748bef00843e2255aba1c1b4f7a3616b19f41f04358e706e3729780301a"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "bde17534e3035031a2b4cadf89808ad4be3870b8e431bcb48e1589f3f748f05c"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "fc42d0f5000a46610d7c036934fd58bf11c4b57508806f06e0bc27e268ab2527",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "ec1cc0c3f5db3d730e635fb58079f48ba19bdf7865ef3dfe1fd3981c6f7d723d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "54fa68b1ada8664ca1694f141440421865b55dbfc21e4f43ae9fe894dea3a04e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "3cda1da0d9d949e6d04bcb63c3e7ca7f300d005096eeefc67e7b779baa554a8e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "eca4244589d571813a4bc5bf33c2d024292696ab3fe8c8c83e2ecc673bc31df0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "072c36ff9acbdfe5cfc41bbecb57b119303c6ce70d57bee2a6ae6f3ad85bea99"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "761da00fd9c9353b76334fd593b54ee083ca92f8cf462f8c47ab167c5f4ffd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "a1337cdc1ab4edd0305a707a0d0f934d6b7326225224d530d25315f83584140d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "b023239a3fb52428341c2d0ac83548aa4c5b56d60f782de7af781665b6c70b71"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "78a8a0e8ffbe795b848306775981ea545d9d3a92fca7a0909194b278582c786d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "aa878cb2e01217ebd62810321dce08cdf989e42661b9559d9814579a08f7a61b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "5f7ba42608a1aa3ba365af07dd4732b6d8e317be259e46915f790f1bca3b6838"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "7ae25e4bd73616a2e26f2b64076ac21f70f247d81f86ddf680cb99e00829b5ce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "e403901ebfa72ca8ca4630d58f72880e096dba80fcb0f33fd0680be27cf9b883"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "a9e6f3df1f60da87742d3c7a8e28ee269f222932e6f039b9c97fdd18d90da3aa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "0ed72ee5665c801c07fc4c670959053d3441657b4d83334bf86bbb7b2e7fd733"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "5a8a7571c7c04d1c3873f8b5ee587bfd4a5f732493cb11d739691c3880d2fb69"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "4bedd28f6c22c627fd07384225906461f0cf7c2ab94743da271a040ceda886df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "179c496072c4b388cb6095ae0c2d5fec453067cba892912a2e186af2a1164eb6"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "be5bac52cc658a3375f516184f19fe3a2e98cb2a71641dc08bd68c5aa3f84f82",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "8038b580be0b90957066d240104b2b6b9e684108acf5a28b8e47a274db7587d8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "1b19c21b95f5925ba9207a5fd50e79ef03627c3322df76403062066e4ab642cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "478834c48ed92db6b1b68ef5256b686eb63bb1f5a21be323e806616f14cda6ea"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "0bab3e540d8d6d413df39c70ef6e9428ef35d2dd92f8981e536bda699fa38835"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "ea928cb6e0f7daa6019218107d8d984f005ea9d6a26e7aceaecac5d331e1bd55"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "e89ee7a61d31802fa65e8f8a3d32d4b2ecd141dd357789ae4bd7db247131c61a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "37e7a3fcf3b9d4d225e31c1e0a45a457161a6d406a0001dcfff004fd8d670f1a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "6b0241e0ca2965fa965855551332d23c57ad30d89c3e8c62b2705ba1d5aedc06"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "b9e5788236231faa76bd019fbb9d12a39d12b8fe404e47286fbcb598fdfea559"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "502a7400785b00f6ce4c98d733e3d6012e58e6c5936040d6351dcc6da0e087d3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "68884f5576f1982bff730e5010fb6936404d7f2f2d1255091c93661ca391507f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "12b4fb9a2da3a268015967a8ebee50c655ea56b2259d53daefb23549ad5a6d8a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "d6e1d6f6663946ef9055d4f679323eb4275b45aa4ecd551a650a3ce6936a00d7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "f9d55b6e7a4c37398aa4df49485984eb0934ac3f6d6ed89abc871314f4604550"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "dcacadab16a91c1904fca96c9a759b6cc76a7ff0fb0d774fac17528464adf4ab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "b6d594e89dbf0b7b6086c9685c5821ab3d1e5ed6fdb92411c7a16214b76c1664"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "02aac6079fb82f4227af84ae12f77b784b724cbaa56d901c20154fb9829bdd13",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "f4309b0710678605195851312563b40c6b8b5b6f890cd24557fdb7deb886fec2"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "027cff22cbec944d0c76a14d2b20e3da88a763c5d984603603bc49c8f5fea69e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "0b79804194bcfc822cbe62a43e5cf22e9adde42e9be9c3d7599b5aeae5a91043"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "d4571749749e7237e01a6ef3b17e7a57bf2579e5e0c6e5b31f0f8a075f81c8ac"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "a6ab2ddd8458660013f81430f6d960c53f7abda003de194bc8e456f1435a2622"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "19beb53e7304115157c2866b9b661eccd98b92e255ebb38530ccfe95d00a191d"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "cd4846b3c8343a749adb33031e900ffab70513fd02439910f94983b73db0ba10"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a7f5e7e70b7d471235fad4108d410ac223410ee89da4a890167054674e2a1bdb"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "b29fb5d7ebe7614170278b592446e0934950c9bea6162ad7024ca6c0cbd0b6a9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "ed564eee994349547da3e832424595f327661b9ca78119ca3b588205ae4904e0"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "973841660aebb81d0b9bb2e554bccb9c42abbc7c78bda6990c392d9a267b60b9"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "fca64be024939db3a20d63f7c52937f93bf38e1eaaacd371835a12b85ba2f72e"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "c1c55bb3d962743a33d334026befb3ecb366df75a20a0b0b34208f7b46b75e29",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "220e0362bb82421af7ff3d4b6c9082a61311aec5b72bc82b9469b541145062ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8767c0257f7efd653535e4c9db000f2fe5079f6b599ab1cc12820304ad684688"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "1cbc420947d42a7eaa25d219d149a424369b095bad7bc2aa9b197d33bca59e16"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "eec3f65bc2dba342ab0f59666133c01bf72b6b5523f0378693885a6a3ddea9df"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "9fcae80247c433b267a4a70c65ddb3854cf95ac24a6d1ab7e0263d02e483c3c7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "97464f4d8cb4f96a6f89b53fc0803fd15371c2ea7750ccc9497daeb71515a120"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "4ecf6b3e8f6078e98afdbb3a7d5329ddcfd85f8e03d9c2eb1aeb71093119170e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "cc22a76d426d138662043e0fd0d16efdc091b67c2dd2aa9b6e1d1ab7bda700d9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "a3846bdec5173518c0bd8bb0194228b0dfee503252ba85320b62fb7a3d390948"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "f146faa74b32cd7911707875af68b95764794f0797f8e39512a83cdd48505b3c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "244e4cd989860f4569b6ee65f70015fd8485c274bc44d686f6b9c5f59a74977d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d4497c72599e234bfd23070bf0dc54e0d0fefd9d8ecf58e22b096f7916a52d59"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "f0fb55a395bccc0f01f7ea862c9744ac6f570f3941597337451aafe3f1f23eed"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "d3d962c346c72cb1250bdff82dbb71fb73c68d88c12365605d7bf793d4b6e874",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "e221c22f277479a9f68ba82fb38565461388815f577bb51aafbe65c1da5a4417"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "a1d4f9a173d15c2cc89514a2cb060f73075d0bdce3ab76e6ed8e91090cfcdac6"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3a03c0be1cb357fc900a26a018ce2f8f6206e2583b09b7ffd0c923551add4c22"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "87661c86057e4c7a58a76e203b2fa56f1cdb3509c4b38bfd3491cebd82fc2c70"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "b21980549ab439249b5ae24c9788b071f51cbafaba31d6589557d0b29a58c789"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "cbbfdca967c26328c7e7acecd6380582e0e1b345c8790bdd2d9077a9f4ee7983",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "76b84167fae4ddce9de6d8ca02c58ed4721c7a642ac742111e904c792047c8de"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "f7e8852b715c28c023fbe375322474fa02bc65d81ef67579e4541e1920ac863e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "f04a19dc7a53c8d24693ece34ef606f74fed7ab8aa7618ab81f19702015e6abe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "63567922dbc71b63439b1e4a3c938f5eedcfdcee9d6fffde5a864f61f5333819"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "9ea4db91d3a779fa30cfdc8687eb9a2a3869d460dacb70c90777b95309675cb3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4b2d038c9381f4898016eb01a2c76913dcc6a4116f100dd9c8e89ac69ce9f593"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "aa89affbc52a6f241bf07e1be914fb2e842c90ca64aa327c642bb5406ff427fb"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "de47d8963e98151f040068e0f034cc51f017ce59b3b90a47be3459618c74e664"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "c07cd48fbb30c66116beea16eef28ba18aee78e8649999c56c865985231d0752",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "33b64f9f4c0ec9b96e7d5a3f8f4b55f73490d61c7ede72c8881e43f38f8406b0",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c280dbc0a622377a6930afad3baedcf4832fda03d4adb50c0b71fbccbe5f0cd9",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "fc5bddb6e146d8a5ca8c213f4709f024c8c4e6394a24d6f33c9770b75304cd84",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "67e669b4b9d32278d7afbb7c518b84dbed53dbc2f84ea9fb5ac83e01cc8c1682",
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
              "updated_at": "2026-08-03T18:04:27.860932802Z"
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
          "duration_seconds": 1.625,
          "exit_code": 0,
          "stderr": "",
          "stdout": "e1589f3f748f05c\"}]}, \"order_items\": {\"manifest_sha256\": \"fc42d0f5000a46610d7c036934fd58bf11c4b57508806f06e0bc27e268ab2527\", \"row_count\": 18, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"order_item_id\": 1, \"row_hash\": \"ec1cc0c3f5db3d730e635fb58079f48ba19bdf7865ef3dfe1fd3981c6f7d723d\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"order_item_id\": 1, \"row_hash\": \"54fa68b1ada8664ca1694f141440421865b55dbfc21e4f43ae9fe894dea3a04e\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"order_item_id\": 1, \"row_hash\": \"3cda1da0d9d949e6d04bcb63c3e7ca7f300d005096eeefc67e7b779baa554a8e\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"order_item_id\": 2, \"row_hash\": \"eca4244589d571813a4bc5bf33c2d024292696ab3fe8c8c83e2ecc673bc31df0\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"order_item_id\": 1, \"row_hash\": \"072c36ff9acbdfe5cfc41bbecb57b119303c6ce70d57bee2a6ae6f3ad85bea99\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"order_item_id\": 1, \"row_hash\": \"761da00fd9c9353b76334fd593b54ee083ca92f8cf462f8c47ab167c5f4ffd87\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"order_item_id\": 1, \"row_hash\": \"a1337cdc1ab4edd0305a707a0d0f934d6b7326225224d530d25315f83584140d\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"order_item_id\": 2, \"row_hash\": \"b023239a3fb52428341c2d0ac83548aa4c5b56d60f782de7af781665b6c70b71\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"order_item_id\": 1, \"row_hash\": \"78a8a0e8ffbe795b848306775981ea545d9d3a92fca7a0909194b278582c786d\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"order_item_id\": 1, \"row_hash\": \"aa878cb2e01217ebd62810321dce08cdf989e42661b9559d9814579a08f7a61b\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"order_item_id\": 1, \"row_hash\": \"5f7ba42608a1aa3ba365af07dd4732b6d8e317be259e46915f790f1bca3b6838\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"order_item_id\": 2, \"row_hash\": \"7ae25e4bd73616a2e26f2b64076ac21f70f247d81f86ddf680cb99e00829b5ce\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"order_item_id\": 1, \"row_hash\": \"e403901ebfa72ca8ca4630d58f72880e096dba80fcb0f33fd0680be27cf9b883\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"order_item_id\": 1, \"row_hash\": \"a9e6f3df1f60da87742d3c7a8e28ee269f222932e6f039b9c97fdd18d90da3aa\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"order_item_id\": 1, \"row_hash\": \"0ed72ee5665c801c07fc4c670959053d3441657b4d83334bf86bbb7b2e7fd733\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"order_item_id\": 2, \"row_hash\": \"5a8a7571c7c04d1c3873f8b5ee587bfd4a5f732493cb11d739691c3880d2fb69\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"order_item_id\": 1, \"row_hash\": \"4bedd28f6c22c627fd07384225906461f0cf7c2ab94743da271a040ceda886df\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"order_item_id\": 2, \"row_hash\": \"179c496072c4b388cb6095ae0c2d5fec453067cba892912a2e186af2a1164eb6\"}]}, \"order_payments\": {\"manifest_sha256\": \"be5bac52cc658a3375f516184f19fe3a2e98cb2a71641dc08bd68c5aa3f84f82\", \"row_count\": 16, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"payment_sequential\": 1, \"row_hash\": \"8038b580be0b90957066d240104b2b6b9e684108acf5a28b8e47a274db7587d8\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"payment_sequential\": 1, \"row_hash\": \"1b19c21b95f5925ba9207a5fd50e79ef03627c3322df76403062066e4ab642cb\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"payment_sequential\": 1, \"row_hash\": \"478834c48ed92db6b1b68ef5256b686eb63bb1f5a21be323e806616f14cda6ea\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"payment_sequential\": 1, \"row_hash\": \"0bab3e540d8d6d413df39c70ef6e9428ef35d2dd92f8981e536bda699fa38835\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"payment_sequential\": 2, \"row_hash\": \"ea928cb6e0f7daa6019218107d8d984f005ea9d6a26e7aceaecac5d331e1bd55\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"payment_sequential\": 1, \"row_hash\": \"e89ee7a61d31802fa65e8f8a3d32d4b2ecd141dd357789ae4bd7db247131c61a\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"payment_sequential\": 1, \"row_hash\": \"37e7a3fcf3b9d4d225e31c1e0a45a457161a6d406a0001dcfff004fd8d670f1a\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"payment_sequential\": 1, \"row_hash\": \"6b0241e0ca2965fa965855551332d23c57ad30d89c3e8c62b2705ba1d5aedc06\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"payment_sequential\": 1, \"row_hash\": \"b9e5788236231faa76bd019fbb9d12a39d12b8fe404e47286fbcb598fdfea559\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"payment_sequential\": 2, \"row_hash\": \"502a7400785b00f6ce4c98d733e3d6012e58e6c5936040d6351dcc6da0e087d3\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"payment_sequential\": 1, \"row_hash\": \"68884f5576f1982bff730e5010fb6936404d7f2f2d1255091c93661ca391507f\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"payment_sequential\": 1, \"row_hash\": \"12b4fb9a2da3a268015967a8ebee50c655ea56b2259d53daefb23549ad5a6d8a\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"payment_sequential\": 1, \"row_hash\": \"d6e1d6f6663946ef9055d4f679323eb4275b45aa4ecd551a650a3ce6936a00d7\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"payment_sequential\": 1, \"row_hash\": \"f9d55b6e7a4c37398aa4df49485984eb0934ac3f6d6ed89abc871314f4604550\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"payment_sequential\": 1, \"row_hash\": \"dcacadab16a91c1904fca96c9a759b6cc76a7ff0fb0d774fac17528464adf4ab\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"payment_sequential\": 2, \"row_hash\": \"b6d594e89dbf0b7b6086c9685c5821ab3d1e5ed6fdb92411c7a16214b76c1664\"}]}, \"order_reviews\": {\"manifest_sha256\": \"02aac6079fb82f4227af84ae12f77b784b724cbaa56d901c20154fb9829bdd13\", \"row_count\": 12, \"rows\": [{\"is_deleted\": false, \"review_id\": \"review_001\", \"row_hash\": \"f4309b0710678605195851312563b40c6b8b5b6f890cd24557fdb7deb886fec2\"}, {\"is_deleted\": false, \"review_id\": \"review_002\", \"row_hash\": \"027cff22cbec944d0c76a14d2b20e3da88a763c5d984603603bc49c8f5fea69e\"}, {\"is_deleted\": false, \"review_id\": \"review_003\", \"row_hash\": \"0b79804194bcfc822cbe62a43e5cf22e9adde42e9be9c3d7599b5aeae5a91043\"}, {\"is_deleted\": false, \"review_id\": \"review_004\", \"row_hash\": \"d4571749749e7237e01a6ef3b17e7a57bf2579e5e0c6e5b31f0f8a075f81c8ac\"}, {\"is_deleted\": false, \"review_id\": \"review_005\", \"row_hash\": \"a6ab2ddd8458660013f81430f6d960c53f7abda003de194bc8e456f1435a2622\"}, {\"is_deleted\": false, \"review_id\": \"review_006\", \"row_hash\": \"19beb53e7304115157c2866b9b661eccd98b92e255ebb38530ccfe95d00a191d\"}, {\"is_deleted\": false, \"review_id\": \"review_007\", \"row_hash\": \"cd4846b3c8343a749adb33031e900ffab70513fd02439910f94983b73db0ba10\"}, {\"is_deleted\": false, \"review_id\": \"review_008\", \"row_hash\": \"a7f5e7e70b7d471235fad4108d410ac223410ee89da4a890167054674e2a1bdb\"}, {\"is_deleted\": false, \"review_id\": \"review_009\", \"row_hash\": \"b29fb5d7ebe7614170278b592446e0934950c9bea6162ad7024ca6c0cbd0b6a9\"}, {\"is_deleted\": false, \"review_id\": \"review_010\", \"row_hash\": \"ed564eee994349547da3e832424595f327661b9ca78119ca3b588205ae4904e0\"}, {\"is_deleted\": false, \"review_id\": \"review_011\", \"row_hash\": \"973841660aebb81d0b9bb2e554bccb9c42abbc7c78bda6990c392d9a267b60b9\"}, {\"is_deleted\": false, \"review_id\": \"review_012\", \"row_hash\": \"fca64be024939db3a20d63f7c52937f93bf38e1eaaacd371835a12b85ba2f72e\"}]}, \"orders\": {\"manifest_sha256\": \"c1c55bb3d962743a33d334026befb3ecb366df75a20a0b0b34208f7b46b75e29\", \"row_count\": 13, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"row_hash\": \"220e0362bb82421af7ff3d4b6c9082a61311aec5b72bc82b9469b541145062ae\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"row_hash\": \"8767c0257f7efd653535e4c9db000f2fe5079f6b599ab1cc12820304ad684688\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"row_hash\": \"1cbc420947d42a7eaa25d219d149a424369b095bad7bc2aa9b197d33bca59e16\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"row_hash\": \"eec3f65bc2dba342ab0f59666133c01bf72b6b5523f0378693885a6a3ddea9df\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"row_hash\": \"9fcae80247c433b267a4a70c65ddb3854cf95ac24a6d1ab7e0263d02e483c3c7\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"row_hash\": \"97464f4d8cb4f96a6f89b53fc0803fd15371c2ea7750ccc9497daeb71515a120\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"row_hash\": \"4ecf6b3e8f6078e98afdbb3a7d5329ddcfd85f8e03d9c2eb1aeb71093119170e\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"row_hash\": \"cc22a76d426d138662043e0fd0d16efdc091b67c2dd2aa9b6e1d1ab7bda700d9\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"row_hash\": \"a3846bdec5173518c0bd8bb0194228b0dfee503252ba85320b62fb7a3d390948\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"row_hash\": \"f146faa74b32cd7911707875af68b95764794f0797f8e39512a83cdd48505b3c\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"row_hash\": \"244e4cd989860f4569b6ee65f70015fd8485c274bc44d686f6b9c5f59a74977d\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"row_hash\": \"d4497c72599e234bfd23070bf0dc54e0d0fefd9d8ecf58e22b096f7916a52d59\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"row_hash\": \"f0fb55a395bccc0f01f7ea862c9744ac6f570f3941597337451aafe3f1f23eed\"}]}, \"product_category_translation\": {\"manifest_sha256\": \"d3d962c346c72cb1250bdff82dbb71fb73c68d88c12365605d7bf793d4b6e874\", \"row_count\": 5, \"rows\": [{\"is_deleted\": false, \"product_category_name\": \"beleza_saude\", \"row_hash\": \"e221c22f277479a9f68ba82fb38565461388815f577bb51aafbe65c1da5a4417\"}, {\"is_deleted\": false, \"product_category_name\": \"informatica_acessorios\", \"row_hash\": \"a1d4f9a173d15c2cc89514a2cb060f73075d0bdce3ab76e6ed8e91090cfcdac6\"}, {\"is_deleted\": false, \"product_category_name\": \"moveis_decoracao\", \"row_hash\": \"3a03c0be1cb357fc900a26a018ce2f8f6206e2583b09b7ffd0c923551add4c22\"}, {\"is_deleted\": false, \"product_category_name\": \"telefonia\", \"row_hash\": \"87661c86057e4c7a58a76e203b2fa56f1cdb3509c4b38bfd3491cebd82fc2c70\"}, {\"is_deleted\": false, \"product_category_name\": \"utilidades_domesticas\", \"row_hash\": \"b21980549ab439249b5ae24c9788b071f51cbafaba31d6589557d0b29a58c789\"}]}, \"products\": {\"manifest_sha256\": \"cbbfdca967c26328c7e7acecd6380582e0e1b345c8790bdd2d9077a9f4ee7983\", \"row_count\": 8, \"rows\": [{\"is_deleted\": false, \"product_id\": \"product_001\", \"row_hash\": \"76b84167fae4ddce9de6d8ca02c58ed4721c7a642ac742111e904c792047c8de\"}, {\"is_deleted\": false, \"product_id\": \"product_002\", \"row_hash\": \"f7e8852b715c28c023fbe375322474fa02bc65d81ef67579e4541e1920ac863e\"}, {\"is_deleted\": false, \"product_id\": \"product_003\", \"row_hash\": \"f04a19dc7a53c8d24693ece34ef606f74fed7ab8aa7618ab81f19702015e6abe\"}, {\"is_deleted\": false, \"product_id\": \"product_004\", \"row_hash\": \"63567922dbc71b63439b1e4a3c938f5eedcfdcee9d6fffde5a864f61f5333819\"}, {\"is_deleted\": false, \"product_id\": \"product_005\", \"row_hash\": \"9ea4db91d3a779fa30cfdc8687eb9a2a3869d460dacb70c90777b95309675cb3\"}, {\"is_deleted\": false, \"product_id\": \"product_006\", \"row_hash\": \"4b2d038c9381f4898016eb01a2c76913dcc6a4116f100dd9c8e89ac69ce9f593\"}, {\"is_deleted\": false, \"product_id\": \"product_007\", \"row_hash\": \"aa89affbc52a6f241bf07e1be914fb2e842c90ca64aa327c642bb5406ff427fb\"}, {\"is_deleted\": false, \"product_id\": \"product_008\", \"row_hash\": \"de47d8963e98151f040068e0f034cc51f017ce59b3b90a47be3459618c74e664\"}]}, \"sellers\": {\"manifest_sha256\": \"c07cd48fbb30c66116beea16eef28ba18aee78e8649999c56c865985231d0752\", \"row_count\": 4, \"rows\": [{\"is_deleted\": false, \"row_hash\": \"33b64f9f4c0ec9b96e7d5a3f8f4b55f73490d61c7ede72c8881e43f38f8406b0\", \"seller_id\": \"seller_001\"}, {\"is_deleted\": false, \"row_hash\": \"c280dbc0a622377a6930afad3baedcf4832fda03d4adb50c0b71fbccbe5f0cd9\", \"seller_id\": \"seller_002\"}, {\"is_deleted\": false, \"row_hash\": \"fc5bddb6e146d8a5ca8c213f4709f024c8c4e6394a24d6f33c9770b75304cd84\", \"seller_id\": \"seller_003\"}, {\"is_deleted\": false, \"row_hash\": \"67e669b4b9d32278d7afbb7c518b84dbed53dbc2f84ea9fb5ac83e01cc8c1682\", \"seller_id\": \"seller_004\"}]}}}, \"runtime\": {\"last_published_sync_run_seq\": 4, \"lease_owner_id\": null, \"source_snapshot_completed\": true}, \"stable_current_counts\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"status\": \"ready\", \"sync_run_id\": \"sync-00000000000000000004\", \"sync_run_seq\": 4}\n",
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
          "duration_seconds": 1.109,
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
          "duration_seconds": 1.547,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"clickhouse\": 200, \"command\": \"status\", \"compose\": [{\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"airflow\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"airflow-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"apicurio-registry\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"clickhouse\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"clickhouse-init\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"clickhouse-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"iceberg-migration\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"kafka\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"kafka-connect\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"kafka-topics\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"minio\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"minio-init\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"mysql\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"platform-postgres\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"platform-postgres-bootstrap\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"polaris\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-admin\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-admin-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-bootstrap\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-credentials-prepare\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-server-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-bronze\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-geolocation\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"spark-master\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-ops\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-silver\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-worker\", \"state\": \"running\"}], \"connector\": {\"connector_state\": \"RUNNING\", \"registered\": true, \"task_0_state\": \"RUNNING\"}, \"iceberg\": {\"contract_version\": 2, \"queries_count\": 10, \"status\": \"READY\", \"updated_at\": \"2026-08-03T18:04:27.860932802Z\"}, \"mysql\": {\"customers\": 9, \"geolocation\": 6, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"polaris\": 200, \"project\": \"olist_stage_v\", \"registry\": {\"compatibility\": \"BACKWARD_TRANSITIVE\", \"status_code\": 200}, \"status\": \"ready\", \"writer_schema_capture\": \"captured\"}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 4.269,
      "gate": "10-final",
      "status": "PASS",
      "timestamp": "2026-08-03T18:04:54.410598+00:00"
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

Raw evidence persisted in `data/stage-v-evidence/stage_v_final_candidate_retry/`.
