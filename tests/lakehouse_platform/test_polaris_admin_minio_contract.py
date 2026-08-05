from __future__ import annotations

from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
POLARIS_DIRECTORY = REPOSITORY_ROOT / "infra" / "polaris"


def _read(relative_path: str) -> str:
    return (POLARIS_DIRECTORY / relative_path).read_text(encoding="utf-8")


def test_admin_bootstrap_does_not_mix_realm_and_credentials_file() -> None:
    bootstrap = _read("admin/bootstrap-jdbc.sh")

    assert "bootstrap" in bootstrap
    assert '--credentials-file="${credentials_file}"' in bootstrap
    assert "--realm" not in bootstrap


def test_minio_mc_config_is_temporary_and_always_cleaned_up() -> None:
    initializer = _read("minio/init.sh")

    mktemp = 'mc_config_dir=$(mktemp -d "${TMPDIR:-/tmp}/olist-minio-mc.XXXXXX")'
    export = 'export MC_CONFIG_DIR="${mc_config_dir}"'
    cleanup = 'rm -rf -- "${mc_config_dir}"'

    assert mktemp in initializer
    assert export in initializer
    assert "cleanup_mc_config()" in initializer
    assert cleanup in initializer
    assert "trap cleanup_mc_config EXIT HUP INT TERM" in initializer
    assert initializer.index("umask 077") < initializer.index(mktemp)
    assert initializer.index(mktemp) < initializer.index("mc alias set olist")
