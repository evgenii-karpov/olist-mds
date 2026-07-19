FROM alpine:3.23.3 AS nifi-extensions

ARG NIFI_VERSION=2.10.0
ARG PARQUET_NAR_SHA1=09966fe6d6ad87b163cea1d122b73cd80c7770c0
ARG HADOOP_LIBRARIES_NAR_SHA1=1d0a80afd64690315b6cf0ab7e5a4ba1ef5766d9

RUN apk add --no-cache curl \
    && curl --fail --location --output /nifi-hadoop-libraries.nar \
       "https://repo.maven.apache.org/maven2/org/apache/nifi/nifi-hadoop-libraries-nar/${NIFI_VERSION}/nifi-hadoop-libraries-nar-${NIFI_VERSION}.nar" \
    && echo "${HADOOP_LIBRARIES_NAR_SHA1}  /nifi-hadoop-libraries.nar" | sha1sum -c - \
    && curl --fail --location --output /nifi-parquet.nar \
       "https://repo.maven.apache.org/maven2/org/apache/nifi/nifi-parquet-nar/${NIFI_VERSION}/nifi-parquet-nar-${NIFI_VERSION}.nar" \
    && echo "${PARQUET_NAR_SHA1}  /nifi-parquet.nar" | sha1sum -c -

FROM python:3.12-slim-bookworm AS nifi-python-runtime

FROM apache/nifi:2.10.0

USER root
COPY --from=nifi-python-runtime /usr/local /usr/local
COPY --from=nifi-extensions /nifi-hadoop-libraries.nar /opt/nifi/nifi-current/lib/nifi-hadoop-libraries-nar-2.10.0.nar
COPY --from=nifi-extensions /nifi-parquet.nar /opt/nifi/nifi-current/lib/nifi-parquet-nar-2.10.0.nar
COPY streaming/nifi/python /opt/olist/python_extensions/olist_cdc
COPY streaming/nifi/flow /opt/olist/flow
COPY streaming/nifi/parameters /opt/olist/parameters
COPY streaming/nifi/deploy_flow.py streaming/nifi/metrics_proxy.py streaming/nifi/component_metrics.py streaming/nifi/start.sh /opt/olist/
COPY streaming/schemas /opt/olist/schemas

RUN mkdir -p /opt/nifi/nifi-current/work \
    && cp -a /opt/nifi/nifi-current/conf /opt/nifi/default-conf \
    && chmod +x /opt/olist/start.sh \
    && chown -R nifi:nifi /opt/olist /opt/nifi/nifi-current/work

USER nifi
ENTRYPOINT ["/opt/olist/start.sh"]
