package com.olist.mds.spark.silver

import com.olist.mds.spark.normalize.FatalContractFailure
import com.olist.mds.spark.normalize.SparkJobException

/** The three explicit CDC ordering contracts. */
sealed trait SourceEventCategory
case object SnapshotEvent extends SourceEventCategory
case object LiveNonTransactionalEvent extends SourceEventCategory
case object LiveTransactionalEvent extends SourceEventCategory

final case class ValidatedSourceOrdering(
    category: SourceEventCategory,
    sourceBinlogFileIndex: Option[Int],
    sourceBinlogPos: Option[Long],
    sourceRow: Option[Int],
    transactionTotalOrder: Option[Long],
    transactionDataCollectionOrder: Option[Long]
)

/** A decoded Silver input row together with the transport coordinates needed to validate a complete
  * micro-batch.
  */
final case class SourceOrderingEvent(
    decoded: DecodedRecord,
    topic: String,
    kafkaPartition: Int,
    kafkaOffset: Long
) {
  def payloadIdentity: (Option[String], Option[String]) =
    (decoded.keyFingerprint, decoded.valueFingerprint)
}

final case class SourceOrderingConflict(
    code: String,
    message: String,
    event: SourceOrderingEvent,
    conflictingEvent: Option[SourceOrderingEvent] = None
)

final class SourceOrderingBatchException(
    val conflicts: Vector[SourceOrderingConflict]
) extends RuntimeException(
      conflicts
        .map(conflict => s"${conflict.code}: ${conflict.message}")
        .mkString("Source ordering batch rejected: ", "; ", "")
    )

/** Single source of truth for source-version ordering inside Spark.
  *
  * Live rows never fall back to timestamps or Kafka offsets when a MySQL coordinate is missing. The
  * Kafka fields are deterministic tie-breakers only after the source coordinates have been
  * validated.
  */
object SourceOrdering {
  private val BinlogFilename = "^[A-Za-z0-9][A-Za-z0-9_.-]*\\.([0-9]+)$".r

  def parseBinlogFileIndex(filename: String): Int = filename match {
    case BinlogFilename(index) =>
      try {
        val parsed = index.toInt
        if (parsed < 0) {
          throw invalid("MALFORMED_BINLOG_FILENAME", "binlog index must be non-negative")
        }
        parsed
      } catch {
        case _: NumberFormatException =>
          throw invalid("MALFORMED_BINLOG_FILENAME", "binlog index is out of range")
      }
    case _ =>
      throw invalid(
        "MALFORMED_BINLOG_FILENAME",
        "source_binlog_file must end with a numeric binlog index"
      )
  }

  def validate(
      decoded: DecodedRecord,
      kafkaPartition: Int,
      kafkaOffset: Long
  ): ValidatedSourceOrdering = {
    if (decoded.eventId.trim.isEmpty) {
      throw invalid("MISSING_EVENT_ID", "event_id is required")
    }
    if (kafkaPartition < 0 || kafkaOffset < 0) {
      throw invalid("MALFORMED_KAFKA_COORDINATE", "Kafka coordinates must be non-negative")
    }

    val transactionPresent = decoded.transactionId.nonEmpty ||
      decoded.transactionTotalOrder.nonEmpty ||
      decoded.transactionDataCollectionOrder.nonEmpty

    if (decoded.isSnapshot) {
      if (transactionPresent) {
        throw invalid(
          "SNAPSHOT_HAS_TRANSACTION_METADATA",
          "snapshot events cannot carry transaction ordering fields"
        )
      }
      ValidatedSourceOrdering(
        SnapshotEvent,
        None,
        None,
        None,
        None,
        None
      )
    } else {
      val filename = decoded.sourceBinlogFile.filter(_.trim.nonEmpty).getOrElse {
        throw invalid("MISSING_BINLOG_FILENAME", "live CDC requires source_binlog_file")
      }
      val parsedIndex = parseBinlogFileIndex(filename)
      val fileIndex = decoded.sourceBinlogFileIndex match {
        case Some(index) if index != parsedIndex =>
          throw invalid(
            "BINLOG_INDEX_MISMATCH",
            "source_binlog_file_index does not match source_binlog_file"
          )
        case Some(index) => index
        case None => parsedIndex
      }
      val sourcePos = decoded.sourceBinlogPos.filter(_ >= 0).getOrElse {
        throw invalid("MISSING_BINLOG_COORDINATE", "source_binlog_pos is required")
      }
      val sourceRow = decoded.sourceRow.filter(_ >= 0).getOrElse {
        throw invalid("MISSING_BINLOG_COORDINATE", "source_row is required")
      }

      if (transactionPresent) {
        if (
          decoded.transactionId.forall(_.trim.isEmpty) ||
          decoded.transactionTotalOrder.isEmpty ||
          decoded.transactionDataCollectionOrder.isEmpty ||
          decoded.transactionTotalOrder.exists(_ < 0) ||
          decoded.transactionDataCollectionOrder.exists(_ < 0)
        ) {
          throw invalid(
            "INCOMPLETE_TRANSACTION_METADATA",
            "transaction id, total order, and collection order are all required"
          )
        }
        ValidatedSourceOrdering(
          LiveTransactionalEvent,
          Some(fileIndex),
          Some(sourcePos),
          Some(sourceRow),
          decoded.transactionTotalOrder,
          decoded.transactionDataCollectionOrder
        )
      } else {
        ValidatedSourceOrdering(
          LiveNonTransactionalEvent,
          Some(fileIndex),
          Some(sourcePos),
          Some(sourceRow),
          None,
          None
        )
      }
    }
  }

  def canonicalKey(
      decoded: DecodedRecord,
      sourceTsMillis: Long,
      kafkaPartition: Int,
      kafkaOffset: Long
  ): (Int, Int, Long, Int, Long, Long, Long, Int, Long, String) = {
    val validated = validate(decoded, kafkaPartition, kafkaOffset)
    (
      if (validated.category == SnapshotEvent) 0 else 1,
      validated.sourceBinlogFileIndex.getOrElse(-1),
      validated.sourceBinlogPos.getOrElse(-1L),
      validated.sourceRow.getOrElse(-1),
      validated.transactionTotalOrder.getOrElse(-1L),
      validated.transactionDataCollectionOrder.getOrElse(-1L),
      sourceTsMillis,
      kafkaPartition,
      kafkaOffset,
      decoded.eventId
    )
  }

  /** Validate every row before Silver state is materialized.
    *
    * An exact replay is the only duplicate accepted: both the event identity and the wire-payload
    * fingerprints must match. Coordinate identity and the canonical tuple prefix are kept
    * separately so an unrelated topic or transport record cannot silently win an otherwise
    * ambiguous ordering.
    */
  def validateBatch(events: Seq[SourceOrderingEvent]): Vector[SourceOrderingEvent] = {
    val conflicts = Vector.newBuilder[SourceOrderingConflict]
    val accepted = Vector.newBuilder[SourceOrderingEvent]
    val coordinates = scala.collection.mutable.Map.empty[Seq[Any], SourceOrderingEvent]
    val canonicalPrefixes = scala.collection.mutable.Map.empty[Seq[Any], SourceOrderingEvent]
    val eventIdentities = scala.collection.mutable.Map.empty[String, SourceOrderingEvent]

    events.foreach { event =>
      try {
        val validated = validate(event.decoded, event.kafkaPartition, event.kafkaOffset)
        val coordinate = sourceCoordinateKey(event, validated)
        val canonicalPrefix = canonicalPrefixKey(event, validated)

        eventIdentities.get(event.decoded.eventId) match {
          case Some(previous) if previous.payloadIdentity != event.payloadIdentity =>
            conflicts += SourceOrderingConflict(
              "EVENT_ID_COLLISION",
              s"event identity ${event.decoded.eventId} was reused with a different payload",
              event,
              Some(previous)
            )
          case Some(_) =>
            () // exact event identity and payload replay: ignore transport re-delivery
          case _ =>
            coordinates.get(coordinate) match {
              case Some(previous)
                  if previous.decoded.eventId == event.decoded.eventId &&
                    previous.payloadIdentity == event.payloadIdentity =>
                () // exact replay: keep the first physical record only
              case Some(previous) =>
                conflicts += SourceOrderingConflict(
                  "CONFLICTING_SOURCE_COORDINATE",
                  s"source coordinates are shared by ${previous.decoded.eventId} and ${event.decoded.eventId}",
                  event,
                  Some(previous)
                )
              case None =>
                canonicalPrefixes.get(canonicalPrefix) match {
                  case Some(previous) if previous.decoded.eventId != event.decoded.eventId =>
                    conflicts += SourceOrderingConflict(
                      "AMBIGUOUS_CANONICAL_ORDER",
                      s"canonical ordering is ambiguous between ${previous.decoded.eventId} and ${event.decoded.eventId}",
                      event,
                      Some(previous)
                    )
                  case _ =>
                    coordinates += coordinate -> event
                    canonicalPrefixes += canonicalPrefix -> event
                    eventIdentities += event.decoded.eventId -> event
                    accepted += event
                }
            }
        }
      } catch {
        case error: SparkJobException =>
          conflicts += SourceOrderingConflict(
            error.code,
            error.message,
            event,
            None
          )
      }
    }

    val result = conflicts.result()
    if (result.nonEmpty) throw new SourceOrderingBatchException(result)
    accepted.result()
  }

  private def sourceCoordinateKey(
      event: SourceOrderingEvent,
      validated: ValidatedSourceOrdering
  ): Seq[Any] = {
    if (validated.category == SnapshotEvent) {
      Seq(event.topic, validated.category, event.kafkaPartition, event.kafkaOffset)
    } else {
      Seq(
        event.topic,
        validated.category,
        validated.sourceBinlogFileIndex,
        validated.sourceBinlogPos,
        validated.sourceRow,
        validated.transactionTotalOrder,
        validated.transactionDataCollectionOrder
      )
    }
  }

  private def canonicalPrefixKey(
      event: SourceOrderingEvent,
      validated: ValidatedSourceOrdering
  ): Seq[Any] = {
    Seq(
      event.topic,
      if (validated.category == SnapshotEvent) 0 else 1,
      validated.sourceBinlogFileIndex.getOrElse(-1),
      validated.sourceBinlogPos.getOrElse(-1L),
      validated.sourceRow.getOrElse(-1),
      validated.transactionTotalOrder.getOrElse(-1L),
      validated.transactionDataCollectionOrder.getOrElse(-1L),
      event.decoded.sourceTsMs.getOrElse(-1L),
      event.kafkaPartition,
      event.kafkaOffset
    )
  }

  private def invalid(code: String, message: String): SparkJobException =
    SparkJobException(code, message, FatalContractFailure)
}
