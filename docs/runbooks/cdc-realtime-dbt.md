# Target streaming and dbt serving

Spark owns CDC normalization and Iceberg Silver state. The ClickHouse dbt
project owns the finite serving candidate and Gold publication; there is no
second realtime transformation project.

Validate the target project statically:

```powershell
uv run dbt parse --project-dir dbt/olist_clickhouse --profiles-dir dbt/olist_clickhouse --target local_clickhouse
uv run dbt compile --project-dir dbt/olist_clickhouse --profiles-dir dbt/olist_clickhouse --target local_clickhouse --vars '{"sync_run_seq": 1, "sync_run_id": "manual-contract"}'
uv run python scripts/ci/check_dbt_clickhouse_contract.py
```

For a live candidate, let `local_lab.py sync-serving` allocate the serving
control run and invoke the target DAG. Validate the result with
`validate-serving`; never mark a publication successful by editing control
state directly.

Schema evolution is governed by the versioned Avro/Apicurio contracts and the
Spark reader policy in `docs/plans/lakehouse/contracts/spark-streaming.md`.
