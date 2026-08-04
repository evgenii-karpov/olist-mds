# Target Kafka topology

Kafka carries the eight MySQL entity topics plus the target transaction,
heartbeat and schema-history topics declared in `topics.json`. Debezium
publishes the source records; Spark consumes them with the explicit target
consumer group and checkpoint contract.

`create-topics.sh` is generated from the committed topic manifest and is safe
to rerun. Connect internal topics are compacted and are never reset as part of
a bounded data replay. Topic names, partition counts, retention and cleanup
policies are validated by `tests/cdc_contracts`.
