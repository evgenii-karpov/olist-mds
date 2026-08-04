# Stage L3 implementation report

Status: **CI/workflow cutover implemented; Stage L remains ACTIVE**.

This report records the CI-only L3 implementation. It does not claim that the
manual candidate acceptance, full Stage V E2E, or F1 parity gate has passed.

## Scope and decision boundary

The L3 worktree changes are limited to GitHub workflows, CI-owned validators
and CI/observability contract tests. No Compose file, Docker runtime image,
Spark/Scala runtime, Airflow DAG implementation, dbt model, fixture, serving
runtime or `scripts/validation/stage_v_candidate_e2e.py` was changed.

Therefore the full Stage V E2E was intentionally not run. A CI-only L3 gate is
closed by workflow/static checks; manual acceptance remains a separate
dispatch-only workflow. Any later L3 change to an executable runtime path must
stop at that boundary and receive a separate decision about a full E2E run.

## Implemented workflow cutover

### Common CI

`.github/workflows/ci.yml` now defines the required target jobs:

- repository/docs contracts, F0 validation and active-legacy guard;
- Ruff, Ruff format and Pyright;
- explicit target Python contract suites with JUnit evidence;
- Scala image build, tests/package and JAR dependency boundary;
- Compose profile contracts;
- exact target Airflow DAG inventory/imports;
- dbt-clickhouse deps/parse/compile/model/source/selector contract;
- `ci-success`, which fails on failed or skipped required jobs.

### Bounded components

`.github/workflows/lakehouse-components.yml` contains real bounded jobs for
Spark image, CDC, serving, Airflow and observability. It uses unique Compose
projects and cleanup in `always()` blocks. The CDC path covers bounded
restart/catch-up; serving covers finite sync, authoritative NOOP retry,
rebuild and maintenance; observability is tested independently of Stage V.

### Manual acceptance

`.github/workflows/lakehouse-acceptance.yml` is `workflow_dispatch` only. It
requires a full candidate SHA and explicit destructive confirmation, performs
preflight validation, defines candidate Stage V/F1 jobs and always publishes
available evidence. It is not run by ordinary PR CI.

The three superseded PostgreSQL/NiFi-era workflows were removed as required by
the validation contract:

- `.github/workflows/batch-cdc-parity.yml`;
- `.github/workflows/cdc-stage2-kafka-debezium.yml`;
- `.github/workflows/cdc-stage6-operations.yml`.

No test files were deleted.

## CI-owned checks added or strengthened

- `scripts/ci/check_repository_contracts.py` validates required/removed
  workflows, workflow permissions/timeouts, YAML/JSON/TOML syntax, controlled
  Markdown links, active legacy references and frozen F0 tracking.
- `scripts/ci/check_dbt_clickhouse_contract.py` validates the compiled target
  dbt project, 20 models, target sources and `serving_candidate` selector.
- `scripts/ci/check_airflow_dag_imports.py` now enforces the two target DAG
  files, exactly four target DAG IDs and absence of the old dbt path.
- `tests/test_clickhouse_phase7_ci_observability.py` asserts the workflow/job
  inventory, observability job, dispatch-only acceptance and legacy workflow
  removal.

## Validation performed

All checks below passed locally without starting the full Stage V stack:

| Check | Result |
| --- | --- |
| Repository/workflow contract checker | `PASS` |
| dbt-clickhouse contract checker | `PASS`; 20 models; `serving_cdc`, `serving_control`; `serving_candidate` |
| Explicit target Python contract suites | `200 passed, 2 skipped`; 86 subtests passed |
| Observability/CI tests | `19 passed` |
| Ruff check | `PASS` |
| Ruff format check | `PASS` |
| Pyright | `0 errors` |

Machine-readable outputs are under
`data/stage-l-evidence/L3/`:

- `l3-static-repository-contracts.json`;
- `l3-static-dbt-contract.json`;
- `l3-python-contract-tests.xml`;
- `l3-observability-contract-tests.xml`.

## Known blocker outside L3

The pre-existing `scripts/cdc/local_lab.py final-parity` command is still a
`not_available` stub and does not accept the normative F1 arguments
`--run-id`, `--oracle` and `--timeout`. The manual workflow is wired to the
contractual F1 interface, but no F1 PASS is claimed. Implementing that CLI and
candidate-only parity execution belongs to Stage F1 and would be a separate
runtime/e2e-affecting change.
