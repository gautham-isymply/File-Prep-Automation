"""Orchestration: never write output if an ERROR is present."""
from __future__ import annotations

from datetime import date
import json
from pathlib import Path
from typing import Any

from .config import load_profile, load_overrides
from .detect import detect_profile
from .io import read_book, read_reference_columns, write_prepared
from .models import Context, Prepared, RunReport
from .pipelines.jz import prepare_jz
from .pipelines.reno import choose_reno_sheet, prepare_reno
from .pipelines.tabular import prepare_tabular, select_tabular_sheet


def run(profile: str, source: Path, output: Path | None = None,
        config_dir: Path | None = None, sheet: str | None = None,
        week_ending: date | None = None, reference: Path | None = None,
        overrides: Path | None = None, strict: bool = False,
        validate_only: bool = False, report_path: Path | None = None) -> RunReport:
    source = Path(source)
    if profile == "auto":
        profile = detect_profile(source, config_dir, sheet)
    spec = load_profile(profile, config_dir)
    fmt = spec.get("output", {}).get("format", "xlsx")
    target = output or source.with_name(f"{source.stem}_{profile}_prepared.{fmt}")
    report_file = report_path or target.with_name(target.stem + "_quality.json")
    result = RunReport(profile, str(source))
    try:
        ctx = Context(spec, week_ending, sheet, load_overrides(overrides), strict, reference)
        if target.suffix.lower() != f".{fmt}":
            result.add("ERROR", "OUTPUT_EXTENSION_MISMATCH",
                       f"Profile creates {fmt.upper()}; output path must end in .{fmt}")
        if week_ending and week_ending.weekday() != 5:
            result.add("ERROR", "INVALID_WEEK_END", "Global week-ending must be a Saturday")
        if spec.get("source_schema_status") == "provisional":
            result.add("WARNING", "PROVISIONAL_SOURCE_SCHEMA",
                       "Manual lacks precise input layout; profile assumes declared staging columns. "
                       "Confirm mappings against an actual source file.")
        book = read_book(source)
        if spec.get("external_refresh"):
            result.add("WARNING", "EXTERNAL_REFRESH_NOT_PERFORMED",
                       "Excel linked/Power Query data is NOT refreshed by this program; "
                       "supply an already refreshed export")
        if spec.get("processor") == "reno":
            selected, index, dates = choose_reno_sheet(book.sheets, ctx)
            result.source_sheet = selected.name
            result.rows_in = max(0, len(selected.rows) - index - 1)
            prepared = prepare_reno(selected, index, dates, ctx, result)
        else:
            selected, index = select_tabular_sheet(book.sheets, ctx, result)
            result.source_sheet = selected.name
            result.rows_in = max(0, len(selected.rows) - index - 1)
            processor = prepare_jz if spec.get("processor") == "jz" else prepare_tabular
            prepared = processor(selected, index, ctx, result)
        result.rows_out = len(prepared.rows)
        result.columns_out = prepared.columns
        result.diagnostics = prepared.diagnostics
        if not prepared.rows:
            result.add("ERROR", "EMPTY_OUTPUT", "No usable rows in prepared output")
        if reference and prepared.columns:
            expected = read_reference_columns(reference)
            _validate_reference(prepared, expected, result)
        blocked = bool(result.errors or (strict and result.warnings))
        if blocked and target.exists() and source.resolve() != target.resolve():
            result.add("WARNING", "PREVIOUS_OUTPUT_REMAINS",
                       f"Old output at {target} was NOT replaced; do not treat it as this run's result")
        if not blocked and not validate_only:
            if source.resolve() == target.resolve():
                result.add("ERROR", "IN_PLACE_OVERWRITE", "Input and output must be different paths")
            else:
                tmp = target.with_name(f".{target.stem}.tmp{target.suffix}")
                try:
                    write_prepared(prepared, tmp, fmt)
                    tmp.replace(target)
                    result.output_path = str(target)
                finally:
                    if tmp.exists():
                        tmp.unlink()
        result.status = "FAILED" if result.errors or (strict and result.warnings) else (
            "VALIDATED" if validate_only else "PREPARED")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result.add("ERROR", "PREPARATION_FAILURE", str(exc))
        result.status = "FAILED"
    finally:
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(result.as_dict(), indent=2, default=str), encoding="utf-8")
    return result


def _validate_reference(prepared: Prepared, expected: list[str], report: RunReport) -> None:
    if len(expected) != len(set(expected)):
        report.add("ERROR", "INVALID_REFERENCE", "Destination reference contains duplicate columns")
        return
    missing = [x for x in expected if x not in prepared.columns]
    unexpected = [x for x in prepared.columns if x not in expected]
    if missing:
        report.add("ERROR", "DESTINATION_COLUMNS_MISSING", f"Template requires {missing}")
    if unexpected:
        report.add("ERROR", "DESTINATION_COLUMNS_EXTRA", f"Not expected by template: {unexpected}")
    if not missing and not unexpected:
        if prepared.columns != expected:
            report.add("INFO", "DESTINATION_COLUMN_ORDER", "Reordered output to reference template")
            prepared.columns = expected


def format_report(r: RunReport) -> str:
    lines = [f"[{r.status}] {r.profile} | source: {r.input_path}",
             f"Sheet: {r.source_sheet or '?'} | rows: {r.rows_in} -> {r.rows_out} | "
             f"errors: {r.errors} | warnings: {r.warnings}"]
    if r.output_path:
        lines.append(f"Output: {r.output_path}")
    for issue in r.issues[:30]:
        location = f" (row {issue.row}, {issue.column})" if issue.row else (
            f" ({issue.column})" if issue.column else "")
        lines.append(f"  {issue.severity}: {issue.code}{location}: {issue.message}")
    if len(r.issues) > 30:
        lines.append(f"  ... {len(r.issues) - 30} further issues in JSON report")
    return "\n".join(lines)
