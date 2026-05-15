# Security Policy

MindHandsHarness is a local protocol-first harness. It prepares prompts, state files, and audit logs for human-operated agent workflows.

## Supported Versions

The project is pre-1.0. Security fixes will target the latest `main` branch until versioned releases begin.

## Reporting a Vulnerability

Please do not open a public issue for sensitive security problems. Use GitHub private vulnerability reporting once the repository is public, or contact the maintainer through the published repository contact method.

Include:

- A short description of the issue.
- Steps to reproduce.
- Affected files or commands.
- Expected impact.
- Suggested fix, if known.

## Current Security Boundaries

- MindHandsHarness does not sandbox worker tools by itself.
- MindHandsHarness does not hide secrets from agents automatically.
- Worker prompts may cause agents to read or modify files according to the permissions of the environment they run in.
- Treat generated `.harness/runtime/`, `.harness/sessions/`, and `.harness/tasks/` artifacts as potentially sensitive.

Before publishing an issue, log, or archive, review it for secrets, private paths, and proprietary code.

