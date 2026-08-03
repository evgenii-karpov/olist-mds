package com.olist.mds.spark.avro

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.olist.mds.spark.contract.EntityContract
import com.olist.mds.spark.normalize.FatalContractFailure
import com.olist.mds.spark.normalize.SparkJobException
import org.apache.avro.Schema

import java.io.ByteArrayOutputStream
import java.net.HttpURLConnection
import java.net.URI
import java.net.URLEncoder
import java.nio.charset.StandardCharsets
import scala.collection.mutable
import scala.jdk.CollectionConverters._

final case class ResolvedRegistrySchema(
    schemaId: Int,
    schema: Schema,
    schemaJson: String,
    referencesJson: String,
    selfContainedSchemaJson: String,
    fingerprintSha256: String
)

final case class RegistrySchemaReference(name: String, subject: String, version: String)

final case class RegistrySchemaDocument(
    schema: JsonNode,
    references: Vector[RegistrySchemaReference]
)

final case class RegistryHttpFailure(status: Int, path: String, body: String)
    extends RuntimeException(s"registry GET $path returned HTTP $status")

/** Resolves a Confluent-compatible schema ID from Apicurio and validates an unapproved value writer
  * as a safe nullable additive evolution.
  *
  * The connector uses TopicIdStrategy for the root Envelope, while Apicurio stores referenced
  * `Value`/`Key` artifacts under their exact artifact IDs. Consequently references are resolved
  * through the native v2 API, trying the exact subject before the TopicIdStrategy spelling.
  */
final class RegistrySchemaResolver(
    ccompatBaseUrl: String,
    nativeRegistryBaseUrl: String,
    timeoutSeconds: Int = 15
) {
  private val mapper = new ObjectMapper()
  private val registryGroup = "olist_cdc"
  private val cache = mutable.Map.empty[Int, ResolvedRegistrySchema]

  def resolveValueWriterSchema(schemaId: Int, contract: EntityContract): Schema = {
    val resolved = resolve(schemaId)
    validateNullableAdditive(resolved.schema, contract)
    resolved.schema
  }

  def resolve(schemaId: Int): ResolvedRegistrySchema = synchronized {
    if (schemaId <= 0) {
      throw SparkJobException(
        "unknown_schema_id",
        s"Schema ID must be positive: $schemaId",
        FatalContractFailure
      )
    }
    cache.getOrElseUpdate(schemaId, resolveUncached(schemaId))
  }

  private def resolveUncached(schemaId: Int): ResolvedRegistrySchema = {
    try {
      val root = document(get(s"${trim(ccompatBaseUrl)}/schemas/ids/$schemaId"))
      val parser = new Schema.Parser()
      val loaded = mutable.Set.empty[(String, String)]

      def loadReference(
          reference: RegistrySchemaReference,
          stack: Vector[(String, String)]
      ): Unit = {
        val key = reference.subject -> reference.version
        if (stack.contains(key)) {
          val chain =
            (stack :+ key).map { case (subject, version) => s"$subject@$version" }.mkString(" -> ")
          throw SparkJobException(
            "incompatible_schema_evolution",
            s"Cyclic Avro reference detected: $chain",
            FatalContractFailure
          )
        }
        if (loaded.contains(key)) return
        val referenced = document(getReference(reference))
        referenced.references.foreach(child => loadReference(child, stack :+ key))
        parser.parse(mapper.writeValueAsString(referenced.schema))
        loaded += key
      }

      root.references.foreach(reference => loadReference(reference, Vector.empty))
      val parsedRoot = parser.parse(mapper.writeValueAsString(root.schema))
      val referencesJson = mapper.writeValueAsString(
        root.references.map(reference =>
          Map(
            "name" -> reference.name,
            "subject" -> reference.subject,
            "version" -> reference.version
          )
        )
      )
      val schemaJson = mapper.writeValueAsString(root.schema)
      val selfContainedSchemaJson = parsedRoot.toString
      ResolvedRegistrySchema(
        schemaId = schemaId,
        schema = parsedRoot,
        schemaJson = schemaJson,
        referencesJson = referencesJson,
        selfContainedSchemaJson = selfContainedSchemaJson,
        fingerprintSha256 = ConfluentFrame.sha256Hex(
          selfContainedSchemaJson.getBytes(StandardCharsets.UTF_8)
        )
      )
    } catch {
      case error: SparkJobException => throw error
      case failure: RegistryHttpFailure if failure.status == 404 =>
        throw SparkJobException(
          "unknown_schema_id",
          s"Schema ID $schemaId is not present in Apicurio: ${failure.body.take(300)}",
          FatalContractFailure,
          failure
        )
      case failure: RegistryHttpFailure =>
        throw SparkJobException(
          "registry_unavailable",
          s"Apicurio returned HTTP ${failure.status} for ${failure.path}",
          com.olist.mds.spark.normalize.TransientFailure,
          failure
        )
      case error: java.net.SocketTimeoutException =>
        throw SparkJobException(
          "registry_unavailable",
          s"Timed out reading Apicurio for schema ID $schemaId",
          com.olist.mds.spark.normalize.TransientFailure,
          error
        )
      case error: java.io.IOException =>
        throw SparkJobException(
          "registry_unavailable",
          s"Could not read Apicurio for schema ID $schemaId: ${error.getMessage}",
          com.olist.mds.spark.normalize.TransientFailure,
          error
        )
      case error: org.apache.avro.AvroRuntimeException =>
        throw SparkJobException(
          "incompatible_schema_evolution",
          s"Apicurio schema ID $schemaId is not a valid resolvable Avro schema: ${error.getMessage}",
          FatalContractFailure,
          error
        )
      case error: Exception =>
        throw SparkJobException(
          "incompatible_schema_evolution",
          s"Could not resolve Apicurio schema ID $schemaId: ${error.getMessage}",
          FatalContractFailure,
          error
        )
    }
  }

  private def validateNullableAdditive(writer: Schema, contract: EntityContract): Unit = {
    val reader = new Schema.Parser().parse(contract.valueReaderSchema)
    if (writer.getType != Schema.Type.RECORD || reader.getType != Schema.Type.RECORD) {
      evolutionFailure(contract, "value schema root must be an Avro record")
    }
    if (writer.getFullName != reader.getFullName) {
      evolutionFailure(
        contract,
        s"value schema root changed from ${reader.getFullName} to ${writer.getFullName}"
      )
    }

    val readerFields = reader.getFields.asScala.map(field => field.name -> field).toMap
    val writerFields = writer.getFields.asScala.map(field => field.name -> field).toMap
    val missingRootFields = readerFields.keySet.diff(writerFields.keySet)
    if (missingRootFields.nonEmpty) {
      evolutionFailure(
        contract,
        s"value schema dropped root fields: ${missingRootFields.toSeq.sorted.mkString(", ")}"
      )
    }
    val addedRootFields = writerFields.keySet.diff(readerFields.keySet)
    if (addedRootFields.nonEmpty) {
      evolutionFailure(
        contract,
        s"value schema added unsupported root fields: ${addedRootFields.toSeq.sorted.mkString(", ")}"
      )
    }

    readerFields.foreach { case (name, readerField) =>
      val writerField = writerFields(name)
      if (name == "before" || name == "after") {
        val readerValue = findNamedRecord(readerField.schema, "Value")
        val writerValue = findNamedRecord(writerField.schema, "Value")
        if (readerValue.isEmpty || writerValue.isEmpty) {
          evolutionFailure(contract, s"$name field no longer contains the contractual Value record")
        }
        validateValueRecord(readerValue.get, writerValue.get, contract)
      } else if (!sameSchemaShape(readerField.schema, writerField.schema)) {
        evolutionFailure(contract, s"value schema changed type of root field '$name'")
      }
    }
  }

  private def validateValueRecord(
      reader: Schema,
      writer: Schema,
      contract: EntityContract
  ): Unit = {
    if (reader.getType != Schema.Type.RECORD || writer.getType != Schema.Type.RECORD) {
      evolutionFailure(contract, "before/after Value must remain records")
    }
    if (reader.getFullName != writer.getFullName) {
      evolutionFailure(
        contract,
        s"Value record changed from ${reader.getFullName} to ${writer.getFullName}"
      )
    }
    val readerFields = reader.getFields.asScala.map(field => field.name -> field).toMap
    val writerFields = writer.getFields.asScala.map(field => field.name -> field).toMap
    val missing = readerFields.keySet.diff(writerFields.keySet)
    if (missing.nonEmpty) {
      evolutionFailure(
        contract,
        s"Value schema dropped fields: ${missing.toSeq.sorted.mkString(", ")}"
      )
    }
    readerFields.foreach { case (name, readerField) =>
      if (!sameSchemaShape(readerField.schema, writerFields(name).schema)) {
        evolutionFailure(contract, s"Value schema changed type of field '$name'")
      }
    }
    writerFields.keySet.diff(readerFields.keySet).foreach { name =>
      val field = writerFields(name)
      if (!isNullableWithNullDefault(field)) {
        evolutionFailure(
          contract,
          s"new Value field '$name' must be a [null, type] union with default null"
        )
      }
    }
  }

  private def findNamedRecord(schema: Schema, shortName: String): Option[Schema] = {
    def walk(value: Schema): Option[Schema] = value.getType match {
      case Schema.Type.RECORD if value.getName == shortName => Some(value)
      case Schema.Type.UNION => value.getTypes.asScala.view.flatMap(walk).headOption
      case _ => None
    }
    walk(schema)
  }

  private def isNullableWithNullDefault(field: Schema.Field): Boolean = {
    val schema = field.schema
    val defaultValue = field.defaultVal()
    schema.getType == Schema.Type.UNION &&
    schema.getTypes.asScala.exists(_.getType == Schema.Type.NULL) &&
    field.hasDefaultValue &&
    (defaultValue == null || defaultValue.getClass.getName == "org.apache.avro.JsonProperties$Null")
  }

  private def sameSchemaShape(left: Schema, right: Schema): Boolean = {
    if (left.getType != right.getType) return false
    left.getType match {
      case Schema.Type.RECORD =>
        val leftFields = left.getFields.asScala.map(field => field.name -> field).toMap
        val rightFields = right.getFields.asScala.map(field => field.name -> field).toMap
        leftFields.keySet == rightFields.keySet &&
        leftFields.forall { case (name, field) =>
          sameSchemaShape(field.schema, rightFields(name).schema)
        }
      case Schema.Type.UNION =>
        val remaining = mutable.ArrayBuffer.from(right.getTypes.asScala)
        left.getTypes.asScala.forall { leftType =>
          val matchIndex = remaining.indexWhere(rightType => sameSchemaShape(leftType, rightType))
          if (matchIndex < 0) false
          else {
            remaining.remove(matchIndex)
            true
          }
        } && remaining.isEmpty
      case Schema.Type.ARRAY => sameSchemaShape(left.getElementType, right.getElementType)
      case Schema.Type.MAP => sameSchemaShape(left.getValueType, right.getValueType)
      case Schema.Type.ENUM =>
        left.getFullName == right.getFullName && left.getEnumSymbols == right.getEnumSymbols
      case Schema.Type.FIXED =>
        left.getFullName == right.getFullName && left.getFixedSize == right.getFixedSize
      case _ => true
    }
  }

  private def evolutionFailure(contract: EntityContract, message: String): Nothing = {
    throw SparkJobException(
      "incompatible_schema_evolution",
      s"${contract.entity}: $message",
      FatalContractFailure
    )
  }

  private def document(node: JsonNode): RegistrySchemaDocument = {
    val rawSchema = Option(node.get("schema")).getOrElse {
      throw new IllegalArgumentException("registry response has no schema field")
    }
    val schema = if (rawSchema.isTextual) mapper.readTree(rawSchema.asText()) else rawSchema
    val referencesNode = Option(node.get("references"))
      .filter(_.isArray)
      .map(_.elements().asScala.toVector)
      .getOrElse(Vector.empty)
    val references = referencesNode.map { reference =>
      val name = Option(reference.get("name")).filter(_.isTextual).map(_.asText()).getOrElse {
        throw new IllegalArgumentException("Avro reference has no name")
      }
      val subject = Option(reference.get("subject"))
        .orElse(Option(reference.get("artifactId")))
        .filter(_.isTextual)
        .map(_.asText())
        .getOrElse {
          throw new IllegalArgumentException(s"Avro reference $name has no subject")
        }
      val version = Option(reference.get("version")).map(_.asText()).getOrElse {
        throw new IllegalArgumentException(s"Avro reference $name has no version")
      }
      RegistrySchemaReference(name, subject, version)
    }
    RegistrySchemaDocument(schema, references)
  }

  private def getReference(reference: RegistrySchemaReference): JsonNode = {
    val exactPath =
      s"${trim(nativeRegistryBaseUrl)}/groups/${encode(registryGroup)}/artifacts/${encode(reference.subject)}/versions/${encode(reference.version)}"
    try documentWrapper(get(exactPath))
    catch {
      case original: RegistryHttpFailure
          if reference.subject.endsWith(".Value") || reference.subject.endsWith(".Key") =>
        val mapped = artifactIdForSubject(reference.subject)
        if (mapped == reference.subject) throw original
        val mappedPath =
          s"${trim(nativeRegistryBaseUrl)}/groups/${encode(registryGroup)}/artifacts/${encode(mapped)}/versions/${encode(reference.version)}"
        documentWrapper(get(mappedPath))
    }
  }

  private def documentWrapper(node: JsonNode): JsonNode = {
    if (node.has("schema")) node
    else {
      val wrapper = mapper.createObjectNode()
      wrapper.set[JsonNode]("schema", node)
      wrapper
    }
  }

  private def get(url: String): JsonNode = {
    val connection = URI.create(url).toURL.openConnection().asInstanceOf[HttpURLConnection]
    connection.setRequestMethod("GET")
    connection.setConnectTimeout(timeoutSeconds * 1000)
    connection.setReadTimeout(timeoutSeconds * 1000)
    connection.setRequestProperty("Accept", "application/json")
    val status = connection.getResponseCode
    val stream = if (status >= 400) connection.getErrorStream else connection.getInputStream
    val output = new ByteArrayOutputStream()
    if (stream != null) {
      val buffer = new Array[Byte](4096)
      var read = stream.read(buffer)
      while (read >= 0) {
        if (read > 0) output.write(buffer, 0, read)
        read = stream.read(buffer)
      }
      stream.close()
    }
    val body = new String(output.toByteArray, StandardCharsets.UTF_8)
    connection.disconnect()
    if (status >= 400) throw RegistryHttpFailure(status, url, body)
    mapper.readTree(body)
  }

  private def trim(value: String): String = value.stripSuffix("/")

  private def encode(value: String): String =
    URLEncoder.encode(value, StandardCharsets.UTF_8.name()).replace("+", "%20")

  private def artifactIdForSubject(subject: String): String = {
    if (subject.endsWith(".Value")) subject.stripSuffix(".Value") + "-value"
    else if (subject.endsWith(".Key")) subject.stripSuffix(".Key") + "-key"
    else subject
  }
}
