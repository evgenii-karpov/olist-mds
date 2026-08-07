ARG UV_VERSION=0.11.28

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

FROM python:3.12-slim

COPY --from=uv /uv /uvx /bin/

WORKDIR /opt/olist

COPY pyproject.toml uv.lock /tmp/project-deps/

RUN cd /tmp/project-deps \
    && uv export --quiet --frozen --only-group bigquery \
        --no-emit-project --format requirements-txt \
        --output-file /tmp/project-requirements.txt \
    && pip install --no-cache-dir --no-deps -r /tmp/project-requirements.txt \
    && rm -rf /root/.cache/pip /tmp/project-deps /tmp/project-requirements.txt

COPY dbt/olist_bigquery /opt/olist/dbt/olist_bigquery

ENTRYPOINT ["dbt"]
