package com.olist.mds.spark.transaction

/** Immutable transaction observations and effective-state reduction helpers. */
final case class TransactionObservation(
    transactionId: String,
    status: String,
    kafkaOffset: Long,
    recordedAtEpochMillis: Long,
    eventId: String
)

object TransactionState {
  private val statusRank: Map[String, Int] =
    Map("OPEN" -> 0, "REJECTED" -> 1, "COMPLETE" -> 2)

  private def order(observation: TransactionObservation): (Long, Long, Int, String) =
    (
      observation.kafkaOffset,
      observation.recordedAtEpochMillis,
      statusRank.getOrElse(observation.status, -1),
      observation.eventId
    )

  /** Keep one effective observation per transaction while preserving order. */
  def collapse(observations: Seq[TransactionObservation]): Seq[TransactionObservation] =
    observations
      .groupBy(_.transactionId)
      .values
      .map(_.maxBy(order))
      .toSeq
      .sortBy(observation =>
        (observation.kafkaOffset, observation.recordedAtEpochMillis, observation.transactionId)
      )
}
