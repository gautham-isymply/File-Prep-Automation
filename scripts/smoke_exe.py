"""Smoke a copied standalone EXE outside the checkout using synthetic inputs only."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def smoke(executable: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="factoryprep-smoke-") as temporary:
        root = Path(temporary)
        binary = root / "factoryprep.exe"
        shutil.copy2(executable, binary)
        env = {key: value for key, value in os.environ.items()
               if key not in {"PYTHONPATH", "PYTHONHOME"}}

        def command(*args: str, expected: int = 0) -> str:
            result = subprocess.run(
                [str(binary), *args], check=False, cwd=root, env=env, capture_output=True,
                text=True, encoding="utf-8", errors="replace", timeout=60,
            )
            if result.returncode != expected:
                raise AssertionError(f"{args}: exit {result.returncode}\n"
                                     f"{result.stdout}\n{result.stderr}")
            return result.stdout + result.stderr

        assert "prepare" in command("--help")
        assert "drop" in command()
        profiles = ("sgp", "gbr", "ccb", "cbg_core", "cbg_starline", "jz",
                    "dayforce_ccb", "dayforce_non_ccb", "reno", "taiwan")
        listed = command("profiles")
        for profile in profiles:
            assert profile in listed
            assert f"id: {profile}" in command("describe", profile)
        sources = [root / "first input.csv", root / "second input.csv"]
        for source in sources:
            source.write_text("DATE,NORM,OT,DAYFORCEUC1\n20260314,8,2,1000\n", encoding="utf-8")
        original = [source.read_bytes() for source in sources]
        assert "PREPARED" in command("prepare", "--profile", "sgp", "--input",
                                     str(sources[0]), "--strict", "--week-ending", "2026-03-14")
        for _ in range(2):
            assert "2 succeeded; 0 failed" in command(*map(str, sources))
        assert len(list(root.glob("factoryprep-*/*_quality.json"))) == 4
        assert "1 succeeded; 1 failed" in command(
            "drop", str(root / "missing.csv"), str(sources[0]), expected=2,
        )
        bad = root / "bad.csv"
        bad.write_text("DATE,NORM,OT\n20260314,-8,2\n", encoding="utf-8")
        assert "FAILED" in command(str(bad), expected=2)
        assert "FAILED" in command("validate", "--profile", "sgp", "--input",
                                   str(bad), expected=2)
        assert [source.read_bytes() for source in sources] == original
        reports = [json.loads(p.read_text()) for p in root.glob("factoryprep-*/*_quality.json")]
        assert {r["status"] for r in reports} == {"PREPARED", "FAILED"}

        gbr = root / "ambiguous-gbr.csv"
        gbr.write_text("DATEIN,DATEOUT,REGHOURS,O1HOURS,O2HOURS\n14/03/2026,14/03/2026,0.5,0,0\n")
        assert "AMBIGUOUS_TIME_FRACTION" in command("prepare", "--profile", "gbr", "--input", str(gbr), expected=2)
        reno = root / "reno.csv"
        with reno.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["Name", *[f"{day:02d}/03/2026" for day in range(8, 15)]])
            writer.writerow(["Synthetic employee", 0, "8,75", "8,75", "8,75", "8,75", "8,75", 0])
        assert "PREPARED" in command("prepare", "--profile", "reno", "--input", str(reno),
                                    "--week-ending", "2026-03-14", "--strict")
        assert json.loads((root / "reno_reno_prepared_quality.json").read_text())["diagnostics"]["weekly_paid_hours"] == 43.75
        components = []
        for profile, code, location in [("dayforce_ccb", "1000 > Direct Labor", "DPC CCB"),
                                        ("dayforce_non_ccb", "1025 > Plugs", "DPC BUS")]:
            source = root / f"{profile}.csv"
            source.write_text("Cost_Center,Pay_Date,Location,Pay_Category,Normal\n"
                              f"{code},03/14/2026,{location},Reg,8\n"
                              f"{code},03/14/2026,{location},OT 1.5,2\n", encoding="utf-8")
            assert "EXTERNAL_REFRESH_NOT_PERFORMED" in command("validate", "--profile", profile,
                                                                 "--input", str(source), expected=2)
            attestation = root / f"{profile}-evidence.yaml"
            attestation.write_text(json.dumps({"source_evidence": {
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "refreshed_at": "2026-03-15T09:00:00-05:00", "approved_by": "synthetic smoke",
            }}), encoding="utf-8")
            audit = root / f"{profile}-audit.json"
            assert "PREPARED" in command("prepare", "--profile", profile, "--input", str(source),
                                        "--week-ending", "2026-03-14", "--overrides", str(attestation),
                                        "--strict", "--report", str(audit))
            components.append(audit)
        combined = root / "combined.json"
        assert "RECONCILED" in command("reconcile", "--group", "us", "--component", str(components[0]),
                                     "--component", str(components[1]), "--output", str(combined))
        assert json.loads(combined.read_text())["paid_hours"] == 16
        print("PASS standalone EXE: help, 10 embedded profiles, prepare, validate, repeated "
              "multi-file bare paths, mixed failures, JSON reports, source preservation, "
              "GBR ambiguity gate, Reno DMY/comma hours, Dayforce evidence and combined US audit")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("executable", type=Path)
    smoke(parser.parse_args().executable.resolve())
