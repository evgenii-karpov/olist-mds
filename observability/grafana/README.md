# Grafana

Grafana provisions Prometheus and Loki as read-only datasources and six target
operational views:

- MySQL/binlog, CDC connector and registry health;
- Kafka broker, scoped lag and Connect task health;
- Spark/Iceberg durability and serving publication SLOs;
- Airflow, control-plane and ClickHouse serving health;
- Prometheus, Alertmanager, Grafana, Loki and Alloy self-health;
- serving publication state and bounded failure indicators.

Dashboard JSON is immutable in the UI. Query and panel changes belong in
source control and must pass the observability contract validator.
