# Phase 6: Local hardening, observability, and recovery

Status: local observability, parity, and operational-drill evidence are
implemented and verified as of 2026-07-26. AWS CDC remains Phase 7 work. The
formal benchmark/SLO evidence and the deferred local security migration remain
separate gates.

## Delivered contract

- Grafana provisions six focused dashboards instead of one mixed component
  board. The views cover the complete local dashboard list from section 11.2.
- Prometheus scrapes the CDC components, OLTP/control PostgreSQL, ClickHouse,
  Airflow StatsD, host/container capacity, MinIO, NiFi, and the warehouse audit
  exporter.
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
- The dedicated manual batch-to-realtime parity workflow and bounded
  report runner now exercise the same small archive through the real batch DAG
  and the Debezium/Kafka/NiFi/MinIO/Airflow realtime path. Its exact claim is
  initial-snapshot business parity for the eight captured source projections,
  item-grain fact, and both consumer marts; it makes no latency-SLO or SCD2
  history-equality claim.
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
  Loki query returned the Alloy stream with low-cardinality labels;
- the manual `Batch and CDC parity integration` workflow completed cleanly and
  uploaded its `batch-cdc-parity-report` artifact;
- the manual `CDC operational drills` workflow completed cleanly and uploaded
  `stage6-operational-drill` evidence for bounded alert fire/recovery.

The first log smoke used host port 13100 because port 3100 was reserved on the
workstation. This changes no container endpoint or committed default.

## AWS handoff notes

- The independent AWS implementation must not depend on local service endpoints,
  local volumes, local Kafka listener assumptions, or local NiFi authorization.
- AWS must provide its own Terraform state, secrets, IAM boundaries,
  observability wiring, and validation reports.
- Do not claim the five-minute p95 SLO until the reference, burst, and soak
  benchmark profiles have passing evidence.

## Commands

```powershell
uv run python scripts/ci/validate_stage6_configuration.py
uv run python scripts/cdc/failure_injection.py --scenario connect
uv run python scripts/cdc/benchmark_local.py --profile reference
```

Add `--execute` to the last two commands only against a disposable full stack.
The operational-drill workflow runs `failure_injection.py --execute` and stores
the report as a GitHub artifact.
