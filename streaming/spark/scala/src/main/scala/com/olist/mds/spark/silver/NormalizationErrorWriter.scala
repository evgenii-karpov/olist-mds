package com.olist.mds.spark.silver

import org.apache.spark.sql.Row
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.types._
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.sql.Timestamp
import java.time.Instant

/** Durable, deterministic evidence for a rejected Silver normalization batch. */
object NormalizationErrorWriter {
  val NormalizationErrorsTable = "lakehouse.audit.normalization_errors"

  val schema: StructType = StructType(
    Seq(
      StructField("error_id", StringType, nullable = false),
      StructField("event_id", StringType, nullable = false),
      StructField("entity", StringType, nullable = false),
      StructField("error_code", StringType, nullable = false),
      StructField("error_message", StringType, nullable = false),
      StructField("kafka_topic", StringType, nullable = false),
      StructField("kafka_partition", IntegerType, nullable = false),
      StructField("kafka_offset", LongType, nullable = false),
      StructField("key_schema_id", IntegerType, nullable = true),
      StructField("value_schema_id", IntegerType, nullable = true),
      StructField("schema_fingerprint", StringType, nullable = true),
      StructField("contract_version", IntegerType, nullable = false),
      StructField("first_seen_at", TimestampType, nullable = false),
      StructField("last_seen_at", TimestampType, nullable = false),
      StructField("occurrence_count", LongType, nullable = false),
      StructField("resolved_at", TimestampType, nullable = true),
      StructField("recorded_at", TimestampType, nullable = false)
    )
  )

  private def sha256Hex(value: String): String = {
    val digest = MessageDigest.getInstance("SHA-256")
    digest
      .digest(value.getBytes(StandardCharsets.UTF_8))
      .map(byte => f"$byte%02x")
      .mkString
  }

  private def stableEventIdentity(event: SourceOrderingEvent): String = {
    val decoded = event.decoded
    Seq(
      decoded.eventId,
      event.topic,
      event.kafkaPartition,
      event.kafkaOffset,
      decoded.keySchemaId.getOrElse(-1),
      decoded.valueSchemaId.getOrElse(-1),
      decoded.keyFingerprint.getOrElse(""),
      decoded.valueFingerprint.getOrElse("")
    ).mkString("\u001f")
  }

  /** Stable across retries and independent of wall-clock evidence timestamps. */
  def deterministicErrorId(
      entity: String,
      contractVersion: Int,
      conflict: SourceOrderingConflict
  ): String = {
    val other = conflict.conflictingEvent.map(stableEventIdentity).getOrElse("")
    val eventPair = Seq(stableEventIdentity(conflict.event), other).sorted
    sha256Hex(
      Seq(
        "normalization-ordering-v1",
        entity,
        contractVersion,
        conflict.code,
        eventPair.head,
        eventPair.last
      ).mkString("\u001e")
    )
  }

  private def evidenceRows(
      entity: String,
      contractVersion: Int,
      conflicts: Seq[SourceOrderingConflict],
      recordedAt: Timestamp
  ): Seq[Row] = {
    conflicts.flatMap { conflict =>
      val events =
        (conflict.event +: conflict.conflictingEvent.toSeq).distinctBy(stableEventIdentity)
      events.map { event =>
        val decoded = event.decoded
        val errorId = sha256Hex(
          Seq(
            deterministicErrorId(entity, contractVersion, conflict),
            stableEventIdentity(event)
          ).mkString("\u001e")
        )
        Row(
          errorId,
          decoded.eventId,
          entity,
          conflict.code,
          conflict.message,
          event.topic,
          event.kafkaPartition,
          event.kafkaOffset,
          decoded.keySchemaId.map(Int.box).orNull,
          decoded.valueSchemaId.map(Int.box).orNull,
          decoded.schemaFingerprint.orNull,
          contractVersion,
          recordedAt,
          recordedAt,
          1L,
          null,
          recordedAt
        )
      }
    }
  }

  /** Append only unseen deterministic evidence IDs while holding the table lock. */
  def writeOrderingFailures(
      spark: SparkSession,
      entity: String,
      contractVersion: Int,
      conflicts: Seq[SourceOrderingConflict],
      catalogAlias: String = "lakehouse"
  ): Unit = {
    if (conflicts.isEmpty) return
    val table = s"$catalogAlias.audit.normalization_errors"
    val now = Timestamp.from(Instant.now())
    val evidence = spark.createDataFrame(
      spark.sparkContext.parallelize(evidenceRows(entity, contractVersion, conflicts, now)),
      schema
    )

    IcebergCommitCoordinator.withLock(table) {
      val existing = spark.table(table).select("error_id").distinct()
      val unseen = evidence
        .join(existing, Seq("error_id"), "left_anti")
        .localCheckpoint(eager = true)
      if (unseen.count() > 0) unseen.writeTo(table).append()
    }
  }
}
