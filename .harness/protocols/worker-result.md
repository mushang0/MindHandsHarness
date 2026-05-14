# Protocol: Worker Result

This template is used by **Worker Hands** to report their findings or work back to the **Coordinator Brain**.

---

## Task Metadata
- **Task ID**: [Matching Task ID from Packet]
- **Worker ID**: [Identity of the worker]
- **Status**: [Success | Partial Success | Failure | Blocked]

## Executive Summary
[A high-level summary of what was accomplished, max 5 bullet points.]

## Output Budget
- **Evidence items**: max 10 items.
- **Evidence format**: file path + line range + one-sentence explanation.
- **Log limit**: Raw logs > 30 lines MUST be saved to `.harness/logs/` and referenced.
- **File limit**: Do not include full file contents unless explicitly requested.

## Detailed Findings / Evidence
[Specific details, links to files, or references to .harness/logs/.]

## Actions Taken
- [e.g., Read file X]
- [e.g., Applied patch to Y]
- [e.g., Ran test command Z]

## Risks & Issues
[Any unexpected findings, side effects, or blockers encountered during the task.]

## Execution Blockers / Factual Handover
[Only list factual blockers or execution-level follow-ups. Do NOT provide strategic or architectural recommendations.]

## Proposed Memory Updates
[List any new facts or rules discovered that should be moved to long-term memory.]
