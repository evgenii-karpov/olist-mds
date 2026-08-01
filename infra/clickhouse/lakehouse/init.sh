#!/usr/bin/env bash
set -euo pipefail
set +x

: "${CLICKHOUSE_HOST:=clickhouse}"
: "${CLICKHOUSE_PORT:=9000}"
: "${CLICKHOUSE_USER:=olist}"
: "${CLICKHOUSE_PASSWORD_FILE:=/run/secrets/clickhouse_password}"

read_secret() {
    local path="$1"
    local label="$2"
    local value
    [[ -r "${path}" ]] || {
        printf '%s file is not readable\n' "${label}" >&2
        exit 1
    }
    value="$(<"${path}")"
    value="${value%$'\r'}"
    [[ -n "${value}" && "${value}" != *$'\n'* && "${value}" != *$'\r'* ]] || {
        printf '%s file must contain exactly one non-empty line\n' "${label}" >&2
        exit 1
    }
    printf '%s' "${value}"
}

xml_escape() {
    sed \
        -e 's/&/\&amp;/g' \
        -e 's/</\&lt;/g' \
        -e 's/>/\&gt;/g' \
        -e 's/"/\&quot;/g' \
        -e "s/'/\\&apos;/g"
}

password="$(read_secret "${CLICKHOUSE_PASSWORD_FILE}" 'ClickHouse password')"
config_file="$(mktemp)"
trap 'rm -f "${config_file}"' EXIT HUP INT TERM
chmod 0600 "${config_file}"
escaped_host="$(printf '%s' "${CLICKHOUSE_HOST}" | xml_escape)"
escaped_port="$(printf '%s' "${CLICKHOUSE_PORT}" | xml_escape)"
escaped_user="$(printf '%s' "${CLICKHOUSE_USER}" | xml_escape)"
escaped_password="$(printf '%s' "${password}" | xml_escape)"
printf '<clickhouse><host>%s</host><port>%s</port><user>%s</user><password>%s</password></clickhouse>\n' \
    "${escaped_host}" "${escaped_port}" "${escaped_user}" "${escaped_password}" \
    >"${config_file}"
unset password escaped_host escaped_port escaped_user escaped_password

for ddl in \
    001_create_databases.sql \
    002_create_serving_control.sql \
    003_create_event_tables.sql \
    004_create_current_version_tables.sql \
    005_create_stable_current_views.sql; do
    clickhouse-client --config-file "${config_file}" --multiquery \
        <"/opt/olist/lakehouse/${ddl}"
done

exec bash /opt/olist/lakehouse/bootstrap-catalog.sh
