FROM alpine:3.22.1

RUN apk add --no-cache jq

COPY infra/polaris/credentials/projection-contract.json /opt/olist/polaris/projection-contract.json
COPY infra/polaris/credentials/project.sh /usr/local/bin/project-polaris-credentials
RUN chmod 0444 /opt/olist/polaris/projection-contract.json \
    && chmod 0555 /usr/local/bin/project-polaris-credentials

USER 0
ENTRYPOINT ["/usr/local/bin/project-polaris-credentials"]
