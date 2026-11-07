"""Internal subprocess worker for trusted local Python evaluation fixtures.

Not a sandbox. Do not run unknown or hostile code on a personal device.
"""
import importlib.util
import json
import sys


def main() -> int:
    if len(sys.argv) != 3:
        raise ValueError("Expected candidate path and function name")
    candidate, function_name = sys.argv[1:]
    spec = importlib.util.spec_from_file_location("candidate_under_test", candidate)
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load candidate")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    function = getattr(module, function_name)
    if not callable(function):
        raise TypeError(f"{function_name} is not callable")
    payload = json.load(sys.stdin)
    result = function(*payload["args"])
    print(json.dumps({"ok": True, "value": result}, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        # Deliberately avoid a traceback; the test report records the failure type.
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
