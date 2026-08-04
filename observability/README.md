# Target observability stack

This directory owns the target telemetry chain for MySQL, Debezium/Kafka
Connect, Kafka, Spark/Iceberg, MinIO, Polaris, ClickHouse serving, Airflow and
the observability services themselves. It deliberately has no retired source
or phantom exporter targets.

The bounded `target-probe` service owns health and domain metrics for components
that do not expose a stable Prometheus endpoint. It reads only bounded status
and control-plane fields; credentials are provided through Compose secret files
and are never emitted as labels or log values. Kafka exporter provides target
partition end offsets; Spark Bronze publishes checkpoint end offsets and the
probe computes scoped lag from the two real sources. Recording rules allowlist
target topics and the fixed Bronze owner.

Start the observability stack separately from the Stage V E2E harness:

```powershell
$env:COMPOSE_PROJECT_NAME="olist_observability_l2"
docker compose --profile platform --profile streaming --profile serving `
  --profile observability --profile logs up -d --build --wait
```

The local endpoints are Prometheus `http://localhost:9090`, Alertmanager
`http://localhost:9093`, Grafana `http://localhost:3000`, Loki
`http://localhost:3100`, Alloy `http://localhost:12345` and the target probe
`http://localhost:9108`.

Run the static contract validator before any live acceptance check:

```powershell
uv run python scripts/ci/validate_observability_contract.py
```

The bounded failure-injection helper uses real target service names and the
`olist_observability_l2` project. It stops only the named service and never
removes volumes unless an operator explicitly runs a separate cleanup command.
