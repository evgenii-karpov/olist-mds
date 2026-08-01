FROM quay.io/debezium/connect:3.6.0.Final

# The pinned Debezium image provides the MySQL connector and Apicurio converter.
# Assert their primary artifacts during the image build; never download mutable
# plugins at container startup.
COPY plugin-inventory.sha256 /tmp/plugin-inventory.sha256
RUN test -s /kafka/connect/debezium-connector-mysql/debezium-connector-mysql-3.6.0.Final.jar \
    && sha256sum --check /tmp/plugin-inventory.sha256

LABEL org.opencontainers.image.source="olist-mds/streaming/connect" \
      org.opencontainers.image.version="3.6.0.Final" \
      io.olist.debezium-connector="mysql" \
      io.olist.apicurio-converter.version="3.2.5"
