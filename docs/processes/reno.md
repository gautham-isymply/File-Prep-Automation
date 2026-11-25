# Process: Reno (3601) Temp Timecards (`reno`)

**Manual evidence:** `FactoryInsights_MANUAL_LOAD_Process.docx`, pages 26–28 (preparation pp. 26–27)  
**Configuration:** [`config/profiles/reno.yaml`](../../config/profiles/reno.yaml) (mirrored in `src/factoryprep/profiles/`)  
**Code:** [`src/factoryprep/pipelines/reno.py`](../../src/factoryprep/pipelines/reno.py)  
**Status:** implemented with synthetic tests; not certified on real sources. **No BW integration.**

## Input identification

Weekly Temp Timecards sheet; employee rows, 7 date columns, optional Total and Agency context.

**Current required shape:** seven daily date columns (Sunday–Saturday) with employee hour rows; no fixed header set. Select the appropriate workbook tab explicitly with `--sheet` if multiple tabs match. Source is read-only.

## Source procedure (manual-derived)

For every Sunday–Saturday date, sum hours from the employee timecards and transfer each day into Reno Paid Hours template. Screenshot example: week 2026-03-01 through 2026-03-07, paid hours vary daily; OT template values are zero. Segment PAC, plant 3601, plant Reno NV, profit center PDU, company code 3600.

## Current Python implementation (code-derived)

`reno` processor locates 7 date headers in first 15 rows, requires Saturday week ending (optionally `--week-ending`), sums per-day employee numeric cells, flags negative and >24h/day, optionally compares employee Total; outputs exactly 7 rows with specified constants and `OT Hours` = 0.

**Output:** `xlsx`; configured sheet `Reno`. If output is an Excel date with a display pattern, the cell is date-typed, not necessarily formatted string data. For real destination header comparison use `--reference` (column names/order only).

## Quality risks, unknowns and safeguards

Week/row selection assumptions, agency and employee subtotals must be tested with real timecard. Manual example totals are not a general fixed rule; never hardcode them. Source may contain merged cells or multiple candidate sheets.

## Operator command

```bash
uv run factoryprep prepare --profile reno --input SOURCE.xlsx --week-ending 2026-03-07 --output reno_prepared.xlsx --report reno_quality.json
```

Inspect `reno_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Certification test (not yet evidenced)

Exactly seven dated template rows match an independently calculated seven-day aggregate; rows with negative/invalid hours fail; duplicate/missing date headers fail; source workbook unchanged.

**Tracked debt:** TD-001, TD-010, TD-015. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
