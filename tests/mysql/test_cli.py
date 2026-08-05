from __future__ import annotations

import tempfile
import unittest
from contextlib import redirect_stderr
from decimal import Decimal
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from scripts.simulation.cli import parser, sanitize_error_message, settings_from_args


class MySQLCommandLineContractTests(unittest.TestCase):
    def test_mysql_environment_and_random_seed_contract(self) -> None:
        environment = {
            "MYSQL_HOST": "mysql",
            "MYSQL_PORT": "3307",
            "MYSQL_DATABASE": "olist_oltp",
            "MYSQL_USER": "olist_simulator",
            "MYSQL_PASSWORD_FILE": "/run/secrets/mysql_simulator_password",
            "MYSQL_CONNECT_TIMEOUT": "17",
        }
        with patch.dict("os.environ", environment, clear=True):
            arguments = parser().parse_args(
                [
                    "run",
                    "--random-seed",
                    "20260801",
                    "--event-limit",
                    "2",
                ]
            )
        self.assertEqual(arguments.host, "mysql")
        self.assertEqual(arguments.port, 3307)
        self.assertEqual(arguments.database, "olist_oltp")
        self.assertEqual(arguments.user, "olist_simulator")
        self.assertEqual(arguments.random_seed, 20260801)
        self.assertEqual(arguments.connect_timeout, 17)
        self.assertFalse(hasattr(arguments, "password"))
        self.assertEqual(
            arguments.password_file,
            "/run/secrets/mysql_simulator_password",
        )

    def test_legacy_seed_flag_is_only_an_alias_for_random_seed(self) -> None:
        arguments = parser().parse_args(
            ["seed", "--archive", "fixture.zip", "--seed", "101"]
        )
        self.assertEqual(arguments.random_seed, 101)

    def test_settings_read_the_secret_file_without_plaintext_cli_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            password_file = Path(directory) / "mysql-password"
            password_file.write_text("secret-value\n", encoding="utf-8")
            arguments = parser().parse_args(
                [
                    "status",
                    "--host",
                    "mysql",
                    "--password-file",
                    str(password_file),
                ]
            )
            settings = settings_from_args(arguments)
        self.assertEqual(settings.host, "mysql")
        self.assertEqual(settings.password_file, password_file)
        self.assertFalse(hasattr(settings, "password"))

    def test_settings_require_a_valid_password_file_from_cli_or_environment(
        self,
    ) -> None:
        with patch.dict(
            "os.environ",
            {"MYSQL_PASSWORD": "must-not-be-accepted"},
            clear=True,
        ):
            arguments = parser().parse_args(["status"])
        with self.assertRaisesRegex(ValueError, "MYSQL_PASSWORD_FILE"):
            settings_from_args(arguments)

        with tempfile.TemporaryDirectory() as directory:
            password_file = Path(directory) / "mysql-password"
            for content, message in (
                ("", "non-empty"),
                ("first\nsecond\n", "exactly one line"),
            ):
                with self.subTest(content=content):
                    password_file.write_text(content, encoding="utf-8")
                    arguments = parser().parse_args(
                        ["status", "--password-file", str(password_file)]
                    )
                    with self.assertRaisesRegex(ValueError, message):
                        settings_from_args(arguments)

    def test_replay_speed_is_normalized_before_execution(self) -> None:
        arguments = parser().parse_args(
            [
                "replay",
                "--random-seed",
                "7",
                "--speed-multiplier",
                "1.23456",
            ]
        )
        self.assertEqual(arguments.speed_multiplier, Decimal("1.2346"))

    def test_replay_speed_rejects_values_not_storable_as_decimal_12_4(self) -> None:
        for value in ("0.000049", "99999999.99995", "NaN"):
            with (
                self.subTest(value=value),
                redirect_stderr(StringIO()),
                self.assertRaises(SystemExit),
            ):
                parser().parse_args(
                    [
                        "replay",
                        "--random-seed",
                        "7",
                        "--speed-multiplier",
                        value,
                    ]
                )

    def test_error_sanitizer_removes_secret_labels_and_mysql_uri_passwords(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            password_file = Path(directory) / "mysql-password"
            password_file.write_text("literal-secret\n", encoding="utf-8")
            result = sanitize_error_message(
                "password=literal-secret mysql://user:uri-secret@mysql/olist_oltp",
                str(password_file),
            )
        self.assertNotIn("literal-secret", result)
        self.assertNotIn("uri-secret", result)
        self.assertEqual(result.count("[REDACTED]"), 2)


if __name__ == "__main__":
    unittest.main()
