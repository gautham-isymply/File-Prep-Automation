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

**Updated 2026-11-26:** Bundled `source_mode: staging` retains the normalized Category/Paid Hours/OT Hours route and provisional warning. A custom `source_mode: raw_cells` can extract an explicitly approved `raw_source` sheet, week-ending cell and five category label/paid/OT cell triples. All mapped addresses must be distinct, labels must match, and the source week must equal the requested Saturday. Raw extraction records source-cell provenance and mapping approval, then applies the existing five-category plant/profit-center mapping. No raw HC locations or Paid/OT split are shipped or guessed.

**Output:** `xlsx`; source files are read-only. `--reference` validates destination column names/order only. See [EP-0007](../exec-plans/active/EP-0007-manual-parsing-corrections.md) and [profile contract](../design-docs/PROFILE_CONTRACT.md).

## Quality risks, unknowns and safeguards

Actual HC positions and Paid/OT derivation remain blocked under TD-003. raw_cells is a configurable extraction capability, not certification of the original workbook. Supply a reviewed contract; normalized staging remains the default. Screenshot week inconsistencies must be resolved against the real source.

## Operator command

```bash
uv run factoryprep prepare --profile jz --input SOURCE.xlsx --week-ending 2026-03-07 --output jz_prepared.xlsx --report jz_quality.json
```

Inspect `jz_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Automated regression evidence

The [test matrix](../quality/TEST_STRATEGY.md) maps shared file/config guards, per-field failures and profile operations to executable synthetic tests. Malformed supported config structures fail before source parsing; CSV delimiter fallback and damaged Excel-container handling are shared input guards. 2026-11-26 corrections are covered by `tests/test_manual_corrections.py`; these are synthetic fixtures. Real-source certification remains open.

## Certification test (not yet evidenced)

Receive sanitized raw “Labour in Plant Support” and business-approved paid-vs-OT mapping; transform it directly and reproduce the exact five-row template. Until then only accept staged category-level input as provisional.

**Tracked debt:** TD-001, TD-003. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
