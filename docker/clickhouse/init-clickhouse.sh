#!/usr/bin/env bash
set -euo pipefail

clickhouse_password="$(tr -d '\r\n' < /run/secrets/clickhouse_password)"
clickhouse_client=(
  clickhouse-client
  --host clickhouse
  --port 9000
  --user "${CLICKHOUSE_USER:-olist}"
  --password "${clickhouse_password}"
)

wait_for_clickhouse() {
  local attempt
  for attempt in {1..30}; do
    if "${clickhouse_client[@]}" --query "SELECT 1" >/dev/null 2>&1; then
      return 0
    fi
    echo "Waiting for ClickHouse network endpoint clickhouse:9000 (${attempt}/30)"
    sleep 2
  done
  echo "ClickHouse network endpoint clickhouse:9000 did not become ready" >&2
  return 1
}

apply_file() {
  local file="$1"
  local attempt output status
  for attempt in {1..12}; do
    echo "Applying ClickHouse init file: ${file} (${attempt}/12)"
    set +e
    output="$("${clickhouse_client[@]}" --multiquery < "${file}" 2>&1)"
    status="$?"
    set -e
    if [[ "${status}" == "0" ]]; then
      return 0
    fi
    echo "${output}" >&2
    if [[ "${status}" != "210" && "${output}" != *"Code: 210"* ]]; then
      return "${status}"
    fi
    sleep 2
  done
  echo "ClickHouse init file failed after retrying network error 210: ${file}" >&2
  return 210
}

wait_for_clickhouse
for file in /opt/olist/clickhouse/initdb/*.sql; do
  apply_file "${file}"
done
