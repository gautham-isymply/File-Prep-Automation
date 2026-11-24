# Operations runbook — source preparation only

## Setup and inspect

```bash
uv sync --extra dev
uv run factoryprep profiles
uv run factoryprep describe sgp
uv run factoryprep detect --input SOURCE.xlsx
```

`--profile auto` is safe only where uniquely recognized. Prefer explicit profile for Dayforce twins and multi-tab workbooks. Use `--sheet` when multiple sheets match. `.xls` must first be exported to `.xlsx`; macro/formula/query execution is not supported.

## Validate then prepare

```bash
uv run factoryprep validate --profile sgp --input SOURCE.xlsx --strict
uv run factoryprep prepare --profile sgp --input SOURCE.xlsx --output SGP_prepared.xlsx   --reference APPROVED_SINGLE_SHEET_HEADER.xlsx --report SGP_quality.json
uv run factoryprep prepare --profile jz --input NORMALIZED_JZ.xlsx --week-ending 2026-02-28
uv run factoryprep batch --manifest config/examples/batch.yaml
```

`validate` writes a JSON report but no prepared output. In regular mode, WARNINGs do not block; `--strict` makes warnings blocking. Exit `2` is an expected failed quality gate. JSON report is stored next to the target by default with `_quality.json` suffix. Do **not** consume a prepared file simply because it exists; old outputs remain after a failed run.

## Triage protocol

1. Check `status`, `summary.errors`, `summary.warnings`, then ordered `issues[].code`, `row`, `column` in report.
2. Match error to one [process contract](processes/index.md) and exact YAML; compare to actual file headers/type and manual page.
3. For output-header mismatch, obtain a verified destination template; no blind header reordering/renaming.
4. For CCB manual 65.8 example, require an approved row-keyed override; never change all rows matching that number.
5. For Dayforce, ensure external refresh was performed before source export; CLI cannot verify freshness.
6. For a failed run, quarantine old prepared output outside the consumer's input directory until a new status PREPARED is confirmed.

Source confidentiality: avoid committing raw employee names/timecards or internal financial details. Use synthetic and properly sanitized fixtures. See [security](SECURITY.md) and [reliability](RELIABILITY.md).
