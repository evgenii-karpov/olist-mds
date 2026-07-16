#!/usr/bin/env sh
set -eu

root_password="$(tr -d '\r\n' < /run/secrets/minio_root_password)"
nifi_password="$(tr -d '\r\n' < /run/secrets/minio_nifi_password)"

until mc alias set local http://minio:9000 minioadmin "${root_password}" >/dev/null 2>&1; do
  sleep 2
done

mc mb --ignore-existing local/olist-cdc
mc version enable local/olist-cdc
mc admin policy create local olist-nifi-cdc /opt/olist/nifi-policy.json >/dev/null
mc admin user add local olist_nifi "${nifi_password}" >/dev/null 2>&1 || true
mc admin policy attach local olist-nifi-cdc --user olist_nifi >/dev/null

echo "MinIO CDC bucket, versioning, and NiFi service policy are ready."

