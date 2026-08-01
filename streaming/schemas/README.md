# MySQL CDC schema contracts

`contracts/<entity>/vN.json` is the immutable version chain for each of the
eight captured entities. Every version fixes the Kafka topic and partition
count, ordered primary key, exact MySQL columns, contractual Avro reader
schemas, Spark `from_avro` input, Iceberg business projection, and the
nullable/additive evolution policy. `contracts/manifest.json` records every
version and digest; adding a ninth entity, deleting history, or breaking
`BACKWARD_TRANSITIVE` compatibility is a contract failure.

Reader schemas are not evidence of bytes produced by Debezium. There are no
placeholder writer digests. `captured-writer-schemas/manifest.json` therefore
starts with all 16 entity/kind slots in `pending_runtime_capture`, and generated
v1 contracts have empty allowlists. Fingerprint checks fail closed until J1 has
captured a complete key/value bundle for all eight topics. The writer-schema
loader recomputes every canonical SHA-256 from a checked-in `.avsc` source and
requires registry URL/group/artifact/version/schema ID, capture time, connector,
and topic provenance before a digest can enter a contract allowlist.

J1 handoff (runtime capture is intentionally not fabricated in Wave 1):

1. Export the actual Apicurio key and value schemas emitted by
   `olist-mysql-cdc` for all eight business topics. Build a bundle with the same
   layout and manifest shape as `captured-writer-schemas/manifest.json`, mark
   every slot `captured`, and include the complete provenance fields beside
   each `.avsc` path and canonical digest.
2. Import and validate the complete evidence bundle:

   ```text
   python -m streaming.schemas.writer_schemas capture-bundle --bundle <runtime-export-directory>
   python -m streaming.schemas.writer_schemas validate --require-captured
   ```

3. Preserve pending v1 and publish the captured allowlists as v2:

   ```text
   python -m streaming.schemas.generate_contracts --write --new-version 2
   python -m streaming.schemas.generate_contracts --check
   python -m streaming.schemas.contracts --require-captured-writers
   ```

If contract history has advanced before J1, replace `2` with the next version
for all eight entities. The generator never rewrites older versions and carries
all previously approved fingerprints forward.

Useful finite checks:

```text
python -m streaming.schemas.generate_contracts --check
python -m streaming.schemas.writer_schemas validate
python -m streaming.schemas.contracts
python -m unittest discover -s tests/cdc_contracts
```

`avro.py` preserves malformed-frame evidence for Bronze while extracting the
five-byte Confluent header when valid. `registry.py` recursively resolves
Apicurio references and builds Spark-ready self-contained schemas.
`compatibility.py` rejects renames, drops, existing-type changes, non-nullable
additions, and key/PK changes across all prior versions.

The old `normalized/`, `cdc-landing/`, and `cdc-coverage/` assets remain only so
Parallel Wave 1 does not prematurely break the legacy NiFi path; the final
legacy-removal phase owns deleting them.
