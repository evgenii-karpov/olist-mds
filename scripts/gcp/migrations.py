"""Credential-free discovery and rendering for BigQuery SQL migrations."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

MIGRATIONS_DIRECTORY = (
    Path(__file__).resolve().parents[2] / "sql" / "bigquery" / "migrations"
)
_MIGRATION_FILE = re.compile(r"^V(?P<version>[0-9]{3})__(?P<name>[a-z0-9_]+)\.sql$")
_IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
_PROJECT_ID = re.compile(r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$")


@dataclass(frozen=True)
class Migration:
    """A versioned SQL file and its source checksum."""

    version: int
    migration_id: str
    path: Path
    checksum: str


def _validate_project_id(project_id: str) -> str:
    if not _PROJECT_ID.fullmatch(project_id):
        raise ValueError("project_id is not a valid GCP project ID")
    return project_id


def _validate_identifier(value: str, label: str) -> str:
    if not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"{label} contains an unsafe identifier")
    return value


def list_migrations(directory: Path = MIGRATIONS_DIRECTORY) -> tuple[Migration, ...]:
    """Return ordered migrations and fail closed on naming/version drift."""

    migrations: list[Migration] = []
    for path in sorted(directory.glob("V*.sql")):
        match = _MIGRATION_FILE.fullmatch(path.name)
        if not match:
            raise ValueError(f"migration filename is not normative: {path.name}")
        content = path.read_bytes()
        migrations.append(
            Migration(
                version=int(match.group("version")),
                migration_id=path.stem,
                path=path,
                checksum=hashlib.sha256(content).hexdigest(),
            )
        )
    migrations.sort(key=lambda migration: migration.version)
    versions = [migration.version for migration in migrations]
    if versions != list(range(1, len(versions) + 1)):
        raise ValueError(f"migration versions must be contiguous from V001: {versions}")
    if len(versions) != len(set(versions)):
        raise ValueError(f"migration versions are duplicated: {versions}")
    return tuple(migrations)


def render_migration(
    migration: Migration,
    project_id: str,
    catalog_id: str,
) -> str:
    """Render only the approved identifiers into one migration file."""

    project = _validate_project_id(project_id)
    catalog = _validate_identifier(catalog_id, "catalog_id")
    content = migration.path.read_text(encoding="utf-8")
    rendered = content.replace("{{ project_id }}", project).replace(
        "{{ catalog_id }}", catalog
    )
    if "{{" in rendered or "}}" in rendered:
        raise ValueError(f"unresolved template placeholder in {migration.path.name}")
    return rendered


def migration_manifest(
    directory: Path = MIGRATIONS_DIRECTORY,
) -> list[dict[str, object]]:
    """Return JSON-safe source metadata for CI and operator evidence."""

    return [
        {
            "version": migration.version,
            "migration_id": migration.migration_id,
            "path": migration.path.relative_to(directory).as_posix(),
            "sha256": migration.checksum,
        }
        for migration in list_migrations(directory)
    ]
