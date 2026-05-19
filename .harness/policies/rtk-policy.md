# RTK Policy

RTK means bounded, purpose-driven reading. The harness does not require a specific binary in this skeleton; it requires the behavior: search, summarize, slice, tail, or filter before full-load.

## Default Uses

Use rtk-style bounded reading for:

- large source files
- logs
- broad searches
- command outputs
- generated files
- unknown-size files
- old task artifacts

## Direct Full Read Allowed

- `AGENTS.md`
- role files
- policy files
- task packets
- files under 200 lines
- files marked `always_full`

## Forbidden

- do not paste full logs into Coordinator context
- do not paste huge command output into Executor result
- do not read entire large source files before search/summary/slice
- do not treat old sessions as default startup context

## Executor Result Compliance

Executor results must include:

```markdown
## Tool Policy Compliance
- Used rtk-style bounded reads for large files/logs:
- Direct full reads:
- Large output saved to logs:
```

Coordinator uses this section when deciding whether the result can be trusted.
