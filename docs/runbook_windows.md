# Windows Runbook

This runbook uses PowerShell commands from the repository root.

## Prerequisites

- Docker Desktop is running.
- `uv` is installed.

The repository includes the full `olist.zip` archive for local runs and the
committed small fixture for CI-style smoke runs.

## One-Time Setup

```powershell
winget install --id astral-sh.uv -e
uv sync --locked
Copy-Item -Force dbt\olist_analytics\profiles.yml.example dbt\olist_analytics\profiles.yml
Push-Location dbt\olist_analytics
uv run dbt deps
Pop-Location
uv run pre-commit install
```

`compose.yaml` points at committed development-only Docker secret files, so the
local stack starts without a `.env` file. Copy `.env.example` to `.env` only
when you want to override local config, point Compose at custom secret files,
or configure the AWS/Redshift path.

## Start The Local Stack

```powershell
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

```powershell
uv run python -m unittest discover -s tests -v
```

Run lint and formatting checks:

```powershell
uv run ruff check airflow\dags scripts tests
uv run ruff format --check airflow\dags scripts tests
uv run sqlfluff lint dbt\olist_analytics\models dbt\olist_analytics\snapshots dbt\olist_analytics\tests dbt\olist_analytics\analyses dbt\olist_analytics\macros
uv run pre-commit run --all-files
```

Run the small fixture pipeline used by CI:

```powershell
docker compose up -d --wait postgres airflow-postgres airflow
docker compose exec -T airflow python scripts/ci/check_fixture_pipeline_idempotency.py
```

The check resets the local analytical schemas and fixture raw directory before
the first Airflow DAG run, so use it for validation runs rather than
exploratory local tables.

## Full Manual Run

Validate the full source archive:

```powershell
uv run python scripts\utilities\validate_source_contract.py
```

Prepare raw files:

```powershell
uv run python scripts\ingestion\prepare_olist_raw_files.py `
  --batch-date 2018-09-01 `
  --batch-id 2018-09-01 `
  --run-id manual_2018_09_01 `
  --dead-letter-max-rows 10 `
  --dead-letter-max-rate 0.001
```

Generate correction feeds:

```powershell
uv run python scripts\ingestion\generate_correction_feeds.py `
  --batch-date 2018-09-01 `
  --batch-id 2018-09-01 `
  --run-id manual_2018_09_01 `
  --dead-letter-max-rows 10 `
  --dead-letter-max-rate 0.001
```

Load raw files into PostgreSQL:

```powershell
uv run python scripts\loading\load_raw_to_postgres.py `
  --bootstrap-sql-dir infra\postgres `
  --batch-date 2018-09-01 `
  --batch-id 2018-09-01 `
  --run-id manual_2018_09_01
```

Run reconciliation:

```powershell
uv run python scripts\quality\reconcile_batch.py `
  --raw-dir data\raw\olist `
  --profile docs\source_profile.json `
  --bootstrap-sql-dir infra\postgres `
  --batch-date 2018-09-01 `
  --batch-id 2018-09-01 `
  --run-id manual_2018_09_01
```

Run dbt with the same unified flow as the Airflow DAG:

```powershell
Set-Location dbt\olist_analytics
$env:DBT_PROFILES_DIR = (Get-Location).Path
$env:DBT_TARGET = "local_pg"
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"
$env:POSTGRES_DB = "olist_analytics"
$env:POSTGRES_USER = "olist"
$env:POSTGRES_PASSWORD = "olist"

uv run dbt build --selector batch --vars '{batch_date: "2018-09-01", lookback_days: 3}'
New-Item -ItemType Directory -Force target\edr | Out-Null
uv run edr report --env prod --profiles-dir . --profile-target local_pg --target-path "$((Get-Location).Path)\target\edr" --file-path "$((Get-Location).Path)\target\edr\elementary_report.html" --open-browser false
Set-Location ..\..
```

The operational `batch` selector also provisions the Elementary package models
required by dbt hooks and the following report command.

Use `uv run dbt build --selector batch --vars '{batch_date: "2018-09-01", lookback_days: 3}' --full-refresh`
when you trigger the equivalent of the DAG's `full_refresh: true` parameter.

The Elementary report is written to:

```text
dbt\olist_analytics\target\edr\elementary_report.html
```

In the Airflow image, Python dependencies and dbt packages are installed during
image build. The DAG run executes `dbt build --selector batch` and `edr report`;
it does not run
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

```powershell
uv run python scripts\utilities\create_dead_letter_demo_archive.py
```

Run ingestion against that archive:

```powershell
uv run python scripts\ingestion\prepare_olist_raw_files.py `
  --archive data\demo\dead_letter\olist_dead_letter_demo.zip `
  --output-dir data\raw\olist_dead_letter_demo `
  --batch-date 2018-09-01 `
  --batch-id 2018-09-01 `
  --run-id dead_letter_demo `
  --dead-letter-max-rows 10 `
  --dead-letter-max-rate 0.001
```

After correcting the dead-letter CSV, replay the fixed row:

```powershell
uv run python scripts\loading\replay_dead_letters.py `
  --entity order_payments `
  --dead-letter-file data\raw\olist_dead_letter_demo\dead_letter\order_payments\batch_date=2018-09-01\run_id=dead_letter_demo\order_payments.csv.gz `
  --replay-id demo_payment_fix `
  --bootstrap-sql-dir infra\postgres
```

## Cleanup

Stop containers:

```powershell
docker compose down
```

Remove local Docker volumes:

```powershell
docker compose down -v
```
