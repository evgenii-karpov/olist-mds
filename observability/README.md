# Local observability stack

This directory owns telemetry for the MySQL, CDC, Spark, Iceberg, ClickHouse
and Airflow services.

Prometheus collects native metrics and metrics from `target-probe` and
Kafka exporter. Alertmanager handles firing and resolved notifications.
Grafana reads Prometheus and Loki. Alloy sends Docker logs to Loki.

Start and validate the stack with:

```powershell
docker compose --profile platform --profile streaming --profile serving --profile observability --profile logs up -d --build --wait
uv run python scripts/ci/validate_observability_contract.py
$env:PYTHONPATH='.'
uv run pytest -q tests/observability
```

The service URLs and operational checks are documented in
`docs/observability.md`.
