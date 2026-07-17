# Alertmanager

The local receiver intentionally keeps routing secret-free. Every Prometheus
alert includes a repository runbook annotation; production notification
credentials belong in an external secret provider, not this file.

Use `docs/runbooks/cdc-alert-testing.md` to exercise `firing -> resolved`
transitions against a disposable stack.
