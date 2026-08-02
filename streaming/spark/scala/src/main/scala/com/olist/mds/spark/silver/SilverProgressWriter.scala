package com.olist.mds.spark.silver

import org.apache.spark.sql.Row
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.types._
import java.sql.Timestamp
import java.time.Instant

final case class SilverProgressRecord(
    queryName: String,
    entity: String,
    contractVersion: Int,
    sourceTopic: String,
    kafkaPartition: Int,
    sparkBatchId: Long,
    changesSnapshotId: Option[Long],
    currentSnapshotId: Option[Long],
    firstKafkaOffset: Long,
    lastKafkaOffset: Long,
    recordsProcessed: Long,
    appliedRecords: Long,
    rejectedRecords: Long,
    status: String
)

object SilverProgressWriter {
  val ProgressTable = "lakehouse.audit.silver_progress"

  val schema = StructType(
    Seq(
      StructField("query_name", StringType, nullable = false),
      StructField("entity", StringType, nullable = false),
      StructField("contract_version", IntegerType, nullable = false),
      StructField("source_topic", StringType, nullable = false),
      StructField("kafka_partition", IntegerType, nullable = false),
      StructField("spark_batch_id", LongType, nullable = false),
      StructField("changes_snapshot_id", LongType, nullable = true),
      StructField("current_snapshot_id", LongType, nullable = true),
      StructField("first_kafka_offset", LongType, nullable = false),
      StructField("last_kafka_offset", LongType, nullable = false),
      StructField("records_processed", LongType, nullable = false),
      StructField("applied_records", LongType, nullable = false),
      StructField("rejected_records", LongType, nullable = false),
      StructField("status", StringType, nullable = false),
      StructField("committed_at", TimestampType, nullable = false)
    )
  )

  def writeProgress(spark: SparkSession, records: Seq[SilverProgressRecord]): Unit = {
    if (records.isEmpty) return

    val now = Timestamp.from(Instant.now())
    val rows = records.map { r =>
      Row(
        r.queryName,
        r.entity,
        r.contractVersion,
        r.sourceTopic,
        r.kafkaPartition,
        r.sparkBatchId,
        r.changesSnapshotId.map(java.lang.Long.valueOf).orNull,
        r.currentSnapshotId.map(java.lang.Long.valueOf).orNull,
        r.firstKafkaOffset,
        r.lastKafkaOffset,
        r.recordsProcessed,
        r.appliedRecords,
        r.rejectedRecords,
        r.status,
        now
      )
    }

    val df = spark.createDataFrame(spark.sparkContext.parallelize(rows), schema)
    df.createOrReplaceTempView("inc_progress")

    val mergeSql =
      s"""
         |MERGE INTO $ProgressTable AS target
         |USING inc_progress AS inc
         |ON target.query_name = inc.query_name
         |   AND target.entity = inc.entity
         |   AND target.contract_version = inc.contract_version
         |   AND target.source_topic = inc.source_topic
         |   AND target.kafka_partition = inc.kafka_partition
         |   AND target.spark_batch_id = inc.spark_batch_id
         |WHEN MATCHED THEN UPDATE SET
         |   changes_snapshot_id = inc.changes_snapshot_id,
         |   current_snapshot_id = inc.current_snapshot_id,
         |   first_kafka_offset = inc.first_kafka_offset,
         |   last_kafka_offset = inc.last_kafka_offset,
         |   records_processed = inc.records_processed,
         |   applied_records = inc.applied_records,
         |   rejected_records = inc.rejected_records,
         |   status = inc.status,
         |   committed_at = inc.committed_at
         |WHEN NOT MATCHED THEN INSERT (
         |   query_name, entity, contract_version, source_topic, kafka_partition, spark_batch_id,
         |   changes_snapshot_id, current_snapshot_id, first_kafka_offset, last_kafka_offset,
         |   records_processed, applied_records, rejected_records, status, committed_at
         |) VALUES (
         |   inc.query_name, inc.entity, inc.contract_version, inc.source_topic, inc.kafka_partition, inc.spark_batch_id,
         |   inc.changes_snapshot_id, inc.current_snapshot_id, inc.first_kafka_offset, inc.last_kafka_offset,
         |   inc.records_processed, inc.applied_records, inc.rejected_records, inc.status, inc.committed_at
         |)
         |""".stripMargin

    IcebergCommitCoordinator.withLock(ProgressTable) {
      spark.sql(mergeSql)
    }
  }

  def getLatestSnapshotId(spark: SparkSession, tableName: String): Option[Long] = {
    try {
      val df = spark.sql(
        s"SELECT snapshot_id FROM $tableName.snapshots ORDER BY committed_at DESC LIMIT 1"
      )
      val rows = df.collect()
      if (rows.nonEmpty) Some(rows(0).getAs[Long]("snapshot_id")) else None
    } catch {
      case _: Exception => None
    }
  }
}
