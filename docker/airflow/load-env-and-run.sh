#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="/opt/airflow/project/.env"
AWS_SECRET_FETCHER="/opt/airflow/project/scripts/utilities/fetch_aws_secret.py"

if [[ -f "${ENV_FILE}" ]]; then
  while IFS='=' read -r key value; do
    key="${key%$'\r'}"
    value="${value%$'\r'}"
    key="${key#export }"

    if [[ -z "${key}" || "${key}" == \#* ]]; then
      continue
    fi

    if [[ "${value}" == \"*\" && "${value}" == *\" ]]; then
      value="${value:1:${#value}-2}"
    elif [[ "${value}" == \'*\' && "${value}" == *\' ]]; then
      value="${value:1:${#value}-2}"
    fi

    if [[ "${key}" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
      export "${key}=${value}"
    fi
  done < "${ENV_FILE}"
fi

resolve_secret_env_var() {
  local base_name="$1"
  local current_value="${!base_name:-}"
  local file_var_name="${base_name}_FILE"
  local secret_id_var_name="${base_name}_AWS_SECRET_ID"
  local secret_field_var_name="${base_name}_AWS_SECRET_FIELD"
  local file_path="${!file_var_name:-}"
  local secret_id="${!secret_id_var_name:-}"
  local secret_field="${!secret_field_var_name:-}"

  if [[ -n "${current_value}" ]]; then
    return 0
  fi

  if [[ -n "${file_path}" ]]; then
    if [[ ! -f "${file_path}" ]]; then
      echo "Secret file not found for ${base_name}: ${file_path}" >&2
      exit 1
    fi

    local file_value
    file_value="$(<"${file_path}")"
    # Command substitution removes LF but preserves the CR from Windows CRLF.
    # Docker secret files are single-line values, so normalize that final CR.
    file_value="${file_value%$'\r'}"
    export "${base_name}=${file_value}"
    return 0
  fi

  if [[ -n "${secret_id}" ]]; then
    local -a fetch_args=("${AWS_SECRET_FETCHER}" "--secret-id" "${secret_id}")
    if [[ -n "${secret_field}" ]]; then
      fetch_args+=("--json-key" "${secret_field}")
    fi

    export "${base_name}=$(python "${fetch_args[@]}")"
  fi
}

while IFS='=' read -r key _; do
  case "${key}" in
    *_FILE)
      resolve_secret_env_var "${key%_FILE}"
      ;;
    *_AWS_SECRET_ID)
      resolve_secret_env_var "${key%_AWS_SECRET_ID}"
      ;;
  esac
done < <(env)

# Preserve local defaults without exposing infrastructure values in Compose config.
: "${AWS_REGION:=us-east-1}"
: "${AWS_DEFAULT_REGION:=${AWS_REGION}}"
: "${OLIST_S3_PREFIX:=olist}"
: "${REDSHIFT_PORT:=5439}"
: "${POSTGRES_PASSWORD:=olist}"
: "${CONTROL_POSTGRES_PASSWORD:=olist_control}"
export AWS_REGION AWS_DEFAULT_REGION OLIST_S3_PREFIX REDSHIFT_PORT CONTROL_POSTGRES_PASSWORD

exec "$@"
