# Acceptance Matrix

| Area | Test | Required result |
|---|---|---|
| Profile isolation | Render local profiles | No GCP credentials/resources required |
| Profile isolation | Render GCP profiles | No Polaris/MinIO/ClickHouse/local-db bootstrap leakage |
| Ordering | Malformed binlog filename | Audit/quarantine and fail closed |
| Ordering | Snapshot/live/transaction field matrix | Correct required-field enforcement |
| Ordering | Conflicting source coordinates in one Silver batch | Audit evidence written; no Silver/current/progress advance |
| Ordering | Exact replay of the same event | Idempotent; no false coordinate conflict |
| Boundary | Missing transaction metadata | Serving run blocked |
| Boundary | Multi-partition transaction | Frozen offsets do not split transaction |
| Timestamp | Source wall clock through production Spark | Interpreted in configured zone and stored as the expected UTC instant |
| Timestamp | Non-default and invalid `SOURCE_TIME_ZONE` | Non-default zone changes the stored instant; invalid zone blocks startup |
| CLI | Normative WP1 command tree | Every documented command parses; `local serving run` is available |
| CLI | Missing GCP authentication | `gcp up` and `gcp streaming start` block with no public bypass |
| Control | Run predecessor changed after allocation | Stale run cannot advance active state |
| Control | Invalid transition or persistence failure | No partial state/result mutation |
| Decimal | Money | BigQuery NUMERIC with exact accepted values |
| Decimal | Geolocation/high precision | BigQuery BIGNUMERIC with accepted precision |
| Checkpoint | Restart GCP query | Continues idempotently from GCS checkpoint |
| Catalog | BigQuery P.C.N.T query | Reads Spark-created Iceberg table |
| Bridge | Permanent view | Stable query and normalized types |
| Visibility | Spark commit during BigQuery reads | Accepted visibility/consistency behavior documented |
| Progress | `audit.silver_progress` | Proves caught-up state for frozen boundary |
| Incremental | Second serving run | Only impacted keys/grains written to history |
| Delete | Fact/current entity delete | Correct current-state deletion/tombstone |
| SCD2 | Corrected dimension history | Active version closed and replacement timeline correct |
| Aggregate | Late/corrected fact | Exact affected day/month recomputed |
| Retry | Same unpublished sequence | Old candidate rows cleared and same boundary rebuilt |
| Concurrency | Stale ready run | Conflict; active state unchanged |
| Atomicity | Failure mid-publication | No current/control partial commit |
| Recovery | Published rollback | New compensating run succeeds |
| Parity | Full deterministic fixture | Strict normalized parity passes |
| CI | Cloud static workflow | No GCP credentials or live resources |
| Cost | BigQuery limits/labels | Caps enforced and actual bytes recorded |
| Cleanup | Main destroy | Managed contour absent; state bucket explicitly remains |
| Evidence | Local acceptance archive | Durable report/checksums exist and cleanup claims match recorded actions |
