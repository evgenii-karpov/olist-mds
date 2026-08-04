# Stage L2 implementation report

Status: **L2 observability acceptance PASS; Stage L remains ACTIVE**.

This report records the target observability implementation and its bounded
runtime evidence. It does not declare Stage L complete: L3 CI cutover, L4
legacy removal and the independent Stage V gate remain outstanding.

## Candidate and evidence

- Candidate: uncommitted L2 worktree on the existing Stage L implementation
  branch.
- Evidence root:
  `data/stage-l-evidence/L2/stage_l2_20260804_full/`.
- Acceptance result:
  `observability-acceptance-final.json` is `PASS`.
- Failure-transition evidence:
  `failure-connect.json` and `failure-minio.json` both record `fired: true`
  and `resolved: true`.
- Live Compose project used for bounded acceptance: `olist_l2_full`.
- `scripts/validation/stage_v_candidate_e2e.py` was not modified and the Stage
  V E2E was not run in L2.

## Implemented target chain

- Added the repository-owned `target-probe` service and image. It exposes
  bounded health probes and redacted Prometheus metrics for MySQL, Kafka,
  Kafka Connect, Apicurio, Spark, MinIO, Polaris, ClickHouse, Airflow and the
  control PostgreSQL database.
- Added pinned Alertmanager and Alloy services. Alertmanager delivers
  fire/resolve webhooks to `target-probe`; Alloy discovers only running Docker
  containers, applies bounded `service`/`environment` labels and writes to
  Loki using the read-only Docker socket.
- Added a pinned Kafka exporter with an explicit topic allowlist. Kafka
  exporter supplies partition end offsets; Bronze now publishes its actual
  Structured Streaming checkpoint end offsets through `StatusPublisher`, and
  `target-probe` joins the two into
  `olist_kafka_consumer_lag{consumer_group="olist-spark-bronze",...}`.
  Ordinary committed consumer-group lag is not treated as Spark truth because
  Structured Streaming manages offsets in its checkpoint. See the [Apache
  Spark Kafka integration documentation](https://spark.apache.org/docs/latest/streaming/structured-streaming-kafka-integration.html).
- Rebuilt Prometheus jobs, recording rules, alerts, dashboards, runbooks and
  validation around the target chain. The target contract contains 18 scrape
  jobs, 23 alert rules and 6 dashboards.
- Made `spark-ops` create its target audit status table when the fresh catalog
  does not contain it. The rebuilt Scala image passed format, compile, test and
  package checks, and the live one-shot `spark-ops` job exited successfully.
- Removed only the explicitly obsolete L2 observability assets:
  `observability/grafana/dashboards/cdc-nifi-storage.json` and
  `observability/postgres/oltp-queries.yml`. No general test deletion was made.

## Runtime diagnostics and corrections

- The initial Kafka lag assumption based on ordinary consumer-group offsets
  did not describe the Spark Structured Streaming runtime: the target group
  list was empty while Bronze checkpoint progress was real. The implementation
  was corrected to use checkpoint-derived offsets plus Kafka partition end
  offsets, with separate business-topic lag for downstream Silver freshness.
- Loki 3.5.0 produced structured-metadata ingestion errors with the local log
  path. L2 pins Loki 3.6.5 and forwards Docker log lines directly through
  `loki.source.docker`; the acceptance run verified `/ready`, bounded labels
  and a non-empty Loki query. The version change is pinned in Compose and
  `streaming/runtime-versions.json`.
- A stale-container discovery path caused Alloy to inspect dead Docker
  container IDs. The running-container filter and Alloy restart removed that
  noise from the active log pipeline.
- The serving publication-stalled alert can remain active in this run because
  Stage V/serving synchronization was intentionally not executed. That is an
  expected diagnostic signal, not a failure of the observability acceptance.

## Validation performed

The following checks passed without running Stage V:

- target observability validator: 18 scrape jobs, 23 alerts, 6 dashboards;
- Compose config with platform, streaming, serving, observability and logs
  profiles;
- 16 target observability/contract tests;
- Ruff check and format check;
- Prometheus `promtool` config validation;
- Alertmanager `amtool check-config`;
- Alloy `fmt --test`;
- live health/readiness and target probes for all configured domains;
- Alertmanager webhook receiver metrics, Loki labels/query and Grafana API
  dashboard/datasource checks;
- real `kafka-connect` and `minio` fault injection with `FIRING -> RESOLVED`
  evidence.

The independent Stage V script remains untouched and is reserved for the L3
CI/manual acceptance gate. The L2 observability test is intentionally
separate from that script.
