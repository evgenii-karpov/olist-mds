package com.olist.mds.spark.silver

import com.olist.mds.spark.normalize.SparkJobException
import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.matchers.should.Matchers

class SourceOrderingSpec extends AnyFunSuite with Matchers {
  test("binlog indexes require a numeric suffix") {
    SourceOrdering.parseBinlogFileIndex("mysql-bin.000007") shouldBe 7
    an[SparkJobException] should be thrownBy {
      SourceOrdering.parseBinlogFileIndex("mysql-bin")
    }
  }
}
