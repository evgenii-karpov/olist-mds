# Small Olist fixture

This committed fixture is a small Olist-shaped dataset for local CDC checks.

- `olist_small.zip` contains the expected CSV names and headers.
- `source_profile_small.json` contains the matching source profile.
- `source/` contains the CSV files for review.

The fixture lets MySQL, CDC, Spark/Iceberg, serving and dbt checks run without
external data downloads. Use the operating-system runbook when regenerating it.
