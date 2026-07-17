# CDC service restart

Use this procedure for Connect, NiFi, registry, or object-store availability
alerts. Do not remove volumes, Connect offsets, the publication, or the
replication slot.

1. Record the active alert, Kafka lag, slot WAL, offset gaps, and latest ingest
   and transform timestamps in Grafana.
2. Inspect bounded logs: `docker compose logs --no-color --tail=300 <service>`.
3. Restart only the affected service with
   `docker compose --profile realtime-core up -d --wait <service>`.
4. For a failed connector task run
   `uv run python scripts/cdc/stage2_admin.py restart-failed`.
5. Confirm connector/task health, heartbeat recovery, draining lag, a decreasing
   or stable retained-WAL value, and zero unexplained offset gaps.
6. Confirm the alert resolves. If it does not, keep the evidence and stop; never
   delete durable state as a health-check shortcut.

Exercise a bounded alert transition with
`uv run python scripts/cdc/failure_injection.py --scenario connect --execute`.
