# macOS Runbook

This runbook uses shell commands from the repository root.

## Prerequisites

- Docker Desktop or another Docker runtime with the Compose plugin is running.
- `uv` is installed.

The repository includes the full `olist.zip` archive for local runs and the
committed small fixture for CI-style smoke runs.

## One-Time Setup

```bash
brew install uv
uv sync --locked
cp dbt/olist_analytics/profiles.yml.example dbt/olist_analytics/profiles.yml
(cd dbt/olist_analytics && uv run dbt deps)
uv run pre-commit install
```

If you do not use Homebrew, install `uv` with Astral's standalone installer and
then rerun the remaining setup commands.

`compose.yaml` already points at committed demo-only Docker secret files, so a
local stack can start without a `.env` file. Copy `.env.example` to `.env` only
when you want to override local config, point Compose at custom secret files,
or configure the AWS/Redshift path.

## Start The Local Stack

```bash
docker compose build
docker compose up -d
```

Airflow is available at:

```text
http://localhost:8080
```

Local development credentials:

```text
username: admin
password: admin
```

## Fast Smoke Checks

Run Python tests:

```bash
uv run python -m unittest discover -s tests -v
```

Run lint and formatting checks:

```bash
uv run ruff check airflow/dags scripts tests
uv run ruff format --check airflow/dags scripts tests
uv run sqlfluff lint dbt/olist_analytics/models dbt/olist_analytics/snapshots dbt/olist_analytics/tests dbt/olist_analytics/analyses dbt/olist_analytics/macros
uv run pre-commit run --all-files
```

Run the small fixture pipeline used by CI:

```bash
docker compose up -d --wait postgres airflow-postgres airflow
docker compose exec -T airflow python scripts/ci/check_fixture_pipeline_idempotency.py
```

The check resets the local analytical schemas and fixture raw directory before
the first Airflow DAG run, so use it for validation runs rather than
exploratory local tables.

## Full Manual Run

Validate the full source archive:

```bash
uv run python scripts/utilities/validate_source_contract.py
```

Prepare raw files:

```bash
uv run python scripts/ingestion/prepare_olist_raw_files.py \
  --batch-date 2018-09-01 \
  --batch-id 2018-09-01 \
  --run-id manual_2018_09_01 \
  --dead-letter-max-rows 10 \
  --dead-letter-max-rate 0.001
```

Generate correction feeds:

```bash
uv run python scripts/ingestion/generate_correction_feeds.py \
  --batch-date 2018-09-01 \
  --batch-id 2018-09-01 \
  --run-id manual_2018_09_01 \
  --dead-letter-max-rows 10 \
  --dead-letter-max-rate 0.001
```

Load raw files into PostgreSQL:

```bash
uv run python scripts/loading/load_raw_to_postgres.py \
  --bootstrap-sql-dir infra/postgres \
  --batch-date 2018-09-01 \
  --batch-id 2018-09-01 \
  --run-id manual_2018_09_01
```

Run reconciliation:

```bash
uv run python scripts/quality/reconcile_batch.py \
  --raw-dir data/raw/olist \
  --profile docs/source_profile.json \
  --bootstrap-sql-dir infra/postgres \
  --batch-date 2018-09-01 \
  --batch-id 2018-09-01 \
  --run-id manual_2018_09_01
```

Run dbt with the same unified flow as the Airflow DAG:

```bash
cd dbt/olist_analytics
export DBT_PROFILES_DIR="$PWD"
export DBT_TARGET="local_pg"
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"
export POSTGRES_DB="olist_analytics"
export POSTGRES_USER="olist"
export POSTGRES_PASSWORD="olist"

uv run dbt build --vars '{batch_date: "2018-09-01", lookback_days: 3}'
mkdir -p target/edr
uv run edr report --env prod --profiles-dir . --profile-target local_pg --target-path "$PWD/target/edr" --file-path "$PWD/target/edr/elementary_report.html" --open-browser false
cd ../..
```

Use `uv run dbt build --vars '{batch_date: "2018-09-01", lookback_days: 3}' --full-refresh`
when you trigger the equivalent of the DAG's `full_refresh: true` parameter.

The Elementary report is written to:

```text
dbt/olist_analytics/target/edr/elementary_report.html
```

In the Airflow image, Python dependencies and dbt packages are installed during
image build. The DAG run executes `dbt build` and `edr report`; it does not run
`dbt deps` at task runtime. The mounted or baked dbt project must include an
up-to-date `profiles.yml` with both the `olist_analytics` and `elementary`
profiles before the DAG starts.

## Airflow Run

Open the `olist_modern_data_stack_local` DAG and trigger it with the default
local parameters:

```text
batch_date: 2018-09-01
lookback_days: 3
full_refresh: false
dead_letter_max_rows: 10
dead_letter_max_rate: 0.001
```

## AWS / Redshift Path

For the AWS DAG, copy `.env.example` to `.env`, fill in the non-secret
Redshift and S3 settings, and prefer `*_AWS_SECRET_ID` entries for sensitive
values such as `REDSHIFT_PASSWORD` and `AIRFLOW__API__SECRET_KEY`. Let AWS
credentials come from the standard provider chain such as IAM role, AWS SSO, or
a short-lived shared-profile session instead of long-lived keys in `.env`.

## Dead-Letter Demo

Create a demo archive with one corrupt payment value:

```bash
uv run python scripts/utilities/create_dead_letter_demo_archive.py
```

Run ingestion against that archive:

```bash
uv run python scripts/ingestion/prepare_olist_raw_files.py \
  --archive data/demo/dead_letter/olist_dead_letter_demo.zip \
  --output-dir data/raw/olist_dead_letter_demo \
  --batch-date 2018-09-01 \
  --batch-id 2018-09-01 \
  --run-id dead_letter_demo \
  --dead-letter-max-rows 10 \
  --dead-letter-max-rate 0.001
```

After correcting the dead-letter CSV, replay the fixed row:

```bash
uv run python scripts/loading/replay_dead_letters.py \
  --entity order_payments \
  --dead-letter-file data/raw/olist_dead_letter_demo/dead_letter/order_payments/batch_date=2018-09-01/run_id=dead_letter_demo/order_payments.csv.gz \
  --replay-id demo_payment_fix \
  --bootstrap-sql-dir infra/postgres
```

## Cleanup

Stop containers:

```bash
docker compose down
```

Remove local Docker volumes:

```bash
docker compose down -v
```
