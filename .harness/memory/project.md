# Project Memory

## Purpose
MindHandsHarness provides a lightweight runtime for long-running AI engineering work.

## Architecture
- Entry Router: `AGENTS.md`
- Standing roles: Coordinator and Executor only
- Runtime CLI: `.harness/bin/harness.py`
- Long-term context: `.harness/context/` and `.harness/memory/`
- Current task state: `.harness/runtime/`
- External skill index: `.harness/skills/registry.json`

## Stable Constraints
- Do not restore Reader/Coder/Tester/Reviewer/Memory Curator as standing roles.
- Use Executor modes instead: `inspect`, `execute`, `verify`, `review`.
- Keep `AGENTS.md` short and route-specific.
- Put detailed behavior in role files, policies, templates, memory, and scripts.
- Treat memory as project state, not a transcript.
