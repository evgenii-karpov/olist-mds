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
uv run python scripts/cdc/local_lab.py stop --volumes
```

This permanently deletes the local PostgreSQL databases, Kafka data, MinIO
objects, NiFi repositories, Airflow metadata, and telemetry history. Use
`uv run python scripts/cdc/local_lab.py stop` when volumes must be preserved.

## 2. Start and smoke-check the local stack

Use the cross-platform helper:

```powershell
uv run python scripts/cdc/local_lab.py start --status
```

It builds the local runtime images, starts the complete Compose stack, deploys
the NiFi process group, validates Airflow DAG discovery, configures Apicurio,
validates Kafka topics, and prints the final Compose status. It also enables
Airflow StatsD metrics for the started Airflow container unless
`AIRFLOW_STATSD_ON` is already set.

For repeated starts after the images already exist:

```powershell
uv run python scripts/cdc/local_lab.py start --skip-build --status
```

Expected result:

- long-running PostgreSQL, ClickHouse, Kafka, Connect, Registry, MinIO, NiFi,
  Airflow, Prometheus, Grafana, Loki, and exporter services are `Up` or
  `healthy`;
- one-shot bootstrap services such as `clickhouse-init`, `control-db-init`,
  `kafka-topics`, and `minio-init` completed with exit code `0`;
- the helper reports `Validated 4 CDC Airflow DAGs` and
  `Validated 22 explicit Kafka topics`.

Airflow is available at <http://localhost:8080>. The local credentials are:

```text
username: admin
password: admin
```

### Local lab helper command reference

The E2E workflow should use `scripts/cdc/local_lab.py` for routine local
operations:

| Command                           | Purpose                                                                  |
| --------------------------------- | ------------------------------------------------------------------------ |
| `start [--skip-build] [--status]` | Build images, start Compose services, deploy NiFi, and run smoke checks. |
| `stop [--volumes]`                | Stop services, optionally deleting local Compose volumes.                |
| `check`                           | Run Airflow DAG discovery plus registry and Kafka topic checks.          |
| `bootstrap-nifi`                  | Deploy or update the version-controlled NiFi CDC process group.          |
| `seed`                            | Load the full local `olist.zip` archive into OLTP PostgreSQL.            |
| `seed-small`                      | Load the committed small fixture archive.                                |
| `register-connector`              | Create or update the Debezium connector and wait for `RUNNING`.          |
| `connector-status`                | Print Debezium connector and task state.                                 |
| `wait-connector-running`          | Wait until the connector and task are `RUNNING`.                         |
| `restart-failed-connector`        | Restart failed Debezium tasks without deleting offsets or slots.         |
| `enable-dags`                     | Unpause the CDC DAGs used by the local near-realtime path.               |
| `trigger-ingest`                  | Trigger one `olist_cdc_ingest_local` run.                                |
| `airflow-runs`                    | List recent CDC DAG runs.                                                |
| `kafka-lag`                       | Show lag for the NiFi CDC consumer group.                                |
| `warehouse-status`                | Print `raw_cdc` counts and `cdc_audit` summary.                          |
| `status`                          | Print Compose plus connector, Kafka, Airflow, and warehouse status.      |

## 3. Seed the OLTP source

Seed before the first connector registration so Debezium takes an initial
snapshot of populated source tables:

```powershell
uv run python scripts/cdc/local_lab.py seed
```

This command loads the full `olist.zip` archive and validates row counts for all
captured CDC tables. For the committed small fixture, use
`uv run python scripts/cdc/local_lab.py seed-small` instead.

## 4. Register and validate Debezium

```powershell
uv run python scripts/cdc/local_lab.py register-connector
uv run python scripts/cdc/local_lab.py connector-status
```

The connector and its task must both be `RUNNING`.

The same status is available through the REST endpoint:

```powershell
Invoke-RestMethod `
  http://localhost:8083/connectors/olist-postgres-cdc/status |
  ConvertTo-Json -Depth 10
```

## 5. Verify Kafka-to-NiFi movement

Inspect the stable NiFi consumer group:

```powershell
uv run python scripts/cdc/local_lab.py kafka-lag
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

## 6. Enable the CDC DAGs

Unpause the Asset-triggered transform before the scheduled ingest:

```powershell
uv run python scripts/cdc/local_lab.py enable-dags
```

Runtime behavior:

- `olist_cdc_ingest_local` runs every two minutes;
- it loads only closed NiFi objects;
- a run that inserts new raw events emits Asset `olist://cdc/raw/local`;
- the Asset starts `olist_cdc_transform_local`;
- `olist_cdc_quality_local` runs hourly, independently of each micro-batch.

To trigger ingest immediately after NiFi has closed its objects:

```powershell
uv run python scripts/cdc/local_lab.py trigger-ingest
```

Do not trigger the transform manually during the normal test. A successful
ingest containing new rows must trigger it through the Asset event.

## 7. Expected timing

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
uv run python scripts/cdc/local_lab.py airflow-runs --limit 5
```

Both DAGs must finish in `success`.

## 8. Verify warehouse ingest and transform audit

Inspect warehouse and audit state:

```powershell
uv run python scripts/cdc/local_lab.py warehouse-status
```

For the first effective run:

- `status = SUCCEEDED`;
- `files_loaded > 0`;
- `inserted_rows > 0`;
- `gap_count = 0`.

The effective transform must have `status = SUCCEEDED`, `files_selected > 0`,
and `events_selected > 0`.

Verify raw CDC events:

```powershell
docker compose exec -T airflow-postgres `
  psql -U olist -d olist_analytics `
  -c "select count(*) as raw_orders, max(_warehouse_loaded_at) as last_loaded_at, max(_source_ts) as last_source_at from raw_cdc.orders;"
```

Verify current realtime order state:

```powershell
docker compose exec -T airflow-postgres `
  psql -U olist -d olist_analytics `
  -c "select count(*) as current_orders, max(_source_ts) as last_source_at from realtime_staging.stg_cdc__orders_current;"
```

Verify realtime marts:

```powershell
docker compose exec -T airflow-postgres `
  psql -U olist -d olist_analytics `
  -c "select count(*) as mart_rows, max(max_source_ts) as last_source_at from realtime_marts.mart_daily_revenue_realtime;"
```

All three queries must return rows.

## 9. Verify integrity

Offset gaps must be zero:

```powershell
docker compose exec -T airflow-postgres `
  psql -U olist -d olist_analytics `
  -c "select coalesce(sum(gap_count), 0) as total_gaps from cdc_audit.cdc_partition_watermarks;"
```

Reconciliation must contain only `PASS`:

```powershell
docker compose exec -T airflow-postgres `
  psql -U olist -d olist_analytics `
  -c "select status, count(*) from cdc_audit.cdc_reconciliation group by status order by status;"
```

No unresolved DLQ records are expected:

```powershell
docker compose exec -T airflow-postgres `
  psql -U olist -d olist_analytics `
  -c "select count(*) as open_dlq from cdc_audit.cdc_dead_letters where resolution_status = 'OPEN';"
```

Inspect mart freshness:

```powershell
docker compose exec -T airflow-postgres `
  psql -U olist -d olist_analytics `
  -c "select model_name, max_source_ts, build_time, latency_seconds from cdc_audit.cdc_mart_freshness order by model_name;"
```

## 10. Prove incremental propagation

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

## 11. Run the quality DAG immediately

The quality DAG normally starts at the beginning of each hour. Trigger it
manually for this validation:

```powershell
docker compose exec -T airflow `
  airflow dags trigger olist_cdc_quality_local
```

The run must succeed. It validates offset continuity, latest reconciliation,
mart freshness, and realtime model invariants.

## 12. Verify observability

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

## 13. Realtime marts versus published analytics

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

## 14. Batch-to-realtime parity integration

For the defining end-to-end evidence, use the disposable default batch plus
`realtime-core` stack and the exact committed fixture on both branches:

```powershell
uv run python scripts/cdc/local_lab.py stop --volumes
uv run python scripts/cdc/local_lab.py start --status
docker compose exec -T airflow `
  python scripts/ci/check_batch_cdc_parity_integration.py `
  --profile tests/fixtures/olist_small/source_profile_small.json `
  --timeout-seconds 1200 `
  --poll-seconds 2 `
  --report data/reports/batch-cdc-parity.json
Get-Content data/reports/batch-cdc-parity.json
uv run python scripts/cdc/local_lab.py stop --volumes
```

The command runs the real batch DAG and the real Debezium snapshot through
Kafka, NiFi, MinIO, CDC ingest, the Asset-triggered transform, and realtime
dbt models. A passing report proves initial-snapshot business parity for all
eight captured source projections, the item-grain fact, and both marts. It
does not prove the latency SLO, SCD2 history equality, or CRUD/replay/recovery
behavior; those remain separate checks. The manual GitHub Actions workflow
runs this same command and uploads the bounded JSON report.

## 15. Troubleshooting

For a compact snapshot of the local lab state, use:

```powershell
uv run python scripts/cdc/local_lab.py status
```

This prints Compose status and non-fatal connector, Kafka lag, Airflow run, and
warehouse summaries.

Connector is not running:

```powershell
docker compose logs --no-color --tail=300 kafka-connect
uv run python scripts/cdc/local_lab.py connector-status
```

Kafka has records but MinIO objects do not appear:

```powershell
docker compose logs --no-color --tail=300 nifi
docker compose logs --no-color nifi-bootstrap
```

MinIO objects exist but `raw_cdc` remains empty:

```powershell
docker compose logs --no-color --tail=300 airflow
uv run python scripts/cdc/local_lab.py trigger-ingest
```

`raw_cdc` contains data but realtime marts remain empty:

```powershell
uv run python scripts/cdc/local_lab.py airflow-runs `
  --dag-id olist_cdc_transform_local `
  --limit 5
```

For focused recovery procedures, see:

- [CDC warehouse ingest](cdc-warehouse-ingest.md);
- [CDC realtime dbt](cdc-realtime-dbt.md);
- [CDC service restart](cdc-service-restart.md);
- [CDC Kafka replay](cdc-kafka-replay.md).
