"""Reno weekly employee timecards -> seven daily rows for plant 3601."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from ..models import Context, Prepared, RawSheet, RunReport
from ..transform import is_blank, parse_date, parse_number, norm


def _dates_in_row(row: list) -> dict[int, date]:
    dates: dict[int, date] = {}
    for index, cell in enumerate(row):
        try:
            val = parse_date(cell.value, "MDY")
        except (ValueError, TypeError):
            continue
        if date(2020, 1, 1) <= val <= date(2100, 12, 31):
            dates[index] = val
    return dates


def choose_reno_sheet(sheets: list[RawSheet], ctx: Context) -> tuple[RawSheet, int, dict[int, date]]:
    candidates = []
    for sheet in sheets:
        if ctx.sheet_override and ctx.sheet_override != sheet.name:
            continue
        for i, row in enumerate(sheet.rows[:15]):
            dates = _dates_in_row(row)
            if len(set(dates.values())) >= 7:
                candidates.append((sheet, i, dates))
                break
    if not candidates:
        raise ValueError("Could not locate a Reno daily date header (7 dates) in first 15 rows")
    if len(candidates) > 1:
        raise ValueError("Multiple Reno timecard sheets detected: use --sheet")
    return candidates[0]


def prepare_reno(sheet: RawSheet, header_index: int, date_columns: dict[int, date],
                 ctx: Context, report: RunReport) -> Prepared:
    week_ending = ctx.week_ending or max(date_columns.values())
    if week_ending.weekday() != 5:
        report.add("ERROR", "INVALID_WEEK_END", f"Expected Saturday week-ending date, got {week_ending}")
    expected = [week_ending - timedelta(days=n) for n in range(6, -1, -1)]
    col_by_date = {dt: col for col, dt in date_columns.items()}
    if len(col_by_date) != len(date_columns):
        report.add("ERROR", "DUPLICATE_WEEK_DATES", "Repeated dates in Reno timecard header")
    missing = [day for day in expected if day not in col_by_date]
    extra = [day for day in col_by_date if day not in expected]
    if missing:
        report.add("ERROR", "MISSING_WEEK_DATES", f"Missing date columns: {missing}")
    if extra:
        report.add("WARNING", "OTHER_WEEK_DATES", f"Other date columns ignored: {extra}")
    totals = {day: 0.0 for day in expected}
    populated = 0
    # A timecard may include an employee Total column after the seven dates.
    # Do not treat it as a daily source column; use it to check row arithmetic.
    total_col = None
    for i in (header_index, header_index + 1):
        if i >= len(sheet.rows):
            continue
        for k, cell in enumerate(sheet.rows[i]):
            if norm(cell.value) in {"total", "totalhrs", "totalhours"}:
                total_col = k
    rows_in = 0
    for origin, cells in enumerate(sheet.rows[header_index + 1:], start=header_index + 2):
        row_vals = [c.value for c in cells]
        if not any(not is_blank(x) for x in row_vals):
            continue
        first = str(row_vals[0] or "").strip().lower()
        if first in {"name", "total", "totals", "grand total", "agency", "subtotal"}:
            continue
        if first.startswith("week") or first.startswith("date"):
            continue
        rows_in += 1
        has_hours = False
        for day in expected:
            index = col_by_date.get(day)
            if index is None or index >= len(cells):
                continue
            value = cells[index].value
            if is_blank(value):
                continue
            try:
                hours = parse_number(value)
                if hours < 0:
                    report.add("ERROR", "NEGATIVE_HOURS", f"Negative Reno hours {hours}", origin, str(day))
                if hours > 24:
                    report.add("WARNING", "LONG_SHIFT", f"Hours >24 for one employee/day: {hours}",
                               origin, str(day))
                totals[day] += hours
                has_hours = True
            except ValueError as exc:
                report.add("ERROR", "INVALID_TIMECARD_HOURS", str(exc), origin, str(day))
        if has_hours:
            populated += 1
            if total_col is not None and total_col < len(cells) and not is_blank(cells[total_col].value):
                try:
                    row_total = parse_number(cells[total_col].value)
                    row_sum = sum(parse_number(cells[col_by_date[d]].value)
                                  for d in expected if d in col_by_date
                                  and col_by_date[d] < len(cells)
                                  and not is_blank(cells[col_by_date[d]].value))
                    if abs(row_total - row_sum) > 0.02:
                        report.add("WARNING", "EMPLOYEE_TOTAL_MISMATCH",
                                   f"Timecard total {row_total} vs daily hours {row_sum}",
                                   origin, "Total")
                except ValueError:
                    report.add("WARNING", "INVALID_EMPLOYEE_TOTAL",
                               "Could not parse employee Total for reconciliation", origin, "Total")
    if not populated:
        report.add("ERROR", "NO_TIMECARD_DATA", "No employee/day hours found")
    defaults = ctx.profile.get("defaults", {})
    columns = ctx.profile.get("output", {}).get("columns", [
        "Segment", "Plant", "Plant name", "Profitcent", "Companycode", "Date", "Paid Hours", "OT Hours"
    ])
    rows = [{"Segment": defaults["segment"], "Plant": str(defaults["plant"]),
             "Plant name": defaults["plant_name"], "Profitcent": defaults["profit_center"],
             "Companycode": str(defaults["company_code"]), "Date": day,
             "Paid Hours": round(totals[day], 8), "OT Hours": 0.0}
            for day in expected]
    return Prepared(columns, rows, ctx.profile.get("output", {}).get("sheet", "Reno"),
                    {"Date": ctx.profile.get("output", {}).get("date_format", "yyyy-mm-dd")},
                    diagnostics={"weekly_paid_hours": round(sum(totals.values()), 6),
                                 "employee_rows_examined": rows_in,
                                 "employee_rows_with_hours": populated,
                                 "week_start": str(expected[0]), "week_end": str(week_ending)})
