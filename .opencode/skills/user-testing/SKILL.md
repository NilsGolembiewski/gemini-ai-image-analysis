---
name: user-testing
description: Use when you need to systematically test a web application from a real user's perspective — discovers missing entry points, incomplete CRUD, dead-end flows, and unreachable features by walking through every user flow in the browser
---

# User Testing

## Overview

Test a web application the way a first-time user would: open it, try to use every feature, and document what works, what is broken, and what is impossible to reach. This is not verification of a specific change — it is a holistic assessment of whether the application is actually usable.

**Core principle:** If a user cannot discover and complete a feature through the UI alone — without reading source code — the feature does not exist.

**Save reports to:** `agent_docs/testing/YYYY-MM-DD-user-testing-<app-name>.md`

## The Iron Law

```
EVERY CLAIMED FEATURE MUST BE REACHABLE, COMPLETABLE, AND RECOVERABLE THROUGH THE UI
```

Reachable: there is a navigation path from the entry point to the feature. Completable: the user can finish the task (full CRUD where applicable). Recoverable: errors show a message and a way forward, not a blank screen.

## When to Use

- Testing a web application holistically after a round of development
- Validating that all features described in a spec or README are actually accessible to users
- Assessing an application you are unfamiliar with to find gaps before planning further work
- After a large refactor or migration, to confirm nothing was lost from the user's perspective
- When the user asks "does this app actually work end to end?"

**Don't use when:**
- Verifying a specific UI change you just made — use `playwright-cli-verification`
- Running automated test suites — use `software-development` Phase 4
- Doing a code review — use `code-review`
- The project has no web UI (backend-only, CLI, library)

### Relationship to Other Skills

| | `user-testing` | `playwright-cli-verification` | `verification` |
|---|---|---|---|
| **Scope** | The entire application, every feature | A specific change or set of changes | Alignment of work with a plan |
| **Perspective** | First-time user who has never seen the code | Developer confirming their change works | Reviewer checking deliverables against requirements |
| **Finds** | Missing features, dead ends, unreachable UI, broken flows | Visual regressions, console errors, layout bugs | Scope drift, missing deliverables, plan misalignment |
| **Trigger** | "Test the whole app" / holistic assessment | After implementing a UI change | After a work phase completes |

## The Process

```
WHEN testing a web application from a user's perspective:

1. DISCOVER: Understand what the app is supposed to do
2. MAP: Build a feature inventory and generate user flows
3. EXECUTE: Walk through every flow in the browser
4. ANALYZE: Categorize gaps by severity
5. REPORT: Write the user testing report
```

### Phase 1: Discover — What Is This App Supposed to Do?

Before testing, you need a clear picture of what features should exist. Gather from multiple sources:

**Specs and requirements (if available):**
- Check `agent_docs/specs/` for spec documents
- Check `agent_docs/design/` for UX design documents
- Check `agent_docs/brainstorm/` for brainstorm documents
- Read the project README
- Check for a features list, user stories, or acceptance criteria

**Codebase structure (always do this):**
- Scan route definitions (look for router files, page directories, API routes)
- Scan navigation components (sidebars, headers, menus) to see what is presented to users
- Look at data models/schemas to understand the domain entities
- Check for feature flags or conditional rendering that might hide features

**The live application (always do this):**
- Open the app in the browser using Playwright CLI
- Take a snapshot and screenshot of the landing/home page
- Identify the primary navigation — what pages and features does the app advertise?
- Note what the app presents itself as (heading, tagline, onboarding text)

**Compile a feature list.** For each feature, note:
- Where you learned about it (spec, route, nav, code, live UI)
- Whether it appears in the UI navigation
- The domain entities involved (e.g., "projects", "tasks", "users")

**Exit criterion:** A written feature list with sources. You can describe what the app claims to do.

### Phase 2: Map — Generate User Flows

For each feature in the inventory, generate concrete user flows. Think like a user, not a developer.

**For every domain entity, check the CRUD lifecycle:**
- **Create:** Can the user create a new one? Is there a button, form, or entry point?
- **Read:** Can the user view a list? View a single item's details?
- **Update:** Can the user edit an existing one?
- **Delete:** Can the user remove one? Is there confirmation?

**For every feature, check entry points:**
- Can the user reach this feature from the main navigation?
- Can the user reach it from related features? (e.g., navigate from a project to its tasks)
- Is there a first-time/empty state that tells the user what to do?

**For feature relationships, check interactions:**
- If entity A belongs to entity B (e.g., tasks belong to projects), can the user navigate between them?
- If a feature depends on another (e.g., creating a task requires a project), is the dependency clear?

**Write each flow as a concrete step sequence:**

```
Flow: Create a new project
1. Open the app (landing page)
2. Navigate to the projects section
3. Click "Create project" (or equivalent)
4. Fill in the project name and details
5. Submit the form
6. Verify: the new project appears in the project list

Flow: First-time experience — empty projects list
1. Open the app with no existing data
2. Navigate to the projects section
3. Verify: empty state message is shown
4. Verify: there is a clear call-to-action to create the first project
```

**Prioritize flows by user impact:**
- P0: Core flows — the primary thing the app exists to do
- P1: Supporting flows — secondary features that complete the experience
- P2: Edge cases — error handling, empty states, boundary conditions

**Exit criterion:** A numbered list of concrete user flows covering every feature. Each flow is a step sequence, not a vague description.

### Phase 3: Execute — Walk Through Every Flow

Use Playwright CLI to execute every flow. Follow the `playwright-cli-verification` patterns for all browser interactions (snapshot-first rule, UIDs, interaction tools).

**Before starting:**
- Ensure the app is running (check for dev server, start one if needed — see `playwright-cli-verification` Phase 0)
- Open the app in the browser
- If testing empty states, clear data or use a fresh session/incognito context

**For each flow, follow this loop:**

```
FOR EACH flow:
  FOR EACH step in the flow:
    1. `playwright-cli snapshot` → understand current page, get UIDs
    2. Interact (`playwright-cli click`, `playwright-cli fill`, `playwright-cli navigate`) using UIDs from snapshot
    3. `playwright-cli snapshot` → verify the interaction had the expected result
    4. `playwright-cli screenshot` → capture visual evidence
    5. Record: PASS (step worked as expected) or FAIL (describe what went wrong)
  END

  After the flow:
    - `playwright-cli console` with types: ["error", "warn"]
    - `playwright-cli requests` → check for failed requests (4xx, 5xx)
    - Record overall flow result: PASS / PARTIAL / FAIL
END
```

**When a step fails:**
- Document exactly what happened (what you expected, what you got)
- Take a screenshot as evidence
- Note the specific gap (missing button, broken link, error message, empty page)
- **Move on to the next step or flow.** Do not stop at the first failure. The goal is to map ALL gaps, not fix the first one.

**When a step is blocked:**
- If a prerequisite is missing (e.g., cannot test "edit project" because "create project" failed), note the dependency and skip
- If the page is in an error state, note it and try navigating back to a known-good state

**Exit criterion:** Every flow has been attempted. Each step has a PASS or FAIL with evidence.

### Phase 4: Analyze — Categorize the Gaps

Review all failures and categorize them:

**Critical — Feature is impossible to use:**
- Missing entry point (no button/link to reach the feature)
- Missing create action (entity exists in the model but users cannot create one)
- Dead-end flow (action leads to error page, blank screen, or infinite loader)
- Data loss (action destroys data without confirmation or undo)

**Major — Feature is usable but broken or incomplete:**
- Incomplete CRUD (can create but not edit, can view but not delete)
- Broken navigation (link exists but leads to wrong page or 404)
- Form submission errors (validation fails silently, error not shown to user)
- Missing empty state (feature shows blank area with no guidance when empty)

**Minor — Feature works but experience is poor:**
- Missing loading states (content pops in without indication)
- Missing confirmation (destructive action with no "are you sure?")
- Unclear labels or confusing navigation
- Console errors that do not affect visible behavior
- Missing feedback after actions (no success message, no visual change)

**Informational — Not a bug, but worth noting:**
- Features found in code but intentionally hidden (behind feature flags)
- Potential accessibility issues noticed during testing
- Performance observations (slow page loads, sluggish interactions)

**Exit criterion:** Every failure is categorized by severity with specific evidence.

### Phase 5: Report

Write the user testing report to `agent_docs/testing/YYYY-MM-DD-user-testing-<app-name>.md`.

**Report template:**

```markdown
# User Testing: [App Name]

**Date:** YYYY-MM-DD
**URL:** [URL tested]
**Verdict:** [usable | usable-with-gaps | not-usable]

## Summary

[2-3 sentences: overall assessment, number of features tested, number of gaps found, most critical finding.]

## Feature Inventory

| Feature | Source | In Nav? | Testable? |
|---------|--------|---------|-----------|
| [Feature 1] | spec, routes, nav | Yes | Yes |
| [Feature 2] | routes, code | No | No — no entry point |
| ... | ... | ... | ... |

## Flow Results

### P0: Core Flows

#### [Flow Name]

**Result:** PASS / PARTIAL / FAIL

| Step | Action | Expected | Actual | Status |
|------|--------|----------|--------|--------|
| 1 | [action] | [expected result] | [actual result] | PASS/FAIL |
| 2 | ... | ... | ... | ... |

**Evidence:** [screenshot references, console errors]

### P1: Supporting Flows

[Same format]

### P2: Edge Cases

[Same format]

## Gap Analysis

### Critical

- **[Gap title]:** [Description of the gap, which flow it affects, evidence]

### Major

- **[Gap title]:** [Description, flow, evidence]

### Minor

- **[Gap title]:** [Description]

### Informational

- **[Note]:** [Description]

## Statistics

- Features inventoried: [N]
- Flows tested: [N]
- Flows passed: [N]
- Flows partial: [N]
- Flows failed: [N]
- Critical gaps: [N]
- Major gaps: [N]
- Minor gaps: [N]

## Recommendation

[What should be fixed first. Prioritized list of remediation actions.
Group by: "fix before shipping" (critical), "fix soon" (major), "fix when convenient" (minor).]
```

**Verdict criteria:**
- **usable:** All P0 flows pass. No critical gaps. Major gaps are few and non-blocking.
- **usable-with-gaps:** P0 flows mostly pass. Some critical or major gaps exist but the core experience works.
- **not-usable:** P0 flows fail. Critical gaps prevent the primary use case from working.


## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Stopping at the first failure | Test ALL flows. The goal is a complete map of gaps, not fixing the first one |
| Testing from a developer's perspective (navigating by URL) | Use only the UI. If there is no button or link to reach a feature, that is a finding |
| Skipping empty states | A first-time user sees empty states first. Test them explicitly |
| Not checking the CRUD lifecycle for every entity | For each domain entity: can the user create, read, update, and delete it through the UI? |
| Only testing what is visible in the nav | Cross-reference the nav against the codebase routes and specs. Missing nav items are critical gaps |
| Vague flow descriptions ("test the projects feature") | Every flow must be a concrete step sequence: go here, click this, type that, verify this |
| Skipping the feature discovery phase | Without knowing what SHOULD exist, you cannot find what is MISSING. Phase 1 is not optional |
| Not categorizing gaps by severity | A missing create button and a missing loading spinner are not equally important. Categorize |
| Fixing bugs during testing | This is a testing skill, not a development skill. Document the gap and move on. Fix later |
| Testing without screenshots as evidence | Every failure needs a screenshot. "It did not work" is not evidence |

## The Bottom Line

**Discover what the app should do. Map every user flow. Walk through every flow in the browser. When something fails, document it and keep going. Categorize every gap. Write the report. The question is not "does the code work?" — it is "can a user actually use this?"**
