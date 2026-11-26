"""Conservative source-file profile detection; ambiguous matches MUST be resolved explicitly."""
from __future__ import annotations

from pathlib import Path

from .config import available_profiles, load_profile
from .io import read_book
from .transform import norm, parse_date


class DetectionError(ValueError):
    pass


def detect_profile(path: Path, config_dir: Path | None = None,
                   sheet: str | None = None) -> str:
    """Select only when one unambiguous source shape is recognized.

    Filename hints only break ties between otherwise identical source schemas;
    they never replace header verification.
    """
    book = read_book(path)
    sheets = [x for x in book.sheets if not sheet or x.name == sheet]
    if not sheets:
        raise DetectionError(f"Sheet {sheet!r} not present in workbook")
    possible: list[tuple[str, int]] = []
    for name in available_profiles(config_dir):
        spec = load_profile(name, config_dir)
        if spec.get("processor") == "reno":
            if _has_weekly_dates(sheets, spec.get("timecard", {}).get("date_input", "DMY")):
                possible.append((name, 7))
            continue
        column_cfg = spec.get("columns", {})
        required = column_cfg.get("required", [])
        if not required:
            continue
        aliases = column_cfg.get("aliases", {})
        accepted = [{norm(k), *(norm(x) for x in aliases.get(k, []))} for k in required]
        if any(any(all(bool(names & candidate) for candidate in accepted)
                   for names in _possible_headers(sh)) for sh in sheets):
            possible.append((name, len(required)))
    if not possible:
        raise DetectionError("No source profile matched the headers. Run 'profiles' and select explicitly.")
    maximum = max(count for _, count in possible)
    candidates = [name for name, count in possible if count == maximum]
    if len(candidates) == 1:
        return candidates[0]
    stem = path.stem.lower().replace("-", "_").replace(" ", "_")
    if set(candidates) == {"dayforce_ccb", "dayforce_non_ccb"}:
        if "non_ccb" in stem or "nonccb" in stem or "rest" in stem:
            return "dayforce_non_ccb"
        if "ccb" in stem:
            return "dayforce_ccb"
    raise DetectionError(f"Ambiguous matching workflows {candidates}; use --profile explicitly")


def _possible_headers(sheet) -> list[set[str]]:
    return [{norm(c.value) for c in row if c.value is not None}
            for row in sheet.rows[:45]]


def _has_weekly_dates(sheets, mode="DMY") -> bool:
    for sh in sheets:
        for row in sh.rows[:15]:
            found = set()
            for cell in row:
                try:
                    date = parse_date(cell.value, mode)
                    if 2020 <= date.year <= 2100:
                        found.add(date)
                except (TypeError, ValueError, OverflowError):
                    pass
            if len(found) >= 7:
                return True
    return False
