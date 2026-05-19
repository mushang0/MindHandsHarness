# Important Files

## Entry
- `AGENTS.md`: universal router and manifest

## Runtime
- `.harness/bin/harness.py`: CLI for sessions, maps, tasks, memory, skills, status, and doctor checks
- `.harness/runtime/state.json`: current runtime state
- `.harness/runtime/sessions/`: session events and task artifacts

## Role Files
- `.harness/roles/coordinator.md`: decision and context gatekeeping rules
- `.harness/roles/executor.md`: action executor rules and modes

## Policies
- `.harness/policies/context-loading.md`: progressive loading and context probe protocol
- `.harness/policies/rtk-policy.md`: bounded reading rules
- `.harness/policies/memory-policy.md`: memory proposal/application rules
- `.harness/policies/skill-policy.md`: external skill registry rules
