package com.olist.mds.spark.transaction

import com.olist.mds.spark.avro.ConfluentFrame
import com.olist.mds.spark.normalize.FatalContractFailure
import com.olist.mds.spark.normalize.SparkJobException
import com.olist.mds.spark.silver.IcebergCommitCoordinator
import com.olist.mds.spark.silver.SilverProgressRecord
import com.olist.mds.spark.silver.SilverProgressWriter
import org.apache.avro.Schema
import org.apache.avro.generic.GenericDatumReader
import org.apache.avro.generic.GenericRecord
import org.apache.avro.io.DecoderFactory
import org.apache.spark.sql.DataFrame
import org.apache.spark.sql.Row
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import java.sql.Timestamp
import java.time.Instant
import scala.jdk.CollectionConverters._

object TransactionBatchWriter {
  val TxTable = "lakehouse.audit.mysql_transactions"

  private val KeySchema = new Schema.Parser().parse(
    """{"type":"record","name":"TransactionMetadataKey","namespace":"io.debezium.connector.common","fields":[{"name":"id","type":"string"}]}"""
  )
  private val ValueSchema = new Schema.Parser().parse(
    """{"type":"record","name":"TransactionMetadataValue","namespace":"io.debezium.connector.common","fields":[{"name":"status","type":"string"},{"name":"id","type":"string"},{"name":"event_count","type":["null","long"],"default":null},{"name":"data_collections","type":["null",{"type":"array","items":["null",{"type":"record","name":"collection","namespace":"event","fields":[{"name":"data_collection","type":"string"},{"name":"event_count","type":"long"}]}]}],"default":null},{"name":"ts_ms","type":"long"}]}"""
  )

  private final case class TransactionEvent(
      transactionId: String,
      status: String,
      eventCount: Option[Long],
      dataCollections: Option[Seq[Row]],
      eventId: String,
      kafkaTopic: String,
      kafkaPartition: Int,
      kafkaOffset: Long,
      kafkaTimestamp: Timestamp,
      sourceTimestamp: Timestamp
  )

  private def optionalLong(value: Any): Option[Long] = value match {
    case n: Number => Some(n.longValue())
    case _ => None
  }

  private def decodeRecord(payload: Array[Byte], schema: Schema): GenericRecord = {
    val reader = new GenericDatumReader[GenericRecord](schema)
    reader.read(null, DecoderFactory.get().binaryDecoder(payload, null))
  }

  private def decodeEvent(row: Row): TransactionEvent = {
    val eventId = row.getAs[String]("event_id")
    val keyInspection = ConfluentFrame.inspect(row.getAs[Array[Byte]]("key_bytes"), isKey = true)
    val valueInspection =
      ConfluentFrame.inspect(row.getAs[Array[Byte]]("value_bytes"), isKey = false)
    if (
      !keyInspection.framingValid || !valueInspection.framingValid ||
      keyInspection.payload.isEmpty || valueInspection.payload.isEmpty
    ) {
      throw SparkJobException(
        "corrupt_transaction_record",
        s"Invalid transaction framing for event $eventId",
        FatalContractFailure
      )
    }

    val keyRecord = decodeRecord(keyInspection.payload.get, KeySchema)
    val valueRecord = decodeRecord(valueInspection.payload.get, ValueSchema)
    val txId = Option(keyRecord.get("id")).map(_.toString).getOrElse {
      throw SparkJobException(
        "corrupt_transaction_record",
        s"Transaction key is missing for event $eventId",
        FatalContractFailure
      )
    }
    val status = Option(valueRecord.get("status")).map(_.toString).getOrElse("") match {
      case "BEGIN" => "OPEN"
      case "END" => "COMPLETE"
      case other =>
        throw SparkJobException(
          "corrupt_transaction_record",
          s"Unknown transaction status '$other' for event $eventId",
          FatalContractFailure
        )
    }
    val eventCount = optionalLong(valueRecord.get("event_count"))
    val collections = valueRecord.get("data_collections") match {
      case values: java.util.Collection[?] =>
        Some(
          values.asScala.toSeq.collect { case record: GenericRecord =>
            Row(
              record.get("data_collection").toString,
              optionalLong(record.get("event_count")).orNull
            )
          }
        )
      case _ => None
    }
    val kafkaTimestamp = row.getAs[Timestamp]("kafka_timestamp")
    val tsMs = optionalLong(valueRecord.get("ts_ms"))
    TransactionEvent(
      transactionId = txId,
      status = status,
      eventCount = eventCount,
      dataCollections = collections,
      eventId = eventId,
      kafkaTopic = row.getAs[String]("topic"),
      kafkaPartition = row.getAs[Int]("partition"),
      kafkaOffset = row.getAs[Long]("offset"),
      kafkaTimestamp = kafkaTimestamp,
      sourceTimestamp =
        tsMs.map(value => Timestamp.from(Instant.ofEpochMilli(value))).getOrElse(kafkaTimestamp)
    )
  }

  def writeBatch(
      spark: SparkSession,
      batchDf: DataFrame,
      batchId: Long,
      sparkQueryId: String = "silver-transaction-replay"
  ): Unit = {
    val txRows = batchDf
      .filter(col("topic").isin("olist_cdc.transaction", "transaction"))
      .filter(col("value_bytes").isNotNull)
    if (txRows.isEmpty) return

    val events = txRows.collect().toSeq.sortBy(_.getAs[Long]("offset")).map(decodeEvent)
    val grouped = events.groupBy(_.transactionId).values.toSeq
    if (grouped.isEmpty) return

    val dataCollectionType = ArrayType(
      StructType(
        Seq(
          StructField("data_collection", StringType, nullable = true),
          StructField("event_count", LongType, nullable = true)
        )
      ),
      containsNull = true
    )
    val schema = StructType(
      Seq(
        StructField("transaction_id", StringType, nullable = false),
        StructField("status", StringType, nullable = false),
        StructField("event_count", LongType, nullable = true),
        StructField("data_collections", dataCollectionType, nullable = true),
        StructField("begin_event_id", StringType, nullable = true),
        StructField("end_event_id", StringType, nullable = true),
        StructField("kafka_topic", StringType, nullable = false),
        StructField("kafka_partition", IntegerType, nullable = false),
        StructField("begin_kafka_offset", LongType, nullable = true),
        StructField("end_kafka_offset", LongType, nullable = true),
        StructField("source_ts", TimestampType, nullable = true),
        StructField("first_seen_at", TimestampType, nullable = false),
        StructField("completed_at", TimestampType, nullable = true),
        StructField(
          "rejected_event_ids",
          ArrayType(StringType, containsNull = true),
          nullable = true
        ),
        StructField("recorded_at", TimestampType, nullable = false)
      )
    )

    val now = Timestamp.from(Instant.now())
    val progressRecords = scala.collection.mutable.ArrayBuffer[SilverProgressRecord]()

    grouped.foreach { transactionEvents =>
      val ordered = transactionEvents.sortBy(_.kafkaOffset)
      val first = ordered.head
      val begin = ordered.find(_.status == "OPEN")
      val end = ordered.reverse.find(_.status == "COMPLETE")
      val status = if (end.nonEmpty) "COMPLETE" else "OPEN"
      val eventCount =
        end.flatMap(_.eventCount).orElse(if (end.nonEmpty) Some(ordered.size.toLong) else None)
      val dataCollections = end.flatMap(_.dataCollections).orElse(begin.flatMap(_.dataCollections))
      val values = Seq[Any](
        first.transactionId,
        status,
        eventCount.map(Long.box).orNull,
        dataCollections.map(_.toArray).orNull,
        begin.map(_.eventId).orNull,
        end.map(_.eventId).orNull,
        first.kafkaTopic,
        first.kafkaPartition,
        begin.map(_.kafkaOffset).map(Long.box).orNull,
        end.map(_.kafkaOffset).map(Long.box).orNull,
        end.map(_.sourceTimestamp).orElse(begin.map(_.sourceTimestamp)).orNull,
        now,
        end.map(_ => now).orNull,
        Array.empty[String],
        now
      )
      val rowDf = spark.createDataFrame(
        spark.sparkContext.parallelize(Seq(Row.fromSeq(values))),
        schema
      )
      IcebergCommitCoordinator.withLock(TxTable) {
        rowDf.writeTo(TxTable).append()
      }

      val last = ordered.last
      progressRecords += SilverProgressRecord(
        queryName = "normalize_mysql_transactions",
        entity = "__transactions__",
        contractVersion = 2,
        sourceTopic = last.kafkaTopic,
        kafkaPartition = last.kafkaPartition,
        lastKafkaOffset = last.kafkaOffset,
        lastEventId = last.eventId,
        lastSourceTs = Some(last.sourceTimestamp),
        sparkQueryId = sparkQueryId,
        sparkBatchId = batchId,
        changesSnapshotId = SilverProgressWriter.getLatestSnapshotId(spark, TxTable),
        currentSnapshotId = None,
        status = "COMMITTED",
        errorClass = None
      )
    }

    SilverProgressWriter.writeProgress(spark, progressRecords.toSeq)
  }
}
