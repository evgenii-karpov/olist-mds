package com.olist.mds.spark.normalize

sealed trait BatchMode
case object StreamingBatch extends BatchMode
case object FiniteReplay extends BatchMode

final case class BatchContext(
    queryName: String,
    entity: String,
    contractVersion: Int,
    sparkQueryId: String,
    sparkBatchId: Long,
    mode: BatchMode
)

sealed trait FailureClass
case object TransientFailure extends FailureClass
case object PermanentRecordFailure extends FailureClass
case object FatalContractFailure extends FailureClass

final case class SparkJobException(
    code: String,
    message: String,
    failureClass: FailureClass,
    cause: Throwable = null
) extends Exception(s"[$code] $message", cause)
