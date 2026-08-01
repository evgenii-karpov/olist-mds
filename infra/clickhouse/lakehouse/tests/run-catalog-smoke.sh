#!/usr/bin/env bash
set -euo pipefail
set +x

: "${CLICKHOUSE_PASSWORD_FILE:?CLICKHOUSE_PASSWORD_FILE is required}"
: "${ICEBERG_CUSTOMERS_SNAPSHOT_ID:?ICEBERG_CUSTOMERS_SNAPSHOT_ID is required}"

read_single_line_secret() {
    local path="$1"
    local label="$2"
    local value

    if [[ ! -r "${path}" ]]; then
        printf '%s file is not readable\n' "${label}" >&2
        return 1
    fi
    value="$(<"${path}")"
    value="${value%$'\r'}"
    if [[ -z "${value}" ]]; then
        printf '%s file must not be empty\n' "${label}" >&2
        return 1
    fi
    if [[ "${value}" == *$'\n'* || "${value}" == *$'\r'* ]]; then
        printf '%s file must contain exactly one line\n' "${label}" >&2
        return 1
    fi
    printf '%s' "${value}"
}

case "${ICEBERG_CUSTOMERS_SNAPSHOT_ID}" in
    ''|*[!0-9]*)
        echo "ICEBERG_CUSTOMERS_SNAPSHOT_ID must be an unsigned integer" >&2
        exit 1
        ;;
esac
if [[ "${ICEBERG_CUSTOMERS_SNAPSHOT_ID}" == "0" ]]; then
    echo "ICEBERG_CUSTOMERS_SNAPSHOT_ID must be positive" >&2
    exit 1
fi
clickhouse_host="${CLICKHOUSE_HOST:-clickhouse}"
clickhouse_port="${CLICKHOUSE_PORT:-9000}"
clickhouse_user="${CLICKHOUSE_USER:-olist}"
smoke_sql="${CLICKHOUSE_CATALOG_SMOKE_SQL:-/lakehouse/tests/catalog-smoke.sql.template}"
clickhouse_password="$(
    read_single_line_secret "${CLICKHOUSE_PASSWORD_FILE}" 'ClickHouse password'
)"

xml_escape() {
    sed \
        -e 's/&/\&amp;/g' \
        -e 's/</\&lt;/g' \
        -e 's/>/\&gt;/g' \
        -e 's/"/\&quot;/g' \
        -e "s/'/\\&apos;/g"
}

client_config="$(mktemp)"
trap 'rm -f "${client_config}"' EXIT
chmod 0600 "${client_config}"
escaped_password="$(printf '%s' "${clickhouse_password}" | xml_escape)"
escaped_host="$(printf '%s' "${clickhouse_host}" | xml_escape)"
escaped_port="$(printf '%s' "${clickhouse_port}" | xml_escape)"
escaped_user="$(printf '%s' "${clickhouse_user}" | xml_escape)"
printf '<clickhouse><host>%s</host><port>%s</port><user>%s</user><password>%s</password></clickhouse>\n' \
    "${escaped_host}" \
    "${escaped_port}" \
    "${escaped_user}" \
    "${escaped_password}" > "${client_config}"

catalog_tables="$(clickhouse-client \
    --config-file "${client_config}" \
    --query 'SHOW TABLES FROM lakehouse FORMAT TSVRaw')"
if ! printf '%s\n' "${catalog_tables}" | grep -Fx 'silver.customers_current' >/dev/null; then
    echo "lakehouse catalog does not expose silver.customers_current" >&2
    exit 1
fi

clickhouse-client \
    --config-file "${client_config}" \
    --multiquery < <(
        # ClickHouse 26.3 does not accept a query parameter inside a SETTINGS
        # expression.  The value was restricted to decimal digits above, so
        # this substitution cannot inject SQL while preserving the template.
        sed "s/{snapshot_id:UInt64}/${ICEBERG_CUSTOMERS_SNAPSHOT_ID}/g" "${smoke_sql}"
    )

unset \
    clickhouse_password \
    escaped_password \
    escaped_host \
    escaped_port \
    escaped_user \
    catalog_tables
