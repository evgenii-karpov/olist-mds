package com.olist.mds.spark.contract

import org.apache.spark.sql.types.DataType

final case class BusinessColumn(
    name: String,
    sparkType: DataType,
    nullable: Boolean,
    primaryKeyOrdinal: Option[Int],
    sourceWallClock: Boolean = false
)

final case class EntityContract(
    entity: String,
    topic: String,
    topicPartitions: Int,
    primaryKey: Vector[String],
    businessColumns: Vector[BusinessColumn],
    keyReaderSchema: String,
    valueReaderSchema: String,
    allowedKeyFingerprints: Set[String],
    allowedValueFingerprints: Set[String],
    allowedKeySchemaIds: Set[Int],
    allowedValueSchemaIds: Set[Int],
    allowedKeyWriterSchemas: Map[Int, String],
    allowedValueWriterSchemas: Map[Int, String],
    allowedKeySchemaFingerprints: Map[Int, String] = Map.empty,
    allowedValueSchemaFingerprints: Map[Int, String] = Map.empty
) {
  def toChangesSparkSchema: org.apache.spark.sql.types.StructType = {
    import org.apache.spark.sql.types._
    val fields = Vector(
      StructField("event_id", StringType, nullable = false),
      StructField("op_type", StringType, nullable = false),
      StructField("source_ts_ms", LongType, nullable = true),
      StructField("kafka_timestamp", TimestampType, nullable = false)
    ) ++ businessColumns.map(c => StructField(c.name, c.sparkType, c.nullable))
    StructType(fields)
  }
}
