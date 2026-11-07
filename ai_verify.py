"""Evidence-first verifier for *trusted local* AI-generated Python examples.

Runs independent, JSON-defined behavioral cases in fresh subprocesses.
Each test is timed out independently. This is NOT a security sandbox.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


class VerificationError(Exception):
    """Invalid verifier input or configuration."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_spec(path: Path) -> dict:
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"Cannot read valid JSON spec: {exc}") from exc
    if not isinstance(spec, dict) or spec.get("schema") != 1:
        raise VerificationError("Spec must be an object with schema: 1")
    function = spec.get("function")
    if not isinstance(function, str) or not re.fullmatch(r"[A-Za-z_]\w*", function, re.ASCII):
        raise VerificationError("Spec function must be a Python identifier")
    cases = spec.get("cases")
    if not isinstance(cases, list) or not cases:
        raise VerificationError("Spec requires at least one case")
    ids = set()
    for position, case in enumerate(cases):
        if not isinstance(case, dict):
            raise VerificationError(f"Case {position} must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", case_id):
            raise VerificationError(f"Case {position} needs a safe non-empty id")
        if case_id in ids:
            raise VerificationError(f"Duplicate case id: {case_id}")
        ids.add(case_id)
        if not isinstance(case.get("args"), list):
            raise VerificationError(f"Case {case_id} args must be a list")
        if "expected" not in case:
            raise VerificationError(f"Case {case_id} lacks expected value")
    return spec


def run_case(candidate: Path, function: str, case: dict, timeout: float) -> dict:
    request = json.dumps({"args": case["args"]}, ensure_ascii=False, allow_nan=False)
    command = [sys.executable, "-I", str(Path(__file__).resolve().parent / "worker.py"), str(candidate), function]
    try:
        completed = subprocess.run(
            command, input=request, text=True, capture_output=True, timeout=timeout,
            check=False, cwd=str(Path(__file__).resolve().parent),
        )
    except subprocess.TimeoutExpired:
        return {"id": case["id"], "status": "FAIL", "reason": "TIMEOUT"}
    if completed.returncode:
        return {
            "id": case["id"], "status": "FAIL", "reason": "EXECUTION_ERROR",
            "detail": completed.stderr.strip()[:400] or f"Exit {completed.returncode}",
        }
    try:
        response = json.loads(completed.stdout)
        if not isinstance(response, dict) or response.get("ok") is not True or "value" not in response:
            raise ValueError("Missing expected worker response")
    except (json.JSONDecodeError, ValueError) as exc:
        return {"id": case["id"], "status": "FAIL", "reason": "INVALID_RESPONSE", "detail": str(exc)[:400]}
    actual = response["value"]
    if type(actual) is type(case["expected"]) and actual == case["expected"]:
        return {"id": case["id"], "status": "PASS"}
    return {
        "id": case["id"], "status": "FAIL", "reason": "WRONG_ANSWER",
        "expected": case["expected"], "actual": actual,
    }


def verify(candidate: Path, spec_path: Path, timeout: float = 2.0) -> dict:
    candidate = candidate.resolve()
    spec_path = spec_path.resolve()
    if timeout <= 0 or timeout > 60:
        raise VerificationError("Timeout must be > 0 and <= 60 seconds")
    if not candidate.is_file():
        raise VerificationError(f"Candidate file not found: {candidate}")
    spec = load_spec(spec_path)
    checks = [run_case(candidate, spec["function"], case, timeout) for case in spec["cases"]]
    passed = sum(case["status"] == "PASS" for case in checks)
    return {
        "schema": 1,
        "candidate_sha256": sha256_file(candidate),
        "spec_sha256": sha256_file(spec_path),
        "function": spec["function"],
        "verdict": "PASS" if passed == len(checks) else "FAIL",
        "passed": passed,
        "total": len(checks),
        "cases": checks,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, type=Path, help="Trusted Python module to check")
    parser.add_argument("--spec", required=True, type=Path, help="Independent behavioral spec JSON")
    parser.add_argument("--timeout", type=float, default=2.0, help="Seconds allowed per test (default 2)")
    parser.add_argument("--report", type=Path, help="Optional JSON report destination")
    args = parser.parse_args(argv)
    try:
        report = verify(args.candidate, args.spec, args.timeout)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{report['verdict']}: {report['passed']}/{report['total']} cases passed")
        for case in report["cases"]:
            print(f"  {case['status']:4} {case['id']} {case.get('reason', '')}".rstrip())
        return 0 if report["verdict"] == "PASS" else 1
    except (VerificationError, OSError, ValueError, TypeError) as exc:
        print(f"VERIFIER_ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
