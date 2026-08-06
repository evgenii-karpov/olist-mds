# Olist MDS GCP and BigQuery Dual-Contour Implementation Plan

This package is the consolidated implementation plan for adding a permanent GCP/BigQuery contour to [`evgenii-karpov/olist-mds`](https://github.com/evgenii-karpov/olist-mds) while preserving the existing local Polaris/MinIO/ClickHouse contour as a first-class target.

**Plan revision date:** 2026-08-07
**Repository baseline:** [`1fe78c4b1d827e2d17fc604be39b6c227a2488ce`](https://github.com/evgenii-karpov/olist-mds/commit/1fe78c4b1d827e2d17fc604be39b6c227a2488ce)
**Decision status:** Architecture interview complete; no unresolved design choice is required before WP0.
**Execution model:** The local and GCP contours are permanent, but only one contour is operated at a time.

## Package map

| Document | Purpose |
|---|---|
| [`00-program-overview.md`](00-program-overview.md) | Scope, target state, invariants, stage graph, completion criteria |
| [`01-decision-register.md`](01-decision-register.md) | Consolidated record of the accepted architecture decisions |
| [`02-repository-baseline-and-required-refactors.md`](02-repository-baseline-and-required-refactors.md) | Current repository facts and mandatory corrections before cloud rollout |
| [`03-target-architecture-and-runtime-isolation.md`](03-target-architecture-and-runtime-isolation.md) | Local/GCP flows, Compose profiles, runtime boundaries |
| [`04-gcp-infrastructure-iam-and-cost-controls.md`](04-gcp-infrastructure-iam-and-cost-controls.md) | Terraform, buckets, datasets, IAM, authentication, zero-spend controls |
| [`05-cdc-ordering-and-serving-boundary.md`](05-cdc-ordering-and-serving-boundary.md) | Canonical CDC ordering, transaction-complete boundaries, retry contracts |
| [`06-spark-iceberg-and-vertical-slice.md`](06-spark-iceberg-and-vertical-slice.md) | Spark backend abstraction, Iceberg ownership, blocking compatibility slice |
| [`07-bigquery-gold-and-publication.md`](07-bigquery-gold-and-publication.md) | Incremental Gold design, history/current tables, atomic publication |
| [`08-orchestration-cli-and-operations.md`](08-orchestration-cli-and-operations.md) | `lab.py`, Airflow, migrations, streaming ownership, destructive commands |
| [`09-testing-parity-observability-and-ci.md`](09-testing-parity-observability-and-ci.md) | Testing, parity, CI, observability, cost evidence |
| [`stages/`](stages/) | Executable work packages WP0–WP12 |
| [`appendices/`](appendices/) | Commands, inventories, acceptance matrix, risks, references |

## Reading order

1. Read the overview and decision register.
2. Review the repository corrections before changing Compose or cloud code.
3. Execute WP0–WP5 in order.
4. Stop after WP5 and make a manual go/no-go decision based on evidence.
5. Continue WP6–WP12 only after a go or go-with-constraints outcome.

## Normative precedence

When two documents appear to conflict, apply this order:

1. `01-decision-register.md`;
2. the relevant architecture document (`03`–`09`);
3. the work-package file;
4. examples and appendices.

The earlier candidate-snapshot/pointer architecture is explicitly superseded. BigQuery publication now uses per-model incremental history/delta tables plus materialized current-state tables updated in one transaction.
