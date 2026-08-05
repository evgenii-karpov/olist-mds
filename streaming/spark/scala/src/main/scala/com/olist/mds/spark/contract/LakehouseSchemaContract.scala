package com.olist.mds.spark.contract

import com.fasterxml.jackson.databind.ObjectMapper
import com.olist.mds.spark.normalize.FatalContractFailure
import com.olist.mds.spark.normalize.SparkJobException
import org.apache.spark.sql.types._
import java.nio.charset.StandardCharsets
import java.security.MessageDigest

final case class IcebergColumnSpec(
    name: String,
    sqlType: String,
    required: Boolean
) {
  def sparkDataType: DataType = sqlType match {
    case "STRING" => StringType
    case "INT" => IntegerType
    case "BIGINT" => LongType
    case "BOOLEAN" => BooleanType
    case "TIMESTAMP_NTZ" => TimestampNTZType
    case "TIMESTAMP_LTZ" => TimestampType
    case "BINARY" => BinaryType
    case s if s.startsWith("DECIMAL(") && s.endsWith(")") =>
      val parts = s.substring(8, s.length - 1).split(",").map(_.trim.toInt)
      DecimalType(parts(0), parts(1))
    case "ARRAY<STRING>" => ArrayType(StringType, containsNull = true)
    case "ARRAY<STRUCT<key: STRING, value: BINARY>>" =>
      ArrayType(
        StructType(
          Seq(
            StructField("key", StringType, nullable = true),
            StructField("value", BinaryType, nullable = true)
          )
        ),
        containsNull = true
      )
    case "ARRAY<STRUCT<data_collection: STRING, event_count: BIGINT>>" =>
      ArrayType(
        StructType(
          Seq(
            StructField("data_collection", StringType, nullable = true),
            StructField("event_count", LongType, nullable = true)
          )
        ),
        containsNull = true
      )
    case other => throw new IllegalArgumentException(s"Unknown type: $other")
  }

  def toStructField: StructField = StructField(name, sparkDataType, nullable = !required)
}

final case class IcebergTableSpec(
    namespace: String,
    name: String,
    columns: Vector[IcebergColumnSpec],
    partitionTransform: Option[String] = None,
    properties: Map[String, String] = Map(
      "format-version" -> "2",
      "write.format.default" -> "parquet",
      "write.parquet.compression-codec" -> "zstd",
      "write.target-file-size-bytes" -> "134217728",
      "write.metadata.delete-after-commit.enabled" -> "true",
      "write.metadata.previous-versions-max" -> "20"
    )
) {
  def qualifiedName(catalogAlias: String = "lakehouse"): String = s"$catalogAlias.$namespace.$name"
  def schema: StructType = StructType(columns.map(_.toStructField))
}

object LakehouseSchemaContract {
  val CatalogAlias = "lakehouse"
  val ExpectedChecksum = "d3bf55d90fbfe953cfbc74eef83e6d83f91ce1986cfb85c849da2c3e788b3d8d"
  val Namespaces: Vector[String] = Vector("bronze", "silver", "reference", "audit")

  private def col(name: String, sqlType: String, required: Boolean = false): IcebergColumnSpec =
    IcebergColumnSpec(name, sqlType, required)

  val BusinessSchemas: Map[String, Vector[IcebergColumnSpec]] = Map(
    "customers" -> Vector(
      col("customer_id", "STRING", required = true),
      col("customer_unique_id", "STRING", required = true),
      col("customer_zip_code_prefix", "STRING", required = true),
      col("customer_city", "STRING", required = true),
      col("customer_state", "STRING", required = true)
    ),
    "orders" -> Vector(
      col("order_id", "STRING", required = true),
      col("customer_id", "STRING", required = true),
      col("order_status", "STRING", required = true),
      col("order_purchase_timestamp", "TIMESTAMP_NTZ", required = true),
      col("order_approved_at", "TIMESTAMP_NTZ", required = false),
      col("order_delivered_carrier_date", "TIMESTAMP_NTZ", required = false),
      col("order_delivered_customer_date", "TIMESTAMP_NTZ", required = false),
      col("order_estimated_delivery_date", "TIMESTAMP_NTZ", required = true)
    ),
    "order_items" -> Vector(
      col("order_id", "STRING", required = true),
      col("order_item_id", "INT", required = true),
      col("product_id", "STRING", required = true),
      col("seller_id", "STRING", required = true),
      col("shipping_limit_date", "TIMESTAMP_NTZ", required = true),
      col("price", "DECIMAL(18,2)", required = true),
      col("freight_value", "DECIMAL(18,2)", required = true)
    ),
    "order_payments" -> Vector(
      col("order_id", "STRING", required = true),
      col("payment_sequential", "INT", required = true),
      col("payment_type", "STRING", required = true),
      col("payment_installments", "INT", required = true),
      col("payment_value", "DECIMAL(18,2)", required = true)
    ),
    "order_reviews" -> Vector(
      col("review_id", "STRING", required = true),
      col("order_id", "STRING", required = true),
      col("review_score", "INT", required = true),
      col("review_comment_title", "STRING", required = false),
      col("review_comment_message", "STRING", required = false),
      col("review_creation_date", "TIMESTAMP_NTZ", required = true),
      col("review_answer_timestamp", "TIMESTAMP_NTZ", required = true)
    ),
    "products" -> Vector(
      col("product_id", "STRING", required = true),
      col("product_category_name", "STRING", required = false),
      col("product_name_lenght", "INT", required = false),
      col("product_description_lenght", "INT", required = false),
      col("product_photos_qty", "INT", required = false),
      col("product_weight_g", "INT", required = false),
      col("product_length_cm", "INT", required = false),
      col("product_height_cm", "INT", required = false),
      col("product_width_cm", "INT", required = false)
    ),
    "sellers" -> Vector(
      col("seller_id", "STRING", required = true),
      col("seller_zip_code_prefix", "STRING", required = true),
      col("seller_city", "STRING", required = true),
      col("seller_state", "STRING", required = true)
    ),
    "product_category_translation" -> Vector(
      col("product_category_name", "STRING", required = true),
      col("product_category_name_english", "STRING", required = true)
    )
  )

  val BronzeTables: Vector[IcebergTableSpec] = Vector(
    IcebergTableSpec(
      namespace = "bronze",
      name = "mysql_cdc_records",
      columns = Vector(
        col("event_id", "STRING", required = true),
        col("record_kind", "STRING", required = true),
        col("topic", "STRING", required = true),
        col("partition", "INT", required = true),
        col("offset", "BIGINT", required = true),
        col("kafka_timestamp", "TIMESTAMP_LTZ", required = true),
        col("kafka_timestamp_type", "INT", required = true),
        col("headers", "ARRAY<STRUCT<key: STRING, value: BINARY>>", required = false),
        col("key_bytes", "BINARY", required = false),
        col("value_bytes", "BINARY", required = false),
        col("is_tombstone", "BOOLEAN", required = true),
        col("key_schema_id", "INT", required = false),
        col("value_schema_id", "INT", required = false),
        col("key_sha256", "STRING", required = false),
        col("value_sha256", "STRING", required = false),
        col("key_framing_valid", "BOOLEAN", required = true),
        col("value_framing_valid", "BOOLEAN", required = true),
        col("framing_error", "STRING", required = false),
        col("ingest_batch_id", "BIGINT", required = true),
        col("spark_query_id", "STRING", required = true),
        col("ingested_at", "TIMESTAMP_LTZ", required = true)
      ),
      partitionTransform = Some("days(ingested_at)")
    ),
    IcebergTableSpec(
      namespace = "bronze",
      name = "avro_schemas",
      columns = Vector(
        col("schema_id", "INT", required = true),
        col("fingerprint_sha256", "STRING", required = true),
        col("subject", "STRING", required = true),
        col("registry_version", "INT", required = true),
        col("schema_json", "STRING", required = true),
        col("references_json", "STRING", required = true),
        col("spark_self_contained_schema_json", "STRING", required = true),
        col("first_seen_at", "TIMESTAMP_LTZ", required = true),
        col("last_verified_at", "TIMESTAMP_LTZ", required = true)
      )
    )
  )

  private val ChangesPrefix = Vector(
    col("event_id", "STRING", required = true),
    col("op", "STRING", required = true),
    col("is_snapshot", "BOOLEAN", required = true),
    col("is_deleted", "BOOLEAN", required = true),
    col("apply_status", "STRING", required = true),
    col("error_code", "STRING", required = false),
    col("error_message", "STRING", required = false)
  )

  private val ChangesSuffix = Vector(
    col("source_ts", "TIMESTAMP_LTZ", required = true),
    col("source_server_id", "BIGINT", required = false),
    col("source_gtid", "STRING", required = false),
    col("source_binlog_file", "STRING", required = false),
    col("source_binlog_file_index", "INT", required = false),
    col("source_binlog_pos", "BIGINT", required = false),
    col("source_row", "INT", required = false),
    col("transaction_id", "STRING", required = false),
    col("transaction_total_order", "BIGINT", required = false),
    col("transaction_data_collection_order", "BIGINT", required = false),
    col("kafka_topic", "STRING", required = true),
    col("kafka_partition", "INT", required = true),
    col("kafka_offset", "BIGINT", required = true),
    col("kafka_timestamp", "TIMESTAMP_LTZ", required = true),
    col("key_schema_id", "INT", required = false),
    col("value_schema_id", "INT", required = false),
    col("schema_fingerprint", "STRING", required = false),
    col("contract_version", "INT", required = true),
    col("before_row_hash", "STRING", required = false),
    col("after_row_hash", "STRING", required = false),
    col("row_hash", "STRING", required = false),
    col("bronze_ingested_at", "TIMESTAMP_LTZ", required = true),
    col("normalized_at", "TIMESTAMP_LTZ", required = true)
  )

  private val CurrentSuffix = Vector(
    col("is_deleted", "BOOLEAN", required = true),
    col("deleted_at", "TIMESTAMP_LTZ", required = false),
    col("last_event_id", "STRING", required = true),
    col("last_source_ts", "TIMESTAMP_LTZ", required = true),
    col("last_transaction_id", "STRING", required = false),
    col("last_kafka_partition", "INT", required = true),
    col("last_kafka_offset", "BIGINT", required = true),
    col("last_row_hash", "STRING", required = true),
    col("contract_version", "INT", required = true),
    col("updated_at", "TIMESTAMP_LTZ", required = true)
  )

  val SilverTables: Vector[IcebergTableSpec] = Vector(
    "customers",
    "orders",
    "order_items",
    "order_payments",
    "order_reviews",
    "products",
    "sellers",
    "product_category_translation"
  ).flatMap { entity =>
    val bCols = BusinessSchemas(entity)
    Vector(
      IcebergTableSpec(
        namespace = "silver",
        name = s"${entity}_changes",
        columns = ChangesPrefix ++ bCols.map(_.copy(required = false)) ++ ChangesSuffix,
        partitionTransform = Some("days(source_ts)")
      ),
      IcebergTableSpec(
        namespace = "silver",
        name = s"${entity}_current",
        columns = bCols ++ CurrentSuffix
      )
    )
  }

  val ReferenceTables: Vector[IcebergTableSpec] = Vector(
    IcebergTableSpec(
      namespace = "reference",
      name = "geolocation",
      columns = Vector(
        col("geolocation_id", "BIGINT", required = true),
        col("geolocation_zip_code_prefix", "STRING", required = true),
        col("geolocation_lat", "DECIMAL(18,14)", required = true),
        col("geolocation_lng", "DECIMAL(18,14)", required = true),
        col("geolocation_city", "STRING", required = true),
        col("geolocation_state", "STRING", required = true),
        col("source_archive_sha256", "STRING", required = true),
        col("source_row_number", "BIGINT", required = true),
        col("loaded_at", "TIMESTAMP_LTZ", required = true)
      )
    )
  )

  val AuditTables: Vector[IcebergTableSpec] = Vector(
    IcebergTableSpec(
      namespace = "audit",
      name = "mysql_transactions",
      columns = Vector(
        col("transaction_id", "STRING", required = true),
        col("status", "STRING", required = true),
        col("event_count", "BIGINT", required = false),
        col(
          "data_collections",
          "ARRAY<STRUCT<data_collection: STRING, event_count: BIGINT>>",
          required = false
        ),
        col("begin_event_id", "STRING", required = false),
        col("end_event_id", "STRING", required = false),
        col("kafka_topic", "STRING", required = true),
        col("kafka_partition", "INT", required = true),
        col("begin_kafka_offset", "BIGINT", required = false),
        col("end_kafka_offset", "BIGINT", required = false),
        col("source_ts", "TIMESTAMP_LTZ", required = false),
        col("first_seen_at", "TIMESTAMP_LTZ", required = true),
        col("completed_at", "TIMESTAMP_LTZ", required = false),
        col("rejected_event_ids", "ARRAY<STRING>", required = false),
        col("recorded_at", "TIMESTAMP_LTZ", required = true)
      ),
      partitionTransform = Some("days(recorded_at)")
    ),
    IcebergTableSpec(
      namespace = "audit",
      name = "silver_progress",
      columns = Vector(
        col("query_name", "STRING", required = true),
        col("entity", "STRING", required = true),
        col("contract_version", "INT", required = true),
        col("source_topic", "STRING", required = true),
        col("kafka_partition", "INT", required = true),
        col("last_kafka_offset", "BIGINT", required = true),
        col("last_event_id", "STRING", required = true),
        col("last_source_ts", "TIMESTAMP_LTZ", required = false),
        col("spark_query_id", "STRING", required = true),
        col("spark_batch_id", "BIGINT", required = true),
        col("changes_snapshot_id", "BIGINT", required = true),
        col("current_snapshot_id", "BIGINT", required = false),
        col("status", "STRING", required = true),
        col("error_class", "STRING", required = false),
        col("updated_at", "TIMESTAMP_LTZ", required = true),
        col("recorded_at", "TIMESTAMP_LTZ", required = true)
      ),
      partitionTransform = Some("days(recorded_at)")
    ),
    IcebergTableSpec(
      namespace = "audit",
      name = "normalization_errors",
      columns = Vector(
        col("error_id", "STRING", required = true),
        col("event_id", "STRING", required = true),
        col("entity", "STRING", required = true),
        col("error_code", "STRING", required = true),
        col("error_message", "STRING", required = true),
        col("kafka_topic", "STRING", required = true),
        col("kafka_partition", "INT", required = true),
        col("kafka_offset", "BIGINT", required = true),
        col("key_schema_id", "INT", required = false),
        col("value_schema_id", "INT", required = false),
        col("schema_fingerprint", "STRING", required = false),
        col("contract_version", "INT", required = true),
        col("first_seen_at", "TIMESTAMP_LTZ", required = true),
        col("last_seen_at", "TIMESTAMP_LTZ", required = true),
        col("occurrence_count", "BIGINT", required = true),
        col("resolved_at", "TIMESTAMP_LTZ", required = false),
        col("recorded_at", "TIMESTAMP_LTZ", required = true)
      ),
      partitionTransform = Some("days(recorded_at)")
    ),
    IcebergTableSpec(
      namespace = "audit",
      name = "schema_violations",
      columns = Vector(
        col("violation_id", "STRING", required = true),
        col("entity", "STRING", required = true),
        col("event_id", "STRING", required = false),
        col("schema_kind", "STRING", required = true),
        col("schema_id", "INT", required = false),
        col("fingerprint_sha256", "STRING", required = false),
        col("contract_version", "INT", required = true),
        col("violation_code", "STRING", required = true),
        col("error_message", "STRING", required = true),
        col("compatibility_result", "STRING", required = false),
        col("details_json", "STRING", required = false),
        col("recorded_at", "TIMESTAMP_LTZ", required = true)
      ),
      partitionTransform = Some("days(recorded_at)")
    ),
    IcebergTableSpec(
      namespace = "audit",
      name = "maintenance_runs",
      columns = Vector(
        col("maintenance_run_id", "STRING", required = true),
        col("procedure", "STRING", required = true),
        col("table_namespace", "STRING", required = true),
        col("table_name", "STRING", required = true),
        col("status", "STRING", required = true),
        col("started_at", "TIMESTAMP_LTZ", required = true),
        col("finished_at", "TIMESTAMP_LTZ", required = false),
        col("options_json", "STRING", required = true),
        col("result_json", "STRING", required = false),
        col("error_code", "STRING", required = false),
        col("error_message", "STRING", required = false),
        col("recorded_at", "TIMESTAMP_LTZ", required = true)
      ),
      partitionTransform = Some("days(recorded_at)")
    ),
    IcebergTableSpec(
      namespace = "audit",
      name = "serving_sync_reports",
      columns = Vector(
        col("sync_run_id", "STRING", required = true),
        col("sync_run_seq", "BIGINT", required = true),
        col("status", "STRING", required = true),
        col("is_noop", "BOOLEAN", required = true),
        col("previous_transaction_id", "STRING", required = false),
        col("target_transaction_id", "STRING", required = false),
        col("target_offsets_json", "STRING", required = true),
        col("expected_event_count", "BIGINT", required = true),
        col("materialized_event_count", "BIGINT", required = true),
        col("entity_counts_json", "STRING", required = true),
        col("error_details_json", "STRING", required = false),
        col("started_at", "TIMESTAMP_LTZ", required = true),
        col("finished_at", "TIMESTAMP_LTZ", required = false),
        col("published_at", "TIMESTAMP_LTZ", required = false),
        col("recorded_at", "TIMESTAMP_LTZ", required = true)
      ),
      partitionTransform = Some("days(recorded_at)")
    ),
    IcebergTableSpec(
      namespace = "audit",
      name = "schema_migrations",
      columns = Vector(
        col("migration_version", "INT", required = true),
        col("migration_id", "STRING", required = true),
        col("checksum_sha256", "STRING", required = true),
        col("status", "STRING", required = true),
        col("applied_by", "STRING", required = true),
        col("spark_app_id", "STRING", required = true),
        col("started_at", "TIMESTAMP_LTZ", required = true),
        col("finished_at", "TIMESTAMP_LTZ", required = true),
        col("error_code", "STRING", required = false),
        col("error_message", "STRING", required = false),
        col("recorded_at", "TIMESTAMP_LTZ", required = true)
      ),
      partitionTransform = Some("days(recorded_at)")
    )
  )

  val AllTables: Vector[IcebergTableSpec] =
    BronzeTables ++ SilverTables ++ ReferenceTables ++ AuditTables

  def canonicalJson(): String = {
    val mapper = new ObjectMapper()
    val root = mapper.createObjectNode()
    root.put("catalog_alias", CatalogAlias)
    val namespacesNode = root.putArray("namespaces")
    Namespaces.foreach(namespacesNode.add)

    val tablesNode = root.putArray("tables")
    AllTables.foreach { t =>
      val tObj = mapper.createObjectNode()

      val colsNode = tObj.putArray("columns")
      t.columns.foreach { c =>
        val cObj = mapper.createObjectNode()
        cObj.put("name", c.name)
        cObj.put("required", c.required)
        cObj.put("type", c.sqlType)
        colsNode.add(cObj)
      }

      tObj.put("name", t.name)
      tObj.put("namespace", t.namespace)

      t.partitionTransform match {
        case Some(pt) => tObj.put("partition_transform", pt)
        case None => tObj.putNull("partition_transform")
      }

      val propsObj = tObj.putObject("properties")
      val sortedProps = t.properties.toSeq.sortBy(_._1)
      sortedProps.foreach { case (k, v) => propsObj.put(k, v) }

      tablesNode.add(tObj)
    }

    mapper.writeValueAsString(root)
  }

  def calculateChecksum(): String = {
    val bytes = canonicalJson().getBytes(StandardCharsets.UTF_8)
    val digest = MessageDigest.getInstance("SHA-256")
    digest.digest(bytes).map("%02x".format(_)).mkString
  }

  def validateChecksum(): Unit = {
    val checksum = calculateChecksum()
    if (checksum != ExpectedChecksum) {
      throw SparkJobException(
        "contract_resource_mismatch",
        s"Lakehouse contract checksum drift! Expected $ExpectedChecksum, computed $checksum",
        FatalContractFailure
      )
    }
  }
}
