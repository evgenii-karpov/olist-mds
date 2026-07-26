#!/usr/bin/env bash
set -euo pipefail

: "${AIRFLOW_POSTGRES_DB:=airflow}"
: "${AIRFLOW_POSTGRES_USER:=airflow}"
: "${CONTROL_POSTGRES_DB:=olist_control}"
: "${CONTROL_POSTGRES_USER:=olist_control}"
: "${CONTROL_POSTGRES_PASSWORD_FILE:=/run/secrets/control_postgres_password}"

control_password="$(<"${CONTROL_POSTGRES_PASSWORD_FILE}")"
control_password="${control_password%$'\r'}"

export PGPASSWORD="$(<"${AIRFLOW_POSTGRES_PASSWORD_FILE}")"
PGPASSWORD="${PGPASSWORD%$'\r'}"

until pg_isready \
  --host "${AIRFLOW_POSTGRES_HOST}" \
  --port "${AIRFLOW_POSTGRES_PORT}" \
  --username "${AIRFLOW_POSTGRES_USER}" \
  --dbname "${AIRFLOW_POSTGRES_DB}"; do
  sleep 1
done

role_exists="$(
  psql \
    --host "${AIRFLOW_POSTGRES_HOST}" \
    --port "${AIRFLOW_POSTGRES_PORT}" \
    --username "${AIRFLOW_POSTGRES_USER}" \
    --dbname "${AIRFLOW_POSTGRES_DB}" \
    --tuples-only \
    --no-align \
    --command "select 1 from pg_roles where rolname = '${CONTROL_POSTGRES_USER}'"
)"

if [[ "${role_exists}" != "1" ]]; then
  psql \
    --host "${AIRFLOW_POSTGRES_HOST}" \
    --port "${AIRFLOW_POSTGRES_PORT}" \
    --username "${AIRFLOW_POSTGRES_USER}" \
    --dbname "${AIRFLOW_POSTGRES_DB}" \
    --command "create role ${CONTROL_POSTGRES_USER} login password '${control_password}'"
else
  psql \
    --host "${AIRFLOW_POSTGRES_HOST}" \
    --port "${AIRFLOW_POSTGRES_PORT}" \
    --username "${AIRFLOW_POSTGRES_USER}" \
    --dbname "${AIRFLOW_POSTGRES_DB}" \
    --command "alter role ${CONTROL_POSTGRES_USER} with login password '${control_password}'"
fi

db_exists="$(
  psql \
    --host "${AIRFLOW_POSTGRES_HOST}" \
    --port "${AIRFLOW_POSTGRES_PORT}" \
    --username "${AIRFLOW_POSTGRES_USER}" \
    --dbname "${AIRFLOW_POSTGRES_DB}" \
    --tuples-only \
    --no-align \
    --command "select 1 from pg_database where datname = '${CONTROL_POSTGRES_DB}'"
)"

if [[ "${db_exists}" != "1" ]]; then
  psql \
    --host "${AIRFLOW_POSTGRES_HOST}" \
    --port "${AIRFLOW_POSTGRES_PORT}" \
    --username "${AIRFLOW_POSTGRES_USER}" \
    --dbname "${AIRFLOW_POSTGRES_DB}" \
    --command "create database ${CONTROL_POSTGRES_DB} owner ${CONTROL_POSTGRES_USER}"
fi

psql \
  --host "${AIRFLOW_POSTGRES_HOST}" \
  --port "${AIRFLOW_POSTGRES_PORT}" \
  --username "${AIRFLOW_POSTGRES_USER}" \
  --dbname "${CONTROL_POSTGRES_DB}" \
  --set "control_user=${CONTROL_POSTGRES_USER}" \
  --file /opt/olist/control-postgres/initdb/001_create_schemas.sql \
  --file /opt/olist/control-postgres/initdb/002_create_batch_control_tables.sql \
  --file /opt/olist/control-postgres/initdb/003_create_cdc_control_tables.sql \
  --file /opt/olist/control-postgres/initdb/004_create_cdc_transform_control_tables.sql \
  --file /opt/olist/control-postgres/initdb/999_grant_control_role.sql
