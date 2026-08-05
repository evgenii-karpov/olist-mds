# Stage F1: Final Candidate-Only Parity

## 1. Decision and provenance

- **Status**: `PASS`
- **Execution date**: 2026-08-05
- **Candidate commit**: `400372a31dcd6cf8f37490f4bb79c93f382f2248`
- **F0 baseline commit**: `1400d08345ad81a0121f0ee85ee9ae81cd575a73`
- **Fixture**: `tests/fixtures/olist_small/olist_small.zip`
- **Fixture SHA-256**: `5cf2ff7a104cae75d8a56cf8c6e00959894154a8d55aed2ddf0e3fa133a13976`
- **F0 oracle**: `tests/fixtures/final_parity/main-1400d08.json`
- **Oracle SHA-256**: `629c36144e64fc9910b822e0907f8a1592b3ef6eb83e438d946267fa3d5b597b`
- **F1 run ID**: `f1-400372a`
- **Compose project**: `final-parity-f1-400372a`

The accepted run used only the cleaned candidate checkout. It did not create a
legacy worktree, start a legacy service, or regenerate/update the frozen F0
oracle.

## 2. Lifecycle evidence

All lifecycle steps completed successfully:

- candidate SHA, fixture, oracle, metadata and contract checks;
- scoped reset and fixture bootstrap;
- Kafka/Spark streaming startup and caught-up barrier;
- ClickHouse serving observer startup before the barrier;
- initial serving sync with `sync_run_seq=1`,
  `sync-00000000000000000001`, and successful dbt execution;
- serving validation and candidate manifest export;
- scoped Compose cleanup with status `PASS`.

The initial serving publication materialized 79 expected events. The dbt run
returned `success=true` with 75 dbt results. The final candidate export
contained all 11 required relations.

## 3. Parity result

The runner comparison and the independent repeat comparator both returned
`PASS`:

- missing keys: `0`;
- extra keys: `0`;
- business-column mismatches: `0`;
- duplicate grains: `0`;
- aggregate-hash mismatches: `0`;
- metrics mismatches: `0`.

| Relation | Oracle rows | Candidate rows | Status |
| --- | ---: | ---: | --- |
| `public.customers` | 8 | 8 | `PASS` |
| `public.orders` | 12 | 12 | `PASS` |
| `public.order_items` | 16 | 16 | `PASS` |
| `public.order_payments` | 14 | 14 | `PASS` |
| `public.order_reviews` | 12 | 12 | `PASS` |
| `public.products` | 8 | 8 | `PASS` |
| `public.sellers` | 4 | 4 | `PASS` |
| `public.product_category_translation` | 5 | 5 | `PASS` |
| `core.fact_order_items` | 16 | 16 | `PASS` |
| `marts.mart_daily_revenue` | 12 | 12 | `PASS` |
| `marts.mart_monthly_arpu` | 6 | 6 | `PASS` |

The independent F0 validator was rerun after the F1 result and returned
`PASS`; the oracle SHA remained unchanged.

Machine-readable evidence for the accepted run is stored under
`data/reports/final-parity/f1-400372a/`:

- `preflight.json`;
- `candidate-manifest.json`;
- `comparison.json`;
- `independent-comparison.json`;
- `report.md`;
- `junit.xml`.

## 4. Candidate fixes required to reach parity

The frozen F0 oracle was not changed. F1 initially exposed four candidate-side
issues, each fixed before the accepted run:

1. Start the ClickHouse serving observer before the catch-up barrier, because
   the barrier reads candidate audit/progress state.
2. Permit the contract-defined initial snapshot publication when no source
   transaction boundary exists yet.
3. Treat a successful initial snapshot sync with a null transaction boundary as
   an authoritative serving result.
4. Decode ClickHouse `FixedString` values returned as `bytes` before applying
   the shared canonical row hash. Without this, `customers` and `sellers`
   hashes represented values such as `b'RJ'` instead of `RJ`.

The final fix is covered by the canonicalization regression test in
`tests/stage_v/test_f0_parity_contracts.py`.

## 5. Acceptance commands

The accepted run used:

```text
uv run python scripts/cdc/local_lab.py final-parity \
  --run-id f1-400372a \
  --oracle tests/fixtures/final_parity/main-1400d08.json \
  --candidate-sha 400372a31dcd6cf8f37490f4bb79c93f382f2248 \
  --confirm-destructive \
  --timeout 5400
```

The repeat checks used the repository F0 validator and
`scripts.parity.compare_manifests` against the emitted candidate manifest.

Stage F1 is complete, and the final candidate-only parity gate is accepted.
