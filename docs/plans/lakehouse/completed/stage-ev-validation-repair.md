# Detailed plan: Stage E and Stage V re-acceptance

- **Status**: `COMPLETE — CLEAN V0–V10 ACCEPTED`
- **Purpose**: close implementation and evidence gaps in Stage E/V and obtain a reproducible full V0–V10 run before freezing the baseline and removing legacy.
- **Stage boundary**: this document is preserved as a frozen plan and contains the actual clean acceptance evidence below.

---

## 1. Why the stage was reopened

Existing Stage E and Stage V reports are retained as historical evidence, but cannot yet be the sole basis for destructive cleanup:

- the Stage V report contains evidence only for the preparatory V0/V1 gates but declares V0–V10 success;
- the report generator permits missing gates and produces `PASS` without evidence for every required step;
- after early gates, the scenario does not stop immediately on failure;
- the control-plane bootstrap does not prove that `005_create_serving_control_tables.sql` was applied;
- the serving publication boundary is built without proven Kafka offsets and Iceberg snapshot IDs;
- the Airflow/dbt runtime still needs to be switched completely from `dbt/olist_analytics` to `dbt/olist_clickhouse`.

Therefore, the E/V statuses are changed to `REVALIDATION REQUIRED`. This does not undo completed development; it adds the missing barrier before F0 and L.

---

## 2. Work packages

### EV1 — make the control plane executable

1. Include `infra/control-postgres/initdb/005_create_serving_control_tables.sql` in the real bootstrap order.
2. Limit grants to the target Airflow, Polaris, Apicurio, and `olist_control.serving` schemas.
3. Add an automated check for the schema version and required tables/constraints.
4. Verify that rerunning bootstrap does not change the already-applied schema.

**Output**: machine-readable evidence listing applied migrations and schema assertion results.

### EV2 — prove the final serving transaction boundary

1. DAG `olist_lakehouse_serving_sync` obtains real committed Kafka offsets and Iceberg snapshot IDs.
2. Empty offsets/snapshots are allowed only for a proven no-op, not as the normal publication path.
3. `sync-serving` compares the final authoritative serving report, not only the Airflow run status.
4. `is_noop` is computed from the actual boundary and published version.
5. Repeating the same boundary returns the same result without duplicating events or the Gold version.

**Output**: accepted boundary, transaction ID, source offsets, snapshot IDs, candidate version, and stable published version in one JSON evidence record.

### EV3 — complete the Airflow/dbt switch

1. The Airflow image and volumes contain `dbt/olist_clickhouse`, and `DBT_PROFILES_DIR` points only to it.
2. The runtime has no required dependencies on `dbt/olist_analytics`, Redshift, or Elementary Redshift.
3. Exactly the target DAGs are imported:
   - `olist_lakehouse_serving_sync`;
   - `olist_lakehouse_quality`;
   - `olist_lakehouse_maintenance`;
   - `olist_lakehouse_serving_rebuild`.
4. DAG names match across code, documentation, and CI.
5. `dbt deps`, `dbt parse`, and candidate `dbt build` run inside the same image used by the DAG.

### EV4 — repair the Stage V harness

The harness must:

- maintain an explicit registry of required V0–V10 gates;
- treat a missing, skipped, or duplicated gate as an error;
- exit non-zero after the first required `FAIL`;
- compute final status only from actual results;
- never write hard-coded counts, IDs, or success claims;
- preserve the command, timestamps, duration, commit SHA, fixture SHA-256, and artifact links;
- clean only its own Compose project in `finally`/`always()`;
- distinguish `PASS`, `FAIL`, `ERROR`, and `SKIPPED`; a skipped required gate does not permit acceptance.

### EV5 — run a full clean V0–V10 run

| Gate | Required evidence |
| --- | --- |
| V0 — preflight | clean/explicitly recorded commit, fixture SHA, Docker resources, free project names |
| V1 — harness | complete gate registry, artifact directories, timeouts, and destructive confirmation |
| V2 — clean bootstrap | new Compose domain and volumes, readiness of all platform components |
| V3 — initial load | seed, Debezium snapshot, 79 active entity rows, 6 reference rows, no rejects |
| V4 — CDC mutations | insert/update/delete/tombstone and exact expected current/events changes |
| V5 — restart/catch-up | Bronze/Silver restart, no duplicate `event_id`, committed progress |
| V6 — serving sync | real frozen boundary, candidate publish, stable switch, correct no-op repeat |
| V7 — dbt/quality | `dbt build`, schema/data tests, and queries against stable `gold`/`FINAL` |
| V8 — schema evolution | nullable additive column passes Avro → Bronze → Silver → serving with `null` |
| V9 — rebuild | ClickHouse is fully cleared and restored only from Iceberg |
| V10 — final assertions | all required gates are present and `PASS`, and the report matches raw evidence |

### EV6 — update evidence

1. Generate a new Stage E report with actual commands and artifacts.
2. Regenerate the Stage V report only after V10 completes.
3. Do not overwrite raw evidence with success declarations after a failure.
4. Record the commit SHA on which the result was obtained.

---

## 3. Checks required in automated CI

Common CI includes unit/contract checks for the gate registry, fail-fast behavior, application of migration 005, DAG inventory, and the prohibition of placeholder boundaries. Full V0–V10 remains manual because of its duration and destructive reset; its exact workflow is described in the [Stage L / CI cutover plan](../completed/stage-l-legacy-removal-ci-cutover.md).

---

## 4. Completion criteria

Stage E/V is re-accepted only if:

1. EV1–EV4 are implemented and covered by automated tests;
2. one clean run contains exactly V0–V10 and all have `PASS`;
3. Stage E/V reports are built from and match raw evidence;
4. rechecking the report with a separate command returns `PASS`;
5. the environment is cleaned after completion and evidence is preserved;
6. only then is the transition to F0 permitted.

---

## 5. Related documents

- [Final-stage coordination plan](../completed/serving-cutover.md)
- [F0 baseline freeze plan](stage-f0-baseline-freeze.md)
- [Validation & CI contract](../contracts/validation-and-ci.md)

## 6. Actual confirmation

- **Result**: clean `PASS` for all 11 required V0–V10 gates; all 42 machine-readable assertions passed.
- **Run ID**: `stage_v_clean_e113c55`.
- **Compose project**: `olist_stage_v`.
- **Commit SHA from V0**: `e113c552cca990636f426b827456a77ddc9d594b`.
- **V0 source tree**: `dirty=false`.
- **Evidence**: `data/stage-v-evidence/stage_v_clean_e113c55/`.
- **Report**: `docs/reports/mysql-spark-iceberg-stage-v-validation.md`.
- **Independent report check**: the report was generated from clean-run raw evidence and contains `PASS` for every required gate.
- **Evidence checksums**: SHA-256 values were created for all 11 nested gate summaries.
- **Next stage**: F0 — freeze the baseline from `main`; Stage L and F1 remain blocked until F0.

### 6.1 Historical manual post-fix check V06–V10

On 3 August 2026, V06–V10 were checked separately in the existing Compose project `olist_stage_v`. This run is not clean-domain V0–V10 acceptance: V06 used one controlled source UPDATE because the original CRUD fixtures had already been consumed by previous attempts.

- **V06**: publish `sync_run_seq=6` (`is_noop=false`, boundary `file=binlog.000002,pos=38910`, `expected=materialized=90`) and repeat `sync_run_seq=7` (`NOOP`, same boundary).
- **V07**: `validate-serving` for seq 6 confirmed the actual `dbt build --selector serving_candidate`: 75 results (`16 success`, `59 pass`), stable current parity, and all eight Gold interfaces.
- **V08**: allowlisted nullable-column fixtures produced customer event offset 10, schema ID 37, `NULL` in the new source column, `schema_violations=0`, and `normalization_errors=0`; publish `sync_run_seq=9` produced `expected=materialized=91`, and repeated serving validation passed.
- **V09**: rebuild `sync_run_seq=10` completed `SUCCEEDED`, with `expected=materialized=91` and eight Iceberg snapshots.
- **V10**: `local_lab.py status --require serving` and post-rebuild current/Gold parity completed `PASS`.
- All four serving DAGs have `schedule=None`, `is_paused=false`; containers were not stopped.

This manual check was interim confirmation and did not remove the EV5 requirement at the time; the subsequent clean run in section 6.2 removed that barrier.

### 6.2 Clean V0–V10 acceptance

On 3 August 2026, a clean-domain run was completed at commit `e113c552cca990636f426b827456a77ddc9d594b`.

- `00-preflight` recorded `dirty=false` and the exact execution commit.
- All required gates `00-preflight`–`10-final` completed `PASS`; `42/42` assertions passed.
- V06 performed a real non-NOOP sync (`seq=1`, `SUCCEEDED`, dbt: `16 success + 59 pass`), then the repeated boundary returned `seq=2`, `NOOP`.
- V08 confirmed nullable Avro propagation (`schema_id=37`, `optional_value=null`, `schema_violations=0`, `normalization_errors=0`).
- V09 restored serving from Iceberg (`seq=4`, `expected_event_count=90`, `materialized_event_count=90`).
- V10 confirmed `PUBLISHED`, empty active/open/rejected control-plane sets, and Iceberg/Stable/Gold parity.
- After completion, runtime cleanup was performed only for Compose project `olist_stage_v`; volumes were retained for diagnostics/reuse.
