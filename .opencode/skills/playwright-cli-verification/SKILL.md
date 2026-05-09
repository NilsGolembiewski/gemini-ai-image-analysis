---
name: playwright-cli-verification
description: Use when developing or testing web applications — systematic browser verification through Playwright CLI to visually confirm UI behavior, test user flows, check console errors, and inspect network requests
---

# Playwright CLI Verification

## Overview

Agents write web UI code but never look at the result. They rely entirely on automated tests, which cannot catch visual regressions, layout issues, missing elements, or console errors that don't crash the page. Playwright CLI gives agents the ability to see what the user sees and interact with the UI the way users do.

**Core principle:** Snapshot first, interact second, verify always. Every browser session starts with a snapshot, every interaction is verified by a follow-up snapshot or screenshot, and every session checks the console for errors.

## The Iron Law

```
NO WEB UI CHANGE SHIPS WITHOUT VISUAL VERIFICATION IN THE BROWSER
```

Automated tests prove logic works. Browser verification proves the user sees what you intended. Both are required.

## When to Use

- Implementing or modifying web application UI
- Fixing CSS or layout bugs
- Testing user interaction flows (forms, navigation, modals, dialogs)
- Verifying responsive behavior across viewport sizes
- Debugging frontend issues (console errors, failed network requests)
- Validating that a feature works end-to-end in the browser after automated tests pass

**Don't use when:**
- The project has no web UI (backend-only, CLI tools, libraries)
- Changes are purely server-side with no browser-visible impact
- You only need to run automated tests — use `software-development` Phase 4

## The Process

```
WHEN verifying web application changes in the browser:

0. SERVE: Ensure a dev server is running (local apps only)
1. OPEN: Navigate to the relevant page
2. SNAPSHOT: Take an a11y tree snapshot to understand page structure and get refs
3. VERIFY: Take a screenshot to visually confirm the UI
4. INTERACT: Test user flows — click, fill forms, navigate, run in-browser assertions
5. CHECK: Inspect console for errors and network requests for correctness
6. RESPONSIVE: Test at different viewport sizes if layout changed
```

### Phase 0: Ensure a Dev Server Is Running

**Skip this phase if the target is an already-running remote URL or a deployed site.** This phase is for local projects only.

Before navigating, verify that the application is being served:

- **Check if a server is already running.** Try navigating to the expected local URL (commonly `http://localhost:3000`, `http://localhost:5173`, or `http://localhost:8080`). If the page loads, skip to Phase 1.
- **If no server is running, start one:**
  1. Check `package.json` for a `dev`, `start`, or `serve` script. Run it in the background (e.g., `npm run dev &`).
  2. If there is no relevant script, use a static file server: `npx serve . &` from the project's build output or root directory.
  3. Wait for the server to be ready before proceeding.
- **Note the URL and port** the server reports. Use that URL in Phase 1.

### Phase 1: Open the Page

- Use `playwright-cli tab-list` to see existing pages.
- Use `playwright-cli open <url>` with the target URL, or `playwright-cli goto <url>` if a page is already open.
- Use `playwright-cli tab-select <index>` to switch between pages when testing multi-tab flows.
- Wait for the page to load before proceeding.

### Phase 2: Snapshot — Understand the Page

**Always take a snapshot (`playwright-cli snapshot`) before any interaction.** The snapshot returns the accessibility tree with refs for every element. These refs are required for all interaction tools.

- Use refs from the snapshot for all subsequent interactions (click, fill, hover, etc.).
- **Do not guess refs.** They change between page loads. Always take a fresh snapshot.
- If the page content changes (navigation, form submission, dynamic update), take a new snapshot before the next interaction.

### Phase 3: Verify Visually

Take a screenshot (`playwright-cli screenshot`) to confirm the UI looks correct:
- Are the right elements visible? Is the layout correct? Are styles applied?
- For element-specific verification, pass a CSS selector to screenshot a specific element.
- Use `--full-page` for pages with content below the fold.

### Phase 4: Interact and Test User Flows

Test the changed functionality by simulating user interactions:

- **Click:** `playwright-cli click <ref>` using the ref from the snapshot.
- **Fill inputs:** `playwright-cli fill <ref> "<value>"` for single inputs; run a sequence of `playwright-cli fill` commands for multiple fields.
- **Type:** `playwright-cli type "<text>"` when you need to type into an already-focused input.
- **Press keys:** `playwright-cli press <key>` for keyboard shortcuts, Enter to submit, Tab to navigate.
- **Hover:** `playwright-cli hover <ref>` for tooltips, dropdowns, or hover-triggered UI.
- **Drag:** `playwright-cli drag <ref1> <ref2>` for drag-and-drop interactions.
- **Upload files:** `playwright-cli upload <path>` for file input elements.
- **Handle dialogs:** `playwright-cli dialog-accept` or `playwright-cli dialog-dismiss` when `alert()`, `confirm()`, or `prompt()` appears.
- **Wait:** Use a manual retry loop or `playwright-cli eval` checks when an action triggers async content that needs time to appear.

**After every interaction that changes the page, take a new snapshot** before the next interaction. Refs may have changed.

**After key interactions, take a screenshot** to visually confirm the result.

#### In-Browser Assertions with `playwright-cli eval`

Use `playwright-cli eval "<js>"` to run JavaScript in the page for verification that goes beyond what snapshots and screenshots reveal:

- **Assert DOM state:** Check element existence, visibility, classes, attributes, text content.
- **Read computed styles:** Verify CSS properties (colors, dimensions, positioning) are applied correctly.
- **Check application state:** Read framework state (React state, Vue data, store values) to verify data correctness.
- **Validate data:** Check that rendered data matches expectations — counts, values, sort order.
- **Test edge cases:** Trigger conditions that are hard to reproduce through UI interaction alone.

```javascript
// Example: verify a list rendered the correct number of items
() => document.querySelectorAll('.item-row').length

// Example: check computed styles
(el) => {
  const styles = window.getComputedStyle(el);
  return { color: styles.color, display: styles.display };
}

// Example: read application state
() => JSON.parse(JSON.stringify(window.__APP_STATE__))
```

**Guidelines for `playwright-cli eval`:**
- Return values must be JSON-serializable.
- Query the DOM by selector when you need to inspect specific elements.
- Use for assertions and reading state. Prefer the dedicated interaction tools (click, fill, type) over JS for triggering actions — they produce better diagnostics and match real user behavior.

### Phase 5: Check Console and Network

**Console messages:**
- `playwright-cli console` to check for problems. **Any console error is a red flag.** Investigate before moving on.

**Network requests:**
- `playwright-cli requests` — verify API calls completed successfully. Check for failed requests (4xx, 5xx).

### Phase 6: Responsive Testing

If the change affects layout, test at multiple viewport sizes:

- `playwright-cli resize <w> <h>` to change dimensions. Common breakpoints:
  - Mobile: 375×667
  - Tablet: 768×1024
  - Desktop: 1280×800
  - Large desktop: 1920×1080
- Take a screenshot at each viewport size to confirm the layout adapts correctly.

## The Snapshot-First Rule

This is the most common mistake, so it deserves emphasis:

```
BEFORE every interaction:    playwright-cli snapshot → get current refs
AFTER every page change:     playwright-cli snapshot → refs are now stale
BEFORE reading page content: playwright-cli snapshot → not screenshot
```

**Screenshots** are for visual confirmation — seeing what the user sees.
**Snapshots** are for understanding page structure and getting refs for interaction.
You need both, but snapshots come first.

## Advanced: Performance and Debugging

Playwright CLI does not expose built-in performance or memory profiling commands. When investigating performance or memory issues, use `playwright-cli eval` to run standard Web APIs inside the page:

- Use `performance.mark()` and `performance.measure()` in `eval` for coarse timing.
- Use `performance.getEntriesByType('resource')` to inspect network timing.
- For deep performance traces or memory snapshots, use a dedicated Playwright test script rather than the CLI.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Interacting without a snapshot first | Always `playwright-cli snapshot` before clicking, filling, or typing. Refs change between page loads |
| Using stale refs after page navigation | Take a new snapshot after any action that changes the page |
| Skipping console error check | Always `playwright-cli console` after testing |
| Only taking screenshots, never snapshots | Screenshots show visuals. Snapshots give you refs for interaction. You need both |
| Testing only at one viewport size | If layout changed, test at least mobile (375px) and desktop (1280px) |
| Ignoring failed network requests | Check `playwright-cli requests` for 4xx/5xx responses after user flow testing |
| Using `playwright-cli eval` for clicks and form fills | Use the dedicated interaction tools — they match real user behavior and produce better errors |
| Not waiting for async content | Use a manual retry loop or `playwright-cli eval` checks when an action triggers content that loads asynchronously |
| Running `playwright-cli eval` without checking return value | Return values must be JSON-serializable. Complex objects need `JSON.parse(JSON.stringify(...))` |
| Navigating to localhost with no server running | Phase 0: check if the server is up, start one if not. Local apps need a running server before you can open them |

## The Bottom Line

**Snapshot first, interact second, verify always. Take a screenshot to see what the user sees. Run in-browser assertions for what screenshots can't show. Check the console for errors. Check the network for failures. If you changed the UI and did not look at it in the browser, you did not verify it.**
