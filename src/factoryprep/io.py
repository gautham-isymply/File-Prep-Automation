"""Read Excel and CSV safely; write new files without mutating originals."""
from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from .models import CellValue, Prepared, SourceBook, RawSheet


class SourceError(ValueError):
    pass


def read_book(path: Path) -> SourceBook:
    if not path.is_file():
        raise SourceError(f"Input does not exist: {path}")
    extension = path.suffix.lower()
    if extension in {".xlsx", ".xlsm"}:
        # Cached formula values only. No Excel refresh, macros or external links execution.
        workbook = load_workbook(path, data_only=True, read_only=True, keep_links=False)
        sheets: list[RawSheet] = []
        try:
            for sh in workbook.worksheets:
                rows = [[CellValue(c.value, c.number_format, c.data_type) for c in row]
                        for row in sh.iter_rows()]
                sheets.append(RawSheet(sh.title, rows))
        finally:
            workbook.close()
        return SourceBook(path, sheets)
    if extension in {".csv", ".tsv"}:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            sample = f.read(4096)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
                delimiter = dialect.delimiter
            except csv.Error:
                delimiter = "\t" if extension == ".tsv" else ","
            rows = [[CellValue(v, "General", "s") for v in row]
                    for row in csv.reader(f, delimiter=delimiter)]
        return SourceBook(path, [RawSheet("CSV", rows)])
    raise SourceError(f"Unsupported input {extension}. Export .xls to .xlsx first.")


def read_reference_columns(path: Path, sheet: str | None = None) -> list[str]:
    book = read_book(path)
    matches = [s for s in book.sheets if s.name == sheet] if sheet else book.sheets
    if len(matches) != 1:
        raise SourceError("Reference has multiple sheets; choose a specific sheet or provide a single-sheet template")
    sh = matches[0]
    for row in sh.rows:
        vals = [str(c.value).strip() if c.value is not None else "" for c in row]
        if any(vals):
            return [v for v in vals if v]
    raise SourceError("Reference template contains no header")


def write_prepared(prepared: Prepared, path: Path, output_format: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "csv":
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(prepared.columns)
            for row in prepared.rows:
                writer.writerow([_csv_value(row.get(c), prepared.date_formats.get(c))
                                 for c in prepared.columns])
    else:
        wb = Workbook()
        sh = wb.active
        sh.title = prepared.sheet_name[:31]
        sh.append(prepared.columns)
        sh.freeze_panes = "A2"
        for record in prepared.rows:
            sh.append([_excel_value(record.get(c)) for c in prepared.columns])
        for index, name in enumerate(prepared.columns, 1):
            if name in prepared.date_formats:
                fmt = prepared.date_formats[name]
                for row in sh.iter_rows(min_row=2, min_col=index, max_col=index):
                    row[0].number_format = fmt
        wb.save(path)


def _excel_value(value: Any) -> Any:
    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime(value.year, value.month, value.day)
    return value


def _csv_value(value: Any, excel_format: str | None) -> Any:
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        if excel_format == "yyyymmdd":
            return value.strftime("%Y%m%d")
        if excel_format in {"m/d/yyyy", "mm/dd/yyyy", "mm/dd/yy"}:
            return value.strftime("%m/%d/%Y")
        return value.strftime("%Y-%m-%d")
    return value
