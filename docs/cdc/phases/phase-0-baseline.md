# Phase 0 Baseline: Contracts and Compatibility

Status: implemented on 2026-07-16.

This document records the shared runtime decision, exact local container
versions, repository ownership, and validation gates established before CDC
services are introduced.

## Shared runtime compatibility

The shared Airflow runtime is Python 3.12 with Apache Airflow 3.2.1. Amazon MWAA
lists that exact pairing as supported, and the official Airflow image
`apache/airflow:slim-3.2.1-python3.12` exists. The project metadata, Ruff,
Pyright, Dockerfile, and lock file use Python 3.12.

Existing local and AWS batch DAGs use public Airflow 3 APIs available in 3.2.1.
The Phase 0 verification gate imports both DAGs from the shared image. No
ADR-010 amendment is required because the verified target is the version
already selected by the accepted ADR.

Airflow metadata created by 3.3.0 cannot be downgraded to the 3.2.1 migration
chain. The user has designated both the local PostgreSQL 18.4 analytics volume
and Airflow metadata volume as disposable, so the accepted transition is
`docker compose down -v` followed by a clean start. No data or metadata
migration is required for this workspace.

Authoritative references:

- [MWAA supported Airflow and Python versions](https://docs.aws.amazon.com/mwaa/latest/userguide/mwaa-faqs.html)
- [Airflow reproducible installation and constraints](https://airflow.apache.org/docs/apache-airflow/stable/installation/installing-from-pypi.html)

## Version matrix

`streaming/runtime-versions.json` is the machine-readable source of truth.
Every image reference uses an exact release tag; CI rejects `latest` and
`stable`. Registry manifests for all listed images were checked on 2026-07-16.

| Capability | Version | Image |
| --- | --- | --- |
| PostgreSQL analytics | 18.4 | `postgres:18.4` |
| PostgreSQL Airflow metadata | 17.10 | `postgres:17.10` |
| Python | 3.12 | Shared local/MWAA runtime |
| Airflow | 3.2.1 / Python 3.12 | `apache/airflow:slim-3.2.1-python3.12` |
| dbt Core | 1.11.8 | Locked Python package |
| dbt PostgreSQL adapter | 1.10.0 | Locked Python package |
| dbt Redshift adapter | 1.10.1 | Locked Python package |
| Kafka | 4.3.1 | `apache/kafka:4.3.1` |
| Debezium Connect | 3.6.0.Final | `quay.io/debezium/connect:3.6.0.Final` |
| NiFi | 2.10.0 | `apache/nifi:2.10.0` |
| Apicurio Registry | 3.3.0 | `quay.io/apicurio/apicurio-registry:3.3.0` |
| Prometheus | 3.12.0 | `prom/prometheus:v3.12.0` |
| Alertmanager | 0.30.0 | `prom/alertmanager:v0.30.0` |
| Grafana | 13.0.2 | `grafana/grafana:13.0.2` |
| Grafana Alloy | 1.16.1 | `grafana/alloy:v1.16.1` |
| Loki | 3.6.5 | `grafana/loki:3.6.5` |
| node_exporter | 1.10.2 | `prom/node-exporter:v1.10.2` |
| postgres_exporter | 0.18.1 | `quay.io/prometheuscommunity/postgres-exporter:v0.18.1` |
| statsd_exporter | 0.29.0 | `prom/statsd-exporter:v0.29.0` |
| cAdvisor | 0.55.1 | `gcr.io/cadvisor/cadvisor:v0.55.1` |

Debezium 3.6 supports PostgreSQL 18 and Kafka Connect 3.1 or later. Its release
was built and tested against Kafka 4.2. Local Kafka 4.3.1 is retained from the
approved plan because the broker protocol is compatible, but Phase 2 must run
the defined restart, snapshot, ordering, schema-history, and WAL integration
tests before declaring the combination proven.

References:

- [Debezium 3.6 tested versions](https://debezium.io/releases/)
- [Debezium 3.6 release notes](https://debezium.io/releases/3.6/release-notes)
- [Apicurio Registry 3.3.0 release](https://www.apicur.io/blog/2026/06/16/registry-3.3.0-released)

## Compose profiles

The supported profile names are `realtime-core`, `observability`, and `logs`.
Existing batch services intentionally remain unprofiled, so the default
`docker compose up` behavior is unchanged. Later phases assign real services to
the appropriate profiles; the default batch services remain unprofiled.

CI validates the default configuration, every individual profile, and useful
profile combinations.

## Directory ownership

| Directory | Owner |
| --- | --- |
| `infra/oltp/` | Phase 1 source DDL, roles, bootstrap, and control schema |
| `scripts/simulation/` | Phase 1 deterministic simulator |
| `streaming/kafka/` | Phase 2 broker and topic assets |
| `streaming/connect/` | Phase 2 Connect image and Debezium templates |
| `streaming/schemas/` | Shared reviewed Avro schemas and compatibility policy |
| `streaming/nifi/` | Phase 3 NiFi flow and parameter contexts |
| `observability/` | Phase 3 metrics and Phase 6 logs |
| `infra/postgres/realtime/` | Phase 4 local warehouse CDC SQL |
| `infra/redshift/realtime/` | Phase 7 Redshift CDC SQL |
| `scripts/cdc/` | Phase 4+ shared loader, audit, replay, and metrics logic |
| `infra/aws/realtime/` | Phase 7 independent Terraform root |

## CI contracts

- `validate_realtime_configuration.py` validates required directories, the
  exact-version manifest, and the Avro policy file without live services.
- `check_avro_schema_compatibility.py` enforces a conservative
  backward-transitive contract across committed subject versions. New fields
  require defaults; removal, rename, and incompatible type changes fail.
- Registry-side compatibility remains mandatory in Phase 2 because the local
  checker is deliberately stricter and is not a substitute for Apicurio's wire
  integration.
- Existing lint, unit, dbt, DAG-import, and batch-fixture-idempotency gates remain in
  place.

## Phase 0 verification record

Verification completed on 2026-07-16 from a clean local PostgreSQL analytics
and Airflow metadata volume:

| Gate | Result |
| --- | --- |
| Runtime lock | Resolved 206 packages for Python 3.12; Airflow locked at 3.2.1, dbt Core at 1.11.8 |
| Image availability | Registry manifests resolved for every image in `streaming/runtime-versions.json` |
| Compose | Default plus all individual and documented combined profiles passed `config --quiet` |
| Python | 18 tests passed; one POSIX-shell-only test skipped on Windows |
| Static analysis | Ruff, Ruff format, Pyright, SQLFluff, and pre-commit passed |
| dbt | `deps`, `parse --no-partial-parse --show-all-deprecations`, and `compile --no-partial-parse` passed |
| Airflow image | `olist-airflow:local` built from Airflow 3.2.1/Python 3.12 |
| DAG imports | Both existing batch DAGs imported from `/opt/airflow/dags` |
| Fixture integration | Initial and replay DAG runs succeeded; raw and analytical fingerprints were identical |

The first attempted local start correctly exposed incompatible metadata left by
Airflow 3.3.0 (`Can't locate revision identified by 'd2f4e1b3c5a7'`). Per the
explicit disposable-state rule, `docker compose down -v` reset both databases;
the clean 3.2.1 initialization and full fixture replay then passed.
