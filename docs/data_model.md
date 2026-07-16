# Data Model

## Modeling Goals

The dbt project demonstrates dimensional modeling, grain discipline, SCD Type 2
history, incremental fact loading, and business-facing marts.

## Source Entities

The Olist source contract covers customers, geolocation, order items, payments,
reviews, orders, products, sellers, and product category translation.

Detailed file names, row counts, columns, and raw warehouse types live in
[source_contract.md](source_contract.md).

## Core Model

### `fact_order_items`

Grain:

```text
one row per order_id + order_item_id
```

This grain keeps product, seller, price, freight, and delivery metrics at the
natural order-item level. Order-level payment values are allocated to items in
proportion to item gross amount.

Key measures include price, freight, gross item amount, allocated payment value,
delivery days, delivery delay days, and late-delivery flags.

### `dim_customer_scd2`

Business key: `customer_unique_id`.

Tracked attributes: zip prefix, city, and state. The dimension demonstrates how
customer profile or address changes affect historical facts.

### `dim_product_scd2`

Business key: `product_id`.

Tracked attributes include category, English category name, weight, and physical
dimensions. The dimension demonstrates category and product-attribute
corrections over time.

### `dim_seller`

Business key: `seller_id`.

This is a Type 1 dimension, which keeps the project focused while still giving a
contrast with the SCD2 customer and product dimensions.

### `dim_date`

Business key: `date_day`.

Used for purchase, approval, delivery, and estimated delivery dates.

### `dim_order_status`

Small reference dimension for Olist order status values such as `created`,
`approved`, `shipped`, `delivered`, `unavailable`, and `canceled`.

## SCD2 Strategy

Olist is a static dataset, so the project generates deterministic correction
feeds to make Type 2 behavior visible across batch dates:

```text
customer_profile_changes
product_attribute_changes
```

dbt snapshots use the `check` strategy. Core SCD2 dimensions expose business
effective windows as `valid_from`, `valid_to`, and `is_current`, while retaining
dbt snapshot timestamps separately for processing-time lineage.

Facts join to SCD2 dimensions by the business event timestamp, so historical
orders resolve to the customer and product attributes that were valid at the
time of purchase.

## Incremental Fact Loading

`fact_order_items` is incremental. Each run reprocesses the widest needed
window across:

- the configured late-arriving lookback;
- the earliest visible customer correction;
- the earliest visible product correction.

This keeps fact-to-dimension surrogate keys correct when a correction is
business-effective in the past.

## Marts

### `mart_daily_revenue`

Grain: one row per purchase date.

Metrics include gross revenue, product revenue, freight revenue, order count,
customer count, item count, average order value, delivery days, and late
deliveries.

### `mart_monthly_arpu`

Grain: one row per month.

Metrics include active customers, total revenue, ARPU, orders per customer,
average order value, and repeat-customer rate.

## Data Quality

dbt tests cover source and staging keys, accepted values, non-negative monetary
fields, fact grain, dimension relationships, SCD2 window validity, current-row
uniqueness, payment allocation balance, and mart metric formulas.

## Realtime CDC Model

The CDC path is isolated from batch schemas. `realtime_staging` contains all
typed events, source-latest non-deleted state, and exact-transform changed keys.
Every current model orders by `_source_lsn`, `_tx_order`, `_partition`, and
`_offset`; warehouse and NiFi timestamps are lineage only.

`realtime_core` retains event-derived history for all eight captured entities.
Delete rows remain in history with `is_deleted=true`, while current models and
`fact_order_items_realtime` exclude deleted orders/items. Payment allocation
uses the same dbt macro as the batch fact.

`realtime_marts` incrementally deletes and rebuilds only the old/new purchase
dates and months associated with the transform's immutable manifest set.
Publication views in `analytics` change only after parity approval and can be
switched back to batch without renaming or dropping either mart set.

The dbt project defines `batch`, `realtime`, and `parity` groups. Runtime entry
points select `batch`, `realtime_transform`, `realtime_quality`, or
`realtime_parity`; a bare `dbt build` is intentionally not used. The three
models under `models/parity` are the only permitted bridge: they may reference
both batch and realtime relations, while neither transformation group may
reference the other.

`batch` is an operational selector: in addition to the batch transformation
graph, snapshots, and batch quality tests, it includes the Elementary package
models required by dbt hooks and `edr report`. It does not include realtime or
parity models.

Realtime fact rebuilds resolve customer and product surrogate keys to the
source-current dimension version. This is an explicit processing-time lineage
choice because the Debezium contract has source ordering timestamps but no
separate business-effective timestamp for profile corrections. Batch facts keep
their existing purchase-time SCD2 joins. Cross-path parity therefore gates
natural grain, attributes, allocations, and mart measures rather than requiring
the two independently generated surrogate keys to match.

Mart freshness records the maximum source timestamp of the exact transform
manifest set. The quality check compares its build horizon with newly loaded
raw manifests, so an idle but fully caught-up source is not reported as stale.
