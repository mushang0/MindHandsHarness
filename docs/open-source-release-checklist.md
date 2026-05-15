# Open Source Release Checklist

Use this checklist before publishing MindHandsHarness on GitHub.

## Repository Hygiene

- [ ] Remove local runtime artifacts:
  - `.harness/runtime/`
  - `.harness/sessions/`
  - `.harness/tasks/`
  - `.harness/logs/`
- [ ] Remove `.DS_Store` files.
- [ ] Confirm `.gitignore` excludes runtime artifacts.
- [ ] Confirm `README.md` renders correctly on GitHub.
- [ ] Confirm Mermaid diagrams render correctly.

## Validation

- [ ] Run regression tests:

```bash
python3 .harness/test_harness_cli.py
```

- [ ] Run syntax checks:

```bash
PYTHONPYCACHEPREFIX=/tmp/mindhandsharness_pycache \
  python3 -m py_compile .harness/bin/harness.py .harness/test_harness_cli.py
```

- [ ] Run health check:

```bash
python3 .harness/bin/harness.py doctor
```

## Required Files

- [ ] `README.md`
- [ ] `LICENSE`
- [ ] `CONTRIBUTING.md`
- [ ] `CODE_OF_CONDUCT.md`
- [ ] `SECURITY.md`
- [ ] `.gitignore`
- [ ] `docs/quickstart.md`
- [ ] `docs/quickstart.zh-CN.md`
- [ ] `docs/architecture.md`
- [ ] `docs/architecture.zh-CN.md`
- [ ] `docs/workflow-protocol.md`
- [ ] `docs/workflow-protocol.zh-CN.md`
- [ ] `docs/open-source-release-checklist.md`
- [ ] `.github/workflows/tests.yml`
- [ ] `.github/PULL_REQUEST_TEMPLATE.md`
- [ ] `.github/ISSUE_TEMPLATE/bug_report.md`
- [ ] `.github/ISSUE_TEMPLATE/feature_request.md`

## GitHub Repository Settings

- [ ] Set repository description:

```text
Protocol-first managed agents for separating the coordinator brain from worker hands.
```

- [ ] Add topics:

```text
ai-agents, agent-harness, coding-agents, multi-agent, llm, workflow, prompt-engineering
```

- [ ] Enable private vulnerability reporting if available.
- [ ] Decide whether Issues and Discussions should be enabled.
- [ ] Add a social preview image later.

## First Release

Suggested first tag:

```text
v0.1.0
```

Suggested release title:

```text
MindHandsHarness v0.1.0 - protocol-first managed agent harness
```

Suggested release notes:

```markdown
Initial public release of MindHandsHarness.

Highlights:
- Coordinator/Worker role protocol.
- Local harness CLI.
- Evidence-backed implementation specs.
- Versioned spec snapshots.
- Per-task artifacts.
- JSONL session events.
- Archive and doctor commands.
- Regression tests for core harness behavior.
```
