# Consolidated Decision Register

The architecture interview contained 87 decision points. This register groups tightly related answers while preserving every accepted constraint.

## A. Contours and runtime

1. The local and GCP contours are both permanent first-class targets.
2. Only one contour is operated at a time; simultaneous execution is unsupported.
3. Spark compute remains local in Docker Compose.
4. Both contours share one Spark master/worker pool but use distinct drivers, query IDs, configs, credentials, and checkpoint roots.
5. Compose uses `core`, `lakehouse-local`, and `lakehouse-gcp`; run `core` plus exactly one lakehouse profile.
6. `core` contains source systems, Kafka stack, shared Spark, Airflow, platform PostgreSQL, and the existing observability stack.
7. Polaris, MinIO, ClickHouse, local Spark drivers, and `dbt-clickhouse` belong only to `lakehouse-local`.
8. GCP Spark drivers, BigQuery migrations, and the dedicated `dbt-bigquery` service belong only to `lakehouse-gcp`.
9. Shared platform-PostgreSQL bootstrap must not create Polaris databases, users, or secrets; Polaris bootstrap is local-profile-specific.
10. The local and GCP serving DAGs are separate; small shared Python helpers are allowed.
11. Airflow does not own long-lived streaming queries.
12. `lab.py gcp up` starts infrastructure/services but does not start streaming; streaming start and stop are explicit commands.

## B. Configuration and code sharing

13. Existing `local-lab.py` becomes the single management CLI, `scripts/lab.py`.
14. `lab.py`, not Make or shell wrappers, is the normative operator interface.
15. The catalog alias resolves as `ICEBERG_SPARK_CATALOG_ALIAS`, then legacy `ICEBERG_CATALOG_NAME`, then `lakehouse`.
16. `ICEBERG_WAREHOUSE` remains the canonical warehouse variable.
17. Spark business logic, CDC normalization, table specs, and transformations remain shared.
18. Only backend/catalog/warehouse/FileIO/checkpoint/credential/query-ID configuration differs by contour.
19. One common Spark image includes both local and GCP dependencies.
20. Iceberg GCP bundle and GCS connector artifacts are pinned and baked into the image with checksums; no runtime Maven/Ivy resolution.
21. Host Terraform is used; `lab.py` verifies that an allowed version is available.
22. Terraform provider constraints use a compatible range such as `>= 7.41, < 8`, with `.terraform.lock.hcl` committed.

## C. GCP project, state, and infrastructure

23. Use one dedicated GCP project for `olist-mds`.
24. Use `us-east1` for regional resources.
25. Support only one cloud environment: `dev`.
26. Project creation, Free Trial billing attachment, and Terraform state-bucket creation are manual bootstrap steps.
27. The state bucket is in the same project, is versioned, is managed outside the main Terraform state, and survives `terraform destroy`.
28. The main Terraform configuration is one flat root module split into thematic `.tf` files; no reusable module layer initially.
29. Main-contour `terraform destroy` is intentionally allowed to delete the complete managed cloud contour; deletion protection is not used.
30. Destructive `lab.py` commands require an explicit `--force` flag; no typed confirmation phrase is required.
31. Terraform creates infrastructure, IAM, buckets, catalog/namespaces, and BigQuery datasets.
32. Versioned idempotent SQL migrations own BigQuery application/control schemas, bridge views, current tables, serving views, and stored procedures.
33. Terraform creates Lakehouse namespaces `bronze`, `silver`, `reference`, and `audit`; Spark creates and evolves Iceberg tables.

## D. Storage

34. Use a dedicated GCS lakehouse bucket and a separate Structured Streaming checkpoint bucket.
35. All Iceberg namespaces share the lakehouse bucket and are separated by catalog-managed namespace/table locations.
36. Both buckets use `STANDARD` storage class.
37. Soft delete and Object Versioning are disabled on the lakehouse and checkpoint buckets.
38. No GCS lifecycle rule automatically deletes lakehouse data or checkpoints.
39. The state bucket is the exception: it retains Object Versioning.
40. Spark receives direct object permissions only on the checkpoint bucket.
41. Iceberg data access uses Lakehouse credential vending rather than broad direct Spark object permissions.

## E. IAM and authentication

42. Use separate service accounts for Terraform deployment, Spark lakehouse writing, and dbt/BigQuery execution.
43. Local authentication uses user `gcloud` login plus service-account impersonation.
44. Long-lived service-account JSON keys are forbidden.
45. Generate one impersonated ADC file per role and mount it read-only only into the relevant container.
46. GitHub Actions receives no GCP credentials in the first implementation.
47. Cloud integration tests do not run in CI initially.

## F. Iceberg and BigQuery compatibility

48. Direct BigQuery querying of Lakehouse runtime catalog tables is accepted as a Preview dependency only behind a mandatory vertical slice.
49. BigQuery accesses Iceberg only through stable native bridge views.
50. Spark remains the writer and schema authority for repository-owned Iceberg tables.
51. BigQuery never writes to Bronze, Silver, Reference, or Audit.
52. Iceberg is V2, data files are Parquet, custom `write.data.path`/`write.metadata.path` are prohibited, metadata JSON size is monitored, and BigQuery does not depend on Iceberg metadata tables.
53. Existing `TIMESTAMP_NTZ` table fields are replaced with timezone-aware instant semantics and rebuilt destructively.
54. Source wall-clock values are interpreted through configurable `SOURCE_TIME_ZONE`, default `America/Sao_Paulo`, then normalized to UTC.
55. Monetary and ordinary business decimals map to BigQuery `NUMERIC`; high-precision coordinates/technical values map to `BIGNUMERIC`.
56. The required vertical slice contains `bronze.mysql_cdc_records`, `silver.order_items_changes`, `reference.geolocation`, and `audit.silver_progress`.
57. A manual go/no-go decision follows the vertical slice.
58. A no-go outcome has no preselected fallback architecture; diagnose the actual failure and redesign then.

## G. CDC ordering and transaction boundaries

59. A malformed or missing MySQL binlog filename/index fails the pipeline, emits audit evidence, and blocks publication.
60. The canonical order is based on source coordinates and deterministic transport tie-breakers, never timestamp fallback.
61. The canonical tuple is: snapshot/live discriminator, binlog file index, binlog position, row, transaction total order, transaction data-collection order, source timestamp, Kafka partition, Kafka offset, event ID.
62. Snapshot, live non-transactional, and transactional events have different required-field contracts.
63. Binlog coordinates are mandatory for ordinary live CDC events.
64. Transaction-order fields are mandatory only for transactional events.
65. Missing required ordering fields are quarantined/audited and block affected processing.
66. Serving boundaries use Debezium transaction metadata and stop at the last fully completed source transaction.
67. The frozen boundary stores offsets per Kafka topic-partition and never splits a source transaction.
68. Missing or incomplete transaction metadata fails closed; there is no end-offset or idle-time fallback.
69. dbt reads immutable `silver.*_changes` bounded by the frozen offsets.
70. `audit.silver_progress` proves Spark caught up to the boundary before a serving build begins.

## H. Gold and publication

71. `dbt-clickhouse` and `dbt-bigquery` are fully independent projects; no provider-neutral shared dbt core is introduced.
72. Both projects preserve the same business grains, keys, SCD2 meaning, metrics, and tests.
73. The initial GCP serving run builds full Gold state.
74. Later runs are truly incremental and derive changed business keys/impacted grains from the exact prior/current boundary interval.
75. No fixed `updated_at` lookback is used for change discovery or late-arriving data.
76. Deletes are model-specific: current facts/dimensions delete or tombstone rows, SCD2 closes versions, aggregates recompute affected grains/partitions.
77. Each Gold model has one append-only history/candidate table containing all runs, identified by `sync_run_seq` and `operation_type`.
78. Each Gold model also has a materialized current-state table used by serving.
79. Stable `olist_gold` views read materialized current-state tables, not `ROW_NUMBER()` over history and not a full-snapshot pointer.
80. Retrying an unpublished `sync_run_seq` first deletes that run's candidate/history rows and rebuilds from the same frozen boundary; a retry does not allocate a new run ID.
81. Published rollback is implemented as a new compensating/recovery run with a new `sync_run_seq`.
82. Additive schema changes use SQL migrations; breaking key/type/structure changes trigger a full reset/rebuild rather than online history migration.
83. One versioned BigQuery stored procedure publishes a run in one multi-statement transaction: validate predecessor, apply every model delta to current state, update SCD2/aggregates, set statuses, and advance `active_sync_run_seq`.
84. Publication uses optimistic concurrency: the expected active run must match; a stale ready run becomes a conflict and cannot overwrite newer state.
85. All successful, failed, and conflicted runs are retained; there is no automatic candidate/history cleanup for this small project.

## I. Datasets, orchestration, validation, and operations

86. BigQuery datasets are `olist_lakehouse_bridge`, `olist_gold_store`, `olist_gold`, `olist_serving_control`, and `olist_cloud_test`.
87. GCP serving-control state is native BigQuery state; local serving-control state remains PostgreSQL.
88. `dbt-bigquery` runs in a dedicated pinned Compose container with its own ADC mount, not in the Airflow image.
89. Airflow invokes the dbt container through Docker API access restricted to the relevant Airflow task/container.
90. Versioned migrations own bridge views, stable Gold views, and publication procedures; dbt builds physical per-run model deltas/history only.
91. Cross-contour parity is a repeatable local CLI command that runs contours sequentially and emits JSON plus Markdown.
92. Parity is strict for keys, row counts, nulls, business fields, aggregates, and checksums, allowing only documented type/timestamp representation differences.
93. Parity is a separate acceptance workflow, not a blocker for each normal GCP publication.
94. The existing Prometheus/Grafana stack is reused; Cloud Monitoring is not separately configured.
95. Required metrics include Spark lag, Kafka offsets, serving-run state, dbt/publication duration, BigQuery processed/billed bytes, BigLake/GCS errors, and active `sync_run_seq`.
96. CI remains credential-free and performs Terraform format/validate, Spark build/tests, Compose rendering, DAG import, migration checks, and `dbt-bigquery parse` only; it does not run `dbt compile` against BigQuery.
97. BigQuery jobs use labels and `maximum_bytes_billed`; actual bytes are recorded.
98. Terraform creates budget alerts, but alerts are notifications rather than hard stops.
99. `lab.py` performs billing and residual-resource preflight checks.
100. The account must remain a Free Trial account and must never be upgraded to paid billing; resources are deleted before trial expiry or credit exhaustion.
101. Initial cloud loading starts from destroyed/recreated local volumes, a fresh Olist load into MySQL, and clean Debezium/Kafka history, with GCP Spark reading from the beginning.
102. GCP infrastructure normally persists between development runs, but explicit destroy removes the complete managed contour.
