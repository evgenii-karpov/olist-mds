package com.olist.mds.spark.silver

import com.olist.mds.spark.contract.EntityContract
import com.olist.mds.spark.normalize.FatalContractFailure
import com.olist.mds.spark.normalize.SparkJobException
import org.apache.spark.sql.DataFrame
import org.apache.spark.sql.Row
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

object SilverBatchWriter {

  def writeBatch(
      spark: SparkSession,
      bronzeDf: DataFrame,
      contract: EntityContract,
      batchId: Long
  ): Unit = {
    val topicRows = bronzeDf.filter(col("topic") === contract.topic)
    if (topicRows.isEmpty) return

    val keyFps = contract.allowedKeyFingerprints
    val valFps = contract.allowedValueFingerprints

    val invalidRows = topicRows.filter(
      col("key_framing_valid") === false ||
        col("value_framing_valid") === false ||
        !lower(col("key_sha256")).isin(keyFps.toSeq: _*) ||
        !lower(col("value_sha256")).isin(valFps.toSeq: _*)
    )

    if (!invalidRows.isEmpty) {
      throw SparkJobException(
        "unknown_schema_id",
        s"Unapproved writer schema or invalid framing in bronze batch $batchId for ${contract.entity}",
        FatalContractFailure
      )
    }

    val rows = topicRows.collect()
    val decodedRows = rows.map { row =>
      val eventId = row.getAs[String]("event_id")
      val keyBytes = row.getAs[Array[Byte]]("key_bytes")
      val valBytes = row.getAs[Array[Byte]]("value_bytes")
      val kafkaTs = row.getAs[java.sql.Timestamp]("kafka_timestamp")
      val kafkaOffset = row.getAs[Long]("offset")

      val decoded = SilverDecoder.decodeRow(eventId, keyBytes, valBytes, contract)
      (decoded, kafkaTs, kafkaOffset)
    }

    val changesTable = s"lakehouse.silver.${contract.entity}_changes"
    val currentTable = s"lakehouse.silver.${contract.entity}_current"

    // Convert decoded rows to DataFrame matching changesTable schema
    val schemaCols = contract.businessColumns.map(_.name)
    val pkCols = contract.primaryKey

    // Build changes DF
    val sparkSchema = contract.toChangesSparkSchema
    val rddRows = spark.sparkContext.parallelize(decodedRows.toVector.map { case (dec, kTs, _) =>
      val values = Vector(
        dec.eventId,
        dec.opType,
        dec.sourceTsMs.map(java.lang.Long.valueOf).orNull,
        kTs
      ) ++ contract.businessColumns.map(c => dec.businessValues.getOrElse(c.name, null))
      Row.fromSeq(values)
    })

    val changesDf = spark.createDataFrame(rddRows, sparkSchema)

    // 1. Append changes to silver.<entity>_changes
    changesDf.writeTo(changesTable).append()

    // 2. Compute latest state per primary key in this micro-batch
    val pkJoinExpr = pkCols.map(pk => s"target.$pk = inc.$pk").mkString(" AND ")

    // Partition by PK, order by kafka_timestamp desc, offset desc
    val windowSpec = org.apache.spark.sql.expressions.Window
      .partitionBy(pkCols.map(col): _*)
      .orderBy(col("kafka_timestamp").desc, col("event_id").desc)

    val latestIncDf = changesDf
      .withColumn("rn", row_number().over(windowSpec))
      .filter(col("rn") === 1)
      .drop("rn")

    latestIncDf.createOrReplaceTempView("inc_batch")

    // MERGE INTO lakehouse.silver.<entity>_current
    val businessUpdateSet = contract.businessColumns
      .map(c => s"target.${c.name} = inc.${c.name}")
      .mkString(", ")
    val businessInsertCols = (Vector("op_type", "kafka_timestamp") ++ schemaCols).mkString(", ")
    val businessInsertVals =
      (Vector("inc.op_type", "inc.kafka_timestamp") ++ schemaCols.map(c => s"inc.$c"))
        .mkString(", ")

    val mergeSql =
      s"""
         |MERGE INTO $currentTable AS target
         |USING inc_batch AS inc
         |ON $pkJoinExpr
         |WHEN MATCHED AND inc.op_type = 'delete' THEN DELETE
         |WHEN MATCHED AND inc.op_type != 'delete' THEN UPDATE SET $businessUpdateSet, target.op_type = inc.op_type, target.kafka_timestamp = inc.kafka_timestamp
         |WHEN NOT MATCHED AND inc.op_type != 'delete' THEN INSERT ($businessInsertCols) VALUES ($businessInsertVals)
         |""".stripMargin

    spark.sql(mergeSql)
  }
}
