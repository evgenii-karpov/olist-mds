# Grafana

Grafana provisions Prometheus and Loki plus six Phase 6 operational views:

- SLO, latency, freshness, and error-budget burn;
- source PostgreSQL, retained WAL, heartbeat, and Debezium;
- Kafka partitions, consumer lag, and Connect;
- NiFi queues/backpressure and object-file behavior;
- Airflow, dbt, warehouse ingest, and mart freshness;
- host/container capacity and correlated Loki logs.

Dashboard JSON is immutable in the UI (`editable=false`); review changes in
source control and keep queries on low-cardinality metrics.
