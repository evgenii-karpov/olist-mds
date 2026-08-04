# CI Quality Gates

CI is split into focused jobs so a failure identifies the affected target
boundary instead of hiding behind one monolithic pipeline. Pull-request CI
uses local, reproducible services and does not require cloud credentials.

## Automatic checks

- `docs-and-repository-contracts` validates Markdown/YAML/TOML contracts,
  Python compilation, the target DAG inventory, the frozen F0 oracle, the
  bounded source fixture and the L4 legacy-orphan guard.
- `python-quality` runs Ruff and Pyright.
- `python-contract-tests` collects the explicit MySQL, CDC, platform, dbt,
  serving and Stage V suites. Observability has its own component job.
- `scala-fast` builds the Spark job image and checks the dependency boundary
  and required application classes.
- `compose-contract` renders every supported target profile combination and
  validates the observability inventory.
- `airflow-dag-imports` builds the target Airflow image and checks the exact
  target DAG inventory.
- `dbt-clickhouse-static` starts an isolated ClickHouse container with
  `docker run`, then parses and compiles `dbt/olist_clickhouse` and validates
  its model/source/selector contract.

The required `ci-success` job aggregates these checks. A missing or skipped
required job is a failure of the workflow contract.

## Bounded and manual checks

`lakehouse-components.yml` owns fast Spark, Airflow and observability checks.
The observability job validates the actual producer → scrape → rule →
dashboard mapping and runs `tests/observability`; it is intentionally
independent of the Stage V runner.

`lakehouse-cdc.yml` and `lakehouse-serving.yml` are dispatch-only bounded
component workflows. `lakehouse-acceptance.yml` is the dispatch-only full
acceptance workflow: it publishes diagnostics even when a gate fails and runs
the complete Stage V V0–V10 candidate script plus the separate F1 parity gate.

## Fixture and evidence policy

The committed bounded fixture is `tests/fixtures/olist_small`. Source-contract
validation checks its archive and profile without mutating either. Stage V
evidence belongs under `data/stage-l-evidence/<stage>/<run-id>/`; reports must
include the candidate SHA, fixture checksum, command, Compose project, gate
statuses and raw failure output with secrets redacted.

The Stage V runner does not start or validate observability services. Those
services are covered by the dedicated observability component contract.
