# Phase 6: Local hardening, observability, and recovery

Status: observability implementation delivered on 2026-07-17; security and
runtime acceptance gates remain open under the approved plan amendment.

## Delivered contract

- Grafana provisions six focused dashboards instead of one mixed component
  board. The views cover the complete local dashboard list from section 11.2.
- Prometheus scrapes the CDC components, both PostgreSQL databases, Airflow
  StatsD, host/container capacity, MinIO, NiFi, and the warehouse audit exporter.
- Pipeline metrics now include ingest/transform success and duration, mart
  latency/build time, file count/size distribution, DLQ, and quarantine state.
- Recording rules expose p95 commit-to-mart latency, ten-minute error-budget burn,
  Kafka lag, and NiFi queue utilization. Seventeen policy alerts cover the
  required fault classes and link to committed runbooks.
- Loki retains seven days of local logs. Alloy discovers Docker logs and uses
  only stable environment/service labels; event/run IDs stay in bodies.
- Fault injection stops and restores only an allowlisted service and records
  alert fire/resolution evidence under ignored `data/reports/`.
- The benchmark helper encodes the approved 5/s reference, 20/s burst, and
  four-hour soak profiles and produces machine-readable latency/capacity data.
Phase 5 manifest membership, ordering, delete, parity, publication, and selector
contracts were not changed.

## Verification evidence

Passed:

- `uv run python scripts/ci/validate_stage6_configuration.py`;
- four Stage 6 contract unit tests;
- targeted Ruff and formatting checks;
- `docker compose --profile realtime-core --profile observability --profile logs config --quiet`;
- Prometheus 3.12 `promtool check config` (20 alert rules, four recording rules);
- Loki 3.6.5 `-verify-config=true`;
- Alloy 1.16.1 `fmt --test` after canonical formatting;
- Prometheus, Alertmanager, StatsD exporter, and Grafana started together;
  Grafana logs confirmed Loki/Prometheus datasource insertion and completed
  file-dashboard provisioning;
- Loki/Alloy Compose smoke: both services started, Loki became ready, and a
  Loki query returned the Alloy stream with low-cardinality labels.

The first log smoke used host port 13100 because port 3100 was reserved on the
workstation. This changes no container endpoint or committed default.

## Open evidence

- Kafka TLS/authentication and separate NiFi metrics authorization were not a
  low-risk isolated change. They are deferred as one coordinated migration.
- The fault helper has not yet been run for every alert against the complete
  continuous stack, so no comprehensive fire-and-resolve matrix is claimed.
- Connect/WAL recovery, NiFi backlog drain, and a clean warehouse rebuild still
  require disposable full-stack drills.
- Reference, burst, and soak benchmark profiles have not been executed. The
  p95 five-minute SLO remains unproven.

## Commands

```powershell
uv run python scripts/ci/validate_stage6_configuration.py
uv run python scripts/cdc/failure_injection.py --scenario connect
uv run python scripts/cdc/benchmark_local.py --profile reference
```

Add `--execute` to the last two commands only against a disposable full stack.
