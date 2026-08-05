package com.olist.mds.spark.silver

import com.olist.mds.spark.contract.ContractLoader
import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.matchers.should.Matchers

class SilverSpec extends AnyFunSuite with Matchers {

  test("ContractLoader loads contracts for Silver engine") {
    val contracts = ContractLoader.loadAll()
    contracts.size shouldBe 8
    contracts.keySet should contain("customers")

    val cust = contracts("customers")
    cust.primaryKey shouldBe Vector("customer_id")
    cust.businessColumns.map(_.name) should contain("customer_state")
  }
}
