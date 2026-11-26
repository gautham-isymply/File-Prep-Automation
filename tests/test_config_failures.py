"""Config failures must be actionable and occur before any source parsing."""
from copy import deepcopy

import pytest
import yaml

from factoryprep.config import ConfigError, available_profiles, load_overrides, load_profile
from factoryprep.engine import run


@pytest.fixture
def write_config(tmp_path):
    def write(data):
        (tmp_path / "sgp.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
        return tmp_path
    return write


@pytest.mark.parametrize("name", ["../sgp", "sgp/other", "", "sgp.yaml", r"..\sgp"])
def test_profile_name_cannot_escape_config_directory(name):
    with pytest.raises(ConfigError, match="Profile may only"):
        load_profile(name)


def test_unknown_profile_lists_available_names(tmp_path):
    with pytest.raises(ConfigError, match="Unknown profile"):
        load_profile("missing", tmp_path)


@pytest.mark.parametrize("data", [None, [], "sgp", {"id": "other"}])
def test_profile_requires_mapping_and_matching_identity(data, write_config):
    with pytest.raises(ConfigError, match="mapping with id: sgp"):
        load_profile("sgp", write_config(data))


BAD_FIELDS = [
    ("processor", "unknown"), ("processor", []),
    ("output", None), ("output.format", "xls"), ("output.format", []),
    ("output.sheet", 42), ("output.columns", "DATE"), ("output.date_format", ""),
    ("columns", []), ("columns.aliases", []), ("columns.aliases.DATE", "Work Date"),
    ("dates", {}), ("dates", [None]), ("dates", [{}]),
    ("dates", [{"column": "DATE", "input": "guess"}]),
    ("dates", [{"column": "DATE", "excel_format": 123}]),
    ("dates", [{"column": "DATE", "split_delimiter": ""}]),
    ("time_to_hours", "NORM"), ("header_scan_rows", 0), ("header_scan_rows", -1),
    ("header_scan_rows", True), ("header_scan_rows", 2.5),
    ("skip_summary_rows", "false"), ("external_refresh", 1),
    ("description", []), ("date_continuity_column", []), ("source_schema_status", []),
    ("exclude_rows", [{}]), ("exclude_rows", [{"column": "CC"}]),
    ("exclude_rows", [{"column": "CC", "in": "1000"}]),
    ("exclude_rows", [{"column": "CC", "contains": "1000", "expect_label_contains": []}]),
    ("manual_review", [{}]), ("manual_review", [{"column": "NORM"}]),
    ("cross_field_sums", [{"parts": "NORM", "total": "OT"}]),
    ("cross_field_sums", [{"parts": ["NORM"], "total": "OT", "tolerance": -1}]),
    ("cross_field_sums", [{"parts": ["NORM"], "total": "OT", "tolerance": "0.1"}]),
    ("cross_field_sums", [{"parts": ["NORM"], "total": "OT", "tolerance": float("nan")}]),
    ("reconciliation", [{}]),
    ("reconciliation", [{"name": "sum", "column": "NORM", "filters": "bad"}]),
    ("reconciliation", [{"name": "sum", "column": "NORM", "filters": [{}]}]),
    ("reconciliation", [{"name": "sum", "column": "NORM", "filters": [
        {"column": "CC", "equals": "1000"}]}]),
]
BAD_FIELDS += [(f"columns.{key}", "NORM") for key in (
    "required", "drop", "expected", "numeric", "negative_forbidden", "non_null", "duplicate_keys"
)]
BAD_FIELDS += [(f"columns.{key}", [None]) for key in (
    "required", "drop", "expected", "numeric", "negative_forbidden", "non_null", "duplicate_keys"
)]
BAD_FIELDS += [("reconciliation", [{"name": "sum", "column": "NORM", "filters": [
    {"column": "CC", key: "1000"}]}]) for key in ("in", "not_in", "contains_any")]


@pytest.mark.parametrize("field,value", BAD_FIELDS)
def test_invalid_profile_structure_fails_before_source_read(
    field, value, write_config, tmp_path, monkeypatch,
):
    spec = deepcopy(load_profile("sgp"))
    parts = field.split(".")
    destination = spec
    for part in parts[:-1]:
        destination = destination[part]
    destination[parts[-1]] = value
    root = write_config(spec)

    def forbidden_read(*args):
        pytest.fail("Malformed profile reached source reader")

    monkeypatch.setattr("factoryprep.engine.read_book", forbidden_read)
    with pytest.raises(ConfigError):
        run("sgp", tmp_path / "never_open.xlsx", config_dir=root)


@pytest.mark.parametrize("change", ["mapping", "entry", "field", "output"])
def test_jz_requires_mapping_shape_and_output_columns(change, tmp_path):
    spec = load_profile("jz")
    if change == "mapping":
        spec["category_mapping"] = None
    elif change == "entry":
        spec["category_mapping"][next(iter(spec["category_mapping"]))] = []
    elif change == "field":
        del spec["category_mapping"][next(iter(spec["category_mapping"]))]["profit_center"]
    else:
        del spec["output"]["columns"]
    (tmp_path / "jz.yaml").write_text(yaml.safe_dump(spec), encoding="utf-8")
    with pytest.raises(ConfigError):
        load_profile("jz", tmp_path)


@pytest.mark.parametrize("kind", ["profile", "overrides"])
def test_invalid_yaml_is_config_error(kind, tmp_path):
    path = tmp_path / "sgp.yaml"
    path.write_text("id: [unterminated", encoding="utf-8")
    with pytest.raises(ConfigError, match="invalid YAML"):
        load_profile("sgp", tmp_path) if kind == "profile" else load_overrides(path)


@pytest.mark.parametrize("data", [
    None, [], {"corrections": {}}, {"corrections": [None]},
    {"corrections": [{}]},
    {"corrections": [{"profile": "ccb", "column": "NORM", "match": {}}]},
    {"corrections": [{"profile": "ccb", "column": "NORM", "match": {"Dept": "1"}}]},
])
def test_malformed_override_files_are_rejected(data, tmp_path):
    path = tmp_path / "overrides.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ConfigError):
        load_overrides(path)


@pytest.mark.parametrize("profile", available_profiles())
def test_bundled_profiles_pass_structural_validation(profile):
    assert load_profile(profile)["id"] == profile


def test_optional_defaults_and_extension_keys_remain_supported(write_config):
    spec = {"id": "sgp", "custom_metadata": {"owner": "test"}}
    assert load_profile("sgp", write_config(spec)) == spec
    assert load_overrides(None) == {}
