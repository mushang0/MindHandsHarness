# Workflow Protocol

MindHandsHarness is built around one central rule:

```text
Evidence before spec. Spec before execution. Execution before review. Review before archive.
```

## Planning Loop

```mermaid
sequenceDiagram
    participant U as User
    participant B as Coordinator Brain
    participant R as Reader Hand
    participant C as Coder Hand
    participant T as Tester/Reviewer

    U->>B: High-level goal
    B->>B: Frame goal and non-goals
    B->>R: Dispatch narrow evidence questions
    R->>B: Evidence-backed result
    B->>B: Evidence sufficiency check
    B->>B: Write and validate spec
    B->>C: Dispatch checked spec
    C->>B: Spec compliance result
    B->>T: Dispatch verification/review when needed
    T->>B: Proof and risks
    B->>U: Summary and next actions
```

## Evidence Sufficiency Checklist

Before writing an implementation spec, the Coordinator should confirm:

- Target files are known.
- Exact insertion points are known.
- Current default behavior is known.
- Input and output formats are known.
- New parameters and defaults are known.
- Risks are identified.
- Verification method is clear.
- Unknowns are turned into assumptions, stop conditions, or user questions.

## Implementation Spec Rules

The spec must include:

- `Objective`
- `Scope`
- `Required Changes`
- `Evidence References`
- `Allowed Autonomy`
- `Must Not Decide`
- `Stop Conditions`

The Coder should stop if the spec leaves a critical business or behavior decision unspecified.

## Role Boundary Rules

Reader:

- Answers the questions asked.
- Provides evidence.
- Reports unknowns.
- Does not recommend architecture or implementation strategy.

Coder:

- Implements the checked spec.
- Reports deviations and assumptions.
- Stops on forbidden or unspecified decisions.

Tester:

- Runs verification.
- Reports commands and evidence.
- Does not patch code.

Reviewer:

- Audits diff, risks, and spec compliance.
- Reports required fixes.
- Does not modify code.

## When to Repeat

Repeat Reader when:

- The evidence does not identify exact files.
- Current behavior is unclear.
- Verification strategy is unknown.
- The requested behavior conflicts with existing code or docs.

Repeat Coder when:

- Reviewer finds a spec violation.
- Tester finds a failing behavior that is covered by the spec.
- The Coder reports a stop condition that the Coordinator can resolve with a spec update.

Ask the user when:

- The decision is product or business intent.
- The code cannot answer the question.
- Multiple valid behaviors exist and none is clearly safer.

