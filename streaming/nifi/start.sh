#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f /opt/nifi/nifi-current/conf/nifi.properties ]]; then
  cp -a /opt/nifi/default-conf/. /opt/nifi/nifi-current/conf/
fi

# NiFi discovers Python processors concurrently. Use CPython 3.12 for the
# processor runtime to avoid the AST parser race present in the base image's
# system Python 3.11 runtime. Apply this on every start because the conf
# directory is backed by a persistent Docker volume.
NIFI_PROPERTIES="/opt/nifi/nifi-current/conf/nifi.properties"
NIFI_PYTHON_COMMAND="/usr/local/bin/python3.12"

if [[ ! -x "${NIFI_PYTHON_COMMAND}" ]]; then
  echo "Required NiFi Python runtime is missing: ${NIFI_PYTHON_COMMAND}" >&2
  exit 1
fi

if grep -q '^nifi.python.command=' "${NIFI_PROPERTIES}"; then
  sed -i "s|^nifi.python.command=.*|nifi.python.command=${NIFI_PYTHON_COMMAND}|" "${NIFI_PROPERTIES}"
elif grep -q '^#nifi.python.command=' "${NIFI_PROPERTIES}"; then
  sed -i "s|^#nifi.python.command=.*|nifi.python.command=${NIFI_PYTHON_COMMAND}|" "${NIFI_PROPERTIES}"
else
  printf '\nnifi.python.command=%s\n' "${NIFI_PYTHON_COMMAND}" >> "${NIFI_PROPERTIES}"
fi

# The upstream image declares python_extensions as a volume. Seed it at
# runtime so image upgrades cannot be hidden by Docker's anonymous copy-up.
mkdir -p /opt/nifi/nifi-current/python_extensions/olist_cdc
cp -a /opt/olist/python_extensions/olist_cdc/. \
  /opt/nifi/nifi-current/python_extensions/olist_cdc/

export SINGLE_USER_CREDENTIALS_USERNAME="${NIFI_ADMIN_USERNAME:-nifi-admin}"
export SINGLE_USER_CREDENTIALS_PASSWORD="$(tr -d '\r\n' < /run/secrets/nifi_admin_password)"

exec /opt/nifi/scripts/start.sh
