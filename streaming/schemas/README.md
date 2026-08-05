# CDC schema contracts

`contracts/<entity>/vN.json` defines the Kafka topic, key, MySQL columns,
Avro reader schema, Iceberg projection and evolution rules for each captured
entity. `contracts/manifest.json` records the versions and digests.

Writer schema evidence is stored in
`captured-writer-schemas/__. The validator checks the Registry group,
artifact, version, schema ID, topic provenance and canonical digest before a
writer fingerprint is accepted.

Useful checks:

```powershell
python -m streaming.schemas.generate_contracts --check
python -m streaming.schemas.writer_schemas validate
python -m streaming.schemas.contracts
uv run pytest -q tests/cdc_contracts
```

`avro.py` preserves malformed-frame evidence for Bronze and decodes the
Confluent header when it is valid. `registry.py` resolves Apicurio
references into Spark-readable schemas. Compatibility checks reject key changes,
renames, drops, incompatible type changes and non-nullable additions.
