# CDC schema migration

A compatible schema change adds a nullable field with a null default.

1. Update the entity contract under `streaming/schemas/contracts/` and
   the captured writer schema evidence.
2. Run the contract generators and compatibility tests:

   ```powershell
   python -m streaming.schemas.generate_contracts --check
   python -m streaming.schemas.writer_schemas validate
   uv run pytest -q tests/cdc_contracts
   ```

3. Check the MySQL column, Avro schema, Spark reader and Iceberg projection
   together.
4. Deploy the reader contract before the connector emits the new field.
5. Run the local CDC acceptance and serving checks.

Do not change a key, remove an existing field or weaken Registry compatibility
as part of a compatible migration. Use a clean local reset when the source
contract and reader cannot be evolved together.
