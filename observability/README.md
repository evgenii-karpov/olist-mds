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

The GCP serving contour uses the same Prometheus/Grafana stack. Its
credential-free metric contract and renderer live in
`scripts/observability/gcp_metrics.py`; cloud runs may export bounded JSON
evidence and render it through that contract. The `lakehouse-serving`
dashboard and `gcp-serving-recording.yml` already reserve panels and recording
rules for offsets/lag, Spark batches/checkpoints, dbt candidates, publication
conflicts, BigQuery bytes/cap rejections, and BigLake errors. They remain
empty until a real GCP run supplies those metrics.
