package com.olist.mds.spark.transaction

import com.olist.mds.spark.silver.IcebergCommitCoordinator
import com.olist.mds.spark.silver.SilverProgressRecord
import com.olist.mds.spark.silver.SilverProgressWriter
import org.apache.spark.sql.DataFrame
import org.apache.spark.sql.Row
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import java.sql.Timestamp
import java.time.Instant

object TransactionBatchWriter {
  val TxTable = "lakehouse.audit.mysql_transactions"

  def writeBatch(spark: SparkSession, batchDf: DataFrame, batchId: Long): Unit = {
    val txRows = batchDf.filter(col("topic").isin("olist_cdc.transaction", "transaction"))
    if (txRows.isEmpty) return

    val rows = txRows.collect()
    if (rows.isEmpty) return

    val now = Timestamp.from(Instant.now())
    val progressRecords = scala.collection.mutable.ArrayBuffer[SilverProgressRecord]()

    rows.foreach { row =>
      val eventId = row.getAs[String]("event_id")
      val kafkaOffset = row.getAs[Long]("offset")
      val partition = row.getAs[Int]("partition")
      val topic = row.getAs[String]("topic")
      val kTs = row.getAs[Timestamp]("kafka_timestamp")

      // Extract transaction metadata fields from row/payload
      val keyBytes = row.getAs[Array[Byte]]("key_bytes")
      val valBytes = row.getAs[Array[Byte]]("value_bytes")

      val txId = if (eventId != null && eventId.nonEmpty) eventId else s"tx_$kafkaOffset"
      val status = "COMPLETE" // Simplified transition for valid batch range

      val txSql =
        s"""
           |MERGE INTO $TxTable AS target
           |USING (SELECT '$txId' AS transaction_id, '$status' AS status, $kafkaOffset AS end_kafka_offset, CAST('$now' AS TIMESTAMP) AS updated_at) AS inc
           |ON target.transaction_id = inc.transaction_id
           |WHEN MATCHED THEN UPDATE SET target.status = inc.status, target.end_kafka_offset = inc.end_kafka_offset, target.updated_at = inc.updated_at
           |WHEN NOT MATCHED THEN INSERT (transaction_id, status, end_kafka_offset, updated_at)
           |VALUES (inc.transaction_id, inc.status, inc.end_kafka_offset, inc.updated_at)
           |""".stripMargin

      IcebergCommitCoordinator.withLock(TxTable) {
        spark.sql(txSql)
      }

      progressRecords += SilverProgressRecord(
        queryName = "normalize_mysql_transactions",
        entity = "__transactions__",
        contractVersion = 2,
        sourceTopic = topic,
        kafkaPartition = partition,
        sparkBatchId = batchId,
        changesSnapshotId = SilverProgressWriter.getLatestSnapshotId(spark, TxTable),
        currentSnapshotId = None,
        firstKafkaOffset = kafkaOffset,
        lastKafkaOffset = kafkaOffset,
        recordsProcessed = 1L,
        appliedRecords = 1L,
        rejectedRecords = 0L,
        status = "COMMITTED"
      )
    }

    if (progressRecords.nonEmpty) {
      SilverProgressWriter.writeProgress(spark, progressRecords.toSeq)
    }
  }
}
