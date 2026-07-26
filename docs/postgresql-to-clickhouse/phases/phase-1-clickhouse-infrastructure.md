# Phase 1: ClickHouse dependencies and infrastructure

Status: completed on 2026-07-23.

## Delivered contract

- Added pinned ClickHouse dependencies:
  `dbt-clickhouse==1.10.1`, `clickhouse-connect==1.5.0`, and
  `elementary-data[clickhouse,redshift]==0.23.4`.
- Added the pinned ClickHouse server image
  `clickhouse/clickhouse-server:26.3.17.4`.
- Added a default Compose `clickhouse` service with persistent data volume,
  UTC server configuration, internal Prometheus endpoint, nofile ulimit,
  Docker-secret password handling, HTTP host port `8123`, and native host port
  `19000` to avoid the MinIO `9000` host-port conflict.
- Added an idempotent `clickhouse-init` service that replays
  `infra/clickhouse/initdb/*.sql` against both new and existing volumes.
- Added ClickHouse databases for raw, runtime, dbt, snapshot, mart, parity, and
  Elementary ownership boundaries.
- Added initial ClickHouse DDL for 11 raw batch entities, eight typed raw CDC
  event tables, and `pipeline_runtime.cdc_transform_run_files`.
- Added `local_clickhouse` outputs to both the project and Elementary dbt
  profiles while retaining `local_pg` as the default target.
- Added `scripts/ci/check_clickhouse_smoke.py` for a trivial connection and
  initialized-table smoke check.
- Added static Phase 1 contract tests covering Compose, dbt profile, pinned
  image/dependency expectations, and ClickHouse storage DDL.

## Verification evidence

Passed:

- `uv lock`;
- `docker compose config --quiet`;
- `docker compose --profile realtime-core config --quiet`;
- `docker compose --profile observability config --quiet`;
- `docker compose up -d --force-recreate clickhouse clickhouse-init`;
- repeated `docker compose up -d --force-recreate clickhouse-init` on the same
  volume, with `clickhouse-init` exiting `0` both times after DDL fixes;
- `uv run python scripts/ci/check_clickhouse_smoke.py`, reporting
  `ClickHouse 26.3.17.4` and 20 initialized Phase 1 tables;
- `dbt debug --target local_clickhouse` using a temporary profiles directory
  copied from `profiles.yml.example`;
- `uv run dbt parse --no-partial-parse` for `local_pg`;
- `uv run dbt parse --target redshift --no-partial-parse` with dummy Redshift
  connection variables;
- `uv run python -m unittest discover -s tests -p test_clickhouse_phase1_contracts.py -v`;
- `uv run python -m unittest discover -s tests -p test_postgres_oracle_export.py -v`;
- `uv run dbt test --select "test_type:unit" --threads 1` against `local_pg`;
- `uv run python scripts/ci/check_stage5_cdc_integration.py`.

Notes:

- `docker compose --profile ... config --quiet` emitted warnings about
  `C:\Users\fyujv\.docker\config.json` being inaccessible, but returned exit
  code `0`.
- `dbt compile` for `local_pg` and Redshift still requires real warehouse
  connections or runtime hooks to acquire connections. Offline compile was not
  usable for those targets; parse remained green.
- The local ignored `dbt/olist_analytics/profiles.yml` did not contain the new
  output. The committed `profiles.yml.example` was copied to a temporary
  profiles directory for the `local_clickhouse` debug check.

## Phase boundary

No shared model SQL was ported, no batch or CDC writer was changed, no control
state was moved, and `local_pg` remains the default oracle. ClickHouse is now
available as initialized local analytical infrastructure for later candidate
phases.
