#!/usr/bin/env sh
set -eu

read_secret() {
    variable_name=$1
    eval "secret_path=\${${variable_name}:-}"
    test -n "${secret_path}" && test -s "${secret_path}" || {
        echo "valid ${variable_name} secret file is required" >&2
        exit 1
    }
    sed -e 's/[[:space:]]*$//' "${secret_path}"
}

polaris_db_user=$(read_secret POLARIS_DB_USERNAME_FILE)
polaris_db_password=$(read_secret POLARIS_DB_PASSWORD_FILE)
root_client_id=$(read_secret POLARIS_ROOT_CLIENT_ID_FILE)
root_client_secret=$(read_secret POLARIS_ROOT_CLIENT_SECRET_FILE)

case "${root_client_id}${root_client_secret}" in
    *:*|*','*|*' '*|*'\t'*)
        echo "Polaris bootstrap credentials contain a forbidden delimiter" >&2
        exit 1
        ;;
esac

export POLARIS_PERSISTENCE_TYPE=relational-jdbc
export POLARIS_PERSISTENCE_RELATIONAL_JDBC_DATABASE_TYPE=postgresql
export QUARKUS_DATASOURCE_JDBC_URL=${POLARIS_JDBC_URL:-jdbc:postgresql://platform-postgres:5432/polaris}
export QUARKUS_DATASOURCE_USERNAME=${polaris_db_user}
export QUARKUS_DATASOURCE_PASSWORD=${polaris_db_password}

runtime_dir=${POLARIS_ADMIN_RUNTIME_DIR:-/tmp/polaris-admin}
credentials_file="${runtime_dir}/root-credentials.yaml"
bootstrap_output_file="${runtime_dir}/bootstrap-output.log"
umask 077
mkdir -p "${runtime_dir}"
chmod 0700 "${runtime_dir}"
trap 'rm -f "${credentials_file}" "${bootstrap_output_file}"' EXIT HUP INT TERM

{
    printf '%s\n' 'POLARIS:'
    printf '  client-id: "%s"\n' "${root_client_id}"
    printf '  client-secret: "%s"\n' "${root_client_secret}"
} > "${credentials_file}"
chmod 0600 "${credentials_file}"

if /opt/jboss/container/java/run/run-java.sh \
    bootstrap \
    --credentials-file="${credentials_file}" \
    >"${bootstrap_output_file}" 2>&1; then
    printf '%s\n' 'Polaris administration bootstrap completed.'
    exit 0
fi

if grep -q 'already been bootstrapped' "${bootstrap_output_file}"; then
    printf '%s\n' 'Polaris administration bootstrap already completed.'
    exit 0
fi

printf '%s\n' 'Polaris administration bootstrap failed.' >&2
exit 1
