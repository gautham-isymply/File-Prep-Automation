"""Pure, reusable parsing and validation helpers (no per-plant logic)."""
from __future__ import annotations

import math
import re
from datetime import date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation
from difflib import get_close_matches
from typing import Any

from openpyxl.utils.datetime import from_excel

from .models import CellValue, RunReport

HEADER_NORMALIZER = re.compile(r"[^a-z0-9]+")


def norm(text: Any) -> str:
    return HEADER_NORMALIZER.sub("", str(text).strip().lower())


def _date_candidates(mode: str) -> list[str]:
    if mode == "DMY":
        return ["%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%d-%m-%y"]
    if mode == "MDY":
        return ["%m/%d/%Y", "%m/%d/%y", "%m-%d-%Y", "%m-%d-%y"]
    if mode == "YMD":
        return ["%Y/%m/%d", "%y/%m/%d"]
    return ["%Y-%m-%d", "%Y/%m/%d"]


def parse_date(value: Any, mode: str = "auto") -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, (int, float)):
        if float(value).is_integer() and 19000101 <= value <= 29991231:
            return datetime.strptime(str(int(value)), "%Y%m%d").date()
        if 20000 <= value <= 80000:
            excel_date = from_excel(value)
            return excel_date.date() if isinstance(excel_date, datetime) else excel_date
        raise ValueError(f"unrecognized numeric date {value!r}")
    s = str(value).strip()
    if not s:
        raise ValueError("blank date")
    if re.fullmatch(r"\d{8}", s):
        return datetime.strptime(s, "%Y%m%d").date()
    if re.fullmatch(r"\d{8}\.0", s):
        return datetime.strptime(s[:8], "%Y%m%d").date()
    for fmt in ["%Y-%m-%d", "%Y/%m/%d", *_date_candidates(mode)]:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    if mode == "auto" and re.fullmatch(r"\d{1,2}/\d{1,2}/\d{2,4}", s):
        a, b, _ = s.split("/")
        if int(a) > 12:
            return parse_date(s, "DMY")
        if int(b) > 12:
            return parse_date(s, "MDY")
        raise ValueError(f"ambiguous date {s!r}; specify DMY or MDY in profile")
    raise ValueError(f"invalid date {s!r} for {mode} convention")


def parse_number(value: Any, decimal_separator: str = ".") -> float:
    if isinstance(value, bool):
        raise TypeError("boolean is not a numeric hour")
    if isinstance(value, (int, float, Decimal)):
        result = float(value)
        if not math.isfinite(result):
            raise ValueError("number must be finite")
        return result
    if value is None or str(value).strip() == "":
        raise ValueError("blank number")
    raw = str(value).strip()
    if raw in {"-", "—"}:
        return 0.0
    if raw.endswith("%"):
        raise ValueError("unexpected percentage")
    if re.fullmatch(r"\d+:\d\d(?::\d\d)?", raw):
        parts = [int(x) for x in raw.split(":")]
        if parts[1] > 59 or (len(parts) == 3 and parts[2] > 59):
            raise ValueError("invalid hours clock")
        return parts[0] + parts[1] / 60 + (parts[2] / 3600 if len(parts) > 2 else 0)
    if raw.startswith("(") and raw.endswith(")"):
        raw = "-" + raw[1:-1]
    raw = raw.replace("$", "").replace("£", "").replace("€", "")
    if decimal_separator == ",":
        if not re.fullmatch(r"[+-]?\d+(?:,\d+)?", raw):
            raise ValueError("expected decimal-comma number without grouping")
        raw = raw.replace(",", ".")
    elif "," in raw:
        if not re.fullmatch(r"[+-]?\d{1,3}(?:,\d{3})+(?:\.\d+)?", raw):
            raise ValueError("ambiguous comma: declare decimal-comma encoding in profile")
        raw = raw.replace(",", "")
    try:
        result = float(Decimal(raw))
        if not math.isfinite(result):
            raise ValueError("number must be finite")
        return result
    except InvalidOperation as exc:
        raise ValueError(f"not a numeric value: {value!r}") from exc


def excel_hours(cell: CellValue, report: RunReport, row: int, column: str,
                encoding: str = "cell_format") -> float:
    """Convert Excel serial-time durations ×24, already decimal-hour values unchanged.

    Ambiguous unformatted fractions block; explicit units override cell formatting.
    The format check handles text HH:MM and datetime.time as durations.
    """
    value = cell.value
    if isinstance(value, timedelta):
        return round(value.total_seconds() / 3600, 8)
    if isinstance(value, (time, datetime)):
        t = value.time() if isinstance(value, datetime) else value
        return round(t.hour + t.minute / 60 + t.second / 3600, 8)
    if isinstance(value, str) and ":" in value:
        return parse_number(value)
    num = parse_number(value)
    if encoding == "decimal_hours":
        return num
    if encoding == "excel_days":
        return round(num * 24, 8)
    format_hint = cell.excel_format.lower()
    time_formatted = any(code in format_hint for code in ("h:", "[h]", "hh", "mm:ss"))
    if 0 < abs(num) < 1:
        if not time_formatted:
            report.add("ERROR", "AMBIGUOUS_TIME_FRACTION",
                       "Declare decimal_hours or excel_days for unformatted fractions",
                       row, column)
            raise ValueError("ambiguous hours encoding")
        return round(num * 24, 8)
    if time_formatted and abs(num) >= 1:
        # Durations >24h are possible in [h]:mm Excel format.
        return round(num * 24, 8)
    if num > 24:
        report.add("WARNING", "LARGE_HOURS_VALUE",
                   f"Unusually large hours value {num}; verify not Excel time serial", row, column)
    return num


def suggest_header(missing: str, seen: list[str]) -> str | None:
    options = get_close_matches(norm(missing), [norm(s) for s in seen], n=1, cutoff=0.65)
    if not options:
        return None
    for item in seen:
        if norm(item) == options[0]:
            return item
    return None


def is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())
