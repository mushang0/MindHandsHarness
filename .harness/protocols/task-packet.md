# Task Packet Protocol

When a Coordinator dispatches a Worker, a `Task Packet` is generated. To enforce strict role boundaries, every task MUST have an explicitly defined `Task Type`.

## Supported Task Types and Boundaries

- **`investigation`**: Used for `Reader` workers. The worker must ONLY answer specific questions and collect evidence. They must NOT suggest implementation plans or modify code.
- **`implementation`**: Used for `Coder` workers. The worker must strictly execute the provided `Implementation Spec`. They must NOT design high-level logic, change scope, or alter defaults not specified in the spec.
- **`verification`**: Used for `Tester` workers. The worker must ONLY verify the system against defined criteria.
- **`review`**: Used for `Reviewer` workers. The worker must audit the diff against the `Implementation Spec` to ensure no unauthorized deviations occurred.
- **`memory-curation`**: Used for `Memory Curator` workers. The worker must only propose updates to long-term project memory based on *verified* facts, never unverified assumptions.

The `Task Type` dictates what the worker is allowed to do. A worker receiving an `investigation` task must never write code. A worker receiving an `implementation` task must never act as a primary investigator.
