# Process: JZ-BUS and JZ-DAT (`jz`)

**Manual evidence:** `FactoryInsights_MANUAL_LOAD_Process.docx`, pages 29–31 (preparation pp. 29–30)  
**Configuration:** [`config/profiles/jz.yaml`](../../config/profiles/jz.yaml) (mirrored in `src/factoryprep/profiles/`)  
**Code:** [`src/factoryprep/pipelines/jz.py`](../../src/factoryprep/pipelines/jz.py)  
**Status:** provisional staged-input only. **No BW integration.**

## Input identification

“Labour in Plant Support” workbook; manual explicitly mentions HC column invoice hours and Direct Hours (Starline/Cables/Fibra/Connectors/Servertech).

**Current required shape:** `Category`, `Paid Hours`, `OT Hours`. Select the appropriate workbook tab explicitly with `--sheet` if multiple tabs match. Source is read-only.

## Source procedure (manual-derived)

Populate Paid Hours Template with five category rows. Direct Hours (Starline)→BUSWAY; Cables→COP; Fibra→FIB; Connectors→RAC; Servertech→DAT. Use Sunday date for that week; screenshot uses BUS plant 3618 and DAT plant 3614, Santa Teresa, company 3600.

## Current Python implementation (code-derived)

`jz` processor supports **only normalized staging** with unique `Category`, `Paid Hours`, `OT Hours`; `--week-ending` Saturday required; maps all 5 groups to fixed segment/plant/profit center fields; flags missing/unknown/duplicate groups and provisional source schema warning.

**Output:** `xlsx`; configured sheet `JZ`. If output is an Excel date with a display pattern, the cell is date-typed, not necessarily formatted string data. For real destination header comparison use `--reference` (column names/order only).

## Quality risks, unknowns and safeguards

Original HC source cell locations and invoice hours versus Paid/OT split are **not defined** in manual. Current normalized input is **not direct raw workbook support**. Do not assume invoice hours equal paid hours or infer overtime. `--strict` blocks provisional warning until signed off.

## Operator command

```bash
uv run factoryprep prepare --profile jz --input SOURCE.xlsx --week-ending 2026-03-07 --output jz_prepared.xlsx --report jz_quality.json
```

Inspect `jz_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Certification test (not yet evidenced)

Receive sanitized raw “Labour in Plant Support” and business-approved paid-vs-OT mapping; transform it directly and reproduce the exact five-row template. Until then only accept staged category-level input as provisional.

**Tracked debt:** TD-001, TD-003. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
