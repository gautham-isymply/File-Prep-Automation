# YAML profile contract — v0.1.0 (implemented subset)

**Canonical reviewed copies:** `config/profiles/*.yaml` plus deployed copies `src/factoryprep/profiles/*.yaml`. Both must be byte-identical. By default `load_profile()` loads the embedded copy; pass `--config-dir config/profiles` to explicitly use development copies.

## Structure

| Key | Meaning / implementation |
|---|---|
| `id`, `description`, `processor` | required identity; `processor` ∈ `tabular`, `jz` |
| `columns.required` | canonical exact semantic headers, alias-aware for input |
| `columns.aliases` | canonical → equivalent labels; normalized by stripping punctuation/case |
| `columns.drop` | columns removed from prepared output, if present |
| `columns.expected` | optional complete schema; extra columns WARN, missing ERROR |
| `columns.numeric` / `negative_forbidden` | parse floats; block negatives for specified columns |
| `columns.non_null` / `duplicate_keys` | optional strict nulls / duplicate-key WARN |
| `dates` | list of `{column, input: DMY|MDY|YMD|auto, excel_format, split_delimiter?}` |
| `time_to_hours` | Excel fraction-of-day ×24 for selected columns, with ambiguity warnings |
| `header_scan_rows`, `skip_summary_rows` | detection budget; generic total-row detection |
| `exclude_rows` | *actual source row exclusion*, with optional expected label safeguard |
| `reconciliation` | `{name, column, filters}` diagnostics; `in`, `not_in`, `contains_any` supported by current metric implementation |
| `manual_review`, `cross_field_sums`, `date_continuity_column` | warning/anomaly checks |
| `external_refresh` | warning when linked data must have been refreshed outside Python |
| `source_schema_status: provisional` | risk warning for incomplete raw-source specification |
| `output.format`, `output.sheet`, `output.columns`, `output.date_format` | output destination; explicit fixed columns are used by the `jz` processor |
| `category_mapping` | processor-specific JZ fields |

**Caution:** This is an implementation description, **not** a published formal schema. Profile keys that are accepted by YAML but unused by a given processor will not automatically fail. No JSON Schema or Pydantic model currently enforces the entire contract ([TD-002](../exec-plans/tech-debt-tracker.md)).

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
