package com.olist.mds.spark.config

import org.apache.spark.sql.SparkSession

object SparkSessionFactory {
  def createSession(appName: String, config: RuntimeConfig): SparkSession = {
    val catalogPrefix = s"spark.sql.catalog.${config.icebergCatalogName}"
    val builder = SparkSession
      .builder()
      .appName(appName)
      .config(
        "spark.sql.extensions",
        "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"
      )
      .config("spark.sql.defaultCatalog", config.icebergCatalogName)
      .config(catalogPrefix, "org.apache.iceberg.spark.SparkCatalog")
      .config(s"$catalogPrefix.type", "rest")
      .config(s"$catalogPrefix.uri", config.icebergCatalogUri)
      .config(s"$catalogPrefix.warehouse", config.icebergWarehouse)
      .config(
        s"$catalogPrefix.header.X-Iceberg-Access-Delegation",
        "vended-credentials"
      )
      .config(s"$catalogPrefix.io-impl", config.icebergFileIo)
      .config("spark.sql.session.timeZone", "UTC")
      .config("spark.sql.shuffle.partitions", "4")

    config.icebergRestAuthType.foreach { authType =>
      builder.config(s"$catalogPrefix.rest.auth.type", authType)
    }
    config.gcpProjectId.foreach { projectId =>
      builder.config(s"$catalogPrefix.header.x-goog-user-project", projectId)
    }

    if (config.sparkBackend == "gcp") {
      builder
        .config(
          "spark.hadoop.fs.gs.impl",
          "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem"
        )
        .config(
          "spark.hadoop.fs.AbstractFileSystem.gs.impl",
          "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS"
        )
        .config("spark.hadoop.fs.gs.auth.type", "APPLICATION_DEFAULT")
        .config("spark.hadoop.fs.gs.client.type", "HTTP_API_CLIENT")
        .config("spark.hadoop.fs.gs.project.id", config.gcpProjectId.get)
    } else {
      builder
        .config("spark.hadoop.fs.s3a.endpoint", config.objectStoreEndpoint)
        .config("spark.hadoop.fs.s3a.path.style.access", config.objectStorePathStyle.toString)
        .config("spark.hadoop.fs.s3a.change.detection.mode", "none")
    }

    builder.getOrCreate()
  }
}
