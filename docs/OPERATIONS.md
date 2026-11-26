# Operations runbook — source preparation only

## Windows executable and drag-and-drop

On a Windows build PC with Python 3.11+ and uv, run from the repository:

```powershell
.\scripts\build_exe.ps1
```

The script also runs `scripts/smoke_exe.py` against a standalone copy outside the
checkout, using only synthetic CSV inputs, and fails if the smoke check fails.

Copy `dist\factoryprep.exe` to the receiving Windows PC; Python and uv are not
required there. Build on the Windows architecture you intend to distribute.
The console build includes the ten default YAML profiles using
[PyInstaller's data-file support](https://pyinstaller.org/en/stable/spec-files.html#adding-data-files).

```powershell
.\factoryprep.exe --help
.\factoryprep.exe profiles
.\factoryprep.exe prepare --profile sgp --input "C:\Exports\source.xlsx"
.\factoryprep.exe drop "C:\Exports\first.xlsx" "C:\Exports\second.csv"
.\factoryprep.exe drop "C:\Exports\source.xlsx" --profile sgp --strict
```

In Explorer, select one or more XLSX/XLSM/CSV/TSV files and drop them onto the EXE
(or a shortcut to it). Bare paths also work in the terminal. Each file uses
conservative profile detection and gets a new `factoryprep-...` folder beside the
source, containing prepared output on success and its JSON quality report.
Repeat drops create new folders. The source directory must be writable.
Files run sequentially; a failed file does not stop the remaining files.
Exit code 2 means at least one failed. Detection failures occur before an output
folder/report is created and print instructions in the console.

Ambiguous profiles, sheets and missing business inputs are never inferred.
Use `drop --profile`, `--sheet`, `--week-ending`, `--config-dir` or the existing
`prepare` command for `--reference`, `--overrides`, and custom output/report paths.
An Explorer-created console waits for Enter after completion or failure. Double-click
with no files displays help. Terminal commands return normally without waiting.

## Python setup and inspect

```bash
uv sync --extra dev
uv run factoryprep profiles
uv run factoryprep describe sgp
uv run factoryprep detect --input SOURCE.xlsx
```

`--profile auto` is safe only where uniquely recognized. Prefer explicit profile for Dayforce twins and multi-tab workbooks. Use `--sheet` when multiple sheets match. `.xls` must first be exported to `.xlsx`; macro/formula/query execution is not supported.

## Validate then prepare

```bash
uv run factoryprep validate --profile sgp --input SOURCE.xlsx --week-ending 2026-03-14 --strict
uv run factoryprep prepare --profile sgp --input SOURCE.xlsx --output SGP_prepared.xlsx   --reference APPROVED_SINGLE_SHEET_HEADER.xlsx --report SGP_quality.json
uv run factoryprep prepare --profile reno --input TIMECARDS.xlsx --week-ending 2026-03-07
uv run factoryprep prepare --profile jz --input NORMALIZED_JZ.xlsx --week-ending 2026-02-28
uv run factoryprep batch --manifest config/examples/batch.yaml
```

`validate` writes a JSON report but no prepared output. In regular mode, WARNINGs do not block; `--strict` makes warnings blocking. Exit `2` is an expected failed quality gate. JSON report is stored next to the target by default with `_quality.json` suffix. Do **not** consume a prepared file simply because it exists; old outputs remain after a failed run.

## Triage protocol

1. Check `status`, `summary.errors`, `summary.warnings`, then ordered `issues[].code`, `row`, `column` in report.
2. Match error to one [process contract](processes/index.md) and exact YAML; compare to actual file headers/type and manual page.
3. For output-header mismatch, obtain a verified destination template; no blind header reordering/renaming.
4. For CCB manual 65.8 example, require an approved row-keyed override; never change all rows matching that number.
5. For Dayforce, refresh and save/export externally, then provide a source-bound attestation as below. Python verifies its hash, not the truth of the attestation.
6. For a failed run, quarantine old prepared output outside the consumer's input directory until a new status PREPARED is confirmed.

Source confidentiality: avoid committing raw employee names/timecards or internal financial details. Use synthetic and properly sanitized fixtures. See [security](SECURITY.md) and [reliability](RELIABILITY.md).

## Manual correction contracts (2026-11-26)

Weekly metrics require `--week-ending YYYY-MM-DD` (Saturday). Date predicates affect diagnostics only. Missing period omits the weekly totals with a warning. Taiwan uses the requested week to detect missing boundary days; strict mode blocks missing dates. CBG Core's bundled department filter is incomplete, so its totals remain provisional.

Copy a complete profile into a reviewed custom directory and pass `--config-dir` to declare supported business contracts. Keep its id unchanged. GBR `hours_encoding` maps each hour column to `excel_days`, `decimal_hours` or default `cell_format`. The default handles explicit duration cells/clock text and treats unformatted values of at least one as decimal hours; unformatted fractions block. Review unformatted units against a real source before acceptance. Setting `excel_days` on already-converted numbers would double-convert them; prepared workbooks should retain numeric format/units.

Reno's default `timecard` is DMY text dates, comma decimals, blank_hours error and no zero_tokens. Explicit owner-approved zero handling can be declared in a custom profile, for example `blank_hours: zero` and `zero_tokens: [term]`; every use is audited. This example is **not** approval of those meanings. Missing source dates always block and are never filled. Table bounds use absolute one-based worksheet row numbers; summary_columns use canonical column names. Unknown trailers block numeric/date validation until the actual boundaries are reviewed.

Dayforce requires an overrides file with this structure (replace every illustrative value with the actual saved export's evidence):

```yaml
source_evidence:
  sha256: "<64-character SHA-256 of the refreshed saved source>"
  refreshed_at: "2026-11-26T09:00:00-05:00"
  approved_by: "<source owner or evidence reference>"
corrections: []
```

Compute the digest with `Get-FileHash -Algorithm SHA256 SOURCE.xlsx`. Supply this file using `prepare`/`validate --overrides REFRESH.yaml`, with an explicit profile and --week-ending. Each source needs its own matching evidence; batch manifests accept per-job overrides. Missing/mismatched evidence blocks regular as well as strict preparation. A fresh-looking date alone is insufficient; no Excel/OData refresh is executed.

JZ raw extraction requires a complete custom JZ profile with `source_mode: raw_cells` and an owner-approved `raw_source` contract. Retain category_mapping/output/column rules from the bundled profile. Supply sheet, approval reference, week_ending_cell, explicit date_input and categories mapping **every** known category to label_cell/paid_cell/ot_cell A1 addresses. All addresses must be distinct. Example shape for one category only:

```yaml
source_mode: raw_cells
raw_source:
  sheet: "<actual source sheet>"
  approval: "<approved Paid/OT mapping reference>"
  week_ending_cell: A1
  date_input: DMY
  categories:
    Direct Hours (Starline): {label_cell: A3, paid_cell: B3, ot_cell: C3}
    # Add all four other categories with reviewed, distinct cells.
```

The illustrative addresses are not the actual HC layout. Do not use this incomplete example on production files. No default raw HC mapping or paid/OT derivation is supplied. Normalized staging remains supported and provisional.

After preparing or validating both US files with matching weeks and attestations:

```bash
uv run factoryprep reconcile --group us --component CCB_quality.json --component NON_CCB_quality.json --output US_weekly_audit.json
```

Use `--group cbg` with Core and SSI reports only after a custom Core profile supplies approved department filters, a parsed reconciliation_date_column and `reconciliation_contract_confirmed: true`. Missing evidence blocks combination. The combined artifact is local source totals, not downstream validation.
