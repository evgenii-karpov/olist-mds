package com.olist.mds.spark.contract

import com.olist.mds.spark.normalize.FatalContractFailure
import com.olist.mds.spark.normalize.SparkJobException
import org.apache.spark.sql.SparkSession

object LakehouseContractValidator {
  def validate(spark: SparkSession, catalogName: String = "lakehouse"): Unit = {
    LakehouseSchemaContract.validateChecksum()

    LakehouseSchemaContract.AllTables.foreach { spec =>
      val qualifiedName = s"$catalogName.${spec.namespace}.${spec.name}"
      if (!spark.catalog.tableExists(qualifiedName)) {
        throw SparkJobException(
          "contract_resource_mismatch",
          s"Required Iceberg table missing in catalog: $qualifiedName",
          FatalContractFailure
        )
      }

      val existingSchema = spark.table(qualifiedName).schema
      val expectedSchema = spec.schema

      if (existingSchema.fields.length != expectedSchema.fields.length) {
        throw SparkJobException(
          "contract_resource_mismatch",
          s"Table schema field count mismatch for $qualifiedName: expected ${expectedSchema.fields.length}, got ${existingSchema.fields.length}",
          FatalContractFailure
        )
      }

      existingSchema.fields.zip(expectedSchema.fields).foreach { case (act, exp) =>
        if (act.name != exp.name || act.dataType != exp.dataType) {
          throw SparkJobException(
            "contract_resource_mismatch",
            s"Table field drift for $qualifiedName.${act.name}: expected ${exp.dataType}, got ${act.dataType}",
            FatalContractFailure
          )
        }
      }
    }
  }
}
