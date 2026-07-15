from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP_SCRIPT = PROJECT_ROOT / "docker" / "airflow" / "load-env-and-run.sh"


@unittest.skipIf(os.name == "nt", "requires a POSIX shell")
class AirflowSecretBootstrapTests(unittest.TestCase):
    def test_file_secret_normalizes_windows_crlf(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            secret_path = Path(temp_dir) / "postgres_password.txt"
            secret_path.write_bytes(b"expected-secret\r\n")

            environment = os.environ.copy()
            environment.pop("POSTGRES_PASSWORD", None)
            environment["POSTGRES_PASSWORD_FILE"] = str(secret_path)

            result = subprocess.run(
                [
                    "bash",
                    str(BOOTSTRAP_SCRIPT),
                    sys.executable,
                    "-c",
                    (
                        "import os; "
                        "assert os.environ['POSTGRES_PASSWORD'] == "
                        "'expected-secret'"
                    ),
                ],
                check=False,
                capture_output=True,
                env=environment,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
