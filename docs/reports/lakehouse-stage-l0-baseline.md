# Stage L0: baseline reset и inventory review

- **Статус**: `COMPLETE` как L0 baseline diagnostic; baseline E2E не является acceptance PASS и Stage L остаётся `ACTIVE`.
- **Дата запуска**: 2026-08-04.
- **Назначение**: зафиксировать фактический baseline после rollback и отделить L0 diagnostics от будущего acceptance evidence.

## 1. Baseline identity

| Поле | Значение |
| --- | --- |
| Candidate commit | `9214cd1de05ab37cdeae27a1a0b633963e8ae8d6` |
| Working tree after rollback | Clean; only committed Stage L plan was retained before L0 documents were added. |
| F0 source | `1400d08345ad81a0121f0ee85ee9ae81cd575a73` |
| Fixture | `tests/fixtures/olist_small/olist_small.zip` |
| Fixture SHA-256 | `5cf2ff7a104cae75d8a56cf8c6e00959894154a8d55aed2ddf0e3fa133a13976` |
| Target test collection | 188 tests collected from `tests/mysql`, `tests/cdc_contracts`, `tests/lakehouse_platform`, `tests/dbt_clickhouse`, `tests/serving` and `tests/stage_v`. |
| Target suite baseline | `186 passed, 2 skipped, 86 subtests passed`; collection and execution were explicit. |

## 2. E2E baseline run

The full runner was started immediately after the rollback, before the repository inventory work:

```powershell
uv run python scripts/validation/stage_v_candidate_e2e.py run `
  --run-id stage_l0_baseline_20260804 `
  --evidence-dir data/stage-l0-baseline-e2e `
  --confirm-reset
```

- Evidence root: `data/stage-l0-baseline-e2e/`.
- Run completed with `overall_status=FAIL`.
- `00-preflight` through `09-rebuild` passed; the first and only failed gate was `10-final`.
- The independent final control-plane check failed because its raw audit-inventory query found one `OPEN` observation: `Final audit transaction inventory contains OPEN/REJECTED rows: [{"row_count": 1, "status": "OPEN"}]`. The baseline output did not include the transaction ID, so this run alone cannot distinguish an unresolved transaction from a historical BEGIN row later completed by a separate immutable record.
- `runtime_cleanup` is `SKIPPED` by design after a failed gate, so the `olist_stage_v` runtime was preserved for diagnostics; the evidence root contains the cleanup record and all gate summaries.
- After diagnostics were captured, the exact failed-run project `olist_stage_v` was manually removed with `docker compose --project-name olist_stage_v down --volumes --remove-orphans`; no unrelated Compose project was touched.
- Evidence root: `data/stage-l0-baseline-e2e/`.
- A failure here is a baseline diagnostic. It does not satisfy any L1–L4 or L5 acceptance gate.

## 3. L0 outputs

- [Legacy disposition register](../plans/lakehouse/contracts/legacy-disposition-register.md) — individual KEEP/REWRITE/REPLACE/DELETE decisions and removal conditions.
- [Target observability contract](../plans/lakehouse/contracts/observability.md) — current phantom-target audit and required target metric chain.
- [Target tests and evidence contract](../plans/lakehouse/contracts/testing-and-evidence.md) — protected suites, transfer rules and evidence boundaries.
- [Stage L detailed plan](../plans/lakehouse/completed/stage-l-legacy-removal-ci-cutover.md) — stage ordering and exit criteria.

## 4. Static findings recorded before runtime implementation

1. The clean baseline retains the target test collection; the deleted-test concern is not solved by hiding root tests in CI.
2. `streaming/connect/**` is a target dependency and is explicitly protected. `local_lab.py` and target CDC contract tests consume it.
3. The baseline Prometheus config contains targets not defined by the baseline Compose service inventory and rules/dashboards for PostgreSQL WAL, NiFi queues and the old `olist-nifi-cdc-v1` group.
4. `postgres_password.txt` is still used as an implicit default for multiple target MySQL role secrets, and `airflow_api_secret_key.txt` is used as an implicit MinIO password default. These are L1 secret wiring defects, not deletion reasons for target tests.
5. `streaming/runtime-versions.json` records Debezium `3.6.0.Final`; any Compose/image change must preserve that contract or update all version evidence together.
6. The observability runtime manifest and baseline Compose also disagree on Prometheus/Grafana/Loki versions; this is an explicit L2/L3 alignment item, not a reason to keep phantom exporters.
7. `scripts/cdc/stage2_admin.py` still points to the missing `streaming/connect/olist-postgres-cdc.json` and old PostgreSQL connector identity; this is an L1 rewrite, while `streaming/connect/olist-mysql-cdc.json` remains protected.
8. Compose also uses the control-PostgreSQL password as the default for the Polaris and Apicurio database roles, while the active observability README claims Alertmanager, Alloy, StatsD and exporters that are absent from the baseline service inventory. These are explicit L1/L2 contract gaps, not reasons to remove target tests or target runtime directories.
9. The CI contract names target `.github/workflows/lakehouse-components.yml` and `.github/workflows/lakehouse-acceptance.yml`, but neither file exists at baseline. They are recorded as L3 replacements and must be added before legacy workflow deletion.
10. The baseline E2E's runtime writer-schema capture rewrites timestamps in tracked `streaming/schemas/captured-writer-schemas/manifest.json`. L1 must redirect that capture to temporary/evidence storage; the frozen writer bundle must remain unchanged by test execution.
11. The register covers all four baseline workflows, all 80 tracked scripts, all 78 tracked test files (including all 22 root `tests/test_*.py` files), all 17 files under `tests/fixtures`, and all 10 existing development secret templates; no test was deleted or hidden during L0. Target suites remain explicit and passed independently.
12. AWS/Redshift is not a deferred compatibility target: its DAGs, infra, utilities, dependencies, secrets and active references are marked `DELETE` for L4. A future GCP stack is explicitly out of the local Stage L implementation scope.
13. A consumer audit showed that `streaming/minio/init.sh` and its `nifi`/`cdc-loader` policies are legacy and unused by the current Compose service; target bucket initialization is `infra/polaris/minio/init.sh`. The register now deletes the old init/policies while retaining the target MinIO image `Dockerfile`/`start.sh`.
14. The current Compose mounts `infra/clickhouse/lakehouse` and does not consume `infra/clickhouse/initdb/**`; all four legacy initdb files are therefore `DELETE`, not partial target replacements.
15. The authoritative baseline E2E reached V0–V9, then failed at V10 because the final check counted one raw `OPEN` audit observation. The baseline validator did not expose the transaction ID or collapse immutable BEGIN/END observations into effective state. L1 must determine whether the observation has a later `COMPLETE`, fix the lifecycle/validator contract accordingly, and produce a new clean PASS; manual SQL cleanup or weakening the final assertion is not acceptable.
16. The active source-profile path still emits/consumes `redshift_raw_type` in `scripts/utilities/profile_olist_zip.py`, `scripts/testing/create_small_fixture_dataset.py` and `tests/fixtures/olist_small/source_profile_small.json`. The register now marks these paths `REWRITE`, while the frozen CSV archive remains `KEEP`.
17. `infra/control-postgres/**` is not homogeneous: target `serving.*` ledger DDL is `KEEP`, but `audit`/`cdc_audit` batch/CDC-transform migrations are legacy and are now explicitly `DELETE` after replacement evidence. `scripts/serving/control.py` must be rewritten because its schema verifier still lists those legacy tables and an absent `audit.pipeline_events` table.
18. The AWS/Redshift removal boundary is now explicit: AWS cloud/Redshift DAGs, infra, secrets, utilities and dependencies are `DELETE`; local MinIO S3-compatible APIs and the Iceberg S3 adapter are retained because they are target object-store mechanics, not an AWS cloud deployment.

The baseline run itself was executed before the corrective runtime change. The
targeted, uncommitted `validate-final` effective-state change is validated by
the separate corrective run below; it does not retroactively turn the baseline
failure into acceptance or close the broader L1 lifecycle work. No workflow or
test was deleted or hidden.

## 5. Corrective V10 diagnostic run

After the baseline failure, `scripts/cdc/local_lab.py` was changed only in the
`validate-final` audit query. The query now collapses append-only transaction
observations by `transaction_id`, ordering a completed observation by its end
offset and an open observation by its begin offset, with `recorded_at` as the
tie-breaker. It reports the effective transaction ID and offsets on failure.
No Iceberg/ClickHouse data was updated manually.

The corrective run was executed from the same clean runtime reset:

```powershell
uv run python scripts/validation/stage_v_candidate_e2e.py run `
  --run-id stage_l0_v10fix_20260804 `
  --evidence-dir data/stage-l0-v10fix-e2e `
  --confirm-reset
```

- Evidence root: `data/stage-l0-v10fix-e2e/`.
- `00-preflight` through `10-final` passed; `10-final` had all three assertions
  `PASS`.
- `validate-final` returned `open_or_rejected_transactions: []`, a `PUBLISHED`
  marker for `sync_run_seq=4`, stable/current parity, and valid Gold views. The
  raw command output is recorded in
  `data/stage-l0-v10fix-e2e/10-final/summary.json`.
- The runner completed its normal cleanup; `olist_stage_v` is not left running.

This proves that V10 can be made green without deleting or mutating the
historical `OPEN` observation: the baseline query had checked raw history as if
it were effective state. It does not close the broader L1 transaction-lifecycle
work. In particular, `TransactionBatchWriter.scala` still needs split-batch,
duplicate/order and rejected-state regression coverage, and
`scripts/serving/clickhouse.py` still drops physical rows with a null end offset
before the boundary planner sees them. The corrective validator is therefore a
targeted L0 diagnosis, not an assertion that L1 is complete.

The E2E writer-schema capture also rewrote tracked generated artifacts during
the run; the manifest and pre-existing Stage V validation report were restored
to the candidate baseline. Their unchanged state is part of the L0 cleanup
check.
