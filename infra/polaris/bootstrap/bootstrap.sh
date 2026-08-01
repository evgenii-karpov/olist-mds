#!/usr/bin/env sh
set -eu

credentials_dir=${POLARIS_CREDENTIALS_DIR:-/run/polaris-credentials}
setup_file=${POLARIS_SETUP_FILE:-/opt/olist/polaris/setup.yaml}
rbac_contract_file=${POLARIS_RBAC_CONTRACT_FILE:-/opt/olist/polaris/expected-rbac.json}
base_url=${POLARIS_BASE_URL:-http://polaris:8181}
realm=${POLARIS_REALM:-POLARIS}

fail() {
    echo "$*" >&2
    exit 1
}

read_credential() {
    path=$1
    test -s "${path}" || {
        echo "missing credential artifact ${path}; reset the full consistency domain" >&2
        exit 1
    }
    value=$(sed -e 's/[[:space:]]*$//' "${path}")
    test -n "${value}" || {
        echo "empty credential artifact ${path}; reset the full consistency domain" >&2
        exit 1
    }
    printf '%s' "${value}"
}

umask 077
mkdir -p "${credentials_dir}"
chmod 0700 "${credentials_dir}"

cleanup_sensitive_temp_files() {
    rm -f \
        "${credentials_dir}/.spark_writer.json" \
        "${credentials_dir}/.spark_writer.created.json" \
        "${credentials_dir}/.clickhouse_reader.json" \
        "${credentials_dir}/.clickhouse_reader.created.json" \
        "${credentials_dir}/.airflow_maintenance.json" \
        "${credentials_dir}/.airflow_maintenance.created.json" \
        "${credentials_dir}/polaris-spark-client-id.tmp" \
        "${credentials_dir}/polaris-spark-client-secret.tmp" \
        "${credentials_dir}/polaris-clickhouse-client-id.tmp" \
        "${credentials_dir}/polaris-clickhouse-client-secret.tmp" \
        "${credentials_dir}/polaris-airflow-client-id.tmp" \
        "${credentials_dir}/polaris-airflow-client-secret.tmp"
}

trap cleanup_sensitive_temp_files EXIT
trap 'exit 1' HUP INT TERM

export CLIENT_ID=$(read_credential "${credentials_dir}/bootstrap-admin-client-id")
export CLIENT_SECRET=$(read_credential "${credentials_dir}/bootstrap-admin-client-secret")
export REALM=${realm}

polaris_cli() {
    polaris --base-url "${base_url}" --realm "${realm}" "$@"
}

ensure_principal_role() {
    role=$1
    if ! polaris_cli principal-roles get "${role}" >/dev/null 2>&1; then
        polaris_cli principal-roles create "${role}" >/dev/null
    fi
}

ensure_principal() {
    principal=$1
    artifact_prefix=$2
    client_id_file="${credentials_dir}/${artifact_prefix}-client-id"
    client_secret_file="${credentials_dir}/${artifact_prefix}-client-secret"
    metadata_file="${credentials_dir}/.${principal}.json"
    response_file="${credentials_dir}/.${principal}.created.json"

    exists=false
    if polaris_cli principals get "${principal}" > "${metadata_file}" 2>/dev/null; then
        exists=true
    fi

    has_credentials=false
    if test -f "${client_id_file}" && test -f "${client_secret_file}"; then
        has_credentials=true
    elif test -e "${client_id_file}" || test -e "${client_secret_file}"; then
        echo "partial credentials for ${principal}; reset the full consistency domain" >&2
        exit 1
    fi

    if test "${exists}" = true && test "${has_credentials}" = false; then
        echo "Polaris DB contains ${principal} but its credential volume is missing; full reset required" >&2
        exit 1
    fi
    if test "${exists}" = false && test "${has_credentials}" = true; then
        echo "credential volume contains ${principal} but Polaris DB does not; full reset required" >&2
        exit 1
    fi

    if test "${exists}" = false; then
        polaris_cli principals create "${principal}" > "${response_file}"
        jq -e '.clientId and .clientSecret' "${response_file}" >/dev/null
        jq -r '.clientId' "${response_file}" > "${client_id_file}.tmp"
        jq -r '.clientSecret' "${response_file}" > "${client_secret_file}.tmp"
        chmod 0600 "${client_id_file}.tmp" "${client_secret_file}.tmp"
        mv "${client_id_file}.tmp" "${client_id_file}"
        mv "${client_secret_file}.tmp" "${client_secret_file}"
    else
        stored_client_id=$(read_credential "${client_id_file}")
        catalog_client_id=$(jq -r '.clientId // .client_id // empty' "${metadata_file}")
        test -n "${catalog_client_id}" && test "${stored_client_id}" = "${catalog_client_id}" || {
            echo "credential artifact does not match Polaris principal ${principal}; full reset required" >&2
            exit 1
        }
    fi

    chmod 0600 "${client_id_file}" "${client_secret_file}"
    rm -f "${metadata_file}" "${response_file}"
}

ensure_principal_role spark_writer_role
ensure_principal_role clickhouse_reader_role
ensure_principal_role airflow_maintenance_role

ensure_principal spark_writer polaris-spark
ensure_principal clickhouse_reader polaris-clickhouse
ensure_principal airflow_maintenance polaris-airflow

polaris_cli setup apply "${setup_file}" >/dev/null

for namespace in bronze silver reference audit; do
    polaris_cli namespaces get --catalog olist_lakehouse "${namespace}" >/dev/null
done

json_line_names() {
    jq -sc 'map(.name // error("missing role name")) | sort'
}

catalog_role_names() {
    # Polaris 1.6 uses `catalog-roles list CATALOG`; the older textual
    # contract was `catalog-roles list --catalog CATALOG`.
    jq -sc '
        map(select(.name != "catalog_admin") | .name // error("missing role name"))
        | sort
    '
}

verify_rbac_contract() {
    jq -e '
        (.catalog | type) == "string"
        and (.smoke_namespace | type) == "string"
        and (.principals | type) == "object"
        and (.principals | length) == 3
        and all(
            .principals[];
            (.artifact_prefix | type) == "string"
            and (.principal_role | type) == "string"
            and (.catalog_role | type) == "string"
            and (.catalog_privileges | type) == "array"
            and (.catalog_privileges | length) > 0
            and all(.catalog_privileges[]; type == "string")
        )
        and all(
            .principals[].catalog_privileges[];
            . as $privilege
            | [
                "CATALOG_READ_PROPERTIES",
                "NAMESPACE_LIST",
                "NAMESPACE_READ_PROPERTIES",
                "TABLE_CREATE",
                "TABLE_LIST",
                "TABLE_READ_PROPERTIES",
                "TABLE_WRITE_PROPERTIES",
                "TABLE_READ_DATA",
                "TABLE_WRITE_DATA"
            ]
            | index($privilege) != null
        )
    ' "${rbac_contract_file}" >/dev/null ||
        fail "invalid Polaris RBAC contract ${rbac_contract_file}"

    catalog=$(jq -er '.catalog' "${rbac_contract_file}")
    smoke_namespace=$(jq -er '.smoke_namespace' "${rbac_contract_file}")

    expected_catalog_roles=$(jq -c \
        '[.principals[].catalog_role] | sort' "${rbac_contract_file}")
    if ! catalog_roles_output=$(
        polaris_cli catalog-roles list "${catalog}"
    ); then
        fail "cannot list Polaris catalog roles for ${catalog}"
    fi
    if ! actual_catalog_roles=$(
        printf '%s\n' "${catalog_roles_output}" | catalog_role_names
    ); then
        fail "Polaris returned malformed catalog-role JSON for ${catalog}"
    fi
    test "${actual_catalog_roles}" = "${expected_catalog_roles}" ||
        fail "Polaris catalog-role drift for ${catalog}; full reset required"

    principals=$(jq -r '.principals | keys[]' "${rbac_contract_file}")
    for principal in ${principals}; do
        principal_role=$(jq -er --arg principal "${principal}" \
            '.principals[$principal].principal_role' "${rbac_contract_file}")
        catalog_role=$(jq -er --arg principal "${principal}" \
            '.principals[$principal].catalog_role' "${rbac_contract_file}")

        expected_principal_roles=$(jq -c --arg principal "${principal}" \
            '[.principals[$principal].principal_role] | sort' \
            "${rbac_contract_file}")
        if ! principal_roles_output=$(
            polaris_cli principal-roles list --principal "${principal}"
        ); then
            fail "cannot list Polaris principal roles for ${principal}"
        fi
        if ! actual_principal_roles=$(
            printf '%s\n' "${principal_roles_output}" | json_line_names
        ); then
            fail "Polaris returned malformed principal-role JSON for ${principal}"
        fi
        test "${actual_principal_roles}" = "${expected_principal_roles}" ||
            fail "Polaris principal-role drift for ${principal}; full reset required"

        expected_assigned_catalog_roles=$(jq -c --arg principal "${principal}" \
            '[.principals[$principal].catalog_role] | sort' \
            "${rbac_contract_file}")
        if ! assigned_catalog_roles_output=$(
            polaris_cli catalog-roles list \
                "${catalog}" \
                --principal-role "${principal_role}"
        ); then
            fail "cannot list catalog roles assigned to ${principal_role}"
        fi
        if ! actual_assigned_catalog_roles=$(
            printf '%s\n' "${assigned_catalog_roles_output}" | json_line_names
        ); then
            fail "Polaris returned malformed catalog-role assignment JSON"
        fi
        test "${actual_assigned_catalog_roles}" = \
            "${expected_assigned_catalog_roles}" ||
            fail "Polaris catalog-role assignment drift for ${principal}; full reset required"

        expected_privileges=$(jq -c --arg principal "${principal}" \
            '.principals[$principal].catalog_privileges | sort' \
            "${rbac_contract_file}")
        if ! privileges_output=$(
            polaris_cli privileges list \
                --catalog "${catalog}" \
                --catalog-role "${catalog_role}"
        ); then
            fail "cannot list Polaris privileges for ${catalog_role}"
        fi
        if ! actual_privileges=$(
            printf '%s\n' "${privileges_output}" |
                jq -sc '
                    if all(
                        .[];
                        .type == "catalog" and (.privilege | type) == "string"
                    ) then
                        map(.privilege) | sort
                    else
                        error("unexpected non-catalog or malformed grant")
                    end
                '
        ); then
            fail "Polaris returned an unexpected grant shape for ${catalog_role}"
        fi
        test "${actual_privileges}" = "${expected_privileges}" ||
            fail "Polaris privilege drift for ${catalog_role}; full reset required"
    done

    for principal in ${principals}; do
        artifact_prefix=$(jq -er --arg principal "${principal}" \
            '.principals[$principal].artifact_prefix' "${rbac_contract_file}")
        runtime_client_id=$(read_credential \
            "${credentials_dir}/${artifact_prefix}-client-id")
        runtime_client_secret=$(read_credential \
            "${credentials_dir}/${artifact_prefix}-client-secret")

        if ! (
            export CLIENT_ID=${runtime_client_id}
            export CLIENT_SECRET=${runtime_client_secret}
            export REALM=${realm}
            polaris --base-url "${base_url}" --realm "${realm}" \
                catalogs get "${catalog}" >/dev/null
            polaris --base-url "${base_url}" --realm "${realm}" \
                namespaces get --catalog "${catalog}" \
                "${smoke_namespace}" >/dev/null
        ); then
            fail "runtime authentication/authorization smoke failed for ${principal}"
        fi
    done
}

verify_rbac_contract

find "${credentials_dir}" -maxdepth 1 -type f -exec chmod 0600 {} \;
printf '%s\n' \
    'Polaris catalog, principals, exact grants, runtime auth, and namespaces are ready.'
