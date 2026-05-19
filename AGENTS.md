# MindHandsHarness Agent Router

This file is the universal entry point for AI agents interacting with the project. It outlines the role-routing protocol and commands that you, the AI agent, must execute automatically.

> [!IMPORTANT]
> **Zero-User CLI Execution**:
> You (the AI model/agent) are responsible for executing all `.harness/bin/harness.py` commands using your terminal execution tools. The user does not run these commands. You must inspect project status and run commands as needed to keep harness state synchronized.

## Always Follow

1. **Read this file first** to orient yourself.
2. **Determine your role**: `Coordinator` (strategic brain) or `Executor` (scoped worker).
3. **Check initialization**: Look for `.harness/runtime/state.json`. If it does not exist or the harness skeleton is missing, run:
   ```bash
   python3 .harness/bin/harness.py init
   ```
4. **Load only required context** for your role using progressive loading. Do not perform broad file reading until status, maps, and memory are loaded.
5. **Use the CLI to manage state**: Always use `harness.py` for starting sessions, dispatching tasks, updating maps, applying memory, and checking status.

## Role Routing

### Coordinator (Decision Maker)

Load the following context sequentially:
1. `.harness/context/boot.md`
2. Run `python3 .harness/bin/harness.py context boot` to view current runtime state.
3. `.harness/roles/coordinator.md`
4. On-demand files: project maps, memory files, and policies.

#### Automated Action Steps:
- **Starting a new goal**: If there is no active session or the user specifies a new goal, start a session automatically:
  ```bash
  python3 .harness/bin/harness.py start "<objective>"
  ```
- **Updating the Project Map**: Before locating files, ensure the map is up to date:
  ```bash
  python3 .harness/bin/harness.py map update
  ```
- **Dispatching Tasks**: When delegating work, create a task packet:
  ```bash
  python3 .harness/bin/harness.py task new --title "<title>" --objective "<objective>" --mode <mode> --allowed "<allowed_paths>" --steps "<steps>" --validation "<validation>"
  ```
  Immediately follow with:
  ```bash
  python3 .harness/bin/harness.py task dispatch
  ```
  Then tell the user: "I have prepared the task packet `<task_id>`. Please copy the contents of `.harness/runtime/sessions/<session_id>/tasks/<task_id>/executor_prompt.md` into a new isolated conversation to run the Executor, and paste the result or confirm when complete."
- **Collecting Task Results**: When the user reports the Executor is done, run:
  ```bash
  python3 .harness/bin/harness.py task collect
  ```
  to display the result and load memory candidates, then review the output.
- **Recording Probes**: If you need to perform a targeted read of source file lines, log it:
  ```bash
  python3 .harness/bin/harness.py context probe --purpose "<purpose>" --method "<method>" --source "<file:lines>" --result "<observations>"
  ```
- **Applying Memory**: When applying a strategic decision or lesson:
  ```bash
  python3 .harness/bin/harness.py memory apply --type <type> --source <source_task_id> --content "<content>"
  ```

### Executor (Task Worker)

When starting in Executor mode, perform the following initialization automatically:
1. Read `.harness/runtime/state.json` to locate the `active_session_id` and `active_task_id`.
2. Read `.harness/roles/executor.md`.
3. Read the assigned task packet or prompt file: `.harness/runtime/sessions/<session_id>/tasks/<task_id>/executor_prompt.md` (or `task.md`).

#### Rules:
- Perform the scoped work within the allowed paths.
- Write your execution result to `.harness/runtime/sessions/<session_id>/tasks/<task_id>/executor_result.md` following the template.
- Do not modify files outside the allowed scope or update long-term memory.

## Global Priority

1. User instruction
2. System and safety constraints
3. `AGENTS.md`
4. Role instructions (`coordinator.md` / `executor.md`)
5. Task packet
6. Project memory

