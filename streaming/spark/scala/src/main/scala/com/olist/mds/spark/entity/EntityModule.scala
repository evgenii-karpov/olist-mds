package com.olist.mds.spark.entity

import com.olist.mds.spark.contract.EntityContract
import com.olist.mds.spark.normalize.FatalContractFailure
import com.olist.mds.spark.normalize.SparkJobException
import org.apache.spark.sql.Column

final case class ValidationRule(
    ordinal: Int,
    code: String,
    redactedMessage: String,
    invalidWhen: Column
)

trait EntityModule {
  def contract: EntityContract
  def validationRules(row: Column): Vector[ValidationRule]
}

object EntityRegistry {
  val allNames: Vector[String] = Vector(
    "customers",
    "orders",
    "order_items",
    "order_payments",
    "order_reviews",
    "products",
    "sellers",
    "product_category_translation"
  )

  private var registry: Map[String, EntityModule] = Map.empty

  def register(module: EntityModule): Unit = synchronized {
    registry += (module.contract.entity -> module)
  }

  def get(entity: String): Option[EntityModule] = registry.get(entity)

  def all: Vector[EntityModule] = allNames.flatMap(registry.get)

  def validateCompleteness(): Unit = synchronized {
    val missing = allNames.filterNot(registry.contains)
    if (missing.nonEmpty || registry.size != 8) {
      throw SparkJobException(
        "contract_resource_mismatch",
        s"EntityRegistry mismatch. Missing or extra modules: missing=${missing.mkString(",")}, size=${registry.size}",
        FatalContractFailure
      )
    }
  }
}
