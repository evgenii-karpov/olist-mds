# Local near-realtime CDC end-to-end validation

This runbook validates the complete local path:

```text
OLTP PostgreSQL
  -> Debezium
  -> Kafka
  -> NiFi
  -> MinIO
  -> Airflow CDC ingest
  -> raw_cdc
  -> dbt realtime transform
  -> realtime_marts
```

Run every command from the repository root in PowerShell. The local stack uses
the stable development-only secrets committed under `docker/secrets/dev/`.
Do not generate replacement passwords before running this procedure.

## 1. Choose whether to preserve local state

For the most reproducible test, remove existing containers and volumes:

```powershell
docker compose `
  --profile realtime-core `
  --profile observability `
  --profile logs `
  down -v --remove-orphans
```

This permanently deletes the local PostgreSQL databases, Kafka data, MinIO
objects, NiFi repositories, Airflow metadata, and telemetry history. Omit `-v`
when those volumes must be preserved.

Enable Airflow StatsD metrics in the current PowerShell session:

```powershell
$env:AIRFLOW_STATSD_ON = "true"
```

## 2. Build the local runtime images

```powershell
docker compose --profile realtime-core build `
  airflow `
  kafka-connect `
  minio `
  nifi
```

The first build can take several minutes.

## 3. Start the complete stack

```powershell
docker compose `
  --profile realtime-core `
  --profile observability `
  --profile logs `
  up -d --wait
```

Inspect all services, including completed bootstrap containers:

```powershell
docker compose `
  --profile realtime-core `
  --profile observability `
  --profile logs `
  ps -a
```

Expected state:

- PostgreSQL, Kafka, Connect, Registry, MinIO, NiFi, Airflow, Prometheus,
  Grafana, Loki, and exporters are `Up` or `healthy`;
- `kafka-topics`, `minio-init`, `nifi-bootstrap`, and `cdc-warehouse-init`
  completed with exit code `0`;
- `cdc-profile-contract` may also be `Exited (0)`.

Inspect bootstrap logs:

```powershell
docker compose logs --no-color `
  kafka-topics `
  minio-init `
  nifi-bootstrap `
  cdc-warehouse-init
```

The logs must not contain a traceback, failed initialization, or invalid NiFi
processors.

## 4. Validate Airflow DAG discovery

```powershell
docker compose exec -T airflow airflow dags list-import-errors

docker compose exec -T airflow airflow dags list |
  Select-String "olist_cdc"
```

There must be no import errors. The list must contain:

- `olist_cdc_ingest_local`;
- `olist_cdc_backfill_local`;
- `olist_cdc_transform_local`;
- `olist_cdc_quality_local`.

Airflow is available at <http://localhost:8080>. The local credentials are:

```text
username: admin
password: admin
```

## 5. Configure Apicurio and validate Kafka topics

```powershell
uv run python scripts/cdc/stage2_admin.py configure-registry

uv run python scripts/cdc/stage2_admin.py validate-topics
```

Expected output confirms `BACKWARD_TRANSITIVE` registry compatibility and a
valid explicit topic inventory.

## 6. Seed the OLTP source

Seed before the first connector registration so Debezium takes an initial
snapshot of populated source tables:

```powershell
uv run python -m scripts.simulation seed `
  --archive tests/fixtures/olist_small/olist_small.zip `
  --seed 101 `
  --run-id e2e_initial_seed `
  --password-file docker/secrets/dev/postgres_password.txt
```

Verify that the source contains orders:

```powershell
docker compose exec -T oltp-postgres `
  psql -U olist_admin -d olist_oltp `
  -c "select count(*) as source_orders from public.orders;"
```

`source_orders` must be greater than zero.

## 7. Register and validate Debezium

```powershell
uv run python scripts/cdc/stage2_admin.py register-connector `
  --password-file docker/secrets/dev/postgres_password.txt

uv run python scripts/cdc/stage2_admin.py connector-status
```

The connector and its task must both be `RUNNING`.

The same status is available through the REST endpoint:

```powershell
Invoke-RestMethod `
  http://localhost:8083/connectors/olist-postgres-cdc/status |
  ConvertTo-Json -Depth 10
```

## 8. Verify Kafka-to-NiFi movement

Inspect the stable NiFi consumer group:

```powershell
docker compose exec -T kafka `
  /opt/kafka/bin/kafka-consumer-groups.sh `
  --bootstrap-server kafka:29092 `
  --describe `
  --group olist-nifi-cdc-v1
```

Lag may be positive during the initial snapshot but must subsequently decrease
to zero.

NiFi closes small files after 45 seconds. Allow approximately one minute after
connector registration before expecting closed objects.

NiFi is available at <https://localhost:8443/nifi/>. A browser warning for the
local certificate is expected.

```text
username: nifi-admin
password: local_dev_only_secret_key
```

In NiFi, verify:

- the `olist-cdc-v1` process group exists;
- processors are running;
- FlowFiles move through the graph;
- queues drain after the snapshot;
- processor errors remain empty.

MinIO is available at <http://localhost:9001>.

```text
username: minioadmin
password: local_dev_only_secret_key
```

Bucket `olist-cdc` must contain objects under:

- `landing/debezium/`;
- `stage/cdc/`;
- `manifests/cdc/`.

## 9. Enable the CDC DAGs

Unpause the Asset-triggered transform before the scheduled ingest:

```powershell
docker compose exec -T airflow `
  airflow dags unpause olist_cdc_transform_local

docker compose exec -T airflow `
  airflow dags unpause olist_cdc_ingest_local

docker compose exec -T airflow `
  airflow dags unpause olist_cdc_quality_local
```

Runtime behavior:

- `olist_cdc_ingest_local` runs every two minutes;
- it loads only closed NiFi objects;
- a run that inserts new raw events emits Asset `olist://cdc/raw/local`;
- the Asset starts `olist_cdc_transform_local`;
- `olist_cdc_quality_local` runs hourly, independently of each micro-batch.

To trigger ingest immediately after NiFi has closed its objects:

```powershell
docker compose exec -T airflow `
  airflow dags trigger olist_cdc_ingest_local
```

Do not trigger the transform manually during the normal test. A successful
ingest containing new rows must trigger it through the Asset event.

## 10. Expected timing

For the small fixture:

1. Debezium snapshot normally takes several seconds.
2. NiFi closes small files within 45 seconds.
3. Scheduled ingest starts at the next two-minute boundary.
4. Transform starts after the ingest Asset event.
5. Data appears in `raw_cdc`, `realtime_core`, and `realtime_marts`.

The normal target is approximately three to five minutes after source changes.
The first run can take longer while Airflow and dbt warm up.

Inspect recent DAG runs:

```powershell
docker compose exec -T airflow `
  airflow dags list-runs `
  --dag-id olist_cdc_ingest_local `
  --limit 5

docker compose exec -T airflow `
  airflow dags list-runs `
  --dag-id olist_cdc_transform_local `
  --limit 5
```

Both DAGs must finish in `success`.

## 11. Verify warehouse ingest and transform audit

Inspect recent ingest runs:

```powershell
docker compose exec -T postgres `
  psql -U olist -d olist_analytics `
  -c "select ingest_run_id, status, files_loaded, inserted_rows, duplicate_rows, gap_count, finished_at from cdc_audit.cdc_ingest_runs order by started_at desc limit 5;"
```

For the first effective run:

- `status = SUCCEEDED`;
- `files_loaded > 0`;
- `inserted_rows > 0`;
- `gap_count = 0`.

Inspect transform runs:

```powershell
docker compose exec -T postgres `
  psql -U olist -d olist_analytics `
  -c "select transform_run_id, status, files_selected, events_selected, finished_at from cdc_audit.cdc_transform_runs order by started_at desc limit 5;"
```

The effective transform must have `status = SUCCEEDED`, `files_selected > 0`,
and `events_selected > 0`.

Verify raw CDC events:

```powershell
docker compose exec -T postgres `
  psql -U olist -d olist_analytics `
  -c "select count(*) as raw_orders, max(_warehouse_loaded_at) as last_loaded_at, max(_source_ts) as last_source_at from raw_cdc.orders;"
```

Verify current realtime order state:

```powershell
docker compose exec -T postgres `
  psql -U olist -d olist_analytics `
  -c "select count(*) as current_orders, max(_source_ts) as last_source_at from realtime_staging.stg_cdc__orders_current;"
```

Verify realtime marts:

```powershell
docker compose exec -T postgres `
  psql -U olist -d olist_analytics `
  -c "select count(*) as mart_rows, max(max_source_ts) as last_source_at from realtime_marts.mart_daily_revenue_realtime;"
```

All three queries must return rows.

## 12. Verify integrity

Offset gaps must be zero:

```powershell
docker compose exec -T postgres `
  psql -U olist -d olist_analytics `
  -c "select coalesce(sum(gap_count), 0) as total_gaps from cdc_audit.cdc_partition_watermarks;"
```

Reconciliation must contain only `PASS`:

```powershell
docker compose exec -T postgres `
  psql -U olist -d olist_analytics `
  -c "select status, count(*) from cdc_audit.cdc_reconciliation group by status order by status;"
```

No unresolved DLQ records are expected:

```powershell
docker compose exec -T postgres `
  psql -U olist -d olist_analytics `
  -c "select count(*) as open_dlq from cdc_audit.cdc_dead_letters where resolution_status = 'OPEN';"
```

Inspect mart freshness:

```powershell
docker compose exec -T postgres `
  psql -U olist -d olist_analytics `
  -c "select model_name, max_source_ts, build_time, latency_seconds from cdc_audit.cdc_mart_freshness order by model_name;"
```

## 13. Prove incremental propagation

After the initial snapshot and transform have completed, create a finite
incremental workload using the current UTC time:

```powershell
$runId = "e2e_" + (Get-Date -Format "yyyyMMdd_HHmmss")
$startTime = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

uv run python -m scripts.simulation run `
  --seed 20260717 `
  --run-id $runId `
  --start-time $startTime `
  --event-limit 20 `
  --rate 5 `
  --password-file docker/secrets/dev/postgres_password.txt
```

Inspect the persisted simulator run:

```powershell
uv run python -m scripts.simulation status `
  --run-id $runId `
  --password-file docker/secrets/dev/postgres_password.txt
```

After three to five minutes, repeat the audit and warehouse queries from the
previous sections. Expected evidence:

- a new successful ingest run;
- a new successful transform run;
- newer raw source/load timestamps;
- updated affected realtime marts;
- refreshed `cdc_mart_freshness`;
- zero offset gaps and zero open DLQ records.

## 14. Run the quality DAG immediately

The quality DAG normally starts at the beginning of each hour. Trigger it
manually for this validation:

```powershell
docker compose exec -T airflow `
  airflow dags trigger olist_cdc_quality_local
```

The run must succeed. It validates offset continuity, latest reconciliation,
mart freshness, and realtime model invariants.

## 15. Verify observability

Open:

- Grafana: <http://localhost:3000>;
- Prometheus targets: <http://localhost:9090/targets>;
- Prometheus alerts: <http://localhost:9090/alerts>;
- Alertmanager: <http://localhost:9093>.

Grafana uses:

```text
username: admin
password: local_dev_only_secret_key
```

Verify:

- required Prometheus targets are `UP`;
- all six CDC dashboards are provisioned;
- Kafka lag returns to zero;
- NiFi queues return to zero;
- commit-to-mart latency has observations;
- mart freshness reflects the latest transform;
- the capacity/logs dashboard contains Loki records.

## 16. Realtime marts versus published analytics

The automatic near-realtime chain terminates in:

```text
realtime_marts.mart_daily_revenue_realtime
realtime_marts.mart_monthly_arpu_realtime
```

It intentionally does not switch stable `analytics.*` views automatically.
Publishing the realtime path requires an equivalent batch baseline, a passing
parity report, and explicit operator approval:

```powershell
uv run python scripts/cdc/realtime_transform.py record-parity

uv run python scripts/cdc/realtime_transform.py publish `
  --target realtime `
  --approved-by operator
```

Publication is not required to validate the CDC chain itself. Successful
ingest/transform runs and data in `raw_cdc`, `realtime_core`, and
`realtime_marts` are the primary evidence.

## 17. Batch-to-realtime parity integration

For the defining end-to-end evidence, use the disposable batch plus
`realtime-core` stack and the exact committed fixture on both branches:

```powershell
docker compose --profile batch --profile realtime-core down -v --remove-orphans
docker compose --profile realtime-core build airflow kafka-connect minio nifi
docker compose --profile batch --profile realtime-core up -d --wait
docker compose exec -T airflow `
  python scripts/ci/check_batch_cdc_parity_integration.py `
  --archive tests/fixtures/olist_small/olist_small.zip `
  --profile tests/fixtures/olist_small/source_profile_small.json `
  --timeout-seconds 1200 `
  --poll-seconds 2 `
  --report data/reports/batch-cdc-parity.json
Get-Content data/reports/batch-cdc-parity.json
docker compose --profile batch --profile realtime-core down -v --remove-orphans
```

The command runs the real batch DAG and the real Debezium snapshot through
Kafka, NiFi, MinIO, CDC ingest, the Asset-triggered transform, and realtime
dbt models. A passing report proves initial-snapshot business parity for all
eight captured source projections, the item-grain fact, and both marts. It
does not prove the latency SLO, SCD2 history equality, or CRUD/replay/recovery
behavior; those remain separate checks. The nightly/manual GitHub Actions
workflow runs this same command and uploads the bounded JSON report.

## 18. Troubleshooting

Connector is not running:

```powershell
docker compose logs --no-color --tail=300 kafka-connect
uv run python scripts/cdc/stage2_admin.py connector-status
```

Kafka has records but MinIO objects do not appear:

```powershell
docker compose logs --no-color --tail=300 nifi
docker compose logs --no-color nifi-bootstrap
```

MinIO objects exist but `raw_cdc` remains empty:

```powershell
docker compose logs --no-color --tail=300 airflow
docker compose exec -T airflow airflow dags trigger olist_cdc_ingest_local
```

`raw_cdc` contains data but realtime marts remain empty:

```powershell
docker compose exec -T airflow `
  airflow dags list-runs `
  --dag-id olist_cdc_transform_local `
  --limit 5
```

For focused recovery procedures, see:

- [CDC warehouse ingest](cdc-warehouse-ingest.md);
- [CDC realtime dbt](cdc-realtime-dbt.md);
- [CDC service restart](cdc-service-restart.md);
- [CDC Kafka replay](cdc-kafka-replay.md).
