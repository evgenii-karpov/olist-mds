package com.olist.mds.spark.contract

import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.matchers.should.Matchers

class ContractLoaderSpec extends AnyFunSuite with Matchers {

  test("LakehouseSchemaContract checksum matches J1 expected SHA-256") {
    val checksum = LakehouseSchemaContract.calculateChecksum()
    checksum shouldBe LakehouseSchemaContract.ExpectedChecksum
  }

  test("ContractLoader loads manifest and all 8 entity contracts successfully") {
    val manifest = ContractLoader.loadManifest()
    manifest("manifest_version") shouldBe 1
    manifest("entity_count") shouldBe 8

    val contracts = ContractLoader.loadAll()
    contracts.keys should contain theSameElementsAs Seq(
      "customers",
      "orders",
      "order_items",
      "order_payments",
      "order_reviews",
      "products",
      "sellers",
      "product_category_translation"
    )

    val customers = contracts("customers")
    customers.topic shouldBe "olist_cdc.olist_oltp.customers"
    customers.primaryKey shouldBe Vector("customer_id")
    customers.allowedKeyFingerprints.nonEmpty shouldBe true
    customers.allowedValueFingerprints.nonEmpty shouldBe true
  }
}
