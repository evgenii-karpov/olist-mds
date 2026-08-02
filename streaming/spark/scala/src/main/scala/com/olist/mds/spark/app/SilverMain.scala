package com.olist.mds.spark.app

import com.olist.mds.spark.config.RuntimeConfig
import com.olist.mds.spark.config.SparkSessionFactory
import com.olist.mds.spark.contract.ContractLoader
import com.olist.mds.spark.schema.SchemaArchiveWriter
import com.olist.mds.spark.silver.SilverBatchWriter
import com.olist.mds.spark.supervisor.QueryStatus
import com.olist.mds.spark.supervisor.StatusPublisher
import com.olist.mds.spark.transaction.TransactionBatchWriter
import org.apache.spark.sql.streaming.Trigger
import java.time.Instant

object SilverMain {

  def main(args: Array[String]): Unit = {
    val config = RuntimeConfig.load()
    val contracts = ContractLoader.loadAll()
    val spark = SparkSessionFactory.createSession("silver-streaming-engine", config)

    val queryStatuses = scala.collection.mutable.Map[String, QueryStatus]()

    println(
      s"DEBUG: SilverMain starting 10 queries (${contracts.size} entities + schemas + transactions)..."
    )

    // 1-8. Entity Queries
    val entityQueries = contracts.values.map { contract =>
      val queryName = s"bronze_to_silver_${contract.entity}"
      val checkpointLocation =
        s"${config.sparkCheckpointRoot}/silver_${contract.entity}/contract-v2/"

      val bronzeStream = spark.readStream
        .table("lakehouse.bronze.mysql_cdc_records")
        .filter(org.apache.spark.sql.functions.col("topic") === contract.topic)

      val streamingQuery = bronzeStream.writeStream
        .queryName(queryName)
        .trigger(Trigger.ProcessingTime("2 seconds"))
        .option("checkpointLocation", checkpointLocation)
        .foreachBatch { (batchDf: org.apache.spark.sql.DataFrame, batchId: Long) =>
          val now = Instant.now()
          val activeQuery = spark.streams.active.find(_.name == queryName).getOrElse {
            throw new IllegalStateException(s"Active query $queryName not found")
          }

          SilverBatchWriter.writeBatch(spark, batchDf, contract, batchId)

          queryStatuses.synchronized {
            queryStatuses(queryName) = QueryStatus(
              name = queryName,
              query_id = activeQuery.id.toString,
              state = "RUNNING",
              last_batch_id = batchId,
              last_progress_at_utc = Some(now.toString),
              partition_offsets = Map.empty,
              error_class = None,
              error_code = None
            )

            StatusPublisher.publish(
              targetDir = s"${config.sparkStatusDir}/silver",
              applicationName = "spark-silver",
              contractVersion = config.sparkContractVersion,
              overallState = "READY",
              queries = queryStatuses.values.toVector
            )
          }
        }
        .start()

      queryStatuses.synchronized {
        queryStatuses(queryName) = QueryStatus(
          name = queryName,
          query_id = streamingQuery.id.toString,
          state = "RUNNING",
          last_batch_id = -1L,
          last_progress_at_utc = None,
          partition_offsets = Map.empty,
          error_class = None,
          error_code = None
        )
      }
      streamingQuery
    }.toVector

    // 9. capture_avro_schemas
    val schemaQueryName = "capture_avro_schemas"
    val schemaCheckpoint = s"${config.sparkCheckpointRoot}/silver_capture_avro_schemas/contract-v2/"
    val schemaStream = spark.readStream
      .table("lakehouse.bronze.mysql_cdc_records")
      .filter(
        org.apache.spark.sql.functions.col("topic").isin("olist_cdc.__schemas__", "__schemas__")
      )
      .writeStream
      .queryName(schemaQueryName)
      .trigger(Trigger.ProcessingTime("2 seconds"))
      .option("checkpointLocation", schemaCheckpoint)
      .foreachBatch { (batchDf: org.apache.spark.sql.DataFrame, batchId: Long) =>
        SchemaArchiveWriter.writeBatch(spark, batchDf, batchId)
      }
      .start()

    // 10. normalize_mysql_transactions
    val txQueryName = "normalize_mysql_transactions"
    val txCheckpoint =
      s"${config.sparkCheckpointRoot}/silver_normalize_mysql_transactions/contract-v2/"
    val txStream = spark.readStream
      .table("lakehouse.bronze.mysql_cdc_records")
      .filter(
        org.apache.spark.sql.functions.col("topic").isin("olist_cdc.transaction", "transaction")
      )
      .writeStream
      .queryName(txQueryName)
      .trigger(Trigger.ProcessingTime("2 seconds"))
      .option("checkpointLocation", txCheckpoint)
      .foreachBatch { (batchDf: org.apache.spark.sql.DataFrame, batchId: Long) =>
        TransactionBatchWriter.writeBatch(spark, batchDf, batchId)
      }
      .start()

    println(
      s"DEBUG: SilverMain started 10 queries. Publishing status to ${config.sparkStatusDir}/silver..."
    )
    StatusPublisher.publish(
      targetDir = s"${config.sparkStatusDir}/silver",
      applicationName = "spark-silver",
      contractVersion = config.sparkContractVersion,
      overallState = "READY",
      queries = queryStatuses.values.toVector
    )

    spark.streams.awaitAnyTermination()
  }
}
