# MySQL source

This directory defines the local MySQL 8.4 source.

- `olist_oltp` contains the Olist business tables. The connector captures
  the eight keyed entities and excludes `geolocation`.
- `olist_simulator` contains deterministic fixture and workload state.

The initialization scripts are mounted read-only at
`/docker-entrypoint-initdb.d`. The source uses these secret files:

```text
/run/secrets/mysql_admin_password
/run/secrets/mysql_simulator_password
/run/secrets/mysql_cdc_reader_password
```

Application code uses the simulator user, schema setup uses the admin user and
Kafka Connect uses the CDC reader user. The source schema preserves Olist
column spellings such as `product_name_lenght`. Business timestamps use
UTC semantics, money uses `DECIMAL(18,2)` and coordinates use
`DECIMAL(18,14)`.
