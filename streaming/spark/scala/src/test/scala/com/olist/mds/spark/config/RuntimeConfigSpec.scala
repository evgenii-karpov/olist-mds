package com.olist.mds.spark.config

import com.olist.mds.spark.normalize.SparkJobException
import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.matchers.should.Matchers

class RuntimeConfigSpec extends AnyFunSuite with Matchers {
  test("SOURCE_TIME_ZONE accepts IANA zones and rejects invalid zones") {
    RuntimeConfig.validateSourceTimeZone("America/Sao_Paulo") shouldBe "America/Sao_Paulo"
    RuntimeConfig.validateSourceTimeZone("UTC") shouldBe "UTC"

    an[SparkJobException] should be thrownBy {
      RuntimeConfig.validateSourceTimeZone("Not/AZone")
    }
  }
}
