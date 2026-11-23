# Process: SGP attendance (`sgp`)

**Manual evidence:** `FactoryInsights_MANUAL_LOAD_Process.docx`, pages 1–3 (preparation on pp. 1–2; source reconciliation on p. 3)  
**Configuration:** [`config/profiles/sgp.yaml`](../../config/profiles/sgp.yaml) (mirrored in `src/factoryprep/profiles/`)  
**Code:** [`src/factoryprep/pipelines/tabular.py`](../../src/factoryprep/pipelines/tabular.py)  
**Status:** implemented with synthetic tests; not certified on real sources. **No BW integration.**

## Input identification

Attendance file, Excel; the manual depicts a `DATE` column and asks to save in Excel format.

**Current required shape:** `DATE`, `NORM`, `OT`. Select the appropriate workbook tab explicitly with `--sheet` if multiple tabs match. Source is read-only.

## Source procedure (manual-derived)

Change `DATE` display to `YYYYMMDD`; remove `SCHEDULED START TIME` and `SCHEDULED END TIME` when present. The manual later filters `DAYFORCEUC1` to 1000, 1025, 1050, 1075, 1300, 1320, 1330, 1340, 1350 to validate NORM and OT totals.

## Current Python implementation (code-derived)

`tabular` requires `DATE`, `NORM`, `OT`; normalizes known aliases, parses DATE as YMD, writes real Excel date with `yyyymmdd` number format, removes scheduled time columns, parses NORM/OT as numeric, forbids negatives. `DAYFORCEUC1` filters only advisory totals, never deletes rows.

**Output:** `xlsx`; configured sheet `SGP`. If output is an Excel date with a display pattern, the cell is date-typed, not necessarily formatted string data. For real destination header comparison use `--reference` (column names/order only).

## Quality risks, unknowns and safeguards

The exact destination schema and whether the consumer expects textual `YYYYMMDD` or formatted Excel date cells are unverified. Optional `DAYFORCEUC1` may be absent, producing reconciliation warning.

## Operator command

```bash
uv run factoryprep prepare --profile sgp --input SOURCE.xlsx --output sgp_prepared.xlsx --report sgp_quality.json
```

Inspect `sgp_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Certification test (not yet evidenced)

A real attendance workbook yields exactly expected source rows minus only the two optional scheduled-time columns; DATE display and NORM/OT totals match manually prepared output; wrong/ambiguous headers and negative hours error.

**Tracked debt:** TD-001, TD-015. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
