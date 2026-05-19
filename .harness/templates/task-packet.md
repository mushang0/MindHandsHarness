# Task Packet Template

## Task ID

## Title

## Mode
inspect | execute | verify | review

## Objective

## Background

Use only relevant facts from boot context, project map, memory, and context probes. Do not invent implementation details that were not established by evidence.

## Allowed Scope

Files, directories, and commands Executor may use.

## Forbidden Scope

Files, directories, behaviors, or decisions Executor must not touch.

## Steps

Concrete ordered steps. If a step requires new scope, Executor must block instead of expanding silently.

## Tool Policy
- Use rtk-style bounded reads for large files, logs, generated files, and broad searches.
- Save large outputs under the task `logs/` directory.

## Validation

## Output Required
- `executor_result.md` with Status, Changed Files, Commands Run, Validation, Issues, Tool Policy Compliance, Memory Candidates, Next Suggested Action.
- `memory_candidates.md` may be created by `task collect` from the result.
- `context-probes.md` records Coordinator reads relevant to this task.
