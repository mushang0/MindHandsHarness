# AI Agents Entry Point

Welcome to the **Managed Agent Harness** system. This project uses a decoupled architecture to manage complexity and maintain a "clean" high-level planning context.

## Operational Mode: Protocol-First

This is a **Protocol-First Harness**. There is no external model dispatcher; `harness.py` automates local bookkeeping, Role-slot tracking, and prompt preparation. Every AI agent MUST follow the communication protocols and act based on their assigned Role (e.g. Reader, Coder) via `.harness/worker_bootstrap.md`.

## Instructions for AI Assistants

Before taking any action, you MUST follow these steps:

1. **Identify Your Role**: Check your current assignment. Are you the **Coordinator** or a **Worker**?
2. **Read the Harness Config**: Review [.harness/config.yaml](file:///.harness/config.yaml).
3. **Use the Harness CLI**: If you are the **Coordinator**, you MUST use `python3 .harness/bin/harness.py` to manage sessions, tasks, and events. Do not ask the user to do this.
4. **Load Role Specifics**: Read your role definition in [.harness/roles/](file:///.harness/roles/).
5. **Access Memory**: Search [.harness/memory/](file:///.harness/memory/) for relevant project facts and rules.
6. **Follow Protocols**: All communication between roles MUST follow the templates in [.harness/protocols/](file:///.harness/protocols/).

## System Boundary Rules

- **Information Gatekeeping**: Do not pollute the Coordinator's context with raw logs or large file contents. Use structured summaries from Worker Results.
- **Persistence**: All key events must be recorded in [.harness/sessions/](file:///.harness/sessions/) using the manual event format.
- **Memory Promotion**: Valuable findings should be proposed for memory update via the `memory-curator` role.

