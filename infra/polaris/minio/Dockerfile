ARG MINIO_MC_IMAGE=quay.io/minio/mc:RELEASE.2025-08-13T08-35-41Z
FROM ${MINIO_MC_IMAGE}

USER root
COPY infra/polaris/minio/warehouse-policy.json /opt/olist/polaris/minio/warehouse-policy.json
COPY infra/polaris/minio/checkpoints-policy.json /opt/olist/polaris/minio/checkpoints-policy.json
COPY infra/polaris/minio/init.sh /usr/local/bin/init-olist-minio
RUN chmod 0444 /opt/olist/polaris/minio/*.json \
    && chmod 0555 /usr/local/bin/init-olist-minio

ENTRYPOINT ["/usr/local/bin/init-olist-minio"]
