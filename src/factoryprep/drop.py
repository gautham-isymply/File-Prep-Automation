"""File-drop adapter; preparation and detection rules stay in the existing engine."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from tempfile import mkdtemp

import typer

from .config import load_profile
from .detect import detect_profile
from .engine import format_report, run


def prepare_dropped(
    files: list[Path], profile: str, config_dir: Path | None,
    sheet: str | None, week_ending: date | None, strict: bool,
) -> int:
    failed = 0
    for source in files:
        typer.echo(f"\nFile: {source}")
        try:
            source = source.resolve()
            if not source.is_file() or source.suffix.lower() not in {
                ".xlsx", ".xlsm", ".csv", ".tsv",
            }:
                raise ValueError("Drop an existing XLSX, XLSM, CSV or TSV file")
            selected = detect_profile(source, config_dir, sheet) if profile == "auto" else profile
            spec = load_profile(selected, config_dir)
            folder = Path(mkdtemp(prefix="factoryprep-", dir=source.parent))
            fmt = spec.get("output", {}).get("format", "xlsx")
            target = folder / f"{source.stem}_{selected}_prepared.{fmt}"
            typer.echo(f"Results folder: {folder}")
            result = run(
                profile=selected, source=source, output=target, config_dir=config_dir,
                sheet=sheet, week_ending=week_ending, strict=strict,
            )
            typer.echo(format_report(result))
            failed += result.status == "FAILED"
        except (ValueError, OSError) as exc:
            failed += 1
            typer.echo(f"Could not prepare: {exc}", err=True)
            typer.echo("Use prepare --profile PROFILE --input FILE with any required "
                       "--sheet or --week-ending options.", err=True)
    typer.echo(f"Drop complete: {len(files) - failed} succeeded; {failed} failed")
    return failed
