# Local observability

The local telemetry path covers the CDC runtime and the serving services:

```text
target-probe and native exporters
  -> Prometheus
  -> Alertmanager and Grafana
Docker logs -> Alloy -> Loki -> Grafana
```

## Services

- `target-probe` exposes bounded health, control and serving metrics.
- Kafka exporter exposes topic and consumer-position metrics.
- Prometheus scrapes runtime endpoints and evaluates recording and alert
  rules.
- Alertmanager routes firing and resolved alerts to the local probe endpoint.
- Grafana provisions Prometheus and Loki data sources and operational views.
- Alloy reads Docker logs and sends them to Loki.

All services run locally through the `observability` and `logs` Compose
profiles. The default endpoints are:

| Service | URL |
| --- | --- |
| Prometheus | `http://localhost:9090` |
| Alertmanager | `http://localhost:9093` |
| Grafana | `http://localhost:3000` |
| Loki | `http://localhost:3100` |
| Alloy | `http://localhost:12345` |
| target-probe | `http://localhost:9108` |

## Start and validate

```powershell
docker compose --profile platform --profile streaming --profile serving --profile observability --profile logs up -d --build --wait
uv run python scripts/ci/validate_observability_contract.py
$env:PYTHONPATH='.'
uv run pytest -q tests/observability
```

Validate the configuration files independently:

```powershell
docker run --rm --entrypoint promtool -v "$PWD:/workspace:ro" prom/prometheus:v3.5.0 check config /workspace/observability/prometheus/prometheus.yml
docker run --rm --entrypoint amtool -v "$PWD:/workspace:ro" prom/alertmanager:v0.30.0 check-config /workspace/observability/alertmanager/alertmanager.yml
```

The CDC acceptance runner does not start telemetry services. Use
[`docs/runbooks/cdc-alert-testing.md`](runbooks/cdc-alert-testing.md) for
fire/resolve checks and the service runbook for recovery.
