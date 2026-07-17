# Handoff: Stage 6 — local hardening, observability, and recovery

## Mission

Implement Phase 6 without changing Phase 5 event ordering, immutable transform
membership, parity gate, or isolated batch/realtime schemas.

## Verified upstream contract

- Transform runs capture exact `LOADED` manifest membership and advance only
  after dbt success plus freshness recording.
- Current state/history use only source LSN, transaction order, partition, and
  offset for ordering.
- Hard deletes disappear from current facts/marts and remain in history.
- Hourly quality and Asset-triggered transform DAGs are separate finite jobs.
- Realtime publication is reversible and requires a recorded parity PASS.
- Batch/realtime builds use named selectors; only `models/parity` may reference
  both transformation groups.
- The operational `batch` selector includes Elementary package models and must
  continue to bootstrap its hooks and `edr report` on a clean warehouse.

## Required boundary

Add security, dashboards, alerts, logs, failure injection, benchmark evidence,
and recovery runbooks. Do not move continuous service supervision into Airflow
or claim the 5-minute SLO until reference and burst workloads are measured.

## Implementation outcome on 2026-07-17

Delivered:

- six provisioned Grafana views covering SLO/error budget, source/WAL,
  Kafka/Connect, NiFi/files, Airflow/dbt/warehouse, and capacity/logs;
- Loki 3.6.5 plus Alloy 1.16.1 Docker log discovery with seven-day retention
  and only `environment`/`service` labels;
- PostgreSQL, Airflow StatsD, node, cAdvisor, pipeline, Kafka, Connect, NiFi,
  and MinIO scrape definitions;
- 17 Phase 6 policy alerts plus four recording rules, all linked to runbooks;
- bounded service fault-injection and reference/burst/soak benchmark helpers;
- recovery runbooks for restart, replay, warehouse/landing rebuild, resnapshot,
  schema migration, and alert testing.

Verified in this change:

- Stage 6 static validator and contract tests pass;
- Compose configuration for `realtime-core,observability,logs` passes;
- Prometheus config and both rule files pass `promtool`;
- Loki config passes the pinned image verifier;
- Alloy config passes canonical formatting and starts with Loki;
- Grafana runtime logs confirm both datasources and dashboard provisioning;
- Loki `/ready` returns 200 and a query returns an Alloy log stream carrying
  `environment=local` and `service=olist-alloy`.

Open gates accepted by the 2026-07-17 plan amendment:

- coordinated Kafka TLS/auth plus NiFi managed metrics authorization;
- controlled `firing -> resolved` evidence for every required alert;
- Connect/WAL and NiFi/backlog recovery drills plus immutable warehouse rebuild;
- 30-minute reference, 10-minute burst, and four-hour soak benchmark reports.

The five-minute SLO and complete Phase 6 exit criterion are not claimed.
