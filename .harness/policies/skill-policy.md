# Skill Policy

Harness does not own external skills. It indexes where they live and loads them on demand.

## Registry

- `.harness/skills/registry.json`: machine-readable index
- `.harness/skills/registry.md`: human-readable index

## Commands

Scan a directory:

```bash
python3 .harness/bin/harness.py skills scan --path ~/.codex/skills
```

Register one skill:

```bash
python3 .harness/bin/harness.py skills register \
  --name rtk \
  --path ~/.codex/skills/rtk/SKILL.md \
  --trigger "large files,logs"
```

Resolve a skill:

```bash
python3 .harness/bin/harness.py skills resolve rtk
```

## Conflict Priority

1. system and safety constraints
2. current user instruction
3. `AGENTS.md`
4. harness role and policy files
5. task packet
6. skill instructions
7. project style

If a skill conflicts with harness flow, follow harness flow and report the conflict.
