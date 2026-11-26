# EP-0004 — verify preparation operations and failure gates

**State:** completed
**Updated:** 2026-11-25  
**Linked debt:** TD-002, TD-001  
**Owner:** unassigned

## Objective

Operators can run `uv run pytest -q` to exercise all eight profiles, supported file
containers, shared validation gates, and malformed configuration rejection.

## Baseline and scope

Baseline: 17 synthetic tests. Add deterministic synthetic regression tests and
structural configuration checks. No SAP BW, external refresh, or new numeric rules.

## Current repository facts

`engine.run` loads profiles before opening input. Seven profiles use `tabular`;
JZ adds category mapping. `config.load_profile` currently checks only a few fields.
Existing process runbooks describe manual steps separately from implementation.

## Unknowns and human decisions

Real source and destination contracts remain unverified (TD-001). Preserve current
GBR fraction handling, SSI date convention, and JZ staged paid/OT inputs.

## Milestones / Progress

- [x] M1 — inspect all profiles, processors, runbooks and existing tests.
- [x] M2 — add profile, operation, file, CLI and config failure coverage.
- [x] M3 — run required checks and document evidence and remaining gaps.

## Step-by-step design

Add parameterized tests for every profile's required fields, aliases, numeric/date
failures and output safety. Exercise parsing, metrics, corrections, templates,
strict/validate modes, batch continuation and reports. Reject malformed supported
config structures with `ConfigError` before parsing input. Keep both profile trees
unchanged and verify they match. Publish a test-to-operation matrix in the test strategy.

## Verification and acceptance

Run `uv run pytest -q`, `uv run python scripts/check_docs.py`, and
`uv run ruff check src tests`. Record actual results, including pre-existing lint
failures. No newly added test or changed config code should introduce lint findings.
Tests must assert output values/issues and source preservation, not just completion.

## Evidence / execution log

2026-11-25: inspected code and all eight process runbooks; no source fixtures supplied.

2026-11-25: `uv run pytest -q` → 435 passed in 19.67s; docs checker → PASS,
52 Markdown files / 8 mirrored profiles. Full Ruff → 63 findings in unchanged files;
all new/changed Python files pass scoped Ruff. `git diff --check` → exit 0.
Initial test failures exposed fixture mistakes (a source/output path collision and
a completely blank row), which were corrected. Semicolon/pipe quoted input failures
exposed a delimiter fallback bug; fixed with header sniff retry. Damaged Excel ZIP
containers now produce audited failures. All tests use temporary synthetic data.

## Decisions

2026-11-25: validate supported configuration structures without imposing new business
schemas or rejecting unknown extension keys; full semantic schema remains EP-0002.

## Risks / rollback

Previously malformed custom profiles may now fail earlier. Valid bundled YAML must
continue loading unchanged. Test fixtures remain temporary; source files stay read-only.

## Next step

Complete semantic config preflight under EP-0002 and obtain certified real-source
fixtures under EP-0001. This bounded coverage change is complete; those plans remain open.
