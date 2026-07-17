# Grafana Alloy

Alloy discovers local Docker containers and forwards Docker-decoded log entries
to Loki. It attaches only the stable `environment=local` and container-derived
`service` labels. `simulation_run_id`, `_event_id`, `cdc_run_id`, object URIs,
and error messages remain searchable in the log body and are never labels.

The Docker socket is mounted read-only; Alloy has no authority to start, stop,
or mutate containers.
