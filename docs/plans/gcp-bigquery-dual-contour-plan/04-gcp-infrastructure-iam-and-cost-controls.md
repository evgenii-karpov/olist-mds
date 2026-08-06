# GCP Infrastructure, IAM, Authentication, and Cost Controls

## 1. Bootstrap boundary

Manual bootstrap creates:

1. one dedicated GCP project;
2. Free Trial billing attachment without upgrading to paid billing;
3. one versioned GCS Terraform state bucket in the same project;
4. initial permissions allowing the Terraform deployer identity to use the backend.

The state bucket is not part of the main Terraform state and is not deleted by main-contour destroy.

## 2. Terraform structure

Use one flat `infra/gcp/dev` root module. Split resources by thematic `.tf` files, not reusable modules. Terraform runs on the host and is invoked through `lab.py`.

Terraform owns:

- required APIs;
- the lakehouse and checkpoint buckets;
- Lakehouse runtime catalog and namespaces;
- BigQuery datasets;
- service accounts and IAM bindings;
- budget notifications;
- outputs used to generate runtime configuration.

Terraform does not own repository application-table schemas or SQL procedures.

## 3. Location and storage

- Region: `us-east1`.
- Lakehouse bucket: `STANDARD`, uniform bucket-level access, no HNS, soft delete disabled, Object Versioning disabled, no lifecycle rules.
- Checkpoint bucket: same storage settings.
- State bucket: versioned; manually managed outside the main state.
- All Iceberg namespaces use the single lakehouse bucket through catalog-managed locations.

The choice of `STANDARD` aligns with active two-week development and the Cloud Storage Always Free allowance available in `us-east1`; cold classes are inappropriate for frequently read/overwritten checkpoints and short-lived data.

## 4. BigQuery datasets

| Dataset | Ownership and purpose |
|---|---|
| `olist_lakehouse_bridge` | Stable read-only views over P.C.N.T Iceberg tables; type normalization |
| `olist_gold_store` | Per-model history/candidate deltas and materialized current-state tables |
| `olist_gold` | Stable consumer-facing views over current state |
| `olist_serving_control` | GCP runs, boundaries, results, active sequence, conflicts, migration state |
| `olist_cloud_test` | Vertical-slice and disposable cloud acceptance objects |

All datasets use a location compatible with the catalog/buckets and BigQuery job location.

## 5. Service accounts

### Terraform deployer

Purpose: create and destroy only the planned infrastructure. Do not reuse it for Spark or dbt.

### Spark lakehouse writer

Purpose: authenticate to the Iceberg REST catalog, use credential vending, and access the checkpoint bucket. It receives no broad direct object role on the lakehouse bucket beyond what the catalog integration requires.

### dbt BigQuery runner

Purpose: create/query native BigQuery Gold/control objects and read source bridge views. It receives job-user permission plus dataset-scoped data permissions.

## 6. Local authentication

Use:

```text
human gcloud login
  -> impersonate role-specific service account
  -> create role-specific ADC file outside the repository
  -> mount read-only only into the matching container
```

Do not commit or generate long-lived JSON keys.

## 7. Zero-spend policy

The financial requirement is **actual spend of USD 0**.

Controls:

- remain on a Free Trial billing account; never select Upgrade/Activate paid billing;
- create budget alerts at multiple thresholds; treat them only as notifications;
- apply BigQuery labels to all jobs;
- set `maximum_bytes_billed` for all script/dbt/query entry points where supported;
- record processed and billed bytes in run-control/audit evidence;
- use small deterministic fixtures for the vertical slice and parity;
- show residual buckets, objects, datasets, and catalog resources before destructive commands;
- delete main-contour resources before the trial ends or credits are exhausted.

`lab.py` should inspect available billing metadata and show an explicit preflight result. Where the API cannot prove trial-vs-paid status, it must instruct the operator to verify the Billing Overview and require a local recorded acknowledgement before proceeding.

## 8. Destruction

`lab.py gcp destroy --force` may destroy the entire Terraform-managed contour. It must:

1. stop GCP streaming;
2. verify no serving transaction is active;
3. show planned residual resources;
4. run Terraform destroy;
5. verify that main-contour buckets/datasets/catalog are gone;
6. report that the state bucket remains and requires a separate manual bootstrap cleanup decision.
