package com.olist.mds.spark.operational

import com.olist.mds.spark.config.RuntimeConfig
import com.olist.mds.spark.config.SparkSessionFactory
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

object GeolocationMain {
  val TargetTable = "lakehouse.reference.geolocation"
  def targetTable(catalogAlias: String): String = s"$catalogAlias.reference.geolocation"
  val DefaultSha256 = "5cf2ff7a104cae75d8a56cf8c6e00959894154a8d55aed2ddf0e3fa133a13976"

  def main(args: Array[String]): Unit = {
    val shaOpt = args.sliding(2).find(_(0) == "--source-archive-sha256").map(_(1))
    val archiveSha = shaOpt.getOrElse(DefaultSha256)
    val config = RuntimeConfig.load()
    val spark = SparkSessionFactory.createSession("geolocation-ingest", config)
    val targetTableName = targetTable(config.icebergCatalogName)

    val dbUser = config.mysqlReferenceReaderUser.getOrElse("olist_spark_reference_reader")
    val dbPass = config.mysqlReferenceReaderPassword.getOrElse("")

    val jdbcUrl =
      s"jdbc:mysql://${config.mysqlHost}:${config.mysqlPort}/${config.mysqlDatabase}?useSSL=false&allowPublicKeyRetrieval=true"

    val mysqlDf = spark.read
      .format("jdbc")
      .option("url", jdbcUrl)
      .option("dbtable", "geolocation")
      .option("user", dbUser)
      .option("password", dbPass)
      .option("driver", "com.mysql.cj.jdbc.Driver")
      .load()

    val nowTs = current_timestamp()

    val projectedDf = mysqlDf
      .select(
        col("geolocation_id").cast(LongType).as("geolocation_id"),
        col("geolocation_zip_code_prefix").cast(StringType).as("geolocation_zip_code_prefix"),
        col("geolocation_lat").cast(DecimalType(18, 14)).as("geolocation_lat"),
        col("geolocation_lng").cast(DecimalType(18, 14)).as("geolocation_lng"),
        col("geolocation_city").cast(StringType).as("geolocation_city"),
        col("geolocation_state").cast(StringType).as("geolocation_state"),
        lit(archiveSha).as("source_archive_sha256"),
        col("geolocation_id").cast(LongType).as("source_row_number"),
        nowTs.as("loaded_at")
      )
      .orderBy("geolocation_id")

    if (spark.catalog.tableExists(targetTableName)) {
      val existingCount = spark.table(targetTableName).count()
      if (existingCount > 0) {
        val sourceCount = projectedDf.count()
        if (existingCount != sourceCount) {
          throw new RuntimeException(
            s"geolocation_reference_drift: target has $existingCount rows, source has $sourceCount"
          )
        }
        println(
          s"Geolocation table $targetTableName already populated with $existingCount rows. No-op."
        )
        return
      }
    }

    projectedDf.writeTo(targetTableName).append()
    val finalCount = spark.table(targetTableName).count()
    println(s"Geolocation dataset written to $targetTableName cleanly with $finalCount rows.")
  }
}
