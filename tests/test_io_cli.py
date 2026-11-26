"""File containers, output lifecycle, reports and operator commands."""
import csv
import json
from datetime import date, datetime

import pytest
import yaml
from openpyxl import load_workbook
from typer.testing import CliRunner

from factoryprep.cli import app
from factoryprep.config import load_profile
from factoryprep.detect import DetectionError, detect_profile
from factoryprep.engine import run


@pytest.mark.parametrize("suffix,delimiter", [
    (".csv", ","), (".csv", ";"), (".csv", "|"), (".tsv", "\t"),
])
def test_delimited_input_bom_quoting_and_source_integrity(suffix, delimiter, tmp_path):
    source = tmp_path / f"input{suffix}"
    with source.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream, delimiter=delimiter)
        writer.writerow(["DATE", "NORM", "OT", "Employee"])
        writer.writerow([20260314, "1,234.5", "2:30", f"name{delimiter}quoted"])
    original = source.read_bytes()
    target = tmp_path / "prepared.xlsx"
    result = run("sgp", source, target)
    assert result.status == "PREPARED", result.as_dict()
    assert source.read_bytes() == original
    wb = load_workbook(target)
    try:
        assert list(wb.active.values)[1] == (
            datetime(2026, 3, 14), 1234.5, 2.5, f"name{delimiter}quoted",
        )
    finally:
        wb.close()


def test_xlsm_container_is_read_without_modifying_input(workbook_factory, tmp_path):
    original = workbook_factory("source", ["DATE", "NORM", "OT"], [[20260314, 8, 2]])
    source = tmp_path / "export.xlsm"
    source.write_bytes(original.read_bytes())
    before = source.read_bytes()
    result = run("sgp", source, tmp_path / "output.xlsx")
    assert result.status == "PREPARED"
    assert source.read_bytes() == before
    # This is an XLSM container smoke test, not certification of real VBA preservation.


def test_csv_output_uses_declared_date_format_and_order(workbook_factory, tmp_path):
    spec = load_profile("sgp")
    spec["output"]["format"] = "csv"
    (tmp_path / "sgp.yaml").write_text(yaml.safe_dump(spec), encoding="utf-8")
    source = workbook_factory("source", ["DATE", "NORM", "OT"], [[20260314, 8, 2]])
    target = tmp_path / "output.csv"
    result = run("sgp", source, target, config_dir=tmp_path)
    assert result.status == "PREPARED"
    with target.open(encoding="utf-8-sig", newline="") as stream:
        assert list(csv.reader(stream)) == [["DATE", "NORM", "OT"], ["20260314", "8.0", "2.0"]]


@pytest.mark.parametrize("failure", ["missing", "unsupported", "sheet", "no_headers"])
def test_source_failures_produce_report_and_preserve_existing_output(
    failure, workbook_factory, tmp_path,
):
    source = workbook_factory("source", ["DATE", "NORM", "OT"], [[20260314, 8, 2]])
    kwargs = {}
    if failure == "missing":
        source = tmp_path / "missing.xlsx"
    elif failure == "unsupported":
        source = tmp_path / "legacy.xls"
        source.write_text("unsupported")
    elif failure == "sheet":
        kwargs["sheet"] = "Not present"
    else:
        source = workbook_factory("unrecognized", ["Unknown"], [["unrelated"]])
    target = tmp_path / "prior.xlsx"
    target.write_bytes(b"previous successful output")
    audit = tmp_path / "reports/audit.json"
    result = run("sgp", source, target, report_path=audit, **kwargs)
    assert result.status == "FAILED"
    assert any(i.code == "PREPARATION_FAILURE" for i in result.issues)
    assert target.read_bytes() == b"previous successful output"
    assert json.loads(audit.read_text())["status"] == "FAILED"


def test_failed_validation_warns_about_stale_output(workbook_factory, tmp_path):
    source = workbook_factory("bad", ["DATE", "NORM", "OT"], [[20260314, -1, 2]])
    target = tmp_path / "previous.xlsx"
    target.write_bytes(b"old output")
    result = run("sgp", source, target)
    assert result.status == "FAILED"
    assert any(i.code == "PREVIOUS_OUTPUT_REMAINS" for i in result.issues)
    assert target.read_bytes() == b"old output"


@pytest.mark.parametrize("validate_only", [False, True])
def test_success_and_validation_only_have_consistent_reports(
    validate_only, workbook_factory, tmp_path,
):
    source = workbook_factory("source", ["DATE", "NORM", "OT", "DAYFORCEUC1"],
                              [[20260314, 8, 2, "1000"]])
    target = tmp_path / "new/output.xlsx"
    audit = tmp_path / "reports/result.json"
    result = run("sgp", source, target, strict=True, validate_only=validate_only, report_path=audit, week_ending=date(2026, 3, 14))
    assert result.status == ("VALIDATED" if validate_only else "PREPARED")
    assert target.exists() is not validate_only
    saved = json.loads(audit.read_text())
    assert saved == result.as_dict()
    assert saved["summary"]["errors"] == saved["summary"]["warnings"] == 0
    assert result.output_path == (None if validate_only else str(target))


def test_in_place_overwrite_is_blocked(workbook_factory):
    source = workbook_factory("source", ["DATE", "NORM", "OT"], [[20260314, 8, 2]])
    original = source.read_bytes()
    result = run("sgp", source, source)
    assert result.status == "FAILED"
    assert any(i.code == "IN_PLACE_OVERWRITE" for i in result.issues)
    assert source.read_bytes() == original


def test_failed_write_removes_temporary_candidate(workbook_factory, tmp_path, monkeypatch):
    source = workbook_factory("source", ["DATE", "NORM", "OT"], [[20260314, 8, 2]])
    target = tmp_path / "output.xlsx"
    target.write_bytes(b"prior")

    def partial_write(prepared, path, fmt):
        path.write_bytes(b"incomplete")
        raise OSError("simulated disk error")

    monkeypatch.setattr("factoryprep.engine.write_prepared", partial_write)
    result = run("sgp", source, target)
    assert result.status == "FAILED"
    assert target.read_bytes() == b"prior"
    assert not (tmp_path / ".output.tmp.xlsx").exists()
    assert json.loads((tmp_path / "output_quality.json").read_text())["status"] == "FAILED"


def test_multiple_matching_sheets_require_explicit_selection(workbook_factory, tmp_path):
    source = workbook_factory("source", ["DATE", "NORM", "OT"], [[20260314, 8, 2]])
    wb = load_workbook(source)
    wb.copy_worksheet(wb.active).title = "Second"
    wb.save(source)
    wb.close()
    target = tmp_path / "output.xlsx"
    assert run("sgp", source, target).status == "FAILED"
    assert not target.exists()
    selected = run("sgp", source, target, sheet="Second")
    assert selected.status == "PREPARED"
    assert selected.source_sheet == "Second"


@pytest.mark.parametrize("headers,issue", [
    (["DATE", "NORM", "OT", "OT"], "INVALID_REFERENCE"),
    (["DATE", "NORM"], "DESTINATION_COLUMNS_EXTRA"),
    (["DATE", "NORM", "OT", "Extra"], "DESTINATION_COLUMNS_MISSING"),
])
def test_bad_destination_templates_block_output(headers, issue, workbook_factory, tmp_path):
    source = workbook_factory("source", ["DATE", "NORM", "OT"], [[20260314, 8, 2]])
    reference = workbook_factory("reference", headers, [])
    target = tmp_path / "output.xlsx"
    result = run("sgp", source, target, reference=reference)
    assert result.status == "FAILED"
    assert any(i.code == issue for i in result.issues)
    assert not target.exists()


def test_auto_detection_does_not_trust_filename_without_headers(workbook_factory):
    source = workbook_factory("dayforce_ccb", ["Nonsense"], [[1]])
    with pytest.raises(DetectionError, match="No source profile"):
        detect_profile(source)


@pytest.mark.parametrize("suffix", [".xlsx", ".xlsm"])
def test_damaged_excel_container_fails_with_json_audit(suffix, tmp_path):
    source = tmp_path / f"damaged{suffix}"
    source.write_bytes(b"not a valid ZIP workbook")
    target = tmp_path / "blocked.xlsx"
    result = run("sgp", source, target)
    assert result.status == "FAILED"
    assert any(i.code == "PREPARATION_FAILURE" and "damaged" in i.message
               for i in result.issues)
    assert json.loads((tmp_path / "blocked_quality.json").read_text())["status"] == "FAILED"
    assert source.read_bytes() == b"not a valid ZIP workbook"
    assert not target.exists()


@pytest.mark.parametrize("fault", ["empty", "multiple_sheets"])
def test_invalid_reference_workbook_shapes(workbook_factory, tmp_path, fault):
    source = workbook_factory("source", ["DATE", "NORM", "OT"], [[20260314, 8, 2]])
    reference = workbook_factory("ref", [] if fault == "empty" else ["DATE", "NORM", "OT"], [])
    if fault == "multiple_sheets":
        wb = load_workbook(reference)
        wb.create_sheet("Second")
        wb.save(reference)
        wb.close()
    target = tmp_path / "blocked.xlsx"
    result = run("sgp", source, target, reference=reference)
    assert result.status == "FAILED"
    assert any(i.code == "PREPARATION_FAILURE" for i in result.issues)
    assert not target.exists()


@pytest.mark.parametrize("command", ["profiles", "describe", "detect", "prepare", "validate"])
def test_cli_commands(command, workbook_factory, tmp_path):
    source = workbook_factory("source", ["DATE", "NORM", "OT"], [[20260314, 8, 2]])
    target = tmp_path / "output.xlsx"
    args = [command]
    if command == "describe":
        args += ["sgp"]
    elif command != "profiles":
        args += ["--input", str(source)]
        if command != "detect":
            args += ["--profile", "sgp", "--output", str(target)]
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 0, result.output
    assert ("VALIDATED" if command == "validate" else "PREPARED"
            if command == "prepare" else "sgp") in result.output
    assert target.exists() == (command == "prepare")


@pytest.mark.parametrize("fault", ["date", "profile", "strict", "data"])
def test_cli_failure_exit_codes(fault, workbook_factory, tmp_path):
    source = workbook_factory("source", ["DATE", "NORM", "OT"],
                              [[20260314, -1 if fault == "data" else 8, 2]])
    target = tmp_path / "blocked.xlsx"
    args = ["prepare", "--profile", "absent" if fault == "profile" else "sgp",
            "--input", str(source), "--output", str(target)]
    if fault == "date":
        args += ["--week-ending", "not-a-date"]
    elif fault == "strict":
        args += ["--strict"]
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 2, result.output
    assert not target.exists()


def test_non_saturday_week_end_blocks_tabular_output(workbook_factory, tmp_path):
    source = workbook_factory("source", ["DATE", "NORM", "OT"], [[20260314, 8, 2]])
    target = tmp_path / "blocked.xlsx"
    result = run("sgp", source, target, week_ending=date(2026, 3, 13))
    assert result.status == "FAILED"
    assert any(i.code == "INVALID_WEEK_END" for i in result.issues)
    assert not target.exists()


def test_batch_continues_after_bad_job_and_keeps_reports_separate(workbook_factory, tmp_path):
    good = workbook_factory("good", ["DATE", "NORM", "OT"], [[20260314, 8, 2]])
    bad = workbook_factory("bad", ["DATE", "NORM", "OT"], [[20260314, -1, 2]])
    jobs = [{"profile": "sgp"},
            {"profile": "sgp", "input": str(bad), "output": str(tmp_path / "bad_out.xlsx")},
            {"profile": "sgp", "input": str(good), "output": str(tmp_path / "good_out.xlsx")}]
    manifest = tmp_path / "batch.yaml"
    manifest.write_text(yaml.safe_dump({"jobs": jobs}), encoding="utf-8")
    result = CliRunner().invoke(app, ["batch", "--manifest", str(manifest)])
    assert result.exit_code == 2, result.output
    assert "1 succeeded; 2 failed" in result.output
    assert not (tmp_path / "bad_out.xlsx").exists()
    assert (tmp_path / "good_out.xlsx").exists()
    assert json.loads((tmp_path / "bad_out_quality.json").read_text())["status"] == "FAILED"
    assert json.loads((tmp_path / "good_out_quality.json").read_text())["status"] == "PREPARED"


@pytest.mark.parametrize("data", [None, [], {"jobs": "bad"}])
def test_batch_rejects_invalid_manifest_shape(data, tmp_path):
    manifest = tmp_path / "batch.yaml"
    manifest.write_text(yaml.safe_dump(data), encoding="utf-8")
    result = CliRunner().invoke(app, ["batch", "--manifest", str(manifest)])
    assert result.exit_code == 2
    assert "jobs: list" in result.output
