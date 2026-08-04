#!/usr/bin/env bash
set -euo pipefail

# Load non-secret local overrides, then resolve only *_FILE secret sources.
# Credentials are deliberately file-only in the target runtime; cloud secret
# providers and legacy warehouse defaults do not belong in this wrapper.
ENV_FILE="/opt/airflow/project/.env"

if [[ -f "${ENV_FILE}" ]]; then
  while IFS='=' read -r key value; do
    key="${key%$'\r'}"
    value="${value%$'\r'}"
    key="${key#export }"

    if [[ -z "${key}" || "${key}" == \#* ]]; then
      continue
    fi

    if [[ "${#value}" -ge 2 && "${value:0:1}" == '"' && "${value: -1}" == '"' ]]; then
      value="${value:1:${#value}-2}"
    elif [[ "${#value}" -ge 2 && "${value:0:1}" == "'" && "${value: -1}" == "'" ]]; then
      value="${value:1:${#value}-2}"
    fi

    if [[ "${key}" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
      export "${key}=${value}"
    fi
  done < "${ENV_FILE}"
fi

resolve_secret_file() {
  local base_name="$1"
  local current_value="${!base_name:-}"
  local file_var_name="${base_name}_FILE"
  local file_path="${!file_var_name:-}"

  if [[ -n "${current_value}" ]]; then
    echo "Plaintext secret environment variable ${base_name} is not supported; use ${base_name}_FILE" >&2
    exit 1
  fi
  if [[ -z "${file_path}" ]]; then
    return 0
  fi
  if [[ ! -f "${file_path}" ]]; then
    echo "Secret file not found for ${base_name}: ${file_path}" >&2
    exit 1
  fi

  local file_value
  file_value="$(<"${file_path}")"
  file_value="${file_value%$'\r'}"
  if [[ -z "${file_value}" || "${file_value}" == *$'\n'* || "${file_value}" == *$'\r'* ]]; then
    echo "Secret file for ${base_name} must contain one non-empty line" >&2
    exit 1
  fi
  export "${base_name}=${file_value}"
}

while IFS='=' read -r key _; do
  case "${key}" in
    *_FILE)
      resolve_secret_file "${key%_FILE}"
      ;;
  esac
done < <(env)

: "${PYTHONPATH:=/opt/airflow/project}"
export PYTHONPATH

exec "$@"
