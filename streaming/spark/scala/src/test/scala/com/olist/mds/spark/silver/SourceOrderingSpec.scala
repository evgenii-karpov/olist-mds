package com.olist.mds.spark.silver

import com.olist.mds.spark.normalize.SparkJobException
import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.matchers.should.Matchers

class SourceOrderingSpec extends AnyFunSuite with Matchers {
  test("binlog indexes require a numeric suffix") {
    SourceOrdering.parseBinlogFileIndex("mysql-bin.000007") shouldBe 7
    an[SparkJobException] should be thrownBy {
      SourceOrdering.parseBinlogFileIndex("mysql-bin")
    }
  }

  test("Debezium snapshot markers include data-collection boundary values") {
    Seq("true", "last", "first_in_data_collection", "last_in_data_collection")
      .foreach(marker => SilverDecoder.isSnapshotMarker(marker) shouldBe true)
  }

  private def event(
      eventId: String,
      snapshot: Boolean = false,
      sourceFile: Option[String] = Some("mysql-bin.000007"),
      sourcePos: Option[Long] = Some(100L),
      sourceRow: Option[Int] = Some(1),
      transactionId: Option[String] = None,
      transactionTotal: Option[Long] = None,
      transactionCollection: Option[Long] = None,
      keyFingerprint: String = "a" * 64,
      valueFingerprint: String = "b" * 64,
      partition: Int = 0,
      offset: Long = 10L
  ): SourceOrderingEvent = {
    SourceOrderingEvent(
      DecodedRecord(
        eventId = eventId,
        op = "c",
        isDeleted = false,
        isSnapshot = snapshot,
        sourceTsMs = Some(1577836800000L),
        sourceServerId = Some(1L),
        sourceGtid = None,
        sourceBinlogFile = sourceFile,
        sourceBinlogFileIndex = sourceFile.map(SourceOrdering.parseBinlogFileIndex),
        sourceBinlogPos = sourcePos,
        sourceRow = sourceRow,
        transactionId = transactionId,
        transactionTotalOrder = transactionTotal,
        transactionDataCollectionOrder = transactionCollection,
        keySchemaId = Some(1),
        valueSchemaId = Some(2),
        keyFingerprint = Some(keyFingerprint),
        valueFingerprint = Some(valueFingerprint),
        beforeRowHash = None,
        afterRowHash = Some(valueFingerprint),
        rowHash = Some(valueFingerprint),
        businessValues = Map.empty,
        businessTypes = Map.empty
      ),
      topic = "olist_cdc.olist_oltp.orders",
      kafkaPartition = partition,
      kafkaOffset = offset
    )
  }

  test("batch validation rejects snapshot coordinate conflicts") {
    val first = event("snapshot-a", snapshot = true)
    val second = event("snapshot-b", snapshot = true)

    val failure = intercept[SourceOrderingBatchException] {
      SourceOrdering.validateBatch(Seq(first, second))
    }

    failure.conflicts.map(_.code) should contain("CONFLICTING_SOURCE_COORDINATE")
  }

  test("batch validation rejects live non-transactional coordinate conflicts") {
    val failure = intercept[SourceOrderingBatchException] {
      SourceOrdering.validateBatch(Seq(event("live-a"), event("live-b", offset = 11L)))
    }

    failure.conflicts.map(_.code) should contain("CONFLICTING_SOURCE_COORDINATE")
  }

  test("batch validation rejects live transactional coordinate conflicts") {
    val first = event(
      "tx-a",
      transactionId = Some("tx-1"),
      transactionTotal = Some(1L),
      transactionCollection = Some(1L)
    )
    val second = event(
      "tx-b",
      transactionId = Some("tx-2"),
      transactionTotal = Some(1L),
      transactionCollection = Some(1L),
      offset = 11L
    )

    val failure = intercept[SourceOrderingBatchException] {
      SourceOrdering.validateBatch(Seq(first, second))
    }

    failure.conflicts.map(_.code) should contain("CONFLICTING_SOURCE_COORDINATE")
  }

  test("exact replay of the same event identity and payload is idempotent") {
    SourceOrdering.validateBatch(Seq(event("replay"), event("replay"))) should have size 1
  }

  test("exact replay remains idempotent when transport coordinates differ") {
    val replay = event("replay", sourcePos = Some(101L), offset = 11L)
    SourceOrdering.validateBatch(Seq(event("replay"), replay)) should have size 1
  }
}
