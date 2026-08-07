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
    icebergFileIo: String,
    icebergRestAuthType: Option[String],
    gcpProjectId: Option[String],
    objectStoreEndpoint: String,
    objectStoreRegion: String,
    objectStorePathStyle: Boolean,
    sparkCheckpointRoot: String,
    sparkContractVersion: Int,
    sparkStatusDir: String,
    sparkRuntimeMode: String,
    sparkBackend: String,
    googleApplicationCredentials: Option[String],
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
    if (mode != "local" && mode != "integration-test" && mode != "gcp") {
      throw SparkJobException(
        "contract_resource_mismatch",
        s"Invalid SPARK_RUNTIME_MODE: $mode",
        FatalContractFailure
      )
    }

    val backend = sys.env
      .get("SPARK_BACKEND")
      .orElse(sys.env.get("SPARK_CONTOUR"))
      .getOrElse(if (mode == "gcp") "gcp" else "local")
    if (backend != "local" && backend != "gcp") {
      throw SparkJobException(
        "contract_resource_mismatch",
        s"Invalid SPARK_BACKEND: $backend",
        FatalContractFailure
      )
    }
    if (mode == "gcp" && backend != "gcp") {
      throw SparkJobException(
        "contract_resource_mismatch",
        "SPARK_RUNTIME_MODE=gcp requires SPARK_BACKEND=gcp",
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

    val catalogAlias = sys.env
      .get("ICEBERG_SPARK_CATALOG_ALIAS")
      .orElse(sys.env.get("ICEBERG_CATALOG_NAME"))
      .getOrElse("lakehouse")
    if (!catalogAlias.matches("[A-Za-z][A-Za-z0-9_]*")) {
      throw SparkJobException(
        "contract_resource_mismatch",
        s"Invalid Iceberg catalog alias: $catalogAlias",
        FatalContractFailure
      )
    }

    val defaultCatalogUri =
      if (backend == "gcp") "https://biglake.googleapis.com/iceberg/v1/restcatalog"
      else "http://polaris:8181/api/catalog"
    val catalogUri = sys.env.getOrElse("ICEBERG_CATALOG_URI", defaultCatalogUri)
    val warehouse = sys.env
      .get("ICEBERG_WAREHOUSE")
      .orElse(if (backend == "local") Some("olist_lakehouse") else None)
      .getOrElse {
        throw SparkJobException(
          "contract_resource_mismatch",
          "ICEBERG_WAREHOUSE is required for the GCP backend",
          FatalContractFailure
        )
      }
    val gcpProjectId = sys.env
      .get("GCP_LAKEHOUSE_PROJECT_ID")
      .orElse(sys.env.get("GCP_PROJECT_ID"))
      .orElse(sys.env.get("GOOGLE_CLOUD_PROJECT"))
      .filter(_.matches("[a-z][a-z0-9-]{4,28}[a-z0-9]"))
    if (backend == "gcp" && gcpProjectId.isEmpty) {
      throw SparkJobException(
        "contract_resource_mismatch",
        "GCP_LAKEHOUSE_PROJECT_ID is required for the GCP backend",
        FatalContractFailure
      )
    }

    val checkpointRoot = sys.env.getOrElse(
      "SPARK_CHECKPOINT_ROOT",
      if (backend == "gcp") "" else "s3a://olist-checkpoints"
    )
    if (backend == "gcp" && !checkpointRoot.startsWith("gs://")) {
      throw SparkJobException(
        "contract_resource_mismatch",
        "GCP SPARK_CHECKPOINT_ROOT must use gs://",
        FatalContractFailure
      )
    }
    val adcPath = sys.env.get("GOOGLE_APPLICATION_CREDENTIALS").filter(_.nonEmpty)
    if (backend == "gcp" && adcPath.forall(path => !Files.isRegularFile(Paths.get(path)))) {
      throw SparkJobException(
        "contract_resource_mismatch",
        "GCP backend requires a mounted GOOGLE_APPLICATION_CREDENTIALS file",
        FatalContractFailure
      )
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
      icebergCatalogUri = catalogUri,
      icebergCatalogName = catalogAlias,
      icebergWarehouse = warehouse,
      icebergFileIo =
        if (backend == "gcp") "org.apache.iceberg.gcp.gcs.GCSFileIO"
        else "org.apache.iceberg.aws.s3.S3FileIO",
      icebergRestAuthType =
        if (backend == "gcp") Some("org.apache.iceberg.gcp.auth.GoogleAuthManager")
        else None,
      gcpProjectId = gcpProjectId,
      objectStoreEndpoint = sys.env.getOrElse("OBJECT_STORE_ENDPOINT", "http://minio:9000"),
      objectStoreRegion = sys.env.getOrElse(
        "OBJECT_STORE_REGION",
        if (backend == "gcp") "us-east1" else "us-east-1"
      ),
      objectStorePathStyle = sys.env
        .getOrElse("OBJECT_STORE_PATH_STYLE", if (backend == "gcp") "false" else "true")
        .toBoolean,
      sparkCheckpointRoot = checkpointRoot,
      sparkContractVersion = contractVersion,
      sparkStatusDir = sys.env.getOrElse("SPARK_STATUS_DIR", "/var/run/olist-spark"),
      sparkRuntimeMode = mode,
      sparkBackend = backend,
      googleApplicationCredentials = adcPath,
      mysqlReferenceReaderUser = getEnvOrSecret("MYSQL_REFERENCE_READER_USERNAME"),
      mysqlReferenceReaderPassword = getEnvOrSecret("MYSQL_REFERENCE_READER_PASSWORD")
    )
  }
}
