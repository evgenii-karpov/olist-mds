# WP3 — GCP Bootstrap and Flat Terraform Root

## Dependencies

WP1, WP2

## Objective

Deliver this work package without weakening the existing local contour or bypassing the contracts in the decision register.

## Tasks

- Document manual project/billing/state-bucket bootstrap.
- Create flat `infra/gcp/dev` Terraform root.
- Enable required APIs.
- Create STANDARD lakehouse/checkpoint buckets with soft delete/versioning disabled and no lifecycle rules.
- Create five BigQuery datasets, service accounts, IAM, catalog/namespaces, and budget alerts.
- Commit provider constraints and lockfile.
- Add `lab.py gcp preflight/terraform` commands.

## Required evidence

- committed code/configuration/migrations relevant to this package;
- automated test output where applicable;
- an operator-readable Markdown record for manual cloud actions;
- exact versions, identifiers, and run IDs needed to reproduce the result.

## Definition of done

- Plan/apply succeeds in the dedicated project.
- Main destroy leaves the state bucket intact.
- Spark has direct object access only to checkpoint storage.
- No long-lived service-account key is created.

## Rollback rule

Changes must be revertible without corrupting the other contour. If this package changes persistent schema or ordering semantics, use the documented reset/rebuild path rather than an unplanned in-place downgrade.
