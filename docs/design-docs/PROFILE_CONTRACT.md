# YAML profile contract — v0.1.0 (implemented subset)

**Canonical reviewed copies:** `config/profiles/*.yaml` plus deployed copies `src/factoryprep/profiles/*.yaml`. Both must be byte-identical. By default `load_profile()` loads the embedded copy; pass `--config-dir config/profiles` to explicitly use development copies.

## Structure

| Key | Meaning / implementation |
|---|---|
| `id`, `description`, `processor` | required identity; `processor` ∈ `tabular`, `reno`, `jz` |
| `columns.required` | canonical exact semantic headers, alias-aware for input |
| `columns.aliases` | canonical → equivalent labels; normalized by stripping punctuation/case |
| `columns.drop` | columns removed from prepared output, if present |
| `columns.expected` | optional complete schema; extra columns WARN, missing ERROR |
| `columns.numeric` / `negative_forbidden` | parse floats; block negatives for specified columns |
| `columns.non_null` / `duplicate_keys` | optional strict nulls / duplicate-key WARN |
| `dates` | list of `{column, input: DMY|MDY|YMD|auto, excel_format, split_delimiter?}` |
| `time_to_hours`, `hours_encoding` | Per-column `cell_format`, `excel_days` or `decimal_hours`; unformatted fractional values block in cell_format mode |
| `header_scan_rows`, `skip_summary_rows`, `table` | Detection budget; summary labels in first mapped column by default, or declared summary_columns; explicit first_data_row/last_data_row and summary_labels; row-removal audit |
| `exclude_rows` | *actual source row exclusion*, with optional expected label safeguard |
| `reconciliation` | `{name, column, filters}` diagnostics; `in`, `not_in`, `contains_any`, exact `cost_center_in` (code > label pairs); selected nonnumeric cells error rather than disappear |
| `reconciliation_date_column` | Requested-week diagnostic date predicate; requires --week-ending for metrics; never trims output rows |
| `reconciliation_contract_confirmed` | False for incomplete Core filters; blocks combined reconciliation; setting true requires owner-reviewed filters/schema |
| `columns.numeric_if_present` | Validate optional metric fields when present; not a required header |
| `manual_review`, `cross_field_sums`, `date_continuity_column` | warning/anomaly checks |
| `external_refresh` | Requires hash-bound source_evidence attestation in overrides; absent/mismatched evidence blocks; no automatic refresh |
| `source_schema_status: provisional` | risk warning for incomplete raw-source specification |
| `output.format`, `output.sheet`, `output.columns`, `output.date_format` | output destination; explicit fixed columns are used by `reno` and `jz` processors |
| `output.number_formats`, `output.preserve_fill_columns`, `output.auto_filter` | Tabular XLSX presentation: canonical column-to-format mapping; static fills follow retained source rows; full-table filter dropdowns without active criteria. Date formats take precedence. CSV has no styling. |
| `defaults`, `category_mapping` | processor-specific Reno/JZ fields |
| `timecard` | Reno date_input, decimal_separator, blank_hours (error/zero), zero_tokens; default DMY/comma/error/no status coercion |
| `source_mode`, `raw_source` | JZ staging default; raw_cells requires sheet, approval, week_ending_cell, explicit date_input and categories with distinct label_cell/paid_cell/ot_cell addresses |

**Structural guard (2026-11-25):** malformed YAML, invalid nested mappings/lists,
non-string column names, invalid date modes, nonpositive header scan budgets,
non-boolean flags, malformed rule/filter structures, negative/nonfinite sum
tolerances, and incomplete JZ mapping structures raise `ConfigError` before source
parsing. Correction files require a profile, target column, nonempty match mapping,
expected old value and new value. See [config failure tests](../../tests/test_config_failures.py).

**Remaining limits:** this is not a complete semantic schema. Unknown extension keys
remain accepted; alias conflicts, missing transform columns and actual correction
matches are checked during preparation. Processor-specific column relationships and
destination type contracts remain unverified ([TD-002](../exec-plans/tech-debt-tracker.md)).

## Example: SGP mapping

```yaml
id: sgp
processor: tabular
columns:
  required: [DATE, NORM, OT]
  drop: [SCHEDULED START TIME, SCHEDULED END TIME]
  numeric: [NORM, OT]
dates:
  - {column: DATE, input: YMD, excel_format: yyyymmdd}
output: {format: xlsx, sheet: SGP}
```

This is illustrative; the *entire* actual profile includes aliases, negative-hour rules, and advisory reconciliations. For change review, inspect `config/profiles/sgp.yaml`.

## Compatibility and rule precedence

Explicit profile > `auto` when ambiguity exists. `--sheet` overrides sheet selection. Row-removal rules apply only through `exclude_rows`, not `reconciliation`. `--reference` can re-order output headers if and only if its column set matches; no type checks. Reviewed YAML correction files use `corrections` items with `{profile, match, column, expected_old, new_value}`; a correction must match exactly one row and old value.

**2026-11-26 correction contracts:** replacements are revalidated for numeric/date/nonnegative/non_null constraints. Comma decimals require an explicit local numeric convention; ordinary numeric parsing permits properly grouped thousands but rejects ambiguous `8,75` and nonfinite values. Dayforce exclusion uses exact cost_center_code plus expect_label; bare code or wrong label blocks. Source hashes and external attestations are audit evidence, not source-owner certification. See [operations](../OPERATIONS.md) for configuration examples and [EP-0007](../exec-plans/active/EP-0007-manual-parsing-corrections.md) for unresolved contracts.
