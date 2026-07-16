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

## Required boundary

Add security, dashboards, alerts, logs, failure injection, benchmark evidence,
and recovery runbooks. Do not move continuous service supervision into Airflow
or claim the 5-minute SLO until reference and burst workloads are measured.
