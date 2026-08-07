# WP0–WP2 — Code review and post-fix acceptance

Date: 2026-08-07
Branch: `gcp-bigquery-dual-contour`

## Result

WP0–WP2 were reviewed after their initial closure. The review found and fixed
three functional defects. The fixes were rechecked with static analysis,
unit/integration tests, Docker Compose rendering, and a clean local CDC
acceptance run. The credential-free local acceptance is complete.

Cloud execution remains pending because no GCP credentials or project were
available.

## Findings and fixes

### WP0 — ordering and timestamps

- Spark latest-row selection ranked `last_is_snapshot = true` below live rows
  after applying descending ordering. The discriminator is now explicit:
  snapshot `0`, live `1`, ordered descending.
- Snapshot duplicate-coordinate identity now includes the topic, preventing
  unrelated topics from conflicting when they reuse Kafka partition/offset
  values.
- Source timestamp epoch conversion uses integer `timedelta` arithmetic, so
  microseconds are not lost through floating-point conversion.
- Naive source timestamps now honor `SOURCE_TIME_ZONE`, defaulting to
  `America/Sao_Paulo`.

### WP1 — Compose and lifecycle CLI

- GCP profile selection rejects legacy local profiles and unknown target
  values.
- `gcp up` cannot bypass incomplete cloud preflight and never starts the GCP
  streaming profile.
- GCP streaming lifecycle commands target only `spark-gcp-bronze` and
  `spark-gcp-silver`.

### WP2 — serving control and boundaries

- Invalid in-memory boundary allocation no longer consumes a run sequence.
- Target checks are enforced before in-memory status mutation.
- BigQuery sequence allocation performs the read/update/insert in one
  transaction and reports optimistic conflicts through `@@row_count`.
- BigQuery run allocation now supplies every required `NOT NULL` field in
  `serving_runs`.
- GCP entity metrics and the generic boundary planner now cover every
  configured Kafka partition. The registry matches the topic contract:
  `customers/products/sellers/product_category_translation` use one
  partition; `orders/order_items/order_payments/order_reviews` use three.
- Missing BigQuery metric result branches fail closed instead of being hidden
  by zero-initialized metric dictionaries.
- The local serving DAG now performs a deliberate planner probe before loading
  Silver metrics, including the initial snapshot path.

## Verification

Passed after the fixes:

```text
uv run ruff check .                         PASS
uv run ruff format --check .                PASS
uv run pyright                              0 errors, 0 warnings
uv lock --check                             PASS
uv run pytest tests -q                      365 passed, 3 skipped
dbt parse (olist_bigquery/local_static)     PASS
Compose local profile render                PASS
Compose GCP profile render                  PASS
Legacy local profile render                 PASS
local_lab.py validate --scope serving       ready
```

Clean local acceptance:

- Run ID: `wp0-wp2-code-review-r5`
- Evidence: `data/acceptance/local-cdc/wp0-wp2-code-review-r5/report.md`
- Result: `PASS`, all 11 mandatory gates passed
- Started: `2026-08-07T12:34:46.625959+00:00`
- Finished: `2026-08-07T12:53:17.650126+00:00`
- The acceptance project containers, network, and volumes were removed after
  the run.

The BigQuery transaction shape was checked against the official Google
Developer Knowledge MCP documentation for multi-statement transactions,
optimistic concurrency, rollback/commit, and `@@row_count`:

- https://docs.cloud.google.com/bigquery/docs/transactions
- https://docs.cloud.google.com/bigquery/docs/reference/system-variables

No BigQuery job, GCP API call, Terraform plan/apply, or cloud resource was
used.

## Remaining cloud checks

The following are intentionally not marked as locally verified:

1. Execute the BigQuery migration and adapter with a real client and typed
   named parameters.
2. Validate GCP IAM, dataset creation, migration ledger behavior, and real
   BigLake/Silver progress data.
3. Run cloud acceptance and parity checks against the real GCP contour.
