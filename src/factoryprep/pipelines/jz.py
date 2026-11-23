"""JZ business units from a structured source extraction, configurable label map.

The manual does not specify the incoming workbook cell locations for Paid/OT values;
we explicitly require a staging source with Category, Paid Hours and OT Hours.
Never guess that HC invoice hours are equivalent to paid/OT hours.
"""
from __future__ import annotations

from datetime import timedelta

from ..models import Context, Prepared, RawSheet, RunReport
from ..transform import norm
from .tabular import prepare_tabular


def prepare_jz(sheet: RawSheet, header_index: int, ctx: Context,
               report: RunReport) -> Prepared:
    source = prepare_tabular(sheet, header_index, ctx, report)
    if report.errors:
        return source
    if ctx.week_ending is None:
        report.add("ERROR", "WEEK_END_REQUIRED", "JZ requires --week-ending YYYY-MM-DD")
        return source
    if ctx.week_ending.weekday() != 5:
        report.add("ERROR", "INVALID_WEEK_END", "JZ week end must be Saturday")
        return source
    sunday = ctx.week_ending - timedelta(days=6)
    mappings = ctx.profile.get("category_mapping", {})
    output = []
    matched: set[str] = set()
    for record, origin in zip(source.rows, source.source_rows):
        raw = record["Category"]
        key = next((k for k in mappings if norm(raw) == norm(k)), None)
        if key is None:
            report.add("ERROR", "UNKNOWN_BUSINESS_LABEL", f"Unmapped category {raw!r}",
                       origin, "Category")
            continue
        if key in matched:
            report.add("ERROR", "DUPLICATE_BUSINESS_CATEGORY",
                       f"Multiple source rows for {key!r}; no implicit aggregation", origin, "Category")
            continue
        matched.add(key)
        spec = mappings[key]
        output.append({"Segment": spec["segment"], "Plant": str(spec["plant"]),
                       "Plant name": spec["plant_name"], "Profitcent": spec["profit_center"],
                       "Companycode": str(spec["company_code"]), "Date": sunday,
                       "Paid Hours": record["Paid Hours"], "OT Hours": record["OT Hours"]})
    for category in mappings:
        if category not in matched:
            report.add("ERROR", "MISSING_BUSINESS_CATEGORY",
                       f"JZ source lacks required group: {category}", column="Category")
    columns = ctx.profile["output"]["columns"]
    return Prepared(columns, output, ctx.profile.get("output", {}).get("sheet", "JZ"),
                    {"Date": ctx.profile.get("output", {}).get("date_format", "m/d/yyyy")},
                    diagnostics={"week_start": str(sunday), "week_end": str(ctx.week_ending),
                                 "categories_matched": len(matched),
                                 "paid_total": round(sum(x["Paid Hours"] for x in output if isinstance(x["Paid Hours"], (float, int))), 6),
                                 "ot_total": round(sum(x["OT Hours"] for x in output if isinstance(x["OT Hours"], (float, int))), 6)})
