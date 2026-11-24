# JSON report contract and issue taxonomy

**Implementation:** `models.RunReport`, `engine.run`, `pipelines/*.py`. Default path: `<prepared_stem>_quality.json` beside target file, or `--report` override. This is an observed v0.1.0 shape, not a versioned external API.

```json
{
  "profile": "sgp",
  "input_path": "SOURCE.xlsx",
  "output_path": "SGP_prepared.xlsx",
  "issues": [{"severity": "INFO", "code": "DROPPED_COLUMN", "message": "...", "column": "SCHEDULED END TIME", "source": "SOURCE.xlsx"}],
  "diagnostics": {"filtered_reconciliation_metrics": {}, "excluded_rows": 0},
  "source_sheet": "Sheet1",
  "rows_in": 12,
  "rows_out": 12,
  "columns_out": ["DATE", "NORM", "OT"],
  "status": "PREPARED",
  "summary": {"errors": 0, "warnings": 0, "info": 1}
}
```

Illustrative values above; do not assume real row counts or diagnostics. `status`: `FAILED`, `VALIDATED`, or `PREPARED`. `output_path` is absent/null for validate-only or failed. The `issues[].row` is an Excel sheet row where supplied. `source` carries input path and may be sensitive.

## Code families

| Concern | Issue codes / search terms |
|---|---|
| Input/schema | `MISSING_COLUMN`, `DUPLICATE_HEADER`, `EXPECTED_COLUMN_MISSING`, `UNEXPECTED_COLUMN`, `TRANSFORM_COLUMN_MISSING` |
| Value correctness | `FORMAT_MISMATCH`, `NULL_VALUE`, `NEGATIVE_VALUE`, `EXCEL_CELL_ERROR`, `AMBIGUOUS_TIME_FRACTION`, `LARGE_HOURS_VALUE` |
| Data consistency | `TOTAL_MISMATCH`, `MISSING_DATES`, `DUPLICATE_KEY` |
| Business labels | `UNKNOWN_BUSINESS_LABEL`, `MISSING_BUSINESS_CATEGORY`, `EXCLUDED_ROW_LABEL_MISMATCH` |
| Controlled correction | `MANUAL_REVIEW_REQUIRED`, `APPROVED_CORRECTION`, `OVERRIDE_MATCH_FAILURE`, `OVERRIDE_OLD_VALUE_MISMATCH` |
| Destination | `DESTINATION_COLUMNS_MISSING`, `DESTINATION_COLUMNS_EXTRA`, `DESTINATION_COLUMN_ORDER` |
| Environment/limits | `EXTERNAL_REFRESH_NOT_PERFORMED`, `PROVISIONAL_SOURCE_SCHEMA`, `PREVIOUS_OUTPUT_REMAINS`, `PREPARATION_FAILURE` |

Actual codes should be enumerated from source when extending this document (`rg -o '"[A-Z][A-Z_]+"' src/factoryprep`). Not every warning proves a bad source; they identify risks requiring review. Some reconciliation warnings do not block normal output; use `--strict` when requiring zero-warning acceptance.
