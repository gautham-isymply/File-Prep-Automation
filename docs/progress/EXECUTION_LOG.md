# Execution and verification log

Logs are append-only summaries of work performed locally. **Not** actual plant file-load runs. Report concrete commands/results; include failures and any environment limits.

## 2026-11-23 — original v0.1.0 baseline inspection

- Inspected uploaded `FactoryPrep_CLI_v0.1.0.zip`, local Python modules, two mirrored sets of ten YAML profiles, and factory manual (39 pages).
- Ran `cd /mnt/data/factoryprep_project && PYTHONPATH=src pytest -q --disable-warnings --maxfail=1` → `19 passed in 0.63s` (exit 0).
- Verified app code has no SAP BW integration. Confirmed `jz` accepts staged `{Category, Paid Hours, OT Hours}`, not arbitrary raw HC workbook.
- Identified unresolved manual specification gaps and encoded them as TD-001 through TD-016. This record does not imply validation against real employee-hours files.

## 2026-11-23 — harness documentation addition

- Added small `AGENTS.md`, architecture and design routing, 10 per-profile runbooks + per-business-unit JZ guidance, plans, ADRs, debt ledger, quality score, current state, security/reliability and source evidence map.
- Added a local documentation integrity check at `scripts/check_docs.py` to detect broken Markdown links, missing runbook coverage and mismatched package/development profile copies.
- **Verification:** results are recorded below by packaging check script (do not claim CI integration).

## 2026-11-23 — verification of the packaged working tree

- Ran `cd /mnt/data/factoryprep_harness && PYTHONPATH=src pytest -q --disable-warnings --maxfail=1` → `19 passed in 1.00s` (exit 0).
- Ran `cd /mnt/data/factoryprep_harness && python scripts/check_docs.py` → `Documentation check: 51 Markdown files, 10 profiles` and `PASS local links, required docs, profile runbooks, YAML copies, entrypoint size` (exit 0).
- Tried `ruff check src tests` → **not executed**, shell reported `ruff: command not found`. Ruff quality gate remains unverified; use `uv sync --extra dev` in an environment with package-registry access, then rerun.
- No actual employee/source workbook or approved destination schema was available for certification. The user-provided manual is **not** distributed in this zip.

## 2026-11-24 — supported workflow scope reduced

- Removed two retired workflows: dedicated processor and date-header detector, mirrored YAML files, dedicated tests, runbooks, batch example, manual evidence and shared documentation details. Retained eight profiles and generic file-format/validation helpers. Source workbooks were untouched.
- User-requested detail removal also applies to prior ADR prose; [ADR-0006](../decisions/ADR-0006-supported-scope.md) records the explicit scope change. Dated historical command evidence above remains historical.
- Initial `uv run pytest -q` and Ruff attempts could not spawn missing executables. Initial `uv sync --extra dev` failed on DNS; authorized network retry installed pytest 9.2.0 and Ruff 0.17.6. Commands used `UV_CACHE_DIR=.uv-cache` because the default sandbox cache was inaccessible. The shell's `python` alias was unavailable; the existing `.venv/Scripts/python.exe` worked.
- `uv run pytest -q`: **17 passed in 2.81s**, exit 0.
- `uv run python scripts/check_docs.py`: **PASS**, 51 Markdown files, 8 profiles; local links, runbooks, YAML mirror equality, entrypoint size verified.
- `uv run factoryprep profiles`: exit 0; exactly eight retained profiles listed.
- `uv run ruff check src tests --output-format concise`: exit 1, **66 findings**. Compared Ruff JSON diagnostics from each retained file against `git show HEAD:<path>` using UTF-8 stdin: original = 66, current = 66, new = 0. Existing lint debt tracked as TD-017; no unrelated lint refactor included.
- Case-insensitive repository text audit for retired workflow names: zero matches. `git diff --check`: exit 0.
- Scope removal is complete; real source/destination certification remains unverified. See [EP-0003](../exec-plans/completed/EP-0003-workflow-scope.md).

## 2026-11-24 — ignore Python bytecode caches

- Added root `.gitignore` entries `__pycache__/` and `*.py[cod]`; no cache files were tracked. `git check-ignore` confirmed all three existing cache directories and a sample `.pyc` path are ignored.
- `uv run pytest -q`: 17 passed in 1.84s. `uv run python scripts/check_docs.py`: PASS, 51 Markdown files / 8 profiles. `uv run ruff check src tests --output-format concise --statistics`: exit 1, unchanged 66 existing findings (TD-017).
