FROM python:3.12.12-alpine3.22

ARG POLARIS_VERSION=1.6.0

RUN apk add --no-cache jq \
    && python -m pip install --no-cache-dir "apache-polaris==${POLARIS_VERSION}"

COPY infra/polaris/bootstrap/setup.yaml /opt/olist/polaris/setup.yaml
COPY infra/polaris/bootstrap/expected-rbac.json /opt/olist/polaris/expected-rbac.json
COPY infra/polaris/bootstrap/bootstrap.sh /usr/local/bin/bootstrap-olist-catalog
RUN chmod 0444 \
        /opt/olist/polaris/setup.yaml \
        /opt/olist/polaris/expected-rbac.json \
    && chmod 0555 /usr/local/bin/bootstrap-olist-catalog

ENTRYPOINT ["/usr/local/bin/bootstrap-olist-catalog"]
