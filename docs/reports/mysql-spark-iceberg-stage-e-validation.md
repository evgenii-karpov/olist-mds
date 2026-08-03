# Stage E Validation Report: Serving Integration

## 1. Executive Summary

| Field | Value |
| --- | --- |
| Stage | Stage E — Serving Integration |
| Status | **PASS** |
| Completed Date | 2026-08-02 |
| Target Architecture | MySQL 8.4 → Debezium → Kafka → Spark Structured Streaming → Iceberg → ClickHouse → dbt Gold |
| Control Schema | PostgreSQL `olist_control.serving` |
| Verification Scope | Stage E component & contract validation |

---

## 2. Completed Scope & Key Deliverables

1. **J2 Contract Repair (E0)**:
   - 10 streaming queries configured in `spark-silver` (`bronze_to_silver_<entity>`, `capture_avro_schemas`, `normalize_mysql_transactions`).
   - Idempotent commit protocol: `changes` → `normalization_errors/schema_violations` → `current` → `silver_progress`.
   - Driver-local table lock coordination via `IcebergCommitCoordinator`.

2. **PostgreSQL Control Ledger (E1)**:
   - Migration `005_create_serving_control_tables.sql` added sequence `serving.sync_run_seq`, tables `serving.sync_runs`, `serving.sync_entity_results`, and `serving.runtime_state`.
   - Python package `scripts/serving` created with control repository, boundary planner, ClickHouse materializer, dbt runner, Airflow client, and metrics exporter.

3. **ClickHouse Candidate Isolation (E2)**:
   - `004_create_current_version_tables.sql` updated to `PARTITION BY sync_run_seq` and `ORDER BY (sync_run_seq, <primary key>)`.
   - Isolation regression test `002_unpublished_current_isolation.sql` added.

4. **dbt Gold Candidate Integration (E3)**:
   - Created `selectors.yml` with selector `serving_candidate` for Gold models.

5. **Airflow Serving Orchestration (E4)**:
   - Added DAGs `olist_lakehouse_serving_sync`, `olist_lakehouse_serving_quality`, `olist_iceberg_maintenance`, and `olist_clickhouse_rebuild`.

6. **Spark Operations & Rebuild (E5)**:
   - Config split into `streaming` and `maintenance` modes.
   - `LakehouseOpsMain` implemented in Scala.

7. **CLI & Observability (E6)**:
   - CLI commands `sync-serving`, `rebuild-serving --yes`, and `run-maintenance` connected in `local_lab.py`.
   - Prometheus alert rules and Grafana dashboard added.
   - Runbooks added to `docs/runbooks/`.

---

## 3. Test & Verification Evidence

- `tests/cdc_contracts/`: 51 passed.
- `tests/serving/`: 6 passed.
- Contract synchronization across normative files completed.

---

## 4. Conclusion

Stage E (Serving Integration) has been successfully implemented and verified in accordance with `docs/plans/lakehouse/completed/stage-e-serving-integration.md`.

The subsequent clean Stage V run `stage_v_clean_e113c55` on commit
`e113c552cca990636f426b827456a77ddc9d594b` revalidated the serving entry gate
and the complete Iceberg → ClickHouse → dbt Gold path. Its raw evidence is
stored under `data/stage-v-evidence/stage_v_clean_e113c55/`.
