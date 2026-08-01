package com.olist.mds.spark.silver

import com.olist.mds.spark.avro.ConfluentFrame
import com.olist.mds.spark.contract.EntityContract
import com.olist.mds.spark.normalize.FatalContractFailure
import com.olist.mds.spark.normalize.SparkJobException
import org.apache.avro.Schema
import org.apache.avro.generic.GenericDatumReader
import org.apache.avro.generic.GenericRecord
import org.apache.avro.io.DecoderFactory
import java.nio.ByteBuffer
import java.sql.Timestamp
import java.time.Instant

final case class DecodedRecord(
    eventId: String,
    opType: String, // "upsert" or "delete"
    sourceTsMs: Option[Long],
    businessValues: Map[String, Any]
)

object SilverDecoder {

  def decodeRow(
      eventId: String,
      keyBytes: Array[Byte],
      valueBytes: Array[Byte],
      contract: EntityContract
  ): DecodedRecord = {
    val keyInsp = ConfluentFrame.inspect(keyBytes, isKey = true)
    val valInsp = ConfluentFrame.inspect(valueBytes, isKey = false)

    if (!keyInsp.framingValid || !valInsp.framingValid) {
      throw SparkJobException(
        "corrupt_cdc_record",
        s"Framing invalid for event $eventId",
        FatalContractFailure
      )
    }

    val keySchema = new Schema.Parser().parse(contract.keyReaderSchema)
    val valSchema = new Schema.Parser().parse(contract.valueReaderSchema)

    val keyRecord = decodeAvro(keyInsp.payload.get, keySchema)
    val valRecord = decodeAvro(valInsp.payload.get, valSchema)

    val opRaw = valRecord.get("op")
    val opStr = if (opRaw != null) opRaw.toString else ""
    val opType = opStr match {
      case "c" | "u" | "r" => "upsert"
      case "d" => "delete"
      case other =>
        throw SparkJobException(
          "corrupt_cdc_record",
          s"Unknown CDC op code '$other' for event $eventId",
          FatalContractFailure
        )
    }

    val sourceObj = valRecord.get("source")
    val sourceTsMs = if (sourceObj != null && sourceObj.isInstanceOf[GenericRecord]) {
      val tsMsObj = sourceObj.asInstanceOf[GenericRecord].get("ts_ms")
      if (tsMsObj != null) Some(tsMsObj.asInstanceOf[Long]) else None
    } else None

    val payloadRecord = if (opType == "delete") {
      valRecord.get("before").asInstanceOf[GenericRecord]
    } else {
      valRecord.get("after").asInstanceOf[GenericRecord]
    }

    if (payloadRecord == null) {
      throw SparkJobException(
        "corrupt_cdc_record",
        s"Payload record missing for op '$opType' in event $eventId",
        FatalContractFailure
      )
    }

    val businessValues = contract.businessColumns.map { col =>
      val rawVal = if (contract.primaryKey.contains(col.name)) {
        keyRecord.get(col.name)
      } else {
        payloadRecord.get(col.name)
      }
      col.name -> convertValue(rawVal, col.sparkType)
    }.toMap

    DecodedRecord(
      eventId = eventId,
      opType = opType,
      sourceTsMs = sourceTsMs,
      businessValues = businessValues
    )
  }

  private def decodeAvro(payload: Array[Byte], schema: Schema): GenericRecord = {
    val reader = new GenericDatumReader[GenericRecord](schema)
    val decoder = DecoderFactory.get().binaryDecoder(payload, null)
    reader.read(null, decoder)
  }

  private def convertValue(raw: Any, sparkType: org.apache.spark.sql.types.DataType): Any = {
    if (raw == null) null
    else {
      sparkType match {
        case org.apache.spark.sql.types.StringType =>
          raw.toString
        case org.apache.spark.sql.types.IntegerType =>
          raw.asInstanceOf[Number].intValue()
        case org.apache.spark.sql.types.LongType =>
          raw.asInstanceOf[Number].longValue()
        case _: org.apache.spark.sql.types.DecimalType =>
          raw match {
            case bb: ByteBuffer =>
              val bytes = new Array[Byte](bb.remaining())
              bb.get(bytes)
              new java.math.BigDecimal(new java.math.BigInteger(bytes), 2)
            case bytes: Array[Byte] =>
              new java.math.BigDecimal(new java.math.BigInteger(bytes), 2)
            case other =>
              new java.math.BigDecimal(other.toString)
          }
        case org.apache.spark.sql.types.TimestampType =>
          val micros = raw.asInstanceOf[Number].longValue()
          val millis = micros / 1000
          val nanos = (micros % 1000) * 1000
          Timestamp.from(Instant.ofEpochMilli(millis).plusNanos(nanos))
        case _ =>
          raw
      }
    }
  }
}
