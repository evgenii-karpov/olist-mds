#!/usr/bin/env bash
set -euo pipefail
set +x

# The official PostgreSQL entrypoint only runs its init directory for a brand
# new data volume.  This bounded, repeatable companion keeps the four-database
# control-plane contract true after an ordinary restart as well.

: "${PLATFORM_POSTGRES_HOST:=platform-postgres}"
: "${PLATFORM_POSTGRES_PORT:=5432}"
: "${POSTGRES_USER:=airflow}"
: "${POSTGRES_DB:=airflow}"
: "${AIRFLOW_POSTGRES_PASSWORD_FILE:=/run/secrets/airflow_postgres_password}"
: "${APICURIO_DB_USERNAME_FILE:=/run/secrets/apicurio_db_user}"
: "${APICURIO_DB_PASSWORD_FILE:=/run/secrets/apicurio_db_password}"

until pg_isready \
    --host "${PLATFORM_POSTGRES_HOST}" \
    --port "${PLATFORM_POSTGRES_PORT}" \
    --username "${POSTGRES_USER}" \
    --dbname "${POSTGRES_DB}" >/dev/null; do
    sleep 1
done

export PGPASSWORD="$(<"${AIRFLOW_POSTGRES_PASSWORD_FILE}")"

export PGHOST="${PLATFORM_POSTGRES_HOST}"
export PGPORT="${PLATFORM_POSTGRES_PORT}"

bash /opt/olist/platform-postgres/create-apicurio-database.sh

export AIRFLOW_POSTGRES_HOST="${PLATFORM_POSTGRES_HOST}"
export AIRFLOW_POSTGRES_PORT="${PLATFORM_POSTGRES_PORT}"
export AIRFLOW_POSTGRES_DB="${POSTGRES_DB}"
export AIRFLOW_POSTGRES_USER="${POSTGRES_USER}"
export AIRFLOW_POSTGRES_PASSWORD_FILE

printf '%s\n' 'Platform PostgreSQL and Apicurio databases are ready.'
