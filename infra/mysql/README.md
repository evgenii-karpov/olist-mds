# MySQL Olist source

This directory is the initialization contract for the disposable MySQL 8.4
source. The instance owns two databases:

- `olist_oltp` contains the nine Olist business tables. Debezium captures the
  eight keyed CDC entities and deliberately excludes `geolocation`.
- `olist_simulator` contains deterministic simulator state, seed identity,
  replay mappings, pending transitions, and the Debezium heartbeat target.

Mount `conf.d/olist.cnf` read-only below `/etc/mysql/conf.d/` and mount
`initdb/` read-only below `/docker-entrypoint-initdb.d/`. The user bootstrap
script expects these Docker secret paths unless their corresponding `_FILE`
variables override them:

```text
/run/secrets/mysql_admin_password
/run/secrets/mysql_simulator_password
/run/secrets/mysql_cdc_reader_password
```

The official image still receives the root credential through
`MYSQL_ROOT_PASSWORD_FILE`. Root is only used by the image entrypoint and the
first-volume bootstrap. Application code uses `olist_simulator`, schema
migrations use `olist_admin`, and Kafka Connect uses `olist_cdc_reader`.

The schema intentionally preserves the source column spellings such as
`product_name_lenght`. Business timestamps are UTC-semantic `DATETIME(6)`,
money is `DECIMAL(18,2)`, and coordinates are `DECIMAL(18,14)`.
