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

Generic tabular header scan (45 rows), `skip_summary_rows` heuristic, required `Pay Rate` (and aliases), numeric nonnegative Pay Rate, output sheet `Core`. Advisory metrics sum `Hours/Units` for `Pay Code` REG and OT if those columns exist.

**Output:** `xlsx`; configured sheet `Core`. If output is an Excel date with a display pattern, the cell is date-typed, not necessarily formatted string data. For real destination header comparison use `--reference` (column names/order only).

## Quality risks, unknowns and safeguards

Manual does not expose a complete machine-readable Core2 header list or unique summary patterns. Generic total-row removal is heuristic and may miss complex subtotals. Mapping/department labels for reconciliation are not complete in profile.

## Operator command

```bash
uv run factoryprep prepare --profile cbg_core --input SOURCE.xlsx --output cbg_core_prepared.xlsx --report cbg_core_quality.json
```

Inspect `cbg_core_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Certification test (not yet evidenced)

Real source with decorative heading, repeated header and totals is transformed into only data rows on exact `Core` sheet; pay-rate values retain precision and approved columns, no dropped data records.

**Tracked debt:** TD-001, TD-015. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
