# Kafka topic contract

`topics.json` is the fixed machine-readable manifest for the MySQL lakehouse
CDC generation. It contains exactly 15 topics. There are no DLQ topics and no
`olist_cdc.public.*` PostgreSQL topics.

`create-topics.sh` is dependency-free and runs inside `apache/kafka:4.3.1`.
It creates missing topics and reapplies every explicit retention/cleanup
property to existing topics. Before altering an existing topic it verifies the
exact partition count and rejects dangerous retention, cleanup, compaction,
segment, timestamp, message-size, ISR, or unclean-election overrides that are
not declared for that topic. Broker auto-creation must be disabled before the
script runs.

`validate_topics.py` compares a live `kafka-topics.sh --describe` response with
the manifest and rejects missing topics, managed-topic extras, partition drift,
replication drift, expected config drift, and dangerous unmanifested overrides.
Example container commands:

```text
/contract/create-topics.sh kafka:29092
python /contract/validate_topics.py --bootstrap-server kafka:29092
```

`olist_cdc.schema_history` deliberately uses `cleanup.policy=delete` with
unbounded retention. It must never be compacted. Kafka Connect's three internal
topics are the only compacted topics in this manifest.
