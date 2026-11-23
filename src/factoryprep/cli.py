"""Unified CLI entry point; all business differences come from YAML profile/plugin."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional
import json

import typer
import yaml

from .config import available_profiles, load_profile
from .detect import detect_profile
from .engine import format_report, run

app = typer.Typer(help="Factory Insights preparation and source-data quality checks (no BW integration)",
                  no_args_is_help=True)


@app.command("profiles")
def profiles(config_dir: Optional[Path] = typer.Option(None, help="Custom directory of YAML profiles")):
    """List available input workflows."""
    for name in available_profiles(config_dir):
        profile = load_profile(name, config_dir)
        typer.echo(f"{name:20} {profile.get('description','')}")


@app.command("detect")
def detect(input: Path = typer.Option(..., "--input", "-i"),
           config_dir: Optional[Path] = typer.Option(None, "--config-dir"),
           sheet: Optional[str] = typer.Option(None, "--sheet")):
    """Conservatively identify a single matching profile from filename and headers."""
    try:
        typer.echo(detect_profile(input, config_dir, sheet))
    except (ValueError, OSError) as exc:
        typer.echo(f"Could not uniquely detect profile: {exc}", err=True)
        raise typer.Exit(2) from exc


@app.command("describe")
def describe(profile: str, config_dir: Optional[Path] = None):
    """Show a profile's expected columns and preparation rules."""
    typer.echo(yaml.safe_dump(load_profile(profile, config_dir), sort_keys=False))


def _parse_week_ending(s: Optional[str]) -> date | None:
    if s is None:
        return None
    try:
        return date.fromisoformat(s)
    except ValueError as exc:
        raise typer.BadParameter("Use YYYY-MM-DD for --week-ending") from exc


def _execute(profile: str, input: Path, output: Optional[Path], config_dir: Optional[Path],
             sheet: Optional[str], week_ending: Optional[str], reference: Optional[Path],
             overrides: Optional[Path], strict: bool, report: Optional[Path],
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
    profile: str = typer.Option(..., "--profile", "-p", help="Workflow ID, e.g. gbr, or auto to detect"),
    input: Path = typer.Option(..., "--input", "-i", help="Original source workbook/CSV"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    config_dir: Optional[Path] = typer.Option(None, "--config-dir"),
    sheet: Optional[str] = typer.Option(None, "--sheet"),
    week_ending: Optional[str] = typer.Option(None, "--week-ending", help="Saturday YYYY-MM-DD"),
    reference: Optional[Path] = typer.Option(None, "--reference", help="Real destination header template"),
    overrides: Optional[Path] = typer.Option(None, "--overrides", help="Audited per-row corrections YAML"),
    strict: bool = typer.Option(False, "--strict", help="Warnings also block output"),
    report: Optional[Path] = typer.Option(None, "--report", help="Path for JSON quality report"),
):
    """Validate, normalize and generate a candidate prepared file (no BW loading)."""
    _execute(profile, input, output, config_dir, sheet, week_ending, reference,
             overrides, strict, report, False)


@app.command("validate")
def validate(
    profile: str = typer.Option(..., "--profile", "-p"),
    input: Path = typer.Option(..., "--input", "-i"),
    output: Optional[Path] = typer.Option(None, "--output", help="Output name used to locate report"),
    config_dir: Optional[Path] = typer.Option(None, "--config-dir"),
    sheet: Optional[str] = typer.Option(None, "--sheet"),
    week_ending: Optional[str] = typer.Option(None, "--week-ending"),
    reference: Optional[Path] = typer.Option(None, "--reference"),
    overrides: Optional[Path] = typer.Option(None, "--overrides"),
    strict: bool = typer.Option(False, "--strict"),
    report: Optional[Path] = typer.Option(None, "--report"),
):
    """Run every check, produce JSON report, but do not create prepared output."""
    _execute(profile, input, output, config_dir, sheet, week_ending, reference,
             overrides, strict, report, True)


@app.command("batch")
def batch(manifest: Path = typer.Option(..., "--manifest", help="YAML containing jobs list"),
          strict: bool = typer.Option(False, "--strict")):
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


if __name__ == "__main__":
    app()
