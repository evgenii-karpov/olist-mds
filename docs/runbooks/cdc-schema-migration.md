# Target CDC schema migration

Compatible changes are limited to nullable fields with a default `null`.

1. Update the versioned entity contract and captured writer evidence.
2. Run `check_avro_schema_compatibility.py` and the Apicurio compatibility
   check.
3. Verify MySQL, Avro, Spark reader and Iceberg projection types together.
4. Roll out the reader before publishing the new writer schema.
5. Run bounded CDC and serving checks, then the full Stage V acceptance before
   removing any old version.

Breaking changes, key changes and partition changes require the documented
full-reset action. Never weaken registry compatibility or accept an unknown
writer fingerprint to bypass a migration failure.
