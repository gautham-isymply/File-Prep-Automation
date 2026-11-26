"""Combine successful, scoped source audits without loading any destination."""
from __future__ import annotations

import json
import math
import re
from datetime import date, timedelta
from pathlib import Path

GROUPS = {
    "us": {
        "dayforce_ccb": ("us_ccb_reg_hours", "us_ccb_ot_hours"),
        "dayforce_non_ccb": ("us_non_ccb_reg_hours", "us_non_ccb_ot_hours"),
    },
    "cbg": {
        "cbg_core": ("core_reg_hours", "core_ot_hours"),
        "cbg_starline": ("starline_straight_hours_filtered", "starline_overtime_hours_filtered"),
    },
}


def combine_reports(group: str, reports: list[Path], output: Path) -> dict:
    if group not in GROUPS:
        raise ValueError("Reconciliation group must be us or cbg")
    expected = GROUPS[group]
    if len(reports) != len(expected):
        raise ValueError("Exactly two component reports are required")
    components = {}
    period = None
    protected = {p.resolve() for p in reports}
    for path in reports:
        report = json.loads(path.read_text(encoding="utf-8"))
        profile = report["profile"]
        if profile not in expected or profile in components:
            raise ValueError("Expected exactly one report per component profile")
        if report["status"] not in {"PREPARED", "VALIDATED"} or any(
            issue["severity"] == "ERROR" for issue in report.get("issues", [])
        ):
            raise ValueError("Failed component cannot be reconciled")
        diagnostics = report["diagnostics"]
        source_hash = diagnostics.get("source_sha256", "")
        if not isinstance(source_hash, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", source_hash):
            raise ValueError("Component needs a valid source SHA-256")
        if not diagnostics.get("reconciliation_contract_confirmed") or not diagnostics.get("reconciliation_scoped"):
            raise ValueError("Component needs confirmed filters and a scoped date column")
        window = diagnostics["reconciliation_period"]
        start, end = date.fromisoformat(window["start"]), date.fromisoformat(window["end"])
        if end.weekday() != 5 or end - start != timedelta(days=6):
            raise ValueError("Component period must be Sunday through Saturday")
        if period is not None and window != period:
            raise ValueError("Component periods differ")
        period = window
        if group == "us":
            refresh = diagnostics.get("refresh_evidence")
            if not isinstance(refresh, dict) or refresh.get("sha256", "").lower() != source_hash.lower():
                raise ValueError("Both US exports require source-bound refresh evidence")
        metrics = diagnostics["filtered_reconciliation_metrics"]
        totals = [metrics[name]["total"] for name in expected[profile]]
        if any(type(t) not in (int, float) or not math.isfinite(t) for t in totals):
            raise ValueError("Component totals must be finite numbers")
        components[profile] = {"paid_hours": totals[0], "ot_hours": totals[1],
                               "source_sha256": diagnostics["source_sha256"],
                               "report": str(path)}
        for key in ("input_path", "output_path"):
            if report.get(key):
                protected.add(Path(report[key]).resolve())
    if output.resolve() in protected:
        raise ValueError("Combined report must not overwrite inputs, outputs or component reports")
    result = {"group": group, "status": "RECONCILED", "period": period,
              "components": components,
              "paid_hours": round(sum(c["paid_hours"] for c in components.values()), 6),
              "ot_hours": round(sum(c["ot_hours"] for c in components.values()), 6)}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
