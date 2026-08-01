#!/usr/bin/env bash
set -euo pipefail
set +x

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

CLICKHOUSE_PASSWORD="$(
    read_single_line_secret "${CLICKHOUSE_PASSWORD_FILE}" 'ClickHouse password'
)"
export CLICKHOUSE_PASSWORD

project_dir="${DBT_PROJECT_DIR:-/opt/olist/dbt/olist_clickhouse}"
target="${DBT_TARGET:-local_clickhouse}"

exec dbt "$@" --project-dir "${project_dir}" --target "${target}"
