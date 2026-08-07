package com.olist.mds.spark.silver

import com.olist.mds.spark.avro.ConfluentFrame
import com.olist.mds.spark.contract.ContractLoader
import org.apache.avro.Schema
import org.apache.avro.generic.{GenericDatumWriter, GenericRecord, GenericRecordBuilder}
import org.apache.avro.io.EncoderFactory
import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.matchers.should.Matchers

import java.io.ByteArrayOutputStream
import java.sql.Timestamp
import java.time.Instant
import scala.jdk.CollectionConverters._

class SourceTimestampSpec extends AnyFunSuite with Matchers {
  private def confluentFrame(schemaId: Int, record: GenericRecord, schema: Schema): Array[Byte] = {
    val payload = new ByteArrayOutputStream()
    val encoder = EncoderFactory.get().binaryEncoder(payload, null)
    new GenericDatumWriter[GenericRecord](schema).write(record, encoder)
    encoder.flush()
    val frame = new Array[Byte](ConfluentFrame.HeaderSize + payload.size())
    frame(0) = ConfluentFrame.MagicByte
    frame(1) = ((schemaId >>> 24) & 0xff).toByte
    frame(2) = ((schemaId >>> 16) & 0xff).toByte
    frame(3) = ((schemaId >>> 8) & 0xff).toByte
    frame(4) = (schemaId & 0xff).toByte
    System.arraycopy(payload.toByteArray, 0, frame, ConfluentFrame.HeaderSize, payload.size())
    frame
  }

  private def decodedPurchaseTimestamp(zone: String): Timestamp = {
    val contract = ContractLoader.loadEntityContract("orders")
    val keySchema = new Schema.Parser().parse(contract.allowedKeyWriterSchemas(11))
    val valueSchema = new Schema.Parser().parse(contract.allowedValueWriterSchemas(13))
    val key = new GenericRecordBuilder(keySchema).set("order_id", "order-1").build()

    val afterSchema = valueSchema
      .getField("after")
      .schema()
      .getTypes
      .asScala
      .find(_.getType == Schema.Type.RECORD)
      .get
    val after = new GenericRecordBuilder(afterSchema)
      .set("order_id", "order-1")
      .set("customer_id", "customer-1")
      .set("order_status", "delivered")
      .set("order_purchase_timestamp", 1577836800000000L)
      .set("order_approved_at", null)
      .set("order_delivered_carrier_date", null)
      .set("order_delivered_customer_date", null)
      .set("order_estimated_delivery_date", 1577836800000000L)
      .build()

    val sourceSchema = valueSchema.getField("source").schema()
    val source = new GenericRecordBuilder(sourceSchema)
      .set("version", "3.5.1.Final")
      .set("connector", "mysql")
      .set("name", "olist_cdc")
      .set("ts_ms", 1577836800000L)
      .set("snapshot", "last")
      .set("db", "olist")
      .set("sequence", null)
      .set("ts_us", null)
      .set("ts_ns", null)
      .set("table", "orders")
      .set("server_id", 1L)
      .set("gtid", null)
      .set("file", "mysql-bin.000007")
      .set("pos", 100L)
      .set("row", 1)
      .set("thread", null)
      .set("query", null)
      .build()

    val value = new GenericRecordBuilder(valueSchema)
      .set("before", null)
      .set("after", after)
      .set("source", source)
      .set("transaction", null)
      .set("op", "r")
      .set("ts_ms", null)
      .set("ts_us", null)
      .set("ts_ns", null)
      .build()

    val decoded = SilverDecoder.decodeRow(
      "orders:0:7",
      confluentFrame(11, key, keySchema),
      confluentFrame(13, value, valueSchema),
      contract,
      None,
      zone
    )
    decoded.businessValues("order_purchase_timestamp").asInstanceOf[Timestamp]
  }

  test("production decoder interprets a MySQL DATETIME wall clock through SOURCE_TIME_ZONE") {
    decodedPurchaseTimestamp("America/Sao_Paulo") shouldBe Timestamp.from(
      Instant.parse("2020-01-01T03:00:00Z")
    )

    decodedPurchaseTimestamp("UTC") shouldBe Timestamp.from(Instant.parse("2020-01-01T00:00:00Z"))
  }
}
