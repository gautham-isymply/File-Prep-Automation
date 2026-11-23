"""Verify repository-local harness documentation integrity; stdlib only."""
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
MANDATORY = ["AGENTS.md", "ARCHITECTURE.md", "docs/index.md", "docs/DESIGN.md",
             "docs/PLANS.md", "docs/progress/CURRENT_STATE.md",
             "docs/exec-plans/tech-debt-tracker.md", "docs/processes/index.md"]


def check() -> list[str]:
    errors: list[str] = []
    for name in MANDATORY:
        if not (ROOT / name).is_file():
            errors.append(f"MISSING_REQUIRED_DOC {name}")
    docs = sorted(list(ROOT.glob("*.md")) + list((ROOT / "docs").rglob("*.md")))
    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        for url in LINK.findall(text):
            target = url.split("#", 1)[0].split("?", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not (doc.parent / target).exists():
                errors.append(f"BROKEN_LINK {doc.relative_to(ROOT)} -> {url}")
    profile_root = ROOT / "config" / "profiles"
    embedded_root = ROOT / "src" / "factoryprep" / "profiles"
    originals = {p.stem: p for p in profile_root.glob("*.yaml")}
    embedded = {p.stem: p for p in embedded_root.glob("*.yaml")}
    if originals.keys() != embedded.keys():
        errors.append(f"PROFILE_SET_MISMATCH original={sorted(originals)} embedded={sorted(embedded)}")
    process_index = (ROOT / "docs" / "processes" / "index.md")
    index_text = process_index.read_text(encoding="utf-8") if process_index.exists() else ""
    for profile, source in originals.items():
        page = ROOT / "docs" / "processes" / f"{profile}.md"
        if not page.exists():
            errors.append(f"MISSING_PROCESS_DOC {profile}")
        if f"({profile}.md)" not in index_text:
            errors.append(f"MISSING_PROCESS_INDEX_LINK {profile}")
        if profile in embedded and source.read_bytes() != embedded[profile].read_bytes():
            errors.append(f"PROFILE_MIRROR_DRIFT {profile}")
    agents = ROOT / "AGENTS.md"
    if agents.exists() and len(agents.read_text(encoding="utf-8").splitlines()) > 100:
        errors.append("ENTRYPOINT_TOO_LONG AGENTS.md exceeds 100 lines")
    print(f"Documentation check: {len(docs)} Markdown files, {len(originals)} profiles")
    if errors:
        for error in errors:
            print(f"ERROR {error}")
    else:
        print("PASS local links, required docs, profile runbooks, YAML copies, entrypoint size")
    return errors


if __name__ == "__main__":
    sys.exit(1 if check() else 0)
