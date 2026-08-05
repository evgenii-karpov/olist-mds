# Debezium connector bootstrap

`olist-mysql-cdc.json` is the secret-free connector contract. It captures
the eight keyed `olist_oltp` entities and publishes Confluent-framed Avro
keys and values to Kafka with Apicurio Registry.

`bootstrap.py` creates the `olist_cdc` Registry group, applies the
compatibility rule, reads the MySQL CDC password from a file and registers the
connector. It never prints or compares the password. Existing non-secret
configuration drift fails closed.

Use the helper after Kafka topics and Connect are available:

```text
python -m streaming.connect.bootstrap --password-file /run/secrets/mysql_cdc_reader_password
```

Connect must be reachable at `http://kafka-connect:8083`. Connector
credentials belong in secret files, not Compose environment values or logs.
