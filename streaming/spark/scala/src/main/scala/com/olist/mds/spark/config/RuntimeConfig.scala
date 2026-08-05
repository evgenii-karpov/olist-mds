package com.olist.mds.spark.config

import com.olist.mds.spark.normalize.FatalContractFailure
import com.olist.mds.spark.normalize.SparkJobException
import java.nio.file.Files
import java.nio.file.Paths

final case class RuntimeConfig(
    mysqlHost: String,
    mysqlPort: Int,
    mysqlDatabase: String,
    kafkaBootstrapServers: String,
    apicurioRegistryUrl: String,
    apicurioCcompatUrl: String,
    icebergCatalogUri: String,
    icebergCatalogName: String,
    icebergWarehouse: String,
    objectStoreEndpoint: String,
    objectStoreRegion: String,
    objectStorePathStyle: Boolean,
    sparkCheckpointRoot: String,
    sparkContractVersion: Int,
    sparkStatusDir: String,
    sparkRuntimeMode: String,
    mysqlReferenceReaderUser: Option[String],
    mysqlReferenceReaderPassword: Option[String]
)

object RuntimeConfig {
  private def getEnvOrSecret(envName: String): Option[String] = {
    val fileEnv = envName + "_FILE"
    sys.env.get(fileEnv) match {
      case Some(filePath) if filePath.nonEmpty =>
        val path = Paths.get(filePath)
        if (Files.exists(path)) {
          val content = new String(Files.readAllBytes(path), "UTF-8").stripLineEnd
          if (content.contains("\n") || content.contains("\r")) {
            throw SparkJobException(
              "contract_resource_mismatch",
              s"Secret file for $envName contains multiple lines",
              FatalContractFailure
            )
          }
          Some(content)
        } else {
          throw SparkJobException(
            "contract_resource_mismatch",
            s"Secret file for $envName does not exist: $filePath",
            FatalContractFailure
          )
        }
      case _ =>
        sys.env.get(envName).filter(_.nonEmpty)
    }
  }

  def load(): RuntimeConfig = {
    val mode = sys.env.getOrElse("SPARK_RUNTIME_MODE", "local")
    if (mode != "local" && mode != "integration-test") {
      throw SparkJobException(
        "contract_resource_mismatch",
        s"Invalid SPARK_RUNTIME_MODE: $mode",
        FatalContractFailure
      )
    }

    val contractVersionStr = sys.env.getOrElse("SPARK_CONTRACT_VERSION", "2")
    val contractVersion = try {
      contractVersionStr.toInt
    } catch {
      case _: Exception =>
        throw SparkJobException(
          "contract_resource_mismatch",
          s"Invalid SPARK_CONTRACT_VERSION: $contractVersionStr",
          FatalContractFailure
        )
    }

    if (contractVersion != 2) {
      throw SparkJobException(
        "contract_resource_mismatch",
        s"Unsupported contract version: $contractVersion",
        FatalContractFailure
      )
    }

    // Check for unsafe test hooks in local mode
    if (mode == "local") {
      val hasTestHooks = sys.env.get("SPARK_TEST_HOOKS_ENABLED").contains("true") ||
        sys.env.get("SPARK_TEST_FORCE_REJECT_EVENT_ID").exists(_.nonEmpty)
      if (hasTestHooks) {
        throw SparkJobException(
          "contract_resource_mismatch",
          "Test hooks are strictly forbidden in SPARK_RUNTIME_MODE=local",
          FatalContractFailure
        )
      }
    }

    RuntimeConfig(
      mysqlHost = sys.env.getOrElse("MYSQL_HOST", "mysql"),
      mysqlPort =
        sys.env.get("MYSQL_PORT").flatMap(s => scala.util.Try(s.toInt).toOption).getOrElse(3306),
      mysqlDatabase = sys.env.getOrElse("MYSQL_DATABASE", "olist_oltp"),
      kafkaBootstrapServers = sys.env.getOrElse("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092"),
      apicurioRegistryUrl = sys.env
        .getOrElse("APICURIO_REGISTRY_URL", "http://apicurio-registry:8080/apis/registry/v2"),
      apicurioCcompatUrl =
        sys.env.getOrElse("APICURIO_CCOMPAT_URL", "http://apicurio-registry:8080/apis/ccompat/v7"),
      icebergCatalogUri =
        sys.env.getOrElse("ICEBERG_CATALOG_URI", "http://polaris:8181/api/catalog"),
      icebergCatalogName = sys.env.getOrElse("ICEBERG_CATALOG_NAME", "lakehouse"),
      icebergWarehouse = sys.env.getOrElse("ICEBERG_WAREHOUSE", "olist_lakehouse"),
      objectStoreEndpoint = sys.env.getOrElse("OBJECT_STORE_ENDPOINT", "http://minio:9000"),
      objectStoreRegion = sys.env.getOrElse("OBJECT_STORE_REGION", "us-east-1"),
      objectStorePathStyle = sys.env.getOrElse("OBJECT_STORE_PATH_STYLE", "true").toBoolean,
      sparkCheckpointRoot = sys.env.getOrElse("SPARK_CHECKPOINT_ROOT", "s3a://olist-checkpoints"),
      sparkContractVersion = contractVersion,
      sparkStatusDir = sys.env.getOrElse("SPARK_STATUS_DIR", "/var/run/olist-spark"),
      sparkRuntimeMode = mode,
      mysqlReferenceReaderUser = getEnvOrSecret("MYSQL_REFERENCE_READER_USERNAME"),
      mysqlReferenceReaderPassword = getEnvOrSecret("MYSQL_REFERENCE_READER_PASSWORD")
    )
  }
}
