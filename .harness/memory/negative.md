# Negative Memory

## Avoid Restoring Old Role Chain
- scope: architecture
- avoid: Reader -> Spec -> Coder -> Tester -> Reviewer -> Memory Curator as a default route
- replacement: Coordinator decides, Executor acts, scripts manage state
- reason: long role chains waste attention and increase prompt drift

## Avoid Full Logs In Coordinator Context
- scope: context loading
- avoid: pasting complete command output or large logs into Coordinator context
- replacement: save logs under task `logs/` and summarize relevant evidence
- reason: noisy execution context degrades handoff quality

## Avoid Copying External Skills Into Harness
- scope: skill management
- avoid: requiring users to move downloaded skills into `.harness/skills`
- replacement: index external skill locations in registry files
- reason: users already manage skills in editor or agent-specific directories
