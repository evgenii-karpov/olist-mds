# Kafka topology

Kafka carries the eight MySQL entity topics plus transaction, heartbeat and
schema-history topics declared in `topics.json`. Debezium publishes the
source records and Spark consumes them with the configured consumer groups and
checkpoint paths.

`create-topics.sh` is generated from the topic manifest and is safe to
rerun. Connect internal topics are compacted and are not changed by normal CDC
recovery operations.

Run the topic contract checks with:

```powershell
uv run pytest -q tests/cdc_contracts
```
