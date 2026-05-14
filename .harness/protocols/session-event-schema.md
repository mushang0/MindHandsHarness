# Session Event JSONL Schema

Each line in a `.jsonl` file in `.harness/sessions/` must be a valid JSON object following this structure.

## Fields

- `timestamp`: (string) ISO 8601 format.
- `session_id`: (string) e.g., "S-20260514-001".
- `task_id`: (string, optional) e.g., "T-20260514-001".
- `event_type`: (string) One of the following:
    - `SESSION_START`: Initializing a new session.
    - `TASK_DISPATCH`: Coordinator sends a task packet.
    - `TOOL_CALL`: Worker uses a tool.
    - `WORKER_RESULT`: Worker reports back.
    - `MEMORY_PROPOSAL`: Memory curator proposes an update.
    - `MEMORY_COMMIT`: Memory update approved and committed.
    - `USER_INTERACTION`: Input or feedback from user.
    - `SESSION_END`: Conclusion of the session.
- `actor`: (string) [coordinator | reader | coder | tester | reviewer | curator | user].
- `summary`: (string) High-level summary of the event.
- `details_ref`: (string, optional) Link to a file in `.harness/tasks/` or `.harness/logs/`.
- `artifacts`: (array of strings, optional) List of files modified or created.
- `memory_candidates`: (array of strings, optional) List of facts proposed for memory.

## Example

```json
{
  "timestamp": "2026-05-14T14:00:00Z",
  "session_id": "S-20260514-001",
  "task_id": "T-20260514-001",
  "event_type": "TASK_DISPATCH",
  "actor": "coordinator",
  "summary": "Dispatching reader to analyze file system structure.",
  "details_ref": ".harness/tasks/T-20260514-001.md"
}
```
