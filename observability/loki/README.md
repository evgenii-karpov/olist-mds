# Loki

Loki runs as a local single-process service with filesystem storage in a named
Compose volume. Grafana reads it as a log data source.

The host endpoint is intended for local diagnostics. Remove the named volume
only when local log evidence is no longer needed.
