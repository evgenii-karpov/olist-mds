from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SPARK_DIRECTORY = REPOSITORY_ROOT / "docker" / "spark"


def _manifest_rows() -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for line in (
        (SPARK_DIRECTORY / "jars.sha256").read_text(encoding="utf-8").splitlines()
    ):
        if not line or line.startswith("#"):
            continue
        checksum, url, filename = line.split()
        rows.append((checksum, url, filename))
    return rows


def test_spark_image_pins_the_wave_one_runtime() -> None:
    dockerfile = (SPARK_DIRECTORY / "Dockerfile").read_text(encoding="utf-8")

    assert "apache/spark:4.1.3-scala2.13-java17-python3-ubuntu" in dockerfile
    assert "FROM alpine:3.22.1 AS artifact-downloader" in dockerfile
    assert "ARG SPARK_VERSION=4.1.3" in dockerfile
    assert "ARG SCALA_BINARY_VERSION=2.13" in dockerfile
    assert "ARG HADOOP_VERSION=3.4.2" in dockerfile
    assert "4.1.3-iceberg1.11.0" in dockerfile
    assert "verify-olist-spark-runtime" in dockerfile
    assert "--from=artifact-downloader" in dockerfile


def test_every_runtime_jar_has_a_real_sha256_and_pinned_maven_url() -> None:
    rows = _manifest_rows()

    assert len(rows) == 12
    assert len({filename for _, _, filename in rows}) == len(rows)
    for checksum, url, filename in rows:
        assert re.fullmatch(r"[0-9a-f]{64}", checksum)
        parsed = urlparse(url)
        assert parsed.scheme == "https"
        assert parsed.netloc == "repo.maven.apache.org"
        assert parsed.path.endswith(f"/{filename}")
        assert all(marker not in url for marker in ("LATEST", "SNAPSHOT", "${"))


def test_manifest_contains_the_exact_connector_matrix() -> None:
    filenames = {filename for _, _, filename in _manifest_rows()}

    assert {
        "iceberg-spark-runtime-4.1_2.13-1.11.0.jar",
        "iceberg-aws-bundle-1.11.0.jar",
        "spark-sql-kafka-0-10_2.13-4.1.3.jar",
        "spark-token-provider-kafka-0-10_2.13-4.1.3.jar",
        "spark-avro_2.13-4.1.3.jar",
        "kafka-clients-3.9.1.jar",
        "commons-pool2-2.12.1.jar",
        "scala-parallel-collections_2.13-1.2.0.jar",
        "hadoop-aws-3.4.2.jar",
        "bundle-2.29.52.jar",
        "mysql-connector-j-9.7.0.jar",
        "protobuf-java-4.31.1.jar",
    } == filenames


def test_runtime_verification_fails_closed_on_spark_scala_or_hadoop_drift() -> None:
    script = (SPARK_DIRECTORY / "verify-runtime.sh").read_text(encoding="utf-8")

    assert "Spark base image mismatch" in script
    assert "Scala base image mismatch" in script
    assert "Hadoop base image mismatch" in script
    assert "hadoop-client-${component}-${expected_hadoop_version}.jar" in script
    assert "expected exactly one" in script


def test_downloader_accepts_only_the_declared_maven_origin() -> None:
    script = (SPARK_DIRECTORY / "download-jars.sh").read_text(encoding="utf-8")

    assert "https://repo.maven.apache.org/maven2/" in script
    assert "sha256sum --check --strict" in script
    assert "-eq 12" in script
