# CDC schema migration

Compatible nullable additions follow expand/backfill/contract:

1. Add nullable warehouse columns and compatible readers first.
2. Verify the Avro change with
   `uv run python scripts/ci/check_avro_schema_compatibility.py`.
3. Apply the source change and verify registry `BACKWARD_TRANSITIVE` acceptance.
4. Observe NiFi, quarantine/DLQ, raw loading, and dbt models before backfilling.
5. Backfill or rebuild affected keys through immutable manifest membership.
6. Contract old fields only in a later reviewed release after all readers move.

A breaking schema must fail CI or registry compatibility. Never disable the
global rule or set `errors.tolerance=all` to bypass a migration failure.
