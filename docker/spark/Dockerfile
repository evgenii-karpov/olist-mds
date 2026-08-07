# syntax=docker/dockerfile:1.7

ARG SPARK_BASE_IMAGE=apache/spark:4.1.3-scala2.13-java17-python3-ubuntu

FROM alpine:3.22.1 AS artifact-downloader

RUN apk add --no-cache ca-certificates wget
COPY docker/spark/jars.sha256 /tmp/jars.sha256
COPY docker/spark/download-jars.sh /usr/local/bin/download-jars
RUN chmod 0555 /usr/local/bin/download-jars \
    && /usr/local/bin/download-jars /tmp/jars.sha256 /opt/olist/jars

FROM alpine:3.22.1 AS sbt-downloader

RUN apk add --no-cache ca-certificates wget
COPY docker/spark/sbt-launch.sha256 /tmp/sbt-launch.sha256
COPY docker/spark/download-sbt-launch.sh /usr/local/bin/download-sbt-launch
RUN chmod 0555 /usr/local/bin/download-sbt-launch \
    && /usr/local/bin/download-sbt-launch /tmp/sbt-launch.sha256 /tmp/sbt-launcher

FROM ${SPARK_BASE_IMAGE} AS scala-builder

USER root

COPY --from=artifact-downloader /opt/olist/jars/ /opt/spark/jars/
COPY --from=sbt-downloader /tmp/sbt-launcher/sbt-launch.jar /tmp/sbt-launch.jar

COPY streaming /tmp/streaming

# The repository is developed on Windows as well as Linux.  Normalize the
# checkout line endings inside the Linux builder so scalafmtCheckAll validates
# the source content rather than failing on CRLF materialized by Git.
RUN find /tmp/streaming/spark/scala -type f -exec sed -i 's/\r$//' {} +

WORKDIR /tmp/streaming/spark/scala

RUN java -jar /tmp/sbt-launch.jar scalafmtCheckAll scalafmtSbtCheck Test/compile test package

FROM ${SPARK_BASE_IMAGE} AS runtime

ARG SPARK_VERSION=4.1.3
ARG SCALA_BINARY_VERSION=2.13
ARG HADOOP_VERSION=3.4.2
ARG GCS_CONNECTOR_VERSION=2.2.31

USER root

COPY --from=artifact-downloader /opt/olist/jars/ /opt/spark/jars/
COPY --from=scala-builder /tmp/streaming/spark/scala/target/scala-2.13/olist-spark-jobs_2.13-0.1.0.jar /opt/olist/jars/olist-spark-jobs.jar
COPY docker/spark/verify-runtime.sh /usr/local/bin/verify-olist-spark-runtime
COPY docker/spark/verify-classpath.sh /usr/local/bin/verify-olist-spark-classpath
COPY docker/spark/run-with-platform-config.sh /usr/local/bin/run-with-platform-config.sh
COPY streaming/spark/platform/ /opt/olist/streaming/spark/platform/

ENV PYTHONPATH=/opt/olist \
    SPARK_VERSION=${SPARK_VERSION} \
    SCALA_BINARY_VERSION=${SCALA_BINARY_VERSION} \
    HADOOP_VERSION=${HADOOP_VERSION} \
    GCS_CONNECTOR_VERSION=${GCS_CONNECTOR_VERSION} \
    SPARK_PROPERTIES_FILE=/run/spark/conf/olist-lakehouse.properties

RUN chmod 0555 \
        /usr/local/bin/verify-olist-spark-runtime \
        /usr/local/bin/verify-olist-spark-classpath \
        /usr/local/bin/run-with-platform-config.sh \
    && mkdir -p /var/run/olist-spark/bronze /var/run/olist-spark/silver /var/run/olist-spark/failpoints \
    && chown -R spark:spark /var/run/olist-spark \
    && chmod 0750 /var/run/olist-spark/bronze /var/run/olist-spark/silver /var/run/olist-spark/failpoints \
    && /usr/local/bin/verify-olist-spark-runtime \
    && /usr/local/bin/verify-olist-spark-classpath \
    && mkdir -p /run/spark/conf \
    && chown -R spark:spark /run/spark

LABEL org.opencontainers.image.title="olist-spark" \
      org.opencontainers.image.version="4.1.3-iceberg1.11.0" \
      org.opencontainers.image.description="Spark 4.1.3 with pinned Iceberg, Kafka, Avro, MySQL, S3A and GCS runtime artifacts"

USER spark
