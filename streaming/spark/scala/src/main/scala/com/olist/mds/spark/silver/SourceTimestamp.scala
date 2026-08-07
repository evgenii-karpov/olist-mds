package com.olist.mds.spark.silver

import java.time.{Instant, LocalDateTime, ZoneId, ZoneOffset}

/** Timestamp conversions used by the production Silver decoder. */
object SourceTimestamp {
  val DefaultSourceTimeZone = "America/Sao_Paulo"

  /** Interpret Avro timestamp-micros representing a MySQL DATETIME wall clock as local fields in
    * `sourceTimeZone`, then return the UTC instant.
    *
    * The intermediate UTC projection preserves the wall-clock fields carried by the timezone-less
    * MySQL value. It must not be used for Debezium `source.ts_ms`, Kafka timestamps, or ingestion
    * time, which are instants.
    */
  def normalizeWallClockMicros(micros: Long, sourceTimeZone: ZoneId): Instant = {
    val epochSecond = Math.floorDiv(micros, 1000000L)
    val microsWithinSecond = Math.floorMod(micros, 1000000L)
    val wallClock = LocalDateTime.ofEpochSecond(
      epochSecond,
      microsWithinSecond.toInt * 1000,
      ZoneOffset.UTC
    )
    wallClock.atZone(sourceTimeZone).toInstant
  }

  def instantFromMicros(micros: Long): Instant = {
    val epochSecond = Math.floorDiv(micros, 1000000L)
    val microsWithinSecond = Math.floorMod(micros, 1000000L)
    Instant.ofEpochSecond(epochSecond, microsWithinSecond.toLong * 1000L)
  }
}
