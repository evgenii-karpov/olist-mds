# WP3 — GCP Bootstrap and Terraform Report

Date: 2026-08-07
Branch: `gcp-bigquery-dual-contour`

## Status

**The credential-free implementation is complete. Cloud completion is
pending a dedicated GCP project, billing account, ADC and gcloud access.**

The flat Terraform root, manual bootstrap instructions, resource ownership
and `lab.py` preflight/terraform commands are available locally. No cloud
API, Terraform backend, plan, apply or service-account key was used.

## Implemented

- Added `infra/gcp/dev` as a flat Terraform root with the `hashicorp/google`
  provider constrained to `>= 7.41, < 8.0` and locked at `7.43.0`.
- Added explicit manual bootstrap instructions for the project, billing,
  ADC and separately managed GCS state bucket. The state bucket is not part
  of the main destroy path.
- Added enablement for the required BigQuery, BigLake, storage, IAM,
  Service Usage, STS, monitoring, billing-budget and resource-manager APIs.
- Added two STANDARD uniform-bucket-level-access buckets. Object versioning,
  soft-delete retention and lifecycle deletion policies are disabled; the
  checkpoint bucket is the only bucket granted Spark object-admin access.
- Added five regional BigQuery datasets, BigLake GCS catalog and the
  `bronze`, `silver`, `reference` and `audit` namespaces.
- Added dedicated Terraform deployer, Spark, dbt and catalog-vending service
  accounts with resource-scoped IAM. No service-account key resource exists.
- Added optional billing-budget thresholds and an optional monitoring email
  notification channel.
- Extended `scripts/lab.py` with credential-aware GCP preflight and explicit
  credential-free Terraform `init`/`validate` support. Plan/apply remain
  guarded by the preflight unless explicitly overridden for a real cloud
  environment.
- Added contract tests covering the root shape, provider lock, storage policy,
  required resources, IAM ownership and credential-free CLI behavior.

The catalog settings follow the current Google Developer Knowledge MCP
guidance for the BigLake Iceberg REST catalog, GCS warehouse URI and vended
credentials:

- [Set up a Lakehouse Iceberg REST catalog](https://docs.cloud.google.com/lakehouse/docs/set-up-lakehouse-iceberg-rest-catalog)
- [Query Iceberg tables with Lakehouse](https://docs.cloud.google.com/lakehouse/docs/query-iceberg-tables-with-lakehouse)
- [Cloud Storage soft delete](https://docs.cloud.google.com/storage/docs/soft-delete)
- [Cloud Storage object versioning](https://docs.cloud.google.com/storage/docs/object-versioning)
- [Understanding APIs and Terraform](https://docs.cloud.google.com/docs/terraform/understanding-apis-and-terraform)

Terraform provider resource contracts were checked with the Terraform MCP
against hashicorp/google `7.43.0`, including BigLake catalog/namespace,
BigQuery dataset, storage bucket, IAM, service account, project service and
budget resources.

## Evidence

All checks were run from the working tree with no GCP credentials.

```text
terraform init -backend=false -input=false
Terraform has been successfully initialized!
Using previously-installed hashicorp/google v7.43.0

terraform fmt -check -recursive
passed

terraform validate
Success! The configuration is valid.

uv run pre-commit run --all-files
Ruff, Ruff format, Pyright and dbt-parse: Passed

uv run pytest -q tests/infrastructure tests/orchestration
15 passed, 1 warning

uv run python scripts/lab.py gcp terraform validate
status: ready

uv lock --check
Resolved 177 packages in 1ms
```

The current local preflight reports the expected cloud blocker:

```text
status: blocked
missing: project_id, region, adc_file, gcloud
terraform: true
```

## Remaining cloud checks

1. Create or select the dedicated project and billing account, then create
   the separately managed GCS state bucket.
2. Authenticate with ADC and gcloud, configure the backend, and run a real
   `terraform plan` followed by an approved `terraform apply`.
3. Verify API enablement, bucket IAM/policies, BigLake catalog vending,
   dataset IAM, service-account impersonation and budget notification in the
   target project.
4. Verify that the main Terraform destroy leaves the state bucket intact and
   that the Spark identity has direct object access only to checkpoint
   storage.
5. Run the cloud acceptance and parity checks after the later Spark, serving,
   DAG and BigQuery integration stages are available.

Until those checks are run, WP3 must not be marked complete in the final
cloud delivery record, although its locally verifiable portion is complete.
