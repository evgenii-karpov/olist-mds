# Grafana Alloy

Alloy discovers local Docker containers through a read-only Docker socket and
forwards Docker-decoded logs to the real Loki service. It attaches only the
bounded `environment` and `service` labels. Correlation IDs, business keys,
object URIs and error messages remain in log bodies and are never labels.

The service exposes its own readiness and metrics endpoint on port `12345` and
has no authority to start, stop or mutate containers.
