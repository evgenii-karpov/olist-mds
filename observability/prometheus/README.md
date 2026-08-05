# Prometheus

Prometheus scrapes native service endpoints, Kafka exporter and the local
`target-probe` exporter. Recording and alert rules use the
`olist_` metric namespace and bounded service, topic and connector labels.

Business keys, object locations, exception text and secret values never appear
as metric labels. Validate the configuration with `promtool` or the
repository observability contract command.
