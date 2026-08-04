# Detailed Stage F0 plan: freeze the baseline from `main`

- **Status**: `COMPLETE` (completed 2026-08-03; report: [docs/reports/mysql-spark-iceberg-f0-baseline.md](../../../reports/mysql-spark-iceberg-f0-baseline.md)).
- **Candidate commit**: `e113c552cca990636f426b827456a77ddc9d594b`.
- **Baseline commit**: `1400d08345ad81a0121f0ee85ee9ae81cd575a73` (the last `main` commit recorded when planning began).
- **Fixture**: `tests/fixtures/olist_small/olist_small.zip`.
- **Fixture SHA-256**: `5cf2ff7a104cae75d8a56cf8c6e00959894154a8d55aed2ddf0e3fa133a13976`.
- **Oracle SHA-256**: `629c36144e64fc9910b822e0907f8a1592b3ef6eb83e438d946267fa3d5b597b`.

---

## 1. Decision

The legacy stack is run once from a separate Git worktree at the exact commit SHA. Its canonical result is stored in the repository as an immutable oracle. Stage L can then remove legacy files from the working branch, while Stage F1 runs only the candidate and compares it with the oracle.

This is faster and simpler than rebuilding both architectures for every final test. Git history remains the reproducibility source but is not part of the normal F1 path.

The existing `tests/fixtures/postgresql_oracle/postgres_batch_oracle.json` cannot be accepted automatically: it contains legacy-specific surrogate/date keys, does not cover the eight current-state entities under one contract, and lacks sufficient provenance metadata.

---

## 2. F0 artifacts

Added:

- `tests/fixtures/final_parity/main-1400d08.json` — canonical rows and aggregates;
- `tests/fixtures/final_parity/main-1400d08.metadata.json` — provenance and checksums;
- `docs/reports/mysql-spark-iceberg-f0-baseline.md` — human-readable one-shot run report.

Metadata contains:

- full baseline commit SHA;
- fixture path and SHA-256;
- Docker image and tool versions;
- UTC start/end timestamps;
- table, grain, column, and row-count inventory;
- SHA-256 for every canonical row set;
- canonicalization rules version;
- final export status.

---

## 3. Execution order

1. Verify that E/V is re-accepted and the candidate commit is recorded.
2. Verify the full baseline SHA and fixture SHA-256; do not use symbolic `main` afterward.
3. Create a temporary worktree outside the candidate tree at commit `1400d083...`.
4. Assign a unique `COMPOSE_PROJECT_NAME`, separate volumes, and free ports.
5. Start the legacy stack in order, load the unchanged fixture, and wait for the batch/dbt path to finish.
6. Export the eight source entities, `fact_order_items`, `mart_daily_revenue`, and `mart_monthly_arpu`.
7. Apply the canonicalization rules from the final-parity contract.
8. Check grain uniqueness, absence of disallowed columns, and consistency of row counts/hash/rows.
9. Write the oracle, metadata, and report; read them again with an independent validator.
10. Run `docker compose down -v` only for the F0 project and remove the temporary worktree.
11. Review the oracle diff: secrets, absolute paths, unstable timestamps, and runtime IDs are forbidden.
12. Record the oracle in a separate reviewable commit before Stage L begins.

---

## 4. Comparison surface

| Class | Datasets | Grain |
| --- | --- | --- |
| Current state | `customers`, `orders`, `order_items`, `order_payments`, `order_reviews`, `products`, `sellers`, `product_category_translation` | natural keys from the final-parity contract |
| Fact | `fact_order_items` | `order_id, order_item_id` |
| Marts | `mart_daily_revenue`, `mart_monthly_arpu` | `order_purchase_date`; `order_month` |

Only explicitly listed business columns are compared. Technical batch IDs, surrogate/date keys, load timestamps, binlog coordinates, and engine-specific metadata are excluded from the oracle.

---

## 5. Baseline protection

- The oracle is never regenerated automatically in PR or push CI.
- Changing the oracle requires a manual F0 run with the same baseline commit or a separate architectural decision to change the baseline.
- Changing a checksum without the corresponding canonical rows is forbidden.
- When F1 differs, fix the candidate; do not fit the oracle to the result.
- Git LFS is not required while the JSON size permits ordinary code review.

---

## 6. Completion criteria

F0 is complete when the oracle and metadata pass independent validation, the report has `PASS`, cleanup is complete, and review confirms the absence of unstable/technical fields. After that, the legacy runtime is no longer an F1 precondition and Stage L is permitted.

---

## 7. Related documents

- [Final parity contract](../contracts/final-parity.md)
- [Stage F1 plan](../active/stage-f1-final-parity.md)
- [Coordination plan](../active/serving-cutover.md)
