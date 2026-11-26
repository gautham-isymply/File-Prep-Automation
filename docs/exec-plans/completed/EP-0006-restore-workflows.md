# EP-0006 — restore Reno and Taiwan while preserving ongoing work

**State:** completed
**Updated:** 2026-11-25
**Owner:** unassigned

## Objective

Restore both workflows with a Git revert of `68db23f`, resolve conflicts, and retain all pre-existing uncommitted executable and validation work.

## Baseline and scope

The starting HEAD was `68db23f` with substantial uncommitted tracked and new files. Scope includes restoring ten profiles, their code/tests/docs, and adapting the in-progress validation matrix to the restored timecard and CSV shapes. No source workbook changes or business-rule changes.

## Current repository facts

The initial work was saved using `git stash push --include-untracked`; the safety stash remains available. Clean revert commit `8a9a0ad` restores the original workflow files. Reapplying the stash generated nine conflicted paths, including configuration and shared documentation.

## Unknowns and human decisions

The user explicitly requested the revert and conflict resolution. Existing uncommitted work must remain uncommitted. Existing EXE artifacts predate restoration; rebuilding binaries is outside this Git restoration request. Production source/destination certification remains unverified.

## Milestones / Progress

- [x] M1 — inspect state, save tracked/new files, create revert commit, restore saved work.
- [x] M2 — merge newer config guards and executable docs with restored workflows; preserve ignore rules and historical evidence.
- [x] M3 — run tests/docs/Ruff, verify ten profiles and no unmerged index entries, restore the original unstaged working-tree posture.

## Step-by-step design

Keep new structural configuration validation while allowing the restored processor. Keep newer docs and restore ten-profile inventories; remove links to records deleted by the revert while retaining dated execution history. Retain `.gitignore` from newer executable work. Extend the named-column matrix to Taiwan CSV output and preserve the dedicated Reno aggregation test. Check all ten mirrored profiles; update standalone smoke inventory for future rebuilds.

## Verification and acceptance

Run `uv run pytest -q`, `uv run python scripts/check_docs.py`, `uv run ruff check src tests`, CLI profile inventory, `git diff --check`, and `git ls-files -u`. Tests/docs must pass, profiles must match across mirrors, and conflicts must be absent. Record existing lint findings separately from restoration findings. Compare every pre-existing stash file with the final tree to identify intentional merges and verify all new files survived.

## Evidence / execution log

2026-11-25: clean revert created as `8a9a0ad`; safety stash retained. Initial stash restoration produced nine conflicts; all resolved while preserving newer features. Final tests: 487 passed in 37.29s. Docs: PASS, 54 Markdown files / 10 mirrored profiles. CLI lists ten profiles. Ruff: 64 legacy findings (61 prior plus three restored), tracked in TD-017. Original tracked/new work audit: 39 paths present, none missing; safety stash retained. Git markers/whitespace/unmerged index checks passed. Initial Taiwan fixture failures and build dependency retry are recorded in the execution log.

## Decisions

Preserve the newer executable/build ignore rules and Python cache rules because they belong to ongoing uncommitted work. Preserve historical test/build counts as historical evidence and distinguish current restored-source validation from older EXE artifacts.

## Risks / rollback

The safety stash preserves all original tracked and new files. Do not drop it during this work. Never use a hard reset or overwrite newer work with old file versions. Restoring the inventory can expose test assumptions about file shapes; adapt fixtures rather than weakening production behavior.

## Next step

Restoration is complete. Existing executable artifacts require a separate rebuild; ongoing work and conflict-resolution adaptations remain uncommitted.
