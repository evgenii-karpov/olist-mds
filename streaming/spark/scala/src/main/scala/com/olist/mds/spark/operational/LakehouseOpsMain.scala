package com.olist.mds.spark.operational

import com.olist.mds.spark.config.RuntimeConfig
import com.olist.mds.spark.config.SparkSessionFactory
import com.olist.mds.spark.silver.IcebergCommitCoordinator
import org.apache.spark.sql.Row
import org.apache.spark.sql.types._
import java.io.File
import java.nio.file.Files
import java.sql.Timestamp
import java.time.Instant

object LakehouseOpsMain {

  val MaintenanceTable = "lakehouse.audit.maintenance_runs"
  val ServingReportsTable = "lakehouse.audit.serving_sync_reports"

  val AllowedProcedures = Set(
    "rewrite_data_files",
    "rewrite_manifests",
    "expire_snapshots",
    "remove_orphan_files"
  )

  def main(args: Array[String]): Unit = {
    if (args.isEmpty) {
      println("Usage: LakehouseOpsMain <subcommand> [options]")
      return
    }

    val subcommand = args(0)
    subcommand match {
      case "record-serving-report" =>
        recordServingReport(args.tail)
      case "maintenance" =>
        runMaintenance(args.tail)
      case other =>
        println(s"Unknown subcommand '$other'")
    }
  }

  private def recordServingReport(args: Array[String]): Unit = {
    var inputFile: Option[String] = None
    var i = 0
    while (i < args.length) {
      if (args(i) == "--input-file" && i + 1 < args.length) {
        inputFile = Some(args(i + 1))
        i += 2
      } else {
        i += 1
      }
    }

    val fileStr = inputFile.getOrElse {
      println("Missing --input-file argument")
      return
    }

    val file = new File(fileStr)
    if (!file.exists()) {
      println(s"Input file $fileStr does not exist")
      return
    }

    val jsonContent = new String(Files.readAllBytes(file.toPath), "UTF-8")
    val config = RuntimeConfig.load()
    val spark = SparkSessionFactory.createSession("lakehouse-serving-report-writer", config)

    val now = Timestamp.from(Instant.now())
    val schema = StructType(
      Seq(
        StructField("report_json", StringType, nullable = false),
        StructField("recorded_at", TimestampType, nullable = false)
      )
    )

    val df = spark.createDataFrame(
      spark.sparkContext.parallelize(Seq(Row(jsonContent, now))),
      schema
    )
    df.createOrReplaceTempView("inc_report")

    val mergeSql =
      s"""
         |MERGE INTO $ServingReportsTable AS target
         |USING inc_report AS inc
         |ON target.report_json = inc.report_json
         |WHEN NOT MATCHED THEN INSERT (report_json, recorded_at) VALUES (inc.report_json, inc.recorded_at)
         |""".stripMargin

    IcebergCommitCoordinator.withLock(ServingReportsTable) {
      spark.sql(mergeSql)
    }
    println("Recorded serving sync report successfully.")
  }

  private def runMaintenance(args: Array[String]): Unit = {
    var runId: Option[String] = None
    var procedure: Option[String] = None
    var table: Option[String] = None

    var i = 0
    while (i < args.length) {
      args(i) match {
        case "--run-id" if i + 1 < args.length =>
          runId = Some(args(i + 1))
          i += 2
        case "--procedure" if i + 1 < args.length =>
          procedure = Some(args(i + 1))
          i += 2
        case "--table" if i + 1 < args.length =>
          table = Some(args(i + 1))
          i += 2
        case _ =>
          i += 1
      }
    }

    val proc = procedure.getOrElse {
      println("Missing --procedure")
      return
    }

    if (!AllowedProcedures.contains(proc)) {
      println(s"Procedure '$proc' is not in allowed list: $AllowedProcedures")
      return
    }

    val tbl = table.getOrElse {
      println("Missing --table")
      return
    }

    val config = RuntimeConfig.load()
    val spark = SparkSessionFactory.createSession("lakehouse-maintenance-executor", config)

    val procCall = s"CALL lakehouse.system.$proc(table => '$tbl')"
    println(s"Executing maintenance procedure: $procCall")

    try {
      spark.sql(procCall)
      println(s"Successfully executed $proc on $tbl.")
    } catch {
      case exc: Exception =>
        println(s"Maintenance procedure failed: ${exc.getMessage}")
    }
  }
}
