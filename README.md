# FactoryPrep — Factory Insights File Preparation CLI

> **Agent navigation:** start at [AGENTS.md](AGENTS.md) → [docs/index.md](docs/index.md); see [current state](docs/progress/CURRENT_STATE.md).


A **Python 3.11+ / uv** tool that prepares manual Factory Insights source files and produces structured quality reports. It intentionally does **not** connect to SAP BW, execute DTPs, delete BW data, send emails, or update PBI.

This project was derived from the user-provided *FactoryInsights_MANUAL_LOAD_Process.docx* (39 pages). The implementation preserves its **pre-load / file preparation** scope; downstream ADSO SQL and SAP steps are excluded. Source file examples and actual destination extracts were **not** attached, so the profiles are a starting implementation, **not** a verified SAP load contract.

## Quick start

Install [uv](https://docs.astral.sh/uv/) if it is not installed. `uv sync` resolves dependencies against your package registry (internet or a configured company mirror is needed). A `uv.lock` is not bundled because the isolated build environment had no access to PyPI; generate it in your own environment with `uv lock` and commit it to your repository for reproducible deployment.

```bash
# From the unzipped project root:
uv sync --extra dev
uv run factoryprep profiles
uv run factoryprep describe gbr
uv run factoryprep detect --input /path/to/an_export.xlsx

# Prepare one file (output is new; original is untouched):
uv run factoryprep prepare --profile auto --input /path/to/sgp.xlsx \
  --output /path/to/sgp_prepared.xlsx

# Validate without creating an output file:
uv run factoryprep validate --profile sgp --input /path/to/sgp.xlsx

# Validate exact target columns using a real single-sheet load template:
uv run factoryprep prepare --profile ccb --input /path/to/ccb.xlsx \
  --reference /path/to/ccb_destination_template.xlsx \
  --output /path/to/ccb_prepared.xlsx

# Process a declared set of files:
uv run factoryprep batch --manifest config/examples/batch.yaml

# Run tests:
uv run pytest -q
```

For each run, a `*_quality.json` report is generated next to the expected output, **even when preparation fails**. Output is only written when there are no ERRORs. `--strict` also blocks WARNINGs. Exit status `2` represents a validation/preparation failure.

## Workflow inventory

| `--profile` | Input file described in manual | Output preparation | Manual pages |
|---|---|---|---|
| `sgp` | SGP attendance workbook | Date `yyyymmdd`; drop scheduled start/end columns | 1–2 |
| `gbr` | GBR WorkSegments workbook | DMY date normalization; `REGHOURS`, `O1HOURS`, `O2HOURS` Excel fractions ×24 | 5–9 |
| `cbg_core` | CBG Starline Core2 | Skip preamble/total rows; `Pay Rate` numeric; sheet `Core` | 12–13 |
| `cbg_starline` | CBG Starline SSI | `W/E Date` normalization; delete `Shift`; numeric `BRD` | 13–16 |
| `ccb` | CCB hours workbook | Numeric Reg/OT/Total; delete `Notes`; flag manual 65.8 example | 20–22 |
| `jz` | JZ-BUS / JZ-DAT category-level source | Five rows mapped to BUSWAY/COP/FIB/RAC/DAT and Sunday date | 29–30 |
| `dayforce_ccb` | Dayforce CCB export | Remove `3600172100 > Receiving Farmingdale`; audit category totals | 32–35 |
| `dayforce_non_ccb` | Dayforce non-CCB export | Validate fields and compute Reg / OT totals by location + cost center | 32–35 |

**Important distinction:** filters used in the manual to *validate totals after a load* (SGP departments, GBR departments and leave codes, CBG pay codes/charge codes, CCB CCs, Dayforce category/location filters) are **used for reconciliation metrics only**. They do **not** remove rows from the prepared source. Only documented pre-load exclusions remove rows (such as Dayforce Receiving Farmingdale).

## Commands

```text
factoryprep profiles [--config-dir PATH]
factoryprep detect --input FILE [--sheet NAME]
factoryprep describe PROFILE [--config-dir PATH]
factoryprep prepare --profile ID|auto --input FILE [--output FILE]
                    [--sheet NAME] [--week-ending YYYY-MM-DD]
                    [--reference TEMPLATE.xlsx] [--overrides corrections.yaml]
                    [--strict] [--report JSON_FILE] [--config-dir PATH]
factoryprep validate (same flags as prepare; never writes the prepared file)
factoryprep batch --manifest jobs.yaml [--strict]
```

Automatic profile selection (`--profile auto`) is conservative: it matches required headers and refuses ambiguous Dayforce variants unless the filename distinguishes them. Supply `--profile` explicitly whenever a workbook has multiple applicable source tabs. The output filename extension must match the profile (`.xlsx` for all bundled profiles). CSV uses UTF-8 with BOM for Excel compatibility. Source `xls` files must first be exported to `xlsx` because `openpyxl` does not read legacy `.xls`. Excel formulas, macros, OData/PowerQuery connections, and linked source refreshes are **never executed** by this CLI.

## Reports, issues, and governance

The JSON report includes source path, selected sheet, input/output row counts, output columns, errors, warnings, details (`row` uses the actual Excel row number), excluded-row count, and filtered source totals. Examples of codes:

- `MISSING_COLUMN`, `DUPLICATE_HEADER`, `EXPECTED_COLUMN_MISSING`, `DESTINATION_COLUMNS_MISSING`, `DESTINATION_COLUMNS_EXTRA`, `HEADER_NORMALIZED`
- `FORMAT_MISMATCH`, `EXCEL_CELL_ERROR`, `AMBIGUOUS_TIME_FRACTION`, `NULL_VALUE`, `NEGATIVE_VALUE`, `MISSING_DATES`, `TOTAL_MISMATCH`
- `MANUAL_REVIEW_REQUIRED`, `OVERRIDE_MATCH_FAILURE`, `UNKNOWN_BUSINESS_LABEL`, `RECONCILIATION_COLUMNS_MISSING`, `EXTERNAL_REFRESH_NOT_PERFORMED`

`--reference` is the recommended way to assert **the exact load-file column set and ordering** after receiving the true destination template. Without it, the tool can validate known columns from the manual but cannot prove the full SAP layout.

### Approved, row-keyed corrections

CCB has an example of replacing **one specific row's** `65.8` regular hours with `75.8`. Changing *every* `65.8` would corrupt data, so the default policy is to **flag** it, not edit it.

To apply a reviewed change, create `corrections.yaml` based on `config/examples/approved_corrections.yaml` with enough `match:` keys to identify **exactly one row**, and specify `expected_old` and `new_value`. Then:

```bash
uv run factoryprep prepare --profile ccb --input /path/to/ccb.xlsx \
  --overrides /path/to/approved_corrections.yaml \
  --output /path/to/ccb_prepared.xlsx
```

The override is rejected if zero/multiple rows match or the old value has changed; corrections are recorded in the JSON report.

## How to add or change a workflow

1. Start from a YAML file in `config/profiles/`; `id` must match the YAML filename.
2. Set `columns.required`, `columns.aliases`, `columns.numeric`, `columns.drop`, and `dates` with explicit source date conventions.
3. Define `reconciliation` filters to calculate quality-control totals, **not** to delete rows.
4. Configure `output.format` and `output.sheet`; for a rigid target layout, supply a true template with `--reference` or configure `output.columns` for a specialized pipeline.
5. Run `uv run pytest -q`, and add representative actual source-based fixtures (without confidential data) for the updated profile.
6. For new source shapes, add a file to `src/factoryprep/pipelines/` and dispatch it from `engine.py`.

Default profiles are embedded inside `src/factoryprep/profiles/` so installed/wheel-based use works. `config/profiles/` is the editable master copy in this project. **When editing a built-in profile, copy it to the embedded directory or use `--config-dir config/profiles`** to force the editable copy. For long-term use, maintain one repository-controlled canonical config directory and pass it in deployment.

## Source assumptions requiring real-file confirmation

1. **Exact SAP load schema.** Most workflows' complete output columns are not listed in the manual; the program preserves source column order except for known removals. The CCB profile treats `Dept` and the manual's `CC` as aliases for reconciliation; confirm this equivalence against a real file. Actual target headers, column order, workbook sheet names, and representations of dates must be verified with a template and `--reference`.
2. **GBR hours encoding.** The manual says to multiply Excel time fractions by 24. The CLI converts Excel serial fractions and clock times, but passes already-decimal numeric hours through; ambiguous fractions are reported. Confirm representative samples before production.
3. **CCB manual adjustment.** Manual's `65.8 → 75.8` example does not provide a robust unique business key; reviewed per-row overrides are mandatory for changing it.
4. **JZ source structure.** The manual shows the *target* mapping and mentions **Invoice Hours in `HC`** but does not provide a machine-readable raw source layout or paid-vs-OT extraction rules. The `jz` profile expects a **normalized source sheet with `Category`, `Paid Hours`, `OT Hours`**; it emits a provisional-schema warning. The program does not infer or invent the HC paid/OT split. An actual JZ file is needed before direct-raw-source parsing is production-ready. This is the one workflow where upstream staging must currently be supplied instead of feeding the original arbitrary workbook directly.
5. **Dayforce automatic refresh.** Opening the original files in Excel refreshes external data according to the manual. This program cannot trigger that refresh; feed it already-refreshed exports. Every Dayforce run reports this limitation.
6. **Week calendar discrepancy.** The manual's introduction specifies **Sunday–Saturday**, while some later SQL examples use a Monday/Sunday range. The tool adopts the stated Sunday–Saturday convention; verify SAP validation windows separately (out of scope).
7. **CBG ambiguous date instructions.** The Core2/SSI screenshots and text do not fully enumerate the original headers, and the SSI wizard's YMD selection conflicts with the shown US-style display. The profile uses MDY parsing and `m/d/yyyy` output, which must be validated with a genuine SSI workbook.

## Safety boundaries

- Never changes the source file; prepared output is written via a temporary file, then atomically renamed.
- Reports exact header/format problems and fails before writing any new output when critical checks fail.
- Does not manufacture missing source rows, dates, daily hours or overtime values beyond the declared profile mapping.
- Includes the requested weekly source preparation only; no BW stage deletion, DTPs, ADSOs, emails or PBI.
- A failed run will not remove a previously generated output; the JSON report warns if an old output remains, so operators must use the report/status, not just file existence.
