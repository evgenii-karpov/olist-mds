package com.olist.mds.spark.avro

final case class ConfluentFrame(
    schemaId: Int,
    payload: Array[Byte]
)

final case class FrameInspection(
    isTombstone: Boolean,
    framingValid: Boolean,
    schemaId: Option[Int],
    payload: Option[Array[Byte]],
    errorCode: Option[String]
)

object ConfluentFrame {
  val MagicByte: Byte = 0
  val HeaderSize: Int = 5

  def inspect(bytes: Array[Byte], isKey: Boolean): FrameInspection = {
    if (bytes == null) {
      FrameInspection(
        isTombstone = !isKey,
        framingValid = true,
        schemaId = None,
        payload = None,
        errorCode = None
      )
    } else if (bytes.length < HeaderSize) {
      val code = if (isKey) "key_frame_too_short" else "value_frame_too_short"
      FrameInspection(
        isTombstone = false,
        framingValid = false,
        schemaId = None,
        payload = None,
        errorCode = Some(code)
      )
    } else if (bytes(0) != MagicByte) {
      val code = if (isKey) "key_invalid_magic_byte" else "value_invalid_magic_byte"
      FrameInspection(
        isTombstone = false,
        framingValid = false,
        schemaId = None,
        payload = None,
        errorCode = Some(code)
      )
    } else {
      val rawId = ((bytes(1).toInt & 0xff) << 24) |
        ((bytes(2).toInt & 0xff) << 16) |
        ((bytes(3).toInt & 0xff) << 8) |
        (bytes(4).toInt & 0xff)

      if (rawId <= 0 || (rawId & 0x80000000) != 0) {
        val code = if (isKey) "key_invalid_schema_id" else "value_invalid_schema_id"
        FrameInspection(
          isTombstone = false,
          framingValid = false,
          schemaId = None,
          payload = None,
          errorCode = Some(code)
        )
      } else {
        val payloadBytes = java.util.Arrays.copyOfRange(bytes, HeaderSize, bytes.length)
        FrameInspection(
          isTombstone = false,
          framingValid = true,
          schemaId = Some(rawId),
          payload = Some(payloadBytes),
          errorCode = None
        )
      }
    }
  }
}
