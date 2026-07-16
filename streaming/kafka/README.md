# Local Kafka contract

Phase 2 runs `apache/kafka:4.3.1` as one persistent KRaft broker. Container
clients use `kafka:29092`; host tools use `localhost:9092`. ZooKeeper and broker
topic auto-creation are disabled.

`topics.json` is the machine-readable contract. `create-topics.sh` creates its
22 topics idempotently before Connect starts. Source and reserved DLQ topics
retain data for seven days. DLQ partitions match their source topic so Phase 3
can preserve parallelism, but no producer is attached to them in Phase 2.

Validate the live broker with:

```text
python scripts/cdc/stage2_admin.py validate-topics
```

The validator checks names, partition counts, replication factor, cleanup
policy, retention, and unexpected source or derived heartbeat topics.
