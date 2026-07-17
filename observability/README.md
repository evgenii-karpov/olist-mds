# Realtime observability assets

This directory owns the complete local Phase 6 telemetry stack: Prometheus,
Alertmanager, Grafana, PostgreSQL/Kafka/NiFi/pipeline exporters, node exporter,
cAdvisor, Airflow StatsD, Loki, and Alloy. Runtime image versions are pinned in
`streaming/runtime-versions.json`.

The local stack uses stable committed development-only Docker secrets. Build
the custom runtime images and start the three explicit profiles:

```powershell
$env:AIRFLOW_STATSD_ON="true"
docker compose --profile realtime-core build airflow kafka-connect minio nifi
docker compose --profile realtime-core --profile observability --profile logs up -d --wait
```

Grafana is on `http://localhost:3000`, Prometheus on `http://localhost:9090`,
Alertmanager on `http://localhost:9093`, and Loki on `http://localhost:3100`.
Grafana credentials come from the local Docker secret contract. Loki retains local logs
for seven days. Alloy labels only `environment` and `service`; correlation IDs
remain in log bodies to avoid unbounded cardinality.

Run `uv run python scripts/ci/validate_stage6_configuration.py` after changing
dashboards, alerts, log labels, retention, or runbook links.
