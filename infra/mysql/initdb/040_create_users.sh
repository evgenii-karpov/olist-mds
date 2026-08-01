#!/usr/bin/env bash
(
set -euo pipefail

read_secret() {
    local path="$1"
    local label="$2"
    local value

    if [[ ! -r "$path" ]]; then
        printf 'Required %s secret is not readable: %s\n' "$label" "$path" >&2
        return 1
    fi
    value="$(<"$path")"
    value="${value%$'\r'}"
    if [[ -z "$value" ]]; then
        printf 'Required %s secret is empty: %s\n' "$label" "$path" >&2
        return 1
    fi
    if [[ "$value" == *$'\n'* || "$value" == *$'\r'* ]]; then
        printf 'Required %s secret must contain exactly one line: %s\n' \
            "$label" "$path" >&2
        return 1
    fi
    printf '%s' "$value"
}

sql_string() {
    local value="$1"
    value="${value//\\/\\\\}"
    value="${value//\'/\'\'}"
    printf "'%s'" "$value"
}

main() {
    local admin_password
    local simulator_password
    local cdc_reader_password
    local root_password
    local admin_password_sql
    local simulator_password_sql
    local cdc_reader_password_sql
    local -a mysql_args

    admin_password="$(
        read_secret \
            "${MYSQL_ADMIN_PASSWORD_FILE:-/run/secrets/mysql_admin_password}" \
            'MySQL admin password'
    )"
    simulator_password="$(
        read_secret \
            "${MYSQL_SIMULATOR_PASSWORD_FILE:-/run/secrets/mysql_simulator_password}" \
            'MySQL simulator password'
    )"
    cdc_reader_password="$(
        read_secret \
            "${MYSQL_CDC_READER_PASSWORD_FILE:-/run/secrets/mysql_cdc_reader_password}" \
            'MySQL CDC reader password'
    )"

    root_password="${MYSQL_ROOT_PASSWORD:-}"
    if [[ -z "$root_password" && -n "${MYSQL_ROOT_PASSWORD_FILE:-}" ]]; then
        root_password="$(
            read_secret "$MYSQL_ROOT_PASSWORD_FILE" 'MySQL root password'
        )"
    fi

    admin_password_sql="$(sql_string "$admin_password")"
    simulator_password_sql="$(sql_string "$simulator_password")"
    cdc_reader_password_sql="$(sql_string "$cdc_reader_password")"

    mysql_args=(--protocol=socket --user=root --batch --skip-column-names)
    if [[ -n "$root_password" ]]; then
        export MYSQL_PWD="$root_password"
    fi

    mysql "${mysql_args[@]}" <<SQL
CREATE USER IF NOT EXISTS 'olist_admin'@'%' IDENTIFIED BY ${admin_password_sql};
ALTER USER 'olist_admin'@'%' IDENTIFIED BY ${admin_password_sql};

CREATE USER IF NOT EXISTS 'olist_simulator'@'%' IDENTIFIED BY ${simulator_password_sql};
ALTER USER 'olist_simulator'@'%' IDENTIFIED BY ${simulator_password_sql};

CREATE USER IF NOT EXISTS 'olist_cdc_reader'@'%' IDENTIFIED BY ${cdc_reader_password_sql};
ALTER USER 'olist_cdc_reader'@'%' IDENTIFIED BY ${cdc_reader_password_sql};

GRANT ALL PRIVILEGES ON olist_oltp.* TO 'olist_admin'@'%';
GRANT ALL PRIVILEGES ON olist_simulator.* TO 'olist_admin'@'%';

GRANT SELECT, INSERT, UPDATE, DELETE ON olist_oltp.* TO 'olist_simulator'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON olist_simulator.* TO 'olist_simulator'@'%';

GRANT RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.*
    TO 'olist_cdc_reader'@'%';
GRANT SELECT, LOCK TABLES ON olist_oltp.* TO 'olist_cdc_reader'@'%';
GRANT INSERT, UPDATE ON olist_simulator.heartbeats TO 'olist_cdc_reader'@'%';
# SELECT is required separately for MySQL's ON DUPLICATE KEY UPDATE evaluation.
GRANT SELECT ON olist_simulator.heartbeats TO 'olist_cdc_reader'@'%';
SQL

    unset MYSQL_PWD
}

main "$@"
)
