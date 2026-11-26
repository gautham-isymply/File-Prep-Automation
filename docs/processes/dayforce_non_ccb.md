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

**Updated 2026-11-26:** Requires the same source-bound refreshed-export attestation as Dayforce CCB. Retains all monthly rows. Requested-week diagnostic totals use exact documented code > label pairs, DPC BUS/DPC PAC and Reg/OT 1.5 categories. No substring code matches. Without --week-ending, weekly metrics are omitted with a warning. `reconcile --group us` combines matching-week successful CCB/non-CCB reports only when both include refresh evidence.

**Output:** `xlsx`; source files are read-only. `--reference` validates destination column names/order only. See [EP-0007](../exec-plans/active/EP-0007-manual-parsing-corrections.md) and [profile contract](../design-docs/PROFILE_CONTRACT.md).

## Quality risks, unknowns and safeguards

Real export freshness and label grammar remain unverified (TD-007/016). Source-owner attestations are auditable prerequisites, not refresh execution. Unknown labels are not silently matched to similar labels. Destination schema remains uncertified.

## Operator command

```bash
uv run factoryprep prepare --profile dayforce_non_ccb --input SOURCE.xlsx --week-ending 2026-03-14 --overrides REFRESH_EVIDENCE.yaml --output dayforce_non_ccb_prepared.xlsx --report dayforce_non_ccb_quality.json
```

Inspect `dayforce_non_ccb_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Automated regression evidence

The [test matrix](../quality/TEST_STRATEGY.md) maps shared file/config guards, per-field failures and profile operations to executable synthetic tests. Malformed supported config structures fail before source parsing; CSV delimiter fallback and damaged Excel-container handling are shared input guards. 2026-11-26 corrections are covered by `tests/test_manual_corrections.py`; these are synthetic fixtures. Real-source certification remains open.

## Certification test (not yet evidenced)

Certified export containing a known week reconciles selected categories/locations and totals exactly; prove that unrelated cost centers are excluded from metrics yet retained in prepared output.

**Tracked debt:** TD-001, TD-007, TD-010, TD-016. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
