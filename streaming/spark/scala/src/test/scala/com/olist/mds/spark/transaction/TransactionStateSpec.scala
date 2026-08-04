package com.olist.mds.spark.transaction

import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.matchers.should.Matchers

class TransactionStateSpec extends AnyFunSuite with Matchers {
  private def observation(
      id: String,
      status: String,
      offset: Long,
      recordedAt: Long,
      eventId: String
  ): TransactionObservation =
    TransactionObservation(id, status, offset, recordedAt, eventId)

  test("BEGIN and END observations split across batches become COMPLETE") {
    val effective = TransactionState.collapse(
      Seq(
        observation("tx-1", "OPEN", 10, 1, "begin"),
        observation("tx-1", "COMPLETE", 11, 2, "end")
      )
    )

    effective shouldBe Seq(observation("tx-1", "COMPLETE", 11, 2, "end"))
  }

  test("an unresolved BEGIN remains visible as OPEN") {
    TransactionState.collapse(
      Seq(observation("tx-open", "OPEN", 20, 1, "begin"))
    ) shouldBe Seq(observation("tx-open", "OPEN", 20, 1, "begin"))
  }

  test("a later COMPLETE replaces a REJECTED observation") {
    val effective = TransactionState.collapse(
      Seq(
        observation("tx-retry", "REJECTED", 30, 1, "rejected"),
        observation("tx-retry", "COMPLETE", 31, 2, "end")
      )
    )

    effective.head.status shouldBe "COMPLETE"
    effective.head.kafkaOffset shouldBe 31
  }

  test("duplicate END observations are idempotent") {
    val effective = TransactionState.collapse(
      Seq(
        observation("tx-duplicate", "OPEN", 40, 1, "begin"),
        observation("tx-duplicate", "COMPLETE", 41, 2, "end-1"),
        observation("tx-duplicate", "COMPLETE", 41, 3, "end-2")
      )
    )

    effective should have size 1
    effective.head.status shouldBe "COMPLETE"
    effective.head.kafkaOffset shouldBe 41
  }

  test("effective transactions are ordered by Kafka offset") {
    val effective = TransactionState.collapse(
      Seq(
        observation("tx-2", "COMPLETE", 200, 2, "end-2"),
        observation("tx-1", "COMPLETE", 100, 1, "end-1")
      )
    )

    effective.map(_.transactionId) shouldBe Seq("tx-1", "tx-2")
  }
}
