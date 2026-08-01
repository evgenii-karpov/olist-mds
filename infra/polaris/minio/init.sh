#!/usr/bin/env sh
set -eu

endpoint=${OBJECT_STORE_ENDPOINT:-http://minio:9000}
credentials_dir=${POLARIS_CREDENTIALS_DIR:-/run/polaris-credentials}
policy_dir=${MINIO_POLICY_DIR:-/opt/olist/polaris/minio}

read_secret_file() {
    variable_name=$1
    eval "path=\${${variable_name}:-}"
    test -n "${path}" && test -s "${path}" || {
        echo "valid ${variable_name} secret file is required" >&2
        exit 1
    }
    tr -d '\r\n' < "${path}"
}

random_secret() {
    generated=$(od -An -N32 -tx1 /dev/urandom | tr -d ' \n')
    test "${#generated}" -eq 64
    printf '%s' "${generated}"
}

root_user=$(read_secret_file MINIO_ROOT_USER_FILE)
root_password=$(read_secret_file MINIO_ROOT_PASSWORD_FILE)

umask 077
mc_config_dir=$(mktemp -d "${TMPDIR:-/tmp}/olist-minio-mc.XXXXXX")
export MC_CONFIG_DIR="${mc_config_dir}"

cleanup_mc_config() {
    rm -rf -- "${mc_config_dir}"
}

trap cleanup_mc_config EXIT HUP INT TERM

mkdir -p "${credentials_dir}"
chmod 0700 "${credentials_dir}"

mc alias set olist "${endpoint}" "${root_user}" "${root_password}" >/dev/null
mc mb --ignore-existing olist/olist-lakehouse >/dev/null
mc mb --ignore-existing olist/olist-checkpoints >/dev/null
mc anonymous set none olist/olist-lakehouse >/dev/null
mc anonymous set none olist/olist-checkpoints >/dev/null

mc admin policy create olist olist-polaris-warehouse "${policy_dir}/warehouse-policy.json" >/dev/null
mc admin policy create olist olist-spark-checkpoints "${policy_dir}/checkpoints-policy.json" >/dev/null

ensure_identity() {
    access_key=$1
    artifact_prefix=$2
    policy=$3
    probe_bucket=$4
    access_key_file="${credentials_dir}/${artifact_prefix}-access-key"
    secret_key_file="${credentials_dir}/${artifact_prefix}-secret-key"

    user_exists=false
    if mc admin user info olist "${access_key}" >/dev/null 2>&1; then
        user_exists=true
    fi
    artifacts_exist=false
    if test -f "${access_key_file}" && test -f "${secret_key_file}"; then
        artifacts_exist=true
    elif test -e "${access_key_file}" || test -e "${secret_key_file}"; then
        echo "partial MinIO credentials for ${access_key}; full reset required" >&2
        exit 1
    fi

    if test "${user_exists}" = true && test "${artifacts_exist}" = false; then
        echo "MinIO contains ${access_key} but credential volume is missing; full reset required" >&2
        exit 1
    fi
    if test "${user_exists}" = false && test "${artifacts_exist}" = true; then
        echo "credential volume contains ${access_key} but MinIO does not; full reset required" >&2
        exit 1
    fi

    if test "${user_exists}" = false; then
        generated_secret=$(random_secret)
        printf '%s\n' "${access_key}" > "${access_key_file}.tmp"
        printf '%s\n' "${generated_secret}" > "${secret_key_file}.tmp"
        chmod 0600 "${access_key_file}.tmp" "${secret_key_file}.tmp"
        mc admin user add olist "${access_key}" "${generated_secret}" >/dev/null
        mc admin policy attach olist "${policy}" --user "${access_key}" >/dev/null
        mv "${access_key_file}.tmp" "${access_key_file}"
        mv "${secret_key_file}.tmp" "${secret_key_file}"
    else
        stored_access_key=$(tr -d '\r\n' < "${access_key_file}")
        stored_secret_key=$(tr -d '\r\n' < "${secret_key_file}")
        test "${stored_access_key}" = "${access_key}" || {
            echo "MinIO access-key artifact mismatch; full reset required" >&2
            exit 1
        }
        mc alias set identity-check "${endpoint}" "${stored_access_key}" "${stored_secret_key}" >/dev/null
        mc ls "identity-check/${probe_bucket}" >/dev/null
        mc alias remove identity-check >/dev/null
        mc admin policy attach olist "${policy}" --user "${access_key}" >/dev/null
    fi
    chmod 0600 "${access_key_file}" "${secret_key_file}"
}

ensure_identity polaris-warehouse minio-polaris olist-polaris-warehouse olist-lakehouse/warehouse
ensure_identity spark-checkpoints minio-checkpoints olist-spark-checkpoints olist-checkpoints

printf '%s\n' 'MinIO lakehouse/checkpoint buckets and isolated identities are ready.'
