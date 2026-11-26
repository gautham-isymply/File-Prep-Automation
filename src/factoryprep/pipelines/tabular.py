"""Config-driven tabular normalization used by seven source families."""
from __future__ import annotations

from datetime import date
from typing import Any

from ..models import CellValue, Context, Prepared, RawSheet, RunReport
from ..transform import excel_hours, is_blank, norm, parse_date, parse_number, suggest_header


def _header_mapping(raw_headers: list[str], profile: dict[str, Any], report: RunReport) -> dict[int, str]:
    cfg = profile.get("columns", {})
    aliases = cfg.get("aliases", {})
    lookup: dict[str, str] = {}
    for required in cfg.get("required", []):
        lookup[norm(required)] = required
    for canonical, names in aliases.items():
        lookup[norm(canonical)] = canonical
        for alias in names:
            key = norm(alias)
            if key in lookup and lookup[key] != canonical:
                report.add("ERROR", "INVALID_PROFILE_ALIASES", f"Conflicting alias {alias}")
            lookup[key] = canonical
    mapping: dict[int, str] = {}
    existing: dict[str, int] = {}
    for index, raw in enumerate(raw_headers):
        if not raw:
            continue
        canonical = lookup.get(norm(raw), raw.strip())
        if canonical in existing or norm(canonical) in {norm(v) for v in mapping.values()}:
            report.add("ERROR", "DUPLICATE_HEADER", f"Repeated/alias-colliding column {raw!r}",
                       column=raw)
        else:
            existing[canonical] = index
            mapping[index] = canonical
            if canonical != raw:
                report.add("INFO", "HEADER_NORMALIZED",
                           f"Header {raw!r} mapped to {canonical!r}", column=canonical)
    for required in cfg.get("required", []):
        if required not in mapping.values():
            suggestion = suggest_header(required, raw_headers)
            hint = f"; possible typo: {suggestion!r}" if suggestion else ""
            report.add("ERROR", "MISSING_COLUMN", f"Missing required column {required!r}{hint}",
                       column=required)
    if cfg.get("expected"):
        expected = set(cfg["expected"])
        found = set(mapping.values())
        for item in sorted(found - expected - set(cfg.get("drop", []))):
            report.add("WARNING", "UNEXPECTED_COLUMN", f"Not in declared full schema: {item}",
                       column=item)
        for item in sorted(expected - found):
            report.add("ERROR", "EXPECTED_COLUMN_MISSING", f"Full schema requires {item}",
                       column=item)
    return mapping


def _find_header(sheet: RawSheet, profile: dict[str, Any]) -> tuple[int, int]:
    cfg = profile.get("columns", {})
    required = [norm(i) for i in cfg.get("required", [])]
    synonyms: dict[str, set[str]] = {}
    for name in cfg.get("required", []):
        synonyms[norm(name)] = {norm(name), *(norm(x) for x in cfg.get("aliases", {}).get(name, []))}
    best_score, best_index = -1, -1
    for i, row in enumerate(sheet.rows[:profile.get("header_scan_rows", 40)]):
        names = {norm(c.value) for c in row if not is_blank(c.value)}
        if not names:
            continue
        score = sum(bool(names & synonyms.get(key, {key})) for key in required)
        if score > best_score:
            best_score, best_index = score, i
        if score == len(required) and required:
            return i, score
    return best_index, best_score


def select_tabular_sheet(sheets: list[RawSheet], ctx: Context, report: RunReport) -> tuple[RawSheet, int]:
    if ctx.sheet_override:
        options = [s for s in sheets if s.name == ctx.sheet_override]
        if not options:
            raise ValueError(f"Sheet {ctx.sheet_override!r} not found; available: {[s.name for s in sheets]}")
    else:
        options = sheets
    matches = [(s, *_find_header(s, ctx.profile)) for s in options]
    if not matches:
        raise ValueError("Source file has no sheets")
    maximum = max(score for _, _, score in matches)
    winners = [(s, index) for s, index, score in matches if score == maximum]
    if maximum <= 0:
        raise ValueError("Cannot detect expected header in workbook; check profile and file layout")
    if len(winners) > 1 and not ctx.sheet_override:
        raise ValueError(f"Multiple sheets match profile equally: {[s.name for s, _ in winners]}; use --sheet")
    return winners[0]


def _row_is_summary(cells: list[CellValue], profile: dict[str, Any],
                    mapping: dict[int, str]) -> bool:
    if not profile.get("skip_summary_rows"):
        return False
    table = profile.get("table", {})
    labels = {str(s).strip().casefold() for s in table.get(
        "summary_labels", ["total", "grand total", "subtotal", "totals"])}
    selected = table.get("summary_columns", [next(iter(mapping.values()))])
    return any(i < len(cells) and str(cells[i].value).strip().casefold() in labels
               for i, name in mapping.items() if name in selected)


def _cost_center(value: Any) -> tuple[str, str] | None:
    """Only the documented code > label shape; never substring-match a code."""
    import re
    match = re.fullmatch(r"\s*(\d+)\s*>\s*(\S.*?)\s*", str(value))
    return (match[1], " ".join(match[2].casefold().split())) if match else None


def _matches(value: Any, rule: dict[str, Any]) -> bool:
    if "cost_center_code" in rule:
        import re
        parsed = _cost_center(value)
        token = re.match(r"\s*(\d+)", str(value))
        # Exact numeric tokens with malformed labels reach the blocking label guard.
        return (parsed[0] if parsed else token[1] if token else "") == rule["cost_center_code"]
    if "equals" in rule and norm(value) != norm(rule["equals"]):
        return False
    if "contains" in rule and norm(rule["contains"]) not in norm(value):
        return False
    return not ("in" in rule and norm(value) not in {norm(x) for x in rule["in"]})


def prepare_tabular(sheet: RawSheet, header_index: int, ctx: Context, report: RunReport) -> Prepared:
    profile = ctx.profile
    cfg = profile.get("columns", {})
    raw_headers = [str(c.value).strip() if not is_blank(c.value) else "" for c in sheet.rows[header_index]]
    errors_before_header = report.errors
    mapping = _header_mapping(raw_headers, profile, report)
    missing = [c for c in cfg.get("required", []) if c not in mapping.values()]
    if missing or report.errors > errors_before_header:
        return Prepared([], [], sheet.name)
    drops = set(cfg.get("drop", []))
    for name in drops:
        if name in mapping.values():
            report.add("INFO", "DROPPED_COLUMN", f"Removed {name} per source procedure", column=name)
    columns = [name for name in mapping.values() if name not in drops]
    dates: dict[str, dict[str, Any]] = {item["column"]: item for item in profile.get("dates", [])}
    numeric = set(cfg.get("numeric", []))
    numeric.update(set(cfg.get("numeric_if_present", [])) & set(columns))
    hours = set(profile.get("time_to_hours", []))
    strict_null = set(cfg.get("non_null", []))
    no_negative = set(cfg.get("negative_forbidden", []))
    if len(columns) != len(set(columns)):
        report.add("ERROR", "DUPLICATE_OUTPUT_COLUMN", "Output has nonunique column names")
    for col in [*dates, *numeric, *hours]:
        if col not in columns and col not in drops:
            report.add("ERROR", "TRANSFORM_COLUMN_MISSING", f"Rule references missing column {col}",
                       column=col)
    rows: list[dict[str, Any]] = []
    origins: list[int] = []
    seen_keys: dict[tuple[Any, ...], int] = {}
    skip_rules = profile.get("exclude_rows", [])
    excluded = 0
    row_audit = []
    table = profile.get("table", {})
    source_dates = []
    date_column = profile.get("reconciliation_date_column")
    if table.get("first_data_row", header_index + 2) <= header_index + 1:
        report.add("ERROR", "INVALID_TABLE_RANGE", "Data range overlaps header")
    for name in table.get("summary_columns", []):
        if name not in mapping.values():
            report.add("ERROR", "SUMMARY_COLUMN_MISSING", f"Missing summary label column {name}")
    for row_index, cells in enumerate(sheet.rows[header_index + 1:], start=header_index + 2):
        if not table.get("first_data_row", header_index + 2) <= row_index <= table.get(
            "last_data_row", len(sheet.rows)
        ):
            row_audit.append({"row": row_index, "reason": "declared_table_boundary"})
            continue
        if all(is_blank(c.value) for c in cells):
            row_audit.append({"row": row_index, "reason": "blank"})
            continue
        if _row_is_summary(cells, profile, mapping):
            row_audit.append({"row": row_index, "reason": "summary_label"})
            continue
        if profile.get("skip_summary_rows") and all(
            i < len(cells) and norm(cells[i].value) == norm(raw_headers[i]) for i in mapping
        ):
            row_audit.append({"row": row_index, "reason": "repeated_header"})
            continue
        raw_data = {name: cells[index] if index < len(cells) else CellValue(None)
                    for index, name in mapping.items()}
        if date_column in raw_data:
            try:
                source_dates.append(parse_date(raw_data[date_column].value,
                                               dates.get(date_column, {}).get("input", "auto")))
            except (ValueError, TypeError):
                pass  # Retained records receive normal field errors below.
        excluded_here = False
        for rule in skip_rules:
            if rule["column"] not in raw_data or not _matches(raw_data[rule["column"]].value, rule):
                continue
            expected_label = rule.get("expect_label_contains")
            if "expect_label" in rule:
                parsed = _cost_center(raw_data[rule["column"]].value)
                if not parsed or parsed[1] != " ".join(rule["expect_label"].casefold().split()):
                    report.add("ERROR", "EXCLUDED_ROW_LABEL_MISMATCH",
                               "Exact exclusion code has an unexpected/missing label",
                               row_index, rule["column"])
                    break
            if expected_label and norm(expected_label) not in norm(raw_data[rule["column"]].value):
                report.add("ERROR", "EXCLUDED_ROW_LABEL_MISMATCH",
                           f"Cost center matches exclusion code but label is not {expected_label!r}",
                           row_index, rule["column"])
                break
            excluded_here = True
            break
        if excluded_here:
            excluded += 1
            row_audit.append({"row": row_index, "reason": "exclude_rows",
                              "hours": raw_data.get("Normal", CellValue(None)).value})
            continue
        record: dict[str, Any] = {}
        for name in columns:
            cell = raw_data[name]
            val = cell.value
            if cell.excel_type == "e" or (isinstance(val, str) and val.startswith(("#VALUE!", "#REF!", "#DIV/0!", "#N/A"))):
                report.add("ERROR", "EXCEL_CELL_ERROR", f"Excel cell error: {val}", row_index, name)
                record[name] = val
                continue
            if is_blank(val):
                if name in strict_null or name in dates or name in hours or name in numeric:
                    report.add("ERROR", "NULL_VALUE", "Required numeric/date value is blank", row_index, name)
                record[name] = None
                continue
            try:
                if name in dates:
                    delim = dates[name].get("split_delimiter")
                    if delim and isinstance(val, str) and delim in val:
                        chunks = val.split(delim)
                        if any(part.strip() for part in chunks[1:]):
                            raise ValueError(f"Date cell has extra nonblank content after {delim!r}")
                        val = chunks[0].strip()
                        report.add("INFO", "EMPTY_DATE_DELIMITER_REMOVED",
                                   f"Removed trailing {delim!r} delimiter", row_index, name)
                    val = parse_date(val, dates[name].get("input", "auto"))
                elif name in hours:
                    val = excel_hours(cell, report, row_index, name,
                                      profile.get("hours_encoding", {}).get(name, "cell_format"))
                elif name in numeric:
                    val = parse_number(val)
                if name in no_negative and isinstance(val, (int, float)) and val < 0:
                    report.add("ERROR", "NEGATIVE_VALUE", f"Unexpected negative value: {val}", row_index, name)
            except (ValueError, TypeError, OverflowError) as exc:
                report.add("ERROR", "FORMAT_MISMATCH", str(exc), row_index, name)
            record[name] = val
        rows.append(record)
        origins.append(row_index)
        keys = cfg.get("duplicate_keys", [])
        if keys and all(k in record for k in keys):
            key = tuple(str(record[k]) for k in keys)
            if key in seen_keys:
                report.add("WARNING", "DUPLICATE_KEY", f"Same source key as row {seen_keys[key]}",
                           row_index)
            else:
                seen_keys[key] = row_index
    if excluded:
        report.add("INFO", "ROWS_EXCLUDED", f"Intentionally removed {excluded} rows by profile filters")
    _apply_overrides(rows, origins, ctx, report)
    _manual_reviews(rows, origins, profile, report)
    _check_cross_field_sums(rows, origins, profile, report)
    _check_dates(rows, origins, profile, ctx, report)
    metrics = _calculate_metrics(rows, profile, report, ctx.week_ending)
    diagnostics = {"filtered_reconciliation_metrics": metrics, "excluded_rows": excluded,
                   "row_audit": row_audit,
                   "reconciliation_contract_confirmed": profile.get(
                       "reconciliation_contract_confirmed", True),
                   "reconciliation_scoped": bool(date_column and ctx.week_ending)}
    if source_dates:
        diagnostics["date_range"] = {"min": str(min(source_dates)), "max": str(max(source_dates))}
    if ctx.week_ending:
        from datetime import timedelta
        diagnostics["reconciliation_period"] = {
            "start": str(ctx.week_ending - timedelta(days=6)), "end": str(ctx.week_ending)}
    return Prepared(columns, rows, profile.get("output", {}).get("sheet", sheet.name),
                    {name: c.get("excel_format", "yyyy-mm-dd") for name, c in dates.items()},
                    diagnostics=diagnostics,
                    source_rows=origins)


def _apply_overrides(rows: list[dict], origins: list[int], ctx: Context, report: RunReport) -> None:
    for fix in ctx.overrides.get("corrections", []):
        if fix.get("profile") != ctx.profile["id"]:
            continue
        where = fix.get("match", {})
        target = fix.get("column")
        matching = [(row, src) for row, src in zip(rows, origins)
                    if all(str(row.get(k)) == str(v) for k, v in where.items())]
        if len(matching) != 1 or not where or target not in matching[0][0]:
            report.add("ERROR", "OVERRIDE_MATCH_FAILURE",
                       f"Correction must match exactly one row and a valid column: {fix}")
            continue
        record, source_row = matching[0]
        if str(record[target]) != str(fix.get("expected_old")):
            report.add("ERROR", "OVERRIDE_OLD_VALUE_MISMATCH",
                       f"Expected {fix.get('expected_old')!r}, found {record[target]!r}", source_row, target)
            continue
        candidate = fix["new_value"]
        cfg = ctx.profile.get("columns", {})
        try:
            if target in cfg.get("numeric", []) + cfg.get("numeric_if_present", []) + ctx.profile.get("time_to_hours", []):
                candidate = parse_number(candidate)
            if target in cfg.get("non_null", []) and is_blank(candidate):
                raise ValueError("blank correction for required value")
            if target in cfg.get("negative_forbidden", []) and isinstance(candidate, (int, float)) and candidate < 0:
                raise ValueError("negative correction")
            for rule in ctx.profile.get("dates", []):
                if target == rule["column"]:
                    candidate = parse_date(candidate, rule.get("input", "auto"))
        except (ValueError, TypeError) as exc:
            report.add("ERROR", "INVALID_CORRECTION_VALUE", str(exc), source_row, target)
            continue
        record[target] = candidate
        report.add("INFO", "APPROVED_CORRECTION",
                   f"Changed {target} from {fix['expected_old']} to {fix['new_value']}", source_row, target)


def _manual_reviews(rows: list[dict], origins: list[int], profile: dict,
                    report: RunReport) -> None:
    for record, origin in zip(rows, origins):
        for review in profile.get("manual_review", []):
            column = review.get("column")
            if column in record and str(record[column]) == str(review.get("equals")):
                report.add("WARNING", "MANUAL_REVIEW_REQUIRED",
                           review.get("message", "Record requires manual confirmation"), origin, column)


def _check_cross_field_sums(rows: list[dict], origins: list[int], profile: dict,
                            report: RunReport) -> None:
    for record, origin in zip(rows, origins):
        for rule in profile.get("cross_field_sums", []):
            parts = rule["parts"]
            total = rule["total"]
            if all(isinstance(record.get(c), (int, float)) for c in [*parts, total]):
                observed = sum(record[c] for c in parts)
                if abs(observed - record[total]) > rule.get("tolerance", 0.02):
                    report.add("WARNING", "TOTAL_MISMATCH",
                               f"{total}={record[total]} vs sum({', '.join(parts)})={observed:.4f}",
                               origin, total)


def _check_dates(rows: list[dict], origins: list[int], profile: dict, ctx: Context,
                 report: RunReport) -> None:
    date_column = profile.get("date_continuity_column")
    if not date_column or not rows:
        return
    values = {r[date_column] for r in rows if isinstance(r.get(date_column), date)}
    if not values:
        return
    seen = set()
    for record, origin in zip(rows, origins):
        day = record.get(date_column)
        if isinstance(day, date):
            if day in seen:
                report.add("WARNING", "DUPLICATE_DATE", "Repeated source date; no rows removed", origin, date_column)
            seen.add(day)
    start = min(values)
    end = max(values)
    from datetime import timedelta
    if ctx.week_ending:
        start, end = ctx.week_ending - timedelta(days=6), ctx.week_ending
    missing = [start + timedelta(days=i) for i in range((end - start).days + 1)
               if start + timedelta(days=i) not in values]
    if missing:
        report.add("WARNING", "MISSING_DATES",
                   f"{len(missing)} calendar days missing from {start} to {end}: "
                   + ", ".join(str(d) for d in missing[:20]))
    if ctx.week_ending and ctx.week_ending.weekday() != 5:
        report.add("ERROR", "INVALID_WEEK_END", "Week-ending date must be a Saturday")


def _calculate_metrics(rows: list[dict], profile: dict, report: RunReport,
                       week_ending: date | None = None) -> dict:
    """Metrics are advisory source totals, NEVER filters applied to output."""
    results: dict[str, Any] = {}
    if not profile.get("reconciliation"):
        return results
    if not profile.get("reconciliation_contract_confirmed", True):
        report.add("WARNING", "RECONCILIATION_CONTRACT_UNCONFIRMED",
                   "Department filters are unconfirmed; totals are provisional")
    date_column = profile.get("reconciliation_date_column")
    if date_column and not week_ending:
        report.add("WARNING", "RECONCILIATION_WEEK_REQUIRED",
                   "Use --week-ending for weekly totals; unscoped totals are not reported")
        return results
    for spec in profile.get("reconciliation", []):
        source = spec["column"]
        required = {source, *(rule["column"] for rule in spec.get("filters", []))}
        if date_column:
            required.add(date_column)
        absent = sorted(required - (set(rows[0]) if rows else set()))
        if absent:
            report.add("WARNING", "RECONCILIATION_COLUMNS_MISSING",
                       f"Cannot calculate {spec['name']}; missing columns {absent}")
            continue
        selected = rows
        if date_column and week_ending:
            from datetime import timedelta
            start = week_ending - timedelta(days=6)
            selected = [r for r in selected if isinstance(r.get(date_column), date)
                        and start <= r[date_column] <= week_ending]
        for rule in spec.get("filters", []):
            col = rule["column"]
            if "in" in rule:
                selected = [r for r in selected if norm(r.get(col)) in {norm(x) for x in rule["in"]}]
            if "not_in" in rule:
                selected = [r for r in selected if norm(r.get(col)) not in {norm(x) for x in rule["not_in"]}]
            if "contains_any" in rule:
                selected = [r for r in selected if any(norm(s) in norm(r.get(col)) for s in rule["contains_any"])]
            if "cost_center_in" in rule:
                selected = [r for r in selected if _cost_center(r.get(col)) in
                            {_cost_center(s) for s in rule["cost_center_in"]} - {None}]
        valid = []
        invalid = False
        for record in selected:
            try:
                valid.append(parse_number(record.get(source)))
            except (ValueError, TypeError):
                report.add("ERROR", "INVALID_RECONCILIATION_VALUE",
                           f"Cannot sum every selected value for {spec['name']}", column=source)
                invalid = True
        if invalid:
            continue
        results[spec["name"]] = {"total": round(sum(valid), 6), "rows": len(selected)}
    return results
