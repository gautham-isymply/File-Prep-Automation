# Process: CCB weekly hours (`ccb`)

**Manual evidence:** `FactoryInsights_MANUAL_LOAD_Process.docx`, pages 20–22 (preparation), 25–26 (reconciliation)  
**Configuration:** [`config/profiles/ccb.yaml`](../../config/profiles/ccb.yaml) (mirrored in `src/factoryprep/profiles/`)  
**Code:** [`src/factoryprep/pipelines/tabular.py`](../../src/factoryprep/pipelines/tabular.py)  
**Status:** implemented with synthetic tests; not certified on real sources. **No BW integration.**

## Input identification

CCB summary workbook with `Row Labels`, `Dept` / possible `CC`, four summarized hour fields and Notes.

**Current required shape:** `Row Labels`, `Dept`, `Sum of Reg Hr`, `Sum of OT1.5 Hr`, `Sum of OT2 Hr`, `Sum of Total Hr`. Select the appropriate workbook tab explicitly with `--sheet` if multiple tabs match. Source is read-only.

## Source procedure (manual-derived)

Filter highlighted row by colour and change one `Sum of Reg Hr` cell from 65.8 to 75.8, then clear filter; change Reg, OT1.5, OT2 and Total Hr columns to numeric; remove Notes. Later validate only selected CC IDs; paid = Reg, OT = OT1.5 + OT2.

## Current Python implementation (code-derived)

Requires Row Labels/Dept/four hours; aliases `CC` to Dept; numeric + nonnegative conversions; date MDY; drop `Notes`; warning when any remaining 65.8 appears; row-keyed `--overrides` can change exactly one preverified value. Warn on Reg+OT1.5+OT2 vs Total mismatch; cost-center metric is advisory.

**Output:** `xlsx`; configured sheet `CCB`. If output is an Excel date with a display pattern, the cell is date-typed, not necessarily formatted string data. For real destination header comparison use `--reference` (column names/order only).

## Quality risks, unknowns and safeguards

The manual does **not** specify a reliable key for the one corrected cell. Never globally change `65.8`. `Dept`≡`CC` is only a profile alias, not confirmed source truth. CCB ADSO selective deletion is out of scope.

## Operator command

```bash
uv run factoryprep prepare --profile ccb --input SOURCE.xlsx --output ccb_prepared.xlsx --report ccb_quality.json
```

Inspect `ccb_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Certification test (not yet evidenced)

A uniquely keyed approved correction is audited and exactly one cell changes; unapproved 65.8 warns; all four fields parse, Notes removed, totals preserved and reference schema verified.

**Tracked debt:** TD-001, TD-005, TD-015. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
