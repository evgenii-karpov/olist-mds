# Технический контракт: target observability lakehouse

- **Статус**: действующий нормативный контракт Stage L; implementation owner — L2.
- **Назначение**: определить, как наблюдаемость переходит с PostgreSQL/NiFi/raw-loader metrics на MySQL → Debezium/Kafka → Spark/Iceberg → ClickHouse serving stack.
- **Главное правило**: конфигурация Prometheus, alert rule или dashboard не считается target-артефактом, пока для него не доказана полная цепочка `producer → endpoint/exporter → scrape job → recording/alert → dashboard/runbook → acceptance evidence`.

## 1. Scope и запреты

В target observability входят:

- доступность и health source MySQL, binlog/GTID и Debezium heartbeat;
- Kafka broker/topic health и lag только target consumer groups/topics;
- Kafka Connect REST, connector/task state и snapshot/restart state;
- Apicurio Registry compatibility/availability;
- Spark Bronze/Silver/ops readiness, progress, failure state и checkpoint health;
- MinIO/Polaris/Iceberg catalog/storage readiness;
- ClickHouse serving, publication watermark, rejected boundary и rebuild state;
- Airflow/control-plane finite DAG health;
- Prometheus/Grafana/Loki/Alertmanager self-health и evidence publication.

Следующее запрещено:

- target scrape target на имя, которого нет в Compose или в явно добавленном exporter service;
- панели/alerts для `nifi`, PostgreSQL replication slot/WAL или старого raw S3 loader;
- сумма всех `kafka_consumergroup_lag` без allowlist target groups/topics;
- метрика без owner, label cardinality rule и теста на существование;
- failure-injection command, использующий fictitious service name;
- принятие `up` только потому, что `docker compose config` успешно разобрал YAML.

## 2. Baseline audit на L0

Baseline Compose содержит `platform-postgres`, `mysql`, `kafka`, `apicurio-registry`, `kafka-connect`, `minio`, `polaris`, `spark-master`, `spark-worker`, `spark-bronze`, `spark-silver`, `spark-ops`, `clickhouse`, `airflow`, `prometheus`, `grafana` и `loki`. В нём нет exporter services для большинства configured Prometheus targets и нет `alertmanager`/Alloy services. L2 обязан добавить target-owned Alertmanager и Alloy services: это не optional gap, поскольку Prometheus уже маршрутизирует alerts в Alertmanager, а log contract требует Loki/Alloy path.

Текущий `observability/prometheus/prometheus.yml` ссылается на `kafka-exporter`, `cdc-component-exporter`, `postgres-exporter-oltp`, `statsd-exporter`, `node-exporter`, `cadvisor`, `nifi-metrics-proxy` и `cdc-pipeline-exporter`; эти endpoints не являются target service inventory baseline. Это зафиксированная L0 gap, а не разрешение оставить phantom targets.

`streaming/runtime-versions.json` также не совпадает с Compose для части observability stack: например, manifest указывает Prometheus `v3.12.0`, Grafana `13.0.2` и Loki `3.6.5`, тогда как baseline Compose использует Prometheus `v3.5.0`, Grafana `12.1.1` и Loki `3.5.0`. L2/L3 должны выбрать один pinned target и согласовать manifest, image, config tests и evidence; silent downgrade или drift не принимается.

Текущие rules/dashboards также содержат legacy surface:

- PostgreSQL replication slot/WAL metrics;
- NiFi queue/backpressure and `olist_nifi_metrics_proxy_up`;
- old `olist-nifi-cdc-v1` consumer group;
- raw S3/warehouse/old dbt transform freshness;
- generic container/node metrics without a configured exporter;
- dashboard tags and runbooks naming PostgreSQL/NiFi.

Supporting observability files are not implicitly target-safe merely because
they live under `observability/`. The L0 decisions are explicit:

| Asset family | L0 decision | L2 requirement |
| --- | --- | --- |
| `observability/alertmanager/**` | `REWRITE` | Add a pinned Alertmanager service to the target observability profile, keep Prometheus routing and prove fire/resolve delivery with secret-free runbook annotations. |
| `observability/alloy/**` | `REWRITE` | Add a pinned Alloy service to the target logs profile, mount the Docker socket read-only, send to the real Loki service and test bounded labels. |
| `observability/statsd/**` | `REPLACE` | Do not enable the mapping until a real Airflow metrics endpoint/exporter exists. |
| `observability/loki/**` | `REWRITE` | Align retention, labels and service wiring with the target log pipeline. |
| `observability/grafana/provisioning/**` | `REWRITE` | Ensure every provisioned datasource/dashboard is present and target-scoped. |
| `observability/*README.md` | `REWRITE` | Active commands and service inventory must match Compose and the target contract. |

The current root README claims Alertmanager, Alloy, StatsD and multiple
exporters that are not present in the baseline Compose service inventory. L2
must wire the required Alertmanager/Alloy services and replace the StatsD and
exporter claims with the concrete target probe/exporter inventory; historical
documentation is not a runtime dependency.

## 3. Target producer and endpoint mapping

The table is normative. `L2 implementation` is intentionally explicit where the baseline has no producer; until that row is implemented, the row must not be enabled in Prometheus or marked healthy in acceptance.

| Signal family | Producer of truth | Endpoint/exporter decision | Target scrape identity | Required alert/evidence |
| --- | --- | --- | --- | --- |
| MySQL availability, connections, binlog/GTID | MySQL 8.4.10 | Add one pinned MySQL exporter or a bounded target probe; no PostgreSQL exporter. | `mysql` target job with explicit exporter/probe owner. | MySQL unavailable, binlog not advancing while source changes, exporter/probe down. |
| Debezium connector/task/heartbeat | Kafka Connect REST + connector state; heartbeat topic/source | Add a pinned Connect state exporter/probe or expose a real Connect metrics endpoint. | `kafka-connect` target job. | Connector/task failed, snapshot not progressing, heartbeat stale. |
| Kafka broker/topic and target lag | Kafka 4.3.1 and consumer group offsets | Add pinned Kafka exporter or use a verified native endpoint. Selector must allowlist Spark Bronze/Silver groups and target topics. | `kafka` and scoped `kafka-lag` jobs. | Broker unavailable, target lag high/growing, no false positives from unrelated groups. |
| Apicurio Registry | Registry HTTP health and compatibility API | Native health endpoint plus bounded compatibility probe; no legacy exporter assumption. | `apicurio` target job/probe. | Registry unavailable or compatibility check fails. |
| Spark master/worker | Spark runtime UI/metrics | Enable a verified Spark metrics endpoint or a target exporter reading real driver status; status JSON alone is not a Prometheus endpoint. | `spark` job(s) with driver/application labels bounded to known values. | Master/worker unavailable, Bronze/Silver query degraded, stale progress/checkpoint. |
| Spark Bronze/Silver/ops | Scala `StatusPublisher`, streaming query progress and Iceberg audit/progress | L2 must choose and test native metrics or a status-to-metrics exporter; no `spark-iceberg` fictitious service. | `spark-streaming` target job. | `DEGRADED/FATAL`, progress stalled while Kafka advances, checkpoint loss. |
| MinIO object storage | MinIO native metrics and health endpoint | Keep native `/minio/v2/metrics/cluster` and health check; target bucket names are `olist-lakehouse`/`olist-checkpoints` as contract requires. | `minio` job. | MinIO unavailable, storage errors, checkpoint/warehouse bucket failure. |
| Polaris catalog | Polaris health/API and catalog auth smoke | Native HTTP health plus bounded catalog read/write/auth probe; do not invent a `polaris-exporter` target without service. | `polaris` target probe. | Catalog unavailable, auth projection failure, namespace/catalog mismatch. |
| ClickHouse serving | ClickHouse native Prometheus endpoint at `clickhouse:9363` and serving control tables | Keep native endpoint; add target serving metrics from `scripts/serving/metrics.py` only when its producer is wired. | `clickhouse` job. | Serving unavailable, publication stalled, watermark drift, rejected boundary. |
| Airflow finite runtime | Airflow health API, DAG/task state and control DB | Health/API probe plus explicit finite-run evidence; StatsD is not target until a real exporter service is defined. | `airflow` job/probe. | Target DAG import/task failure, stale run, control DB unavailable. |
| Control PostgreSQL | `platform-postgres` control schemas | Add verified PostgreSQL exporter/probe only for control DB; name must not be `postgres-exporter-oltp`. | `control-postgres` job. | Control DB unavailable, migration/status write failure. |
| Prometheus/Grafana/Loki/Alertmanager | Their own HTTP/metrics endpoints | Keep self-health and wire Alertmanager because the target Prometheus configuration routes alerts to it. | `observability` jobs. | Rule reload/config failure, alert delivery failure, evidence/dashboard datasource failure. |

## 4. Metric and label policy

- Metric names use `olist_` prefix and identify the target component, not the historical implementation name.
- Labels are bounded to entity (8-value allowlist), topic (8 CDC topics + internal target topics), partition, connector, task, DAG and status enumerations. User IDs, order IDs, file URIs, error messages and secrets are never labels.
- Kafka lag recording rules filter by explicit target consumer group/topic allowlists. A global sum is not a valid SLO.
- `up` is a scrape signal, not a domain success signal. Domain alerts require a target-produced timestamp/counter and a bounded freshness condition.
- All metrics emitted by custom exporters must have a unit, help text, stable label set and a unit test for redaction/low cardinality.
- Logs and evidence redact secret values and do not include connector passwords, file-secret contents or credential projection payloads.

## 5. Rules, dashboards and runbooks

The following current assets require L2 work:

| Current asset | Decision | Required target work |
| --- | --- | --- |
| `observability/prometheus/prometheus.yml` | `REWRITE` | Derive jobs from actual Compose/exporter inventory; validation must fail on unknown targets. |
| `observability/prometheus/rules/cdc-component-alerts.yml` | `REWRITE` | Remove PostgreSQL WAL/NiFi/raw-loader alerts; add target MySQL/Connect/Kafka/Spark signals. |
| `observability/prometheus/rules/cdc-slo-recording.yml` | `REWRITE` | Scope lag and freshness to target groups and durability path. |
| `observability/prometheus/rules/lakehouse-serving-alerts.yml` | `REWRITE` | Retain serving intent; align names with actual target producer and runbook. |
| `observability/grafana/dashboards/cdc-nifi-storage.json` | `DELETE` | No NiFi dashboard may remain after replacement review. |
| `observability/grafana/dashboards/cdc-source-debezium.json` | `REWRITE` | MySQL/binlog and Connect state, no slot/WAL panels. |
| `observability/grafana/dashboards/cdc-kafka-connect.json` | `REWRITE` | Target connector and scoped lag. |
| `observability/grafana/dashboards/cdc-slo.json` | `REWRITE` | Target durability/serving SLOs. |
| `observability/grafana/dashboards/cdc-airflow-warehouse.json` | `REWRITE` | Target Iceberg/serving/Airflow, no raw warehouse wording. |
| `observability/grafana/dashboards/cdc-capacity-logs.json` | `REWRITE` | Actual target service/Loki labels. |
| `observability/postgres/oltp-queries.yml` | `DELETE` | Old PostgreSQL-OLTP query pack has no target consumer; target control-plane health belongs to the concrete control probe/exporter owner. |
| `scripts/cdc/failure_injection.py` | `REWRITE` | Real target services and alert identities. |
| `scripts/ci/validate_stage6_configuration.py` | `REPLACE` | Target observability contract validator and acceptance probe. |
| `tests/test_clickhouse_phase7_ci_observability.py` and `tests/test_stage6_contracts.py` | `REWRITE` | Target chain tests; preserve actionable runbook and failure-transition assertions. |

## 6. Acceptance requirements for L2

L2 is not complete until all of the following are present as raw evidence under `data/stage-l-evidence/L2/<run-id>/`:

1. Prometheus configuration parses and every configured target exists in the Compose/exporter inventory.
2. Every required target is `UP` in a healthy bounded stack. An unimplemented target may not remain unspecified; it must either be implemented and gated or removed from the target contract before acceptance.
3. Target alerts can be forced to `FIRING` and then `RESOLVED` using real service/metric failpoints, without NiFi/PostgreSQL source assumptions.
4. Grafana dashboard JSON parses, datasources exist, target queries return data, and no panel references a removed metric.
5. Alert/runbook links resolve to target runbooks and contain no secret values.
6. The full clean Stage V E2E V0–V10 passes after the observability changes.
