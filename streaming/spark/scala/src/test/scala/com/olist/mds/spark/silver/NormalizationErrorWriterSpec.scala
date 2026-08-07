package com.olist.mds.spark.silver

import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.matchers.should.Matchers

class NormalizationErrorWriterSpec extends AnyFunSuite with Matchers {
  private def event(eventId: String, valueFingerprint: String): SourceOrderingEvent =
    SourceOrderingEvent(
      DecodedRecord(
        eventId = eventId,
        op = "c",
        isDeleted = false,
        isSnapshot = true,
        sourceTsMs = Some(1577836800000L),
        sourceServerId = None,
        sourceGtid = None,
        sourceBinlogFile = None,
        sourceBinlogFileIndex = None,
        sourceBinlogPos = None,
        sourceRow = None,
        transactionId = None,
        transactionTotalOrder = None,
        transactionDataCollectionOrder = None,
        keySchemaId = Some(11),
        valueSchemaId = Some(13),
        keyFingerprint = Some("a" * 64),
        valueFingerprint = Some(valueFingerprint),
        beforeRowHash = None,
        afterRowHash = Some(valueFingerprint),
        rowHash = Some(valueFingerprint),
        businessValues = Map.empty,
        businessTypes = Map.empty
      ),
      topic = "olist_cdc.olist_oltp.orders",
      kafkaPartition = 0,
      kafkaOffset = 10L
    )

  test("audit error IDs are deterministic and schema carries the Bronze locator") {
    val first = event("event-a", "b" * 64)
    val second = event("event-b", "c" * 64)
    val conflict = SourceOrderingConflict(
      "CONFLICTING_SOURCE_COORDINATE",
      "same source coordinate",
      second,
      Some(first)
    )

    val idOne = NormalizationErrorWriter.deterministicErrorId("orders", 2, conflict)
    val idTwo = NormalizationErrorWriter.deterministicErrorId(
      "orders",
      2,
      conflict.copy(event = first, conflictingEvent = Some(second))
    )

    idOne shouldBe idTwo
    idOne should have length 64
    NormalizationErrorWriter.schema.fieldNames.toSeq should contain theSameElementsInOrderAs Seq(
      "error_id",
      "event_id",
      "entity",
      "error_code",
      "error_message",
      "kafka_topic",
      "kafka_partition",
      "kafka_offset",
      "key_schema_id",
      "value_schema_id",
      "schema_fingerprint",
      "contract_version",
      "first_seen_at",
      "last_seen_at",
      "occurrence_count",
      "resolved_at",
      "recorded_at"
    )
  }
}
