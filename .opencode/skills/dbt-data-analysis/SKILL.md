---
name: dbt-data-analysis
description: Use when investigating data issues, analyzing datasets, or performing ad-hoc analysis in a DBT project - requires using DBT MCP tools to query actual data and producing a reproducible report
---

# DBT Data Analysis

## Overview

Data analysis requires evidence from actual data, not assumptions about what the data contains.

**Core principle:** Query first, conclude second. Every claim in your report must trace back to a query you ran.

**Save reports to:** `agent_docs/analysis/YYYY-MM-DD-<analysis-name>.md`

## When to Use

Use for ANY data investigation in a DBT project:
- Investigating data quality issues or anomalies
- Ad-hoc analysis requests (counts, distributions, trends)
- Debugging model output discrepancies
- Validating business logic against actual data
- Answering stakeholder questions about the data

**Don't use when:**
- Task is pure DBT model development (writing/refactoring SQL models)
- Task is DBT configuration (sources, tests, docs)
- No data querying is needed

## The Process

```
WHEN given an analysis task:

1. UNDERSTAND: Restate the problem in your own words
2. ORIENT: Inspect relevant models, sources, and schema
3. INVESTIGATE: Query actual data using DBT MCP tools
4. ANALYZE: Draw conclusions from query results
5. REPORT: Write reproducible findings to output file
```

### Phase 1: Understand the Problem

Before touching any data:
- Restate what you're investigating and why
- Identify what "done" looks like — what questions need answering?
- Note any constraints (date ranges, specific entities, thresholds)

If the problem statement is ambiguous, ask for clarification before proceeding.

### Phase 2: Orient — Inspect the Landscape

Use DBT MCP tools to understand the relevant data:
- List available models and sources
- Inspect schemas and column types for relevant tables
- Check row counts and date ranges to understand data scope
- Look at DBT docs/descriptions if available

**Goal:** Know what data exists and how it's structured before writing analysis queries.

### Phase 3: Investigate — Query the Data

Run queries against actual data using DBT MCP tools.

**Rules:**
- Start broad, then narrow down (overview → detail)
- Run one query per question — don't try to answer everything in a single query
- Record every query you run and its results
- If a result surprises you, verify it with a different approach
- Use `LIMIT` on exploratory queries to avoid unnecessary load

**Common investigation patterns:**
```sql
-- Distribution / cardinality
SELECT column, COUNT(*) FROM model GROUP BY 1 ORDER BY 2 DESC;

-- Nulls / missing data
SELECT COUNT(*) AS total, COUNT(column) AS non_null,
       COUNT(*) - COUNT(column) AS nulls FROM model;

-- Date range / freshness
SELECT MIN(date_col), MAX(date_col), COUNT(DISTINCT date_col) FROM model;

-- Duplicates
SELECT key_col, COUNT(*) FROM model GROUP BY 1 HAVING COUNT(*) > 1;

-- Cross-model join validation
SELECT a.id, b.id FROM model_a a LEFT JOIN model_b b ON a.id = b.id
WHERE b.id IS NULL;
```

### Phase 4: Analyze — Draw Conclusions

- Summarize what the data tells you
- Distinguish between facts (query results) and interpretation
- Note caveats, assumptions, or data quality issues encountered
- If analysis is inconclusive, say so — don't fabricate certainty

### Phase 5: Report — Write Reproducible Findings

Save the report to `agent_docs/analysis/YYYY-MM-DD-<analysis-name>.md`. Every report MUST follow this structure:

```markdown
# [Analysis Title]

**Date:** YYYY-MM-DD

## Problem Description

[What was investigated and why. Restate the original question/issue.]

## Method

[How the analysis was performed. Which models/sources were queried.]

## Reproducing Results

[Exact SQL queries used, in order. Each query should be copy-pasteable
and produce the results referenced in the findings.]

### Query 1: [Description]

    ```sql
    SELECT ... FROM ...
    ```

**Result:** [Summary of what this returned]

### Query 2: [Description]

    ```sql
    SELECT ... FROM ...
    ```

**Result:** [Summary of what this returned]

[... repeat for each query ...]

## Findings

[What the data shows. Reference specific query results.
Separate facts from interpretation.]

## Conclusions

[Answer the original question. State confidence level.
Note caveats or limitations.]
```


## Report Quality Checklist

Before finalizing the report, verify:

- [ ] Problem is clearly stated — a reader unfamiliar with the task understands what was investigated
- [ ] Every finding traces back to a specific query in the report
- [ ] All queries are exact and copy-pasteable (no pseudocode, no `...`)
- [ ] Query results are summarized accurately (numbers match what was returned)
- [ ] Conclusions answer the original question
- [ ] Caveats and limitations are noted
- [ ] Report is saved to `agent_docs/analysis/YYYY-MM-DD-<analysis-name>.md`

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Concluding without querying | Run the query. Look at the data. |
| Queries reference tables that don't exist | Inspect available models first (Phase 2) |
| Report contains "approximately" without a query | Get the exact number |
| Single query for everything | One query per question — easier to reproduce |
| Forgetting to record a query | Write queries into report as you go |
| Assuming data quality is fine | Check for nulls, duplicates, date gaps |
| Report has no reproduction instructions | Every finding needs its query |
| Drawing conclusions from `LIMIT 10` | Aggregations on full data for conclusions |

## The Bottom Line

**Query the data. Record what you ran. Write it up so someone else can reproduce it.**

No assumptions. No hand-waving. Evidence and reproducibility.
