# Process: Taiwan production-hours CSV (`taiwan`)

**Manual evidence:** `FactoryInsights_MANUAL_LOAD_Process.docx`, pages 36–39 (preparation p. 36; SAP steps pp. 36–39)  
**Configuration:** [`config/profiles/taiwan.yaml`](../../config/profiles/taiwan.yaml) (mirrored in `src/factoryprep/profiles/`)  
**Code:** [`src/factoryprep/pipelines/tabular.py`](../../src/factoryprep/pipelines/tabular.py)  
**Status:** implemented with synthetic tests; not certified on real sources. **No BW integration.**

## Input identification

Production Hours Update file; screenshot shows columns `Date`, `Earn_Hours`, `Paid_Hours`, `Overtime_Hours` with numeric decimals and dates.

**Current required shape:** `Date`, `Earn_Hours`, `Paid_Hours`, `Overtime_Hours`. Select the appropriate workbook tab explicitly with `--sheet` if multiple tabs match. Source is read-only.

## Source procedure (manual-derived)

Make sure dates are correct, check null or negative values, and detect missing dates in the series. Earned, Paid and OT hours are in same source; later ADSO loads and PBI verification are BW scope and excluded.

## Current Python implementation (code-derived)

Require four columns; parse MDY Date, numeric nonnegative Earn/Paid/Overtime; check missing calendar dates **between min and max source dates**; write UTF-8-with-BOM CSV, with current date rendering `MM/DD/YYYY` via `m/d/yyyy` format hint. Missing day is WARNING unless `--strict`.

**Output:** `csv`; configured sheet `Taiwan`. If output is an Excel date with a display pattern, the cell is date-typed, not necessarily formatted string data. For real destination header comparison use `--reference` (column names/order only).

## Quality risks, unknowns and safeguards

Manual does not explicitly certify CSV target date representation or full schema. Continuity check does not assert a specific expected week or future missing days; source examples may have gaps due to non-daily production.

## Operator command

```bash
uv run factoryprep prepare --profile taiwan --input SOURCE.csv --output taiwan_prepared.csv --report taiwan_quality.json
```

Inspect `taiwan_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Certification test (not yet evidenced)

Validate real CSV against approved target encoding and Date locale, null/negative error handling, sequence warnings and exact decimal values; signed-off treatment of nonproduction days.

**Tracked debt:** TD-001, TD-008, TD-015. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
