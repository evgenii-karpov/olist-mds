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
warehouse_access_key=$(read_secret POLARIS_WAREHOUSE_ACCESS_KEY_FILE)
warehouse_secret_key=$(read_secret POLARIS_WAREHOUSE_SECRET_KEY_FILE)

export QUARKUS_CONFIG_LOCATIONS=${QUARKUS_CONFIG_LOCATIONS:-file:/opt/olist/polaris/application.properties}
export QUARKUS_DATASOURCE_JDBC_URL=${POLARIS_JDBC_URL:-jdbc:postgresql://platform-postgres:5432/polaris}
export QUARKUS_DATASOURCE_USERNAME=${polaris_db_user}
export QUARKUS_DATASOURCE_PASSWORD=${polaris_db_password}
export POLARIS_BOOTSTRAP_CREDENTIALS="POLARIS,${root_client_id},${root_client_secret}"
export AWS_REGION=${OBJECT_STORE_REGION:-us-east-1}
export AWS_ACCESS_KEY_ID=${warehouse_access_key}
export AWS_SECRET_ACCESS_KEY=${warehouse_secret_key}
export POLARIS_STORAGE_AWS_ACCESS_KEY=${warehouse_access_key}
export POLARIS_STORAGE_AWS_SECRET_KEY=${warehouse_secret_key}

exec /opt/jboss/container/java/run/run-java.sh "$@"
