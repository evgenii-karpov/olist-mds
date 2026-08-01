package com.olist.mds.spark.operational

import com.olist.mds.spark.config.RuntimeConfig
import com.olist.mds.spark.config.SparkSessionFactory
import com.olist.mds.spark.contract.ContractLoader
import com.olist.mds.spark.silver.SilverBatchWriter
import org.apache.spark.sql.functions._

object ReplayMain {

  def main(args: Array[String]): Unit = {
    val entityOpt = args.sliding(2).find(_(0) == "--entity").map(_(1))
    val fromTsOpt = args.sliding(2).find(_(0) == "--from-timestamp").map(_(1))
    val toTsOpt = args.sliding(2).find(_(0) == "--to-timestamp").map(_(1))
    val executeFlag = args.contains("--execute")

    if (entityOpt.isEmpty) {
      println(
        "Usage: ReplayMain --entity <entity> [--from-timestamp ISO] [--to-timestamp ISO] [--execute]"
      )
      return
    }

    val entity = entityOpt.get
    val config = RuntimeConfig.load()
    val contracts = ContractLoader.loadAll()

    if (!contracts.contains(entity)) {
      throw new IllegalArgumentException(s"Unknown entity: $entity")
    }

    val contract = contracts(entity)
    val spark = SparkSessionFactory.createSession(s"replay-$entity", config)

    val bronzeDf = spark
      .table("lakehouse.bronze.mysql_cdc_records")
      .filter(col("topic") === contract.topic)

    val filteredDf = (fromTsOpt, toTsOpt) match {
      case (Some(f), Some(t)) =>
        bronzeDf.filter(col("kafka_timestamp") >= f && col("kafka_timestamp") <= t)
      case (Some(f), None) =>
        bronzeDf.filter(col("kafka_timestamp") >= f)
      case (None, Some(t)) =>
        bronzeDf.filter(col("kafka_timestamp") <= t)
      case (None, None) =>
        bronzeDf
    }

    val count = filteredDf.count()
    println(s"Replay target entity '$entity': $count records selected from bronze.")

    if (executeFlag && count > 0) {
      println(s"Executing replay for $entity...")
      SilverBatchWriter.writeBatch(spark, filteredDf, contract, batchId = -1L)
      println(s"Replay completed for $entity.")
    } else if (!executeFlag) {
      println("Dry-run mode. Pass --execute to run re-ingestion.")
    }
  }
}
