package com.olist.mds.spark.schema

import com.olist.mds.spark.silver.IcebergCommitCoordinator
import org.apache.spark.sql.DataFrame
import org.apache.spark.sql.Row
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import java.sql.Timestamp
import java.time.Instant

object SchemaArchiveWriter {
  val SchemaTable = "lakehouse.bronze.avro_schemas"

  def writeBatch(spark: SparkSession, batchDf: DataFrame, batchId: Long): Unit = {
    val schemaTopicRows = batchDf.filter(col("topic").isin("olist_cdc.__schemas__", "__schemas__"))
    if (schemaTopicRows.isEmpty) return

    val rows = schemaTopicRows.collect()
    if (rows.isEmpty) return

    val archiveRows = scala.collection.mutable.ArrayBuffer[Row]()
    val now = Timestamp.from(Instant.now())

    rows.foreach { row =>
      val keyBytes = row.getAs[Array[Byte]]("key_bytes")
      val valBytes = row.getAs[Array[Byte]]("value_bytes")
      val topic = row.getAs[String]("topic")

      if (valBytes != null && valBytes.nonEmpty) {
        val valStr = new String(valBytes, "UTF-8")
        // Basic parsing of schema definition payload if structured, or extract fingerprint
        val fingerprint = com.olist.mds.spark.avro.ConfluentFrame.sha256Hex(valBytes)
        archiveRows += Row(topic, 0, fingerprint, valStr, now)
      }
    }

    if (archiveRows.isEmpty) return

    val sparkSchema = StructType(
      Seq(
        StructField("topic", StringType, nullable = false),
        StructField("schema_id", IntegerType, nullable = false),
        StructField("fingerprint_sha256", StringType, nullable = false),
        StructField("schema_json", StringType, nullable = false),
        StructField("captured_at", TimestampType, nullable = false)
      )
    )

    val df = spark.createDataFrame(spark.sparkContext.parallelize(archiveRows.toSeq), sparkSchema)
    df.createOrReplaceTempView("inc_schemas")

    val mergeSql =
      s"""
         |MERGE INTO $SchemaTable AS target
         |USING inc_schemas AS inc
         |ON target.topic = inc.topic AND target.fingerprint_sha256 = inc.fingerprint_sha256
         |WHEN NOT MATCHED THEN INSERT (
         |  topic, schema_id, fingerprint_sha256, schema_json, captured_at
         |) VALUES (
         |  inc.topic, inc.schema_id, inc.fingerprint_sha256, inc.schema_json, inc.captured_at
         |)
         |""".stripMargin

    IcebergCommitCoordinator.withLock(SchemaTable) {
      spark.sql(mergeSql)
    }
  }
}
