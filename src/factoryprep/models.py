"""Shared data types; independent of all individual plant implementations."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any


@dataclass
class CellValue:
    value: Any
    excel_format: str = "General"
    excel_type: str = "n"
    fill: Any = None


@dataclass
class RawSheet:
    name: str
    rows: list[list[CellValue]]


@dataclass
class SourceBook:
    path: Path
    sheets: list[RawSheet]


@dataclass
class Issue:
    severity: str  # ERROR | WARNING | INFO
    code: str
    message: str
    row: int | None = None
    column: str | None = None
    source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class Prepared:
    columns: list[str]
    rows: list[dict[str, Any]]
    sheet_name: str
    date_formats: dict[str, str] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    source_rows: list[int | None] = field(default_factory=list)
    number_formats: dict[str, str] = field(default_factory=dict)
    cell_fills: list[dict[str, Any]] = field(default_factory=list)
    auto_filter: bool = False


@dataclass
class Context:
    profile: dict[str, Any]
    week_ending: date | None = None
    sheet_override: str | None = None
    overrides: dict[str, Any] = field(default_factory=dict)
    strict: bool = False
    reference: Path | None = None


@dataclass
class RunReport:
    profile: str
    input_path: str
    output_path: str | None = None
    issues: list[Issue] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    source_sheet: str | None = None
    rows_in: int = 0
    rows_out: int = 0
    columns_out: list[str] = field(default_factory=list)
    status: str = "FAILED"

    def add(self, severity: str, code: str, message: str,
            row: int | None = None, column: str | None = None) -> None:
        self.issues.append(Issue(severity, code, message, row, column, self.input_path))

    @property
    def errors(self) -> int:
        return sum(i.severity == "ERROR" for i in self.issues)

    @property
    def warnings(self) -> int:
        return sum(i.severity == "WARNING" for i in self.issues)

    def as_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["summary"] = {"errors": self.errors, "warnings": self.warnings,
                          "info": sum(i.severity == "INFO" for i in self.issues)}
        return out
