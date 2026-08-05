#!/usr/bin/env bash
set -euo pipefail

# Clean-volume initialization delegates to the same idempotent implementation
# used by platform-postgres-bootstrap.  The official entrypoint runs this only
# once; the one-shot service handles later restarts.
bash /opt/olist/platform-postgres/create-apicurio-database.sh
