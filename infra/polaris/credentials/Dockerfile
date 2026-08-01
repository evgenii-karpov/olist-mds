FROM alpine:3.22.1

COPY infra/polaris/credentials/prepare.sh /usr/local/bin/prepare-polaris-credentials
RUN chmod 0555 /usr/local/bin/prepare-polaris-credentials

ENTRYPOINT ["/usr/local/bin/prepare-polaris-credentials"]
