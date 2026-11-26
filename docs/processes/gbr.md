# Process: GBR WorkSegments (`gbr`)

**Manual evidence:** `FactoryInsights_MANUAL_LOAD_Process.docx`, pages 5–11 (preparation on pp. 5–9; reconciliation pp. 10–11)  
**Configuration:** [`config/profiles/gbr.yaml`](../../config/profiles/gbr.yaml) (mirrored in `src/factoryprep/profiles/`)  
**Code:** [`src/factoryprep/pipelines/tabular.py`](../../src/factoryprep/pipelines/tabular.py)  
**Status:** implemented with synthetic tests; not certified on real sources. **No BW integration.**

## Input identification

WorkSegments workbook from GBR reporting contact. Source includes `DATEIN`, `DATEOUT`, `REGHOURS`, `O1HOURS`, `O2HOURS`.

**Current required shape:** `DATEIN`, `DATEOUT`, `REGHOURS`, `O1HOURS`, `O2HOURS`. Select the appropriate workbook tab explicitly with `--sheet` if multiple tabs match. Source is read-only.

## Source procedure (manual-derived)

Convert `DATEIN` and `DATEOUT` using DMY source convention, display `YYYYMMDD`; convert `REGHOURS`, `O1HOURS`, `O2HOURS` from Excel time to decimal hours with ×24, then paste values. For reconciliation, filter `DEPARTMENT` codes 1000/1025/1050/1075/1300/1320/1330/1340/1350 and exclude job descriptions PTO, PARENTAL LEAVE, UNPAID TIME; paid = REG, OT = O1 + O2.

## Current Python implementation (code-derived)

**Updated 2026-11-26:** DATEIN/DATEOUT use DMY and `yyyymmdd` display. Each time field has `hours_encoding`: `cell_format` (default), `excel_days`, or `decimal_hours`. Cell-format mode converts explicit Excel/clock durations; unformatted fractions block with `AMBIGUOUS_TIME_FRACTION` rather than assuming ×24. Declare reviewed units in a custom profile for such values. Weekly department/leave-code diagnostic totals require `--week-ending`; no leave-code rows are removed.

**Output:** `xlsx`; source files are read-only. `--reference` validates destination column names/order only. See [EP-0007](../exec-plans/active/EP-0007-manual-parsing-corrections.md) and [profile contract](../design-docs/PROFILE_CONTRACT.md).

## Quality risks, unknowns and safeguards

Raw duration versus already-decimal units remain unverified (TD-004). Never apply excel_days to a prepared decimal-hours export. Explicit unit choices are trusted profile contracts; native duration cells and clock text still carry their duration meaning. Destination schema remains uncertified.

## Operator command

```bash
uv run factoryprep prepare --profile gbr --input SOURCE.xlsx --week-ending 2026-03-14 --output gbr_prepared.xlsx --report gbr_quality.json
```

Inspect `gbr_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Automated regression evidence

The [test matrix](../quality/TEST_STRATEGY.md) maps shared file/config guards, per-field failures and profile operations to executable synthetic tests. Malformed supported config structures fail before source parsing; CSV delimiter fallback and damaged Excel-container handling are shared input guards. 2026-11-26 corrections are covered by `tests/test_manual_corrections.py`; these are synthetic fixtures. Real-source certification remains open.

## Certification test (not yet evidenced)

Use a source with real Excel time formats, text clock values and already-decimal values, independently reconcile REG and O1+O2, and verify DMY dates, target columns and no lost rows.

**Tracked debt:** TD-001, TD-004. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
