# ClickHouse dbt project

This project builds the local ClickHouse analytical models from the serving
projection created by Airflow. It uses the `local_clickhouse` target and no
other warehouse adapter.

Each build identifies the serving sync that supplies its input:

```text
dbt build --project-dir dbt/olist_clickhouse --profiles-dir dbt/olist_clickhouse --target local_clickhouse --vars '{sync_run_seq: 42, sync_run_id: "sync-000042"}'
```

Models write physical rows to `gold_store` under the sync sequence. Post-hooks
expose only the latest published sequence through `gold` views. A retry of
the same sync sequence is idempotent.

See [MODEL_CATALOG.md](MODEL_CATALOG.md) for the model grains and ordering.

Inside the Airflow image, use `bin/run-dbt.sh`. It reads the ClickHouse
password from `CLICKHOUSE_PASSWORD_FILE` and does not print credentials.

Run static checks with:

```powershell
uv run dbt parse --project-dir dbt/olist_clickhouse --profiles-dir dbt/olist_clickhouse --target local_clickhouse
uv run python scripts/ci/check_dbt_clickhouse_contract.py
```
