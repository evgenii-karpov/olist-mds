# MySQL Debezium and Apicurio bootstrap

`olist-mysql-cdc.json` is the secret-free connector contract. It captures only
the eight `olist_oltp` business tables, keeps the complete Debezium envelope,
and uses only the heartbeat topic router SMT. Both key and value converters
emit Confluent-framed Avro and register artifacts in the `olist_cdc` Apicurio
group.

`bootstrap.py` is deliberately standard-library-only. It first creates the
`olist_cdc` Registry v3 group and its group-level
`COMPATIBILITY=BACKWARD_TRANSITIVE` rule, then reads the MySQL CDC password from
a file and inserts `database.password` only into the in-memory request body.
Registration is idempotent. `database.password` is sent only in the create
`POST /connectors` body; an existing connector is checked without comparing or
printing its password. Non-secret config drift causes a failure instead of a
secret-bearing PUT, delete, or resnapshot. After create or idempotent reuse,
bootstrap polls until both the connector and task 0 are `RUNNING`; `FAILED`
stops immediately, while `PAUSED`, `UNASSIGNED`, `RESTARTING`, and an empty task
list are bounded by the readiness timeout. Secret-bearing HTTP failures never
include the response body, and literal plus JSON-escaped secret variants are
redacted from status and transport diagnostics.

`apicurio-contract.json` also fixes SQL/PostgreSQL storage and the two `_FILE`
credential inputs. If the selected Registry image does not expand `_FILE`
itself, `apicurio-file-env.sh` is a no-echo entrypoint wrapper that exports the
two values only into the Registry process environment.

```text
python -m streaming.connect.bootstrap \
  --password-file /run/secrets/mysql_cdc_reader_password
```

The integration join must mount that secret file, make Kafka Connect available
at `http://kafka-connect:8083`, and run topic bootstrap before Connect starts.
No connector credential belongs in Compose environment, the connector JSON,
logs, or diagnostic reports.
