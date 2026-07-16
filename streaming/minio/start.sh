#!/bin/sh
set -eu

export MINIO_ROOT_USER="${MINIO_ROOT_USER:-minioadmin}"
export MINIO_ROOT_PASSWORD="$(tr -d '\r\n' < /run/secrets/minio_root_password)"

exec minio "$@"

