"""Configuration discovery and fail-fast config integrity validation."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    pass


def _read_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"{path}: invalid YAML: {exc}") from exc


def _mapping(value: Any, location: str) -> dict:
    if not isinstance(value, dict):
        raise ConfigError(f"{location} must be a mapping")
    return value


def _strings(value: Any, location: str) -> None:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ConfigError(f"{location} must be a list of nonblank strings")


def _text(value: Any, location: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{location} must be a nonblank string")


def _rules(data: dict, key: str, location: str) -> list[dict]:
    value = data.get(key, [])
    if not isinstance(value, list):
        raise ConfigError(f"{location}.{key} must be a list")
    for index, item in enumerate(value):
        _mapping(item, f"{location}.{key}[{index}]")
    return value


def _validate_structure(data: dict, location: str) -> None:
    """Validate consumed structures; unknown extension keys remain compatible."""
    columns = _mapping(data.get("columns", {}), f"{location}.columns")
    for key in ("required", "drop", "expected", "numeric", "negative_forbidden",
                "non_null", "duplicate_keys"):
        if key in columns:
            _strings(columns[key], f"{location}.columns.{key}")
    aliases = _mapping(columns.get("aliases", {}), f"{location}.columns.aliases")
    for key in ("numeric_if_present",):
        if key in columns:
            _strings(columns[key], f"{location}.columns.{key}")
    encodings = _mapping(data.get("hours_encoding", {}), f"{location}.hours_encoding")
    for column, encoding in encodings.items():
        if column not in data.get("time_to_hours", []) or encoding not in (
            "cell_format", "decimal_hours", "excel_days"
        ):
            raise ConfigError(f"{location}.hours_encoding needs a time_to_hours column and valid units")
    table = _mapping(data.get("table", {}), f"{location}.table")
    for key in ("first_data_row", "last_data_row"):
        if key in table and (type(table[key]) is not int or table[key] <= 0):
            raise ConfigError(f"{location}.table.{key} must be a positive integer")
    if table.get("last_data_row", float("inf")) < table.get("first_data_row", 1):
        raise ConfigError(f"{location}.table row range is reversed")
    for key in ("summary_columns", "summary_labels"):
        if key in table:
            _strings(table[key], f"{location}.table.{key}")
    for key in ("reconciliation_date_column", "source_mode"):
        if key in data:
            _text(data[key], f"{location}.{key}")
    if "reconciliation_contract_confirmed" in data and type(data["reconciliation_contract_confirmed"]) is not bool:
        raise ConfigError(f"{location}.reconciliation_contract_confirmed must be boolean")
    reno = _mapping(data.get("timecard", {}), f"{location}.timecard")
    for key, choices in {"date_input": ("DMY", "MDY", "YMD", "auto"),
                         "decimal_separator": (".", ","),
                         "blank_hours": ("error", "zero")}.items():
        if key in reno and reno[key] not in choices:
            raise ConfigError(f"{location}.timecard.{key} must be one of {choices}")
    if "zero_tokens" in reno:
        _strings(reno["zero_tokens"], f"{location}.timecard.zero_tokens")
    for key, names in aliases.items():
        _text(key, f"{location}.columns.aliases key")
        _strings(names, f"{location}.columns.aliases.{key}")
    output = _mapping(data.get("output", {}), f"{location}.output")
    if output.get("format", "xlsx") not in ("xlsx", "csv"):
        raise ConfigError(f"{location}: output format must be xlsx or csv")
    for key in ("sheet", "date_format"):
        if key in output:
            _text(output[key], f"{location}.output.{key}")
    if "columns" in output:
        _strings(output["columns"], f"{location}.output.columns")
    if "header_scan_rows" in data:
        count = data["header_scan_rows"]
        if type(count) is not int or count <= 0:
            raise ConfigError(f"{location}.header_scan_rows must be a positive integer")
    for key in ("skip_summary_rows", "external_refresh"):
        if key in data and type(data[key]) is not bool:
            raise ConfigError(f"{location}.{key} must be a boolean")
    if "time_to_hours" in data:
        _strings(data["time_to_hours"], f"{location}.time_to_hours")
    for key in ("description", "date_continuity_column", "source_schema_status"):
        if key in data:
            _text(data[key], f"{location}.{key}")
    for rule in _rules(data, "dates", location):
        _text(rule.get("column"), f"{location}.dates.column")
        if rule.get("input", "auto") not in ("auto", "DMY", "MDY", "YMD"):
            raise ConfigError(f"{location}.dates.input must be auto, DMY, MDY or YMD")
        for key in ("excel_format", "split_delimiter"):
            if key in rule:
                _text(rule[key], f"{location}.dates.{key}")
    for rule in _rules(data, "exclude_rows", location):
        _text(rule.get("column"), f"{location}.exclude_rows.column")
        if not any(key in rule for key in ("equals", "contains", "in", "cost_center_code")):
            raise ConfigError(f"{location}.exclude_rows needs equals, contains or in")
        if "in" in rule and not isinstance(rule["in"], list):
            raise ConfigError(f"{location}.exclude_rows.in must be a list")
        for key in ("contains", "expect_label_contains"):
            if key in rule:
                _text(rule[key], f"{location}.exclude_rows.{key}")
        for key in ("cost_center_code", "expect_label"):
            if key in rule:
                _text(rule[key], f"{location}.exclude_rows.{key}")
        if "cost_center_code" in rule and not rule["cost_center_code"].isdigit():
            raise ConfigError(f"{location}.cost_center_code must contain only digits")
    for rule in _rules(data, "manual_review", location):
        _text(rule.get("column"), f"{location}.manual_review.column")
        if "equals" not in rule:
            raise ConfigError(f"{location}.manual_review needs equals")
        if "message" in rule:
            _text(rule["message"], f"{location}.manual_review.message")
    for rule in _rules(data, "cross_field_sums", location):
        _strings(rule.get("parts"), f"{location}.cross_field_sums.parts")
        _text(rule.get("total"), f"{location}.cross_field_sums.total")
        tolerance = rule.get("tolerance", 0.02)
        if (type(tolerance) not in (int, float) or not math.isfinite(tolerance)
                or tolerance < 0):
            raise ConfigError(f"{location}.cross_field_sums.tolerance must be finite and nonnegative")
    for rule in _rules(data, "reconciliation", location):
        _text(rule.get("name"), f"{location}.reconciliation.name")
        _text(rule.get("column"), f"{location}.reconciliation.column")
        for filt in _rules(rule, "filters", f"{location}.reconciliation"):
            _text(filt.get("column"), f"{location}.reconciliation.filters.column")
            if not any(key in filt for key in ("in", "not_in", "contains_any", "cost_center_in")):
                raise ConfigError(f"{location}.reconciliation.filters needs a supported operator")
            for key in ("in", "not_in", "contains_any", "cost_center_in"):
                if key in filt and not isinstance(filt[key], list):
                    raise ConfigError(f"{location}.reconciliation.filters.{key} must be a list")
            if "cost_center_in" in filt:
                import re
                _strings(filt["cost_center_in"], f"{location}.cost_center_in")
                if any(not re.fullmatch(r"\s*\d+\s*>\s*\S.*", s) for s in filt["cost_center_in"]):
                    raise ConfigError(f"{location}.cost_center_in needs code > label entries")
    if data.get("reconciliation_date_column") and data["reconciliation_date_column"] not in {
        rule["column"] for rule in data.get("dates", [])
    }:
        raise ConfigError(f"{location}.reconciliation_date_column needs a declared date transform")
    if data.get("processor") == "jz":
        if data.get("source_mode", "staging") not in ("staging", "raw_cells"):
            raise ConfigError(f"{location}.source_mode must be staging or raw_cells")
        mappings = _mapping(data.get("category_mapping"), f"{location}.category_mapping")
        if not mappings or not output.get("columns"):
            raise ConfigError(f"{location}: jz needs category_mapping and output.columns")
        for category, spec in mappings.items():
            _text(category, f"{location}.category_mapping key")
            _mapping(spec, f"{location}.category_mapping.{category}")
            for key in ("segment", "plant", "plant_name", "profit_center", "company_code"):
                if not isinstance(spec.get(key), (str, int)) or isinstance(spec.get(key), bool):
                    raise ConfigError(f"{location}.category_mapping.{category}.{key} is required")
        if data.get("source_mode") == "raw_cells":
            import re
            raw = _mapping(data.get("raw_source"), f"{location}.raw_source")
            for key in ("sheet", "approval", "week_ending_cell"):
                _text(raw.get(key), f"{location}.raw_source.{key}")
            if raw.get("date_input") not in ("DMY", "MDY", "YMD"):
                raise ConfigError(f"{location}.raw_source.date_input must be explicit")
            cells = _mapping(raw.get("categories"), f"{location}.raw_source.categories")
            if cells.keys() != mappings.keys():
                raise ConfigError(f"{location}.raw_source must map exactly all categories")
            addresses = [raw["week_ending_cell"]]
            for category, item in cells.items():
                _mapping(item, f"{location}.raw_source.{category}")
                for key in ("label_cell", "paid_cell", "ot_cell"):
                    _text(item.get(key), f"{location}.raw_source.{category}.{key}")
                    addresses.append(item[key])
            if any(not re.fullmatch(r"[A-Z]{1,3}[1-9][0-9]*", a) for a in addresses):
                raise ConfigError(f"{location}.raw_source requires A1 cell addresses")
            if len(addresses) != len(set(addresses)):
                raise ConfigError(f"{location}.raw_source cell addresses must be distinct")


def profiles_directory() -> Path:
    # Development editable install and wheel installations both contain profiles.
    embedded = Path(__file__).parent / "profiles"
    return embedded if embedded.is_dir() else Path(__file__).resolve().parents[2] / "config/profiles"


def load_profile(name: str, config_dir: Path | None = None) -> dict[str, Any]:
    root = config_dir or profiles_directory()
    if not name.replace("_", "").replace("-", "").isalnum():
        raise ConfigError("Profile may only contain letters, digits, hyphens and underscores")
    path = root / f"{name}.yaml"
    if not path.is_file():
        raise ConfigError(f"Unknown profile '{name}'. Available: {', '.join(available_profiles(root))}")
    data = _read_yaml(path)
    if not isinstance(data, dict) or data.get("id") != name:
        raise ConfigError(f"{path}: profile must be a mapping with id: {name}")
    if data.get("processor", "tabular") not in ("tabular", "reno", "jz"):
        raise ConfigError(f"{path}: unknown processor '{data.get('processor')}'")
    _validate_structure(data, str(path))
    return data


def available_profiles(root: Path | None = None) -> list[str]:
    return sorted(p.stem for p in (root or profiles_directory()).glob("*.yaml"))


def load_overrides(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    content = _read_yaml(path)
    if not isinstance(content, dict) or not isinstance(content.get("corrections", []), list):
        raise ConfigError("Overrides must be YAML mapping containing a corrections list")
    if "source_evidence" in content:
        import re
        from datetime import datetime
        evidence = _mapping(content["source_evidence"], f"{path}.source_evidence")
        for key in ("sha256", "refreshed_at", "approved_by"):
            _text(evidence.get(key), f"{path}.source_evidence.{key}")
        if not re.fullmatch(r"[a-fA-F0-9]{64}", evidence["sha256"]):
            raise ConfigError("source_evidence.sha256 must be a SHA-256 hex digest")
        try:
            refreshed = datetime.fromisoformat(evidence["refreshed_at"])
            if refreshed.tzinfo is None:
                raise ValueError("timezone missing")
        except ValueError as exc:
            raise ConfigError("source_evidence.refreshed_at needs an ISO timestamp with timezone") from exc
    for fix in _rules(content, "corrections", str(path)):
        for key in ("profile", "column"):
            _text(fix.get(key), f"{path}.corrections.{key}")
        if not _mapping(fix.get("match"), f"{path}.corrections.match"):
            raise ConfigError(f"{path}.corrections.match must not be empty")
        if not {"expected_old", "new_value"} <= fix.keys():
            raise ConfigError(f"{path}.corrections needs expected_old and new_value")
    return content
