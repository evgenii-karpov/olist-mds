import java.nio.file.Files
import java.nio.file.StandardCopyOption
import scala.jdk.CollectionConverters._

organization := "com.olist.mds"
name := "olist-spark-jobs"
version := "0.1.0"
scalaVersion := "2.13.17"

scalacOptions ++= Seq(
  "-deprecation",
  "-feature",
  "-unchecked",
  "-Werror",
  "-Wunused:imports"
)

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-sql" % "4.1.3" % Provided,
  "org.apache.spark" %% "spark-sql-kafka-0-10" % "4.1.3" % Provided,
  "org.apache.spark" %% "spark-avro" % "4.1.3" % Provided,
  "org.apache.iceberg" % "iceberg-spark-runtime-4.1_2.13" % "1.11.0" % Provided,
  "org.apache.iceberg" % "iceberg-aws-bundle" % "1.11.0" % Provided,
  "com.mysql" % "mysql-connector-j" % "9.7.0" % Provided,
  "org.scalatest" %% "scalatest" % "3.2.19" % Test
)

Test / fork := true
Test / parallelExecution := false
Test / javaOptions ++= Seq("-Duser.timezone=UTC")

Compile / resourceGenerators += Def.task {
  val managedDir = (Compile / resourceManaged).value
  val streamingDir = baseDirectory.value / ".." / ".."
  val contractsSource = streamingDir / "schemas" / "contracts"
  val topicsSource = streamingDir / "kafka" / "topics.json"

  val entities = Seq(
    "customers",
    "orders",
    "order_items",
    "order_payments",
    "order_reviews",
    "products",
    "sellers",
    "product_category_translation"
  )

  var copiedFiles = Seq[File]()

  // Copy manifest.json
  val manifestSrc = contractsSource / "manifest.json"
  if (!manifestSrc.exists()) {
    sys.error(s"Source contract manifest missing: ${manifestSrc.getAbsolutePath}")
  }
  val manifestTarget = managedDir / "contracts" / "manifest.json"
  manifestTarget.getParentFile.mkdirs()
  Files.copy(manifestSrc.toPath, manifestTarget.toPath, StandardCopyOption.REPLACE_EXISTING)
  copiedFiles = copiedFiles :+ manifestTarget

  // Copy entity v2.json contracts
  for (entity <- entities) {
    val v2Src = contractsSource / entity / "v2.json"
    if (!v2Src.exists()) {
      sys.error(s"Source v2 contract for $entity missing: ${v2Src.getAbsolutePath}")
    }
    val v2Target = managedDir / "contracts" / entity / "v2.json"
    v2Target.getParentFile.mkdirs()
    Files.copy(v2Src.toPath, v2Target.toPath, StandardCopyOption.REPLACE_EXISTING)
    copiedFiles = copiedFiles :+ v2Target
  }

  // The Bronze contract stores the durable fingerprint while the Kafka
  // payload carries a numeric writer schema ID.  Package the captured writer
  // schemas so Silver can use Avro's writer/reader resolution instead of
  // incorrectly decoding writer bytes with the contractual reader schema.
  val capturedSchemasSource = streamingDir / "schemas" / "captured-writer-schemas"
  if (capturedSchemasSource.exists()) {
    val schemaFiles = Files.walk(capturedSchemasSource.toPath)
    try {
      schemaFiles.iterator().asScala.foreach { sourcePath =>
        if (Files.isRegularFile(sourcePath)) {
          val relative = capturedSchemasSource.toPath.relativize(sourcePath)
          val targetPath = managedDir.toPath
            .resolve("captured-writer-schemas")
            .resolve(relative)
          targetPath.toFile.getParentFile.mkdirs()
          Files.copy(sourcePath, targetPath, StandardCopyOption.REPLACE_EXISTING)
          copiedFiles = copiedFiles :+ targetPath.toFile
        }
      }
    } finally {
      schemaFiles.close()
    }
  }

  // Copy topics.json
  if (!topicsSource.exists()) {
    sys.error(s"Source topics.json missing: ${topicsSource.getAbsolutePath}")
  }
  val topicsTarget = managedDir / "topics.json"
  topicsTarget.getParentFile.mkdirs()
  Files.copy(topicsSource.toPath, topicsTarget.toPath, StandardCopyOption.REPLACE_EXISTING)
  copiedFiles = copiedFiles :+ topicsTarget

  copiedFiles
}.taskValue
