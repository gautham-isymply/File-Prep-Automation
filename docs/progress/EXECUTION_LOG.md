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
- User-requested detail removal also applies to prior ADR prose; `ADR-0006` (removed when the scope-reduction commit was reverted) records the explicit scope change. Dated historical command evidence above remains historical.
- Initial `uv run pytest -q` and Ruff attempts could not spawn missing executables. Initial `uv sync --extra dev` failed on DNS; authorized network retry installed pytest 9.2.0 and Ruff 0.17.6. Commands used `UV_CACHE_DIR=.uv-cache` because the default sandbox cache was inaccessible. The shell's `python` alias was unavailable; the existing `.venv/Scripts/python.exe` worked.
- `uv run pytest -q`: **17 passed in 2.81s**, exit 0.
- `uv run python scripts/check_docs.py`: **PASS**, 51 Markdown files, 8 profiles; local links, runbooks, YAML mirror equality, entrypoint size verified.
- `uv run factoryprep profiles`: exit 0; exactly eight retained profiles listed.
- `uv run ruff check src tests --output-format concise`: exit 1, **66 findings**. Compared Ruff JSON diagnostics from each retained file against `git show HEAD:<path>` using UTF-8 stdin: original = 66, current = 66, new = 0. Existing lint debt tracked as TD-017; no unrelated lint refactor included.
- Case-insensitive repository text audit for retired workflow names: zero matches. `git diff --check`: exit 0.
- Scope removal is complete; real source/destination certification remains unverified. See `EP-0003` (removed when the scope-reduction commit was reverted).

## 2026-11-24 — ignore Python bytecode caches

- Added root `.gitignore` entries `__pycache__/` and `*.py[cod]`; no cache files were tracked. `git check-ignore` confirmed all three existing cache directories and a sample `.pyc` path are ignored.
- `uv run pytest -q`: 17 passed in 1.84s. `uv run python scripts/check_docs.py`: PASS, 51 Markdown files / 8 profiles. `uv run ruff check src tests --output-format concise --statistics`: exit 1, unchanged 66 existing findings (TD-017).

## 2026-11-25 — preparation and failure regression matrix

- Completed [EP-0004](../exec-plans/completed/EP-0004-validation-coverage.md). Added 418 synthetic cases (435 total) covering every profile with XLSX/XLSM/CSV/TSV and canonical/alias headers, each required header and numeric/date failure, profile operations and diagnostic totals, JZ mapping, correction safety, destination references, strict/validate gates, source/output integrity, write-failure cleanup, CLI exits and batch continuation.
- Malformed supported profile/correction structures and YAML now raise `ConfigError`; profile structure failures are tested before source parsing. Full semantic schema remains TD-002/EP-0002. Unknown extension keys are intentionally retained.
- Fixed quoted semicolon/pipe CSV fallback using header sniffing; invalid Excel ZIP containers now become audited preparation failures. All eight profile YAML files remain unchanged and byte-identical to embedded copies.
- `uv run pytest -q`: **435 passed in 19.67s**, exit 0. Earlier runs: 272 passed / 9 fixture failures, then 381 passed / 2 CSV regression failures; fixture construction and delimiter fallback were corrected before final verification.
- `uv run python scripts/check_docs.py`: **PASS**, 52 Markdown files / 8 profiles, exit 0.
- `uv run ruff check src tests`: exit 1, **63 findings in unchanged files**, down from 66. Scoped check of `config.py`, `io.py` and all four new test modules: **All checks passed**, exit 0. Existing TD-017 remains open; no unrelated lint refactor performed.
- `git diff --check`: exit 0. Commands used `UV_CACHE_DIR=.venv/uv-cache` after default sandbox cache access was denied; no escalation was needed.
- Source fixtures are synthetic temporary files; XLSM tests use macro-free workbook containers and do not certify VBA handling. No production/source/destination signoff claimed. The [test strategy](../quality/TEST_STRATEGY.md) maps processing steps to tests and records remaining assurance limits.
## 2026-11-25 — Windows executable and drag-and-drop

- Added a one-file console spec, optional build dependencies and Windows build script;
  updated tracked `uv.lock`. Shared launcher preserves CLI commands, routes bare file
  paths to `drop`, and holds an Explorer-owned console open, accounting for the
  one-file bootloader parent. Per-profile processing rules/YAMLs are unchanged.
- Drop adapter uses conservative detection, fresh sibling result folders, sequential
  processing and aggregate exit 2 on any failure. Sources and prior results are preserved.
- `scripts/build_exe.ps1`: exit 0 on Windows 11 x64 / Python 3.13.6 / PyInstaller 6.22.3;
  built `dist/factoryprep.exe` (17,820,006 bytes). Included standalone-copy smoke passed
  help, eight profile descriptions, explicit prepare/validate, repeated bare multi-file
  paths with spaces, mixed failures, JSON reports and source preservation.
- `uv run pytest -q`: **449 passed in 37.36s**, exit 0.
- `uv run python scripts/check_docs.py`: **PASS**, 53 Markdown files / 8 mirrored
  profiles, exit 0. Final `git diff --check`: exit 0 after trimming added EOF blanks.
- `uv run ruff check src tests --output-format concise`: **61 pre-existing findings**,
  exit 1 (TD-017; down from 63 after CLI import cleanup). Scoped Ruff of launcher,
  drop adapter, executable tests and smoke script: **PASS**, exit 0.
- Dependency install initially hit default-cache permissions and sandbox DNS failure;
  a permitted network retry with `UV_CACHE_DIR=.uv-cache` succeeded. Build used a
  workspace `PYINSTALLER_CONFIG_DIR` and passed without further escalation.
- Synthetic packaging acceptance is complete in [EP-0005](../exec-plans/completed/EP-0005-windows-executable.md).
  Manual Explorer gesture, console presentation on a receiving PC and production
  source/destination certification remain unverified.

## 2026-11-25 — reverted workflow removal and merged ongoing work

- User requested restoration by reverting `68db23f`. Saved all ongoing work with `git stash push --include-untracked`; created clean revert commit `8a9a0ad`. Reapplied the stash and resolved nine conflicts in ignore rules, config, indexes, state/log and quality docs. Preserved newer structural guards, CSV parsing fixes, executable/drop work and tests. Safety stash retained; original work remains uncommitted.
- All 27 originally modified tracked paths and 12 originally new files are present. Before final evidence updates, comparison against the stash showed 24 files unchanged and 15 intentionally merged/adapted. Existing build/dist artifacts remain unchanged; they predate restoration and must be rebuilt to include the restored profiles.
- Restored both mirrored profile pairs, Reno processor/detection/dispatch, dedicated tests, runbooks, examples, manual evidence and Taiwan debt. Kept newer Python/build ignore rules. Historical removal evidence remains dated in this log, with deleted-record links converted to plain identifiers.
- Adapted the ongoing validation matrix to nine named-column profiles, Taiwan CSV date/numeric output, and per-profile output extensions; Reno keeps its dedicated timecard test. Original profile YAML and business rules are unchanged. Standalone smoke inventory now expects ten profiles on a future rebuild.
- Initial required test command hit build-dependency DNS restrictions; an authorized network retry built the editable package. First integration runs had 470 passes and 17 Taiwan fixture failures caused by XLSX output paths; fixture extensions were corrected without changing production behavior.
- Final `uv run pytest -q`: **487 passed in 37.29s**, exit 0. `uv run python scripts/check_docs.py`: **PASS**, 54 Markdown files / 10 profiles, exit 0. CLI `profiles`: ten profiles including Reno and Taiwan.
- `uv run ruff check src tests --output-format concise`: **64 legacy findings**, exit 1; 61 from the saved working tree plus three in the restored Reno source. TD-017 updated. No production certification or rebuilt executable claim.
- Conflict-marker scan and `git diff --check` passed. Git conflict index entries cleared and all ongoing changes returned to unstaged/untracked state. See [EP-0006](../exec-plans/completed/EP-0006-restore-workflows.md).

## 2026-11-26 — reviewed supplied manual and planned parsing corrections

- User requested every process and a correction plan. Read actual `FactoryInsights_MANUAL_LOAD_Process.docx` from Downloads using ZIP/XML without modifying it; hash and paragraph evidence are in [EP-0007](../exec-plans/active/EP-0007-manual-parsing-corrections.md). Inspected available embedded Reno, JZ and SSI screenshots. Document instructions were process evidence, not authorization for external actions.
- Added a ten-workflow plan with manual facts, code-derived behavior, unresolved decisions, proposed edits and acceptance checks. No runtime, profile or test changes. Preserved pre-existing working-tree changes. Linked plan/state/evidence map and added TD-018–021 for Reno locale/date/status risks, CBG boundaries/numeric metrics, Dayforce weekly diagnostics and missing Core evidence.
- Initial uv extraction failed on default-cache permissions; used existing `.venv/Scripts/python.exe` for extraction. A contact-sheet attempt found Pillow unavailable; inspected original images directly. Three Core relationships targeted absent image files. Temporary extracted screenshots removed after review.
- With workspace-local `UV_CACHE_DIR=.uv-cache`, `uv run --offline pytest -q`: **487 passed in 18.68s**, exit 0. Existing synthetic tests do not validate proposed corrections or real source contracts.
- `uv run --offline python scripts/check_docs.py`: **PASS**, 55 Markdown files / 10 mirrored profiles, exit 0.
- `uv run --offline ruff check src tests --output-format concise`: **64 findings**, exit 1, consistent with existing TD-017. No lint fixes included in this documentation task.
- Proposed implementation remains open under EP-0007; real-source certification remains under EP-0001. No production or external-load certification claimed.


## 2026-11-26 — implemented manual parsing corrections (EP-0007)

- Implemented the engineering safeguards for ten workflows, with byte-identical development/embedded profiles and updated per-process docs, profile/report contracts and operations. Existing user changes were preserved; no original source workbook or supplied DOCX was modified.
- GBR has explicit per-column duration units and blocking ambiguous unformatted fractions. Numeric parsing rejects nonfinite/ambiguous comma values; Reno declares DMY/comma encoding and requires explicit blank/status semantics, selected date coverage and daily evidence. Multiple candidate headers/weeks block ambiguous selection. No missing Saturday or hours are invented.
- Tabular cleanup now checks designated/first-column summaries, exact repeated headers and explicit worksheet bounds with a removal ledger. Core requires Pay Code/Hours/Units and parses hours; SSI blocks ambiguous slash dates. Selected metric values cannot be silently omitted. CCB replacement values are revalidated and all three Reg/OT components have weekly metrics. Taiwan checks requested-week boundary gaps and warns on duplicate dates without deletion.
- Weekly diagnostic predicates retain monthly data. Dayforce exact code/label matching replaces substring filters/exclusions; malformed exclusion labels block. Missing source-owner refresh attestation now blocks normal/strict mode; hashes bind attestations to export bytes. Python performs no refresh. Reports include source hashes/date ranges and row audit.
- Optional JZ raw_cells extraction requires a complete reviewed sheet/week/category/cell contract, distinct Paid/OT cells, matching labels/week and numeric validity; provenance recorded. Default remains provisional staging. No actual HC map or Paid/OT derivation is supplied. Core missing department filters remain explicitly unconfirmed. Combined US/CBG source-audit command validates successful matching-week, scoped and confirmed components; US also needs matching refresh evidence. ADR-0006 documents the boundary.
- New synthetic adversarial cases cover layout/date/units failures, exact labels, source evidence, correction revalidation, source/report protection, combined US/CBG totals and raw JZ invalid mappings/values. Intermediate runs exposed changed-contract expectations, two test source/output path collisions and missing value diagnostics under the new refresh gate; corrected these and reran the full suite. Synthetic expected values are not manufactured business approvals.
- Migrated touched CLI options to Annotated Typer options and cleaned legacy imports/style; boolean numeric rejection retains a blocking field issue. TD-017 now closes with full Ruff evidence. Other source-contract debt remains open/in-progress, not certified.
- With workspace-local `UV_CACHE_DIR=.uv-cache`: `uv run --offline pytest -q` — **535 passed in 24.28s**, exit 0; `uv run --offline ruff check src tests` — **PASS**, exit 0. Additional Ruff check including `scripts/smoke_exe.py` also passed.
- `uv run --offline python -m PyInstaller --noconfirm factoryprep.spec` with workspace-local `PYINSTALLER_CONFIG_DIR=build/pyinstaller-config` — **PASS**, exit 0 (Windows 11 x64, Python 3.13.6, PyInstaller 6.22.3). Rebuilt `dist/factoryprep.exe`; no dependency/network escalation required.
- `uv run --offline python scripts/smoke_exe.py dist/factoryprep.exe` — standalone-copy synthetic smoke **PASS**: ten profiles/descriptions, prepare/validate, repeated multi-file paths, failure reports and source preservation, GBR fraction gate, Reno DMY/comma hours, Dayforce required/hash-bound evidence and combined US audit.
- `uv run --offline python scripts/check_docs.py` — **PASS**, 56 Markdown files / 10 mirrored profiles. `git diff --check` — **PASS** (line-ending normalization notices only).
- EP-0007 remains active: M2 and synthetic packaging complete; M1/M3/M4 still require sanitized real files, missing Core filter evidence, actual JZ mappings, locale/unit/status/calendar decisions, approved destination schemas and source-owner acceptance under EP-0001. No production, receiving-PC UI gesture or downstream-load certification claimed.
