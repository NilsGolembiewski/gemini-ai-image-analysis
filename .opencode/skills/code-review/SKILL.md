---
name: code-review
description: Use when reviewing code changes — PRs, diffs, branches, or post-implementation validation — produces a structured review report
---

# Code Review

## Overview

Review code to find what's wrong, what's risky, and what's unclear. A review is not a style guide audit — it's a technical assessment of whether changes are correct, safe, and maintainable.

**Core principle:** Every review finding must be actionable and justified. No vague "this could be improved" — say what's wrong and how to fix it.

**Save reports to:** `agent_docs/reviews/YYYY-MM-DD-review-<subject>.md`

## The Iron Law

```
NO REVIEW WITHOUT A WRITTEN REPORT
```

A review that exists only in conversation is a review that never happened. The report is the deliverable.

## When to Use

- Reviewing a pull request or merge request
- Reviewing a diff or branch before merge
- Post-implementation validation of a worker's changes
- Auditing code for correctness, safety, or maintainability
- User asks you to review code, a file, or a set of changes

**Don't use when:**
- Reading code to understand it (that's research, not review)
- The user just wants a quick opinion on a snippet (respond directly, no process needed)

## The Process

```
WHEN reviewing code changes:

1. SCOPE: Understand what changed and why
2. READ: Study the diff thoroughly, with full file context
3. ASSESS: Evaluate against review dimensions
4. REPORT: Write the review report with categorized findings
```

### Phase 1: Scope

Before reading code, understand the intent:

- **What is this change supposed to do?** Read the PR description, commit messages, linked issues, or delegation brief.
- **What are the acceptance criteria?** What does "correct" look like for this change?
- **What is out of scope?** Don't flag pre-existing issues unless the change makes them worse.

If no description or context is available, infer the intent from the changes themselves — but note this in the report as a gap.

### Phase 2: Read

Read the full diff. For each changed file, also read enough surrounding context to understand the change in situ.

**How to read a diff:**
- Start with the test changes. Tests reveal intent — what the author expected the code to do.
- Then read the implementation changes. Do they match what the tests expect?
- Check for files that *should* have changed but didn't (missing migration, missing config update, missing type export).
- Read changed functions in full, not just the changed lines. A correct diff can create an incorrect function.

**Don't skim.** A review that misses a bug in a file it "reviewed" is worse than no review — it creates false confidence.

### Phase 3: Assess

Evaluate the changes against these dimensions. Not all dimensions apply to every review — skip those that are irrelevant to the change at hand.

#### Correctness
- Does the code do what it claims to do?
- Are edge cases handled (null, empty, boundary values, error conditions)?
- Are there off-by-one errors, race conditions, or logic inversions?
- Do types and interfaces match across call boundaries?

#### Safety
- Could this change break existing functionality? Are there regressions?
- Are error conditions caught and handled appropriately?
- Is user input validated at system boundaries?
- Are resources properly acquired and released (connections, file handles, locks)?

#### Testing
- Do tests cover the changed behavior?
- Do tests actually exercise the changed code paths (not just exist near them)?
- Are edge cases and error conditions tested?
- Would the tests catch a regression if this code were changed again?

#### Clarity
- Is the code understandable without the PR description?
- Are names accurate and specific (not misleading or vague)?
- Is complex logic explained where it's not self-evident?
- Could a future developer modify this code without introducing bugs?

#### Design
- Does the change fit the existing architecture and patterns of the codebase?
- Is the abstraction level appropriate (not too abstract, not too concrete)?
- Are there unnecessary dependencies or coupling introduced?
- Is there duplicated logic that should be unified (or unified logic that shouldn't be)?

#### Completeness
- Does the change fully address the stated requirements?
- Are all necessary files updated (types, tests, config, docs)?
- Are there TODO comments or partial implementations left behind?

### Phase 4: Review Report

**Write the report every time. This is the deliverable of a review.**

Save to `agent_docs/reviews/YYYY-MM-DD-review-<subject>.md`.

**Report template:**

```markdown
# Review: [Subject — PR title, feature name, or change description]

**Date:** YYYY-MM-DD
**Scope:** [What was reviewed: PR number, branch, file list, or commit range]
**Verdict:** [approve | request-changes | comment-only]

## Summary

[2-3 sentences: what the change does, overall assessment, key concern if any.]

## Findings

### Critical

[Issues that must be fixed before merge. Bugs, data loss risks, security issues, broken functionality.]

- **[File:line]** — [Description of the issue. Why it's a problem. How to fix it.]

### Important

[Issues that should be fixed. Missing edge cases, inadequate tests, misleading names, design concerns.]

- **[File:line]** — [Description. Why it matters. Suggested fix.]

### Nitpicks

[Optional improvements. Style, naming preferences, minor simplifications. Author's discretion to address.]

- **[File:line]** — [Description. Suggestion.]

### Positive

[Things done well worth noting. Good patterns, thorough tests, clean abstractions. Keep the review balanced.]

- **[File:line]** — [What was done well and why it's notable.]

## Missing

[Anything expected but absent: missing tests, missing validation, missing migration, missing docs update.]

## Questions

[Things that are unclear and need author clarification before the review can be finalized.]
```

**Finding format rules:**
- Every finding references a specific file and line (or line range)
- Every finding explains *why* it's an issue, not just *that* it's an issue
- Every critical or important finding includes a suggested fix or direction
- Positive findings are not filler — only note genuinely good work

**Verdict criteria:**
- **approve:** No critical findings. Important findings are minor or debatable.
- **request-changes:** One or more critical findings, or multiple important findings that together constitute a significant risk.
- **comment-only:** Review is informational. Used when reviewing without merge authority, or when the review is advisory.


## Reviewing Without a Diff

When reviewing existing code (not a diff):
- Skip Phase 1 scope of "what changed" — instead, define what you're reviewing and why
- In Phase 2, read the code as-is rather than as a diff
- Phase 3 applies the same dimensions
- Phase 4 report uses the same template, but "Verdict" becomes an overall assessment rather than a merge decision

## Scaling Depth to the Change

| Change type | Depth | Focus |
|-------------|-------|-------|
| Config or dependency update | Quick pass | Correctness, safety, completeness |
| Small bug fix (< 20 lines) | Focused | Correctness, regression test, root cause addressed |
| Feature addition | Full review | All dimensions |
| Refactoring | Full review | Behavioral equivalence, test coverage preserved |
| Architecture change | Deep review | Design, safety, completeness, migration path |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Reviewing only the diff lines, not surrounding context | Read the full function. A correct diff can create an incorrect function |
| Flagging style issues as critical | Style is a nitpick. Bugs and safety issues are critical. Calibrate severity |
| "This could be improved" without saying how | Every finding needs a concrete suggestion or direction |
| Missing what's *not* in the diff | Check for missing tests, missing error handling, missing updates to related files |
| Rubber-stamping (approve without reading) | If you can't describe what the change does, you haven't reviewed it |
| Reviewing code you don't understand | Read the surrounding code until you understand it. Ask questions if needed |
| Skipping the report for a "quick review" | The report is the deliverable. No report, no review |

## The Bottom Line

**Read the code. Find what's wrong. Explain why it's wrong. Suggest how to fix it. Write the report. Every time.**
