#!/usr/bin/env sh
set -eu

# Apicurio images that do not natively implement *_FILE can use this wrapper.
# Values are never echoed and exist only in the registry process environment.
load_secret() {
  target_name="$1"
  secret_path="$2"
  if [ -z "$secret_path" ]; then
    echo "required secret file variable for $target_name is not set" >&2
    exit 1
  fi
  if [ ! -r "$secret_path" ]; then
    echo "required secret file for $target_name is not readable" >&2
    exit 1
  fi
  secret_value="$(cat "$secret_path")"
  if [ -z "$secret_value" ]; then
    echo "required secret file for $target_name is empty" >&2
    exit 1
  fi
  export "$target_name=$secret_value"
  unset secret_value
}

load_secret APICURIO_DATASOURCE_USERNAME "${APICURIO_DATASOURCE_USERNAME_FILE:-}"
load_secret APICURIO_DATASOURCE_PASSWORD "${APICURIO_DATASOURCE_PASSWORD_FILE:-}"
unset APICURIO_DATASOURCE_USERNAME_FILE APICURIO_DATASOURCE_PASSWORD_FILE

# Apicurio Registry 3.3 reads the SQL credentials from the APICURIO_*
# namespace.  Keep the public Compose contract file-based while exposing the
# resolved values only to the registry process.
: "${APICURIO_DATASOURCE_URL:?required}"
# The image also materializes the selected SQL kind as a named Quarkus
# datasource.  Supplying the equivalent named properties keeps the wrapper
# compatible with the 3.3.0 runtime's datasource build-time wiring.
export QUARKUS_DATASOURCE__POSTGRESQL__ACTIVE=true
export QUARKUS_DATASOURCE__POSTGRESQL__DB_KIND=postgresql
export QUARKUS_DATASOURCE__POSTGRESQL__JDBC_URL="${APICURIO_DATASOURCE_URL}"
export QUARKUS_DATASOURCE__POSTGRESQL__USERNAME="${APICURIO_DATASOURCE_USERNAME}"
export QUARKUS_DATASOURCE__POSTGRESQL__PASSWORD="${APICURIO_DATASOURCE_PASSWORD}"
export QUARKUS_DATASOURCE_POSTGRESQL_ACTIVE=true

if [ "$#" -eq 0 ]; then
  set -- /opt/jboss/container/java/run/run-java.sh
fi
exec "$@"
