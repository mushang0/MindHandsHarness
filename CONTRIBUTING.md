# Contributing to MindHandsHarness

Thanks for considering a contribution. MindHandsHarness is early, so the best contributions are small, well-tested improvements to the harness protocol, CLI behavior, documentation, and regression coverage.

## Development Setup

MindHandsHarness currently uses only the Python standard library.

Run the regression tests:

```bash
python3 .harness/test_harness_cli.py
```

Run syntax checks:

```bash
PYTHONPYCACHEPREFIX=/tmp/mindhandsharness_pycache \
  python3 -m py_compile .harness/bin/harness.py .harness/test_harness_cli.py
```

Run the harness health check:

```bash
python3 .harness/bin/harness.py doctor
```

## Contribution Guidelines

- Keep the protocol-first design simple.
- Preserve auditability: task IDs, session events, specs, and archives should remain traceable.
- Add or update regression tests for CLI behavior changes.
- Avoid adding dependencies unless there is a strong reason.
- Do not commit `.harness/runtime/`, `.harness/sessions/`, `.harness/tasks/`, or local generated logs.

## Pull Request Checklist

- [ ] The change has a clear purpose and narrow scope.
- [ ] `python3 .harness/test_harness_cli.py` passes.
- [ ] `python3 .harness/bin/harness.py doctor` passes in a clean state.
- [ ] Documentation has been updated when behavior changes.
- [ ] Runtime artifacts are not included.

