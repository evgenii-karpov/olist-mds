ARG UV_VERSION=0.11.28

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

FROM apache/airflow:slim-3.2.1-python3.12

COPY --from=uv /uv /uvx /bin/

COPY pyproject.toml uv.lock /tmp/project-deps/

RUN cd /tmp/project-deps \
    && uv export --quiet --frozen --no-dev --no-emit-project --format requirements-txt --output-file /tmp/project-requirements.txt \
    && pip install --no-cache-dir --no-deps -r /tmp/project-requirements.txt

WORKDIR /opt/airflow/project

COPY --chown=airflow:0 \
    pyproject.toml \
    docker \
    docs \
    infra \
    scripts \
    /opt/airflow/project/

COPY --chown=airflow:0 airflow /opt/airflow/project/airflow
COPY --chown=airflow:0 dbt/olist_analytics /opt/airflow/project/dbt/olist_analytics

RUN cd /opt/airflow/project/dbt/olist_analytics \
    && cp profiles.yml.example profiles.yml \
    && dbt deps \
    && edr --help >/dev/null \
    && mkdir -p /opt/airflow/dags \
    && cp -r /opt/airflow/project/airflow/dags/. /opt/airflow/dags/
