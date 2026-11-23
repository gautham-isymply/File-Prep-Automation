"""Configuration discovery and fail-fast config integrity validation."""
from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import Any
import yaml


class ConfigError(ValueError):
    pass


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
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("id") != name:
        raise ConfigError(f"{path}: profile must be a mapping with id: {name}")
    if data.get("processor", "tabular") not in {"tabular", "reno", "jz"}:
        raise ConfigError(f"{path}: unknown processor '{data.get('processor')}'")
    if data.get("output", {}).get("format", "xlsx") not in {"xlsx", "csv"}:
        raise ConfigError(f"{path}: output format must be xlsx or csv")
    columns = data.get("columns", {})
    for key in ("required", "drop", "expected", "numeric", "negative_forbidden"):
        if key in columns and not isinstance(columns[key], list):
            raise ConfigError(f"{path}: columns.{key} must be a list")
    return data


def available_profiles(root: Path | None = None) -> list[str]:
    return sorted(p.stem for p in (root or profiles_directory()).glob("*.yaml"))


def load_overrides(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    content = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(content, dict) or not isinstance(content.get("corrections", []), list):
        raise ConfigError("Overrides must be YAML mapping containing a corrections list")
    return content
