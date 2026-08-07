# WP3 Remediation Brief — GCP Bootstrap and Terraform

## Audience

This document is an implementation brief for the AI agent responsible for
correcting the reviewed WP3 implementation.

## Scope

Work only on WP3: the GCP bootstrap documentation, the flat
`infra/gcp/dev` Terraform root, the WP3 portions of `scripts/lab.py`, the WP3
contract tests, and the WP3 implementation report.

Do not analyze, redesign, or modify WP0-WP2 or WP4 and later stages. If a WP3
output is consumed later, correct the WP3 contract without reviewing or
changing the downstream implementation.

The implementation under review was introduced by commit `ddc8c5c`. Preserve
unrelated changes made after that commit.

## Current status

WP3 is not complete. Credential-free checks pass, but the cloud definition of
done has not been exercised, and static review found blocking defects that
must be corrected before a real GCP plan or apply is attempted.

Do not mark WP3 complete until both:

1. every credential-free acceptance check in this document passes; and
2. the cloud-only acceptance checks have been run successfully in the
   dedicated GCP project.

When credentials remain unavailable, report the local portion as complete and
the cloud portion as `PENDING_GCP_ACCESS`.

## Required corrections

### 1. Grant the Spark writer write access to the catalog

The Spark writer currently receives `roles/biglake.viewer`. That role supports
reads but not writes through BigLake credential vending.

Change the Spark catalog role to `roles/biglake.editor`. Keep direct Spark
object access limited to the checkpoint bucket. Do not grant the Spark writer
any direct role on the lakehouse bucket.

Add a semantic test that proves all three conditions:

- the Spark writer has `roles/biglake.editor` at project scope;
- the Spark writer has `roles/storage.objectAdmin` only on the checkpoint
  bucket;
- no lakehouse-bucket IAM member grants a direct storage role to the Spark
  writer.

### 2. Make the catalog type and warehouse URI consistent

The Terraform resource uses `CATALOG_TYPE_GCS_BUCKET`, while the
`lakehouse_warehouse` output currently emits a `bl://` URI. These contracts are
incompatible.

Keep the planned single lakehouse-bucket design and return:

```text
gs://<lakehouse-bucket-name>
```

from `lakehouse_warehouse`.

Do not change the catalog to `CATALOG_TYPE_BIGLAKE` as part of this remediation;
that would be an architecture change rather than a WP3 defect fix.

Add a test that derives the expected URI from the selected catalog type. A
simple test that independently searches for both strings is insufficient.

### 3. Replace the circular Terraform deployer bootstrap with a coherent flow

Terraform creates a deployer service account, but the existing bootstrap does
not explain how the first apply creates that identity, how the operator later
impersonates it, or how it obtains access to the separately managed state
bucket. The deployer also lacks the permission required to maintain
`google_project_iam_member` resources.

Implement and document this two-phase flow:

1. A human bootstrap operator creates the dedicated project, attaches Free
   Trial billing, enables Service Usage, creates the versioned state bucket,
   and performs the first approved apply using short-lived user ADC.
2. The first apply creates the Terraform deployer service account and grants
   it all project-scoped permissions required by this root, including the
   ability to maintain project IAM policies.
3. Terraform grants a configured operator principal
   `roles/iam.serviceAccountTokenCreator` on the deployer service account. Use
   a validated input variable for the operator principal; do not hard-code a
   user address.
4. The runbook gives exact manual commands to grant the deployer access to the
   external state bucket and the billing-account permission required to manage
   the budget.
5. All subsequent plan/apply/destroy operations use an impersonated ADC for
   the Terraform deployer.

At minimum, the deployer must be able to maintain every resource declared in
the root. Account for:

- `resourcemanager.projects.getIamPolicy` and
  `resourcemanager.projects.setIamPolicy` for project IAM members;
- service-account administration and impersonation bindings;
- API enablement;
- BigLake, BigQuery, Storage, and Monitoring resources;
- the external GCS backend objects;
- budget creation, update, and deletion at billing-account scope.

Use predefined least-privilege roles where practical. Clearly identify which
grants are Terraform-managed and which are manual bootstrap grants. Do not
create a service-account key resource or instruct the operator to download a
long-lived key.

The documentation must not silently assume that the bootstrap operator is a
permanent Project Owner or Billing Account Administrator.

### 4. Correct ADC discovery and preflight behavior

The documented `gcloud auth application-default login` flow stores ADC at the
platform well-known location. The current preflight accepts only an explicitly
configured credential-file path and therefore rejects valid documented ADC.

Update WP3 preflight behavior so that it recognizes, without contacting GCP:

- an existing file referenced by `GOOGLE_APPLICATION_CREDENTIALS`;
- the standard local ADC file on Windows;
- the standard local ADC file on Linux/macOS;
- an approved impersonated ADC configuration file.

Do not require the `gcloud` executable when Terraform has usable explicit or
well-known ADC. Report `gcloud` availability separately because it is needed
for manual bootstrap operations, not by every Terraform provider invocation.

Preflight must also validate that:

- a non-empty project ID is available;
- the configured region is exactly `us-east1`;
- Terraform is installed and its version satisfies the root constraint;
- the discovered ADC path points to a regular file.

Never parse or print credential contents.

Preserve credential-free `terraform init -backend=false` and `terraform
validate`. Real plan/apply must remain guarded.

### 5. Make budget creation mandatory

WP3 requires budget alerts, but `billing_account_id = null` currently causes
Terraform to create no budget.

Make `billing_account_id` a required, non-null input for the real cloud
configuration and create exactly one development budget. The notification
email may remain optional if default IAM recipients remain enabled, but the
budget itself must not be optional.

If `budget_limit_usd` is assigned directly to the Money `units` field, validate
that it is a positive whole number. Alternatively, correctly split fractional
amounts into `units` and `nanos`.

Update `terraform.tfvars.example` so that the billing account is an explicit
required placeholder rather than a commented optional setting.

Document the billing-account IAM grant needed by the Terraform deployer. A
project-level grant is not a substitute for a permission required on the
billing account.

### 6. Reduce the catalog-vending service account storage role

Replace the lakehouse-bucket `roles/storage.admin` grant for the
auto-provisioned catalog service account with `roles/storage.objectUser`, as
required for credential vending.

Preserve an explicit dependency on catalog creation. Account for service
account propagation if the provider does not already retry the transient IAM
failure; do not add an unconditional sleep.

### 7. Return non-zero exit codes for blocked Terraform operations

The current shared emitter treats `blocked` as a successful exit. For the WP3
command surface, the following conditions must return a non-zero process exit
code while still emitting structured JSON with `status: "blocked"`:

- incomplete GCP preflight;
- `terraform apply` without `--yes`;
- missing Terraform executable;
- missing variable file;
- missing real-backend configuration for cloud plan/apply, when applicable.

Do not change unrelated command behavior outside the WP3 command surface.
Introduce a WP3-specific result helper or explicit return code if changing the
shared emitter would alter other stages.

Define and test the exit-code contract. Prefer `2` for an unmet precondition
and `1` for an attempted command that failed.

### 8. Strengthen tests and correct the WP3 report

Replace or supplement string-presence tests with assertions over meaningful
Terraform or parsed configuration contracts. At minimum, tests must fail for
each defect listed above.

Update the WP3 report to:

- include the implementation/remediation commit SHA;
- record the exact Terraform CLI and provider versions used;
- distinguish the three repository-managed service accounts from the
  Google-managed catalog-vending service account;
- stop describing the budget as optional;
- state that the catalog is a GCS-bucket catalog and uses a `gs://` warehouse;
- list credential-free commands and their actual outputs;
- retain an explicit `PENDING_GCP_ACCESS` section until cloud evidence exists.

Do not fabricate project IDs, backend bucket names, plan identifiers, apply
timestamps, or run IDs.

## Files expected to change

The remediation should normally be limited to:

- `infra/gcp/dev/iam.tf`
- `infra/gcp/dev/outputs.tf`
- `infra/gcp/dev/budgets.tf`
- `infra/gcp/dev/variables.tf`
- `infra/gcp/dev/terraform.tfvars.example`
- `infra/gcp/dev/README.md`
- `scripts/lab.py`, only for the WP3 preflight/Terraform command surface
- `tests/infrastructure/test_gcp_terraform_contract.py`
- relevant WP3 CLI tests
- `docs/reports/gcp-bigquery-dual-contour/WP3-gcp-bootstrap-and-terraform.md`

Changes to additional files require a written WP3-specific justification.

## Credential-free acceptance

Run all commands from the repository root unless a command explicitly changes
directory:

```powershell
terraform -chdir=infra/gcp/dev fmt -check -recursive
terraform -chdir=infra/gcp/dev init -backend=false -input=false
terraform -chdir=infra/gcp/dev validate
uv run pytest -q tests/infrastructure tests/orchestration
uv run python scripts/lab.py gcp terraform validate
```

Add focused tests for:

1. Spark BigLake Editor and checkpoint-only direct storage access.
2. GCS catalog type producing a `gs://` warehouse output.
3. Catalog service account receiving `roles/storage.objectUser`, not
   `roles/storage.admin`.
4. Required billing account and unconditional budget resource creation.
5. Whole-dollar validation or correct Money nanos handling.
6. Explicit ADC and well-known ADC discovery on Windows and POSIX systems.
7. Valid ADC succeeding without `gcloud` on `PATH`.
8. Wrong region being blocked.
9. Blocked preflight/plan/apply returning non-zero.
10. Credential-free init/validate remaining successful.
11. Absence of `google_service_account_key` resources.
12. Terraform deployer permissions and operator impersonation binding.

Tests must not contact GCP, require credentials, mutate a real backend, or
write credential material into the repository.

## Cloud-only acceptance

These checks require the dedicated Free Trial project and explicit operator
approval. They cannot be replaced by mocks or `terraform validate`.

1. Complete manual bootstrap and record the project ID, billing account ID,
   state bucket, operator principal, Terraform version, provider version, and
   UTC timestamp in a non-secret evidence record.
2. Initialize the real GCS backend using the explicit state bucket.
3. Run and save an approved `terraform plan`; verify that it includes one
   budget and no service-account keys.
4. Apply the plan successfully.
5. Re-run plan using impersonated Terraform deployer ADC and obtain an empty
   plan.
6. As the Spark writer, prove catalog write access while proving direct
   lakehouse-bucket object access is denied.
7. Verify direct checkpoint-bucket object create/update/delete access for the
   Spark writer.
8. Verify the catalog service account has Storage Object User on the
   lakehouse bucket and does not have Storage Admin.
9. Verify all five datasets, four namespaces, required APIs, service accounts,
   and the budget notification configuration.
10. Run the approved main-contour destroy.
11. Verify managed buckets, datasets, catalog, namespaces, service accounts,
    IAM grants, and budget are removed as designed while the external state
    bucket and its versioning remain intact.

Record exact command versions, plan/apply identifiers where available, UTC
timestamps, and sanitized results. Never commit credentials or access tokens.

## Completion rule

The remediation agent may report **WP3 locally remediated** after all
credential-free acceptance checks pass. It may report **WP3 complete** only
after every cloud-only acceptance item also passes and the evidence record is
updated with real, reproducible identifiers.
