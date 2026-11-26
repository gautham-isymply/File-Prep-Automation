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

**Updated 2026-11-26:** Requires Date and the three nonnegative numeric hour measures; rejects nulls, nonfinite numbers and invalid dates. With --week-ending, date continuity covers the entire requested Sunday–Saturday week, including missing first/last dates; otherwise checks observed min/max. Repeated dates warn without deleting rows. Missing dates warn (strict mode blocks); no rows or zero hours are synthesized. CSV serialization remains UTF-8 BOM with current MDY rendering pending the destination contract.

**Output:** `csv`; source files are read-only. `--reference` validates destination column names/order only. See [EP-0007](../exec-plans/active/EP-0007-manual-parsing-corrections.md) and [profile contract](../design-docs/PROFILE_CONTRACT.md).

## Quality risks, unknowns and safeguards

Date locale, CSV schema/precision and expected production calendar remain unverified (TD-008). The explicit week checks calendar days; nonproduction-day exceptions need a reviewed future contract. No SAP/PBI integrations or source-row deduplication are performed.

## Operator command

```bash
uv run factoryprep prepare --profile taiwan --input SOURCE.csv --week-ending 2026-03-14 --output taiwan_prepared.csv --report taiwan_quality.json
```

Inspect `taiwan_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Certification test (not yet evidenced)

Validate real CSV against approved target encoding and Date locale, null/negative error handling, sequence warnings and exact decimal values; signed-off treatment of nonproduction days.

**Tracked debt:** TD-001, TD-008, TD-015. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
