# Risks and Open Gates

These are implementation risks, not unresolved architecture decisions.

## R1 — Preview BigQuery query path

Direct BigQuery queries of Lakehouse runtime catalog tables are Preview. The vertical slice is the blocking evidence gate. Record exact behavior and versions.

## R2 — Type compatibility

Timestamp, binary, nested, and decimal behavior must be proved with repository schemas. Explicit bridge casts are allowed only when semantics remain correct.

## R3 — Spark dependency conflicts

A combined local/GCP image can introduce Hadoop/Google library conflicts. Image-build classpath tests are mandatory.

## R4 — Transaction metadata completeness

The architecture deliberately fails closed. Operational procedures must make missing transaction metadata diagnosable rather than tempting operators to bypass the boundary.

## R5 — BigQuery transaction limits

All-model publication must fit supported transaction/DML behavior. Test actual model sizes and statements early after the vertical slice. If a limit is encountered, stop and redesign the publication mechanism; do not silently weaken atomicity.

## R6 — Trial and billing visibility

Budget alerts do not stop usage and some billing-account metadata may require manual console verification. Never upgrade the account; keep workloads small and delete resources proactively.

## R7 — Public-network Spark-to-GCP dependence

Local Spark requires stable network/auth access to GCP. Retry policy must distinguish transient catalog/storage failures from data-contract failures.

## R8 — No preselected no-go fallback

A no-go result ends the current rollout. The next architecture is chosen only after the actual failing constraint is documented.
