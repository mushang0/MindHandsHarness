# MindHandsHarness

MindHandsHarness is a lightweight Coordinator/Executor harness for long-running
AI software work. It keeps the model-facing flow short and moves durable state
into scripts, maps, task packets, memory files, and session logs.

## Core Model

```text
User
  -> Coordinator
       decides, gates context, writes task packets, reviews results, updates memory
  -> Executor
       acts within a task packet, validates, reports, proposes memory candidates
  -> Harness Runtime
       manages maps, tasks, sessions, events, memory, skills, and boot context
```

MindHandsHarness v2 has only two standing roles:

- `Coordinator`
- `Executor`

Reader, Coder, Tester, Reviewer, and Memory Curator are not standing roles.
Their useful behaviors are Executor task modes: `inspect`, `execute`, `verify`,
and `review`.

## Why This Shape

- Project maps are created once and updated incrementally.
- `AGENTS.md` is a short router/manifest, not a role-rule warehouse.
- Coordinator can read narrowly and progressively instead of delegating every
  lookup to a Reader.
- Executor handles context-heavy action so command logs and debugging loops do
  not pollute the Coordinator context.
- Memory updates are decided by Coordinator and formatted by scripts.
- Skills are indexed where they live; the harness does not copy skill bodies.

## Design Principles

1. Few Roles, Strong Runtime
2. Coordinator Decides, Executor Acts
3. Context Before Files
4. Progressive Loading
5. Map Once, Update Incrementally
6. RTK-Style Bounded Reading By Default
7. Direct Small Actions
8. Delegate Context-Heavy Work
9. Scripted Handoff
10. Memory as Project State

## Quick Start

```bash
git clone https://github.com/mushang0/MindHandsHarness.git
cd MindHandsHarness
python3 .harness/bin/harness.py init
python3 .harness/bin/harness.py start "Your project goal"
python3 .harness/bin/harness.py context boot
```

Create and dispatch an Executor task:

```bash
python3 .harness/bin/harness.py task new \
  --title "Inspect auth flow" \
  --objective "Find the files and functions responsible for login" \
  --mode inspect \
  --allowed "src/auth, tests/auth" \
  --steps "locate login entry points; summarize relevant files" \
  --validation "no code changes"

python3 .harness/bin/harness.py task dispatch
```

Record a context probe when Coordinator reads targeted details:

```bash
python3 .harness/bin/harness.py context probe \
  --task-id T-20260519-001 \
  --purpose "confirm insertion point" \
  --method "rtk_slice" \
  --source "src/auth.py:20-80" \
  --result "login handler starts at line 31"
```

Initialize or refresh the project map:

```bash
python3 .harness/bin/harness.py map init
python3 .harness/bin/harness.py map update
python3 .harness/bin/harness.py map show
```

Apply an approved memory update:

```bash
python3 .harness/bin/harness.py memory apply \
  --type decision \
  --source T-20260519-001 \
  --content "Use Coordinator + Executor as the only standing roles."
```

Propose and then apply memory:

```bash
python3 .harness/bin/harness.py memory propose \
  --type negative \
  --source T-20260519-001 \
  --content "Do not paste full command logs into Coordinator context." \
  --evidence "Task logs exceeded useful chat context."

python3 .harness/bin/harness.py memory apply --proposal-id P-20260519-001
python3 .harness/bin/harness.py memory show-boot
```

Index external skills without copying them:

```bash
python3 .harness/bin/harness.py skills scan --path ~/.codex/skills
python3 .harness/bin/harness.py skills register \
  --name rtk \
  --path ~/.codex/skills/rtk/SKILL.md \
  --trigger "large files,logs"
python3 .harness/bin/harness.py skills resolve rtk
python3 .harness/bin/harness.py skills list
```

## Directory Structure

```text
.harness/
  bin/harness.py
  context/
    boot.md
    project-status.md
    recent-summary.md
    project-map.md
    project-map.index.json
  roles/
    coordinator.md
    executor.md
  policies/
    context-loading.md
    rtk-policy.md
    memory-policy.md
    skill-policy.md
  templates/
    task-packet.md
    executor-result.md
    memory-entry.md
  memory/
    project.md
    status.md
    decisions.md
    negative.md
    commands.md
    files.md
    user-preferences.md
    lessons.md
  runtime/
    state.json
    sessions/
    memory-proposals/
  skills/
    registry.md
    registry.json
```

## Standard Flow

```text
User request
  -> Coordinator loads boot context
  -> Coordinator checks map/memory/policies
  -> Coordinator either acts directly or creates a task packet
  -> Executor performs scoped work
  -> Executor reports result and memory candidates
  -> Coordinator reviews, validates, and applies memory when useful
```

## Tests

```bash
python3 .harness/test_harness_cli.py
```
