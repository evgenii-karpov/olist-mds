package com.olist.mds.spark.silver

import com.olist.mds.spark.contract.EntityContract
import com.olist.mds.spark.avro.RegistrySchemaResolver
import com.olist.mds.spark.normalize.FatalContractFailure
import com.olist.mds.spark.normalize.SparkJobException
import org.apache.spark.sql.DataFrame
import org.apache.spark.sql.Row
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.expressions.Window
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import java.sql.Timestamp
import java.time.Instant

object SilverBatchWriter {

  def writeBatch(
      spark: SparkSession,
      bronzeDf: DataFrame,
      contract: EntityContract,
      batchId: Long,
      sparkQueryId: String = "silver-replay",
      registryResolver: Option[RegistrySchemaResolver] = None
  ): Unit = {
    // Tombstones are a Kafka bookkeeping record, not a second delete event.
    // The preceding Debezium delete envelope is the record that belongs in
    // Silver.
    val topicRows = bronzeDf
      .filter(col("topic") === contract.topic)
      .filter(coalesce(col("is_tombstone"), lit(false)) === lit(false))
      .filter(col("value_bytes").isNotNull)

    if (topicRows.isEmpty) return

    // Bronze stores the hash of the wire payload.  Contract fingerprints are
    // hashes of the writer schema, so validation must use the framed schema
    // IDs and not compare the two unrelated hashes.
    val invalidRows = topicRows.filter(
      col("key_framing_valid") =!= lit(true) ||
        col("value_framing_valid") =!= lit(true) ||
        col("key_schema_id").isNull ||
        col("value_schema_id").isNull ||
        !col("key_schema_id").isin(contract.allowedKeySchemaIds.toSeq: _*)
    )

    if (!invalidRows.isEmpty) {
      throw SparkJobException(
        "unknown_schema_id",
        s"Unapproved writer schema or invalid framing in bronze batch $batchId for ${contract.entity}",
        FatalContractFailure
      )
    }

    val rows = topicRows.collect().toSeq
    if (rows.isEmpty) return

    val decodedRows = rows.map { row =>
      val eventId = row.getAs[String]("event_id")
      val keyBytes = row.getAs[Array[Byte]]("key_bytes")
      val valueBytes = row.getAs[Array[Byte]]("value_bytes")
      val decoded = SilverDecoder.decodeRow(
        eventId,
        keyBytes,
        valueBytes,
        contract,
        registryResolver
      )
      val kafkaTimestamp = row.getAs[Timestamp]("kafka_timestamp")
      val sourceTimestamp = decoded.sourceTsMs
        .map(value => Timestamp.from(Instant.ofEpochMilli(value)))
        .getOrElse(kafkaTimestamp)
      (decoded, row, sourceTimestamp)
    }

    decodedRows.foreach { case (decoded, row, _) =>
      SourceOrdering.validate(
        decoded,
        row.getAs[Int]("partition"),
        row.getAs[Long]("offset")
      )
    }

    val changesTable = s"lakehouse.silver.${contract.entity}_changes"
    val currentTable = s"lakehouse.silver.${contract.entity}_current"
    val now = Timestamp.from(Instant.now())

    val contractColumns = contract.businessColumns.map(column => column.name).toSet
    val dynamicTypes = decodedRows
      .flatMap { case (decoded, _, _) => decoded.businessTypes }
      .toMap
      .filterNot { case (name, _) => contractColumns.contains(name) }
    dynamicTypes.keys.foreach { name =>
      if (!name.matches("[A-Za-z0-9_]+")) {
        throw SparkJobException(
          "incompatible_schema_evolution",
          s"Dynamic Value field has an invalid identifier: $name",
          FatalContractFailure
        )
      }
    }
    val dynamicColumns = dynamicTypes.toVector.sortBy(_._1).map { case (name, dataType) =>
      com.olist.mds.spark.contract.BusinessColumn(name, dataType, nullable = true, None)
    }
    val businessColumns = contract.businessColumns ++ dynamicColumns
    ensureIcebergColumns(spark, changesTable, dynamicColumns)
    ensureIcebergColumns(spark, currentTable, dynamicColumns)

    val changesSchema = StructType(
      Vector(
        StructField("event_id", StringType, nullable = false),
        StructField("op", StringType, nullable = false),
        StructField("is_snapshot", BooleanType, nullable = false),
        StructField("is_deleted", BooleanType, nullable = false),
        StructField("apply_status", StringType, nullable = false),
        StructField("error_code", StringType, nullable = true),
        StructField("error_message", StringType, nullable = true)
      ) ++
        businessColumns.map(column =>
          StructField(column.name, column.sparkType, nullable = true)
        ) ++ Vector(
          StructField("source_ts", TimestampType, nullable = false),
          StructField("source_server_id", LongType, nullable = true),
          StructField("source_gtid", StringType, nullable = true),
          StructField("source_binlog_file", StringType, nullable = true),
          StructField("source_binlog_file_index", IntegerType, nullable = true),
          StructField("source_binlog_pos", LongType, nullable = true),
          StructField("source_row", IntegerType, nullable = true),
          StructField("transaction_id", StringType, nullable = true),
          StructField("transaction_total_order", LongType, nullable = true),
          StructField("transaction_data_collection_order", LongType, nullable = true),
          StructField("kafka_topic", StringType, nullable = false),
          StructField("kafka_partition", IntegerType, nullable = false),
          StructField("kafka_offset", LongType, nullable = false),
          StructField("kafka_timestamp", TimestampType, nullable = false),
          StructField("key_schema_id", IntegerType, nullable = true),
          StructField("value_schema_id", IntegerType, nullable = true),
          StructField("schema_fingerprint", StringType, nullable = true),
          StructField("contract_version", IntegerType, nullable = false),
          StructField("before_row_hash", StringType, nullable = true),
          StructField("after_row_hash", StringType, nullable = true),
          StructField("row_hash", StringType, nullable = true),
          StructField("bronze_ingested_at", TimestampType, nullable = true),
          StructField("normalized_at", TimestampType, nullable = false)
        )
    )

    val changesRows = decodedRows.map { case (decoded, row, sourceTimestamp) =>
      val businessValues =
        businessColumns.map(column => decoded.businessValues.getOrElse(column.name, null))
      Row.fromSeq(
        Vector[Any](
          decoded.eventId,
          decoded.op,
          decoded.isSnapshot,
          decoded.isDeleted,
          "APPLIED",
          null,
          null
        ) ++ businessValues ++ Vector[Any](
          sourceTimestamp,
          decoded.sourceServerId.map(Long.box).orNull,
          decoded.sourceGtid.orNull,
          decoded.sourceBinlogFile.orNull,
          decoded.sourceBinlogFileIndex.map(Int.box).orNull,
          decoded.sourceBinlogPos.map(Long.box).orNull,
          decoded.sourceRow.map(Int.box).orNull,
          decoded.transactionId.orNull,
          decoded.transactionTotalOrder.map(Long.box).orNull,
          decoded.transactionDataCollectionOrder.map(Long.box).orNull,
          row.getAs[String]("topic"),
          row.getAs[Int]("partition"),
          row.getAs[Long]("offset"),
          row.getAs[Timestamp]("kafka_timestamp"),
          decoded.keySchemaId.map(Int.box).orNull,
          decoded.valueSchemaId.map(Int.box).orNull,
          null,
          2,
          decoded.beforeRowHash.orNull,
          decoded.afterRowHash.orNull,
          decoded.rowHash.orNull,
          row.getAs[Timestamp]("ingested_at"),
          now
        )
      )
    }
    val changesDf = spark.createDataFrame(
      spark.sparkContext.parallelize(changesRows),
      changesSchema
    )

    // Avoid MERGE here: Spark 4.1.3 can invalidate the analyzed plan of an
    // Iceberg V2 MERGE from inside foreachBatch.  A materialized anti-join
    // gives the same event-id idempotency without reusing a table-backed plan.
    val existingEventIds = spark.table(changesTable).select("event_id").distinct()
    val newChanges = changesDf
      .join(existingEventIds, Seq("event_id"), "left_anti")
      .localCheckpoint(eager = true)
    IcebergCommitCoordinator.withLock(changesTable) {
      if (newChanges.count() > 0) newChanges.writeTo(changesTable).append()
    }
    val changesSnapshotId = SilverProgressWriter.getLatestSnapshotId(spark, changesTable)

    val currentSchema = StructType(
      businessColumns.map(column =>
        StructField(column.name, column.sparkType, nullable = true)
      ) ++ Vector(
        StructField("is_deleted", BooleanType, nullable = false),
        StructField("deleted_at", TimestampType, nullable = true),
        StructField("last_event_id", StringType, nullable = false),
        StructField("last_source_ts", TimestampType, nullable = false),
        StructField("last_is_snapshot", BooleanType, nullable = false),
        StructField("last_source_binlog_file_index", IntegerType, nullable = true),
        StructField("last_source_binlog_pos", LongType, nullable = true),
        StructField("last_source_row", IntegerType, nullable = true),
        StructField("last_transaction_total_order", LongType, nullable = true),
        StructField("last_transaction_data_collection_order", LongType, nullable = true),
        StructField("last_transaction_id", StringType, nullable = true),
        StructField("last_kafka_partition", IntegerType, nullable = false),
        StructField("last_kafka_offset", LongType, nullable = false),
        StructField("last_row_hash", StringType, nullable = false),
        StructField("contract_version", IntegerType, nullable = false),
        StructField("updated_at", TimestampType, nullable = false)
      )
    )
    val currentRows = decodedRows.map { case (decoded, row, sourceTimestamp) =>
      val businessValues =
        businessColumns.map(column => decoded.businessValues.getOrElse(column.name, null))
      Row.fromSeq(
        businessValues ++ Vector[Any](
          decoded.isDeleted,
          if (decoded.isDeleted) sourceTimestamp else null,
          decoded.eventId,
          sourceTimestamp,
          decoded.isSnapshot,
          decoded.sourceBinlogFileIndex.map(Int.box).orNull,
          decoded.sourceBinlogPos.map(Long.box).orNull,
          decoded.sourceRow.map(Int.box).orNull,
          decoded.transactionTotalOrder.map(Long.box).orNull,
          decoded.transactionDataCollectionOrder.map(Long.box).orNull,
          decoded.transactionId.orNull,
          row.getAs[Int]("partition"),
          row.getAs[Long]("offset"),
          decoded.rowHash.getOrElse(throw new IllegalStateException("Missing row hash")),
          2,
          now
        )
      )
    }
    val currentDf = spark.createDataFrame(
      spark.sparkContext.parallelize(currentRows),
      currentSchema
    )

    val pkWindow = Window
      .partitionBy(contract.primaryKey.map(col): _*)
      .orderBy(
        col("last_is_snapshot").cast("int").desc,
        coalesce(col("last_source_binlog_file_index"), lit(-1)).desc,
        coalesce(col("last_source_binlog_pos"), lit(-1L)).desc,
        coalesce(col("last_source_row"), lit(-1)).desc,
        coalesce(col("last_transaction_total_order"), lit(-1L)).desc,
        coalesce(col("last_transaction_data_collection_order"), lit(-1L)).desc,
        col("last_source_ts").desc,
        col("last_kafka_partition").desc,
        col("last_kafka_offset").desc,
        col("last_event_id").desc
      )
    val latestCurrentDf = currentDf
      .withColumn("_rn", row_number().over(pkWindow))
      .filter(col("_rn") === 1)
      .drop("_rn")
    IcebergCommitCoordinator.withLock(currentTable) {
      latestCurrentDf.writeTo(currentTable).append()
    }
    val currentSnapshotId = SilverProgressWriter.getLatestSnapshotId(spark, currentTable)

    val progressRecords = decodedRows
      .groupBy { case (_, row, _) => row.getAs[Int]("partition") }
      .values
      .map { items =>
        val last = items.maxBy { case (_, row, _) => row.getAs[Long]("offset") }
        val lastDecoded = last._1
        val lastRow = last._2
        SilverProgressRecord(
          queryName = s"bronze_to_silver_${contract.entity}",
          entity = contract.entity,
          contractVersion = 2,
          sourceTopic = lastRow.getAs[String]("topic"),
          kafkaPartition = lastRow.getAs[Int]("partition"),
          lastKafkaOffset = lastRow.getAs[Long]("offset"),
          lastEventId = lastDecoded.eventId,
          lastSourceTs = Some(last._3),
          sparkQueryId = sparkQueryId,
          sparkBatchId = batchId,
          changesSnapshotId = changesSnapshotId,
          currentSnapshotId = currentSnapshotId,
          status = "COMMITTED",
          errorClass = None
        )
      }
      .toSeq

    SilverProgressWriter.writeProgress(spark, progressRecords)
  }

  private def ensureIcebergColumns(
      spark: SparkSession,
      table: String,
      columns: Vector[com.olist.mds.spark.contract.BusinessColumn]
  ): Unit = {
    if (columns.isEmpty) return
    val existing = spark.table(table).schema.fieldNames.toSet
    columns.filterNot(column => existing.contains(column.name)).foreach { column =>
      spark.sql(
        s"ALTER TABLE $table ADD COLUMN `${column.name}` ${column.sparkType.sql}"
      )
    }
  }
}
