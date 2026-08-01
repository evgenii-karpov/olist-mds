from __future__ import annotations

import unittest
from datetime import UTC, datetime

from streaming.spark.platform.normalization_api import (
    CanonicalEventMetadata,
    DebeziumEnvelope,
    NormalizationContext,
    NormalizationEvent,
    WriterSchemaFingerprint,
    deduplicate_event_ids,
    ensure_checkpoint_contract,
)


class NormalizationApiContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.writer = WriterSchemaFingerprint(
            entity="customers",
            contract_version=1,
            key_fingerprint_sha256="a" * 64,
            value_fingerprint_sha256="b" * 64,
        )

    def _event(self, offset: int) -> NormalizationEvent:
        return NormalizationEvent(
            metadata=CanonicalEventMetadata(
                topic="olist_cdc.olist_oltp.customers",
                partition=0,
                offset=offset,
                kafka_timestamp=datetime(2026, 8, 1, tzinfo=UTC),
                key_schema_id=1,
                value_schema_id=2,
                schema_fingerprint=self.writer.value_fingerprint_sha256,
            ),
            envelope=DebeziumEnvelope(
                before=None,
                after={"customer_id": "c-1"},
                op="r",
                source={"file": "mysql-bin.000001", "pos": 4},
                transaction=None,
            ),
            writer=self.writer,
        )

    def test_event_id_is_canonical_and_dedupes_only_same_transport_identity(
        self,
    ) -> None:
        first = self._event(7)
        duplicate = self._event(7)
        later = self._event(8)
        self.assertEqual("olist_cdc.olist_oltp.customers:0:7", first.event_id)
        self.assertEqual(
            (first, later), deduplicate_event_ids((first, duplicate, later))
        )

    def test_context_uses_fixed_topology_checkpoint(self) -> None:
        context = NormalizationContext.for_entity(
            "customers", contract_version=1, writer=self.writer
        )
        self.assertEqual("normalize_customers", context.query_name)
        self.assertEqual(
            "s3a://olist-checkpoints/normalize_customers/contract-v1/",
            context.checkpoint,
        )
        ensure_checkpoint_contract(context, expected_contract_version=1)

    def test_context_rejects_other_checkpoint_bucket(self) -> None:
        context = NormalizationContext(
            entity="customers",
            contract_version=1,
            query_name="normalize_customers",
            checkpoint="s3a://wrong-bucket/normalize_customers/contract-v1/",
            writer=self.writer,
        )
        with self.assertRaises(ValueError):
            ensure_checkpoint_contract(context, expected_contract_version=1)


if __name__ == "__main__":
    unittest.main()
