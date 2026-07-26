# Phase 2: Separate control PostgreSQL

Status: completed on 2026-07-23.

## Delivered contract

- Added a dedicated `olist_control` database and `olist_control` role on the
  existing `airflow-postgres` server.
- Added the `control-db-init` one-shot Compose service. It waits for
  `airflow-postgres`, creates or updates the control role, creates the control
  database idempotently, and applies control DDL on new and existing volumes.
- Added `CONTROL_POSTGRES_HOST`, `CONTROL_POSTGRES_PORT`,
  `CONTROL_POSTGRES_DB`, `CONTROL_POSTGRES_USER`,
  `CONTROL_POSTGRES_PASSWORD_FILE`, and
  `CONTROL_POSTGRES_PASSWORD_SOURCE_FILE` configuration surfaces.
- Added a `control_postgres_password` Docker secret and committed local
  development secret file.
- Split mutable batch and CDC control DDL into
  `infra/control-postgres/initdb` while preserving the analytical
  `infra/postgres` DDL for the temporary PostgreSQL oracle.
- Moved local batch control state to explicit control PostgreSQL defaults.
  `WAREHOUSE_*` remains an intentional override for the AWS/Redshift batch
  control path.
- Split local PostgreSQL raw batch loading and reconciliation so warehouse row
  operations still use analytical `POSTGRES_*`, while audit, dead-letter,
  reconciliation, and batch status writes use `CONTROL_POSTGRES_*`.
- Split CDC ingest orchestration so claims, attempts, watermarks,
  reconciliation, replay requests, and failure callbacks use
  `CONTROL_POSTGRES_*`; raw CDC inserts still use analytical `POSTGRES_*`.
- Split realtime transform orchestration so transform runs, transform file
  selection, publication state, mart freshness, and parity status use
  `CONTROL_POSTGRES_*`; dbt model execution and publication views still use the
  analytical warehouse target.
- Added focused Phase 2 tests proving control defaults do not fall back to
  warehouse `POSTGRES_*`, Compose exposes the control init contract, and
  control DDL excludes warehouse raw tables.

## Verification evidence

Passed:

- `docker compose config --quiet`;
- `docker compose --profile realtime-core config --quiet`;
- `docker compose up -d airflow-postgres control-db-init`;
- repeated `docker compose up -d --force-recreate control-db-init`, with
  `control-db-init` exiting `0` on an existing volume;
- direct PostgreSQL checks showing:
  - Airflow metadata remains `airflow|airflow`;
  - `olist_control` exists on the same server;
  - the `olist_control` role can query `audit.batch_runs`;
- `uv run python -m unittest discover -s tests -p "test_*control*.py" -v`;
- `uv run python -m unittest discover -s tests -p test_postgres_oracle_export.py -v`;
- `uv run dbt test --select "test_type:unit" --threads 1`;
- `uv run python scripts/ci/check_stage4_cdc_integration.py --postgres-password-file docker/secrets/dev/postgres_password.txt --s3-secret-file docker/secrets/dev/airflow_api_secret_key.txt`;
- `uv run python scripts/ci/check_stage5_cdc_integration.py`;
- `uv run ruff check .`;
- targeted `uv run pyright` over changed Python modules and CI helpers.

Notes:

- `docker compose --profile realtime-core config --quiet` emitted warnings
  about `C:\Users\fyujv\.docker\config.json` being inaccessible, but returned
  exit code `0`.
- Local Airflow DAG import cannot run directly on this Windows host because
  Airflow imports `fcntl`; this remains a platform limitation. The DAG import
  check should be run in the Linux Airflow container or CI.
- The local PostgreSQL oracle service was started for dbt unit verification.

## Phase boundary

No dbt model SQL was ported to ClickHouse, `local_pg` remains the default dbt
target, the analytical PostgreSQL oracle remains active, and raw batch/CDC
warehouse writes still target PostgreSQL. Phase 2 only separates transactional
control state and configuration from the analytical warehouse.
