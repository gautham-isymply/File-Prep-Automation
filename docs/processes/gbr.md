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

Requires five columns, parses DMY dates and sets date display `yyyymmdd`; `time_to_hours` uses Excel format/fraction and emits `AMBIGUOUS_TIME_FRACTION` or `LARGE_HOURS_VALUE` warnings; negative values blocked. Leave-code/department filters compute diagnostics only.

**Output:** `xlsx`; configured sheet `GBR`. If output is an Excel date with a display pattern, the cell is date-typed, not necessarily formatted string data. For real destination header comparison use `--reference` (column names/order only).

## Quality risks, unknowns and safeguards

Time fraction vs already-decimal-hour representation can be ambiguous; `0.5` may mean half an hour or twelve hours. Source and target encoding must be confirmed; current `parse_number` accepts dash as zero. Manual does not enumerate a full destination schema.

## Operator command

```bash
uv run factoryprep prepare --profile gbr --input SOURCE.xlsx --output gbr_prepared.xlsx --report gbr_quality.json
```

Inspect `gbr_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Certification test (not yet evidenced)

Use a source with real Excel time formats, text clock values and already-decimal values, independently reconcile REG and O1+O2, and verify DMY dates, target columns and no lost rows.

**Tracked debt:** TD-001, TD-004. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
