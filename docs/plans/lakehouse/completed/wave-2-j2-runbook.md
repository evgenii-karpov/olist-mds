# Wave 2 / J2 runbook: Scala data plane and integration

- **Status**: Completed / Frozen
- **Purpose**: Historical execution and acceptance runbook for Wave 2/J2
- **Active instruction**: No
- **Evidence**: [docs/reports/mysql-spark-iceberg-wave2-j2-validation.md](../../../reports/mysql-spark-iceberg-wave2-j2-validation.md)
- **Implementation commit**: `33a34de87250a9e34b320e9698764b23d6eaef37`

---

## 1. Wave 2 / J2 purpose and scope

Wave 2 implements a CDC streaming engine based on Spark Structured Streaming and Scala 2.13.17.
Main components:
- Bronze (`BronzeMain`) and Silver (`SilverMain`) streaming processors;
- automatic Avro schema archiving and resolution in Apicurio;
- shared normalization engine for eight business entities (`EntityBatchProcessor`);
- idempotent writers for the Iceberg `changes`, `current`, and `audit` tables;
- query supervisor with transient/fatal error handling;
- finite replay (`ReplayMain`) and one-shot geolocation reference loading (`GeolocationMain`).

Active normative data-plane contracts:
- [Spark Structured Streaming contract](../contracts/spark-streaming.md)
- [Iceberg data model contract](../contracts/iceberg-data-model.md)
- [Architecture and runtime contract](../contracts/architecture-and-runtime.md)

---

## 2. Historical S0–S8 package structure

1. **S0 — Baseline freeze**: validation of 26 Iceberg tables, migration checksums, and contract v2.
2. **S1 — Scala foundation**: creation of the single `streaming/spark/scala` build root (sbt 1.12.11, Scala 2.13.17), contract resource generation, and five main entrypoints.
3. **S2 — Bronze engine**: writing raw Kafka bytes to `bronze.mysql_cdc_records` with Confluent Avro framing validation and an anti-join on `event_id`.
4. **S3 — Schema archive**: implementation of `capture_avro_schemas` and the Apicurio-to-`bronze.avro_schemas` schema registrar.
5. **S4 — Common normalization engine**: an 11-step decoding pipeline, Avro FAILFAST validation, and deterministic column hash calculation.
6. **S5 — Eight entity modules**: validation rules for `customers`, `orders`, `order_items`, `order_payments`, `order_reviews`, `products`, `sellers`, and `product_category_translation`.
7. **S6 — Idempotent writers**: ordered `changes → errors → current → progress` commits with audit-table-level locking.
8. **S7 — Supervisor & Ops**: failure handler with exponential backoff, `ReplayMain`, `GeolocationMain`, and `LakehouseStatusMain`.
9. **S8 — Image & CLI**: build of the unified `olist-spark:4.1.3-iceberg1.11.0` image and integration of `start-streaming` and `wait-caught-up` into `local_lab.py`.

---

## 3. J2 acceptance criteria (J2.1 – J2.7)

- **J2.1 Static & Build gate**: successful execution of `sbt test package`, `uv lock --check`, `ruff`, `pyright`, and pytest tests.
- **J2.2 Clean Bootstrap & Initial Snapshot**: start from a clean domain and import the initial 79-row snapshot without data loss.
- **J2.3 CRUD / Transaction scenario**: process INSERT, UPDATE, and DELETE transaction scenarios with version validation in `current` and `changes`.
- **J2.4 Retry & Isolation drills**: verify resilience after commit failures and isolation of individual query failures.
- **J2.5 Replay proof**: confirm correct ReplayMain behavior (`rejected → applied`).
- **J2.6 dbt regression boundary**: confirm dbt-clickhouse tests pass (`PASS=78`) without reverse dependencies.
- **J2.7 Report**: final report with status `J2 ACCEPTANCE PASS`.

---

## 4. Acceptance result

All Wave 2 / J2 acceptance criteria were completed. The final acceptance report is recorded in [docs/reports/mysql-spark-iceberg-wave2-j2-validation.md](../../../reports/mysql-spark-iceberg-wave2-j2-validation.md).

**Status**: COMPLETE (`J2 ACCEPTANCE PASS`)
