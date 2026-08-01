# syntax=docker/dockerfile:1.7

ARG SPARK_BASE_IMAGE=apache/spark:4.1.3-scala2.13-java17-python3-ubuntu

FROM alpine:3.22.1 AS artifact-downloader

RUN apk add --no-cache ca-certificates wget
COPY docker/spark/jars.sha256 /tmp/jars.sha256
COPY docker/spark/download-jars.sh /usr/local/bin/download-jars
RUN chmod 0555 /usr/local/bin/download-jars \
    && /usr/local/bin/download-jars /tmp/jars.sha256 /opt/olist/jars

FROM ${SPARK_BASE_IMAGE} AS runtime

ARG SPARK_VERSION=4.1.3
ARG SCALA_BINARY_VERSION=2.13
ARG HADOOP_VERSION=3.4.2

USER root

COPY --from=artifact-downloader /opt/olist/jars/ /opt/spark/jars/
COPY docker/spark/verify-runtime.sh /usr/local/bin/verify-olist-spark-runtime
COPY docker/spark/run-with-platform-config.sh /usr/local/bin/run-with-platform-config.sh
COPY streaming/spark/platform/ /opt/olist/streaming/spark/platform/

ENV PYTHONPATH=/opt/olist \
    SPARK_VERSION=${SPARK_VERSION} \
    SCALA_BINARY_VERSION=${SCALA_BINARY_VERSION} \
    HADOOP_VERSION=${HADOOP_VERSION} \
    SPARK_PROPERTIES_FILE=/run/spark/conf/olist-lakehouse.properties

RUN chmod 0555 \
        /usr/local/bin/verify-olist-spark-runtime \
        /usr/local/bin/run-with-platform-config.sh \
    && /usr/local/bin/verify-olist-spark-runtime \
    && mkdir -p /run/spark/conf \
    && chown -R spark:spark /run/spark

LABEL org.opencontainers.image.title="olist-spark" \
      org.opencontainers.image.version="4.1.3-iceberg1.11.0" \
      org.opencontainers.image.description="Spark 4.1.3 with pinned Iceberg, Kafka, Avro, MySQL and S3A runtime artifacts"

USER spark
