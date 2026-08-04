# Technical Contract: Final Parity (F0/F1)

- **Status**: Active normative contract.
- **Purpose**: define creation of the frozen pre-cleanup baseline at F0 and the final candidate-only comparison at F1.
- **Main invariant**: after F0 acceptance, the final run does not depend on retired runtime being present in the current tree.

---

## 1. Stage separation

### F0 — one-shot baseline export before cleanup

Legacy runs from a temporary worktree at the exact commit `1400d08345ad81a0121f0ee85ee9ae81cd575a73`. Versioned oracle and metadata are built from the result. The symbolic `main` branch is not used after the SHA is verified.

### F1 — final test after cleanup

The cleaned candidate runs with the same fixture, exports the same data surface and is compared row by row with the frozen oracle. F1 does not create a worktree, start legacy or update the oracle.

---

## 2. Baseline artifacts

Normative paths:

- `tests/fixtures/final_parity/main-1400d08.json`;
- `tests/fixtures/final_parity/main-1400d08.metadata.json`.

Metadata records the full baseline SHA, fixture SHA-256, canonicalization version, image/tool versions, relation manifest, grains, business columns, row counts and SHA-256 hashes of canonical rows.

The oracle is an immutable F1 input. Updating it requires another controlled F0 and review; automatic regeneration in CI is forbidden.

---

## 3. Comparison surface

### 3.1 Current state

| Entity | Grain |
| --- | --- |
| `customers` | `customer_id` |
| `orders` | `order_id` |
| `order_items` | `order_id, order_item_id` |
| `order_payments` | `order_id, payment_sequential` |
| `order_reviews` | `review_id, order_id` |
| `products` | `product_id` |
| `sellers` | `seller_id` |
| `product_category_translation` | `product_category_name` |

The baseline is frozen in immutable F0 fixtures; the candidate comes from `silver.<entity>_current` with `is_deleted = false`. Compare all explicitly described business columns, but not transport/load metadata.

### 3.2 Fact

`fact_order_items`, grain `order_id, order_item_id`.

Business columns: `customer_id`, `customer_unique_id`, `product_id`, `seller_id`, `order_status`, `order_purchase_timestamp`, `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`, `order_estimated_delivery_date`, `shipping_limit_date`, `price`, `freight_value`, `gross_item_amount`, `allocated_payment_value`, `delivery_days`, `delivery_delay_days`, `is_delivered_late`.

Surrogate keys, date keys, batch IDs and load timestamps are excluded.

### 3.3 Marts

1. `mart_daily_revenue`, grain `order_purchase_date`:
   `order_purchase_date`, `gross_revenue`, `allocated_payment_revenue`, `product_revenue`, `freight_revenue`, `orders_count`, `customers_count`, `items_count`, `average_order_value`, `average_paid_order_value`, `average_delivery_days`, `late_deliveries_count`.
2. `mart_monthly_arpu`, grain `order_month`:
   `order_month`, `active_customers`, `total_revenue`, `arpu`, `orders_count`, `orders_per_customer`, `average_order_value`, `repeat_customer_rate`.

---

## 4. Canonicalization

Only the following transformations are allowed:

- timestamp → UTC ISO-8601 with six fractional digits;
- decimal → contract-defined precision without additional rounding;
- boolean → `true`/`false`;
- strings and `null` are preserved without trim/case/default substitutions;
- JSON object keys are sorted;
- relation rows are sorted by grain.

The rules version and manifest must match between the F0 baseline export and the F1 candidate exporter. Do not exclude divergent rows or accept a result based only on a checksum.

---

## 5. F1 runner contract

Target interface:

```text
python scripts/cdc/local_lab.py final-parity \
  --run-id <run-id> \
  --oracle tests/fixtures/final_parity/main-1400d08.json \
  --confirm-destructive \
  --timeout 5400
```

The runner must:

1. verify candidate SHA, fixture/oracle/metadata checksums and schema;
2. create a unique candidate Compose project;
3. run clean seed → stream catch-up → serving sync → dbt build;
4. export the candidate using the baseline manifest;
5. compare the grain, keys and values of every business column;
6. save the raw machine-readable diff before generating the summary;
7. compute the exit code and `PASS/FAIL` only from the diff;
8. clean up only its own resources on every outcome.

---

## 6. Acceptance

`PASS` requires all of the following:

1. exit code `0`;
2. all relations are present and the grain is unique;
3. missing keys: `0`;
4. extra keys: `0`;
5. business-column mismatches: `0`;
6. provenance checksums match;
7. the report agrees with the raw diff.

On `FAIL`, fix the candidate and repeat F1 with the same oracle. Regenerating the oracle to obtain `PASS` is forbidden.

---

## 7. CI policy

F1 runs only as the manual `final-parity` job in `.github/workflows/lakehouse-acceptance.yml`. It is not part of normal PR CI. F0 is not a regular GitHub workflow.

---

## 8. Related documents

- [F0 plan](../completed/stage-f0-baseline-freeze.md)
- [F1 plan](../active/stage-f1-final-parity.md)
- [Validation and CI contract](validation-and-ci.md)
- [Coordination plan](../active/serving-cutover.md)
