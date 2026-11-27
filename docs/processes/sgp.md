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

**Updated 2026-11-26:** Requires DATE/NORM/OT, parses configured YMD dates and retains real Excel date cells displayed as `yyyymmdd`; removes only the two scheduled-time columns. Numeric hours reject negatives, nonfinite values and ambiguous decimal-comma text, while `allow_blank: [NORM, OT]` allows blank attendance cells on off/unworked days. With `--week-ending`, DAYFORCEUC1 reconciliation covers Sunday through Saturday. Without a week, weekly metrics are omitted with a warning; rows are retained. Reports include source hash, date range and a row-removal ledger.

**Output:** `xlsx`; source files are read-only. `--reference` validates destination column names/order only. See [EP-0007](../exec-plans/active/EP-0007-manual-parsing-corrections.md) and [profile contract](../design-docs/PROFILE_CONTRACT.md).

## Quality risks, unknowns and safeguards

Real source/target cell types and complete schema remain unverified. Diagnostic filters never trim source rows. Header references check names/order only.

## Operator command

```bash
uv run factoryprep prepare --profile sgp --input SOURCE.xlsx --week-ending 2026-03-14 --output sgp_prepared.xlsx --report sgp_quality.json
```

Inspect `sgp_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Automated regression evidence

The [test matrix](../quality/TEST_STRATEGY.md) maps shared file/config guards, per-field failures and profile operations to executable synthetic tests. Malformed supported config structures fail before source parsing; CSV delimiter fallback and damaged Excel-container handling are shared input guards. 2026-11-26 corrections are covered by `tests/test_manual_corrections.py`; these are synthetic fixtures. Real-source certification remains open.

## Certification test (not yet evidenced)

A real attendance workbook yields exactly expected source rows minus only the two optional scheduled-time columns; DATE display and NORM/OT totals match manually prepared output; wrong/ambiguous headers and negative hours error.

**Tracked debt:** TD-001, TD-015. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
