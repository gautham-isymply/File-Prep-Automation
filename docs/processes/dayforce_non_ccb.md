# Process: Dayforce OData non-CCB (`dayforce_non_ccb`)

**Manual evidence:** `FactoryInsights_MANUAL_LOAD_Process.docx`, pages 32–35 (validation pp. 34–35)  
**Configuration:** [`config/profiles/dayforce_non_ccb.yaml`](../../config/profiles/dayforce_non_ccb.yaml) (mirrored in `src/factoryprep/profiles/`)  
**Code:** [`src/factoryprep/pipelines/tabular.py`](../../src/factoryprep/pipelines/tabular.py)  
**Status:** implemented with synthetic tests; not certified on real sources. **No BW integration.**

## Input identification

`Dayforce_OData 1_REST_Non_CCB` one-month export with refreshed Pay_Date and operational label columns.

**Current required shape:** `Cost_Center`, `Pay_Date`, `Location`, `Pay_Category`, `Normal`. Select the appropriate workbook tab explicitly with `--sheet` if multiple tabs match. Source is read-only.

## Source procedure (manual-derived)

For source validation, filter Cost_Center labels: `1000 > Direct Labour`, `1000 > Straights`, `1025 > Plugs`, `1050 > Fittings`, `1075 > Small Parts Assembly`, `1300 > Machine Shop`, `1330 > Powdercoat`; `Location` in DPC BUS/DPC PAC; `Pay_Category` Reg for paid and OT 1.5 for OT; date filter weekly range.

## Current Python implementation (code-derived)

Require Cost_Center/Pay_Date/Location/Pay_Category/Normal; parse MDY Pay_Date, numeric nonnegative Normal; no row exclusions. Advisory `us_non_ccb_reg_hours` / `us_non_ccb_ot_hours` metrics use `contains_any` matches and location/category constraints. External refresh warning on every run.

**Output:** `xlsx`; configured sheet `Dayforce_Non_CCB`. If output is an Excel date with a display pattern, the cell is date-typed, not necessarily formatted string data. For real destination header comparison use `--reference` (column names/order only).

## Quality risks, unknowns and safeguards

Manual cost-center labels may vary; substring matching could include unintended centers. Date window not automatically applied to output; current metrics calculate across source rows, so compare weekly totals only after certified exported window or adding a verified date filter. No actual external refresh.

## Operator command

```bash
uv run factoryprep prepare --profile dayforce_non_ccb --input SOURCE.xlsx --output dayforce_non_ccb_prepared.xlsx --report dayforce_non_ccb_quality.json
```

Inspect `dayforce_non_ccb_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Certification test (not yet evidenced)

Certified export containing a known week reconciles selected categories/locations and totals exactly; prove that unrelated cost centers are excluded from metrics yet retained in prepared output.

**Tracked debt:** TD-001, TD-007, TD-010, TD-016. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
