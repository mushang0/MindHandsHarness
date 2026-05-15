# Protocol: Worker Result

This template is used by **Worker Hands** to report their findings or work back to the **Coordinator Brain**. Depending on your assigned role, you MUST include specific mandatory blocks.

---

## Common Metadata
- **Role**: [reader | coder | tester | reviewer]
- **Status**: [Success | Partial Success | Failure | Blocked]

---

## 1. Reader Result (Mandatory Blocks)
If you are a `Reader` (Task Type: `investigation`), your output MUST be structured as:

```markdown
### Questions Answered
#### Q1: [Repeat the exact question asked by Coordinator]
- Answer:
- Evidence: [File path + line numbers]
- Confidence: [High | Medium | Low]
- Unknowns: [Any missing context]

#### Q2: ...

### Facts
[List concrete discoveries]

### Contradictions
[List any conflicts found between code, documentation, or hypotheses]

### Remaining Unknowns
[List anything that could not be verified]

### Boundary Statement
*Reader does not decide implementation. Coordinator must convert evidence into Implementation Spec.*
```

---

## 2. Coder Result (Mandatory Blocks)
If you are a `Coder` (Task Type: `implementation`), your output MUST be structured as:

```markdown
### Spec Compliance
- Fully Followed: [List spec items executed exactly as requested]

### Deviations
- [List any approved deviations or Tier B choices]

### Assumptions Made
- [List any engineering assumptions made]

### Stop Conditions Encountered
- [List if you were blocked and why]

### Files Modified
- [List files modified]
```

---

## 3. Tester Result (Mandatory Blocks)
If you are a `Tester` (Task Type: `verification`), your output MUST be structured as:

```markdown
## Verification Matrix
- [Test 1]: [Description]

## Commands Run
- [Exact shell commands]

## Pass/Fail
- [Result summary]

## Evidence
- [Relevant logs or outputs]
```

---

## 4. Reviewer Result (Mandatory Blocks)
If you are a `Reviewer` (Task Type: `review`), your output MUST be structured as:

```markdown
## Spec Audit
- [Did the Coder strictly adhere to the Implementation Spec?]

## Scope Violations
- [Did the Coder take unauthorized autonomy or expand scope?]

## Risk Rating
- [Low | Medium | High]

## Required Fixes
- [List specific feedback]
```
---

## 5. Memory Curator Result (Mandatory Blocks)
If you are a `Memory Curator` (Task Type: `memory-curation`), your output MUST be structured as:

```markdown
## Proposed Memory Updates
- [List specific changes to project.md]

## Evidence
- [Reasoning/Findings backing the update]

## Verification
- [How can this memory be verified as stable?]
```
