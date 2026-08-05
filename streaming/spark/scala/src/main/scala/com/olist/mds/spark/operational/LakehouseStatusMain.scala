package com.olist.mds.spark.operational

import com.fasterxml.jackson.databind.ObjectMapper
import com.olist.mds.spark.config.RuntimeConfig
import com.olist.mds.spark.config.SparkSessionFactory
import org.apache.spark.sql.Row
import org.apache.spark.sql.types._
import java.io.File
import java.nio.file.Files
import java.sql.Timestamp
import java.time.Instant

object LakehouseStatusMain {
  val TargetTable = "lakehouse.audit.lakehouse_status"

  def main(args: Array[String]): Unit = {
    val config = RuntimeConfig.load()
    val spark = SparkSessionFactory.createSession("lakehouse-status-collector", config)

    val statusDirs = Vector(
      s"${config.sparkStatusDir}/bronze/status.json",
      s"${config.sparkStatusDir}/silver/status.json"
    )

    val mapper = new ObjectMapper()
    val rows = scala.collection.mutable.ArrayBuffer[Row]()
    val nowTs = Timestamp.from(Instant.now())

    statusDirs.foreach { pathStr =>
      val file = new File(pathStr)
      if (file.exists()) {
        val content = new String(Files.readAllBytes(file.toPath), "UTF-8")
        val tree = mapper.readTree(content)

        if (
          tree != null && tree.has("application") && tree.has("queries") && !tree
            .get("application")
            .isNull
        ) {
          val appName = tree.get("application").asText()
          val contractVer = tree.get("contract_version").asInt()
          val overallState = tree.get("overall_state").asText()
          val updatedAtStr = tree.get("updated_at_utc").asText()
          val updatedAt = Timestamp.from(Instant.parse(updatedAtStr))

          val queriesNode = tree.get("queries")
          val iter = queriesNode.elements()
          while (iter.hasNext) {
            val q = iter.next()
            val qName = q.get("name").asText()
            val qId = q.get("query_id").asText()
            val qState = q.get("state").asText()
            val lastBatchId = q.get("last_batch_id").asLong()
            val lastProgStr =
              if (q.has("last_progress_at_utc") && !q.get("last_progress_at_utc").isNull) {
                q.get("last_progress_at_utc").asText()
              } else null
            val lastProgTs =
              if (lastProgStr != null) Timestamp.from(Instant.parse(lastProgStr)) else null

            rows += Row(
              appName,
              contractVer,
              overallState,
              updatedAt,
              qName,
              qId,
              qState,
              lastBatchId,
              lastProgTs,
              nowTs
            )
          }
        }
      }
    }

    // The status collector is a one-shot operational writer. Keep its target
    // relation self-healing so a fresh catalog does not turn a valid status
    // snapshot into a failed spark-ops container before the first append.
    spark.sql(
      s"""
         |CREATE TABLE IF NOT EXISTS $TargetTable (
         |  application STRING NOT NULL,
         |  contract_version INT NOT NULL,
         |  overall_state STRING NOT NULL,
         |  updated_at_utc TIMESTAMP NOT NULL,
         |  query_name STRING NOT NULL,
         |  query_id STRING NOT NULL,
         |  query_state STRING NOT NULL,
         |  last_batch_id BIGINT NOT NULL,
         |  last_progress_at_utc TIMESTAMP,
         |  recorded_at TIMESTAMP NOT NULL
         |) USING iceberg
         |TBLPROPERTIES (
         |  'format-version' = '2',
         |  'write.format.default' = 'parquet',
         |  'write.parquet.compression-codec' = 'zstd',
         |  'write.target-file-size-bytes' = '134217728',
         |  'write.metadata.delete-after-commit.enabled' = 'true',
         |  'write.metadata.previous-versions-max' = '20'
         |)
         |""".stripMargin
    )

    if (rows.nonEmpty) {
      val schema = StructType(
        Seq(
          StructField("application", StringType, nullable = false),
          StructField("contract_version", IntegerType, nullable = false),
          StructField("overall_state", StringType, nullable = false),
          StructField("updated_at_utc", TimestampType, nullable = false),
          StructField("query_name", StringType, nullable = false),
          StructField("query_id", StringType, nullable = false),
          StructField("query_state", StringType, nullable = false),
          StructField("last_batch_id", LongType, nullable = false),
          StructField("last_progress_at_utc", TimestampType, nullable = true),
          StructField("recorded_at", TimestampType, nullable = false)
        )
      )

      val df = spark.createDataFrame(spark.sparkContext.parallelize(rows.toSeq), schema)
      df.writeTo(TargetTable).append()
      println(s"Appended ${rows.size} status records to $TargetTable.")
    } else {
      println("No active status files found.")
    }
  }
}
