#!/usr/bin/env bash
set -euo pipefail
set +x

: "${POLARIS_PRINCIPAL_ID_FILE:?POLARIS_PRINCIPAL_ID_FILE is required}"
: "${POLARIS_PRINCIPAL_SECRET_FILE:?POLARIS_PRINCIPAL_SECRET_FILE is required}"
: "${CLICKHOUSE_PASSWORD_FILE:?CLICKHOUSE_PASSWORD_FILE is required}"

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

template_path="${CLICKHOUSE_CATALOG_TEMPLATE:-/lakehouse/catalog.sql.template}"
clickhouse_host="${CLICKHOUSE_HOST:-clickhouse}"
clickhouse_port="${CLICKHOUSE_PORT:-9000}"
clickhouse_user="${CLICKHOUSE_USER:-olist}"

principal_id="$(
    read_single_line_secret "${POLARIS_PRINCIPAL_ID_FILE}" 'Polaris principal id'
)"
principal_secret="$(
    read_single_line_secret "${POLARIS_PRINCIPAL_SECRET_FILE}" 'Polaris principal secret'
)"
clickhouse_password="$(
    read_single_line_secret "${CLICKHOUSE_PASSWORD_FILE}" 'ClickHouse password'
)"

catalog_credential="${principal_id}:${principal_secret}"
catalog_credential_hex="$(printf '%s' "${catalog_credential}" | od -An -tx1 | tr -d ' \n')"
case "${catalog_credential_hex}" in
    ''|*[!0-9a-f]*)
        echo "failed to encode Polaris catalog credential" >&2
        exit 1
        ;;
esac
catalog_credential_escaped="$(printf '%s' "${catalog_credential_hex}" | sed 's/../\\x&/g')"
catalog_sql="$(<"${template_path}")"
catalog_sql="${catalog_sql//__POLARIS_CATALOG_CREDENTIAL_ESCAPED__/${catalog_credential_escaped}}"

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
escaped_clickhouse_password="$(printf '%s' "${clickhouse_password}" | xml_escape)"
escaped_clickhouse_host="$(printf '%s' "${clickhouse_host}" | xml_escape)"
escaped_clickhouse_port="$(printf '%s' "${clickhouse_port}" | xml_escape)"
escaped_clickhouse_user="$(printf '%s' "${clickhouse_user}" | xml_escape)"
printf '<clickhouse><host>%s</host><port>%s</port><user>%s</user><password>%s</password></clickhouse>\n' \
    "${escaped_clickhouse_host}" \
    "${escaped_clickhouse_port}" \
    "${escaped_clickhouse_user}" \
    "${escaped_clickhouse_password}" > "${client_config}"

# The credential is sent over stdin, never as a process argument or a file.
printf '%s\n' "${catalog_sql}" | clickhouse-client \
    --config-file "${client_config}" \
    --multiquery

unset \
    principal_id \
    principal_secret \
    clickhouse_password \
    escaped_clickhouse_host \
    escaped_clickhouse_port \
    escaped_clickhouse_user \
    escaped_clickhouse_password \
    catalog_credential \
    catalog_credential_hex \
    catalog_credential_escaped \
    catalog_sql
