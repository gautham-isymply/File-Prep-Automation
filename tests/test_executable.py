"""Exercise file-drop safety and the shared executable/installed launcher."""
import json
import sys
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from factoryprep import launcher
from factoryprep.cli import app

runner = CliRunner()


def test_drop_multiple_files_and_repeat_preserve_sources(workbook_factory, tmp_path):
    files = [workbook_factory(name, ["DATE", "NORM", "OT"], [[20260314, 8, 2]])
             for name in ("first input", "second input")]
    originals = [p.read_bytes() for p in files]
    for _ in range(2):
        result = runner.invoke(app, ["drop", *map(str, files)])
        assert result.exit_code == 0, result.output
        assert "2 succeeded; 0 failed" in result.output
    reports = list(tmp_path.glob("factoryprep-*/*_quality.json"))
    assert len(reports) == 4
    assert all(json.loads(p.read_text())["status"] == "PREPARED" for p in reports)
    assert [p.read_bytes() for p in files] == originals


def test_drop_mixed_failures_continue_and_return_two(workbook_factory, tmp_path):
    good = workbook_factory("good", ["DATE", "NORM", "OT"], [[20260314, 8, 2]])
    bad = workbook_factory("bad", ["DATE", "NORM", "OT"], [[20260314, -8, 2]])
    result = runner.invoke(app, ["drop", str(tmp_path / "missing.csv"), str(bad), str(good)])
    assert result.exit_code == 2, result.output
    assert "1 succeeded; 2 failed" in result.output
    statuses = {json.loads(p.read_text())["status"]
                for p in tmp_path.glob("factoryprep-*/*_quality.json")}
    assert statuses == {"PREPARED", "FAILED"}


def test_drop_ambiguous_detection_requires_explicit_profile(tmp_path):
    from factoryprep.config import load_profile

    headers = load_profile("dayforce_ccb")["columns"]["required"]
    source = tmp_path / "ambiguous.csv"
    source.write_text(",".join(headers) + "\n", encoding="utf-8")
    result = runner.invoke(app, ["drop", str(source)])
    assert result.exit_code == 2
    assert "Ambiguous" in result.output
    assert not list(tmp_path.glob("factoryprep-*"))


def test_drop_explicit_profile_and_strict_gate(workbook_factory, tmp_path):
    source = workbook_factory("input", ["DATE", "NORM", "OT"], [[20260314, 8, 2]])
    result = runner.invoke(app, ["drop", str(source), "--profile", "sgp", "--strict"])
    assert result.exit_code == 2
    assert "FAILED" in result.output
    assert not list(tmp_path.glob("factoryprep-*/*.xlsx"))


@pytest.mark.parametrize("args,expected", [
    ([], ["--help"]),
    (["profiles"], ["profiles"]),
    (["prepare", "--help"], ["prepare", "--help"]),
    (["C:/folder with spaces/file.xlsx"], ["drop", "C:/folder with spaces/file.xlsx"]),
])
def test_launcher_dispatch(args, expected, monkeypatch):
    calls = []
    monkeypatch.setattr(sys, "argv", ["factoryprep.exe", *args])
    monkeypatch.setattr(launcher, "app", lambda **kwargs: calls.append(kwargs))
    monkeypatch.setattr(launcher, "_owns_console", lambda: False)
    launcher.main()
    assert calls == [{"args": expected, "prog_name": "factoryprep"}]


def test_explorer_console_pauses_even_on_failed_command(monkeypatch):
    pauses = []
    monkeypatch.setattr(sys, "argv", ["factoryprep.exe", "profiles"])
    monkeypatch.setattr(launcher, "_owns_console", lambda: True)
    monkeypatch.setattr("builtins.input", lambda prompt: pauses.append(prompt))

    def fail(**kwargs):
        raise SystemExit(2)

    monkeypatch.setattr(launcher, "app", fail)
    with pytest.raises(SystemExit, match="2"):
        launcher.main()
    assert len(pauses) == 1


@pytest.mark.parametrize("ids,bootloader,expected", [
    ([123], False, True),
    ([123, 456], True, True),
    ([123, 456], False, False),
    ([123, 456, 789], True, False),
    ([], False, False),
])
def test_console_ownership_accounts_for_onefile_bootloader(ids, bootloader, expected, monkeypatch):
    def console_list(buffer, size):
        for index, pid in enumerate(ids):
            buffer[index] = pid
        return len(ids)

    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(launcher.os, "getppid", lambda: 456)
    monkeypatch.setattr(launcher, "_parent_is_bootloader", lambda: bootloader)
    monkeypatch.setattr(launcher.ctypes, "windll", SimpleNamespace(
        kernel32=SimpleNamespace(GetConsoleProcessList=console_list)), raising=False)
    assert launcher._owns_console() is expected
