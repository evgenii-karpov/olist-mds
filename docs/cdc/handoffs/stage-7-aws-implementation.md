# Handoff: Stage 7 — independent AWS implementation

## Mission

Build the independent AWS path without depending on local runtime state. Reuse
logical event, schema, ordering, manifest, audit, dbt, parity, observability,
and recovery contracts; use AWS-native security and secret providers.

## Verified local contracts

- Phase 5 exact-manifest transforms, source ordering, deletes, parity, and
  reversible publication remain authoritative.
- Six dashboard information domains, low-cardinality metrics/log labels, the
  alert policy, and recovery catalog are version-controlled.
- Loki/Alloy log correlation is runtime-smoke-tested locally.

## Open prerequisites

- Complete the bounded local Kafka authenticated-TLS and NiFi managed-authorizer
  migration. Do not copy local plaintext Kafka or single-user NiFi access to
  AWS.
- Exercise alert fire/resolution, Connect/WAL recovery, NiFi backlog drain, and
  immutable warehouse rebuild on disposable local state.
- Execute and retain reference/burst benchmark evidence before claiming shared
  thresholds or the five-minute SLO.

These prerequisites do not authorize AWS resources to access local services and
do not change Phase 7's independent Terraform/state boundary.
