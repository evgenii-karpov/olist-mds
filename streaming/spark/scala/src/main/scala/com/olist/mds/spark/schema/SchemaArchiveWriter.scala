package com.olist.mds.spark.schema

import com.olist.mds.spark.avro.RegistrySchemaResolver
import com.olist.mds.spark.silver.IcebergCommitCoordinator
import org.apache.spark.sql.DataFrame
import org.apache.spark.sql.Row
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import java.sql.Timestamp
import java.time.Instant

object SchemaArchiveWriter {
  val SchemaTable = "lakehouse.bronze.avro_schemas"
  def schemaTable(catalogAlias: String): String = s"$catalogAlias.bronze.avro_schemas"

  def writeBatch(
      spark: SparkSession,
      batchDf: DataFrame,
      batchId: Long,
      knownValueSchemaIds: Set[Int],
      registryResolver: RegistrySchemaResolver,
      catalogAlias: String = "lakehouse"
  ): Unit = {
    val schemaRows = batchDf
      .filter(col("value_bytes").isNotNull)
      .filter(col("value_schema_id").isNotNull)
      .filter(!col("value_schema_id").isin(knownValueSchemaIds.toSeq: _*))
    if (schemaRows.isEmpty) return

    val now = Timestamp.from(Instant.now())
    val rows = schemaRows
      .select("value_schema_id", "topic")
      .distinct()
      .collect()
      .toSeq
      .map { row =>
        val schemaId = row.getAs[Int]("value_schema_id")
        val resolved = registryResolver.resolve(schemaId)
        Row(
          schemaId,
          resolved.fingerprintSha256,
          row.getAs[String]("topic"),
          1,
          resolved.schemaJson,
          resolved.referencesJson,
          resolved.selfContainedSchemaJson,
          now,
          now
        )
      }

    val schema = StructType(
      Seq(
        StructField("schema_id", IntegerType, nullable = false),
        StructField("fingerprint_sha256", StringType, nullable = false),
        StructField("subject", StringType, nullable = false),
        StructField("registry_version", IntegerType, nullable = false),
        StructField("schema_json", StringType, nullable = false),
        StructField("references_json", StringType, nullable = false),
        StructField("spark_self_contained_schema_json", StringType, nullable = false),
        StructField("first_seen_at", TimestampType, nullable = false),
        StructField("last_verified_at", TimestampType, nullable = false)
      )
    )
    val df = spark.createDataFrame(spark.sparkContext.parallelize(rows), schema)

    // Keep one durable row per registry ID.  The query checkpoint normally
    // makes this idempotent; the anti-join also protects a replay after a
    // restart or a manual checkpoint repair.
    val targetTable = schemaTable(catalogAlias)
    val existingSchemaIds = spark.table(targetTable).select("schema_id").distinct()
    val newSchemas = df
      .join(existingSchemaIds, Seq("schema_id"), "left_anti")
      .localCheckpoint(eager = true)
    IcebergCommitCoordinator.withLock(targetTable) {
      if (newSchemas.count() > 0) newSchemas.writeTo(targetTable).append()
    }
  }
}
