# Prometheus

Prometheus scrapes Kafka, Connect, both PostgreSQL databases, NiFi, MinIO,
Airflow StatsD, the warehouse audit exporter, node exporter, and cAdvisor.

Recording rules compute ten-minute p95 commit-to-mart latency, ten-minute latency
error-budget burn, Kafka lag, and NiFi queue utilization. Initial thresholds
remain those approved in the plan: 300-second p95, 512 MiB growing WAL, 70%
NiFi queue utilization, 100 files/table/hour, 1 MiB median file size, and 85%
disk use. Tune them only from committed benchmark evidence and record why.

Correlation IDs, object URIs, error text, and business keys are forbidden as
Prometheus labels.
