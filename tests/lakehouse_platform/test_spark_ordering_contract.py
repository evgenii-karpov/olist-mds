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


def test_spark_latest_selection_uses_the_canonical_snapshot_discriminator() -> None:
    source = SILVER_BATCH_WRITER.read_text(encoding="utf-8")

    assert 'when(col("last_is_snapshot"), lit(0)).otherwise(lit(1)).desc' in source
    assert 'col("last_is_snapshot").cast("int").desc' not in source
