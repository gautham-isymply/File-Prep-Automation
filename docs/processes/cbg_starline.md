# Process: CBG Starline SSI (`cbg_starline`)

**Manual evidence:** `FactoryInsights_MANUAL_LOAD_Process.docx`, pages 13–16 (preparation), 17–19 (validation)  
**Configuration:** [`config/profiles/cbg_starline.yaml`](../../config/profiles/cbg_starline.yaml) (mirrored in `src/factoryprep/profiles/`)  
**Code:** [`src/factoryprep/pipelines/tabular.py`](../../src/factoryprep/pipelines/tabular.py)  
**Status:** implemented with synthetic tests; not certified on real sources. **No BW integration.**

## Input identification

Starline SSI workbook tab with preamble, week-ending dates, Shift and BRD columns.

**Current required shape:** `W/E Date`, `BRD`. Select the appropriate workbook tab explicitly with `--sheet` if multiple tabs match. Source is read-only.

## Source procedure (manual-derived)

Remove rows above header and below last data; convert `W/E Date` using Text to Columns and semicolon wizard (text says select YMD) then display `m/d/yyyy`; remove `Shift`; format `BRD` numeric. For reconciliation, use `CHARGECODE` 1000/1025/1050/1075/1300/1330, `Straight Hrs` and `Overtime Hrs`.

## Current Python implementation (code-derived)

Scan up to 45 rows, drop total/subtotal marker rows, require `W/E Date` and `BRD`, parse dates as `MDY`, permit only empty trailing semicolon in date cell, format `m/d/yyyy`, drop `Shift`, numeric nonnegative BRD. `CHARGECODE` filters are advisory source metrics.

**Output:** `xlsx`; configured sheet `Starline SSI`. If output is an Excel date with a display pattern, the cell is date-typed, not necessarily formatted string data. For real destination header comparison use `--reference` (column names/order only).

## Quality risks, unknowns and safeguards

Screenshot date examples appear MDY while wizard says YMD; current MDY is an **assumption**, not verified. Nonempty text after semicolon is treated as error, avoiding data loss. Exact end-of-table structures/headers unknown.

## Operator command

```bash
uv run factoryprep prepare --profile cbg_starline --input SOURCE.xlsx --output cbg_starline_prepared.xlsx --report cbg_starline_quality.json
```

Inspect `cbg_starline_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Certification test (not yet evidenced)

Compare date parse for genuinely ambiguous days from a sanctioned source; verify all data rows, no Shift, numeric BRD and proper W/E date display; source totals match independent manual sums.

**Tracked debt:** TD-001, TD-009. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
