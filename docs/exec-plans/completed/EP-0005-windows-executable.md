# EP-0005 — Windows executable and file drops

## Objective

Operators can build a standalone console EXE, run existing CLI commands, and drop
one or more source files onto it without installing Python on the receiving PC.

## Baseline and scope

Existing Typer commands and processing rules stay authoritative. Packaging and a
file-drop adapter are added; no integrations or profile semantics change.

## Current repository facts

Profiles are loaded relative to `config.py`; PyInstaller must bundle all eight YAMLs
under `factoryprep/profiles`. Existing working-tree edits predate this task.

## Unknowns and human decisions

Real input/destination certification remains outside this change. The manual Explorer
gesture and console lifetime on a receiving PC remain unverified; subprocess checks
cover the same file arguments, and unit tests cover pause ownership including the
one-file bootloader parent. Manual desktop checks are follow-up operational validation.

## Milestones / Progress

- [x] Add console launcher, drop adapter, spec and build script.
- [x] Verify adapter behavior and build actual Windows executable.
- [x] Run required checks, record evidence and operator instructions.

## Step-by-step design

Use `uv sync --extra build --extra dev` and PyInstaller's one-file spec. Route bare
file paths to `drop`; retain named CLI commands. Detect profiles conservatively.
Create a unique sibling result folder for each source; continue other files after
a failure and return 2 if any fail. Pause only when the frozen process owns its console.

## Verification and acceptance

Unit/integration tests cover multiple paths with spaces, source preservation,
ambiguous detection, mixed success/failure, and launcher dispatch. Build on Windows;
smoke the copied standalone EXE outside the repository with profiles, help, explicit
prepare, bare paths and failed input. Run pytest, docs checker and Ruff.

## Evidence / execution log

2026-11-25: inspected CLI, engine, configuration resource lookup and current state.
2026-11-25: `scripts/build_exe.ps1` succeeded on Windows 11 x64 / Python 3.13.6 /
PyInstaller 6.22.3; `dist/factoryprep.exe` is 17,820,006 bytes. Its standalone-copy
smoke check passed help, all eight embedded profile descriptions, prepare, validate,
repeated multi-file bare paths, mixed failures, reports and source preservation.
`uv run pytest -q`: 449 passed in 37.36s. Full Ruff: 61 pre-existing findings,
TD-017; scoped Ruff of launcher, drop adapter, executable tests and smoke script passed.
Documentation and whitespace checks are recorded in the execution log.

## Decisions

Use a console executable for CLI compatibility. File drops use auto detection and
fresh directories; explicit CLI options resolve ambiguous inputs. Per-profile YAMLs
and business rules are unchanged.

## Risks / rollback

Builds are platform-specific; Windows must build the EXE. No production certification
is claimed. Remove packaging/adapter changes to return to the prior CLI.

## Next step

Complete for synthetic packaging acceptance. Optionally validate Explorer gestures
and console presentation on a receiving PC before operational rollout.
