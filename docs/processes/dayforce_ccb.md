# Process: Dayforce OData CCB (`dayforce_ccb`)

**Manual evidence:** `FactoryInsights_MANUAL_LOAD_Process.docx`, pages 32–35 (preparation p. 34, validation pp. 34–35)  
**Configuration:** [`config/profiles/dayforce_ccb.yaml`](../../config/profiles/dayforce_ccb.yaml) (mirrored in `src/factoryprep/profiles/`)  
**Code:** [`src/factoryprep/pipelines/tabular.py`](../../src/factoryprep/pipelines/tabular.py)  
**Status:** implemented with synthetic tests; not certified on real sources. **No BW integration.**

## Input identification

`Dayforce_OData 1_CCB` one-month export; data refreshes when original Excel workbook is opened in Excel.

**Current required shape:** `Cost_Center`, `Pay_Date`, `Location`, `Pay_Category`, `Normal`. Select the appropriate workbook tab explicitly with `--sheet` if multiple tabs match. Source is read-only.

## Source procedure (manual-derived)

Use refreshed month view; identify minimum date (relevant to BW delete, out of scope); remove CCB records whose Cost_center is `3600172100 > Receiving Farmingdale`; for validation use `Location = DPC CCB`, CCB Direct Labor cost centers 1000–1005, Pay_Date in weekly range, categories Reg and OT 1.5 (Normal hours).

## Current Python implementation (code-derived)

Require Cost_Center/Pay_Date/Location/Pay_Category/Normal; parse MDY dates; exclude rows matching code `3600172100` only when text also includes “Receiving Farmingdale”; error if expected label absent. Other cost/location/category selections are **advisory reconciliation metrics**, not deletions. Every run warns external refresh unverified.

**Output:** `xlsx`; configured sheet `Dayforce_CCB`. If output is an Excel date with a display pattern, the cell is date-typed, not necessarily formatted string data. For real destination header comparison use `--reference` (column names/order only).

## Quality risks, unknowns and safeguards

Program cannot refresh/verify OData. Current cost-center diagnostic filter uses substring matching, not validated code semantics; week-date selection is advisory only. BW minimum-date selective deletion explicitly excluded.

## Operator command

```bash
uv run factoryprep prepare --profile dayforce_ccb --input SOURCE.xlsx --output dayforce_ccb_prepared.xlsx --report dayforce_ccb_quality.json
```

Inspect `dayforce_ccb_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Certification test (not yet evidenced)

Refreshed representative source confirms only intended Receiving Farmingdale rows removed; no other rows deleted; Normal Reg/OT totals by location/code match independently validated source.

**Tracked debt:** TD-001, TD-007, TD-010. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
