# J1 runbook: finalizing MySQL → Kafka → Spark/Iceberg Wave 1

- **Status**: Completed / Frozen
- **Purpose**: Historical execution and acceptance runbook for Wave 1/J1
- **Active instruction**: No
- **Evidence**: [docs/reports/mysql-spark-iceberg-wave1-j1-validation.md](../../../reports/mysql-spark-iceberg-wave1-j1-validation.md)
- **Implementation commits**: `6088ebe3dcaee0345bedfb0524caa4aa96842e50`, `b1cd1ab1b6f59166aa6dfad60bc02419bd0bfcf8`

---

Primary architecture source:
[`mysql-spark-iceberg-lakehouse-migration.md`](../../mysql-spark-iceberg-lakehouse-migration.md).
This document describes the historical execution order for J1 integration and is archival material.

## 1. J1 mission

Complete **J1 only**:

1. Record the component changes already written for streams A–D.
2. Merge shared dependencies once and update `uv.lock`.
3. Build the new platform runtime in `compose.yaml`.
4. Move `scripts/cdc/local_lab.py` to the Wave 1 lifecycle.
5. Start a clean disposable Docker consistency domain.
6. Check MySQL, Kafka, Connect, Apicurio, MinIO, Polaris, Spark/Iceberg, and ClickHouse with real component smoke tests.
7. Obtain all real writer schemas from the running Debezium/Apicurio stack, preserve the evidence bundle, and release contract version `v2`.
8. Record the shared Spark normalization API for future Wave 2 agents.
9. Preserve a secret-free validation report and create focused commits.

## 2. Starting state

P0 was recorded in commit `685cd6f docs: add mysql spark iceberg migration plans`.

Component code A–D (path ownership):
- A: `infra/mysql/**`, `scripts/simulation/**`, `tests/mysql/**`
- B: `streaming/kafka/**`, `streaming/connect/**`, `streaming/schemas/**`, `tests/cdc_contracts/**`
- C: `docker/spark/**`, `infra/polaris/**`, `streaming/spark/platform/**`, `tests/lakehouse_platform/**`
- D: `infra/clickhouse/lakehouse/**`, `dbt/olist_clickhouse/**`, `tests/dbt_clickhouse/**`

## 3. Non-negotiable rules

1. All persisted services belong to one disposable consistency domain.
2. Loss or divergence of an authoritative volume requires a full `reset --yes`.
3. Passwords, tokens, and secrets are passed strictly through `*_FILE`.
4. Warehouse data is accessed strictly through credentials vended by Polaris.

## 4. Required deliverables

1. Updated `pyproject.toml` and `uv.lock`.
2. Valid `compose.yaml` with `platform`, `streaming`, `serving`, and `observability` profiles.
3. Wave 1 lifecycle implementation in `scripts/cdc/local_lab.py`.
4. Isolated Polaris credential projections.
5. Applied Iceberg migration `0001_initial_lakehouse`.
6. Created ClickHouse `DataLakeCatalog` named `lakehouse`.
7. Writer-schema evidence repository and contract `v2`.
8. Validation report `docs/reports/mysql-spark-iceberg-wave1-j1-validation.md`.

## 5. J1 completion result

Wave 1 and J1 were completed successfully and recorded in [docs/reports/mysql-spark-iceberg-wave1-j1-validation.md](../../../reports/mysql-spark-iceberg-wave1-j1-validation.md).
