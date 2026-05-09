---
name: dbt-development
description: Use when building, modifying, or refactoring DBT models - requires understanding source data before writing SQL, continuous validation against actual data during development, and thorough testing
---

# DBT Development

## Overview

Models that aren't grounded in actual data are guesses. Guesses break in production.

**Core principle:** Look at the data before you write SQL. Keep looking while you write it. Verify when you're done. Test everything.

**Save reports to:** `agent_docs/development/YYYY-MM-DD-<model-name>.md`

## When to Use

Use for ANY DBT model work:
- New models
- Modifying existing models
- Refactoring model logic
- Adding/changing business logic
- Fixing model bugs

**Don't use when:**
- Pure configuration changes (project.yml, profiles)
- Documentation-only changes
- Task is data analysis, not model building (use `dbt-data-analysis` skill instead)

## The Iron Law

```
NO MODEL CODE WITHOUT UNDERSTANDING THE SOURCE DATA FIRST
NO "DONE" WITHOUT VALIDATING MODEL OUTPUT AGAINST DATA
NO COMPLETION WITHOUT TESTS
```

## The Process

```
WHEN building or modifying a DBT model:

1. UNDERSTAND: Query source data to learn its shape, quirks, edge cases
2. DESIGN: Decide on model structure based on what the data actually contains
3. BUILD: Implement incrementally, validating against data at each step
4. TEST: Add tests during development, not after
5. VALIDATE: Final check — model output matches data reality
```

### Phase 1: Understand the Source Data

**BEFORE writing any model SQL**, use DBT MCP tools to answer:

**Shape and scope:**
```sql
-- What tables/sources am I working with?
-- What columns exist? What types?
-- How many rows? What date range?
SELECT COUNT(*) FROM source;
SELECT MIN(created_at), MAX(created_at) FROM source;
```

**Data quality:**
```sql
-- Nulls in key columns?
SELECT COUNT(*) - COUNT(key_col) AS null_count FROM source;

-- Duplicates on expected keys?
SELECT key_col, COUNT(*) FROM source GROUP BY 1 HAVING COUNT(*) > 1;

-- Unexpected values?
SELECT DISTINCT status FROM source ORDER BY 1;
SELECT column, COUNT(*) FROM source GROUP BY 1 ORDER BY 2 DESC LIMIT 20;
```

**Relationships:**
```sql
-- Do foreign keys actually match?
SELECT COUNT(*) FROM a LEFT JOIN b ON a.id = b.a_id WHERE b.a_id IS NULL;

-- Cardinality: one-to-one, one-to-many, many-to-many?
SELECT a_id, COUNT(*) FROM b GROUP BY 1 ORDER BY 2 DESC LIMIT 10;
```

**What you're looking for:**
- Nulls where you'll assume NOT NULL
- Duplicates where you'll assume uniqueness
- Values you didn't expect (edge cases in business logic)
- Orphaned foreign keys
- Date gaps, timezone issues, formatting inconsistencies

**Document what you find.** These findings drive your model design and your tests.

### Phase 2: Design Based on Data Reality

With actual data knowledge:

1. **Choose grain** — what does one row represent? Verified against data, not assumed.
2. **Choose keys** — verified unique, verified non-null.
3. **Plan joins** — verified relationships and cardinality. Know your fanout risk.
4. **Plan transformations** — based on actual values you saw, not spec assumptions.
5. **Note edge cases** — nulls, duplicates, unexpected values found in Phase 1. Each becomes a test.

If the data contradicts your assumptions, update your approach. Don't force the data into a shape it doesn't fit.

### Phase 3: Build with Continuous Validation

Implement incrementally. After each meaningful change, check it against data.

**The cycle:**

```
Write/modify model SQL
  ↓
Run: dbt run --select model_name
  ↓
Query model output — does it match what you expect from the source data?
  ↓
  YES → continue building
  NO  → fix before adding more logic
```

**Validation queries during development:**

```sql
-- Row count sanity check: does the output grain match expectations?
SELECT COUNT(*) FROM model;

-- Spot-check: pick a known entity, trace it through
SELECT * FROM model WHERE id = 'known_value';
-- Compare against source:
SELECT * FROM source WHERE id = 'known_value';

-- Join validation: no accidental fanout?
-- (output rows should not exceed expected grain)
SELECT key, COUNT(*) FROM model GROUP BY 1 HAVING COUNT(*) > 1;

-- Aggregation check: do totals reconcile?
SELECT SUM(amount) FROM model;
SELECT SUM(amount) FROM source WHERE <same_filters>;

-- Null propagation: did joins introduce unexpected nulls?
SELECT COUNT(*) - COUNT(important_col) FROM model;
```

**Rules:**
- Don't pile up 50 lines of SQL and run once at the end
- Build in layers: start with the base query, validate, add joins, validate, add transformations, validate
- When something doesn't match, stop and investigate before adding more complexity
- If a join changes your row count unexpectedly, understand why immediately

### Phase 4: Test During Development

Add tests **as you build**, not after. Every finding from Phase 1 and every assumption in your model becomes a test.

#### Schema Tests (schema.yml)

Add these for every model:

```yaml
models:
  - name: my_model
    columns:
      - name: id
        tests:
          - unique
          - not_null
      - name: status
        tests:
          - not_null
          - accepted_values:
              values: ['active', 'inactive', 'pending']
      - name: account_id
        tests:
          - not_null
          - relationships:
              to: ref('stg_accounts')
              field: account_id
```

**Minimum schema tests for every model:**
- `unique` + `not_null` on primary key
- `not_null` on columns that must not be null
- `accepted_values` on status/type/category columns
- `relationships` on foreign keys

#### Data Tests (tests/ directory)

For business logic and cross-model invariants that schema tests can't express:

```sql
-- tests/assert_order_total_matches_line_items.sql
-- Order total should equal sum of line item amounts
SELECT
    o.order_id,
    o.total_amount,
    SUM(li.amount) AS line_item_total
FROM {{ ref('fct_orders') }} o
JOIN {{ ref('fct_order_line_items') }} li ON o.order_id = li.order_id
GROUP BY 1, 2
HAVING o.total_amount != SUM(li.amount)
```

Data tests should return **zero rows** when passing. Write them for:
- Business rules (amounts reconcile, statuses are consistent)
- Cross-model consistency (fact table references match dimension)
- Temporal logic (end_date >= start_date, no future dates where unexpected)
- Edge cases you found in Phase 1

#### Run Tests Continuously

```bash
# Run tests for your model as you build
dbt test --select model_name

# Run tests including upstream/downstream
dbt test --select +model_name+
```

Don't wait until the model is "done" to run tests. Run them after adding each batch of logic. A failing test during development is cheap. A failing test in production is expensive.

### Phase 5: Final Validation

When the model is complete and all tests pass, perform a final data validation.

**Completeness:**
```sql
-- All source records accounted for?
SELECT COUNT(*) FROM source;
SELECT COUNT(*) FROM model;
-- If counts differ, understand and document why (filters, dedup, grain change)
```

**Accuracy:**
```sql
-- Pick 3-5 representative records, trace them end-to-end
SELECT * FROM model WHERE id IN ('a', 'b', 'c');
-- Manually verify each against source data
```

**Edge cases:**
```sql
-- The nulls, duplicates, and quirks you found in Phase 1 —
-- are they handled correctly in the model output?
SELECT * FROM model WHERE <edge_case_condition>;
```

**Full test suite:**
```bash
dbt test --select +model_name+
```

All tests must pass. If any fail, fix the model or the test (if the test was wrong), then re-run.

### Phase 6: Development Report

**Write the report every time you make changes — do not wait for the work to be "complete."**

If you changed any model, test, or configuration, write or update the development report before finishing your turn. Even if more work is expected, write the report now with what you've done so far. If the user asks for more changes later, update the report after those changes. The report is a living document — it reflects the current state, not the final state.

Never skip the report because "there's more to do." There is always more to do.

Save the development report to `agent_docs/development/YYYY-MM-DD-<model-name>.md`.

**Report template:**

```markdown
# [Model Name] Development Report

**Date:** YYYY-MM-DD
**Status:** [in-progress | complete]
**Model(s):** [list of models created or modified, with file paths]
```

**Every report must contain the following sections. Write concretely — no placeholders, no "TBD", no empty sections.**

#### Source Data Findings

Document what you learned about the source data in Phase 1:
- Row counts, date ranges, and data scope
- Nulls, duplicates, or unexpected values found in key columns
- Relationship cardinalities (one-to-one, one-to-many, many-to-many) verified between tables
- Data quality issues that affect model design

These findings justify your design decisions and test choices. A reader should understand _why_ the model is built the way it is.

#### Design Decisions

For each significant decision, state what was decided and why:
- **Grain:** What one row represents. Reference the data finding that confirmed this.
- **Keys:** Which columns are used as primary/foreign keys. Reference the uniqueness/null checks that verified them.
- **Joins:** Which tables are joined and how. Reference the cardinality checks.
- **Transformations:** Business logic applied. Reference the actual values found in the data that drove this logic.
- **Edge cases:** How nulls, duplicates, or unexpected values are handled.

#### Validation Results

Evidence that the model is correct — not assertions, evidence:
- Row count comparison between source and model (with explanation if they differ)
- Spot-check results: specific records traced end-to-end from source to model
- Aggregation reconciliation: totals that match between source and model
- Edge case verification: how the edge cases from Phase 1 appear in model output

#### Tests Added

List every test added, grouped by type:
- **Schema tests:** Which columns have `unique`, `not_null`, `accepted_values`, `relationships` — and what each protects against
- **Data tests:** Custom SQL tests added, what business rule or invariant each enforces
- **Test results:** Output of `dbt test` confirming all tests pass

#### Caveats

Be explicit about what is NOT covered:
- Known data quality issues not yet addressed
- Edge cases handled with assumptions that may not hold for future data
- Upstream dependencies that could break this model
- Performance concerns for large data volumes


This prevents accidental commits of development reports containing production data.

## Test Quality Standards

Tests exist to catch real problems. Bad tests give false confidence.

**Good tests:**
- Test behavior that could actually break (nulls on a key column, unexpected values)
- Catch real data quality issues (orphaned foreign keys, broken business rules)
- Are specific enough that a failure tells you what's wrong

**Bad tests:**
- Test things that can never fail (e.g., unique test on a column you just generated with `row_number()`)
- Duplicate what another test already covers
- Are so broad that a failure tells you nothing useful

| Test Type | When to Use | Example |
|-----------|-------------|---------|
| `unique` | Primary/natural keys | Order ID, user ID |
| `not_null` | Required columns | Foreign keys, status fields |
| `accepted_values` | Enum/category columns | Status, type, category |
| `relationships` | Foreign keys | `account_id` exists in accounts |
| Data test | Business logic, cross-model rules | Amounts reconcile, dates are sane |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Writing model SQL before looking at data | Phase 1 first. Always. |
| Assuming uniqueness without checking | Query for duplicates before choosing keys |
| Adding joins without checking cardinality | Verify cardinality → know your fanout risk |
| "It compiled, ship it" | Compilation proves syntax, not correctness. Query the output. |
| Tests added as afterthought | Add tests during Phase 3, not after Phase 5 |
| Only `unique` + `not_null` tests | Add `accepted_values`, `relationships`, and data tests |
| Testing what can't fail | Test assumptions that could actually be violated |
| Fixing a failing test by loosening it | If data violates your test, understand why first |
| Building entire model, validating once | Build in layers. Validate each layer. |
| Trusting the spec over the data | Specs describe intent. Data describes reality. When they conflict, data wins. |

## Red Flags — STOP

If you catch yourself:
- Writing a `SELECT` in a model file before querying the source → **STOP. Phase 1.**
- Adding a join without knowing the cardinality → **STOP. Query it.**
- Model row count surprises you → **STOP. Investigate before continuing.**
- About to say "done" without running `dbt test` → **STOP. Run tests.**
- Adding tests after the model is "finished" → You skipped Phase 4. Go back.
- Thinking "I'll check the data later" → Later is now.
- Skipping the report because "there's more work coming" → Write it now. Update it later.

## The Bottom Line

**Look at the data. Build against what you see. Validate what you built. Test everything.**

The data is the authority. Not the spec, not the ticket, not your assumptions.
