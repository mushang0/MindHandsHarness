# Memory Policy

Memory is project state, not chat history. Store only facts, decisions, commands, preferences, lessons, and negative knowledge that are likely to help future sessions.

## Authority

- Executor may propose memory candidates.
- Coordinator decides whether to remember them.
- Scripts apply memory updates and maintain formatting.

## Commands

Propose memory:

```bash
python3 .harness/bin/harness.py memory propose \
  --type decision \
  --source T-YYYYMMDD-001 \
  --content "Use Executor mode verify for high-output test runs." \
  --evidence "Task result saved logs under task logs directory."
```

Apply a proposal:

```bash
python3 .harness/bin/harness.py memory apply --proposal-id P-YYYYMMDD-001
```

Apply directly:

```bash
python3 .harness/bin/harness.py memory apply \
  --type command \
  --source manual \
  --content "Run CLI tests with python3 .harness/test_harness_cli.py."
```

Show compact memory for startup:

```bash
python3 .harness/bin/harness.py memory show-boot
```

## Memory Types

- `project`: stable architecture and project facts
- `status`: current handoff state
- `decision`: choices and rationale
- `negative`: traps and anti-patterns
- `command`: reusable commands
- `file`: important files and why they matter
- `preference`: stable user preferences
- `lesson`: reusable lessons from completed work

## Quality Bar

Only write memory when it is verified, reusable, concise, and likely to prevent future confusion or repeated work.
