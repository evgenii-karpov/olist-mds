# Orchestration, CLI, Migrations, and Operations

## 1. `lab.py` command surface

`lab.py` is the only normative management entry point. It validates profile exclusivity, prerequisites, credentials, and destructive flags before calling Docker Compose, Terraform, dbt, or migration tooling.

Core command groups:

```text
lab.py doctor
lab.py local ...
lab.py gcp ...
lab.py parity ...
```

A detailed proposed command tree is in `appendices/A-command-surface.md`.

## 2. Service lifecycle

### GCP up

`lab.py gcp up`:

- verifies Terraform/gcloud/ADC/config;
- applies or validates infrastructure as requested;
- starts `core + lakehouse-gcp` services;
- applies pending BigQuery SQL migrations;
- does not start streaming.

### Streaming

```text
lab.py gcp streaming start
lab.py gcp streaming status
lab.py gcp streaming stop
```

Streaming is long-lived and remains outside Airflow task ownership.

## 3. Airflow DAGs

### `olist_local_serving`

Preserve the current local serving semantics and PostgreSQL ledger.

### `olist_gcp_serving`

Task flow:

1. validate GCP contour and migrations;
2. acquire GCP serving lease/control lock;
3. freeze a transaction-complete boundary;
4. wait for `audit.silver_progress`;
5. initialize or clean same-run candidate/history rows;
6. invoke `dbt-bigquery` in the dedicated Compose service;
7. collect dbt artifacts and write model/entity results;
8. invoke the versioned publication procedure;
9. emit metrics/report and release the lease.

## 4. Dedicated dbt service

The `dbt-bigquery` image pins dbt-core and the BigQuery adapter. It receives only the dbt ADC mount and repository project files. It is not embedded in the Airflow image.

Airflow's Docker API access must be narrowed to the task/container that invokes this service. Avoid general daemon access in unrelated Airflow components.

## 5. SQL migrations

Migrations are:

- ordered and versioned;
- idempotent or guarded by a migration ledger;
- checksummed;
- applied before DAG publication work;
- validated in CI without GCP credentials through static parsing/conventions;
- recorded in `olist_serving_control`.

Breaking migrations declare a reset requirement and must not be applied as an online mutation of existing history.

## 6. Destructive operations

Commands such as:

```text
lab.py gcp reset-data --force
lab.py gcp destroy --force
```

must refuse to run without `--force`. Before mutation they print project ID, active run, streams, buckets/datasets/catalog resources, and the intended scope.

`reset-data` clears application data using catalog-aware/table-aware operations and explicit checkpoint cleanup. It must not rely on GCS lifecycle rules.

## 7. Initial bootstrap sequence

1. Manually create project, attach Free Trial billing, and create the state bucket.
2. Generate role-specific impersonated ADC files.
3. Run `lab.py doctor` and `lab.py gcp preflight`.
4. Initialize/apply Terraform.
5. Apply BigQuery migrations.
6. Destroy/recreate local data volumes and reload Olist source data.
7. Start GCP contour services.
8. Start GCP streaming explicitly.
9. Execute the vertical slice and manual decision.
10. Continue full implementation only after go approval.
