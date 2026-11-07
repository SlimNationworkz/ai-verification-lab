# AI Verification Lab

**Independent evidence for AI-generated code — Python-based and compatible with Android Termux.**

A small, reproducible portfolio project by **SlimNationworkz** demonstrating a
principle: **"The AI says it works" is not a verification result.**

Instead of trusting a model's explanation or a script's green output, this project:

1. Defines test expectations independently in JSON.
2. Executes a *trusted local* Python candidate in a fresh subprocess per case.
3. Checks behavioral outcomes, including case-sensitive bugs, blank inputs,
   errors, and timeouts.
4. Produces machine-readable evidence including SHA-256 content hashes.
5. Includes positive and negative controls and CI regression tests.

## Quick start (Android Termux, Linux, macOS or Windows)

Requires Python 3.10+; no third-party Python dependencies.

```sh
python ai_verify.py --candidate examples/buggy.py --spec specs/usernames.json
# Expected: FAIL with exit code 1

python ai_verify.py --candidate examples/fixed.py --spec specs/usernames.json
# Expected: PASS with exit code 0

python -m unittest discover -s tests -v
# Tests should pass
```

To write JSON reports:

```sh
python ai_verify.py --candidate examples/fixed.py --spec specs/usernames.json --report reports/fixed.json
```

See [sample failing report](evidence/buggy-report.json) and
[sample passing report](evidence/fixed-report.json), generated using Python 3.
These reports are examples; rerun the commands to independently verify results.

## What the tests prove

| Check | Expected from fixed.py | Expected from buggy.py |
| --- | --- | --- |
| Basic two names | Pass | Pass |
| Trim spaces | Pass | Pass |
| Case-insensitive duplicates | Pass | Fail |
| Ignore blank entries | Pass | Fail |
| Preserve first spelling | Pass | Fail |
| Empty input | Pass | Pass |
| Mixed edge cases | Pass | Fail |

The test suite also checks timeouts, input validation, and proper exit-code
semantics; GitHub Actions deliberately verifies that the buggy control fails.

## Why this matters for AI evaluation

This is a demonstration of an evaluation workflow, **not a claim about access to any
particular AI model's internal training or production systems**. A coding assistant
may generate plausible source that contains subtle defects. A separate test
specification and negative-control suite can expose those defects, document
the failure, and let a reviewer reproduce it.

Learn about [methodology](docs/methodology.md) and [security boundaries](SECURITY.md).

## Security boundary

**Not a security sandbox.** Never run unknown or hostile code with this tool.
Only run candidate code that you authored or independently reviewed and trust.
The worker can access files and other OS resources available to your account;
a timeout is not a security boundary. No confidential company materials are
included in this repository.

## Roadmap

- Add more independent behavioral contracts and negative controls.
- Add mutation tests that intentionally alter correct code to verify test sensitivity.
- Add reproducibility manifests for CI and additional runtimes.
- Add isolated worker execution for untrusted submissions on suitable hosts.

## License

MIT License. See [LICENSE](LICENSE).
