# CDC warehouse rebuild

Rebuild only the isolated realtime schemas from immutable normalized objects.
The batch schemas remain untouched.

1. Stop the CDC ingest and transform DAG schedules and wait for active runs.
2. Back up `cdc_audit` ledgers and record the current publication target.
3. Create a new disposable warehouse database or new isolated rebuild schemas.
   Do not truncate the active warehouse for the first validation attempt.
4. Apply `infra/postgres/001_create_schemas.sql`,
   `006_create_cdc_tables.sql`, and `007_create_cdc_transform_audit.sql`.
5. Discover every immutable normalized and coverage manifest from MinIO and run
   the loader in bounded date/table ranges. Verify ETags and tombstone coverage.
6. Run focused realtime dbt builds and full quality/parity checks.
7. Compare event counts, offset watermarks, current keys, history, facts, and
   marts with the active warehouse. Switch publication only after parity PASS.

If normalized objects are missing, use the landing rebuild runbook first.
