#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f /opt/nifi/nifi-current/conf/nifi.properties ]]; then
  cp -a /opt/nifi/default-conf/. /opt/nifi/nifi-current/conf/
fi

# The upstream image declares python_extensions as a volume. Seed it at
# runtime so image upgrades cannot be hidden by Docker's anonymous copy-up.
mkdir -p /opt/nifi/nifi-current/python_extensions/olist_cdc
cp -a /opt/olist/python_extensions/olist_cdc/. \
  /opt/nifi/nifi-current/python_extensions/olist_cdc/

export SINGLE_USER_CREDENTIALS_USERNAME="${NIFI_ADMIN_USERNAME:-nifi-admin}"
export SINGLE_USER_CREDENTIALS_PASSWORD="$(tr -d '\r\n' < /run/secrets/nifi_admin_password)"

exec /opt/nifi/scripts/start.sh
