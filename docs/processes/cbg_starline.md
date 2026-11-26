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

**Updated 2026-11-26:** W/E Date now uses conservative `auto`: native/ISO/unambiguous dates parse, but ambiguous slash dates fail until an approved custom profile declares MDY or DMY. Empty semicolon suffixes are accepted; nonblank extra content blocks. Shift is removed; BRD and present Straight Hrs/Overtime Hrs fields are numeric. First-column summary detection, exact repeated-header detection, explicit table bounds and skipped-row audit replace any-cell total detection. CHARGECODE totals require a requested week; combined CBG audit requires an approved Core counterpart.

**Output:** `xlsx`; source files are read-only. `--reference` validates destination column names/order only. See [EP-0007](../exec-plans/active/EP-0007-manual-parsing-corrections.md) and [profile contract](../design-docs/PROFILE_CONTRACT.md).

## Quality risks, unknowns and safeguards

YMD wizard versus MDY-looking screenshot remains unresolved (TD-009). Auto mode is a blocking safeguard, not locale certification. Exact table boundaries and destination schema remain unverified. Numeric source errors must be resolved, never silently omitted from sums.

## Operator command

```bash
uv run factoryprep prepare --profile cbg_starline --input SOURCE.xlsx --week-ending 2026-03-14 --output cbg_starline_prepared.xlsx --report cbg_starline_quality.json
```

Inspect `cbg_starline_quality.json` for `issues`, `status`, row counts and `diagnostics`; **do not** use stale output from a failed run. `--strict` treats all warnings as blocking.

## Automated regression evidence

The [test matrix](../quality/TEST_STRATEGY.md) maps shared file/config guards, per-field failures and profile operations to executable synthetic tests. Malformed supported config structures fail before source parsing; CSV delimiter fallback and damaged Excel-container handling are shared input guards. 2026-11-26 corrections are covered by `tests/test_manual_corrections.py`; these are synthetic fixtures. Real-source certification remains open.

## Certification test (not yet evidenced)

Compare date parse for genuinely ambiguous days from a sanctioned source; verify all data rows, no Shift, numeric BRD and proper W/E date display; source totals match independent manual sums.

**Tracked debt:** TD-001, TD-009. See [debt tracker](../exec-plans/tech-debt-tracker.md), [test strategy](../quality/TEST_STRATEGY.md), [source evidence](../references/MANUAL_EVIDENCE.md).
