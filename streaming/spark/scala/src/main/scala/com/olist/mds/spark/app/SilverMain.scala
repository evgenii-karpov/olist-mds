package com.olist.mds.spark.app

import com.olist.mds.spark.config.RuntimeConfig
import com.olist.mds.spark.config.SparkSessionFactory
import com.olist.mds.spark.contract.ContractLoader
import com.olist.mds.spark.silver.SilverBatchWriter
import com.olist.mds.spark.supervisor.QueryStatus
import com.olist.mds.spark.supervisor.StatusPublisher
import org.apache.spark.sql.streaming.Trigger
import java.time.Instant

object SilverMain {

  def main(args: Array[String]): Unit = {
    val config = RuntimeConfig.load()
    val contracts = ContractLoader.loadAll()
    val spark = SparkSessionFactory.createSession("silver-streaming-engine", config)

    val queryStatuses = scala.collection.mutable.Map[String, QueryStatus]()

    println(s"DEBUG: SilverMain starting queries for ${contracts.size} entities...")

    val queries = contracts.values.map { contract =>
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

    println(
      s"DEBUG: SilverMain started ${queries.size} queries. Publishing initial status to ${config.sparkStatusDir}/silver..."
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
