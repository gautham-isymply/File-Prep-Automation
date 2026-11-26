"""Operation-level evidence for profile-specific rules and optional checks."""
from datetime import date, datetime, time, timedelta

import pytest
import yaml
from openpyxl import load_workbook

from factoryprep.config import load_profile
from factoryprep.engine import run
from factoryprep.models import CellValue, RunReport
from factoryprep.transform import excel_hours, parse_date, parse_number


@pytest.mark.parametrize("value,expected", [
    ("$1,234.50", 1234.5), ("£12.25", 12.25), ("€8.5", 8.5),
    ("(2.5)", -2.5), ("-", 0), ("—", 0), ("08:30", 8.5),
    ("27:15:30", 27 + 15 / 60 + 30 / 3600), (" 8.25 ", 8.25),
])
def test_numeric_encodings(value, expected):
    assert parse_number(value) == pytest.approx(expected)


@pytest.mark.parametrize("value", [True, None, "", "5%", "8:60", "1:00:60", "words"])
def test_invalid_numeric_encodings(value):
    with pytest.raises((ValueError, TypeError)):
        parse_number(value)


@pytest.mark.parametrize("value,mode,expected", [
    ("03/04/2026", "DMY", date(2026, 4, 3)),
    ("03/04/2026", "MDY", date(2026, 3, 4)),
    ("14/03/2026", "auto", date(2026, 3, 14)),
    ("03/14/2026", "auto", date(2026, 3, 14)),
    ("20260314.0", "YMD", date(2026, 3, 14)),
    (46095, "auto", date(2026, 3, 14)),
    (datetime(2026, 3, 14, 9), "auto", date(2026, 3, 14)),
    (date(2026, 3, 14), "auto", date(2026, 3, 14)),
])
def test_date_representations_and_locale(value, mode, expected):
    assert parse_date(value, mode) == expected


@pytest.mark.parametrize("value,mode", [
    ("03/14/2026", "DMY"), ("14/03/2026", "MDY"), ("03/04/2026", "auto"),
    ("20260229", "YMD"), ("", "auto"), (100, "auto"),
])
def test_dates_reject_wrong_locale_ambiguity_and_invalid_values(value, mode):
    with pytest.raises(ValueError):
        parse_date(value, mode)


@pytest.mark.parametrize("value,fmt,expected,warning", [
    (0.5, "hh:mm", 12, None), (1.5, "[h]:mm", 36, None),
    (time(8, 30), "hh:mm", 8.5, None),
    (datetime(2026, 3, 14, 8, 30), "hh:mm", 8.5, None),
    (timedelta(hours=27, minutes=30), "[h]:mm", 27.5, None),
    ("08:30", "General", 8.5, None), (8.5, "General", 8.5, None),
    (25, "General", 25, "LARGE_HOURS_VALUE"), (0, "General", 0, None),
])
def test_gbr_duration_encodings_and_warnings(value, fmt, expected, warning):
    report = RunReport("gbr", "synthetic")
    assert excel_hours(CellValue(value, fmt), report, 2, "REGHOURS") == expected
    assert [i.code for i in report.issues] == ([warning] if warning else [])


@pytest.mark.parametrize("profile,headers,rows,totals", [
    ("sgp", ["DATE", "NORM", "OT", "DAYFORCEUC1"],
     [[20260314, 8, 2, "1000"], [20260314, 99, 50, "9999"]],
     {"paid_hours_selected_dayforceuc1": 8, "ot_hours_selected_dayforceuc1": 2}),
    ("gbr", ["DATEIN", "DATEOUT", "REGHOURS", "O1HOURS", "O2HOURS",
             "DEPARTMENT", "JOBCODEDESC"],
     [["14/03/2026", "14/03/2026", 8, 2, 1, "1000", "WORK"],
      ["14/03/2026", "14/03/2026", 99, 50, 25, "1000", "PTO"],
      ["14/03/2026", "14/03/2026", 99, 50, 25, "9999", "WORK"]],
     {"paid_hours_filtered": 8, "ot1_hours_filtered": 2, "ot2_hours_filtered": 1}),
    ("cbg_core", ["Pay Rate", "Hours/Units", "Pay Code"],
     [[12, 8, "REG"], [12, 2, "OT"], [12, 99, "OTHER"]],
     {"core_reg_hours": 8, "core_ot_hours": 2}),
    ("cbg_starline", ["W/E Date", "BRD", "CHARGECODE", "Straight Hrs", "Overtime Hrs"],
     [["03/14/2026", 12, "1000", 8, 2], ["03/14/2026", 12, "9999", 99, 50]],
     {"starline_straight_hours_filtered": 8, "starline_overtime_hours_filtered": 2}),
    ("ccb", ["Row Labels", "Dept", "Sum of Reg Hr", "Sum of OT1.5 Hr",
             "Sum of OT2 Hr", "Sum of Total Hr"],
     [["03/14/2026", "3600171000", 8, 2, 1, 11],
      ["03/14/2026", "9999", 99, 50, 25, 174]],
     {"ccb_selected_cost_centers_reg": 8, "ccb_selected_cost_centers_ot1": 2, "ccb_selected_cost_centers_ot2": 1}),
    ("dayforce_ccb", ["Cost_Center", "Pay_Date", "Location", "Pay_Category", "Normal"],
     [["1000 > Direct Labor", "03/14/2026", "DPC CCB", "Reg", 8],
      ["1000 > Direct Labor", "03/14/2026", "DPC CCB", "OT 1.5", 2],
      ["1000 > Direct Labor", "03/14/2026", "OTHER", "Reg", 99],
      ["9999", "03/14/2026", "DPC CCB", "Reg", 99]],
     {"us_ccb_reg_hours": 8, "us_ccb_ot_hours": 2}),
    ("dayforce_non_ccb", ["Cost_Center", "Pay_Date", "Location", "Pay_Category", "Normal"],
     [["1025 > Plugs", "03/14/2026", "DPC BUS", "Reg", 8],
      ["1025 > Plugs", "03/14/2026", "DPC PAC", "OT 1.5", 2],
      ["1025 > Plugs", "03/14/2026", "OTHER", "Reg", 99],
      ["9999", "03/14/2026", "DPC BUS", "Reg", 99]],
     {"us_non_ccb_reg_hours": 8, "us_non_ccb_ot_hours": 2}),
])
def test_all_tabular_metrics_filter_totals_without_deleting_rows(
    profile, headers, rows, totals, workbook_factory, tmp_path, refresh_evidence,
):
    src = workbook_factory("metrics", headers, rows)
    result = run(profile, src, tmp_path / "prepared.xlsx", week_ending=date(2026, 3, 14), overrides=refresh_evidence(src))
    assert result.status == "PREPARED", result.as_dict()
    assert result.rows_out == len(rows)
    metrics = result.diagnostics["filtered_reconciliation_metrics"]
    assert {name: item["total"] for name, item in metrics.items()} == totals
    assert all(item["rows"] == 1 for item in metrics.values())


def test_dayforce_exclusion_label_must_match(workbook_factory, tmp_path):
    src = workbook_factory("mislabeled", [
        "Cost_Center", "Pay_Date", "Location", "Pay_Category", "Normal",
    ], [["3600172100 > Other label", "03/14/2026", "DPC CCB", "Reg", 8]])
    target = tmp_path / "blocked.xlsx"
    result = run("dayforce_ccb", src, target)
    assert result.status == "FAILED"
    assert result.diagnostics["excluded_rows"] == 0
    assert any(i.code == "EXCLUDED_ROW_LABEL_MISMATCH" for i in result.issues)
    assert not target.exists()


@pytest.mark.parametrize("fault,issue", [
    ("unknown", "UNKNOWN_BUSINESS_LABEL"), ("missing", "MISSING_BUSINESS_CATEGORY"),
    ("duplicate", "DUPLICATE_BUSINESS_CATEGORY"), ("week", "WEEK_END_REQUIRED"),
    ("weekday", "INVALID_WEEK_END"), ("strict", "PROVISIONAL_SOURCE_SCHEMA"),
])
def test_jz_rejects_category_and_week_failures(fault, issue, workbook_factory, tmp_path):
    rows = [[category, 8, 2] for category in load_profile("jz")["category_mapping"]]
    week = date(2026, 3, 14)
    if fault == "unknown":
        rows[0][0] = "HC invoice hours"
    elif fault == "missing":
        rows.pop()
    elif fault == "duplicate":
        rows.append(rows[0].copy())
    elif fault == "week":
        week = None
    elif fault == "weekday":
        week = date(2026, 3, 13)
    src = workbook_factory("jz_bad", ["Category", "Paid Hours", "OT Hours"], rows)
    target = tmp_path / "blocked.xlsx"
    result = run("jz", src, target, week_ending=week, strict=fault == "strict")
    assert result.status == "FAILED"
    assert any(i.code == issue for i in result.issues)
    assert not target.exists()


def test_jz_exact_mapping_dates_and_totals(workbook_factory, tmp_path):
    categories = ["Starline", "Cables", "Fibra", "Connectors", "Servertech"]
    src = workbook_factory("jz", ["Category", "Paid Hours", "OT Hours"],
                           [[f"Direct Hours ({cat})", 8 + i, i] for i, cat in enumerate(categories)])
    target = tmp_path / "jz_output.xlsx"
    result = run("jz", src, target, week_ending=date(2026, 3, 14))
    assert result.status == "PREPARED"
    assert {k: v for k, v in result.diagnostics.items() if k != "source_sha256"} == {"week_start": "2026-03-08", "week_end": "2026-03-14",
                                  "categories_matched": 5, "paid_total": 50, "ot_total": 10}
    wb = load_workbook(target)
    try:
        records = list(wb.active.values)[1:]
        assert [row[:5] for row in records] == [
            ("BUS", "3618", "Santa Teresa", "BUSWAY", "3600"),
            ("DAT", "3614", "Santa Teresa", "COP", "3600"),
            ("DAT", "3614", "Santa Teresa", "FIB", "3600"),
            ("DAT", "3614", "Santa Teresa", "RAC", "3600"),
            ("DAT", "3614", "Santa Teresa", "DAT", "3600"),
        ]
        assert all(row[5].date() == date(2026, 3, 8) for row in records)
        assert [row[6:] for row in records] == [(8 + i, i) for i in range(5)]
    finally:
        wb.close()


@pytest.mark.parametrize("fault,issue", [
    ("no_match", "OVERRIDE_MATCH_FAILURE"), ("many", "OVERRIDE_MATCH_FAILURE"),
    ("column", "OVERRIDE_MATCH_FAILURE"), ("old", "OVERRIDE_OLD_VALUE_MISMATCH"),
])
def test_corrections_require_unique_row_column_and_old_value(
    fault, issue, workbook_factory, tmp_path,
):
    rows = [[20260314, 8, 0, "E1"]]
    fix = {"profile": "sgp", "match": {"Employee": "E1"}, "column": "NORM",
           "expected_old": 8.0, "new_value": 9}
    if fault == "no_match":
        fix["match"] = {"Employee": "missing"}
    elif fault == "many":
        rows *= 2
    elif fault == "column":
        fix["column"] = "absent"
    else:
        fix["expected_old"] = 7
    src = workbook_factory("fix", ["DATE", "NORM", "OT", "Employee"], rows)
    original = src.read_bytes()
    overrides = tmp_path / "fixes.yaml"
    overrides.write_text(yaml.safe_dump({"corrections": [fix]}), encoding="utf-8")
    target = tmp_path / "blocked.xlsx"
    result = run("sgp", src, target, overrides=overrides)
    assert result.status == "FAILED"
    assert any(i.code == issue for i in result.issues)
    assert src.read_bytes() == original
    assert not target.exists()


def test_optional_schema_duplicate_null_continuity_and_sum_checks(workbook_factory, tmp_path):
    spec = load_profile("sgp")
    spec["columns"].update({"non_null": ["Employee"], "duplicate_keys": ["DATE"]})
    spec["date_continuity_column"] = "DATE"
    spec["cross_field_sums"] = [{"parts": ["NORM", "OT"], "total": "Total"}]
    spec["columns"]["numeric"].append("Total")
    (tmp_path / "sgp.yaml").write_text(yaml.safe_dump(spec), encoding="utf-8")
    src = workbook_factory("checks", ["DATE", "NORM", "OT", "Employee", "Total"], [
        [20260312, 8, 2, "E1", 10], [20260314, 8, 2, "E2", 99],
        [20260314, 8, 2, None, 10],
    ])
    result = run("sgp", src, tmp_path / "blocked.xlsx", config_dir=tmp_path)
    assert result.status == "FAILED"
    assert {"NULL_VALUE", "DUPLICATE_KEY", "MISSING_DATES", "TOTAL_MISMATCH"} <= {
        i.code for i in result.issues
    }


@pytest.mark.parametrize("change,issue", [
    ("expected", "EXPECTED_COLUMN_MISSING"), ("extra", "UNEXPECTED_COLUMN"),
    ("transform", "TRANSFORM_COLUMN_MISSING"), ("aliases", "INVALID_PROFILE_ALIASES"),
])
def test_semantic_config_and_schema_checks(change, issue, workbook_factory, tmp_path):
    spec = load_profile("sgp")
    if change == "expected":
        spec["columns"]["expected"] = ["DATE", "NORM", "OT", "Employee"]
    elif change == "extra":
        spec["columns"]["expected"] = ["DATE", "NORM"]
    elif change == "transform":
        spec["columns"]["numeric"].append("Absent")
    else:
        spec["columns"]["aliases"]["OT"].append("Normal")
    (tmp_path / "sgp.yaml").write_text(yaml.safe_dump(spec), encoding="utf-8")
    src = workbook_factory("schema", ["DATE", "NORM", "OT"], [[20260314, 8, 2]])
    target = tmp_path / "schema_out.xlsx"
    result = run("sgp", src, target, config_dir=tmp_path, strict=True)
    assert result.status == "FAILED"
    assert any(i.code == issue for i in result.issues)
    assert not target.exists()


@pytest.mark.parametrize("summary", ["Total", "Grand Total", "Subtotal", "Totals"])
def test_core_skips_blank_and_summary_rows_only(summary, workbook_factory, tmp_path):
    src = workbook_factory("core", ["Pay Rate", "Hours/Units", "Pay Code"], [
        [12, 8, "REG"], [None, None, None], [summary, 8, None], [15, 2, "OT"],
    ], preamble=[["Report title"]])
    result = run("cbg_core", src, tmp_path / "core_out.xlsx")
    assert result.status == "PREPARED"
    assert result.rows_in == 4
    assert result.rows_out == 2
