# CDC Avro schemas

Store reviewed logical Avro schemas as
`streaming/schemas/<subject>/v<positive-integer>.avsc`. Versions must be
contiguous, beginning with `v1.avsc`.

CI enforces the committed `BACKWARD_TRANSITIVE` policy: every new reader schema
must be able to read every older writer schema. The Phase 0 checker is
intentionally conservative: removing or renaming fields and changing existing
types fails; new fields require defaults. Registry-side compatibility remains a
required integration check when Apicurio is introduced in Phase 2.
