#!/usr/bin/env sh
set -eu

credentials_dir=${POLARIS_CREDENTIALS_DIR:-/run/polaris-credentials}
client_id_file="${credentials_dir}/bootstrap-admin-client-id"
client_secret_file="${credentials_dir}/bootstrap-admin-client-secret"

umask 077
mkdir -p "${credentials_dir}"
chmod 0700 "${credentials_dir}"

validate_pair() {
    id_path=$1
    secret_path=$2
    if { test -f "${id_path}" && ! test -f "${secret_path}"; } || \
       { ! test -f "${id_path}" && test -f "${secret_path}"; }; then
        echo "partial Polaris credential pair; reset the full consistency domain" >&2
        exit 1
    fi
    if test -f "${id_path}"; then
        test -s "${id_path}" && test -s "${secret_path}" || {
            echo "empty Polaris credential artifact; reset the full consistency domain" >&2
            exit 1
        }
        chmod 0600 "${id_path}" "${secret_path}"
        return 0
    fi
    return 1
}

if ! validate_pair "${client_id_file}" "${client_secret_file}"; then
    random_secret=$(od -An -N32 -tx1 /dev/urandom | tr -d ' \n')
    test "${#random_secret}" -eq 64
    printf '%s\n' 'root' > "${client_id_file}.tmp"
    printf '%s\n' "${random_secret}" > "${client_secret_file}.tmp"
    chmod 0600 "${client_id_file}.tmp" "${client_secret_file}.tmp"
    mv "${client_id_file}.tmp" "${client_id_file}"
    mv "${client_secret_file}.tmp" "${client_secret_file}"
fi

find "${credentials_dir}" -maxdepth 1 -type f -exec chmod 0600 {} \;

printf '%s\n' 'Polaris bootstrap credential artifacts are ready.'
