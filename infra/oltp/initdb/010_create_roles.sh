#!/usr/bin/env bash
set -euo pipefail

simulator_password="$(cat /run/secrets/oltp_simulator_password)"
reader_password="$(cat /run/secrets/oltp_cdc_reader_password)"

psql --set=ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  --set=simulator_password="$simulator_password" \
  --set=reader_password="$reader_password" <<'SQL'
SELECT format(
  'CREATE ROLE olist_simulator LOGIN PASSWORD %L',
  :'simulator_password'
) WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'olist_simulator') \gexec

SELECT format(
  'CREATE ROLE olist_cdc_reader LOGIN PASSWORD %L',
  :'reader_password'
) WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'olist_cdc_reader') \gexec

ALTER ROLE olist_cdc_reader WITH REPLICATION;
SQL
