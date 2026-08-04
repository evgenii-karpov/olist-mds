# Target architecture diagrams

## End-to-end data path

```mermaid
flowchart LR
    mysql["MySQL OLTP"]
    connect["Debezium / Kafka Connect"]
    kafka["Kafka topics"]
    registry["Apicurio Registry"]
    spark["Spark Bronze/Silver"]
    storage["Iceberg on MinIO"]
    polaris["Polaris catalog"]
    serving["ClickHouse serving"]
    airflow["Airflow serving DAGs"]
    dbt["dbt ClickHouse Gold"]
    obs["Prometheus / Alertmanager / Grafana / Loki / Alloy"]

    mysql --> connect
    connect --> kafka
    registry --> connect
    kafka --> spark
    registry --> spark
    spark --> storage
    polaris --> storage
    storage --> serving
    airflow --> serving
    serving --> dbt
    mysql --> obs
    connect --> obs
    kafka --> obs
    spark --> obs
    serving --> obs
```

## Transaction and rejection boundary

```mermaid
flowchart LR
    event["CDC event"] --> bronze["Bronze raw/framing evidence"]
    bronze --> normalize["Spark normalization"]
    normalize --> changes["Silver changes"]
    normalize --> current["Silver current"]
    normalize --> audit["normalization_errors / schema_violations"]
    normalize --> tx["audit.mysql_transactions"]
    tx --> planner["Serving boundary planner"]
    changes --> planner
    current --> planner
    planner -->|complete prefix| candidate["ClickHouse candidate"]
    planner -->|OPEN or REJECTED| blocked["WAITING/BLOCKED"]
    candidate --> publish["Finite publication"]
```

## Serving state machine

```mermaid
stateDiagram-v2
    [*] --> PLANNING
    PLANNING --> WAITING: source not caught up or OPEN transaction
    PLANNING --> BLOCKED: rejected boundary or invariant failure
    PLANNING --> MATERIALIZING: complete transaction prefix
    MATERIALIZING --> PUBLISHING
    PUBLISHING --> SUCCEEDED
    PUBLISHING --> NOOP: already published boundary
    MATERIALIZING --> FAILED_RETRYABLE
    FAILED_RETRYABLE --> PLANNING
    SUCCEEDED --> [*]
    NOOP --> [*]
```

## Target dbt publication

```mermaid
sequenceDiagram
    participant Airflow
    participant Control as serving control ledger
    participant Iceberg
    participant ClickHouse
    participant DBT as dbt olist_clickhouse

    Airflow->>Control: allocate finite sync run
    Control->>Iceberg: resolve completed transaction boundary
    Iceberg-->>Control: candidate snapshot and counts
    Airflow->>ClickHouse: materialize serving candidate
    Airflow->>DBT: build candidate Gold models
    DBT->>ClickHouse: publish stable views for approved run
    ClickHouse-->>Control: entity results and publication evidence
```

Historical phase diagrams remain in the migration records under `docs/cdc/`
and `docs/reports/`; they are not operating instructions for the target stack.
