# Planning Protocol: The Investigation Loop

To prevent hallucination and unauthorized architectural decisions by execution workers, the Coordinator MUST follow this strict 7-stage Planning Protocol before dispatching a Coder.

## Stage 1: Goal Framing
The Coordinator converts the user's high-level request into concrete engineering objectives and explicitly identifies non-goals (what we will NOT do).

## Stage 2: Investigation Questions
The Coordinator lists hypotheses, unknowns, and the specific evidence required from the codebase. 
*Example: "Is left/right swapped in notebook X vs script Y?", "Where does parameter Z default?"*

## Stage 3: Reader Dispatch
The Coordinator dispatches a `Reader` worker. Reader tasks MUST be narrow, specific, and question-driven. Broad requests like "analyze this directory" are forbidden unless exploring completely unknown territory.

## Stage 4: Evidence Sufficiency Check
Upon receiving the Reader's result, the Coordinator MUST check if it holds sufficient facts.
**Checklist:**
- [ ] Are the target files confirmed?
- [ ] Are the exact insertion points verified?
- [ ] Is the current default behavior confirmed?
- [ ] Are input/output formats confirmed?
- [ ] Are new parameters and their default values confirmed?
- [ ] Are risks identified?
- [ ] Is the verification method clear?
- [ ] Are unknown items converted into Stop Conditions or questions for the User?

## Stage 5: Repeat or Freeze
- **If insufficient**: Dispatch another Reader with refined questions.
- **If unresolvable via code**: Convert the missing information into an Assumption, a Stop Condition for the Coder, a conservative default, or ask the User.

## Stage 6: Implementation Spec
ONLY after passing the Evidence Sufficiency Check may the Coordinator write the `Implementation Spec` (`.harness/runtime/current/implementation_spec.md`). The Spec MUST be backed by Evidence References (e.g., "Insert at line X based on finding Y").

After editing the active spec, the Coordinator MUST run `python3 .harness/bin/harness.py spec-check`. A successful check freezes a versioned snapshot in `.harness/runtime/current/specs/`. Execution workers are bound to the checked snapshot; do not treat an unchecked mutable draft as executable.

## Stage 7: Execution
The `Coder` executes the Spec exactly as written. The Coder MUST NOT infer missing requirements from the Reader Result. If the Spec is lacking, the Coder MUST halt and report.
