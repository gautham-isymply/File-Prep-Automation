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
| Data consistency | `TOTAL_MISMATCH`, `MISSING_DATES`, `DUPLICATE_KEY`, `EMPLOYEE_TOTAL_MISMATCH` |
| Business labels | `UNKNOWN_BUSINESS_LABEL`, `MISSING_BUSINESS_CATEGORY`, `EXCLUDED_ROW_LABEL_MISMATCH` |
| Controlled correction | `MANUAL_REVIEW_REQUIRED`, `APPROVED_CORRECTION`, `OVERRIDE_MATCH_FAILURE`, `OVERRIDE_OLD_VALUE_MISMATCH` |
| Destination | `DESTINATION_COLUMNS_MISSING`, `DESTINATION_COLUMNS_EXTRA`, `DESTINATION_COLUMN_ORDER` |
| Environment/limits | `EXTERNAL_REFRESH_NOT_PERFORMED`, `PROVISIONAL_SOURCE_SCHEMA`, `PREVIOUS_OUTPUT_REMAINS`, `PREPARATION_FAILURE` |

Actual codes should be enumerated from source when extending this document (`rg -o '"[A-Z][A-Z_]+"' src/factoryprep`). Not every warning proves a bad source; they identify risks requiring review. Some reconciliation warnings do not block normal output; use `--strict` when requiring zero-warning acceptance.

## 2026-11-26 source audit extensions

Successful parsing adds `diagnostics.source_sha256`, tabular `row_audit` (worksheet row/reason; excluded Dayforce hours where supplied), `date_range` (valid source dates before exclusions), optional `reconciliation_period` with start/end, `reconciliation_scoped` and `reconciliation_contract_confirmed`. Report fields remain compatible; consumers must tolerate added diagnostics. `refresh_evidence` records a matching source-owner attestation or null. Raw JZ adds mapped sheet/cell provenance and mapping approval. Missing/failed metric components are omitted rather than represented by a misleading zero; an empty successfully filtered population legitimately totals zero.

New blocking conditions include `SOURCE_EVIDENCE_MISMATCH`, missing `EXTERNAL_REFRESH_NOT_PERFORMED` evidence, `UNRESOLVED_BLANK_HOURS`, `NO_DAILY_EVIDENCE`, `INVALID_CORRECTION_VALUE`, `INVALID_RECONCILIATION_VALUE`, and `AMBIGUOUS_TIME_FRACTION`. `RECONCILIATION_WEEK_REQUIRED` omits unscoped weekly metrics; `RECONCILIATION_CONTRACT_UNCONFIRMED` flags provisional Core totals. `DUPLICATE_DATE` warns without row deletion.

`reconcile --group us|cbg --component A.json --component B.json --output COMBINED.json` produces a separate `{group, status: RECONCILED, period, components, paid_hours, ot_hours}` source audit. Each component includes its source hash, report path, paid and OT totals. Exactly the two expected successful profiles, identical Sunday–Saturday windows, confirmed/scoped filters and (for US) refresh attestations are required. The command refuses to overwrite any declared source, candidate or component report. It validates report evidence and adds totals; it does not compare a destination or independently verify the truth of an owner attestation.
