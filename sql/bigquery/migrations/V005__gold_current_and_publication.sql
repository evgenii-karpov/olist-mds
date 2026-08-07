-- SQL-owned BigQuery Gold current state and atomic publication procedure.
--
-- dbt writes <model>__history rows.  This migration owns the durable current
-- tables, stable views, and the one procedure that applies a validated run.
-- The procedure is deliberately fail-closed when control/model evidence is
-- incomplete or the active predecessor has changed.

CREATE TABLE IF NOT EXISTS `{{ project_id }}.olist_gold_store.dim_date__current` (
  sync_run_seq INT64,
  sync_run_id STRING,
  operation_type STRING,
  build_mode STRING,
  previous_boundary_id STRING,
  current_boundary_id STRING,
  built_at TIMESTAMP,
  date_key INT64,
  date_day DATE,
  year_number INT64,
  month_number INT64,
  day_number INT64,
  quarter_number INT64,
  week_number INT64,
  day_of_week_number INT64,
  year_month STRING,
  month_name STRING,
  is_weekend BOOL
)
CLUSTER BY date_key;

CREATE TABLE IF NOT EXISTS `{{ project_id }}.olist_gold_store.dim_order_status__current` (
  sync_run_seq INT64,
  sync_run_id STRING,
  operation_type STRING,
  build_mode STRING,
  previous_boundary_id STRING,
  current_boundary_id STRING,
  built_at TIMESTAMP,
  order_status_key STRING,
  order_status STRING,
  is_successful_status BOOL,
  is_failed_status BOOL
)
CLUSTER BY order_status;

CREATE TABLE IF NOT EXISTS `{{ project_id }}.olist_gold_store.dim_seller__current` (
  sync_run_seq INT64,
  sync_run_id STRING,
  operation_type STRING,
  build_mode STRING,
  previous_boundary_id STRING,
  current_boundary_id STRING,
  built_at TIMESTAMP,
  seller_key STRING,
  seller_id STRING,
  seller_zip_code_prefix STRING,
  seller_city STRING,
  seller_state STRING
)
CLUSTER BY seller_id;

CREATE TABLE IF NOT EXISTS `{{ project_id }}.olist_gold_store.dim_customer_scd2__current` (
  sync_run_seq INT64,
  sync_run_id STRING,
  operation_type STRING,
  build_mode STRING,
  previous_boundary_id STRING,
  current_boundary_id STRING,
  built_at TIMESTAMP,
  customer_key STRING,
  customer_id STRING,
  customer_unique_id STRING,
  customer_zip_code_prefix STRING,
  customer_city STRING,
  customer_state STRING,
  valid_from TIMESTAMP,
  valid_to TIMESTAMP,
  is_current BOOL,
  opening_event_id STRING,
  dimension_row_hash STRING,
  opening_source_ts TIMESTAMP,
  opening_kafka_topic STRING,
  opening_kafka_partition INT64,
  opening_kafka_offset INT64
)
CLUSTER BY customer_unique_id;

CREATE TABLE IF NOT EXISTS `{{ project_id }}.olist_gold_store.dim_product_scd2__current` (
  sync_run_seq INT64,
  sync_run_id STRING,
  operation_type STRING,
  build_mode STRING,
  previous_boundary_id STRING,
  current_boundary_id STRING,
  built_at TIMESTAMP,
  product_key STRING,
  product_id STRING,
  product_category_name STRING,
  product_category_name_english STRING,
  product_name_lenght INT64,
  product_description_lenght INT64,
  product_photos_qty INT64,
  product_weight_g INT64,
  product_length_cm INT64,
  product_height_cm INT64,
  product_width_cm INT64,
  valid_from TIMESTAMP,
  valid_to TIMESTAMP,
  is_current BOOL,
  opening_event_id STRING,
  dimension_row_hash STRING,
  opening_source_ts TIMESTAMP,
  opening_kafka_topic STRING,
  opening_kafka_partition INT64,
  opening_kafka_offset INT64
)
CLUSTER BY product_id;

CREATE TABLE IF NOT EXISTS `{{ project_id }}.olist_gold_store.fact_order_items__current` (
  sync_run_seq INT64,
  sync_run_id STRING,
  operation_type STRING,
  build_mode STRING,
  previous_boundary_id STRING,
  current_boundary_id STRING,
  built_at TIMESTAMP,
  order_item_key STRING,
  order_id STRING,
  order_item_id INT64,
  customer_key STRING,
  product_key STRING,
  seller_key STRING,
  order_status_key STRING,
  order_purchase_date_key INT64,
  order_approved_date_key INT64,
  order_delivered_customer_date_key INT64,
  order_estimated_delivery_date_key INT64,
  customer_id STRING,
  customer_unique_id STRING,
  product_id STRING,
  seller_id STRING,
  order_status STRING,
  order_purchase_timestamp TIMESTAMP,
  order_approved_at TIMESTAMP,
  order_delivered_carrier_date TIMESTAMP,
  order_delivered_customer_date TIMESTAMP,
  order_estimated_delivery_date TIMESTAMP,
  shipping_limit_date TIMESTAMP,
  price NUMERIC,
  freight_value NUMERIC,
  gross_item_amount NUMERIC,
  allocated_payment_value NUMERIC,
  delivery_days INT64,
  delivery_delay_days INT64,
  is_delivered_late BOOL
)
PARTITION BY DATE(order_purchase_timestamp)
CLUSTER BY order_id, customer_id, product_id;

CREATE TABLE IF NOT EXISTS `{{ project_id }}.olist_gold_store.mart_daily_revenue__current` (
  sync_run_seq INT64,
  sync_run_id STRING,
  operation_type STRING,
  build_mode STRING,
  previous_boundary_id STRING,
  current_boundary_id STRING,
  built_at TIMESTAMP,
  order_purchase_date DATE,
  gross_revenue NUMERIC,
  allocated_payment_revenue NUMERIC,
  product_revenue NUMERIC,
  freight_revenue NUMERIC,
  orders_count INT64,
  customers_count INT64,
  items_count INT64,
  average_order_value NUMERIC,
  average_paid_order_value NUMERIC,
  average_delivery_days NUMERIC,
  late_deliveries_count INT64
)
PARTITION BY order_purchase_date
CLUSTER BY order_purchase_date;

CREATE TABLE IF NOT EXISTS `{{ project_id }}.olist_gold_store.mart_monthly_arpu__current` (
  sync_run_seq INT64,
  sync_run_id STRING,
  operation_type STRING,
  build_mode STRING,
  previous_boundary_id STRING,
  current_boundary_id STRING,
  built_at TIMESTAMP,
  order_month DATE,
  active_customers INT64,
  total_revenue NUMERIC,
  arpu NUMERIC,
  orders_count INT64,
  orders_per_customer NUMERIC,
  average_order_value NUMERIC,
  repeat_customer_rate NUMERIC
)
PARTITION BY order_month
CLUSTER BY order_month;

CREATE OR REPLACE VIEW `{{ project_id }}.olist_gold.dim_date`
OPTIONS (description = 'Stable published Gold date dimension')
AS SELECT * FROM `{{ project_id }}.olist_gold_store.dim_date__current`;

CREATE OR REPLACE VIEW `{{ project_id }}.olist_gold.dim_order_status`
OPTIONS (description = 'Stable published Gold order-status dimension')
AS SELECT * FROM `{{ project_id }}.olist_gold_store.dim_order_status__current`;

CREATE OR REPLACE VIEW `{{ project_id }}.olist_gold.dim_seller`
OPTIONS (description = 'Stable published Gold seller dimension')
AS SELECT * FROM `{{ project_id }}.olist_gold_store.dim_seller__current`;

CREATE OR REPLACE VIEW `{{ project_id }}.olist_gold.dim_customer_scd2`
OPTIONS (description = 'Stable published Gold customer SCD2 dimension')
AS SELECT * FROM `{{ project_id }}.olist_gold_store.dim_customer_scd2__current`;

CREATE OR REPLACE VIEW `{{ project_id }}.olist_gold.dim_product_scd2`
OPTIONS (description = 'Stable published Gold product SCD2 dimension')
AS SELECT * FROM `{{ project_id }}.olist_gold_store.dim_product_scd2__current`;

CREATE OR REPLACE VIEW `{{ project_id }}.olist_gold.fact_order_items`
OPTIONS (description = 'Stable published Gold order-item fact')
AS SELECT * FROM `{{ project_id }}.olist_gold_store.fact_order_items__current`;

CREATE OR REPLACE VIEW `{{ project_id }}.olist_gold.mart_daily_revenue`
OPTIONS (description = 'Stable published Gold daily revenue mart')
AS SELECT * FROM `{{ project_id }}.olist_gold_store.mart_daily_revenue__current`;

CREATE OR REPLACE VIEW `{{ project_id }}.olist_gold.mart_monthly_arpu`
OPTIONS (description = 'Stable published Gold monthly ARPU mart')
AS SELECT * FROM `{{ project_id }}.olist_gold_store.mart_monthly_arpu__current`;

CREATE OR REPLACE PROCEDURE
  `{{ project_id }}.olist_serving_control.publish_gcp_run`(
    IN p_sync_run_seq INT64,
    IN p_expected_active_sync_run_seq INT64
  )
BEGIN
  DECLARE active_seq INT64;
  DECLARE run_status STRING;
  DECLARE model_count INT64;
  DECLARE ready_model_count INT64;
  DECLARE entity_count INT64;
  DECLARE ready_entity_count INT64;
  DECLARE control_updated_count INT64;
  DECLARE publication_updated_count INT64;

  SET active_seq = COALESCE(
    (
      SELECT active_sync_run_seq
      FROM `{{ project_id }}.olist_serving_control.control_state`
      WHERE state_key = 'gcp' AND target = 'gcp'
    ),
    0
  );
  SET run_status = (
    SELECT status
    FROM `{{ project_id }}.olist_serving_control.serving_runs`
    WHERE target = 'gcp' AND sync_run_seq = p_sync_run_seq
  );

  BEGIN TRANSACTION;
  IF active_seq = p_sync_run_seq THEN
    UPDATE `{{ project_id }}.olist_serving_control.serving_runs`
    SET status = 'SUCCEEDED',
        status_reason = 'NONE',
        published_at = COALESCE(published_at, CURRENT_TIMESTAMP()),
        completed_at = COALESCE(completed_at, CURRENT_TIMESTAMP()),
        updated_at = CURRENT_TIMESTAMP()
    WHERE target = 'gcp' AND sync_run_seq = p_sync_run_seq;
    COMMIT TRANSACTION;
    SELECT 'IDEMPOTENT' AS publication_result, p_sync_run_seq AS sync_run_seq;
  ELSEIF active_seq != p_expected_active_sync_run_seq THEN
    UPDATE `{{ project_id }}.olist_serving_control.serving_runs`
    SET status = 'FAILED_TERMINAL',
        status_reason = 'PUBLICATION_DRIFT',
        error_code = 'STALE_PREDECESSOR',
        error_message = 'active_sync_run_seq changed before publication',
        conflicted_at = CURRENT_TIMESTAMP(),
        failed_at = CURRENT_TIMESTAMP(),
        completed_at = CURRENT_TIMESTAMP(),
        updated_at = CURRENT_TIMESTAMP()
    WHERE target = 'gcp'
      AND sync_run_seq = p_sync_run_seq
      AND status != 'SUCCEEDED';
    COMMIT TRANSACTION;
    SELECT 'CONFLICTED' AS publication_result, p_sync_run_seq AS sync_run_seq;
  ELSEIF COALESCE(run_status, '') != 'READY_TO_PUBLISH' THEN
    ROLLBACK TRANSACTION;
    SELECT 'NOT_READY' AS publication_result, p_sync_run_seq AS sync_run_seq;
  ELSE
    SET model_count = (
      SELECT COUNT(*)
      FROM `{{ project_id }}.olist_serving_control.model_results`
      WHERE target = 'gcp' AND sync_run_seq = p_sync_run_seq
    );
    SET ready_model_count = (
      SELECT COUNT(*)
      FROM `{{ project_id }}.olist_serving_control.model_results`
      WHERE target = 'gcp'
        AND sync_run_seq = p_sync_run_seq
        AND status = 'SUCCEEDED'
    );
    SET entity_count = (
      SELECT COUNT(*)
      FROM `{{ project_id }}.olist_serving_control.entity_results`
      WHERE target = 'gcp' AND sync_run_seq = p_sync_run_seq
    );
    SET ready_entity_count = (
      SELECT COUNT(*)
      FROM `{{ project_id }}.olist_serving_control.entity_results`
      WHERE target = 'gcp'
        AND sync_run_seq = p_sync_run_seq
        AND status IN ('VALIDATED', 'MATERIALIZED')
    );

    IF model_count != 8 OR ready_model_count != 8
       OR entity_count != 8 OR ready_entity_count != 8 THEN
      ROLLBACK TRANSACTION;
      SELECT 'NOT_READY' AS publication_result, p_sync_run_seq AS sync_run_seq;
    ELSE
      DELETE FROM `{{ project_id }}.olist_gold_store.dim_date__current`
      WHERE date_key IN (
        SELECT date_key
        FROM `{{ project_id }}.olist_gold_store.dim_date__history`
        WHERE sync_run_seq = p_sync_run_seq
      );
      INSERT INTO `{{ project_id }}.olist_gold_store.dim_date__current`
      SELECT *
      FROM `{{ project_id }}.olist_gold_store.dim_date__history`
      WHERE sync_run_seq = p_sync_run_seq;

      DELETE FROM `{{ project_id }}.olist_gold_store.dim_order_status__current`
      WHERE order_status IN (
        SELECT order_status
        FROM `{{ project_id }}.olist_gold_store.dim_order_status__history`
        WHERE sync_run_seq = p_sync_run_seq
      );
      INSERT INTO `{{ project_id }}.olist_gold_store.dim_order_status__current`
      SELECT *
      FROM `{{ project_id }}.olist_gold_store.dim_order_status__history`
      WHERE sync_run_seq = p_sync_run_seq;

      MERGE `{{ project_id }}.olist_gold_store.dim_seller__current` AS target
      USING (
        SELECT *
        FROM `{{ project_id }}.olist_gold_store.dim_seller__history`
        WHERE sync_run_seq = p_sync_run_seq
      ) AS source
      ON target.seller_id = source.seller_id
      WHEN MATCHED AND source.operation_type = 'DELETE' THEN DELETE
      WHEN MATCHED THEN UPDATE SET
        sync_run_seq = source.sync_run_seq,
        sync_run_id = source.sync_run_id,
        operation_type = source.operation_type,
        build_mode = source.build_mode,
        previous_boundary_id = source.previous_boundary_id,
        current_boundary_id = source.current_boundary_id,
        built_at = source.built_at,
        seller_key = source.seller_key,
        seller_id = source.seller_id,
        seller_zip_code_prefix = source.seller_zip_code_prefix,
        seller_city = source.seller_city,
        seller_state = source.seller_state
      WHEN NOT MATCHED AND source.operation_type != 'DELETE' THEN INSERT ROW;

      MERGE `{{ project_id }}.olist_gold_store.dim_customer_scd2__current` AS target
      USING (
        SELECT *
        FROM `{{ project_id }}.olist_gold_store.dim_customer_scd2__history`
        WHERE sync_run_seq = p_sync_run_seq
      ) AS source
      ON target.customer_key = source.customer_key
      WHEN MATCHED AND source.operation_type = 'DELETE' THEN DELETE
      WHEN MATCHED THEN UPDATE SET
        sync_run_seq = source.sync_run_seq,
        sync_run_id = source.sync_run_id,
        operation_type = source.operation_type,
        build_mode = source.build_mode,
        previous_boundary_id = source.previous_boundary_id,
        current_boundary_id = source.current_boundary_id,
        built_at = source.built_at,
        customer_key = source.customer_key,
        customer_id = source.customer_id,
        customer_unique_id = source.customer_unique_id,
        customer_zip_code_prefix = source.customer_zip_code_prefix,
        customer_city = source.customer_city,
        customer_state = source.customer_state,
        valid_from = source.valid_from,
        valid_to = source.valid_to,
        is_current = source.is_current,
        opening_event_id = source.opening_event_id,
        dimension_row_hash = source.dimension_row_hash,
        opening_source_ts = source.opening_source_ts,
        opening_kafka_topic = source.opening_kafka_topic,
        opening_kafka_partition = source.opening_kafka_partition,
        opening_kafka_offset = source.opening_kafka_offset
      WHEN NOT MATCHED AND source.operation_type != 'DELETE' THEN INSERT ROW;

      MERGE `{{ project_id }}.olist_gold_store.dim_product_scd2__current` AS target
      USING (
        SELECT *
        FROM `{{ project_id }}.olist_gold_store.dim_product_scd2__history`
        WHERE sync_run_seq = p_sync_run_seq
      ) AS source
      ON target.product_key = source.product_key
      WHEN MATCHED AND source.operation_type = 'DELETE' THEN DELETE
      WHEN MATCHED THEN UPDATE SET
        sync_run_seq = source.sync_run_seq,
        sync_run_id = source.sync_run_id,
        operation_type = source.operation_type,
        build_mode = source.build_mode,
        previous_boundary_id = source.previous_boundary_id,
        current_boundary_id = source.current_boundary_id,
        built_at = source.built_at,
        product_key = source.product_key,
        product_id = source.product_id,
        product_category_name = source.product_category_name,
        product_category_name_english = source.product_category_name_english,
        product_name_lenght = source.product_name_lenght,
        product_description_lenght = source.product_description_lenght,
        product_photos_qty = source.product_photos_qty,
        product_weight_g = source.product_weight_g,
        product_length_cm = source.product_length_cm,
        product_height_cm = source.product_height_cm,
        product_width_cm = source.product_width_cm,
        valid_from = source.valid_from,
        valid_to = source.valid_to,
        is_current = source.is_current,
        opening_event_id = source.opening_event_id,
        dimension_row_hash = source.dimension_row_hash,
        opening_source_ts = source.opening_source_ts,
        opening_kafka_topic = source.opening_kafka_topic,
        opening_kafka_partition = source.opening_kafka_partition,
        opening_kafka_offset = source.opening_kafka_offset
      WHEN NOT MATCHED AND source.operation_type != 'DELETE' THEN INSERT ROW;

      MERGE `{{ project_id }}.olist_gold_store.fact_order_items__current` AS target
      USING (
        SELECT *
        FROM `{{ project_id }}.olist_gold_store.fact_order_items__history`
        WHERE sync_run_seq = p_sync_run_seq
      ) AS source
      ON target.order_id = source.order_id
         AND target.order_item_id = source.order_item_id
      WHEN MATCHED AND source.operation_type = 'DELETE' THEN DELETE
      WHEN MATCHED THEN UPDATE SET
        sync_run_seq = source.sync_run_seq,
        sync_run_id = source.sync_run_id,
        operation_type = source.operation_type,
        build_mode = source.build_mode,
        previous_boundary_id = source.previous_boundary_id,
        current_boundary_id = source.current_boundary_id,
        built_at = source.built_at,
        order_item_key = source.order_item_key,
        order_id = source.order_id,
        order_item_id = source.order_item_id,
        customer_key = source.customer_key,
        product_key = source.product_key,
        seller_key = source.seller_key,
        order_status_key = source.order_status_key,
        order_purchase_date_key = source.order_purchase_date_key,
        order_approved_date_key = source.order_approved_date_key,
        order_delivered_customer_date_key = source.order_delivered_customer_date_key,
        order_estimated_delivery_date_key = source.order_estimated_delivery_date_key,
        customer_id = source.customer_id,
        customer_unique_id = source.customer_unique_id,
        product_id = source.product_id,
        seller_id = source.seller_id,
        order_status = source.order_status,
        order_purchase_timestamp = source.order_purchase_timestamp,
        order_approved_at = source.order_approved_at,
        order_delivered_carrier_date = source.order_delivered_carrier_date,
        order_delivered_customer_date = source.order_delivered_customer_date,
        order_estimated_delivery_date = source.order_estimated_delivery_date,
        shipping_limit_date = source.shipping_limit_date,
        price = source.price,
        freight_value = source.freight_value,
        gross_item_amount = source.gross_item_amount,
        allocated_payment_value = source.allocated_payment_value,
        delivery_days = source.delivery_days,
        delivery_delay_days = source.delivery_delay_days,
        is_delivered_late = source.is_delivered_late
      WHEN NOT MATCHED AND source.operation_type != 'DELETE' THEN INSERT ROW;

      DELETE FROM `{{ project_id }}.olist_gold_store.mart_daily_revenue__current`
      WHERE order_purchase_date IN (
        SELECT order_purchase_date
        FROM `{{ project_id }}.olist_gold_store.mart_daily_revenue__history`
        WHERE sync_run_seq = p_sync_run_seq
      );
      INSERT INTO `{{ project_id }}.olist_gold_store.mart_daily_revenue__current`
      SELECT *
      FROM `{{ project_id }}.olist_gold_store.mart_daily_revenue__history`
      WHERE sync_run_seq = p_sync_run_seq;

      DELETE FROM `{{ project_id }}.olist_gold_store.mart_monthly_arpu__current`
      WHERE order_month IN (
        SELECT order_month
        FROM `{{ project_id }}.olist_gold_store.mart_monthly_arpu__history`
        WHERE sync_run_seq = p_sync_run_seq
      );
      INSERT INTO `{{ project_id }}.olist_gold_store.mart_monthly_arpu__current`
      SELECT *
      FROM `{{ project_id }}.olist_gold_store.mart_monthly_arpu__history`
      WHERE sync_run_seq = p_sync_run_seq;

      UPDATE `{{ project_id }}.olist_serving_control.control_state`
      SET active_sync_run_seq = p_sync_run_seq,
          row_version = row_version + 1,
          updated_at = CURRENT_TIMESTAMP()
      WHERE state_key = 'gcp'
        AND target = 'gcp'
        AND active_sync_run_seq = p_expected_active_sync_run_seq;
      SET control_updated_count = @@row_count;
      UPDATE `{{ project_id }}.olist_serving_control.publication_state`
      SET active_sync_run_seq = p_sync_run_seq,
          updated_at = CURRENT_TIMESTAMP()
      WHERE state_key = 'gcp' AND target = 'gcp';
      SET publication_updated_count = @@row_count;
      IF control_updated_count != 1 OR publication_updated_count != 1 THEN
        ROLLBACK TRANSACTION;
        UPDATE `{{ project_id }}.olist_serving_control.serving_runs`
        SET status = 'FAILED_TERMINAL',
            status_reason = 'PUBLICATION_DRIFT',
            error_code = 'STALE_PREDECESSOR',
            error_message = 'active predecessor compare-and-set failed',
            conflicted_at = CURRENT_TIMESTAMP(),
            failed_at = CURRENT_TIMESTAMP(),
            completed_at = CURRENT_TIMESTAMP(),
            updated_at = CURRENT_TIMESTAMP()
        WHERE target = 'gcp'
          AND sync_run_seq = p_sync_run_seq
          AND status != 'SUCCEEDED';
        SELECT 'CONFLICTED' AS publication_result, p_sync_run_seq AS sync_run_seq;
      ELSE
        UPDATE `{{ project_id }}.olist_serving_control.serving_runs`
        SET status = 'SUCCEEDED',
            status_reason = 'NONE',
            published_at = CURRENT_TIMESTAMP(),
            completed_at = CURRENT_TIMESTAMP(),
            updated_at = CURRENT_TIMESTAMP()
        WHERE target = 'gcp' AND sync_run_seq = p_sync_run_seq;
        COMMIT TRANSACTION;
        SELECT 'PUBLISHED' AS publication_result, p_sync_run_seq AS sync_run_seq;
      END IF;
    END IF;
  END IF;
END;
