package com.olist.mds.spark.bronze

import com.olist.mds.spark.normalize.FatalContractFailure
import com.olist.mds.spark.normalize.SparkJobException
import org.apache.spark.sql.DataFrame
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import java.time.Instant

object BronzeBatchWriter {
  val TargetTable = "lakehouse.bronze.mysql_cdc_records"
  def targetTable(catalogAlias: String): String =
    s"$catalogAlias.bronze.mysql_cdc_records"

  def writeBatch(
      spark: SparkSession,
      batchDf: DataFrame,
      batchId: Long,
      sparkQueryId: String,
      ingestedAt: Instant,
      catalogAlias: String = "lakehouse"
  ): Unit = {
    if (batchDf.isEmpty) return

    val targetTableName = targetTable(catalogAlias)

    val projected = BronzeProjection.project(batchDf, batchId, sparkQueryId, ingestedAt)

    // 1. In-batch collision & duplicate check
    val distinctCount = projected.select("event_id").distinct().count()
    val totalCount = projected.count()

    if (distinctCount != totalCount) {
      // Check if duplicate event_ids are exact byte matches
      val checkDuplicates = projected
        .groupBy("event_id")
        .agg(
          countDistinct("topic").as("c_topic"),
          countDistinct("partition").as("c_partition"),
          countDistinct("offset").as("c_offset"),
          countDistinct("record_kind").as("c_kind"),
          countDistinct("is_tombstone").as("c_tombstone"),
          countDistinct("key_sha256").as("c_ksha"),
          countDistinct("value_sha256").as("c_vsha"),
          countDistinct("key_framing_valid").as("c_kfv"),
          countDistinct("value_framing_valid").as("c_vfv"),
          countDistinct("framing_error").as("c_fe")
        )

      val collision = checkDuplicates.filter(
        col("c_topic") > 1 || col("c_partition") > 1 || col("c_offset") > 1 ||
          col("c_kind") > 1 || col("c_tombstone") > 1 || col("c_ksha") > 1 ||
          col("c_vsha") > 1 || col("c_kfv") > 1 || col("c_vfv") > 1 || col("c_fe") > 1
      )

      if (!collision.isEmpty) {
        throw SparkJobException(
          "event_identity_collision",
          "In-batch event_id collision detected with conflicting payload metadata",
          FatalContractFailure
        )
      }
    }

    // Collapse exact in-batch duplicates
    val deduplicated = projected.dropDuplicates("event_id")

    // 2. Check existing target rows
    if (spark.catalog.tableExists(targetTableName)) {
      val existing = spark.table(targetTableName)

      // Join existing target rows on event_id
      val joined = deduplicated
        .alias("inc")
        .join(
          existing.alias("ext"),
          col("inc.event_id") === col("ext.event_id"),
          "inner"
        )

      if (!joined.isEmpty) {
        // Verify collision on existing target rows
        val mismatch = joined.filter(
          col("inc.topic") =!= col("ext.topic") ||
            col("inc.partition") =!= col("ext.partition") ||
            col("inc.offset") =!= col("ext.offset") ||
            col("inc.record_kind") =!= col("ext.record_kind") ||
            col("inc.is_tombstone") =!= col("ext.is_tombstone") ||
            col("inc.key_sha256") <=> col("ext.key_sha256") === false ||
            col("inc.value_sha256") <=> col("ext.value_sha256") === false ||
            col("inc.key_framing_valid") =!= col("ext.key_framing_valid") ||
            col("inc.value_framing_valid") =!= col("ext.value_framing_valid") ||
            col("inc.framing_error") <=> col("ext.framing_error") === false
        )

        if (!mismatch.isEmpty) {
          throw SparkJobException(
            "event_identity_collision",
            "Target table contains conflicting event_id metadata",
            FatalContractFailure
          )
        }
      }

      // Left-anti join to append only NEW rows
      val newRows = deduplicated.join(existing, Seq("event_id"), "left_anti")

      // Spark 4.1 can invalidate the analyzed plan when a V2 table-backed
      // anti-join is inspected and then reused by DataFrameWriterV2.  Cut
      // the lineage after the existence check so the append receives a
      // stable, already-materialized batch plan.
      if (newRows.count() > 0) {
        newRows.localCheckpoint(eager = true).writeTo(targetTableName).append()
      }
    } else {
      deduplicated.writeTo(targetTableName).append()
    }
  }
}
