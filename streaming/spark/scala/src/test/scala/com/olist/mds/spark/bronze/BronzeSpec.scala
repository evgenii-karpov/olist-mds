package com.olist.mds.spark.bronze

import com.olist.mds.spark.avro.ConfluentFrame
import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.matchers.should.Matchers

class BronzeSpec extends AnyFunSuite with Matchers {

  test("ConfluentFrame inspect correctly classifies framing error codes") {
    // Null key
    val nullKey = ConfluentFrame.inspect(null, isKey = true)
    nullKey.framingValid shouldBe true
    nullKey.schemaId shouldBe None
    nullKey.errorCode shouldBe None

    // Null value (tombstone)
    val nullVal = ConfluentFrame.inspect(null, isKey = false)
    nullVal.isTombstone shouldBe true
    nullVal.framingValid shouldBe true

    // Short frame (< 5 bytes)
    val shortBytes = Array[Byte](0x00, 0x00, 0x00)
    val shortKey = ConfluentFrame.inspect(shortBytes, isKey = true)
    shortKey.framingValid shouldBe false
    shortKey.errorCode shouldBe Some("key_frame_too_short")

    // Invalid magic byte (!= 0)
    val badMagic = Array[Byte](0x01, 0x00, 0x00, 0x00, 0x01, 0x05)
    val badMagicKey = ConfluentFrame.inspect(badMagic, isKey = true)
    badMagicKey.framingValid shouldBe false
    badMagicKey.errorCode shouldBe Some("key_invalid_magic_byte")

    // Invalid schema ID (0)
    val zeroId = Array[Byte](0x00, 0x00, 0x00, 0x00, 0x00, 0x05)
    val zeroIdVal = ConfluentFrame.inspect(zeroId, isKey = false)
    zeroIdVal.framingValid shouldBe false
    zeroIdVal.errorCode shouldBe Some("value_invalid_schema_id")

    // Valid frame (magic=0, schema_id=42)
    val validBytes = Array[Byte](0x00, 0x00, 0x00, 0x00, 0x2a, 0x01, 0x02, 0x03)
    val validVal = ConfluentFrame.inspect(validBytes, isKey = false)
    validVal.framingValid shouldBe true
    validVal.schemaId shouldBe Some(42)
    validVal.payload.get shouldBe Array[Byte](0x01, 0x02, 0x03)
  }
}
