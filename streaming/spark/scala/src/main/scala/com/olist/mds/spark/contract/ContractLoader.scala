package com.olist.mds.spark.contract

import com.fasterxml.jackson.databind.ObjectMapper
import com.olist.mds.spark.normalize.FatalContractFailure
import com.olist.mds.spark.normalize.SparkJobException
import org.apache.spark.sql.types._
import java.io.InputStream
import java.security.MessageDigest

object ContractLoader {
  private val mapper = new ObjectMapper()

  def sha256Hex(bytes: Array[Byte]): String = {
    val digest = MessageDigest.getInstance("SHA-256")
    digest.digest(bytes).map("%02x".format(_)).mkString
  }

  def canonicalSchemaJson(node: com.fasterxml.jackson.databind.JsonNode): String = {
    val sortedMapper = new ObjectMapper()
    sortedMapper.configure(
      com.fasterxml.jackson.databind.SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS,
      true
    )
    val obj = sortedMapper.treeToValue(node, classOf[Object])
    sortedMapper.writeValueAsString(obj)
  }

  private def readResourceBytes(path: String): Array[Byte] = {
    val is: InputStream = getClass.getClassLoader.getResourceAsStream(path)
    if (is == null) {
      throw SparkJobException(
        "contract_resource_mismatch",
        s"Resource not found: $path",
        FatalContractFailure
      )
    }
    try {
      val buffer = new Array[Byte](65536)
      val baos = new java.io.ByteArrayOutputStream()
      var len = 0
      while ({ len = is.read(buffer); len != -1 }) {
        baos.write(buffer, 0, len)
      }
      baos.toByteArray
    } finally {
      is.close()
    }
  }

  private def parseSparkType(typeStr: String): DataType = typeStr match {
    case "string" => StringType
    case "int" => IntegerType
    case "long" => LongType
    case "boolean" => BooleanType
    case s if s.startsWith("decimal(") && s.endsWith(")") =>
      val parts = s.substring(8, s.length - 1).split(",").map(_.trim.toInt)
      DecimalType(parts(0), parts(1))
    case "timestamp" => TimestampType
    case "timestamptz" => TimestampType
    case "binary" => BinaryType
    case other =>
      throw SparkJobException(
        "contract_resource_mismatch",
        s"Unsupported Spark type in contract: $other",
        FatalContractFailure
      )
  }

  def loadManifest(): Map[String, Any] = {
    val bytes = readResourceBytes("contracts/manifest.json")
    val tree = mapper.readTree(bytes)
    val manifestVersion = tree.get("manifest_version").asInt()
    val entityCount = tree.get("entity_count").asInt()
    if (manifestVersion != 1 || entityCount != 8) {
      throw SparkJobException(
        "contract_resource_mismatch",
        s"Invalid manifest version ($manifestVersion) or entity count ($entityCount)",
        FatalContractFailure
      )
    }
    Map(
      "manifest_version" -> manifestVersion,
      "entity_count" -> entityCount
    )
  }

  def loadEntityContract(entity: String): EntityContract = {
    val manifestBytes = readResourceBytes("contracts/manifest.json")
    val manifestTree = mapper.readTree(manifestBytes)
    val entitiesNode = manifestTree.get("entities")

    var expectedSha: Option[String] = None
    val entriesIter = entitiesNode.elements()
    while (entriesIter.hasNext) {
      val entry = entriesIter.next()
      if (entry.get("entity").asText() == entity) {
        if (entry.get("contract_version").asInt() != 2) {
          throw SparkJobException(
            "contract_resource_mismatch",
            s"Contract version for $entity is not 2",
            FatalContractFailure
          )
        }
        expectedSha = Some(entry.get("contract_sha256").asText())
      }
    }

    val sha256Expected = expectedSha.getOrElse(
      throw SparkJobException(
        "contract_resource_mismatch",
        s"Entity $entity not in manifest",
        FatalContractFailure
      )
    )

    val path = s"contracts/$entity/v2.json"
    val bytes = readResourceBytes(path)
    val tree = mapper.readTree(bytes)

    val canonicalJsonStr = canonicalSchemaJson(tree)
    val actualSha = sha256Hex(canonicalJsonStr.getBytes(java.nio.charset.StandardCharsets.UTF_8))

    if (actualSha.toLowerCase != sha256Expected.toLowerCase) {
      throw SparkJobException(
        "contract_resource_mismatch",
        s"SHA256 mismatch for $path: expected $sha256Expected, got $actualSha",
        FatalContractFailure
      )
    }

    // Check invariants
    val avroNode = tree.get("avro")
    val sparkSchemaNode = tree.get("spark_reader_schema")

    val wireFormat = avroNode.get("wire_format").asText()
    val magicByte = avroNode.get("magic_byte").asInt()
    val prefixBytes = sparkSchemaNode.get("strip_confluent_prefix_bytes").asInt()
    val fpAlgo = avroNode.get("fingerprint_algorithm").asText()
    val fromAvroMode = sparkSchemaNode.get("from_avro_mode").asText()

    if (
      wireFormat != "confluent" || magicByte != 0 || prefixBytes != 5 ||
      fpAlgo != "sha256-canonical-json-v1" || fromAvroMode != "FAILFAST"
    ) {
      throw SparkJobException(
        "contract_resource_mismatch",
        s"Wire format or fingerprint algorithm mismatch for $entity",
        FatalContractFailure
      )
    }

    val topic = tree.get("topic").asText()
    val topicPartitions = tree.get("topic_partitions").asInt()

    val pkNode = tree.get("primary_key")
    val pk = Vector.tabulate(pkNode.size())(i => pkNode.get(i).asText())
    val pkOrdinals = pk.zipWithIndex.toMap

    val colsNode = tree.get("iceberg_projection").get("business_columns")
    val businessColumns = Vector.tabulate(colsNode.size()) { i =>
      val c = colsNode.get(i)
      val name = c.get("name").asText()
      val st = parseSparkType(c.get("type").asText())
      val nullable = c.get("nullable").asBoolean()
      val pkOrd = pkOrdinals.get(name)
      BusinessColumn(name, st, nullable, pkOrd)
    }

    val keyReaderSchema = avroNode.get("key_reader_schema").toString
    val valueReaderSchema = avroNode.get("value_reader_schema").toString

    val allowedKeyFpNode = avroNode.get("allowed_key_fingerprints")
    val allowedKeyFps = Set.tabulate(allowedKeyFpNode.size()) { i =>
      val node = allowedKeyFpNode.get(i)
      if (node.isObject && node.has("sha256")) node.get("sha256").asText().toLowerCase
      else node.asText().toLowerCase
    }

    val allowedValFpNode = avroNode.get("allowed_value_fingerprints")
    val allowedValFps = Set.tabulate(allowedValFpNode.size()) { i =>
      val node = allowedValFpNode.get(i)
      if (node.isObject && node.has("sha256")) node.get("sha256").asText().toLowerCase
      else node.asText().toLowerCase
    }

    // Bronze stores the numeric Confluent schema IDs and the raw payload
    // hashes.  The contract fingerprint is the durable identity of the
    // writer schema, so it cannot be compared with those payload hashes.
    // The captured-writer-schema provenance contains the IDs that are
    // approved for the current contract generation.
    val schemaIdPattern = "schema-(\\d+)-.*".r
    def schemaIds(node: com.fasterxml.jackson.databind.JsonNode): Set[Int] = {
      val ids = scala.collection.mutable.Set[Int]()
      var i = 0
      while (i < node.size()) {
        val item = node.get(i)
        val source =
          if (item.isObject && item.has("source")) item.get("source").asText()
          else ""
        schemaIdPattern
          .findFirstMatchIn(source)
          .foreach(matchData => ids += matchData.group(1).toInt)
        i += 1
      }
      ids.toSet
    }
    val allowedKeySchemaIds = schemaIds(allowedKeyFpNode)
    val allowedValueSchemaIds = schemaIds(allowedValFpNode)

    def writerSchemas(node: com.fasterxml.jackson.databind.JsonNode): Map[Int, String] = {
      val schemas = scala.collection.mutable.Map[Int, String]()
      var i = 0
      while (i < node.size()) {
        val item = node.get(i)
        val source =
          if (item.isObject && item.has("source")) item.get("source").asText()
          else ""
        schemaIdPattern
          .findFirstMatchIn(source)
          .foreach(matchData => {
            val schemaId = matchData.group(1).toInt
            schemas(schemaId) = new String(
              readResourceBytes(source),
              java.nio.charset.StandardCharsets.UTF_8
            )
          })
        i += 1
      }
      schemas.toMap
    }
    val allowedKeyWriterSchemas = writerSchemas(allowedKeyFpNode)
    val allowedValueWriterSchemas = writerSchemas(allowedValFpNode)

    if (
      allowedKeyFps.isEmpty || allowedValFps.isEmpty ||
      allowedKeySchemaIds.isEmpty || allowedValueSchemaIds.isEmpty ||
      allowedKeyWriterSchemas.keySet != allowedKeySchemaIds ||
      allowedValueWriterSchemas.keySet != allowedValueSchemaIds
    ) {
      throw SparkJobException(
        "contract_resource_mismatch",
        s"Allowed writer schema provenance is incomplete for $entity",
        FatalContractFailure
      )
    }

    EntityContract(
      entity = entity,
      topic = topic,
      topicPartitions = topicPartitions,
      primaryKey = pk,
      businessColumns = businessColumns,
      keyReaderSchema = keyReaderSchema,
      valueReaderSchema = valueReaderSchema,
      allowedKeyFingerprints = allowedKeyFps,
      allowedValueFingerprints = allowedValFps,
      allowedKeySchemaIds = allowedKeySchemaIds,
      allowedValueSchemaIds = allowedValueSchemaIds,
      allowedKeyWriterSchemas = allowedKeyWriterSchemas,
      allowedValueWriterSchemas = allowedValueWriterSchemas
    )
  }

  def loadAll(): Map[String, EntityContract] = {
    loadManifest()
    val entities = Vector(
      "customers",
      "orders",
      "order_items",
      "order_payments",
      "order_reviews",
      "products",
      "sellers",
      "product_category_translation"
    )
    entities.map(e => e -> loadEntityContract(e)).toMap
  }
}
