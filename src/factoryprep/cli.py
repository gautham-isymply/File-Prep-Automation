"""Unified CLI entry point; all business differences come from YAML profile/plugin."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Annotated

import typer
import yaml

from .config import available_profiles, load_profile
from .detect import detect_profile
from .drop import prepare_dropped
from .engine import format_report, run
from .reconcile import combine_reports

app = typer.Typer(help="Factory Insights preparation and source-data quality checks (no BW integration)",
                  no_args_is_help=True)


@app.command("profiles")
def profiles(config_dir: Annotated[Path | None, typer.Option(help="Custom directory of YAML profiles")] = None):
    """List available input workflows."""
    for name in available_profiles(config_dir):
        profile = load_profile(name, config_dir)
        typer.echo(f"{name:20} {profile.get('description','')}")


@app.command("detect")
def detect(input: Annotated[Path, typer.Option("--input", "-i")],
           config_dir: Annotated[Path | None, typer.Option("--config-dir")] = None,
           sheet: Annotated[str | None, typer.Option("--sheet")] = None):
    """Conservatively identify a single matching profile from filename and headers."""
    try:
        typer.echo(detect_profile(input, config_dir, sheet))
    except (ValueError, OSError) as exc:
        typer.echo(f"Could not uniquely detect profile: {exc}", err=True)
        raise typer.Exit(2) from exc


@app.command("describe")
def describe(profile: str, config_dir: Path | None = None):
    """Show a profile's expected columns and preparation rules."""
    typer.echo(yaml.safe_dump(load_profile(profile, config_dir), sort_keys=False))


def _parse_week_ending(s: str | None) -> date | None:
    if s is None:
        return None
    try:
        return date.fromisoformat(s)
    except ValueError as exc:
        raise typer.BadParameter("Use YYYY-MM-DD for --week-ending") from exc


def _execute(profile: str, input: Path, output: Path | None, config_dir: Path | None,
             sheet: str | None, week_ending: str | None, reference: Path | None,
             overrides: Path | None, strict: bool, report: Path | None,
             validate_only: bool) -> None:
    try:
        result = run(profile=profile, source=input, output=output, config_dir=config_dir,
                     sheet=sheet, week_ending=_parse_week_ending(week_ending),
                     reference=reference, overrides=overrides, strict=strict,
                     validate_only=validate_only, report_path=report)
    except (ValueError, OSError) as exc:
        typer.echo(f"Could not start: {exc}", err=True)
        raise typer.Exit(2) from exc
    typer.echo(format_report(result))
    if result.status == "FAILED":
        raise typer.Exit(2)


@app.command("prepare")
def prepare(
    profile: Annotated[str, typer.Option("--profile", "-p", help="Workflow ID, e.g. gbr, or auto to detect")],
    input: Annotated[Path, typer.Option("--input", "-i", help="Original source workbook/CSV")],
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
    config_dir: Annotated[Path | None, typer.Option("--config-dir")] = None,
    sheet: Annotated[str | None, typer.Option("--sheet")] = None,
    week_ending: Annotated[str | None, typer.Option("--week-ending", help="Saturday YYYY-MM-DD")] = None,
    reference: Annotated[Path | None, typer.Option("--reference", help="Real destination header template")] = None,
    overrides: Annotated[Path | None, typer.Option("--overrides", help="Reviewed corrections and source evidence YAML")] = None,
    strict: Annotated[bool, typer.Option("--strict", help="Warnings also block output")] = False,
    report: Annotated[Path | None, typer.Option("--report", help="Path for JSON quality report")] = None,
):
    """Validate, normalize and generate a candidate prepared file (no BW loading)."""
    _execute(profile, input, output, config_dir, sheet, week_ending, reference,
             overrides, strict, report, False)


@app.command("validate")
def validate(
    profile: Annotated[str, typer.Option("--profile", "-p")],
    input: Annotated[Path, typer.Option("--input", "-i")],
    output: Annotated[Path | None, typer.Option("--output", help="Output name used to locate report")] = None,
    config_dir: Annotated[Path | None, typer.Option("--config-dir")] = None,
    sheet: Annotated[str | None, typer.Option("--sheet")] = None,
    week_ending: Annotated[str | None, typer.Option("--week-ending")] = None,
    reference: Annotated[Path | None, typer.Option("--reference")] = None,
    overrides: Annotated[Path | None, typer.Option("--overrides")] = None,
    strict: Annotated[bool, typer.Option("--strict")] = False,
    report: Annotated[Path | None, typer.Option("--report")] = None,
):
    """Run every check, produce JSON report, but do not create prepared output."""
    _execute(profile, input, output, config_dir, sheet, week_ending, reference,
             overrides, strict, report, True)


@app.command("batch")
def batch(manifest: Annotated[Path, typer.Option("--manifest", help="YAML containing jobs list")],
          strict: Annotated[bool, typer.Option("--strict")] = False):
    """Prepare multiple files sequentially, each with its own YAML profile."""
    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise typer.BadParameter("Manifest needs a jobs: list")
    failed = 0
    for index, job in enumerate(data["jobs"], 1):
        try:
            result = run(profile=job["profile"], source=Path(job["input"]),
                         output=Path(job["output"]) if job.get("output") else None,
                         config_dir=Path(job["config_dir"]) if job.get("config_dir") else None,
                         sheet=job.get("sheet"),
                         week_ending=_parse_week_ending(job.get("week_ending")),
                         reference=Path(job["reference"]) if job.get("reference") else None,
                         overrides=Path(job["overrides"]) if job.get("overrides") else None,
                         strict=strict or job.get("strict", False),
                         report_path=Path(job["report"]) if job.get("report") else None)
            typer.echo(f"Job {index}/{len(data['jobs'])}:\n{format_report(result)}")
            if result.status == "FAILED":
                failed += 1
        except (ValueError, OSError, KeyError) as exc:
            failed += 1
            typer.echo(f"Job {index}: ERROR: {exc}", err=True)
    typer.echo(f"Batch complete: {len(data['jobs']) - failed} succeeded; {failed} failed")
    if failed:
        raise typer.Exit(2)


@app.command("drop")
def drop(
    files: Annotated[list[Path], typer.Argument(help="One or more source files")],
    profile: Annotated[str, typer.Option("--profile", "-p")] = "auto",
    config_dir: Annotated[Path | None, typer.Option("--config-dir")] = None,
    sheet: Annotated[str | None, typer.Option("--sheet")] = None,
    week_ending: Annotated[str | None, typer.Option("--week-ending")] = None,
    strict: Annotated[bool, typer.Option("--strict")] = False,
):
    """Prepare dropped files in fresh folders beside each source; never guess a profile."""
    if prepare_dropped(files, profile, config_dir, sheet, _parse_week_ending(week_ending), strict):
        raise typer.Exit(2)


@app.command("reconcile")
def reconcile(
    group: Annotated[str, typer.Option("--group")],
    reports: Annotated[list[Path], typer.Option("--component", help="Repeat for each component quality JSON")],
    output: Annotated[Path, typer.Option("--output", "-o")],
):
    """Combine two approved weekly CBG or US source audits."""
    try:
        result = combine_reports(group, reports, output)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        typer.echo(f"Cannot reconcile: {exc}", err=True)
        raise typer.Exit(2) from exc
    typer.echo(f"[{result['status']}] {group}: paid={result['paid_hours']}, OT={result['ot_hours']}")


if __name__ == "__main__":
    app()
