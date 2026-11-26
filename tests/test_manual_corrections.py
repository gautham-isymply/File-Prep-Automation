"""Adversarial manual layouts and explicit source-contract gates (synthetic)."""
import hashlib
import json
from datetime import date, timedelta

import pytest
import yaml
from openpyxl import Workbook, load_workbook
from typer.testing import CliRunner

from factoryprep.cli import app
from factoryprep.config import ConfigError, load_profile
from factoryprep.detect import detect_profile
from factoryprep.engine import run
from factoryprep.models import CellValue, RunReport
from factoryprep.reconcile import combine_reports
from factoryprep.transform import excel_hours, parse_number

WEEK = date(2026, 3, 14)
DF_HEADERS = ["Cost_Center", "Pay_Date", "Location", "Pay_Category", "Normal"]


def custom(tmp_path, name, **changes):
    spec = load_profile(name)
    spec.update(changes)
    (tmp_path / f"{name}.yaml").write_text(yaml.safe_dump(spec), encoding="utf-8")
    return tmp_path


def evidence(tmp_path, source):
    path = tmp_path / f"{source.stem}-evidence.yaml"
    path.write_text(yaml.safe_dump({"source_evidence": {
        "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "refreshed_at": "2026-03-15T09:00:00-05:00", "approved_by": "synthetic owner",
    }}), encoding="utf-8")
    return path


@pytest.mark.parametrize("value", [float("nan"), float("inf"), "NaN", "Infinity", "8,75"])
def test_ambiguous_or_nonfinite_numbers_never_pass(value):
    with pytest.raises(ValueError):
        parse_number(value)


def test_local_decimal_comma_does_not_change_other_profiles():
    assert parse_number("8,75", ",") == 8.75
    assert parse_number(8.75, ",") == 8.75
    assert parse_number("$1,234.50") == 1234.5
    with pytest.raises(ValueError):
        parse_number("1.234,50", ",")


def test_gbr_requires_units_for_unformatted_fraction(workbook_factory, tmp_path):
    src = workbook_factory("gbr", ["DATEIN", "DATEOUT", "REGHOURS", "O1HOURS", "O2HOURS"],
                           [["14/03/2026", "14/03/2026", 0.5, 0, 0]])
    target = tmp_path / "candidate.xlsx"
    digest = src.read_bytes()
    result = run("gbr", src, target)
    assert result.status == "FAILED" and not target.exists()
    assert "AMBIGUOUS_TIME_FRACTION" in {i.code for i in result.issues}
    for mode, expected in [("decimal_hours", 0.5), ("excel_days", 12)]:
        custom(tmp_path, "gbr", hours_encoding={"REGHOURS": mode})
        result = run("gbr", src, target, config_dir=tmp_path)
        assert result.status == "PREPARED"
        wb = load_workbook(target)
        assert wb.active.cell(2, 3).value == expected
        wb.close()
    assert src.read_bytes() == digest
    assert excel_hours(CellValue(1.25), RunReport("gbr", "test"), 2, "REGHOURS", "excel_days") == 30


def test_reno_dmy_decimal_comma_and_two_headers(workbook_factory, tmp_path):
    dates = [(WEEK - timedelta(days=i)).strftime("%d/%m/%Y") for i in range(6, -1, -1)]
    src = workbook_factory("reno", ["Date:", *dates, None], [
        ["Name", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Total"],
        ["Employee A", "0", "8,75", "9", "8", "8", "5,5", "0", "39,25"],
        ["Employee B", 0, 1.25, 0, 0, 0, 0, 0, 1.25],
        ["Total", 0, 10, 9, 8, 8, 5.5, 0, 40.5],
    ])
    assert detect_profile(src) == "reno"
    result = run("reno", src, tmp_path / "reno-out.xlsx", week_ending=WEEK)
    assert result.status == "PREPARED", result.as_dict()
    assert result.diagnostics["weekly_paid_hours"] == 40.5
    wb = load_workbook(tmp_path / "reno-out.xlsx")
    records = list(wb.active.values)[1:]
    wb.close()
    assert [r[5].date() for r in records] == [WEEK - timedelta(days=i) for i in range(6, -1, -1)]
    assert [r[6] for r in records] == [0, 10, 9, 8, 8, 5.5, 0]


@pytest.mark.parametrize("fault,code", [("blank", "UNRESOLVED_BLANK_HOURS"),
                                       ("term", "INVALID_TIMECARD_HOURS"),
                                       ("missing_saturday", "MISSING_WEEK_DATES"),
                                       ("duplicate_header", "PREPARATION_FAILURE")])
def test_reno_blocks_unresolved_layouts(fault, code, workbook_factory, tmp_path):
    dates = [WEEK - timedelta(days=i) for i in range(6, -1, -1)]
    hours = [0, 8, 8, 8, 8, 8, 0]
    if fault == "missing_saturday":
        dates = [d - timedelta(days=1) for d in dates]
    if fault == "blank":
        hours[2] = None
    if fault == "term":
        hours[2] = "term"
    rows = [["Employee", *hours]]
    if fault == "duplicate_header":
        rows.insert(0, ["Date:", *dates])
    src = workbook_factory("reno_bad", ["Name", *dates], rows)
    target = tmp_path / "blocked.xlsx"
    result = run("reno", src, target, week_ending=WEEK)
    assert result.status == "FAILED" and not target.exists()
    assert code in {i.code for i in result.issues}


def test_reno_explicit_status_and_blank_policy_is_audited(workbook_factory, tmp_path):
    dates = [WEEK - timedelta(days=i) for i in range(6, -1, -1)]
    src = workbook_factory("reno_approved", ["Name", *dates], [["Employee", 0, 8, "term", None, 0, 0, 0]])
    custom(tmp_path, "reno", timecard={"date_input": "DMY", "decimal_separator": ",",
                                      "zero_tokens": ["term"], "blank_hours": "zero"})
    result = run("reno", src, tmp_path / "approved.xlsx", config_dir=tmp_path, week_ending=WEEK)
    assert result.status == "PREPARED"
    assert result.diagnostics["weekly_paid_hours"] == 8
    assert {a["reason"] for a in result.diagnostics["row_audit"]} == {
        "approved_blank_zero", "approved_status_zero"}


def test_core_retains_total_word_in_detail_and_sums_text_hours(workbook_factory, tmp_path):
    src = workbook_factory("core", ["Pay Rate", "Pay Code", "Hours/Units", "Description"], [
        [12, "REG", "8.75", "Total"], [12, "OT", "1.25", "Detail"],
        ["Pay Rate", "Pay Code", "Hours/Units", "Description"],
        ["Grand Total", None, 10, None],
    ])
    result = run("cbg_core", src, tmp_path / "core-prepared.xlsx")
    assert result.status == "PREPARED" and result.rows_out == 2
    assert result.diagnostics["filtered_reconciliation_metrics"]["core_reg_hours"]["total"] == 8.75
    assert {a["reason"] for a in result.diagnostics["row_audit"]} == {"repeated_header", "summary_label"}
    assert not result.diagnostics["reconciliation_contract_confirmed"]


def test_core_explicit_table_boundary_and_label_column(workbook_factory, tmp_path):
    src = workbook_factory("core_boundary", ["Name", "Pay Rate", "Pay Code", "Hours/Units"], [
        ["Employee", 12, "REG", 8], ["Subtotal", None, None, 8], ["Notes", "Not a rate", None, None],
    ])
    custom(tmp_path, "cbg_core", table={"last_data_row": 3, "summary_columns": ["Name"]})
    result = run("cbg_core", src, tmp_path / "boundary.xlsx", config_dir=tmp_path)
    assert result.status == "PREPARED" and result.rows_out == 1
    assert result.diagnostics["row_audit"] == [
        {"row": 3, "reason": "summary_label"}, {"row": 4, "reason": "declared_table_boundary"}]


def test_ssi_ambiguous_date_blocks_until_locale_declared(workbook_factory, tmp_path):
    src = workbook_factory("ssi", ["W/E Date", "BRD"], [["03/04/2026", 12]])
    result = run("cbg_starline", src, tmp_path / "blocked.xlsx")
    assert result.status == "FAILED"
    spec = load_profile("cbg_starline")
    spec["dates"][0]["input"] = "MDY"
    custom(tmp_path, "cbg_starline", dates=spec["dates"])
    assert run("cbg_starline", src, tmp_path / "ssi-prepared.xlsx", config_dir=tmp_path).status == "PREPARED"


def test_dayforce_month_retained_week_scoped_exact_codes(workbook_factory, tmp_path):
    src = workbook_factory("dayforce", DF_HEADERS, [
        ["1000 > Direct Labor", "03/14/2026", "DPC CCB", "Reg", 8],
        ["1000 > Direct Labor", "03/01/2026", "DPC CCB", "Reg", 99],
        ["11000 > Direct Labor", "03/14/2026", "DPC CCB", "Reg", 900],
        ["1000 > Direct Laboratory", "03/14/2026", "DPC CCB", "Reg", 900],
        ["13600172100 > Receiving Farmingdale", "03/14/2026", "DPC CCB", "Reg", 900],
        ["3600172100 > Receiving Farmingdale", "03/14/2026", "DPC CCB", "Reg", 20],
    ])
    result = run("dayforce_ccb", src, tmp_path / "month.xlsx", week_ending=WEEK, overrides=evidence(tmp_path, src))
    assert result.status == "PREPARED" and result.rows_out == 5
    assert result.diagnostics["filtered_reconciliation_metrics"]["us_ccb_reg_hours"] == {"total": 8, "rows": 1}
    assert result.diagnostics["row_audit"] == [{"row": 7, "reason": "exclude_rows", "hours": 20}]
    unscoped = run("dayforce_ccb", src, tmp_path / "unscoped.xlsx")
    assert unscoped.diagnostics["filtered_reconciliation_metrics"] == {}


def test_refresh_attestation_hash_bound_and_strict(workbook_factory, tmp_path):
    src = workbook_factory("df", DF_HEADERS, [["1000 > Direct Labor", "03/14/2026", "DPC CCB", "Reg", 8]])
    attestation = evidence(tmp_path, src)
    missing = run("dayforce_ccb", src, tmp_path / "missing-evidence.xlsx", week_ending=WEEK)
    assert missing.status == "FAILED"
    assert "EXTERNAL_REFRESH_NOT_PERFORMED" in {i.code for i in missing.issues}
    result = run("dayforce_ccb", src, tmp_path / "fresh.xlsx", overrides=attestation, strict=True, week_ending=WEEK)
    assert result.status == "PREPARED", result.as_dict()
    src.write_bytes(src.read_bytes() + b"changed")
    result = run("dayforce_ccb", src, tmp_path / "stale.xlsx", overrides=attestation, week_ending=WEEK)
    assert result.status == "FAILED"
    assert "SOURCE_EVIDENCE_MISMATCH" in {i.code for i in result.issues}


def test_taiwan_reports_missing_boundary_dates_without_filling(workbook_factory, tmp_path):
    src = workbook_factory("taiwan", ["Date", "Earn_Hours", "Paid_Hours", "Overtime_Hours"],
                           [["03/09/2026", 8, 8, 0], ["03/13/2026", 8, 8, 0]])
    result = run("taiwan", src, tmp_path / "tw.csv", week_ending=WEEK)
    assert result.rows_out == 2
    issue = next(i for i in result.issues if i.code == "MISSING_DATES")
    assert "2026-03-08" in issue.message and "2026-03-14" in issue.message


@pytest.mark.parametrize("new_value", [-1, "NaN", "words"])
def test_correction_cannot_bypass_numeric_guards(new_value, workbook_factory, tmp_path):
    src = workbook_factory("sgp", ["DATE", "NORM", "OT", "Employee"], [[20260314, 8, 0, "E1"]])
    fix = tmp_path / "fix.yaml"
    fix.write_text(yaml.safe_dump({"corrections": [{"profile": "sgp", "match": {"Employee": "E1"},
                    "column": "NORM", "expected_old": 8.0, "new_value": new_value}]}))
    result = run("sgp", src, tmp_path / "blocked.xlsx", overrides=fix)
    assert result.status == "FAILED"
    assert "INVALID_CORRECTION_VALUE" in {i.code for i in result.issues}


def raw_jz(tmp_path):
    categories = list(load_profile("jz")["category_mapping"])
    wb = Workbook()
    sheet = wb.active
    sheet.title = "Labour"
    sheet["A1"] = WEEK
    mapping = {}
    for row, category in enumerate(categories, 3):
        sheet.cell(row, 1, category)
        sheet.cell(row, 2, 10 + row)
        sheet.cell(row, 3, row)
        mapping[category] = {"label_cell": f"A{row}", "paid_cell": f"B{row}", "ot_cell": f"C{row}"}
    src = tmp_path / "raw.xlsx"
    wb.save(src)
    wb.close()
    custom(tmp_path, "jz", source_mode="raw_cells", raw_source={
        "sheet": "Labour", "approval": "synthetic mapping, not a real HC contract",
        "week_ending_cell": "A1", "date_input": "YMD", "categories": mapping})
    return src


def test_raw_jz_requires_explicit_separate_cells_and_source_week(tmp_path):
    src = raw_jz(tmp_path)
    result = run("jz", src, tmp_path / "jz.xlsx", config_dir=tmp_path, week_ending=WEEK)
    assert result.status == "PREPARED", result.as_dict()
    assert result.rows_out == 5 and len(result.diagnostics["raw_cell_provenance"]) == 5
    assert result.diagnostics["paid_total"] == 75 and result.diagnostics["ot_total"] == 25
    mismatch = run("jz", src, tmp_path / "wrong.xlsx", config_dir=tmp_path, week_ending=WEEK - timedelta(days=7))
    assert mismatch.status == "FAILED"
    assert "source week" in mismatch.issues[-1].message
    spec = load_profile("jz", tmp_path)
    item = next(iter(spec["raw_source"]["categories"].values()))
    item["ot_cell"] = item["paid_cell"]
    (tmp_path / "jz.yaml").write_text(yaml.safe_dump(spec))
    with pytest.raises(ConfigError, match="distinct"):
        load_profile("jz", tmp_path)


def test_combined_us_audit_cli_and_mismatched_weeks(workbook_factory, tmp_path):
    reports = []
    for profile, cost, location in [("dayforce_ccb", "1000 > Direct Labor", "DPC CCB"),
                                    ("dayforce_non_ccb", "1025 > Plugs", "DPC BUS")]:
        src = workbook_factory(profile, DF_HEADERS, [[cost, "03/14/2026", location, "Reg", 8],
                                                     [cost, "03/14/2026", location, "OT 1.5", 2]])
        path = tmp_path / f"{profile}.json"
        report = run(profile, src, tmp_path / f"{profile}-out.xlsx", week_ending=WEEK,
                     overrides=evidence(tmp_path, src), report_path=path, strict=True)
        assert report.status == "PREPARED"
        reports.append(path)
    output = tmp_path / "combined.json"
    result = CliRunner().invoke(app, ["reconcile", "--group", "us", "--component", str(reports[0]),
                                     "--component", str(reports[1]), "--output", str(output)])
    assert result.exit_code == 0, result.output
    saved = json.loads(output.read_text())
    assert saved["paid_hours"] == 16 and saved["ot_hours"] == 4
    original = output.read_bytes()
    bad = json.loads(reports[0].read_text())
    bad["diagnostics"]["reconciliation_period"] = {"start": "2026-03-01", "end": "2026-03-07"}
    reports[0].write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="periods differ"):
        combine_reports("us", reports, output)
    assert output.read_bytes() == original


@pytest.mark.parametrize("change", [{"hours_encoding": {"REGHOURS": "guess"}},
                                   {"timecard": {"decimal_separator": "auto"}},
                                   {"table": {"first_data_row": 8, "last_data_row": 2}},
                                   {"reconciliation_contract_confirmed": "yes"}])
def test_new_contract_options_fail_fast(change, tmp_path):
    custom(tmp_path, "gbr", **change)
    with pytest.raises(ConfigError):
        load_profile("gbr", tmp_path)


def test_report_never_overwrites_source_or_candidate(workbook_factory, tmp_path):
    src = workbook_factory("sgp", ["DATE", "NORM", "OT"], [[20260314, 8, 0]])
    original = src.read_bytes()
    with pytest.raises(ValueError, match="Report must differ"):
        run("sgp", src, tmp_path / "out.xlsx", report_path=src)
    assert src.read_bytes() == original


def test_combined_cbg_requires_reviewed_department_and_date_contract(workbook_factory, tmp_path):
    core = workbook_factory("core", ["Pay Rate", "Pay Code", "Hours/Units", "Date", "Department"], [
        [12, "REG", "8", 20260314, "APPROVED"], [12, "OT", "2", 20260314, "APPROVED"],
        [12, "REG", 99, 20260307, "APPROVED"], [12, "REG", 99, 20260314, "OTHER"],
    ])
    core_report = tmp_path / "core.json"
    run("cbg_core", core, tmp_path / "core-out.xlsx", week_ending=WEEK, report_path=core_report)
    ssi = workbook_factory("ssi", ["W/E Date", "BRD", "CHARGECODE", "Straight Hrs", "Overtime Hrs"],
                           [[20260314, 12, "1000", "4", "1"]])
    ssi_report = tmp_path / "ssi.json"
    assert run("cbg_starline", ssi, tmp_path / "ssi-out.xlsx", week_ending=WEEK,
               report_path=ssi_report).status == "PREPARED"
    target = tmp_path / "cbg.json"
    with pytest.raises(ValueError, match="confirmed filters"):
        combine_reports("cbg", [core_report, ssi_report], target)
    spec = load_profile("cbg_core")
    for metric in spec["reconciliation"]:
        metric["filters"].append({"column": "Department", "in": ["APPROVED"]})
    custom(tmp_path, "cbg_core", reconciliation_contract_confirmed=True,
           dates=[{"column": "Date", "input": "YMD"}], reconciliation_date_column="Date",
           reconciliation=spec["reconciliation"])
    approved = run("cbg_core", core, tmp_path / "core-out.xlsx", config_dir=tmp_path,
                   week_ending=WEEK, report_path=core_report, strict=True)
    assert approved.status == "PREPARED" and approved.rows_out == 4
    combined = combine_reports("cbg", [core_report, ssi_report], target)
    assert (combined["paid_hours"], combined["ot_hours"]) == (12, 3)
    with pytest.raises(ValueError, match="overwrite"):
        combine_reports("cbg", [core_report, ssi_report], core)


@pytest.mark.parametrize("fault", ["missing_cell", "label", "negative", "invalid", "excel_error"])
def test_raw_jz_never_guesses_invalid_source_values(fault, tmp_path):
    src = raw_jz(tmp_path)
    wb = load_workbook(src)
    if fault == "label":
        wb.active["A3"] = "Unknown invoice category"
    else:
        wb.active["B3"] = {"missing_cell": None, "negative": -1, "invalid": "unknown", "excel_error": "#REF!"}[fault]
    wb.save(src)
    wb.close()
    target = tmp_path / "blocked.xlsx"
    result = run("jz", src, target, config_dir=tmp_path, week_ending=WEEK)
    assert result.status == "FAILED" and not target.exists()


def test_taiwan_duplicate_dates_remain_visible(workbook_factory, tmp_path):
    src = workbook_factory("tw", ["Date", "Earn_Hours", "Paid_Hours", "Overtime_Hours"],
                           [[20260314, 1, 2, 0], [20260314, 3, 4, 0]])
    result = run("taiwan", src, tmp_path / "tw-out.csv")
    assert result.rows_out == 2
    assert "DUPLICATE_DATE" in {i.code for i in result.issues}


@pytest.mark.parametrize("value", ["3600172100", "3600172100 Receiving Farmingdale",
                                   "3600172100 > Wrong label"])
def test_exclusion_code_with_unresolved_label_blocks(value, workbook_factory, tmp_path):
    src = workbook_factory("malformed", DF_HEADERS, [[value, "03/14/2026", "DPC CCB", "Reg", 8]])
    result = run("dayforce_ccb", src, tmp_path / "blocked.xlsx", week_ending=WEEK,
                 overrides=evidence(tmp_path, src))
    assert result.status == "FAILED"
    assert "EXCLUDED_ROW_LABEL_MISMATCH" in {i.code for i in result.issues}


def test_reno_multiple_weeks_require_explicit_selection(workbook_factory, tmp_path):
    dates = [WEEK - timedelta(days=i) for i in range(13, -1, -1)]
    src = workbook_factory("two_weeks", ["Name", *dates], [["Employee", *([1] * 14)]])
    result = run("reno", src, tmp_path / "ambiguous.xlsx")
    assert result.status == "FAILED"
    assert "WEEK_END_REQUIRED" in {i.code for i in result.issues}
    selected = run("reno", src, tmp_path / "selected.xlsx", week_ending=WEEK)
    assert selected.status == "PREPARED"
    assert selected.diagnostics["weekly_paid_hours"] == 7
