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

**Updated 2026-11-26:** The mirrored `timecard` contract declares DMY text dates, decimal-comma text and `blank_hours: error`; native numeric/date cells are preserved. The processor aligns actual dates with Sunday–Saturday, requires every date and observations for every day, and blocks unresolved blanks/statuses instead of fabricating hours. Explicit owner-approved `blank_hours: zero` or `zero_tokens` in a custom profile are audited by row/column. Multiple date-header candidates block. Employee rows require a label; summary/header rows are audited. Employee Total is compared only when source and selected periods agree. Output remains seven template rows with OT zero under the illustrated contract.

**Output:** `xlsx`; source files are read-only. `--reference` validates destination column names/order only. See [EP-0007](../exec-plans/active/EP-0007-manual-parsing-corrections.md) and [profile contract](../design-docs/PROFILE_CONTRACT.md).

## Quality risks, unknowns and safeguards

Real source Saturday–Friday versus template Sunday–Saturday coverage remains unresolved. Obtain the actual missing Saturday; never shift dates. Status meanings and blank-day semantics need owner approval. No real-source certification is claimed (TD-018). A malformed source blocks output even when some daily sums are calculable.

## Operator command

```bash
uv run factoryprep prepare --profile reno --input SOURCE.xlsx --week-ending 2026-03-07 --output reno_prepared.xlsx --report reno_quality.json
```

Inspect `reno_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Certification test (not yet evidenced)

Exactly seven dated template rows match an independently calculated seven-day aggregate; rows with negative/invalid hours fail; duplicate/missing date headers fail; source workbook unchanged.

**Tracked debt:** TD-001, TD-010, TD-015. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
