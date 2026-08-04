# Stage V Candidate E2E Validation Report

- **Status**: `PASS`
- **Run ID**: `stage_l1_20260804_v6`
- **Compose Project**: `olist_stage_v`
- **Started At**: `2026-08-04T15:37:57.240519+00:00`
- **Finished At**: `2026-08-04T15:59:35.998139+00:00`

---

## 1. Final Verdict

Stage V validation completed with status `PASS`.

All mandatory gates passed in a single clean-domain run.

- **Stage L Authorization**: `AUTHORIZED` (allowed to proceed to Stage L)

---

## 2. Gate Execution Results (V0 - V10)

| Gate | Name | Status | Duration (s) |
| --- | --- | --- | ---: |
| `00-preflight` | 00-preflight | `PASS` | 51.345 |
| `01-harness-ready` | 01-harness-ready | `PASS` | 0.0 |
| `02-clean-bootstrap` | 02-clean-bootstrap | `PASS` | 312.708 |
| `03-initial-snapshot` | 03-initial-snapshot | `PASS` | 290.904 |
| `04-crud-and-restart` | 04-crud-and-restart | `PASS` | 166.325 |
| `05-caught-up` | 05-caught-up | `PASS` | 88.157 |
| `06-serving-sync` | 06-serving-sync | `PASS` | 241.568 |
| `07-dbt-and-stable-views` | 07-dbt-and-stable-views | `PASS` | 5.679 |
| `08-additive-schema` | 08-additive-schema | `PASS` | 68.2 |
| `09-rebuild` | 09-rebuild | `PASS` | 33.146 |
| `10-final` | 10-final | `PASS` | 6.083 |

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
              ".env.example",
              "airflow/dags/olist_lakehouse_serving.py",
              "compose.yaml",
              "docker/airflow/load-env-and-run.sh",
              "docs/source_contract.md",
              "docs/source_profile.json",
              "scripts/cdc/local_lab.py",
              "scripts/cdc/stage2_admin.py",
              "scripts/ingestion/raw_files.py",
              "scripts/serving/boundary.py",
              "scripts/serving/clickhouse.py",
              "scripts/serving/control.py",
              "scripts/simulation/README.md",
              "scripts/testing/create_small_fixture_dataset.py",
              "scripts/utilities/profile_olist_zip.py",
              "scripts/validation/stage_v_probes.py",
              "streaming/runtime-versions.json",
              "streaming/spark/scala/src/main/scala/com/olist/mds/spark/transaction/TransactionBatchWriter.scala",
              "tests/fixtures/olist_small/README.md",
              "tests/fixtures/olist_small/source_profile_small.json",
              "tests/serving/test_boundary.py",
              "tests/stage_v/test_stage_v_harness.py",
              "tests/test_control_postgres_phase2.py",
              "tests/test_stage2_configuration.py",
              "docker/secrets/dev/apicurio_db_password.txt",
              "docker/secrets/dev/minio_root_password.txt",
              "docker/secrets/dev/mysql_admin_password.txt",
              "docker/secrets/dev/mysql_cdc_reader_password.txt",
              "docker/secrets/dev/mysql_root_password.txt",
              "docker/secrets/dev/mysql_simulator_password.txt",
              "docker/secrets/dev/polaris_db_password.txt",
              "streaming/spark/scala/src/main/scala/com/olist/mds/spark/transaction/TransactionState.scala",
              "streaming/spark/scala/src/test/scala/com/olist/mds/spark/transaction/TransactionStateSpec.scala",
              "tests/lakehouse_platform/test_l1_runtime_contracts.py",
              "tests/serving/test_control.py"
            ],
            "commands_ok": true,
            "diagnostics": "warning: in the working copy of '.env.example', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'airflow/dags/olist_lakehouse_serving.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'compose.yaml', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'docs/source_profile.json', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'scripts/serving/boundary.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'scripts/serving/clickhouse.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'scripts/serving/control.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'scripts/simulation/README.md', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/runtime-versions.json', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/spark/scala/src/main/scala/com/olist/mds/spark/transaction/TransactionBatchWriter.scala', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/fixtures/olist_small/README.md', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/fixtures/olist_small/source_profile_small.json', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it\n",
            "dirty": true,
            "head": "9c0036c84b758ebe72b31388d009982e16dd2a75",
            "worktree_digest": "0e5cca168bc6728101a6adcc4c0429b6a2a087d1c9610108064a5fe07ad12874"
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
          "duration_seconds": 30.859,
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
          "stdout": "9c0036c84b758ebe72b31388d009982e16dd2a75\n",
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
          "stdout": " M .env.example\n M airflow/dags/olist_lakehouse_serving.py\n M compose.yaml\n M docker/airflow/load-env-and-run.sh\n M docs/source_contract.md\n M docs/source_profile.json\n M scripts/cdc/local_lab.py\n M scripts/cdc/stage2_admin.py\n M scripts/ingestion/raw_files.py\n M scripts/serving/boundary.py\n M scripts/serving/clickhouse.py\n M scripts/serving/control.py\n M scripts/simulation/README.md\n M scripts/testing/create_small_fixture_dataset.py\n M scripts/utilities/profile_olist_zip.py\n M scripts/validation/stage_v_probes.py\n M streaming/runtime-versions.json\n M streaming/spark/scala/src/main/scala/com/olist/mds/spark/transaction/TransactionBatchWriter.scala\n M tests/fixtures/olist_small/README.md\n M tests/fixtures/olist_small/source_profile_small.json\n M tests/serving/test_boundary.py\n M tests/stage_v/test_stage_v_harness.py\n M tests/test_control_postgres_phase2.py\n M tests/test_stage2_configuration.py\n?? docker/secrets/dev/apicurio_db_password.txt\n?? docker/secrets/dev/minio_root_password.txt\n?? docker/secrets/dev/mysql_admin_password.txt\n?? docker/secrets/dev/mysql_cdc_reader_password.txt\n?? docker/secrets/dev/mysql_root_password.txt\n?? docker/secrets/dev/mysql_simulator_password.txt\n?? docker/secrets/dev/polaris_db_password.txt\n?? streaming/spark/scala/src/main/scala/com/olist/mds/spark/transaction/TransactionState.scala\n?? streaming/spark/scala/src/test/scala/com/olist/mds/spark/transaction/TransactionStateSpec.scala\n?? tests/lakehouse_platform/test_l1_runtime_contracts.py\n?? tests/serving/test_control.py\n",
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
          "duration_seconds": 0.078,
          "exit_code": 0,
          "stderr": "warning: in the working copy of '.env.example', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'airflow/dags/olist_lakehouse_serving.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'compose.yaml', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'docs/source_profile.json', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'scripts/serving/boundary.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'scripts/serving/clickhouse.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'scripts/serving/control.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'scripts/simulation/README.md', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/runtime-versions.json', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'streaming/spark/scala/src/main/scala/com/olist/mds/spark/transaction/TransactionBatchWriter.scala', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/fixtures/olist_small/README.md', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/fixtures/olist_small/source_profile_small.json', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it\n",
          "stdout": "se_transaction_history(\n+        [\n+            {\n+                \"transaction_id\": \"tx-1\",\n+                \"status\": \"OPEN\",\n+                \"begin_kafka_offset\": 10,\n+                \"end_kafka_offset\": None,\n+                \"recorded_at\": \"2026-08-04T00:00:01Z\",\n+            },\n+            {\n+                \"transaction_id\": \"tx-1\",\n+                \"status\": \"COMPLETE\",\n+                \"begin_kafka_offset\": 10,\n+                \"end_kafka_offset\": 11,\n+                \"recorded_at\": \"2026-08-04T00:00:02Z\",\n+            },\n+            {\n+                \"transaction_id\": \"tx-1\",\n+                \"status\": \"COMPLETE\",\n+                \"begin_kafka_offset\": 10,\n+                \"end_kafka_offset\": 11,\n+                \"recorded_at\": \"2026-08-04T00:00:03Z\",\n+            },\n+        ]\n+    )\n+\n+    assert len(rows) == 1\n+    assert rows[0][\"status\"] == \"COMPLETE\"\n+    assert rows[0][\"end_kafka_offset\"] == 11\n+\n+\n+def test_unresolved_open_transaction_is_visible_to_planner():\n+    rows = [\n+        {\n+            \"transaction_id\": \"tx-open\",\n+            \"status\": \"OPEN\",\n+            \"begin_kafka_offset\": 20,\n+            \"end_kafka_offset\": None,\n+            \"event_count\": None,\n+            \"recorded_at\": \"2026-08-04T00:00:01Z\",\n+        }\n+    ]\n+\n+    assert transaction_boundary_state(rows) == \"READY\"\n+    plan = ServingBoundaryPlanner.plan_next_sync_run(\n+        sync_run_seq=1,\n+        runtime_state={\"source_snapshot_completed\": True},\n+        transaction_rows=rows,\n+        iceberg_snapshots={},\n+    )\n+    assert plan.status == \"WAITING\"\n+    assert plan.status_reason == \"OPEN_TRANSACTION\"\n+\n+\n+def test_rejected_observation_can_become_complete():\n+    rows = collapse_transaction_history(\n+        [\n+            {\n+                \"transaction_id\": \"tx-retry\",\n+                \"status\": \"REJECTED\",\n+                \"begin_kafka_offset\": 30,\n+                \"end_kafka_offset\": None,\n+                \"recorded_at\": \"2026-08-04T00:00:01Z\",\n+            },\n+            {\n+                \"transaction_id\": \"tx-retry\",\n+                \"status\": \"COMPLETE\",\n+                \"begin_kafka_offset\": 30,\n+                \"end_kafka_offset\": 31,\n+                \"event_count\": 1,\n+                \"recorded_at\": \"2026-08-04T00:00:02Z\",\n+            },\n+        ]\n+    )\n+\n+    assert transaction_boundary_state(rows) == \"READY\"\n+    plan = ServingBoundaryPlanner.plan_next_sync_run(\n+        sync_run_seq=1,\n+        runtime_state={\"source_snapshot_completed\": True},\n+        transaction_rows=rows,\n+        iceberg_snapshots={},\n+    )\n+    assert plan.status == \"MATERIALIZING\"\n+    assert plan.target_transaction_id == \"tx-retry\"\n+\n+\n+def test_unknown_transaction_state_fails_closed():\n+    plan = ServingBoundaryPlanner.plan_next_sync_run(\n+        sync_run_seq=1,\n+        runtime_state={\"source_snapshot_completed\": True},\n+        transaction_rows=[\n+            {\n+                \"transaction_id\": \"tx-invalid\",\n+                \"status\": \"UNKNOWN\",\n+                \"begin_kafka_offset\": 40,\n+                \"end_kafka_offset\": None,\n+            }\n+        ],\n+        iceberg_snapshots={},\n+    )\n+\n+    assert plan.status == \"BLOCKED\"\n+    assert plan.status_reason == \"INVARIANT_FAILURE\"\n \n \n def test_boundary_planner_not_caught_up():\ndiff --git a/tests/stage_v/test_stage_v_harness.py b/tests/stage_v/test_stage_v_harness.py\nindex d1ee3c4..b44325a 100644\n--- a/tests/stage_v/test_stage_v_harness.py\n+++ b/tests/stage_v/test_stage_v_harness.py\n@@ -2,6 +2,7 @@ from __future__ import annotations\n \n import decimal\n import json\n+import os\n import tempfile\n import unittest\n from datetime import UTC, datetime\n@@ -143,6 +144,30 @@ class StageVHarnessUnitTests(unittest.TestCase):\n         with self.assertRaises(ValueError):\n             probe.execute_fixture(\"unauthorized_drop_tables.sql\")\n \n+    def test_mysql_probe_default_identity_matches_simulator_secret(self) -> None:\n+        with (\n+            patch.dict(os.environ, {}, clear=True),\n+            patch(\"scripts.simulation.database.connect\") as connect,\n+        ):\n+            MySQLProbe()._connect()\n+\n+        settings = connect.call_args.args[0]\n+        self.assertEqual(settings.user, \"olist_simulator\")\n+        self.assertEqual(settings.password_file.name, \"mysql_simulator_password.txt\")\n+\n+    def test_mysql_probe_schema_fixture_uses_admin_secret(self) -> None:\n+        probe = MySQLProbe()\n+        connection = MagicMock()\n+        cursor = MagicMock()\n+        connection.cursor.return_value = cursor\n+        with patch.object(probe, \"_connect_admin\", return_value=connection) as admin:\n+            probe.execute_fixture(\"add_nullable_column.sql\")\n+\n+        admin.assert_called_once_with()\n+        connection.commit.assert_called_once()\n+        connection.close.assert_called_once()\n+        cursor.close.assert_called_once()\n+\n     def test_mysql_probe_fixture_connection_errors_are_not_suppressed(self) -> None:\n         probe = MySQLProbe()\n         with (\ndiff --git a/tests/test_control_postgres_phase2.py b/tests/test_control_postgres_phase2.py\nindex 4d76c97..e87ba91 100644\n--- a/tests/test_control_postgres_phase2.py\n+++ b/tests/test_control_postgres_phase2.py\n@@ -42,9 +42,12 @@ class ControlPostgresPhase2Tests(unittest.TestCase):\n     def test_compose_defines_control_database_init_and_secret(self) -> None:\n         compose = (PROJECT_ROOT / \"compose.yaml\").read_text(encoding=\"utf-8\")\n \n-        self.assertIn(\"control-db-init:\", compose)\n+        self.assertIn(\"platform-postgres-bootstrap:\", compose)\n         self.assertIn(\n-            'CONTROL_POSTGRES_DB: \"${CONTROL_POSTGRES_DB:-olist_control}\"',\n+            \"./infra/control-postgres:/opt/olist/control-postgres:ro\", compose\n+        )\n+        self.assertIn(\n+            \"CONTROL_POSTGRES_DB: olist_control\",\n             compose,\n         )\n         self.assertIn(\n@@ -52,6 +55,15 @@ class ControlPostgresPhase2Tests(unittest.TestCase):\n             compose,\n         )\n         self.assertIn(\"control_postgres_password:\", compose)\n+        self.assertIn(\n+            \"serving.sync_runs\",\n+            \"\\n\".join(\n+                path.read_text(encoding=\"utf-8\")\n+                for path in (\n+                    PROJECT_ROOT / \"infra\" / \"control-postgres\" / \"initdb\"\n+                ).glob(\"*.sql\")\n+            ),\n+        )\n \n     def test_control_postgres_ddl_excludes_warehouse_raw_tables(self) -> None:\n         ddl_dir = PROJECT_ROOT / \"infra\" / \"control-postgres\" / \"initdb\"\ndiff --git a/tests/test_stage2_configuration.py b/tests/test_stage2_configuration.py\nindex a58130d..970beb4 100644\n--- a/tests/test_stage2_configuration.py\n+++ b/tests/test_stage2_configuration.py\n@@ -4,12 +4,15 @@ import json\n import re\n import unittest\n from pathlib import Path\n+from tempfile import TemporaryDirectory\n from unittest.mock import Mock, patch\n \n from scripts.cdc.stage2_admin import (\n+    CONNECTOR_NAME,\n     connector_has_failed,\n     connector_is_running,\n     parse_topic_description,\n+    render_connector,\n     wait_connector_status,\n )\n \n@@ -29,11 +32,12 @@ CAPTURED = {\n \n class Stage2ConfigurationTests(unittest.TestCase):\n     def setUp(self) -> None:\n-        self.topics = json.loads(\n+        self.topic_manifest = json.loads(\n             (ROOT / \"streaming/kafka/topics.json\").read_text(encoding=\"utf-8\")\n-        )[\"topics\"]\n+        )\n+        self.topics = self.topic_manifest[\"topics\"]\n         self.connector = json.loads(\n-            (ROOT / \"streaming/connect/olist-postgres-cdc.json\").read_text(\n+            (ROOT / \"streaming/connect/olist-mysql-cdc.json\").read_text(\n                 encoding=\"utf-8\"\n             )\n         )\n@@ -47,17 +51,15 @@ class Stage2ConfigurationTests(unittest.TestCase):\n         self.assertNotIn(\"quay.io/debezium/connect:3.6\\n\", dockerfile)\n         self.assertNotIn(\":latest\", compose + dockerfile)\n \n-    def test_source_and_dlq_topics_match_contract(self) -> None:\n+    def test_source_topics_match_contract(self) -> None:\n         by_name = {topic[\"name\"]: topic for topic in self.topics}\n         for table, (partitions, _key_fields) in CAPTURED.items():\n-            source = by_name[f\"olist_cdc.public.{table}\"]\n-            dlq = by_name[f\"olist_cdc.dlq.{table}\"]\n-            for topic in (source, dlq):\n-                self.assertEqual(partitions, topic[\"partitions\"])\n-                self.assertEqual(1, topic[\"replication_factor\"])\n-                self.assertEqual(\"delete\", topic[\"cleanup_policy\"])\n-                self.assertEqual(604_800_000, topic[\"retention_ms\"])\n-        self.assertNotIn(\"olist_cdc.public.geolocation\", by_name)\n+            source = by_name[f\"olist_cdc.olist_oltp.{table}\"]\n+            self.assertEqual(partitions, source[\"partitions\"])\n+            self.assertEqual(1, self.topic_manifest[\"replication_factor\"])\n+            self.assertEqual(\"delete\", source[\"config\"][\"cleanup.policy\"])\n+            self.assertEqual(604_800_000, int(source[\"config\"][\"retention.ms\"]))\n+        self.assertNotIn(\"olist_cdc.olist_oltp.geolocation\", by_name)\n \n     def test_topic_bootstrap_matches_manifest(self) -> None:\n         script = (ROOT / \"streaming/kafka/create-topics.sh\").read_text(encoding=\"utf-8\")\n@@ -70,21 +72,25 @@ class Stage2ConfigurationTests(unittest.TestCase):\n             \"olist_connect_configs\": (1, \"compact\"),\n             \"olist_connect_offsets\": (25, \"compact\"),\n             \"olist_connect_status\": (5, \"compact\"),\n-            \"olist_cdc.schema_history\": (1, \"compact\"),\n+            \"olist_cdc.schema_history\": (1, \"delete\"),\n             \"olist_cdc.transaction\": (1, \"delete\"),\n             \"olist_cdc.heartbeat\": (1, \"delete\"),\n         }\n         for name, (partitions, policy) in expected.items():\n             self.assertEqual(partitions, by_name[name][\"partitions\"])\n-            self.assertEqual(policy, by_name[name][\"cleanup_policy\"])\n+            self.assertEqual(policy, by_name[name][\"config\"][\"cleanup.policy\"])\n \n     def test_connector_is_secret_free_and_excludes_control_data(self) -> None:\n         config = self.connector[\"config\"]\n-        self.assertEqual(\"${OLTP_CDC_READER_PASSWORD}\", config[\"database.password\"])\n+        self.assertEqual(CONNECTOR_NAME, self.connector[\"name\"])\n+        self.assertEqual(\n+            \"io.debezium.connector.mysql.MySqlConnector\", config[\"connector.class\"]\n+        )\n+        self.assertNotIn(\"database.password\", config)\n         include = set(config[\"table.include.list\"].split(\",\"))\n-        self.assertEqual({f\"public.{name}\" for name in CAPTURED}, include)\n-        self.assertNotIn(\"public.geolocation\", include)\n-        self.assertNotIn(\"simulator_control\", config[\"schema.include.list\"])\n+        self.assertEqual({f\"olist_oltp.{name}\" for name in CAPTURED}, include)\n+        self.assertNotIn(\"olist_oltp.geolocation\", include)\n+        self.assertEqual(\"olist_oltp\", config[\"database.include.list\"])\n         self.assertEqual(\"true\", config[\"provide.transaction.metadata\"])\n         self.assertEqual(\"true\", config[\"tombstones.on.delete\"])\n         self.assertFalse(any(key.startswith(\"topic.creation.\") for key in config))\n@@ -98,6 +104,17 @@ class Stage2ConfigurationTests(unittest.TestCase):\n             \"olist_cdc.heartbeat\", config[\"transforms.routeHeartbeat.replacement\"]\n         )\n \n+    def test_render_connector_injects_only_file_secret(self) -> None:\n+        with TemporaryDirectory() as temp_dir:\n+            password_file = Path(temp_dir) / \"mysql-cdc-password\"\n+            password_file.write_text(\"mysql-cdc-secret\\n\", encoding=\"utf-8\")\n+\n+            rendered = render_connector(password_file)\n+\n+        self.assertEqual(CONNECTOR_NAME, rendered[\"name\"])\n+        self.assertEqual(\"mysql-cdc-secret\", rendered[\"config\"][\"database.password\"])\n+        self.assertNotIn(\"mysql-cdc-secret\", json.dumps(self.connector))\n+\n     def test_confluent_compatible_avro_converter_contract(self) -> None:\n         config = self.connector[\"config\"]\n         for side in (\"key\", \"value\"):\n",
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
          "duration_seconds": 0.125,
          "exit_code": 0,
          "stderr": "",
          "stdout": "docker/secrets/dev/apicurio_db_password.txt\u0000docker/secrets/dev/minio_root_password.txt\u0000docker/secrets/dev/mysql_admin_password.txt\u0000docker/secrets/dev/mysql_cdc_reader_password.txt\u0000docker/secrets/dev/mysql_root_password.txt\u0000docker/secrets/dev/mysql_simulator_password.txt\u0000docker/secrets/dev/polaris_db_password.txt\u0000streaming/spark/scala/src/main/scala/com/olist/mds/spark/transaction/TransactionState.scala\u0000streaming/spark/scala/src/test/scala/com/olist/mds/spark/transaction/TransactionStateSpec.scala\u0000tests/lakehouse_platform/test_l1_runtime_contracts.py\u0000tests/serving/test_control.py\u0000",
          "timed_out": false
        },
        {
          "args": [
            "uv",
            "lock",
            "--check"
          ],
          "duration_seconds": 0.094,
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
          "duration_seconds": 16.015,
          "exit_code": 0,
          "stderr": "",
          "stdout": "============================= test session starts =============================\nplatform win32 -- Python 3.12.13, pytest-9.0.3, pluggy-1.6.0\nrootdir: C:\\Users\\fyujv\\source\\repos\\olist-mds\nconfigfile: pyproject.toml\nplugins: anyio-4.13.0\ncollected 202 items\n\ntests\\cdc_contracts\\test_avro_helpers.py ..........                      [  4%]\ntests\\cdc_contracts\\test_connector_bootstrap.py ................         [ 12%]\ntests\\cdc_contracts\\test_entity_contracts.py ..............              [ 19%]\ntests\\cdc_contracts\\test_topics.py .......                               [ 23%]\ntests\\cdc_contracts\\test_writer_schemas.py ....                          [ 25%]\ntests\\lakehouse_platform\\test_l1_runtime_contracts.py ......             [ 28%]\ntests\\lakehouse_platform\\test_local_lab_live_readiness.py ...            [ 29%]\ntests\\lakehouse_platform\\test_local_lab_profile_boundaries.py .....      [ 32%]\ntests\\lakehouse_platform\\test_normalization_api.py ...                   [ 33%]\ntests\\lakehouse_platform\\test_polaris_admin_minio_contract.py ..         [ 34%]\ntests\\lakehouse_platform\\test_polaris_contract.py .......                [ 38%]\ntests\\lakehouse_platform\\test_polaris_credentials_projection.py ...      [ 39%]\ntests\\lakehouse_platform\\test_spark_config.py ....                       [ 41%]\ntests\\lakehouse_platform\\test_spark_image_contract.py .....              [ 44%]\ntests\\lakehouse_platform\\test_table_contracts.py .......                 [ 47%]\ntests\\mysql\\test_cli.py .......                                          [ 50%]\ntests\\mysql\\test_mysql_integration.py ss                                 [ 51%]\ntests\\mysql\\test_repository.py .................                         [ 60%]\ntests\\mysql\\test_seeding.py ......                                       [ 63%]\ntests\\mysql\\test_source_schema.py ............                           [ 69%]\ntests\\dbt_clickhouse\\test_dbt_parse.py .                                 [ 69%]\ntests\\dbt_clickhouse\\test_native_ddl_contract.py ........                [ 73%]\ntests\\dbt_clickhouse\\test_project_contract.py ......                     [ 76%]\ntests\\serving\\test_airflow_api.py .....                                  [ 79%]\ntests\\serving\\test_boundary.py ...........                               [ 84%]\ntests\\serving\\test_control.py ..                                         [ 85%]\ntests\\serving\\test_dbt_runner.py .                                       [ 86%]\ntests\\serving\\test_entities.py ...                                       [ 87%]\ntests\\stage_v\\test_stage_v_harness.py .....................              [ 98%]\ntests\\stage_v\\test_stage_v_oracles.py ....                               [100%]\n\n============================== warnings summary ===============================\n.venv\\Lib\\site-packages\\airflow\\__init__.py:47\n  C:\\Users\\fyujv\\source\\repos\\olist-mds\\.venv\\Lib\\site-packages\\airflow\\__init__.py:47: RuntimeWarning: Airflow currently can be run on POSIX-compliant Operating Systems. For development, it is regularly tested on fairly modern Linux Distros and recent versions of macOS. On Windows you can run it via WSL2 (Windows Subsystem for Linux 2) or via Linux Containers. The work to add Windows support is tracked via https://github.com/apache/airflow/issues/10388, but it is not a high priority.\n    warnings.warn(\n\n.venv\\Lib\\site-packages\\_pytest\\cacheprovider.py:475\n  C:\\Users\\fyujv\\source\\repos\\olist-mds\\.venv\\Lib\\site-packages\\_pytest\\cacheprovider.py:475: PytestCacheWarning: could not create cache path C:\\Users\\fyujv\\source\\repos\\olist-mds\\.pytest_cache\\v\\cache\\nodeids: [WinError 5] Access is denied: 'C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.pytest_cache\\\\v\\\\cache'\n    config.cache.set(\"cache/nodeids\", sorted(self.cached_nodeids))\n\n-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html\n================= 200 passed, 2 skipped, 2 warnings in 13.88s =================\n",
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
          "duration_seconds": 4.047,
          "exit_code": 0,
          "stderr": "#0 building with \"desktop-linux\" instance using docker driver\n\n#1 [internal] load build definition from Dockerfile\n#1 transferring dockerfile: 2.73kB 0.0s done\n#1 DONE 0.0s\n\n#2 resolve image config for docker-image://docker.io/docker/dockerfile:1.7\n#2 DONE 2.5s\n\n#3 docker-image://docker.io/docker/dockerfile:1.7@sha256:a57df69d0ea827fb7266491f2813635de6f17269be881f696fbfdf2d83dda33e\n#3 CACHED\n\n#4 [internal] load metadata for docker.io/apache/spark:4.1.3-scala2.13-java17-python3-ubuntu\n#4 DONE 0.0s\n\n#5 [internal] load metadata for docker.io/library/alpine:3.22.1\n#5 DONE 0.0s\n\n#6 [internal] load .dockerignore\n#6 transferring context: 1.74kB done\n#6 DONE 0.0s\n\n#7 [sbt-downloader 1/5] FROM docker.io/library/alpine:3.22.1\n#7 DONE 0.0s\n\n#8 [scala-builder 1/6] FROM docker.io/apache/spark:4.1.3-scala2.13-java17-python3-ubuntu\n#8 DONE 0.0s\n\n#9 [internal] load build context\n#9 transferring context: 88.33kB 0.2s done\n#9 DONE 0.2s\n\n#10 [sbt-downloader 3/5] COPY docker/spark/sbt-launch.sha256 /tmp/sbt-launch.sha256\n#10 CACHED\n\n#11 [scala-builder 5/6] WORKDIR /tmp/streaming/spark/scala\n#11 CACHED\n\n#12 [artifact-downloader 4/5] COPY docker/spark/download-jars.sh /usr/local/bin/download-jars\n#12 CACHED\n\n#13 [scala-builder 2/6] COPY --from=artifact-downloader /opt/olist/jars/ /opt/spark/jars/\n#13 CACHED\n\n#14 [artifact-downloader 5/5] RUN chmod 0555 /usr/local/bin/download-jars     && /usr/local/bin/download-jars /tmp/jars.sha256 /opt/olist/jars\n#14 CACHED\n\n#15 [sbt-downloader 4/5] COPY docker/spark/download-sbt-launch.sh /usr/local/bin/download-sbt-launch\n#15 CACHED\n\n#16 [sbt-downloader 5/5] RUN chmod 0555 /usr/local/bin/download-sbt-launch     && /usr/local/bin/download-sbt-launch /tmp/sbt-launch.sha256 /tmp/sbt-launcher\n#16 CACHED\n\n#17 [sbt-downloader 2/5] RUN apk add --no-cache ca-certificates wget\n#17 CACHED\n\n#18 [scala-builder 3/6] COPY --from=sbt-downloader /tmp/sbt-launcher/sbt-launch.jar /tmp/sbt-launch.jar\n#18 CACHED\n\n#19 [scala-builder 4/6] COPY streaming /tmp/streaming\n#19 CACHED\n\n#20 [artifact-downloader 3/5] COPY docker/spark/jars.sha256 /tmp/jars.sha256\n#20 CACHED\n\n#21 [scala-builder 6/6] RUN java -jar /tmp/sbt-launch.jar scalafmtCheckAll scalafmtSbtCheck Test/compile test package\n#21 CACHED\n\n#22 exporting to image\n#22 exporting layers done\n#22 writing image sha256:69461a632288844e72ce00384ed941e6cfd8a428c0b85e2aa8bf8fc15de46afb done\n#22 DONE 0.0s\n\nView build details: docker-desktop://dashboard/build/desktop-linux/desktop-linux/epwcje26d9e9xx0ifx0n9uqxz\n",
          "stdout": "",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 51.345,
      "gate": "00-preflight",
      "status": "PASS",
      "timestamp": "2026-08-04T15:38:48.587433+00:00"
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
      "timestamp": "2026-08-04T15:38:48.588837+00:00"
    },
    "02-clean-bootstrap": {
      "assertions": [
        {
          "detail": "{\"command\": \"reset\", \"scoped_to\": \"olist_stage_v\", \"status\": \"ready\"}",
          "name": "lab_reset",
          "status": "PASS"
        },
        {
          "detail": "{\"capture\": {\"capture_state\": \"captured\", \"contract_version\": 2}, \"command\": \"bootstrap\", \"readiness_level\": \"wave1_platform\", \"seed\": {\"archive\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\tests\\\\fixtures\\\\olist_small\\\\olist_small.zip\", \"exit_code\": 0, \"row_counts\": {\"customers\": 8, \"geolocation\": 6, \"order_items\": 16, \"order_payments\": 14, \"order_reviews\": 12, \"orders\": 12, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"run_id\": \"stage_l1_20260804_v6_seed_64afdd7955a5\"}, \"status\": \"ready\", \"validation\": {\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 216 packages in 1ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"ts/fixtures/<redacted>_small/README.md', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/fixtures/<redacted>_small/source_profile_small.json', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it\", \"exit_code\": 0, \"status\": \"passed\"}], \"status\": \"ready\"}}",
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
          "stage_l1_20260804_v6_seed_64afdd7955a5",
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
          "duration_seconds": 0.469,
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
            "stage_l1_20260804_v6_seed_64afdd7955a5",
            "--random-seed",
            "20260801"
          ],
          "duration_seconds": 312.25,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"capture\": {\"capture_state\": \"captured\", \"contract_version\": 2}, \"command\": \"bootstrap\", \"readiness_level\": \"wave1_platform\", \"seed\": {\"archive\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\tests\\\\fixtures\\\\olist_small\\\\olist_small.zip\", \"exit_code\": 0, \"row_counts\": {\"customers\": 8, \"geolocation\": 6, \"order_items\": 16, \"order_payments\": 14, \"order_reviews\": 12, \"orders\": 12, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"run_id\": \"stage_l1_20260804_v6_seed_64afdd7955a5\"}, \"status\": \"ready\", \"validation\": {\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 216 packages in 1ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"ts/fixtures/<redacted>_small/README.md', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/fixtures/<redacted>_small/source_profile_small.json', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it\", \"exit_code\": 0, \"status\": \"passed\"}], \"status\": \"ready\"}}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 312.708,
      "gate": "02-clean-bootstrap",
      "status": "PASS",
      "timestamp": "2026-08-04T15:44:01.298755+00:00"
    },
    "03-initial-snapshot": {
      "assertions": [
        {
          "detail": "{\"command\": \"start-streaming\", \"freshness_basis\": \"initial_start\", \"freshness_verified\": false, \"new_query_ids\": {\"bronze\": \"d900c364-cc51-42eb-9c68-36e15a344e2c\", \"silver\": \"1cea72e7-a4c5-4fc6-ba4e-6e4a535c8801,51b42e59-29c8-4f02-81ae-396ba858becc,589e5679-0a5d-4d76-81aa-d605ae8dcae8,a032893b-307a-42a7-9ebb-a8b3fda845f7,aecdb3fa-b438-4f7b-8135-617489a8f4d0,b2afdbb6-9b0d-4abc-8fc8-9b0a16d4c3e3,df64a116-32ff-464b-974c-2240b00a108c,ebb0b090-6ae1-42f0-8479-78a9ca17db47,f7adbce4-cbbd-4b9e-ac4f-e196b58564af,fcb11be6-c0ba-4f93-99f3-1fd2eb67ef30\"}, \"old_query_ids\": {}, \"restart_barrier_at_utc\": null, \"status\": \"ready\", \"status_files\": {\"bronze\": {\"query_count\": 1, \"updated_at_utc\": \"2026-08-04T15:46:10.913865354Z\"}, \"silver\": {\"query_count\": 10, \"updated_at_utc\": \"2026-08-04T15:46:27.467690554Z\"}}}",
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
                  "changes_snapshot_id": 4997046798937304080,
                  "entity": "customers",
                  "last_kafka_offset": 7,
                  "status": "COMMITTED"
                },
                "order_items": {
                  "changes_snapshot_id": 6203981237016326604,
                  "entity": "order_items",
                  "last_kafka_offset": 3,
                  "status": "COMMITTED"
                },
                "order_payments": {
                  "changes_snapshot_id": 3834667265461565431,
                  "entity": "order_payments",
                  "last_kafka_offset": 4,
                  "status": "COMMITTED"
                },
                "order_reviews": {
                  "changes_snapshot_id": 7769147630215613047,
                  "entity": "order_reviews",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "orders": {
                  "changes_snapshot_id": 8990242861401746456,
                  "entity": "orders",
                  "last_kafka_offset": 1,
                  "status": "COMMITTED"
                },
                "product_category_translation": {
                  "changes_snapshot_id": 4378261172774740424,
                  "entity": "product_category_translation",
                  "last_kafka_offset": 4,
                  "status": "COMMITTED"
                },
                "products": {
                  "changes_snapshot_id": 8405389069284592997,
                  "entity": "products",
                  "last_kafka_offset": 7,
                  "status": "COMMITTED"
                },
                "sellers": {
                  "changes_snapshot_id": 8065609369146321385,
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
          "duration_seconds": 151.234,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"start-streaming\", \"freshness_basis\": \"initial_start\", \"freshness_verified\": false, \"new_query_ids\": {\"bronze\": \"d900c364-cc51-42eb-9c68-36e15a344e2c\", \"silver\": \"1cea72e7-a4c5-4fc6-ba4e-6e4a535c8801,51b42e59-29c8-4f02-81ae-396ba858becc,589e5679-0a5d-4d76-81aa-d605ae8dcae8,a032893b-307a-42a7-9ebb-a8b3fda845f7,aecdb3fa-b438-4f7b-8135-617489a8f4d0,b2afdbb6-9b0d-4abc-8fc8-9b0a16d4c3e3,df64a116-32ff-464b-974c-2240b00a108c,ebb0b090-6ae1-42f0-8479-78a9ca17db47,f7adbce4-cbbd-4b9e-ac4f-e196b58564af,fcb11be6-c0ba-4f93-99f3-1fd2eb67ef30\"}, \"old_query_ids\": {}, \"restart_barrier_at_utc\": null, \"status\": \"ready\", \"status_files\": {\"bronze\": {\"query_count\": 1, \"updated_at_utc\": \"2026-08-04T15:46:10.913865354Z\"}, \"silver\": {\"query_count\": 10, \"updated_at_utc\": \"2026-08-04T15:46:27.467690554Z\"}}}\n",
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
          "duration_seconds": 106.469,
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
          "duration_seconds": 28.985,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"wait-caught-up\", \"status\": \"ready\"}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 290.904,
      "gate": "03-initial-snapshot",
      "status": "PASS",
      "timestamp": "2026-08-04T15:48:52.205839+00:00"
    },
    "04-crud-and-restart": {
      "assertions": [
        {
          "detail": "{\"command\": \"stop-streaming\", \"old_query_ids\": {\"bronze\": \"d900c364-cc51-42eb-9c68-36e15a344e2c\", \"silver\": \"1cea72e7-a4c5-4fc6-ba4e-6e4a535c8801,51b42e59-29c8-4f02-81ae-396ba858becc,589e5679-0a5d-4d76-81aa-d605ae8dcae8,a032893b-307a-42a7-9ebb-a8b3fda845f7,aecdb3fa-b438-4f7b-8135-617489a8f4d0,b2afdbb6-9b0d-4abc-8fc8-9b0a16d4c3e3,df64a116-32ff-464b-974c-2240b00a108c,ebb0b090-6ae1-42f0-8479-78a9ca17db47,f7adbce4-cbbd-4b9e-ac4f-e196b58564af,fcb11be6-c0ba-4f93-99f3-1fd2eb67ef30\"}, \"status\": \"ready\", \"status_files_removed\": true}",
          "name": "stop_spark_streaming",
          "status": "PASS"
        },
        {
          "detail": "Executed insert (8 statements), update (5 statements), delete (4 statements)",
          "name": "execute_crud_fixtures",
          "status": "PASS"
        },
        {
          "detail": "{\"command\": \"start-streaming\", \"freshness_basis\": \"status_updated_at_after_restart_barrier\", \"freshness_verified\": true, \"new_query_ids\": {\"bronze\": \"d900c364-cc51-42eb-9c68-36e15a344e2c\", \"silver\": \"1cea72e7-a4c5-4fc6-ba4e-6e4a535c8801,51b42e59-29c8-4f02-81ae-396ba858becc,589e5679-0a5d-4d76-81aa-d605ae8dcae8,a032893b-307a-42a7-9ebb-a8b3fda845f7,aecdb3fa-b438-4f7b-8135-617489a8f4d0,b2afdbb6-9b0d-4abc-8fc8-9b0a16d4c3e3,df64a116-32ff-464b-974c-2240b00a108c,ebb0b090-6ae1-42f0-8479-78a9ca17db47,f7adbce4-cbbd-4b9e-ac4f-e196b58564af,fcb11be6-c0ba-4f93-99f3-1fd2eb67ef30\"}, \"old_query_ids\": {\"bronze\": \"d900c364-cc51-42eb-9c68-36e15a344e2c\", \"silver\": \"1cea72e7-a4c5-4fc6-ba4e-6e4a535c8801,51b42e59-29c8-4f02-81ae-396ba858becc,589e5679-0a5d-4d76-81aa-d605ae8dcae8,a032893b-307a-42a7-9ebb-a8b3fda845f7,aecdb3fa-b438-4f7b-8135-617489a8f4d0,b2afdbb6-9b0d-4abc-8fc8-9b0a16d4c3e3,df64a116-32ff-464b-974c-2240b00a108c,ebb0b090-6ae1-42f0-8479-78a9ca17db47,f7adbce4-cbbd-4b9e-ac4f-e196b58564af,fcb11be6-c0ba-4f93-99f3-1fd2eb67ef30\"}, \"restart_barrier_at_utc\": \"2026-08-04T15:49:03.277670+00:00\", \"status\": \"ready\", \"status_files\": {\"bronze\": {\"query_count\": 1, \"updated_at_utc\": \"2026-08-04T15:51:26.892624957Z\"}, \"silver\": {\"query_count\": 10, \"updated_at_utc\": \"2026-08-04T15:51:37.432885505Z\"}}}",
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
          "duration_seconds": 11.11,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"stop-streaming\", \"old_query_ids\": {\"bronze\": \"d900c364-cc51-42eb-9c68-36e15a344e2c\", \"silver\": \"1cea72e7-a4c5-4fc6-ba4e-6e4a535c8801,51b42e59-29c8-4f02-81ae-396ba858becc,589e5679-0a5d-4d76-81aa-d605ae8dcae8,a032893b-307a-42a7-9ebb-a8b3fda845f7,aecdb3fa-b438-4f7b-8135-617489a8f4d0,b2afdbb6-9b0d-4abc-8fc8-9b0a16d4c3e3,df64a116-32ff-464b-974c-2240b00a108c,ebb0b090-6ae1-42f0-8479-78a9ca17db47,f7adbce4-cbbd-4b9e-ac4f-e196b58564af,fcb11be6-c0ba-4f93-99f3-1fd2eb67ef30\"}, \"status\": \"ready\", \"status_files_removed\": true}\n",
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
          "duration_seconds": 154.765,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"start-streaming\", \"freshness_basis\": \"status_updated_at_after_restart_barrier\", \"freshness_verified\": true, \"new_query_ids\": {\"bronze\": \"d900c364-cc51-42eb-9c68-36e15a344e2c\", \"silver\": \"1cea72e7-a4c5-4fc6-ba4e-6e4a535c8801,51b42e59-29c8-4f02-81ae-396ba858becc,589e5679-0a5d-4d76-81aa-d605ae8dcae8,a032893b-307a-42a7-9ebb-a8b3fda845f7,aecdb3fa-b438-4f7b-8135-617489a8f4d0,b2afdbb6-9b0d-4abc-8fc8-9b0a16d4c3e3,df64a116-32ff-464b-974c-2240b00a108c,ebb0b090-6ae1-42f0-8479-78a9ca17db47,f7adbce4-cbbd-4b9e-ac4f-e196b58564af,fcb11be6-c0ba-4f93-99f3-1fd2eb67ef30\"}, \"old_query_ids\": {\"bronze\": \"d900c364-cc51-42eb-9c68-36e15a344e2c\", \"silver\": \"1cea72e7-a4c5-4fc6-ba4e-6e4a535c8801,51b42e59-29c8-4f02-81ae-396ba858becc,589e5679-0a5d-4d76-81aa-d605ae8dcae8,a032893b-307a-42a7-9ebb-a8b3fda845f7,aecdb3fa-b438-4f7b-8135-617489a8f4d0,b2afdbb6-9b0d-4abc-8fc8-9b0a16d4c3e3,df64a116-32ff-464b-974c-2240b00a108c,ebb0b090-6ae1-42f0-8479-78a9ca17db47,f7adbce4-cbbd-4b9e-ac4f-e196b58564af,fcb11be6-c0ba-4f93-99f3-1fd2eb67ef30\"}, \"restart_barrier_at_utc\": \"2026-08-04T15:49:03.277670+00:00\", \"status\": \"ready\", \"status_files\": {\"bronze\": {\"query_count\": 1, \"updated_at_utc\": \"2026-08-04T15:51:26.892624957Z\"}, \"silver\": {\"query_count\": 10, \"updated_at_utc\": \"2026-08-04T15:51:37.432885505Z\"}}}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 166.325,
      "gate": "04-crud-and-restart",
      "status": "PASS",
      "timestamp": "2026-08-04T15:51:38.533679+00:00"
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
                  "changes_snapshot_id": 2101074686807524779,
                  "entity": "customers",
                  "last_kafka_offset": 8,
                  "status": "COMMITTED"
                },
                "order_items": {
                  "changes_snapshot_id": 7260055445008051617,
                  "entity": "order_items",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "order_payments": {
                  "changes_snapshot_id": 8604726252198231125,
                  "entity": "order_payments",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "order_reviews": {
                  "changes_snapshot_id": 5372656209178888275,
                  "entity": "order_reviews",
                  "last_kafka_offset": 2,
                  "status": "COMMITTED"
                },
                "orders": {
                  "changes_snapshot_id": 1034207959551505294,
                  "entity": "orders",
                  "last_kafka_offset": 3,
                  "status": "COMMITTED"
                },
                "product_category_translation": {
                  "changes_snapshot_id": 4378261172774740424,
                  "entity": "product_category_translation",
                  "last_kafka_offset": 4,
                  "status": "COMMITTED"
                },
                "products": {
                  "changes_snapshot_id": 8405389069284592997,
                  "entity": "products",
                  "last_kafka_offset": 7,
                  "status": "COMMITTED"
                },
                "sellers": {
                  "changes_snapshot_id": 8065609369146321385,
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
              "bronze": "d900c364-cc51-42eb-9c68-36e15a344e2c",
              "silver": "1cea72e7-a4c5-4fc6-ba4e-6e4a535c8801,51b42e59-29c8-4f02-81ae-396ba858becc,589e5679-0a5d-4d76-81aa-d605ae8dcae8,a032893b-307a-42a7-9ebb-a8b3fda845f7,aecdb3fa-b438-4f7b-8135-617489a8f4d0,b2afdbb6-9b0d-4abc-8fc8-9b0a16d4c3e3,df64a116-32ff-464b-974c-2240b00a108c,ebb0b090-6ae1-42f0-8479-78a9ca17db47,f7adbce4-cbbd-4b9e-ac4f-e196b58564af,fcb11be6-c0ba-4f93-99f3-1fd2eb67ef30"
            },
            "old_query_ids": {
              "bronze": "d900c364-cc51-42eb-9c68-36e15a344e2c",
              "silver": "1cea72e7-a4c5-4fc6-ba4e-6e4a535c8801,51b42e59-29c8-4f02-81ae-396ba858becc,589e5679-0a5d-4d76-81aa-d605ae8dcae8,a032893b-307a-42a7-9ebb-a8b3fda845f7,aecdb3fa-b438-4f7b-8135-617489a8f4d0,b2afdbb6-9b0d-4abc-8fc8-9b0a16d4c3e3,df64a116-32ff-464b-974c-2240b00a108c,ebb0b090-6ae1-42f0-8479-78a9ca17db47,f7adbce4-cbbd-4b9e-ac4f-e196b58564af,fcb11be6-c0ba-4f93-99f3-1fd2eb67ef30"
            },
            "restart_barrier_at_utc": "2026-08-04T15:49:03.277670+00:00",
            "status": "ready",
            "status_files": {
              "bronze": {
                "query_count": 1,
                "updated_at_utc": "2026-08-04T15:51:26.892624957Z"
              },
              "silver": {
                "query_count": 10,
                "updated_at_utc": "2026-08-04T15:51:37.432885505Z"
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
          "duration_seconds": 84.407,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"wait-caught-up\", \"status\": \"ready\"}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 88.157,
      "gate": "05-caught-up",
      "status": "PASS",
      "timestamp": "2026-08-04T15:53:06.692559+00:00"
    },
    "06-serving-sync": {
      "assertions": [
        {
          "detail": "{\"command\": \"start-serving\", \"profiles\": [\"platform\", \"serving\"], \"required_services\": [\"clickhouse\", \"airflow\"], \"status\": \"ready\"}",
          "name": "start_serving",
          "status": "PASS"
        },
        {
          "detail": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_l1_20260804_v6_crud_publish_64afdd7955a5\", \"dbt_result\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 1, \\\"sync_run_id\\\": \\\"sync-00000000000000000001\\\"}\"], \"exception\": null, \"results\": [{\"execution_time\": 0.16335201263427734, \"node\": \"stg_customers_current\", \"status\": \"success\"}, {\"execution_time\": 0.07895159721374512, \"node\": \"stg_customers_events\", \"status\": \"success\"}, {\"execution_time\": 0.10897231101989746, \"node\": \"stg_order_items_current\", \"status\": \"success\"}, {\"execution_time\": 0.10536766052246094, \"node\": \"stg_order_payments_current\", \"status\": \"success\"}, {\"execution_time\": 0.07300949096679688, \"node\": \"stg_orders_current\", \"status\": \"success\"}, {\"execution_time\": 0.10689949989318848, \"node\": \"stg_product_category_translation_events\", \"status\": \"success\"}, {\"execution_time\": 0.0819852352142334, \"node\": \"stg_products_events\", \"status\": \"success\"}, {\"execution_time\": 0.06784534454345703, \"node\": \"stg_sellers_current\", \"status\": \"success\"}, {\"execution_time\": 0.5991013050079346, \"node\": \"customer_scd2_collapses_identical_update_and_closes_on_delete\", \"status\": \"pass\"}, {\"execution_time\": 0.35622191429138184, \"node\": \"dim_customer_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.26253700256347656, \"node\": \"payment_allocation_is_proportional_at_item_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.35297584533691406, \"node\": \"zero_gross_order_has_null_payment_allocation\", \"status\": \"pass\"}, {\"execution_time\": 0.18056058883666992, \"node\": \"dim_date\", \"status\": \"success\"}, {\"execution_time\": 0.09459066390991211, \"node\": \"dim_order_status\", \"status\": \"success\"}, {\"execution_time\": 0.47009778022766113, \"node\": \"product_translation_does_not_resurrect_an_old_category\", \"status\": \"pass\"}, {\"execution_time\": 0.23499059677124023, \"node\": \"dim_product_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.11588597297668457, \"node\": \"dim_seller\", \"status\": \"success\"}, {\"execution_time\": 0.10479068756103516, \"node\": \"assert_customer_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.047231435775756836, \"node\": \"candidate_not_null_dim_customer_scd2_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04086899757385254, \"node\": \"candidate_not_null_dim_customer_scd2_customer_unique_id\", \"status\": \"pass\"}, {\"execution_time\": 0.0394587516784668, \"node\": \"candidate_not_null_dim_customer_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.04480624198913574, \"node\": \"unique_combination_of_columns_dim_customer_scd2_sync_run_seq__customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.06540608406066895, \"node\": \"assert_payment_allocations_balance\", \"status\": \"pass\"}, {\"execution_time\": 0.038781166076660156, \"node\": \"candidate_not_null_dim_date_date_day\", \"status\": \"pass\"}, {\"execution_time\": 0.038831233978271484, \"node\": \"candidate_not_null_dim_date_date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04087066650390625, \"node\": \"candidate_not_null_dim_date_sync_run_seq\", \"status\": \"pass\"}, {\"execution_time\": 0.052419424057006836, \"node\": \"unique_combination_of_columns_dim_date_sync_run_seq__date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05044889450073242, \"node\": \"candidate_not_null_dim_order_status_order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.04595637321472168, \"node\": \"candidate_not_null_dim_order_status_order_status_key\", \"status\": \"pass\"}, {\"execution_time\": 0.0617983341217041, \"node\": \"unique_combination_of_columns_dim_order_status_sync_run_seq__order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.0554049015045166, \"node\": \"assert_product_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.04609513282775879, \"node\": \"candidate_not_null_dim_product_scd2_product_id\", \"status\": \"pass\"}, {\"execution_time\": 0.042207956314086914, \"node\": \"candidate_not_null_dim_product_scd2_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05921602249145508, \"node\": \"candidate_not_null_dim_product_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.05939292907714844, \"node\": \"unique_combination_of_columns_dim_product_scd2_sync_run_seq__product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05300140380859375, \"node\": \"candidate_not_null_dim_seller_seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.04585146903991699, \"node\": \"candidate_not_null_dim_seller_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04691290855407715, \"node\": \"unique_combination_of_columns_dim_seller_sync_run_seq__seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.5423080921173096, \"node\": \"fact_order_items\", \"status\": \"success\"}, {\"execution_time\": 0.04485344886779785, \"node\": \"assert_fact_order_items_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.04673027992248535, \"node\": \"candidate_not_null_fact_order_items_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04409456253051758, \"node\": \"candidate_not_null_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.047715187072753906, \"node\": \"candidate_not_null_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.05735158920288086, \"node\": \"candidate_not_null_fact_order_items_order_item_key\", \"status\": \"pass\"}, {\"execution_time\": 0.142503023147583, \"node\": \"candidate_not_null_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.05195283889770508, \"node\": \"candidate_not_null_fact_order_items_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.049108266830444336, \"node\": \"candidate_not_null_fact_order_items_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.06205248832702637, \"node\": \"candidate_relationships_fact_order_items_customer_key__customer_key__ref_dim_customer_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.06219816207885742, \"node\": \"candidate_relationships_fact_order_items_product_key__product_key__ref_dim_product_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.06193876266479492, \"node\": \"candidate_relationships_fact_order_items_seller_key__seller_key__ref_dim_seller_\", \"status\": \"pass\"}, {\"execution_time\": 0.05310964584350586, \"node\": \"non_negative_fact_order_items_allocated_payment_value\", \"status\": \"pass\"}, {\"execution_time\": 0.05081605911254883, \"node\": \"non_negative_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.05236077308654785, \"node\": \"non_negative_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.05789446830749512, \"node\": \"non_negative_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.04750370979309082, \"node\": \"unique_combination_of_columns_fact_order_items_sync_run_seq__order_id__order_item_id\", \"status\": \"pass\"}, {\"execution_time\": 0.10718512535095215, \"node\": \"mart_daily_revenue\", \"status\": \"success\"}, {\"execution_time\": 0.12667202949523926, \"node\": \"mart_monthly_arpu\", \"status\": \"success\"}, {\"execution_time\": 0.04152989387512207, \"node\": \"assert_daily_revenue_components\", \"status\": \"pass\"}, {\"execution_time\": 0.04152822494506836, \"node\": \"candidate_not_null_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.046202898025512695, \"node\": \"candidate_not_null_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04314446449279785, \"node\": \"candidate_not_null_mart_daily_revenue_order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.0457150936126709, \"node\": \"candidate_not_null_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.042151451110839844, \"node\": \"non_negative_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.043474435806274414, \"node\": \"non_negative_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04642772674560547, \"node\": \"non_negative_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.04214811325073242, \"node\": \"unique_combination_of_columns_mart_daily_revenue_sync_run_seq__order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.05444955825805664, \"node\": \"assert_monthly_arpu_formulas\", \"status\": \"pass\"}, {\"execution_time\": 0.047429561614990234, \"node\": \"candidate_not_null_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.04909920692443848, \"node\": \"candidate_not_null_mart_monthly_arpu_order_month\", \"status\": \"pass\"}, {\"execution_time\": 0.04603767395019531, \"node\": \"candidate_not_null_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.04693961143493652, \"node\": \"candidate_not_null_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04758715629577637, \"node\": \"non_negative_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.04490351676940918, \"node\": \"non_negative_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.04301285743713379, \"node\": \"non_negative_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.045908451080322266, \"node\": \"unique_combination_of_columns_mart_monthly_arpu_sync_run_seq__order_month\", \"status\": \"pass\"}], \"selector\": \"serving_candidate\", \"status_counts\": {\"pass\": 59, \"success\": 16}, \"success\": true, \"vars\": {\"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1}}, \"expected_entity_counts\": {\"customers\": 9, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 89, \"iceberg_snapshot_ids\": {\"customers\": 2101074686807524779, \"order_items\": 7260055445008051617, \"order_payments\": 8604726252198231125, \"order_reviews\": 5372656209178888275, \"orders\": 1034207959551505294, \"product_category_translation\": 4378261172774740424, \"products\": 8405389069284592997, \"sellers\": 8065609369146321385}, \"is_noop\": false, \"materialized_entity_counts\": {\"customers\": 9, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"materialized_event_count\": 89, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1, \"sync_run_status\": \"SUCCEEDED\", \"target_offsets\": {\"olist_cdc.olist_oltp.customers:0\": 8, \"olist_cdc.olist_oltp.order_items:0\": 5, \"olist_cdc.olist_oltp.order_items:1\": 5, \"olist_cdc.olist_oltp.order_items:2\": 6, \"olist_cdc.olist_oltp.order_payments:0\": 5, \"olist_cdc.olist_oltp.order_payments:1\": 4, \"olist_cdc.olist_oltp.order_payments:2\": 4, \"olist_cdc.olist_oltp.order_reviews:0\": 5, \"olist_cdc.olist_oltp.order_reviews:1\": 4, \"olist_cdc.olist_oltp.order_reviews:2\": 2, \"olist_cdc.olist_oltp.orders:0\": 3, \"olist_cdc.olist_oltp.orders:1\": 4, \"olist_cdc.olist_oltp.orders:2\": 4, \"olist_cdc.olist_oltp.product_category_translation:0\": 4, \"olist_cdc.olist_oltp.products:0\": 7, \"olist_cdc.olist_oltp.sellers:0\": 3}, \"target_transaction_id\": \"file=binlog.000002,pos=17636\"}",
          "name": "sync_serving_crud",
          "status": "PASS"
        },
        {
          "detail": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_l1_20260804_v6_crud_repeat_64afdd7955a5\", \"dbt_result\": null, \"expected_entity_counts\": {\"customers\": 0, \"order_items\": 0, \"order_payments\": 0, \"order_reviews\": 0, \"orders\": 0, \"product_category_translation\": 0, \"products\": 0, \"sellers\": 0}, \"expected_event_count\": 0, \"iceberg_snapshot_ids\": {\"customers\": 2101074686807524779, \"order_items\": 7260055445008051617, \"order_payments\": 8604726252198231125, \"order_reviews\": 5372656209178888275, \"orders\": 1034207959551505294, \"product_category_translation\": 4378261172774740424, \"products\": 8405389069284592997, \"sellers\": 8065609369146321385}, \"is_noop\": true, \"materialized_entity_counts\": {\"customers\": 0, \"order_items\": 0, \"order_payments\": 0, \"order_reviews\": 0, \"orders\": 0, \"product_category_translation\": 0, \"products\": 0, \"sellers\": 0}, \"materialized_event_count\": 0, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000002\", \"sync_run_seq\": 2, \"sync_run_status\": \"NOOP\", \"target_offsets\": {}, \"target_transaction_id\": \"file=binlog.000002,pos=17636\"}",
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
          "stage_l1_20260804_v6_crud_publish_64afdd7955a5",
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
          "stage_l1_20260804_v6_crud_repeat_64afdd7955a5",
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
          "duration_seconds": 202.906,
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
            "stage_l1_20260804_v6_crud_publish_64afdd7955a5",
            "--timeout",
            "1800"
          ],
          "duration_seconds": 32.766,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_l1_20260804_v6_crud_publish_64afdd7955a5\", \"dbt_result\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 1, \\\"sync_run_id\\\": \\\"sync-00000000000000000001\\\"}\"], \"exception\": null, \"results\": [{\"execution_time\": 0.16335201263427734, \"node\": \"stg_customers_current\", \"status\": \"success\"}, {\"execution_time\": 0.07895159721374512, \"node\": \"stg_customers_events\", \"status\": \"success\"}, {\"execution_time\": 0.10897231101989746, \"node\": \"stg_order_items_current\", \"status\": \"success\"}, {\"execution_time\": 0.10536766052246094, \"node\": \"stg_order_payments_current\", \"status\": \"success\"}, {\"execution_time\": 0.07300949096679688, \"node\": \"stg_orders_current\", \"status\": \"success\"}, {\"execution_time\": 0.10689949989318848, \"node\": \"stg_product_category_translation_events\", \"status\": \"success\"}, {\"execution_time\": 0.0819852352142334, \"node\": \"stg_products_events\", \"status\": \"success\"}, {\"execution_time\": 0.06784534454345703, \"node\": \"stg_sellers_current\", \"status\": \"success\"}, {\"execution_time\": 0.5991013050079346, \"node\": \"customer_scd2_collapses_identical_update_and_closes_on_delete\", \"status\": \"pass\"}, {\"execution_time\": 0.35622191429138184, \"node\": \"dim_customer_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.26253700256347656, \"node\": \"payment_allocation_is_proportional_at_item_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.35297584533691406, \"node\": \"zero_gross_order_has_null_payment_allocation\", \"status\": \"pass\"}, {\"execution_time\": 0.18056058883666992, \"node\": \"dim_date\", \"status\": \"success\"}, {\"execution_time\": 0.09459066390991211, \"node\": \"dim_order_status\", \"status\": \"success\"}, {\"execution_time\": 0.47009778022766113, \"node\": \"product_translation_does_not_resurrect_an_old_category\", \"status\": \"pass\"}, {\"execution_time\": 0.23499059677124023, \"node\": \"dim_product_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.11588597297668457, \"node\": \"dim_seller\", \"status\": \"success\"}, {\"execution_time\": 0.10479068756103516, \"node\": \"assert_customer_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.047231435775756836, \"node\": \"candidate_not_null_dim_customer_scd2_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04086899757385254, \"node\": \"candidate_not_null_dim_customer_scd2_customer_unique_id\", \"status\": \"pass\"}, {\"execution_time\": 0.0394587516784668, \"node\": \"candidate_not_null_dim_customer_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.04480624198913574, \"node\": \"unique_combination_of_columns_dim_customer_scd2_sync_run_seq__customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.06540608406066895, \"node\": \"assert_payment_allocations_balance\", \"status\": \"pass\"}, {\"execution_time\": 0.038781166076660156, \"node\": \"candidate_not_null_dim_date_date_day\", \"status\": \"pass\"}, {\"execution_time\": 0.038831233978271484, \"node\": \"candidate_not_null_dim_date_date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04087066650390625, \"node\": \"candidate_not_null_dim_date_sync_run_seq\", \"status\": \"pass\"}, {\"execution_time\": 0.052419424057006836, \"node\": \"unique_combination_of_columns_dim_date_sync_run_seq__date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05044889450073242, \"node\": \"candidate_not_null_dim_order_status_order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.04595637321472168, \"node\": \"candidate_not_null_dim_order_status_order_status_key\", \"status\": \"pass\"}, {\"execution_time\": 0.0617983341217041, \"node\": \"unique_combination_of_columns_dim_order_status_sync_run_seq__order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.0554049015045166, \"node\": \"assert_product_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.04609513282775879, \"node\": \"candidate_not_null_dim_product_scd2_product_id\", \"status\": \"pass\"}, {\"execution_time\": 0.042207956314086914, \"node\": \"candidate_not_null_dim_product_scd2_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05921602249145508, \"node\": \"candidate_not_null_dim_product_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.05939292907714844, \"node\": \"unique_combination_of_columns_dim_product_scd2_sync_run_seq__product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05300140380859375, \"node\": \"candidate_not_null_dim_seller_seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.04585146903991699, \"node\": \"candidate_not_null_dim_seller_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04691290855407715, \"node\": \"unique_combination_of_columns_dim_seller_sync_run_seq__seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.5423080921173096, \"node\": \"fact_order_items\", \"status\": \"success\"}, {\"execution_time\": 0.04485344886779785, \"node\": \"assert_fact_order_items_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.04673027992248535, \"node\": \"candidate_not_null_fact_order_items_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.04409456253051758, \"node\": \"candidate_not_null_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.047715187072753906, \"node\": \"candidate_not_null_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.05735158920288086, \"node\": \"candidate_not_null_fact_order_items_order_item_key\", \"status\": \"pass\"}, {\"execution_time\": 0.142503023147583, \"node\": \"candidate_not_null_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.05195283889770508, \"node\": \"candidate_not_null_fact_order_items_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.049108266830444336, \"node\": \"candidate_not_null_fact_order_items_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.06205248832702637, \"node\": \"candidate_relationships_fact_order_items_customer_key__customer_key__ref_dim_customer_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.06219816207885742, \"node\": \"candidate_relationships_fact_order_items_product_key__product_key__ref_dim_product_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.06193876266479492, \"node\": \"candidate_relationships_fact_order_items_seller_key__seller_key__ref_dim_seller_\", \"status\": \"pass\"}, {\"execution_time\": 0.05310964584350586, \"node\": \"non_negative_fact_order_items_allocated_payment_value\", \"status\": \"pass\"}, {\"execution_time\": 0.05081605911254883, \"node\": \"non_negative_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.05236077308654785, \"node\": \"non_negative_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.05789446830749512, \"node\": \"non_negative_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.04750370979309082, \"node\": \"unique_combination_of_columns_fact_order_items_sync_run_seq__order_id__order_item_id\", \"status\": \"pass\"}, {\"execution_time\": 0.10718512535095215, \"node\": \"mart_daily_revenue\", \"status\": \"success\"}, {\"execution_time\": 0.12667202949523926, \"node\": \"mart_monthly_arpu\", \"status\": \"success\"}, {\"execution_time\": 0.04152989387512207, \"node\": \"assert_daily_revenue_components\", \"status\": \"pass\"}, {\"execution_time\": 0.04152822494506836, \"node\": \"candidate_not_null_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.046202898025512695, \"node\": \"candidate_not_null_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04314446449279785, \"node\": \"candidate_not_null_mart_daily_revenue_order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.0457150936126709, \"node\": \"candidate_not_null_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.042151451110839844, \"node\": \"non_negative_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.043474435806274414, \"node\": \"non_negative_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04642772674560547, \"node\": \"non_negative_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.04214811325073242, \"node\": \"unique_combination_of_columns_mart_daily_revenue_sync_run_seq__order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.05444955825805664, \"node\": \"assert_monthly_arpu_formulas\", \"status\": \"pass\"}, {\"execution_time\": 0.047429561614990234, \"node\": \"candidate_not_null_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.04909920692443848, \"node\": \"candidate_not_null_mart_monthly_arpu_order_month\", \"status\": \"pass\"}, {\"execution_time\": 0.04603767395019531, \"node\": \"candidate_not_null_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.04693961143493652, \"node\": \"candidate_not_null_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.04758715629577637, \"node\": \"non_negative_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.04490351676940918, \"node\": \"non_negative_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.04301285743713379, \"node\": \"non_negative_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.045908451080322266, \"node\": \"unique_combination_of_columns_mart_monthly_arpu_sync_run_seq__order_month\", \"status\": \"pass\"}], \"selector\": \"serving_candidate\", \"status_counts\": {\"pass\": 59, \"success\": 16}, \"success\": true, \"vars\": {\"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1}}, \"expected_entity_counts\": {\"customers\": 9, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 89, \"iceberg_snapshot_ids\": {\"customers\": 2101074686807524779, \"order_items\": 7260055445008051617, \"order_payments\": 8604726252198231125, \"order_reviews\": 5372656209178888275, \"orders\": 1034207959551505294, \"product_category_translation\": 4378261172774740424, \"products\": 8405389069284592997, \"sellers\": 8065609369146321385}, \"is_noop\": false, \"materialized_entity_counts\": {\"customers\": 9, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"materialized_event_count\": 89, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1, \"sync_run_status\": \"SUCCEEDED\", \"target_offsets\": {\"olist_cdc.olist_oltp.customers:0\": 8, \"olist_cdc.olist_oltp.order_items:0\": 5, \"olist_cdc.olist_oltp.order_items:1\": 5, \"olist_cdc.olist_oltp.order_items:2\": 6, \"olist_cdc.olist_oltp.order_payments:0\": 5, \"olist_cdc.olist_oltp.order_payments:1\": 4, \"olist_cdc.olist_oltp.order_payments:2\": 4, \"olist_cdc.olist_oltp.order_reviews:0\": 5, \"olist_cdc.olist_oltp.order_reviews:1\": 4, \"olist_cdc.olist_oltp.order_reviews:2\": 2, \"olist_cdc.olist_oltp.orders:0\": 3, \"olist_cdc.olist_oltp.orders:1\": 4, \"olist_cdc.olist_oltp.orders:2\": 4, \"olist_cdc.olist_oltp.product_category_translation:0\": 4, \"olist_cdc.olist_oltp.products:0\": 7, \"olist_cdc.olist_oltp.sellers:0\": 3}, \"target_transaction_id\": \"file=binlog.000002,pos=17636\"}\n",
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
            "stage_l1_20260804_v6_crud_repeat_64afdd7955a5",
            "--timeout",
            "1800"
          ],
          "duration_seconds": 5.875,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_l1_20260804_v6_crud_repeat_64afdd7955a5\", \"dbt_result\": null, \"expected_entity_counts\": {\"customers\": 0, \"order_items\": 0, \"order_payments\": 0, \"order_reviews\": 0, \"orders\": 0, \"product_category_translation\": 0, \"products\": 0, \"sellers\": 0}, \"expected_event_count\": 0, \"iceberg_snapshot_ids\": {\"customers\": 2101074686807524779, \"order_items\": 7260055445008051617, \"order_payments\": 8604726252198231125, \"order_reviews\": 5372656209178888275, \"orders\": 1034207959551505294, \"product_category_translation\": 4378261172774740424, \"products\": 8405389069284592997, \"sellers\": 8065609369146321385}, \"is_noop\": true, \"materialized_entity_counts\": {\"customers\": 0, \"order_items\": 0, \"order_payments\": 0, \"order_reviews\": 0, \"orders\": 0, \"product_category_translation\": 0, \"products\": 0, \"sellers\": 0}, \"materialized_event_count\": 0, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000002\", \"sync_run_seq\": 2, \"sync_run_status\": \"NOOP\", \"target_offsets\": {}, \"target_transaction_id\": \"file=binlog.000002,pos=17636\"}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 241.568,
      "gate": "06-serving-sync",
      "status": "PASS",
      "timestamp": "2026-08-04T15:57:08.263565+00:00"
    },
    "07-dbt-and-stable-views": {
      "assertions": [
        {
          "detail": "{\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 216 packages in 2ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"ts/fixtures/<redacted>_small/README.md', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/fixtures/<redacted>_small/source_profile_small.json', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"All checks passed!\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"93 files already formatted\", \"exit_code\": 0, \"status\": \"passed\"}], \"command\": \"validate\", \"status\": \"ready\"}",
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
                "candidate": 10,
                "stable": 10
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
                  "diagnostic": "ts/fixtures/<redacted>_small/README.md', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/fixtures/<redacted>_small/source_profile_small.json', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it",
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
                  "diagnostic": "93 files already formatted",
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
          "duration_seconds": 1.875,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 216 packages in 2ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"ts/fixtures/<redacted>_small/README.md', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/fixtures/<redacted>_small/source_profile_small.json', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"All checks passed!\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"93 files already formatted\", \"exit_code\": 0, \"status\": \"passed\"}], \"command\": \"validate\", \"status\": \"ready\"}\n",
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
          "duration_seconds": 3.797,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"validate-serving\", \"current_views\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"dbt\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 1, \\\"sync_run_id\\\": \\\"sync-00000000000000000001\\\"}\"], \"result_count\": 75, \"status_counts\": {\"pass\": 59, \"success\": 16}}, \"gold_views\": {\"dim_customer_scd2\": {\"candidate\": 7, \"stable\": 7}, \"dim_date\": {\"candidate\": 46, \"stable\": 46}, \"dim_order_status\": {\"candidate\": 2, \"stable\": 2}, \"dim_product_scd2\": {\"candidate\": 10, \"stable\": 10}, \"dim_seller\": {\"candidate\": 4, \"stable\": 4}, \"fact_order_items\": {\"candidate\": 18, \"stable\": 18}, \"mart_daily_revenue\": {\"candidate\": 13, \"stable\": 13}, \"mart_monthly_arpu\": {\"candidate\": 7, \"stable\": 7}}, \"static_validation\": {\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 216 packages in 1ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"ts/fixtures/<redacted>_small/README.md', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/fixtures/<redacted>_small/source_profile_small.json', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"All checks passed!\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"93 files already formatted\", \"exit_code\": 0, \"status\": \"passed\"}], \"status\": \"ready\"}, \"status\": \"ready\", \"sync_run_id\": \"sync-00000000000000000001\", \"sync_run_seq\": 1}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 5.679,
      "gate": "07-dbt-and-stable-views",
      "status": "PASS",
      "timestamp": "2026-08-04T15:57:13.947256+00:00"
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
          "detail": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_l1_20260804_v6_schema_publish_64afdd7955a5\", \"dbt_result\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 3, \\\"sync_run_id\\\": \\\"sync-00000000000000000003\\\"}\"], \"exception\": null, \"results\": [{\"execution_time\": 0.2090756893157959, \"node\": \"stg_customers_current\", \"status\": \"success\"}, {\"execution_time\": 0.08597350120544434, \"node\": \"stg_customers_events\", \"status\": \"success\"}, {\"execution_time\": 0.09011292457580566, \"node\": \"stg_order_items_current\", \"status\": \"success\"}, {\"execution_time\": 0.07588934898376465, \"node\": \"stg_order_payments_current\", \"status\": \"success\"}, {\"execution_time\": 0.060515403747558594, \"node\": \"stg_orders_current\", \"status\": \"success\"}, {\"execution_time\": 0.061234474182128906, \"node\": \"stg_product_category_translation_events\", \"status\": \"success\"}, {\"execution_time\": 0.05806851387023926, \"node\": \"stg_products_events\", \"status\": \"success\"}, {\"execution_time\": 0.06110262870788574, \"node\": \"stg_sellers_current\", \"status\": \"success\"}, {\"execution_time\": 0.3662240505218506, \"node\": \"customer_scd2_collapses_identical_update_and_closes_on_delete\", \"status\": \"pass\"}, {\"execution_time\": 0.29740285873413086, \"node\": \"dim_customer_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.21623802185058594, \"node\": \"payment_allocation_is_proportional_at_item_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.18890762329101562, \"node\": \"zero_gross_order_has_null_payment_allocation\", \"status\": \"pass\"}, {\"execution_time\": 0.22670245170593262, \"node\": \"dim_date\", \"status\": \"success\"}, {\"execution_time\": 0.1566009521484375, \"node\": \"dim_order_status\", \"status\": \"success\"}, {\"execution_time\": 0.47406888008117676, \"node\": \"product_translation_does_not_resurrect_an_old_category\", \"status\": \"pass\"}, {\"execution_time\": 0.24090909957885742, \"node\": \"dim_product_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.1720411777496338, \"node\": \"dim_seller\", \"status\": \"success\"}, {\"execution_time\": 0.08452057838439941, \"node\": \"assert_customer_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.04116320610046387, \"node\": \"candidate_not_null_dim_customer_scd2_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.051149845123291016, \"node\": \"candidate_not_null_dim_customer_scd2_customer_unique_id\", \"status\": \"pass\"}, {\"execution_time\": 0.055173397064208984, \"node\": \"candidate_not_null_dim_customer_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.0619044303894043, \"node\": \"unique_combination_of_columns_dim_customer_scd2_sync_run_seq__customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.0932919979095459, \"node\": \"assert_payment_allocations_balance\", \"status\": \"pass\"}, {\"execution_time\": 0.04244732856750488, \"node\": \"candidate_not_null_dim_date_date_day\", \"status\": \"pass\"}, {\"execution_time\": 0.05323028564453125, \"node\": \"candidate_not_null_dim_date_date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05259084701538086, \"node\": \"candidate_not_null_dim_date_sync_run_seq\", \"status\": \"pass\"}, {\"execution_time\": 0.0758354663848877, \"node\": \"unique_combination_of_columns_dim_date_sync_run_seq__date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05667757987976074, \"node\": \"candidate_not_null_dim_order_status_order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.0515444278717041, \"node\": \"candidate_not_null_dim_order_status_order_status_key\", \"status\": \"pass\"}, {\"execution_time\": 0.050505638122558594, \"node\": \"unique_combination_of_columns_dim_order_status_sync_run_seq__order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.07617783546447754, \"node\": \"assert_product_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.06236839294433594, \"node\": \"candidate_not_null_dim_product_scd2_product_id\", \"status\": \"pass\"}, {\"execution_time\": 0.060146331787109375, \"node\": \"candidate_not_null_dim_product_scd2_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.060446739196777344, \"node\": \"candidate_not_null_dim_product_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.1657543182373047, \"node\": \"unique_combination_of_columns_dim_product_scd2_sync_run_seq__product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05002546310424805, \"node\": \"candidate_not_null_dim_seller_seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.052121877670288086, \"node\": \"candidate_not_null_dim_seller_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05554795265197754, \"node\": \"unique_combination_of_columns_dim_seller_sync_run_seq__seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.9753568172454834, \"node\": \"fact_order_items\", \"status\": \"success\"}, {\"execution_time\": 0.1531062126159668, \"node\": \"assert_fact_order_items_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.12785863876342773, \"node\": \"candidate_not_null_fact_order_items_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.08735466003417969, \"node\": \"candidate_not_null_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.08636736869812012, \"node\": \"candidate_not_null_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.07675027847290039, \"node\": \"candidate_not_null_fact_order_items_order_item_key\", \"status\": \"pass\"}, {\"execution_time\": 0.09600186347961426, \"node\": \"candidate_not_null_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.06660008430480957, \"node\": \"candidate_not_null_fact_order_items_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.06977295875549316, \"node\": \"candidate_not_null_fact_order_items_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.08321452140808105, \"node\": \"candidate_relationships_fact_order_items_customer_key__customer_key__ref_dim_customer_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.09178566932678223, \"node\": \"candidate_relationships_fact_order_items_product_key__product_key__ref_dim_product_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.0696859359741211, \"node\": \"candidate_relationships_fact_order_items_seller_key__seller_key__ref_dim_seller_\", \"status\": \"pass\"}, {\"execution_time\": 0.07352471351623535, \"node\": \"non_negative_fact_order_items_allocated_payment_value\", \"status\": \"pass\"}, {\"execution_time\": 0.0540158748626709, \"node\": \"non_negative_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.0461726188659668, \"node\": \"non_negative_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.04985308647155762, \"node\": \"non_negative_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.05977940559387207, \"node\": \"unique_combination_of_columns_fact_order_items_sync_run_seq__order_id__order_item_id\", \"status\": \"pass\"}, {\"execution_time\": 0.17527222633361816, \"node\": \"mart_daily_revenue\", \"status\": \"success\"}, {\"execution_time\": 0.1535196304321289, \"node\": \"mart_monthly_arpu\", \"status\": \"success\"}, {\"execution_time\": 0.04846310615539551, \"node\": \"assert_daily_revenue_components\", \"status\": \"pass\"}, {\"execution_time\": 0.045552968978881836, \"node\": \"candidate_not_null_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.06228828430175781, \"node\": \"candidate_not_null_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.05558180809020996, \"node\": \"candidate_not_null_mart_daily_revenue_order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.10495328903198242, \"node\": \"candidate_not_null_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.08288860321044922, \"node\": \"non_negative_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.10504293441772461, \"node\": \"non_negative_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.06905198097229004, \"node\": \"non_negative_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.0594325065612793, \"node\": \"unique_combination_of_columns_mart_daily_revenue_sync_run_seq__order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.06436514854431152, \"node\": \"assert_monthly_arpu_formulas\", \"status\": \"pass\"}, {\"execution_time\": 0.06229066848754883, \"node\": \"candidate_not_null_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.06270694732666016, \"node\": \"candidate_not_null_mart_monthly_arpu_order_month\", \"status\": \"pass\"}, {\"execution_time\": 0.0452425479888916, \"node\": \"candidate_not_null_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.04958653450012207, \"node\": \"candidate_not_null_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.059821128845214844, \"node\": \"non_negative_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.07184672355651855, \"node\": \"non_negative_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.0551760196685791, \"node\": \"non_negative_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.049199819564819336, \"node\": \"unique_combination_of_columns_mart_monthly_arpu_sync_run_seq__order_month\", \"status\": \"pass\"}], \"selector\": \"serving_candidate\", \"status_counts\": {\"pass\": 59, \"success\": 16}, \"success\": true, \"vars\": {\"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3}}, \"expected_entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 90, \"iceberg_snapshot_ids\": {\"customers\": 5661301511364570764, \"order_items\": 7260055445008051617, \"order_payments\": 8604726252198231125, \"order_reviews\": 5372656209178888275, \"orders\": 1034207959551505294, \"product_category_translation\": 4378261172774740424, \"products\": 8405389069284592997, \"sellers\": 8065609369146321385}, \"is_noop\": false, \"materialized_entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"materialized_event_count\": 90, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3, \"sync_run_status\": \"SUCCEEDED\", \"target_offsets\": {\"olist_cdc.olist_oltp.customers:0\": 9, \"olist_cdc.olist_oltp.order_items:0\": 5, \"olist_cdc.olist_oltp.order_items:1\": 5, \"olist_cdc.olist_oltp.order_items:2\": 6, \"olist_cdc.olist_oltp.order_payments:0\": 5, \"olist_cdc.olist_oltp.order_payments:1\": 4, \"olist_cdc.olist_oltp.order_payments:2\": 4, \"olist_cdc.olist_oltp.order_reviews:0\": 5, \"olist_cdc.olist_oltp.order_reviews:1\": 4, \"olist_cdc.olist_oltp.order_reviews:2\": 2, \"olist_cdc.olist_oltp.orders:0\": 3, \"olist_cdc.olist_oltp.orders:1\": 4, \"olist_cdc.olist_oltp.orders:2\": 4, \"olist_cdc.olist_oltp.product_category_translation:0\": 4, \"olist_cdc.olist_oltp.products:0\": 7, \"olist_cdc.olist_oltp.sellers:0\": 3}, \"target_transaction_id\": \"file=binlog.000002,pos=21950\"}",
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
              "transaction_id": "file=binlog.000002,pos=21950",
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
                  "changes_snapshot_id": 5661301511364570764,
                  "entity": "customers",
                  "last_kafka_offset": 9,
                  "status": "COMMITTED"
                },
                "order_items": {
                  "changes_snapshot_id": 7260055445008051617,
                  "entity": "order_items",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "order_payments": {
                  "changes_snapshot_id": 8604726252198231125,
                  "entity": "order_payments",
                  "last_kafka_offset": 5,
                  "status": "COMMITTED"
                },
                "order_reviews": {
                  "changes_snapshot_id": 5372656209178888275,
                  "entity": "order_reviews",
                  "last_kafka_offset": 2,
                  "status": "COMMITTED"
                },
                "orders": {
                  "changes_snapshot_id": 1034207959551505294,
                  "entity": "orders",
                  "last_kafka_offset": 3,
                  "status": "COMMITTED"
                },
                "product_category_translation": {
                  "changes_snapshot_id": 4378261172774740424,
                  "entity": "product_category_translation",
                  "last_kafka_offset": 4,
                  "status": "COMMITTED"
                },
                "products": {
                  "changes_snapshot_id": 8405389069284592997,
                  "entity": "products",
                  "last_kafka_offset": 7,
                  "status": "COMMITTED"
                },
                "sellers": {
                  "changes_snapshot_id": 8065609369146321385,
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
                "candidate": 10,
                "stable": 10
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
                  "diagnostic": "ts/fixtures/<redacted>_small/README.md', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/fixtures/<redacted>_small/source_profile_small.json', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it",
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
                  "diagnostic": "93 files already formatted",
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
          "stage_l1_20260804_v6_schema_publish_64afdd7955a5",
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
          "duration_seconds": 35.547,
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
            "stage_l1_20260804_v6_schema_publish_64afdd7955a5",
            "--timeout",
            "1800"
          ],
          "duration_seconds": 26.047,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"sync-serving\", \"dag_run_id\": \"stage_l1_20260804_v6_schema_publish_64afdd7955a5\", \"dbt_result\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 3, \\\"sync_run_id\\\": \\\"sync-00000000000000000003\\\"}\"], \"exception\": null, \"results\": [{\"execution_time\": 0.2090756893157959, \"node\": \"stg_customers_current\", \"status\": \"success\"}, {\"execution_time\": 0.08597350120544434, \"node\": \"stg_customers_events\", \"status\": \"success\"}, {\"execution_time\": 0.09011292457580566, \"node\": \"stg_order_items_current\", \"status\": \"success\"}, {\"execution_time\": 0.07588934898376465, \"node\": \"stg_order_payments_current\", \"status\": \"success\"}, {\"execution_time\": 0.060515403747558594, \"node\": \"stg_orders_current\", \"status\": \"success\"}, {\"execution_time\": 0.061234474182128906, \"node\": \"stg_product_category_translation_events\", \"status\": \"success\"}, {\"execution_time\": 0.05806851387023926, \"node\": \"stg_products_events\", \"status\": \"success\"}, {\"execution_time\": 0.06110262870788574, \"node\": \"stg_sellers_current\", \"status\": \"success\"}, {\"execution_time\": 0.3662240505218506, \"node\": \"customer_scd2_collapses_identical_update_and_closes_on_delete\", \"status\": \"pass\"}, {\"execution_time\": 0.29740285873413086, \"node\": \"dim_customer_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.21623802185058594, \"node\": \"payment_allocation_is_proportional_at_item_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.18890762329101562, \"node\": \"zero_gross_order_has_null_payment_allocation\", \"status\": \"pass\"}, {\"execution_time\": 0.22670245170593262, \"node\": \"dim_date\", \"status\": \"success\"}, {\"execution_time\": 0.1566009521484375, \"node\": \"dim_order_status\", \"status\": \"success\"}, {\"execution_time\": 0.47406888008117676, \"node\": \"product_translation_does_not_resurrect_an_old_category\", \"status\": \"pass\"}, {\"execution_time\": 0.24090909957885742, \"node\": \"dim_product_scd2\", \"status\": \"success\"}, {\"execution_time\": 0.1720411777496338, \"node\": \"dim_seller\", \"status\": \"success\"}, {\"execution_time\": 0.08452057838439941, \"node\": \"assert_customer_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.04116320610046387, \"node\": \"candidate_not_null_dim_customer_scd2_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.051149845123291016, \"node\": \"candidate_not_null_dim_customer_scd2_customer_unique_id\", \"status\": \"pass\"}, {\"execution_time\": 0.055173397064208984, \"node\": \"candidate_not_null_dim_customer_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.0619044303894043, \"node\": \"unique_combination_of_columns_dim_customer_scd2_sync_run_seq__customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.0932919979095459, \"node\": \"assert_payment_allocations_balance\", \"status\": \"pass\"}, {\"execution_time\": 0.04244732856750488, \"node\": \"candidate_not_null_dim_date_date_day\", \"status\": \"pass\"}, {\"execution_time\": 0.05323028564453125, \"node\": \"candidate_not_null_dim_date_date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05259084701538086, \"node\": \"candidate_not_null_dim_date_sync_run_seq\", \"status\": \"pass\"}, {\"execution_time\": 0.0758354663848877, \"node\": \"unique_combination_of_columns_dim_date_sync_run_seq__date_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05667757987976074, \"node\": \"candidate_not_null_dim_order_status_order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.0515444278717041, \"node\": \"candidate_not_null_dim_order_status_order_status_key\", \"status\": \"pass\"}, {\"execution_time\": 0.050505638122558594, \"node\": \"unique_combination_of_columns_dim_order_status_sync_run_seq__order_status\", \"status\": \"pass\"}, {\"execution_time\": 0.07617783546447754, \"node\": \"assert_product_scd2_windows\", \"status\": \"pass\"}, {\"execution_time\": 0.06236839294433594, \"node\": \"candidate_not_null_dim_product_scd2_product_id\", \"status\": \"pass\"}, {\"execution_time\": 0.060146331787109375, \"node\": \"candidate_not_null_dim_product_scd2_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.060446739196777344, \"node\": \"candidate_not_null_dim_product_scd2_valid_from\", \"status\": \"pass\"}, {\"execution_time\": 0.1657543182373047, \"node\": \"unique_combination_of_columns_dim_product_scd2_sync_run_seq__product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05002546310424805, \"node\": \"candidate_not_null_dim_seller_seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.052121877670288086, \"node\": \"candidate_not_null_dim_seller_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.05554795265197754, \"node\": \"unique_combination_of_columns_dim_seller_sync_run_seq__seller_id\", \"status\": \"pass\"}, {\"execution_time\": 0.9753568172454834, \"node\": \"fact_order_items\", \"status\": \"success\"}, {\"execution_time\": 0.1531062126159668, \"node\": \"assert_fact_order_items_grain\", \"status\": \"pass\"}, {\"execution_time\": 0.12785863876342773, \"node\": \"candidate_not_null_fact_order_items_customer_key\", \"status\": \"pass\"}, {\"execution_time\": 0.08735466003417969, \"node\": \"candidate_not_null_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.08636736869812012, \"node\": \"candidate_not_null_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.07675027847290039, \"node\": \"candidate_not_null_fact_order_items_order_item_key\", \"status\": \"pass\"}, {\"execution_time\": 0.09600186347961426, \"node\": \"candidate_not_null_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.06660008430480957, \"node\": \"candidate_not_null_fact_order_items_product_key\", \"status\": \"pass\"}, {\"execution_time\": 0.06977295875549316, \"node\": \"candidate_not_null_fact_order_items_seller_key\", \"status\": \"pass\"}, {\"execution_time\": 0.08321452140808105, \"node\": \"candidate_relationships_fact_order_items_customer_key__customer_key__ref_dim_customer_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.09178566932678223, \"node\": \"candidate_relationships_fact_order_items_product_key__product_key__ref_dim_product_scd2_\", \"status\": \"pass\"}, {\"execution_time\": 0.0696859359741211, \"node\": \"candidate_relationships_fact_order_items_seller_key__seller_key__ref_dim_seller_\", \"status\": \"pass\"}, {\"execution_time\": 0.07352471351623535, \"node\": \"non_negative_fact_order_items_allocated_payment_value\", \"status\": \"pass\"}, {\"execution_time\": 0.0540158748626709, \"node\": \"non_negative_fact_order_items_freight_value\", \"status\": \"pass\"}, {\"execution_time\": 0.0461726188659668, \"node\": \"non_negative_fact_order_items_gross_item_amount\", \"status\": \"pass\"}, {\"execution_time\": 0.04985308647155762, \"node\": \"non_negative_fact_order_items_price\", \"status\": \"pass\"}, {\"execution_time\": 0.05977940559387207, \"node\": \"unique_combination_of_columns_fact_order_items_sync_run_seq__order_id__order_item_id\", \"status\": \"pass\"}, {\"execution_time\": 0.17527222633361816, \"node\": \"mart_daily_revenue\", \"status\": \"success\"}, {\"execution_time\": 0.1535196304321289, \"node\": \"mart_monthly_arpu\", \"status\": \"success\"}, {\"execution_time\": 0.04846310615539551, \"node\": \"assert_daily_revenue_components\", \"status\": \"pass\"}, {\"execution_time\": 0.045552968978881836, \"node\": \"candidate_not_null_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.06228828430175781, \"node\": \"candidate_not_null_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.05558180809020996, \"node\": \"candidate_not_null_mart_daily_revenue_order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.10495328903198242, \"node\": \"candidate_not_null_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.08288860321044922, \"node\": \"non_negative_mart_daily_revenue_allocated_payment_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.10504293441772461, \"node\": \"non_negative_mart_daily_revenue_gross_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.06905198097229004, \"node\": \"non_negative_mart_daily_revenue_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.0594325065612793, \"node\": \"unique_combination_of_columns_mart_daily_revenue_sync_run_seq__order_purchase_date\", \"status\": \"pass\"}, {\"execution_time\": 0.06436514854431152, \"node\": \"assert_monthly_arpu_formulas\", \"status\": \"pass\"}, {\"execution_time\": 0.06229066848754883, \"node\": \"candidate_not_null_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.06270694732666016, \"node\": \"candidate_not_null_mart_monthly_arpu_order_month\", \"status\": \"pass\"}, {\"execution_time\": 0.0452425479888916, \"node\": \"candidate_not_null_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.04958653450012207, \"node\": \"candidate_not_null_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.059821128845214844, \"node\": \"non_negative_mart_monthly_arpu_active_customers\", \"status\": \"pass\"}, {\"execution_time\": 0.07184672355651855, \"node\": \"non_negative_mart_monthly_arpu_orders_count\", \"status\": \"pass\"}, {\"execution_time\": 0.0551760196685791, \"node\": \"non_negative_mart_monthly_arpu_total_revenue\", \"status\": \"pass\"}, {\"execution_time\": 0.049199819564819336, \"node\": \"unique_combination_of_columns_mart_monthly_arpu_sync_run_seq__order_month\", \"status\": \"pass\"}], \"selector\": \"serving_candidate\", \"status_counts\": {\"pass\": 59, \"success\": 16}, \"success\": true, \"vars\": {\"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3}}, \"expected_entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 90, \"iceberg_snapshot_ids\": {\"customers\": 5661301511364570764, \"order_items\": 7260055445008051617, \"order_payments\": 8604726252198231125, \"order_reviews\": 5372656209178888275, \"orders\": 1034207959551505294, \"product_category_translation\": 4378261172774740424, \"products\": 8405389069284592997, \"sellers\": 8065609369146321385}, \"is_noop\": false, \"materialized_entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"materialized_event_count\": 90, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3, \"sync_run_status\": \"SUCCEEDED\", \"target_offsets\": {\"olist_cdc.olist_oltp.customers:0\": 9, \"olist_cdc.olist_oltp.order_items:0\": 5, \"olist_cdc.olist_oltp.order_items:1\": 5, \"olist_cdc.olist_oltp.order_items:2\": 6, \"olist_cdc.olist_oltp.order_payments:0\": 5, \"olist_cdc.olist_oltp.order_payments:1\": 4, \"olist_cdc.olist_oltp.order_payments:2\": 4, \"olist_cdc.olist_oltp.order_reviews:0\": 5, \"olist_cdc.olist_oltp.order_reviews:1\": 4, \"olist_cdc.olist_oltp.order_reviews:2\": 2, \"olist_cdc.olist_oltp.orders:0\": 3, \"olist_cdc.olist_oltp.orders:1\": 4, \"olist_cdc.olist_oltp.orders:2\": 4, \"olist_cdc.olist_oltp.product_category_translation:0\": 4, \"olist_cdc.olist_oltp.products:0\": 7, \"olist_cdc.olist_oltp.sellers:0\": 3}, \"target_transaction_id\": \"file=binlog.000002,pos=21950\"}\n",
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
          "duration_seconds": 2.563,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"validate-serving\", \"current_views\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"dbt\": {\"command\": [\"build\", \"--project-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--profiles-dir\", \"/opt/airflow/project/dbt/olist_clickhouse\", \"--selector\", \"serving_candidate\", \"--vars\", \"{\\\"sync_run_seq\\\": 3, \\\"sync_run_id\\\": \\\"sync-00000000000000000003\\\"}\"], \"result_count\": 75, \"status_counts\": {\"pass\": 59, \"success\": 16}}, \"gold_views\": {\"dim_customer_scd2\": {\"candidate\": 8, \"stable\": 8}, \"dim_date\": {\"candidate\": 46, \"stable\": 46}, \"dim_order_status\": {\"candidate\": 2, \"stable\": 2}, \"dim_product_scd2\": {\"candidate\": 10, \"stable\": 10}, \"dim_seller\": {\"candidate\": 4, \"stable\": 4}, \"fact_order_items\": {\"candidate\": 18, \"stable\": 18}, \"mart_daily_revenue\": {\"candidate\": 13, \"stable\": 13}, \"mart_monthly_arpu\": {\"candidate\": 7, \"stable\": 7}}, \"static_validation\": {\"checks\": [{\"command\": \"uv lock --check\", \"diagnostic\": \"Resolved 216 packages in 1ms\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.generate_contracts\", \"diagnostic\": \"Eight versioned entity contract chains are current\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.writer_schemas\", \"diagnostic\": \"captured writer schema repository is valid: captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"C:\\\\Users\\\\fyujv\\\\source\\\\repos\\\\olist-mds\\\\.venv\\\\Scripts\\\\python.exe -m streaming.schemas.contracts\", \"diagnostic\": \"CDC entity contracts are valid: eight entities, writers=captured\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"docker compose --profile\", \"diagnostic\": \"\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"git diff --check\", \"diagnostic\": \"ts/fixtures/<redacted>_small/README.md', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/fixtures/<redacted>_small/source_profile_small.json', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/serving/test_boundary.py', LF will be replaced by CRLF the next time Git touches it\\nwarning: in the working copy of 'tests/stage_v/test_stage_v_harness.py', LF will be replaced by CRLF the next time Git touches it\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"All checks passed!\", \"exit_code\": 0, \"status\": \"passed\"}, {\"command\": \"uv run ruff\", \"diagnostic\": \"93 files already formatted\", \"exit_code\": 0, \"status\": \"passed\"}], \"status\": \"ready\"}, \"status\": \"ready\", \"sync_run_id\": \"sync-00000000000000000003\", \"sync_run_seq\": 3}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 68.2,
      "gate": "08-additive-schema",
      "status": "PASS",
      "timestamp": "2026-08-04T15:58:22.151217+00:00"
    },
    "09-rebuild": {
      "assertions": [
        {
          "detail": {
            "command": "rebuild-serving",
            "dag_run_id": "stage_l1_20260804_v6_rebuild_64afdd7955a5",
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
              "customers": 5661301511364570764,
              "order_items": 7260055445008051617,
              "order_payments": 8604726252198231125,
              "order_reviews": 5372656209178888275,
              "orders": 1034207959551505294,
              "product_category_translation": 4378261172774740424,
              "products": 8405389069284592997,
              "sellers": 8065609369146321385
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
                "candidate": 10,
                "stable": 10
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
              "customers": 5661301511364570764,
              "order_items": 7260055445008051617,
              "order_payments": 8604726252198231125,
              "order_reviews": 5372656209178888275,
              "orders": 1034207959551505294,
              "product_category_translation": 4378261172774740424,
              "products": 8405389069284592997,
              "sellers": 8065609369146321385
            },
            "materialized_event_count": 90,
            "row_manifests": {
              "candidate_physical": {
                "customers": {
                  "manifest_sha256": "d6a5f54143df5300268413dcecaeeae0a04c588748a410320d85bdff3f298b2c",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "89ab2f62f07ee82dbdd1ae16117ad47979248c38760527041e32234682954c85"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "3a192bd6290c000cc1febc688fa1b3ecdf958809a41d12088dba58891a5da1c6"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "1b0046875b6d0b5b885fd41e2fd786033e8d5ca072ef25e8183d4542757ea33c"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "d634c2bb23d334b22578fc16a3f999a7fc00a2d186485bdd496617f2218bd74b"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "09cccb56bb6ac7f80cd494acabe5d911e61d7ae1d964c16ff790689f750f067b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "89fad7a5227a28282e16ba2cc8d113a8eaa7513bdb3e2a2da37e2ecf572f92e8"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "2c7b1778c310ddfedc92b2f27a5fa019ae1ddf17488e1ef28ce67a9ae1d9e4f9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "5639c71dd4d12217d94951f14f03eae4bd4abc560d1c6d23bc7ccb8dd3ba03b6"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "a75b340c2c1f027bb1217116f516238dcadb7094de9e0890337902c111c49f53"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "6f5f8124e64aec5e0a8510daa2b0866a4ab2ff02ee2e9ce6f6b9223663eaa9a2",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1977794759b3ec343596436e3934e66e8c558c8898614a082cba6471de9d039e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "f32c450df3aa968cb753da8afc6276af2a3b9d727ef09d76497ee926ac9a0726"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "33d79dde3cd0240226c1ef559a8283e67186af636336576f523f08d5ef4806cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "105509c2c83d9a892268219c4a8cc5ef5d07b2e1dfdcc2c972dc2e16a651b7f2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "35eb0ee1af3c9f296b097ee79ad2e2e14e1903c22afd8e2a4e7a3647991d9e2e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "89ea878484dd532f38e75bf25ec4bec4313d160840154b8117581234332bc41d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "4694609b3768ce8f16ae6a45cbc7fe9ad5eaae00411cdb2668f81079ea8b1d19"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "f8ea173a7aded2a525c61b40674f0b2e5ed23a9fe035863cf19e97ea7b3a89c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "851e5a3dbf8604b382de69b085273bfba69fd549ed56ba40c5bd94c55499bb7b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "3e3991e79ec9e19f558cd88ef2f12cc5b8a46fda127c6a8248eeb949bfeb1f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "57c81b3b00e28d8949d847c16b283f7712416dc442d389f623f29c1bfb06a26c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "425bc2716b33cb2419919e3f727410465f2ad5afb55a9202bbc8f3c17ccb03f8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "389f22d86008d40537fb1b786003b4a01e1b5ee97eaab60ef8ab0b7708c8ebe8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3670c8008bfae0adf652945e3e0db009f1d97aeef4bdaa6765cd31511372f744"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "2caa530c697d498bb7f2769e714524a29ea1441db42f9db0782fce6cdc4616ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "a8874fdce193e31aeb772a7cff9849f68a63937b4f7cfe5ea73101be332236e6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "438349cddfc22426ffcb71243f54210010e91e377fcb7de48befba856ffa01d6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "5c1d2e75e7939078406a8d82052cba363b10c25a18ff847f570d50688cd50295"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "b7f20300651573509a976f9579056c462de6a2397fc7e7895437802e79d0867d",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "0d50f161adc12f443d89c3291c41198f8a042aab383efe97670fcbc5a37096da"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "4eb5c2975c1f31cfec36c8192a8e4d4fea817058a6ccb8b4af8e693126201717"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "0fcabf6d1133f7662ba91b3c5adf5e9ee84f75f0506c672163f35632ee311d1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "57aace58c7aeecddf7c79be2b8c1fa761db82b16929b56f451c182b74fd5a1e2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "8a37f338d2d9b06687978117a3ed88dd6ac81d77459a9aefdd3963da63f360c9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "809383f342e45e18fe73122ca945cc743dcbb5745c10d1c6cb8ba33322f8caee"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "d9bc37dc49eb9a2eb3b629adbca76a109916c17fe9c7ad7273876b9ac2097dce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "78543816f081471fb95712be39a71d25c9f45d19d198409e50fb07231fad2869"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "f0f6fa77b8b70951fe7c1b7988c0ecd418cb4c0728e086afac5a9cdf77cf6148"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "6381f5c559155fb588a2221a9b4320368410ccbf2028d3758ea8b0bd60426c40"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "67fda8aea9b21d87c023b3f511b377cbad5fafe98841ddc9d86b05b4a393dee8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "643b3a6835d5abfbbec3a932e1f631dff78717d9108458d09a758892afe0659e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "997ef7f136abc78cc56056c1606ec8024979671e603dc4814191b4fd8fd8b6dc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "a4e78c01ea8a0970b92035fa280a59a9f71e6b9a366fa5789e8caad5e1137870"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "305bf4232d86e9aa1820206099d70394f7ddd1b63c620e3c11e3d29445d275fa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "f4b47a2b0dde31053d3f0cd8520eebe75d3ac867bdb26438d6e233914ea4b355"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "9763aa2c24b67661cb49b67c9ebd7a9829050afcceffcae79ce92ab36711221b",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "ce68d93e3f41387798241b2606709a2affcd6eca26f94778218ee71e9582ebd1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "b583026fb692bed89bcdc5b6166498161e509aea537c9d8dac41b7bad1385be5"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "6b20f420b88ebebbb39e68b53a5c42e8ff74e9097a4390f200a04c6d90beee39"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "ae5cb8ee890d5486c20589d12099119db53fe173acbe463a805f29fd7873bf9f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "fb0dba632f405b8e5d5d08547c4146198bacac259902f8d4cf4fb821008a116e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "65a12285c329ef79c536f03bf90f64cce4bec177df73ed1b095bfb297b7468f7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "e5c510c11e907b0b6a03dc98fc9cb093cd804d1961676accff9b4f2e68ed4020"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a0bba76263d315bd8e51f80d94ee30a572f58fde30918b83d60997ec2240e084"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "39c6898d4f43e149fe05ea20b5caa480ddced312aca5f86ecfa0bde7a63029b4"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "724fd7272fec8bb2da540251686e9b779241556c1317c7d5aacf3e9045955c07"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "67799f4f0c5b59bfbd23b1a12c537e160148fc0080b6600905f1b2245fe70b7c"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "876c3ae0d4af03706e0ac64c31353375e466c76479cd2c8714b3637b70d1bd14"
                    },
                    {
                      "is_deleted": true,
                      "review_id": "wave2_review_001",
                      "row_hash": "d86306f9c001d524a7050108279dab9c93cffa0883e2e9f729af8d8db411ca76"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "820140bf9165f9c63799fda6d1989523e41b24affcbe08934e039453db99b28f",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "fada5fd81799360365f0f3f2f7e7fd2282cb79a3ca4d679d6321f6367815e329"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8fe73ef692ce87d1e7fabfb0d3e3ae2b601945485b450dc692989e0bb8a0307c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "e833e41529c746c4a9b71026b94582cf2c38d5c6341df83d54caf3b76ff1d193"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "2a581f705e2767771716df2e8997eda2e382c6494a873a5bb9321e068b1c8e0a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "2b7a24beb99aca492dd114f9242c41d45ab177643560ff54e0241bdab5bf660e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "cbdb7ae5c2bb413e4f06f655b22dcae2d5db5d6ce05a029d5c12dd53bc576774"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "0352d0852e4a15d0fd3e5f13d12c653a3934204026984f6431772d97db09ed8b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "d7df4b5849d0ff8ba4235ed9dd23eae8e5b248b4f1b757b7b14d4f282a938240"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "32be1be57cba3d2b3434d7896b6f189aebd24af63c0bf260a5a03106c165c0a9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "e5e90df101e4a37d68ad0d370e19c1bd7c4df584213c70d544703d1f74089a67"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "adc16f849c3cdef0c960d41d63c1b16eacd16451d1fa1233afb4b2e9107cc74e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d55ce1a8050fda8baeec458d3b75a511565f13b1716de8db82711cca4f5c5685"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "3f126287622599f71b701dcdeae241e7ef27976d9ebf477968295a8f390a3adc"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "fb943b0ee210613a5db749d5dde4c88b31bc2702622c245497415674766c78ae",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "cd7108f72c72c22e5596eaa11887855bcaed985a4455252168ada7cfbae7d2ae"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "f7e085e2b205fc34cf22d020d86e0401900ddd53a86ad8454dd00e3b2048569d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "a30afc8bce67a9c25fa537f02b7ac8966f7e1c1508b69f0560eec4c49872df5a"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "6d2ed878891db72a489df091f6dcfba0108e79872a67f595499823a84974ba57"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "3ca9361539f5cc8f2ae0ba8574ca45b2a72f642930b46b76626e1959aaa37972"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1a103d949cbcc175f44d038284930510ff41ed8271ba24d2705b1e867adc56ab",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "eb48389bc974f6e16576aba40dce122e708a92688ac3f737b374ce7d315261c1"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f0e4025ea03a83d2a12c368550f99ce55764a1f074492c92d46f5a1bfa329e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "37db3f8b4dff5a83224a72b2b1a69e8be383226bd865087c391668bcd90e71f3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "8f9702ee001bbde6c39488863d031a77c63eac41518ad8ff980ea5ff6e757542"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "6b418454cbf219b7c0a7b62b15013a0897eb0e90fc0cdd3675acc081a1952bfe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4ceb44986ab7d2e165f5282350cf94af482def9cfa7acf740a32b0cd214698aa"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "4bea3afd00092cd3f27dcedf6eedf800580513a12585b57584fe207e864414d2"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "8f5890b61905a2faec5299473b988c15b58c640c32184da6aeaad0b2e42ff66d"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "57e892beb9296880003f697df09dc297229147170b5bc9ebc3bcaa6dbe70f57d",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "544d88ba003be3195cbd48ec3de37509ad5562137cc62ae7a365f0e6252f4873",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "2005aa0cdb07be24feb69dd6534283fbc30207290a0b62edff161e65c93e1868",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6c3fd29b27b37ba4c6a6ff3edbdecc9784bb89563f50718dd67044ec2436e661",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "113871d5a6e2ef39c649ee9a78d51788343c9d2e1d912303deedb93ed473131c",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "candidate_visible": {
                "customers": {
                  "manifest_sha256": "d6a5f54143df5300268413dcecaeeae0a04c588748a410320d85bdff3f298b2c",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "89ab2f62f07ee82dbdd1ae16117ad47979248c38760527041e32234682954c85"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "3a192bd6290c000cc1febc688fa1b3ecdf958809a41d12088dba58891a5da1c6"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "1b0046875b6d0b5b885fd41e2fd786033e8d5ca072ef25e8183d4542757ea33c"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "d634c2bb23d334b22578fc16a3f999a7fc00a2d186485bdd496617f2218bd74b"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "09cccb56bb6ac7f80cd494acabe5d911e61d7ae1d964c16ff790689f750f067b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "89fad7a5227a28282e16ba2cc8d113a8eaa7513bdb3e2a2da37e2ecf572f92e8"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "2c7b1778c310ddfedc92b2f27a5fa019ae1ddf17488e1ef28ce67a9ae1d9e4f9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "5639c71dd4d12217d94951f14f03eae4bd4abc560d1c6d23bc7ccb8dd3ba03b6"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "a75b340c2c1f027bb1217116f516238dcadb7094de9e0890337902c111c49f53"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "6f5f8124e64aec5e0a8510daa2b0866a4ab2ff02ee2e9ce6f6b9223663eaa9a2",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1977794759b3ec343596436e3934e66e8c558c8898614a082cba6471de9d039e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "f32c450df3aa968cb753da8afc6276af2a3b9d727ef09d76497ee926ac9a0726"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "33d79dde3cd0240226c1ef559a8283e67186af636336576f523f08d5ef4806cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "105509c2c83d9a892268219c4a8cc5ef5d07b2e1dfdcc2c972dc2e16a651b7f2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "35eb0ee1af3c9f296b097ee79ad2e2e14e1903c22afd8e2a4e7a3647991d9e2e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "89ea878484dd532f38e75bf25ec4bec4313d160840154b8117581234332bc41d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "4694609b3768ce8f16ae6a45cbc7fe9ad5eaae00411cdb2668f81079ea8b1d19"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "f8ea173a7aded2a525c61b40674f0b2e5ed23a9fe035863cf19e97ea7b3a89c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "851e5a3dbf8604b382de69b085273bfba69fd549ed56ba40c5bd94c55499bb7b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "3e3991e79ec9e19f558cd88ef2f12cc5b8a46fda127c6a8248eeb949bfeb1f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "57c81b3b00e28d8949d847c16b283f7712416dc442d389f623f29c1bfb06a26c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "425bc2716b33cb2419919e3f727410465f2ad5afb55a9202bbc8f3c17ccb03f8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "389f22d86008d40537fb1b786003b4a01e1b5ee97eaab60ef8ab0b7708c8ebe8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3670c8008bfae0adf652945e3e0db009f1d97aeef4bdaa6765cd31511372f744"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "2caa530c697d498bb7f2769e714524a29ea1441db42f9db0782fce6cdc4616ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "a8874fdce193e31aeb772a7cff9849f68a63937b4f7cfe5ea73101be332236e6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "438349cddfc22426ffcb71243f54210010e91e377fcb7de48befba856ffa01d6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "5c1d2e75e7939078406a8d82052cba363b10c25a18ff847f570d50688cd50295"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "b7f20300651573509a976f9579056c462de6a2397fc7e7895437802e79d0867d",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "0d50f161adc12f443d89c3291c41198f8a042aab383efe97670fcbc5a37096da"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "4eb5c2975c1f31cfec36c8192a8e4d4fea817058a6ccb8b4af8e693126201717"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "0fcabf6d1133f7662ba91b3c5adf5e9ee84f75f0506c672163f35632ee311d1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "57aace58c7aeecddf7c79be2b8c1fa761db82b16929b56f451c182b74fd5a1e2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "8a37f338d2d9b06687978117a3ed88dd6ac81d77459a9aefdd3963da63f360c9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "809383f342e45e18fe73122ca945cc743dcbb5745c10d1c6cb8ba33322f8caee"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "d9bc37dc49eb9a2eb3b629adbca76a109916c17fe9c7ad7273876b9ac2097dce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "78543816f081471fb95712be39a71d25c9f45d19d198409e50fb07231fad2869"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "f0f6fa77b8b70951fe7c1b7988c0ecd418cb4c0728e086afac5a9cdf77cf6148"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "6381f5c559155fb588a2221a9b4320368410ccbf2028d3758ea8b0bd60426c40"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "67fda8aea9b21d87c023b3f511b377cbad5fafe98841ddc9d86b05b4a393dee8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "643b3a6835d5abfbbec3a932e1f631dff78717d9108458d09a758892afe0659e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "997ef7f136abc78cc56056c1606ec8024979671e603dc4814191b4fd8fd8b6dc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "a4e78c01ea8a0970b92035fa280a59a9f71e6b9a366fa5789e8caad5e1137870"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "305bf4232d86e9aa1820206099d70394f7ddd1b63c620e3c11e3d29445d275fa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "f4b47a2b0dde31053d3f0cd8520eebe75d3ac867bdb26438d6e233914ea4b355"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "a9726e9b86a974f26367081574f6e7a8a1f47b57ae389b760fab3580fd59313f",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "ce68d93e3f41387798241b2606709a2affcd6eca26f94778218ee71e9582ebd1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "b583026fb692bed89bcdc5b6166498161e509aea537c9d8dac41b7bad1385be5"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "6b20f420b88ebebbb39e68b53a5c42e8ff74e9097a4390f200a04c6d90beee39"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "ae5cb8ee890d5486c20589d12099119db53fe173acbe463a805f29fd7873bf9f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "fb0dba632f405b8e5d5d08547c4146198bacac259902f8d4cf4fb821008a116e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "65a12285c329ef79c536f03bf90f64cce4bec177df73ed1b095bfb297b7468f7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "e5c510c11e907b0b6a03dc98fc9cb093cd804d1961676accff9b4f2e68ed4020"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a0bba76263d315bd8e51f80d94ee30a572f58fde30918b83d60997ec2240e084"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "39c6898d4f43e149fe05ea20b5caa480ddced312aca5f86ecfa0bde7a63029b4"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "724fd7272fec8bb2da540251686e9b779241556c1317c7d5aacf3e9045955c07"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "67799f4f0c5b59bfbd23b1a12c537e160148fc0080b6600905f1b2245fe70b7c"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "876c3ae0d4af03706e0ac64c31353375e466c76479cd2c8714b3637b70d1bd14"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "820140bf9165f9c63799fda6d1989523e41b24affcbe08934e039453db99b28f",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "fada5fd81799360365f0f3f2f7e7fd2282cb79a3ca4d679d6321f6367815e329"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8fe73ef692ce87d1e7fabfb0d3e3ae2b601945485b450dc692989e0bb8a0307c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "e833e41529c746c4a9b71026b94582cf2c38d5c6341df83d54caf3b76ff1d193"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "2a581f705e2767771716df2e8997eda2e382c6494a873a5bb9321e068b1c8e0a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "2b7a24beb99aca492dd114f9242c41d45ab177643560ff54e0241bdab5bf660e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "cbdb7ae5c2bb413e4f06f655b22dcae2d5db5d6ce05a029d5c12dd53bc576774"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "0352d0852e4a15d0fd3e5f13d12c653a3934204026984f6431772d97db09ed8b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "d7df4b5849d0ff8ba4235ed9dd23eae8e5b248b4f1b757b7b14d4f282a938240"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "32be1be57cba3d2b3434d7896b6f189aebd24af63c0bf260a5a03106c165c0a9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "e5e90df101e4a37d68ad0d370e19c1bd7c4df584213c70d544703d1f74089a67"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "adc16f849c3cdef0c960d41d63c1b16eacd16451d1fa1233afb4b2e9107cc74e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d55ce1a8050fda8baeec458d3b75a511565f13b1716de8db82711cca4f5c5685"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "3f126287622599f71b701dcdeae241e7ef27976d9ebf477968295a8f390a3adc"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "fb943b0ee210613a5db749d5dde4c88b31bc2702622c245497415674766c78ae",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "cd7108f72c72c22e5596eaa11887855bcaed985a4455252168ada7cfbae7d2ae"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "f7e085e2b205fc34cf22d020d86e0401900ddd53a86ad8454dd00e3b2048569d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "a30afc8bce67a9c25fa537f02b7ac8966f7e1c1508b69f0560eec4c49872df5a"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "6d2ed878891db72a489df091f6dcfba0108e79872a67f595499823a84974ba57"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "3ca9361539f5cc8f2ae0ba8574ca45b2a72f642930b46b76626e1959aaa37972"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1a103d949cbcc175f44d038284930510ff41ed8271ba24d2705b1e867adc56ab",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "eb48389bc974f6e16576aba40dce122e708a92688ac3f737b374ce7d315261c1"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f0e4025ea03a83d2a12c368550f99ce55764a1f074492c92d46f5a1bfa329e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "37db3f8b4dff5a83224a72b2b1a69e8be383226bd865087c391668bcd90e71f3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "8f9702ee001bbde6c39488863d031a77c63eac41518ad8ff980ea5ff6e757542"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "6b418454cbf219b7c0a7b62b15013a0897eb0e90fc0cdd3675acc081a1952bfe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4ceb44986ab7d2e165f5282350cf94af482def9cfa7acf740a32b0cd214698aa"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "4bea3afd00092cd3f27dcedf6eedf800580513a12585b57584fe207e864414d2"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "8f5890b61905a2faec5299473b988c15b58c640c32184da6aeaad0b2e42ff66d"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "57e892beb9296880003f697df09dc297229147170b5bc9ebc3bcaa6dbe70f57d",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "544d88ba003be3195cbd48ec3de37509ad5562137cc62ae7a365f0e6252f4873",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "2005aa0cdb07be24feb69dd6534283fbc30207290a0b62edff161e65c93e1868",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6c3fd29b27b37ba4c6a6ff3edbdecc9784bb89563f50718dd67044ec2436e661",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "113871d5a6e2ef39c649ee9a78d51788343c9d2e1d912303deedb93ed473131c",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "iceberg_physical": {
                "customers": {
                  "manifest_sha256": "d6a5f54143df5300268413dcecaeeae0a04c588748a410320d85bdff3f298b2c",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "89ab2f62f07ee82dbdd1ae16117ad47979248c38760527041e32234682954c85"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "3a192bd6290c000cc1febc688fa1b3ecdf958809a41d12088dba58891a5da1c6"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "1b0046875b6d0b5b885fd41e2fd786033e8d5ca072ef25e8183d4542757ea33c"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "d634c2bb23d334b22578fc16a3f999a7fc00a2d186485bdd496617f2218bd74b"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "09cccb56bb6ac7f80cd494acabe5d911e61d7ae1d964c16ff790689f750f067b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "89fad7a5227a28282e16ba2cc8d113a8eaa7513bdb3e2a2da37e2ecf572f92e8"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "2c7b1778c310ddfedc92b2f27a5fa019ae1ddf17488e1ef28ce67a9ae1d9e4f9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "5639c71dd4d12217d94951f14f03eae4bd4abc560d1c6d23bc7ccb8dd3ba03b6"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "a75b340c2c1f027bb1217116f516238dcadb7094de9e0890337902c111c49f53"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "6f5f8124e64aec5e0a8510daa2b0866a4ab2ff02ee2e9ce6f6b9223663eaa9a2",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1977794759b3ec343596436e3934e66e8c558c8898614a082cba6471de9d039e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "f32c450df3aa968cb753da8afc6276af2a3b9d727ef09d76497ee926ac9a0726"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "33d79dde3cd0240226c1ef559a8283e67186af636336576f523f08d5ef4806cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "105509c2c83d9a892268219c4a8cc5ef5d07b2e1dfdcc2c972dc2e16a651b7f2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "35eb0ee1af3c9f296b097ee79ad2e2e14e1903c22afd8e2a4e7a3647991d9e2e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "89ea878484dd532f38e75bf25ec4bec4313d160840154b8117581234332bc41d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "4694609b3768ce8f16ae6a45cbc7fe9ad5eaae00411cdb2668f81079ea8b1d19"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "f8ea173a7aded2a525c61b40674f0b2e5ed23a9fe035863cf19e97ea7b3a89c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "851e5a3dbf8604b382de69b085273bfba69fd549ed56ba40c5bd94c55499bb7b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "3e3991e79ec9e19f558cd88ef2f12cc5b8a46fda127c6a8248eeb949bfeb1f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "57c81b3b00e28d8949d847c16b283f7712416dc442d389f623f29c1bfb06a26c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "425bc2716b33cb2419919e3f727410465f2ad5afb55a9202bbc8f3c17ccb03f8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "389f22d86008d40537fb1b786003b4a01e1b5ee97eaab60ef8ab0b7708c8ebe8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3670c8008bfae0adf652945e3e0db009f1d97aeef4bdaa6765cd31511372f744"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "2caa530c697d498bb7f2769e714524a29ea1441db42f9db0782fce6cdc4616ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "a8874fdce193e31aeb772a7cff9849f68a63937b4f7cfe5ea73101be332236e6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "438349cddfc22426ffcb71243f54210010e91e377fcb7de48befba856ffa01d6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "5c1d2e75e7939078406a8d82052cba363b10c25a18ff847f570d50688cd50295"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "b7f20300651573509a976f9579056c462de6a2397fc7e7895437802e79d0867d",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "0d50f161adc12f443d89c3291c41198f8a042aab383efe97670fcbc5a37096da"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "4eb5c2975c1f31cfec36c8192a8e4d4fea817058a6ccb8b4af8e693126201717"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "0fcabf6d1133f7662ba91b3c5adf5e9ee84f75f0506c672163f35632ee311d1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "57aace58c7aeecddf7c79be2b8c1fa761db82b16929b56f451c182b74fd5a1e2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "8a37f338d2d9b06687978117a3ed88dd6ac81d77459a9aefdd3963da63f360c9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "809383f342e45e18fe73122ca945cc743dcbb5745c10d1c6cb8ba33322f8caee"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "d9bc37dc49eb9a2eb3b629adbca76a109916c17fe9c7ad7273876b9ac2097dce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "78543816f081471fb95712be39a71d25c9f45d19d198409e50fb07231fad2869"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "f0f6fa77b8b70951fe7c1b7988c0ecd418cb4c0728e086afac5a9cdf77cf6148"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "6381f5c559155fb588a2221a9b4320368410ccbf2028d3758ea8b0bd60426c40"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "67fda8aea9b21d87c023b3f511b377cbad5fafe98841ddc9d86b05b4a393dee8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "643b3a6835d5abfbbec3a932e1f631dff78717d9108458d09a758892afe0659e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "997ef7f136abc78cc56056c1606ec8024979671e603dc4814191b4fd8fd8b6dc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "a4e78c01ea8a0970b92035fa280a59a9f71e6b9a366fa5789e8caad5e1137870"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "305bf4232d86e9aa1820206099d70394f7ddd1b63c620e3c11e3d29445d275fa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "f4b47a2b0dde31053d3f0cd8520eebe75d3ac867bdb26438d6e233914ea4b355"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "9763aa2c24b67661cb49b67c9ebd7a9829050afcceffcae79ce92ab36711221b",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "ce68d93e3f41387798241b2606709a2affcd6eca26f94778218ee71e9582ebd1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "b583026fb692bed89bcdc5b6166498161e509aea537c9d8dac41b7bad1385be5"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "6b20f420b88ebebbb39e68b53a5c42e8ff74e9097a4390f200a04c6d90beee39"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "ae5cb8ee890d5486c20589d12099119db53fe173acbe463a805f29fd7873bf9f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "fb0dba632f405b8e5d5d08547c4146198bacac259902f8d4cf4fb821008a116e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "65a12285c329ef79c536f03bf90f64cce4bec177df73ed1b095bfb297b7468f7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "e5c510c11e907b0b6a03dc98fc9cb093cd804d1961676accff9b4f2e68ed4020"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a0bba76263d315bd8e51f80d94ee30a572f58fde30918b83d60997ec2240e084"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "39c6898d4f43e149fe05ea20b5caa480ddced312aca5f86ecfa0bde7a63029b4"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "724fd7272fec8bb2da540251686e9b779241556c1317c7d5aacf3e9045955c07"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "67799f4f0c5b59bfbd23b1a12c537e160148fc0080b6600905f1b2245fe70b7c"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "876c3ae0d4af03706e0ac64c31353375e466c76479cd2c8714b3637b70d1bd14"
                    },
                    {
                      "is_deleted": true,
                      "review_id": "wave2_review_001",
                      "row_hash": "d86306f9c001d524a7050108279dab9c93cffa0883e2e9f729af8d8db411ca76"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "820140bf9165f9c63799fda6d1989523e41b24affcbe08934e039453db99b28f",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "fada5fd81799360365f0f3f2f7e7fd2282cb79a3ca4d679d6321f6367815e329"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8fe73ef692ce87d1e7fabfb0d3e3ae2b601945485b450dc692989e0bb8a0307c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "e833e41529c746c4a9b71026b94582cf2c38d5c6341df83d54caf3b76ff1d193"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "2a581f705e2767771716df2e8997eda2e382c6494a873a5bb9321e068b1c8e0a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "2b7a24beb99aca492dd114f9242c41d45ab177643560ff54e0241bdab5bf660e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "cbdb7ae5c2bb413e4f06f655b22dcae2d5db5d6ce05a029d5c12dd53bc576774"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "0352d0852e4a15d0fd3e5f13d12c653a3934204026984f6431772d97db09ed8b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "d7df4b5849d0ff8ba4235ed9dd23eae8e5b248b4f1b757b7b14d4f282a938240"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "32be1be57cba3d2b3434d7896b6f189aebd24af63c0bf260a5a03106c165c0a9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "e5e90df101e4a37d68ad0d370e19c1bd7c4df584213c70d544703d1f74089a67"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "adc16f849c3cdef0c960d41d63c1b16eacd16451d1fa1233afb4b2e9107cc74e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d55ce1a8050fda8baeec458d3b75a511565f13b1716de8db82711cca4f5c5685"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "3f126287622599f71b701dcdeae241e7ef27976d9ebf477968295a8f390a3adc"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "fb943b0ee210613a5db749d5dde4c88b31bc2702622c245497415674766c78ae",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "cd7108f72c72c22e5596eaa11887855bcaed985a4455252168ada7cfbae7d2ae"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "f7e085e2b205fc34cf22d020d86e0401900ddd53a86ad8454dd00e3b2048569d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "a30afc8bce67a9c25fa537f02b7ac8966f7e1c1508b69f0560eec4c49872df5a"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "6d2ed878891db72a489df091f6dcfba0108e79872a67f595499823a84974ba57"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "3ca9361539f5cc8f2ae0ba8574ca45b2a72f642930b46b76626e1959aaa37972"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1a103d949cbcc175f44d038284930510ff41ed8271ba24d2705b1e867adc56ab",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "eb48389bc974f6e16576aba40dce122e708a92688ac3f737b374ce7d315261c1"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f0e4025ea03a83d2a12c368550f99ce55764a1f074492c92d46f5a1bfa329e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "37db3f8b4dff5a83224a72b2b1a69e8be383226bd865087c391668bcd90e71f3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "8f9702ee001bbde6c39488863d031a77c63eac41518ad8ff980ea5ff6e757542"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "6b418454cbf219b7c0a7b62b15013a0897eb0e90fc0cdd3675acc081a1952bfe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4ceb44986ab7d2e165f5282350cf94af482def9cfa7acf740a32b0cd214698aa"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "4bea3afd00092cd3f27dcedf6eedf800580513a12585b57584fe207e864414d2"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "8f5890b61905a2faec5299473b988c15b58c640c32184da6aeaad0b2e42ff66d"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "57e892beb9296880003f697df09dc297229147170b5bc9ebc3bcaa6dbe70f57d",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "544d88ba003be3195cbd48ec3de37509ad5562137cc62ae7a365f0e6252f4873",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "2005aa0cdb07be24feb69dd6534283fbc30207290a0b62edff161e65c93e1868",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6c3fd29b27b37ba4c6a6ff3edbdecc9784bb89563f50718dd67044ec2436e661",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "113871d5a6e2ef39c649ee9a78d51788343c9d2e1d912303deedb93ed473131c",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "iceberg_visible": {
                "customers": {
                  "manifest_sha256": "d6a5f54143df5300268413dcecaeeae0a04c588748a410320d85bdff3f298b2c",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "89ab2f62f07ee82dbdd1ae16117ad47979248c38760527041e32234682954c85"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "3a192bd6290c000cc1febc688fa1b3ecdf958809a41d12088dba58891a5da1c6"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "1b0046875b6d0b5b885fd41e2fd786033e8d5ca072ef25e8183d4542757ea33c"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "d634c2bb23d334b22578fc16a3f999a7fc00a2d186485bdd496617f2218bd74b"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "09cccb56bb6ac7f80cd494acabe5d911e61d7ae1d964c16ff790689f750f067b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "89fad7a5227a28282e16ba2cc8d113a8eaa7513bdb3e2a2da37e2ecf572f92e8"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "2c7b1778c310ddfedc92b2f27a5fa019ae1ddf17488e1ef28ce67a9ae1d9e4f9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "5639c71dd4d12217d94951f14f03eae4bd4abc560d1c6d23bc7ccb8dd3ba03b6"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "a75b340c2c1f027bb1217116f516238dcadb7094de9e0890337902c111c49f53"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "6f5f8124e64aec5e0a8510daa2b0866a4ab2ff02ee2e9ce6f6b9223663eaa9a2",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1977794759b3ec343596436e3934e66e8c558c8898614a082cba6471de9d039e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "f32c450df3aa968cb753da8afc6276af2a3b9d727ef09d76497ee926ac9a0726"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "33d79dde3cd0240226c1ef559a8283e67186af636336576f523f08d5ef4806cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "105509c2c83d9a892268219c4a8cc5ef5d07b2e1dfdcc2c972dc2e16a651b7f2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "35eb0ee1af3c9f296b097ee79ad2e2e14e1903c22afd8e2a4e7a3647991d9e2e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "89ea878484dd532f38e75bf25ec4bec4313d160840154b8117581234332bc41d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "4694609b3768ce8f16ae6a45cbc7fe9ad5eaae00411cdb2668f81079ea8b1d19"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "f8ea173a7aded2a525c61b40674f0b2e5ed23a9fe035863cf19e97ea7b3a89c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "851e5a3dbf8604b382de69b085273bfba69fd549ed56ba40c5bd94c55499bb7b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "3e3991e79ec9e19f558cd88ef2f12cc5b8a46fda127c6a8248eeb949bfeb1f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "57c81b3b00e28d8949d847c16b283f7712416dc442d389f623f29c1bfb06a26c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "425bc2716b33cb2419919e3f727410465f2ad5afb55a9202bbc8f3c17ccb03f8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "389f22d86008d40537fb1b786003b4a01e1b5ee97eaab60ef8ab0b7708c8ebe8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3670c8008bfae0adf652945e3e0db009f1d97aeef4bdaa6765cd31511372f744"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "2caa530c697d498bb7f2769e714524a29ea1441db42f9db0782fce6cdc4616ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "a8874fdce193e31aeb772a7cff9849f68a63937b4f7cfe5ea73101be332236e6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "438349cddfc22426ffcb71243f54210010e91e377fcb7de48befba856ffa01d6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "5c1d2e75e7939078406a8d82052cba363b10c25a18ff847f570d50688cd50295"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "b7f20300651573509a976f9579056c462de6a2397fc7e7895437802e79d0867d",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "0d50f161adc12f443d89c3291c41198f8a042aab383efe97670fcbc5a37096da"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "4eb5c2975c1f31cfec36c8192a8e4d4fea817058a6ccb8b4af8e693126201717"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "0fcabf6d1133f7662ba91b3c5adf5e9ee84f75f0506c672163f35632ee311d1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "57aace58c7aeecddf7c79be2b8c1fa761db82b16929b56f451c182b74fd5a1e2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "8a37f338d2d9b06687978117a3ed88dd6ac81d77459a9aefdd3963da63f360c9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "809383f342e45e18fe73122ca945cc743dcbb5745c10d1c6cb8ba33322f8caee"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "d9bc37dc49eb9a2eb3b629adbca76a109916c17fe9c7ad7273876b9ac2097dce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "78543816f081471fb95712be39a71d25c9f45d19d198409e50fb07231fad2869"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "f0f6fa77b8b70951fe7c1b7988c0ecd418cb4c0728e086afac5a9cdf77cf6148"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "6381f5c559155fb588a2221a9b4320368410ccbf2028d3758ea8b0bd60426c40"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "67fda8aea9b21d87c023b3f511b377cbad5fafe98841ddc9d86b05b4a393dee8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "643b3a6835d5abfbbec3a932e1f631dff78717d9108458d09a758892afe0659e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "997ef7f136abc78cc56056c1606ec8024979671e603dc4814191b4fd8fd8b6dc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "a4e78c01ea8a0970b92035fa280a59a9f71e6b9a366fa5789e8caad5e1137870"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "305bf4232d86e9aa1820206099d70394f7ddd1b63c620e3c11e3d29445d275fa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "f4b47a2b0dde31053d3f0cd8520eebe75d3ac867bdb26438d6e233914ea4b355"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "a9726e9b86a974f26367081574f6e7a8a1f47b57ae389b760fab3580fd59313f",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "ce68d93e3f41387798241b2606709a2affcd6eca26f94778218ee71e9582ebd1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "b583026fb692bed89bcdc5b6166498161e509aea537c9d8dac41b7bad1385be5"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "6b20f420b88ebebbb39e68b53a5c42e8ff74e9097a4390f200a04c6d90beee39"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "ae5cb8ee890d5486c20589d12099119db53fe173acbe463a805f29fd7873bf9f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "fb0dba632f405b8e5d5d08547c4146198bacac259902f8d4cf4fb821008a116e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "65a12285c329ef79c536f03bf90f64cce4bec177df73ed1b095bfb297b7468f7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "e5c510c11e907b0b6a03dc98fc9cb093cd804d1961676accff9b4f2e68ed4020"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a0bba76263d315bd8e51f80d94ee30a572f58fde30918b83d60997ec2240e084"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "39c6898d4f43e149fe05ea20b5caa480ddced312aca5f86ecfa0bde7a63029b4"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "724fd7272fec8bb2da540251686e9b779241556c1317c7d5aacf3e9045955c07"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "67799f4f0c5b59bfbd23b1a12c537e160148fc0080b6600905f1b2245fe70b7c"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "876c3ae0d4af03706e0ac64c31353375e466c76479cd2c8714b3637b70d1bd14"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "820140bf9165f9c63799fda6d1989523e41b24affcbe08934e039453db99b28f",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "fada5fd81799360365f0f3f2f7e7fd2282cb79a3ca4d679d6321f6367815e329"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8fe73ef692ce87d1e7fabfb0d3e3ae2b601945485b450dc692989e0bb8a0307c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "e833e41529c746c4a9b71026b94582cf2c38d5c6341df83d54caf3b76ff1d193"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "2a581f705e2767771716df2e8997eda2e382c6494a873a5bb9321e068b1c8e0a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "2b7a24beb99aca492dd114f9242c41d45ab177643560ff54e0241bdab5bf660e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "cbdb7ae5c2bb413e4f06f655b22dcae2d5db5d6ce05a029d5c12dd53bc576774"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "0352d0852e4a15d0fd3e5f13d12c653a3934204026984f6431772d97db09ed8b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "d7df4b5849d0ff8ba4235ed9dd23eae8e5b248b4f1b757b7b14d4f282a938240"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "32be1be57cba3d2b3434d7896b6f189aebd24af63c0bf260a5a03106c165c0a9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "e5e90df101e4a37d68ad0d370e19c1bd7c4df584213c70d544703d1f74089a67"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "adc16f849c3cdef0c960d41d63c1b16eacd16451d1fa1233afb4b2e9107cc74e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d55ce1a8050fda8baeec458d3b75a511565f13b1716de8db82711cca4f5c5685"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "3f126287622599f71b701dcdeae241e7ef27976d9ebf477968295a8f390a3adc"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "fb943b0ee210613a5db749d5dde4c88b31bc2702622c245497415674766c78ae",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "cd7108f72c72c22e5596eaa11887855bcaed985a4455252168ada7cfbae7d2ae"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "f7e085e2b205fc34cf22d020d86e0401900ddd53a86ad8454dd00e3b2048569d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "a30afc8bce67a9c25fa537f02b7ac8966f7e1c1508b69f0560eec4c49872df5a"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "6d2ed878891db72a489df091f6dcfba0108e79872a67f595499823a84974ba57"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "3ca9361539f5cc8f2ae0ba8574ca45b2a72f642930b46b76626e1959aaa37972"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1a103d949cbcc175f44d038284930510ff41ed8271ba24d2705b1e867adc56ab",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "eb48389bc974f6e16576aba40dce122e708a92688ac3f737b374ce7d315261c1"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f0e4025ea03a83d2a12c368550f99ce55764a1f074492c92d46f5a1bfa329e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "37db3f8b4dff5a83224a72b2b1a69e8be383226bd865087c391668bcd90e71f3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "8f9702ee001bbde6c39488863d031a77c63eac41518ad8ff980ea5ff6e757542"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "6b418454cbf219b7c0a7b62b15013a0897eb0e90fc0cdd3675acc081a1952bfe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4ceb44986ab7d2e165f5282350cf94af482def9cfa7acf740a32b0cd214698aa"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "4bea3afd00092cd3f27dcedf6eedf800580513a12585b57584fe207e864414d2"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "8f5890b61905a2faec5299473b988c15b58c640c32184da6aeaad0b2e42ff66d"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "57e892beb9296880003f697df09dc297229147170b5bc9ebc3bcaa6dbe70f57d",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "544d88ba003be3195cbd48ec3de37509ad5562137cc62ae7a365f0e6252f4873",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "2005aa0cdb07be24feb69dd6534283fbc30207290a0b62edff161e65c93e1868",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6c3fd29b27b37ba4c6a6ff3edbdecc9784bb89563f50718dd67044ec2436e661",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "113871d5a6e2ef39c649ee9a78d51788343c9d2e1d912303deedb93ed473131c",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "stable_visible": {
                "customers": {
                  "manifest_sha256": "d6a5f54143df5300268413dcecaeeae0a04c588748a410320d85bdff3f298b2c",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "89ab2f62f07ee82dbdd1ae16117ad47979248c38760527041e32234682954c85"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "3a192bd6290c000cc1febc688fa1b3ecdf958809a41d12088dba58891a5da1c6"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "1b0046875b6d0b5b885fd41e2fd786033e8d5ca072ef25e8183d4542757ea33c"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "d634c2bb23d334b22578fc16a3f999a7fc00a2d186485bdd496617f2218bd74b"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "09cccb56bb6ac7f80cd494acabe5d911e61d7ae1d964c16ff790689f750f067b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "89fad7a5227a28282e16ba2cc8d113a8eaa7513bdb3e2a2da37e2ecf572f92e8"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "2c7b1778c310ddfedc92b2f27a5fa019ae1ddf17488e1ef28ce67a9ae1d9e4f9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "5639c71dd4d12217d94951f14f03eae4bd4abc560d1c6d23bc7ccb8dd3ba03b6"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "a75b340c2c1f027bb1217116f516238dcadb7094de9e0890337902c111c49f53"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "6f5f8124e64aec5e0a8510daa2b0866a4ab2ff02ee2e9ce6f6b9223663eaa9a2",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1977794759b3ec343596436e3934e66e8c558c8898614a082cba6471de9d039e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "f32c450df3aa968cb753da8afc6276af2a3b9d727ef09d76497ee926ac9a0726"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "33d79dde3cd0240226c1ef559a8283e67186af636336576f523f08d5ef4806cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "105509c2c83d9a892268219c4a8cc5ef5d07b2e1dfdcc2c972dc2e16a651b7f2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "35eb0ee1af3c9f296b097ee79ad2e2e14e1903c22afd8e2a4e7a3647991d9e2e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "89ea878484dd532f38e75bf25ec4bec4313d160840154b8117581234332bc41d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "4694609b3768ce8f16ae6a45cbc7fe9ad5eaae00411cdb2668f81079ea8b1d19"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "f8ea173a7aded2a525c61b40674f0b2e5ed23a9fe035863cf19e97ea7b3a89c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "851e5a3dbf8604b382de69b085273bfba69fd549ed56ba40c5bd94c55499bb7b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "3e3991e79ec9e19f558cd88ef2f12cc5b8a46fda127c6a8248eeb949bfeb1f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "57c81b3b00e28d8949d847c16b283f7712416dc442d389f623f29c1bfb06a26c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "425bc2716b33cb2419919e3f727410465f2ad5afb55a9202bbc8f3c17ccb03f8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "389f22d86008d40537fb1b786003b4a01e1b5ee97eaab60ef8ab0b7708c8ebe8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3670c8008bfae0adf652945e3e0db009f1d97aeef4bdaa6765cd31511372f744"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "2caa530c697d498bb7f2769e714524a29ea1441db42f9db0782fce6cdc4616ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "a8874fdce193e31aeb772a7cff9849f68a63937b4f7cfe5ea73101be332236e6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "438349cddfc22426ffcb71243f54210010e91e377fcb7de48befba856ffa01d6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "5c1d2e75e7939078406a8d82052cba363b10c25a18ff847f570d50688cd50295"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "b7f20300651573509a976f9579056c462de6a2397fc7e7895437802e79d0867d",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "0d50f161adc12f443d89c3291c41198f8a042aab383efe97670fcbc5a37096da"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "4eb5c2975c1f31cfec36c8192a8e4d4fea817058a6ccb8b4af8e693126201717"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "0fcabf6d1133f7662ba91b3c5adf5e9ee84f75f0506c672163f35632ee311d1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "57aace58c7aeecddf7c79be2b8c1fa761db82b16929b56f451c182b74fd5a1e2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "8a37f338d2d9b06687978117a3ed88dd6ac81d77459a9aefdd3963da63f360c9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "809383f342e45e18fe73122ca945cc743dcbb5745c10d1c6cb8ba33322f8caee"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "d9bc37dc49eb9a2eb3b629adbca76a109916c17fe9c7ad7273876b9ac2097dce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "78543816f081471fb95712be39a71d25c9f45d19d198409e50fb07231fad2869"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "f0f6fa77b8b70951fe7c1b7988c0ecd418cb4c0728e086afac5a9cdf77cf6148"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "6381f5c559155fb588a2221a9b4320368410ccbf2028d3758ea8b0bd60426c40"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "67fda8aea9b21d87c023b3f511b377cbad5fafe98841ddc9d86b05b4a393dee8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "643b3a6835d5abfbbec3a932e1f631dff78717d9108458d09a758892afe0659e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "997ef7f136abc78cc56056c1606ec8024979671e603dc4814191b4fd8fd8b6dc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "a4e78c01ea8a0970b92035fa280a59a9f71e6b9a366fa5789e8caad5e1137870"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "305bf4232d86e9aa1820206099d70394f7ddd1b63c620e3c11e3d29445d275fa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "f4b47a2b0dde31053d3f0cd8520eebe75d3ac867bdb26438d6e233914ea4b355"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "a9726e9b86a974f26367081574f6e7a8a1f47b57ae389b760fab3580fd59313f",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "ce68d93e3f41387798241b2606709a2affcd6eca26f94778218ee71e9582ebd1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "b583026fb692bed89bcdc5b6166498161e509aea537c9d8dac41b7bad1385be5"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "6b20f420b88ebebbb39e68b53a5c42e8ff74e9097a4390f200a04c6d90beee39"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "ae5cb8ee890d5486c20589d12099119db53fe173acbe463a805f29fd7873bf9f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "fb0dba632f405b8e5d5d08547c4146198bacac259902f8d4cf4fb821008a116e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "65a12285c329ef79c536f03bf90f64cce4bec177df73ed1b095bfb297b7468f7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "e5c510c11e907b0b6a03dc98fc9cb093cd804d1961676accff9b4f2e68ed4020"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a0bba76263d315bd8e51f80d94ee30a572f58fde30918b83d60997ec2240e084"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "39c6898d4f43e149fe05ea20b5caa480ddced312aca5f86ecfa0bde7a63029b4"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "724fd7272fec8bb2da540251686e9b779241556c1317c7d5aacf3e9045955c07"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "67799f4f0c5b59bfbd23b1a12c537e160148fc0080b6600905f1b2245fe70b7c"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "876c3ae0d4af03706e0ac64c31353375e466c76479cd2c8714b3637b70d1bd14"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "820140bf9165f9c63799fda6d1989523e41b24affcbe08934e039453db99b28f",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "fada5fd81799360365f0f3f2f7e7fd2282cb79a3ca4d679d6321f6367815e329"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8fe73ef692ce87d1e7fabfb0d3e3ae2b601945485b450dc692989e0bb8a0307c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "e833e41529c746c4a9b71026b94582cf2c38d5c6341df83d54caf3b76ff1d193"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "2a581f705e2767771716df2e8997eda2e382c6494a873a5bb9321e068b1c8e0a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "2b7a24beb99aca492dd114f9242c41d45ab177643560ff54e0241bdab5bf660e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "cbdb7ae5c2bb413e4f06f655b22dcae2d5db5d6ce05a029d5c12dd53bc576774"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "0352d0852e4a15d0fd3e5f13d12c653a3934204026984f6431772d97db09ed8b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "d7df4b5849d0ff8ba4235ed9dd23eae8e5b248b4f1b757b7b14d4f282a938240"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "32be1be57cba3d2b3434d7896b6f189aebd24af63c0bf260a5a03106c165c0a9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "e5e90df101e4a37d68ad0d370e19c1bd7c4df584213c70d544703d1f74089a67"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "adc16f849c3cdef0c960d41d63c1b16eacd16451d1fa1233afb4b2e9107cc74e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d55ce1a8050fda8baeec458d3b75a511565f13b1716de8db82711cca4f5c5685"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "3f126287622599f71b701dcdeae241e7ef27976d9ebf477968295a8f390a3adc"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "fb943b0ee210613a5db749d5dde4c88b31bc2702622c245497415674766c78ae",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "cd7108f72c72c22e5596eaa11887855bcaed985a4455252168ada7cfbae7d2ae"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "f7e085e2b205fc34cf22d020d86e0401900ddd53a86ad8454dd00e3b2048569d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "a30afc8bce67a9c25fa537f02b7ac8966f7e1c1508b69f0560eec4c49872df5a"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "6d2ed878891db72a489df091f6dcfba0108e79872a67f595499823a84974ba57"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "3ca9361539f5cc8f2ae0ba8574ca45b2a72f642930b46b76626e1959aaa37972"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1a103d949cbcc175f44d038284930510ff41ed8271ba24d2705b1e867adc56ab",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "eb48389bc974f6e16576aba40dce122e708a92688ac3f737b374ce7d315261c1"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f0e4025ea03a83d2a12c368550f99ce55764a1f074492c92d46f5a1bfa329e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "37db3f8b4dff5a83224a72b2b1a69e8be383226bd865087c391668bcd90e71f3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "8f9702ee001bbde6c39488863d031a77c63eac41518ad8ff980ea5ff6e757542"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "6b418454cbf219b7c0a7b62b15013a0897eb0e90fc0cdd3675acc081a1952bfe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4ceb44986ab7d2e165f5282350cf94af482def9cfa7acf740a32b0cd214698aa"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "4bea3afd00092cd3f27dcedf6eedf800580513a12585b57584fe207e864414d2"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "8f5890b61905a2faec5299473b988c15b58c640c32184da6aeaad0b2e42ff66d"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "57e892beb9296880003f697df09dc297229147170b5bc9ebc3bcaa6dbe70f57d",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "544d88ba003be3195cbd48ec3de37509ad5562137cc62ae7a365f0e6252f4873",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "2005aa0cdb07be24feb69dd6534283fbc30207290a0b62edff161e65c93e1868",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6c3fd29b27b37ba4c6a6ff3edbdecc9784bb89563f50718dd67044ec2436e661",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "113871d5a6e2ef39c649ee9a78d51788343c9d2e1d912303deedb93ed473131c",
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
          "stage_l1_20260804_v6_rebuild_64afdd7955a5",
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
            "stage_l1_20260804_v6_rebuild_64afdd7955a5",
            "--timeout",
            "5400"
          ],
          "duration_seconds": 30.875,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"command\": \"rebuild-serving\", \"dag_run_id\": \"stage_l1_20260804_v6_rebuild_64afdd7955a5\", \"entity_counts\": {\"customers\": 10, \"order_items\": 19, \"order_payments\": 16, \"order_reviews\": 14, \"orders\": 14, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"expected_event_count\": 90, \"iceberg_snapshot_ids\": {\"customers\": 5661301511364570764, \"order_items\": 7260055445008051617, \"order_payments\": 8604726252198231125, \"order_reviews\": 5372656209178888275, \"orders\": 1034207959551505294, \"product_category_translation\": 4378261172774740424, \"products\": 8405389069284592997, \"sellers\": 8065609369146321385}, \"materialized_event_count\": 90, \"status\": \"succeeded\", \"sync_run_id\": \"sync-00000000000000000004\", \"sync_run_seq\": 4}\n",
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
          "duration_seconds": 2.266,
          "exit_code": 0,
          "stderr": "",
          "stdout": "37902c111c49f53\"}]}, \"order_items\": {\"manifest_sha256\": \"6f5f8124e64aec5e0a8510daa2b0866a4ab2ff02ee2e9ce6f6b9223663eaa9a2\", \"row_count\": 18, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"order_item_id\": 1, \"row_hash\": \"1977794759b3ec343596436e3934e66e8c558c8898614a082cba6471de9d039e\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"order_item_id\": 1, \"row_hash\": \"f32c450df3aa968cb753da8afc6276af2a3b9d727ef09d76497ee926ac9a0726\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"order_item_id\": 1, \"row_hash\": \"33d79dde3cd0240226c1ef559a8283e67186af636336576f523f08d5ef4806cb\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"order_item_id\": 2, \"row_hash\": \"105509c2c83d9a892268219c4a8cc5ef5d07b2e1dfdcc2c972dc2e16a651b7f2\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"order_item_id\": 1, \"row_hash\": \"35eb0ee1af3c9f296b097ee79ad2e2e14e1903c22afd8e2a4e7a3647991d9e2e\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"order_item_id\": 1, \"row_hash\": \"89ea878484dd532f38e75bf25ec4bec4313d160840154b8117581234332bc41d\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"order_item_id\": 1, \"row_hash\": \"4694609b3768ce8f16ae6a45cbc7fe9ad5eaae00411cdb2668f81079ea8b1d19\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"order_item_id\": 2, \"row_hash\": \"f8ea173a7aded2a525c61b40674f0b2e5ed23a9fe035863cf19e97ea7b3a89c3\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"order_item_id\": 1, \"row_hash\": \"851e5a3dbf8604b382de69b085273bfba69fd549ed56ba40c5bd94c55499bb7b\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"order_item_id\": 1, \"row_hash\": \"3e3991e79ec9e19f558cd88ef2f12cc5b8a46fda127c6a8248eeb949bfeb1f4d\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"order_item_id\": 1, \"row_hash\": \"57c81b3b00e28d8949d847c16b283f7712416dc442d389f623f29c1bfb06a26c\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"order_item_id\": 2, \"row_hash\": \"425bc2716b33cb2419919e3f727410465f2ad5afb55a9202bbc8f3c17ccb03f8\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"order_item_id\": 1, \"row_hash\": \"389f22d86008d40537fb1b786003b4a01e1b5ee97eaab60ef8ab0b7708c8ebe8\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"order_item_id\": 1, \"row_hash\": \"3670c8008bfae0adf652945e3e0db009f1d97aeef4bdaa6765cd31511372f744\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"order_item_id\": 1, \"row_hash\": \"2caa530c697d498bb7f2769e714524a29ea1441db42f9db0782fce6cdc4616ae\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"order_item_id\": 2, \"row_hash\": \"a8874fdce193e31aeb772a7cff9849f68a63937b4f7cfe5ea73101be332236e6\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"order_item_id\": 1, \"row_hash\": \"438349cddfc22426ffcb71243f54210010e91e377fcb7de48befba856ffa01d6\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"order_item_id\": 2, \"row_hash\": \"5c1d2e75e7939078406a8d82052cba363b10c25a18ff847f570d50688cd50295\"}]}, \"order_payments\": {\"manifest_sha256\": \"b7f20300651573509a976f9579056c462de6a2397fc7e7895437802e79d0867d\", \"row_count\": 16, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"payment_sequential\": 1, \"row_hash\": \"0d50f161adc12f443d89c3291c41198f8a042aab383efe97670fcbc5a37096da\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"payment_sequential\": 1, \"row_hash\": \"4eb5c2975c1f31cfec36c8192a8e4d4fea817058a6ccb8b4af8e693126201717\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"payment_sequential\": 1, \"row_hash\": \"0fcabf6d1133f7662ba91b3c5adf5e9ee84f75f0506c672163f35632ee311d1f\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"payment_sequential\": 1, \"row_hash\": \"57aace58c7aeecddf7c79be2b8c1fa761db82b16929b56f451c182b74fd5a1e2\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"payment_sequential\": 2, \"row_hash\": \"8a37f338d2d9b06687978117a3ed88dd6ac81d77459a9aefdd3963da63f360c9\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"payment_sequential\": 1, \"row_hash\": \"809383f342e45e18fe73122ca945cc743dcbb5745c10d1c6cb8ba33322f8caee\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"payment_sequential\": 1, \"row_hash\": \"d9bc37dc49eb9a2eb3b629adbca76a109916c17fe9c7ad7273876b9ac2097dce\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"payment_sequential\": 1, \"row_hash\": \"78543816f081471fb95712be39a71d25c9f45d19d198409e50fb07231fad2869\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"payment_sequential\": 1, \"row_hash\": \"f0f6fa77b8b70951fe7c1b7988c0ecd418cb4c0728e086afac5a9cdf77cf6148\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"payment_sequential\": 2, \"row_hash\": \"6381f5c559155fb588a2221a9b4320368410ccbf2028d3758ea8b0bd60426c40\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"payment_sequential\": 1, \"row_hash\": \"67fda8aea9b21d87c023b3f511b377cbad5fafe98841ddc9d86b05b4a393dee8\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"payment_sequential\": 1, \"row_hash\": \"643b3a6835d5abfbbec3a932e1f631dff78717d9108458d09a758892afe0659e\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"payment_sequential\": 1, \"row_hash\": \"997ef7f136abc78cc56056c1606ec8024979671e603dc4814191b4fd8fd8b6dc\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"payment_sequential\": 1, \"row_hash\": \"a4e78c01ea8a0970b92035fa280a59a9f71e6b9a366fa5789e8caad5e1137870\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"payment_sequential\": 1, \"row_hash\": \"305bf4232d86e9aa1820206099d70394f7ddd1b63c620e3c11e3d29445d275fa\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"payment_sequential\": 2, \"row_hash\": \"f4b47a2b0dde31053d3f0cd8520eebe75d3ac867bdb26438d6e233914ea4b355\"}]}, \"order_reviews\": {\"manifest_sha256\": \"a9726e9b86a974f26367081574f6e7a8a1f47b57ae389b760fab3580fd59313f\", \"row_count\": 12, \"rows\": [{\"is_deleted\": false, \"review_id\": \"review_001\", \"row_hash\": \"ce68d93e3f41387798241b2606709a2affcd6eca26f94778218ee71e9582ebd1\"}, {\"is_deleted\": false, \"review_id\": \"review_002\", \"row_hash\": \"b583026fb692bed89bcdc5b6166498161e509aea537c9d8dac41b7bad1385be5\"}, {\"is_deleted\": false, \"review_id\": \"review_003\", \"row_hash\": \"6b20f420b88ebebbb39e68b53a5c42e8ff74e9097a4390f200a04c6d90beee39\"}, {\"is_deleted\": false, \"review_id\": \"review_004\", \"row_hash\": \"ae5cb8ee890d5486c20589d12099119db53fe173acbe463a805f29fd7873bf9f\"}, {\"is_deleted\": false, \"review_id\": \"review_005\", \"row_hash\": \"fb0dba632f405b8e5d5d08547c4146198bacac259902f8d4cf4fb821008a116e\"}, {\"is_deleted\": false, \"review_id\": \"review_006\", \"row_hash\": \"65a12285c329ef79c536f03bf90f64cce4bec177df73ed1b095bfb297b7468f7\"}, {\"is_deleted\": false, \"review_id\": \"review_007\", \"row_hash\": \"e5c510c11e907b0b6a03dc98fc9cb093cd804d1961676accff9b4f2e68ed4020\"}, {\"is_deleted\": false, \"review_id\": \"review_008\", \"row_hash\": \"a0bba76263d315bd8e51f80d94ee30a572f58fde30918b83d60997ec2240e084\"}, {\"is_deleted\": false, \"review_id\": \"review_009\", \"row_hash\": \"39c6898d4f43e149fe05ea20b5caa480ddced312aca5f86ecfa0bde7a63029b4\"}, {\"is_deleted\": false, \"review_id\": \"review_010\", \"row_hash\": \"724fd7272fec8bb2da540251686e9b779241556c1317c7d5aacf3e9045955c07\"}, {\"is_deleted\": false, \"review_id\": \"review_011\", \"row_hash\": \"67799f4f0c5b59bfbd23b1a12c537e160148fc0080b6600905f1b2245fe70b7c\"}, {\"is_deleted\": false, \"review_id\": \"review_012\", \"row_hash\": \"876c3ae0d4af03706e0ac64c31353375e466c76479cd2c8714b3637b70d1bd14\"}]}, \"orders\": {\"manifest_sha256\": \"820140bf9165f9c63799fda6d1989523e41b24affcbe08934e039453db99b28f\", \"row_count\": 13, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"row_hash\": \"fada5fd81799360365f0f3f2f7e7fd2282cb79a3ca4d679d6321f6367815e329\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"row_hash\": \"8fe73ef692ce87d1e7fabfb0d3e3ae2b601945485b450dc692989e0bb8a0307c\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"row_hash\": \"e833e41529c746c4a9b71026b94582cf2c38d5c6341df83d54caf3b76ff1d193\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"row_hash\": \"2a581f705e2767771716df2e8997eda2e382c6494a873a5bb9321e068b1c8e0a\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"row_hash\": \"2b7a24beb99aca492dd114f9242c41d45ab177643560ff54e0241bdab5bf660e\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"row_hash\": \"cbdb7ae5c2bb413e4f06f655b22dcae2d5db5d6ce05a029d5c12dd53bc576774\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"row_hash\": \"0352d0852e4a15d0fd3e5f13d12c653a3934204026984f6431772d97db09ed8b\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"row_hash\": \"d7df4b5849d0ff8ba4235ed9dd23eae8e5b248b4f1b757b7b14d4f282a938240\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"row_hash\": \"32be1be57cba3d2b3434d7896b6f189aebd24af63c0bf260a5a03106c165c0a9\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"row_hash\": \"e5e90df101e4a37d68ad0d370e19c1bd7c4df584213c70d544703d1f74089a67\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"row_hash\": \"adc16f849c3cdef0c960d41d63c1b16eacd16451d1fa1233afb4b2e9107cc74e\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"row_hash\": \"d55ce1a8050fda8baeec458d3b75a511565f13b1716de8db82711cca4f5c5685\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"row_hash\": \"3f126287622599f71b701dcdeae241e7ef27976d9ebf477968295a8f390a3adc\"}]}, \"product_category_translation\": {\"manifest_sha256\": \"fb943b0ee210613a5db749d5dde4c88b31bc2702622c245497415674766c78ae\", \"row_count\": 5, \"rows\": [{\"is_deleted\": false, \"product_category_name\": \"beleza_saude\", \"row_hash\": \"cd7108f72c72c22e5596eaa11887855bcaed985a4455252168ada7cfbae7d2ae\"}, {\"is_deleted\": false, \"product_category_name\": \"informatica_acessorios\", \"row_hash\": \"f7e085e2b205fc34cf22d020d86e0401900ddd53a86ad8454dd00e3b2048569d\"}, {\"is_deleted\": false, \"product_category_name\": \"moveis_decoracao\", \"row_hash\": \"a30afc8bce67a9c25fa537f02b7ac8966f7e1c1508b69f0560eec4c49872df5a\"}, {\"is_deleted\": false, \"product_category_name\": \"telefonia\", \"row_hash\": \"6d2ed878891db72a489df091f6dcfba0108e79872a67f595499823a84974ba57\"}, {\"is_deleted\": false, \"product_category_name\": \"utilidades_domesticas\", \"row_hash\": \"3ca9361539f5cc8f2ae0ba8574ca45b2a72f642930b46b76626e1959aaa37972\"}]}, \"products\": {\"manifest_sha256\": \"1a103d949cbcc175f44d038284930510ff41ed8271ba24d2705b1e867adc56ab\", \"row_count\": 8, \"rows\": [{\"is_deleted\": false, \"product_id\": \"product_001\", \"row_hash\": \"eb48389bc974f6e16576aba40dce122e708a92688ac3f737b374ce7d315261c1\"}, {\"is_deleted\": false, \"product_id\": \"product_002\", \"row_hash\": \"e2f0e4025ea03a83d2a12c368550f99ce55764a1f074492c92d46f5a1bfa329e\"}, {\"is_deleted\": false, \"product_id\": \"product_003\", \"row_hash\": \"37db3f8b4dff5a83224a72b2b1a69e8be383226bd865087c391668bcd90e71f3\"}, {\"is_deleted\": false, \"product_id\": \"product_004\", \"row_hash\": \"8f9702ee001bbde6c39488863d031a77c63eac41518ad8ff980ea5ff6e757542\"}, {\"is_deleted\": false, \"product_id\": \"product_005\", \"row_hash\": \"6b418454cbf219b7c0a7b62b15013a0897eb0e90fc0cdd3675acc081a1952bfe\"}, {\"is_deleted\": false, \"product_id\": \"product_006\", \"row_hash\": \"4ceb44986ab7d2e165f5282350cf94af482def9cfa7acf740a32b0cd214698aa\"}, {\"is_deleted\": false, \"product_id\": \"product_007\", \"row_hash\": \"4bea3afd00092cd3f27dcedf6eedf800580513a12585b57584fe207e864414d2\"}, {\"is_deleted\": false, \"product_id\": \"product_008\", \"row_hash\": \"8f5890b61905a2faec5299473b988c15b58c640c32184da6aeaad0b2e42ff66d\"}]}, \"sellers\": {\"manifest_sha256\": \"57e892beb9296880003f697df09dc297229147170b5bc9ebc3bcaa6dbe70f57d\", \"row_count\": 4, \"rows\": [{\"is_deleted\": false, \"row_hash\": \"544d88ba003be3195cbd48ec3de37509ad5562137cc62ae7a365f0e6252f4873\", \"seller_id\": \"seller_001\"}, {\"is_deleted\": false, \"row_hash\": \"2005aa0cdb07be24feb69dd6534283fbc30207290a0b62edff161e65c93e1868\", \"seller_id\": \"seller_002\"}, {\"is_deleted\": false, \"row_hash\": \"6c3fd29b27b37ba4c6a6ff3edbdecc9784bb89563f50718dd67044ec2436e661\", \"seller_id\": \"seller_003\"}, {\"is_deleted\": false, \"row_hash\": \"113871d5a6e2ef39c649ee9a78d51788343c9d2e1d912303deedb93ed473131c\", \"seller_id\": \"seller_004\"}]}}}, \"runtime\": {\"last_published_sync_run_seq\": 4, \"lease_owner_id\": null, \"source_snapshot_completed\": true}, \"stable_current_counts\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"status\": \"ready\", \"sync_run_id\": \"sync-00000000000000000004\", \"sync_run_seq\": 4}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 33.146,
      "gate": "09-rebuild",
      "status": "PASS",
      "timestamp": "2026-08-04T15:58:55.300627+00:00"
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
                "candidate": 10,
                "stable": 10
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
              "customers": 5661301511364570764,
              "order_items": 7260055445008051617,
              "order_payments": 8604726252198231125,
              "order_reviews": 5372656209178888275,
              "orders": 1034207959551505294,
              "product_category_translation": 4378261172774740424,
              "products": 8405389069284592997,
              "sellers": 8065609369146321385
            },
            "materialized_event_count": 90,
            "row_manifests": {
              "candidate_physical": {
                "customers": {
                  "manifest_sha256": "d6a5f54143df5300268413dcecaeeae0a04c588748a410320d85bdff3f298b2c",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "89ab2f62f07ee82dbdd1ae16117ad47979248c38760527041e32234682954c85"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "3a192bd6290c000cc1febc688fa1b3ecdf958809a41d12088dba58891a5da1c6"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "1b0046875b6d0b5b885fd41e2fd786033e8d5ca072ef25e8183d4542757ea33c"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "d634c2bb23d334b22578fc16a3f999a7fc00a2d186485bdd496617f2218bd74b"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "09cccb56bb6ac7f80cd494acabe5d911e61d7ae1d964c16ff790689f750f067b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "89fad7a5227a28282e16ba2cc8d113a8eaa7513bdb3e2a2da37e2ecf572f92e8"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "2c7b1778c310ddfedc92b2f27a5fa019ae1ddf17488e1ef28ce67a9ae1d9e4f9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "5639c71dd4d12217d94951f14f03eae4bd4abc560d1c6d23bc7ccb8dd3ba03b6"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "a75b340c2c1f027bb1217116f516238dcadb7094de9e0890337902c111c49f53"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "6f5f8124e64aec5e0a8510daa2b0866a4ab2ff02ee2e9ce6f6b9223663eaa9a2",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1977794759b3ec343596436e3934e66e8c558c8898614a082cba6471de9d039e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "f32c450df3aa968cb753da8afc6276af2a3b9d727ef09d76497ee926ac9a0726"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "33d79dde3cd0240226c1ef559a8283e67186af636336576f523f08d5ef4806cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "105509c2c83d9a892268219c4a8cc5ef5d07b2e1dfdcc2c972dc2e16a651b7f2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "35eb0ee1af3c9f296b097ee79ad2e2e14e1903c22afd8e2a4e7a3647991d9e2e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "89ea878484dd532f38e75bf25ec4bec4313d160840154b8117581234332bc41d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "4694609b3768ce8f16ae6a45cbc7fe9ad5eaae00411cdb2668f81079ea8b1d19"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "f8ea173a7aded2a525c61b40674f0b2e5ed23a9fe035863cf19e97ea7b3a89c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "851e5a3dbf8604b382de69b085273bfba69fd549ed56ba40c5bd94c55499bb7b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "3e3991e79ec9e19f558cd88ef2f12cc5b8a46fda127c6a8248eeb949bfeb1f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "57c81b3b00e28d8949d847c16b283f7712416dc442d389f623f29c1bfb06a26c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "425bc2716b33cb2419919e3f727410465f2ad5afb55a9202bbc8f3c17ccb03f8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "389f22d86008d40537fb1b786003b4a01e1b5ee97eaab60ef8ab0b7708c8ebe8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3670c8008bfae0adf652945e3e0db009f1d97aeef4bdaa6765cd31511372f744"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "2caa530c697d498bb7f2769e714524a29ea1441db42f9db0782fce6cdc4616ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "a8874fdce193e31aeb772a7cff9849f68a63937b4f7cfe5ea73101be332236e6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "438349cddfc22426ffcb71243f54210010e91e377fcb7de48befba856ffa01d6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "5c1d2e75e7939078406a8d82052cba363b10c25a18ff847f570d50688cd50295"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "b7f20300651573509a976f9579056c462de6a2397fc7e7895437802e79d0867d",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "0d50f161adc12f443d89c3291c41198f8a042aab383efe97670fcbc5a37096da"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "4eb5c2975c1f31cfec36c8192a8e4d4fea817058a6ccb8b4af8e693126201717"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "0fcabf6d1133f7662ba91b3c5adf5e9ee84f75f0506c672163f35632ee311d1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "57aace58c7aeecddf7c79be2b8c1fa761db82b16929b56f451c182b74fd5a1e2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "8a37f338d2d9b06687978117a3ed88dd6ac81d77459a9aefdd3963da63f360c9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "809383f342e45e18fe73122ca945cc743dcbb5745c10d1c6cb8ba33322f8caee"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "d9bc37dc49eb9a2eb3b629adbca76a109916c17fe9c7ad7273876b9ac2097dce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "78543816f081471fb95712be39a71d25c9f45d19d198409e50fb07231fad2869"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "f0f6fa77b8b70951fe7c1b7988c0ecd418cb4c0728e086afac5a9cdf77cf6148"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "6381f5c559155fb588a2221a9b4320368410ccbf2028d3758ea8b0bd60426c40"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "67fda8aea9b21d87c023b3f511b377cbad5fafe98841ddc9d86b05b4a393dee8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "643b3a6835d5abfbbec3a932e1f631dff78717d9108458d09a758892afe0659e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "997ef7f136abc78cc56056c1606ec8024979671e603dc4814191b4fd8fd8b6dc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "a4e78c01ea8a0970b92035fa280a59a9f71e6b9a366fa5789e8caad5e1137870"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "305bf4232d86e9aa1820206099d70394f7ddd1b63c620e3c11e3d29445d275fa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "f4b47a2b0dde31053d3f0cd8520eebe75d3ac867bdb26438d6e233914ea4b355"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "9763aa2c24b67661cb49b67c9ebd7a9829050afcceffcae79ce92ab36711221b",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "ce68d93e3f41387798241b2606709a2affcd6eca26f94778218ee71e9582ebd1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "b583026fb692bed89bcdc5b6166498161e509aea537c9d8dac41b7bad1385be5"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "6b20f420b88ebebbb39e68b53a5c42e8ff74e9097a4390f200a04c6d90beee39"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "ae5cb8ee890d5486c20589d12099119db53fe173acbe463a805f29fd7873bf9f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "fb0dba632f405b8e5d5d08547c4146198bacac259902f8d4cf4fb821008a116e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "65a12285c329ef79c536f03bf90f64cce4bec177df73ed1b095bfb297b7468f7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "e5c510c11e907b0b6a03dc98fc9cb093cd804d1961676accff9b4f2e68ed4020"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a0bba76263d315bd8e51f80d94ee30a572f58fde30918b83d60997ec2240e084"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "39c6898d4f43e149fe05ea20b5caa480ddced312aca5f86ecfa0bde7a63029b4"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "724fd7272fec8bb2da540251686e9b779241556c1317c7d5aacf3e9045955c07"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "67799f4f0c5b59bfbd23b1a12c537e160148fc0080b6600905f1b2245fe70b7c"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "876c3ae0d4af03706e0ac64c31353375e466c76479cd2c8714b3637b70d1bd14"
                    },
                    {
                      "is_deleted": true,
                      "review_id": "wave2_review_001",
                      "row_hash": "d86306f9c001d524a7050108279dab9c93cffa0883e2e9f729af8d8db411ca76"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "820140bf9165f9c63799fda6d1989523e41b24affcbe08934e039453db99b28f",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "fada5fd81799360365f0f3f2f7e7fd2282cb79a3ca4d679d6321f6367815e329"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8fe73ef692ce87d1e7fabfb0d3e3ae2b601945485b450dc692989e0bb8a0307c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "e833e41529c746c4a9b71026b94582cf2c38d5c6341df83d54caf3b76ff1d193"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "2a581f705e2767771716df2e8997eda2e382c6494a873a5bb9321e068b1c8e0a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "2b7a24beb99aca492dd114f9242c41d45ab177643560ff54e0241bdab5bf660e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "cbdb7ae5c2bb413e4f06f655b22dcae2d5db5d6ce05a029d5c12dd53bc576774"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "0352d0852e4a15d0fd3e5f13d12c653a3934204026984f6431772d97db09ed8b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "d7df4b5849d0ff8ba4235ed9dd23eae8e5b248b4f1b757b7b14d4f282a938240"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "32be1be57cba3d2b3434d7896b6f189aebd24af63c0bf260a5a03106c165c0a9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "e5e90df101e4a37d68ad0d370e19c1bd7c4df584213c70d544703d1f74089a67"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "adc16f849c3cdef0c960d41d63c1b16eacd16451d1fa1233afb4b2e9107cc74e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d55ce1a8050fda8baeec458d3b75a511565f13b1716de8db82711cca4f5c5685"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "3f126287622599f71b701dcdeae241e7ef27976d9ebf477968295a8f390a3adc"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "fb943b0ee210613a5db749d5dde4c88b31bc2702622c245497415674766c78ae",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "cd7108f72c72c22e5596eaa11887855bcaed985a4455252168ada7cfbae7d2ae"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "f7e085e2b205fc34cf22d020d86e0401900ddd53a86ad8454dd00e3b2048569d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "a30afc8bce67a9c25fa537f02b7ac8966f7e1c1508b69f0560eec4c49872df5a"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "6d2ed878891db72a489df091f6dcfba0108e79872a67f595499823a84974ba57"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "3ca9361539f5cc8f2ae0ba8574ca45b2a72f642930b46b76626e1959aaa37972"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1a103d949cbcc175f44d038284930510ff41ed8271ba24d2705b1e867adc56ab",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "eb48389bc974f6e16576aba40dce122e708a92688ac3f737b374ce7d315261c1"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f0e4025ea03a83d2a12c368550f99ce55764a1f074492c92d46f5a1bfa329e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "37db3f8b4dff5a83224a72b2b1a69e8be383226bd865087c391668bcd90e71f3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "8f9702ee001bbde6c39488863d031a77c63eac41518ad8ff980ea5ff6e757542"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "6b418454cbf219b7c0a7b62b15013a0897eb0e90fc0cdd3675acc081a1952bfe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4ceb44986ab7d2e165f5282350cf94af482def9cfa7acf740a32b0cd214698aa"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "4bea3afd00092cd3f27dcedf6eedf800580513a12585b57584fe207e864414d2"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "8f5890b61905a2faec5299473b988c15b58c640c32184da6aeaad0b2e42ff66d"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "57e892beb9296880003f697df09dc297229147170b5bc9ebc3bcaa6dbe70f57d",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "544d88ba003be3195cbd48ec3de37509ad5562137cc62ae7a365f0e6252f4873",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "2005aa0cdb07be24feb69dd6534283fbc30207290a0b62edff161e65c93e1868",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6c3fd29b27b37ba4c6a6ff3edbdecc9784bb89563f50718dd67044ec2436e661",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "113871d5a6e2ef39c649ee9a78d51788343c9d2e1d912303deedb93ed473131c",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "candidate_visible": {
                "customers": {
                  "manifest_sha256": "d6a5f54143df5300268413dcecaeeae0a04c588748a410320d85bdff3f298b2c",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "89ab2f62f07ee82dbdd1ae16117ad47979248c38760527041e32234682954c85"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "3a192bd6290c000cc1febc688fa1b3ecdf958809a41d12088dba58891a5da1c6"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "1b0046875b6d0b5b885fd41e2fd786033e8d5ca072ef25e8183d4542757ea33c"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "d634c2bb23d334b22578fc16a3f999a7fc00a2d186485bdd496617f2218bd74b"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "09cccb56bb6ac7f80cd494acabe5d911e61d7ae1d964c16ff790689f750f067b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "89fad7a5227a28282e16ba2cc8d113a8eaa7513bdb3e2a2da37e2ecf572f92e8"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "2c7b1778c310ddfedc92b2f27a5fa019ae1ddf17488e1ef28ce67a9ae1d9e4f9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "5639c71dd4d12217d94951f14f03eae4bd4abc560d1c6d23bc7ccb8dd3ba03b6"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "a75b340c2c1f027bb1217116f516238dcadb7094de9e0890337902c111c49f53"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "6f5f8124e64aec5e0a8510daa2b0866a4ab2ff02ee2e9ce6f6b9223663eaa9a2",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1977794759b3ec343596436e3934e66e8c558c8898614a082cba6471de9d039e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "f32c450df3aa968cb753da8afc6276af2a3b9d727ef09d76497ee926ac9a0726"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "33d79dde3cd0240226c1ef559a8283e67186af636336576f523f08d5ef4806cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "105509c2c83d9a892268219c4a8cc5ef5d07b2e1dfdcc2c972dc2e16a651b7f2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "35eb0ee1af3c9f296b097ee79ad2e2e14e1903c22afd8e2a4e7a3647991d9e2e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "89ea878484dd532f38e75bf25ec4bec4313d160840154b8117581234332bc41d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "4694609b3768ce8f16ae6a45cbc7fe9ad5eaae00411cdb2668f81079ea8b1d19"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "f8ea173a7aded2a525c61b40674f0b2e5ed23a9fe035863cf19e97ea7b3a89c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "851e5a3dbf8604b382de69b085273bfba69fd549ed56ba40c5bd94c55499bb7b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "3e3991e79ec9e19f558cd88ef2f12cc5b8a46fda127c6a8248eeb949bfeb1f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "57c81b3b00e28d8949d847c16b283f7712416dc442d389f623f29c1bfb06a26c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "425bc2716b33cb2419919e3f727410465f2ad5afb55a9202bbc8f3c17ccb03f8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "389f22d86008d40537fb1b786003b4a01e1b5ee97eaab60ef8ab0b7708c8ebe8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3670c8008bfae0adf652945e3e0db009f1d97aeef4bdaa6765cd31511372f744"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "2caa530c697d498bb7f2769e714524a29ea1441db42f9db0782fce6cdc4616ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "a8874fdce193e31aeb772a7cff9849f68a63937b4f7cfe5ea73101be332236e6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "438349cddfc22426ffcb71243f54210010e91e377fcb7de48befba856ffa01d6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "5c1d2e75e7939078406a8d82052cba363b10c25a18ff847f570d50688cd50295"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "b7f20300651573509a976f9579056c462de6a2397fc7e7895437802e79d0867d",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "0d50f161adc12f443d89c3291c41198f8a042aab383efe97670fcbc5a37096da"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "4eb5c2975c1f31cfec36c8192a8e4d4fea817058a6ccb8b4af8e693126201717"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "0fcabf6d1133f7662ba91b3c5adf5e9ee84f75f0506c672163f35632ee311d1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "57aace58c7aeecddf7c79be2b8c1fa761db82b16929b56f451c182b74fd5a1e2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "8a37f338d2d9b06687978117a3ed88dd6ac81d77459a9aefdd3963da63f360c9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "809383f342e45e18fe73122ca945cc743dcbb5745c10d1c6cb8ba33322f8caee"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "d9bc37dc49eb9a2eb3b629adbca76a109916c17fe9c7ad7273876b9ac2097dce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "78543816f081471fb95712be39a71d25c9f45d19d198409e50fb07231fad2869"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "f0f6fa77b8b70951fe7c1b7988c0ecd418cb4c0728e086afac5a9cdf77cf6148"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "6381f5c559155fb588a2221a9b4320368410ccbf2028d3758ea8b0bd60426c40"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "67fda8aea9b21d87c023b3f511b377cbad5fafe98841ddc9d86b05b4a393dee8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "643b3a6835d5abfbbec3a932e1f631dff78717d9108458d09a758892afe0659e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "997ef7f136abc78cc56056c1606ec8024979671e603dc4814191b4fd8fd8b6dc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "a4e78c01ea8a0970b92035fa280a59a9f71e6b9a366fa5789e8caad5e1137870"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "305bf4232d86e9aa1820206099d70394f7ddd1b63c620e3c11e3d29445d275fa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "f4b47a2b0dde31053d3f0cd8520eebe75d3ac867bdb26438d6e233914ea4b355"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "a9726e9b86a974f26367081574f6e7a8a1f47b57ae389b760fab3580fd59313f",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "ce68d93e3f41387798241b2606709a2affcd6eca26f94778218ee71e9582ebd1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "b583026fb692bed89bcdc5b6166498161e509aea537c9d8dac41b7bad1385be5"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "6b20f420b88ebebbb39e68b53a5c42e8ff74e9097a4390f200a04c6d90beee39"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "ae5cb8ee890d5486c20589d12099119db53fe173acbe463a805f29fd7873bf9f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "fb0dba632f405b8e5d5d08547c4146198bacac259902f8d4cf4fb821008a116e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "65a12285c329ef79c536f03bf90f64cce4bec177df73ed1b095bfb297b7468f7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "e5c510c11e907b0b6a03dc98fc9cb093cd804d1961676accff9b4f2e68ed4020"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a0bba76263d315bd8e51f80d94ee30a572f58fde30918b83d60997ec2240e084"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "39c6898d4f43e149fe05ea20b5caa480ddced312aca5f86ecfa0bde7a63029b4"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "724fd7272fec8bb2da540251686e9b779241556c1317c7d5aacf3e9045955c07"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "67799f4f0c5b59bfbd23b1a12c537e160148fc0080b6600905f1b2245fe70b7c"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "876c3ae0d4af03706e0ac64c31353375e466c76479cd2c8714b3637b70d1bd14"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "820140bf9165f9c63799fda6d1989523e41b24affcbe08934e039453db99b28f",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "fada5fd81799360365f0f3f2f7e7fd2282cb79a3ca4d679d6321f6367815e329"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8fe73ef692ce87d1e7fabfb0d3e3ae2b601945485b450dc692989e0bb8a0307c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "e833e41529c746c4a9b71026b94582cf2c38d5c6341df83d54caf3b76ff1d193"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "2a581f705e2767771716df2e8997eda2e382c6494a873a5bb9321e068b1c8e0a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "2b7a24beb99aca492dd114f9242c41d45ab177643560ff54e0241bdab5bf660e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "cbdb7ae5c2bb413e4f06f655b22dcae2d5db5d6ce05a029d5c12dd53bc576774"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "0352d0852e4a15d0fd3e5f13d12c653a3934204026984f6431772d97db09ed8b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "d7df4b5849d0ff8ba4235ed9dd23eae8e5b248b4f1b757b7b14d4f282a938240"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "32be1be57cba3d2b3434d7896b6f189aebd24af63c0bf260a5a03106c165c0a9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "e5e90df101e4a37d68ad0d370e19c1bd7c4df584213c70d544703d1f74089a67"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "adc16f849c3cdef0c960d41d63c1b16eacd16451d1fa1233afb4b2e9107cc74e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d55ce1a8050fda8baeec458d3b75a511565f13b1716de8db82711cca4f5c5685"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "3f126287622599f71b701dcdeae241e7ef27976d9ebf477968295a8f390a3adc"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "fb943b0ee210613a5db749d5dde4c88b31bc2702622c245497415674766c78ae",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "cd7108f72c72c22e5596eaa11887855bcaed985a4455252168ada7cfbae7d2ae"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "f7e085e2b205fc34cf22d020d86e0401900ddd53a86ad8454dd00e3b2048569d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "a30afc8bce67a9c25fa537f02b7ac8966f7e1c1508b69f0560eec4c49872df5a"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "6d2ed878891db72a489df091f6dcfba0108e79872a67f595499823a84974ba57"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "3ca9361539f5cc8f2ae0ba8574ca45b2a72f642930b46b76626e1959aaa37972"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1a103d949cbcc175f44d038284930510ff41ed8271ba24d2705b1e867adc56ab",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "eb48389bc974f6e16576aba40dce122e708a92688ac3f737b374ce7d315261c1"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f0e4025ea03a83d2a12c368550f99ce55764a1f074492c92d46f5a1bfa329e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "37db3f8b4dff5a83224a72b2b1a69e8be383226bd865087c391668bcd90e71f3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "8f9702ee001bbde6c39488863d031a77c63eac41518ad8ff980ea5ff6e757542"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "6b418454cbf219b7c0a7b62b15013a0897eb0e90fc0cdd3675acc081a1952bfe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4ceb44986ab7d2e165f5282350cf94af482def9cfa7acf740a32b0cd214698aa"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "4bea3afd00092cd3f27dcedf6eedf800580513a12585b57584fe207e864414d2"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "8f5890b61905a2faec5299473b988c15b58c640c32184da6aeaad0b2e42ff66d"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "57e892beb9296880003f697df09dc297229147170b5bc9ebc3bcaa6dbe70f57d",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "544d88ba003be3195cbd48ec3de37509ad5562137cc62ae7a365f0e6252f4873",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "2005aa0cdb07be24feb69dd6534283fbc30207290a0b62edff161e65c93e1868",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6c3fd29b27b37ba4c6a6ff3edbdecc9784bb89563f50718dd67044ec2436e661",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "113871d5a6e2ef39c649ee9a78d51788343c9d2e1d912303deedb93ed473131c",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "iceberg_physical": {
                "customers": {
                  "manifest_sha256": "d6a5f54143df5300268413dcecaeeae0a04c588748a410320d85bdff3f298b2c",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "89ab2f62f07ee82dbdd1ae16117ad47979248c38760527041e32234682954c85"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "3a192bd6290c000cc1febc688fa1b3ecdf958809a41d12088dba58891a5da1c6"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "1b0046875b6d0b5b885fd41e2fd786033e8d5ca072ef25e8183d4542757ea33c"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "d634c2bb23d334b22578fc16a3f999a7fc00a2d186485bdd496617f2218bd74b"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "09cccb56bb6ac7f80cd494acabe5d911e61d7ae1d964c16ff790689f750f067b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "89fad7a5227a28282e16ba2cc8d113a8eaa7513bdb3e2a2da37e2ecf572f92e8"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "2c7b1778c310ddfedc92b2f27a5fa019ae1ddf17488e1ef28ce67a9ae1d9e4f9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "5639c71dd4d12217d94951f14f03eae4bd4abc560d1c6d23bc7ccb8dd3ba03b6"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "a75b340c2c1f027bb1217116f516238dcadb7094de9e0890337902c111c49f53"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "6f5f8124e64aec5e0a8510daa2b0866a4ab2ff02ee2e9ce6f6b9223663eaa9a2",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1977794759b3ec343596436e3934e66e8c558c8898614a082cba6471de9d039e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "f32c450df3aa968cb753da8afc6276af2a3b9d727ef09d76497ee926ac9a0726"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "33d79dde3cd0240226c1ef559a8283e67186af636336576f523f08d5ef4806cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "105509c2c83d9a892268219c4a8cc5ef5d07b2e1dfdcc2c972dc2e16a651b7f2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "35eb0ee1af3c9f296b097ee79ad2e2e14e1903c22afd8e2a4e7a3647991d9e2e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "89ea878484dd532f38e75bf25ec4bec4313d160840154b8117581234332bc41d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "4694609b3768ce8f16ae6a45cbc7fe9ad5eaae00411cdb2668f81079ea8b1d19"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "f8ea173a7aded2a525c61b40674f0b2e5ed23a9fe035863cf19e97ea7b3a89c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "851e5a3dbf8604b382de69b085273bfba69fd549ed56ba40c5bd94c55499bb7b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "3e3991e79ec9e19f558cd88ef2f12cc5b8a46fda127c6a8248eeb949bfeb1f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "57c81b3b00e28d8949d847c16b283f7712416dc442d389f623f29c1bfb06a26c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "425bc2716b33cb2419919e3f727410465f2ad5afb55a9202bbc8f3c17ccb03f8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "389f22d86008d40537fb1b786003b4a01e1b5ee97eaab60ef8ab0b7708c8ebe8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3670c8008bfae0adf652945e3e0db009f1d97aeef4bdaa6765cd31511372f744"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "2caa530c697d498bb7f2769e714524a29ea1441db42f9db0782fce6cdc4616ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "a8874fdce193e31aeb772a7cff9849f68a63937b4f7cfe5ea73101be332236e6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "438349cddfc22426ffcb71243f54210010e91e377fcb7de48befba856ffa01d6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "5c1d2e75e7939078406a8d82052cba363b10c25a18ff847f570d50688cd50295"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "b7f20300651573509a976f9579056c462de6a2397fc7e7895437802e79d0867d",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "0d50f161adc12f443d89c3291c41198f8a042aab383efe97670fcbc5a37096da"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "4eb5c2975c1f31cfec36c8192a8e4d4fea817058a6ccb8b4af8e693126201717"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "0fcabf6d1133f7662ba91b3c5adf5e9ee84f75f0506c672163f35632ee311d1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "57aace58c7aeecddf7c79be2b8c1fa761db82b16929b56f451c182b74fd5a1e2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "8a37f338d2d9b06687978117a3ed88dd6ac81d77459a9aefdd3963da63f360c9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "809383f342e45e18fe73122ca945cc743dcbb5745c10d1c6cb8ba33322f8caee"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "d9bc37dc49eb9a2eb3b629adbca76a109916c17fe9c7ad7273876b9ac2097dce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "78543816f081471fb95712be39a71d25c9f45d19d198409e50fb07231fad2869"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "f0f6fa77b8b70951fe7c1b7988c0ecd418cb4c0728e086afac5a9cdf77cf6148"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "6381f5c559155fb588a2221a9b4320368410ccbf2028d3758ea8b0bd60426c40"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "67fda8aea9b21d87c023b3f511b377cbad5fafe98841ddc9d86b05b4a393dee8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "643b3a6835d5abfbbec3a932e1f631dff78717d9108458d09a758892afe0659e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "997ef7f136abc78cc56056c1606ec8024979671e603dc4814191b4fd8fd8b6dc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "a4e78c01ea8a0970b92035fa280a59a9f71e6b9a366fa5789e8caad5e1137870"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "305bf4232d86e9aa1820206099d70394f7ddd1b63c620e3c11e3d29445d275fa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "f4b47a2b0dde31053d3f0cd8520eebe75d3ac867bdb26438d6e233914ea4b355"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "9763aa2c24b67661cb49b67c9ebd7a9829050afcceffcae79ce92ab36711221b",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "ce68d93e3f41387798241b2606709a2affcd6eca26f94778218ee71e9582ebd1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "b583026fb692bed89bcdc5b6166498161e509aea537c9d8dac41b7bad1385be5"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "6b20f420b88ebebbb39e68b53a5c42e8ff74e9097a4390f200a04c6d90beee39"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "ae5cb8ee890d5486c20589d12099119db53fe173acbe463a805f29fd7873bf9f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "fb0dba632f405b8e5d5d08547c4146198bacac259902f8d4cf4fb821008a116e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "65a12285c329ef79c536f03bf90f64cce4bec177df73ed1b095bfb297b7468f7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "e5c510c11e907b0b6a03dc98fc9cb093cd804d1961676accff9b4f2e68ed4020"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a0bba76263d315bd8e51f80d94ee30a572f58fde30918b83d60997ec2240e084"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "39c6898d4f43e149fe05ea20b5caa480ddced312aca5f86ecfa0bde7a63029b4"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "724fd7272fec8bb2da540251686e9b779241556c1317c7d5aacf3e9045955c07"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "67799f4f0c5b59bfbd23b1a12c537e160148fc0080b6600905f1b2245fe70b7c"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "876c3ae0d4af03706e0ac64c31353375e466c76479cd2c8714b3637b70d1bd14"
                    },
                    {
                      "is_deleted": true,
                      "review_id": "wave2_review_001",
                      "row_hash": "d86306f9c001d524a7050108279dab9c93cffa0883e2e9f729af8d8db411ca76"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "820140bf9165f9c63799fda6d1989523e41b24affcbe08934e039453db99b28f",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "fada5fd81799360365f0f3f2f7e7fd2282cb79a3ca4d679d6321f6367815e329"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8fe73ef692ce87d1e7fabfb0d3e3ae2b601945485b450dc692989e0bb8a0307c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "e833e41529c746c4a9b71026b94582cf2c38d5c6341df83d54caf3b76ff1d193"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "2a581f705e2767771716df2e8997eda2e382c6494a873a5bb9321e068b1c8e0a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "2b7a24beb99aca492dd114f9242c41d45ab177643560ff54e0241bdab5bf660e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "cbdb7ae5c2bb413e4f06f655b22dcae2d5db5d6ce05a029d5c12dd53bc576774"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "0352d0852e4a15d0fd3e5f13d12c653a3934204026984f6431772d97db09ed8b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "d7df4b5849d0ff8ba4235ed9dd23eae8e5b248b4f1b757b7b14d4f282a938240"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "32be1be57cba3d2b3434d7896b6f189aebd24af63c0bf260a5a03106c165c0a9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "e5e90df101e4a37d68ad0d370e19c1bd7c4df584213c70d544703d1f74089a67"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "adc16f849c3cdef0c960d41d63c1b16eacd16451d1fa1233afb4b2e9107cc74e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d55ce1a8050fda8baeec458d3b75a511565f13b1716de8db82711cca4f5c5685"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "3f126287622599f71b701dcdeae241e7ef27976d9ebf477968295a8f390a3adc"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "fb943b0ee210613a5db749d5dde4c88b31bc2702622c245497415674766c78ae",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "cd7108f72c72c22e5596eaa11887855bcaed985a4455252168ada7cfbae7d2ae"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "f7e085e2b205fc34cf22d020d86e0401900ddd53a86ad8454dd00e3b2048569d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "a30afc8bce67a9c25fa537f02b7ac8966f7e1c1508b69f0560eec4c49872df5a"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "6d2ed878891db72a489df091f6dcfba0108e79872a67f595499823a84974ba57"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "3ca9361539f5cc8f2ae0ba8574ca45b2a72f642930b46b76626e1959aaa37972"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1a103d949cbcc175f44d038284930510ff41ed8271ba24d2705b1e867adc56ab",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "eb48389bc974f6e16576aba40dce122e708a92688ac3f737b374ce7d315261c1"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f0e4025ea03a83d2a12c368550f99ce55764a1f074492c92d46f5a1bfa329e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "37db3f8b4dff5a83224a72b2b1a69e8be383226bd865087c391668bcd90e71f3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "8f9702ee001bbde6c39488863d031a77c63eac41518ad8ff980ea5ff6e757542"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "6b418454cbf219b7c0a7b62b15013a0897eb0e90fc0cdd3675acc081a1952bfe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4ceb44986ab7d2e165f5282350cf94af482def9cfa7acf740a32b0cd214698aa"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "4bea3afd00092cd3f27dcedf6eedf800580513a12585b57584fe207e864414d2"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "8f5890b61905a2faec5299473b988c15b58c640c32184da6aeaad0b2e42ff66d"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "57e892beb9296880003f697df09dc297229147170b5bc9ebc3bcaa6dbe70f57d",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "544d88ba003be3195cbd48ec3de37509ad5562137cc62ae7a365f0e6252f4873",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "2005aa0cdb07be24feb69dd6534283fbc30207290a0b62edff161e65c93e1868",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6c3fd29b27b37ba4c6a6ff3edbdecc9784bb89563f50718dd67044ec2436e661",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "113871d5a6e2ef39c649ee9a78d51788343c9d2e1d912303deedb93ed473131c",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "iceberg_visible": {
                "customers": {
                  "manifest_sha256": "d6a5f54143df5300268413dcecaeeae0a04c588748a410320d85bdff3f298b2c",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "89ab2f62f07ee82dbdd1ae16117ad47979248c38760527041e32234682954c85"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "3a192bd6290c000cc1febc688fa1b3ecdf958809a41d12088dba58891a5da1c6"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "1b0046875b6d0b5b885fd41e2fd786033e8d5ca072ef25e8183d4542757ea33c"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "d634c2bb23d334b22578fc16a3f999a7fc00a2d186485bdd496617f2218bd74b"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "09cccb56bb6ac7f80cd494acabe5d911e61d7ae1d964c16ff790689f750f067b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "89fad7a5227a28282e16ba2cc8d113a8eaa7513bdb3e2a2da37e2ecf572f92e8"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "2c7b1778c310ddfedc92b2f27a5fa019ae1ddf17488e1ef28ce67a9ae1d9e4f9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "5639c71dd4d12217d94951f14f03eae4bd4abc560d1c6d23bc7ccb8dd3ba03b6"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "a75b340c2c1f027bb1217116f516238dcadb7094de9e0890337902c111c49f53"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "6f5f8124e64aec5e0a8510daa2b0866a4ab2ff02ee2e9ce6f6b9223663eaa9a2",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1977794759b3ec343596436e3934e66e8c558c8898614a082cba6471de9d039e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "f32c450df3aa968cb753da8afc6276af2a3b9d727ef09d76497ee926ac9a0726"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "33d79dde3cd0240226c1ef559a8283e67186af636336576f523f08d5ef4806cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "105509c2c83d9a892268219c4a8cc5ef5d07b2e1dfdcc2c972dc2e16a651b7f2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "35eb0ee1af3c9f296b097ee79ad2e2e14e1903c22afd8e2a4e7a3647991d9e2e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "89ea878484dd532f38e75bf25ec4bec4313d160840154b8117581234332bc41d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "4694609b3768ce8f16ae6a45cbc7fe9ad5eaae00411cdb2668f81079ea8b1d19"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "f8ea173a7aded2a525c61b40674f0b2e5ed23a9fe035863cf19e97ea7b3a89c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "851e5a3dbf8604b382de69b085273bfba69fd549ed56ba40c5bd94c55499bb7b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "3e3991e79ec9e19f558cd88ef2f12cc5b8a46fda127c6a8248eeb949bfeb1f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "57c81b3b00e28d8949d847c16b283f7712416dc442d389f623f29c1bfb06a26c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "425bc2716b33cb2419919e3f727410465f2ad5afb55a9202bbc8f3c17ccb03f8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "389f22d86008d40537fb1b786003b4a01e1b5ee97eaab60ef8ab0b7708c8ebe8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3670c8008bfae0adf652945e3e0db009f1d97aeef4bdaa6765cd31511372f744"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "2caa530c697d498bb7f2769e714524a29ea1441db42f9db0782fce6cdc4616ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "a8874fdce193e31aeb772a7cff9849f68a63937b4f7cfe5ea73101be332236e6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "438349cddfc22426ffcb71243f54210010e91e377fcb7de48befba856ffa01d6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "5c1d2e75e7939078406a8d82052cba363b10c25a18ff847f570d50688cd50295"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "b7f20300651573509a976f9579056c462de6a2397fc7e7895437802e79d0867d",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "0d50f161adc12f443d89c3291c41198f8a042aab383efe97670fcbc5a37096da"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "4eb5c2975c1f31cfec36c8192a8e4d4fea817058a6ccb8b4af8e693126201717"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "0fcabf6d1133f7662ba91b3c5adf5e9ee84f75f0506c672163f35632ee311d1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "57aace58c7aeecddf7c79be2b8c1fa761db82b16929b56f451c182b74fd5a1e2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "8a37f338d2d9b06687978117a3ed88dd6ac81d77459a9aefdd3963da63f360c9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "809383f342e45e18fe73122ca945cc743dcbb5745c10d1c6cb8ba33322f8caee"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "d9bc37dc49eb9a2eb3b629adbca76a109916c17fe9c7ad7273876b9ac2097dce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "78543816f081471fb95712be39a71d25c9f45d19d198409e50fb07231fad2869"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "f0f6fa77b8b70951fe7c1b7988c0ecd418cb4c0728e086afac5a9cdf77cf6148"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "6381f5c559155fb588a2221a9b4320368410ccbf2028d3758ea8b0bd60426c40"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "67fda8aea9b21d87c023b3f511b377cbad5fafe98841ddc9d86b05b4a393dee8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "643b3a6835d5abfbbec3a932e1f631dff78717d9108458d09a758892afe0659e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "997ef7f136abc78cc56056c1606ec8024979671e603dc4814191b4fd8fd8b6dc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "a4e78c01ea8a0970b92035fa280a59a9f71e6b9a366fa5789e8caad5e1137870"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "305bf4232d86e9aa1820206099d70394f7ddd1b63c620e3c11e3d29445d275fa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "f4b47a2b0dde31053d3f0cd8520eebe75d3ac867bdb26438d6e233914ea4b355"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "a9726e9b86a974f26367081574f6e7a8a1f47b57ae389b760fab3580fd59313f",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "ce68d93e3f41387798241b2606709a2affcd6eca26f94778218ee71e9582ebd1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "b583026fb692bed89bcdc5b6166498161e509aea537c9d8dac41b7bad1385be5"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "6b20f420b88ebebbb39e68b53a5c42e8ff74e9097a4390f200a04c6d90beee39"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "ae5cb8ee890d5486c20589d12099119db53fe173acbe463a805f29fd7873bf9f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "fb0dba632f405b8e5d5d08547c4146198bacac259902f8d4cf4fb821008a116e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "65a12285c329ef79c536f03bf90f64cce4bec177df73ed1b095bfb297b7468f7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "e5c510c11e907b0b6a03dc98fc9cb093cd804d1961676accff9b4f2e68ed4020"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a0bba76263d315bd8e51f80d94ee30a572f58fde30918b83d60997ec2240e084"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "39c6898d4f43e149fe05ea20b5caa480ddced312aca5f86ecfa0bde7a63029b4"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "724fd7272fec8bb2da540251686e9b779241556c1317c7d5aacf3e9045955c07"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "67799f4f0c5b59bfbd23b1a12c537e160148fc0080b6600905f1b2245fe70b7c"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "876c3ae0d4af03706e0ac64c31353375e466c76479cd2c8714b3637b70d1bd14"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "820140bf9165f9c63799fda6d1989523e41b24affcbe08934e039453db99b28f",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "fada5fd81799360365f0f3f2f7e7fd2282cb79a3ca4d679d6321f6367815e329"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8fe73ef692ce87d1e7fabfb0d3e3ae2b601945485b450dc692989e0bb8a0307c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "e833e41529c746c4a9b71026b94582cf2c38d5c6341df83d54caf3b76ff1d193"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "2a581f705e2767771716df2e8997eda2e382c6494a873a5bb9321e068b1c8e0a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "2b7a24beb99aca492dd114f9242c41d45ab177643560ff54e0241bdab5bf660e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "cbdb7ae5c2bb413e4f06f655b22dcae2d5db5d6ce05a029d5c12dd53bc576774"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "0352d0852e4a15d0fd3e5f13d12c653a3934204026984f6431772d97db09ed8b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "d7df4b5849d0ff8ba4235ed9dd23eae8e5b248b4f1b757b7b14d4f282a938240"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "32be1be57cba3d2b3434d7896b6f189aebd24af63c0bf260a5a03106c165c0a9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "e5e90df101e4a37d68ad0d370e19c1bd7c4df584213c70d544703d1f74089a67"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "adc16f849c3cdef0c960d41d63c1b16eacd16451d1fa1233afb4b2e9107cc74e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d55ce1a8050fda8baeec458d3b75a511565f13b1716de8db82711cca4f5c5685"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "3f126287622599f71b701dcdeae241e7ef27976d9ebf477968295a8f390a3adc"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "fb943b0ee210613a5db749d5dde4c88b31bc2702622c245497415674766c78ae",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "cd7108f72c72c22e5596eaa11887855bcaed985a4455252168ada7cfbae7d2ae"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "f7e085e2b205fc34cf22d020d86e0401900ddd53a86ad8454dd00e3b2048569d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "a30afc8bce67a9c25fa537f02b7ac8966f7e1c1508b69f0560eec4c49872df5a"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "6d2ed878891db72a489df091f6dcfba0108e79872a67f595499823a84974ba57"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "3ca9361539f5cc8f2ae0ba8574ca45b2a72f642930b46b76626e1959aaa37972"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1a103d949cbcc175f44d038284930510ff41ed8271ba24d2705b1e867adc56ab",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "eb48389bc974f6e16576aba40dce122e708a92688ac3f737b374ce7d315261c1"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f0e4025ea03a83d2a12c368550f99ce55764a1f074492c92d46f5a1bfa329e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "37db3f8b4dff5a83224a72b2b1a69e8be383226bd865087c391668bcd90e71f3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "8f9702ee001bbde6c39488863d031a77c63eac41518ad8ff980ea5ff6e757542"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "6b418454cbf219b7c0a7b62b15013a0897eb0e90fc0cdd3675acc081a1952bfe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4ceb44986ab7d2e165f5282350cf94af482def9cfa7acf740a32b0cd214698aa"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "4bea3afd00092cd3f27dcedf6eedf800580513a12585b57584fe207e864414d2"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "8f5890b61905a2faec5299473b988c15b58c640c32184da6aeaad0b2e42ff66d"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "57e892beb9296880003f697df09dc297229147170b5bc9ebc3bcaa6dbe70f57d",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "544d88ba003be3195cbd48ec3de37509ad5562137cc62ae7a365f0e6252f4873",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "2005aa0cdb07be24feb69dd6534283fbc30207290a0b62edff161e65c93e1868",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6c3fd29b27b37ba4c6a6ff3edbdecc9784bb89563f50718dd67044ec2436e661",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "113871d5a6e2ef39c649ee9a78d51788343c9d2e1d912303deedb93ed473131c",
                      "seller_id": "seller_004"
                    }
                  ]
                }
              },
              "stable_visible": {
                "customers": {
                  "manifest_sha256": "d6a5f54143df5300268413dcecaeeae0a04c588748a410320d85bdff3f298b2c",
                  "row_count": 9,
                  "rows": [
                    {
                      "customer_id": "customer_001",
                      "is_deleted": false,
                      "row_hash": "89ab2f62f07ee82dbdd1ae16117ad47979248c38760527041e32234682954c85"
                    },
                    {
                      "customer_id": "customer_002",
                      "is_deleted": false,
                      "row_hash": "3a192bd6290c000cc1febc688fa1b3ecdf958809a41d12088dba58891a5da1c6"
                    },
                    {
                      "customer_id": "customer_003",
                      "is_deleted": false,
                      "row_hash": "1b0046875b6d0b5b885fd41e2fd786033e8d5ca072ef25e8183d4542757ea33c"
                    },
                    {
                      "customer_id": "customer_004",
                      "is_deleted": false,
                      "row_hash": "d634c2bb23d334b22578fc16a3f999a7fc00a2d186485bdd496617f2218bd74b"
                    },
                    {
                      "customer_id": "customer_005",
                      "is_deleted": false,
                      "row_hash": "09cccb56bb6ac7f80cd494acabe5d911e61d7ae1d964c16ff790689f750f067b"
                    },
                    {
                      "customer_id": "customer_006",
                      "is_deleted": false,
                      "row_hash": "89fad7a5227a28282e16ba2cc8d113a8eaa7513bdb3e2a2da37e2ecf572f92e8"
                    },
                    {
                      "customer_id": "customer_007",
                      "is_deleted": false,
                      "row_hash": "2c7b1778c310ddfedc92b2f27a5fa019ae1ddf17488e1ef28ce67a9ae1d9e4f9"
                    },
                    {
                      "customer_id": "customer_008",
                      "is_deleted": false,
                      "row_hash": "5639c71dd4d12217d94951f14f03eae4bd4abc560d1c6d23bc7ccb8dd3ba03b6"
                    },
                    {
                      "customer_id": "wave2_customer_001",
                      "is_deleted": false,
                      "row_hash": "a75b340c2c1f027bb1217116f516238dcadb7094de9e0890337902c111c49f53"
                    }
                  ]
                },
                "order_items": {
                  "manifest_sha256": "6f5f8124e64aec5e0a8510daa2b0866a4ab2ff02ee2e9ce6f6b9223663eaa9a2",
                  "row_count": 18,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "order_item_id": 1,
                      "row_hash": "1977794759b3ec343596436e3934e66e8c558c8898614a082cba6471de9d039e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "order_item_id": 1,
                      "row_hash": "f32c450df3aa968cb753da8afc6276af2a3b9d727ef09d76497ee926ac9a0726"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 1,
                      "row_hash": "33d79dde3cd0240226c1ef559a8283e67186af636336576f523f08d5ef4806cb"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "order_item_id": 2,
                      "row_hash": "105509c2c83d9a892268219c4a8cc5ef5d07b2e1dfdcc2c972dc2e16a651b7f2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "order_item_id": 1,
                      "row_hash": "35eb0ee1af3c9f296b097ee79ad2e2e14e1903c22afd8e2a4e7a3647991d9e2e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "order_item_id": 1,
                      "row_hash": "89ea878484dd532f38e75bf25ec4bec4313d160840154b8117581234332bc41d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 1,
                      "row_hash": "4694609b3768ce8f16ae6a45cbc7fe9ad5eaae00411cdb2668f81079ea8b1d19"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "order_item_id": 2,
                      "row_hash": "f8ea173a7aded2a525c61b40674f0b2e5ed23a9fe035863cf19e97ea7b3a89c3"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "order_item_id": 1,
                      "row_hash": "851e5a3dbf8604b382de69b085273bfba69fd549ed56ba40c5bd94c55499bb7b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "order_item_id": 1,
                      "row_hash": "3e3991e79ec9e19f558cd88ef2f12cc5b8a46fda127c6a8248eeb949bfeb1f4d"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 1,
                      "row_hash": "57c81b3b00e28d8949d847c16b283f7712416dc442d389f623f29c1bfb06a26c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "order_item_id": 2,
                      "row_hash": "425bc2716b33cb2419919e3f727410465f2ad5afb55a9202bbc8f3c17ccb03f8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "order_item_id": 1,
                      "row_hash": "389f22d86008d40537fb1b786003b4a01e1b5ee97eaab60ef8ab0b7708c8ebe8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "order_item_id": 1,
                      "row_hash": "3670c8008bfae0adf652945e3e0db009f1d97aeef4bdaa6765cd31511372f744"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 1,
                      "row_hash": "2caa530c697d498bb7f2769e714524a29ea1441db42f9db0782fce6cdc4616ae"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "order_item_id": 2,
                      "row_hash": "a8874fdce193e31aeb772a7cff9849f68a63937b4f7cfe5ea73101be332236e6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 1,
                      "row_hash": "438349cddfc22426ffcb71243f54210010e91e377fcb7de48befba856ffa01d6"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "order_item_id": 2,
                      "row_hash": "5c1d2e75e7939078406a8d82052cba363b10c25a18ff847f570d50688cd50295"
                    }
                  ]
                },
                "order_payments": {
                  "manifest_sha256": "b7f20300651573509a976f9579056c462de6a2397fc7e7895437802e79d0867d",
                  "row_count": 16,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "payment_sequential": 1,
                      "row_hash": "0d50f161adc12f443d89c3291c41198f8a042aab383efe97670fcbc5a37096da"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "payment_sequential": 1,
                      "row_hash": "4eb5c2975c1f31cfec36c8192a8e4d4fea817058a6ccb8b4af8e693126201717"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "payment_sequential": 1,
                      "row_hash": "0fcabf6d1133f7662ba91b3c5adf5e9ee84f75f0506c672163f35632ee311d1f"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 1,
                      "row_hash": "57aace58c7aeecddf7c79be2b8c1fa761db82b16929b56f451c182b74fd5a1e2"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "payment_sequential": 2,
                      "row_hash": "8a37f338d2d9b06687978117a3ed88dd6ac81d77459a9aefdd3963da63f360c9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "payment_sequential": 1,
                      "row_hash": "809383f342e45e18fe73122ca945cc743dcbb5745c10d1c6cb8ba33322f8caee"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "payment_sequential": 1,
                      "row_hash": "d9bc37dc49eb9a2eb3b629adbca76a109916c17fe9c7ad7273876b9ac2097dce"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "payment_sequential": 1,
                      "row_hash": "78543816f081471fb95712be39a71d25c9f45d19d198409e50fb07231fad2869"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 1,
                      "row_hash": "f0f6fa77b8b70951fe7c1b7988c0ecd418cb4c0728e086afac5a9cdf77cf6148"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "payment_sequential": 2,
                      "row_hash": "6381f5c559155fb588a2221a9b4320368410ccbf2028d3758ea8b0bd60426c40"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "payment_sequential": 1,
                      "row_hash": "67fda8aea9b21d87c023b3f511b377cbad5fafe98841ddc9d86b05b4a393dee8"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "payment_sequential": 1,
                      "row_hash": "643b3a6835d5abfbbec3a932e1f631dff78717d9108458d09a758892afe0659e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "payment_sequential": 1,
                      "row_hash": "997ef7f136abc78cc56056c1606ec8024979671e603dc4814191b4fd8fd8b6dc"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "payment_sequential": 1,
                      "row_hash": "a4e78c01ea8a0970b92035fa280a59a9f71e6b9a366fa5789e8caad5e1137870"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 1,
                      "row_hash": "305bf4232d86e9aa1820206099d70394f7ddd1b63c620e3c11e3d29445d275fa"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "payment_sequential": 2,
                      "row_hash": "f4b47a2b0dde31053d3f0cd8520eebe75d3ac867bdb26438d6e233914ea4b355"
                    }
                  ]
                },
                "order_reviews": {
                  "manifest_sha256": "a9726e9b86a974f26367081574f6e7a8a1f47b57ae389b760fab3580fd59313f",
                  "row_count": 12,
                  "rows": [
                    {
                      "is_deleted": false,
                      "review_id": "review_001",
                      "row_hash": "ce68d93e3f41387798241b2606709a2affcd6eca26f94778218ee71e9582ebd1"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_002",
                      "row_hash": "b583026fb692bed89bcdc5b6166498161e509aea537c9d8dac41b7bad1385be5"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_003",
                      "row_hash": "6b20f420b88ebebbb39e68b53a5c42e8ff74e9097a4390f200a04c6d90beee39"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_004",
                      "row_hash": "ae5cb8ee890d5486c20589d12099119db53fe173acbe463a805f29fd7873bf9f"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_005",
                      "row_hash": "fb0dba632f405b8e5d5d08547c4146198bacac259902f8d4cf4fb821008a116e"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_006",
                      "row_hash": "65a12285c329ef79c536f03bf90f64cce4bec177df73ed1b095bfb297b7468f7"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_007",
                      "row_hash": "e5c510c11e907b0b6a03dc98fc9cb093cd804d1961676accff9b4f2e68ed4020"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_008",
                      "row_hash": "a0bba76263d315bd8e51f80d94ee30a572f58fde30918b83d60997ec2240e084"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_009",
                      "row_hash": "39c6898d4f43e149fe05ea20b5caa480ddced312aca5f86ecfa0bde7a63029b4"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_010",
                      "row_hash": "724fd7272fec8bb2da540251686e9b779241556c1317c7d5aacf3e9045955c07"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_011",
                      "row_hash": "67799f4f0c5b59bfbd23b1a12c537e160148fc0080b6600905f1b2245fe70b7c"
                    },
                    {
                      "is_deleted": false,
                      "review_id": "review_012",
                      "row_hash": "876c3ae0d4af03706e0ac64c31353375e466c76479cd2c8714b3637b70d1bd14"
                    }
                  ]
                },
                "orders": {
                  "manifest_sha256": "820140bf9165f9c63799fda6d1989523e41b24affcbe08934e039453db99b28f",
                  "row_count": 13,
                  "rows": [
                    {
                      "is_deleted": false,
                      "order_id": "order_001",
                      "row_hash": "fada5fd81799360365f0f3f2f7e7fd2282cb79a3ca4d679d6321f6367815e329"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_002",
                      "row_hash": "8fe73ef692ce87d1e7fabfb0d3e3ae2b601945485b450dc692989e0bb8a0307c"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_003",
                      "row_hash": "e833e41529c746c4a9b71026b94582cf2c38d5c6341df83d54caf3b76ff1d193"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_004",
                      "row_hash": "2a581f705e2767771716df2e8997eda2e382c6494a873a5bb9321e068b1c8e0a"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_005",
                      "row_hash": "2b7a24beb99aca492dd114f9242c41d45ab177643560ff54e0241bdab5bf660e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_006",
                      "row_hash": "cbdb7ae5c2bb413e4f06f655b22dcae2d5db5d6ce05a029d5c12dd53bc576774"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_007",
                      "row_hash": "0352d0852e4a15d0fd3e5f13d12c653a3934204026984f6431772d97db09ed8b"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_008",
                      "row_hash": "d7df4b5849d0ff8ba4235ed9dd23eae8e5b248b4f1b757b7b14d4f282a938240"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_009",
                      "row_hash": "32be1be57cba3d2b3434d7896b6f189aebd24af63c0bf260a5a03106c165c0a9"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_010",
                      "row_hash": "e5e90df101e4a37d68ad0d370e19c1bd7c4df584213c70d544703d1f74089a67"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_011",
                      "row_hash": "adc16f849c3cdef0c960d41d63c1b16eacd16451d1fa1233afb4b2e9107cc74e"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "order_012",
                      "row_hash": "d55ce1a8050fda8baeec458d3b75a511565f13b1716de8db82711cca4f5c5685"
                    },
                    {
                      "is_deleted": false,
                      "order_id": "wave2_order_001",
                      "row_hash": "3f126287622599f71b701dcdeae241e7ef27976d9ebf477968295a8f390a3adc"
                    }
                  ]
                },
                "product_category_translation": {
                  "manifest_sha256": "fb943b0ee210613a5db749d5dde4c88b31bc2702622c245497415674766c78ae",
                  "row_count": 5,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_category_name": "beleza_saude",
                      "row_hash": "cd7108f72c72c22e5596eaa11887855bcaed985a4455252168ada7cfbae7d2ae"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "informatica_acessorios",
                      "row_hash": "f7e085e2b205fc34cf22d020d86e0401900ddd53a86ad8454dd00e3b2048569d"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "moveis_decoracao",
                      "row_hash": "a30afc8bce67a9c25fa537f02b7ac8966f7e1c1508b69f0560eec4c49872df5a"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "telefonia",
                      "row_hash": "6d2ed878891db72a489df091f6dcfba0108e79872a67f595499823a84974ba57"
                    },
                    {
                      "is_deleted": false,
                      "product_category_name": "utilidades_domesticas",
                      "row_hash": "3ca9361539f5cc8f2ae0ba8574ca45b2a72f642930b46b76626e1959aaa37972"
                    }
                  ]
                },
                "products": {
                  "manifest_sha256": "1a103d949cbcc175f44d038284930510ff41ed8271ba24d2705b1e867adc56ab",
                  "row_count": 8,
                  "rows": [
                    {
                      "is_deleted": false,
                      "product_id": "product_001",
                      "row_hash": "eb48389bc974f6e16576aba40dce122e708a92688ac3f737b374ce7d315261c1"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_002",
                      "row_hash": "e2f0e4025ea03a83d2a12c368550f99ce55764a1f074492c92d46f5a1bfa329e"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_003",
                      "row_hash": "37db3f8b4dff5a83224a72b2b1a69e8be383226bd865087c391668bcd90e71f3"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_004",
                      "row_hash": "8f9702ee001bbde6c39488863d031a77c63eac41518ad8ff980ea5ff6e757542"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_005",
                      "row_hash": "6b418454cbf219b7c0a7b62b15013a0897eb0e90fc0cdd3675acc081a1952bfe"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_006",
                      "row_hash": "4ceb44986ab7d2e165f5282350cf94af482def9cfa7acf740a32b0cd214698aa"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_007",
                      "row_hash": "4bea3afd00092cd3f27dcedf6eedf800580513a12585b57584fe207e864414d2"
                    },
                    {
                      "is_deleted": false,
                      "product_id": "product_008",
                      "row_hash": "8f5890b61905a2faec5299473b988c15b58c640c32184da6aeaad0b2e42ff66d"
                    }
                  ]
                },
                "sellers": {
                  "manifest_sha256": "57e892beb9296880003f697df09dc297229147170b5bc9ebc3bcaa6dbe70f57d",
                  "row_count": 4,
                  "rows": [
                    {
                      "is_deleted": false,
                      "row_hash": "544d88ba003be3195cbd48ec3de37509ad5562137cc62ae7a365f0e6252f4873",
                      "seller_id": "seller_001"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "2005aa0cdb07be24feb69dd6534283fbc30207290a0b62edff161e65c93e1868",
                      "seller_id": "seller_002"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "6c3fd29b27b37ba4c6a6ff3edbdecc9784bb89563f50718dd67044ec2436e661",
                      "seller_id": "seller_003"
                    },
                    {
                      "is_deleted": false,
                      "row_hash": "113871d5a6e2ef39c649ee9a78d51788343c9d2e1d912303deedb93ed473131c",
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
              "dim_product_scd2": 10,
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
              "updated_at": "2026-08-04T15:58:15.932079798Z"
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
          "duration_seconds": 2.766,
          "exit_code": 0,
          "stderr": "",
          "stdout": "37902c111c49f53\"}]}, \"order_items\": {\"manifest_sha256\": \"6f5f8124e64aec5e0a8510daa2b0866a4ab2ff02ee2e9ce6f6b9223663eaa9a2\", \"row_count\": 18, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"order_item_id\": 1, \"row_hash\": \"1977794759b3ec343596436e3934e66e8c558c8898614a082cba6471de9d039e\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"order_item_id\": 1, \"row_hash\": \"f32c450df3aa968cb753da8afc6276af2a3b9d727ef09d76497ee926ac9a0726\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"order_item_id\": 1, \"row_hash\": \"33d79dde3cd0240226c1ef559a8283e67186af636336576f523f08d5ef4806cb\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"order_item_id\": 2, \"row_hash\": \"105509c2c83d9a892268219c4a8cc5ef5d07b2e1dfdcc2c972dc2e16a651b7f2\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"order_item_id\": 1, \"row_hash\": \"35eb0ee1af3c9f296b097ee79ad2e2e14e1903c22afd8e2a4e7a3647991d9e2e\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"order_item_id\": 1, \"row_hash\": \"89ea878484dd532f38e75bf25ec4bec4313d160840154b8117581234332bc41d\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"order_item_id\": 1, \"row_hash\": \"4694609b3768ce8f16ae6a45cbc7fe9ad5eaae00411cdb2668f81079ea8b1d19\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"order_item_id\": 2, \"row_hash\": \"f8ea173a7aded2a525c61b40674f0b2e5ed23a9fe035863cf19e97ea7b3a89c3\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"order_item_id\": 1, \"row_hash\": \"851e5a3dbf8604b382de69b085273bfba69fd549ed56ba40c5bd94c55499bb7b\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"order_item_id\": 1, \"row_hash\": \"3e3991e79ec9e19f558cd88ef2f12cc5b8a46fda127c6a8248eeb949bfeb1f4d\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"order_item_id\": 1, \"row_hash\": \"57c81b3b00e28d8949d847c16b283f7712416dc442d389f623f29c1bfb06a26c\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"order_item_id\": 2, \"row_hash\": \"425bc2716b33cb2419919e3f727410465f2ad5afb55a9202bbc8f3c17ccb03f8\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"order_item_id\": 1, \"row_hash\": \"389f22d86008d40537fb1b786003b4a01e1b5ee97eaab60ef8ab0b7708c8ebe8\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"order_item_id\": 1, \"row_hash\": \"3670c8008bfae0adf652945e3e0db009f1d97aeef4bdaa6765cd31511372f744\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"order_item_id\": 1, \"row_hash\": \"2caa530c697d498bb7f2769e714524a29ea1441db42f9db0782fce6cdc4616ae\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"order_item_id\": 2, \"row_hash\": \"a8874fdce193e31aeb772a7cff9849f68a63937b4f7cfe5ea73101be332236e6\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"order_item_id\": 1, \"row_hash\": \"438349cddfc22426ffcb71243f54210010e91e377fcb7de48befba856ffa01d6\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"order_item_id\": 2, \"row_hash\": \"5c1d2e75e7939078406a8d82052cba363b10c25a18ff847f570d50688cd50295\"}]}, \"order_payments\": {\"manifest_sha256\": \"b7f20300651573509a976f9579056c462de6a2397fc7e7895437802e79d0867d\", \"row_count\": 16, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"payment_sequential\": 1, \"row_hash\": \"0d50f161adc12f443d89c3291c41198f8a042aab383efe97670fcbc5a37096da\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"payment_sequential\": 1, \"row_hash\": \"4eb5c2975c1f31cfec36c8192a8e4d4fea817058a6ccb8b4af8e693126201717\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"payment_sequential\": 1, \"row_hash\": \"0fcabf6d1133f7662ba91b3c5adf5e9ee84f75f0506c672163f35632ee311d1f\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"payment_sequential\": 1, \"row_hash\": \"57aace58c7aeecddf7c79be2b8c1fa761db82b16929b56f451c182b74fd5a1e2\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"payment_sequential\": 2, \"row_hash\": \"8a37f338d2d9b06687978117a3ed88dd6ac81d77459a9aefdd3963da63f360c9\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"payment_sequential\": 1, \"row_hash\": \"809383f342e45e18fe73122ca945cc743dcbb5745c10d1c6cb8ba33322f8caee\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"payment_sequential\": 1, \"row_hash\": \"d9bc37dc49eb9a2eb3b629adbca76a109916c17fe9c7ad7273876b9ac2097dce\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"payment_sequential\": 1, \"row_hash\": \"78543816f081471fb95712be39a71d25c9f45d19d198409e50fb07231fad2869\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"payment_sequential\": 1, \"row_hash\": \"f0f6fa77b8b70951fe7c1b7988c0ecd418cb4c0728e086afac5a9cdf77cf6148\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"payment_sequential\": 2, \"row_hash\": \"6381f5c559155fb588a2221a9b4320368410ccbf2028d3758ea8b0bd60426c40\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"payment_sequential\": 1, \"row_hash\": \"67fda8aea9b21d87c023b3f511b377cbad5fafe98841ddc9d86b05b4a393dee8\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"payment_sequential\": 1, \"row_hash\": \"643b3a6835d5abfbbec3a932e1f631dff78717d9108458d09a758892afe0659e\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"payment_sequential\": 1, \"row_hash\": \"997ef7f136abc78cc56056c1606ec8024979671e603dc4814191b4fd8fd8b6dc\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"payment_sequential\": 1, \"row_hash\": \"a4e78c01ea8a0970b92035fa280a59a9f71e6b9a366fa5789e8caad5e1137870\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"payment_sequential\": 1, \"row_hash\": \"305bf4232d86e9aa1820206099d70394f7ddd1b63c620e3c11e3d29445d275fa\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"payment_sequential\": 2, \"row_hash\": \"f4b47a2b0dde31053d3f0cd8520eebe75d3ac867bdb26438d6e233914ea4b355\"}]}, \"order_reviews\": {\"manifest_sha256\": \"a9726e9b86a974f26367081574f6e7a8a1f47b57ae389b760fab3580fd59313f\", \"row_count\": 12, \"rows\": [{\"is_deleted\": false, \"review_id\": \"review_001\", \"row_hash\": \"ce68d93e3f41387798241b2606709a2affcd6eca26f94778218ee71e9582ebd1\"}, {\"is_deleted\": false, \"review_id\": \"review_002\", \"row_hash\": \"b583026fb692bed89bcdc5b6166498161e509aea537c9d8dac41b7bad1385be5\"}, {\"is_deleted\": false, \"review_id\": \"review_003\", \"row_hash\": \"6b20f420b88ebebbb39e68b53a5c42e8ff74e9097a4390f200a04c6d90beee39\"}, {\"is_deleted\": false, \"review_id\": \"review_004\", \"row_hash\": \"ae5cb8ee890d5486c20589d12099119db53fe173acbe463a805f29fd7873bf9f\"}, {\"is_deleted\": false, \"review_id\": \"review_005\", \"row_hash\": \"fb0dba632f405b8e5d5d08547c4146198bacac259902f8d4cf4fb821008a116e\"}, {\"is_deleted\": false, \"review_id\": \"review_006\", \"row_hash\": \"65a12285c329ef79c536f03bf90f64cce4bec177df73ed1b095bfb297b7468f7\"}, {\"is_deleted\": false, \"review_id\": \"review_007\", \"row_hash\": \"e5c510c11e907b0b6a03dc98fc9cb093cd804d1961676accff9b4f2e68ed4020\"}, {\"is_deleted\": false, \"review_id\": \"review_008\", \"row_hash\": \"a0bba76263d315bd8e51f80d94ee30a572f58fde30918b83d60997ec2240e084\"}, {\"is_deleted\": false, \"review_id\": \"review_009\", \"row_hash\": \"39c6898d4f43e149fe05ea20b5caa480ddced312aca5f86ecfa0bde7a63029b4\"}, {\"is_deleted\": false, \"review_id\": \"review_010\", \"row_hash\": \"724fd7272fec8bb2da540251686e9b779241556c1317c7d5aacf3e9045955c07\"}, {\"is_deleted\": false, \"review_id\": \"review_011\", \"row_hash\": \"67799f4f0c5b59bfbd23b1a12c537e160148fc0080b6600905f1b2245fe70b7c\"}, {\"is_deleted\": false, \"review_id\": \"review_012\", \"row_hash\": \"876c3ae0d4af03706e0ac64c31353375e466c76479cd2c8714b3637b70d1bd14\"}]}, \"orders\": {\"manifest_sha256\": \"820140bf9165f9c63799fda6d1989523e41b24affcbe08934e039453db99b28f\", \"row_count\": 13, \"rows\": [{\"is_deleted\": false, \"order_id\": \"order_001\", \"row_hash\": \"fada5fd81799360365f0f3f2f7e7fd2282cb79a3ca4d679d6321f6367815e329\"}, {\"is_deleted\": false, \"order_id\": \"order_002\", \"row_hash\": \"8fe73ef692ce87d1e7fabfb0d3e3ae2b601945485b450dc692989e0bb8a0307c\"}, {\"is_deleted\": false, \"order_id\": \"order_003\", \"row_hash\": \"e833e41529c746c4a9b71026b94582cf2c38d5c6341df83d54caf3b76ff1d193\"}, {\"is_deleted\": false, \"order_id\": \"order_004\", \"row_hash\": \"2a581f705e2767771716df2e8997eda2e382c6494a873a5bb9321e068b1c8e0a\"}, {\"is_deleted\": false, \"order_id\": \"order_005\", \"row_hash\": \"2b7a24beb99aca492dd114f9242c41d45ab177643560ff54e0241bdab5bf660e\"}, {\"is_deleted\": false, \"order_id\": \"order_006\", \"row_hash\": \"cbdb7ae5c2bb413e4f06f655b22dcae2d5db5d6ce05a029d5c12dd53bc576774\"}, {\"is_deleted\": false, \"order_id\": \"order_007\", \"row_hash\": \"0352d0852e4a15d0fd3e5f13d12c653a3934204026984f6431772d97db09ed8b\"}, {\"is_deleted\": false, \"order_id\": \"order_008\", \"row_hash\": \"d7df4b5849d0ff8ba4235ed9dd23eae8e5b248b4f1b757b7b14d4f282a938240\"}, {\"is_deleted\": false, \"order_id\": \"order_009\", \"row_hash\": \"32be1be57cba3d2b3434d7896b6f189aebd24af63c0bf260a5a03106c165c0a9\"}, {\"is_deleted\": false, \"order_id\": \"order_010\", \"row_hash\": \"e5e90df101e4a37d68ad0d370e19c1bd7c4df584213c70d544703d1f74089a67\"}, {\"is_deleted\": false, \"order_id\": \"order_011\", \"row_hash\": \"adc16f849c3cdef0c960d41d63c1b16eacd16451d1fa1233afb4b2e9107cc74e\"}, {\"is_deleted\": false, \"order_id\": \"order_012\", \"row_hash\": \"d55ce1a8050fda8baeec458d3b75a511565f13b1716de8db82711cca4f5c5685\"}, {\"is_deleted\": false, \"order_id\": \"wave2_order_001\", \"row_hash\": \"3f126287622599f71b701dcdeae241e7ef27976d9ebf477968295a8f390a3adc\"}]}, \"product_category_translation\": {\"manifest_sha256\": \"fb943b0ee210613a5db749d5dde4c88b31bc2702622c245497415674766c78ae\", \"row_count\": 5, \"rows\": [{\"is_deleted\": false, \"product_category_name\": \"beleza_saude\", \"row_hash\": \"cd7108f72c72c22e5596eaa11887855bcaed985a4455252168ada7cfbae7d2ae\"}, {\"is_deleted\": false, \"product_category_name\": \"informatica_acessorios\", \"row_hash\": \"f7e085e2b205fc34cf22d020d86e0401900ddd53a86ad8454dd00e3b2048569d\"}, {\"is_deleted\": false, \"product_category_name\": \"moveis_decoracao\", \"row_hash\": \"a30afc8bce67a9c25fa537f02b7ac8966f7e1c1508b69f0560eec4c49872df5a\"}, {\"is_deleted\": false, \"product_category_name\": \"telefonia\", \"row_hash\": \"6d2ed878891db72a489df091f6dcfba0108e79872a67f595499823a84974ba57\"}, {\"is_deleted\": false, \"product_category_name\": \"utilidades_domesticas\", \"row_hash\": \"3ca9361539f5cc8f2ae0ba8574ca45b2a72f642930b46b76626e1959aaa37972\"}]}, \"products\": {\"manifest_sha256\": \"1a103d949cbcc175f44d038284930510ff41ed8271ba24d2705b1e867adc56ab\", \"row_count\": 8, \"rows\": [{\"is_deleted\": false, \"product_id\": \"product_001\", \"row_hash\": \"eb48389bc974f6e16576aba40dce122e708a92688ac3f737b374ce7d315261c1\"}, {\"is_deleted\": false, \"product_id\": \"product_002\", \"row_hash\": \"e2f0e4025ea03a83d2a12c368550f99ce55764a1f074492c92d46f5a1bfa329e\"}, {\"is_deleted\": false, \"product_id\": \"product_003\", \"row_hash\": \"37db3f8b4dff5a83224a72b2b1a69e8be383226bd865087c391668bcd90e71f3\"}, {\"is_deleted\": false, \"product_id\": \"product_004\", \"row_hash\": \"8f9702ee001bbde6c39488863d031a77c63eac41518ad8ff980ea5ff6e757542\"}, {\"is_deleted\": false, \"product_id\": \"product_005\", \"row_hash\": \"6b418454cbf219b7c0a7b62b15013a0897eb0e90fc0cdd3675acc081a1952bfe\"}, {\"is_deleted\": false, \"product_id\": \"product_006\", \"row_hash\": \"4ceb44986ab7d2e165f5282350cf94af482def9cfa7acf740a32b0cd214698aa\"}, {\"is_deleted\": false, \"product_id\": \"product_007\", \"row_hash\": \"4bea3afd00092cd3f27dcedf6eedf800580513a12585b57584fe207e864414d2\"}, {\"is_deleted\": false, \"product_id\": \"product_008\", \"row_hash\": \"8f5890b61905a2faec5299473b988c15b58c640c32184da6aeaad0b2e42ff66d\"}]}, \"sellers\": {\"manifest_sha256\": \"57e892beb9296880003f697df09dc297229147170b5bc9ebc3bcaa6dbe70f57d\", \"row_count\": 4, \"rows\": [{\"is_deleted\": false, \"row_hash\": \"544d88ba003be3195cbd48ec3de37509ad5562137cc62ae7a365f0e6252f4873\", \"seller_id\": \"seller_001\"}, {\"is_deleted\": false, \"row_hash\": \"2005aa0cdb07be24feb69dd6534283fbc30207290a0b62edff161e65c93e1868\", \"seller_id\": \"seller_002\"}, {\"is_deleted\": false, \"row_hash\": \"6c3fd29b27b37ba4c6a6ff3edbdecc9784bb89563f50718dd67044ec2436e661\", \"seller_id\": \"seller_003\"}, {\"is_deleted\": false, \"row_hash\": \"113871d5a6e2ef39c649ee9a78d51788343c9d2e1d912303deedb93ed473131c\", \"seller_id\": \"seller_004\"}]}}}, \"runtime\": {\"last_published_sync_run_seq\": 4, \"lease_owner_id\": null, \"source_snapshot_completed\": true}, \"stable_current_counts\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"status\": \"ready\", \"sync_run_id\": \"sync-00000000000000000004\", \"sync_run_seq\": 4}\n",
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
          "duration_seconds": 1.64,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"active_runs\": [], \"command\": \"validate-final\", \"gold_views\": {\"dim_customer_scd2\": 8, \"dim_date\": 46, \"dim_order_status\": 2, \"dim_product_scd2\": 10, \"dim_seller\": 4, \"fact_order_items\": 18, \"mart_daily_revenue\": 13, \"mart_monthly_arpu\": 7}, \"iceberg_current_counts\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"open_or_rejected_transactions\": [], \"publication_marker\": {\"publication_status\": \"PUBLISHED\", \"sync_run_id\": \"sync-00000000000000000004\", \"sync_run_seq\": 4}, \"runtime\": {\"last_published_sync_run_seq\": 4, \"lease_operation\": null, \"lease_owner_id\": null}, \"stable_current_counts\": {\"customers\": 9, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"status\": \"ready\", \"sync_run_id\": \"sync-00000000000000000004\", \"sync_run_seq\": 4}\n",
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
          "duration_seconds": 1.688,
          "exit_code": 0,
          "stderr": "",
          "stdout": "{\"clickhouse\": 200, \"command\": \"status\", \"compose\": [{\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"airflow\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"airflow-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"apicurio-registry\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"clickhouse\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"clickhouse-init\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"clickhouse-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"iceberg-migration\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"kafka\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"kafka-connect\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"kafka-topics\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"minio\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"minio-init\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"mysql\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"platform-postgres\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"platform-postgres-bootstrap\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"polaris\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-admin\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-admin-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-bootstrap\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-credentials-prepare\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"polaris-server-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-bronze\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-geolocation\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"healthy\", \"service\": \"spark-master\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-ops\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-projector\", \"state\": \"exited\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-silver\", \"state\": \"running\"}, {\"exit_code\": 0, \"health\": \"\", \"service\": \"spark-worker\", \"state\": \"running\"}], \"connector\": {\"connector_state\": \"RUNNING\", \"registered\": true, \"task_0_state\": \"RUNNING\"}, \"iceberg\": {\"contract_version\": 2, \"queries_count\": 10, \"status\": \"READY\", \"updated_at\": \"2026-08-04T15:58:15.932079798Z\"}, \"mysql\": {\"customers\": 9, \"geolocation\": 6, \"order_items\": 18, \"order_payments\": 16, \"order_reviews\": 12, \"orders\": 13, \"product_category_translation\": 5, \"products\": 8, \"sellers\": 4}, \"polaris\": 200, \"project\": \"olist_stage_v\", \"registry\": {\"compatibility\": \"BACKWARD_TRANSITIVE\", \"status_code\": 200}, \"status\": \"ready\", \"writer_schema_capture\": \"captured\"}\n",
          "timed_out": false
        }
      ],
      "details": {},
      "duration_seconds": 6.083,
      "gate": "10-final",
      "status": "PASS",
      "timestamp": "2026-08-04T15:59:01.390687+00:00"
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

Raw evidence persisted in `data/stage-v-evidence/stage_l1_20260804_v6/`.
