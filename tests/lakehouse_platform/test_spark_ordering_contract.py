from __future__ import annotations

from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SILVER_BATCH_WRITER = (
    REPOSITORY_ROOT
    / "streaming"
    / "spark"
    / "scala"
    / "src"
    / "main"
    / "scala"
    / "com"
    / "olist"
    / "mds"
    / "spark"
    / "silver"
    / "SilverBatchWriter.scala"
)
SILVER_MAIN = SILVER_BATCH_WRITER.parent.parent / "app" / "SilverMain.scala"


def test_spark_latest_selection_uses_the_canonical_snapshot_discriminator() -> None:
    source = SILVER_BATCH_WRITER.read_text(encoding="utf-8")

    assert 'when(col("last_is_snapshot"), lit(0)).otherwise(lit(1)).desc' in source
    assert 'col("last_is_snapshot").cast("int").desc' not in source


def test_silver_production_path_uses_source_time_zone_for_business_timestamps() -> None:
    decoder = (
        REPOSITORY_ROOT
        / "streaming"
        / "spark"
        / "scala"
        / "src"
        / "main"
        / "scala"
        / "com"
        / "olist"
        / "mds"
        / "spark"
        / "silver"
        / "SilverDecoder.scala"
    ).read_text(encoding="utf-8")
    main = SILVER_MAIN.read_text(encoding="utf-8")

    assert "sourceTimeZone" in decoder
    assert "normalizeWallClockMicros" in decoder
    assert "config.sourceTimeZone" in main


def test_silver_batch_rejects_and_audits_before_any_state_write() -> None:
    writer = SILVER_BATCH_WRITER.read_text(encoding="utf-8")
    audit = (
        REPOSITORY_ROOT
        / "streaming"
        / "spark"
        / "scala"
        / "src"
        / "main"
        / "scala"
        / "com"
        / "olist"
        / "mds"
        / "spark"
        / "silver"
        / "NormalizationErrorWriter.scala"
    ).read_text(encoding="utf-8")

    validation = writer.index("SourceOrdering.validateBatch")
    audit_call = writer.index("NormalizationErrorWriter.writeOrderingFailures")
    first_state_write = writer.index("writeTo(changesTable)")
    assert validation < audit_call < first_state_write
    assert "ordering_batch_rejected" in writer
    assert 'join(existing, Seq("error_id"), "left_anti")' in audit
    assert "deterministicErrorId" in audit
