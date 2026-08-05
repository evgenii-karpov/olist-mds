# Grafana

Grafana provisions Prometheus and Loki as read-only data sources and provides
operational views for CDC health, Kafka position, Spark/Iceberg progress,
serving publication, Airflow and local service health.

Dashboard JSON is managed in source control. Query or panel changes must pass
the observability contract validator.
