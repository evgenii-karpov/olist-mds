# Stage F0: Baseline Freeze Validation & Evidence Report

## 1. Summary & Status

- **Status**: `PASS`
- **Execution Date**: 2026-08-03
- **Candidate Commit**: `e113c552cca990636f426b827456a77ddc9d594b`
- **Frozen Baseline SHA**: `1400d08345ad81a0121f0ee85ee9ae81cd575a73`
- **Fixture Archive**: `tests/fixtures/olist_small/olist_small.zip`
- **Fixture SHA-256**: `5cf2ff7a104cae75d8a56cf8c6e00959894154a8d55aed2ddf0e3fa133a13976`
- **Oracle Artifact**: `tests/fixtures/final_parity/main-1400d08.json`
- **Oracle SHA-256**: `629c36144e64fc9910b822e0907f8a1592b3ef6eb83e438d946267fa3d5b597b`
- **Metadata Artifact**: `tests/fixtures/final_parity/main-1400d08.metadata.json`

Stage F0 has completed successfully. A single-run legacy baseline export was executed from a temporary worktree detached at commit `1400d08345ad81a0121f0ee85ee9ae81cd575a73`. The exported canonical oracle covers all 11 target relations with zero duplicate grain keys, valid canonicalization, and deterministic SHA-256 hashes. Independent validation passed.

---

## 2. Relation Inventory & Hashes

| Relation | Schema | Grain | Row Count | Duplicate Grain Count | Aggregate Hash (SHA-256) |
| --- | --- | --- | --- | --- | --- |
| `customers` | `public` | `customer_id` | 8 | 0 | `e52cc9e869649f77da6363d6690e837ef6671fe130585e386f8ee5d0ae528643` |
| `orders` | `public` | `order_id` | 12 | 0 | `878bbb9f417c0b9968b313a092955cd0db3360fd4d891adc7025d0f5f8c620b7` |
| `order_items` | `public` | `order_id, order_item_id` | 16 | 0 | `c6e854dae8d93d9f4c73039cffd0c7a574d2dfa51514079a68aa11d2fcbccec1` |
| `order_payments` | `public` | `order_id, payment_sequential` | 14 | 0 | `a122c793fd89d49e168e823dd345162f957936cc6f927ce49ad1755e338a1551` |
| `order_reviews` | `public` | `review_id, order_id` | 12 | 0 | `173ab20b61c14fc568bcb0e46ddcc90de41c861e49bc6e9bc68cc93f98527bb4` |
| `products` | `public` | `product_id` | 8 | 0 | `9636250f6eed982d0e7f72bcd29af613052d7a7f115a7af1bafeef42483eb675` |
| `sellers` | `public` | `seller_id` | 4 | 0 | `42156d82102cbf4ee6829308a8af063ca1d346a2e4d36bb3772e566bf0039c48` |
| `product_category_translation` | `public` | `product_category_name` | 5 | 0 | `c2d3098813fdabd96905444ec175371e65a1484aa94277d892cf3f63addf7dae` |
| `fact_order_items` | `core` | `order_id, order_item_id` | 16 | 0 | `54e1b46cfa93c3cacc47d2bdf4e3e0faee84e11ee9b3d6017dd398f3835d8b9b` |
| `mart_daily_revenue` | `marts` | `order_purchase_date` | 12 | 0 | `85c4ac1987b6ce0ee07be56aba78080cd6e79b4e27325928e6693cb2d423c187` |
| `mart_monthly_arpu` | `marts` | `order_month` | 6 | 0 | `12f6c72319748d18dcfccfbedbd3176d64d2cbd41a1fd433ce3a6afb7aea4fa3` |

---

## 3. Verification & Safety Checks

- **Independent Validator**: Executed `python scripts/parity/validate_f0_oracle.py`. Status: `PASS`.
- **Grain Uniqueness**: All 11 relations have `duplicate_grain_count = 0`.
- **Content Integrity**: All dates, timestamps, decimals, booleans, strings, and null representations adhere strictly to `final-parity.md` canonicalization rules.
- **Sanitization**: Verified zero internal passwords, local filesystem paths, or dynamic runtime session IDs inside oracle and metadata artifacts.
- **Clean Teardown**: Temporary Compose stack (`COMPOSE_PROJECT_NAME=olist-f0-baseline`) was stopped and purged with `docker compose down -v`. Temporary worktree directory was pruned.

---

## 4. Next Steps

With Stage F0 baseline frozen and verified, Stage L (Legacy Removal & CI Cutover) can proceed safely without requiring legacy PostgreSQL or NiFi runtimes for candidate parity testing.
