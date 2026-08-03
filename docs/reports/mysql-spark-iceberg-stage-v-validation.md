# Stage V Candidate E2E Validation Report

- **Status**: `PASS`
- **Run ID**: `stage_v_clean_e113c55`
- **Compose Project**: `olist_stage_v`
- **Started At**: `2026-08-03T18:53:19.339586+00:00`
- **Finished At**: `2026-08-03T19:13:55.558745+00:00`

---

## 1. Final Verdict

Stage V validation completed with status `PASS`.

All mandatory gates passed in a single clean-domain run.

- **Stage L Authorization**: `AUTHORIZED` (allowed to proceed to Stage L)

---

## 2. Gate Execution Results (V0 - V10)

| Gate | Name | Status | Duration (s) |
| --- | --- | --- | ---: |
| `00-preflight` | 00-preflight | `PASS` | 49.317 |
| `01-harness-ready` | 01-harness-ready | `PASS` | 0.001 |
| `02-clean-bootstrap` | 02-clean-bootstrap | `PASS` | 417.204 |
| `03-initial-snapshot` | 03-initial-snapshot | `PASS` | 250.932 |
| `04-crud-and-restart` | 04-crud-and-restart | `PASS` | 149.569 |
| `05-caught-up` | 05-caught-up | `PASS` | 70.188 |
| `06-serving-sync` | 06-serving-sync | `PASS` | 174.72 |
| `07-dbt-and-stable-views` | 07-dbt-and-stable-views | `PASS` | 4.035 |
| `08-additive-schema` | 08-additive-schema | `PASS` | 60.298 |
| `09-rebuild` | 09-rebuild | `PASS` | 22.309 |
| `10-final` | 10-final | `PASS` | 4.251 |

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
            "changed_paths": [],
            "commands_ok": true,
            "diagnostics": "",
            "dirty": false,
            "head": "e113c552cca990636f426b827456a77ddc9d594b",
            "worktree_digest": "ff5693af49845798f303491d6f558ff9de396b15c733d4f0fd9be56af88a31d6"
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
          "duration_seconds": 22.515,
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
          "duration_seconds": 0.032,
          "exit_code": 0,
          "stderr": "",
          "stdout": "e113c552cca990636f426b827456a77ddc9d594b\n",
          "timed_out": false
        },
        {
          "args": [
            "git",
            "status",
            "--porcelain=v1",
            "--untracked-files=all"
          ],
          "duration_seconds": 0.062,
          "exit_code": 0,
          "stderr": "",
          "stdout": "",
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
          "duration_seconds": 0.047,
          "exit_code": 0,
          "stderr": "",
          "stdout": "",
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
          "duration_seconds": 0.062,
          "exit_code": 0,
          "stderr": "",
          "stdout": "",
          "timed_out": false
        },
        {
          "args": [
            "uv",
            "lock",
            "--check"
          ],
          "duration_seconds": 0.032,
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
          "duration_seconds": 19.25,
          "exit_code": 0,
          "stderr": "",
          "stdout": "============================= test session starts =============================\nplatform win32 -- Python 3.12.13, pytest-9.0.3, pluggy-1.6.0\nrootdir: C:\\Users\\fyujv\\source\\repos\\olist-mds\nconfigfile: pyproject.toml\nplugins: anyio-4.13.0\ncollected 188 items\n\ntests\\cdc_contracts\\test_avro_helpers.py ..........                      [  5%]\ntests\\cdc_contracts\\test_connector_bootstrap.py ................         [ 13%]\ntests\\cdc_contracts\\test_entity_contracts.py ..............              [ 21%]\ntests\\cdc_contracts\\test_topics.py .......                               [ 25%]\ntests\\cdc_contracts\\test_writer_schemas.py ....                          [ 27%]\ntests\\lakehouse_platform\\test_local_lab_live_readiness.py ...            [ 28%]\ntests\\lakehouse_platform\\test_local_lab_profile_boundaries.py .....      [ 31%]\ntests\\lakehouse_platform\\test_normalization_api.py ...                   [ 32%]\ntests\\lakehouse_platform\\test_polaris_admin_minio_contract.py ..         [ 34%]\ntests\\lakehouse_platform\\test_polaris_contract.py .......                [ 37%]\ntests\\lakehouse_platform\\test_polaris_credentials_projection.py ...      [ 39%]\ntests\\lakehouse_platform\\test_spark_config.py ....                       [ 41%]\ntests\\lakehouse_platform\\test_spark_image_contract.py .....              [ 44%]\ntests\\lakehouse_platform\\test_table_contracts.py .......                 [ 47%]\ntests\\mysql\\test_cli.py .......                                          [ 51%]\ntests\\mysql\\test_mysql_integration.py ss                                 [ 52%]\ntests\\mysql\\test_repository.py .................                         [ 61%]\ntests\\mysql\\test_seeding.py ......                                       [ 64%]\ntests\\mysql\\test_source_schema.py ............                           [ 71%]\ntests\\dbt_clickhouse\\test_dbt_parse.py .                                 [ 71%]\ntests\\dbt_clickhouse\\test_native_ddl_contract.py ........                [ 76%]\ntests\\dbt_clickhouse\\test_project_contract.py ......                     [ 79%]\ntests\\serving\\test_airflow_api.py .....                                  [ 81%]\ntests\\serving\\test_boundary.py .......                                   [ 85%]\ntests\\serving\\test_dbt_runner.py .                                       [ 86%]\ntests\\serving\\test_entities.py ...                                       [ 87%]\ntests\\stage_v\\test_stage_v_harness.py ...................                [ 97%]\ntests\\stage_v\\test_stage_v_oracles.py ....                               [100%]\n\n============================== warnings summary ===============================\n.venv\\Lib\\site-packages\\airflow\\__init__.py:47\n  C:\\Users\\fyujv\\source\\repos\\olist-mds\\.venv\\Lib\\site-packages\\airflow\\__init__.py:47: RuntimeWarning: Airflow currently can be run on POSIX-compliant Operating Systems. For development, it is regularly tested on fairly modern Linux Distros and recent versions of macOS. On Windows you can run it via WSL2 (Windows Subsystem for Linux 2) or via Linux Containers. The work to add Windows support is tracked via https://github.com/apache/airflow/issues/10388, but it is not a high priority.\n    warnings.warn(\n\n.venv\\Lib\\site-packages\\_pytest\\cacheprovider.py:475\n  C:\\Users\\fyujv\\source\\repos\\olist-mds\\.venv\\Lib\\site-packages\\_pytest\\cacheprovider.py:475: PytestCacheWarning: could not create cache path C:\\Users\\fyujv\\source\\repos\\olist-mds\\.pytest_cache\\v\\cache\\nodeids: [WinError 5] Access is denied: 'C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.pytest_cache\\\\v\\\\cache'\n    config.cache.set(\"cache/nodeids\", sorted(self.cached_nodeids))\n\n-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html\n================= 186 passed, 2 skipped, 2 warnings in 17.50s =================\n",
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
          "duration_seconds": 7.328,
          "exit_code": 0,
          "stderr": "#0 building with \"desktop-linux\" instance using docker driver\n\n#1 [internal] load build definition from Dockerfile\n#1 transferring dockerfile: 2.73kB 0.0s done\n#1 DONE 0.0s\n\n#2 resolve image config for docker-image://docker.io/docker/dockerfile:1.7\n#2 DONE 1.7s\n\n#3 docker-image://docker.io/docker/dockerfile:1.7@sha256:a57df69d0ea827fb7266491f2813635de6f17269be881f696fbfdf2d83dda33e\n#3 CACHED\n\n#4 [internal] load metadata for docker.io/apache/spark:4.1.3-scala2.13-java17-python3-ubuntu\n#4 DONE 0.0s\n\n#5 [internal] load metadata for docker.io/library/alpine:3.22.1\n#5 DONE 0.0s\n\n#6 [internal] load .dockerignore\n#6 transferring context: 1.65kB done\n#6 DONE 0.0s\n\n#7 [artifact-downloader 1/5] FROM docker.io/library/alpine:3.22.1\n#7 DONE 0.0s\n\n#8 [scala-builder 1/6] FROM docker.io/apache/spark:4.1.3-scala2.13-java17-python3-ubuntu\n#8 DONE 0.0s\n\n#9 [internal] load build context\n#9 transferring context: 3.59MB 0.6s done\n#9 DONE 0.6s\n\n#10 [scala-builder 4/6] COPY streaming /tmp/streaming\n#10 CACHED\n\n#11 [artifact-downloader 4/5] COPY docker/spark/download-jars.sh /usr/local/bin/download-jars\n#11 CACHED\n\n#12 [scala-builder 2/6] COPY --from=artifact-downloader /opt/olist/jars/ /opt/spark/jars/\n#12 CACHED\n\n#13 [sbt-downloader 3/5] COPY docker/spark/sbt-launch.sha256 /tmp/sbt-launch.sha256\n#13 CACHED\n\n#14 [sbt-downloader 4/5] COPY docker/spark/download-sbt-launch.sh /usr/local/bin/download-sbt-launch\n#14 CACHED\n\n#15 [sbt-downloader 5/5] RUN chmod 0555 /usr/local/bin/download-sbt-launch     && /usr/local/bin/download-sbt-launch /tmp/sbt-launch.sha256 /tmp/sbt-launcher\n#15 CACHED\n\n#16 [artifact-downloader 2/5] RUN apk add --no-cache ca-certificates wget\n#16 CACHED\n\n#17 [artifact-downloader 5/5] RUN chmod 0555 /usr/local/bin/download-jars     && /usr/local/bin/download-jars /tmp/jars.sha256 /opt/olist/jars\n#17 CACHED\n\n#18 [scala-builder 3/6] COPY --from=sbt-downloader /tmp/sbt-launcher/sbt-launch.jar /tmp/sbt-launch.jar\n#18 CACHED\n\n#19 [scala-builder 5/6] WORKDIR /tmp/streaming/spark/scala\n#19 CACHED\n\n#20 [artifact-downloader 3/5] COPY docker/spark/jars.sha256 /tmp/jars.sha256\n#20 CACHED\n\n#21 [scala-builder 6/6] RUN java -jar /tmp/sbt-launch.jar scalafmtCheckAll scalafmtSbtCheck Test/compile test package\n#21 CACHED\n\n#22 exporting to image\n#22 exporting layers\n#22 exporting layers 3.7s done\n#22 writing image sha256:5b8d63c788a4f751015d5e8c784a23bad469a584bd4e99f4bbebd6a18d70032d done\n#22 DONE 3.7s\n\nView build details: docker-desktop://dashboard/build/desktop-linux/desktop-linux/k1225ah8q0arj29568s39wcvn\n",
          "stdout": "",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 49.317,
      "gate": "00-preflight",
      "status": "PASS",
      "timestamp": "2026-08-03T18:54:08.658595+00:00"
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
      "timestamp": "2026-08-03T18:54:08.660761+00:00"
    },
    "02-clean-bootstrap": {
      "assertions": [
        {
          "detail": "{\"command\": \"reset\", \"scoped_to\": \"olist_stage_v\", \"status\": \"ready\"}",
          "name": "lab_reset",
          "status": "PASS"
        },
        {
          "detail": "{\"capture\": {\"capture_state\": \"captured\", \"contract_version\": 2}, \"command\": \"bootstrap\", \"readiness_level\": \"wave1_platform\", \"seed\": {\"archive\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\tests\\\\fixtures\\\\olist_small\\\\olist_small.zip\", \"exit_code\": 0, \"row_counts\": {\"customers\": 8, \"geolocation\": 6, \"order_items\": 16, \"order_payments\": 14, \"order_reviews\": 12, \"orders\": 12, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"run_id\": \"stage_v_clean_e113c55_seed_bbf07a25933a\"}, \"status\": \"ready\", \"validation\": {\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 216 packages in 2ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"warning: in the working copy of 'streaming/schemas/captured-writer-schemas/manifest.json', LF will be replaced by CRLF the next time Git touches it\", \"exit_code\": 0, \"status\": \"passed\"}], \"status\": \"ready\"}}",
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
          "stage_v_clean_e113c55_seed_bbf07a25933a",
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
          "duration_seconds": 1.953,
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
            "stage_v_clean_e113c55_seed_bbf07a25933a",
            "--random-seed",
            "20260801"
          ],
          "duration_seconds": 415.25,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"capture\": {\"capture_state\": \"captured\", \"contract_version\": 2}, \"command\": \"bootstrap\", \"readiness_level\": \"wave1_platform\", \"seed\": {\"archive\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\tests\\\\fixtures\\\\olist_small\\\\olist_small.zip\", \"exit_code\": 0, \"row_counts\": {\"customers\": 8, \"geolocation\": 6, \"order_items\": 16, \"order_payments\": 14, \"order_reviews\": 12, \"orders\": 12, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"run_id\": \"stage_v_clean_e113c55_seed_bbf07a25933a\"}, \"status\": \"ready\", \"validation\": {\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 216 packages in 2ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"warning: in the working copy of 'streaming/schemas/captured-writer-schemas/manifest.json', LF will be replaced by CRLF the next time Git touches it\", \"exit_code\": 0, \"status\": \"passed\"}], \"status\": \"ready\"}}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 417.204,
      "gate": "02-clean-bootstrap",
      "status": "PASS",
      "timestamp": "2026-08-03T19:01:05.868727+00:00"
    },
    "03-initial-snapshot": {
      "assertions": [
        {
          "detail": "{\"command\": \"start-streaming\", \"freshness_basis\": \"initial_start\", \"freshness_verified\": false, \"new_query_ids\": {\"bronze\": \"4afca84a-83a5-4400-80f1-8677043e381b\", \"silver\": \"10b1128d-e2d3-4781-b645-f2b55cf63641,34eff0db-758c-4107-94d2-57df5542734c,3ae53c9d-c964-44df-ac5f-757320003cc6,41451eb2-5702-42d4-b0fa-127c0feeb8f4,487b64cf-9b2d-485e-9815-8d3756631f25,5a249b28-62e3-42c5-af6d-d91e8c31f7cb,6bcf2cd2-957b-4d17-b8ef-86ebae101aa7,897ddcf7-c6a2-418a-a0a5-c5a4e16f7df1,8cc276ee-5333-4a57-882c-d128c5d9b8fd,b268c285-c294-439d-869f-2bd001357a64\"}, \"old_query_ids\": {}, \"restart_barrier_at_utc\": null, \"status\": \"ready\", \"status_files\": {\"bronze\": {\"query_count\": 1, \"updated_at_utc\": \"2026-08-03T19:02:58.390003362Z\"}, \"silver\": {\"query_count\": 10, \"updated_at_utc\": \"2026-08-03T19:03:08.364634388Z\"}}}",
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
                  "changes_snapshot_id": 4327187749456063570,
                  "entity": "customers",
                  "last_kafka_offset": 7,
                  "status": "COMMITTED"
                },
                "order_items": {
                  "changes_snapshot_id": 7722738888475921000,
                  "entity": "order_items",
                  "last_kafka_offset": 3,
                  "status": "COMMITTED"
                },
                "order_payments": {
                  "changes_snapshot_id": 2291984525540829799,
                  "entity": "order_payments",
                  "last_kafka_offset": 4,
                  "status": "COMMITTED"
                },
                "order_reviews": {
                  "changes_snapshot_id": 7232028679231485715,
                  "entity": "order_reviews",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "orders": {
                  "changes_snapshot_id": 8830695266972307893,
                  "entity": "orders",
                  "last_kafka_offset": 1,
                  "status": "COMMITTED"
                },
                "product_category_translation": {
                  "changes_snapshot_id": 8401292361000666733,
                  "entity": "product_category_translation",
                  "last_kafka_offset": 4,
                  "status": "COMMITTED"
                },
                "products": {
                  "changes_snapshot_id": 6511797434303314151,
                  "entity": "products",
                  "last_kafka_offset": 7,
                  "status": "COMMITTED"
                },
                "sellers": {
                  "changes_snapshot_id": 3940700634153017490,
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
          "duration_seconds": 126.594,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"start-streaming\", \"freshness_basis\": \"initial_start\", \"freshness_verified\": false, \"new_query_ids\": {\"bronze\": \"4afca84a-83a5-4400-80f1-8677043e381b\", \"silver\": \"10b1128d-e2d3-4781-b645-f2b55cf63641,34eff0db-758c-4107-94d2-57df5542734c,3ae53c9d-c964-44df-ac5f-757320003cc6,41451eb2-5702-42d4-b0fa-127c0feeb8f4,487b64cf-9b2d-485e-9815-8d3756631f25,5a249b28-62e3-42c5-af6d-d91e8c31f7cb,6bcf2cd2-957b-4d17-b8ef-86ebae101aa7,897ddcf7-c6a2-418a-a0a5-c5a4e16f7df1,8cc276ee-5333-4a57-882c-d128c5d9b8fd,b268c285-c294-439d-869f-2bd001357a64\"}, \"old_query_ids\": {}, \"restart_barrier_at_utc\": null, \"status\": \"ready\", \"status_files\": {\"bronze\": {\"query_count\": 1, \"updated_at_utc\": \"2026-08-03T19:02:58.390003362Z\"}, \"silver\": {\"query_count\": 10, \"updated_at_utc\": \"2026-08-03T19:03:08.364634388Z\"}}}\n",
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
          "duration_seconds": 93.422,
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
          "duration_seconds": 26.906,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"wait-caught-up\", \"status\": \"ready\"}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 250.932,
      "gate": "03-initial-snapshot",
      "status": "PASS",
      "timestamp": "2026-08-03T19:05:16.801950+00:00"
    },
    "04-crud-and-restart": {
      "assertions": [
        {
          "detail": "{\"command\": \"stop-streaming\", \"old_query_ids\": {\"bronze\": \"4afca84a-83a5-4400-80f1-8677043e381b\", \"silver\": \"10b1128d-e2d3-4781-b645-f2b55cf63641,34eff0db-758c-4107-94d2-57df5542734c,3ae53c9d-c964-44df-ac5f-757320003cc6,41451eb2-5702-42d4-b0fa-127c0feeb8f4,487b64cf-9b2d-485e-9815-8d3756631f25,5a249b28-62e3-42c5-af6d-d91e8c31f7cb,6bcf2cd2-957b-4d17-b8ef-86ebae101aa7,897ddcf7-c6a2-418a-a0a5-c5a4e16f7df1,8cc276ee-5333-4a57-882c-d128c5d9b8fd,b268c285-c294-439d-869f-2bd001357a64\"}, \"status\": \"ready\", \"status_files_removed\": true}",
          "name": "stop_spark_streaming",
          "status": "PASS"
        },
        {
          "detail": "Executed insert (8 statements), update (5 statements), delete (4 statements)",
          "name": "execute_crud_fixtures",
          "status": "PASS"
        },
        {
          "detail": "{\"command\": \"start-streaming\", \"freshness_basis\": \"status_updated_at_after_restart_barrier\", \"freshness_verified\": true, \"new_query_ids\": {\"bronze\": \"4afca84a-83a5-4400-80f1-8677043e381b\", \"silver\": \"10b1128d-e2d3-4781-b645-f2b55cf63641,34eff0db-758c-4107-94d2-57df5542734c,3ae53c9d-c964-44df-ac5f-757320003cc6,41451eb2-5702-42d4-b0fa-127c0feeb8f4,487b64cf-9b2d-485e-9815-8d3756631f25,5a249b28-62e3-42c5-af6d-d91e8c31f7cb,6bcf2cd2-957b-4d17-b8ef-86ebae101aa7,897ddcf7-c6a2-418a-a0a5-c5a4e16f7df1,8cc276ee-5333-4a57-882c-d128c5d9b8fd,b268c285-c294-439d-869f-2bd001357a64\"}, \"old_query_ids\": {\"bronze\": \"4afca84a-83a5-4400-80f1-8677043e381b\", \"silver\": \"10b1128d-e2d3-4781-b645-f2b55cf63641,34eff0db-758c-4107-94d2-57df5542734c,3ae53c9d-c964-44df-ac5f-757320003cc6,41451eb2-5702-42d4-b0fa-127c0feeb8f4,487b64cf-9b2d-485e-9815-8d3756631f25,5a249b28-62e3-42c5-af6d-d91e8c31f7cb,6bcf2cd2-957b-4d17-b8ef-86ebae101aa7,897ddcf7-c6a2-418a-a0a5-c5a4e16f7df1,8cc276ee-5333-4a57-882c-d128c5d9b8fd,b268c285-c294-439d-869f-2bd001357a64\"}, \"restart_barrier_at_utc\": \"2026-08-03T19:05:28.108815+00:00\", \"status\": \"ready\", \"status_files\": {\"bronze\": {\"query_count\": 1, \"updated_at_utc\": \"2026-08-03T19:07:31.317676598Z\"}, \"silver\": {\"query_count\": 10, \"updated_at_utc\": \"2026-08-03T19:07:39.802545111Z\"}}}",
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
          "duration_seconds": 11.329,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"stop-streaming\", \"old_query_ids\": {\"bronze\": \"4afca84a-83a5-4400-80f1-8677043e381b\", \"silver\": \"10b1128d-e2d3-4781-b645-f2b55cf63641,34eff0db-758c-4107-94d2-57df5542734c,3ae53c9d-c964-44df-ac5f-757320003cc6,41451eb2-5702-42d4-b0fa-127c0feeb8f4,487b64cf-9b2d-485e-9815-8d3756631f25,5a249b28-62e3-42c5-af6d-d91e8c31f7cb,6bcf2cd2-957b-4d17-b8ef-86ebae101aa7,897ddcf7-c6a2-418a-a0a5-c5a4e16f7df1,8cc276ee-5333-4a57-882c-d128c5d9b8fd,b268c285-c294-439d-869f-2bd001357a64\"}, \"status\": \"ready\", \"status_files_removed\": true}\n",
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
          "duration_seconds": 137.906,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"start-streaming\", \"freshness_basis\": \"status_updated_at_after_restart_barrier\", \"freshness_verified\": true, \"new_query_ids\": {\"bronze\": \"4afca84a-83a5-4400-80f1-8677043e381b\", \"silver\": \"10b1128d-e2d3-4781-b645-f2b55cf63641,34eff0db-758c-4107-94d2-57df5542734c,3ae53c9d-c964-44df-ac5f-757320003cc6,41451eb2-5702-42d4-b0fa-127c0feeb8f4,487b64cf-9b2d-485e-9815-8d3756631f25,5a249b28-62e3-42c5-af6d-d91e8c31f7cb,6bcf2cd2-957b-4d17-b8ef-86ebae101aa7,897ddcf7-c6a2-418a-a0a5-c5a4e16f7df1,8cc276ee-5333-4a57-882c-d128c5d9b8fd,b268c285-c294-439d-869f-2bd001357a64\"}, \"old_query_ids\": {\"bronze\": \"4afca84a-83a5-4400-80f1-8677043e381b\", \"silver\": \"10b1128d-e2d3-4781-b645-f2b55cf63641,34eff0db-758c-4107-94d2-57df5542734c,3ae53c9d-c964-44df-ac5f-757320003cc6,41451eb2-5702-42d4-b0fa-127c0feeb8f4,487b64cf-9b2d-485e-9815-8d3756631f25,5a249b28-62e3-42c5-af6d-d91e8c31f7cb,6bcf2cd2-957b-4d17-b8ef-86ebae101aa7,897ddcf7-c6a2-418a-a0a5-c5a4e16f7df1,8cc276ee-5333-4a57-882c-d128c5d9b8fd,b268c285-c294-439d-869f-2bd001357a64\"}, \"restart_barrier_at_utc\": \"2026-08-03T19:05:28.108815+00:00\", \"status\": \"ready\", \"status_files\": {\"bronze\": {\"query_count\": 1, \"updated_at_utc\": \"2026-08-03T19:07:31.317676598Z\"}, \"silver\": {\"query_count\": 10, \"updated_at_utc\": \"2026-08-03T19:07:39.802545111Z\"}}}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 149.569,
      "gate": "04-crud-and-restart",
      "status": "PASS",
      "timestamp": "2026-08-03T19:07:46.374319+00:00"
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
                  "changes_snapshot_id": 5869387453591450525,
                  "entity": "customers",
                  "last_kafka_offset": 8,
                  "status": "COMMITTED"
                },
                "order_items": {
                  "changes_snapshot_id": 5948428514509384907,
                  "entity": "order_items",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "order_payments": {
                  "changes_snapshot_id": 3389689790513587639,
                  "entity": "order_payments",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "order_reviews": {
                  "changes_snapshot_id": 2583938958004099503,
                  "entity": "order_reviews",
                  "last_kafka_offset": 2,
                  "status": "COMMITTED"
                },
                "orders": {
                  "changes_snapshot_id": 8111531154139198555,
                  "entity": "orders",
                  "last_kafka_offset": 3,
                  "status": "COMMITTED"
                },
                "product_category_translation": {
                  "changes_snapshot_id": 8401292361000666733,
                  "entity": "product_category_translation",
                  "last_kafka_offset": 4,
                  "status": "COMMITTED"
                },
                "products": {
                  "changes_snapshot_id": 6511797434303314151,
                  "entity": "products",
                  "last_kafka_offset": 7,
                  "status": "COMMITTED"
                },
                "sellers": {
                  "changes_snapshot_id": 3940700634153017490,
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
              "bronze": "4afca84a-83a5-4400-80f1-8677043e381b",
              "silver": "10b1128d-e2d3-4781-b645-f2b55cf63641,34eff0db-758c-4107-94d2-57df5542734c,3ae53c9d-c964-44df-ac5f-757320003cc6,41451eb2-5702-42d4-b0fa-127c0feeb8f4,487b64cf-9b2d-485e-9815-8d3756631f25,5a249b28-62e3-42c5-af6d-d91e8c31f7cb,6bcf2cd2-957b-4d17-b8ef-86ebae101aa7,897ddcf7-c6a2-418a-a0a5-c5a4e16f7df1,8cc276ee-5333-4a57-882c-d128c5d9b8fd,b268c285-c294-439d-869f-2bd001357a64"
            },
            "old_query_ids": {
              "bronze": "4afca84a-83a5-4400-80f1-8677043e381b",
              "silver": "10b1128d-e2d3-4781-b645-f2b55cf63641,34eff0db-758c-4107-94d2-57df5542734c,3ae53c9d-c964-44df-ac5f-757320003cc6,41451eb2-5702-42d4-b0fa-127c0feeb8f4,487b64cf-9b2d-485e-9815-8d3756631f25,5a249b28-62e3-42c5-af6d-d91e8c31f7cb,6bcf2cd2-957b-4d17-b8ef-86ebae101aa7,897ddcf7-c6a2-418a-a0a5-c5a4e16f7df1,8cc276ee-5333-4a57-882c-d128c5d9b8fd,b268c285-c294-439d-869f-2bd001357a64"
            },
            "restart_barrier_at_utc": "2026-08-03T19:05:28.108815+00:00",
            "status": "ready",
            "status_files": {
              "bronze": {
                "query_count": 1,
                "updated_at_utc": "2026-08-03T19:07:31.317676598Z"
              },
              "silver": {
                "query_count": 10,
                "updated_at_utc": "2026-08-03T19:07:39.802545111Z"
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
          "duration_seconds": 68.015,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"wait-caught-up\", \"status\": \"ready\"}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 70.188,
      "gate": "05-caught-up",
      "status": "PASS",
      "timestamp": "2026-08-03T19:08:56.564218+00:00"
    },
    "06-serving-sync": {
      "assertions": [
        {
          "detail": "{\"command\": \"start-serving\", \"profiles\": [\"platform\", \"serving\"], \"required_services\": [\"clickhouse\", \"airflow\"], \"status\": \"ready\"}",
          "name": "start_serving",
          "status": "PASS"
        },
        {
          "detail": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_v_clean_e113c55_crud_publish_bbf07a25933a\", \"dbt_result\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 1, \\\"sync_run_id\\\": \\\"sync-00000000000000000001\\\"}\"], \"exception\": null, \"results\": [{\"execution_time\": 0.08674764633178711, \"node\": \"stg_customers_current\", \"status\": \"success\"}, {\"execution_time\": 0.035370826721191406, \"node\": \"stg_customers_events\", \"status\": \"success\"}, {\"execution_time\": 0.035785675048828125, \"node\": \"stg_order_items_current\", \"status\": \"success\"}, {\"execution_time\": 0.039778709411621094, \"node\": \"stg_order_payments_current\", \"status\": \"success\"}, {\"execution_time\": 0.04660320281982422, \"node\": \"stg_orders_current\", \"status\": \"success\"}, {\"execution_time\": 0.04019045829772949, \"node\": \"stg_product_category_translation_events\", \"status\": \"success\"}, {\"execution_time\": 0.05130791664123535, \"node\": \"stg_products_events\", \"status\": \"success\"}, {\"execution_time\": 0.06457257270812988, \"node\": \"stg_sellers_current\", \"status\": \"success\"}, {\"execution_time\": 0.3661458492279053, \"node\": \"customer_scd2_collapses_identical_update_and_closes_on_delete\", \"status\": \"pass\"}, {\"execution_time\": 0.1745615005493164, \"node\": \"dim_customer_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.15787291526794434, \"node\": \"payment_allocation_is_proportional_at_item_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.20959019660949707, \"node\": \"zero_gross_order_has_null_payment_allocation\", \"status\": \"pass\"}, {\"execution_time\": 0.11711978912353516, \"node\": \"dim_date\", \"status\": \"success\"}, {\"execution_time\": 0.07377028465270996, \"node\": \"dim_order_status\", \"status\": \"success\"}, {\"execution_time\": 0.3469853401184082, \"node\": \"product_translation_does_not_resurrect_an_old_category\", \"status\": \"pass\"}, {\"execution_time\": 0.1569368839263916, \"node\": \"dim_product_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.08724045753479004, \"node\": \"dim_seller\", \"status\": \"success\"}, {\"execution_time\": 0.06554341316223145, \"node\": \"assert_customer_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.03660941123962402, \"node\": \"candidate_not_null_dim_customer_scd2_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03559422492980957, \"node\": \"candidate_not_null_dim_customer_scd2_customer_unique_id\", \"status\": \"pass\"}, {\"execution_time\": 0.03554081916809082, \"node\": \"candidate_not_null_dim_customer_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.043413639068603516, \"node\": \"unique_combination_of_columns_dim_customer_scd2_sync_run_seq__customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.06219649314880371, \"node\": \"assert_payment_allocations_balance\", \"status\": \"pass\"}, {\"execution_time\": 0.03378176689147949, \"node\": \"candidate_not_null_dim_date_date_day\", \"status\": \"pass\"}, {\"execution_time\": 0.03389883041381836, \"node\": \"candidate_not_null_dim_date_date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03381824493408203, \"node\": \"candidate_not_null_dim_date_sync_run_seq\", \"status\": \"pass\"}, {\"execution_time\": 0.03730630874633789, \"node\": \"unique_combination_of_columns_dim_date_sync_run_seq__date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03297877311706543, \"node\": \"candidate_not_null_dim_order_status_order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.04607748985290527, \"node\": \"candidate_not_null_dim_order_status_order_status_key\", \"status\": \"pass\"}, {\"execution_time\": 0.0472872257232666, \"node\": \"unique_combination_of_columns_dim_order_status_sync_run_seq__order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.039618730545043945, \"node\": \"assert_product_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.039426565170288086, \"node\": \"candidate_not_null_dim_product_scd2_product_id\", \"status\": \"pass\"}, {\"execution_time\": 0.03596663475036621, \"node\": \"candidate_not_null_dim_product_scd2_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03792619705200195, \"node\": \"candidate_not_null_dim_product_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.03751850128173828, \"node\": \"unique_combination_of_columns_dim_product_scd2_sync_run_seq__product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03453683853149414, \"node\": \"candidate_not_null_dim_seller_seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.03740096092224121, \"node\": \"candidate_not_null_dim_seller_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.035036563873291016, \"node\": \"unique_combination_of_columns_dim_seller_sync_run_seq__seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.39510130882263184, \"node\": \"fact_order_items\", \"status\": \"success\"}, {\"execution_time\": 0.046743154525756836, \"node\": \"assert_fact_order_items_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.04925537109375, \"node\": \"candidate_not_null_fact_order_items_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.044309377670288086, \"node\": \"candidate_not_null_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.04565238952636719, \"node\": \"candidate_not_null_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.05279040336608887, \"node\": \"candidate_not_null_fact_order_items_order_item_key\", \"status\": \"pass\"}, {\"execution_time\": 0.1944580078125, \"node\": \"candidate_not_null_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.04627060890197754, \"node\": \"candidate_not_null_fact_order_items_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.043517351150512695, \"node\": \"candidate_not_null_fact_order_items_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04907965660095215, \"node\": \"candidate_relationships_fact_order_items_customer_key__customer_key__ref_dim_customer_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.04830479621887207, \"node\": \"candidate_relationships_fact_order_items_product_key__product_key__ref_dim_product_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.041723012924194336, \"node\": \"candidate_relationships_fact_order_items_seller_key__seller_key__ref_dim_seller_\", \"status\": \"pass\"}, {\"execution_time\": 0.04195213317871094, \"node\": \"non_negative_fact_order_items_allocated_payment_value\", \"status\": \"pass\"}, {\"execution_time\": 0.03923916816711426, \"node\": \"non_negative_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.03493785858154297, \"node\": \"non_negative_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.037851572036743164, \"node\": \"non_negative_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.03514719009399414, \"node\": \"unique_combination_of_columns_fact_order_items_sync_run_seq__order_id__order_item_id\", \"status\": \"pass\"}, {\"execution_time\": 0.09172391891479492, \"node\": \"mart_daily_revenue\", \"status\": \"success\"}, {\"execution_time\": 0.08764791488647461, \"node\": \"mart_monthly_arpu\", \"status\": \"success\"}, {\"execution_time\": 0.047689199447631836, \"node\": \"assert_daily_revenue_components\", \"status\": \"pass\"}, {\"execution_time\": 0.04887676239013672, \"node\": \"candidate_not_null_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.03859972953796387, \"node\": \"candidate_not_null_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04001116752624512, \"node\": \"candidate_not_null_mart_daily_revenue_order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.042054176330566406, \"node\": \"candidate_not_null_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.03744339942932129, \"node\": \"non_negative_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.03914666175842285, \"node\": \"non_negative_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.03798055648803711, \"node\": \"non_negative_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.038424015045166016, \"node\": \"unique_combination_of_columns_mart_daily_revenue_sync_run_seq__order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.03922867774963379, \"node\": \"assert_monthly_arpu_formulas\", \"status\": \"pass\"}, {\"execution_time\": 0.037647247314453125, \"node\": \"candidate_not_null_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.03580641746520996, \"node\": \"candidate_not_null_mart_monthly_arpu_order_month\", \"status\": \"pass\"}, {\"execution_time\": 0.03899812698364258, \"node\": \"candidate_not_null_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.03975725173950195, \"node\": \"candidate_not_null_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04474234580993652, \"node\": \"non_negative_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.039789676666259766, \"node\": \"non_negative_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.04421210289001465, \"node\": \"non_negative_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.0444333553314209, \"node\": \"unique_combination_of_columns_mart_monthly_arpu_sync_run_seq__order_month\", \"status\": \"pass\"}], \"selector\": \"serving_candidate\", \"status_counts\": {\"pass\": 59, \"success\": 16}, \"success\": true, \"vars\": {\"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1}}, \"expected_entity_counts\": {\"customers\": 9, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 89, \"iceberg_snapshot_ids\": {\"customers\": 5869387453591450525, \"order_items\": 5948428514509384907, \"order_payments\": 3389689790513587639, \"order_reviews\": 2583938958004099503, \"orders\": 8111531154139198555, \"product_category_translation\": 8401292361000666733, \"products\": 6511797434303314151, \"sellers\": 3940700634153017490}, \"is_noop\": false, \"materialized_entity_counts\": {\"customers\": 9, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"materialized_event_count\": 89, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1, \"sync_run_status\": \"SUCCEEDED\", \"target_offsets\": {\"olist_cdc.olist_oltp.customers:0\": 8, \"olist_cdc.olist_oltp.order_items:0\": 5, \"olist_cdc.olist_oltp.order_items:1\": 5, \"olist_cdc.olist_oltp.order_items:2\": 6, \"olist_cdc.olist_oltp.order_payments:0\": 5, \"olist_cdc.olist_oltp.order_payments:1\": 4, \"olist_cdc.olist_oltp.order_payments:2\": 4, \"olist_cdc.olist_oltp.order_reviews:0\": 5, \"olist_cdc.olist_oltp.order_reviews:1\": 4, \"olist_cdc.olist_oltp.order_reviews:2\": 2, \"olist_cdc.olist_oltp.orders:0\": 3, \"olist_cdc.olist_oltp.orders:1\": 4, \"olist_cdc.olist_oltp.orders:2\": 4, \"olist_cdc.olist_oltp.product_category_translation:0\": 4, \"olist_cdc.olist_oltp.products:0\": 7, \"olist_cdc.olist_oltp.sellers:0\": 3}, \"target_transaction_id\": \"file=binlog.000002,pos=18315\"}",
          "name": "sync_serving_crud",
          "status": "PASS"
        },
        {
          "detail": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_v_clean_e113c55_crud_repeat_bbf07a25933a\", \"dbt_result\": null, \"expected_entity_counts\": {\"customers\": 0, \"order_items\": 0, \"order_payments\": 0, \"order_reviews\": 0, \"orders\": 0, \"product_category_translation\": 0, \"products\": 0, \"sellers\": 0}, \"expected_event_count\": 0, \"iceberg_snapshot_ids\": {\"customers\": 5869387453591450525, \"order_items\": 5948428514509384907, \"order_payments\": 3389689790513587639, \"order_reviews\": 2583938958004099503, \"orders\": 8111531154139198555, \"product_category_translation\": 8401292361000666733, \"products\": 6511797434303314151, \"sellers\": 3940700634153017490}, \"is_noop\": true, \"materialized_entity_counts\": {\"customers\": 0, \"order_items\": 0, \"order_payments\": 0, \"order_reviews\": 0, \"orders\": 0, \"product_category_translation\": 0, \"products\": 0, \"sellers\": 0}, \"materialized_event_count\": 0, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000002\", \"sync_run_seq\": 2, \"sync_run_status\": \"NOOP\", \"target_offsets\": {}, \"target_transaction_id\": \"file=binlog.000002,pos=18315\"}",
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
          "stage_v_clean_e113c55_crud_publish_bbf07a25933a",
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
          "stage_v_clean_e113c55_crud_repeat_bbf07a25933a",
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
          "duration_seconds": 143.047,
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
            "stage_v_clean_e113c55_crud_publish_bbf07a25933a",
            "--timeout",
            "1800"
          ],
          "duration_seconds": 25.937,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_v_clean_e113c55_crud_publish_bbf07a25933a\", \"dbt_result\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 1, \\\"sync_run_id\\\": \\\"sync-00000000000000000001\\\"}\"], \"exception\": null, \"results\": [{\"execution_time\": 0.08674764633178711, \"node\": \"stg_customers_current\", \"status\": \"success\"}, {\"execution_time\": 0.035370826721191406, \"node\": \"stg_customers_events\", \"status\": \"success\"}, {\"execution_time\": 0.035785675048828125, \"node\": \"stg_order_items_current\", \"status\": \"success\"}, {\"execution_time\": 0.039778709411621094, \"node\": \"stg_order_payments_current\", \"status\": \"success\"}, {\"execution_time\": 0.04660320281982422, \"node\": \"stg_orders_current\", \"status\": \"success\"}, {\"execution_time\": 0.04019045829772949, \"node\": \"stg_product_category_translation_events\", \"status\": \"success\"}, {\"execution_time\": 0.05130791664123535, \"node\": \"stg_products_events\", \"status\": \"success\"}, {\"execution_time\": 0.06457257270812988, \"node\": \"stg_sellers_current\", \"status\": \"success\"}, {\"execution_time\": 0.3661458492279053, \"node\": \"customer_scd2_collapses_identical_update_and_closes_on_delete\", \"status\": \"pass\"}, {\"execution_time\": 0.1745615005493164, \"node\": \"dim_customer_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.15787291526794434, \"node\": \"payment_allocation_is_proportional_at_item_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.20959019660949707, \"node\": \"zero_gross_order_has_null_payment_allocation\", \"status\": \"pass\"}, {\"execution_time\": 0.11711978912353516, \"node\": \"dim_date\", \"status\": \"success\"}, {\"execution_time\": 0.07377028465270996, \"node\": \"dim_order_status\", \"status\": \"success\"}, {\"execution_time\": 0.3469853401184082, \"node\": \"product_translation_does_not_resurrect_an_old_category\", \"status\": \"pass\"}, {\"execution_time\": 0.1569368839263916, \"node\": \"dim_product_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.08724045753479004, \"node\": \"dim_seller\", \"status\": \"success\"}, {\"execution_time\": 0.06554341316223145, \"node\": \"assert_customer_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.03660941123962402, \"node\": \"candidate_not_null_dim_customer_scd2_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03559422492980957, \"node\": \"candidate_not_null_dim_customer_scd2_customer_unique_id\", \"status\": \"pass\"}, {\"execution_time\": 0.03554081916809082, \"node\": \"candidate_not_null_dim_customer_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.043413639068603516, \"node\": \"unique_combination_of_columns_dim_customer_scd2_sync_run_seq__customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.06219649314880371, \"node\": \"assert_payment_allocations_balance\", \"status\": \"pass\"}, {\"execution_time\": 0.03378176689147949, \"node\": \"candidate_not_null_dim_date_date_day\", \"status\": \"pass\"}, {\"execution_time\": 0.03389883041381836, \"node\": \"candidate_not_null_dim_date_date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03381824493408203, \"node\": \"candidate_not_null_dim_date_sync_run_seq\", \"status\": \"pass\"}, {\"execution_time\": 0.03730630874633789, \"node\": \"unique_combination_of_columns_dim_date_sync_run_seq__date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03297877311706543, \"node\": \"candidate_not_null_dim_order_status_order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.04607748985290527, \"node\": \"candidate_not_null_dim_order_status_order_status_key\", \"status\": \"pass\"}, {\"execution_time\": 0.0472872257232666, \"node\": \"unique_combination_of_columns_dim_order_status_sync_run_seq__order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.039618730545043945, \"node\": \"assert_product_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.039426565170288086, \"node\": \"candidate_not_null_dim_product_scd2_product_id\", \"status\": \"pass\"}, {\"execution_time\": 0.03596663475036621, \"node\": \"candidate_not_null_dim_product_scd2_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03792619705200195, \"node\": \"candidate_not_null_dim_product_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.03751850128173828, \"node\": \"unique_combination_of_columns_dim_product_scd2_sync_run_seq__product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03453683853149414, \"node\": \"candidate_not_null_dim_seller_seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.03740096092224121, \"node\": \"candidate_not_null_dim_seller_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.035036563873291016, \"node\": \"unique_combination_of_columns_dim_seller_sync_run_seq__seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.39510130882263184, \"node\": \"fact_order_items\", \"status\": \"success\"}, {\"execution_time\": 0.046743154525756836, \"node\": \"assert_fact_order_items_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.04925537109375, \"node\": \"candidate_not_null_fact_order_items_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.044309377670288086, \"node\": \"candidate_not_null_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.04565238952636719, \"node\": \"candidate_not_null_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.05279040336608887, \"node\": \"candidate_not_null_fact_order_items_order_item_key\", \"status\": \"pass\"}, {\"execution_time\": 0.1944580078125, \"node\": \"candidate_not_null_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.04627060890197754, \"node\": \"candidate_not_null_fact_order_items_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.043517351150512695, \"node\": \"candidate_not_null_fact_order_items_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04907965660095215, \"node\": \"candidate_relationships_fact_order_items_customer_key__customer_key__ref_dim_customer_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.04830479621887207, \"node\": \"candidate_relationships_fact_order_items_product_key__product_key__ref_dim_product_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.041723012924194336, \"node\": \"candidate_relationships_fact_order_items_seller_key__seller_key__ref_dim_seller_\", \"status\": \"pass\"}, {\"execution_time\": 0.04195213317871094, \"node\": \"non_negative_fact_order_items_allocated_payment_value\", \"status\": \"pass\"}, {\"execution_time\": 0.03923916816711426, \"node\": \"non_negative_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.03493785858154297, \"node\": \"non_negative_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.037851572036743164, \"node\": \"non_negative_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.03514719009399414, \"node\": \"unique_combination_of_columns_fact_order_items_sync_run_seq__order_id__order_item_id\", \"status\": \"pass\"}, {\"execution_time\": 0.09172391891479492, \"node\": \"mart_daily_revenue\", \"status\": \"success\"}, {\"execution_time\": 0.08764791488647461, \"node\": \"mart_monthly_arpu\", \"status\": \"success\"}, {\"execution_time\": 0.047689199447631836, \"node\": \"assert_daily_revenue_components\", \"status\": \"pass\"}, {\"execution_time\": 0.04887676239013672, \"node\": \"candidate_not_null_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.03859972953796387, \"node\": \"candidate_not_null_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04001116752624512, \"node\": \"candidate_not_null_mart_daily_revenue_order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.042054176330566406, \"node\": \"candidate_not_null_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.03744339942932129, \"node\": \"non_negative_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.03914666175842285, \"node\": \"non_negative_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.03798055648803711, \"node\": \"non_negative_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.038424015045166016, \"node\": \"unique_combination_of_columns_mart_daily_revenue_sync_run_seq__order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.03922867774963379, \"node\": \"assert_monthly_arpu_formulas\", \"status\": \"pass\"}, {\"execution_time\": 0.037647247314453125, \"node\": \"candidate_not_null_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.03580641746520996, \"node\": \"candidate_not_null_mart_monthly_arpu_order_month\", \"status\": \"pass\"}, {\"execution_time\": 0.03899812698364258, \"node\": \"candidate_not_null_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.03975725173950195, \"node\": \"candidate_not_null_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04474234580993652, \"node\": \"non_negative_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.039789676666259766, \"node\": \"non_negative_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.04421210289001465, \"node\": \"non_negative_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.0444333553314209, \"node\": \"unique_combination_of_columns_mart_monthly_arpu_sync_run_seq__order_month\", \"status\": \"pass\"}], \"selector\": \"serving_candidate\", \"status_counts\": {\"pass\": 59, \"success\": 16}, \"success\": true, \"vars\": {\"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1}}, \"expected_entity_counts\": {\"customers\": 9, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 89, \"iceberg_snapshot_ids\": {\"customers\": 5869387453591450525, \"order_items\": 5948428514509384907, \"order_payments\": 3389689790513587639, \"order_reviews\": 2583938958004099503, \"orders\": 8111531154139198555, \"product_category_translation\": 8401292361000666733, \"products\": 6511797434303314151, \"sellers\": 3940700634153017490}, \"is_noop\": false, \"materialized_entity_counts\": {\"customers\": 9, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"materialized_event_count\": 89, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1, \"sync_run_status\": \"SUCCEEDED\", \"target_offsets\": {\"olist_cdc.olist_oltp.customers:0\": 8, \"olist_cdc.olist_oltp.order_items:0\": 5, \"olist_cdc.olist_oltp.order_items:1\": 5, \"olist_cdc.olist_oltp.order_items:2\": 6, \"olist_cdc.olist_oltp.order_payments:0\": 5, \"olist_cdc.olist_oltp.order_payments:1\": 4, \"olist_cdc.olist_oltp.order_payments:2\": 4, \"olist_cdc.olist_oltp.order_reviews:0\": 5, \"olist_cdc.olist_oltp.order_reviews:1\": 4, \"olist_cdc.olist_oltp.order_reviews:2\": 2, \"olist_cdc.olist_oltp.orders:0\": 3, \"olist_cdc.olist_oltp.orders:1\": 4, \"olist_cdc.olist_oltp.orders:2\": 4, \"olist_cdc.olist_oltp.product_category_translation:0\": 4, \"olist_cdc.olist_oltp.products:0\": 7, \"olist_cdc.olist_oltp.sellers:0\": 3}, \"target_transaction_id\": \"file=binlog.000002,pos=18315\"}\n",
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
            "stage_v_clean_e113c55_crud_repeat_bbf07a25933a",
            "--timeout",
            "1800"
          ],
          "duration_seconds": 5.719,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_v_clean_e113c55_crud_repeat_bbf07a25933a\", \"dbt_result\": null, \"expected_entity_counts\": {\"customers\": 0, \"order_items\": 0, \"order_payments\": 0, \"order_reviews\": 0, \"orders\": 0, \"product_category_translation\": 0, \"products\": 0, \"sellers\": 0}, \"expected_event_count\": 0, \"iceberg_snapshot_ids\": {\"customers\": 5869387453591450525, \"order_items\": 5948428514509384907, \"order_payments\": 3389689790513587639, \"order_reviews\": 2583938958004099503, \"orders\": 8111531154139198555, \"product_category_translation\": 8401292361000666733, \"products\": 6511797434303314151, \"sellers\": 3940700634153017490}, \"is_noop\": true, \"materialized_entity_counts\": {\"customers\": 0, \"order_items\": 0, \"order_payments\": 0, \"order_reviews\": 0, \"orders\": 0, \"product_category_translation\": 0, \"products\": 0, \"sellers\": 0}, \"materialized_event_count\": 0, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000002\", \"sync_run_seq\": 2, \"sync_run_status\": \"NOOP\", \"target_offsets\": {}, \"target_transaction_id\": \"file=binlog.000002,pos=18315\"}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 174.72,
      "gate": "06-serving-sync",
      "status": "PASS",
      "timestamp": "2026-08-03T19:11:51.284879+00:00"
    },
    "07-dbt-and-stable-views": {
      "assertions": [
        {
          "detail": "{\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 216 packages in 1ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"warning: in the working copy of 'streaming/schemas/captured-writer-schemas/manifest.json', LF will be replaced by CRLF the next time Git touches it\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"All checks passed!\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"91 files already formatted\", \"exit_code\": 0, \"status\": \"passed\"}], \"command\": \"validate\", \"status\": \"ready\"}",
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
                  "diagnostic": "warning: in the working copy of 'streaming/schemas/captured-writer-schemas/manifest.json', LF will be replaced by CRLF the next time Git touches it",
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
          "duration_seconds": 1.531,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 216 packages in 1ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"warning: in the working copy of 'streaming/schemas/captured-writer-schemas/manifest.json', LF will be replaced by CRLF the next time Git touches it\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"All checks passed!\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"91 files already formatted\", \"exit_code\": 0, \"status\": \"passed\"}], \"command\": \"validate\", \"status\": \"ready\"}\n",
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
          "duration_seconds": 2.5,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"validate-serving\", \"current_views\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"dbt\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 1, \\\"sync_run_id\\\": \\\"sync-00000000000000000001\\\"}\"], \"result_count\": 75, \"status_counts\": {\"pass\": 59, \"success\": 16}}, \"gold_views\": {\"dim_customer_scd2\": {\"candidate\": 7, \"stable\": 7}, \"dim_date\": {\"candidate\": 46, \"stable\": 46}, \"dim_order_status\": {\"candidate\": 2, \"stable\": 2}, \"dim_product_scd2\": {\"candidate\": 8, \"stable\": 8}, \"dim_seller\": {\"candidate\": 4, \"stable\": 4}, \"fact_order_items\": {\"candidate\": 18, \"stable\": 18}, \"mart_daily_revenue\": {\"candidate\": 13, \"stable\": 13}, \"mart_monthly_arpu\": {\"candidate\": 7, \"stable\": 7}}, \"static_validation\": {\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 216 packages in 1ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"warning: in the working copy of 'streaming/schemas/captured-writer-schemas/manifest.json', LF will be replaced by CRLF the next time Git touches it\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"All checks passed!\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"91 files already formatted\", \"exit_code\": 0, \"status\": \"passed\"}], \"status\": \"ready\"}, \"status\": \"ready\", \"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 4.035,
      "gate": "07-dbt-and-stable-views",
      "status": "PASS",
      "timestamp": "2026-08-03T19:11:55.325633+00:00"
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
          "detail": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_v_clean_e113c55_schema_publish_bbf07a25933a\", \"dbt_result\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 3, \\\"sync_run_id\\\": \\\"sync-00000000000000000003\\\"}\"], \"exception\": null, \"results\": [{\"execution_time\": 0.10910725593566895, \"node\": \"stg_customers_current\", \"status\": \"success\"}, {\"execution_time\": 0.0437471866607666, \"node\": \"stg_customers_events\", \"status\": \"success\"}, {\"execution_time\": 0.04930877685546875, \"node\": \"stg_order_items_current\", \"status\": \"success\"}, {\"execution_time\": 0.05227947235107422, \"node\": \"stg_order_payments_current\", \"status\": \"success\"}, {\"execution_time\": 0.046048641204833984, \"node\": \"stg_orders_current\", \"status\": \"success\"}, {\"execution_time\": 0.0433497428894043, \"node\": \"stg_product_category_translation_events\", \"status\": \"success\"}, {\"execution_time\": 0.043076515197753906, \"node\": \"stg_products_events\", \"status\": \"success\"}, {\"execution_time\": 0.04483532905578613, \"node\": \"stg_sellers_current\", \"status\": \"success\"}, {\"execution_time\": 0.4458656311035156, \"node\": \"customer_scd2_collapses_identical_update_and_closes_on_delete\", \"status\": \"pass\"}, {\"execution_time\": 0.2964026927947998, \"node\": \"dim_customer_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.19407296180725098, \"node\": \"payment_allocation_is_proportional_at_item_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.18792223930358887, \"node\": \"zero_gross_order_has_null_payment_allocation\", \"status\": \"pass\"}, {\"execution_time\": 0.14940953254699707, \"node\": \"dim_date\", \"status\": \"success\"}, {\"execution_time\": 0.11028242111206055, \"node\": \"dim_order_status\", \"status\": \"success\"}, {\"execution_time\": 0.33182334899902344, \"node\": \"product_translation_does_not_resurrect_an_old_category\", \"status\": \"pass\"}, {\"execution_time\": 0.21037650108337402, \"node\": \"dim_product_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.11596202850341797, \"node\": \"dim_seller\", \"status\": \"success\"}, {\"execution_time\": 0.06764483451843262, \"node\": \"assert_customer_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.04871177673339844, \"node\": \"candidate_not_null_dim_customer_scd2_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03938603401184082, \"node\": \"candidate_not_null_dim_customer_scd2_customer_unique_id\", \"status\": \"pass\"}, {\"execution_time\": 0.03508114814758301, \"node\": \"candidate_not_null_dim_customer_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.03595232963562012, \"node\": \"unique_combination_of_columns_dim_customer_scd2_sync_run_seq__customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.06631660461425781, \"node\": \"assert_payment_allocations_balance\", \"status\": \"pass\"}, {\"execution_time\": 0.03881573677062988, \"node\": \"candidate_not_null_dim_date_date_day\", \"status\": \"pass\"}, {\"execution_time\": 0.04301261901855469, \"node\": \"candidate_not_null_dim_date_date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03258991241455078, \"node\": \"candidate_not_null_dim_date_sync_run_seq\", \"status\": \"pass\"}, {\"execution_time\": 0.03568768501281738, \"node\": \"unique_combination_of_columns_dim_date_sync_run_seq__date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03516101837158203, \"node\": \"candidate_not_null_dim_order_status_order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.036608219146728516, \"node\": \"candidate_not_null_dim_order_status_order_status_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03608584403991699, \"node\": \"unique_combination_of_columns_dim_order_status_sync_run_seq__order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.03546762466430664, \"node\": \"assert_product_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.032393455505371094, \"node\": \"candidate_not_null_dim_product_scd2_product_id\", \"status\": \"pass\"}, {\"execution_time\": 0.03371906280517578, \"node\": \"candidate_not_null_dim_product_scd2_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04016709327697754, \"node\": \"candidate_not_null_dim_product_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.10913205146789551, \"node\": \"unique_combination_of_columns_dim_product_scd2_sync_run_seq__product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.033445119857788086, \"node\": \"candidate_not_null_dim_seller_seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.0547487735748291, \"node\": \"candidate_not_null_dim_seller_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.06275749206542969, \"node\": \"unique_combination_of_columns_dim_seller_sync_run_seq__seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.7015261650085449, \"node\": \"fact_order_items\", \"status\": \"success\"}, {\"execution_time\": 0.05932188034057617, \"node\": \"assert_fact_order_items_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.05270195007324219, \"node\": \"candidate_not_null_fact_order_items_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04614877700805664, \"node\": \"candidate_not_null_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.042337894439697266, \"node\": \"candidate_not_null_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.04498124122619629, \"node\": \"candidate_not_null_fact_order_items_order_item_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04719042778015137, \"node\": \"candidate_not_null_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.04277658462524414, \"node\": \"candidate_not_null_fact_order_items_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.0422670841217041, \"node\": \"candidate_not_null_fact_order_items_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.044832468032836914, \"node\": \"candidate_relationships_fact_order_items_customer_key__customer_key__ref_dim_customer_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.053900718688964844, \"node\": \"candidate_relationships_fact_order_items_product_key__product_key__ref_dim_product_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.0505220890045166, \"node\": \"candidate_relationships_fact_order_items_seller_key__seller_key__ref_dim_seller_\", \"status\": \"pass\"}, {\"execution_time\": 0.04542040824890137, \"node\": \"non_negative_fact_order_items_allocated_payment_value\", \"status\": \"pass\"}, {\"execution_time\": 0.0441129207611084, \"node\": \"non_negative_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.046563148498535156, \"node\": \"non_negative_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.043653249740600586, \"node\": \"non_negative_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.04676365852355957, \"node\": \"unique_combination_of_columns_fact_order_items_sync_run_seq__order_id__order_item_id\", \"status\": \"pass\"}, {\"execution_time\": 0.16716909408569336, \"node\": \"mart_daily_revenue\", \"status\": \"success\"}, {\"execution_time\": 0.15833473205566406, \"node\": \"mart_monthly_arpu\", \"status\": \"success\"}, {\"execution_time\": 0.06080317497253418, \"node\": \"assert_daily_revenue_components\", \"status\": \"pass\"}, {\"execution_time\": 0.06313300132751465, \"node\": \"candidate_not_null_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.06130862236022949, \"node\": \"candidate_not_null_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.05366706848144531, \"node\": \"candidate_not_null_mart_daily_revenue_order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.05156826972961426, \"node\": \"candidate_not_null_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.0486445426940918, \"node\": \"non_negative_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.05683469772338867, \"node\": \"non_negative_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.0474851131439209, \"node\": \"non_negative_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.04796314239501953, \"node\": \"unique_combination_of_columns_mart_daily_revenue_sync_run_seq__order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.043645381927490234, \"node\": \"assert_monthly_arpu_formulas\", \"status\": \"pass\"}, {\"execution_time\": 0.03497743606567383, \"node\": \"candidate_not_null_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.034363508224487305, \"node\": \"candidate_not_null_mart_monthly_arpu_order_month\", \"status\": \"pass\"}, {\"execution_time\": 0.03560638427734375, \"node\": \"candidate_not_null_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.03290700912475586, \"node\": \"candidate_not_null_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.03879904747009277, \"node\": \"non_negative_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.03554534912109375, \"node\": \"non_negative_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.034639596939086914, \"node\": \"non_negative_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.03925514221191406, \"node\": \"unique_combination_of_columns_mart_monthly_arpu_sync_run_seq__order_month\", \"status\": \"pass\"}], \"selector\": \"serving_candidate\", \"status_counts\": {\"pass\": 59, \"success\": 16}, \"success\": true, \"vars\": {\"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3}}, \"expected_entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 90, \"iceberg_snapshot_ids\": {\"customers\": 2110013481413148761, \"order_items\": 5948428514509384907, \"order_payments\": 3389689790513587639, \"order_reviews\": 2583938958004099503, \"orders\": 8111531154139198555, \"product_category_translation\": 8401292361000666733, \"products\": 6511797434303314151, \"sellers\": 3940700634153017490}, \"is_noop\": false, \"materialized_entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"materialized_event_count\": 90, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3, \"sync_run_status\": \"SUCCEEDED\", \"target_offsets\": {\"olist_cdc.olist_oltp.customers:0\": 9, \"olist_cdc.olist_oltp.order_items:0\": 5, \"olist_cdc.olist_oltp.order_items:1\": 5, \"olist_cdc.olist_oltp.order_items:2\": 6, \"olist_cdc.olist_oltp.order_payments:0\": 5, \"olist_cdc.olist_oltp.order_payments:1\": 4, \"olist_cdc.olist_oltp.order_payments:2\": 4, \"olist_cdc.olist_oltp.order_reviews:0\": 5, \"olist_cdc.olist_oltp.order_reviews:1\": 4, \"olist_cdc.olist_oltp.order_reviews:2\": 2, \"olist_cdc.olist_oltp.orders:0\": 3, \"olist_cdc.olist_oltp.orders:1\": 4, \"olist_cdc.olist_oltp.orders:2\": 4, \"olist_cdc.olist_oltp.product_category_translation:0\": 4, \"olist_cdc.olist_oltp.products:0\": 7, \"olist_cdc.olist_oltp.sellers:0\": 3}, \"target_transaction_id\": \"file=binlog.000002,pos=21633\"}",
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
              "transaction_id": "file=binlog.000002,pos=21633",
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
                  "changes_snapshot_id": 2110013481413148761,
                  "entity": "customers",
                  "last_kafka_offset": 9,
                  "status": "COMMITTED"
                },
                "order_items": {
                  "changes_snapshot_id": 5948428514509384907,
                  "entity": "order_items",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "order_payments": {
                  "changes_snapshot_id": 3389689790513587639,
                  "entity": "order_payments",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "order_reviews": {
                  "changes_snapshot_id": 2583938958004099503,
                  "entity": "order_reviews",
                  "last_kafka_offset": 2,
                  "status": "COMMITTED"
                },
                "orders": {
                  "changes_snapshot_id": 8111531154139198555,
                  "entity": "orders",
                  "last_kafka_offset": 3,
                  "status": "COMMITTED"
                },
                "product_category_translation": {
                  "changes_snapshot_id": 8401292361000666733,
                  "entity": "product_category_translation",
                  "last_kafka_offset": 4,
                  "status": "COMMITTED"
                },
                "products": {
                  "changes_snapshot_id": 6511797434303314151,
                  "entity": "products",
                  "last_kafka_offset": 7,
                  "status": "COMMITTED"
                },
                "sellers": {
                  "changes_snapshot_id": 3940700634153017490,
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
                  "diagnostic": "warning: in the working copy of 'streaming/schemas/captured-writer-schemas/manifest.json', LF will be replaced by CRLF the next time Git touches it",
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
          "stage_v_clean_e113c55_schema_publish_bbf07a25933a",
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
          "duration_seconds": 34.015,
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
            "stage_v_clean_e113c55_schema_publish_bbf07a25933a",
            "--timeout",
            "1800"
          ],
          "duration_seconds": 20.797,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_v_clean_e113c55_schema_publish_bbf07a25933a\", \"dbt_result\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 3, \\\"sync_run_id\\\": \\\"sync-00000000000000000003\\\"}\"], \"exception\": null, \"results\": [{\"execution_time\": 0.10910725593566895, \"node\": \"stg_customers_current\", \"status\": \"success\"}, {\"execution_time\": 0.0437471866607666, \"node\": \"stg_customers_events\", \"status\": \"success\"}, {\"execution_time\": 0.04930877685546875, \"node\": \"stg_order_items_current\", \"status\": \"success\"}, {\"execution_time\": 0.05227947235107422, \"node\": \"stg_order_payments_current\", \"status\": \"success\"}, {\"execution_time\": 0.046048641204833984, \"node\": \"stg_orders_current\", \"status\": \"success\"}, {\"execution_time\": 0.0433497428894043, \"node\": \"stg_product_category_translation_events\", \"status\": \"success\"}, {\"execution_time\": 0.043076515197753906, \"node\": \"stg_products_events\", \"status\": \"success\"}, {\"execution_time\": 0.04483532905578613, \"node\": \"stg_sellers_current\", \"status\": \"success\"}, {\"execution_time\": 0.4458656311035156, \"node\": \"customer_scd2_collapses_identical_update_and_closes_on_delete\", \"status\": \"pass\"}, {\"execution_time\": 0.2964026927947998, \"node\": \"dim_customer_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.19407296180725098, \"node\": \"payment_allocation_is_proportional_at_item_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.18792223930358887, \"node\": \"zero_gross_order_has_null_payment_allocation\", \"status\": \"pass\"}, {\"execution_time\": 0.14940953254699707, \"node\": \"dim_date\", \"status\": \"success\"}, {\"execution_time\": 0.11028242111206055, \"node\": \"dim_order_status\", \"status\": \"success\"}, {\"execution_time\": 0.33182334899902344, \"node\": \"product_translation_does_not_resurrect_an_old_category\", \"status\": \"pass\"}, {\"execution_time\": 0.21037650108337402, \"node\": \"dim_product_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.11596202850341797, \"node\": \"dim_seller\", \"status\": \"success\"}, {\"execution_time\": 0.06764483451843262, \"node\": \"assert_customer_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.04871177673339844, \"node\": \"candidate_not_null_dim_customer_scd2_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03938603401184082, \"node\": \"candidate_not_null_dim_customer_scd2_customer_unique_id\", \"status\": \"pass\"}, {\"execution_time\": 0.03508114814758301, \"node\": \"candidate_not_null_dim_customer_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.03595232963562012, \"node\": \"unique_combination_of_columns_dim_customer_scd2_sync_run_seq__customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.06631660461425781, \"node\": \"assert_payment_allocations_balance\", \"status\": \"pass\"}, {\"execution_time\": 0.03881573677062988, \"node\": \"candidate_not_null_dim_date_date_day\", \"status\": \"pass\"}, {\"execution_time\": 0.04301261901855469, \"node\": \"candidate_not_null_dim_date_date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03258991241455078, \"node\": \"candidate_not_null_dim_date_sync_run_seq\", \"status\": \"pass\"}, {\"execution_time\": 0.03568768501281738, \"node\": \"unique_combination_of_columns_dim_date_sync_run_seq__date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03516101837158203, \"node\": \"candidate_not_null_dim_order_status_order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.036608219146728516, \"node\": \"candidate_not_null_dim_order_status_order_status_key\", \"status\": \"pass\"}, {\"execution_time\": 0.03608584403991699, \"node\": \"unique_combination_of_columns_dim_order_status_sync_run_seq__order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.03546762466430664, \"node\": \"assert_product_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.032393455505371094, \"node\": \"candidate_not_null_dim_product_scd2_product_id\", \"status\": \"pass\"}, {\"execution_time\": 0.03371906280517578, \"node\": \"candidate_not_null_dim_product_scd2_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04016709327697754, \"node\": \"candidate_not_null_dim_product_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.10913205146789551, \"node\": \"unique_combination_of_columns_dim_product_scd2_sync_run_seq__product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.033445119857788086, \"node\": \"candidate_not_null_dim_seller_seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.0547487735748291, \"node\": \"candidate_not_null_dim_seller_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.06275749206542969, \"node\": \"unique_combination_of_columns_dim_seller_sync_run_seq__seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.7015261650085449, \"node\": \"fact_order_items\", \"status\": \"success\"}, {\"execution_time\": 0.05932188034057617, \"node\": \"assert_fact_order_items_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.05270195007324219, \"node\": \"candidate_not_null_fact_order_items_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04614877700805664, \"node\": \"candidate_not_null_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.042337894439697266, \"node\": \"candidate_not_null_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.04498124122619629, \"node\": \"candidate_not_null_fact_order_items_order_item_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04719042778015137, \"node\": \"candidate_not_null_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.04277658462524414, \"node\": \"candidate_not_null_fact_order_items_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.0422670841217041, \"node\": \"candidate_not_null_fact_order_items_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.044832468032836914, \"node\": \"candidate_relationships_fact_order_items_customer_key__customer_key__ref_dim_customer_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.053900718688964844, \"node\": \"candidate_relationships_fact_order_items_product_key__product_key__ref_dim_product_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.0505220890045166, \"node\": \"candidate_relationships_fact_order_items_seller_key__seller_key__ref_dim_seller_\", \"status\": \"pass\"}, {\"execution_time\": 0.04542040824890137, \"node\": \"non_negative_fact_order_items_allocated_payment_value\", \"status\": \"pass\"}, {\"execution_time\": 0.0441129207611084, \"node\": \"non_negative_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.046563148498535156, \"node\": \"non_negative_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.043653249740600586, \"node\": \"non_negative_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.04676365852355957, \"node\": \"unique_combination_of_columns_fact_order_items_sync_run_seq__order_id__order_item_id\", \"status\": \"pass\"}, {\"execution_time\": 0.16716909408569336, \"node\": \"mart_daily_revenue\", \"status\": \"success\"}, {\"execution_time\": 0.15833473205566406, \"node\": \"mart_monthly_arpu\", \"status\": \"success\"}, {\"execution_time\": 0.06080317497253418, \"node\": \"assert_daily_revenue_components\", \"status\": \"pass\"}, {\"execution_time\": 0.06313300132751465, \"node\": \"candidate_not_null_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.06130862236022949, \"node\": \"candidate_not_null_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.05366706848144531, \"node\": \"candidate_not_null_mart_daily_revenue_order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.05156826972961426, \"node\": \"candidate_not_null_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.0486445426940918, \"node\": \"non_negative_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.05683469772338867, \"node\": \"non_negative_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.0474851131439209, \"node\": \"non_negative_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.04796314239501953, \"node\": \"unique_combination_of_columns_mart_daily_revenue_sync_run_seq__order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.043645381927490234, \"node\": \"assert_monthly_arpu_formulas\", \"status\": \"pass\"}, {\"execution_time\": 0.03497743606567383, \"node\": \"candidate_not_null_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.034363508224487305, \"node\": \"candidate_not_null_mart_monthly_arpu_order_month\", \"status\": \"pass\"}, {\"execution_time\": 0.03560638427734375, \"node\": \"candidate_not_null_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.03290700912475586, \"node\": \"candidate_not_null_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.03879904747009277, \"node\": \"non_negative_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.03554534912109375, \"node\": \"non_negative_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.034639596939086914, \"node\": \"non_negative_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.03925514221191406, \"node\": \"unique_combination_of_columns_mart_monthly_arpu_sync_run_seq__order_month\", \"status\": \"pass\"}], \"selector\": \"serving_candidate\", \"status_counts\": {\"pass\": 59, \"success\": 16}, \"success\": true, \"vars\": {\"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3}}, \"expected_entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 90, \"iceberg_snapshot_ids\": {\"customers\": 2110013481413148761, \"order_items\": 5948428514509384907, \"order_payments\": 3389689790513587639, \"order_reviews\": 2583938958004099503, \"orders\": 8111531154139198555, \"product_category_translation\": 8401292361000666733, \"products\": 6511797434303314151, \"sellers\": 3940700634153017490}, \"is_noop\": false, \"materialized_entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"materialized_event_count\": 90, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3, \"sync_run_status\": \"SUCCEEDED\", \"target_offsets\": {\"olist_cdc.olist_oltp.customers:0\": 9, \"olist_cdc.olist_oltp.order_items:0\": 5, \"olist_cdc.olist_oltp.order_items:1\": 5, \"olist_cdc.olist_oltp.order_items:2\": 6, \"olist_cdc.olist_oltp.order_payments:0\": 5, \"olist_cdc.olist_oltp.order_payments:1\": 4, \"olist_cdc.olist_oltp.order_payments:2\": 4, \"olist_cdc.olist_oltp.order_reviews:0\": 5, \"olist_cdc.olist_oltp.order_reviews:1\": 4, \"olist_cdc.olist_oltp.order_reviews:2\": 2, \"olist_cdc.olist_oltp.orders:0\": 3, \"olist_cdc.olist_oltp.orders:1\": 4, \"olist_cdc.olist_oltp.orders:2\": 4, \"olist_cdc.olist_oltp.product_category_translation:0\": 4, \"olist_cdc.olist_oltp.products:0\": 7, \"olist_cdc.olist_oltp.sellers:0\": 3}, \"target_transaction_id\": \"file=binlog.000002,pos=21633\"}\n",
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
          "duration_seconds": 2.532,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"validate-serving\", \"current_views\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"dbt\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 3, \\\"sync_run_id\\\": \\\"sync-00000000000000000003\\\"}\"], \"result_count\": 75, \"status_counts\": {\"pass\": 59, \"success\": 16}}, \"gold_views\": {\"dim_customer_scd2\": {\"candidate\": 8, \"stable\": 8}, \"dim_date\": {\"candidate\": 46, \"stable\": 46}, \"dim_order_status\": {\"candidate\": 2, \"stable\": 2}, \"dim_product_scd2\": {\"candidate\": 8, \"stable\": 8}, \"dim_seller\": {\"candidate\": 4, \"stable\": 4}, \"fact_order_items\": {\"candidate\": 18, \"stable\": 18}, \"mart_daily_revenue\": {\"candidate\": 13, \"stable\": 13}, \"mart_monthly_arpu\": {\"candidate\": 7, \"stable\": 7}}, \"static_validation\": {\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 216 packages in 1ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"warning: in the working copy of 'streaming/schemas/captured-writer-schemas/manifest.json', LF will be replaced by CRLF the next time Git touches it\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"All checks passed!\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"91 files already formatted\", \"exit_code\": 0, \"status\": \"passed\"}], \"status\": \"ready\"}, \"status\": \"ready\", \"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 60.298,
      "gate": "08-additive-schema",
      "status": "PASS",
      "timestamp": "2026-08-03T19:12:55.628533+00:00"
    },
    "09-rebuild": {
      "assertions": [
        {
          "detail": {
            "command": "rebuild-serving",
            "dag_run_id": "stage_v_clean_e113c55_rebuild_bbf07a25933a",
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
              "customers": 2110013481413148761,
              "order_items": 5948428514509384907,
              "order_payments": 3389689790513587639,
              "order_reviews": 2583938958004099503,
              "orders": 8111531154139198555,
              "product_category_translation": 8401292361000666733,
              "products": 6511797434303314151,
              "sellers": 3940700634153017490
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
              "customers": 2110013481413148761,
              "order_items": 5948428514509384907,
              "order_payments": 3389689790513587639,
              "order_reviews": 2583938958004099503,
              "orders": 8111531154139198555,
              "product_category_translation": 8401292361000666733,
              "products": 6511797434303314151,
              "sellers": 3940700634153017490
            },
            "materialized_event_count": 90,
            "row_manifests": {
              "candidate_physical": {
                "customers": {
                  "manifest_sha256": "2163b64da4630010afb36a5a1d647f7f9061dd27721750be5d4343756f68f509",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "6504201ef8e7783b67bcd3c6cdc25343a6fd7e3ba5d05c20f586e5066addd019"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "1af1f9b6f8bee67ec321c0c76a6fd7747dcd16efd15541c145fc45dc04671aaf"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "58e95e7e89fdf89a9219ae3c4784a078cabf33ce1bd3cdb9a24ba78515d0cfcc"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "1347812f4872f7ec8a5d1d1de1e6f5e728f5197826f19f2044b83426400d8b04"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "4d37ae8594d7c6a23ef1a2da18c51ff718860cc0e86cd8df9fe1b7fd386c1492"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "28095779e50db90fb650a166495817f630c58b4d9cfd86b7cbb23afd9de6ab9b"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "cd2331d56a106934ebf661221b1e11246cc7f037086902c7c348a4011f1f6ae9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "c237aab742403af52fcd2448e403a9a4bde89f4c3e13e708b99a994b7678cb77"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "b137c7cc3317992c2b86690f77bed9476bd93d2bfa2e8cc7db57889448024428"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "e61f13501d7d8d1e775be282615a521f628c487cc8d540c22908f4a80e4de93b",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1bc0c002d676f3311cfea0d8b439ef18c4b8838a25ef73469a86aa6d481ead1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "1cba70c1a36d197dbd2565aa114d7167e6fc2720856d7d2d79cbf4ba638a1b68"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "ac570e4fafeddd75713c36c59f0e238a78dc7673abd7284f9de3f8d413e0d484"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "34a13c47774cdf4dc0fcfe2399e92ef24795ed26114b063d90860024c8169f3a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "92e2358a73d0feda7de085ffbcf46bbe5faccc646ea6f8a7580a7d1f727ceeb2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "5e8794d558c53b77db572e965c2c76b1f4b7107e0a290000cbea6b220954a7c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "d80b661447f72f73422ee13dc5f0d50510fae086f0fc33a018b86a0bde4c2854"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "18bef5dae4b7ea33e98cef90dba7d518d4e0c0a1bfa5d386c9bc49699b98bb48"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "9c86590292dde1ecb5b398eb7c824839425642d6cb013f20dfd67e7294f6a3a7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "ae677f2af1b2eeb86529c9f58795495fc1292fa03898b6c27a0238cc0d9df487"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "d4dd8379bed1c7ead2e1823b6d840f63116331ecac68bde5e5d949d20a62efab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "774071905f13623890360e71b932fa6018f714c8e960696902dd82d815c56d17"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "5b53b626984338449402b2cff29e5de47118f84925d6f0e7c3acb25d841d9bac"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3ad64585ebd623659647c86343fb2c3a67a8abcbb149d6330076d7f65ebc2c33"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fbb723f947479ff4bc85a380e8d03868843e9d915fa195522c1123133944cd1b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "d246fb12f69180726adc9b18d00eee7c5c16f9bc9cd05944a9e1514420b1d251"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "82ffb47c67b5d59f3827598210003985afe288fa0bb6d4a674d929812f66c218"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "8015c870ad4d3fb197b8ed140e5bdbfd3f7779fcea07f9491a78f6a4f979df16"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f830be77e3f72131fd368f713cd5ba24bb18bb685cfb5424703be24b79f14ea2",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "85f2d626fe0728e4f24a8471fd325cf48590889d8f31fceecf42599539bff7ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "f4b7abdb8d2442513de5691e82787365d4010be7961664bd6693ae08befabd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "99a192a428458105fb40a98049f80638e12deb5f48cee3961a2b93920e086617"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "013f5cf35c61796bd9160b65580daf0c2db5950646e9cd650b078fea05cda065"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "113198c969adc46ae00c7870b4827e919ac2d22b7f7236822e0319de82f93dde"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "c93e9d5e5c1a2116dba1602dc14ae29862849bb14573ce125508cec212abb103"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "0e6d5b58695652438712a319b0d8f50377144fa9f00aed7dd7a7ff28b19d7dbc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "2ace57e0772a079483309452020fb09cba21887f860f97622ceb8b5751b81dff"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "81d6d943fe9d5cd9d3fa062893a5b24c5ce830619737427cdde1ec7dd2fd31af"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "e3cc2445917d5c788f424487949b5ad7cd6adbd015ccf3c764f85cd2b823c9ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "fd0f02a874dd9893caa2cb234e353fa3ec5c44a09ca618452fdd50e0873108a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "1e00d0c46041fcf5d023c8c3cc3f29cda7ad4b80e8ac3e6288c87dff6ae13195"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "def771ab7abb15d4f8dda741e0f122a6ba34cd1c83799fa57488fd20e1f1312a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "e02b86ed8ec39dc40bd6cdf0a9258f0a057211e46aa8e2a92524821c8d5e877e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "de3a04e84f1756cc07b586194ad1b19731d5fe4adce8db4c73eced3405cd1977"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "850a3cc7e4d77c7ee693f5bee94098d78fdb2fb00607a557ab6d3d35ca2ab851"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "584689f836ec7c27688a8e040062b6453f969e004cd946b6018186d43f055242",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "2006044943c124b8aa17b3cc2c69d633434c66b4d54e999004b7a7a61f2b2f56"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "c84bb7e7e04a6cab45811148e29ab241908b4f0fde9b38548f22778cc5e86e6f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "1ce0098440765769980aedcf22eea71ca59e5e0beb63ef07b00228f7f7a7fe25"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "44150e36c1224c180bdbb3dfc20382a6e59ed1b328e91579c56362436a591a00"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "c6c2760a11e553aa0a0ddefb66299493f2d4ed5bc249ea9fb7246fae104312ad"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "893bfe7b6f9694d12d9daad1ffd17a96bdcc2440dd21dae66656ed15b7e15e67"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "7017290069cd0d4390830739b6bea8e131d18cfda5f92a7b574b3c592d5f50e1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "ace2d4fb20ac23e26ca426152f507ba7bd511c52d31d030439392a70f2159429"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "ec9008c1ce945999916de5ce7fafca0e1e4b7e866838932eb069e55f85f77ee7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "a8731f1d44d1c55e309048156f7694bc1b1c14f4f7816dadc0c19c1a16b53616"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "be359fe95a1275a648eb31724f47ccaa581b6a019f828f62b1c47be9be5dc612"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "16bd411e3ee55397c8244b79be7083587a38a1b0e1e326ab466b732f87cafa52"
                    },
                    {
                      "is_deleted": true,
                      "review_id": "wave2_review_001",
                      "row_hash": "44f322e87cfd6880ce4fccfc29daf4fda32b62a4bd96a936f77494c04d14f25a"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "2a79b4a6501ef52b8186ebb0e9a718d53f150b6c0991e9705f0c9a4e974d97c1",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "4d0bdbee23e2bff1eb2a3d7581eaa25e4be28916a635d552d6ae3ce7eb53fc72"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "ba0c5d34562bc3805739d60905f0e1e8125b8287f81dba8fac6b65f0699e8266"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "697542590d2ffbe526948106f9a00c17f131df530a05017602aa705bc15faab8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "7f9a69d1646f89a2577cc1641155fba1c106cb76cf69586615d871d8b9b5611a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "8dcaf1f60fd4ab2b22798f49e9edca0a9a0320de87e8d52d89e75f38133ef554"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "65cb1e8426a81079cafa2ea5c53d1d74a825ea578abca611623139ce9213fa3d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "8793912f4b5c53dac2896586711a58e4405fd64d1f9c537545e3f29af5d2bdcb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "81bdf76398323b4a8ecf7444e06ce90881809d83caa476e36af8486a60f1068c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "58fec23f57c0ae6968f7d2ba90ea3b8c10e2abe383861d186f381f36f3db1f9e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "602b9edbeb97ee10c6c400c0089877803091724a0cdcc8aedfc9b4fae09efbd8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "cece245d60ddf1cb6705edda55d24404c22d5e21bbd734cfa3e125c4a620a167"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d95f8484809272ffe78deba80f32795f617f62d412dbd75c6456a94e5ab08254"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "68edf4824734005ac066bbfc5641f3e1a1de318d1a4db8d0874d30c750af2be8"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61b9c2df074518276bd3d99a8c9acadb133c4afea4f258debe4db8e3ced6a830",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "64ed3899495ebff9294340b3518eb34b72d73e3940870866807ac3958cdee332"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "fa10f800c026c3a1ff361d6110d265045b2e2b09d9ca3417716f1a5b4d83fce0"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3da61d52af39daefde08800dbec20595d14e7a7c45427feae30faecdbca978d4"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "fae1f30a10d1bc550812f344ee228a3ab362e21da161e87e47ecdac7326268ba"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "63bc2cbf4d0d9e4d0923f8f9aebd401748f17cbdf025518fa7d7536b85bde2c5"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "2583e4f16a2500e34069514018a8f2ea03fea0586a6ac598d1e292122df73a43",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "f30c3de8a18b52fbffe84cc3eeb38190285cbfc14eec690df3510ec8174bf8e8"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "a866f66b3a60a873b64f8664e230b21d2618ce37d80256e55edb58b2d1609311"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "5bba82f9177b6051a2bec4766f3818c95a3a218b6cb3f49f0f7f2ce08eabc08a"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "54120120288b40e126390f879475128a7c546dc5894244ffbab2dc41ec0bbdea"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "e3e302109075c5e71050af30fa60a9d9622ab255ff6498c436b7c2b08ab9e27c"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "876feb4157608ae15730542019e1787f95a35542f7e90339dae0471f76530717"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "badd932ef5030c719beb1cc00b0d76c54317dcaa503b1b8850bbfaa39d0a73b6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "e53554b6fa0e0c8fa01fa8e1394faf6c45176fc6a7497a9e1e26d2b0253b599e"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "301a7ea1b2514321ab751e3194dd500461ea2d3a4cc51eb96b552288e2597da2",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "232ca4156abc6eecc1c68444c6e1983abd566b30c7d808b5705f4794bd1c7edf",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c443142ddbf50fb18a4de115e8821940265fdb8eb305adaf2fd6a53e74b92e67",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "a6b81e430572ec5b290105fcd24df2e7811dbfe7e1cbcaf0d0246ef1fe4b6c9d",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5a794eb23d83d8ef0d7a5cd636119e122d8f5d946fd04ca69b1541bd06dffb1e",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "candidate_visible": {
                "customers": {
                  "manifest_sha256": "2163b64da4630010afb36a5a1d647f7f9061dd27721750be5d4343756f68f509",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "6504201ef8e7783b67bcd3c6cdc25343a6fd7e3ba5d05c20f586e5066addd019"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "1af1f9b6f8bee67ec321c0c76a6fd7747dcd16efd15541c145fc45dc04671aaf"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "58e95e7e89fdf89a9219ae3c4784a078cabf33ce1bd3cdb9a24ba78515d0cfcc"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "1347812f4872f7ec8a5d1d1de1e6f5e728f5197826f19f2044b83426400d8b04"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "4d37ae8594d7c6a23ef1a2da18c51ff718860cc0e86cd8df9fe1b7fd386c1492"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "28095779e50db90fb650a166495817f630c58b4d9cfd86b7cbb23afd9de6ab9b"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "cd2331d56a106934ebf661221b1e11246cc7f037086902c7c348a4011f1f6ae9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "c237aab742403af52fcd2448e403a9a4bde89f4c3e13e708b99a994b7678cb77"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "b137c7cc3317992c2b86690f77bed9476bd93d2bfa2e8cc7db57889448024428"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "e61f13501d7d8d1e775be282615a521f628c487cc8d540c22908f4a80e4de93b",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1bc0c002d676f3311cfea0d8b439ef18c4b8838a25ef73469a86aa6d481ead1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "1cba70c1a36d197dbd2565aa114d7167e6fc2720856d7d2d79cbf4ba638a1b68"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "ac570e4fafeddd75713c36c59f0e238a78dc7673abd7284f9de3f8d413e0d484"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "34a13c47774cdf4dc0fcfe2399e92ef24795ed26114b063d90860024c8169f3a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "92e2358a73d0feda7de085ffbcf46bbe5faccc646ea6f8a7580a7d1f727ceeb2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "5e8794d558c53b77db572e965c2c76b1f4b7107e0a290000cbea6b220954a7c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "d80b661447f72f73422ee13dc5f0d50510fae086f0fc33a018b86a0bde4c2854"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "18bef5dae4b7ea33e98cef90dba7d518d4e0c0a1bfa5d386c9bc49699b98bb48"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "9c86590292dde1ecb5b398eb7c824839425642d6cb013f20dfd67e7294f6a3a7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "ae677f2af1b2eeb86529c9f58795495fc1292fa03898b6c27a0238cc0d9df487"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "d4dd8379bed1c7ead2e1823b6d840f63116331ecac68bde5e5d949d20a62efab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "774071905f13623890360e71b932fa6018f714c8e960696902dd82d815c56d17"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "5b53b626984338449402b2cff29e5de47118f84925d6f0e7c3acb25d841d9bac"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3ad64585ebd623659647c86343fb2c3a67a8abcbb149d6330076d7f65ebc2c33"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fbb723f947479ff4bc85a380e8d03868843e9d915fa195522c1123133944cd1b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "d246fb12f69180726adc9b18d00eee7c5c16f9bc9cd05944a9e1514420b1d251"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "82ffb47c67b5d59f3827598210003985afe288fa0bb6d4a674d929812f66c218"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "8015c870ad4d3fb197b8ed140e5bdbfd3f7779fcea07f9491a78f6a4f979df16"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f830be77e3f72131fd368f713cd5ba24bb18bb685cfb5424703be24b79f14ea2",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "85f2d626fe0728e4f24a8471fd325cf48590889d8f31fceecf42599539bff7ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "f4b7abdb8d2442513de5691e82787365d4010be7961664bd6693ae08befabd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "99a192a428458105fb40a98049f80638e12deb5f48cee3961a2b93920e086617"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "013f5cf35c61796bd9160b65580daf0c2db5950646e9cd650b078fea05cda065"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "113198c969adc46ae00c7870b4827e919ac2d22b7f7236822e0319de82f93dde"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "c93e9d5e5c1a2116dba1602dc14ae29862849bb14573ce125508cec212abb103"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "0e6d5b58695652438712a319b0d8f50377144fa9f00aed7dd7a7ff28b19d7dbc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "2ace57e0772a079483309452020fb09cba21887f860f97622ceb8b5751b81dff"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "81d6d943fe9d5cd9d3fa062893a5b24c5ce830619737427cdde1ec7dd2fd31af"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "e3cc2445917d5c788f424487949b5ad7cd6adbd015ccf3c764f85cd2b823c9ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "fd0f02a874dd9893caa2cb234e353fa3ec5c44a09ca618452fdd50e0873108a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "1e00d0c46041fcf5d023c8c3cc3f29cda7ad4b80e8ac3e6288c87dff6ae13195"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "def771ab7abb15d4f8dda741e0f122a6ba34cd1c83799fa57488fd20e1f1312a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "e02b86ed8ec39dc40bd6cdf0a9258f0a057211e46aa8e2a92524821c8d5e877e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "de3a04e84f1756cc07b586194ad1b19731d5fe4adce8db4c73eced3405cd1977"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "850a3cc7e4d77c7ee693f5bee94098d78fdb2fb00607a557ab6d3d35ca2ab851"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "1a68c883a84f0e08442a5ffbf147824a4512efaa314ead2ee5d26cba1542311e",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "2006044943c124b8aa17b3cc2c69d633434c66b4d54e999004b7a7a61f2b2f56"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "c84bb7e7e04a6cab45811148e29ab241908b4f0fde9b38548f22778cc5e86e6f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "1ce0098440765769980aedcf22eea71ca59e5e0beb63ef07b00228f7f7a7fe25"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "44150e36c1224c180bdbb3dfc20382a6e59ed1b328e91579c56362436a591a00"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "c6c2760a11e553aa0a0ddefb66299493f2d4ed5bc249ea9fb7246fae104312ad"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "893bfe7b6f9694d12d9daad1ffd17a96bdcc2440dd21dae66656ed15b7e15e67"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "7017290069cd0d4390830739b6bea8e131d18cfda5f92a7b574b3c592d5f50e1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "ace2d4fb20ac23e26ca426152f507ba7bd511c52d31d030439392a70f2159429"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "ec9008c1ce945999916de5ce7fafca0e1e4b7e866838932eb069e55f85f77ee7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "a8731f1d44d1c55e309048156f7694bc1b1c14f4f7816dadc0c19c1a16b53616"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "be359fe95a1275a648eb31724f47ccaa581b6a019f828f62b1c47be9be5dc612"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "16bd411e3ee55397c8244b79be7083587a38a1b0e1e326ab466b732f87cafa52"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "2a79b4a6501ef52b8186ebb0e9a718d53f150b6c0991e9705f0c9a4e974d97c1",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "4d0bdbee23e2bff1eb2a3d7581eaa25e4be28916a635d552d6ae3ce7eb53fc72"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "ba0c5d34562bc3805739d60905f0e1e8125b8287f81dba8fac6b65f0699e8266"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "697542590d2ffbe526948106f9a00c17f131df530a05017602aa705bc15faab8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "7f9a69d1646f89a2577cc1641155fba1c106cb76cf69586615d871d8b9b5611a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "8dcaf1f60fd4ab2b22798f49e9edca0a9a0320de87e8d52d89e75f38133ef554"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "65cb1e8426a81079cafa2ea5c53d1d74a825ea578abca611623139ce9213fa3d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "8793912f4b5c53dac2896586711a58e4405fd64d1f9c537545e3f29af5d2bdcb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "81bdf76398323b4a8ecf7444e06ce90881809d83caa476e36af8486a60f1068c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "58fec23f57c0ae6968f7d2ba90ea3b8c10e2abe383861d186f381f36f3db1f9e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "602b9edbeb97ee10c6c400c0089877803091724a0cdcc8aedfc9b4fae09efbd8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "cece245d60ddf1cb6705edda55d24404c22d5e21bbd734cfa3e125c4a620a167"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d95f8484809272ffe78deba80f32795f617f62d412dbd75c6456a94e5ab08254"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "68edf4824734005ac066bbfc5641f3e1a1de318d1a4db8d0874d30c750af2be8"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61b9c2df074518276bd3d99a8c9acadb133c4afea4f258debe4db8e3ced6a830",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "64ed3899495ebff9294340b3518eb34b72d73e3940870866807ac3958cdee332"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "fa10f800c026c3a1ff361d6110d265045b2e2b09d9ca3417716f1a5b4d83fce0"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3da61d52af39daefde08800dbec20595d14e7a7c45427feae30faecdbca978d4"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "fae1f30a10d1bc550812f344ee228a3ab362e21da161e87e47ecdac7326268ba"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "63bc2cbf4d0d9e4d0923f8f9aebd401748f17cbdf025518fa7d7536b85bde2c5"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "2583e4f16a2500e34069514018a8f2ea03fea0586a6ac598d1e292122df73a43",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "f30c3de8a18b52fbffe84cc3eeb38190285cbfc14eec690df3510ec8174bf8e8"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "a866f66b3a60a873b64f8664e230b21d2618ce37d80256e55edb58b2d1609311"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "5bba82f9177b6051a2bec4766f3818c95a3a218b6cb3f49f0f7f2ce08eabc08a"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "54120120288b40e126390f879475128a7c546dc5894244ffbab2dc41ec0bbdea"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "e3e302109075c5e71050af30fa60a9d9622ab255ff6498c436b7c2b08ab9e27c"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "876feb4157608ae15730542019e1787f95a35542f7e90339dae0471f76530717"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "badd932ef5030c719beb1cc00b0d76c54317dcaa503b1b8850bbfaa39d0a73b6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "e53554b6fa0e0c8fa01fa8e1394faf6c45176fc6a7497a9e1e26d2b0253b599e"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "301a7ea1b2514321ab751e3194dd500461ea2d3a4cc51eb96b552288e2597da2",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "232ca4156abc6eecc1c68444c6e1983abd566b30c7d808b5705f4794bd1c7edf",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c443142ddbf50fb18a4de115e8821940265fdb8eb305adaf2fd6a53e74b92e67",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "a6b81e430572ec5b290105fcd24df2e7811dbfe7e1cbcaf0d0246ef1fe4b6c9d",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5a794eb23d83d8ef0d7a5cd636119e122d8f5d946fd04ca69b1541bd06dffb1e",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "iceberg_physical": {
                "customers": {
                  "manifest_sha256": "2163b64da4630010afb36a5a1d647f7f9061dd27721750be5d4343756f68f509",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "6504201ef8e7783b67bcd3c6cdc25343a6fd7e3ba5d05c20f586e5066addd019"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "1af1f9b6f8bee67ec321c0c76a6fd7747dcd16efd15541c145fc45dc04671aaf"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "58e95e7e89fdf89a9219ae3c4784a078cabf33ce1bd3cdb9a24ba78515d0cfcc"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "1347812f4872f7ec8a5d1d1de1e6f5e728f5197826f19f2044b83426400d8b04"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "4d37ae8594d7c6a23ef1a2da18c51ff718860cc0e86cd8df9fe1b7fd386c1492"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "28095779e50db90fb650a166495817f630c58b4d9cfd86b7cbb23afd9de6ab9b"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "cd2331d56a106934ebf661221b1e11246cc7f037086902c7c348a4011f1f6ae9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "c237aab742403af52fcd2448e403a9a4bde89f4c3e13e708b99a994b7678cb77"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "b137c7cc3317992c2b86690f77bed9476bd93d2bfa2e8cc7db57889448024428"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "e61f13501d7d8d1e775be282615a521f628c487cc8d540c22908f4a80e4de93b",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1bc0c002d676f3311cfea0d8b439ef18c4b8838a25ef73469a86aa6d481ead1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "1cba70c1a36d197dbd2565aa114d7167e6fc2720856d7d2d79cbf4ba638a1b68"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "ac570e4fafeddd75713c36c59f0e238a78dc7673abd7284f9de3f8d413e0d484"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "34a13c47774cdf4dc0fcfe2399e92ef24795ed26114b063d90860024c8169f3a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "92e2358a73d0feda7de085ffbcf46bbe5faccc646ea6f8a7580a7d1f727ceeb2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "5e8794d558c53b77db572e965c2c76b1f4b7107e0a290000cbea6b220954a7c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "d80b661447f72f73422ee13dc5f0d50510fae086f0fc33a018b86a0bde4c2854"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "18bef5dae4b7ea33e98cef90dba7d518d4e0c0a1bfa5d386c9bc49699b98bb48"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "9c86590292dde1ecb5b398eb7c824839425642d6cb013f20dfd67e7294f6a3a7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "ae677f2af1b2eeb86529c9f58795495fc1292fa03898b6c27a0238cc0d9df487"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "d4dd8379bed1c7ead2e1823b6d840f63116331ecac68bde5e5d949d20a62efab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "774071905f13623890360e71b932fa6018f714c8e960696902dd82d815c56d17"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "5b53b626984338449402b2cff29e5de47118f84925d6f0e7c3acb25d841d9bac"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3ad64585ebd623659647c86343fb2c3a67a8abcbb149d6330076d7f65ebc2c33"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fbb723f947479ff4bc85a380e8d03868843e9d915fa195522c1123133944cd1b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "d246fb12f69180726adc9b18d00eee7c5c16f9bc9cd05944a9e1514420b1d251"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "82ffb47c67b5d59f3827598210003985afe288fa0bb6d4a674d929812f66c218"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "8015c870ad4d3fb197b8ed140e5bdbfd3f7779fcea07f9491a78f6a4f979df16"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f830be77e3f72131fd368f713cd5ba24bb18bb685cfb5424703be24b79f14ea2",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "85f2d626fe0728e4f24a8471fd325cf48590889d8f31fceecf42599539bff7ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "f4b7abdb8d2442513de5691e82787365d4010be7961664bd6693ae08befabd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "99a192a428458105fb40a98049f80638e12deb5f48cee3961a2b93920e086617"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "013f5cf35c61796bd9160b65580daf0c2db5950646e9cd650b078fea05cda065"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "113198c969adc46ae00c7870b4827e919ac2d22b7f7236822e0319de82f93dde"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "c93e9d5e5c1a2116dba1602dc14ae29862849bb14573ce125508cec212abb103"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "0e6d5b58695652438712a319b0d8f50377144fa9f00aed7dd7a7ff28b19d7dbc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "2ace57e0772a079483309452020fb09cba21887f860f97622ceb8b5751b81dff"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "81d6d943fe9d5cd9d3fa062893a5b24c5ce830619737427cdde1ec7dd2fd31af"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "e3cc2445917d5c788f424487949b5ad7cd6adbd015ccf3c764f85cd2b823c9ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "fd0f02a874dd9893caa2cb234e353fa3ec5c44a09ca618452fdd50e0873108a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "1e00d0c46041fcf5d023c8c3cc3f29cda7ad4b80e8ac3e6288c87dff6ae13195"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "def771ab7abb15d4f8dda741e0f122a6ba34cd1c83799fa57488fd20e1f1312a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "e02b86ed8ec39dc40bd6cdf0a9258f0a057211e46aa8e2a92524821c8d5e877e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "de3a04e84f1756cc07b586194ad1b19731d5fe4adce8db4c73eced3405cd1977"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "850a3cc7e4d77c7ee693f5bee94098d78fdb2fb00607a557ab6d3d35ca2ab851"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "584689f836ec7c27688a8e040062b6453f969e004cd946b6018186d43f055242",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "2006044943c124b8aa17b3cc2c69d633434c66b4d54e999004b7a7a61f2b2f56"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "c84bb7e7e04a6cab45811148e29ab241908b4f0fde9b38548f22778cc5e86e6f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "1ce0098440765769980aedcf22eea71ca59e5e0beb63ef07b00228f7f7a7fe25"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "44150e36c1224c180bdbb3dfc20382a6e59ed1b328e91579c56362436a591a00"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "c6c2760a11e553aa0a0ddefb66299493f2d4ed5bc249ea9fb7246fae104312ad"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "893bfe7b6f9694d12d9daad1ffd17a96bdcc2440dd21dae66656ed15b7e15e67"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "7017290069cd0d4390830739b6bea8e131d18cfda5f92a7b574b3c592d5f50e1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "ace2d4fb20ac23e26ca426152f507ba7bd511c52d31d030439392a70f2159429"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "ec9008c1ce945999916de5ce7fafca0e1e4b7e866838932eb069e55f85f77ee7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "a8731f1d44d1c55e309048156f7694bc1b1c14f4f7816dadc0c19c1a16b53616"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "be359fe95a1275a648eb31724f47ccaa581b6a019f828f62b1c47be9be5dc612"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "16bd411e3ee55397c8244b79be7083587a38a1b0e1e326ab466b732f87cafa52"
                    },
                    {
                      "is_deleted": true,
                      "review_id": "wave2_review_001",
                      "row_hash": "44f322e87cfd6880ce4fccfc29daf4fda32b62a4bd96a936f77494c04d14f25a"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "2a79b4a6501ef52b8186ebb0e9a718d53f150b6c0991e9705f0c9a4e974d97c1",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "4d0bdbee23e2bff1eb2a3d7581eaa25e4be28916a635d552d6ae3ce7eb53fc72"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "ba0c5d34562bc3805739d60905f0e1e8125b8287f81dba8fac6b65f0699e8266"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "697542590d2ffbe526948106f9a00c17f131df530a05017602aa705bc15faab8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "7f9a69d1646f89a2577cc1641155fba1c106cb76cf69586615d871d8b9b5611a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "8dcaf1f60fd4ab2b22798f49e9edca0a9a0320de87e8d52d89e75f38133ef554"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "65cb1e8426a81079cafa2ea5c53d1d74a825ea578abca611623139ce9213fa3d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "8793912f4b5c53dac2896586711a58e4405fd64d1f9c537545e3f29af5d2bdcb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "81bdf76398323b4a8ecf7444e06ce90881809d83caa476e36af8486a60f1068c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "58fec23f57c0ae6968f7d2ba90ea3b8c10e2abe383861d186f381f36f3db1f9e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "602b9edbeb97ee10c6c400c0089877803091724a0cdcc8aedfc9b4fae09efbd8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "cece245d60ddf1cb6705edda55d24404c22d5e21bbd734cfa3e125c4a620a167"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d95f8484809272ffe78deba80f32795f617f62d412dbd75c6456a94e5ab08254"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "68edf4824734005ac066bbfc5641f3e1a1de318d1a4db8d0874d30c750af2be8"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61b9c2df074518276bd3d99a8c9acadb133c4afea4f258debe4db8e3ced6a830",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "64ed3899495ebff9294340b3518eb34b72d73e3940870866807ac3958cdee332"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "fa10f800c026c3a1ff361d6110d265045b2e2b09d9ca3417716f1a5b4d83fce0"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3da61d52af39daefde08800dbec20595d14e7a7c45427feae30faecdbca978d4"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "fae1f30a10d1bc550812f344ee228a3ab362e21da161e87e47ecdac7326268ba"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "63bc2cbf4d0d9e4d0923f8f9aebd401748f17cbdf025518fa7d7536b85bde2c5"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "2583e4f16a2500e34069514018a8f2ea03fea0586a6ac598d1e292122df73a43",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "f30c3de8a18b52fbffe84cc3eeb38190285cbfc14eec690df3510ec8174bf8e8"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "a866f66b3a60a873b64f8664e230b21d2618ce37d80256e55edb58b2d1609311"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "5bba82f9177b6051a2bec4766f3818c95a3a218b6cb3f49f0f7f2ce08eabc08a"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "54120120288b40e126390f879475128a7c546dc5894244ffbab2dc41ec0bbdea"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "e3e302109075c5e71050af30fa60a9d9622ab255ff6498c436b7c2b08ab9e27c"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "876feb4157608ae15730542019e1787f95a35542f7e90339dae0471f76530717"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "badd932ef5030c719beb1cc00b0d76c54317dcaa503b1b8850bbfaa39d0a73b6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "e53554b6fa0e0c8fa01fa8e1394faf6c45176fc6a7497a9e1e26d2b0253b599e"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "301a7ea1b2514321ab751e3194dd500461ea2d3a4cc51eb96b552288e2597da2",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "232ca4156abc6eecc1c68444c6e1983abd566b30c7d808b5705f4794bd1c7edf",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c443142ddbf50fb18a4de115e8821940265fdb8eb305adaf2fd6a53e74b92e67",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "a6b81e430572ec5b290105fcd24df2e7811dbfe7e1cbcaf0d0246ef1fe4b6c9d",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5a794eb23d83d8ef0d7a5cd636119e122d8f5d946fd04ca69b1541bd06dffb1e",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "iceberg_visible": {
                "customers": {
                  "manifest_sha256": "2163b64da4630010afb36a5a1d647f7f9061dd27721750be5d4343756f68f509",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "6504201ef8e7783b67bcd3c6cdc25343a6fd7e3ba5d05c20f586e5066addd019"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "1af1f9b6f8bee67ec321c0c76a6fd7747dcd16efd15541c145fc45dc04671aaf"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "58e95e7e89fdf89a9219ae3c4784a078cabf33ce1bd3cdb9a24ba78515d0cfcc"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "1347812f4872f7ec8a5d1d1de1e6f5e728f5197826f19f2044b83426400d8b04"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "4d37ae8594d7c6a23ef1a2da18c51ff718860cc0e86cd8df9fe1b7fd386c1492"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "28095779e50db90fb650a166495817f630c58b4d9cfd86b7cbb23afd9de6ab9b"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "cd2331d56a106934ebf661221b1e11246cc7f037086902c7c348a4011f1f6ae9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "c237aab742403af52fcd2448e403a9a4bde89f4c3e13e708b99a994b7678cb77"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "b137c7cc3317992c2b86690f77bed9476bd93d2bfa2e8cc7db57889448024428"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "e61f13501d7d8d1e775be282615a521f628c487cc8d540c22908f4a80e4de93b",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1bc0c002d676f3311cfea0d8b439ef18c4b8838a25ef73469a86aa6d481ead1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "1cba70c1a36d197dbd2565aa114d7167e6fc2720856d7d2d79cbf4ba638a1b68"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "ac570e4fafeddd75713c36c59f0e238a78dc7673abd7284f9de3f8d413e0d484"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "34a13c47774cdf4dc0fcfe2399e92ef24795ed26114b063d90860024c8169f3a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "92e2358a73d0feda7de085ffbcf46bbe5faccc646ea6f8a7580a7d1f727ceeb2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "5e8794d558c53b77db572e965c2c76b1f4b7107e0a290000cbea6b220954a7c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "d80b661447f72f73422ee13dc5f0d50510fae086f0fc33a018b86a0bde4c2854"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "18bef5dae4b7ea33e98cef90dba7d518d4e0c0a1bfa5d386c9bc49699b98bb48"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "9c86590292dde1ecb5b398eb7c824839425642d6cb013f20dfd67e7294f6a3a7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "ae677f2af1b2eeb86529c9f58795495fc1292fa03898b6c27a0238cc0d9df487"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "d4dd8379bed1c7ead2e1823b6d840f63116331ecac68bde5e5d949d20a62efab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "774071905f13623890360e71b932fa6018f714c8e960696902dd82d815c56d17"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "5b53b626984338449402b2cff29e5de47118f84925d6f0e7c3acb25d841d9bac"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3ad64585ebd623659647c86343fb2c3a67a8abcbb149d6330076d7f65ebc2c33"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fbb723f947479ff4bc85a380e8d03868843e9d915fa195522c1123133944cd1b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "d246fb12f69180726adc9b18d00eee7c5c16f9bc9cd05944a9e1514420b1d251"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "82ffb47c67b5d59f3827598210003985afe288fa0bb6d4a674d929812f66c218"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "8015c870ad4d3fb197b8ed140e5bdbfd3f7779fcea07f9491a78f6a4f979df16"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f830be77e3f72131fd368f713cd5ba24bb18bb685cfb5424703be24b79f14ea2",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "85f2d626fe0728e4f24a8471fd325cf48590889d8f31fceecf42599539bff7ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "f4b7abdb8d2442513de5691e82787365d4010be7961664bd6693ae08befabd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "99a192a428458105fb40a98049f80638e12deb5f48cee3961a2b93920e086617"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "013f5cf35c61796bd9160b65580daf0c2db5950646e9cd650b078fea05cda065"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "113198c969adc46ae00c7870b4827e919ac2d22b7f7236822e0319de82f93dde"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "c93e9d5e5c1a2116dba1602dc14ae29862849bb14573ce125508cec212abb103"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "0e6d5b58695652438712a319b0d8f50377144fa9f00aed7dd7a7ff28b19d7dbc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "2ace57e0772a079483309452020fb09cba21887f860f97622ceb8b5751b81dff"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "81d6d943fe9d5cd9d3fa062893a5b24c5ce830619737427cdde1ec7dd2fd31af"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "e3cc2445917d5c788f424487949b5ad7cd6adbd015ccf3c764f85cd2b823c9ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "fd0f02a874dd9893caa2cb234e353fa3ec5c44a09ca618452fdd50e0873108a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "1e00d0c46041fcf5d023c8c3cc3f29cda7ad4b80e8ac3e6288c87dff6ae13195"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "def771ab7abb15d4f8dda741e0f122a6ba34cd1c83799fa57488fd20e1f1312a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "e02b86ed8ec39dc40bd6cdf0a9258f0a057211e46aa8e2a92524821c8d5e877e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "de3a04e84f1756cc07b586194ad1b19731d5fe4adce8db4c73eced3405cd1977"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "850a3cc7e4d77c7ee693f5bee94098d78fdb2fb00607a557ab6d3d35ca2ab851"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "1a68c883a84f0e08442a5ffbf147824a4512efaa314ead2ee5d26cba1542311e",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "2006044943c124b8aa17b3cc2c69d633434c66b4d54e999004b7a7a61f2b2f56"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "c84bb7e7e04a6cab45811148e29ab241908b4f0fde9b38548f22778cc5e86e6f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "1ce0098440765769980aedcf22eea71ca59e5e0beb63ef07b00228f7f7a7fe25"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "44150e36c1224c180bdbb3dfc20382a6e59ed1b328e91579c56362436a591a00"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "c6c2760a11e553aa0a0ddefb66299493f2d4ed5bc249ea9fb7246fae104312ad"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "893bfe7b6f9694d12d9daad1ffd17a96bdcc2440dd21dae66656ed15b7e15e67"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "7017290069cd0d4390830739b6bea8e131d18cfda5f92a7b574b3c592d5f50e1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "ace2d4fb20ac23e26ca426152f507ba7bd511c52d31d030439392a70f2159429"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "ec9008c1ce945999916de5ce7fafca0e1e4b7e866838932eb069e55f85f77ee7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "a8731f1d44d1c55e309048156f7694bc1b1c14f4f7816dadc0c19c1a16b53616"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "be359fe95a1275a648eb31724f47ccaa581b6a019f828f62b1c47be9be5dc612"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "16bd411e3ee55397c8244b79be7083587a38a1b0e1e326ab466b732f87cafa52"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "2a79b4a6501ef52b8186ebb0e9a718d53f150b6c0991e9705f0c9a4e974d97c1",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "4d0bdbee23e2bff1eb2a3d7581eaa25e4be28916a635d552d6ae3ce7eb53fc72"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "ba0c5d34562bc3805739d60905f0e1e8125b8287f81dba8fac6b65f0699e8266"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "697542590d2ffbe526948106f9a00c17f131df530a05017602aa705bc15faab8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "7f9a69d1646f89a2577cc1641155fba1c106cb76cf69586615d871d8b9b5611a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "8dcaf1f60fd4ab2b22798f49e9edca0a9a0320de87e8d52d89e75f38133ef554"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "65cb1e8426a81079cafa2ea5c53d1d74a825ea578abca611623139ce9213fa3d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "8793912f4b5c53dac2896586711a58e4405fd64d1f9c537545e3f29af5d2bdcb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "81bdf76398323b4a8ecf7444e06ce90881809d83caa476e36af8486a60f1068c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "58fec23f57c0ae6968f7d2ba90ea3b8c10e2abe383861d186f381f36f3db1f9e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "602b9edbeb97ee10c6c400c0089877803091724a0cdcc8aedfc9b4fae09efbd8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "cece245d60ddf1cb6705edda55d24404c22d5e21bbd734cfa3e125c4a620a167"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d95f8484809272ffe78deba80f32795f617f62d412dbd75c6456a94e5ab08254"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "68edf4824734005ac066bbfc5641f3e1a1de318d1a4db8d0874d30c750af2be8"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61b9c2df074518276bd3d99a8c9acadb133c4afea4f258debe4db8e3ced6a830",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "64ed3899495ebff9294340b3518eb34b72d73e3940870866807ac3958cdee332"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "fa10f800c026c3a1ff361d6110d265045b2e2b09d9ca3417716f1a5b4d83fce0"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3da61d52af39daefde08800dbec20595d14e7a7c45427feae30faecdbca978d4"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "fae1f30a10d1bc550812f344ee228a3ab362e21da161e87e47ecdac7326268ba"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "63bc2cbf4d0d9e4d0923f8f9aebd401748f17cbdf025518fa7d7536b85bde2c5"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "2583e4f16a2500e34069514018a8f2ea03fea0586a6ac598d1e292122df73a43",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "f30c3de8a18b52fbffe84cc3eeb38190285cbfc14eec690df3510ec8174bf8e8"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "a866f66b3a60a873b64f8664e230b21d2618ce37d80256e55edb58b2d1609311"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "5bba82f9177b6051a2bec4766f3818c95a3a218b6cb3f49f0f7f2ce08eabc08a"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "54120120288b40e126390f879475128a7c546dc5894244ffbab2dc41ec0bbdea"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "e3e302109075c5e71050af30fa60a9d9622ab255ff6498c436b7c2b08ab9e27c"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "876feb4157608ae15730542019e1787f95a35542f7e90339dae0471f76530717"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "badd932ef5030c719beb1cc00b0d76c54317dcaa503b1b8850bbfaa39d0a73b6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "e53554b6fa0e0c8fa01fa8e1394faf6c45176fc6a7497a9e1e26d2b0253b599e"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "301a7ea1b2514321ab751e3194dd500461ea2d3a4cc51eb96b552288e2597da2",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "232ca4156abc6eecc1c68444c6e1983abd566b30c7d808b5705f4794bd1c7edf",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c443142ddbf50fb18a4de115e8821940265fdb8eb305adaf2fd6a53e74b92e67",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "a6b81e430572ec5b290105fcd24df2e7811dbfe7e1cbcaf0d0246ef1fe4b6c9d",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5a794eb23d83d8ef0d7a5cd636119e122d8f5d946fd04ca69b1541bd06dffb1e",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "stable_visible": {
                "customers": {
                  "manifest_sha256": "2163b64da4630010afb36a5a1d647f7f9061dd27721750be5d4343756f68f509",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "6504201ef8e7783b67bcd3c6cdc25343a6fd7e3ba5d05c20f586e5066addd019"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "1af1f9b6f8bee67ec321c0c76a6fd7747dcd16efd15541c145fc45dc04671aaf"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "58e95e7e89fdf89a9219ae3c4784a078cabf33ce1bd3cdb9a24ba78515d0cfcc"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "1347812f4872f7ec8a5d1d1de1e6f5e728f5197826f19f2044b83426400d8b04"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "4d37ae8594d7c6a23ef1a2da18c51ff718860cc0e86cd8df9fe1b7fd386c1492"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "28095779e50db90fb650a166495817f630c58b4d9cfd86b7cbb23afd9de6ab9b"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "cd2331d56a106934ebf661221b1e11246cc7f037086902c7c348a4011f1f6ae9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "c237aab742403af52fcd2448e403a9a4bde89f4c3e13e708b99a994b7678cb77"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "b137c7cc3317992c2b86690f77bed9476bd93d2bfa2e8cc7db57889448024428"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "e61f13501d7d8d1e775be282615a521f628c487cc8d540c22908f4a80e4de93b",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1bc0c002d676f3311cfea0d8b439ef18c4b8838a25ef73469a86aa6d481ead1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "1cba70c1a36d197dbd2565aa114d7167e6fc2720856d7d2d79cbf4ba638a1b68"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "ac570e4fafeddd75713c36c59f0e238a78dc7673abd7284f9de3f8d413e0d484"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "34a13c47774cdf4dc0fcfe2399e92ef24795ed26114b063d90860024c8169f3a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "92e2358a73d0feda7de085ffbcf46bbe5faccc646ea6f8a7580a7d1f727ceeb2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "5e8794d558c53b77db572e965c2c76b1f4b7107e0a290000cbea6b220954a7c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "d80b661447f72f73422ee13dc5f0d50510fae086f0fc33a018b86a0bde4c2854"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "18bef5dae4b7ea33e98cef90dba7d518d4e0c0a1bfa5d386c9bc49699b98bb48"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "9c86590292dde1ecb5b398eb7c824839425642d6cb013f20dfd67e7294f6a3a7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "ae677f2af1b2eeb86529c9f58795495fc1292fa03898b6c27a0238cc0d9df487"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "d4dd8379bed1c7ead2e1823b6d840f63116331ecac68bde5e5d949d20a62efab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "774071905f13623890360e71b932fa6018f714c8e960696902dd82d815c56d17"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "5b53b626984338449402b2cff29e5de47118f84925d6f0e7c3acb25d841d9bac"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3ad64585ebd623659647c86343fb2c3a67a8abcbb149d6330076d7f65ebc2c33"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fbb723f947479ff4bc85a380e8d03868843e9d915fa195522c1123133944cd1b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "d246fb12f69180726adc9b18d00eee7c5c16f9bc9cd05944a9e1514420b1d251"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "82ffb47c67b5d59f3827598210003985afe288fa0bb6d4a674d929812f66c218"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "8015c870ad4d3fb197b8ed140e5bdbfd3f7779fcea07f9491a78f6a4f979df16"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f830be77e3f72131fd368f713cd5ba24bb18bb685cfb5424703be24b79f14ea2",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "85f2d626fe0728e4f24a8471fd325cf48590889d8f31fceecf42599539bff7ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "f4b7abdb8d2442513de5691e82787365d4010be7961664bd6693ae08befabd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "99a192a428458105fb40a98049f80638e12deb5f48cee3961a2b93920e086617"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "013f5cf35c61796bd9160b65580daf0c2db5950646e9cd650b078fea05cda065"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "113198c969adc46ae00c7870b4827e919ac2d22b7f7236822e0319de82f93dde"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "c93e9d5e5c1a2116dba1602dc14ae29862849bb14573ce125508cec212abb103"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "0e6d5b58695652438712a319b0d8f50377144fa9f00aed7dd7a7ff28b19d7dbc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "2ace57e0772a079483309452020fb09cba21887f860f97622ceb8b5751b81dff"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "81d6d943fe9d5cd9d3fa062893a5b24c5ce830619737427cdde1ec7dd2fd31af"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "e3cc2445917d5c788f424487949b5ad7cd6adbd015ccf3c764f85cd2b823c9ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "fd0f02a874dd9893caa2cb234e353fa3ec5c44a09ca618452fdd50e0873108a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "1e00d0c46041fcf5d023c8c3cc3f29cda7ad4b80e8ac3e6288c87dff6ae13195"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "def771ab7abb15d4f8dda741e0f122a6ba34cd1c83799fa57488fd20e1f1312a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "e02b86ed8ec39dc40bd6cdf0a9258f0a057211e46aa8e2a92524821c8d5e877e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "de3a04e84f1756cc07b586194ad1b19731d5fe4adce8db4c73eced3405cd1977"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "850a3cc7e4d77c7ee693f5bee94098d78fdb2fb00607a557ab6d3d35ca2ab851"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "1a68c883a84f0e08442a5ffbf147824a4512efaa314ead2ee5d26cba1542311e",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "2006044943c124b8aa17b3cc2c69d633434c66b4d54e999004b7a7a61f2b2f56"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "c84bb7e7e04a6cab45811148e29ab241908b4f0fde9b38548f22778cc5e86e6f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "1ce0098440765769980aedcf22eea71ca59e5e0beb63ef07b00228f7f7a7fe25"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "44150e36c1224c180bdbb3dfc20382a6e59ed1b328e91579c56362436a591a00"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "c6c2760a11e553aa0a0ddefb66299493f2d4ed5bc249ea9fb7246fae104312ad"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "893bfe7b6f9694d12d9daad1ffd17a96bdcc2440dd21dae66656ed15b7e15e67"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "7017290069cd0d4390830739b6bea8e131d18cfda5f92a7b574b3c592d5f50e1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "ace2d4fb20ac23e26ca426152f507ba7bd511c52d31d030439392a70f2159429"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "ec9008c1ce945999916de5ce7fafca0e1e4b7e866838932eb069e55f85f77ee7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "a8731f1d44d1c55e309048156f7694bc1b1c14f4f7816dadc0c19c1a16b53616"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "be359fe95a1275a648eb31724f47ccaa581b6a019f828f62b1c47be9be5dc612"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "16bd411e3ee55397c8244b79be7083587a38a1b0e1e326ab466b732f87cafa52"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "2a79b4a6501ef52b8186ebb0e9a718d53f150b6c0991e9705f0c9a4e974d97c1",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "4d0bdbee23e2bff1eb2a3d7581eaa25e4be28916a635d552d6ae3ce7eb53fc72"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "ba0c5d34562bc3805739d60905f0e1e8125b8287f81dba8fac6b65f0699e8266"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "697542590d2ffbe526948106f9a00c17f131df530a05017602aa705bc15faab8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "7f9a69d1646f89a2577cc1641155fba1c106cb76cf69586615d871d8b9b5611a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "8dcaf1f60fd4ab2b22798f49e9edca0a9a0320de87e8d52d89e75f38133ef554"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "65cb1e8426a81079cafa2ea5c53d1d74a825ea578abca611623139ce9213fa3d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "8793912f4b5c53dac2896586711a58e4405fd64d1f9c537545e3f29af5d2bdcb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "81bdf76398323b4a8ecf7444e06ce90881809d83caa476e36af8486a60f1068c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "58fec23f57c0ae6968f7d2ba90ea3b8c10e2abe383861d186f381f36f3db1f9e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "602b9edbeb97ee10c6c400c0089877803091724a0cdcc8aedfc9b4fae09efbd8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "cece245d60ddf1cb6705edda55d24404c22d5e21bbd734cfa3e125c4a620a167"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d95f8484809272ffe78deba80f32795f617f62d412dbd75c6456a94e5ab08254"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "68edf4824734005ac066bbfc5641f3e1a1de318d1a4db8d0874d30c750af2be8"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61b9c2df074518276bd3d99a8c9acadb133c4afea4f258debe4db8e3ced6a830",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "64ed3899495ebff9294340b3518eb34b72d73e3940870866807ac3958cdee332"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "fa10f800c026c3a1ff361d6110d265045b2e2b09d9ca3417716f1a5b4d83fce0"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3da61d52af39daefde08800dbec20595d14e7a7c45427feae30faecdbca978d4"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "fae1f30a10d1bc550812f344ee228a3ab362e21da161e87e47ecdac7326268ba"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "63bc2cbf4d0d9e4d0923f8f9aebd401748f17cbdf025518fa7d7536b85bde2c5"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "2583e4f16a2500e34069514018a8f2ea03fea0586a6ac598d1e292122df73a43",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "f30c3de8a18b52fbffe84cc3eeb38190285cbfc14eec690df3510ec8174bf8e8"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "a866f66b3a60a873b64f8664e230b21d2618ce37d80256e55edb58b2d1609311"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "5bba82f9177b6051a2bec4766f3818c95a3a218b6cb3f49f0f7f2ce08eabc08a"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "54120120288b40e126390f879475128a7c546dc5894244ffbab2dc41ec0bbdea"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "e3e302109075c5e71050af30fa60a9d9622ab255ff6498c436b7c2b08ab9e27c"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "876feb4157608ae15730542019e1787f95a35542f7e90339dae0471f76530717"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "badd932ef5030c719beb1cc00b0d76c54317dcaa503b1b8850bbfaa39d0a73b6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "e53554b6fa0e0c8fa01fa8e1394faf6c45176fc6a7497a9e1e26d2b0253b599e"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "301a7ea1b2514321ab751e3194dd500461ea2d3a4cc51eb96b552288e2597da2",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "232ca4156abc6eecc1c68444c6e1983abd566b30c7d808b5705f4794bd1c7edf",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c443142ddbf50fb18a4de115e8821940265fdb8eb305adaf2fd6a53e74b92e67",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "a6b81e430572ec5b290105fcd24df2e7811dbfe7e1cbcaf0d0246ef1fe4b6c9d",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5a794eb23d83d8ef0d7a5cd636119e122d8f5d946fd04ca69b1541bd06dffb1e",
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
          "stage_v_clean_e113c55_rebuild_bbf07a25933a",
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
            "stage_v_clean_e113c55_rebuild_bbf07a25933a",
            "--timeout",
            "5400"
          ],
          "duration_seconds": 20.812,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"rebuild-serving\", \"dag_run_id\": \"stage_v_clean_e113c55_rebuild_bbf07a25933a\", \"entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 90, \"iceberg_snapshot_ids\": {\"customers\": 2110013481413148761, \"order_items\": 5948428514509384907, \"order_payments\": 3389689790513587639, \"order_reviews\": 2583938958004099503, \"orders\": 8111531154139198555, \"product_category_translation\": 8401292361000666733, \"products\": 6511797434303314151, \"sellers\": 3940700634153017490}, \"materialized_event_count\": 90, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000004\", \"sync_run_seq\": 4}\n",
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
          "duration_seconds": 1.5,
          "exit_code": 0,
          "stderr": "",
          "stdout": "b57889448024428\"}]}, \"order_items\": {\"manifest_sha256\": \"e61f13501d7d8d1e775be282615a521f628c487cc8d540c22908f4a80e4de93b\", \"row_count\": 18, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"order_item_id\": 1, \"row_hash\": \"1bc0c002d676f3311cfea0d8b439ef18c4b8838a25ef73469a86aa6d481ead1f\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"order_item_id\": 1, \"row_hash\": \"1cba70c1a36d197dbd2565aa114d7167e6fc2720856d7d2d79cbf4ba638a1b68\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"order_item_id\": 1, \"row_hash\": \"ac570e4fafeddd75713c36c59f0e238a78dc7673abd7284f9de3f8d413e0d484\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"order_item_id\": 2, \"row_hash\": \"34a13c47774cdf4dc0fcfe2399e92ef24795ed26114b063d90860024c8169f3a\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"order_item_id\": 1, \"row_hash\": \"92e2358a73d0feda7de085ffbcf46bbe5faccc646ea6f8a7580a7d1f727ceeb2\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"order_item_id\": 1, \"row_hash\": \"5e8794d558c53b77db572e965c2c76b1f4b7107e0a290000cbea6b220954a7c3\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"order_item_id\": 1, \"row_hash\": \"d80b661447f72f73422ee13dc5f0d50510fae086f0fc33a018b86a0bde4c2854\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"order_item_id\": 2, \"row_hash\": \"18bef5dae4b7ea33e98cef90dba7d518d4e0c0a1bfa5d386c9bc49699b98bb48\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"order_item_id\": 1, \"row_hash\": \"9c86590292dde1ecb5b398eb7c824839425642d6cb013f20dfd67e7294f6a3a7\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"order_item_id\": 1, \"row_hash\": \"ae677f2af1b2eeb86529c9f58795495fc1292fa03898b6c27a0238cc0d9df487\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"order_item_id\": 1, \"row_hash\": \"d4dd8379bed1c7ead2e1823b6d840f63116331ecac68bde5e5d949d20a62efab\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"order_item_id\": 2, \"row_hash\": \"774071905f13623890360e71b932fa6018f714c8e960696902dd82d815c56d17\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"order_item_id\": 1, \"row_hash\": \"5b53b626984338449402b2cff29e5de47118f84925d6f0e7c3acb25d841d9bac\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"order_item_id\": 1, \"row_hash\": \"3ad64585ebd623659647c86343fb2c3a67a8abcbb149d6330076d7f65ebc2c33\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"order_item_id\": 1, \"row_hash\": \"fbb723f947479ff4bc85a380e8d03868843e9d915fa195522c1123133944cd1b\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"order_item_id\": 2, \"row_hash\": \"d246fb12f69180726adc9b18d00eee7c5c16f9bc9cd05944a9e1514420b1d251\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"order_item_id\": 1, \"row_hash\": \"82ffb47c67b5d59f3827598210003985afe288fa0bb6d4a674d929812f66c218\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"order_item_id\": 2, \"row_hash\": \"8015c870ad4d3fb197b8ed140e5bdbfd3f7779fcea07f9491a78f6a4f979df16\"}]}, \"order_payments\": {\"manifest_sha256\": \"f830be77e3f72131fd368f713cd5ba24bb18bb685cfb5424703be24b79f14ea2\", \"row_count\": 16, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"payment_sequential\": 1, \"row_hash\": \"85f2d626fe0728e4f24a8471fd325cf48590889d8f31fceecf42599539bff7ae\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"payment_sequential\": 1, \"row_hash\": \"f4b7abdb8d2442513de5691e82787365d4010be7961664bd6693ae08befabd87\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"payment_sequential\": 1, \"row_hash\": \"99a192a428458105fb40a98049f80638e12deb5f48cee3961a2b93920e086617\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"payment_sequential\": 1, \"row_hash\": \"013f5cf35c61796bd9160b65580daf0c2db5950646e9cd650b078fea05cda065\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"payment_sequential\": 2, \"row_hash\": \"113198c969adc46ae00c7870b4827e919ac2d22b7f7236822e0319de82f93dde\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"payment_sequential\": 1, \"row_hash\": \"c93e9d5e5c1a2116dba1602dc14ae29862849bb14573ce125508cec212abb103\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"payment_sequential\": 1, \"row_hash\": \"0e6d5b58695652438712a319b0d8f50377144fa9f00aed7dd7a7ff28b19d7dbc\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"payment_sequential\": 1, \"row_hash\": \"2ace57e0772a079483309452020fb09cba21887f860f97622ceb8b5751b81dff\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"payment_sequential\": 1, \"row_hash\": \"81d6d943fe9d5cd9d3fa062893a5b24c5ce830619737427cdde1ec7dd2fd31af\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"payment_sequential\": 2, \"row_hash\": \"e3cc2445917d5c788f424487949b5ad7cd6adbd015ccf3c764f85cd2b823c9ae\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"payment_sequential\": 1, \"row_hash\": \"fd0f02a874dd9893caa2cb234e353fa3ec5c44a09ca618452fdd50e0873108a0\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"payment_sequential\": 1, \"row_hash\": \"1e00d0c46041fcf5d023c8c3cc3f29cda7ad4b80e8ac3e6288c87dff6ae13195\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"payment_sequential\": 1, \"row_hash\": \"def771ab7abb15d4f8dda741e0f122a6ba34cd1c83799fa57488fd20e1f1312a\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"payment_sequential\": 1, \"row_hash\": \"e02b86ed8ec39dc40bd6cdf0a9258f0a057211e46aa8e2a92524821c8d5e877e\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"payment_sequential\": 1, \"row_hash\": \"de3a04e84f1756cc07b586194ad1b19731d5fe4adce8db4c73eced3405cd1977\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"payment_sequential\": 2, \"row_hash\": \"850a3cc7e4d77c7ee693f5bee94098d78fdb2fb00607a557ab6d3d35ca2ab851\"}]}, \"order_reviews\": {\"manifest_sha256\": \"1a68c883a84f0e08442a5ffbf147824a4512efaa314ead2ee5d26cba1542311e\", \"row_count\": 12, \"rows\": [{\"is_deleted\": false, \"review_id\": \"review_001\", \"row_hash\": \"2006044943c124b8aa17b3cc2c69d633434c66b4d54e999004b7a7a61f2b2f56\"}, {\"is_deleted\": false, \"review_id\": \"review_002\", \"row_hash\": \"c84bb7e7e04a6cab45811148e29ab241908b4f0fde9b38548f22778cc5e86e6f\"}, {\"is_deleted\": false, \"review_id\": \"review_003\", \"row_hash\": \"1ce0098440765769980aedcf22eea71ca59e5e0beb63ef07b00228f7f7a7fe25\"}, {\"is_deleted\": false, \"review_id\": \"review_004\", \"row_hash\": \"44150e36c1224c180bdbb3dfc20382a6e59ed1b328e91579c56362436a591a00\"}, {\"is_deleted\": false, \"review_id\": \"review_005\", \"row_hash\": \"c6c2760a11e553aa0a0ddefb66299493f2d4ed5bc249ea9fb7246fae104312ad\"}, {\"is_deleted\": false, \"review_id\": \"review_006\", \"row_hash\": \"893bfe7b6f9694d12d9daad1ffd17a96bdcc2440dd21dae66656ed15b7e15e67\"}, {\"is_deleted\": false, \"review_id\": \"review_007\", \"row_hash\": \"7017290069cd0d4390830739b6bea8e131d18cfda5f92a7b574b3c592d5f50e1\"}, {\"is_deleted\": false, \"review_id\": \"review_008\", \"row_hash\": \"ace2d4fb20ac23e26ca426152f507ba7bd511c52d31d030439392a70f2159429\"}, {\"is_deleted\": false, \"review_id\": \"review_009\", \"row_hash\": \"ec9008c1ce945999916de5ce7fafca0e1e4b7e866838932eb069e55f85f77ee7\"}, {\"is_deleted\": false, \"review_id\": \"review_010\", \"row_hash\": \"a8731f1d44d1c55e309048156f7694bc1b1c14f4f7816dadc0c19c1a16b53616\"}, {\"is_deleted\": false, \"review_id\": \"review_011\", \"row_hash\": \"be359fe95a1275a648eb31724f47ccaa581b6a019f828f62b1c47be9be5dc612\"}, {\"is_deleted\": false, \"review_id\": \"review_012\", \"row_hash\": \"16bd411e3ee55397c8244b79be7083587a38a1b0e1e326ab466b732f87cafa52\"}]}, \"orders\": {\"manifest_sha256\": \"2a79b4a6501ef52b8186ebb0e9a718d53f150b6c0991e9705f0c9a4e974d97c1\", \"row_count\": 13, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"row_hash\": \"4d0bdbee23e2bff1eb2a3d7581eaa25e4be28916a635d552d6ae3ce7eb53fc72\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"row_hash\": \"ba0c5d34562bc3805739d60905f0e1e8125b8287f81dba8fac6b65f0699e8266\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"row_hash\": \"697542590d2ffbe526948106f9a00c17f131df530a05017602aa705bc15faab8\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"row_hash\": \"7f9a69d1646f89a2577cc1641155fba1c106cb76cf69586615d871d8b9b5611a\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"row_hash\": \"8dcaf1f60fd4ab2b22798f49e9edca0a9a0320de87e8d52d89e75f38133ef554\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"row_hash\": \"65cb1e8426a81079cafa2ea5c53d1d74a825ea578abca611623139ce9213fa3d\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"row_hash\": \"8793912f4b5c53dac2896586711a58e4405fd64d1f9c537545e3f29af5d2bdcb\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"row_hash\": \"81bdf76398323b4a8ecf7444e06ce90881809d83caa476e36af8486a60f1068c\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"row_hash\": \"58fec23f57c0ae6968f7d2ba90ea3b8c10e2abe383861d186f381f36f3db1f9e\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"row_hash\": \"602b9edbeb97ee10c6c400c0089877803091724a0cdcc8aedfc9b4fae09efbd8\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"row_hash\": \"cece245d60ddf1cb6705edda55d24404c22d5e21bbd734cfa3e125c4a620a167\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"row_hash\": \"d95f8484809272ffe78deba80f32795f617f62d412dbd75c6456a94e5ab08254\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"row_hash\": \"68edf4824734005ac066bbfc5641f3e1a1de318d1a4db8d0874d30c750af2be8\"}]}, \"product_category_translation\": {\"manifest_sha256\": \"61b9c2df074518276bd3d99a8c9acadb133c4afea4f258debe4db8e3ced6a830\", \"row_count\": 5, \"rows\": [{\"is_deleted\": false, \"product_category_name\": \"beleza_saude\", \"row_hash\": \"64ed3899495ebff9294340b3518eb34b72d73e3940870866807ac3958cdee332\"}, {\"is_deleted\": false, \"product_category_name\": \"informatica_acessorios\", \"row_hash\": \"fa10f800c026c3a1ff361d6110d265045b2e2b09d9ca3417716f1a5b4d83fce0\"}, {\"is_deleted\": false, \"product_category_name\": \"moveis_decoracao\", \"row_hash\": \"3da61d52af39daefde08800dbec20595d14e7a7c45427feae30faecdbca978d4\"}, {\"is_deleted\": false, \"product_category_name\": \"telefonia\", \"row_hash\": \"fae1f30a10d1bc550812f344ee228a3ab362e21da161e87e47ecdac7326268ba\"}, {\"is_deleted\": false, \"product_category_name\": \"utilidades_domesticas\", \"row_hash\": \"63bc2cbf4d0d9e4d0923f8f9aebd401748f17cbdf025518fa7d7536b85bde2c5\"}]}, \"products\": {\"manifest_sha256\": \"2583e4f16a2500e34069514018a8f2ea03fea0586a6ac598d1e292122df73a43\", \"row_count\": 8, \"rows\": [{\"is_deleted\": false, \"product_id\": \"product_001\", \"row_hash\": \"f30c3de8a18b52fbffe84cc3eeb38190285cbfc14eec690df3510ec8174bf8e8\"}, {\"is_deleted\": false, \"product_id\": \"product_002\", \"row_hash\": \"a866f66b3a60a873b64f8664e230b21d2618ce37d80256e55edb58b2d1609311\"}, {\"is_deleted\": false, \"product_id\": \"product_003\", \"row_hash\": \"5bba82f9177b6051a2bec4766f3818c95a3a218b6cb3f49f0f7f2ce08eabc08a\"}, {\"is_deleted\": false, \"product_id\": \"product_004\", \"row_hash\": \"54120120288b40e126390f879475128a7c546dc5894244ffbab2dc41ec0bbdea\"}, {\"is_deleted\": false, \"product_id\": \"product_005\", \"row_hash\": \"e3e302109075c5e71050af30fa60a9d9622ab255ff6498c436b7c2b08ab9e27c\"}, {\"is_deleted\": false, \"product_id\": \"product_006\", \"row_hash\": \"876feb4157608ae15730542019e1787f95a35542f7e90339dae0471f76530717\"}, {\"is_deleted\": false, \"product_id\": \"product_007\", \"row_hash\": \"badd932ef5030c719beb1cc00b0d76c54317dcaa503b1b8850bbfaa39d0a73b6\"}, {\"is_deleted\": false, \"product_id\": \"product_008\", \"row_hash\": \"e53554b6fa0e0c8fa01fa8e1394faf6c45176fc6a7497a9e1e26d2b0253b599e\"}]}, \"sellers\": {\"manifest_sha256\": \"301a7ea1b2514321ab751e3194dd500461ea2d3a4cc51eb96b552288e2597da2\", \"row_count\": 4, \"rows\": [{\"is_deleted\": false, \"row_hash\": \"232ca4156abc6eecc1c68444c6e1983abd566b30c7d808b5705f4794bd1c7edf\", \"seller_id\": \"seller_001\"}, {\"is_deleted\": false, \"row_hash\": \"c443142ddbf50fb18a4de115e8821940265fdb8eb305adaf2fd6a53e74b92e67\", \"seller_id\": \"seller_002\"}, {\"is_deleted\": false, \"row_hash\": \"a6b81e430572ec5b290105fcd24df2e7811dbfe7e1cbcaf0d0246ef1fe4b6c9d\", \"seller_id\": \"seller_003\"}, {\"is_deleted\": false, \"row_hash\": \"5a794eb23d83d8ef0d7a5cd636119e122d8f5d946fd04ca69b1541bd06dffb1e\", \"seller_id\": \"seller_004\"}]}}}, \"runtime\": {\"last_published_sync_run_seq\": 4, \"lease_owner_id\": null, \"source_snapshot_completed\": true}, \"stable_current_counts\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"status\": \"ready\", \"sync_run_id\": \"sync-00000000000000000004\", \"sync_run_seq\": 4}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 22.309,
      "gate": "09-rebuild",
      "status": "PASS",
      "timestamp": "2026-08-03T19:13:17.937117+00:00"
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
              "customers": 2110013481413148761,
              "order_items": 5948428514509384907,
              "order_payments": 3389689790513587639,
              "order_reviews": 2583938958004099503,
              "orders": 8111531154139198555,
              "product_category_translation": 8401292361000666733,
              "products": 6511797434303314151,
              "sellers": 3940700634153017490
            },
            "materialized_event_count": 90,
            "row_manifests": {
              "candidate_physical": {
                "customers": {
                  "manifest_sha256": "2163b64da4630010afb36a5a1d647f7f9061dd27721750be5d4343756f68f509",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "6504201ef8e7783b67bcd3c6cdc25343a6fd7e3ba5d05c20f586e5066addd019"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "1af1f9b6f8bee67ec321c0c76a6fd7747dcd16efd15541c145fc45dc04671aaf"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "58e95e7e89fdf89a9219ae3c4784a078cabf33ce1bd3cdb9a24ba78515d0cfcc"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "1347812f4872f7ec8a5d1d1de1e6f5e728f5197826f19f2044b83426400d8b04"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "4d37ae8594d7c6a23ef1a2da18c51ff718860cc0e86cd8df9fe1b7fd386c1492"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "28095779e50db90fb650a166495817f630c58b4d9cfd86b7cbb23afd9de6ab9b"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "cd2331d56a106934ebf661221b1e11246cc7f037086902c7c348a4011f1f6ae9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "c237aab742403af52fcd2448e403a9a4bde89f4c3e13e708b99a994b7678cb77"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "b137c7cc3317992c2b86690f77bed9476bd93d2bfa2e8cc7db57889448024428"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "e61f13501d7d8d1e775be282615a521f628c487cc8d540c22908f4a80e4de93b",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1bc0c002d676f3311cfea0d8b439ef18c4b8838a25ef73469a86aa6d481ead1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "1cba70c1a36d197dbd2565aa114d7167e6fc2720856d7d2d79cbf4ba638a1b68"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "ac570e4fafeddd75713c36c59f0e238a78dc7673abd7284f9de3f8d413e0d484"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "34a13c47774cdf4dc0fcfe2399e92ef24795ed26114b063d90860024c8169f3a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "92e2358a73d0feda7de085ffbcf46bbe5faccc646ea6f8a7580a7d1f727ceeb2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "5e8794d558c53b77db572e965c2c76b1f4b7107e0a290000cbea6b220954a7c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "d80b661447f72f73422ee13dc5f0d50510fae086f0fc33a018b86a0bde4c2854"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "18bef5dae4b7ea33e98cef90dba7d518d4e0c0a1bfa5d386c9bc49699b98bb48"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "9c86590292dde1ecb5b398eb7c824839425642d6cb013f20dfd67e7294f6a3a7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "ae677f2af1b2eeb86529c9f58795495fc1292fa03898b6c27a0238cc0d9df487"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "d4dd8379bed1c7ead2e1823b6d840f63116331ecac68bde5e5d949d20a62efab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "774071905f13623890360e71b932fa6018f714c8e960696902dd82d815c56d17"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "5b53b626984338449402b2cff29e5de47118f84925d6f0e7c3acb25d841d9bac"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3ad64585ebd623659647c86343fb2c3a67a8abcbb149d6330076d7f65ebc2c33"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fbb723f947479ff4bc85a380e8d03868843e9d915fa195522c1123133944cd1b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "d246fb12f69180726adc9b18d00eee7c5c16f9bc9cd05944a9e1514420b1d251"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "82ffb47c67b5d59f3827598210003985afe288fa0bb6d4a674d929812f66c218"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "8015c870ad4d3fb197b8ed140e5bdbfd3f7779fcea07f9491a78f6a4f979df16"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f830be77e3f72131fd368f713cd5ba24bb18bb685cfb5424703be24b79f14ea2",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "85f2d626fe0728e4f24a8471fd325cf48590889d8f31fceecf42599539bff7ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "f4b7abdb8d2442513de5691e82787365d4010be7961664bd6693ae08befabd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "99a192a428458105fb40a98049f80638e12deb5f48cee3961a2b93920e086617"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "013f5cf35c61796bd9160b65580daf0c2db5950646e9cd650b078fea05cda065"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "113198c969adc46ae00c7870b4827e919ac2d22b7f7236822e0319de82f93dde"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "c93e9d5e5c1a2116dba1602dc14ae29862849bb14573ce125508cec212abb103"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "0e6d5b58695652438712a319b0d8f50377144fa9f00aed7dd7a7ff28b19d7dbc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "2ace57e0772a079483309452020fb09cba21887f860f97622ceb8b5751b81dff"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "81d6d943fe9d5cd9d3fa062893a5b24c5ce830619737427cdde1ec7dd2fd31af"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "e3cc2445917d5c788f424487949b5ad7cd6adbd015ccf3c764f85cd2b823c9ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "fd0f02a874dd9893caa2cb234e353fa3ec5c44a09ca618452fdd50e0873108a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "1e00d0c46041fcf5d023c8c3cc3f29cda7ad4b80e8ac3e6288c87dff6ae13195"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "def771ab7abb15d4f8dda741e0f122a6ba34cd1c83799fa57488fd20e1f1312a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "e02b86ed8ec39dc40bd6cdf0a9258f0a057211e46aa8e2a92524821c8d5e877e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "de3a04e84f1756cc07b586194ad1b19731d5fe4adce8db4c73eced3405cd1977"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "850a3cc7e4d77c7ee693f5bee94098d78fdb2fb00607a557ab6d3d35ca2ab851"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "584689f836ec7c27688a8e040062b6453f969e004cd946b6018186d43f055242",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "2006044943c124b8aa17b3cc2c69d633434c66b4d54e999004b7a7a61f2b2f56"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "c84bb7e7e04a6cab45811148e29ab241908b4f0fde9b38548f22778cc5e86e6f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "1ce0098440765769980aedcf22eea71ca59e5e0beb63ef07b00228f7f7a7fe25"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "44150e36c1224c180bdbb3dfc20382a6e59ed1b328e91579c56362436a591a00"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "c6c2760a11e553aa0a0ddefb66299493f2d4ed5bc249ea9fb7246fae104312ad"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "893bfe7b6f9694d12d9daad1ffd17a96bdcc2440dd21dae66656ed15b7e15e67"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "7017290069cd0d4390830739b6bea8e131d18cfda5f92a7b574b3c592d5f50e1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "ace2d4fb20ac23e26ca426152f507ba7bd511c52d31d030439392a70f2159429"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "ec9008c1ce945999916de5ce7fafca0e1e4b7e866838932eb069e55f85f77ee7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "a8731f1d44d1c55e309048156f7694bc1b1c14f4f7816dadc0c19c1a16b53616"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "be359fe95a1275a648eb31724f47ccaa581b6a019f828f62b1c47be9be5dc612"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "16bd411e3ee55397c8244b79be7083587a38a1b0e1e326ab466b732f87cafa52"
                    },
                    {
                      "is_deleted": true,
                      "review_id": "wave2_review_001",
                      "row_hash": "44f322e87cfd6880ce4fccfc29daf4fda32b62a4bd96a936f77494c04d14f25a"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "2a79b4a6501ef52b8186ebb0e9a718d53f150b6c0991e9705f0c9a4e974d97c1",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "4d0bdbee23e2bff1eb2a3d7581eaa25e4be28916a635d552d6ae3ce7eb53fc72"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "ba0c5d34562bc3805739d60905f0e1e8125b8287f81dba8fac6b65f0699e8266"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "697542590d2ffbe526948106f9a00c17f131df530a05017602aa705bc15faab8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "7f9a69d1646f89a2577cc1641155fba1c106cb76cf69586615d871d8b9b5611a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "8dcaf1f60fd4ab2b22798f49e9edca0a9a0320de87e8d52d89e75f38133ef554"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "65cb1e8426a81079cafa2ea5c53d1d74a825ea578abca611623139ce9213fa3d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "8793912f4b5c53dac2896586711a58e4405fd64d1f9c537545e3f29af5d2bdcb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "81bdf76398323b4a8ecf7444e06ce90881809d83caa476e36af8486a60f1068c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "58fec23f57c0ae6968f7d2ba90ea3b8c10e2abe383861d186f381f36f3db1f9e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "602b9edbeb97ee10c6c400c0089877803091724a0cdcc8aedfc9b4fae09efbd8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "cece245d60ddf1cb6705edda55d24404c22d5e21bbd734cfa3e125c4a620a167"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d95f8484809272ffe78deba80f32795f617f62d412dbd75c6456a94e5ab08254"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "68edf4824734005ac066bbfc5641f3e1a1de318d1a4db8d0874d30c750af2be8"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61b9c2df074518276bd3d99a8c9acadb133c4afea4f258debe4db8e3ced6a830",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "64ed3899495ebff9294340b3518eb34b72d73e3940870866807ac3958cdee332"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "fa10f800c026c3a1ff361d6110d265045b2e2b09d9ca3417716f1a5b4d83fce0"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3da61d52af39daefde08800dbec20595d14e7a7c45427feae30faecdbca978d4"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "fae1f30a10d1bc550812f344ee228a3ab362e21da161e87e47ecdac7326268ba"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "63bc2cbf4d0d9e4d0923f8f9aebd401748f17cbdf025518fa7d7536b85bde2c5"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "2583e4f16a2500e34069514018a8f2ea03fea0586a6ac598d1e292122df73a43",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "f30c3de8a18b52fbffe84cc3eeb38190285cbfc14eec690df3510ec8174bf8e8"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "a866f66b3a60a873b64f8664e230b21d2618ce37d80256e55edb58b2d1609311"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "5bba82f9177b6051a2bec4766f3818c95a3a218b6cb3f49f0f7f2ce08eabc08a"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "54120120288b40e126390f879475128a7c546dc5894244ffbab2dc41ec0bbdea"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "e3e302109075c5e71050af30fa60a9d9622ab255ff6498c436b7c2b08ab9e27c"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "876feb4157608ae15730542019e1787f95a35542f7e90339dae0471f76530717"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "badd932ef5030c719beb1cc00b0d76c54317dcaa503b1b8850bbfaa39d0a73b6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "e53554b6fa0e0c8fa01fa8e1394faf6c45176fc6a7497a9e1e26d2b0253b599e"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "301a7ea1b2514321ab751e3194dd500461ea2d3a4cc51eb96b552288e2597da2",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "232ca4156abc6eecc1c68444c6e1983abd566b30c7d808b5705f4794bd1c7edf",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c443142ddbf50fb18a4de115e8821940265fdb8eb305adaf2fd6a53e74b92e67",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "a6b81e430572ec5b290105fcd24df2e7811dbfe7e1cbcaf0d0246ef1fe4b6c9d",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5a794eb23d83d8ef0d7a5cd636119e122d8f5d946fd04ca69b1541bd06dffb1e",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "candidate_visible": {
                "customers": {
                  "manifest_sha256": "2163b64da4630010afb36a5a1d647f7f9061dd27721750be5d4343756f68f509",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "6504201ef8e7783b67bcd3c6cdc25343a6fd7e3ba5d05c20f586e5066addd019"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "1af1f9b6f8bee67ec321c0c76a6fd7747dcd16efd15541c145fc45dc04671aaf"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "58e95e7e89fdf89a9219ae3c4784a078cabf33ce1bd3cdb9a24ba78515d0cfcc"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "1347812f4872f7ec8a5d1d1de1e6f5e728f5197826f19f2044b83426400d8b04"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "4d37ae8594d7c6a23ef1a2da18c51ff718860cc0e86cd8df9fe1b7fd386c1492"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "28095779e50db90fb650a166495817f630c58b4d9cfd86b7cbb23afd9de6ab9b"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "cd2331d56a106934ebf661221b1e11246cc7f037086902c7c348a4011f1f6ae9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "c237aab742403af52fcd2448e403a9a4bde89f4c3e13e708b99a994b7678cb77"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "b137c7cc3317992c2b86690f77bed9476bd93d2bfa2e8cc7db57889448024428"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "e61f13501d7d8d1e775be282615a521f628c487cc8d540c22908f4a80e4de93b",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1bc0c002d676f3311cfea0d8b439ef18c4b8838a25ef73469a86aa6d481ead1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "1cba70c1a36d197dbd2565aa114d7167e6fc2720856d7d2d79cbf4ba638a1b68"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "ac570e4fafeddd75713c36c59f0e238a78dc7673abd7284f9de3f8d413e0d484"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "34a13c47774cdf4dc0fcfe2399e92ef24795ed26114b063d90860024c8169f3a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "92e2358a73d0feda7de085ffbcf46bbe5faccc646ea6f8a7580a7d1f727ceeb2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "5e8794d558c53b77db572e965c2c76b1f4b7107e0a290000cbea6b220954a7c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "d80b661447f72f73422ee13dc5f0d50510fae086f0fc33a018b86a0bde4c2854"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "18bef5dae4b7ea33e98cef90dba7d518d4e0c0a1bfa5d386c9bc49699b98bb48"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "9c86590292dde1ecb5b398eb7c824839425642d6cb013f20dfd67e7294f6a3a7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "ae677f2af1b2eeb86529c9f58795495fc1292fa03898b6c27a0238cc0d9df487"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "d4dd8379bed1c7ead2e1823b6d840f63116331ecac68bde5e5d949d20a62efab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "774071905f13623890360e71b932fa6018f714c8e960696902dd82d815c56d17"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "5b53b626984338449402b2cff29e5de47118f84925d6f0e7c3acb25d841d9bac"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3ad64585ebd623659647c86343fb2c3a67a8abcbb149d6330076d7f65ebc2c33"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fbb723f947479ff4bc85a380e8d03868843e9d915fa195522c1123133944cd1b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "d246fb12f69180726adc9b18d00eee7c5c16f9bc9cd05944a9e1514420b1d251"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "82ffb47c67b5d59f3827598210003985afe288fa0bb6d4a674d929812f66c218"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "8015c870ad4d3fb197b8ed140e5bdbfd3f7779fcea07f9491a78f6a4f979df16"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f830be77e3f72131fd368f713cd5ba24bb18bb685cfb5424703be24b79f14ea2",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "85f2d626fe0728e4f24a8471fd325cf48590889d8f31fceecf42599539bff7ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "f4b7abdb8d2442513de5691e82787365d4010be7961664bd6693ae08befabd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "99a192a428458105fb40a98049f80638e12deb5f48cee3961a2b93920e086617"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "013f5cf35c61796bd9160b65580daf0c2db5950646e9cd650b078fea05cda065"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "113198c969adc46ae00c7870b4827e919ac2d22b7f7236822e0319de82f93dde"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "c93e9d5e5c1a2116dba1602dc14ae29862849bb14573ce125508cec212abb103"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "0e6d5b58695652438712a319b0d8f50377144fa9f00aed7dd7a7ff28b19d7dbc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "2ace57e0772a079483309452020fb09cba21887f860f97622ceb8b5751b81dff"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "81d6d943fe9d5cd9d3fa062893a5b24c5ce830619737427cdde1ec7dd2fd31af"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "e3cc2445917d5c788f424487949b5ad7cd6adbd015ccf3c764f85cd2b823c9ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "fd0f02a874dd9893caa2cb234e353fa3ec5c44a09ca618452fdd50e0873108a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "1e00d0c46041fcf5d023c8c3cc3f29cda7ad4b80e8ac3e6288c87dff6ae13195"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "def771ab7abb15d4f8dda741e0f122a6ba34cd1c83799fa57488fd20e1f1312a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "e02b86ed8ec39dc40bd6cdf0a9258f0a057211e46aa8e2a92524821c8d5e877e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "de3a04e84f1756cc07b586194ad1b19731d5fe4adce8db4c73eced3405cd1977"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "850a3cc7e4d77c7ee693f5bee94098d78fdb2fb00607a557ab6d3d35ca2ab851"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "1a68c883a84f0e08442a5ffbf147824a4512efaa314ead2ee5d26cba1542311e",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "2006044943c124b8aa17b3cc2c69d633434c66b4d54e999004b7a7a61f2b2f56"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "c84bb7e7e04a6cab45811148e29ab241908b4f0fde9b38548f22778cc5e86e6f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "1ce0098440765769980aedcf22eea71ca59e5e0beb63ef07b00228f7f7a7fe25"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "44150e36c1224c180bdbb3dfc20382a6e59ed1b328e91579c56362436a591a00"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "c6c2760a11e553aa0a0ddefb66299493f2d4ed5bc249ea9fb7246fae104312ad"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "893bfe7b6f9694d12d9daad1ffd17a96bdcc2440dd21dae66656ed15b7e15e67"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "7017290069cd0d4390830739b6bea8e131d18cfda5f92a7b574b3c592d5f50e1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "ace2d4fb20ac23e26ca426152f507ba7bd511c52d31d030439392a70f2159429"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "ec9008c1ce945999916de5ce7fafca0e1e4b7e866838932eb069e55f85f77ee7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "a8731f1d44d1c55e309048156f7694bc1b1c14f4f7816dadc0c19c1a16b53616"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "be359fe95a1275a648eb31724f47ccaa581b6a019f828f62b1c47be9be5dc612"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "16bd411e3ee55397c8244b79be7083587a38a1b0e1e326ab466b732f87cafa52"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "2a79b4a6501ef52b8186ebb0e9a718d53f150b6c0991e9705f0c9a4e974d97c1",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "4d0bdbee23e2bff1eb2a3d7581eaa25e4be28916a635d552d6ae3ce7eb53fc72"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "ba0c5d34562bc3805739d60905f0e1e8125b8287f81dba8fac6b65f0699e8266"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "697542590d2ffbe526948106f9a00c17f131df530a05017602aa705bc15faab8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "7f9a69d1646f89a2577cc1641155fba1c106cb76cf69586615d871d8b9b5611a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "8dcaf1f60fd4ab2b22798f49e9edca0a9a0320de87e8d52d89e75f38133ef554"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "65cb1e8426a81079cafa2ea5c53d1d74a825ea578abca611623139ce9213fa3d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "8793912f4b5c53dac2896586711a58e4405fd64d1f9c537545e3f29af5d2bdcb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "81bdf76398323b4a8ecf7444e06ce90881809d83caa476e36af8486a60f1068c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "58fec23f57c0ae6968f7d2ba90ea3b8c10e2abe383861d186f381f36f3db1f9e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "602b9edbeb97ee10c6c400c0089877803091724a0cdcc8aedfc9b4fae09efbd8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "cece245d60ddf1cb6705edda55d24404c22d5e21bbd734cfa3e125c4a620a167"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d95f8484809272ffe78deba80f32795f617f62d412dbd75c6456a94e5ab08254"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "68edf4824734005ac066bbfc5641f3e1a1de318d1a4db8d0874d30c750af2be8"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61b9c2df074518276bd3d99a8c9acadb133c4afea4f258debe4db8e3ced6a830",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "64ed3899495ebff9294340b3518eb34b72d73e3940870866807ac3958cdee332"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "fa10f800c026c3a1ff361d6110d265045b2e2b09d9ca3417716f1a5b4d83fce0"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3da61d52af39daefde08800dbec20595d14e7a7c45427feae30faecdbca978d4"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "fae1f30a10d1bc550812f344ee228a3ab362e21da161e87e47ecdac7326268ba"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "63bc2cbf4d0d9e4d0923f8f9aebd401748f17cbdf025518fa7d7536b85bde2c5"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "2583e4f16a2500e34069514018a8f2ea03fea0586a6ac598d1e292122df73a43",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "f30c3de8a18b52fbffe84cc3eeb38190285cbfc14eec690df3510ec8174bf8e8"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "a866f66b3a60a873b64f8664e230b21d2618ce37d80256e55edb58b2d1609311"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "5bba82f9177b6051a2bec4766f3818c95a3a218b6cb3f49f0f7f2ce08eabc08a"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "54120120288b40e126390f879475128a7c546dc5894244ffbab2dc41ec0bbdea"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "e3e302109075c5e71050af30fa60a9d9622ab255ff6498c436b7c2b08ab9e27c"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "876feb4157608ae15730542019e1787f95a35542f7e90339dae0471f76530717"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "badd932ef5030c719beb1cc00b0d76c54317dcaa503b1b8850bbfaa39d0a73b6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "e53554b6fa0e0c8fa01fa8e1394faf6c45176fc6a7497a9e1e26d2b0253b599e"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "301a7ea1b2514321ab751e3194dd500461ea2d3a4cc51eb96b552288e2597da2",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "232ca4156abc6eecc1c68444c6e1983abd566b30c7d808b5705f4794bd1c7edf",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c443142ddbf50fb18a4de115e8821940265fdb8eb305adaf2fd6a53e74b92e67",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "a6b81e430572ec5b290105fcd24df2e7811dbfe7e1cbcaf0d0246ef1fe4b6c9d",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5a794eb23d83d8ef0d7a5cd636119e122d8f5d946fd04ca69b1541bd06dffb1e",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "iceberg_physical": {
                "customers": {
                  "manifest_sha256": "2163b64da4630010afb36a5a1d647f7f9061dd27721750be5d4343756f68f509",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "6504201ef8e7783b67bcd3c6cdc25343a6fd7e3ba5d05c20f586e5066addd019"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "1af1f9b6f8bee67ec321c0c76a6fd7747dcd16efd15541c145fc45dc04671aaf"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "58e95e7e89fdf89a9219ae3c4784a078cabf33ce1bd3cdb9a24ba78515d0cfcc"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "1347812f4872f7ec8a5d1d1de1e6f5e728f5197826f19f2044b83426400d8b04"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "4d37ae8594d7c6a23ef1a2da18c51ff718860cc0e86cd8df9fe1b7fd386c1492"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "28095779e50db90fb650a166495817f630c58b4d9cfd86b7cbb23afd9de6ab9b"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "cd2331d56a106934ebf661221b1e11246cc7f037086902c7c348a4011f1f6ae9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "c237aab742403af52fcd2448e403a9a4bde89f4c3e13e708b99a994b7678cb77"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "b137c7cc3317992c2b86690f77bed9476bd93d2bfa2e8cc7db57889448024428"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "e61f13501d7d8d1e775be282615a521f628c487cc8d540c22908f4a80e4de93b",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1bc0c002d676f3311cfea0d8b439ef18c4b8838a25ef73469a86aa6d481ead1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "1cba70c1a36d197dbd2565aa114d7167e6fc2720856d7d2d79cbf4ba638a1b68"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "ac570e4fafeddd75713c36c59f0e238a78dc7673abd7284f9de3f8d413e0d484"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "34a13c47774cdf4dc0fcfe2399e92ef24795ed26114b063d90860024c8169f3a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "92e2358a73d0feda7de085ffbcf46bbe5faccc646ea6f8a7580a7d1f727ceeb2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "5e8794d558c53b77db572e965c2c76b1f4b7107e0a290000cbea6b220954a7c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "d80b661447f72f73422ee13dc5f0d50510fae086f0fc33a018b86a0bde4c2854"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "18bef5dae4b7ea33e98cef90dba7d518d4e0c0a1bfa5d386c9bc49699b98bb48"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "9c86590292dde1ecb5b398eb7c824839425642d6cb013f20dfd67e7294f6a3a7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "ae677f2af1b2eeb86529c9f58795495fc1292fa03898b6c27a0238cc0d9df487"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "d4dd8379bed1c7ead2e1823b6d840f63116331ecac68bde5e5d949d20a62efab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "774071905f13623890360e71b932fa6018f714c8e960696902dd82d815c56d17"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "5b53b626984338449402b2cff29e5de47118f84925d6f0e7c3acb25d841d9bac"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3ad64585ebd623659647c86343fb2c3a67a8abcbb149d6330076d7f65ebc2c33"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fbb723f947479ff4bc85a380e8d03868843e9d915fa195522c1123133944cd1b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "d246fb12f69180726adc9b18d00eee7c5c16f9bc9cd05944a9e1514420b1d251"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "82ffb47c67b5d59f3827598210003985afe288fa0bb6d4a674d929812f66c218"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "8015c870ad4d3fb197b8ed140e5bdbfd3f7779fcea07f9491a78f6a4f979df16"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f830be77e3f72131fd368f713cd5ba24bb18bb685cfb5424703be24b79f14ea2",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "85f2d626fe0728e4f24a8471fd325cf48590889d8f31fceecf42599539bff7ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "f4b7abdb8d2442513de5691e82787365d4010be7961664bd6693ae08befabd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "99a192a428458105fb40a98049f80638e12deb5f48cee3961a2b93920e086617"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "013f5cf35c61796bd9160b65580daf0c2db5950646e9cd650b078fea05cda065"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "113198c969adc46ae00c7870b4827e919ac2d22b7f7236822e0319de82f93dde"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "c93e9d5e5c1a2116dba1602dc14ae29862849bb14573ce125508cec212abb103"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "0e6d5b58695652438712a319b0d8f50377144fa9f00aed7dd7a7ff28b19d7dbc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "2ace57e0772a079483309452020fb09cba21887f860f97622ceb8b5751b81dff"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "81d6d943fe9d5cd9d3fa062893a5b24c5ce830619737427cdde1ec7dd2fd31af"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "e3cc2445917d5c788f424487949b5ad7cd6adbd015ccf3c764f85cd2b823c9ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "fd0f02a874dd9893caa2cb234e353fa3ec5c44a09ca618452fdd50e0873108a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "1e00d0c46041fcf5d023c8c3cc3f29cda7ad4b80e8ac3e6288c87dff6ae13195"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "def771ab7abb15d4f8dda741e0f122a6ba34cd1c83799fa57488fd20e1f1312a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "e02b86ed8ec39dc40bd6cdf0a9258f0a057211e46aa8e2a92524821c8d5e877e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "de3a04e84f1756cc07b586194ad1b19731d5fe4adce8db4c73eced3405cd1977"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "850a3cc7e4d77c7ee693f5bee94098d78fdb2fb00607a557ab6d3d35ca2ab851"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "584689f836ec7c27688a8e040062b6453f969e004cd946b6018186d43f055242",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "2006044943c124b8aa17b3cc2c69d633434c66b4d54e999004b7a7a61f2b2f56"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "c84bb7e7e04a6cab45811148e29ab241908b4f0fde9b38548f22778cc5e86e6f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "1ce0098440765769980aedcf22eea71ca59e5e0beb63ef07b00228f7f7a7fe25"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "44150e36c1224c180bdbb3dfc20382a6e59ed1b328e91579c56362436a591a00"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "c6c2760a11e553aa0a0ddefb66299493f2d4ed5bc249ea9fb7246fae104312ad"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "893bfe7b6f9694d12d9daad1ffd17a96bdcc2440dd21dae66656ed15b7e15e67"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "7017290069cd0d4390830739b6bea8e131d18cfda5f92a7b574b3c592d5f50e1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "ace2d4fb20ac23e26ca426152f507ba7bd511c52d31d030439392a70f2159429"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "ec9008c1ce945999916de5ce7fafca0e1e4b7e866838932eb069e55f85f77ee7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "a8731f1d44d1c55e309048156f7694bc1b1c14f4f7816dadc0c19c1a16b53616"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "be359fe95a1275a648eb31724f47ccaa581b6a019f828f62b1c47be9be5dc612"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "16bd411e3ee55397c8244b79be7083587a38a1b0e1e326ab466b732f87cafa52"
                    },
                    {
                      "is_deleted": true,
                      "review_id": "wave2_review_001",
                      "row_hash": "44f322e87cfd6880ce4fccfc29daf4fda32b62a4bd96a936f77494c04d14f25a"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "2a79b4a6501ef52b8186ebb0e9a718d53f150b6c0991e9705f0c9a4e974d97c1",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "4d0bdbee23e2bff1eb2a3d7581eaa25e4be28916a635d552d6ae3ce7eb53fc72"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "ba0c5d34562bc3805739d60905f0e1e8125b8287f81dba8fac6b65f0699e8266"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "697542590d2ffbe526948106f9a00c17f131df530a05017602aa705bc15faab8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "7f9a69d1646f89a2577cc1641155fba1c106cb76cf69586615d871d8b9b5611a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "8dcaf1f60fd4ab2b22798f49e9edca0a9a0320de87e8d52d89e75f38133ef554"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "65cb1e8426a81079cafa2ea5c53d1d74a825ea578abca611623139ce9213fa3d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "8793912f4b5c53dac2896586711a58e4405fd64d1f9c537545e3f29af5d2bdcb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "81bdf76398323b4a8ecf7444e06ce90881809d83caa476e36af8486a60f1068c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "58fec23f57c0ae6968f7d2ba90ea3b8c10e2abe383861d186f381f36f3db1f9e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "602b9edbeb97ee10c6c400c0089877803091724a0cdcc8aedfc9b4fae09efbd8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "cece245d60ddf1cb6705edda55d24404c22d5e21bbd734cfa3e125c4a620a167"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d95f8484809272ffe78deba80f32795f617f62d412dbd75c6456a94e5ab08254"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "68edf4824734005ac066bbfc5641f3e1a1de318d1a4db8d0874d30c750af2be8"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61b9c2df074518276bd3d99a8c9acadb133c4afea4f258debe4db8e3ced6a830",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "64ed3899495ebff9294340b3518eb34b72d73e3940870866807ac3958cdee332"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "fa10f800c026c3a1ff361d6110d265045b2e2b09d9ca3417716f1a5b4d83fce0"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3da61d52af39daefde08800dbec20595d14e7a7c45427feae30faecdbca978d4"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "fae1f30a10d1bc550812f344ee228a3ab362e21da161e87e47ecdac7326268ba"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "63bc2cbf4d0d9e4d0923f8f9aebd401748f17cbdf025518fa7d7536b85bde2c5"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "2583e4f16a2500e34069514018a8f2ea03fea0586a6ac598d1e292122df73a43",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "f30c3de8a18b52fbffe84cc3eeb38190285cbfc14eec690df3510ec8174bf8e8"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "a866f66b3a60a873b64f8664e230b21d2618ce37d80256e55edb58b2d1609311"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "5bba82f9177b6051a2bec4766f3818c95a3a218b6cb3f49f0f7f2ce08eabc08a"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "54120120288b40e126390f879475128a7c546dc5894244ffbab2dc41ec0bbdea"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "e3e302109075c5e71050af30fa60a9d9622ab255ff6498c436b7c2b08ab9e27c"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "876feb4157608ae15730542019e1787f95a35542f7e90339dae0471f76530717"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "badd932ef5030c719beb1cc00b0d76c54317dcaa503b1b8850bbfaa39d0a73b6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "e53554b6fa0e0c8fa01fa8e1394faf6c45176fc6a7497a9e1e26d2b0253b599e"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "301a7ea1b2514321ab751e3194dd500461ea2d3a4cc51eb96b552288e2597da2",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "232ca4156abc6eecc1c68444c6e1983abd566b30c7d808b5705f4794bd1c7edf",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c443142ddbf50fb18a4de115e8821940265fdb8eb305adaf2fd6a53e74b92e67",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "a6b81e430572ec5b290105fcd24df2e7811dbfe7e1cbcaf0d0246ef1fe4b6c9d",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5a794eb23d83d8ef0d7a5cd636119e122d8f5d946fd04ca69b1541bd06dffb1e",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "iceberg_visible": {
                "customers": {
                  "manifest_sha256": "2163b64da4630010afb36a5a1d647f7f9061dd27721750be5d4343756f68f509",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "6504201ef8e7783b67bcd3c6cdc25343a6fd7e3ba5d05c20f586e5066addd019"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "1af1f9b6f8bee67ec321c0c76a6fd7747dcd16efd15541c145fc45dc04671aaf"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "58e95e7e89fdf89a9219ae3c4784a078cabf33ce1bd3cdb9a24ba78515d0cfcc"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "1347812f4872f7ec8a5d1d1de1e6f5e728f5197826f19f2044b83426400d8b04"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "4d37ae8594d7c6a23ef1a2da18c51ff718860cc0e86cd8df9fe1b7fd386c1492"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "28095779e50db90fb650a166495817f630c58b4d9cfd86b7cbb23afd9de6ab9b"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "cd2331d56a106934ebf661221b1e11246cc7f037086902c7c348a4011f1f6ae9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "c237aab742403af52fcd2448e403a9a4bde89f4c3e13e708b99a994b7678cb77"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "b137c7cc3317992c2b86690f77bed9476bd93d2bfa2e8cc7db57889448024428"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "e61f13501d7d8d1e775be282615a521f628c487cc8d540c22908f4a80e4de93b",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1bc0c002d676f3311cfea0d8b439ef18c4b8838a25ef73469a86aa6d481ead1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "1cba70c1a36d197dbd2565aa114d7167e6fc2720856d7d2d79cbf4ba638a1b68"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "ac570e4fafeddd75713c36c59f0e238a78dc7673abd7284f9de3f8d413e0d484"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "34a13c47774cdf4dc0fcfe2399e92ef24795ed26114b063d90860024c8169f3a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "92e2358a73d0feda7de085ffbcf46bbe5faccc646ea6f8a7580a7d1f727ceeb2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "5e8794d558c53b77db572e965c2c76b1f4b7107e0a290000cbea6b220954a7c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "d80b661447f72f73422ee13dc5f0d50510fae086f0fc33a018b86a0bde4c2854"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "18bef5dae4b7ea33e98cef90dba7d518d4e0c0a1bfa5d386c9bc49699b98bb48"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "9c86590292dde1ecb5b398eb7c824839425642d6cb013f20dfd67e7294f6a3a7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "ae677f2af1b2eeb86529c9f58795495fc1292fa03898b6c27a0238cc0d9df487"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "d4dd8379bed1c7ead2e1823b6d840f63116331ecac68bde5e5d949d20a62efab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "774071905f13623890360e71b932fa6018f714c8e960696902dd82d815c56d17"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "5b53b626984338449402b2cff29e5de47118f84925d6f0e7c3acb25d841d9bac"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3ad64585ebd623659647c86343fb2c3a67a8abcbb149d6330076d7f65ebc2c33"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fbb723f947479ff4bc85a380e8d03868843e9d915fa195522c1123133944cd1b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "d246fb12f69180726adc9b18d00eee7c5c16f9bc9cd05944a9e1514420b1d251"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "82ffb47c67b5d59f3827598210003985afe288fa0bb6d4a674d929812f66c218"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "8015c870ad4d3fb197b8ed140e5bdbfd3f7779fcea07f9491a78f6a4f979df16"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f830be77e3f72131fd368f713cd5ba24bb18bb685cfb5424703be24b79f14ea2",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "85f2d626fe0728e4f24a8471fd325cf48590889d8f31fceecf42599539bff7ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "f4b7abdb8d2442513de5691e82787365d4010be7961664bd6693ae08befabd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "99a192a428458105fb40a98049f80638e12deb5f48cee3961a2b93920e086617"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "013f5cf35c61796bd9160b65580daf0c2db5950646e9cd650b078fea05cda065"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "113198c969adc46ae00c7870b4827e919ac2d22b7f7236822e0319de82f93dde"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "c93e9d5e5c1a2116dba1602dc14ae29862849bb14573ce125508cec212abb103"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "0e6d5b58695652438712a319b0d8f50377144fa9f00aed7dd7a7ff28b19d7dbc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "2ace57e0772a079483309452020fb09cba21887f860f97622ceb8b5751b81dff"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "81d6d943fe9d5cd9d3fa062893a5b24c5ce830619737427cdde1ec7dd2fd31af"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "e3cc2445917d5c788f424487949b5ad7cd6adbd015ccf3c764f85cd2b823c9ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "fd0f02a874dd9893caa2cb234e353fa3ec5c44a09ca618452fdd50e0873108a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "1e00d0c46041fcf5d023c8c3cc3f29cda7ad4b80e8ac3e6288c87dff6ae13195"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "def771ab7abb15d4f8dda741e0f122a6ba34cd1c83799fa57488fd20e1f1312a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "e02b86ed8ec39dc40bd6cdf0a9258f0a057211e46aa8e2a92524821c8d5e877e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "de3a04e84f1756cc07b586194ad1b19731d5fe4adce8db4c73eced3405cd1977"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "850a3cc7e4d77c7ee693f5bee94098d78fdb2fb00607a557ab6d3d35ca2ab851"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "1a68c883a84f0e08442a5ffbf147824a4512efaa314ead2ee5d26cba1542311e",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "2006044943c124b8aa17b3cc2c69d633434c66b4d54e999004b7a7a61f2b2f56"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "c84bb7e7e04a6cab45811148e29ab241908b4f0fde9b38548f22778cc5e86e6f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "1ce0098440765769980aedcf22eea71ca59e5e0beb63ef07b00228f7f7a7fe25"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "44150e36c1224c180bdbb3dfc20382a6e59ed1b328e91579c56362436a591a00"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "c6c2760a11e553aa0a0ddefb66299493f2d4ed5bc249ea9fb7246fae104312ad"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "893bfe7b6f9694d12d9daad1ffd17a96bdcc2440dd21dae66656ed15b7e15e67"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "7017290069cd0d4390830739b6bea8e131d18cfda5f92a7b574b3c592d5f50e1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "ace2d4fb20ac23e26ca426152f507ba7bd511c52d31d030439392a70f2159429"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "ec9008c1ce945999916de5ce7fafca0e1e4b7e866838932eb069e55f85f77ee7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "a8731f1d44d1c55e309048156f7694bc1b1c14f4f7816dadc0c19c1a16b53616"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "be359fe95a1275a648eb31724f47ccaa581b6a019f828f62b1c47be9be5dc612"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "16bd411e3ee55397c8244b79be7083587a38a1b0e1e326ab466b732f87cafa52"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "2a79b4a6501ef52b8186ebb0e9a718d53f150b6c0991e9705f0c9a4e974d97c1",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "4d0bdbee23e2bff1eb2a3d7581eaa25e4be28916a635d552d6ae3ce7eb53fc72"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "ba0c5d34562bc3805739d60905f0e1e8125b8287f81dba8fac6b65f0699e8266"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "697542590d2ffbe526948106f9a00c17f131df530a05017602aa705bc15faab8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "7f9a69d1646f89a2577cc1641155fba1c106cb76cf69586615d871d8b9b5611a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "8dcaf1f60fd4ab2b22798f49e9edca0a9a0320de87e8d52d89e75f38133ef554"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "65cb1e8426a81079cafa2ea5c53d1d74a825ea578abca611623139ce9213fa3d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "8793912f4b5c53dac2896586711a58e4405fd64d1f9c537545e3f29af5d2bdcb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "81bdf76398323b4a8ecf7444e06ce90881809d83caa476e36af8486a60f1068c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "58fec23f57c0ae6968f7d2ba90ea3b8c10e2abe383861d186f381f36f3db1f9e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "602b9edbeb97ee10c6c400c0089877803091724a0cdcc8aedfc9b4fae09efbd8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "cece245d60ddf1cb6705edda55d24404c22d5e21bbd734cfa3e125c4a620a167"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d95f8484809272ffe78deba80f32795f617f62d412dbd75c6456a94e5ab08254"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "68edf4824734005ac066bbfc5641f3e1a1de318d1a4db8d0874d30c750af2be8"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61b9c2df074518276bd3d99a8c9acadb133c4afea4f258debe4db8e3ced6a830",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "64ed3899495ebff9294340b3518eb34b72d73e3940870866807ac3958cdee332"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "fa10f800c026c3a1ff361d6110d265045b2e2b09d9ca3417716f1a5b4d83fce0"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3da61d52af39daefde08800dbec20595d14e7a7c45427feae30faecdbca978d4"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "fae1f30a10d1bc550812f344ee228a3ab362e21da161e87e47ecdac7326268ba"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "63bc2cbf4d0d9e4d0923f8f9aebd401748f17cbdf025518fa7d7536b85bde2c5"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "2583e4f16a2500e34069514018a8f2ea03fea0586a6ac598d1e292122df73a43",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "f30c3de8a18b52fbffe84cc3eeb38190285cbfc14eec690df3510ec8174bf8e8"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "a866f66b3a60a873b64f8664e230b21d2618ce37d80256e55edb58b2d1609311"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "5bba82f9177b6051a2bec4766f3818c95a3a218b6cb3f49f0f7f2ce08eabc08a"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "54120120288b40e126390f879475128a7c546dc5894244ffbab2dc41ec0bbdea"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "e3e302109075c5e71050af30fa60a9d9622ab255ff6498c436b7c2b08ab9e27c"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "876feb4157608ae15730542019e1787f95a35542f7e90339dae0471f76530717"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "badd932ef5030c719beb1cc00b0d76c54317dcaa503b1b8850bbfaa39d0a73b6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "e53554b6fa0e0c8fa01fa8e1394faf6c45176fc6a7497a9e1e26d2b0253b599e"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "301a7ea1b2514321ab751e3194dd500461ea2d3a4cc51eb96b552288e2597da2",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "232ca4156abc6eecc1c68444c6e1983abd566b30c7d808b5705f4794bd1c7edf",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c443142ddbf50fb18a4de115e8821940265fdb8eb305adaf2fd6a53e74b92e67",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "a6b81e430572ec5b290105fcd24df2e7811dbfe7e1cbcaf0d0246ef1fe4b6c9d",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5a794eb23d83d8ef0d7a5cd636119e122d8f5d946fd04ca69b1541bd06dffb1e",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "stable_visible": {
                "customers": {
                  "manifest_sha256": "2163b64da4630010afb36a5a1d647f7f9061dd27721750be5d4343756f68f509",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "6504201ef8e7783b67bcd3c6cdc25343a6fd7e3ba5d05c20f586e5066addd019"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "1af1f9b6f8bee67ec321c0c76a6fd7747dcd16efd15541c145fc45dc04671aaf"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "58e95e7e89fdf89a9219ae3c4784a078cabf33ce1bd3cdb9a24ba78515d0cfcc"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "1347812f4872f7ec8a5d1d1de1e6f5e728f5197826f19f2044b83426400d8b04"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "4d37ae8594d7c6a23ef1a2da18c51ff718860cc0e86cd8df9fe1b7fd386c1492"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "28095779e50db90fb650a166495817f630c58b4d9cfd86b7cbb23afd9de6ab9b"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "cd2331d56a106934ebf661221b1e11246cc7f037086902c7c348a4011f1f6ae9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "c237aab742403af52fcd2448e403a9a4bde89f4c3e13e708b99a994b7678cb77"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "b137c7cc3317992c2b86690f77bed9476bd93d2bfa2e8cc7db57889448024428"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "e61f13501d7d8d1e775be282615a521f628c487cc8d540c22908f4a80e4de93b",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1bc0c002d676f3311cfea0d8b439ef18c4b8838a25ef73469a86aa6d481ead1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "1cba70c1a36d197dbd2565aa114d7167e6fc2720856d7d2d79cbf4ba638a1b68"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "ac570e4fafeddd75713c36c59f0e238a78dc7673abd7284f9de3f8d413e0d484"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "34a13c47774cdf4dc0fcfe2399e92ef24795ed26114b063d90860024c8169f3a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "92e2358a73d0feda7de085ffbcf46bbe5faccc646ea6f8a7580a7d1f727ceeb2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "5e8794d558c53b77db572e965c2c76b1f4b7107e0a290000cbea6b220954a7c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "d80b661447f72f73422ee13dc5f0d50510fae086f0fc33a018b86a0bde4c2854"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "18bef5dae4b7ea33e98cef90dba7d518d4e0c0a1bfa5d386c9bc49699b98bb48"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "9c86590292dde1ecb5b398eb7c824839425642d6cb013f20dfd67e7294f6a3a7"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "ae677f2af1b2eeb86529c9f58795495fc1292fa03898b6c27a0238cc0d9df487"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "d4dd8379bed1c7ead2e1823b6d840f63116331ecac68bde5e5d949d20a62efab"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "774071905f13623890360e71b932fa6018f714c8e960696902dd82d815c56d17"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "5b53b626984338449402b2cff29e5de47118f84925d6f0e7c3acb25d841d9bac"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3ad64585ebd623659647c86343fb2c3a67a8abcbb149d6330076d7f65ebc2c33"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "fbb723f947479ff4bc85a380e8d03868843e9d915fa195522c1123133944cd1b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "d246fb12f69180726adc9b18d00eee7c5c16f9bc9cd05944a9e1514420b1d251"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "82ffb47c67b5d59f3827598210003985afe288fa0bb6d4a674d929812f66c218"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "8015c870ad4d3fb197b8ed140e5bdbfd3f7779fcea07f9491a78f6a4f979df16"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "f830be77e3f72131fd368f713cd5ba24bb18bb685cfb5424703be24b79f14ea2",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "85f2d626fe0728e4f24a8471fd325cf48590889d8f31fceecf42599539bff7ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "f4b7abdb8d2442513de5691e82787365d4010be7961664bd6693ae08befabd87"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "99a192a428458105fb40a98049f80638e12deb5f48cee3961a2b93920e086617"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "013f5cf35c61796bd9160b65580daf0c2db5950646e9cd650b078fea05cda065"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "113198c969adc46ae00c7870b4827e919ac2d22b7f7236822e0319de82f93dde"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "c93e9d5e5c1a2116dba1602dc14ae29862849bb14573ce125508cec212abb103"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "0e6d5b58695652438712a319b0d8f50377144fa9f00aed7dd7a7ff28b19d7dbc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "2ace57e0772a079483309452020fb09cba21887f860f97622ceb8b5751b81dff"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "81d6d943fe9d5cd9d3fa062893a5b24c5ce830619737427cdde1ec7dd2fd31af"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "e3cc2445917d5c788f424487949b5ad7cd6adbd015ccf3c764f85cd2b823c9ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "fd0f02a874dd9893caa2cb234e353fa3ec5c44a09ca618452fdd50e0873108a0"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "1e00d0c46041fcf5d023c8c3cc3f29cda7ad4b80e8ac3e6288c87dff6ae13195"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "def771ab7abb15d4f8dda741e0f122a6ba34cd1c83799fa57488fd20e1f1312a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "e02b86ed8ec39dc40bd6cdf0a9258f0a057211e46aa8e2a92524821c8d5e877e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "de3a04e84f1756cc07b586194ad1b19731d5fe4adce8db4c73eced3405cd1977"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "850a3cc7e4d77c7ee693f5bee94098d78fdb2fb00607a557ab6d3d35ca2ab851"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "1a68c883a84f0e08442a5ffbf147824a4512efaa314ead2ee5d26cba1542311e",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "2006044943c124b8aa17b3cc2c69d633434c66b4d54e999004b7a7a61f2b2f56"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "c84bb7e7e04a6cab45811148e29ab241908b4f0fde9b38548f22778cc5e86e6f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "1ce0098440765769980aedcf22eea71ca59e5e0beb63ef07b00228f7f7a7fe25"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "44150e36c1224c180bdbb3dfc20382a6e59ed1b328e91579c56362436a591a00"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "c6c2760a11e553aa0a0ddefb66299493f2d4ed5bc249ea9fb7246fae104312ad"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "893bfe7b6f9694d12d9daad1ffd17a96bdcc2440dd21dae66656ed15b7e15e67"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "7017290069cd0d4390830739b6bea8e131d18cfda5f92a7b574b3c592d5f50e1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "ace2d4fb20ac23e26ca426152f507ba7bd511c52d31d030439392a70f2159429"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "ec9008c1ce945999916de5ce7fafca0e1e4b7e866838932eb069e55f85f77ee7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "a8731f1d44d1c55e309048156f7694bc1b1c14f4f7816dadc0c19c1a16b53616"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "be359fe95a1275a648eb31724f47ccaa581b6a019f828f62b1c47be9be5dc612"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "16bd411e3ee55397c8244b79be7083587a38a1b0e1e326ab466b732f87cafa52"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "2a79b4a6501ef52b8186ebb0e9a718d53f150b6c0991e9705f0c9a4e974d97c1",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "4d0bdbee23e2bff1eb2a3d7581eaa25e4be28916a635d552d6ae3ce7eb53fc72"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "ba0c5d34562bc3805739d60905f0e1e8125b8287f81dba8fac6b65f0699e8266"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "697542590d2ffbe526948106f9a00c17f131df530a05017602aa705bc15faab8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "7f9a69d1646f89a2577cc1641155fba1c106cb76cf69586615d871d8b9b5611a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "8dcaf1f60fd4ab2b22798f49e9edca0a9a0320de87e8d52d89e75f38133ef554"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "65cb1e8426a81079cafa2ea5c53d1d74a825ea578abca611623139ce9213fa3d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "8793912f4b5c53dac2896586711a58e4405fd64d1f9c537545e3f29af5d2bdcb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "81bdf76398323b4a8ecf7444e06ce90881809d83caa476e36af8486a60f1068c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "58fec23f57c0ae6968f7d2ba90ea3b8c10e2abe383861d186f381f36f3db1f9e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "602b9edbeb97ee10c6c400c0089877803091724a0cdcc8aedfc9b4fae09efbd8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "cece245d60ddf1cb6705edda55d24404c22d5e21bbd734cfa3e125c4a620a167"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d95f8484809272ffe78deba80f32795f617f62d412dbd75c6456a94e5ab08254"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "68edf4824734005ac066bbfc5641f3e1a1de318d1a4db8d0874d30c750af2be8"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "61b9c2df074518276bd3d99a8c9acadb133c4afea4f258debe4db8e3ced6a830",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "64ed3899495ebff9294340b3518eb34b72d73e3940870866807ac3958cdee332"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "fa10f800c026c3a1ff361d6110d265045b2e2b09d9ca3417716f1a5b4d83fce0"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "3da61d52af39daefde08800dbec20595d14e7a7c45427feae30faecdbca978d4"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "fae1f30a10d1bc550812f344ee228a3ab362e21da161e87e47ecdac7326268ba"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "63bc2cbf4d0d9e4d0923f8f9aebd401748f17cbdf025518fa7d7536b85bde2c5"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "2583e4f16a2500e34069514018a8f2ea03fea0586a6ac598d1e292122df73a43",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "f30c3de8a18b52fbffe84cc3eeb38190285cbfc14eec690df3510ec8174bf8e8"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "a866f66b3a60a873b64f8664e230b21d2618ce37d80256e55edb58b2d1609311"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "5bba82f9177b6051a2bec4766f3818c95a3a218b6cb3f49f0f7f2ce08eabc08a"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "54120120288b40e126390f879475128a7c546dc5894244ffbab2dc41ec0bbdea"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "e3e302109075c5e71050af30fa60a9d9622ab255ff6498c436b7c2b08ab9e27c"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "876feb4157608ae15730542019e1787f95a35542f7e90339dae0471f76530717"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "badd932ef5030c719beb1cc00b0d76c54317dcaa503b1b8850bbfaa39d0a73b6"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "e53554b6fa0e0c8fa01fa8e1394faf6c45176fc6a7497a9e1e26d2b0253b599e"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "301a7ea1b2514321ab751e3194dd500461ea2d3a4cc51eb96b552288e2597da2",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "232ca4156abc6eecc1c68444c6e1983abd566b30c7d808b5705f4794bd1c7edf",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "c443142ddbf50fb18a4de115e8821940265fdb8eb305adaf2fd6a53e74b92e67",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "a6b81e430572ec5b290105fcd24df2e7811dbfe7e1cbcaf0d0246ef1fe4b6c9d",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "5a794eb23d83d8ef0d7a5cd636119e122d8f5d946fd04ca69b1541bd06dffb1e",
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
              "updated_at": "2026-08-03T19:12:57.638870884Z"
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
          "stdout": "b57889448024428\"}]}, \"order_items\": {\"manifest_sha256\": \"e61f13501d7d8d1e775be282615a521f628c487cc8d540c22908f4a80e4de93b\", \"row_count\": 18, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"order_item_id\": 1, \"row_hash\": \"1bc0c002d676f3311cfea0d8b439ef18c4b8838a25ef73469a86aa6d481ead1f\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"order_item_id\": 1, \"row_hash\": \"1cba70c1a36d197dbd2565aa114d7167e6fc2720856d7d2d79cbf4ba638a1b68\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"order_item_id\": 1, \"row_hash\": \"ac570e4fafeddd75713c36c59f0e238a78dc7673abd7284f9de3f8d413e0d484\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"order_item_id\": 2, \"row_hash\": \"34a13c47774cdf4dc0fcfe2399e92ef24795ed26114b063d90860024c8169f3a\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"order_item_id\": 1, \"row_hash\": \"92e2358a73d0feda7de085ffbcf46bbe5faccc646ea6f8a7580a7d1f727ceeb2\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"order_item_id\": 1, \"row_hash\": \"5e8794d558c53b77db572e965c2c76b1f4b7107e0a290000cbea6b220954a7c3\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"order_item_id\": 1, \"row_hash\": \"d80b661447f72f73422ee13dc5f0d50510fae086f0fc33a018b86a0bde4c2854\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"order_item_id\": 2, \"row_hash\": \"18bef5dae4b7ea33e98cef90dba7d518d4e0c0a1bfa5d386c9bc49699b98bb48\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"order_item_id\": 1, \"row_hash\": \"9c86590292dde1ecb5b398eb7c824839425642d6cb013f20dfd67e7294f6a3a7\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"order_item_id\": 1, \"row_hash\": \"ae677f2af1b2eeb86529c9f58795495fc1292fa03898b6c27a0238cc0d9df487\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"order_item_id\": 1, \"row_hash\": \"d4dd8379bed1c7ead2e1823b6d840f63116331ecac68bde5e5d949d20a62efab\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"order_item_id\": 2, \"row_hash\": \"774071905f13623890360e71b932fa6018f714c8e960696902dd82d815c56d17\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"order_item_id\": 1, \"row_hash\": \"5b53b626984338449402b2cff29e5de47118f84925d6f0e7c3acb25d841d9bac\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"order_item_id\": 1, \"row_hash\": \"3ad64585ebd623659647c86343fb2c3a67a8abcbb149d6330076d7f65ebc2c33\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"order_item_id\": 1, \"row_hash\": \"fbb723f947479ff4bc85a380e8d03868843e9d915fa195522c1123133944cd1b\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"order_item_id\": 2, \"row_hash\": \"d246fb12f69180726adc9b18d00eee7c5c16f9bc9cd05944a9e1514420b1d251\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"order_item_id\": 1, \"row_hash\": \"82ffb47c67b5d59f3827598210003985afe288fa0bb6d4a674d929812f66c218\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"order_item_id\": 2, \"row_hash\": \"8015c870ad4d3fb197b8ed140e5bdbfd3f7779fcea07f9491a78f6a4f979df16\"}]}, \"order_payments\": {\"manifest_sha256\": \"f830be77e3f72131fd368f713cd5ba24bb18bb685cfb5424703be24b79f14ea2\", \"row_count\": 16, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"payment_sequential\": 1, \"row_hash\": \"85f2d626fe0728e4f24a8471fd325cf48590889d8f31fceecf42599539bff7ae\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"payment_sequential\": 1, \"row_hash\": \"f4b7abdb8d2442513de5691e82787365d4010be7961664bd6693ae08befabd87\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"payment_sequential\": 1, \"row_hash\": \"99a192a428458105fb40a98049f80638e12deb5f48cee3961a2b93920e086617\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"payment_sequential\": 1, \"row_hash\": \"013f5cf35c61796bd9160b65580daf0c2db5950646e9cd650b078fea05cda065\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"payment_sequential\": 2, \"row_hash\": \"113198c969adc46ae00c7870b4827e919ac2d22b7f7236822e0319de82f93dde\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"payment_sequential\": 1, \"row_hash\": \"c93e9d5e5c1a2116dba1602dc14ae29862849bb14573ce125508cec212abb103\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"payment_sequential\": 1, \"row_hash\": \"0e6d5b58695652438712a319b0d8f50377144fa9f00aed7dd7a7ff28b19d7dbc\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"payment_sequential\": 1, \"row_hash\": \"2ace57e0772a079483309452020fb09cba21887f860f97622ceb8b5751b81dff\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"payment_sequential\": 1, \"row_hash\": \"81d6d943fe9d5cd9d3fa062893a5b24c5ce830619737427cdde1ec7dd2fd31af\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"payment_sequential\": 2, \"row_hash\": \"e3cc2445917d5c788f424487949b5ad7cd6adbd015ccf3c764f85cd2b823c9ae\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"payment_sequential\": 1, \"row_hash\": \"fd0f02a874dd9893caa2cb234e353fa3ec5c44a09ca618452fdd50e0873108a0\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"payment_sequential\": 1, \"row_hash\": \"1e00d0c46041fcf5d023c8c3cc3f29cda7ad4b80e8ac3e6288c87dff6ae13195\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"payment_sequential\": 1, \"row_hash\": \"def771ab7abb15d4f8dda741e0f122a6ba34cd1c83799fa57488fd20e1f1312a\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"payment_sequential\": 1, \"row_hash\": \"e02b86ed8ec39dc40bd6cdf0a9258f0a057211e46aa8e2a92524821c8d5e877e\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"payment_sequential\": 1, \"row_hash\": \"de3a04e84f1756cc07b586194ad1b19731d5fe4adce8db4c73eced3405cd1977\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"payment_sequential\": 2, \"row_hash\": \"850a3cc7e4d77c7ee693f5bee94098d78fdb2fb00607a557ab6d3d35ca2ab851\"}]}, \"order_reviews\": {\"manifest_sha256\": \"1a68c883a84f0e08442a5ffbf147824a4512efaa314ead2ee5d26cba1542311e\", \"row_count\": 12, \"rows\": [{\"is_deleted\": false, \"review_id\": \"review_001\", \"row_hash\": \"2006044943c124b8aa17b3cc2c69d633434c66b4d54e999004b7a7a61f2b2f56\"}, {\"is_deleted\": false, \"review_id\": \"review_002\", \"row_hash\": \"c84bb7e7e04a6cab45811148e29ab241908b4f0fde9b38548f22778cc5e86e6f\"}, {\"is_deleted\": false, \"review_id\": \"review_003\", \"row_hash\": \"1ce0098440765769980aedcf22eea71ca59e5e0beb63ef07b00228f7f7a7fe25\"}, {\"is_deleted\": false, \"review_id\": \"review_004\", \"row_hash\": \"44150e36c1224c180bdbb3dfc20382a6e59ed1b328e91579c56362436a591a00\"}, {\"is_deleted\": false, \"review_id\": \"review_005\", \"row_hash\": \"c6c2760a11e553aa0a0ddefb66299493f2d4ed5bc249ea9fb7246fae104312ad\"}, {\"is_deleted\": false, \"review_id\": \"review_006\", \"row_hash\": \"893bfe7b6f9694d12d9daad1ffd17a96bdcc2440dd21dae66656ed15b7e15e67\"}, {\"is_deleted\": false, \"review_id\": \"review_007\", \"row_hash\": \"7017290069cd0d4390830739b6bea8e131d18cfda5f92a7b574b3c592d5f50e1\"}, {\"is_deleted\": false, \"review_id\": \"review_008\", \"row_hash\": \"ace2d4fb20ac23e26ca426152f507ba7bd511c52d31d030439392a70f2159429\"}, {\"is_deleted\": false, \"review_id\": \"review_009\", \"row_hash\": \"ec9008c1ce945999916de5ce7fafca0e1e4b7e866838932eb069e55f85f77ee7\"}, {\"is_deleted\": false, \"review_id\": \"review_010\", \"row_hash\": \"a8731f1d44d1c55e309048156f7694bc1b1c14f4f7816dadc0c19c1a16b53616\"}, {\"is_deleted\": false, \"review_id\": \"review_011\", \"row_hash\": \"be359fe95a1275a648eb31724f47ccaa581b6a019f828f62b1c47be9be5dc612\"}, {\"is_deleted\": false, \"review_id\": \"review_012\", \"row_hash\": \"16bd411e3ee55397c8244b79be7083587a38a1b0e1e326ab466b732f87cafa52\"}]}, \"orders\": {\"manifest_sha256\": \"2a79b4a6501ef52b8186ebb0e9a718d53f150b6c0991e9705f0c9a4e974d97c1\", \"row_count\": 13, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"row_hash\": \"4d0bdbee23e2bff1eb2a3d7581eaa25e4be28916a635d552d6ae3ce7eb53fc72\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"row_hash\": \"ba0c5d34562bc3805739d60905f0e1e8125b8287f81dba8fac6b65f0699e8266\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"row_hash\": \"697542590d2ffbe526948106f9a00c17f131df530a05017602aa705bc15faab8\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"row_hash\": \"7f9a69d1646f89a2577cc1641155fba1c106cb76cf69586615d871d8b9b5611a\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"row_hash\": \"8dcaf1f60fd4ab2b22798f49e9edca0a9a0320de87e8d52d89e75f38133ef554\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"row_hash\": \"65cb1e8426a81079cafa2ea5c53d1d74a825ea578abca611623139ce9213fa3d\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"row_hash\": \"8793912f4b5c53dac2896586711a58e4405fd64d1f9c537545e3f29af5d2bdcb\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"row_hash\": \"81bdf76398323b4a8ecf7444e06ce90881809d83caa476e36af8486a60f1068c\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"row_hash\": \"58fec23f57c0ae6968f7d2ba90ea3b8c10e2abe383861d186f381f36f3db1f9e\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"row_hash\": \"602b9edbeb97ee10c6c400c0089877803091724a0cdcc8aedfc9b4fae09efbd8\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"row_hash\": \"cece245d60ddf1cb6705edda55d24404c22d5e21bbd734cfa3e125c4a620a167\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"row_hash\": \"d95f8484809272ffe78deba80f32795f617f62d412dbd75c6456a94e5ab08254\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"row_hash\": \"68edf4824734005ac066bbfc5641f3e1a1de318d1a4db8d0874d30c750af2be8\"}]}, \"product_category_translation\": {\"manifest_sha256\": \"61b9c2df074518276bd3d99a8c9acadb133c4afea4f258debe4db8e3ced6a830\", \"row_count\": 5, \"rows\": [{\"is_deleted\": false, \"product_category_name\": \"beleza_saude\", \"row_hash\": \"64ed3899495ebff9294340b3518eb34b72d73e3940870866807ac3958cdee332\"}, {\"is_deleted\": false, \"product_category_name\": \"informatica_acessorios\", \"row_hash\": \"fa10f800c026c3a1ff361d6110d265045b2e2b09d9ca3417716f1a5b4d83fce0\"}, {\"is_deleted\": false, \"product_category_name\": \"moveis_decoracao\", \"row_hash\": \"3da61d52af39daefde08800dbec20595d14e7a7c45427feae30faecdbca978d4\"}, {\"is_deleted\": false, \"product_category_name\": \"telefonia\", \"row_hash\": \"fae1f30a10d1bc550812f344ee228a3ab362e21da161e87e47ecdac7326268ba\"}, {\"is_deleted\": false, \"product_category_name\": \"utilidades_domesticas\", \"row_hash\": \"63bc2cbf4d0d9e4d0923f8f9aebd401748f17cbdf025518fa7d7536b85bde2c5\"}]}, \"products\": {\"manifest_sha256\": \"2583e4f16a2500e34069514018a8f2ea03fea0586a6ac598d1e292122df73a43\", \"row_count\": 8, \"rows\": [{\"is_deleted\": false, \"product_id\": \"product_001\", \"row_hash\": \"f30c3de8a18b52fbffe84cc3eeb38190285cbfc14eec690df3510ec8174bf8e8\"}, {\"is_deleted\": false, \"product_id\": \"product_002\", \"row_hash\": \"a866f66b3a60a873b64f8664e230b21d2618ce37d80256e55edb58b2d1609311\"}, {\"is_deleted\": false, \"product_id\": \"product_003\", \"row_hash\": \"5bba82f9177b6051a2bec4766f3818c95a3a218b6cb3f49f0f7f2ce08eabc08a\"}, {\"is_deleted\": false, \"product_id\": \"product_004\", \"row_hash\": \"54120120288b40e126390f879475128a7c546dc5894244ffbab2dc41ec0bbdea\"}, {\"is_deleted\": false, \"product_id\": \"product_005\", \"row_hash\": \"e3e302109075c5e71050af30fa60a9d9622ab255ff6498c436b7c2b08ab9e27c\"}, {\"is_deleted\": false, \"product_id\": \"product_006\", \"row_hash\": \"876feb4157608ae15730542019e1787f95a35542f7e90339dae0471f76530717\"}, {\"is_deleted\": false, \"product_id\": \"product_007\", \"row_hash\": \"badd932ef5030c719beb1cc00b0d76c54317dcaa503b1b8850bbfaa39d0a73b6\"}, {\"is_deleted\": false, \"product_id\": \"product_008\", \"row_hash\": \"e53554b6fa0e0c8fa01fa8e1394faf6c45176fc6a7497a9e1e26d2b0253b599e\"}]}, \"sellers\": {\"manifest_sha256\": \"301a7ea1b2514321ab751e3194dd500461ea2d3a4cc51eb96b552288e2597da2\", \"row_count\": 4, \"rows\": [{\"is_deleted\": false, \"row_hash\": \"232ca4156abc6eecc1c68444c6e1983abd566b30c7d808b5705f4794bd1c7edf\", \"seller_id\": \"seller_001\"}, {\"is_deleted\": false, \"row_hash\": \"c443142ddbf50fb18a4de115e8821940265fdb8eb305adaf2fd6a53e74b92e67\", \"seller_id\": \"seller_002\"}, {\"is_deleted\": false, \"row_hash\": \"a6b81e430572ec5b290105fcd24df2e7811dbfe7e1cbcaf0d0246ef1fe4b6c9d\", \"seller_id\": \"seller_003\"}, {\"is_deleted\": false, \"row_hash\": \"5a794eb23d83d8ef0d7a5cd636119e122d8f5d946fd04ca69b1541bd06dffb1e\", \"seller_id\": \"seller_004\"}]}}}, \"runtime\": {\"last_published_sync_run_seq\": 4, \"lease_owner_id\": null, \"source_snapshot_completed\": true}, \"stable_current_counts\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"status\": \"ready\", \"sync_run_id\": \"sync-00000000000000000004\", \"sync_run_seq\": 4}\n",
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
          "duration_seconds": 1.156,
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
          "duration_seconds": 1.469,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"clickhouse\": 200, \"command\": \"status\", \"compose\": [{\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"airflow\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"airflow-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"apicurio-registry\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"clickhouse\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"clickhouse-init\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"clickhouse-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"iceberg-migration\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"kafka\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"kafka-connect\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"kafka-topics\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"minio\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"minio-init\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"mysql\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"platform-postgres\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"platform-postgres-bootstrap\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"polaris\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-admin\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-admin-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-bootstrap\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-credentials-prepare\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-server-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-bronze\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-geolocation\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"spark-master\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-ops\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-silver\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-worker\", \"state\": \"running\"}], \"connector\": {\"connector_state\": \"RUNNING\", \"registered\": true, \"task_0_state\": \"RUNNING\"}, \"iceberg\": {\"contract_version\": 2, \"queries_count\": 10, \"status\": \"READY\", \"updated_at\": \"2026-08-03T19:12:57.638870884Z\"}, \"mysql\": {\"customers\": 9, \"geolocation\": 6, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"polaris\": 200, \"project\": \"olist_stage_v\", \"registry\": {\"compatibility\": \"BACKWARD_TRANSITIVE\", \"status_code\": 200}, \"status\": \"ready\", \"writer_schema_capture\": \"captured\"}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 4.251,
      "gate": "10-final",
      "status": "PASS",
      "timestamp": "2026-08-03T19:13:22.201611+00:00"
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

Raw evidence persisted in `data/stage-v-evidence/stage_v_clean_e113c55/`.
