# Protocol: Task Packet

This template is used by the **Coordinator Brain** to dispatch a specific task to a **Worker Hand**.

---

## Task Metadata
- **Task ID**: [Unique ID, e.g., T-2026-05-14-001]
- **Worker Type**: [Reader | Coder | Tester | Reviewer]
- **Priority**: [Low | Medium | High | Critical]

## Objective
[Clear, concise description of what the worker needs to achieve.]

## Context & Scope
- **Files Allowed**: [List of files or directories]
- **Relevant Snippets**: [Links to specific code or previous findings]
- **Excluded Areas / Non-Goals**: [What the worker should NOT touch or look at]

## Permissions
- **Read**: [Allowed paths]
- **Write**: [Allowed paths or None]
- **Shell**: [Allowed commands or None]
- **Network**: [Allowed | Forbidden]

## Context Budget
- **Max files to inspect**: [Number]
- **Max snippets to return**: [Number]
- **Max output length**: [e.g., 1000 tokens]

## Success Criteria
- [e.g., All tests in X file must pass]
- [e.g., Provide a summary of the logic in Y]

## Escalation Conditions
Stop and report back if:
- Required file is missing or inaccessible.
- Scope is significantly larger than expected.
- Task conflicts with existing memory or constraints.
- Environment setup is missing or unknown.

## Rollback Plan
[How to revert if this worker modifies files, e.g., git checkout -- file]

## Output Format
- **Format**: [Summary | Patch | Evidence List]
- **Required Fields**: [e.g., Conclusion, Evidence, Risks]
