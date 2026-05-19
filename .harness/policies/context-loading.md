# Context Loading Policy

MindHandsHarness uses progressive loading. The goal is to give Coordinator enough evidence to decide accurately without filling its context with source dumps, logs, or worker chatter.

## Levels

### L0: Boot
- `AGENTS.md`
- `.harness/context/boot.md`
- `python3 .harness/bin/harness.py context boot`
- active role file

### L1: Orientation
- `.harness/context/project-map.md`
- `.harness/context/project-map.index.json`
- `.harness/memory/project.md`
- `.harness/memory/status.md`
- `.harness/memory/decisions.md`
- `.harness/memory/negative.md`
- relevant policies

### L2: Targeted Detail
- specific source ranges
- specific logs
- specific task packets
- specific Executor results
- specific skill entry documents

## Escalation Rule

Use this order:

1. boot/status/recent summary
2. project map and memory
3. rtk-style search or summary
4. targeted slice
5. full read only with reason

## Context Probe Protocol

For non-trivial reads, record why the context was loaded:

```bash
python3 .harness/bin/harness.py context probe \
  --task-id T-YYYYMMDD-001 \
  --purpose "confirm insertion point" \
  --method "rtk_slice" \
  --source "src/app.py:20-60" \
  --result "login handler starts at line 31"
```

This creates or updates the task `context-probes.md` file.

## Full Read Rule

Full reads are acceptable for small files, role files, policy files, `AGENTS.md`, task packets, and files explicitly marked `always_full` in the project map. Large source files, logs, generated files, and command output should be summarized or sliced first.
