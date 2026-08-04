# Small Olist Fixture

This fixture is a tiny, synthetic Olist-shaped dataset for CI.

- `olist_small.zip` contains the same CSV file names and headers as the full
  Kaggle archive.
- `source_profile_small.json` is the matching source contract.
- `source/` contains the uncompressed CSVs so fixture changes are reviewable.

The fixture is intentionally committed because it is small and lets CI run the
target MySQL seed, CDC, Spark/Iceberg and serving contract checks without
downloading the full dataset.

Use the OS-specific runbook if the fixture needs to be regenerated locally.
