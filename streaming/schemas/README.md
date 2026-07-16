# CDC Avro schemas

Store reviewed logical Avro schemas as
`streaming/schemas/<subject>/v<positive-integer>.avsc`. Versions must be
contiguous, beginning with `v1.avsc`.

CI enforces the committed `BACKWARD_TRANSITIVE` policy: every new reader schema
must be able to read every older writer schema. The Phase 0 checker is
intentionally conservative: removing or renaming fields and changing existing
types fails; new fields require defaults. Registry-side compatibility remains a
required integration check when Apicurio is introduced in Phase 2.

`cdc-coverage/v1.schema.json` is a JSON control-plane contract rather than an
Avro event schema. It classifies landing Kafka offsets into business-event and
tombstone ranges and is validated independently from registry compatibility.
