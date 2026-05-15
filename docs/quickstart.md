# Quick Start

This guide walks through one complete MindHandsHarness mission.

## 1. Check the Harness

```bash
python3 .harness/bin/harness.py status
python3 .harness/bin/harness.py doctor
```

Expected clean output:

```text
Active Session: None
Active Mission: None
Active Stage:   idle
Spec Status:    missing
OK! All checks passed.
```

## 2. Start a Mission

```bash
python3 .harness/bin/harness.py start "Implement the requested feature"
```

This creates:

- An active session ID.
- An active mission ID.
- `.harness/runtime/current/mission.json`.
- Session events in `.harness/sessions/`.

## 3. Dispatch a Reader

Reader tasks should be narrow and evidence-driven.

```bash
python3 .harness/bin/harness.py dispatch-role \
  --role Reader \
  --objective "Find the files and behavior relevant to the requested feature" \
  --questions "Which files own this behavior?; What exact insertion points matter?; What default behavior must not change?; What unknowns remain?"
```

Then print instructions:

```bash
python3 .harness/bin/harness.py worker-instructions
```

Open a new agent window and paste the printed worker instruction.

## 4. Collect the Reader Result

After the worker replies `Completed.`:

```bash
python3 .harness/bin/harness.py collect-role --role Reader
```

The Coordinator should now decide whether the evidence is sufficient. If not, dispatch another Reader with narrower questions.

## 5. Create and Check the Spec

```bash
python3 .harness/bin/harness.py write-spec
```

Edit:

```text
.harness/runtime/current/implementation_spec.md
```

The spec should include:

- Objective.
- Scope.
- Required changes.
- Evidence references.
- Allowed autonomy.
- Must-not-decide boundaries.
- Stop conditions.

Validate and freeze a versioned snapshot:

```bash
python3 .harness/bin/harness.py spec-check
```

Successful checks create:

```text
.harness/runtime/current/specs/implementation_spec.v001.md
```

## 6. Dispatch a Coder

```bash
python3 .harness/bin/harness.py dispatch-role \
  --role Coder \
  --objective "Implement the checked implementation spec"
```

Print worker instructions again:

```bash
python3 .harness/bin/harness.py worker-instructions
```

Open a new worker window and run the Coder.

## 7. Collect, Verify, Review

```bash
python3 .harness/bin/harness.py collect-role --role Coder
```

For higher-risk changes, dispatch Tester and Reviewer roles:

```bash
python3 .harness/bin/harness.py dispatch-role \
  --role Tester \
  --objective "Verify the implementation against the checked spec"

python3 .harness/bin/harness.py dispatch-role \
  --role Reviewer \
  --objective "Audit the diff for spec compliance and scope violations"
```

## 8. Archive

When the mission is complete:

```bash
python3 .harness/bin/harness.py archive-current
```

The archive preserves:

- Mission metadata.
- Mission state.
- Per-task prompts and results.
- Versioned specs.
- Session event references.

