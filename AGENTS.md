# MindHandsHarness Agent Router

This file is the universal entry point. It is a router and manifest, not a
warehouse for role-specific rules.

## Always Follow

1. Read this file first.
2. Determine your role: Coordinator or Executor.
3. Load only the required context for that role.
4. Use `.harness/bin/harness.py` for sessions, tasks, maps, memory, skills, and status.
5. Use progressive loading before reading source or logs in full.
6. Do not guess missing context. Load the relevant map, memory, policy, or task packet.

## Global Priority

1. User instruction
2. System and safety constraints
3. `AGENTS.md`
4. Harness role file
5. Task packet
6. Project memory
7. External skill instructions

## Role Routing

### Coordinator

Load:

1. `.harness/context/boot.md`
2. `python3 .harness/bin/harness.py context boot`
3. `.harness/roles/coordinator.md`

Then load on demand:

- `.harness/context/project-map.md`
- `.harness/context/project-map.index.json`
- `.harness/policies/context-loading.md`
- `.harness/policies/rtk-policy.md`
- `.harness/policies/memory-policy.md`
- `.harness/policies/skill-policy.md`
- `.harness/memory/*.md`

Coordinator decides, plans, gates context, creates task packets, reviews Executor
results, and applies approved memory updates.

### Executor

Load:

1. `.harness/roles/executor.md`
2. the assigned task packet
3. policies referenced by the task packet

Executor acts within the task packet. Executor may inspect, edit, run commands,
validate, and report, but must not redefine the objective or update long-term
memory directly.

## Context Loading Rule

Use this order:

1. Boot/status/recent summary
2. Project map and memory
3. rtk-style search or summary
4. targeted file ranges
5. full read only when the file is small, protocol-like, or explicitly justified

For non-trivial targeted reads, record a probe with:

```bash
python3 .harness/bin/harness.py context probe ...
```

For memory handoff, prefer:

```bash
python3 .harness/bin/harness.py memory show-boot
```

## Standing Roles

MindHandsHarness v2 has only two standing roles:

- Coordinator
- Executor

Reader, Coder, Tester, Reviewer, and Memory Curator are no longer standing
roles. Their useful behaviors are Executor task modes: `inspect`, `execute`,
`verify`, and `review`.

## Scripted Handoff

Task packets, Executor prompts, Executor results, context probes, logs, artifacts,
memory proposals, and session events must live under `.harness/runtime/`. Do not
use chat history as the source of truth for project state.
