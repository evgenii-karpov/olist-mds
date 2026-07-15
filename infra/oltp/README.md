# OLTP source assets

Phase 1 owns source PostgreSQL DDL, roles, bootstrap SQL, seed manifests, and
control-schema migrations in this directory. The source database must remain
separate from both the analytical PostgreSQL database and Airflow metadata.
