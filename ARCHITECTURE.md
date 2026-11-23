# Architecture — FactoryPrep v0.1.0

**Status:** inspected against source as of 2026-11-23; functional baseline verified by 19 local tests. **Scope:** source-file preparation, format validation, candidate output and JSON audit. BW integration is intentionally absent. Detailed behavior lives in [design docs](docs/design-docs/index.md).

## Dataflow and trust boundaries

```text
User input / batch manifest / optional template, override
        |
CLI: src/factoryprep/cli.py
        | profile selection: detect.py + config.py
        v
read_book(): io.py -> SourceBook / RawSheet / CellValue
        |  [UNTRUSTED: files, headers, cell values]
        v
engine.run() -> Context -> processor dispatch
        |-- tabular: pipelines/tabular.py (8 profiles)
        |-- reno:    pipelines/reno.py (1 profile)
        `-- jz:      pipelines/jz.py (1 provisional profile)
        |  transform.py: parse dates, numeric/hours, label normalization
        v
Prepared rows + issues + diagnostic reconciliation totals
        |  optional destination HEADER comparison (not type validation)
        v
Quality gate: ERROR blocks; --strict also blocks WARNING
        |-- fail/validate-only -> JSON report
        `-- pass/prepare    -> temporary candidate file -> replace target + JSON report
```

## Module ownership and edges

| Module | What it owns | May depend on |
|---|---|---|
| `models.py` | `CellValue`, `SourceBook`, `Prepared`, `Context`, `Issue`, `RunReport` | stdlib |
| `transform.py` | Pure normalizers; time/date/number parsing | models, openpyxl |
| `config.py` | Load YAML, shallow config checks, correction files | stdlib, yaml |
| `io.py` | Read xlsx/xlsm/csv/tsv, write xlsx/csv, reference headers | models, openpyxl |
| `detect.py` | Conservative header + filename profile detection | config, io, transform |
| `pipelines/tabular.py` | Header selection, row cleanup, validation, source metrics | models, transform |
| `pipelines/reno.py` | Seven-day timecard aggregation | models, transform |
| `pipelines/jz.py` | Five-category-to-profit-center transformation | models, transform, tabular |
| `engine.py` | Orchestration, quality gate, report, output lifecycle | config, detect, io, models, pipelines |
| `cli.py` | Typer commands, CLI exit codes and sequential batch | config, detect, engine |

Rule for new work: extend a YAML profile when behavior fits the tabular primitives; create a pipeline module only for distinct input shape/aggregation. Do not add business-specific parsing to `cli.py` or `io.py`. **This is a documented target boundary, not yet enforced by an import linter** ([TD-006](docs/exec-plans/tech-debt-tracker.md)).

## Operational invariants

1. Source is never overwritten; existing target is **not** deleted on failure.
2. `RunReport` is the only public result contract; it records `status`, issues, counts, output columns and diagnostics.
3. The report is written even for errors caught after `run()` begins; failures before `run()` and some batch errors may not produce a report.
4. `--reference` checks destination **column names and order only**; no type/format/row-level template verification.
5. Reconciliation filters affect totals in the report, not source rows; declared `exclude_rows` is the exception.
6. `--strict` blocks WARNINGs; regular mode blocks only ERRORs.
7. Excel dates in `.xlsx` remain date-typed with a number format; a display pattern such as `yyyymmdd` is not the same as eight-character text.

## Navigate by concern

- [YAML profile schema](docs/design-docs/PROFILE_CONTRACT.md)
- [Data model and module interfaces](docs/design-docs/MODULE_CONTRACTS.md)
- [Validation and reporting](docs/design-docs/QUALITY_GATES.md)
- [Operational reliability](docs/RELIABILITY.md)
- [Process-specific contracts](docs/processes/index.md)
- [Known risks and architecture debt](docs/exec-plans/tech-debt-tracker.md)
