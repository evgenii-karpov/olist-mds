FROM apache/airflow:3.2.1-python3.13

COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /uvx /bin/

COPY pyproject.toml uv.lock /tmp/project-deps/

RUN cd /tmp/project-deps \
    && /bin/uv export --quiet --frozen --no-dev --no-emit-project --format requirements-txt --output-file /tmp/project-requirements.txt \
    && pip install --no-cache-dir --no-deps -r /tmp/project-requirements.txt
