"""Synthetic source contracts: shared gates must hold for every bundled profile."""
import csv
import hashlib
import json
from datetime import date
from pathlib import Path

import pytest
from openpyxl import load_workbook

from factoryprep.config import available_profiles, load_profile
from factoryprep.engine import run

# Reno has date-column timecards rather than a named-column tabular contract;
# its aggregation is exercised by the restored dedicated profile test.
PROFILES = [name for name in available_profiles()
            if load_profile(name).get("processor") != "reno"]
WEEK_END = date(2026, 3, 14)


def source_rows(spec):
    columns = spec["columns"]["required"]
    values = {
        "DATE": "20260314", "DATEIN": "14/03/2026", "DATEOUT": "14/03/2026",
        "W/E Date": "03/14/2026", "Row Labels": "03/14/2026",
        "Pay_Date": "03/14/2026", "Date": "03/14/2026", "Dept": "3600171000",
        "Cost_Center": "1000 > Direct Labor", "Location": "DPC CCB",
        "Pay_Category": "Reg", "Sum of Total Hr": 24,
    }
    categories = list(spec.get("category_mapping", {"unused": {}}))
    return [[category if col == "Category" else values.get(col, 8)
             for col in columns] for category in categories]


def codes(report):
    return {issue.code for issue in report.issues}


@pytest.mark.parametrize("profile", PROFILES)
@pytest.mark.parametrize("aliases", [False, True], ids=["canonical", "aliases"])
@pytest.mark.parametrize("container", ["xlsx", "xlsm", "csv", "tsv"])
def test_profile_round_trip_and_source_integrity(
    profile, aliases, container, workbook_factory, tmp_path, refresh_evidence,
):
    spec = load_profile(profile)
    columns = spec["columns"]["required"]
    headers = [spec["columns"].get("aliases", {}).get(col, [col])[0]
               if aliases else col for col in columns]
    rows = source_rows(spec)
    if container in {"csv", "tsv"}:
        src = tmp_path / f"{profile}.{container}"
        with src.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream, delimiter="\t" if container == "tsv" else ",")
            writer.writerow(headers)
            writer.writerows(rows)
    else:
        src = workbook_factory(profile, headers, rows, preamble=[["Export title"], []])
        if container == "xlsm":
            renamed = src.with_suffix(".xlsm")
            renamed.write_bytes(src.read_bytes())
            src = renamed
    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    target = tmp_path / f"prepared.{spec['output']['format']}"
    report_file = tmp_path / "audit.json"
    report = run(profile, src, target, week_ending=WEEK_END, report_path=report_file, overrides=refresh_evidence(src))
    assert report.status == "PREPARED", report.as_dict()
    assert report.rows_in == report.rows_out == len(rows)
    assert hashlib.sha256(src.read_bytes()).hexdigest() == digest
    saved = json.loads(report_file.read_text())
    assert saved["status"] == report.status
    assert saved["rows_out"] == report.rows_out
    if spec["output"]["format"] == "csv":
        with target.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            records = list(reader)
            assert reader.fieldnames == report.columns_out == columns
        assert len(records) == len(rows)
        assert records[0]["Date"] == "03/14/2026"
        for col in spec["columns"].get("numeric", []):
            assert float(records[0][col]) == 8
        return
    wb = load_workbook(target)
    try:
        sheet = wb.active
        assert sheet.title == spec["output"]["sheet"]
        assert sheet.freeze_panes == "A2"
        assert list(next(sheet.values)) == report.columns_out
        assert report.columns_out == spec["output"].get("columns", columns)
        record = dict(zip(report.columns_out, list(sheet.values)[1]))
        for col in spec["columns"].get("numeric", []) + spec.get("time_to_hours", []):
            assert isinstance(record[col], (int, float))
            assert record[col] == (24 if col == "Sum of Total Hr" else 8)
        for rule in spec.get("dates", []):
            index = report.columns_out.index(rule["column"]) + 1
            assert sheet.cell(2, index).value.date() == WEEK_END
            assert sheet.cell(2, index).number_format == rule["excel_format"]
    finally:
        wb.close()


REQUIRED = [(name, col) for name in PROFILES
            for col in load_profile(name)["columns"]["required"]]
NUMERIC = [(name, col) for name in PROFILES for col in
           load_profile(name)["columns"].get("numeric", [])
           + load_profile(name).get("time_to_hours", [])]
DATES = [(name, rule["column"]) for name in PROFILES
         for rule in load_profile(name).get("dates", [])]


@pytest.mark.parametrize("profile,column", REQUIRED)
@pytest.mark.parametrize("fault", ["missing", "duplicate"])
def test_each_required_header_rejects_missing_or_duplicate(
    profile, column, fault, workbook_factory, tmp_path,
):
    spec = load_profile(profile)
    headers = spec["columns"]["required"].copy()
    rows = source_rows(spec)
    if fault == "missing":
        index = headers.index(column)
        headers.pop(index)
        rows = [row[:index] + row[index + 1:] for row in rows]
    else:
        headers.append(spec["columns"].get("aliases", {}).get(column, [column])[0])
        rows = [row + [row[spec["columns"]["required"].index(column)]] for row in rows]
    src = workbook_factory("bad", headers, rows)
    target = tmp_path / f"blocked.{spec['output']['format']}"
    report = run(profile, src, target, week_ending=WEEK_END)
    assert report.status == "FAILED"
    expected = "DUPLICATE_HEADER" if fault == "duplicate" else "MISSING_COLUMN"
    # Single-column profiles cannot locate any header after its only column is removed.
    assert expected in codes(report) or (
        len(spec["columns"]["required"]) == 1 and "PREPARATION_FAILURE" in codes(report)
    )
    assert not target.exists()


@pytest.mark.parametrize("profile,column", NUMERIC)
@pytest.mark.parametrize("value,issue", [
    (None, "NULL_VALUE"), (-1, "NEGATIVE_VALUE"), ("bad", "FORMAT_MISMATCH"),
    ("#DIV/0!", "EXCEL_CELL_ERROR"), (True, "FORMAT_MISMATCH"),
])
def test_every_numeric_field_blocks_invalid_values(
    profile, column, value, issue, workbook_factory, tmp_path,
):
    spec = load_profile(profile)
    rows = source_rows(spec)
    rows[0][spec["columns"]["required"].index(column)] = value
    # Keep a null in a data row distinguishable from a completely blank row.
    src = workbook_factory("bad_numeric", spec["columns"]["required"] + ["Employee"],
                           [row + ["E1"] for row in rows])
    target = tmp_path / f"blocked.{spec['output']['format']}"
    report = run(profile, src, target, week_ending=WEEK_END)
    assert report.status == "FAILED"
    assert any(i.code == issue and i.column == column and i.row == 2 for i in report.issues)
    assert not target.exists()


@pytest.mark.parametrize("profile,column", DATES)
@pytest.mark.parametrize("value,issue", [(None, "NULL_VALUE"), ("2026-02-30", "FORMAT_MISMATCH")])
def test_every_date_field_blocks_null_or_impossible_dates(
    profile, column, value, issue, workbook_factory, tmp_path,
):
    spec = load_profile(profile)
    rows = source_rows(spec)
    rows[0][spec["columns"]["required"].index(column)] = value
    src = workbook_factory("bad_date", spec["columns"]["required"], rows)
    target = tmp_path / f"blocked.{spec['output']['format']}"
    result = run(profile, src, target)
    assert result.status == "FAILED"
    assert any(i.code == issue and i.column == column for i in result.issues)
    assert not target.exists()


@pytest.mark.parametrize("profile", PROFILES)
def test_empty_profile_output_is_blocked(profile, workbook_factory, tmp_path):
    spec = load_profile(profile)
    src = workbook_factory("empty", spec["columns"]["required"], [])
    target = tmp_path / f"empty_output.{spec['output']['format']}"
    result = run(profile, src, target, week_ending=WEEK_END)
    assert result.status == "FAILED"
    assert "EMPTY_OUTPUT" in codes(result)
    assert not target.exists()


def test_profile_mirrors_are_byte_identical():
    root = Path(__file__).resolve().parents[1]
    development = root / "config/profiles"
    embedded = root / "src/factoryprep/profiles"
    assert {p.name for p in development.glob("*.yaml")} == {
        p.name for p in embedded.glob("*.yaml")
    }
    for profile in available_profiles():
        assert (development / f"{profile}.yaml").read_bytes() == (
            embedded / f"{profile}.yaml"
        ).read_bytes()
