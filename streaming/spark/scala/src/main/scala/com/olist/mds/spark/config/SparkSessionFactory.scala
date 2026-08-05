package com.olist.mds.spark.config

import org.apache.spark.sql.SparkSession

object SparkSessionFactory {
  def createSession(appName: String, config: RuntimeConfig): SparkSession = {
    val builder = SparkSession
      .builder()
      .appName(appName)
      .config(
        "spark.sql.extensions",
        "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"
      )
      .config(
        s"spark.sql.catalog.${config.icebergCatalogName}",
        "org.apache.iceberg.spark.SparkCatalog"
      )
      .config(s"spark.sql.catalog.${config.icebergCatalogName}.type", "rest")
      .config(s"spark.sql.catalog.${config.icebergCatalogName}.uri", config.icebergCatalogUri)
      .config(s"spark.sql.catalog.${config.icebergCatalogName}.warehouse", config.icebergWarehouse)
      .config(
        s"spark.sql.catalog.${config.icebergCatalogName}.oauth2-server-uri",
        s"${config.icebergCatalogUri}/v1/oauth/tokens"
      )
      .config(
        s"spark.sql.catalog.${config.icebergCatalogName}.header.X-Iceberg-Access-Delegation",
        "vended-credentials"
      )
      .config(s"spark.sql.catalog.${config.icebergCatalogName}.token-refresh-enabled", "false")
      .config(
        s"spark.sql.catalog.${config.icebergCatalogName}.io-impl",
        "org.apache.iceberg.aws.s3.S3FileIO"
      )
      .config("spark.sql.session.timeZone", "UTC")
      .config("spark.sql.shuffle.partitions", "4")

    // Additional AWS/S3A configs for MinIO if needed
    builder
      .config("spark.hadoop.fs.s3a.endpoint", config.objectStoreEndpoint)
      .config("spark.hadoop.fs.s3a.path.style.access", config.objectStorePathStyle.toString)
      .config("spark.hadoop.fs.s3a.change.detection.mode", "none")
      .getOrCreate()
  }
}
