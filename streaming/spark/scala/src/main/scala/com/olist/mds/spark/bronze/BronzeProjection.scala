package com.olist.mds.spark.bronze

import com.olist.mds.spark.avro.ConfluentFrame
import org.apache.spark.sql.DataFrame
import org.apache.spark.sql.functions._
import java.time.Instant

object BronzeProjection {

  private val inspectKeyUdf = udf((bytes: Array[Byte]) => {
    val insp = ConfluentFrame.inspect(bytes, isKey = true)
    (insp.framingValid, insp.schemaId.map(Integer.valueOf).orNull, insp.errorCode.orNull)
  })

  private val inspectValueUdf = udf((bytes: Array[Byte]) => {
    val insp = ConfluentFrame.inspect(bytes, isKey = false)
    (insp.framingValid, insp.schemaId.map(Integer.valueOf).orNull, insp.errorCode.orNull)
  })

  def project(
      df: DataFrame,
      batchId: Long,
      sparkQueryId: String,
      ingestedAt: Instant
  ): DataFrame = {
    val ingestedAtTs = java.sql.Timestamp.from(ingestedAt)

    df
      .withColumn("key_bytes", col("key"))
      .withColumn("value_bytes", col("value"))
      .withColumn("kafka_timestamp", col("timestamp"))
      .withColumn("kafka_timestamp_type", col("timestampType"))
      .withColumn(
        "event_id",
        concat(col("topic"), lit(":"), col("partition"), lit(":"), col("offset"))
      )
      .withColumn(
        "record_kind",
        when(col("topic") === "olist_cdc.transaction", lit("transaction"))
          .when(col("topic") === "olist_cdc.heartbeat", lit("heartbeat"))
          .when(col("topic") === "olist_cdc", lit("schema_change"))
          .when(col("value").isNull, lit("tombstone"))
          .otherwise(lit("data"))
      )
      .withColumn(
        "is_tombstone",
        col("topic").startsWith("olist_cdc.olist_oltp.") && col("value").isNull
      )
      .withColumn(
        "key_sha256",
        when(col("key_bytes").isNotNull, lower(sha2(col("key_bytes"), 256))).otherwise(null)
      )
      .withColumn(
        "value_sha256",
        when(col("value_bytes").isNotNull, lower(sha2(col("value_bytes"), 256))).otherwise(null)
      )
      .withColumn("key_inspection", inspectKeyUdf(col("key_bytes")))
      .withColumn("value_inspection", inspectValueUdf(col("value_bytes")))
      .withColumn("key_framing_valid", col("key_inspection._1"))
      .withColumn("key_schema_id", col("key_inspection._2"))
      .withColumn("key_error_code", col("key_inspection._3"))
      .withColumn("value_framing_valid", col("value_inspection._1"))
      .withColumn("value_schema_id", col("value_inspection._2"))
      .withColumn("value_error_code", col("value_inspection._3"))
      .withColumn("framing_error", coalesce(col("key_error_code"), col("value_error_code")))
      .withColumn("ingest_batch_id", lit(batchId))
      .withColumn("spark_query_id", lit(sparkQueryId))
      .withColumn("ingested_at", lit(ingestedAtTs))
      .select(
        col("event_id"),
        col("record_kind"),
        col("topic"),
        col("partition"),
        col("offset"),
        col("kafka_timestamp"),
        col("kafka_timestamp_type"),
        col("headers"),
        col("key_bytes"),
        col("value_bytes"),
        col("is_tombstone"),
        col("key_schema_id"),
        col("value_schema_id"),
        col("key_sha256"),
        col("value_sha256"),
        col("key_framing_valid"),
        col("value_framing_valid"),
        col("framing_error"),
        col("ingest_batch_id"),
        col("spark_query_id"),
        col("ingested_at")
      )
  }
}
