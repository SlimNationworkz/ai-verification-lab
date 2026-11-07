# Verification method: requirements -> observable evidence

## Contract

For the `unique_usernames` example:
1. Strip leading/trailing whitespace.
2. Ignore empty or whitespace-only names.
3. Uniqueness is determined case-insensitively (`str.lower`).
4. Preserve the spelling of the *first* accepted name.
5. Preserve original order.

The expected outcomes in `specs/usernames.json` are authored independently of
both implementations. The checker compares real behavior, not source-code text.

## Positive and negative controls

- `examples/fixed.py` is a positive control: all specified cases should PASS.
- `examples/buggy.py` is a negative control: duplicate case variants and blanks
  must be detected as FAIL. A verifier that passes this file would be defective.
- `examples/hanging.py` is a negative control for timeout handling.

## Evidence and limits

Each report records ordered case verdicts plus SHA-256 hashes of the candidate
and the test specification. An exit status of 0 means all specified tests passed;
1 means the candidate failed at least one; 2 means the verifier could not
establish a valid verdict. The verifier is not claiming formal proof or exhaustive
correctness. More cases, code review, and an appropriately isolated execution
environment are needed for broader assurance.

Use `python -m unittest discover -s tests -v` to independently exercise the
verifier's pass, fail, timeout, invalid-spec, and exit-code behaviors.
