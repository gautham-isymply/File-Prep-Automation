# EP-0003 — reduce supported workflow scope

**State:** completed  
**Updated:** 2026-11-24  
**Owner:** unassigned

## Objective

Expose only eight supported profiles and remove the two retired workflows from source, configuration, tests, examples, and documentation.

## Baseline and scope

The starting tree has ten profiles and three processors. Remove workflow-specific material while preserving shared CSV, date parsing, validation, and reporting. Source workbooks remain read-only.

## Current repository facts

Profiles are mirrored in `config/profiles/` and `src/factoryprep/profiles/`. Dispatch lives in `engine.py`, detection in `detect.py`, and functional coverage in `tests/test_profiles.py`.

## Unknowns and human decisions

The user explicitly requested complete removal of the two workflows and their documentation. No business mappings are inferred. Historical ADR text containing retired details is edited for that request; ADR-0006 records the scope change.

## Milestones / Progress

- [x] M1 — inventory workflow-specific code, profiles, tests, and documentation.
- [x] M2 — remove implementation and details; reconcile inventories and references.
- [x] M3 — run required checks, audit remaining references, and record evidence.

## Step-by-step design

Delete the dedicated retired processor, both pairs of retired YAML profiles, and their runbooks. Remove dispatch/detection branches and dedicated tests. Update shared inventories, examples, contracts, active plans, and debt references. Preserve dated historical command evidence.

## Verification and acceptance

Run `uv run pytest -q`, `uv run python scripts/check_docs.py`, and `uv run ruff check src tests`. Confirm mirrored profile directories and CLI contain eight profiles and a case-insensitive repository search has no retired names. Record environment or pre-existing check failures honestly. Existing lint findings do not block the scope removal when the original-file comparison proves zero added findings; track them independently.

## Evidence / execution log

2026-11-24: inventory and removal completed. Tests: 17 passed in 2.81s. Docs checker: PASS, 51 Markdown files / 8 profiles. CLI: eight retained profiles. Retired-name text search: zero matches. Diff whitespace check: pass. Ruff: 66 pre-existing findings, zero additions compared with original retained files; TD-017. Initial dependency/cache failures and successful retry are recorded in the execution log.

## Decisions

2026-11-24: preserve shared file-format and validation primitives. See [ADR-0006](../../decisions/ADR-0006-supported-scope.md).

## Risks / rollback

Old manifests using retired profiles fail with the existing unknown-profile error. Version control can restore the prior scope; source workbooks are untouched.

## Next step

No scope-removal work remains. Continue source certification under EP-0001 and address TD-017 separately.
