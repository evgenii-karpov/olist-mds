# Target secret rotation

The target runtime accepts credentials through Docker secret files or explicit
`*_SOURCE_FILE` paths. Never paste resolved values into commands, logs, issues
or evidence.

1. Inventory the target identity and capture health without reading the value.
2. Rotate the server-side identity and replace only its secret file with
   restrictive permissions.
3. Recreate affected target clients, preserving Kafka offsets and Iceberg
   checkpoints.
4. Verify MySQL, Kafka Connect, Apicurio, MinIO/Polaris, Spark and serving
   authentication, then confirm the relevant observability alert resolves.
5. Revoke the old value after all clients use the replacement.
