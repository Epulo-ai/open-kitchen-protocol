"""CLI regression tests for the OKP validator's JSON parsing boundary."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
VALIDATOR = REPOSITORY / "tools" / "validate_okp.py"
EXAMPLES = sorted((REPOSITORY / "examples").glob("*.json"))


def run_validator(arguments, input_text=None):
    return subprocess.run(
        [sys.executable, str(VALIDATOR)] + arguments,
        cwd=str(REPOSITORY),
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


class ValidateOkpCliTests(unittest.TestCase):
    def assert_rejects_constant(self, constant, use_stdin):
        content = '{"confidence": ' + constant + '}'
        if use_stdin:
            result = run_validator(["-"], content)
        else:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "invalid.json"
                path.write_text(content, encoding="utf-8")
                result = run_validator([str(path)])

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid JSON constant '{}'".format(constant), result.stdout)
        self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_rejects_non_json_constants_from_file(self):
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant):
                self.assert_rejects_constant(constant, use_stdin=False)

    def test_rejects_non_json_constants_from_stdin(self):
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant):
                self.assert_rejects_constant(constant, use_stdin=True)

    def test_accepts_valid_json_numbers(self):
        for value in ("0", "-1.25", "6.02e23"):
            with self.subTest(value=value):
                result = run_validator(["-"], '{"confidence": ' + value + '}')
                self.assertEqual(result.returncode, 1)
                self.assertNotIn("invalid JSON constant", result.stdout)
                self.assertIn("not an OKP document", result.stdout)
                self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_rejects_non_json_constants_in_custom_schema(self):
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "schema.json"
                    path.write_text('{"minimum": ' + constant + '}', encoding="utf-8")
                    result = run_validator(["--schema", str(path), "-"], "{}")
                self.assertEqual(result.returncode, 2)
                self.assertIn("cannot read the schema", result.stderr)
                self.assertIn("invalid JSON constant '{}'".format(constant), result.stderr)
                self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_examples_pass_strict(self):
        result = run_validator(["--strict"] + [str(path) for path in EXAMPLES])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("[episode, 5 events]", result.stdout)
        self.assertEqual(result.stdout.count("[episode, 4 events]"), 2)


if __name__ == "__main__":
    unittest.main()
