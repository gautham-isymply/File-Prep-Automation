# Validation and output gates

## Order of checks

Profile selection → config parsing → source reading → sheet/header detection → expected columns/duplicates → value transforms (date/number/time) → negative/null checks → exclusion by explicit rule → manual review/overrides → cross-field totals/continuity → advisory reconciliation metrics → optional reference header comparison → output gate → JSON report.

**Reality check:** helper order inside `tabular.py` is: build/parse rows, apply overrides, flag remaining manual-review values, then cross-field totals, continuity and metrics. The table above is a conceptual pipeline; use code for exact exception paths.

| Severity | Default behavior | `--strict` |
|---|---|---|
| ERROR | blocks candidate output, status FAILED, exit 2 | blocks |
| WARNING | recorded; candidate may be produced | blocks, status FAILED, exit 2 |
| INFO | recorded only | recorded only |

Typical ERRORs: `MISSING_COLUMN`, `FORMAT_MISMATCH`, `DUPLICATE_HEADER`, `NEGATIVE_VALUE`, `EXCEL_CELL_ERROR`, `DESTINATION_COLUMNS_EXTRA`, `OVERRIDE_MATCH_FAILURE`.
Typical WARNINGs: `MISSING_DATES`, `AMBIGUOUS_TIME_FRACTION`, `MANUAL_REVIEW_REQUIRED`, `TOTAL_MISMATCH`, `RECONCILIATION_COLUMNS_MISSING`, `EXTERNAL_REFRESH_NOT_PERFORMED`, `PROVISIONAL_SOURCE_SCHEMA`.

The report includes first-class `issues` and generic `diagnostics.filtered_reconciliation_metrics` for tabular processors. It does **not** currently compare source totals to a live BW system. Source-level reconciliation metrics can be absent with a WARNING if source fields are missing.

## Invariants that need reinforcement

- Preserve prior candidate file on failed run but never regard it as current; see `PREVIOUS_OUTPUT_REMAINS` warning.
- `--reference` uses the first nonempty row of a single-sheet template; header sets/order only.
- Validate source before writing; writing occurs via temporary filename next to target then rename. Report writing happens separately, not in a cross-file transaction.
- Source row number in `Issue.row` is an Excel-sheet row for tabular inputs, not always a stable record key.

See [report contract](../quality/REPORT_CONTRACT.md), [operations](../OPERATIONS.md), and [reliability limitations](../RELIABILITY.md).
