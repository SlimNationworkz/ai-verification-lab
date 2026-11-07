"""Independent tests that ensure the verifier rejects negative controls."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ai_verify import VerificationError, load_spec, verify  # noqa: E402


class VerifierTests(unittest.TestCase):
    def test_correct_candidate_passes_all_cases(self):
        report = verify(ROOT / "examples/fixed.py", ROOT / "specs/usernames.json")
        self.assertEqual(report["verdict"], "PASS")
        self.assertEqual(report["passed"], 7)
        self.assertEqual(report["total"], 7)
        self.assertEqual(len(report["candidate_sha256"]), 64)
        self.assertEqual(len(report["spec_sha256"]), 64)

    def test_intentionally_buggy_candidate_fails(self):
        report = verify(ROOT / "examples/buggy.py", ROOT / "specs/usernames.json")
        self.assertEqual(report["verdict"], "FAIL")
        failures = {case["id"]: case["reason"] for case in report["cases"] if case["status"] == "FAIL"}
        self.assertEqual(failures["case_insensitive"], "WRONG_ANSWER")
        self.assertEqual(failures["blank_entries"], "WRONG_ANSWER")
        self.assertIn("mixed", failures)

    def test_timeout_is_recorded_as_failure(self):
        report = verify(ROOT / "examples/hanging.py", ROOT / "specs/usernames.json", timeout=0.15)
        self.assertEqual(report["verdict"], "FAIL")
        self.assertTrue(all(case.get("reason") == "TIMEOUT" for case in report["cases"]))

    def test_duplicate_case_ids_are_rejected(self):
        spec = {"schema": 1, "function": "unique_usernames", "cases": [
            {"id": "same", "args": [], "expected": []},
            {"id": "same", "args": [], "expected": []},
        ]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "spec.json"
            path.write_text(json.dumps(spec))
            with self.assertRaisesRegex(VerificationError, "Duplicate"):
                load_spec(path)

    def test_missing_expected_is_rejected(self):
        spec = {"schema": 1, "function": "f", "cases": [{"id": "a", "args": []}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "spec.json"
            path.write_text(json.dumps(spec))
            with self.assertRaisesRegex(VerificationError, "lacks expected"):
                load_spec(path)

    def test_cli_exit_codes_match_evidence(self):
        for candidate, expected_code in (("fixed.py", 0), ("buggy.py", 1)):
            with self.subTest(candidate=candidate):
                result = subprocess.run(
                    [sys.executable, str(ROOT / "ai_verify.py"), "--candidate", str(ROOT / "examples" / candidate),
                     "--spec", str(ROOT / "specs/usernames.json")],
                    capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, expected_code, result.stdout + result.stderr)

    def test_error_exit_code_is_distinct_from_failing_candidate(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "ai_verify.py"), "--candidate", str(ROOT / "examples/fixed.py"),
             "--spec", str(ROOT / "specs/nonexistent.json")],
            capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("VERIFIER_ERROR", result.stderr)


if __name__ == "__main__":
    unittest.main()
