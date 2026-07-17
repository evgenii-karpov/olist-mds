# Loki

The local single-process Loki uses filesystem TSDB storage in a named Compose
volume and retains data for 168 hours. Authentication is disabled only inside
the local Compose lab; the host port is for developer diagnostics and must not
be exposed outside the workstation.

Grafana provisions Loki as a non-default datasource. Clear the named Loki
volume only when the operator explicitly intends to discard local evidence.
