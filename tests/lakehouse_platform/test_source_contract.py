from __future__ import annotations

import csv
import shutil
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest
from scripts.utilities.validate_source_contract import (
    load_contract,
    validate_archive,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ARCHIVE = ROOT / "tests/fixtures/olist_small/olist_small.zip"
FIXTURE_PROFILE = ROOT / "tests/fixtures/olist_small/source_profile_small.json"


def test_source_contract_rejects_missing_required_column() -> None:
    with temporary_workspace_directory() as tmpdir:
        broken_archive = tmpdir / "missing_customer_state.zip"
        _write_archive_with_removed_column(
            source_archive=FIXTURE_ARCHIVE,
            output_archive=broken_archive,
            member_name="olist_customers_dataset.csv",
            removed_column="customer_state",
        )

        with pytest.raises(ValueError, match="customers: expected columns"):
            validate_archive(broken_archive, load_contract(FIXTURE_PROFILE))


def test_source_contract_accepts_committed_small_fixture() -> None:
    validate_archive(FIXTURE_ARCHIVE, load_contract(FIXTURE_PROFILE))


def _write_archive_with_removed_column(
    *,
    source_archive: Path,
    output_archive: Path,
    member_name: str,
    removed_column: str,
) -> None:
    with (
        ZipFile(source_archive) as source_zip,
        ZipFile(output_archive, "w", compression=ZIP_DEFLATED) as output_zip,
    ):
        for source_info in source_zip.infolist():
            content = source_zip.read(source_info.filename)
            if source_info.filename != member_name:
                output_zip.writestr(source_info, content)
                continue

            rows = list(csv.DictReader(content.decode("utf-8").splitlines()))
            fieldnames = [
                fieldname for fieldname in rows[0] if fieldname != removed_column
            ]
            output = []
            output.append(",".join(fieldnames))
            output.extend(
                ",".join(row.get(fieldname, "") for fieldname in fieldnames)
                for row in rows
            )
            output_zip.writestr(member_name, "\n".join(output) + "\n")


@contextmanager
def temporary_workspace_directory() -> Iterator[Path]:
    root = ROOT / "data/test_tmp"
    root.mkdir(parents=True, exist_ok=True)
    directory = root / f"source_contract_{uuid.uuid4().hex}"
    directory.mkdir()
    try:
        yield directory
    finally:
        shutil.rmtree(directory, ignore_errors=True)
