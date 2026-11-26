# Current state / agent resume checkpoint

**2026-11-26 CCB presentation fix:** [EP-0008](../exec-plans/completed/EP-0008-ccb-excel-formatting.md) completed. Four hours columns now use Number `0.00`, static Row Labels fills survive cleanup, and full-table AutoFilter is enabled with no active criteria. Full suite: **540 passed in 21.27s**; Ruff PASS. Local user output regenerated: 2676 data rows unchanged, 11 RGB fills preserved, source hash unchanged. This local check is not destination certification; Excel UI was not exercised.

**2026-11-26 implementation checkpoint:** [EP-0007](../exec-plans/active/EP-0007-manual-parsing-corrections.md) engineering safeguards are implemented across all ten workflows, with mirrored YAMLs and updated process pages. Added explicit duration units, Reno DMY/comma/status/date guards, audited table boundaries, numeric metric validation, weekly diagnostics, exact Dayforce code matching and required hash-bound refresh attestations, correction revalidation, expected-week Taiwan continuity, approved-cell JZ extraction and combined US/CBG audit command. Real contracts remain open; no actual HC mapping or missing Core department filter is invented.

**Latest checks:** `uv run --offline pytest -q` — **535 passed in 24.28s**; `uv run --offline ruff check src tests` — **PASS** (TD-017 closed; touched CLI options migrated to Annotated and legacy imports cleaned). Workspace-local UV cache used. Documentation checker PASS (56 Markdown files / 10 mirrored profiles); executable build and standalone synthetic smoke PASS. Exact commands are in the execution log; historical results below remain dated.

**Snapshot:** 2026-11-26; `factoryprep` version `0.1.0` as found in project archive. **Assurance:** functional synthetic-test coverage, **not** real-world destination certification.

## Implemented and verified locally

- Python package with uv-compatible `pyproject.toml`; Typer CLI: `profiles`, `detect`, `describe`, `prepare`, `validate`, `batch`, `drop`, `reconcile`.
- Windows one-file console build: `scripts/build_exe.ps1`, `factoryprep.spec`; embedded YAMLs and shared launcher. Bare file paths route to sequential file drops with fresh result folders. See [Windows operations](../OPERATIONS.md#windows-executable-and-drag-and-drop).
- 10 YAML profiles: `sgp`, `gbr`, `cbg_core`, `cbg_starline`, `ccb`, `reno`, `jz`, `dayforce_ccb`, `dayforce_non_ccb`, `taiwan`.
- Three processors (`tabular` for 8, `reno`, `jz`); report severity and output gate; optional header reference and reviewed corrections.
- Repository `.gitignore` excludes Python bytecode caches (`__pycache__/`, `*.py[cod]`); verified with `git check-ignore` on 2026-11-24.
- `uv run pytest -q` after restoring Reno/Taiwan on 2026-11-25: **487 passed in 37.29 seconds**, including restored profile tests, Taiwan CSV round trips and per-field failures, and the newer executable/drop tests. The named-column matrix covers nine profiles; Reno has a dedicated timecard test. See [test matrix](../quality/TEST_STRATEGY.md).
- Config/correction structures now fail with `ConfigError`; malformed profile structures are tested before source parsing. Full semantic preflight remains TD-002. CSV header delimiter fallback and invalid Excel ZIP reporting have regression tests.
- `uv run python scripts/check_docs.py`: **PASS**, 54 Markdown files / 10 mirrored profiles after restoration (2026-11-25).
- `uv run ruff check src tests`: **failed**, 64 legacy findings including three in the restored Reno code (TD-017). Scoped Ruff check of the new launcher, drop adapter, executable tests and smoke script: **PASS**; older CLI lint remains.
- Before restoration, `scripts/build_exe.ps1`: **PASS** on Windows 11 x64 with PyInstaller 6.22.3; standalone-copy smoke **PASS**, including all eight embedded profiles, prepare/validate, repeated multi-file bare paths, reports, failure exit codes and source preservation. See [EP-0005](../exec-plans/completed/EP-0005-windows-executable.md).
- Restored Reno and Taiwan by reverting `68db23f` in `8a9a0ad`; preserved existing uncommitted executable/validation work and Python/build ignore rules. The 2026-11-26 executable rebuild now includes all ten profiles; standalone synthetic smoke passed. Current verification is recorded in the execution log.
- Harness documentation assembled from the uploaded manual and source inspected on 2026-11-23; see [execution log](EXECUTION_LOG.md) for checker result.

## Not implemented / unverified

- No BW loading, DTP/ADSO operations, email/PBI or external Excel refresh. Intentionally excluded.
- Actual JZ HC layout/Paid–OT contract is still missing. Default staging remains; approved custom raw_cells extraction is supported without a shipped HC map.
- Real destination header/types/templates for most processes; some manual labels and dates ambiguous.
- `git ls-files uv.lock` confirms a tracked lockfile; updated 2026-11-25 for the optional PyInstaller build dependencies. Windows executable verification is synthetic; no clean receiving-PC or manual Explorer gesture certification is claimed.
- No input-source/business signoff or operational pipeline history; data quality reports are per-run only.

## Next 2 actions

1. [EP-0001](../exec-plans/active/EP-0001-source-contract-certification.md): get sanitized raw files + approved target template; resolve JZ, GBR, CBG and Taiwan rules.
2. [EP-0002](../exec-plans/active/EP-0002-harness-guardrails.md): grow mechanical config/type/dependency checks; execute docs checker each change.

## Where to read next

[Process index](../processes/index.md) → one file, [architecture](../../ARCHITECTURE.md), [tech debt](../exec-plans/tech-debt-tracker.md). Updated state must include exact command evidence and limitations, not guessed progress.
