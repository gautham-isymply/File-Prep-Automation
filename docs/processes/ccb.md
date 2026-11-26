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

**Updated 2026-11-26:** Four hours fields are numeric; Notes is removed. A reviewed override must match one row and the expected old value; replacement values are parsed and checked for invalid/negative values before use. The program never globally replaces 65.8 or silently recalculates Total. Summary markers are tested only in the first mapped column, with optional explicit table configuration and audit. Requested-week diagnostics now include separate Reg, OT1.5 and OT2 totals for the documented CC list; combine the two OT values for source reconciliation.

**Excel presentation (2026-11-26):** Four summarized hours columns use Number format `0.00` (two displayed decimals; stored values are not rounded). Static source fills in `Row Labels` follow retained rows. AutoFilter dropdowns cover all output rows, enabling colour filtering in Excel, with no active criteria as the manual instructs. Conditional formatting rules, font colours and other source styling are not copied. See [regressions](../../tests/test_ccb_formatting.py) and [EP-0008](../exec-plans/completed/EP-0008-ccb-excel-formatting.md).

**Output:** `xlsx`; source files are read-only. `--reference` validates destination column names/order only. See [EP-0007](../exec-plans/active/EP-0007-manual-parsing-corrections.md) and [profile contract](../design-docs/PROFILE_CONTRACT.md).

## Quality risks, unknowns and safeguards

The documented correction still lacks an approved unique key (TD-005); Dept/CC identity remains provisional. Remaining 65.8 and arithmetic mismatches warn; strict mode blocks warnings. No SAP deletion or destination certification is performed.

## Operator command

```bash
uv run factoryprep prepare --profile ccb --input SOURCE.xlsx --week-ending 2026-03-14 --output ccb_prepared.xlsx --report ccb_quality.json
```

Inspect `ccb_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Automated regression evidence

The [test matrix](../quality/TEST_STRATEGY.md) maps shared file/config guards, per-field failures and profile operations to executable synthetic tests. Malformed supported config structures fail before source parsing; CSV delimiter fallback and damaged Excel-container handling are shared input guards. 2026-11-26 corrections are covered by `tests/test_manual_corrections.py`; these are synthetic fixtures. Real-source certification remains open.

## Certification test (not yet evidenced)

A uniquely keyed approved correction is audited and exactly one cell changes; unapproved 65.8 warns; all four fields parse, Notes removed, totals preserved and reference schema verified.

**Tracked debt:** TD-001, TD-005, TD-015. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
