---
name: verification
description: Use when the orchestrating agent needs independent verification that completed work aligns with the original plan, user intent, and acceptance criteria — performed by a different session than the one that did the work
---

# Verification

## Overview

Verify that completed work matches what was planned and what the user asked for. This is not a code review — it's an alignment check across plan, intent, and deliverables.

**Core principle:** The agent that did the work cannot judge whether it achieved its purpose. Verification requires an independent perspective with the original intent as the measuring stick.

**Save reports to:** `agent_docs/verification/YYYY-MM-DD-verification-<subject>.md`

## The Iron Laws

```
1. THE VERIFIER MUST BE A DIFFERENT SESSION THAN THE DOER
2. NO VERIFICATION WITHOUT THE ORIGINAL PLAN AND USER INTENT AS MEASURING STICK
```

If you don't have the plan and user intent, request them before proceeding. Never verify in a vacuum.

## When to Use

- The orchestrating agent has completed implementation phase(s) of a medium or large task
- Work produced by an implementing agent/session needs independent validation before the orchestrator accepts it
- The task involved a plan or spec that the output should align with
- User explicitly requests verification of completed work

**Don't use when:**
- Small-tier tasks (orchestrator executes directly — too lightweight for a verification phase)
- The task is code review only (use `skills:code-review` — it covers technical quality)
- Only research or planning phases completed (nothing to verify against yet)

### Relationship to `code-review`

| | `code-review` | `verification` |
|---|---|---|
| **Focus** | Technical quality of code changes | Alignment of work with plan and user intent |
| **Scope** | The diff | All deliverables (code, tests, reports, artifacts) |
| **Checks** | Correctness, safety, testing, clarity, design | Intent alignment, plan alignment, completeness, scope discipline, quality |

These skills are complementary. If the task involves code changes and a detailed technical review is warranted, the orchestrating agent should invoke `code-review` separately.

## The Process

```
WHEN verifying completed work:

1. ORIENT: Understand the original intent, plan, and acceptance criteria
2. INVENTORY: Catalog what was actually produced
3. VERIFY: Check alignment across five dimensions
4. REPORT: Write the verification report with verdict and findings
```

### Phase 1: Orient

Read — in this order:
1. The original user request (from the handoff)
2. The plan or spec (path provided in the handoff — read the file)
3. The acceptance criteria (from the handoff)
4. Any prior phase reports (research, planning) referenced in the handoff

Do NOT read the implementation session's conversation or internal reasoning. Only read its outputs. This prevents inheriting the implementer's perspective.

**Exit criterion:** You can state, in your own words, what the user wanted and what the plan said to build.

### Phase 2: Inventory

Catalog what was actually produced:
- Files created or modified (from the development report or `git diff`)
- Reports written (check `agent_docs/` subdirectories)
- Tests added or modified
- Any other artifacts

Compare this inventory against what the plan said would be produced. Note:
- Items in the plan but missing from the inventory
- Items in the inventory but not in the plan

**Exit criterion:** A complete list of what exists vs. what was planned.

### Phase 3: Verify

Check alignment across five dimensions:

#### Intent alignment
- Does the work solve what the user actually asked for?
- Would the user recognize this as what they wanted?
- Is the user's original problem addressed — not just the plan's interpretation of it?

#### Plan alignment
- Were all plan tasks completed?
- Were plan constraints respected?
- Any deviations? If so, were they documented with rationale in the development report?
- Distinguish between "deviated from plan" (flag it) and "deviated from plan for a documented reason" (note it, but don't flag as blocking)

#### Completeness
- All planned files present?
- All tests written?
- All reports produced?
- All acceptance criteria met?

#### Scope discipline
- Was only the planned scope implemented?
- Any scope creep or gold-plating (unplanned additions)?
- Any unplanned changes to files outside the plan's scope?

#### Quality
- For SE tasks: tests pass, conventions followed, no regressions
- For general tasks: accurate, well-structured, appropriate
- This is a high-level check — defer deep technical analysis to `code-review`

#### Product verification (when browser tools are available)

If the work involves a web application and Playwright CLI is available, verify the product from the user's perspective:

- Open the application in the browser and visually confirm the implemented changes match what the plan described
- Walk through the core user flow(s) that the work was supposed to enable or change
- Check that the UI reflects the user's intent — not just that it "works", but that it looks and behaves the way the user would expect
- Check the console for errors and the network panel for failed requests
- Use `skills:playwright-cli-verification` for the full process

This is not optional for web UI work. Screenshots and user flow walkthroughs provide the strongest evidence for intent alignment — stronger than reading code alone.

**Exit criterion:** Each dimension has a finding (pass, concern, or fail) with evidence.

### Phase 4: Report

Write the verification report to `agent_docs/verification/YYYY-MM-DD-verification-<subject>.md`.

**Report template:**

```markdown
# Verification: [Subject]

**Date:** YYYY-MM-DD
**Scope:** [What was verified: feature name, plan reference, file list]
**Verdict:** [pass | pass-with-concerns | fail]

## Summary

[2-3 sentences: what the work accomplished, overall assessment, key concern if any.]

## Intent Alignment

[Does the work address the user's original request? Evidence.]

## Plan Alignment

[Task-by-task comparison against the plan.]
- Task 1: [plan description] — [completed / partial / missing / deviated]
- Task 2: ...

## Completeness

- [ ] [Expected deliverable 1] — [present / absent]
- [ ] [Expected deliverable 2] — [present / absent]

## Scope Discipline

[Was the scope respected? Additions or omissions beyond the plan?]

## Quality

[High-level quality assessment.]

## Findings

### Blocking

[Issues that must be fixed before acceptance. Each with specific evidence.]

### Non-blocking

[Worth noting but not blocking. Suggestions for improvement.]

### Positive

[Things done well. Keep the report balanced.]

## Recommendation

[Specific guidance for the orchestrating agent:
- If pass: ready to accept
- If fail: specific items to remediate, with enough context for a re-delegation handoff]
```

**Verdict criteria:**
- **pass:** All five dimensions satisfied. Non-blocking findings only.
- **pass-with-concerns:** All dimensions substantially satisfied. Non-blocking findings the orchestrating agent should be aware of.
- **fail:** One or more blocking findings in any dimension. Must include specific remediation guidance.


## Constraint: Read-Only

During verification, do NOT modify implementation files. Do not fix, refactor, or "improve" anything. The report is the only deliverable. Mixing verification with implementation defeats the independence guarantee.

If you find something to fix — describe it in the report. A separate implementation session handles remediation.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Verifying only code quality, ignoring plan alignment | Check all five dimensions. Quality is one of five, not the only one |
| Accepting work that "looks good" without checking the plan | Read the plan. Compare task by task |
| Rubber-stamping because the tests pass | Tests prove code works. They don't prove the right code was written |
| Verifying from the implementer's perspective | Re-read the user's original request. Would they recognize this as what they asked for? |
| Skipping the report for a "quick check" | The report is the deliverable. No report, no verification |
| Flagging style issues as blocking | Style is a code-review concern. Focus on alignment and completeness |
| Fail verdict without remediation guidance | A fail without specific guidance forces the orchestrating agent to guess. Include actionable next steps |
| Fixing things during verification | Read-only. The report is the deliverable. A separate session handles fixes |

## The Bottom Line

**Read the plan. Read the user's intent. Compare against what was built. Check all five dimensions. Write the report. Every time.**
