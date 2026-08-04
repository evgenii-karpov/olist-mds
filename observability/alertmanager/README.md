# Alertmanager

The local Alertmanager route sends firing and resolved notifications to the
repository-owned target-probe webhook. This keeps the acceptance path
secret-free while proving that Prometheus rules reach Alertmanager and that
resolved transitions are delivered.

Production notification credentials do not belong in this file. Use
`docs/runbooks/cdc-alert-testing.md` for bounded fire/resolve checks.
