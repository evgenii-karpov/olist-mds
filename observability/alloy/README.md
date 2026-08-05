# Grafana Alloy

Alloy discovers local Compose containers through a read-only Docker socket and
sends their logs to Loki. It attaches only bounded `environment` and
`service` labels.

Business keys, object locations and exception text remain in log bodies. Alloy
does not start, stop or mutate containers.
