# Prometheus

Prometheus scrapes native metrics from Prometheus, Alertmanager, Grafana, Loki,
Alloy, MinIO and ClickHouse. The bounded `target-probe` service provides
MySQL/binlog, Kafka Connect, Apicurio, Spark, Polaris, Airflow, control-plane
and serving metrics. Kafka exporter provides target partition end offsets;
Spark Bronze checkpoint offsets are joined by `target-probe` into scoped lag,
which is recorded only for target topics and the fixed Bronze owner.

Every scrape target is a real Compose service or the explicitly owned
`target-probe` exporter. Recording and alert rules use the `olist_` namespace,
bounded labels and target connector/topic identities. Business keys, object
URIs, exception text and secret values are never labels.
