package com.olist.mds.spark.supervisor

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.SerializationFeature
import com.fasterxml.jackson.module.scala.DefaultScalaModule
import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.nio.file.Paths
import java.time.Instant

final case class QueryStatus(
    name: String,
    query_id: String,
    state: String,
    last_batch_id: Long,
    last_progress_at_utc: Option[String],
    partition_offsets: Map[String, Long],
    error_class: Option[String],
    error_code: Option[String]
)

final case class ApplicationStatus(
    application: String,
    contract_version: Int,
    overall_state: String,
    updated_at_utc: String,
    queries: Vector[QueryStatus]
)

object StatusPublisher {
  private val mapper = new ObjectMapper()
    .registerModule(DefaultScalaModule)
    .enable(SerializationFeature.INDENT_OUTPUT)

  def publish(
      targetDir: String,
      applicationName: String,
      contractVersion: Int,
      overallState: String,
      queries: Vector[QueryStatus]
  ): Unit = {
    try {
      val dir = Paths.get(targetDir)
      if (!Files.exists(dir)) {
        Files.createDirectories(dir)
      }

      val sortedQueries = queries.sortBy(_.name)
      val status = ApplicationStatus(
        application = applicationName,
        contract_version = contractVersion,
        overall_state = overallState,
        updated_at_utc = Instant.now().toString,
        queries = sortedQueries
      )

      val jsonString = mapper.writeValueAsString(status)
      val targetFile = dir.resolve("status.json")

      Files.write(targetFile, jsonString.getBytes(StandardCharsets.UTF_8))
    } catch {
      case e: Throwable =>
        System.err.println(
          s"StatusPublisher failed for $applicationName in $targetDir: ${e.getMessage}"
        )
        e.printStackTrace()
    }
  }
}
