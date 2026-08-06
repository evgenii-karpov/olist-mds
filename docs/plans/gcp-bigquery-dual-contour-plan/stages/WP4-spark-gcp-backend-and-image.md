# WP4 — Spark GCP Backend and Common Image

## Dependencies

WP3

## Objective

Deliver this work package without weakening the existing local contour or bypassing the contracts in the decision register.

## Tasks

- Implement the backend configuration abstraction.
- Add Lakehouse REST catalog/credential-vending configuration.
- Add GCSFileIO and GCS checkpoint filesystem configuration.
- Bake pinned/checksummed dependencies into the common image.
- Add classpath conflict tests.
- Generate/mount separate Spark ADC.
- Verify the local backend with the same image.

## Required evidence

- committed code/configuration/migrations relevant to this package;
- automated test output where applicable;
- an operator-readable Markdown record for manual cloud actions;
- exact versions, identifiers, and run IDs needed to reproduce the result.

## Definition of done

- Local Spark acceptance still passes.
- GCP Spark can create a namespace test table and checkpoint.
- No runtime Maven/Ivy download occurs.
- Catalog alias compatibility is preserved.

## Rollback rule

Changes must be revertible without corrupting the other contour. If this package changes persistent schema or ordering semantics, use the documented reset/rebuild path rather than an unplanned in-place downgrade.
