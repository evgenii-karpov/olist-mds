#!/usr/bin/env bash
set -euo pipefail
set +x

: "${APICURIO_DB_USERNAME_FILE:=/run/secrets/apicurio_db_user}"
: "${APICURIO_DB_PASSWORD_FILE:=/run/secrets/apicurio_db_password}"
: "${PGHOST:=platform-postgres}"
: "${PGPORT:=5432}"
: "${POSTGRES_USER:=airflow}"

read_secret() {
    local path="$1"
    local label="$2"
    local value
    [[ -r "${path}" ]] || {
        printf '%s secret is not readable\n' "${label}" >&2
        exit 1
    }
    value="$(<"${path}")"
    value="${value%$'\r'}"
    [[ -n "${value}" && "${value}" != *$'\n'* && "${value}" != *$'\r'* ]] || {
        printf '%s secret must contain exactly one non-empty line\n' "${label}" >&2
        exit 1
    }
    printf '%s' "${value}"
}

sql_literal() {
    local value="$1"
    value="${value//\\/\\\\}"
    value="${value//\'/\'\'}"
    printf "'%s'" "${value}"
}

database_user="$(read_secret "${APICURIO_DB_USERNAME_FILE}" 'Apicurio database username')"
database_password="$(read_secret "${APICURIO_DB_PASSWORD_FILE}" 'Apicurio database password')"
user_literal="$(sql_literal "${database_user}")"
password_literal="$(sql_literal "${database_password}")"

sql_file="$(mktemp)"
trap 'rm -f "${sql_file}"' EXIT HUP INT TERM
chmod 0600 "${sql_file}"
{
    printf "\\set apicurio_user %s\n" "${user_literal}"
    printf "\\set apicurio_password %s\n" "${password_literal}"
    cat <<'SQL'
SELECT format(
    'CREATE ROLE %I LOGIN PASSWORD %L',
    :'apicurio_user',
    :'apicurio_password'
)
WHERE NOT EXISTS (
    SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = :'apicurio_user'
) \gexec

SELECT format(
    'ALTER ROLE %I WITH LOGIN PASSWORD %L',
    :'apicurio_user',
    :'apicurio_password'
) \gexec

SELECT format(
    'CREATE DATABASE apicurio OWNER %I ENCODING %L TEMPLATE template0',
    :'apicurio_user',
    'UTF8'
)
WHERE NOT EXISTS (
    SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'apicurio'
) \gexec

SELECT format('GRANT CONNECT ON DATABASE apicurio TO %I', :'apicurio_user') \gexec
SQL
} >"${sql_file}"

psql --set=ON_ERROR_STOP=1 \
    --username "${POSTGRES_USER}" \
    --dbname postgres \
    --file "${sql_file}" >/dev/null

printf '%s\n' 'Apicurio PostgreSQL database and role are ready.'
