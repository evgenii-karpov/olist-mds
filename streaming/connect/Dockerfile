FROM quay.io/debezium/connect@sha256:61d29e5a0316de5dd0a564ec40eaa662d837a05217523e1a1745ecde3d790455

# Debezium 3.6 already ships the Apicurio converter. Assert the exact primary
# artifacts at build time so a changed upstream image cannot silently alter the
# connector surface even when a mutable local cache is involved.
COPY plugin-inventory.sha256 /tmp/plugin-inventory.sha256
RUN sha256sum --check /tmp/plugin-inventory.sha256

LABEL org.opencontainers.image.source="olist-mds/streaming/connect" \
      org.opencontainers.image.version="3.6.0.Final" \
      io.olist.apicurio-converter.version="3.2.5"
