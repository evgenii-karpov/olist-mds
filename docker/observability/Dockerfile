FROM apache/airflow:slim-3.2.1-python3.12

USER airflow

RUN pip install --no-cache-dir --no-deps \
    mysql-connector-python==9.7.0 \
    psycopg2-binary==2.9.12

WORKDIR /opt/olist

COPY scripts/observability /opt/olist/scripts/observability

ENV PYTHONPATH=/opt/olist

USER airflow

ENTRYPOINT ["python", "/opt/olist/scripts/observability/target_probe.py"]
