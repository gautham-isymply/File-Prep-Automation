# Module and data contracts (as implemented)

**Code as source of truth:** `src/factoryprep`. This document describes exposed functions and ownership, not an API compatibility guarantee.

## Records (`models.py`)

- `CellValue(value, excel_format, excel_type)` retains original cell formatting/type information needed to interpret Excel time fractions.
- `RawSheet(name, rows)` and `SourceBook(path, sheets)` represent loaded input, with `rows` as cell grids.
- `Context(profile, week_ending, sheet_override, overrides, strict, reference)` passes validated input options to processors.
- `Prepared(columns, rows, sheet_name, date_formats, diagnostics, source_rows)` is the processor output. Rows are mapping objects; tabular pipeline retains source row numbers.
- `Issue(severity, code, message, row?, column?, source?)`; `RunReport` collects issues and run summary.

## Function flow

| Function | Inputs → outputs | Important behavior |
|---|---|---|
| `detect.detect_profile` | path + optional sheet → profile id or error | header verification; filename disambiguates Dayforce only |
| `config.load_profile` | profile id + optional directory → dict | checks identity, processor, output format and some list fields; **not full schema validation** |
| `io.read_book` | path → `SourceBook` | xlsx/xlsm `data_only=True`, CSV delimiter sniff; not `.xls` |
| `tabular.select_tabular_sheet` | sheets + Context → `(sheet, header_index)` | best required-header score; tie requires explicit sheet |
| `tabular.prepare_tabular` | sheet + header + Context + report → `Prepared` | aliases, data checks, exclusion, transformations, advisory metrics |
| `reno.choose_reno_sheet` | sheets + Context → sheet/header/date columns | finds 7 dates in first 15 rows |
| `reno.prepare_reno` | sheet/header/dates + Context → `Prepared` | 7 daily sums and 0 OT template |
| `jz.prepare_jz` | sheet/header + Context → `Prepared` | requires normalized category/paid/OT input and Saturday |
| `engine.run` | run args → `RunReport` | dispatch, quality gate, reference headers, atomic candidate output, JSON report |
| `cli.app` | Typer commands | exit 2 on validation failure |

## Allowed extension pattern

Profile change → `config/profiles/<id>.yaml` and `src/factoryprep/profiles/<id>.yaml` → one process doc → tests. A new shape → `pipelines/<name>.py` + small `engine.py` dispatch; do not place source-specific business rules in `cli.py`, `io.py`, `models.py`.

## Known API limitations

The profile config shape is only shallowly checked. Some errors are reported after readers start; CLI input errors may exit before a JSON report is created. Input is materialized as a complete in-memory grid. Current record diagnostics do not carry row-level provenance for every derived aggregate. See [debt](../exec-plans/tech-debt-tracker.md).
