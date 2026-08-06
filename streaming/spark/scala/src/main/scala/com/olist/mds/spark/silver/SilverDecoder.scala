package com.olist.mds.spark.silver

import com.olist.mds.spark.avro.ConfluentFrame
import com.olist.mds.spark.avro.RegistrySchemaResolver
import com.olist.mds.spark.contract.EntityContract
import com.olist.mds.spark.normalize.FatalContractFailure
import com.olist.mds.spark.normalize.SparkJobException
import org.apache.avro.Schema
import org.apache.avro.generic.GenericDatumReader
import org.apache.avro.generic.GenericRecord
import org.apache.avro.io.DecoderFactory
import org.apache.spark.sql.types._
import java.nio.ByteBuffer
import java.sql.Timestamp
import java.time.Instant
import scala.jdk.CollectionConverters._

final case class DecodedRecord(
    eventId: String,
    op: String,
    isDeleted: Boolean,
    isSnapshot: Boolean,
    sourceTsMs: Option[Long],
    sourceServerId: Option[Long],
    sourceGtid: Option[String],
    sourceBinlogFile: Option[String],
    sourceBinlogFileIndex: Option[Int],
    sourceBinlogPos: Option[Long],
    sourceRow: Option[Int],
    transactionId: Option[String],
    transactionTotalOrder: Option[Long],
    transactionDataCollectionOrder: Option[Long],
    keySchemaId: Option[Int],
    valueSchemaId: Option[Int],
    keyFingerprint: Option[String],
    valueFingerprint: Option[String],
    beforeRowHash: Option[String],
    afterRowHash: Option[String],
    rowHash: Option[String],
    businessValues: Map[String, Any],
    businessTypes: Map[String, DataType]
)

object SilverDecoder {

  def decodeRow(
      eventId: String,
      keyBytes: Array[Byte],
      valueBytes: Array[Byte],
      contract: EntityContract,
      registryResolver: Option[RegistrySchemaResolver] = None
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
    val keyWriterSchema = keyInsp.schemaId
      .flatMap(contract.allowedKeyWriterSchemas.get)
      .map(new Schema.Parser().parse)
      .getOrElse(keySchema)
    val valueWriterSchema = valInsp.schemaId match {
      case Some(schemaId) if contract.allowedValueWriterSchemas.contains(schemaId) =>
        new Schema.Parser().parse(contract.allowedValueWriterSchemas(schemaId))
      case Some(schemaId) =>
        registryResolver
          .map(_.resolveValueWriterSchema(schemaId, contract))
          .getOrElse {
            throw SparkJobException(
              "unknown_schema_id",
              s"No registry resolver is configured for value schema ID $schemaId",
              FatalContractFailure
            )
          }
      case None => valSchema
    }

    val keyRecord = decodeAvro(keyInsp.payload.get, keyWriterSchema, keySchema)
    // RegistrySchemaResolver has already enforced the compatibility policy for
    // an unapproved writer.  Reading the value with its writer schema as the
    // reader preserves newly-added nullable fields instead of silently
    // dropping them against the v2 contractual reader schema.
    val valRecord = decodeAvro(valInsp.payload.get, valueWriterSchema, valueWriterSchema)

    val opRaw = valRecord.get("op")
    val opStr = if (opRaw != null) opRaw.toString else ""
    val isDeleted = opStr == "d"
    opStr match {
      case "c" | "u" | "r" | "d" => ()
      case other =>
        throw SparkJobException(
          "corrupt_cdc_record",
          s"Unknown CDC op code '$other' for event $eventId",
          FatalContractFailure
        )
    }

    def optionalLong(value: Any): Option[Long] = value match {
      case n: Number => Some(n.longValue())
      case _ => None
    }

    def optionalInt(value: Any): Option[Int] = value match {
      case n: Number => Some(n.intValue())
      case _ => None
    }

    def optionalString(value: Any): Option[String] =
      if (value == null) None else Some(value.toString)

    val source = valRecord.get("source") match {
      case record: GenericRecord => Some(record)
      case _ => None
    }
    val sourceTsMs = source.flatMap(record => optionalLong(record.get("ts_ms")))
    val sourceServerId = source.flatMap(record => optionalLong(record.get("server_id")))
    val sourceGtid = source.flatMap(record => optionalString(record.get("gtid")))
    val sourceBinlogFile = source.flatMap(record => optionalString(record.get("file")))
    val sourceBinlogFileIndex = sourceBinlogFile.map(SourceOrdering.parseBinlogFileIndex)
    val sourceBinlogPos = source.flatMap(record => optionalLong(record.get("pos")))
    val sourceRow = source.flatMap(record => optionalInt(record.get("row")))

    val snapshot = source.flatMap(record => optionalString(record.get("snapshot")))
    val transaction = valRecord.get("transaction") match {
      case record: GenericRecord => Some(record)
      case _ => None
    }
    val transactionId = transaction.flatMap(record => optionalString(record.get("id")))
    val transactionTotalOrder =
      transaction.flatMap(record => optionalLong(record.get("total_order")))
    val transactionDataCollectionOrder =
      transaction.flatMap(record => optionalLong(record.get("data_collection_order")))

    val payloadRecord = if (isDeleted) {
      valRecord.get("before").asInstanceOf[GenericRecord]
    } else {
      valRecord.get("after").asInstanceOf[GenericRecord]
    }

    if (payloadRecord == null) {
      throw SparkJobException(
        "corrupt_cdc_record",
        s"Payload record missing for op '$opStr' in event $eventId",
        FatalContractFailure
      )
    }

    val valueSchema = valueRecordSchema(valueWriterSchema)
    val valueFields = valueSchema.getFields.asScala.map(field => field.name -> field).toMap
    val contractColumns = contract.businessColumns.map(column => column.name -> column).toMap
    val businessNames = (contract.businessColumns.map(_.name) ++ valueFields.keys).distinct
    val businessTypes = businessNames.map { name =>
      val resolvedType = contractColumns.get(name).map(_.sparkType).getOrElse {
        valueFields.get(name).map(field => toSparkType(field.schema)).getOrElse {
          throw SparkJobException(
            "incompatible_schema_evolution",
            s"Value writer field '$name' has no usable Spark type",
            FatalContractFailure
          )
        }
      }
      name -> resolvedType
    }.toMap
    val businessValues = businessTypes.map { case (name, resolvedType) =>
      val rawVal = if (contract.primaryKey.contains(name)) {
        keyRecord.get(name)
      } else {
        payloadRecord.get(name)
      }
      name -> convertValue(rawVal, resolvedType)
    }

    DecodedRecord(
      eventId = eventId,
      op = opStr,
      isDeleted = isDeleted,
      isSnapshot = snapshot.exists(value => value == "true" || value == "last"),
      sourceTsMs = sourceTsMs,
      sourceServerId = sourceServerId,
      sourceGtid = sourceGtid,
      sourceBinlogFile = sourceBinlogFile,
      sourceBinlogFileIndex = sourceBinlogFileIndex,
      sourceBinlogPos = sourceBinlogPos,
      sourceRow = sourceRow,
      transactionId = transactionId,
      transactionTotalOrder = transactionTotalOrder,
      transactionDataCollectionOrder = transactionDataCollectionOrder,
      keySchemaId = keyInsp.schemaId,
      valueSchemaId = valInsp.schemaId,
      keyFingerprint = Some(ConfluentFrame.sha256Hex(keyBytes)),
      valueFingerprint = Some(ConfluentFrame.sha256Hex(valueBytes)),
      beforeRowHash = if (isDeleted) Some(ConfluentFrame.sha256Hex(keyBytes)) else None,
      afterRowHash = if (!isDeleted) Some(ConfluentFrame.sha256Hex(valueBytes)) else None,
      rowHash = Some(ConfluentFrame.sha256Hex(valueBytes)),
      businessValues = businessValues,
      businessTypes = businessTypes
    )
  }

  private def valueRecordSchema(envelope: Schema): Schema = {
    val after = envelope.getField("after")
    if (after == null) {
      throw SparkJobException(
        "incompatible_schema_evolution",
        "Value envelope has no after field",
        FatalContractFailure
      )
    }
    after
      .schema()
      .getTypes
      .asScala
      .collectFirst {
        case schema if schema.getType == Schema.Type.RECORD && schema.getName == "Value" => schema
      }
      .getOrElse {
        throw SparkJobException(
          "incompatible_schema_evolution",
          "Value envelope after field has no named Value record",
          FatalContractFailure
        )
      }
  }

  private def toSparkType(schema: Schema): DataType = {
    val nonNull = schema.getType match {
      case Schema.Type.UNION =>
        schema.getTypes.asScala.find(_.getType != Schema.Type.NULL).getOrElse(schema)
      case _ => schema
    }
    nonNull.getType match {
      case Schema.Type.STRING | Schema.Type.ENUM => StringType
      case Schema.Type.INT => IntegerType
      case Schema.Type.LONG => LongType
      case Schema.Type.BOOLEAN => BooleanType
      case Schema.Type.FLOAT | Schema.Type.DOUBLE => DoubleType
      case Schema.Type.BYTES | Schema.Type.FIXED => BinaryType
      case Schema.Type.RECORD | Schema.Type.ARRAY | Schema.Type.MAP =>
        throw SparkJobException(
          "incompatible_schema_evolution",
          s"Unsupported nested Value field type: ${nonNull.getType}",
          FatalContractFailure
        )
      case Schema.Type.UNION =>
        throw SparkJobException(
          "incompatible_schema_evolution",
          "Nullable Value field union has no non-null branch",
          FatalContractFailure
        )
      case Schema.Type.NULL => StringType
    }
  }

  private def decodeAvro(
      payload: Array[Byte],
      writerSchema: Schema,
      readerSchema: Schema
  ): GenericRecord = {
    val reader = new GenericDatumReader[GenericRecord](writerSchema, readerSchema)
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
              val copy = bb.duplicate()
              val bytes = new Array[Byte](copy.remaining())
              copy.get(bytes)
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
