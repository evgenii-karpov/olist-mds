#!/usr/bin/env sh
set -eu

: "${AIRFLOW_POSTGRES_PASSWORD_FILE:=}"

if [ -n "${AIRFLOW_POSTGRES_PASSWORD_FILE}" ] && [ -r "${AIRFLOW_POSTGRES_PASSWORD_FILE}" ]; then
    PGPASSWORD="$(sed -e 's/[[:space:]]*$//' "${AIRFLOW_POSTGRES_PASSWORD_FILE}")"
    export PGPASSWORD
fi

read_secret() {
    variable_name=$1
    eval "secret_path=\${${variable_name}:-}"
    test -n "${secret_path}" || {
        echo "${variable_name} is required" >&2
        exit 1
    }
    test -f "${secret_path}" || {
        echo "secret file configured by ${variable_name} is missing" >&2
        exit 1
    }
    value=$(sed -e 's/[[:space:]]*$//' "${secret_path}")
    test -n "${value}" || {
        echo "secret file configured by ${variable_name} is empty" >&2
        exit 1
    }
    printf '%s' "${value}"
}

polaris_db_user=$(read_secret POLARIS_DB_USERNAME_FILE)
polaris_db_password=$(read_secret POLARIS_DB_PASSWORD_FILE)

psql --set=ON_ERROR_STOP=1 \
    --username "${POSTGRES_USER}" \
    --dbname "${POSTGRES_DB}" \
    --set=polaris_user="${polaris_db_user}" \
    --set=polaris_password="${polaris_db_password}" <<'SQL'
SELECT format(
    'CREATE ROLE %I LOGIN PASSWORD %L',
    :'polaris_user',
    :'polaris_password'
)
WHERE NOT EXISTS (
    SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = :'polaris_user'
) \gexec

SELECT format(
    'ALTER ROLE %I WITH LOGIN PASSWORD %L',
    :'polaris_user',
    :'polaris_password'
) \gexec

SELECT format(
    'CREATE DATABASE polaris OWNER %I ENCODING %L TEMPLATE template0',
    :'polaris_user',
    'UTF8'
)
WHERE NOT EXISTS (
    SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'polaris'
) \gexec

SELECT format('GRANT CONNECT ON DATABASE polaris TO %I', :'polaris_user') \gexec
SQL
