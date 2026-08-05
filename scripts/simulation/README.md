# MySQL fixture simulator

The simulator seeds the local Olist fixture and can generate deterministic
source changes in MySQL. Its commands are `seed`, `run`,
`replay`, `status` and `stop`.

For the normal local path, use `local_lab.py bootstrap`, which prepares
the fixture and registers CDC. Use the module directly when a simulator
operation needs to be inspected:

```text
uv run python -m scripts.simulation seed --archive tests/fixtures/olist_small/olist_small.zip --random-seed 101 --password-file /run/secrets/mysql_simulator_password
uv run python -m scripts.simulation run --random-seed 20260716 --event-limit 20 --rate 5 --password-file /run/secrets/mysql_simulator_password
```

Connection settings come from `MYSQL_HOST`, `MYSQL_PORT` and
`MYSQL_DATABASE`. The password is read from `MYSQL_PASSWORD_FILE`.
Logs are JSON and never contain secret values.

Seed order follows the MySQL foreign-key constraints. Every simulator action
uses an explicit transaction and records its status in
`olist_simulator.simulation_runs`.
