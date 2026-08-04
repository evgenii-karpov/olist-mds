package com.olist.mds.spark.app

import com.fasterxml.jackson.databind.ObjectMapper
import com.olist.mds.spark.bronze.BronzeBatchWriter
import com.olist.mds.spark.config.RuntimeConfig
import com.olist.mds.spark.config.SparkSessionFactory
import com.olist.mds.spark.contract.ContractLoader
import com.olist.mds.spark.supervisor.QueryStatus
import com.olist.mds.spark.supervisor.StatusPublisher
import org.apache.spark.sql.streaming.Trigger
import org.apache.spark.sql.streaming.StreamingQuery
import java.io.InputStream
import java.time.Instant
import scala.jdk.CollectionConverters._

object BronzeMain {
  val QueryName = "kafka_to_bronze"

  private val offsetMapper = new ObjectMapper()

  // Structured Streaming owns Kafka offsets in its checkpoint rather than
  // committing a normal consumer-group offset. Publish the source end
  // offsets from the query progress so the target probe can calculate lag
  // against Kafka's current partition offsets without inventing a consumer
  // group that Spark does not maintain.
  private def extractPartitionOffsets(query: StreamingQuery): Map[String, Long] = {
    val progress = query.lastProgress
    if (progress == null) {
      Map.empty
    } else {
      progress.sources.toSeq.flatMap { source =>
        val endOffset = offsetMapper.readTree(source.endOffset)
        if (endOffset == null || !endOffset.isObject) {
          Seq.empty
        } else {
          endOffset.properties().asScala.toSeq.flatMap { topicEntry =>
            val topic = topicEntry.getKey
            val partitions = topicEntry.getValue
            if (!partitions.isObject) {
              Seq.empty
            } else {
              partitions
                .properties()
                .asScala
                .map { partitionEntry =>
                  s"$topic:${partitionEntry.getKey}" -> partitionEntry.getValue.asLong()
                }
                .toSeq
            }
          }
        }
      }.toMap
    }
  }

  private def loadSubscribeTopics(): String = {
    val is: InputStream = getClass.getClassLoader.getResourceAsStream("topics.json")
    if (is == null) throw new IllegalStateException("Resource topics.json missing")
    val mapper = new ObjectMapper()
    val tree = mapper.readTree(is)
    is.close()

    val topicsNode = tree.get("topics")
    val topics = scala.collection.mutable.ArrayBuffer[String]()

    val iter = topicsNode.elements()
    while (iter.hasNext) {
      val t = iter.next()
      val name = t.get("name").asText()
      val purpose = t.get("purpose").asText()
      if (
        purpose == "business_cdc" || purpose == "transaction_metadata" ||
        purpose == "operational_heartbeat" || purpose == "external_schema_changes"
      ) {
        topics += name
      }
    }
    topics.mkString(",")
  }

  def main(args: Array[String]): Unit = {
    val config = RuntimeConfig.load()
    ContractLoader.loadManifest()
    val spark = SparkSessionFactory.createSession("kafka_to_bronze", config)

    val subscribeTopics = loadSubscribeTopics()
    val checkpointLocation = s"${config.sparkCheckpointRoot}/$QueryName/contract-v2/"

    val kafkaStream = spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", config.kafkaBootstrapServers)
      .option("subscribe", subscribeTopics)
      .option("startingOffsets", "earliest")
      .option("failOnDataLoss", "true")
      .option("includeHeaders", "true")
      .load()

    println("DEBUG: BronzeMain starting streaming query...")
    val query = kafkaStream.writeStream
      .queryName(QueryName)
      .trigger(Trigger.ProcessingTime("2 seconds"))
      .option("checkpointLocation", checkpointLocation)
      .foreachBatch { (batchDf: org.apache.spark.sql.DataFrame, batchId: Long) =>
        val now = Instant.now()
        val activeQuery = spark.streams.active.find(_.name == QueryName).getOrElse {
          throw new IllegalStateException(s"Active query $QueryName not found")
        }

        BronzeBatchWriter.writeBatch(spark, batchDf, batchId, activeQuery.id.toString, now)

        // Publish status
        val qStatus = QueryStatus(
          name = QueryName,
          query_id = activeQuery.id.toString,
          state = "RUNNING",
          last_batch_id = batchId,
          last_progress_at_utc = Some(now.toString),
          partition_offsets = extractPartitionOffsets(activeQuery),
          error_class = None,
          error_code = None
        )
        StatusPublisher.publish(
          targetDir = s"${config.sparkStatusDir}/bronze",
          applicationName = "spark-bronze",
          contractVersion = config.sparkContractVersion,
          overallState = "READY",
          queries = Vector(qStatus)
        )
      }
      .start()

    println(s"DEBUG: BronzeMain query started (id: ${query.id}). Publishing initial status...")
    val initStatus = QueryStatus(
      name = QueryName,
      query_id = query.id.toString,
      state = "RUNNING",
      last_batch_id = -1L,
      last_progress_at_utc = None,
      partition_offsets = Map.empty,
      error_class = None,
      error_code = None
    )
    StatusPublisher.publish(
      targetDir = s"${config.sparkStatusDir}/bronze",
      applicationName = "spark-bronze",
      contractVersion = config.sparkContractVersion,
      overallState = "READY",
      queries = Vector(initStatus)
    )

    query.awaitTermination()
  }
}
