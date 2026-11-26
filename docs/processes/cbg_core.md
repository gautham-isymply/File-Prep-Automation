# Process: CBG Starline Core2 (`cbg_core`)

**Manual evidence:** `FactoryInsights_MANUAL_LOAD_Process.docx`, pages 12–13 (Core2 preparation; validation pp. 17–18)  
**Configuration:** [`config/profiles/cbg_core.yaml`](../../config/profiles/cbg_core.yaml) (mirrored in `src/factoryprep/profiles/`)  
**Code:** [`src/factoryprep/pipelines/tabular.py`](../../src/factoryprep/pipelines/tabular.py)  
**Status:** implemented with synthetic tests; not certified on real sources. **No BW integration.**

## Input identification

Core2 worksheet embedded in a CBG invoice workbook; headings above actual grid and totals below.

**Current required shape:** `Pay Rate`. Select the appropriate workbook tab explicitly with `--sheet` if multiple tabs match. Source is read-only.

## Source procedure (manual-derived)

Copy data only (excluding headings and totals) to a new worksheet named `Core`; format `Pay Rate` as Number. Later reconciliation pivots `Hours/Units` by `Pay Code` REG/OT and filters selected operational departments.

## Current Python implementation (code-derived)

**Updated 2026-11-26:** Header detection now requires Pay Rate, Pay Code and Hours/Units. Pay Rate and Hours/Units are parsed numerically and reject negatives/nonfinite values. Summary detection checks only the first mapped column by default; approved `table.summary_columns` and `table.summary_labels` can make this explicit. Exact repeated headers and skipped-row reasons are audited. `table.first_data_row`/`last_data_row` are explicit worksheet row boundaries; unrecognized trailers fail field validation. REG/OT metrics include numeric text. The bundled `reconciliation_contract_confirmed: false` warns that department filters are missing and prevents combined CBG acceptance.

**Output:** `xlsx`; source files are read-only. `--reference` validates destination column names/order only. See [EP-0007](../exec-plans/active/EP-0007-manual-parsing-corrections.md) and [profile contract](../design-docs/PROFILE_CONTRACT.md).

## Quality risks, unknowns and safeguards

Core screenshots/department filters are missing in the supplied DOCX (TD-021). A real approved layout, summary-label column and department list remain required. Use a custom profile with approved filters, date parsing/reconciliation_date_column and confirmed contract before combined CBG reconciliation. Do not invent departments or call provisional totals certified.

## Operator command

```bash
uv run factoryprep prepare --profile cbg_core --input SOURCE.xlsx --output cbg_core_prepared.xlsx --report cbg_core_quality.json
```

Inspect `cbg_core_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Automated regression evidence

The [test matrix](../quality/TEST_STRATEGY.md) maps shared file/config guards, per-field failures and profile operations to executable synthetic tests. Malformed supported config structures fail before source parsing; CSV delimiter fallback and damaged Excel-container handling are shared input guards. 2026-11-26 corrections are covered by `tests/test_manual_corrections.py`; these are synthetic fixtures. Real-source certification remains open.

## Certification test (not yet evidenced)

Real source with decorative heading, repeated header and totals is transformed into only data rows on exact `Core` sheet; pay-rate values retain precision and approved columns, no dropped data records.

**Tracked debt:** TD-001, TD-015. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
