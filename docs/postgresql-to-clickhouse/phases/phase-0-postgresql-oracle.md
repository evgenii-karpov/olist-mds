# Phase 0: PostgreSQL oracle

Status: completed on 2026-07-23.

## Delivered contract

- The unchanged PostgreSQL warehouse is captured by two deterministic fixtures:
  the `olist_small` batch fixture and the synthetic Stage 5 initial-parity
  fixture. Together they cover 15 migration-relevant analytical relations.
- Every one of the 13 terminal project models has a dbt unit test. The two
  terminal snapshots remain covered by the batch rerun and manifest contracts.
- Focused unit tests freeze latest-source selection, correction precedence,
  proportional payment allocation, SCD2 windows, CDC ordering, translation
  history, related-order propagation, and hard-delete behavior.
- The canonical manifest format preserves case and whitespace, distinguishes
  null from empty string, fixes decimal scale, renders timestamps in UTC with
  six fractional digits, and hashes sorted canonical JSON with SHA-256.
- Manifests contain relation metadata, semantic column types, declared grain,
  complete grain-key sets, row hashes, aggregate hashes, duplicate counts,
  null counts, temporal bounds, configured measures/distinct counts, and
  snapshot business-version summaries. They do not contain source rows.
- PostgreSQL snapshot runtime fields (`dbt_scd_id`, `dbt_updated_at`,
  `dbt_valid_from`, and `dbt_valid_to`) are excluded. Snapshot comparison uses
  business keys and correction-effective versions.

## dbt inventory

The Phase 0 inventory was recorded with:

```powershell
uv run dbt ls --resource-type model snapshot test --output json
```

Before Phase 0 there were 64 project models, two snapshots, 274 data tests,
four unit tests, 13 terminal models, and two terminal snapshots (15 terminal
relations). Phase 0 retains all relation/data-test counts and raises unit tests
to 21. The exact terminal names are committed in
`tests/fixtures/postgresql_oracle/dbt_inventory.json`.

## Verification evidence

Passed:

- `check_fixture_pipeline_idempotency.py`: two clean
  `olist_modern_data_stack_local` DAG runs completed successfully; the replay
  retained 16 fact rows, 12 daily mart rows, six monthly mart rows, and stable
  raw/analytical fingerprints;
- `check_stage5_cdc_integration.py`: initial transform, ordered updates,
  hard delete, publication round-trip, parity mutation detection, and parity
  restoration all passed;
- the Stage 5 proof passed twice against independently created disposable
  PostgreSQL databases;
- all 21 dbt unit tests passed;
- the canonical exporter unit tests passed;
- Ruff, Ruff formatting, and targeted Pyright checks passed;
- dbt parse accepted all new unit-test definitions.

The committed compact artifacts are:

- `postgres_batch_oracle.json` — SHA-256
  `4cea33bb0974dcf7e7992fa846283e9a8b3b8320d755b06010be5b68015a36b7`;
- `postgres_stage5_oracle.json` — SHA-256
  `2384273bb8840706321ab8a8b70231322ff62136fe4dbcf20866e207c064dff5`.

Each artifact was regenerated independently and matched byte-for-byte.

## Regeneration commands

With the small batch fixture built in the local PostgreSQL warehouse:

```powershell
uv run python scripts/parity/export_postgres_oracle.py `
  --output tests/fixtures/postgresql_oracle/postgres_batch_oracle.json
```

For the disposable synthetic realtime fixture:

```powershell
uv run python scripts/ci/check_stage5_cdc_integration.py `
  --oracle-output tests/fixtures/postgresql_oracle/postgres_stage5_oracle.json
```

The second command exports at the restored initial-parity PASS boundary, then
continues through ordered updates and the hard-delete proof before dropping the
disposable database.

## Phase boundary

No analytical SQL was ported and no ClickHouse dependency or infrastructure
was introduced. `local_pg` remains the default oracle. Phase 1 must consume
these tests and manifests as immutable compatibility evidence.
