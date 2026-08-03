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
    lastKafkaOffset: Long,
    lastEventId: String,
    lastSourceTs: Option[Timestamp],
    sparkQueryId: String,
    sparkBatchId: Long,
    changesSnapshotId: Option[Long],
    currentSnapshotId: Option[Long],
    status: String,
    errorClass: Option[String]
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
      StructField("last_kafka_offset", LongType, nullable = false),
      StructField("last_event_id", StringType, nullable = false),
      StructField("last_source_ts", TimestampType, nullable = true),
      StructField("spark_query_id", StringType, nullable = false),
      StructField("spark_batch_id", LongType, nullable = false),
      StructField("changes_snapshot_id", LongType, nullable = false),
      StructField("current_snapshot_id", LongType, nullable = true),
      StructField("status", StringType, nullable = false),
      StructField("error_class", StringType, nullable = true),
      StructField("updated_at", TimestampType, nullable = false),
      StructField("recorded_at", TimestampType, nullable = false)
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
        r.lastKafkaOffset,
        r.lastEventId,
        r.lastSourceTs.orNull,
        r.sparkQueryId,
        r.sparkBatchId,
        r.changesSnapshotId.map(java.lang.Long.valueOf).getOrElse {
          throw new IllegalStateException(
            s"Missing changes snapshot for ${r.entity} batch ${r.sparkBatchId}"
          )
        },
        r.currentSnapshotId.map(java.lang.Long.valueOf).orNull,
        r.status,
        r.errorClass.orNull,
        now,
        now
      )
    }

    val df = spark.createDataFrame(spark.sparkContext.parallelize(rows), schema)
    IcebergCommitCoordinator.withLock(ProgressTable) { df.writeTo(ProgressTable).append() }
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
