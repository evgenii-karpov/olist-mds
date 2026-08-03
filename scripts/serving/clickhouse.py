"""ClickHouse candidate materialization, marker publication and rebuild helpers."""

from __future__ import annotations

import contextlib
import json
import logging
import os
import time
import urllib.request
from pathlib import Path
from urllib.error import HTTPError

from scripts.serving.entities import ALL_SERVING_ENTITIES, ServingEntitySpec
from scripts.serving.models import ServingSyncReport

logger = logging.getLogger(__name__)


def _as_int(value: object, default: int = 0) -> int:
    return int(value) if isinstance(value, (int, float, str)) else default


def get_clickhouse_url() -> str:
    host = os.environ.get("CLICKHOUSE_HOST", "127.0.0.1")
    port = int(os.environ.get("CLICKHOUSE_PORT", "8123"))
    return f"http://{host}:{port}"


def get_clickhouse_credentials() -> tuple[str, str]:
    user = os.environ.get("CLICKHOUSE_USER", "olist")
    password = os.environ.get("CLICKHOUSE_PASSWORD")
    if not password:
        pw_file = os.environ.get(
            "CLICKHOUSE_PASSWORD_FILE", "/run/secrets/clickhouse_password"
        )
        if os.path.exists(pw_file):
            with (
                contextlib.suppress(Exception),
                open(pw_file, encoding="utf-8") as f,
            ):
                password = f.read().strip()
    if not password:
        password = "olist"
    return user, password


def clickhouse_query(
    sql: str, params: dict[str, str | int | float] | None = None
) -> list[dict[str, object]]:
    url = f"{get_clickhouse_url()}/?default_format=JSON"
    data = sql.encode("utf-8")
    user, password = get_clickhouse_credentials()
    for attempt in range(1, 6):
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("X-ClickHouse-User", user)
        req.add_header("X-ClickHouse-Key", password)
        try:
            with urllib.request.urlopen(req, timeout=30.0) as resp:
                raw = resp.read().decode("utf-8")
                if not raw.strip():
                    return []
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    data_val = parsed.get("data")
                    if isinstance(data_val, list):
                        return [item for item in data_val if isinstance(item, dict)]
                return []
        except Exception as exc:
            err_msg = str(exc)
            if isinstance(exc, HTTPError):
                with contextlib.suppress(Exception):
                    body = exc.read().decode("utf-8", errors="replace")
                    if body:
                        err_msg = f"{exc}: {body.strip()}"
            if attempt == 5:
                logger.error("ClickHouse query error: %s", err_msg)
                raise
            time.sleep(2.0)
    return []


def clickhouse_execute(sql: str) -> None:
    """Execute a ClickHouse DDL/administrative statement without row parsing."""

    url = f"{get_clickhouse_url()}/"
    data = sql.encode("utf-8")
    user, password = get_clickhouse_credentials()
    for attempt in range(1, 6):
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("X-ClickHouse-User", user)
        req.add_header("X-ClickHouse-Key", password)
        try:
            with urllib.request.urlopen(req, timeout=60.0) as resp:
                resp.read()
            return
        except Exception as exc:
            err_msg = str(exc)
            if isinstance(exc, HTTPError):
                with contextlib.suppress(Exception):
                    body = exc.read().decode("utf-8", errors="replace")
                    if body:
                        err_msg = f"{exc}: {body.strip()}"
            if attempt == 5:
                logger.error("ClickHouse command error: %s", err_msg)
                raise
            time.sleep(2.0)


def _ddl_statements(script: str) -> list[str]:
    """Split the repository's simple semicolon-terminated DDL files."""

    return [statement.strip() for statement in script.split(";") if statement.strip()]


def format_ch_relation(relation: str) -> str:
    parts = relation.split(".", 1)
    if len(parts) == 2 and not parts[1].startswith('"'):
        return f'{parts[0]}."{parts[1]}"'
    return relation


class ClickHouseServingMaterializer:
    _DDL_ROOT = (
        Path(__file__).resolve().parents[2] / "infra" / "clickhouse" / "lakehouse"
    )
    _DERIVED_DATABASES = ("gold", "gold_store", "serving_cdc", "serving_control")

    @classmethod
    def recreate_derived_databases(cls) -> None:
        """Recreate serving databases from the versioned native DDL files."""

        for database in cls._DERIVED_DATABASES:
            clickhouse_execute(f"DROP DATABASE IF EXISTS `{database}`")

        for name in (
            "001_create_databases.sql",
            "002_create_serving_control.sql",
            "003_create_event_tables.sql",
            "004_create_current_version_tables.sql",
            "005_create_stable_current_views.sql",
        ):
            path = cls._DDL_ROOT / name
            if not path.is_file():
                raise FileNotFoundError(f"Serving DDL file is missing: {path}")
            for statement in _ddl_statements(path.read_text(encoding="utf-8")):
                clickhouse_execute(statement)

    @staticmethod
    def fetch_current_counts() -> dict[str, int]:
        """Return row counts from the currently published ClickHouse views."""

        counts: dict[str, int] = {}
        for spec in ALL_SERVING_ENTITIES:
            rows = clickhouse_query(
                f"SELECT count() AS cnt FROM {spec.ch_current_view}"
            )
            value = rows[0].get("cnt") if rows else None
            if not isinstance(value, (int, float, str)):
                raise RuntimeError(
                    f"Could not read current serving count for {spec.entity}"
                )
            counts[spec.entity] = int(value)
        return counts

    @staticmethod
    def fetch_iceberg_current_counts() -> dict[str, int]:
        """Return non-deleted current counts calculated directly from Silver."""

        counts: dict[str, int] = {}
        for spec in ALL_SERVING_ENTITIES:
            relation = format_ch_relation(spec.changes_relation)
            primary_key = ", ".join(spec.primary_key)
            rows = clickhouse_query(
                f"""
                SELECT count() AS cnt
                FROM
                (
                    SELECT
                        {primary_key},
                        argMax(is_deleted, (kafka_partition, kafka_offset)) AS latest_deleted
                    FROM {relation}
                    GROUP BY {primary_key}
                    HAVING latest_deleted = 0
                )
                """
            )
            value = rows[0].get("cnt") if rows else None
            if not isinstance(value, (int, float, str)):
                raise RuntimeError(
                    f"Could not read Iceberg current count for {spec.entity}"
                )
            counts[spec.entity] = int(value)
        return counts

    @staticmethod
    def fetch_iceberg_physical_counts() -> dict[str, int]:
        """Return one latest row per primary key, including tombstoned rows."""

        counts: dict[str, int] = {}
        for spec in ALL_SERVING_ENTITIES:
            relation = format_ch_relation(spec.changes_relation)
            primary_key = ", ".join(spec.primary_key)
            rows = clickhouse_query(
                f"""
                SELECT count() AS cnt
                FROM
                (
                    SELECT {primary_key}
                    FROM {relation}
                    GROUP BY {primary_key}
                )
                """
            )
            value = rows[0].get("cnt") if rows else None
            if not isinstance(value, (int, float, str)):
                raise RuntimeError(
                    f"Could not read physical current count for {spec.entity}"
                )
            counts[spec.entity] = int(value)
        return counts

    @staticmethod
    def fetch_iceberg_deleted_counts() -> dict[str, int]:
        """Return the number of latest tombstoned keys per entity."""

        counts: dict[str, int] = {}
        for spec in ALL_SERVING_ENTITIES:
            relation = format_ch_relation(spec.changes_relation)
            primary_key = ", ".join(spec.primary_key)
            rows = clickhouse_query(
                f"""
                SELECT count() AS cnt
                FROM
                (
                    SELECT
                        {primary_key},
                        argMax(is_deleted, (kafka_partition, kafka_offset)) AS latest_deleted
                    FROM {relation}
                    GROUP BY {primary_key}
                    HAVING latest_deleted = 1
                )
                """
            )
            value = rows[0].get("cnt") if rows else None
            if not isinstance(value, (int, float, str)):
                raise RuntimeError(
                    f"Could not read deleted current count for {spec.entity}"
                )
            counts[spec.entity] = int(value)
        return counts

    @staticmethod
    def fetch_iceberg_current_rows() -> dict[str, list[dict[str, object]]]:
        """Return the latest Iceberg row identity for every business key.

        The row hash is the canonical business-value identity produced by
        Silver.  Keeping the delete bit alongside it lets rebuild validation
        compare both visible and tombstoned keys rather than only row counts.
        """

        rows_by_entity: dict[str, list[dict[str, object]]] = {}
        for spec in ALL_SERVING_ENTITIES:
            relation = format_ch_relation(spec.changes_relation)
            primary_key = ", ".join(spec.primary_key)
            rows_by_entity[spec.entity] = clickhouse_query(
                f"""
                SELECT
                    {primary_key},
                    argMax(row_hash, (kafka_partition, kafka_offset)) AS row_hash,
                    argMax(is_deleted, (kafka_partition, kafka_offset)) AS is_deleted
                FROM {relation}
                GROUP BY {primary_key}
                """
            )
        return rows_by_entity

    @staticmethod
    def fetch_candidate_current_rows(
        sync_run_seq: int,
    ) -> dict[str, list[dict[str, object]]]:
        """Return the latest physical candidate row for every business key."""

        rows_by_entity: dict[str, list[dict[str, object]]] = {}
        for spec in ALL_SERVING_ENTITIES:
            primary_key = ", ".join(spec.primary_key)
            rows_by_entity[spec.entity] = clickhouse_query(
                f"""
                SELECT {primary_key}, last_row_hash AS row_hash, is_deleted
                FROM
                (
                    SELECT
                        {primary_key},
                        last_row_hash,
                        is_deleted,
                        row_number() OVER (
                            PARTITION BY {primary_key}
                            ORDER BY kafka_offset DESC, sync_run_seq DESC
                        ) AS _version_rank
                    FROM {spec.ch_current_versions_table}
                    WHERE sync_run_seq = {sync_run_seq}
                )
                WHERE _version_rank = 1
                """
            )
        return rows_by_entity

    @staticmethod
    def fetch_current_rows() -> dict[str, list[dict[str, object]]]:
        """Return visible rows from the currently published stable views."""

        rows_by_entity: dict[str, list[dict[str, object]]] = {}
        for spec in ALL_SERVING_ENTITIES:
            primary_key = ", ".join(spec.primary_key)
            rows_by_entity[spec.entity] = clickhouse_query(
                f"""
                SELECT {primary_key}, last_row_hash AS row_hash, is_deleted
                FROM {spec.ch_current_view}
                """
            )
        return rows_by_entity

    @staticmethod
    def fetch_audit_error_counts() -> dict[str, int]:
        """Return rejected/schema-error counts used by the Stage V oracle."""

        queries = {
            "rejected": """
                SELECT count() AS cnt
                FROM lakehouse.`silver.customers_changes`
                WHERE lower(toString(apply_status)) != 'applied'
            """,
            "schema_violations": """
                SELECT count() AS cnt
                FROM lakehouse.`audit.schema_violations`
            """,
        }
        # Rejection records are stored in each entity's Silver changes table;
        # sum them rather than looking at one representative entity.
        rejected = 0
        for spec in ALL_SERVING_ENTITIES:
            relation = format_ch_relation(spec.changes_relation)
            rows = clickhouse_query(
                f"""
                SELECT count() AS cnt
                FROM {relation}
                WHERE lower(toString(apply_status)) != 'applied'
                """
            )
            value = rows[0].get("cnt") if rows else None
            if not isinstance(value, (int, float, str)):
                raise RuntimeError(f"Could not read rejected count for {spec.entity}")
            rejected += int(value)

        result: dict[str, int] = {"rejected": rejected}
        rows = clickhouse_query(queries["schema_violations"])
        value = rows[0].get("cnt") if rows else None
        if not isinstance(value, (int, float, str)):
            raise RuntimeError("Could not read schema violation count")
        result["schema_violations"] = int(value)
        return result

    @staticmethod
    def _serving_business_columns(spec: ServingEntitySpec) -> tuple[str, ...]:
        """Discover additive Silver fields and mirror them into serving tables."""

        relation = format_ch_relation(spec.changes_relation)
        rows = clickhouse_query(f"DESCRIBE TABLE {relation}")
        metadata_columns = {
            "event_id",
            "op",
            "is_snapshot",
            "is_deleted",
            "apply_status",
            "error_code",
            "error_message",
            "source_ts",
            "source_server_id",
            "source_gtid",
            "source_binlog_file",
            "source_binlog_file_index",
            "source_binlog_pos",
            "source_row",
            "transaction_id",
            "transaction_total_order",
            "transaction_data_collection_order",
            "kafka_topic",
            "kafka_partition",
            "kafka_offset",
            "kafka_timestamp",
            "key_schema_id",
            "value_schema_id",
            "schema_fingerprint",
            "contract_version",
            "before_row_hash",
            "after_row_hash",
            "row_hash",
            "bronze_ingested_at",
            "normalized_at",
        }
        fixed = set(spec.primary_key) | set(spec.business_columns)
        extras: list[tuple[str, str]] = []
        for row in rows:
            name = row.get("name")
            data_type = row.get("type")
            if (
                not isinstance(name, str)
                or not isinstance(data_type, str)
                or name in metadata_columns
                or name in fixed
            ):
                continue
            if not name.replace("_", "").isalnum():
                raise RuntimeError(f"Invalid additive Silver column name: {name}")
            extras.append((name, data_type))

        for name, data_type in extras:
            for table in (spec.ch_events_table, spec.ch_current_versions_table):
                clickhouse_execute(
                    f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS `{name}` {data_type}"
                )
        if extras:
            ClickHouseServingMaterializer._refresh_current_view(spec)
        return (*spec.business_columns, *(name for name, _ in extras))

    @staticmethod
    def _refresh_current_view(spec: ServingEntitySpec) -> None:
        """Recreate a stable current view after an additive table change.

        ClickHouse stores the output schema of a view created from ``SELECT
        *``.  Adding a column to ``*_current_versions`` therefore does not
        automatically expose it through the already-created stable view.
        Refreshing the view after discovering additive Silver fields keeps the
        serving contract aligned with the version table while preserving the
        publication and latest-version filters.
        """

        primary_key = ", ".join(spec.primary_key)
        clickhouse_execute(
            f"""
            CREATE OR REPLACE VIEW {spec.ch_current_view} AS
            SELECT * EXCEPT (_version_rank)
            FROM
            (
                SELECT
                    *,
                    row_number() OVER (
                        PARTITION BY {primary_key}
                        ORDER BY kafka_offset DESC, sync_run_seq DESC
                    ) AS _version_rank
                FROM {spec.ch_current_versions_table}
                WHERE sync_run_seq IN
                (
                    SELECT sync_run_seq
                    FROM serving_control.published_runs_current
                    WHERE publication_status = 'PUBLISHED'
                )
            )
            WHERE _version_rank = 1 AND NOT is_deleted
            """
        )

    @staticmethod
    def fetch_candidate_current_counts(sync_run_seq: int) -> dict[str, int]:
        """Return deduplicated non-deleted current counts for one candidate run."""

        counts: dict[str, int] = {}
        for spec in ALL_SERVING_ENTITIES:
            primary_key = ", ".join(spec.primary_key)
            rows = clickhouse_query(
                f"""
                SELECT count() AS cnt
                FROM
                (
                    SELECT
                        {primary_key},
                        is_deleted,
                        row_number() OVER (
                            PARTITION BY {primary_key}
                            ORDER BY kafka_offset DESC, sync_run_seq DESC
                        ) AS _version_rank
                    FROM {spec.ch_current_versions_table}
                    WHERE sync_run_seq = {sync_run_seq}
                )
                WHERE _version_rank = 1 AND NOT is_deleted
                """
            )
            value = rows[0].get("cnt") if rows else None
            if not isinstance(value, (int, float, str)):
                raise RuntimeError(
                    f"Could not read candidate serving count for {spec.entity}"
                )
            counts[spec.entity] = int(value)
        return counts

    @staticmethod
    def materialize_entity_events(
        spec: ServingEntitySpec,
        sync_run_seq: int,
        sync_run_id: str,
        target_transaction_id: str | None = None,
        target_offsets: dict[str, int] | None = None,
    ) -> int:
        # Drop candidate partition if exists
        drop_sql = f"ALTER TABLE {spec.ch_events_table} DROP PARTITION {sync_run_seq}"
        with contextlib.suppress(Exception):
            clickhouse_query(drop_sql)

        business_columns = ClickHouseServingMaterializer._serving_business_columns(spec)
        event_columns = (
            "event_id",
            "op",
            "is_snapshot",
            "is_deleted",
            "apply_status",
            "error_code",
            "error_message",
            *spec.primary_key,
            *business_columns,
            "source_ts",
            "source_server_id",
            "source_gtid",
            "source_binlog_file",
            "source_binlog_file_index",
            "source_binlog_pos",
            "source_row",
            "transaction_id",
            "transaction_total_order",
            "transaction_data_collection_order",
            "kafka_topic",
            "kafka_partition",
            "kafka_offset",
            "kafka_timestamp",
            "key_schema_id",
            "value_schema_id",
            "schema_fingerprint",
            "contract_version",
            "before_row_hash",
            "after_row_hash",
            "row_hash",
            "bronze_ingested_at",
            "normalized_at",
        )
        cols = ", ".join(event_columns)
        relation = format_ch_relation(spec.changes_relation)

        where_sql = ""
        if target_offsets:
            entity_topic = f"olist_cdc.olist_oltp.{spec.entity}"
            clauses = []
            for key, offset in sorted(target_offsets.items()):
                topic, separator, partition_text = key.rpartition(":")
                if separator and topic == entity_topic and partition_text.isdigit():
                    clauses.append(
                        "(kafka_topic = "
                        f"'{topic}' AND kafka_partition = {int(partition_text)} "
                        f"AND kafka_offset <= {int(offset)})"
                    )
            if not clauses:
                raise RuntimeError(
                    f"No serving boundary offset exists for entity {spec.entity}"
                )
            where_sql = "WHERE " + " OR ".join(clauses)

        insert_sql = f"""
        INSERT INTO {spec.ch_events_table} (
            {cols}, sync_run_seq, sync_run_id
        )
        SELECT
            {cols}, {sync_run_seq}, '{sync_run_id}'
        FROM {relation}
        {where_sql}
        """
        clickhouse_query(insert_sql)

        count_sql = f"SELECT count() as cnt FROM {spec.ch_events_table} WHERE sync_run_seq = {sync_run_seq}"
        res = clickhouse_query(count_sql)
        cnt_val = res[0].get("cnt") if res else None
        return int(cnt_val) if isinstance(cnt_val, (int, str, float)) else 0

    @staticmethod
    def materialize_entity_current(
        spec: ServingEntitySpec,
        sync_run_seq: int,
        sync_run_id: str,
    ) -> int:
        drop_sql = f"ALTER TABLE {spec.ch_current_versions_table} DROP PARTITION {sync_run_seq}"
        with contextlib.suppress(Exception):
            clickhouse_query(drop_sql)

        business_columns = ClickHouseServingMaterializer._serving_business_columns(spec)
        cols = ", ".join(business_columns)
        pk_cols = ", ".join(spec.primary_key)

        insert_sql = f"""
        INSERT INTO {spec.ch_current_versions_table} (
            sync_run_seq, sync_run_id, {pk_cols}, {cols}, is_deleted,
            deleted_at, last_event_id, last_source_ts, last_transaction_id,
            kafka_partition, kafka_offset, last_row_hash, contract_version,
            updated_at
        )
        SELECT
            {sync_run_seq}, '{sync_run_id}', {pk_cols}, {cols}, is_deleted,
            if(is_deleted, source_ts, NULL) AS deleted_at,
            event_id AS last_event_id,
            source_ts AS last_source_ts,
            transaction_id AS last_transaction_id,
            kafka_partition,
            kafka_offset,
            coalesce(row_hash, '') AS last_row_hash,
            contract_version,
            now64(6, 'UTC') AS updated_at
        FROM {spec.ch_events_table}
        WHERE sync_run_seq = {sync_run_seq}
        """
        clickhouse_query(insert_sql)

        count_sql = f"SELECT count() as cnt FROM {spec.ch_current_versions_table} WHERE sync_run_seq = {sync_run_seq}"
        res = clickhouse_query(count_sql)
        cnt_val = res[0].get("cnt") if res else None
        return int(cnt_val) if isinstance(cnt_val, (int, str, float)) else 0

    @staticmethod
    def publish_marker(report: ServingSyncReport) -> None:
        published_at_str = report.published_at
        canonical_json = json.dumps(report.to_canonical_dict())
        # The report is stored in a ClickHouse String literal.  JSON values
        # such as the dbt ``--vars`` argument contain backslash-escaped
        # quotes; preserve those backslashes in the stored value so the
        # marker remains parseable JSON when read back for final validation.
        clickhouse_report_json = canonical_json.replace("\\", "\\\\").replace(
            "'", "\\'"
        )

        insert_sql = f"""
        INSERT INTO serving_control.published_runs (
            sync_run_seq, sync_run_id, previous_transaction_id, target_transaction_id,
            publication_status, source_snapshot_completed, published_at, report_json
        ) VALUES (
            {report.sync_run_seq},
            '{report.sync_run_id}',
            {f"'{report.previous_transaction_id}'" if report.previous_transaction_id else "NULL"},
            {f"'{report.target_transaction_id}'" if report.target_transaction_id else "NULL"},
            'PUBLISHED',
            1,
            parseDateTime64BestEffort('{published_at_str}'),
            '{clickhouse_report_json}'
        )
        """
        clickhouse_query(insert_sql)

    @staticmethod
    def fetch_transaction_rows() -> list[dict[str, object]]:
        sql = """
        SELECT
            transaction_id,
            status,
            end_kafka_offset,
            event_count
        FROM lakehouse."audit.mysql_transactions"
        ORDER BY recorded_at ASC, end_kafka_offset ASC
        """
        transaction_rows = clickhouse_query(sql)
        count_sql = """
        SELECT transaction_id, entity, count() AS entity_event_count
        FROM (
            SELECT transaction_id, 'customers' AS entity
            FROM lakehouse."silver.customers_changes"
            WHERE transaction_id IS NOT NULL
            UNION ALL
            SELECT transaction_id, 'orders' AS entity
            FROM lakehouse."silver.orders_changes"
            WHERE transaction_id IS NOT NULL
            UNION ALL
            SELECT transaction_id, 'order_items' AS entity
            FROM lakehouse."silver.order_items_changes"
            WHERE transaction_id IS NOT NULL
            UNION ALL
            SELECT transaction_id, 'order_payments' AS entity
            FROM lakehouse."silver.order_payments_changes"
            WHERE transaction_id IS NOT NULL
            UNION ALL
            SELECT transaction_id, 'order_reviews' AS entity
            FROM lakehouse."silver.order_reviews_changes"
            WHERE transaction_id IS NOT NULL
            UNION ALL
            SELECT transaction_id, 'products' AS entity
            FROM lakehouse."silver.products_changes"
            WHERE transaction_id IS NOT NULL
            UNION ALL
            SELECT transaction_id, 'sellers' AS entity
            FROM lakehouse."silver.sellers_changes"
            WHERE transaction_id IS NOT NULL
            UNION ALL
            SELECT transaction_id, 'product_category_translation' AS entity
            FROM lakehouse."silver.product_category_translation_changes"
            WHERE transaction_id IS NOT NULL
        )
        GROUP BY transaction_id, entity
        """
        counts_by_transaction: dict[str, dict[str, int]] = {}
        for row in clickhouse_query(count_sql):
            transaction_id = row.get("transaction_id")
            entity = row.get("entity")
            count = row.get("entity_event_count")
            if transaction_id is None or entity is None:
                continue
            if isinstance(count, (int, float, str)):
                counts_by_transaction.setdefault(str(transaction_id), {})[
                    str(entity)
                ] = int(count)

        # The audit table can contain the same completion record more than
        # once after a scheduler retry.  Keep one row per physical boundary;
        # do not deduplicate by transaction_id alone because the same MySQL
        # transaction may be observed at successive Kafka end offsets.
        unique_rows: dict[tuple[str, str, str], dict[str, object]] = {}
        for row in transaction_rows:
            transaction_id = row.get("transaction_id")
            status = str(row.get("status", ""))
            end_offset = row.get("end_kafka_offset")
            if transaction_id is None or end_offset is None:
                continue
            key = (str(transaction_id), status, str(end_offset))
            unique_rows[key] = row

        for row in sorted(
            unique_rows.values(),
            key=lambda item: (
                _as_int(item.get("end_kafka_offset", 0)),
                str(item.get("transaction_id", "")),
            ),
        ):
            transaction_id = row.get("transaction_id")
            entity_counts = counts_by_transaction.get(str(transaction_id), {})
            row["entity_counts"] = entity_counts
            raw_count = row.get("event_count")
            if (
                not isinstance(raw_count, (int, float, str)) or int(raw_count) == 0
            ) and entity_counts:
                row["event_count"] = sum(entity_counts.values())
        return sorted(
            unique_rows.values(),
            key=lambda item: (
                _as_int(item.get("end_kafka_offset", 0)),
                str(item.get("transaction_id", "")),
            ),
        )

    @staticmethod
    def fetch_entity_metrics(
        target_transaction_end_offset: int | None = None,
    ) -> dict[str, dict[str, object]]:
        """Return Silver metrics bounded by a selected committed transaction.

        Silver is written continuously, while serving publication is allowed
        to consume only the complete transaction prefix selected by the
        boundary planner.  Without this predicate an OPEN transaction that
        has already reached Silver could leak into the candidate counts and
        offsets, making a publication appear complete when it is not.

        Snapshot rows have no transaction ID and remain eligible for the
        initial snapshot.  For a transaction-bound sync, all other rows must
        belong to a COMPLETE audit transaction whose end offset is within the
        frozen boundary.
        """

        if target_transaction_end_offset is not None:
            if target_transaction_end_offset < 0:
                raise ValueError("target_transaction_end_offset must be non-negative")
            boundary_filter = f"""
                    WHERE transaction_id IS NULL
                       OR transaction_id IN
                       (
                           SELECT transaction_id
                           FROM lakehouse."audit.mysql_transactions"
                           WHERE status = 'COMPLETE'
                             AND end_kafka_offset <= {target_transaction_end_offset}
                       )
                    """
        else:
            boundary_filter = ""

        rows: list[dict[str, object]] = []
        for spec in ALL_SERVING_ENTITIES:
            relation = format_ch_relation(spec.changes_relation)
            rows.extend(
                clickhouse_query(
                    f"""
                    SELECT
                        '{spec.entity}' AS entity,
                        kafka_topic,
                        kafka_partition,
                        max(kafka_offset) AS max_offset,
                        count() AS event_count
                    FROM {relation}
                    {boundary_filter}
                    GROUP BY kafka_topic, kafka_partition
                    """
                )
            )

        metrics: dict[str, dict[str, object]] = {
            spec.entity: {
                "event_count": 0,
                "target_offsets": {},
            }
            for spec in ALL_SERVING_ENTITIES
        }
        for row in rows:
            entity = str(row.get("entity", ""))
            if entity not in metrics:
                continue
            raw_count = row.get("event_count")
            raw_offset = row.get("max_offset")
            topic = row.get("kafka_topic")
            partition = row.get("kafka_partition")
            if not isinstance(raw_count, (int, float, str)):
                continue
            entity_metrics = metrics[entity]
            entity_metrics["event_count"] = _as_int(
                entity_metrics.get("event_count")
            ) + int(raw_count)
            if (
                isinstance(raw_offset, (int, float, str))
                and isinstance(topic, str)
                and isinstance(partition, (int, float, str))
            ):
                offsets = entity_metrics["target_offsets"]
                assert isinstance(offsets, dict)
                offsets[f"{topic}:{int(partition)}"] = int(raw_offset)
        return metrics

    @staticmethod
    def fetch_silver_progress() -> dict[str, dict[str, object]]:
        """Return the committed Silver progress row for every entity."""

        allowed_entities = {spec.entity for spec in ALL_SERVING_ENTITIES}
        entity_literals = ", ".join(
            f"'{entity}'" for entity in sorted(allowed_entities)
        )
        rows = clickhouse_query(
            f"""
            SELECT
                entity,
                argMax(last_kafka_offset, recorded_at) AS last_kafka_offset,
                argMax(changes_snapshot_id, recorded_at) AS changes_snapshot_id,
                argMax(status, recorded_at) AS status
            FROM lakehouse.`audit.silver_progress`
            WHERE entity IN ({entity_literals})
            GROUP BY entity
            """
        )
        return {
            str(row["entity"]): dict(row)
            for row in rows
            if isinstance(row.get("entity"), str) and row["entity"] in allowed_entities
        }

    @staticmethod
    def fetch_iceberg_snapshots() -> dict[str, int]:
        sql = """
        SELECT
            entity,
            argMax(changes_snapshot_id, recorded_at) AS snapshot_id
        FROM lakehouse."audit.silver_progress"
        WHERE entity IN (
            'customers',
            'orders',
            'order_items',
            'order_payments',
            'order_reviews',
            'products',
            'sellers',
            'product_category_translation'
        )
        GROUP BY entity
        """
        res = clickhouse_query(sql)
        out: dict[str, int] = {}
        allowed_entities = {spec.entity for spec in ALL_SERVING_ENTITIES}
        for row in res:
            ent = str(row.get("entity", ""))
            snap = row.get("snapshot_id")
            if (
                ent in allowed_entities
                and isinstance(snap, (int, str, float))
                and int(snap) > 0
            ):
                out[ent] = int(snap)
        if set(out) != allowed_entities:
            missing = sorted(allowed_entities - set(out))
            raise RuntimeError(
                "Silver progress is missing committed snapshots for: "
                + ", ".join(missing)
            )
        return out
