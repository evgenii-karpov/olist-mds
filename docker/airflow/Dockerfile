FROM apache/airflow:3.2.1-python3.13

COPY pyproject.toml uv.lock /tmp/project-deps/

RUN cd /tmp/project-deps \
    && uv export --quiet --frozen --no-dev --no-emit-project --format requirements-txt --output-file /tmp/project-requirements.txt \
    && pip install --no-cache-dir --no-deps -r /tmp/project-requirements.txt

WORKDIR /opt/airflow/project

COPY --chown=airflow:0 . /opt/airflow/project

RUN cd /opt/airflow/project/dbt/olist_analytics \
    && dbt deps \
    && edr --help >/dev/null \
    && mkdir -p /opt/airflow/dags \
    && cp -r /opt/airflow/project/airflow/dags/. /opt/airflow/dags/
