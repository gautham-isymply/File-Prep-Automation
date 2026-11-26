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

**Updated 2026-11-26:** Requires a refreshed-export attestation in `--overrides` source_evidence with exact SHA-256, timezone-bearing refreshed_at and approved_by. Missing evidence is an ERROR; a mismatched hash blocks. Python does not refresh Excel or prove that the owner attestation is true. Exact code/label parsing removes only `3600172100 > Receiving Farmingdale`; missing/unexpected label for that exact code blocks. Similar longer codes remain. `row_audit` records excluded origins/hours. Requested-week metrics use exact direct-labor code/label pairs, Location and Pay_Category; monthly records outside the week remain. Source date range is recorded before exclusions. `reconcile --group us` combines two successful, refreshed, matching-week reports.

**Output:** `xlsx`; source files are read-only. `--reference` validates destination column names/order only. See [EP-0007](../exec-plans/active/EP-0007-manual-parsing-corrections.md) and [profile contract](../design-docs/PROFILE_CONTRACT.md).

## Quality risks, unknowns and safeguards

Approved export/refresh practice and label variants still need real-source certification (TD-007/016). The parser accepts whitespace/case variants of documented code > label pairs, without substring matching or invented synonyms. Without --week-ending, weekly metrics are omitted and combined reconciliation is blocked.

## Operator command

```bash
uv run factoryprep prepare --profile dayforce_ccb --input SOURCE.xlsx --week-ending 2026-03-14 --overrides REFRESH_EVIDENCE.yaml --output dayforce_ccb_prepared.xlsx --report dayforce_ccb_quality.json
```

Inspect `dayforce_ccb_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Automated regression evidence

The [test matrix](../quality/TEST_STRATEGY.md) maps shared file/config guards, per-field failures and profile operations to executable synthetic tests. Malformed supported config structures fail before source parsing; CSV delimiter fallback and damaged Excel-container handling are shared input guards. 2026-11-26 corrections are covered by `tests/test_manual_corrections.py`; these are synthetic fixtures. Real-source certification remains open.

## Certification test (not yet evidenced)

Refreshed representative source confirms only intended Receiving Farmingdale rows removed; no other rows deleted; Normal Reg/OT totals by location/code match independently validated source.

**Tracked debt:** TD-001, TD-007, TD-010. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
